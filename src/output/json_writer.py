import json
import os
from datetime import datetime
from src.output.object_mapper import build_object_tree, detect_component_object
from src.analyser.graph_builder import build_graph


def build_graph_structure(components, relationships, orphans, endpoints):
    """
    Translates parsed components, relationships, endpoints, and orphans
    into the full node-and-edge layout using graph_builder.build_graph.
    Also injects parent Object nodes to ensure object hierarchy mapping.
    """
    base_graph = build_graph(components, relationships, orphans, endpoints)
    nodes = base_graph.get("nodes", [])
    edges = base_graph.get("edges", [])
    
    # Inject parent Object nodes for Object filtering & focus mode
    objects_dict, _ = build_object_tree(components)
    node_ids = {n["id"] for n in nodes}
    
    for obj_name, obj_data in objects_dict.items():
        obj_id = f"object:{obj_name.lower()}"
        if obj_id not in node_ids:
            nodes.append({
                "id": obj_id,
                "type": "object",
                "label": obj_name,
                "data": {
                    "componentCount": sum(len(c_list) for c_list in obj_data["components"].values()),
                    "osvc_table": obj_data.get("osvc_table")
                }
            })
            node_ids.add(obj_id)
            
            # Connect parent object node to member component nodes
            for comp_cat, comp_list in obj_data["components"].items():
                for citem in comp_list:
                    c_name = citem.get("name") or "Unknown"
                    # Find matching nodes
                    for n in nodes:
                        if n["id"] != obj_id and c_name.lower() in n["label"].lower():
                            edge_id = f"e_obj_{obj_name}_{n['id']}"
                            edges.append({
                                "id": edge_id,
                                "source": obj_id,
                                "target": n["id"],
                                "label": "belongs to object"
                            })

    return {"nodes": nodes, "edges": edges}


