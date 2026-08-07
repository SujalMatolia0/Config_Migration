import os
import sys
import tempfile
import zipfile
import io
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Add field_extractor directory to Python path if needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from excel_exporter import (
    _enrich_workspace_fields,
    _field_type_from_obj,
    _field_type_from_ws_id,
    _obj_field_key,
    _format_option,
    write_workspaces_excel,
    write_objects_excel,
    write_combined_excel,
)
from osvc_rest_fetcher import fetch_standard_objects_via_rest

app = Flask(__name__, template_folder=os.path.join(CURRENT_DIR, "templates"))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max upload limit

# Global store for current session outputs
RESULTS_CACHE = {
    "workspaces": [],
    "objects_map": {},
    "output_dir": None,
    "summary": {},
    "logs": []
}

def add_log(msg, level="INFO"):
    t_str = datetime.now().strftime("%H:%M:%S")
    entry = f"[{t_str}] [{level}] {msg}"
    print(entry)
    RESULTS_CACHE["logs"].append(entry)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": RESULTS_CACHE["logs"]})

@app.route("/api/logs/clear", methods=["POST"])
def clear_logs():
    RESULTS_CACHE["logs"] = []
    add_log("Log history cleared.", "INFO")
    return jsonify({"success": True})

@app.route("/api/load_sample", methods=["POST"])
def load_sample():
    """Loads sample input files from field_extractor/sample_inputs."""
    add_log("Loading sample input files...", "INFO")
    sample_dir = os.path.join(CURRENT_DIR, "sample_inputs")
    if not os.path.exists(sample_dir):
        add_log("Sample inputs directory not found.", "ERROR")
        return jsonify({"success": False, "error": "Sample inputs directory not found."}), 404

    ws_files = []
    obj_files = []
    for f in os.listdir(sample_dir):
        if f.endswith(".xml") and not f.startswith("."):
            full_path = os.path.join(sample_dir, f)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handle:
                    content = file_handle.read(2048)
                if "<CustomObject" in content or "<Fields>" in content:
                    obj_files.append(full_path)
                elif "<Workspace" in content:
                    ws_files.append(full_path)
            except Exception:
                pass

    add_log(f"Found {len(ws_files)} workspace XML(s) and {len(obj_files)} object XML(s) in sample_inputs", "INFO")
    return _process_xml_files(ws_files, obj_files)

