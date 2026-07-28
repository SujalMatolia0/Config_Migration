import re

OSVC_TABLE_TO_OBJECT = {
    "contacts": "Contact",
    "incidents": "Incident",
    "opportunities": "Opportunity",
    "organizations": "Organization",
    "org": "Organization",
    "tasks": "Task",
    "chats": "Chat",
    "assets": "Asset",
    "interactions": "Interaction",
    "accounts": "Account",
    "answers": "Answer",
    "sla_instances": None,
    "sss_users": None,
}

OSVC_FIELD_PREFIX_TO_OBJECT = {
    "Contact.": "Contact",
    "contact.": "Contact",
    "Incident.": "Incident",
    "incident.": "Incident",
    "Opportunity.": "Opportunity",
    "opportunity.": "Opportunity",
    "Organization.": "Organization",
    "organization.": "Organization",
    "org.": "Organization",
    "Org.": "Organization",
    "Task.": "Task",
    "task.": "Task",
    "Chat.": "Chat",
    "chat.": "Chat",
    "Asset.": "Asset",
    "asset.": "Asset",
    "Account.": "Account",
    "account.": "Account",
    "Answer.": "Answer",
    "answer.": "Answer"
}

def detect_workspace_object(ws: dict) -> list:
    obj = ws.get("type") or ws.get("ui_type")
    if not obj and ws.get("name"):
        name_lower = ws["name"].lower()
        for candidate in ["Contact", "Incident", "Opportunity", "Organization", "Task", "Chat", "Asset", "Account", "Answer"]:
            if candidate.lower() in name_lower:
                return [candidate]
    return [obj] if obj else ["Unknown"]

def detect_report_object(rep: dict) -> list:
    primary_table = rep.get("primary_table")
    if primary_table:
        osvc_obj = OSVC_TABLE_TO_OBJECT.get(primary_table.lower())
        if osvc_obj:
            return [osvc_obj]

    for table in rep.get("tables", []):
        if not table.get("join_type"):
            tbl_name = table.get("table_name") or table.get("name") or ""
            osvc_obj = OSVC_TABLE_TO_OBJECT.get(tbl_name.lower())
            if osvc_obj:
                return [osvc_obj]

    rep_name = (rep.get("name") or "").lower()
    for candidate in ["Contact", "Incident", "Opportunity", "Organization", "Task", "Chat", "Asset", "Account", "Answer"]:
        if candidate.lower() in rep_name:
            return [candidate]

    return ["Unknown"]

def detect_bui_object(bui: dict) -> list:
    objects = set()
    all_fields = (
        bui.get("osvc_fields_read", []) + 
        bui.get("osvc_fields_written", []) + 
        bui.get("fields_read", []) + 
        bui.get("fields_written", [])
    )
    for field in all_fields:
        f_str = str(field)
        for prefix, obj in OSVC_FIELD_PREFIX_TO_OBJECT.items():
            if f_str.startswith(prefix) or f_str.lower().startswith(prefix.lower()):
                objects.add(obj)

    if not objects and bui.get("name"):
        bname = bui["name"].lower()
        for candidate in ["Contact", "Incident", "Opportunity", "Organization", "Task", "Chat", "Asset", "Account", "Answer"]:
            if candidate.lower() in bname:
                objects.add(candidate)

    return list(objects) if objects else ["Unknown"]

def detect_cpm_object(cpm: dict) -> list:
    objects = set()
    if cpm.get("object"):
        objects.add(cpm["object"])
    
    bound_classes = cpm.get("bound_classes", [])
    for b in bound_classes:
        b_str = str(b)
        if "Contact" in b_str: objects.add("Contact")
        elif "Incident" in b_str: objects.add("Incident")
        elif "Opportunity" in b_str: objects.add("Opportunity")
        elif "Organization" in b_str or "Org" in b_str: objects.add("Organization")
        elif "Task" in b_str: objects.add("Task")

    osvc_objects = cpm.get("osvc_objects", [])
    for o in osvc_objects:
        o_str = str(o)
        if "Contact" in o_str: objects.add("Contact")
        elif "Incident" in o_str: objects.add("Incident")
        elif "Opportunity" in o_str: objects.add("Opportunity")
        elif "Organization" in o_str or "Org" in o_str: objects.add("Organization")
        elif "Task" in o_str: objects.add("Task")

    return list(objects) if objects else ["Unknown"]

def detect_custom_script_object(script: dict) -> list:
    objects = set()
    s_name = (script.get("file_name") or script.get("name") or "").lower()
    if any(k in s_name for k in ["contact", "call", "sms"]): objects.add("Contact")
    if any(k in s_name for k in ["incident", "note", "clock", "validation", "sr"]): objects.add("Incident")
    if any(k in s_name for k in ["org", "account", "siebel"]): objects.add("Organization")

    raw = (script.get("raw_code") or "").lower()
    if "contact" in raw or "rncphp\\contact" in raw: objects.add("Contact")
    if "incident" in raw or "rncphp\\incident" in raw: objects.add("Incident")
    if "organization" in raw or "rncphp\\organization" in raw: objects.add("Organization")