def write_master_json(components, relationships, orphans, endpoints, output_file, meta_info=None, use_ai_summary=None):
    """
    Writes lightweight master.json index and individual component JSON files.
    """
    output_dir = os.path.dirname(output_file)
    json_dir = os.path.join(output_dir, "json")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    objects_dict, shared_items = build_object_tree(components)

    total_comps = sum(
        len(components.get(k, []))
        for k in ["workspaces", "reports", "cpm", "buiAddins", "customScripts", "navigationSets", "businessRules", "customObjects", "objectRelationships"]
    )

    has_ai = bool(use_ai_summary)

    meta = {
        "exportedAt": datetime.now().strftime("%Y-%m-%d"),
        "serverVersion": (meta_info or {}).get("serverVersion", "Oracle Service Cloud 26A SP2"),
        "totalComponents": total_comps,
        "useAiSummary": has_ai,
        "generatedAt": datetime.now().isoformat()
    }

    # Cross-reference map for reports
    report_xref = {}
    for rep in components.get("reports", []):
        r_id = str(rep.get("id"))
        if r_id:
            report_xref[r_id] = {
                "name": rep.get("name"),
                "referencedBy": []
            }

    # Populate flat index & write individual JSON files
    flat_index = {
        "workspaces": {},
        "reports": {},
        "cpm": {},
        "bui_addins": {},
        "custom_scripts": {},
        "custom_objects": {},
        "business_rules": {}
    }

    # Workspaces
    sorted_ws = sorted(components.get("workspaces", []), key=lambda x: x.get("name", "").lower())
    for ws in sorted_ws:
        name = ws.get("name", "Workspace")
        slug = name.replace(" ", "_")
        rel_path = f"json/workspaces/{slug}.json"
        flat_index["workspaces"][slug] = rel_path
        
        comp_data = {
            "meta": {"type": "workspace", "name": name, "osvc_object": detect_component_object(ws, "workspace"), "generatedAt": meta["generatedAt"]},
            "data": ws,
            "relationships": [r for r in relationships if r.get("from", {}).get("name") == name],
            "unknowns": ws.get("unknowns", {})
        }
        out_p = os.path.join(json_dir, "workspaces", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # Reports
    sorted_reports = sorted(components.get("reports", []), key=lambda x: x.get("name", "").lower())
    for rep in sorted_reports:
        name = rep.get("name", "Report")
        ac_id = str(rep.get("id", "doc"))
        slug = f"{name.replace(' ', '_')}_{ac_id}"
        rel_path = f"json/reports/{slug}.json"
        flat_index["reports"][ac_id] = rel_path

        comp_data = {
            "meta": {"type": "report", "name": name, "ac_id": ac_id, "osvc_object": detect_component_object(rep, "report"), "generatedAt": meta["generatedAt"]},
            "data": rep
        }
        out_p = os.path.join(json_dir, "reports", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # CPM
    sorted_cpm = sorted(components.get("cpm", []), key=lambda x: (x.get("name") or x.get("file_name") or "").lower())
    for cpm in sorted_cpm:
        name = cpm.get("name") or cpm.get("file_name") or "CPMHandler"
        slug = name.replace(" ", "_")
        rel_path = f"json/cpm/{slug}.json"
        flat_index["cpm"][slug] = rel_path

        comp_data = {
            "meta": {"type": "cpm", "name": name, "osvc_object": detect_component_object(cpm, "cpm"), "generatedAt": meta["generatedAt"]},
            "data": cpm
        }
        out_p = os.path.join(json_dir, "cpm", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # BUI Add-Ins
    sorted_bui = sorted(components.get("buiAddins", []), key=lambda x: x.get("name", "").lower())
    for bui in sorted_bui:
        name = bui.get("name", "BUIAddin")
        slug = name.replace(" ", "_")
        rel_path = f"json/bui_addins/{slug}.json"
        flat_index["bui_addins"][slug] = rel_path

        comp_data = {
            "meta": {"type": "bui_addin", "name": name, "osvc_object": detect_component_object(bui, "bui_addin"), "generatedAt": meta["generatedAt"]},
            "data": bui
        }
        out_p = os.path.join(json_dir, "bui_addins", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # Custom Scripts
    sorted_scripts = sorted(components.get("customScripts", []), key=lambda x: x.get("file_name", "").lower())
    for cs in sorted_scripts:
        name = cs.get("file_name", "Script")
        slug = name.replace(" ", "_")
        rel_path = f"json/scripts/{slug}.json"
        flat_index["custom_scripts"][slug] = rel_path

        comp_data = {
            "meta": {"type": "custom_script", "name": name, "osvc_object": detect_component_object(cs, "custom_script"), "generatedAt": meta["generatedAt"]},
            "data": cs
        }
        out_p = os.path.join(json_dir, "scripts", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # Custom Objects
    sorted_co = sorted(components.get("customObjects", []), key=lambda x: x.get("name", "").lower())
    for co in sorted_co:
        name = co.get("name", "CustomObject")
        slug = name.replace(" ", "_")
        rel_path = f"json/objects/{slug}.json"
        flat_index["custom_objects"][slug] = rel_path

        comp_data = {
            "meta": {"type": "custom_object", "name": name, "generatedAt": meta["generatedAt"]},
            "data": co
        }
        out_p = os.path.join(json_dir, "objects", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    # Business Rules
    sorted_br = sorted(components.get("businessRules", []), key=lambda x: x.get("file_name", "").lower())
    for br in sorted_br:
        r_name = br.get("name") or br.get("file_name") or "Business_Rules"
        slug = r_name.replace(" ", "_")
        flat_index["business_rules"][slug] = "rules/report_Business_Rules.md"

    # Ensure all dictionary keys in flat_index are sorted alphabetically
    for key in flat_index:
        flat_index[key] = dict(sorted(flat_index[key].items()))

    graph_payload = build_graph_structure(components, relationships, orphans, endpoints)

    master_data = {
        "meta": meta,
        "objects": objects_dict,
        "shared_components": {
            "description": "Components that reference multiple objects",
            "items": shared_items
        },
        "orphans": [
            {
                "type": o.get("type"),
                "name": o.get("name"),
                "file": f"json/workspaces/{o.get('name', '').replace(' ', '_')}.json",
                "reason": o.get("reason")
            }
            for o in orphans
        ],
        "endpoints": [
            {
                "url": ep.get("url"),
                "referencedBy": ep.get("source_assets", []),
                "risk": ep.get("risk_notes") or "External API Call"
            }
            for ep in endpoints
        ],
        "report_cross_reference": report_xref,
        "index": flat_index,
        "graph": graph_payload
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)

    return master_data


def write_index_json(workspaces, output_file, shared_reports=None):
    ws_items = []
    for ws in workspaces:
        ws_name = ws.get("name", "Unknown")
        ws_slug = ws_name.replace(" ", "_")
        ws_items.append({
            "name": ws_name,
            "slug": ws_slug,
            "tabsCount": len(ws.get("tabs", [])),
            "fieldsCount": len(ws.get("fields", [])),
            "rulesCount": len(ws.get("rules", [])),
            "reportMarkdownPath": f"workspaces/{ws_slug}/report.md",
            "reportJsonPath": f"workspaces/{ws_slug}/report.json"
        })

    index_data = {
        "title": "OSVC Configuration Workspace Index",
        "totalWorkspaces": len(workspaces),
        "workspaces": ws_items,
        "sharedReports": shared_reports or []
    }

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    return index_data

def write_cpm_summary_json(cpm_items, orphans, workspaces, output_file, use_ai_summary=None):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"cpm_count": len(cpm_items), "items": cpm_items}, f, indent=2, ensure_ascii=False)

def write_bui_addin_summary_json(bui_items, reports, workspaces, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"bui_count": len(bui_items), "items": bui_items}, f, indent=2, ensure_ascii=False)

def write_single_bui_addin_json(bui, reports, workspaces, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bui, f, indent=2, ensure_ascii=False)

def write_analytics_report_json(report_item, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report_item, f, indent=2, ensure_ascii=False)

def write_workspace_report_json(ws_item, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ws_item, f, indent=2, ensure_ascii=False)

def write_custom_scripts_summary_json(script_items, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"custom_script_count": len(script_items), "items": script_items}, f, indent=2, ensure_ascii=False)

def write_single_custom_script_json(script_item, output_file):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(script_item, f, indent=2, ensure_ascii=False)

def write_business_rules_summary_json(rule_items, output_file):
    import csv
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    total_rules = sum(r.get("total_rules", len(r.get("rules", []))) for r in rule_items)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_rules": total_rules,
            "rule_sets_count": len(rule_items),
            "rule_sets": rule_items
        }, f, indent=2, ensure_ascii=False)

    # Export CSV files by Object and Action Type under results/csv/rules/
    results_base = output_dir
    while os.path.basename(results_base) in ("rules", "json"):
        results_base = os.path.dirname(results_base)
    csv_rules_dir = os.path.join(results_base, "csv", "rules")
    os.makedirs(csv_rules_dir, exist_ok=True)

    # Flatten rules across sets
    all_rules = []
    for rset in rule_items:
        all_rules.extend(rset.get("rules", []))

    # Group rules by Object and Action Type
    object_action_rules = {}
    for r in all_rules:
        obj = r.get("object") or "Incidents"
        actions_by_type = r.get("actions_by_type", {})
        if not actions_by_type:
            # fallback categorization
            actions_by_type = {"Other": r.get("actions_raw", [])}

        for atype, act_list in actions_by_type.items():
            key = (obj, atype)
            if key not in object_action_rules:
                object_action_rules[key] = []
            object_action_rules[key].append({
                "rule_name": r.get("name"),
                "group_name": r.get("group_name"),
                "group_type": r.get("group_type"),
                "status": "Enabled" if r.get("active", True) else "Disabled",
                "condition": r.get("condition_raw"),
                "actions": " | ".join(act_list)
            })

    # Write individual CSV file for each Object and Action Type
    for (obj, atype), r_rows in object_action_rules.items():
        csv_file_name = f"{obj}_{atype}.csv"
        csv_p = os.path.join(csv_rules_dir, csv_file_name)
        with open(csv_p, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Object", "Action Type", "Rule Group", "Rule Name", "Status", "Condition", "Actions"])
            for row in r_rows:
                writer.writerow([obj, atype, row["group_name"], row["rule_name"], row["status"], row["condition"], row["actions"]])


def write_customer_portal_summary_json(cp_data, output_file):
    """
    Writes Customer Portal JSON report data to output_file.
    """
    out_dir = os.path.dirname(output_file)
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(),
        "component": "Customer Portal (CP3) MVC Framework",
        "summary": cp_data.get("summary", []),
        "models": cp_data.get("models", []),
        "hooks": cp_data.get("hooks", []),
        "templates": cp_data.get("templates", []),
        "pages": [
            {
                "page_file": p.get("page_file"),
                "key_widgets": p.get("key_widgets"),
                "purpose": p.get("purpose"),
                "login_required": p.get("login_required")
            } for p in cp_data.get("pages", [])
        ],
        "widgets": [
            {
                "name": w.get("name"),
                "file_path": w.get("file_path"),
                "purpose": w.get("purpose"),
                "used_in_pages": w.get("used_in_pages_str")
            } for w in cp_data.get("widgets", [])
        ],
        "community": cp_data.get("community", [])
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return output_file
