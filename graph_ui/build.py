#!/usr/bin/env python
"""
Standalone builder for the OSVC dependency graph viewer.

Decoupled from the analyser pipeline: it only needs a master.json (the file
osvc_analyser.py already writes to <output>/master.json or
<output>/<workspace>/master.json). Point it at any master.json -- from this
project or copied elsewhere -- and it produces a self-contained, portable
viewer folder with no server or build step required to open it.

Usage:
    python build.py path/to/master.json [output_dir]

If output_dir is omitted, a "graph" folder is created next to master.json.
"""
import argparse
import json
import os
import shutil

_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS = ["index.html", "style.css", "app.js"]


def _load_master(master_json):
    """Accepts either a path to master.json or an already-loaded dict."""
    if isinstance(master_json, dict):
        return master_json
    with open(master_json, "r", encoding="utf-8") as f:
        return json.load(f)


def write_all_details(components, details_dir):
    os.makedirs(details_dir, exist_ok=True)
    
    def normalise_id(val):
        return str(val) if val is not None else None

    def is_custom_script_url(url):
        if not url:
            return False
        u = url.lower()
        return "php/custom" in u or "gcb.cfg/php/custom" in u or ".cfg/php/custom" in u

    def safe_basename(url):
        import urllib.parse
        try:
            path = urllib.parse.urlparse(url).path.rstrip("/")
            base = path.split("/")[-1] if path else ""
            return base if base else url
        except Exception:
            return url

    def get_all_tabs_flat(tabs_list):
        flat = []
        for t in tabs_list:
            flat.append(t)
            for ts in t.get("nested_tabsets", []):
                for sub_t in ts.get("sub_tabs", []):
                    flat.extend(get_all_tabs_flat([sub_t]))
        return flat

    def get_detail_filename(node_id):
        safe_name = node_id.replace(":", "_").replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in ("_", "-", "."))
        return f"{safe_name}.json"

    def add_secondary_node(child_nodes, node_type, label):
        sub_id = f"{node_type.lower()}:{label.lower()}"
        if not any(m["id"] == sub_id for m in child_nodes):
            child_nodes.append({
                "id": sub_id,
                "type": node_type.lower(),
                "label": label,
                "data": {"_fallback": True}
            })
        return sub_id

    # Report lookup for Workspace Field/Tab connections
    report_id_to_label_map = {
        normalise_id(r.get("id")): r.get("name", f"Report {r.get('id')}")
        for r in components.get("reports", [])
        if r.get("id") is not None
    }

    # Workspaces
    for ws in components.get("workspaces", []):
        ws_name = ws.get("name")
        node_id = f"workspace:{ws_name.lower()}"
        child_nodes = []
        child_edges = []
        
        all_tabs = get_all_tabs_flat(ws.get("tabs", []))
        for t in all_tabs:
            tab_text = t.get("text", "Tab")
            tab_id = t.get("id") or f"tab_{tab_text.lower().replace(' ', '_')}"
            t_node_id = f"{node_id}/tab:{tab_id.lower()}"
            child_nodes.append({
                "id": t_node_id,
                "type": "workspace_tab",
                "label": tab_text,
                "data": {"type": "Tab", "id": tab_id}
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{t_node_id}",
                "source": node_id,
                "target": t_node_id,
                "label": "contains"
            })
            
            # Browsers in tab
            for br in t.get("browsers", []):
                br_url = br.get("url") or "Browser"
                br_id = br.get("id") or f"browser_{br_url[:20].lower().replace('/', '_')}"
                br_node_id = f"{node_id}/browser:{br_id.lower()}"
                child_nodes.append({
                    "id": br_node_id,
                    "type": "workspace_browser",
                    "label": br_url[:30] + ("..." if len(br_url) > 30 else ""),
                    "data": {"type": "Browser", "url": br_url}
                })
                child_edges.append({
                    "id": f"edge-{t_node_id}-to-{br_node_id}",
                    "source": t_node_id,
                    "target": br_node_id,
                    "label": "has_browser"
                })
                
                if is_custom_script_url(br_url):
                    script_name = safe_basename(br_url)
                    child_edges.append({
                        "id": f"edge-{br_node_id}-to-customscript-{script_name.lower()}",
                        "source": br_node_id,
                        "target": f"customscript:{script_name.lower()}",
                        "label": "redirects_to"
                    })
                else:
                    child_edges.append({
                        "id": f"edge-{br_node_id}-to-endpoint-{br_url.lower()}",
                        "source": br_node_id,
                        "target": f"externalendpoint:{br_url.lower()}",
                        "label": "fetches"
                    })
                    
            # Add-ins in tab
            for addin in t.get("add_in_items", []):
                addin_id = addin.get("id") or "AddIn"
                addin_node_id = f"{node_id}/addin:{addin_id.lower()}"
                child_nodes.append({
                    "id": addin_node_id,
                    "type": "workspace_addin",
                    "label": addin_id,
                    "data": addin
                })
                child_edges.append({
                    "id": f"edge-{t_node_id}-to-{addin_node_id}",
                    "source": t_node_id,
                    "target": addin_node_id,
                    "label": "has_addin"
                })
                
            # Fields in tab
            for f in t.get("fields", []):
                field_id = f.get("field_id") or "Field"
                f_node_id = f"{node_id}/field:{field_id.lower()}"
                child_nodes.append({
                    "id": f_node_id,
                    "type": "workspace_field",
                    "label": field_id,
                    "data": f
                })
                child_edges.append({
                    "id": f"edge-{t_node_id}-to-{f_node_id}",
                    "source": t_node_id,
                    "target": f_node_id,
                    "label": "has_field"
                })
                
                obj_id = f.get("object_id")
                if obj_id:
                    obj_node_id = add_secondary_node(child_nodes, "OSVCObject", obj_id)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-{obj_node_id}",
                        "source": f_node_id,
                        "target": obj_node_id,
                        "label": "table"
                    })
                
                if "c$" in field_id.lower():
                    cf_name = "c$" + field_id.lower().split("c$", 1)[1]
                    cf_node_id = add_secondary_node(child_nodes, "CustomField", cf_name)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-{cf_node_id}",
                        "source": f_node_id,
                        "target": cf_node_id,
                        "label": "references"
                    })
                
                rep_id = f.get("report_id")
                if rep_id is not None:
                    nid = normalise_id(rep_id)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-report-{nid}",
                        "source": f_node_id,
                        "target": f"report:{report_id_to_label_map.get(nid, f'report {nid}').lower()}",
                        "label": "runs_report"
                    })
                    
        # Workspace fields not inside any tab
        for f in ws.get("fields", []):
            field_id = f.get("field_id") or "Field"
            f_node_id = f"{node_id}/field:{field_id.lower()}"
            if not any(n["id"] == f_node_id for n in child_nodes):
                child_nodes.append({
                    "id": f_node_id,
                    "type": "workspace_field",
                    "label": field_id,
                    "data": f
                })
                child_edges.append({
                    "id": f"edge-{node_id}-to-{f_node_id}",
                    "source": node_id,
                    "target": f_node_id,
                    "label": "has_field"
                })
                
                obj_id = f.get("object_id")
                if obj_id:
                    obj_node_id = add_secondary_node(child_nodes, "OSVCObject", obj_id)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-{obj_node_id}",
                        "source": f_node_id,
                        "target": obj_node_id,
                        "label": "table"
                    })
                
                if "c$" in field_id.lower():
                    cf_name = "c$" + field_id.lower().split("c$", 1)[1]
                    cf_node_id = add_secondary_node(child_nodes, "CustomField", cf_name)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-{cf_node_id}",
                        "source": f_node_id,
                        "target": cf_node_id,
                        "label": "references"
                    })
                
                rep_id = f.get("report_id")
                if rep_id is not None:
                    nid = normalise_id(rep_id)
                    child_edges.append({
                        "id": f"edge-{f_node_id}-to-report-{nid}",
                        "source": f_node_id,
                        "target": f"report:{report_id_to_label_map.get(nid, f'report {nid}').lower()}",
                        "label": "runs_report"
                    })
                    
        # Rules
        for rule in ws.get("rules", []):
            rule_name = rule.get("name") or "Rule"
            rule_node_id = f"{node_id}/rule:{rule_name.lower().replace(' ', '_')}"
            child_nodes.append({
                "id": rule_node_id,
                "type": "workspace_rule",
                "label": rule_name,
                "data": rule
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{rule_node_id}",
                "source": node_id,
                "target": rule_node_id,
                "label": "has_rule"
            })
            
        detail_data = {
            "id": node_id,
            "type": "workspace",
            "label": ws_name,
            "data": ws,
            "childNodes": child_nodes,
            "childEdges": child_edges
        }
        filename = get_detail_filename(node_id)
        with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
            json.dump(detail_data, f_out, indent=2, ensure_ascii=False)

    # Reports
    for rep in components.get("reports", []):
        rep_label = rep.get("name") or f"Report {normalise_id(rep.get('id'))}"
        node_id = f"report:{rep_label.lower()}"
        child_nodes = []
        child_edges = []
        
        for col in rep.get("columns", []):
            col_id = col.get("col_id") or col.get("label") or "Column"
            col_node_id = f"{node_id}/column:{col_id.lower()}"
            child_nodes.append({
                "id": col_node_id,
                "type": "report_column",
                "label": col.get("label") or col_id,
                "data": col
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{col_node_id}",
                "source": node_id,
                "target": col_node_id,
                "label": "has_column"
            })
            
            field_expr = col.get("field", "")
            if "c$" in field_expr.lower():
                cf_name = "c$" + field_expr.lower().split("c$", 1)[1]
                cf_node_id = add_secondary_node(child_nodes, "CustomField", cf_name)
                child_edges.append({
                    "id": f"edge-{col_node_id}-to-{cf_node_id}",
                    "source": col_node_id,
                    "target": cf_node_id,
                    "label": "references"
                })
            
            if "." in field_expr:
                tbl = field_expr.split(".")[0]
                tbl_node_id = add_secondary_node(child_nodes, "OSVCObject", tbl)
                child_edges.append({
                    "id": f"edge-{col_node_id}-to-{tbl_node_id}",
                    "source": col_node_id,
                    "target": tbl_node_id,
                    "label": "table"
                })
                
        for filt in rep.get("filters", []):
            filt_id = filt.get("col_id") or filt.get("expression") or "Filter"
            filt_node_id = f"{node_id}/filter:{filt_id.lower()}"
            child_nodes.append({
                "id": filt_node_id,
                "type": "report_filter",
                "label": filt.get("expression") or filt_id,
                "data": filt
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{filt_node_id}",
                "source": node_id,
                "target": filt_node_id,
                "label": "has_filter"
            })
            
        detail_data = {
            "id": node_id,
            "type": "report",
            "label": rep_label,
            "data": rep,
            "childNodes": child_nodes,
            "childEdges": child_edges
        }
        filename = get_detail_filename(node_id)
        with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
            json.dump(detail_data, f_out, indent=2, ensure_ascii=False)

    # CPM Procedures
    for cpm in components.get("cpm", []):
        if cpm.get("format") in ("cpm_procedure", "cpm_php"):
            label = cpm.get("name") or cpm.get("display_name") or cpm.get("file_name")
            is_async = cpm.get("is_async")
            render_type = "asynccpm" if is_async else "cpm"
            node_id = f"cpm:{label.lower()}"
            
            child_nodes = []
            child_edges = []
            
            for b in cpm.get("bound_classes", []):
                b_node_id = f"{node_id}/bound:{b.lower()}"
                child_nodes.append({
                    "id": b_node_id,
                    "type": "cpm_bound_class",
                    "label": b,
                    "data": {"class": b}
                })
                child_edges.append({
                    "id": f"edge-{node_id}-to-{b_node_id}",
                    "source": node_id,
                    "target": b_node_id,
                    "label": "binds_to"
                })
                
                obj_node_id = add_secondary_node(child_nodes, "OSVCObject", b)
                child_edges.append({
                    "id": f"edge-{b_node_id}-to-{obj_node_id}",
                    "source": b_node_id,
                    "target": obj_node_id,
                    "label": "targets"
                })
                
            for soap in cpm.get("soap_actions", []):
                soap_node_id = f"{node_id}/soap:{soap.lower()}"
                child_nodes.append({
                    "id": soap_node_id,
                    "type": "cpm_soap_action",
                    "label": soap,
                    "data": {"action": soap}
                })
                child_edges.append({
                    "id": f"edge-{node_id}-to-{soap_node_id}",
                    "source": node_id,
                    "target": soap_node_id,
                    "label": "calls_soap"
                })
                
            detail_data = {
                "id": node_id,
                "type": render_type,
                "label": label,
                "data": cpm,
                "childNodes": child_nodes,
                "childEdges": child_edges
            }
            filename = get_detail_filename(node_id)
            with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
                json.dump(detail_data, f_out, indent=2, ensure_ascii=False)

    # BUI Add-ins
    for bui in components.get("buiAddins", []):
        label = bui.get("name", "BUI Add-In")
        node_id = f"buiaddin:{label.lower()}"
        child_nodes = []
        child_edges = []
        
        for api in bui.get("api_calls", []):
            api_node_id = f"{node_id}/api:{api.lower()}"
            child_nodes.append({
                "id": api_node_id,
                "type": "bui_api_call",
                "label": api,
                "data": {"api": api}
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{api_node_id}",
                "source": node_id,
                "target": api_node_id,
                "label": "calls_api"
            })
            
        for listener in bui.get("lifecycle_listeners", []):
            lis_node_id = f"{node_id}/listener:{listener.lower()}"
            child_nodes.append({
                "id": lis_node_id,
                "type": "bui_listener",
                "label": listener,
                "data": {"listener": listener}
            })
            child_edges.append({
                "id": f"edge-{node_id}-to-{lis_node_id}",
                "source": node_id,
                "target": lis_node_id,
                "label": "listens_to"
            })
            
        detail_data = {
            "id": node_id,
            "type": "buiaddin",
            "label": label,
            "data": bui,
            "childNodes": child_nodes,
            "childEdges": child_edges
        }
        filename = get_detail_filename(node_id)
        with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
            json.dump(detail_data, f_out, indent=2, ensure_ascii=False)

    # Navigation Sets
    for ns in components.get("navigationSets", []):
        node_id = f"navigationset:{ns['name'].lower()}"
        detail_data = {
            "id": node_id,
            "type": "navigationset",
            "label": ns["name"],
            "data": ns,
            "childNodes": [],
            "childEdges": []
        }
        filename = get_detail_filename(node_id)
        with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
            json.dump(detail_data, f_out, indent=2, ensure_ascii=False)

    # Custom Scripts
    for script in components.get("customScripts", []):
        node_id = f"customscript:{script['file_name'].lower()}"
        detail_data = {
            "id": node_id,
            "type": "customscript",
            "label": script["file_name"],
            "data": script,
            "childNodes": [],
            "childEdges": []
        }
        filename = get_detail_filename(node_id)
        with open(os.path.join(details_dir, filename), "w", encoding="utf-8") as f_out:
            json.dump(detail_data, f_out, indent=2, ensure_ascii=False)


