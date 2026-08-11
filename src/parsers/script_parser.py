import os
import re

def parse_script_file(file_path):
    """
    Statically analyzes custom scripts (PHP or JS) to map dependencies, object usage,
    and 3 categorized API types (Internal ROQL/Connect, External SOAP, External REST)
    along with flow execution steps for Mermaid sequence diagrams.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Script file not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_name = os.path.basename(file_path)
    script_type = "Unknown"
    
    normalized_path = file_path.replace("\\", "/").lower()
    if "widget" in normalized_path:
        script_type = "Widget Component"
    elif "controller" in normalized_path or "class " in content and "controller" in content.lower():
        script_type = "Controller Endpoint"
    elif "model" in normalized_path:
        script_type = "Model Helper"
    elif ext == ".js":
        script_type = "Client-side Script"
    elif ext == ".php":
        script_type = "Server-side Utility"

    imports = []
    osvc_objects = []
    external_calls = []
    urls = []
    exposed_routes = []
    risk_flags = []

    # 3 Categorized API Structures
    internal_apis = []
    external_soap_apis = []
    external_rest_apis = []
    flow_steps = []

    # ── PHP Parsing ────────────────────────────────────────────────────────
    if ext == ".php":
        # Imports: require, include
        import_matches = re.findall(r'(?:require|include)(?:_once)?\s*\(?\s*["\']([^"\'\(\)]+?)["\']\s*\)?', content, re.IGNORECASE)
        imports = sorted(list(set(import_matches)))

        # OSVC Objects referenced
        osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\(\w+)', content))))

        # 1. INTERNAL APIS (ROQL & Native Connect PHP Objects)
        roql_queries = re.findall(r'["\'](SELECT[\s\S]*?FROM[\s\S]*?)["\']', content, re.IGNORECASE)
        for q in roql_queries:
            clean_q = " ".join(q.split())
            internal_apis.append({
                "type": "ROQL Query",
                "detail": clean_q,
                "operation": "SELECT Query"
            })
            flow_steps.append({"stage": "Internal DB", "action": f"Execute ROQL Query: {clean_q[:60]}..."})

        fetch_matches = re.findall(r'RNCPHP\\(\w+)::fetch\(([^)]*)\)', content)
        for obj, args in fetch_matches:
            internal_apis.append({
                "type": "Connect PHP Fetch",
                "detail": f"RNCPHP\\{obj}::fetch({args.strip()})",
                "operation": f"Fetch {obj}"
            })
            flow_steps.append({"stage": "Internal API", "action": f"Fetch {obj} instance ({args.strip()})"})

        if "AgentAuthenticator::authenticateSessionID" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateSessionID($session_id)",
                "operation": "Validate Agent Session"
            })
            flow_steps.append({"stage": "Authentication", "action": "Validate Agent Session ID"})

        if "AgentAuthenticator::authenticateCredentials" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateCredentials($username, $password)",
                "operation": "Validate Agent Credentials"
            })
            flow_steps.append({"stage": "Authentication", "action": "Authenticate Agent Credentials"})

        if "save()" in content:
            save_objs = re.findall(r'\$(\w+)->save\(\)', content)
            for var in set(save_objs):
                internal_apis.append({
                    "type": "Connect PHP Save",
                    "detail": f"${var}->save()",
                    "operation": f"Commit changes to {var}"
                })
                flow_steps.append({"stage": "Internal API", "action": f"Commit record changes (${var}->save())"})

        # 2. EXTERNAL SOAP APIS
        if "SoapClient" in content or "soap" in content.lower() or "wsdl" in content.lower():
            soap_urls = re.findall(r'["\'](https?://[^"\'\s]+\.wsdl|https?://[^"\'\s]+soap[^"\'\s]*)["\']', content, re.IGNORECASE)
            if not soap_urls and "CUSTOM_CFG_SIEBEL_URL" in content:
                soap_urls = ["SIEBEL_SOAP_ENDPOINT (CUSTOM_CFG_SIEBEL_URL)"]

            for surl in (soap_urls or ["SOAP Web Service"]):
                external_soap_apis.append({
                    "protocol": "SOAP 1.1 / 1.2",
                    "endpoint": surl,
                    "action": "SOAP Web Service Request"
                })
                external_calls.append(f"SOAP Service: {surl}")
                flow_steps.append({"stage": "External SOAP", "action": f"Invoke SOAP Service ({surl})"})

        if "xml_parse_into_struct" in content or "php://input" in content:
            external_soap_apis.append({
                "protocol": "XML Payload Ingestion",
                "endpoint": "php://input",
                "action": "Parse Incoming XML Payload"
            })
            flow_steps.append({"stage": "Ingestion", "action": "Receive & Parse XML POST Payload"})

        # 3. EXTERNAL REST APIS
        if "curl_init" in content or "curl_exec" in content:
            curl_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
            clean_urls = [u for u in curl_urls if "schemas/dbaudit" not in u and "rightnow.com" not in u]

            method_match = re.search(r'CURLOPT_CUSTOMREQUEST\s*,\s*["\'](\w+)["\']', content)
            http_method = method_match.group(1) if method_match else "POST/GET"

            if clean_urls:
                for curl_url in set(clean_urls):
                    external_rest_apis.append({
                        "protocol": "REST / HTTP",
                        "method": http_method,
                        "endpoint": curl_url,
                        "details": f"cURL {http_method} request"
                    })
                    urls.append(curl_url)
                    external_calls.append(f"REST cURL {http_method}: {curl_url}")
                    flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} call -> {curl_url}"})
            else:
                external_rest_apis.append({
                    "protocol": "REST / HTTP",
                    "method": http_method,
                    "endpoint": "Dynamic / Configured REST Endpoint",
                    "details": f"cURL {http_method} request via Configuration"
                })
                external_calls.append("cURL REST Client Invocation")
                flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} HTTP Request"})

        # Additional URL extraction
        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        for u in set(raw_urls):
            if "schemas/dbaudit" not in u and "rightnow.com" not in u and u not in urls:
                urls.append(u)

        # Extract Analytics Report IDs
        report_ids_raw = re.findall(r'(?:AnalyticsReport::fetch|runReport|report_id|AcId|SearchReportId|report\s*id)\D*(\d{4,6})', content, re.IGNORECASE)
        report_ids = sorted(list(set([int(r) for r in report_ids_raw])))

        # Exposed routes/endpoints
        route_matches = re.findall(r'public\s+function\s+(action\w+)\s*\(', content, re.IGNORECASE)
        for route in route_matches:
            clean_route = route[6:].lower() if route.lower().startswith("action") else route.lower()
            exposed_routes.append(clean_route)

    # ── JS Parsing ─────────────────────────────────────────────────────────
    elif ext == ".js":
        es6_imports = re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content)
        commonjs_imports = re.findall(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        imports = sorted(list(set(es6_imports + commonjs_imports)))

        if "fetch(" in content or re.search(r'fetch\s*\(', content):
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "fetch API",
                "endpoint": "Asynchronous REST Fetch",
                "details": "JS Fetch API call"
            })
            external_calls.append("JS Fetch REST API call")
            flow_steps.append({"stage": "External REST", "action": "JS Fetch API request"})

        if "$.ajax" in content or "$.get" in content or "$.post" in content:
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "jQuery AJAX",
                "endpoint": "AJAX HTTP Request",
                "details": "jQuery AJAX request"
            })
            external_calls.append("jQuery AJAX request")
            flow_steps.append({"stage": "External REST", "action": "jQuery AJAX request"})

        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        urls = sorted(list(set(raw_urls)))

        if "RightNow" in content or "RightNow.Action" in content:
            osvc_objects.append("RightNow Client Framework")
            internal_apis.append({
                "type": "Client Framework",
                "detail": "RightNow Client JS Framework Action",
                "operation": "UI Event Handler"
            })

    # Hardcoded credentials check
    cred_patterns = [
        r'(?:password|passwd|pwd|secret|key|api_key|token|auth)\s*[:=]\s*["\']([^"\'\$]+)["\']',
    ]
    for pattern in cred_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        valid_creds = [m for m in matches if len(m.strip()) > 3]
        if valid_creds:
            risk_flags.append({
                "type": "Hardcoded Credential",
                "detail": f"Potential credentials found in variable assignments (count: {len(valid_creds)})"
            })

def generate_script_summary(script_name, content, internal_apis, soap_apis, rest_apis, osvc_objects, flow_steps):
    """
    Generates a purely dynamic, data-driven summary based on static code metrics
    and parsed API operations. Zero hardcoded script names.
    """
    _, ext = os.path.splitext(script_name.lower())
    script_kind = "Client-side JavaScript file" if ext == ".js" else "Server-side PHP script"

    desc = f"{script_kind} (`{script_name}`)"

    details = []
    if internal_apis:
        details.append(f"executes {len(internal_apis)} internal OSVC database/Connect PHP operation(s)")
    if rest_apis:
        details.append(f"integrates with {len(rest_apis)} external REST HTTP service(s)")
    if soap_apis:
        details.append(f"integrates with {len(soap_apis)} external SOAP web service(s)")

    if details:
        desc += " that " + ", ".join(details) + "."
    else:
        desc += " providing utility helper functions."

    if osvc_objects:
        clean_objs = [o for o in osvc_objects if o not in ("ROQL", "RNObject", "ConnectAPI", "RightNow Client Framework")]
        if clean_objs:
            desc += f" Primary entity target(s): {', '.join(clean_objs[:3])}."

    return desc


def parse_script_file(file_path):
    """
    Statically analyzes custom scripts (PHP or JS) to map dependencies, object usage,
    and 3 categorized API types (Internal ROQL/Connect, External SOAP, External REST)
    along with flow execution steps for Mermaid sequence diagrams.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Script file not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_name = os.path.basename(file_path)
    script_type = "Unknown"
    
    normalized_path = file_path.replace("\\", "/").lower()
    if "widget" in normalized_path:
        script_type = "Widget Component"
    elif "controller" in normalized_path or "class " in content and "controller" in content.lower():
        script_type = "Controller Endpoint"
    elif "model" in normalized_path:
        script_type = "Model Helper"
    elif ext == ".js":
        script_type = "Client-side Script"
    elif ext == ".php":
        script_type = "Server-side Utility"

    imports = []
    osvc_objects = []
    external_calls = []
    urls = []
    exposed_routes = []
    risk_flags = []

    # 3 Categorized API Structures
    internal_apis = []
    external_soap_apis = []
    external_rest_apis = []
    flow_steps = []

    # ── PHP Parsing ────────────────────────────────────────────────────────
    if ext == ".php":
        import_matches = re.findall(r'(?:require|include)(?:_once)?\s*\(?\s*["\']([^"\'\(\)]+?)["\']\s*\)?', content, re.IGNORECASE)
        imports = sorted(list(set(import_matches)))

        osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\(\w+)', content))))

        # 1. INTERNAL APIS
        roql_queries = re.findall(r'["\'](SELECT[\s\S]*?FROM[\s\S]*?)["\']', content, re.IGNORECASE)
        for q in roql_queries:
            clean_q = " ".join(q.split())
            internal_apis.append({
                "type": "ROQL Query",
                "detail": clean_q,
                "operation": "SELECT Query"
            })
            flow_steps.append({"stage": "Internal DB", "action": f"Execute ROQL Query: {clean_q[:60]}..."})

        fetch_matches = re.findall(r'RNCPHP\\(\w+)::fetch\(([^)]*)\)', content)
        for obj, args in fetch_matches:
            internal_apis.append({
                "type": "Connect PHP Fetch",
                "detail": f"RNCPHP\\{obj}::fetch({args.strip()})",
                "operation": f"Fetch {obj}"
            })
            flow_steps.append({"stage": "Internal API", "action": f"Fetch {obj} instance ({args.strip()})"})

        if "AgentAuthenticator::authenticateSessionID" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateSessionID($session_id)",
                "operation": "Validate Agent Session"
            })
            flow_steps.append({"stage": "Authentication", "action": "Validate Agent Session ID"})

        if "AgentAuthenticator::authenticateCredentials" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateCredentials($username, $password)",
                "operation": "Validate Agent Credentials"
            })
            flow_steps.append({"stage": "Authentication", "action": "Authenticate Agent Credentials"})

        if "save()" in content:
            save_objs = re.findall(r'\$(\w+)->save\(\)', content)
            for var in set(save_objs):
                internal_apis.append({
                    "type": "Connect PHP Save",
                    "detail": f"${var}->save()",
                    "operation": f"Commit changes to {var}"
                })
                flow_steps.append({"stage": "Internal API", "action": f"Commit record changes (${var}->save())"})

        # 2. EXTERNAL SOAP APIS
        if "SoapClient" in content or "soap" in content.lower() or "wsdl" in content.lower():
            soap_urls = re.findall(r'["\'](https?://[^"\'\s]+\.wsdl|https?://[^"\'\s]+soap[^"\'\s]*)["\']', content, re.IGNORECASE)
            if not soap_urls and "CUSTOM_CFG_SIEBEL_URL" in content:
                soap_urls = ["SIEBEL_SOAP_ENDPOINT (CUSTOM_CFG_SIEBEL_URL)"]

            for surl in (soap_urls or ["SOAP Web Service"]):
                external_soap_apis.append({
                    "protocol": "SOAP 1.1 / 1.2",
                    "endpoint": surl,
                    "action": "SOAP Web Service Request"
                })
                external_calls.append(f"SOAP Service: {surl}")
                flow_steps.append({"stage": "External SOAP", "action": f"Invoke SOAP Service ({surl})"})

        if "xml_parse_into_struct" in content or "php://input" in content:
            external_soap_apis.append({
                "protocol": "XML Payload Ingestion",
                "endpoint": "php://input",
                "action": "Parse Incoming XML Payload"
            })
            flow_steps.append({"stage": "Ingestion", "action": "Receive & Parse XML POST Payload"})

        # 3. EXTERNAL REST APIS
        if "curl_init" in content or "curl_exec" in content:
            curl_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
            clean_urls = [u for u in curl_urls if "schemas/dbaudit" not in u and "rightnow.com" not in u]

            method_match = re.search(r'CURLOPT_CUSTOMREQUEST\s*,\s*["\'](\w+)["\']', content)
            http_method = method_match.group(1) if method_match else "POST/GET"

            if clean_urls:
                for curl_url in set(clean_urls):
                    external_rest_apis.append({
                        "protocol": "REST / HTTP",
                        "method": http_method,
                        "endpoint": curl_url,
                        "details": f"cURL {http_method} request"
                    })
                    urls.append(curl_url)
                    external_calls.append(f"REST cURL {http_method}: {curl_url}")
                    flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} call -> {curl_url}"})
            else:
                external_rest_apis.append({
                    "protocol": "REST / HTTP",
                    "method": http_method,
                    "endpoint": "Dynamic / Configured REST Endpoint",
                    "details": f"cURL {http_method} request via Configuration"
                })
                external_calls.append("cURL REST Client Invocation")
                flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} HTTP Request"})

        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        for u in set(raw_urls):
            if "schemas/dbaudit" not in u and "rightnow.com" not in u and u not in urls:
                urls.append(u)

        route_matches = re.findall(r'public\s+function\s+(action\w+)\s*\(', content, re.IGNORECASE)
        for route in route_matches:
            clean_route = route[6:].lower() if route.lower().startswith("action") else route.lower()
            exposed_routes.append(clean_route)

    # ── JS Parsing ─────────────────────────────────────────────────────────
    elif ext == ".js":
        es6_imports = re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content)
        commonjs_imports = re.findall(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        imports = sorted(list(set(es6_imports + commonjs_imports)))

        if "fetch(" in content or re.search(r'fetch\s*\(', content):
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "fetch API",
                "endpoint": "Asynchronous REST Fetch",
                "details": "JS Fetch API call"
            })
            external_calls.append("JS Fetch REST API call")
            flow_steps.append({"stage": "External REST", "action": "JS Fetch API request"})

        if "$.ajax" in content or "$.get" in content or "$.post" in content:
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "jQuery AJAX",
                "endpoint": "AJAX HTTP Request",
                "details": "jQuery AJAX request"
            })
            external_calls.append("jQuery AJAX request")
            flow_steps.append({"stage": "External REST", "action": "jQuery AJAX request"})

        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        urls = sorted(list(set(raw_urls)))

        if "RightNow" in content or "RightNow.Action" in content:
            osvc_objects.append("RightNow Client Framework")
            internal_apis.append({
                "type": "Client Framework",
                "detail": "RightNow Client JS Framework Action",
                "operation": "UI Event Handler"
            })

    # Hardcoded credentials check
    cred_patterns = [
        (r'initConnectAPI\s*\(\s*["\']([^"\'\$]+)["\']\s*,\s*["\']([^"\'\$]+)["\']\s*\)', "Hardcoded ConnectAPI Credentials"),
        (r'CURLOPT_USERPWD\s*,\s*["\']([^"\'\$]+)["\']', "Hardcoded cURL Basic Auth Credentials"),
        (r'(?:password|passwd|pwd|secret|key|api_key|token|auth)\s*[:=]\s*["\']([^"\'\$]+)["\']', "Hardcoded Variable Credentials")
    ]
    for pattern, cred_label in cred_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    user_val, pass_val = match[0], match[1]
                    risk_flags.append({
                        "type": "Hardcoded Credential",
                        "detail": f"{cred_label}: User '{user_val}' with plaintext password"
                    })
                else:
                    if len(match.strip()) > 3:
                        risk_flags.append({
                            "type": "Hardcoded Credential",
                            "detail": f"{cred_label}: '{match.strip()}'"
                        })

    # ── HTML & JavaScript Extraction for Live Previews ─────────────────────
    has_html = False
    has_js = False
    html_snippets = []
    js_snippets = []

    if ext == ".js":
        has_js = True
        js_snippets.append(content[:4000])

    elif ext == ".php":
        script_blocks = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content, re.IGNORECASE)
        for sb in script_blocks:
            if sb.strip():
                has_js = True
                js_snippets.append(sb.strip())

        if not has_js and any(k in content for k in ["document.getElementById", "window.", "function()", "$.ajax", "jQuery("]):
            has_js = True

        echo_html_matches = re.findall(r'(?:echo|print)\s*["\']\s*(<(?:div|table|tr|td|th|form|p|span|input|button|h\d)[\s\S]*?>[\s\S]*?)["\'];', content, re.IGNORECASE)
        for eh in echo_html_matches:
            has_html = True
            clean_eh = re.sub(r'\.\s*\$[a-zA-Z0-9_]+(?:\-\>[a-zA-Z0-9_]+)*\s*\.', ' [Dynamic] ', eh)
            clean_eh = re.sub(r'\"\.([^\"]+)\.\"', ' [Dynamic] ', clean_eh)
            html_snippets.append(clean_eh.strip())

        heredocs = re.findall(r'<<<\s*HTML([\s\S]*?)HTML;', content)
        for hd in heredocs:
            has_html = True
            html_snippets.append(hd.strip())

        clean_php = re.sub(r'<\?php[\s\S]*?\?>', '', content, flags=re.IGNORECASE)
        clean_php = re.sub(r'<\?[\s\S]*?\?>', '', clean_php)
        if clean_php.strip() and ("<div" in clean_php or "<table" in clean_php or "<html" in clean_php or "<span" in clean_php or "<form" in clean_php):
            has_html = True
            html_snippets.append(clean_php.strip())

