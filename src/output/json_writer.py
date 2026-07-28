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
        for k in ["workspaces", "reports", "cpm", "buiAddins", "customScripts", "navigationSets", "businessRules", "customObjects"]
    )

    meta = {
        "exportedAt": datetime.now().strftime("%Y-%m-%d"),
        "serverVersion": (meta_info or {}).get("serverVersion", "Oracle Service Cloud 26A SP2"),
        "totalComponents": total_comps,
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
        "custom_objects": {}
    }

    for ws in components.get("workspaces", []):
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

    for rep in components.get("reports", []):
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

    for cpm in components.get("cpm", []):
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

    for bui in components.get("buiAddins", []):
        name = bui.get("name", "BUIAddin")
        slug = name.replace(" ", "_")
        rel_path = f"json/scripts/{slug}.json"
        flat_index["bui_addins"][slug] = rel_path

        comp_data = {
            "meta": {"type": "bui_addin", "name": name, "osvc_object": detect_component_object(bui, "bui_addin"), "generatedAt": meta["generatedAt"]},
            "data": bui
        }
        out_p = os.path.join(json_dir, "scripts", f"{slug}.json")
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(comp_data, f, indent=2, ensure_ascii=False)

    for co in components.get("customObjects", []):
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