def detect_custom_object(co: dict) -> list:
    name = co.get("name") or co.get("label")
    return [name] if name else ["Unknown"]

def detect_component_object(component: dict, component_type: str) -> list:
    dispatch = {
        "workspace": detect_workspace_object,
        "report": detect_report_object,
        "bui_addin": detect_bui_object,
        "cpm": detect_cpm_object,
        "custom_script": detect_custom_script_object,
        "custom_object": detect_custom_object
    }
    fn = dispatch.get(component_type.lower())
    res = fn(component) if fn else ["Other"]
    return res if res else ["Other"]

def build_object_tree(all_components: dict) -> tuple:
    """
    Builds the object index hierarchy and shared components list.
    Returns: (objects_dict, shared_components_list)
    """
    objects = {}
    shared_items = []

    def ensure_object(obj_name):
        if obj_name not in objects:
            table_name = obj_name.lower() + "s"
            objects[obj_name] = {
                "label": obj_name,
                "osvc_table": table_name,
                "components": {
                    "workspaces": [],
                    "reports": [],
                    "cpm": [],
                    "bui_addins": [],
                    "custom_scripts": [],
                    "navigation_sets": [],
                    "business_rules": [],
                    "custom_objects": []
                }
            }

    comp_mappings = [
        ("workspaces", "workspace"),
        ("reports", "report"),
        ("cpm", "cpm"),
        ("buiAddins", "bui_addin"),
        ("customScripts", "custom_script"),
        ("navigationSets", "nav_set"),
        ("businessRules", "rule"),
        ("customObjects", "custom_object")
    ]

    for key, ctype in comp_mappings:
        for item in all_components.get(key, []):
            item_name = item.get("name") or item.get("file_name") or item.get("id") or "Unknown"
            matched_objs = detect_component_object(item, ctype)
            
            if len(matched_objs) > 1:
                shared_items.append({
                    "type": item.get("type") or ctype,
                    "name": item_name,
                    "objects": matched_objs,
                    "reason": f"Component references multiple objects: {', '.join(matched_objs)}"
                })

            for obj_name in matched_objs:
                ensure_object(obj_name)
                
                # File path resolution
                file_rel_path = ""
                summary_str = ""
                
                if ctype == "workspace":
                    ws_slug = item_name.replace(" ", "_")
                    file_rel_path = f"json/workspaces/{ws_slug}.json"
                    tabs_cnt = len(item.get("tabs", []))
                    fields_cnt = len(item.get("fields", []))
                    rules_cnt = len(item.get("rules", []))
                    summary_str = f"{fields_cnt} fields, {tabs_cnt} tabs, {rules_cnt} rules"
                    objects[obj_name]["components"]["workspaces"].append({
                        "name": item_name,
                        "file": file_rel_path,
                        "summary": summary_str
                    })
                elif ctype == "report":
                    rep_name = (item.get("name") or "Report").replace(" ", "_")
                    ac_id = item.get("id") or "doc"
                    file_rel_path = f"json/reports/{rep_name}_{ac_id}.json"
                    cols_cnt = len(item.get("columns", []))
                    tables_cnt = len(item.get("tables", []))
                    summary_str = f"{cols_cnt} columns, {tables_cnt} tables joined"
                    objects[obj_name]["components"]["reports"].append({
                        "name": item_name,
                        "ac_id": ac_id,
                        "file": file_rel_path,
                        "summary": summary_str
                    })
                elif ctype == "cpm":
                    cname = item.get("name") or item.get("file_name") or "CPMHandler"
                    cname_slug = cname.replace(" ", "_")
                    file_rel_path = f"json/cpm/{cname_slug}.json"
                    event = item.get("event") or "event_handler"
                    summary_str = f"Event: {event}"
                    objects[obj_name]["components"]["cpm"].append({
                        "name": cname,
                        "file": file_rel_path,
                        "summary": summary_str
                    })
                elif ctype == "bui_addin":
                    bname = item_name.replace(" ", "_")
                    file_rel_path = f"json/scripts/{bname}.json"
                    f_read = len(item.get("osvc_fields_read", []))
                    f_write = len(item.get("osvc_fields_written", []))
                    api_cnt = len(item.get("api_calls", []))
                    summary_str = f"{f_read} fields read, {f_write} fields written, {api_cnt} API calls"
                    objects[obj_name]["components"]["bui_addins"].append({
                        "name": item_name,
                        "file": file_rel_path,
                        "summary": summary_str
                    })
                elif ctype == "custom_object":
                    coname = item_name.replace(" ", "_")
                    file_rel_path = f"json/objects/{coname}.json"
                    fields_cnt = len(item.get("fields", []))
                    summary_str = f"{fields_cnt} custom fields defined"
                    objects[obj_name]["components"]["custom_objects"].append({
                        "name": item_name,
                        "file": file_rel_path,
                        "summary": summary_str
                    })

    return objects, shared_items