def generate_js_behavioral_summary(script_name, js_content):
    """
    Generates a natural language summary of client-side JavaScript behaviors
    without dumping raw source code into reports.
    """
    if not js_content:
        return []
    behaviors = []
    if "DataTable" in js_content or "jquery.dataTables" in js_content:
        behaviors.append("Initializes interactive DataTables grid formatting for thumbnail & search results display.")
    if "extension_loader" in js_content or "registerWorkspaceExtension" in js_content:
        behaviors.append("Registers BUI Extension Loader hooks (`ORACLE_SERVICE_CLOUD.extension_loader`) and binds workspace record events.")
    if "addFieldValueListener" in js_content or "fieldValueListener" in js_content:
        behaviors.append("Attaches dynamic workspace field value change listeners to trigger real-time search and validation as fields are edited.")
    if "triggerNamedEvent" in js_content:
        behaviors.append("Fires custom workspace named events (`focusDuplicateTab` / `hideDuplicateTab`) to dynamically toggle console tab visibility.")
    if "openContact" in js_content or "insertRow" in js_content:
        behaviors.append("Dynamically constructs HTML table rows and inserts clickable contact selection links into DOM container elements.")
    if "arcgis" in js_content.lower() or "esri" in js_content.lower():
        behaviors.append("Loads ArcGIS JavaScript API components for map rendering and geocoding coordinate selection.")
    if "fetch(" in js_content or "$.ajax" in js_content or "$.get" in js_content or "$.post" in js_content:
        behaviors.append("Issues asynchronous client-side HTTP AJAX / REST requests to communicate with server controllers.")

    if not behaviors:
        behaviors.append("Executes client-side UI manipulation and DOM event handling logic.")

    return behaviors

