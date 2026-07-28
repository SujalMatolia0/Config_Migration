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

    return {
        "file_name": script_name,
        "script_type": script_type,
        "imports": imports,
        "osvc_objects": osvc_objects,
        "external_calls": external_calls,
        "urls": urls,
        "exposed_routes": exposed_routes,
        "risk_flags": risk_flags,
        "internal_apis": internal_apis,
        "external_soap_apis": external_soap_apis,
        "external_rest_apis": external_rest_apis,
        "flow_steps": flow_steps
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_script_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python script_parser.py <path_to_script_file>")
