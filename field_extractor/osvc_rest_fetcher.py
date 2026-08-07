import time
import requests
from requests.auth import HTTPBasicAuth

# ---------------------------------------------------------------------------
# Strict Read-Only OSVC Connect REST API Metadata Fetcher
# ONLY HTTP GET REQUESTS ARE PERMITTED.
# ---------------------------------------------------------------------------

DEFAULT_REST_VERSION = "v1.4"
HEADERS_SCHEMA_JSON = {
    'Accept': 'application/schema+json',
    'OSvC-CREST-Application-Context': 'Metadata-Schema-Fetch'
}
HEADERS_CATALOG_JSON = {
    'Accept': 'application/json',
    'OSvC-CREST-Application-Context': 'Metadata-Catalog-List'
}

from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_SCHEMA_CACHE = {}

def _create_http_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def _clean_host_url(host):
    """
    Extracts scheme and domain from any user-provided URL or host string.
    Prevents path duplication when user enters full endpoint URLs.
    """
    host = host.strip()
    if not host.startswith('http://') and not host.startswith('https://'):
        host = f"https://{host}"
    
    parsed = urlparse(host)
    scheme = parsed.scheme or 'https'
    netloc = parsed.netloc or parsed.path.split('/')[0]
    return f"{scheme}://{netloc}"

