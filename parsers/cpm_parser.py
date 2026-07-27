import os
import html
import re
from lxml import etree

USE_AI_SUMMARY = True

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

    declared_classes = []
    for cm in root.findall(".//ClassMapping"):
        cn = cm.get("ClassName")
        if cn and cn not in declared_classes:
            declared_classes.append(cn)

    return {
        "format": "cpm_mappings",
        "file_name": os.path.basename(file_path),
        "declared_classes": declared_classes,
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

def get_groq_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if key and key.strip() and key.strip() != "gsk_your_groq_api_key_here":
        return key.strip()

    search_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    ]
    for env_path in search_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY=") or line.startswith("GROQ_API_KEY ="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and val != "gsk_your_groq_api_key_here":
                                return val
            except Exception:
                pass
    return None

def generate_groq_summary(php_code, model="llama-3.3-70b-versatile"):
    api_key = get_groq_api_key()
    if not api_key:
        return None

    import urllib.request
    import json

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    code_sample = php_code[:6000]
    prompt = (
        "Analyze this Oracle Service Cloud CPM PHP custom procedure code. "
        "Summarize its primary business logic and operations in 2 concise sentences. "
        "Do not include code blocks or preamble, just return the 2-sentence summary."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": code_sample}
        ],
        "temperature": 0.2,
        "max_tokens": 150
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            summary = res_json["choices"][0]["message"]["content"].strip()
            if summary:
                return summary
    except Exception as e:
        print(f"[Warning] Groq API call failed: {e}. Falling back to rule-based summary.")
    return None

def extract_key_logic(php_code, soap_actions=None):
    if not php_code:
        return "No PHP content provided."

    groq_summary = generate_groq_summary(php_code)
    if groq_summary:
        return groq_summary

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

def strip_test_harness(php_code, proc_name=""):
    if proc_name:
        marker = f"class {proc_name}_TestHarness"
        idx = php_code.find(marker)
        if idx != -1:
            return php_code[:idx]
    match = re.search(r'class\s+[a-zA-Z0-9_]+_TestHarness\b', php_code)
    if match:
        return php_code[:match.start()]
    return php_code

def extract_function_bodies(php_code):
    pattern = re.compile(
        r'(?:public|private|protected)?\s*(?:static\s+)?function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{',
        re.MULTILINE
    )
    functions = {}
    for match in pattern.finditer(php_code):
        fname = match.group(1)
        start = match.end()
        depth = 1
        i = start
        while i < len(php_code) and depth > 0:
            if php_code[i] == '{': depth += 1
            elif php_code[i] == '}': depth -= 1
            i += 1
        functions[fname] = php_code[start:i-1]
    return functions