def build_graph_ui(master_json, output_dir):
    """
    Renders a portable graph viewer into output_dir from a master.json
    (path or dict). Copies index.html/style.css/app.js from this folder
    alongside a generated data.js holding the graph + meta payload, so
    output_dir becomes fully self-contained and drop-in-anywhere -- just
    open index.html in a browser.
    """
    master_data = _load_master(master_json)
    graph_data = master_data.get("graph", {"nodes": [], "edges": []})
    meta = master_data.get("meta", {})
    components = master_data.get("components", {})

    os.makedirs(output_dir, exist_ok=True)

    for asset in _ASSETS:
        shutil.copyfile(os.path.join(_DIR, asset), os.path.join(output_dir, asset))

    data_js = (
        f"window.GRAPH_DATA = {json.dumps(graph_data)};\n"
        f"window.GRAPH_META = {json.dumps(meta)};\n"
    )
    with open(os.path.join(output_dir, "data.js"), "w", encoding="utf-8") as f:
        f.write(data_js)

    if components:
        write_all_details(components, os.path.join(output_dir, "details"))

    return os.path.join(output_dir, "index.html")


def main():
    parser = argparse.ArgumentParser(
        description="Build a portable OSVC dependency graph viewer from a master.json export."
    )
    parser.add_argument("master_json", help="Path to a master.json produced by osvc_analyser.py")
    parser.add_argument(
        "output_dir", nargs="?", default=None,
        help="Directory to write the viewer into (default: a 'graph' folder next to master.json)"
    )
    args = parser.parse_args()

    output_dir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(args.master_json)), "graph"
    )
    index_path = build_graph_ui(args.master_json, output_dir)
    print(f"Graph viewer written -> {index_path}")
    print("Open it directly in any browser (no server needed).")


if __name__ == "__main__":
    main()
