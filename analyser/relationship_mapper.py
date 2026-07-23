import os
import re
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

def map_relationships(components):
    """
    Given a dictionary of parsed components, maps relationships and returns
    a list of relationship dictionaries:
    [
      {
        "from": { "type": "ComponentType", "name": "ComponentName" },
        "to": { "type": "TargetType", "id": "TargetId", "name": "TargetName" },
        "via": "Details of the reference"
      }
    ]
    """
    relationships = []
    
    workspaces = components.get("workspaces", [])
    reports = components.get("reports", [])
    scripts = components.get("customScripts", [])
    cpm_handlers = components.get("cpm", [])
    business_rules_list = components.get("businessRules", [])
    nav_sets = components.get("navigationSets", [])

    # Map reports by ID and name for easy lookups
    reports_by_id = {r.get("id"): r for r in reports if r.get("id")}
    reports_by_name = {r.get("name"): r for r in reports if r.get("name")}
    
    # Map workspaces by name
    workspaces_by_name = {w.get("name").lower(): w for w in workspaces if w.get("name")}
    
    # Map scripts by filename
    scripts_by_name = {s.get("file_name").lower(): s for s in scripts if s.get("file_name")}

    # 1. Workspaces -> Reports, Custom Scripts, External Endpoints
    for ws in workspaces:
        ws_name = ws.get("name")
        
        # Tabs and relationship items
        all_tabs = get_all_tabs_flat(ws.get("tabs", []))
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            
            for ri in tab.get("relationship_items", []):
                ac_id = ri.get("ac_id")
                search_id = ri.get("search_report_id")
                item_type = ri.get("item_type")
                if ac_id:
                    # Find referenced report name if possible
                    ref_rep = reports_by_id.get(ac_id)
                    rep_name = ref_rep.get("name") if ref_rep else f"Report {ac_id}"
                    
                    relationships.append({
                        "from": { "type": "Workspace", "name": ws_name },
                        "to": { "type": "Report", "id": ac_id, "name": rep_name },
                        "via": f"Tab '{tab_text}' -> RelationshipItem Type: {item_type} (AcId: {ac_id})"
                    })
                if search_id:
                    ref_rep = reports_by_id.get(search_id)
                    rep_name = ref_rep.get("name") if ref_rep else f"Report {search_id}"
                    
                    relationships.append({
                        "from": { "type": "Workspace", "name": ws_name },
                        "to": { "type": "Report", "id": search_id, "name": rep_name },
                        "via": f"Tab '{tab_text}' -> RelationshipItem Search Report (SearchReportId: {search_id})"
                    })

        # Workspace Fields -> Reports
        for f in ws.get("fields", []):
            field_id = f.get("field_id")
            rep_id = f.get("report_id")
            if rep_id:
                ref_rep = reports_by_id.get(rep_id)
                rep_name = ref_rep.get("name") if ref_rep else f"Report {rep_id}"
                
                relationships.append({
                    "from": { "type": "Workspace", "name": ws_name },
                    "to": { "type": "Report", "id": rep_id, "name": rep_name },
                    "via": f"Field '{field_id}' -> ReportId property (Report: {rep_id})"
                })

        # Tab Fields -> Reports
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            for f in tab.get("fields", []):
                field_id = f.get("field_id")
                rep_id = f.get("report_id")
                if rep_id:
                    ref_rep = reports_by_id.get(rep_id)
                    rep_name = ref_rep.get("name") if ref_rep else f"Report {rep_id}"
                    
                    relationships.append({
                        "from": { "type": "Workspace", "name": ws_name },
                        "to": { "type": "Report", "id": rep_id, "name": rep_name },
                        "via": f"Tab '{tab_text}' -> Field '{field_id}' -> ReportId property (Report: {rep_id})"
                    })

        # Tab Embedded Browsers -> Custom Script or External Endpoint
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            for br in tab.get("browsers", []):
                url = br.get("url")
                if url:
                    if is_custom_script_url(url):
                        script_name = os.path.basename(urllib.parse.urlparse(url).path) or url
                        relationships.append({
                            "from": { "type": "Workspace", "name": ws_name },
                            "to": { "type": "CustomScript", "name": script_name },
                            "via": f"Tab '{tab_text}' -> Browser -> Custom PHP Script ({url})"
                        })
                    else:
                        relationships.append({
                            "from": { "type": "Workspace", "name": ws_name },
                            "to": { "type": "ExternalEndpoint", "name": url },
                            "via": f"Tab '{tab_text}' -> Browser -> External Endpoint ({url})"
                        })

        # Workspace Ribbon Links -> External Endpoints / Custom Scripts
        for link in ws.get("ribbon_links", []):
            title = link.get("title")
            url = link.get("url")
            if url:
                if is_custom_script_url(url):
                    script_name = os.path.basename(urllib.parse.urlparse(url).path) or url
                    relationships.append({
                        "from": { "type": "Workspace", "name": ws_name },
                        "to": { "type": "CustomScript", "name": script_name },
                        "via": f"Ribbon Link '{title}' -> Custom PHP Script ({url})"
                    })
                else:
                    relationships.append({
                        "from": { "type": "Workspace", "name": ws_name },
                        "to": { "type": "ExternalEndpoint", "name": url },
                        "via": f"Ribbon Link '{title}' -> External Endpoint ({url})"
                    })

        # Workspace Rules -> Scripts or Messages
        for rule in ws.get("rules", []):
            rule_name = rule.get("name")
            for action in rule.get("actions", []):
                # If rule runs a script or custom action
                if action.get("type") == "RunScript" or action.get("script_path"):
                    script_path = action.get("script_path") or action.get("value")
                    if script_path:
                        script_base = os.path.basename(script_path).lower()
                        # See if we have this script parsed
                        ref_script = scripts_by_name.get(script_base)
                        script_name = ref_script.get("file_name") if ref_script else script_path
                        
                        relationships.append({
                            "from": { "type": "Workspace", "name": ws_name },
                            "to": { "type": "CustomScript", "name": script_name },
                            "via": f"Workspace Rule: '{rule_name}' -> Action: RunScript"
                        })

    # 2. Standalone Business Rules -> Scripts or Other rules
    for br_file in business_rules_list:
        file_name = br_file.get("file_name")
        for rule in br_file.get("rules", []):
            rule_name = rule.get("name")
            for action in rule.get("actions", []):
                if action.get("type") == "RunScript" or action.get("script_path"):
                    script_path = action.get("script_path") or action.get("value")
                    if script_path:
                        script_base = os.path.basename(script_path).lower()
                        ref_script = scripts_by_name.get(script_base)
                        script_name = ref_script.get("file_name") if ref_script else script_path
                        
                        relationships.append({
                            "from": { "type": "BusinessRule", "name": rule_name },
                            "to": { "type": "CustomScript", "name": script_name },
                            "via": f"Business Rule File '{file_name}' -> Action: RunScript"
                        })

    # 3. Navigation Sets -> Workspaces, Reports
    for ns in nav_sets:
        ns_name = ns.get("name")
        
        # Navigation Items
        for item in ns.get("items", []):
            label = item.get("label")
            item_type = item.get("type")
            ws_ref = item.get("workspace")
            rep_ref_id = item.get("report_id")
            
            if ws_ref:
                ref_ws = workspaces_by_name.get(ws_ref.lower())
                ws_actual_name = ref_ws.get("name") if ref_ws else ws_ref
                
                relationships.append({
                    "from": { "type": "NavigationSet", "name": ns_name },
                    "to": { "type": "Workspace", "name": ws_actual_name },
                    "via": f"Nav Item '{label}' ({item_type})"
                })
                
            if rep_ref_id:
                ref_rep = reports_by_id.get(rep_ref_id)
                rep_actual_name = ref_rep.get("name") if ref_rep else f"Report {rep_ref_id}"
                
                relationships.append({
                    "from": { "type": "NavigationSet", "name": ns_name },
                    "to": { "type": "Report", "id": rep_ref_id, "name": rep_actual_name },
                    "via": f"Nav Item '{label}' ({item_type})"
                })

    # 4. Custom Scripts -> Other Custom Scripts
    for script in scripts:
        script_name = script.get("file_name")
        
        for imp in script.get("imports", []):
            imp_base = os.path.basename(imp).lower()
            ref_script = scripts_by_name.get(imp_base)
            imported_script_name = ref_script.get("file_name") if ref_script else imp
            
            relationships.append({
                "from": { "type": "CustomScript", "name": script_name },
                "to": { "type": "CustomScript", "name": imported_script_name },
                "via": f"import/require statement: '{imp}'"
            })

    # 5. CPM Handlers -> OSVC Objects/Reports
    for cpm in cpm_handlers:
        cpm_name = cpm.get("file_name")
        
        # OSVC objects references
        for obj in cpm.get("osvc_objects", []):
            relationships.append({
                "from": { "type": "CPM", "name": cpm_name },
                "to": { "type": "OSVCObject", "name": obj },
                "via": "Connect PHP Object reference"
            })
            
        # OSVC Query calls
        for query in cpm.get("query_calls", []):
            # Parse table references inside query like 'FROM Contact', 'FROM Incident'
            # Look for "FROM <Table>" pattern
            from_matches = re.findall(r'FROM\s+(\w+)', query, re.IGNORECASE)
            for tbl in from_matches:
                relationships.append({
                    "from": { "type": "CPM", "name": cpm_name },
                    "to": { "type": "OSVCObject", "name": tbl },
                    "via": f"Connect Query: '{query}'"
                })

    return relationships
