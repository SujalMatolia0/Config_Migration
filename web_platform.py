import os
import sys
import subprocess
import shutil
import io
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file

app = Flask(__name__, static_folder='results', static_url_path='/results')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "bin", "python")

if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

import zipfile

def detect_osvc_file_type(file_path):
    """
    Inspects XML content or ZIP manifests to return accurate OSVC component classification & sub-group labels.
    """
    lower = os.path.basename(file_path).lower()
    ext = os.path.splitext(lower)[1]

    if ext == ".zip":
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                names = [n.lower() for n in z.namelist()]
                if any("init.html" in n or "manifest.json" in n or ".js" in n for n in names):
                    return "bui", "BUI Add-In Package", "BUI Extension Archives", "ZIP package with JS/HTML entrypoint"
        except Exception:
            pass
        return "bui", "BUI Add-In (ZIP)", "BUI Extension Archives", "ZIP Archive"

    if ext in [".php", ".inc"]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)
                if "ObjectEventHandler" in content or "RNCPM" in content:
                    return "cpm", "CPM Procedure", "Object Event Handlers", "PHP handler implementing ObjectEventHandler"
        except Exception:
            pass
        return "scripts", "Custom Script (PHP)", "Custom PHP Scripts", "Standalone PHP Source Script"

    if ext == ".js":
        return "scripts", "JavaScript Add-In", "Custom Scripts & JS", "JS Source File"

    if ext == ".csv":
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2048).lower()
                if "rule" in content or "state" in content or "object" in content or "action" in content or "if" in content or "then" in content or "rule" in lower:
                    return "rule", "Business Rule CSV", "Business Rules & Engine Logic", "Detected CSV Business Rules export format"
        except Exception:
            pass
        return "rule", "Business Rule CSV", "Business Rules & Engine Logic", "CSV Business Rules File"

    if ext in [".xml", ".txt"]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)
                if "<analytics_core" in content or "xmlns=\"urn:obj.api.rightnow.com\"" in content or "<ac_id>" in content:
                    return "report", "Analytics Report XML", "Analytics Reports Inventory", "Detected analytics_core report XML schema"
                elif "<ObjectProcedure" in content or "objectprocedure" in lower:
                    return "cpm", "CPM Procedure XML", "Object Event Handlers", "Detected ObjectProcedure CPM handler schema"
                elif "mappings.xml" in lower or "<mappings" in content.lower() or "<suppressflagmapping" in content.lower():
                    return "cpm", "CPM Mappings XML", "CPM Routing Mappings", "Detected CPM routing Mappings.xml table"
                elif "<tabset" in content.lower() or "<table" in content.lower() or "<recordtypes" in content.lower() or "<ribbon" in content.lower():
                    sub = "Standard Object Workspaces" if ("contact" in lower or "incident" in lower) else "Custom & Edge Workspaces"
                    return "workspace", "Workspace XML", sub, "Detected TabSet/Table workspace layout schema"
                elif "<customobject" in content.lower() or "<object" in content.lower():
                    return "objects", "Custom Object XML", "Custom Objects & Data Schema", "Detected CustomObject schema XML"
                elif "<relationship" in content.lower():
                    return "objects", "Relationship XML", "Object Relationships Schema", "Detected Relationship schema XML"
                elif "<rule" in content.lower() or "<rules" in content.lower():
                    return "rule", "Business Rule XML", "Business Rules & Engine Logic", "Detected Rule engine logic schema"
                elif "<navitem" in content.lower() or "<nav_set" in content.lower() or "<item_id" in content.lower():
                    return "nav", "Navigation Set XML", "Navigation Sets & Menus", "Detected Navigation Set menu schema"
        except Exception:
            pass
        return "xml", "OSVC XML Export", "Generic XML Exports", "Generic OSVC XML file"

    return "other", "Resource File", "Generic Resource Exports", "Generic file export"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/files", methods=["GET"])
