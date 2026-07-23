import urllib.parse

def get_all_tabs_flat(tabs_list):
    flat = []
    for t in tabs_list:
        flat.append(t)
        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                flat.extend(get_all_tabs_flat([sub_t]))
    return flat

def is_custom_script_url(url):
    if not url:
        return False
    u = url.lower()
    return "php/custom" in u or "gcb.cfg/php/custom" in u or ".cfg/php/custom" in u

def extract_endpoints(components):
    """
    Scans components for external HTTP/S endpoints and evaluates risk configurations.
    """
    endpoints = []
    # Map URLs to their consolidated endpoint dictionaries to merge duplicates
    endpoints_by_url = {}

    workspaces = components.get("workspaces", [])
    scripts = components.get("customScripts", [])
    cpm_handlers = components.get("cpm", [])

    # Helper to add/merge endpoints
    def add_endpoint(url, ref_name, ref_type, params=None, risk=""):
        if not url:
            return
        
        if is_custom_script_url(url) and "Custom" not in ref_type:
            ref_type = f"{ref_type} (Custom PHP Script)"

        # Parse query params from the URL if not explicitly provided
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        extracted_params = []
        if params:
            extracted_params.extend(params)
        else:
            for k, vals in query_params.items():
                for v in vals:
                    extracted_params.append(f"{k}={v}")

        url_base = parsed_url._replace(query="").geturl()
        ref_str = f"{ref_type}: {ref_name}"

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
                "url": url_base,
                "referencedIn": [ref_str],
                "params": extracted_params,
                "type": ref_type,
                "risk": risk
            }

    # 1. Workspaces (Browser tabs)
    for ws in workspaces:
        ws_name = ws.get("name")
        for tab in get_all_tabs_flat(ws.get("tabs", [])):
            tab_text = tab.get("text", "Unknown Tab")
            for br in tab.get("browsers", []):
                url = br.get("url")
                if url:
                    risk = ""
                    if br.get("suppress_errors"):
                        risk = "SuppressErrors=True — silent failures possible"
                    add_endpoint(
                        url=url,
                        ref_name=f"{ws_name} → {tab_text} tab",
                        ref_type="EmbeddedBrowser",
                        risk=risk
                    )

        # Workspace Ribbon Links
        for link in ws.get("ribbon_links", []):
            url = link.get("url")
            if url:
                add_endpoint(
                    url=url,
                    ref_name=f"{ws_name} → Ribbon Link: {link.get('title')}",
                    ref_type="RibbonLink",
                    risk=""
                )

    # 2. CPM Handlers
    for cpm in cpm_handlers:
        cpm_name = cpm.get("file_name")
        risk_details = [rf.get("detail") for rf in cpm.get("risk_flags", [])]
        risk_str = "; ".join(risk_details) if risk_details else ""
        
        # Check if it has cURL calls
        cpm_type = "CPM (cURL)" if cpm.get("external_calls") else "CPM"
        
        for url in cpm.get("urls", []):
            add_endpoint(
                url=url,
                ref_name=cpm_name,
                ref_type=cpm_type,
                risk=risk_str
            )

    # 3. Custom Scripts
    for script in scripts:
        script_name = script.get("file_name")
        risk_details = [rf.get("detail") for rf in script.get("risk_flags", [])]
        risk_str = "; ".join(risk_details) if risk_details else ""
        
        ref_type = "CustomScript"
        if script.get("external_calls"):
            ref_type += f" ({', '.join(script.get('external_calls'))})"

        for url in script.get("urls", []):
            add_endpoint(
                url=url,
                ref_name=script_name,
                ref_type=ref_type,
                risk=risk_str
            )

    return list(endpoints_by_url.values())