@app.route("/api/fetch_rest_schemas", methods=["POST"])
def fetch_rest_schemas():
    """
    STRICT READ-ONLY: Fetches standard object schemas directly from OSVC Connect REST API
    using HTTP GET requests ONLY.
    """
    data = request.json or {}
    host = data.get("host", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    include_custom = bool(data.get("include_custom", False))

    add_log("Received REST extraction request (STRICT HTTP GET ONLY)", "INFO")

    if not host or not username or not password:
        add_log("Missing required credentials (host/username/password)", "ERROR")
        return jsonify({
            "success": False,
            "error": "Host URL, Username, and Password are required."
        }), 400

    try:
        fetched_objects = fetch_standard_objects_via_rest(
            host=host,
            username=username,
            password=password,
            include_custom=include_custom,
            log_cb=add_log
        )

        if not fetched_objects:
            add_log("No standard object schemas returned from REST API.", "WARNING")
            return jsonify({
                "success": False,
                "error": "No standard object schemas could be extracted from the specified OSVC instance."
            }), 404

        existing_ws = RESULTS_CACHE.get("workspaces") or []
        if not existing_ws:
            sample_dir = os.path.join(CURRENT_DIR, "sample_inputs")
            if os.path.exists(sample_dir):
                for f in os.listdir(sample_dir):
                    if f.endswith(".xml") and "Workspace" in f:
                        try:
                            existing_ws.append(parse_workspace_xml(os.path.join(sample_dir, f)))
                        except Exception:
                            pass

        out_dir = os.path.join(CURRENT_DIR, "results")
        os.makedirs(out_dir, exist_ok=True)

        ws_xlsx_path = os.path.join(out_dir, "workspaces.xlsx")
        obj_xlsx_path = os.path.join(out_dir, "objects.xlsx")
        comb_xlsx_path = os.path.join(out_dir, "combined.xlsx")

        write_workspaces_excel(existing_ws, fetched_objects, ws_xlsx_path)
        write_objects_excel(fetched_objects, obj_xlsx_path)
        write_combined_excel(existing_ws, fetched_objects, comb_xlsx_path)

        RESULTS_CACHE["workspaces"] = existing_ws
        RESULTS_CACHE["objects_map"] = fetched_objects
        RESULTS_CACHE["output_dir"] = out_dir

        add_log(f"Generated Excel workbooks in: {out_dir}", "SUCCESS")

        # Build JSON preview
        preview_objects = []
        for o_name, o_data in fetched_objects.items():
            disp_name = o_data.get("object_name", o_name)
            rows = []
            for of in o_data.get("fields", []):
                rows.append({
                    "field_key": _obj_field_key(of),
                    "field_label": of.get("field_label", ""),
                    "data_type": of.get("data_type", ""),
                    "field_type": _field_type_from_obj(of),
                    "is_nullable": "Yes" if of.get("is_nullable") else "No",
                    "is_lookup": "Yes" if of.get("is_lookup") else "No",
                    "is_readonly": "Yes" if of.get("is_readonly") else "No",
                    "max_length": of.get("max_length", "-"),
                    "description": of.get("description", "")
                })
            preview_objects.append({
                "object_name": disp_name,
                "field_count": len(rows),
                "rows": rows
            })

        preview_workspaces = []
        preview_combined = []
        for ws_data in existing_ws:
            bound_obj = ws_data.get("bound_object", "Contact")
            enriched = _enrich_workspace_fields(ws_data.get("fields", []), fetched_objects, bound_obj)
            rows = []
            for item in enriched:
                rows.append({
                    "bound_object": item["bound_object"],
                    "target_object": item["target_object"],
                    "object_field_name": item["obj_field_key"],
                    "field_label": item["field_label"],
                    "location_tab": item["location_tab"],
                    "workspace_tab": item["location_tab"],
                    "required": item["required_fmt"],
                    "readonly": item["readonly_fmt"],
                    "data_type": item["data_type"],
                    "field_type": item["field_type"],
                    "is_nullable": item["is_nullable"],
                    "is_lookup": item["is_lookup"],
                    "max_length": item["max_length"],
                    "in_layout": "Yes"
                })
            preview_workspaces.append({
                "workspace_name": ws_data["workspace_name"],
                "bound_object": bound_obj,
                "field_count": len(rows),
                "rows": rows
            })
            preview_combined.append({
                "workspace_name": ws_data["workspace_name"],
                "bound_object": bound_obj,
                "field_count": len(rows),
                "rows": rows
            })

        summary = {
            "workspace_count": len(existing_ws),
            "object_count": len(fetched_objects),
            "total_workspace_fields": sum(len(w.get("fields", [])) for w in existing_ws),
            "total_object_fields": sum(len(o.get("fields", [])) for o in fetched_objects.values()),
            "skipped_files": 0
        }
        RESULTS_CACHE["summary"] = summary

        return jsonify({
            "success": True,
            "summary": summary,
            "workspaces": preview_workspaces,
            "objects": preview_objects,
            "combined": preview_combined
        })

    except Exception as err:
        tb = traceback.format_exc()
        add_log(f"REST API Connection error: {str(err)}", "ERROR")
        add_log(tb, "TRACEBACK")
        return jsonify({
            "success": False,
            "error": f"REST API Connection error: {str(err)}",
            "traceback": tb
        }), 200

@app.route("/api/extract", methods=["POST"])
def extract_files():
    """Handles file uploads for Workspace XMLs and Object XMLs."""
    uploaded_ws_files = request.files.getlist("workspace_files")
    uploaded_obj_files = request.files.getlist("object_files")

    if not uploaded_ws_files and not uploaded_obj_files:
        return jsonify({"success": False, "error": "No XML files uploaded."}), 400

    temp_dir = tempfile.mkdtemp(prefix="field_extractor_upload_")
    ws_temp_paths = []
    obj_temp_paths = []

    for f in uploaded_ws_files:
        if f and f.filename and f.filename.endswith(".xml"):
            s_name = secure_filename(f.filename) or "workspace.xml"
            dest = os.path.join(temp_dir, f"ws_{s_name}")
            f.save(dest)
            ws_temp_paths.append(dest)

    for f in uploaded_obj_files:
        if f and f.filename and f.filename.endswith(".xml"):
            s_name = secure_filename(f.filename) or "object.xml"
            dest = os.path.join(temp_dir, f"obj_{s_name}")
            f.save(dest)
            obj_temp_paths.append(dest)

    add_log(f"Uploaded {len(ws_temp_paths)} workspace file(s) and {len(obj_temp_paths)} object file(s)", "INFO")
    return _process_xml_files(ws_temp_paths, obj_temp_paths)


def _process_xml_files(ws_file_paths, obj_file_paths):
    """Processes workspace and object XML file paths, generates Excel files, and returns preview data."""
    parsed_objects = {}
    for o_path in obj_file_paths:
        try:
            o_data = parse_object_xml(o_path)
            obj_name = o_data.get("object_name", "")
            if obj_name:
                parsed_objects[obj_name.lower()] = o_data
                add_log(f"Parsed Object XML: {obj_name} ({len(o_data.get('fields', []))} fields)", "INFO")
        except Exception as e:
            add_log(f"Skipped non-valid Object XML: {os.path.basename(o_path)}", "WARNING")

    parsed_workspaces = []
    skipped_count = 0
    for w_path in ws_file_paths:
        try:
            w_data = parse_workspace_xml(w_path)
            parsed_workspaces.append(w_data)
            add_log(f"Parsed Workspace XML: {w_data['workspace_name']} ({len(w_data.get('fields', []))} fields)", "INFO")
        except Exception as e:
            skipped_count += 1
            add_log(f"Skipped non-valid Workspace XML: {os.path.basename(w_path)}", "WARNING")

    if not parsed_workspaces and not parsed_objects:
        add_log("No valid Workspace or Object XML files parsed.", "ERROR")
        return jsonify({
            "success": False,
            "error": "Failed to parse any valid Workspace or Object XML files."
        }), 400

    out_dir = os.path.join(CURRENT_DIR, "results")
    os.makedirs(out_dir, exist_ok=True)

    ws_xlsx_path = os.path.join(out_dir, "workspaces.xlsx")
    obj_xlsx_path = os.path.join(out_dir, "objects.xlsx")
    comb_xlsx_path = os.path.join(out_dir, "combined.xlsx")

    write_workspaces_excel(parsed_workspaces, parsed_objects, ws_xlsx_path)
    write_objects_excel(parsed_objects, obj_xlsx_path)
    write_combined_excel(parsed_workspaces, parsed_objects, comb_xlsx_path)

    RESULTS_CACHE["workspaces"] = parsed_workspaces
    RESULTS_CACHE["objects_map"] = parsed_objects
    RESULTS_CACHE["output_dir"] = out_dir

    add_log("Generated Excel files: workspaces.xlsx, objects.xlsx, combined.xlsx", "SUCCESS")

    # Build JSON preview payload for the UI
    preview_workspaces = []
    for ws_data in parsed_workspaces:
        bound_obj = ws_data.get("bound_object", "Contact")
        enriched = _enrich_workspace_fields(ws_data.get("fields", []), parsed_objects, bound_obj)
        rows = []
        for item in enriched:
            rows.append({
                "bound_object": item["bound_object"],
                "target_object": item["target_object"],
                "object_field_name": item["obj_field_key"],
                "field_label": item["field_label"],
                "location_tab": item["location_tab"],
                "required": item["required_fmt"],
                "readonly": item["readonly_fmt"],
                "data_type": item["data_type"],
                "field_type": item["field_type"],
                "is_nullable": item["is_nullable"],
                "is_lookup": item["is_lookup"],
                "max_length": item["max_length"],
            })
        preview_workspaces.append({
            "workspace_name": ws_data["workspace_name"],
            "bound_object": bound_obj,
            "field_count": len(rows),
            "rows": rows
        })

    preview_objects = []
    for o_name, o_data in parsed_objects.items():
        disp_name = o_data.get("object_name", o_name)
        rows = []
        for of in o_data.get("fields", []):
            rows.append({
                "field_key": _obj_field_key(of),
                "field_label": of.get("field_label", ""),
                "data_type": of.get("data_type", ""),
                "field_type": _field_type_from_obj(of),
                "is_nullable": "Yes" if of.get("is_nullable") else "No",
                "is_lookup": "Yes" if of.get("is_lookup") else "No",
                "is_readonly": "Yes" if of.get("is_readonly") else "No",
                "max_length": of.get("max_length", "-"),
                "description": of.get("description", "")
            })
        preview_objects.append({
            "object_name": disp_name,
            "field_count": len(rows),
            "rows": rows
        })

    preview_combined = []
    for ws_data in parsed_workspaces:
        bound_obj = ws_data.get("bound_object", "Contact")
        enriched = _enrich_workspace_fields(ws_data.get("fields", []), parsed_objects, bound_obj)
        rows = []
        for item in enriched:
            rows.append({
                "bound_object": item["bound_object"],
                "target_object": item["target_object"],
                "object_field_name": item["obj_field_key"],
                "field_label": item["field_label"],
                "workspace_tab": item["location_tab"],
                "required": item["required_fmt"],
                "readonly": item["readonly_fmt"],
                "data_type": item["data_type"],
                "field_type": item["field_type"],
                "is_nullable": item["is_nullable"],
                "is_lookup": item["is_lookup"],
                "max_length": item["max_length"],
                "in_layout": "Yes"
            })
        preview_combined.append({
            "workspace_name": ws_data["workspace_name"],
            "bound_object": bound_obj,
            "field_count": len(rows),
            "rows": rows
        })

    summary = {
        "workspace_count": len(parsed_workspaces),
        "object_count": len(parsed_objects),
        "total_workspace_fields": sum(len(w.get("fields", [])) for w in parsed_workspaces),
        "total_object_fields": sum(len(o.get("fields", [])) for o in parsed_objects.values()),
        "skipped_files": skipped_count
    }
    RESULTS_CACHE["summary"] = summary

    return jsonify({
        "success": True,
        "summary": summary,
        "workspaces": preview_workspaces,
        "objects": preview_objects,
        "combined": preview_combined
    })

@app.route("/api/download/<filename>")
def download_file(filename):
    """Downloads generated Excel files or ZIP package."""
    out_dir = RESULTS_CACHE.get("output_dir") or os.path.join(CURRENT_DIR, "results")

    if filename in ["workspaces.xlsx", "objects.xlsx", "combined.xlsx"]:
        file_path = os.path.join(out_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({"error": f"File {filename} not found."}), 404

    if filename == "all_reports.zip":
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for fname in ["workspaces.xlsx", "objects.xlsx", "combined.xlsx"]:
                fpath = os.path.join(out_dir, fname)
                if os.path.exists(fpath):
                    z.write(fpath, arcname=fname)
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="OSVC_Field_Extractor_Excel_Reports.zip"
        )

    return jsonify({"error": "Invalid file request."}), 400


def run_server(port=5050, debug=False):
    add_log(f"Field Extractor Web UI Server running on port {port}", "INFO")
    print("==========================================================================")
    print(f"       OSVC FIELD EXTRACTOR WEB UI SERVER RUNNING ON PORT {port}")
    print(f"       Open browser to: http://localhost:{port}")
    print("==========================================================================")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    port_arg = 5050
    if len(sys.argv) > 1:
        try:
            port_arg = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port=port_arg)
