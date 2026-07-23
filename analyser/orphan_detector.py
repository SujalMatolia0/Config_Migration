def get_all_tabs_flat(tabs_list):
    flat = []
    for t in tabs_list:
        flat.append(t)
        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                flat.extend(get_all_tabs_flat([sub_t]))
    return flat

def detect_orphans(components, relationships):
    """
    Identifies orphaned or inactive OSVC components by analyzing references.
    """
    orphans = []
    
    workspaces = components.get("workspaces", [])
    reports = components.get("reports", [])
    scripts = components.get("customScripts", [])
    business_rules_list = components.get("businessRules", [])
    nav_sets = components.get("navigationSets", [])

    # Keep track of what is referenced
    referenced_workspaces = set()
    referenced_reports = set()
    referenced_scripts = set()

    for rel in relationships:
        to_comp = rel.get("to", {})
        to_type = to_comp.get("type")
        to_name = to_comp.get("name")
        to_id = to_comp.get("id")

        if to_type == "Workspace" and to_name:
            referenced_workspaces.add(to_name.lower())
        elif to_type == "Report":
            if to_id:
                referenced_reports.add(str(to_id))
            if to_name:
                referenced_reports.add(to_name.lower())
        elif to_type == "CustomScript" and to_name:
            referenced_scripts.add(to_name.lower())

    # 1. Workspace Orphans
    # Rule: Workspace not referenced by any Navigation Set
    for ws in workspaces:
        ws_name = ws.get("name")
        # Check if ws_name is in referenced_workspaces
        # Note: Nav Set references workspaces. If it's not in referenced_workspaces, it's an orphan.
        if ws_name.lower() not in referenced_workspaces:
            orphans.append({
                "type": "Workspace",
                "name": ws_name,
                "reason": "Not referenced in any Navigation Set"
            })

    # 2. Report Orphans
    # Rule: Report not referenced by any Workspace, Script, CPM or Nav Set
    for rep in reports:
        rep_id = rep.get("id")
        rep_name = rep.get("name")
        
        id_ref = str(rep_id) in referenced_reports if rep_id else False
        name_ref = rep_name.lower() in referenced_reports if rep_name else False
        
        if not id_ref and not name_ref:
            orphans.append({
                "type": "Report",
                "name": rep_name or f"Report ID: {rep_id}",
                "reason": "Not referenced by any Workspace, Script, CPM, or Navigation Set"
            })

    # 3. Custom Script Orphans
    # Rule: Custom Script not referenced or imported anywhere
    for scr in scripts:
        scr_name = scr.get("file_name")
        if scr_name.lower() not in referenced_scripts:
            # Heuristic: exclude files that are likely standard boilerplate entry points
            if not scr_name.lower().startswith("index."):
                orphans.append({
                    "type": "CustomScript",
                    "name": scr_name,
                    "reason": "Not imported or called by any Workspace Rule, CPM, or other Custom Script"
                })

    # 4. Inactive Business Rules
    # Standard Rule (nested inside Workspace)
    for ws in workspaces:
        ws_name = ws.get("name")
        for rule in ws.get("rules", []):
            if not rule.get("active", True):
                orphans.append({
                    "type": "BusinessRule",
                    "name": f"Workspace '{ws_name}' Rule: {rule.get('name')}",
                    "reason": "Rule is marked Inactive (Active=\"False\")"
                })

    # Standalone Rules
    for br_file in business_rules_list:
        file_name = br_file.get("file_name")
        for rule in br_file.get("rules", []):
            if not rule.get("active", True):
                orphans.append({
                    "type": "BusinessRule",
                    "name": f"Rule file '{file_name}' Rule: {rule.get('name')}",
                    "reason": "Rule is marked Inactive"
                })

    # 5. Workspace Relabeling Mismatch and Browser Error Suppression Checks
    for ws in workspaces:
        ws_name = ws.get("name")
        
        # Check standard fields relabeling
        for f in ws.get("fields", []):
            fid = f.get("field_id") or ""
            flabel = f.get("label") or ""
            if fid.lower() == "phoffice" and "mobile" in flabel.lower():
                orphans.append({
                    "type": "ConfigAnomaly",
                    "name": f"Workspace '{ws_name}' Field: {fid}",
                    "reason": f"Field '{fid}' is relabeled as '{flabel}'. Standard mobile fields should be used instead to avoid data fragmentation."
                })
            
        # Check browser tabs for SuppressErrors
        for tab in get_all_tabs_flat(ws.get("tabs", [])):
            tab_text = tab.get("text", "Unknown Tab")
            for br in tab.get("browsers", []):
                if br.get("suppress_errors"):
                    orphans.append({
                        "type": "ConfigRisk",
                        "name": f"Workspace '{ws_name}' Tab: '{tab_text}'",
                        "reason": f"Embedded Browser has SuppressErrors=True (Url: {br.get('url')}) - fails silently."
                    })

    return orphans
