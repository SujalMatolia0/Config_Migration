import os
import re

def parse_script_file(file_path):
    """
    Statically analyzes custom scripts (PHP or JS) to map dependencies, object usage, and routes.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Script file not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    script_name = os.path.basename(file_path)
    script_type = "Unknown"
    
    # Simple heuristics to identify script type based on path/content
    normalized_path = file_path.replace("\\", "/").lower()
    if "widget" in normalized_path:
        script_type = "Widget Component"
    elif "controller" in normalized_path or "class " in content and "controller" in content.lower():
        script_type = "Controller Endpoint"
    elif "model" in normalized_path:
        script_type = "Model helper"
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

    # PHP parsing
    if ext == ".php":
        # Find imports: require, include, require_once, include_once
        import_matches = re.findall(r'(?:require|include)(?:_once)?\s*\(?\s*["\']([^"\'\(\)]+?)["\']\s*\)?', content, re.IGNORECASE)
        imports = sorted(list(set(import_matches)))

        # Find OSVC objects
        osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\(\w+)', content))))

        # Find external calls (curl, file_get_contents)
        if "curl_init" in content or "curl_exec" in content:
            external_calls.append("cURL client invocation")
        if re.search(r'file_get_contents\s*\(\s*["\']https?://', content):
            external_calls.append("file_get_contents HTTP request")

        # Hardcoded URLs
        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        urls = sorted(list(set([u for u in raw_urls if "schemas/dbaudit" not in u and "rightnow.com" not in u])))

        # Exposed routes/endpoints (for controllers, methods starting with action...)
        route_matches = re.findall(r'public\s+function\s+(action\w+)\s*\(', content, re.IGNORECASE)
        for route in route_matches:
            # actionIndex -> index
            clean_route = route[6:].lower() if route.lower().startswith("action") else route.lower()
            exposed_routes.append(clean_route)

    # JS parsing
    elif ext == ".js":
        # Find imports: ES6 import or CommonJS require
        es6_imports = re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', content)
        commonjs_imports = re.findall(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        imports = sorted(list(set(es6_imports + commonjs_imports)))

        # Look for fetch/AJAX external calls
        if "fetch(" in content or re.search(r'fetch\s*\(', content):
            external_calls.append("fetch API call")
        if "$.ajax" in content or "$.get" in content or "$.post" in content:
            external_calls.append("jQuery AJAX request")
        if "axios." in content:
            external_calls.append("Axios HTTP request")

        # Hardcoded URLs in JS
        raw_urls = re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content)
        urls = sorted(list(set(raw_urls)))

        # In JS we can check for OSVC Client side framework references
        if "RightNow" in content or "RightNow.Action" in content:
            osvc_objects.append("RightNow Client Framework")

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
                "detail": f"Potential credentials found in variable assignments (length: {len(valid_creds)})"
            })

    return {
        "file_name": script_name,
        "script_type": script_type,
        "imports": imports,
        "osvc_objects": osvc_objects,
        "external_calls": external_calls,
        "urls": urls,
        "exposed_routes": exposed_routes,
        "risk_flags": risk_flags
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_script_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python script_parser.py <path_to_script_file>")
