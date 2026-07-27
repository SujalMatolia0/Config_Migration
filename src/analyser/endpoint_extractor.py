import urllib.parse
try:
    from .utils import get_all_tabs_flat, is_custom_script_url, safe_basename
except ImportError:
    from utils import get_all_tabs_flat, is_custom_script_url, safe_basename


def extract_endpoints(components):
    """
    Scans all parsed components for external HTTP/S endpoints and config risks.

    Fixes vs previous version:
    - risk_flags handled as strings (cpm_parser output) not dicts
    - has_curl used instead of missing 'external_calls' key
    - safe_basename() used for script name extraction from URLs
    - No duplicate get_all_tabs_flat definition

    Enhancements:
    - SOAP endpoint URLs from CPM config_vars surfaced as endpoint hints
    - Risk label includes cURL flag explicitly
    - Endpoint type distinguishes CPM-Async from CPM-Sync
    - External URLs from custom scripts also captured
    """
    endpoints_by_url = {}

    workspaces   = components.get("workspaces", [])
    scripts      = components.get("customScripts", [])
    cpm_handlers = components.get("cpm", [])

    def add_endpoint(url, ref_name, ref_type, params=None, risk=""):
        if not url:
            return

        if is_custom_script_url(url) and "Custom" not in ref_type:
            ref_type = f"{ref_type} (Custom PHP Script)"

        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            parsed = urllib.parse.urlparse(urllib.parse.quote(url, safe="://?=&"))
        query_params = urllib.parse.parse_qs(parsed.query)

        extracted_params = list(params) if params else [
            f"{k}={v}" for k, vals in query_params.items() for v in vals
        ]

        url_base = parsed._replace(query="").geturl()
        ref_str  = f"{ref_type}: {ref_name}"

        if url_base in endpoints_by_url:
            existing = endpoints_by_url[url_base]
            if ref_str not in existing["referencedIn"]:
                existing["referencedIn"].append(ref_str)
            for p in extracted_params:
                if p not in existing["params"]:
                    existing["params"].append(p)
            if risk and risk not in existing["risk"]:
                existing["risk"] = (existing["risk"] + "; " + risk).strip("; ")
        else:
            endpoints_by_url[url_base] = {
                "url":          url_base,
                "referencedIn": [ref_str],
                "params":       extracted_params,
                "type":         ref_type,
                "risk":         risk
            }

    # ── 1. Workspace embedded browsers & ribbon links ──────────────────────
    for ws in workspaces:
        ws_name = ws.get("name", "")
        for tab in get_all_tabs_flat(ws.get("tabs", [])):
            tab_text = tab.get("text", "Unknown Tab")
            for br in tab.get("browsers", []):
                url = br.get("url")
                if url:
                    risk = "SuppressErrors=True — silent failures possible" if br.get("suppress_errors") else ""
                    add_endpoint(
                        url=url,
                        ref_name=f"{ws_name} → {tab_text}",
                        ref_type="EmbeddedBrowser",
                        risk=risk
                    )

        for link in ws.get("ribbon_links", []):
            url = link.get("url")
            if url:
                add_endpoint(
                    url=url,
                    ref_name=f"{ws_name} → Ribbon: {link.get('title')}",
                    ref_type="RibbonLink"
                )

    # ── 2. CPM Handlers ────────────────────────────────────────────────────
    for cpm in cpm_handlers:
        if cpm.get("format") not in ("cpm_procedure", "cpm_php"):
            continue

        cpm_name = cpm.get("name") or cpm.get("file_name", "")

        # FIX: risk_flags are strings in cpm_parser, not dicts
        risk_parts = []
        for rf in cpm.get("risk_flags", []):
            risk_parts.append(rf if isinstance(rf, str) else rf.get("detail", str(rf)))
        # FIX: use has_curl bool, not missing 'external_calls' key
        if cpm.get("has_curl"):
            risk_parts.append("Uses cURL for outbound HTTP")
        risk_str = "; ".join(risk_parts)

        # Enhancement: async vs sync label
        cpm_type = "CPM-Async" if cpm.get("is_async") else "CPM-Sync"

        for url in cpm.get("urls", []):
            add_endpoint(url=url, ref_name=cpm_name, ref_type=cpm_type, risk=risk_str)

        # Enhancement: SOAP actions surfaced as pseudo-endpoints (for visibility)
        for soap in cpm.get("soap_actions", []):
            siebel_url_hint = next(
                (v for v in cpm.get("config_vars", []) if "SIEBEL_URL" in v), None
            )
            # Use a safe pseudo-URL that won't trip urlparse bracket parsing
            hint_suffix = f" via {siebel_url_hint}" if siebel_url_hint else ""
            pseudo_url = f"urn:soap:{soap}{hint_suffix}"
            add_endpoint(
                url=pseudo_url,
                ref_name=cpm_name,
                ref_type=f"{cpm_type} (SOAP)",
                risk=risk_str
            )

    # ── 3. Custom Scripts ──────────────────────────────────────────────────
    for script in scripts:
        script_name = script.get("file_name", "")

        risk_parts = []
        for rf in script.get("risk_flags", []):
            risk_parts.append(rf if isinstance(rf, str) else rf.get("detail", str(rf)))
        # FIX: use has_curl bool not 'external_calls'
        if script.get("has_curl"):
            risk_parts.append("Uses cURL for outbound HTTP")
        risk_str = "; ".join(risk_parts)

        ref_type = "CustomScript"
        if script.get("has_curl"):
            ref_type += " (cURL)"

        for url in script.get("urls", []):
            add_endpoint(url=url, ref_name=script_name, ref_type=ref_type, risk=risk_str)

    # ── 4. BUI Add-Ins ────────────────────────────────────────────────────
    bui_addins = components.get("buiAddins", [])
    for bui in bui_addins:
        bui_name = bui.get("name", "BUI Add-In")
        risk_parts = [rf.get("detail", str(rf)) for rf in bui.get("risk_flags", [])]
        risk_str = "; ".join(risk_parts)

        for api_call in bui.get("api_calls", []):
            raw_ep = api_call.get("endpoint", "REST Endpoint")
            detail = ""
            if api_call.get("object"):
                detail = f" ({api_call['object']})"
            elif api_call.get("report_id"):
                detail = f" (Report ID {api_call['report_id']})"

            if raw_ep.startswith("connect/v1.3/") or raw_ep.startswith("/"):
                clean_url = raw_ep
            else:
                clean_url = f"connect/v1.3/{raw_ep}"

            full_url_label = f"{clean_url}{detail}"
            call_type = f"BUI Add-In ({api_call.get('type', 'REST API')})"

            add_endpoint(
                url=full_url_label,
                ref_name=f"{bui_name} ({api_call.get('file', 'UI')})",
                ref_type=call_type,
                risk=risk_str
            )

    return list(endpoints_by_url.values())
