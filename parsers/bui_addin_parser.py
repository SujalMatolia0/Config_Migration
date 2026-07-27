import os
import re
import zipfile

def normalize_field_name(field_str):
    """
    Normalizes field names case-insensitively while preserving standard OSVC casing (e.g. C$ -> c$).
    """
    if not isinstance(field_str, str):
        return field_str
    parts = field_str.split(".")
    norm_parts = []
    for p in parts:
        if p.startswith("C$"):
            p = "c$" + p[2:]
        norm_parts.append(p)
    return ".".join(norm_parts)

def parse_bui_addin(target_path):
    """
    Statically analyzes OSVC BUI (Browser UI) Add-In packages (ZIP archives or folders).
    Extracts entry points, scripts, field reads/writes, field listeners, lifecycle hooks,
    editor commands, report dependencies, CP/REST API endpoints, modal views with dimensions,
    workspace operations, extension IDs, and risk flags.
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"BUI Add-In path not found: {target_path}")

    addin_name = os.path.basename(target_path).replace(".zip", "").replace(".ZIP", "")
    files_map = {}  # filename -> content string

    if os.path.isfile(target_path) and target_path.lower().endswith(".zip"):
        with zipfile.ZipFile(target_path, 'r') as z:
            for item in z.infolist():
                if item.is_dir():
                    continue
                filename = os.path.basename(item.filename)
                if not filename or filename.startswith("."):
                    continue
                try:
                    raw_bytes = z.read(item)
                    content = raw_bytes.decode('utf-8', errors='ignore')
                    files_map[item.filename] = content
                except Exception:
                    pass
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for f in files:
                if f.startswith("."):
                    continue
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, target_path)
                try:
                    with open(full_p, 'r', encoding='utf-8', errors='ignore') as fp:
                        files_map[rel_p] = fp.read()
                except Exception:
                    pass
    else:
        try:
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as fp:
                files_map[addin_name] = fp.read()
        except Exception:
            pass

    entry_point = "Unknown"
    html_files = []
    js_files = []
    css_files = []

    for path_key in files_map.keys():
        lower_p = path_key.lower()
        if lower_p.endswith(".html") or lower_p.endswith(".htm"):
            html_files.append(path_key)
            if "init.html" in lower_p or "index.html" in lower_p:
                entry_point = path_key
        elif lower_p.endswith(".js"):
            js_files.append(path_key)
        elif lower_p.endswith(".css"):
            css_files.append(path_key)

    if entry_point == "Unknown":
        for path_key, content in files_map.items():
            if "registerWorkspaceExtension" in content or "ORACLE_SERVICE_CLOUD" in content:
                entry_point = path_key
                break
        if entry_point == "Unknown" and html_files:
            entry_point = html_files[0]

    all_file_names = list(files_map.keys())

    osvc_fields_read_map = {}     # lower -> norm
    osvc_fields_written_map = {}  # lower -> norm
    field_listeners_map = {}      # lower -> norm
    lifecycle_listeners = set()
    editor_commands = set()
    report_ids = set()
    api_calls = []
    modal_views_details = []
    modal_views = set()
    workspace_objects_opened = set()
    external_dependencies = set()
    external_libraries = set()
    extension_ids_registered = {}  # file -> set of app IDs
    extension_ids_closed = {}      # file -> set of app IDs
    risk_flags = []

    read_patterns = [
        r'getFieldValues\s*\(\s*\[\s*["\']([^"\']+)["\']',
        r'getField\s*\(\s*["\']([^"\']+)["\']',
        r'getValue\s*\(\s*["\']([^"\']+)["\']',
        r'extensionProvider\.getGlobalContext\(\)\.getField\s*\(\s*["\']([^"\']+)["\']',
        r'["\']((?:Incident|Contact|Organization|CO\$\w+)\.[a-zA-Z0-9_\$]+)["\']'
    ]

    write_patterns = [
        r'updateField\s*\(\s*["\']([^"\']+)["\']',
        r'setFieldValue\s*\(\s*["\']([^"\']+)["\']',
        r'setValue\s*\(\s*["\']([^"\']+)["\']',
        r'field\.setValue\s*\(\s*["\']([^"\']+)["\']'
    ]

    listener_patterns = [
        r'addFieldValueListener\s*\(\s*["\']([^"\']+)["\']',
        r'onFieldChange\s*\(\s*["\']([^"\']+)["\']',
        r'subscribe\s*\(\s*["\']([^"\']+)["\']'
    ]

    report_patterns = [
        r'ContactLookupSearchReportID\s*=\s*(\d+)',
        r'ReportID\s*=\s*(\d+)',
        r'report_id\s*[:=]\s*(\d+)',
        r'"id"\s*:\s*(\d{4,6})',
        r'analyticsReportResults.*?["\']?id["\']?\s*:\s*(\d+)'
    ]

    script_src_by_html = {}

    for path_key, content in files_map.items():
        lower_p = path_key.lower()

        # HTML inspection
        if lower_p.endswith(".html") or lower_p.endswith(".htm"):
            src_matches = re.findall(r'<script\s+[^>]*src=["\']([^"\']+)["\']', content, re.IGNORECASE)
            script_src_by_html[path_key] = src_matches

            for src in src_matches:
                if src.startswith("../"):
                    external_dependencies.add(src)
                if "jquery" in src.lower():
                    m = re.search(r'jquery[^\/]*?([\d\.]+)?(?:\.min)?\.js', src, re.IGNORECASE)
                    lib_name = m.group(0) if m else "jQuery"
                    external_libraries.add(lib_name)
                elif "jspdf" in src.lower():
                    m = re.search(r'jspdf[^\/]*?([\d\.]+)?(?:\.min)?\.js', src, re.IGNORECASE)
                    lib_name = m.group(0) if m else "jsPDF"
                    external_libraries.add(lib_name)
                elif "autotable" in src.lower():
                    external_libraries.add("jsPDF-AutoTable")

        # Field Reads (with case-insensitive deduplication)
        for pat in read_patterns:
            matches = re.findall(pat, content)
            for m in matches:
                if isinstance(m, str) and ("." in m or "$" in m) and not m.startswith("http"):
                    norm = normalize_field_name(m)
                    osvc_fields_read_map.setdefault(norm.lower(), norm)

        # Field Writes (with case-insensitive deduplication)
        for pat in write_patterns:
            matches = re.findall(pat, content)
            for m in matches:
                if isinstance(m, str) and ("." in m or "$" in m):
                    norm = normalize_field_name(m)
                    osvc_fields_written_map.setdefault(norm.lower(), norm)

        # Field Listeners
        for pat in listener_patterns:
            matches = re.findall(pat, content)
            for m in matches:
                if isinstance(m, str) and ("." in m or "$" in m):
                    norm = normalize_field_name(m)
                    field_listeners_map.setdefault(norm.lower(), norm)

        # Workspace Lifecycle Listeners (addRecordSavedListener, etc.)
        if "addRecordSavedListener" in content:
            lifecycle_listeners.add("RecordSaved")
        if "addRecordClosingListener" in content:
            lifecycle_listeners.add("RecordClosing")
        if "addRecordLoadedListener" in content:
            lifecycle_listeners.add("RecordLoaded")
        if "addRecordSavingListener" in content:
            lifecycle_listeners.add("RecordSaving")

        # Editor Commands (executeEditorCommand('Save'), etc.)
        cmd_matches = re.findall(r'executeEditorCommand\s*\(\s*["\']([^"\']+)["\']', content)
        for cmd in cmd_matches:
            editor_commands.add(cmd)

        # Extension IDs registered or closed
        reg_ids = re.findall(r'extension_loader\.load\s*\(\s*["\']([^"\']+)["\']', content)
        if not reg_ids:
            reg_ids = re.findall(r'registerWorkspaceExtension\s*\(\s*function\s*\(.*?\).*?["\']?([a-zA-Z0-9_\-]+)["\']?\s*\)', content, re.DOTALL)
        if not reg_ids:
            reg_ids = re.findall(r'extensionProvider\.registerWorkspaceExtension\s*\(\s*["\']([^"\']+)["\']', content)
        if not reg_ids:
            reg_ids = re.findall(r'ORACLE_SERVICE_CLOUD\.extensionProvider\s*\(\s*["\']([^"\']+)["\']', content)

        for r_id in reg_ids:
            if r_id and r_id != "function":
                extension_ids_registered.setdefault(path_key, set()).add(r_id)

        close_ids = re.findall(r'closeModalWindow\s*\(\s*["\']([^"\']+)["\']', content)
        for c_id in close_ids:
            extension_ids_closed.setdefault(path_key, set()).add(c_id)

        # Report IDs
        for pat in report_patterns:
            matches = re.findall(pat, content)
            for m in matches:
                try:
                    val = int(m)
                    if val > 1000:
                        report_ids.add(val)
                except ValueError:
                    pass

        # REST API & CP Controller Endpoint Calls
        if "connect/v1.3/queryResults" in content or "queryResults" in content:
            roql_match = re.search(r'FROM\s+(\w+)', content, re.IGNORECASE)
            tbl = roql_match.group(1) if roql_match else "OSVC Table"
            api_calls.append({
                "method": "GET",
                "endpoint": "connect/v1.3/queryResults",
                "object": tbl,
                "type": "REST API",
                "file": path_key
            })

        if "connect/v1.3/analyticsReportResults" in content or "analyticsReportResults" in content:
            api_calls.append({
                "method": "POST",
                "endpoint": "connect/v1.3/analyticsReportResults",
                "report_id": list(report_ids)[0] if report_ids else None,
                "type": "REST API",
                "file": path_key
            })

        # Customer Portal (CP) Controller Endpoints (e.g. /cc/ajaxCustom/addSrToSiebel)
        cp_matches = re.findall(r'["\']((?:https?://[^"\'\s]+)?/(?:cc|ci|custom|ajaxCustom)/[a-zA-Z0-9_\-/]+)["\']', content)
        if not cp_matches:
            cp_matches = re.findall(r'["\'](ajaxCustom/[a-zA-Z0-9_\-/]+)["\']', content)

        for cp_ep in cp_matches:
            api_calls.append({
                "method": "POST" if ("post" in content.lower() or "add" in cp_ep.lower()) else "GET/POST",
                "endpoint": cp_ep,
                "type": "CP Controller Endpoint",
                "file": path_key
            })

        # Modal Views with Dimensions (supports createModalWindow('url') AND setContentUrl('url'))
        modal_urls = re.findall(r'(?:createModalWindow|setContentUrl)\s*\(\s*["\']([^"\']+)["\']', content)
        for mw in modal_urls:
            clean_mw = mw.lstrip("/").split("?")[0]
            if clean_mw.lower() != os.path.basename(path_key).lower() and clean_mw != entry_point:
                modal_views.add(clean_mw)
                pos = content.find(mw)
                snippet = content[max(0, pos-150):min(len(content), pos+350)]
                w_m = re.search(r'(?:setWidth|width)\s*\(?\s*[:=]?\s*["\']?(\d+)', snippet, re.IGNORECASE)
                h_m = re.search(r'(?:setHeight|height)\s*\(?\s*[:=]?\s*["\']?(\d+)', snippet, re.IGNORECASE)
                dims = f"{w_m.group(1)}x{h_m.group(1)}px" if (w_m and h_m) else "Standard Modal"
                modal_views_details.append({
                    "url": mw.lstrip("/"),
                    "clean_url": clean_mw,
                    "dimensions": dims,
                    "triggered_in": path_key
                })

        # Workspace objects opened
        ws_obj_matches = re.findall(r'(?:editWorkspaceRecord|openWorkspaceRecord|createRecord|openWorkspace)\s*\(\s*["\']([a-zA-Z0-9_\$]+)["\']', content)
        for obj_type in ws_obj_matches:
            workspace_objects_opened.add(obj_type)
        if "editWorkspaceRecord" in content or "openWorkspace" in content:
            for obj in ["Contact", "Org", "Organization", "Incident", "Task"]:
                if obj in content:
                    workspace_objects_opened.add(obj)

        # Risk Auditing Checks
        if re.search(r'async\s*:\s*false', content, re.IGNORECASE):
            risk_flags.append({
                "severity": "medium",
                "type": "Synchronous AJAX",
                "detail": f"Synchronous AJAX (async: false) detected in {path_key} — blocks browser UI thread"
            })

        if re.search(r'CustomFields\.c\.\w+\.LookupName', content):
            risk_flags.append({
                "severity": "medium",
                "type": "Custom Field Schema Dependency",
                "detail": f"Direct CustomFields.c ROQL LookupName query in {path_key} — vulnerable to schema alterations"
            })

    # Deduplicate API calls
    unique_api_calls = []
    seen_api = set()
    for call in api_calls:
        key = (call["method"], call["endpoint"], call.get("object"), call.get("report_id"))
        if key not in seen_api:
            seen_api.add(key)
            unique_api_calls.append(call)

    # Audit check: Duplicate jQuery/libraries loaded in same HTML
    for html_file, src_list in script_src_by_html.items():
        jq_sources = [s for s in src_list if "jquery" in s.lower() and "ui" not in s.lower()]
        if len(jq_sources) > 1:
            risk_flags.append({
                "severity": "high",
                "type": "Duplicate Library Load",
                "detail": f"Duplicate jQuery versions loaded in {html_file}: {', '.join(jq_sources)}"
            })

    # Audit check: Relative path dependencies PER FILE
    for html_file, src_list in script_src_by_html.items():
        for src in src_list:
            if src.startswith("../"):
                risk_flags.append({
                    "severity": "high",
                    "type": "Relative Path Dependency",
                    "detail": f"Relative path script reference '{src}' in {html_file} — will fail if add-in path changes"
                })

    # Audit check: Extension ID mismatch between register and closeModalWindow
    all_registered = set()
    for reg_set in extension_ids_registered.values():
        all_registered.update(reg_set)

    for c_file, c_set in extension_ids_closed.items():
        for c_id in c_set:
            if all_registered and c_id not in all_registered:
                reg_str = ", ".join(f"'{r}'" for r in sorted(list(all_registered)))
                risk_flags.append({
                    "severity": "high",
                    "type": "Extension ID Mismatch",
                    "detail": f"Extension ID mismatch in {c_file}: closeModalWindow specifies '{c_id}', but add-in registered as {reg_str} — modal close operation will fail."
                })

    # Audit check: Hardcoded Report IDs
    for rid in sorted(list(report_ids)):
        risk_flags.append({
            "severity": "medium",
            "type": "Hardcoded Report ID",
            "detail": f"Hardcoded Report ID {rid} in BUI Add-In code — risks silent failure if report ID changes"
        })

    # Audit check: Dead/Unused libraries
    full_combined_text = "\n".join(files_map.values())
    if any("jspdf" in lib.lower() for lib in external_libraries):
        if "jspdf" not in full_combined_text.lower() or "new jspdf" not in full_combined_text.lower():
            risk_flags.append({
                "severity": "low",
                "type": "Unused Library Import",
                "detail": "jsPDF / jsPDF-AutoTable loaded in HTML headers but unreferenced in JavaScript"
            })

    html_previews = {}
    for fk, fc in files_map.items():
        if fk.lower().endswith(".html") or fk.lower().endswith(".htm"):
            html_previews[fk] = fc

    return {
        "name": addin_name,
        "format": "bui_addin",
        "type": "BUIAddin",
        "entry_point": entry_point,
        "files": sorted(all_file_names),
        "html_previews": html_previews,
        "external_dependencies": sorted(list(external_dependencies)),
        "external_libraries": sorted(list(external_libraries)),
        "osvc_fields_read": sorted(list(osvc_fields_read_map.values())),
        "osvc_fields_written": sorted(list(osvc_fields_written_map.values())),
        "field_listeners": sorted(list(field_listeners_map.values())),
        "lifecycle_listeners": sorted(list(lifecycle_listeners)),
        "editor_commands": sorted(list(editor_commands)),
        "report_ids": sorted(list(report_ids)),
        "api_calls": unique_api_calls,
        "modal_views": sorted(list(modal_views)),
        "modal_views_details": modal_views_details,
        "workspace_objects_opened": sorted(list(workspace_objects_opened)),
        "extension_ids_registered": {k: sorted(list(v)) for k, v in extension_ids_registered.items()},
        "risk_flags": risk_flags
    }
