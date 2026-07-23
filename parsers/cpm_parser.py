import os
import re

def parse_cpm_file(file_path):
    """
    Statically analyzes an OSVC CPM PHP file to extract metadata, references, and risk flags.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CPM file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # 1. Extract Class Name
    class_match = re.search(r'class\s+(\w+)', content, re.IGNORECASE)
    class_name = class_match.group(1) if class_match else None

    # 2. Identify Hooks Implemented
    hooks = []
    # Standard hook names: pre_process, post_process, validate
    for hook in ["pre_process", "post_process", "validate"]:
        if re.search(rf'function\s+{hook}\s*\(', content, re.IGNORECASE):
            hooks.append(hook)

    # 3. Connect PHP Object References
    # e.g., RNCPHP\Contact, RNCPHP\Incident
    osvc_objects = sorted(list(set(re.findall(r'RNCPHP\\(\w+)', content))))

    query_calls = []
    # Match query statements e.g., ConnectAPI::query("...") or Connect::query("...")
    queries = re.findall(r'(Connect(?:API)?::query\s*\(\s*["\'](.+?)["\']\s*\))', content, re.DOTALL)
    for match, q_str in queries:
        # Clean up whitespace inside query
        cleaned_query = " ".join(q_str.split())
        query_calls.append(cleaned_query)

    # Also catch variable-based query calls e.g., Connect::query($q)
    var_queries = re.findall(r'Connect(?:API)?::query\s*\(\s*\$(\w+)\s*\)', content)
    for var in var_queries:
        query_calls.append(f"[dynamic query via variable: ${var}]")

    # 5. External Endpoints (curl_setopt, file_get_contents, hardcoded URLs)
    external_calls = []
    
    # Check for curl use
    has_curl = False
    if "curl_init" in content or "curl_exec" in content:
        has_curl = True
        external_calls.append("cURL client invocation")
        
    # Check file_get_contents on URLs
    if re.search(r'file_get_contents\s*\(\s*["\']https?://', content):
        external_calls.append("file_get_contents HTTP request")

    # Hardcoded URLs
    urls = sorted(list(set(re.findall(r'["\'](https?://[a-zA-Z0-9_\-\.\/\?&\=\+\%]+)["\']', content))))
    # Filter out standard Oracle/RightNow schemas if they look like namespaces or help URLs
    filtered_urls = [u for u in urls if "schemas/dbaudit" not in u and "rightnow.com" not in u]

    # 6. Hardcoded Credentials / Risk Flags
    risk_flags = []
    
    # Look for assignment of credentials
    # e.g., $password = "abc"; $secret = 'xyz'; $apiKey = "foo";
    cred_patterns = [
        r'\$(?:password|passwd|pwd|secret|key|api_key|token|auth)\s*=\s*["\']([^"\'\$]+)["\']',
    ]
    for pattern in cred_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # Avoid matching empty strings or tiny strings
        valid_creds = [m for m in matches if len(m.strip()) > 3]
        if valid_creds:
            risk_flags.append({
                "type": "Hardcoded Credential",
                "detail": f"Potential credentials found in variable assignments (length: {len(valid_creds)})"
            })

    # Look for error suppression in curl or queries
    if has_curl and ("CURLOPT_FAILONERROR" not in content and "CURLOPT_RETURNTRANSFER" not in content):
        risk_flags.append({
            "type": "CURL Configuration Risk",
            "detail": "cURL call does not check for errors explicitly"
        })

    return {
        "file_name": os.path.basename(file_path),
        "class_name": class_name,
        "hooks": hooks,
        "osvc_objects": osvc_objects,
        "query_calls": query_calls,
        "external_calls": external_calls,
        "urls": filtered_urls,
        "risk_flags": risk_flags
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_cpm_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python cpm_parser.py <path_to_cpm_php>")
