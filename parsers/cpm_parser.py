import os
import html
import re
from lxml import etree

OPERATIONS_MAP = {
    1: "Create",
    2: "Update",
    4: "Destroy",
    3: "Create, Update",
    5: "Create, Destroy",
    6: "Update, Destroy",
    7: "Create, Update, Destroy"
}

def decode_operations(oper_val):
    try:
        val = int(oper_val)
        if val in OPERATIONS_MAP:
            return OPERATIONS_MAP[val]
        op_list = []
        if val & 1: op_list.append("Create")
        if val & 2: op_list.append("Update")
        if val & 4: op_list.append("Destroy")
        return ", ".join(op_list) if op_list else f"Unknown / Custom (code: {val})"
    except (ValueError, TypeError):
        return str(oper_val or "—")

def parse_cpm_mappings(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Mappings file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    mappings = []
    suppress_flags = []

    for cm in root.findall(".//ClassMapping"):
        class_name = cm.get("ClassName") or "Unknown"
        mappings_elem = cm.find("Mappings")
        if mappings_elem is not None:
            for m in mappings_elem.findall("Mapping"):
                interface_name = m.get("Interface") or "Public"
                operation = m.get("Operation") or "Unknown"
                procedure = m.get("Procedure") or ""
                mappings.append({
                    "object": class_name,
                    "interface": interface_name,
                    "operation": operation,
                    "procedure": procedure
                })
            for sf in mappings_elem.findall("SuppressFlagMapping"):
                interface_name = sf.get("Interface") or "Public"
                suppress_flags.append({
                    "object": class_name,
                    "interface": interface_name
                })

    return {
        "format": "cpm_mappings",
        "file_name": os.path.basename(file_path),
        "mappings": mappings,
        "suppress_flags": suppress_flags
    }

def decode_php_version(php_ver):
    if not php_ver or php_ver == "—":
        return "—"
    try:
        val = int(php_ver)
        major = val // 10000
        minor = (val % 10000) // 100
        patch = val % 100
        return f"{major}.{minor}.{patch} ({php_ver})"
    except (ValueError, TypeError):
        return str(php_ver)

def format_cpm_version(ver):
    if not ver or ver == "—":
        return "—"
    if str(ver).isdigit():
        return f"{ver} [internal version stamp]"
    return str(ver)

EXCLUDE_CF = {"c", "CO", "save", "fetch", "destroy", "CustomFields", "Organization", "Contact", "Incident", "SocialUser"}

def extract_key_logic(php_code, soap_actions=None):
    if not php_code:
        return "No PHP content provided."

    summaries = []

    if "Source->ID == 5001" in php_code or "Techmail" in php_code:
        summaries.append("Processes Techmail-originated incoming records.")
    elif "Source->ID == 3001" in php_code or "AAQ" in php_code:
        summaries.append("Processes Ask-A-Question / End-User web portal submissions.")

    if "preg_match" in php_code and ("Subject" in php_code or "MailHeader" in php_code):
        summaries.append("Parses email headers and subject lines for reference numbers and customer identifiers via regex.")

    if "sendSoapRequest" in php_code or "CUSTOM_CFG_SIEBEL_URL" in php_code:
        if soap_actions:
            action_str = ", ".join(f"`{a}`" for a in soap_actions)
            summaries.append(f"Queries external Siebel SOAP web services ({action_str}).")
        else:
            summaries.append("Queries external Siebel SOAP web services.")

    roql_matches = re.findall(r'ROQL::query(?:Object)?\s*\(\s*["\']([^"\']+)["\']', php_code)
    if roql_matches:
        tables_queried = set()
        for q in roql_matches:
            m = re.search(r'FROM\s+([a-zA-Z0-9_\.]+)', q, re.IGNORECASE)
            if m:
                tables_queried.add(m.group(1))
        if tables_queried:
            summaries.append(f"Executes ROQL queries against OSVC tables ({', '.join(f'`{t}`' for t in sorted(tables_queried))}).")

    rn_objects = sorted(list(set(re.findall(r'RNCPHP\\([a-zA-Z0-9_\\]+)', php_code))))
    filtered_objs = [o for o in rn_objects if o not in ("ConnectAPIError", "ConnectAPIErrorBase", "RNObject", "v1_1", "v1_3", "v1_4")]
    if filtered_objs:
        shown = filtered_objs[:4]
        suffix = ", ..." if len(filtered_objs) > 4 else ""
        summaries.append(f"Instantiates and updates OSVC Connect API objects ({', '.join(f'`{o}`' for o in shown)}{suffix}).")

    if "handleRejects" in php_code:
        summaries.append("Evaluates customer eligibility and dispatches rejection notification emails for unregistered or invalid accounts.")

    if not summaries:
        class_match = re.search(r'class\s+([a-zA-Z0-9_]+)', php_code)
        cname = class_match.group(1) if class_match else "handler"
        summaries.append(f"Executes static custom handler logic for `{cname}`.")

    return " ".join(summaries)

def analyze_php_content(php_code):
    if not php_code:
        return {
            "soap_actions": [],
            "custom_fields_read": [],
            "custom_fields_written": [],
            "config_vars": [],
            "key_logic": "No PHP code available.",
            "urls": [],
            "imports": [],
            "osvc_objects": [],
            "has_curl": False,
            "risk_flags": []
        }

    # 1. SOAP Action Names (literal and variable assigned)
    raw_soaps = (
        re.findall(r'SOAPAction.*?"(?:document/http://[^:]+:)?([^"]+)"', php_code, re.IGNORECASE) +
        re.findall(r"sendSoapRequest\s*\(\s*['\"]([a-zA-Z0-9_]+)['\"]", php_code, re.IGNORECASE)
    )
    soap_actions_set = set([s for s in raw_soaps if s and re.match(r'^[a-zA-Z0-9_]+$', s)])

    var_assignments = dict(re.findall(r'\$([a-zA-Z0-9_]+)\s*=\s*["\']([a-zA-Z0-9_]+)["\']', php_code))
    for call_var in re.findall(r'sendSoapRequest\s*\(\s*\$([a-zA-Z0-9_]+)', php_code):
        if call_var in var_assignments and re.match(r'^[a-zA-Z0-9_]+$', var_assignments[call_var]):
            soap_actions_set.add(var_assignments[call_var])

    soap_actions = sorted(list(soap_actions_set))

    # 2. Config Variables
    config_vars = sorted(list(set(
        re.findall(r'["\'](CUST(?:OM|OMER)_CFG_[a-zA-Z0-9_]+)["\']', php_code) +
        re.findall(r'\b(CUST(?:OM|OMER)_CFG_[a-zA-Z0-9_]+)\b', php_code)
    )))

    # 3. Custom Fields Read / Written Detection
    # OSVC patterns: CustomFields->c->field, CustomFields->field, CustomFields.c.field, c$field, setCustomField('field', ...)
    write_patterns = [
        r'CustomFields->c->([a-zA-Z0-9_]+)\s*=',
        r'CustomFields->([a-zA-Z0-9_]+)\s*=',
        r'CustomFields\.c\.([a-zA-Z0-9_]+)\s*=',
        r'c\$([a-zA-Z0-9_]+)\s*=',
        r'\$c\$([a-zA-Z0-9_]+)\s*=',
        r'setCustomField\s*\(\s*["\']([a-zA-Z0-9_]+)["\']'
    ]
    cf_written_set = set()
    for p in write_patterns:
        for match in re.findall(p, php_code):
            if match not in EXCLUDE_CF and len(match) > 1:
                cf_written_set.add(match)

    read_patterns = [
        r'CustomFields->c->([a-zA-Z0-9_]+)',
        r'CustomFields->([a-zA-Z0-9_]+)',
        r'CustomFields\.c\.([a-zA-Z0-9_]+)',
        r'c\$([a-zA-Z0-9_]+)',
        r'\$c\$([a-zA-Z0-9_]+)',
        r'getCustomField\s*\(\s*["\']([a-zA-Z0-9_]+)["\']'
    ]
    cf_read_set = set()
    for p in read_patterns:
        for match in re.findall(p, php_code):
            if match not in EXCLUDE_CF and len(match) > 1:
                cf_read_set.add(match)

    # Bug 1 Fix: Deduplicate cf_read to represent true read-only fields
    cf_read_only_set = cf_read_set - cf_written_set
    cf_written = sorted(list(cf_written_set))
    cf_read_only = sorted(list(cf_read_only_set))

    cf_written_formatted = [f"c${f}" for f in cf_written]
    cf_read_formatted = [f"c${f}" for f in cf_read_only]

    # 4. Key Logic Summary (Bug 5 Fix: Pass detected soap_actions)
    key_logic = extract_key_logic(php_code, soap_actions)

    # 5. External URLs
    urls = sorted(list(set(re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', php_code))))
    filtered_urls = [u for u in urls if "schemas" not in u and "rightnow.com" not in u and "w3.org" not in u and "siebel.com/webservices" not in u]

    # 6. Require / Include statements
    imports = sorted(list(set(
        re.findall(r'(?:require_once|include_once|require|include)\s+["\']([^"\'\$;]+)["\']', php_code)
    )))

    # 7. Connected OSVC Classes
    osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\([a-zA-Z0-9_\\]+)', php_code))))
    filtered_osvc_objects = [o for o in osvc_objects if o not in ("v1_1", "v1_3", "v1_4")]

    # 8. cURL Check & Risk Flags
    has_curl = ("curl_init" in php_code or "curl_exec" in php_code)
    risk_flags = []
    if re.search(r'\$(?:password|passwd|pwd|secret|key|api_key|token|auth)\s*=\s*["\']([^"\'\$]+)["\']', php_code, re.IGNORECASE):
        risk_flags.append("Potential credentials in variable assignments")

    return {
        "soap_actions": soap_actions,
        "config_vars": config_vars,
        "custom_fields_read": cf_read_formatted,
        "custom_fields_written": cf_written_formatted,
        "key_logic": key_logic,
        "urls": filtered_urls,
        "imports": imports,
        "osvc_objects": filtered_osvc_objects,
        "has_curl": has_curl,
        "risk_flags": risk_flags
    }

def parse_cpm_object_procedure(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CPM ObjectProcedure file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    proc_id = root.get("Id") or "—"
    display_name = root.get("DisplayName") or ""
    proc_name = root.get("Name") or display_name or os.path.basename(file_path).replace(".xml", "")
    version_raw = root.get("Version") or "—"
    version_label = format_cpm_version(version_raw)
    operations_code = root.get("Operations") or "1"
    operations_label = decode_operations(operations_code)
    is_async = (root.get("ExecuteAsynchronously") or "False").lower() == "true"
    php_version_raw = root.get("PhpVersion") or "—"
    php_version_label = decode_php_version(php_version_raw)

    # Bound Classes
    bound_classes = []
    classes_elem = root.find("Classes")
    if classes_elem is not None:
        for c in classes_elem.findall("Class"):
            c_name = c.get("ClassName")
            if c_name:
                bound_classes.append(c_name)

    # HTML-entity decode Content attribute
    raw_content_attr = root.get("Content") or ""
    php_content = html.unescape(raw_content_attr)

    # Perform static analysis on PHP code
    analysis = analyze_php_content(php_content)

    return {
        "format": "cpm_procedure",
        "file_name": os.path.basename(file_path),
        "id": proc_id,
        "display_name": display_name,
        "name": proc_name,
        "version": version_label,
        "version_raw": version_raw,
        "operations_code": operations_code,
        "operations_label": operations_label,
        "is_async": is_async,
        "php_version": php_version_label,
        "php_version_raw": php_version_raw,
        "bound_classes": bound_classes,
        "php_content": php_content,
        "soap_actions": analysis["soap_actions"],
        "config_vars": analysis["config_vars"],
        "custom_fields_read": analysis["custom_fields_read"],
        "custom_fields_written": analysis["custom_fields_written"],
        "key_logic": analysis["key_logic"],
        "urls": analysis["urls"],
        "imports": analysis["imports"],
        "osvc_objects": analysis["osvc_objects"],
        "has_curl": analysis["has_curl"],
        "risk_flags": analysis["risk_flags"]
    }

def parse_cpm_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CPM file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    tag = root.tag.split("}")[-1]
    if tag in ["ClassMappings", "Mappings"]:
        return parse_cpm_mappings(file_path)
    elif tag == "ObjectProcedure":
        return parse_cpm_object_procedure(file_path)
    else:
        # Fallback for plain PHP files
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        analysis = analyze_php_content(content)
        class_match = re.search(r'class\s+(\w+)', content, re.IGNORECASE)
        class_name = class_match.group(1) if class_match else os.path.basename(file_path)
        return {
            "format": "cpm_php",
            "file_name": os.path.basename(file_path),
            "id": "—",
            "display_name": class_name,
            "name": class_name,
            "version": "—",
            "operations_code": "—",
            "operations_label": "—",
            "is_async": False,
            "php_version": "—",
            "bound_classes": analysis["osvc_objects"],
            "php_content": content,
            "soap_actions": analysis["soap_actions"],
            "config_vars": analysis["config_vars"],
            "custom_fields_read": analysis["custom_fields_read"],
            "custom_fields_written": analysis["custom_fields_written"],
            "key_logic": analysis["key_logic"],
            "urls": analysis["urls"],
            "imports": analysis["imports"],
            "osvc_objects": analysis["osvc_objects"],
            "has_curl": analysis["has_curl"],
            "risk_flags": analysis["risk_flags"]
        }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_cpm_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python cpm_parser.py <path_to_cpm_xml>")