def parse_script_file(file_path):
    """
    Statically analyzes custom scripts (PHP or JS) to map dependencies, object usage,
    and 3 categorized API types (Internal ROQL/Connect, External SOAP, External REST)
    along with flow execution steps for Mermaid sequence diagrams.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Script file not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_name = os.path.basename(file_path)
    script_type = "Unknown"
    
    normalized_path = file_path.replace("\\", "/").lower()
    if "widget" in normalized_path:
        script_type = "Widget Component"
    elif "controller" in normalized_path or "class " in content and "controller" in content.lower():
        script_type = "Controller Endpoint"
    elif "model" in normalized_path:
        script_type = "Model Helper"
    elif ext == ".js":
        script_type = "Client-side Script"
    elif ext == ".php":
        script_type = "Server-side Utility"

    imports = []
    osvc_objects = []
    external_calls = []
    urls = []
    exposed_routes = []
    risk_flags = []

    # 3 Categorized API Structures
    internal_apis = []
    external_soap_apis = []
    external_rest_apis = []
    flow_steps = []

    # ── PHP Parsing ────────────────────────────────────────────────────────
    if ext == ".php":
        import_matches = re.findall(r'(?:require|include)(?:_once)?\s*\(?\s*["\']([^"\'\(\)]+?)["\']\s*\)?', content, re.IGNORECASE)
        imports = sorted(list(set(import_matches)))

        osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\(\w+)', content))))

        # 1. INTERNAL APIS
        roql_queries = re.findall(r'["\'](SELECT[\s\S]*?FROM[\s\S]*?)["\']', content, re.IGNORECASE)
        for q in roql_queries:
            clean_q = " ".join(q.split())
            internal_apis.append({
                "type": "ROQL Query",
                "detail": clean_q,
                "operation": "SELECT Query"
            })
            flow_steps.append({"stage": "Internal DB", "action": f"Execute ROQL Query: {clean_q[:60]}..."})

        fetch_matches = re.findall(r'RNCPHP\\(\w+)::fetch\(([^)]*)\)', content)
        for obj, args in fetch_matches:
            internal_apis.append({
                "type": "Connect PHP Fetch",
                "detail": f"RNCPHP\\{obj}::fetch({args.strip()})",
                "operation": f"Fetch {obj}"
            })
            flow_steps.append({"stage": "Internal API", "action": f"Fetch {obj} instance ({args.strip()})"})

        if "AgentAuthenticator::authenticateSessionID" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateSessionID($session_id)",
                "operation": "Validate Agent Session"
            })
            flow_steps.append({"stage": "Authentication", "action": "Validate Agent Session ID"})

        if "AgentAuthenticator::authenticateCredentials" in content:
            internal_apis.append({
                "type": "Agent Authenticator",
                "detail": "AgentAuthenticator::authenticateCredentials($username, $password)",
                "operation": "Validate Agent Credentials"
            })
            flow_steps.append({"stage": "Authentication", "action": "Authenticate Agent Credentials"})

        if "save()" in content:
            save_objs = re.findall(r'\$(\w+)->save\(\)', content)
            for var in set(save_objs):
                internal_apis.append({
                    "type": "Connect PHP Save",
                    "detail": f"${var}->save()",
                    "operation": f"Commit changes to {var}"
                })
                flow_steps.append({"stage": "Internal API", "action": f"Commit record changes (${var}->save())"})

        # 2. EXTERNAL SOAP APIS
        if "SoapClient" in content or "soap" in content.lower() or "wsdl" in content.lower():
            soap_urls = re.findall(r'["\'](https?://[^"\'\s]+\.wsdl|https?://[^"\'\s]+soap[^"\'\s]*)["\']', content, re.IGNORECASE)
            if not soap_urls and "CUSTOM_CFG_SIEBEL_URL" in content:
                soap_urls = ["SIEBEL_SOAP_ENDPOINT (CUSTOM_CFG_SIEBEL_URL)"]

            for surl in (soap_urls or ["SOAP Web Service"]):
                external_soap_apis.append({
                    "protocol": "SOAP 1.1 / 1.2",
                    "endpoint": surl,
                    "action": "SOAP Web Service Request"
                })
                external_calls.append(f"SOAP Service: {surl}")
                flow_steps.append({"stage": "External SOAP", "action": f"Invoke SOAP Service ({surl})"})

        if "xml_parse_into_struct" in content or "php://input" in content:
            external_soap_apis.append({
                "protocol": "XML Payload Ingestion",
                "endpoint": "php://input",
                "action": "Parse Incoming XML Payload"
            })
            flow_steps.append({"stage": "Ingestion", "action": "Receive & Parse XML POST Payload"})

        # 3. EXTERNAL REST APIS
        if "curl_init" in content or "curl_exec" in content:
            curl_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
            clean_urls = [u for u in curl_urls if "schemas/dbaudit" not in u and "rightnow.com" not in u]

            method_match = re.search(r'CURLOPT_CUSTOMREQUEST\s*,\s*["\'](\w+)["\']', content)
            http_method = method_match.group(1) if method_match else "POST/GET"

            if clean_urls:
                for curl_url in set(clean_urls):
                    external_rest_apis.append({
                        "protocol": "REST / HTTP",
                        "method": http_method,
                        "endpoint": curl_url,
                        "details": f"cURL {http_method} request"
                    })
                    urls.append(curl_url)
                    external_calls.append(f"REST cURL {http_method}: {curl_url}")
                    flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} call -> {curl_url}"})
            else:
                external_rest_apis.append({
                    "protocol": "REST / HTTP",
                    "method": http_method,
                    "endpoint": "Dynamic / Configured REST Endpoint",
                    "details": f"cURL {http_method} request via Configuration"
                })
                external_calls.append("cURL REST Client Invocation")
                flow_steps.append({"stage": "External REST", "action": f"cURL {http_method} HTTP Request"})

        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        for u in set(raw_urls):
            if "schemas/dbaudit" not in u and "rightnow.com" not in u and u not in urls:
                urls.append(u)

        route_matches = re.findall(r'public\s+function\s+(action\w+)\s*\(', content, re.IGNORECASE)
        for route in route_matches:
            clean_route = route[6:].lower() if route.lower().startswith("action") else route.lower()
            exposed_routes.append(clean_route)

    # ── JS Parsing ─────────────────────────────────────────────────────────
    elif ext == ".js":
        es6_imports = re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content)
        commonjs_imports = re.findall(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        imports = sorted(list(set(es6_imports + commonjs_imports)))

        if "fetch(" in content or re.search(r'fetch\s*\(', content):
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "fetch API",
                "endpoint": "Asynchronous REST Fetch",
                "details": "JS Fetch API call"
            })
            external_calls.append("JS Fetch REST API call")
            flow_steps.append({"stage": "External REST", "action": "JS Fetch API request"})

        if "$.ajax" in content or "$.get" in content or "$.post" in content:
            external_rest_apis.append({
                "protocol": "REST / HTTP",
                "method": "jQuery AJAX",
                "endpoint": "AJAX HTTP Request",
                "details": "jQuery AJAX request"
            })
            external_calls.append("jQuery AJAX request")
            flow_steps.append({"stage": "External REST", "action": "jQuery AJAX request"})

        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        urls = sorted(list(set(raw_urls)))

        if "RightNow" in content or "RightNow.Action" in content:
            osvc_objects.append("RightNow Client Framework")
            internal_apis.append({
                "type": "Client Framework",
                "detail": "RightNow Client JS Framework Action",
                "operation": "UI Event Handler"
            })

    # Hardcoded credentials check
    cred_patterns = [
        r'(?:password|passwd|pwd|secret|key|api_key|token|auth)\s*[:=]\s*["\']([^"\'\$]+)["\']',
    ]
    for pattern in cred_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        valid_creds = [m for m in matches if len(m.strip()) > 3]
        if valid_creds:
            risk_flags.append({
                "type": "Hardcoded Credential",
                "detail": f"Potential credentials found in variable assignments (count: {len(valid_creds)})"
            })

    # ── HTML & JavaScript Extraction for Live Previews ─────────────────────
    has_html = False
    has_js = False
    html_snippets = []
    js_snippets = []

    if ext == ".js":
        has_js = True
        js_snippets.append(content[:4000])

    elif ext == ".php":
        script_blocks = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content, re.IGNORECASE)
        for sb in script_blocks:
            if sb.strip():
                has_js = True
                js_snippets.append(sb.strip())

        if not has_js and any(k in content for k in ["document.getElementById", "window.", "function()", "$.ajax", "jQuery("]):
            has_js = True

        echo_html_matches = re.findall(r'(?:echo|print)\s*["\']\s*(<(?:div|table|tr|td|th|form|p|span|input|button|h\d)[\s\S]*?>[\s\S]*?)["\'];', content, re.IGNORECASE)
        for eh in echo_html_matches:
            has_html = True
            clean_eh = re.sub(r'\.\s*\$[a-zA-Z0-9_]+(?:\-\>[a-zA-Z0-9_]+)*\s*\.', ' [Dynamic] ', eh)
            clean_eh = re.sub(r'\"\.([^\"]+)\.\"', ' [Dynamic] ', clean_eh)
            html_snippets.append(clean_eh.strip())

        heredocs = re.findall(r'<<<\s*HTML([\s\S]*?)HTML;', content)
        for hd in heredocs:
            has_html = True
            html_snippets.append(hd.strip())

        clean_php = re.sub(r'<\?php[\s\S]*?\?>', '', content, flags=re.IGNORECASE)
        clean_php = re.sub(r'<\?[\s\S]*?\?>', '', clean_php)
        if clean_php.strip() and ("<div" in clean_php or "<table" in clean_php or "<html" in clean_php or "<span" in clean_php or "<form" in clean_php):
            has_html = True
            html_snippets.append(clean_php.strip())

    full_html = "\n\n".join(html_snippets) if html_snippets else ""
    full_js = "\n\n".join(js_snippets) if js_snippets else ""

    summary = generate_script_summary(script_name, content, internal_apis, external_soap_apis, external_rest_apis, osvc_objects, flow_steps)
    js_behaviors = generate_js_behavioral_summary(script_name, full_js)

    return {
        "file_name": script_name,
        "script_type": script_type,
        "summary": summary,
        "imports": imports,
        "report_ids": report_ids if 'report_ids' in locals() else [],
        "osvc_objects": osvc_objects,
        "external_calls": external_calls,
        "urls": urls,
        "exposed_routes": exposed_routes,
        "risk_flags": risk_flags,
        "internal_apis": internal_apis,
        "external_soap_apis": external_soap_apis,
        "external_rest_apis": external_rest_apis,
        "flow_steps": flow_steps,
        "has_html": has_html,
        "has_js": has_js,
        "js_behaviors": js_behaviors,
        "html_content": full_html[:6000],
        "js_content": full_js[:6000],
        "unhandled_elements": [],
        "unknowns": {
            "unknown_attrs": [],
            "unknown_children": []
        }
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_script_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python script_parser.py <path_to_script_file>")
