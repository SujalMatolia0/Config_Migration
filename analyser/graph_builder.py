import os

def build_graph(components, relationships, orphans, endpoints):
    """
    Translates parsed components, relationships, endpoints, and orphans 
    into a structured node-and-edge layout consumed directly by React Flow.
    """
    nodes = []
    edges = []
    node_ids = set()

    orphans_map = {o["name"].lower(): o for o in orphans if o.get("name")}
    
    # Helpers to find details from parsed components
    workspaces_by_name = {w["name"].lower(): w for w in components.get("workspaces", [])}
    reports_by_id = {str(r["id"]): r for r in components.get("reports", []) if r.get("id")}
    scripts_by_name = {s["file_name"].lower(): s for s in components.get("customScripts", [])}
    cpm_by_name = {c["file_name"].lower(): c for c in components.get("cpm", [])}

    def add_node(node_id, label, type_name, extra_data=None):
        node_id_lower = node_id.lower()
        if node_id_lower in node_ids:
            return
            
        # Determine if this node represents an orphan
        is_orphan = False
        orphan_reason = None
        
        # Check standard references in orphans mapping
        if label.lower() in orphans_map:
            is_orphan = True
            orphan_reason = orphans_map[label.lower()]["reason"]
            
        # If it's a report ID, check if mapped to report name and if that is orphaned
        if type_name == "Report" and str(node_id).isdigit():
            # If the ID or name is orphaned
            r_data = reports_by_id.get(str(node_id))
            r_name = r_data["name"] if r_data else None
            if r_name and r_name.lower() in orphans_map:
                is_orphan = True
                orphan_reason = orphans_map[r_name.lower()]["reason"]
            elif f"report id: {node_id}" in orphans_map:
                is_orphan = True
                orphan_reason = orphans_map[f"report id: {node_id}"]["reason"]

        node_ids.add(node_id_lower)
        nodes.append({
            "id": node_id_lower,
            "type": type_name.lower(),
            "label": label,
            "isOrphan": is_orphan,
            "orphanReason": orphan_reason,
            "data": extra_data or {}
        })

    # 1. Workspace Nodes
    for ws in components.get("workspaces", []):
        add_node(f"Workspace:{ws['name']}", ws["name"], "Workspace", ws)

    # 2. Report Nodes
    for rep in components.get("reports", []):
        add_node(f"Report:{rep['id']}", rep["name"] or f"Report {rep['id']}", "Report", rep)

    # 3. Nav Set Nodes
    for ns in components.get("navigationSets", []):
        add_node(f"NavigationSet:{ns['name']}", ns["name"], "NavigationSet", ns)

    # 4. Rules Nodes
    for br in components.get("businessRules", []):
        for r in br.get("rules", []):
            add_node(f"BusinessRule:{r['name']}", r["name"], "BusinessRule", r)

    # 5. Custom Script Nodes
    for script in components.get("customScripts", []):
        add_node(f"CustomScript:{script['file_name']}", script["file_name"], "CustomScript", script)

    # 6. CPM Nodes
    for cpm in components.get("cpm", []):
        label = cpm.get("class_name") or cpm.get("file_name")
        add_node(f"CPM:{cpm['file_name']}", label, "CPM", cpm)

    # 7. Endpoint Nodes
    for ep in endpoints:
        add_node(f"ExternalEndpoint:{ep['url']}", ep["url"], "ExternalEndpoint", ep)

    # 8. OSVC Object Target Nodes (queried tables)
    for rel in relationships:
        to_type = rel["to"]["type"]
        to_name = rel["to"].get("name")
        if to_type == "OSVCObject" and to_name:
            add_node(f"OSVCObject:{to_name}", to_name, "OSVCObject")

    # 9. Build Edges mapping relationships
    for idx, rel in enumerate(relationships):
        from_type = rel["from"]["type"]
        from_name = rel["from"]["name"]
        from_id = f"{from_type}:{from_name}".lower()

        to_type = rel["to"]["type"]
        to_target = rel["to"].get("name") or rel["to"].get("id")
        to_id = f"{to_type}:{to_target}".lower()

        # Add target/source nodes to graph if not already parsed (fallbacks)
        if from_id not in node_ids:
            add_node(from_id, from_name, from_type)
        if to_id not in node_ids:
            add_node(to_id, str(to_target), to_type)

        edges.append({
            "id": f"edge-{idx}",
            "source": from_id,
            "target": to_id,
            "label": rel["via"]
        })

    return {
        "nodes": nodes,
        "edges": edges
    }