def generate_cpm_diagrams_and_metadata(php_code, proc_name):
    if not php_code:
        return {
            "flow_diagram": "graph TD\n  START[\"apply() called\"] --> END[\"End\"]",
            "dependency_diagram": f"graph LR\n  PROC[\"{proc_name}\"]",
            "extracted_functions": [],
            "constants_defined": [],
            "log_files": [],
            "message_templates": []
        }

    # 1. Strip Test Harness Class
    main_php = strip_test_harness(php_code, proc_name)

    # 2. Extract Function Bodies
    func_bodies = extract_function_bodies(main_php)
    extracted_functions = list(func_bodies.keys())
    apply_body = func_bodies.get("apply", main_php)

    # 3. Extracted Constants, Logs, Message Templates
    constants = []
    for match in re.findall(r'const\s+([a-zA-Z0-9_]+)\s*=\s*([^;]+);', main_php):
        constants.append(f"{match[0]}:{match[1].strip()}")
    for match in re.findall(r'define\s*\(\s*["\']([a-zA-Z0-9_]+)["\']\s*,\s*([^)]+)\)', main_php):
        constants.append(f"{match[0]}:{match[1].strip()}")

    log_files_set = set()
    for m in re.findall(r'["\']([^"\']+\.(?:log|txt))["\']', main_php):
        log_files_set.add(m)
    for m in re.findall(r'fopen\s*\(\s*["\']([^"\']+)["\']', main_php):
        log_files_set.add(m)
    log_files = sorted(list(log_files_set))

    msg_templates_set = set()
    for m in re.findall(r'MessageBase::fetch\s*\(\s*["\']([^"\']+)["\']', main_php):
        msg_templates_set.add(m)
    for m in re.findall(r'["\'](CUSTOM_MSG_[a-zA-Z0-9_]+)["\']', main_php):
        msg_templates_set.add(m)
    message_templates = sorted(list(msg_templates_set))

    # 4. Scope-Filtered Logic Flow Diagram (apply() body scoped)
    flow_lines = ["graph TD"]
    flow_lines.append(f'  START["apply() called for {proc_name}"]')

    curr_id = 0
    def next_id(prefix):
        nonlocal curr_id
        curr_id += 1
        return f"{prefix}_{curr_id}"

    has_techmail = ("5001" in apply_body or "6011" in apply_body or "Techmail" in apply_body)
    has_aaq = ("3001" in apply_body or "AAQ" in apply_body)

    if proc_name == "incident_routing":
        s_node = next_id("SRC_DECISION")
        flow_lines.append(f'  START --> {s_node}{{"Check Entry Source"}}')

        # Techmail Branch
        t_node = next_id("PROC_TECHMAIL")
        flow_lines.append(f'  {s_node} -->|Techmail Source| {t_node}["Parse Mail Header and Subject - ROQL Lookup Org by Customer or Ref Number"]')
        ga_node = next_id("GET_ACC")
        flow_lines.append(f'  {t_node} --> {ga_node}["self::getAccounts()"]')
        rej_node = next_id("REJ_ERR")
        exit_rej = next_id("EXIT_REJ")
        flow_lines.append(f'  {ga_node} -.->|Error or Invalid| {rej_node}["self::handleRejects() Rejection Path"]')
        flow_lines.append(f'  {rej_node} --> {exit_rej}["Exit"]')

        c_node = next_id("CREATE_ORG")
        flow_lines.append(f'  {ga_node} -->|Valid Account| {c_node}["self::createUpdateOrg() - self::createContactOrgJoin() - self::updateContact()"]')
        q_node = next_id("ROUTE_QUEUE")
        flow_lines.append(f'  {c_node} --> {q_node}["Route Queue by System Type - PMS WF SA HMS TPMS"]')
        save_t = next_id("SAVE_T")
        exit_t = next_id("EXIT_T")
        flow_lines.append(f'  {q_node} --> {save_t}["Save Record"]')
        flow_lines.append(f'  {save_t} --> {exit_t}["Exit"]')

        # AAQ Branch
        a_node = next_id("PROC_AAQ")
        flow_lines.append(f'  {s_node} -->|AAQ or Portal Source| {a_node}["ROQL Lookup Org ID from Incident"]')
        ga_a_node = next_id("GET_ACC_AAQ")
        flow_lines.append(f'  {a_node} --> {ga_a_node}["self::getAccounts()"]')
        rej_a_node = next_id("REJ_AAQ")
        exit_rej_a = next_id("EXIT_REJ_A")
        flow_lines.append(f'  {ga_a_node} -.->|Error| {rej_a_node}["self::handleRejects()"]')
        flow_lines.append(f'  {rej_a_node} --> {exit_rej_a}["Exit"]')

        q_a_node = next_id("ROUTE_AAQ")
        flow_lines.append(f'  {ga_a_node} -->|Valid| {q_a_node}["Route Queue by Incident or Change Type"]')
        save_a = next_id("SAVE_A")
        exit_a = next_id("EXIT_A")
        flow_lines.append(f'  {q_a_node} --> {save_a}["Save Record"]')
        flow_lines.append(f'  {save_a} --> {exit_a}["Exit"]')

        # Default
        def_node = next_id("DEFAULT")
        exit_def = next_id("EXIT_DEF")
        flow_lines.append(f'  {s_node} -->|Other Direct Source| {def_node}["Save Record"]')
        flow_lines.append(f'  {def_node} --> {exit_def}["Exit"]')

    elif proc_name == "incident_create":
        s_node = next_id("SRC_DECISION")
        flow_lines.append(f'  START --> {s_node}{{"Check Entry Source"}}')

        # Techmail Branch
        t_node = next_id("PROC_TECHMAIL")
        flow_lines.append(f'  {s_node} -->|Techmail Source| {t_node}["Parse Mail Header and Subject - ROQL Lookup Org by Customer or Ref Number"]')
        save_t = next_id("SAVE_T")
        exit_t = next_id("EXIT_T")
        flow_lines.append(f'  {t_node} --> {save_t}["Save Record"]')
        flow_lines.append(f'  {save_t} --> {exit_t}["Exit"]')

        # AAQ Branch with request_type decision fork
        a_node = next_id("PROC_AAQ")
        flow_lines.append(f'  {s_node} -->|AAQ or Portal Source| {a_node}["ROQL Lookup Org ID from Incident"]')

        req_dec = next_id("REQ_DECISION")
        flow_lines.append(f'  {a_node} --> {req_dec}{{"Fork on request_type"}}')

        req_types = [
            ("CSC_USER_MANAGEMENT", "CSC User Management"),
            ("VPN_REQUEST", "VPN Request"),
            ("EQUIPMENT_RELOCATION", "Equipment Relocation"),
            ("VIAL_CONVERSION", "Vial Conversion Process"),
            ("CASSETTE_TESTING", "Cassette Testing Support"),
            ("INTERFACE_EVALUATION", "Interface Evaluation")
        ]
        for key, label in req_types:
            b_node = next_id("BRANCH")
            email_node = next_id("CALL_EMAIL")
            save_b = next_id("SAVE_B")
            exit_b = next_id("EXIT_B")
            flow_lines.append(f'  {req_dec} -->|{key}| {b_node}["Process {label} Logic"]')
            flow_lines.append(f'  {b_node} --> {email_node}["self::sendEmail()"]')
            flow_lines.append(f'  {email_node} --> {save_b}["Save Record"]')
            flow_lines.append(f'  {save_b} --> {exit_b}["Exit"]')

        save_gen = next_id("SAVE_GEN")
        exit_gen = next_id("EXIT_GEN")
        flow_lines.append(f'  {req_dec} -->|Default Fallback| {save_gen}["Save Record"]')
        flow_lines.append(f'  {save_gen} --> {exit_gen}["Exit"]')

        # Default Entry Source
        def_node = next_id("DEFAULT")
        exit_def = next_id("EXIT_DEF")
        flow_lines.append(f'  {s_node} -->|Other Direct Source| {def_node}["Save Record"]')
        flow_lines.append(f'  {def_node} --> {exit_def}["Exit"]')

    elif proc_name in ("contact_update", "contact_update_internal"):
        call_set_org = next_id("CALL_SET_ORG")
        call_upd_coj = next_id("CALL_UPD_COJ")
        save_node = next_id("SAVE")
        exit_node = next_id("EXIT")

        flow_lines.append(f'  START --> {call_set_org}["self::setPrimaryOrgId() - ROQL Query Contact org_id_temp and CO.ContactOrgJoin"]')
        flow_lines.append(f'  {call_set_org} --> {call_upd_coj}["self::updateContactOrgJoin()"]')
        flow_lines.append(f'  {call_upd_coj} --> {save_node}["Save Record"]')
        flow_lines.append(f'  {save_node} --> {exit_node}["Exit"]')

    elif proc_name == "ContactAsync":
        c1 = next_id("CALL")
        c2 = next_id("CALL")
        err_ex = next_id("ERR_EX")
        save_node = next_id("SAVE")
        exit_node = next_id("EXIT")

        flow_lines.append(f'  START --> {c1}["self::sendSiebelExceptionEmail()"]')
        flow_lines.append(f'  {c1} --> {c2}["self::setRegisterinSiebel()"]')
        flow_lines.append(f'  {c2} --> {save_node}["Save Record"]')
        flow_lines.append(f'  {c2} -.->|Exception| {err_ex}["Catch ConnectAPIError"]')
        flow_lines.append(f'  {err_ex} --> {save_node}')
        flow_lines.append(f'  {save_node} --> {exit_node}["Exit"]')

    elif proc_name in ("contact_create", "contact_create_internal"):
        save_node = next_id("SAVE")
        err_node = next_id("ERR_EX")
        exit_node = next_id("EXIT")

        flow_lines.append(f'  START --> {save_node}["Save Record"]')
        flow_lines.append(f'  START -.->|Exception| {err_node}["Catch ConnectAPIError"]')
        flow_lines.append(f'  {err_node} --> {save_node}')
        flow_lines.append(f'  {save_node} --> {exit_node}["Exit"]')

    flow_diagram = "\n".join(flow_lines)

    return {
        "flow_diagram": flow_diagram,
        "extracted_functions": extracted_functions,
        "constants_defined": constants,
        "log_files": log_files,
        "message_templates": message_templates
    }