def fetch_schema_get_only(url, session, auth):
    """
    STRICT READ-ONLY: Executes HTTP GET request to fetch JSON schema metadata.
    Uses in-memory _SCHEMA_CACHE to prevent repeated network requests for same endpoint.
    """
    if url in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[url]

    time.sleep(0.1)  # Gentle delay to avoid rate limiting
    resp = session.get(url, headers=HEADERS_SCHEMA_JSON, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    _SCHEMA_CACHE[url] = data
    return data

def fetch_metadata_catalog_get_only(catalog_url, session, auth):
    """
    STRICT READ-ONLY: Executes HTTP GET request to fetch OSVC metadata catalog.
    """
    resp = session.get(catalog_url, headers=HEADERS_CATALOG_JSON, auth=auth, timeout=30)
    resp.raise_for_status()
    return resp.json()

def _resolve_property_field(field_name, field_info, session, auth, base_url, log_cb=print, parent_prefix="", depth=0):
    """
    Recursively inspects a schema property definition and resolves $ref links via HTTP GET.
    Returns a list of extracted field metadata dicts.
    """
    if depth > 2:  # Safeguard against deep circular $ref loops
        return []

    full_name = f"{parent_prefix}.{field_name}" if parent_prefix else field_name
    field_type = field_info.get("type", "unknown")
    if isinstance(field_type, list):
        field_type = [t for t in field_type if t != "null"]
        field_type = field_type[0] if field_type else "unknown"

    label = field_info.get("label") or field_info.get("title") or field_name.replace('_', ' ').title()
    desc = field_info.get("description", "")
    nullable = field_info.get("nullable", True)
    max_len = field_info.get("maxLength", field_info.get("maxLengthBytes", "-"))

    ref_url = field_info.get("$ref")

    # Fast-path namedIDs and lookup shortcuts without unnecessary network recursion
    if ref_url:
        # Prepend base_url if ref_url is a relative path
        if not ref_url.startswith("http"):
            if not ref_url.startswith("/"):
                ref_url = f"/{ref_url}"
            ref_url = f"{base_url}{ref_url}"

        ref_basename = ref_url.rstrip('/').split('/')[-1]

        # NamedID fast-path
        if "/namedIDs/" in ref_url or "namedID" in ref_url.lower():
            field_type = f"_lookup:NamedID({ref_basename})"
        elif field_type in ("object", "unknown"):
            try:
                ref_schema = fetch_schema_get_only(ref_url, session, auth)
                singular = ref_schema.get("definitions", {}).get("singularResource", {})
                is_menu = singular.get("isMenu", False)
                ref_name = singular.get("name") or ref_basename

                if is_menu:
                    field_type = f"_menu:{ref_name}"
                else:
                    child_props = singular.get("properties", {})
                    # Only recurse into composite structures (like name -> first, last)
                    if child_props and depth < 1 and not ref_name.startswith("http"):
                        sub_fields = []
                        for c_name, c_info in child_props.items():
                            if c_name != "customFields":
                                sub_fields.extend(
                                    _resolve_property_field(c_name, c_info, session, auth, base_url, log_cb=log_cb, parent_prefix=full_name, depth=depth+1)
                                )
                        if sub_fields:
                            return sub_fields
                    field_type = f"_lookup:{ref_name}"
            except Exception as err:
                log_cb(f"[WARN] Unable to resolve $ref schema for field '{full_name}': {err}")
                field_type = f"_lookup:{ref_basename}"

    is_custom = field_name.startswith("c$") or "customFields" in full_name
    pkg_name = "c" if is_custom else "OracleServiceCloud"

    field_dict = {
        "field_id": field_name,
        "field_name": full_name,
        "field_label": label,
        "data_type": str(field_type),
        "is_system_field": not is_custom,
        "package_name": pkg_name,
        "is_nullable": bool(nullable),
        "is_lookup": str(field_type).startswith("_lookup") or str(field_type).startswith("lookup"),
        "is_readonly": not field_info.get("isAvailableForPOST", True),
        "max_length": str(max_len),
        "description": desc,
        "is_available_get": field_info.get("isAvailableForGET", True),
        "is_available_post": field_info.get("isAvailableForPOST", False),
        "is_available_patch": field_info.get("isAvailableForPATCH", False),
        "is_deprecated": field_info.get("isDeprecated", False)
    }

    return [field_dict]


# Known OSVC standard object names to probe directly when catalog list is empty
KNOWN_STANDARD_OBJECTS = [
    "contacts", "incidents", "organizations", "answers", "tasks",
    "opportunities", "quotes", "products", "assets", "serviceContracts",
    "accounts", "surveys", "chats", "emails", "notes", "threads"
]

def fetch_standard_objects_via_rest(host, username, password, selected_objects=None, include_custom=False, log_cb=print):
    """
    STRICT READ-ONLY API FETCHER:
    Connects to the OSVC Connect REST API via HTTP GET requests only.
    Fetches standard object schemas and converts them into standard objects_map format.

    Strategy:
      1. GET /metadata-catalog (root) to discover all object names + alternate schema links.
      2. If root returns no items (some instances restrict it), directly probe known standard
         object endpoints: GET /metadata-catalog/{objectName} with Accept: application/schema+json.
    """
    base_url = _clean_host_url(host)
    catalog_url = f"{base_url}/services/rest/connect/{DEFAULT_REST_VERSION}/metadata-catalog"

    _SCHEMA_CACHE.clear()
    session = _create_http_session()
    auth = HTTPBasicAuth(username, password)

    log_cb(f"[STRICT GET ONLY] Connecting to OSVC Metadata Catalog root: {catalog_url}")

    items = []
    try:
        catalog_data = fetch_metadata_catalog_get_only(catalog_url, session, auth)
        items = catalog_data.get("items", []) or catalog_data.get("objects", [])
        if not items and isinstance(catalog_data, list):
            items = catalog_data
        log_cb(f"[SUCCESS] Metadata catalog root returned {len(items)} objects")
    except Exception as err:
        log_cb(f"[WARNING] Catalog root returned error ({err}). Will probe standard object endpoints directly.")

    # If catalog root returned no items, build synthetic items from known standard objects
    if not items:
        probe_targets = selected_objects if selected_objects else KNOWN_STANDARD_OBJECTS
        log_cb(f"[INFO] Probing {len(probe_targets)} standard object schema endpoints directly via GET")
        for obj_name in probe_targets:
            items.append({
                "name": obj_name,
                "links": [{"rel": "alternate", "href": f"{base_url}/services/rest/connect/{DEFAULT_REST_VERSION}/metadata-catalog/{obj_name}"}]
            })

    log_cb(f"[INFO] Processing {len(items)} object candidate(s)...")

    objects_map = {}
    processed_count = 0

    for item in items:
        obj_name = item.get("name") or item.get("canonicalName") or ""
        if not obj_name:
            continue

        # Skip custom objects if standard-only mode is active (custom objects contain a dot, e.g. CO.MyObj)
        is_custom_obj = '.' in obj_name
        if is_custom_obj and not include_custom:
            continue

        # Filter by selected objects list if provided
        if selected_objects:
            sel_lower = [s.strip().lower() for s in selected_objects]
            if obj_name.lower() not in sel_lower:
                continue

        # Locate alternate link for schema GET request
        links = item.get("links", [])
        schema_url = None
        for l in links:
            if l.get("rel") in ("alternate", "canonical", "describedby", "self"):
                schema_url = l.get("href")
                break

        if not schema_url:
            schema_url = f"{base_url}/services/rest/connect/{DEFAULT_REST_VERSION}/metadata-catalog/{obj_name}"
        elif not schema_url.startswith("http"):
            schema_url = f"{base_url}{schema_url}"

        try:
            log_cb(f"[STRICT GET ONLY] Fetching schema for object: {obj_name}")
            # Use per-object context header (e.g. Get-contacts) matching OSVC Postman conventions
            obj_context_headers = {
                'Accept': 'application/schema+json',
                'OSvC-CREST-Application-Context': f'Get-{obj_name}'
            }
            time.sleep(0.3)
            resp = session.get(schema_url, headers=obj_context_headers, auth=auth, timeout=30)
            resp.raise_for_status()
            schema_data = resp.json()

            singular = schema_data.get("definitions", {}).get("singularResource", {})
            if singular.get("isMenu") is True:
                log_cb(f"[INFO] Skipping menu-only object: {obj_name}")
                continue

            properties = singular.get("properties", {})
            extracted_fields = []

            for f_name, f_info in properties.items():
                if f_name == "customFields" and not include_custom:
                    continue

                fields_resolved = _resolve_property_field(f_name, f_info, session, auth, base_url, log_cb=log_cb)
                extracted_fields.extend(fields_resolved)

            if extracted_fields:
                objects_map[obj_name.lower()] = {
                    "object_name": obj_name.capitalize(),
                    "fields": extracted_fields
                }
                processed_count += 1
                log_cb(f"[SUCCESS] Extracted {len(extracted_fields)} standard fields for '{obj_name}'")

        except Exception as err:
            log_cb(f"[WARNING] Failed to fetch schema for object '{obj_name}': {err}")

    log_cb(f"[COMPLETED] Extracted {processed_count} standard object schemas via HTTP GET.")
    return objects_map