def list_files():
    files_list = []
    category_counts = {
        "workspace": 0,
        "report": 0,
        "cpm": 0,
        "scripts": 0,
        "bui": 0,
        "objects": 0,
        "rule": 0,
        "nav": 0,
        "other": 0
    }

    seen_paths = set()

    for item in os.listdir(INPUT_DIR):
        if item.startswith("."):
            continue
        item_path = os.path.join(INPUT_DIR, item)

        if os.path.isdir(item_path):
            sub_items = os.listdir(item_path)
            for sub in sub_items:
                if sub.startswith("."):
                    continue
                sub_full = os.path.join(item_path, sub)
                rel_p = os.path.relpath(sub_full, INPUT_DIR)

                if os.path.isdir(sub_full):
                    cat_code, cat_name, sub_group, reason = "bui", "BUI Add-In Package", "BUI Extension Archives", "Extracted BUI Extension Directory"
                    category_counts["bui"] += 1
                    stat = os.stat(sub_full)
                    total_size = sum(os.path.getsize(os.path.join(r, file)) for r, _, f_list in os.walk(sub_full) for file in f_list if not file.startswith("."))
                    files_list.append({
                        "name": sub,
                        "path": rel_p,
                        "cat_code": cat_code,
                        "cat_name": cat_name,
                        "sub_group": sub_group,
                        "detection_reason": reason,
                        "size_bytes": total_size,
                        "is_dir": True,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
                    seen_paths.add(rel_p)
                elif os.path.isfile(sub_full) and rel_p not in seen_paths:
                    cat_code, cat_name, sub_group, reason = detect_osvc_file_type(sub_full)
                    category_counts[cat_code] = category_counts.get(cat_code, 0) + 1
                    stat = os.stat(sub_full)
                    files_list.append({
                        "name": sub,
                        "path": rel_p,
                        "cat_code": cat_code,
                        "cat_name": cat_name,
                        "sub_group": sub_group,
                        "detection_reason": reason,
                        "size_bytes": stat.st_size,
                        "is_dir": False,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
                    seen_paths.add(rel_p)
        elif os.path.isfile(item_path):
            rel_p = item
            cat_code, cat_name, sub_group, reason = detect_osvc_file_type(item_path)
            category_counts[cat_code] = category_counts.get(cat_code, 0) + 1
            stat = os.stat(item_path)
            files_list.append({
                "name": item,
                "path": rel_p,
                "cat_code": cat_code,
                "cat_name": cat_name,
                "sub_group": sub_group,
                "detection_reason": reason,
                "size_bytes": stat.st_size,
                "is_dir": False,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

    return jsonify({
        "success": True,
        "files": files_list,
        "counts": category_counts
    })

@app.route("/api/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        return jsonify({"success": False, "error": "No files uploaded"}), 400

    uploaded_files = request.files.getlist("files")
    category_target = request.form.get("category", "auto")

    saved_files = []
    for file_obj in uploaded_files:
        if not file_obj.filename:
            continue
        
        filename = os.path.basename(file_obj.filename)
        temp_path = os.path.join(INPUT_DIR, f"_temp_{filename}")
        file_obj.save(temp_path)

        cat_code, cat_name, _sub_group, reason = detect_osvc_file_type(temp_path)
        
        # Route to specific subfolder if auto-detect is selected or explicit category
        subfolder = ""
        if category_target == "auto":
            if cat_code == "workspace":
                subfolder = "workspaces"
            elif cat_code == "report":
                subfolder = "reports"
            elif cat_code == "cpm":
                subfolder = "cpm"
            elif cat_code in ["bui", "scripts"]:
                subfolder = "scripts"
            elif cat_code == "rule":
                subfolder = "rules"
            elif cat_code == "nav":
                subfolder = "navigation"
        else:
            if category_target == "workspaces": subfolder = "workspaces"
            elif category_target == "reports": subfolder = "reports"
            elif category_target == "cpm": subfolder = "cpm"
            elif category_target == "scripts": subfolder = "scripts"
            elif category_target == "rules": subfolder = "rules"
            elif category_target == "objects": subfolder = "objects"

        target_dir = os.path.join(INPUT_DIR, subfolder) if subfolder else INPUT_DIR
        os.makedirs(target_dir, exist_ok=True)
        final_path = os.path.join(target_dir, filename)

        if os.path.exists(final_path):
            os.remove(final_path)
        os.rename(temp_path, final_path)

        saved_files.append({
            "filename": filename,
            "category": cat_name,
            "code": cat_code,
            "reason": reason,
            "folder": subfolder or "input (root)"
        })

    return jsonify({"success": True, "saved": saved_files})

@app.route("/api/delete-file", methods=["POST"])
def delete_file():
    data = request.json or {}
    rel_path = data.get("path")
    if not rel_path:
        return jsonify({"success": False, "error": "Path required"}), 400

    full_path = os.path.abspath(os.path.join(INPUT_DIR, rel_path))
    if not full_path.startswith(INPUT_DIR):
        return jsonify({"success": False, "error": "Invalid path"}), 403

    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return jsonify({"success": True, "removed": rel_path})
    return jsonify({"success": False, "error": "File not found"}), 440

@app.route("/api/clear-input", methods=["POST"])
def clear_input():
    for item in os.listdir(INPUT_DIR):
        item_path = os.path.join(INPUT_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
    return jsonify({"success": True, "message": "Input directory cleared"})

@app.route("/api/run-analysis", methods=["POST"])
def run_analysis():
    data = request.json or {}
    use_ai = data.get("use_ai_summary", True)
    strict = data.get("strict", False)
    dump_unknowns = data.get("dump_unknowns", True)
    export_format = data.get("format", "html")

    cmd = [
        VENV_PYTHON,
        os.path.join(BASE_DIR, "osvc_analyser.py"),
        "--input", INPUT_DIR,
        "--output", RESULTS_DIR,
        "--format", export_format
    ]

    if not use_ai:
        cmd.append("--no-ai-summary")
    else:
        cmd.append("--use-ai-summary")

    if strict:
        cmd.append("--strict")

    if dump_unknowns:
        cmd.append("--dump-unknowns")

    try:
        process = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180
        )
        return jsonify({
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "output": process.stdout
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Analysis timed out after 180s"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/results-summary", methods=["GET"])
def get_results_summary():
    master_json_path = os.path.join(RESULTS_DIR, "master.json")
    unknowns_json_path = os.path.join(RESULTS_DIR, "unknowns.json")

    summary = {
        "has_results": os.path.exists(master_json_path),
        "workspaces_count": 0,
        "reports_count": 0,
        "cpm_count": 0,
        "bui_count": 0,
        "unknowns_count": 0,
        "unknowns_details": []
    }

    if os.path.exists(master_json_path):
        try:
            import json
            with open(master_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            s_dict = data.get("summary", {})
            summary["workspaces_count"] = s_dict.get("workspaces", 0)
            summary["reports_count"] = s_dict.get("reports", 0)
            summary["cpm_count"] = s_dict.get("cpmHandlers", 0)
            bui_list = data.get("components", {}).get("buiAddins", [])
            summary["bui_count"] = len(bui_list) if bui_list else s_dict.get("customScripts", 0)
            if summary["bui_count"] == 0:
                bui_dir = os.path.join(INPUT_DIR, "bui")
                if os.path.exists(bui_dir):
                    summary["bui_count"] = len([d for d in os.listdir(bui_dir) if not d.startswith(".")])
        except Exception:
            pass

    if os.path.exists(unknowns_json_path):
        try:
            import json
            with open(unknowns_json_path, "r", encoding="utf-8") as f:
                unk_data = json.load(f)
            summary["unknowns_details"] = unk_data.get("workspaces", [])
            summary["unknowns_count"] = sum(w.get("total_unknowns", 0) for w in unk_data.get("workspaces", []))
        except Exception:
            pass

    return jsonify({"success": True, "summary": summary})


@app.route("/api/download-results", methods=["GET"])
def download_results():
    if not os.path.exists(RESULTS_DIR) or not os.listdir(RESULTS_DIR):
        return jsonify({"success": False, "error": "No results to download."}), 404
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(RESULTS_DIR):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.startswith("."):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, RESULTS_DIR)
                zf.write(file_path, arcname)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="OSVC_Accelerator_Results.zip"
    )

@app.route("/api/download-master-report", methods=["GET"])
def download_master_report():
    report_path = os.path.join(RESULTS_DIR, "COMPLETE_SYSTEM_MAPPING.md")
    if not os.path.exists(report_path):
        return jsonify({"success": False, "error": "Master report not generated yet."}), 404
    return send_file(
        report_path,
        mimetype="text/markdown",
        as_attachment=True,
        download_name="COMPLETE_SYSTEM_MAPPING.md"
    )

@app.route("/results/<path:filename>", methods=["GET"])
def serve_results_static(filename):
    resp = send_from_directory(RESULTS_DIR, filename)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


def _build_graph_data(master):
    nodes = []
    edges = []
    _id = [0]
    node_map = {}
    edge_set = set()

    def nid():
        _id[0] += 1
        return _id[0]

    def add_node(key, label, group, title="", shape="dot", size=22, extra=None):
        if key in node_map:
            return node_map[key]
        n = _id[0] + 1
        _id[0] = n
        node_map[key] = n
        entry = {"id": n, "label": label, "group": group, "title": title, "shape": shape, "size": size}
        if extra:
            entry.update(extra)
        nodes.append(entry)
        return n

    def add_edge(frm, to, label="", dashes=False):
        key = (frm, to, label)
        if key in edge_set:
            return
        edge_set.add(key)
        edges.append({"from": frm, "to": to, "label": label, "dashes": dashes})

    meta = master.get("meta", {})
    summary = master.get("summary", {})
    comps = master.get("components", {})

    ver = meta.get("serverVersion", "OSVC Instance").split("\n")[0].strip()
    inst_id = add_node("instance", "OSVC\nInstance", "instance",
                       title=ver, shape="star", size=44)

    # --- CPM mappings ---
    for cpm in comps.get("cpm", []):
        for mapping in cpm.get("mappings", []):
            obj  = mapping.get("object", "")
            iface = mapping.get("interface", "")
            op   = mapping.get("operation", "")
            proc = mapping.get("procedure", "")
            if not (obj and iface and proc):
                continue

            iface_id = add_node(
                f"iface:{iface}", iface, "interface",
                title=f"Interface: {iface}", shape="diamond", size=26
            )
            add_edge(inst_id, iface_id, "routes via")

            obj_id = add_node(
                f"obj:{obj}", obj, "object",
                title=f"Object Type: {obj}", shape="hexagon", size=32
            )
            add_edge(iface_id, obj_id, "manages")

            proc_id = add_node(
                f"proc:{proc}", proc.replace("_", "_\n"), "procedure",
                title=f"{obj} → {op}\nProcedure: {proc}\nFile: {cpm.get('file_name','')}",
                shape="ellipse", size=18
            )
            add_edge(obj_id, proc_id, op.lower())

    # --- Workspaces ---
    for ws in comps.get("workspaces", []):
        ws_type = ws.get("type", "")
        ws_name = ws.get("name", "")
        recs = ", ".join(r.get("name", "") for r in ws.get("record_types", []))
        ws_id = add_node(
            f"ws:{ws_name}", ws_name, "workspace",
            title=f"Workspace: {ws_name}\nType: {ws_type}\nRecord Types: {recs}\nRows: {ws.get('row_count',0)}  Cols: {ws.get('column_count',0)}",
            shape="square", size=20
        )
        obj_key = f"obj:{ws_type}"
        if obj_key in node_map:
            add_edge(node_map[obj_key], ws_id, "UI for")
        else:
            add_edge(inst_id, ws_id, "workspace", dashes=True)

    # --- Analytics Reports ---
    report_id_map = {}
    for rpt in comps.get("reports", []):
        rpt_name = rpt.get("name", "")
        rpt_rid  = str(rpt.get("id", ""))
        tables   = ", ".join(rpt.get("tables", []))
        rpt_id = add_node(
            f"rpt:{rpt_rid}",
            f"Report\n{rpt_name}",
            "report",
            title=f"Analytics Report: {rpt_name}\nID: {rpt_rid}\nTables: {tables}",
            shape="database", size=22
        )
        report_id_map[rpt_rid] = rpt_id
        add_edge(inst_id, rpt_id, "analytics", dashes=True)

    # --- BUI Add-ins ---
    for bui in comps.get("buiAddins", []):
        bui_name  = bui.get("name", "")
        bui_files = ", ".join(bui.get("files", []))
        risk      = ", ".join(bui.get("risk_flags", []))
        bui_id = add_node(
            f"bui:{bui_name}", bui_name, "bui",
            title=f"BUI Add-in: {bui_name}\nFiles: {bui_files}\nRisk: {risk or 'none'}",
            shape="triangle", size=26
        )
        add_edge(inst_id, bui_id, "extension")

        # BUI -> Reports
        for rid in bui.get("report_ids", []):
            rid_str = str(rid)
            if rid_str in report_id_map:
                add_edge(bui_id, report_id_map[rid_str], "queries")

        # BUI -> Object types (via field access)
        touched_objs = set()
        for fld in bui.get("osvc_fields_read", []) + bui.get("osvc_fields_written", []):
            obj = fld.split(".")[0] if "." in fld else ""
            if obj:
                touched_objs.add(obj)
        for obj in touched_objs:
            if f"obj:{obj}" in node_map:
                add_edge(bui_id, node_map[f"obj:{obj}"], "reads/writes")

        # BUI -> External API calls
        for call in bui.get("api_calls", []):
            ep  = call.get("endpoint", "")
            mth = call.get("method", "")
            ep_label = ep if len(ep) <= 34 else ep[:31] + "..."
            ep_id = add_node(
                f"api:{ep}", ep_label, "external",
                title=f"{mth} {ep}\nType: {call.get('type','')}\nFile: {call.get('file','')}",
                shape="box", size=16
            )
            add_edge(bui_id, ep_id, mth.lower())

    # --- External endpoints not yet captured ---
    for ep in summary.get("externalEndpoints", []):
        ep_key = f"api:{ep}"
        if ep_key not in node_map:
            ep_label = ep if len(ep) <= 34 else ep[:31] + "..."
            ep_id = add_node(
                ep_key, ep_label, "external",
                title=ep, shape="box", size=16
            )
            add_edge(inst_id, ep_id, "external", dashes=True)

    return nodes, edges


def _render_architect_html(master, nodes, edges):
    meta    = master.get("meta", {})
    summary = master.get("summary", {})
    ver     = meta.get("serverVersion", "OSVC Instance").split("\n")[0].strip()
    exported = meta.get("exportedAt", "")
    stats = [
        ("Workspaces",   summary.get("workspaces", 0)),
        ("CPM Handlers", summary.get("cpmHandlers", 0)),
        ("Reports",      summary.get("reports", 0)),
        ("BUI Add-ins",  len(master.get("components", {}).get("buiAddins", []))),
        ("Ext. APIs",    len(summary.get("externalEndpoints", []))),
    ]
    stats_html = "".join(
        f'<div class="stat-chip"><span class="stat-val">{v}</span><span class="stat-lbl">{k}</span></div>'
        for k, v in stats
    )
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSVC Architect Graph</title>
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/dist/vis-network.min.js"></script>
<link href="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/dist/vis-network.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0A0A14; color: #E2E8F0; font-family: 'Inter', sans-serif;
       height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
header {{
  background: linear-gradient(135deg, #12012A 0%, #1A0308 100%);
  border-bottom: 1px solid rgba(153,0,38,0.4);
  padding: 12px 20px;
  display: flex; align-items: center; gap: 16px; flex-shrink: 0;
  box-shadow: 0 2px 20px rgba(0,0,0,0.5);
}}
.brand-badge {{
  background: linear-gradient(135deg,#990026,#660019);
  color: #fff; font-size: 9px; font-weight: 800; letter-spacing: 1px;
  padding: 4px 8px; border-radius: 4px; text-transform: uppercase;
}}
.brand-title {{ font-size: 15px; font-weight: 800; color: #fff; white-space: nowrap; }}
.instance-name {{ font-size: 11px; color: #94A3B8; font-family: 'JetBrains Mono', monospace;
                  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.stats {{ display: flex; gap: 8px; flex-shrink: 0; }}
.stat-chip {{
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px; padding: 4px 10px; display: flex; flex-direction: column; align-items: center;
}}
.stat-val {{ font-size: 14px; font-weight: 800; color: #F8F8FF; }}
.stat-lbl {{ font-size: 9px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }}
.toolbar {{ display: flex; gap: 6px; flex-shrink: 0; }}
.tool-btn {{
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: #CBD5E1; border-radius: 5px; padding: 5px 10px; font-size: 10px;
  font-weight: 700; cursor: pointer; letter-spacing: 0.5px; transition: all 0.15s;
}}
.tool-btn:hover {{ background: rgba(153,0,38,0.3); border-color: rgba(153,0,38,0.6); color: #fff; }}
.tool-btn.active {{ background: rgba(153,0,38,0.4); border-color: #990026; color: #fff; }}
#search-box {{
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: #E2E8F0; border-radius: 5px; padding: 5px 10px; font-size: 11px;
  outline: none; width: 180px;
}}
#search-box:focus {{ border-color: rgba(153,0,38,0.6); }}
.app-body {{ display: flex; flex: 1; overflow: hidden; }}
/* Sidebar */
.sidebar {{
  width: 200px; flex-shrink: 0;
  background: rgba(10,10,20,0.9); border-right: 1px solid rgba(255,255,255,0.07);
  display: flex; flex-direction: column; overflow-y: auto; padding: 16px 12px;
}}
.sidebar-title {{
  font-size: 9px; font-weight: 800; color: #64748B; letter-spacing: 1px;
  text-transform: uppercase; margin-bottom: 10px; padding-bottom: 6px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}}
.legend-item {{
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
  cursor: pointer; padding: 5px 7px; border-radius: 5px; transition: background 0.15s;
}}
.legend-item:hover {{ background: rgba(255,255,255,0.05); }}
.legend-item.hidden {{ opacity: 0.35; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
.legend-label {{ font-size: 11px; color: #94A3B8; font-weight: 500; }}
.legend-count {{ font-size: 10px; color: #475569; margin-left: auto; }}
.sidebar-sep {{ border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 12px 0; }}
/* Graph */
#network-container {{ flex: 1; position: relative; }}
#graph {{ width: 100%; height: 100%; }}
.graph-hint {{
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px; padding: 5px 14px; font-size: 10px; color: #64748B;
  pointer-events: none;
}}
/* Detail panel */
.detail-panel {{
  width: 0; overflow: hidden; transition: width 0.25s ease;
  background: rgba(10,10,20,0.95); border-left: 1px solid rgba(255,255,255,0.07);
  display: flex; flex-direction: column;
}}
.detail-panel.open {{ width: 290px; }}
.dp-header {{
  padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.07);
  display: flex; align-items: flex-start; justify-content: space-between;
}}
.dp-close {{
  background: none; border: none; color: #64748B; font-size: 16px;
  cursor: pointer; padding: 2px 6px; border-radius: 3px;
}}
.dp-close:hover {{ color: #fff; }}
.dp-group {{
  font-size: 9px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
  padding: 2px 7px; border-radius: 3px; margin-bottom: 4px; display: inline-block;
}}
.dp-name {{ font-size: 14px; font-weight: 700; color: #F8F8FF; line-height: 1.3; }}
.dp-body {{ padding: 16px; flex: 1; overflow-y: auto; }}
.dp-section {{ margin-bottom: 16px; }}
.dp-section-title {{
  font-size: 9px; font-weight: 700; color: #475569;
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;
}}
.dp-row {{ display: flex; gap: 8px; margin-bottom: 4px; align-items: flex-start; }}
.dp-key {{ font-size: 10px; color: #64748B; width: 70px; flex-shrink: 0; padding-top: 1px; }}
.dp-val {{ font-size: 11px; color: #CBD5E1; font-family: 'JetBrains Mono', monospace;
           word-break: break-all; line-height: 1.4; }}
.dp-tag {{
  display: inline-block; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 3px;
  padding: 1px 6px; font-size: 10px; color: #94A3B8; margin: 2px 2px 0 0;
  font-family: 'JetBrains Mono', monospace;
}}
.connected-node {{
  display: flex; align-items: center; gap: 6px; padding: 5px 8px;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 5px; margin-bottom: 4px; cursor: pointer; transition: background 0.15s;
}}
.connected-node:hover {{ background: rgba(255,255,255,0.07); }}
.cn-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.cn-label {{ font-size: 10px; color: #94A3B8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
</style>
</head>
<body>
<header>
  <span class="brand-badge">OSVC</span>
  <div class="brand-title">Architect Graph</div>
  <div class="instance-name">{ver}</div>
  <div class="stats">{stats_html}</div>
  <div class="toolbar">
    <button class="tool-btn" onclick="fitGraph()">FIT VIEW</button>
    <button class="tool-btn active" id="physicsBtn" onclick="togglePhysics()">PHYSICS ON</button>
    <button class="tool-btn" onclick="exportPNG()">EXPORT PNG</button>
  </div>
  <input id="search-box" type="search" placeholder="Search nodes..." oninput="searchNodes(this.value)">
</header>
<div class="app-body">
  <div class="sidebar">
    <div class="sidebar-title">Node Types</div>
    <div id="legend"></div>
    <hr class="sidebar-sep">
    <div class="sidebar-title" style="margin-top:0">Graph Info</div>
    <div style="font-size:11px;color:#64748B;line-height:1.6;">
      <div>Exported: {exported}</div>
      <div id="node-count" style="margin-top:4px;"></div>
      <div id="edge-count"></div>
    </div>
  </div>
  <div id="network-container">
    <div id="graph"></div>
    <div class="graph-hint">Scroll to zoom  &middot;  Drag to pan  &middot;  Click node for details</div>
  </div>
  <div class="detail-panel" id="detailPanel">
    <div class="dp-header">
      <div id="dp-header-content"></div>
      <button class="dp-close" onclick="closeDetail()">&#x2715;</button>
    </div>
    <div class="dp-body" id="dp-body"></div>
  </div>
</div>
<script>
const RAW_NODES = {nodes_json};
const RAW_EDGES = {edges_json};

const GROUP_META = {{
  instance:  {{ label: 'Instance',    color: '#CC0033', shape: 'star' }},
  interface: {{ label: 'Interface',   color: '#7C3AED', shape: 'diamond' }},
  object:    {{ label: 'Object Type', color: '#1D6ECA', shape: 'hexagon' }},
  workspace: {{ label: 'Workspace',   color: '#0891B2', shape: 'square' }},
  procedure: {{ label: 'CPM Proc.',   color: '#EA580C', shape: 'ellipse' }},
  report:    {{ label: 'Report',      color: '#16A34A', shape: 'database' }},
  bui:       {{ label: 'BUI Add-in',  color: '#D97706', shape: 'triangle' }},
  external:  {{ label: 'External API',color: '#64748B', shape: 'box' }},
}};

const visGroups = {{}};
Object.keys(GROUP_META).forEach(g => {{
  const m = GROUP_META[g];
  visGroups[g] = {{
    color: {{ background: m.color + '22', border: m.color, highlight: {{ background: m.color + '44', border: m.color }}, hover: {{ background: m.color + '33', border: m.color }} }},
    font: {{ color: '#E2E8F0', size: 11, face: 'Inter' }},
    borderWidth: 2, borderWidthSelected: 3,
  }};
}});

const hiddenGroups = new Set();
let physicsOn = true;
let network;

function buildDatasets() {{
  const nodeArr = RAW_NODES.filter(n => !hiddenGroups.has(n.group));
  const visibleIds = new Set(nodeArr.map(n => n.id));
  const edgeArr = RAW_EDGES.filter(e => visibleIds.has(e.from) && visibleIds.has(e.to));
  return {{ nodeArr, edgeArr }};
}}

function initGraph() {{
  const container = document.getElementById('graph');
  const {{ nodeArr, edgeArr }} = buildDatasets();
  const nodesDS = new vis.DataSet(nodeArr);
  const edgesDS = new vis.DataSet(edgeArr);
  const data = {{ nodes: nodesDS, edges: edgesDS }};
  const options = {{
    groups: visGroups,
    physics: {{
      enabled: true,
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {{ gravitationalConstant: -60, centralGravity: 0.01, springLength: 120, springConstant: 0.06, damping: 0.4, avoidOverlap: 0.5 }},
      stabilization: {{ iterations: 180, fit: true }},
    }},
    edges: {{
      arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
      color: {{ color: '#334155', highlight: '#990026', hover: '#64748B', opacity: 0.7 }},
      font: {{ color: '#475569', size: 9, face: 'JetBrains Mono', strokeWidth: 0, align: 'middle' }},
      smooth: {{ type: 'continuous', roundness: 0.15 }},
      width: 1.2,
    }},
    nodes: {{
      font: {{ color: '#E2E8F0', size: 11, face: 'Inter', multi: 'html' }},
      shadow: {{ enabled: true, color: 'rgba(0,0,0,0.5)', size: 8, x: 2, y: 2 }},
    }},
    interaction: {{
      hover: true, tooltipDelay: 150,
      navigationButtons: false, keyboard: true,
      hideEdgesOnDrag: true,
    }},
    layout: {{ improvedLayout: true }},
  }};
  network = new vis.Network(container, data, options);
  network._nodesDS = nodesDS;
  network._edgesDS = edgesDS;

  network.on('click', params => {{
    if (params.nodes.length > 0) {{
      showDetail(params.nodes[0]);
    }} else {{
      closeDetail();
    }}
  }});

  document.getElementById('node-count').textContent = 'Nodes: ' + nodeArr.length;
  document.getElementById('edge-count').textContent  = 'Edges: ' + edgeArr.length;
}}

function fitGraph() {{ if (network) network.fit({{ animation: {{ duration: 500, easingFunction: 'easeInOutQuad' }} }}); }}

function togglePhysics() {{
  physicsOn = !physicsOn;
  if (network) network.setOptions({{ physics: {{ enabled: physicsOn }} }});
  const btn = document.getElementById('physicsBtn');
  btn.textContent = physicsOn ? 'PHYSICS ON' : 'PHYSICS OFF';
  btn.classList.toggle('active', physicsOn);
}}

function exportPNG() {{
  if (!network) return;
  const canvas = document.querySelector('#graph canvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = 'osvc_architect_graph.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
}}

function searchNodes(q) {{
  if (!network) return;
  q = q.trim().toLowerCase();
  if (!q) {{ network.unselectAll(); return; }}
  const found = RAW_NODES.filter(n => n.label.toLowerCase().includes(q) || (n.title||'').toLowerCase().includes(q)).map(n => n.id);
  network.selectNodes(found);
  if (found.length > 0) network.focus(found[0], {{ scale: 1.4, animation: true }});
}}

function buildLegend() {{
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  const counts = {{}};
  RAW_NODES.forEach(n => {{ counts[n.group] = (counts[n.group] || 0) + 1; }});
  Object.keys(GROUP_META).forEach(g => {{
    if (!counts[g]) return;
    const m = GROUP_META[g];
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.id = 'legend-' + g;
    item.innerHTML = `<div class="legend-dot" style="background:${{m.color}}"></div>
      <span class="legend-label">${{m.label}}</span>
      <span class="legend-count">${{counts[g]}}</span>`;
    item.onclick = () => toggleGroup(g);
    legend.appendChild(item);
  }});
}}

function toggleGroup(g) {{
  if (hiddenGroups.has(g)) hiddenGroups.delete(g);
  else hiddenGroups.add(g);
  document.getElementById('legend-' + g).classList.toggle('hidden', hiddenGroups.has(g));
  refreshGraph();
}}

function refreshGraph() {{
  if (!network) return;
  const {{ nodeArr, edgeArr }} = buildDatasets();
  network._nodesDS.clear();
  network._edgesDS.clear();
  network._nodesDS.add(nodeArr);
  network._edgesDS.add(edgeArr);
  document.getElementById('node-count').textContent = 'Nodes: ' + nodeArr.length;
  document.getElementById('edge-count').textContent  = 'Edges: ' + edgeArr.length;
}}

const nodeInfoMap = {{}};
RAW_NODES.forEach(n => {{ nodeInfoMap[n.id] = n; }});

function showDetail(nodeId) {{
  const n = nodeInfoMap[nodeId];
  if (!n) return;
  const m = GROUP_META[n.group] || {{}};
  const panel = document.getElementById('detailPanel');
  panel.classList.add('open');

  const hdr = document.getElementById('dp-header-content');
  hdr.innerHTML = `<div class="dp-group" style="background:${{m.color}}22;color:${{m.color}};border:1px solid ${{m.color}}44">${{m.label || n.group}}</div>
    <div class="dp-name">${{n.label.replace(/\\n/g, ' ')}}</div>`;

  // Connected nodes
  const connectedEdges = RAW_EDGES.filter(e => e.from === nodeId || e.to === nodeId);
  const connectedIds = new Set();
  const edgeDetails = [];
  connectedEdges.forEach(e => {{
    const otherId = e.from === nodeId ? e.to : e.from;
    const dir = e.from === nodeId ? 'out' : 'in';
    connectedIds.add(otherId);
    edgeDetails.push({{ id: otherId, label: e.label || '', dir }});
  }});

  const body = document.getElementById('dp-body');
  let html = '';

  // Tooltip lines as key-value
  if (n.title) {{
    html += '<div class="dp-section"><div class="dp-section-title">Details</div>';
    n.title.split('\\n').forEach(line => {{
      if (!line.trim()) return;
      const parts = line.split(': ');
      if (parts.length >= 2) {{
        html += `<div class="dp-row"><span class="dp-key">${{parts[0]}}</span><span class="dp-val">${{parts.slice(1).join(': ')}}</span></div>`;
      }} else {{
        html += `<div class="dp-row"><span class="dp-val">${{line}}</span></div>`;
      }}
    }});
    html += '</div>';
  }}

  if (edgeDetails.length > 0) {{
    html += '<div class="dp-section"><div class="dp-section-title">Connections (' + edgeDetails.length + ')</div>';
    edgeDetails.forEach(ed => {{
      const cn = nodeInfoMap[ed.id];
      if (!cn) return;
      const cm = GROUP_META[cn.group] || {{}};
      const arrow = ed.dir === 'out' ? '&rarr;' : '&larr;';
      html += `<div class="connected-node" onclick="showDetail(${{ed.id}})">
        <div class="cn-dot" style="background:${{cm.color || '#64748B'}}"></div>
        <span class="cn-label">${{arrow}} ${{ed.label ? '['+ed.label+'] ' : ''}}${{cn.label.replace(/\\n/g,' ')}}</span>
      </div>`;
    }});
    html += '</div>';
  }}

  body.innerHTML = html || '<div style="color:#475569;font-size:12px;">No additional details.</div>';
}}

function closeDetail() {{
  document.getElementById('detailPanel').classList.remove('open');
}}

buildLegend();
initGraph();
</script>
</body>
</html>"""


@app.route("/api/generate-architect-report", methods=["POST"])
def generate_architect_report():
    master_json_path = os.path.join(RESULTS_DIR, "master.json")
    if not os.path.exists(master_json_path):
        return jsonify({"success": False, "error": "master.json not found. Run analysis first."}), 404
    try:
        from graph_ui.build import build_graph_ui
        graph_dir = os.path.join(RESULTS_DIR, "graph")
        index_path = build_graph_ui(master_json_path, graph_dir)
        return jsonify({"success": True, "path": "/results/graph/index.html"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"[START] OSVC Platform Server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)