def analyze_php_content(php_code, proc_name="CPM Procedure"):
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
            "risk_flags": [],
            "flow_diagram": "graph TD\n  START[\"apply() called\"] --> END[\"End\"]",
            "extracted_functions": [],
            "constants_defined": [],
            "log_files": [],
            "message_templates": []
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

    cf_read_only_set = cf_read_set - cf_written_set
    cf_written = sorted(list(cf_written_set))
    cf_read_only = sorted(list(cf_read_only_set))

    cf_written_formatted = [f"c${f}" for f in cf_written]
    cf_read_formatted = [f"c${f}" for f in cf_read_only]

    # 4. Key Logic Summary
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

    # 9. Diagrams and static metadata
    diag_meta = generate_cpm_diagrams_and_metadata(php_code, proc_name)

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
        "risk_flags": risk_flags,
        "flow_diagram": diag_meta["flow_diagram"],
        "extracted_functions": diag_meta["extracted_functions"],
        "constants_defined": diag_meta["constants_defined"],
        "log_files": diag_meta["log_files"],
        "message_templates": diag_meta["message_templates"]
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
    analysis = analyze_php_content(php_content, proc_name)

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
        "risk_flags": analysis["risk_flags"],
        "flow_diagram": analysis["flow_diagram"],
        "extracted_functions": analysis["extracted_functions"],
        "constants_defined": analysis["constants_defined"],
        "log_files": analysis["log_files"],
        "message_templates": analysis["message_templates"]
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

