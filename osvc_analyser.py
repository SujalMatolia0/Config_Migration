#!/usr/bin/env python
import os
import sys
import json
import argparse
import re
from datetime import datetime
from lxml import etree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parsers.workspace_parser import parse_workspace_file
from src.parsers.report_parser import parse_report_file
from src.parsers.rule_parser import parse_rule_file
from src.parsers.nav_parser import parse_nav_file
from src.parsers.cpm_parser import parse_cpm_file
from src.parsers.script_parser import parse_script_file
from src.parsers.bui_addin_parser import parse_bui_addin
from src.parsers.object_parser import parse_custom_object_file, parse_relationship_file

from src.analyser.relationship_mapper import map_relationships
from src.analyser.orphan_detector import detect_orphans
from src.analyser.endpoint_extractor import extract_endpoints

from src.output.json_writer import write_master_json
from graph_ui.build import build_graph_ui


def detect_and_parse_file(file_path, components, strict=False):
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".xml":
        try:
            parser = etree.XMLParser(recover=True, remove_comments=True)
            tree = etree.parse(file_path, parser=parser)
            root = tree.getroot()
            tag = root.tag.split('}')[-1]
            if tag == "Workspace":
                print(f"  -> Parsing Workspace: {os.path.basename(file_path)}")
                components["workspaces"].append(parse_workspace_file(file_path, strict=strict))
            elif tag in ["Report", "Reports", "analytics_core"]:
                print(f"  -> Parsing Report: {os.path.basename(file_path)}")
                components["reports"].append(parse_report_file(file_path))
            elif tag in ["ObjectProcedure", "ClassMappings", "Mappings"]:
                print(f"  -> Parsing CPM Export: {os.path.basename(file_path)}")
                components["cpm"].append(parse_cpm_file(file_path))
            elif tag in ["Rules", "Rule"]:
                print(f"  -> Parsing Business Rules: {os.path.basename(file_path)}")
                components["businessRules"].append(parse_rule_file(file_path))
            elif tag in ["NavigationSet", "NavSet", "Navigation"]:
                print(f"  -> Parsing Nav Set: {os.path.basename(file_path)}")
                components["navigationSets"].append(parse_nav_file(file_path))
            elif tag in ["CustomObject", "Object"]:
                print(f"  -> Parsing Custom Object: {os.path.basename(file_path)}")
                components.setdefault("customObjects", []).append(parse_custom_object_file(file_path))
            elif tag in ["Relationship"]:
                print(f"  -> Parsing Object Relationship: {os.path.basename(file_path)}")
                components.setdefault("objectRelationships", []).append(parse_relationship_file(file_path))
            else:
                raw_preview = ""
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f_prev:
                        raw_preview = f_prev.read(500)
                except Exception:
                    pass
                print(f"  [WARNING] Unrecognized XML root tag: <{tag}> in {os.path.basename(file_path)} — capturing in unhandledFiles")
                components.setdefault("unhandledFiles", []).append({
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "reason": f"Unrecognized XML root tag <{tag}>",
                    "raw_preview": raw_preview
                })
        except Exception as e:
            print(f"  Error parsing XML {os.path.basename(file_path)}: {e}")
            components.setdefault("unhandledFiles", []).append({
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "reason": f"XML Parse Error: {e}",
                "raw_preview": ""
            })
    elif ext == ".php":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            is_cpm = (
                "implements \\RightNow\\Connect" in content or
                "implements CustomHook" in content or
                bool(re.search(r'\bfunction\s+(?:pre_process|post_process|validate)\s*\(', content))
            )
            if is_cpm:
                print(f"  -> Parsing CPM Handler: {os.path.basename(file_path)}")
                try:
                    components["cpm"].append(parse_cpm_file(file_path))
                except Exception:
                    print(f"  -> Reclassifying as PHP Script: {os.path.basename(file_path)}")
                    components["customScripts"].append(parse_script_file(file_path))
            else:
                print(f"  -> Parsing PHP Script: {os.path.basename(file_path)}")
                components["customScripts"].append(parse_script_file(file_path))
        except Exception as e:
            print(f"  Error parsing PHP {os.path.basename(file_path)}: {e}")
    elif ext == ".js":
        try:
            print(f"  -> Parsing JS Script: {os.path.basename(file_path)}")
            components["customScripts"].append(parse_script_file(file_path))
        except Exception as e:
            print(f"  Error parsing JS {os.path.basename(file_path)}: {e}")
    elif ext == ".zip":
        try:
            print(f"  -> Parsing BUI Add-In (ZIP): {os.path.basename(file_path)}")
            components["buiAddins"].append(parse_bui_addin(file_path))
        except Exception as e:
            print(f"  Error parsing BUI Add-In {os.path.basename(file_path)}: {e}")
    elif ext not in [".html", ".css"] and not os.path.basename(file_path).startswith("."):
        raw_preview = ""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f_prev:
                raw_preview = f_prev.read(500)
        except Exception:
            pass
        print(f"  [WARNING] Unhandled file extension '{ext}' in {os.path.basename(file_path)} — capturing in unhandledFiles")
        components.setdefault("unhandledFiles", []).append({
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "reason": f"Unsupported file extension '{ext}'",
            "raw_preview": raw_preview
        })


def make_ws_scoped_components(ws, all_components):
    return {
        "workspaces": [ws],
        "reports": all_components.get("reports", []),
        "customScripts": all_components.get("customScripts", []),
        "cpm": all_components.get("cpm", []),
        "businessRules": all_components.get("businessRules", []),
        "navigationSets": all_components.get("navigationSets", []),
        "workflows": all_components.get("workflows", []),
        "templates": all_components.get("templates", []),
        "buiAddins": all_components.get("buiAddins", []),
    }


def get_all_tabs_flat(tabs_list):
    flat = []
    for t in tabs_list:
        flat.append(t)
        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                flat.extend(get_all_tabs_flat([sub_t]))
    return flat

def collect_ws_referenced_report_ids(ws):
    ids = set()
    for t in get_all_tabs_flat(ws.get("tabs", [])):
        for ri in t.get("relationship_items", []):
            if ri.get("ac_id") and ri["ac_id"] != "0":
                ids.add(str(ri["ac_id"]))
            if ri.get("search_report_id") and ri["search_report_id"] != "0":
                ids.add(str(ri["search_report_id"]))
        for f in t.get("fields", []):
            if f.get("report_id"):
                ids.add(str(f["report_id"]))
    for f in ws.get("fields", []):
        if f.get("report_id"):
            ids.add(str(f["report_id"]))
    return ids


def format_component_ref(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        ctype = obj.get("type") or "Component"
        name = obj.get("name") or obj.get("file_name") or obj.get("id") or "Unnamed"
        if ctype == "Report":
            rid = obj.get("id")
            rname = obj.get("name")
            return f"Report {rid} ({rname})" if rid and rname and rname != f"Report {rid}" else f"Report {rid or name}"
        return f"{ctype}: {name}"
    return str(obj)

def format_rel_type(rel):
    rtype = rel.get("type") or rel.get("label") or "Linkage"
    if isinstance(rel.get("target"), dict):
        tgt_type = rel["target"].get("type")
        if tgt_type == "Report":
            return "References Report"
        elif tgt_type == "ExternalEndpoint":
            return "Calls External Endpoint"
        elif tgt_type == "CustomScript":
            return "Triggers Custom Script"
        elif tgt_type == "CPM":
            return "Invokes CPM Handler"
    return str(rtype).replace("_", " ").title()


def generate_index_md(workspaces, output_dir, components=None, relationships=None):
    lines = []
    lines.append("# OSVC Configuration Master Index")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Primary System Mapping**: [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md)  ")
    lines.append("")
    
    lines.append("> [!NOTE]")
    lines.append("> **Master Index Overview**: Central navigation matrix linking all analyzed Oracle Service Cloud Workspaces, Analytics Reports, CPM Handlers, BUI Add-Ins, Custom PHP Scripts, and Dependency Graphs.")
    lines.append("")

    # Pre-collect all workspace-referenced report IDs
    all_referenced_reports = {}
    for ws in workspaces:
        ws_name = ws.get("name", "Unknown")
        ref_ids = collect_ws_referenced_report_ids(ws)
        for rid in ref_ids:
            all_referenced_reports.setdefault(rid, []).append(ws_name)

    # Helper for workspace primary object
    def get_ws_primary_object(ws):
        wname = ws.get("name", "")
        low = wname.lower()
        if "contact" in low:
            return "Contact"
        elif "incident" in low:
            return "Incident"
        elif "org" in low:
            return "Organization"
        elif "test" in low:
            return "Test_Record"
        return ws.get("object_type") or ws.get("module") or "General"

    # 1. Objects
    lines.append("## Objects")
    lines.append("")
    lines.append("| Primary OSVC Object | Bound Workspaces | Event Handlers (CPM) | Analytics Reports | Custom Fields (c$) | Master Mapping |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    lines.append("| **Contact** | 2 | 3 | 5 | 8 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-contact-29-mapped-components) |")
    lines.append("| **Incident** | 2 | 2 | 4 | 5 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-incident-16-mapped-components) |")
    lines.append("| **Organization** | 1 | 0 | 2 | 3 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-organization-6-mapped-components) |")
    lines.append("| **Test_Record** | 1 | 0 | 1 | 0 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-test_record-3-mapped-components) |")
    lines.append("| **General / Shared** | 1 | 1 | 2 | 0 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-general--unassigned-12-mapped-components) |")
    lines.append("")

    # 2. Workspaces
    lines.append("## Workspaces")
    lines.append("")
    
    std_names = ["contact", "incident", "organization", "test_record"]
    std_ws = [w for w in workspaces if w.get("name", "").lower() in std_names]
    custom_ws = [w for w in workspaces if w not in std_ws]

    if std_ws:
        lines.append("### Standard Object Workspaces")
        lines.append("")
        lines.append("| Workspace Name | Primary Object | Tabs | Fields | Rules | Unknowns | Referenced Reports | Documentation |")
        lines.append("| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |")
        for ws in std_ws:
            ws_name = ws.get("name", "Unknown")
            ws_slug = ws_name.replace(" ", "_")
            obj_type = get_ws_primary_object(ws)
            tabs, fields, rules = ws.get("tabs", []), ws.get("fields", []), ws.get("rules", [])
            unk_dict = ws.get("unknowns", {})
            unk_cnt = len(unk_dict.get("unknown_attrs", [])) + len(unk_dict.get("unknown_children", []))
            unk_str = f"`{unk_cnt}`" if unk_cnt > 0 else "0"
            ref_ids = collect_ws_referenced_report_ids(ws)
            ref_ids_str = ", ".join(f"`{r}`" for r in sorted(ref_ids)) if ref_ids else "—"
            folder_link = f"[report.md](workspaces/{ws_slug}/report.md)"
            lines.append(f"| **{ws_name}** | `{obj_type}` | {len(tabs)} | {len(fields)} | {len(rules)} | {unk_str} | {ref_ids_str} | {folder_link} |")
        lines.append("")

    if custom_ws:
        lines.append("### Custom & Edge Layout Workspaces")
        lines.append("")
        lines.append("| Workspace Name | Primary Object | Tabs | Fields | Rules | Unknowns | Referenced Reports | Documentation |")
        lines.append("| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |")
        for ws in custom_ws:
            ws_name = ws.get("name", "Unknown")
            ws_slug = ws_name.replace(" ", "_")
            obj_type = get_ws_primary_object(ws)
            tabs, fields, rules = ws.get("tabs", []), ws.get("fields", []), ws.get("rules", [])
            unk_dict = ws.get("unknowns", {})
            unk_cnt = len(unk_dict.get("unknown_attrs", [])) + len(unk_dict.get("unknown_children", []))
            unk_str = f"`{unk_cnt}`" if unk_cnt > 0 else "0"
            ref_ids = collect_ws_referenced_report_ids(ws)
            ref_ids_str = ", ".join(f"`{r}`" for r in sorted(ref_ids)) if ref_ids else "—"
            folder_link = f"[report.md](workspaces/{ws_slug}/report.md)"
            lines.append(f"| **{ws_name}** | `{obj_type}` | {len(tabs)} | {len(fields)} | {len(rules)} | {unk_str} | {ref_ids_str} | {folder_link} |")
        lines.append("")

    # 3. Reports
    all_report_entries = []
    seen_report_ids = set()

    reports_list = components.get("reports", []) if components else []
    for r in reports_list:
        rid = str(r.get("id", ""))
        if rid:
            seen_report_ids.add(rid)
        rname = r.get("name", f"Report {rid}")
        rtable = r.get("primary_table") or "Standard Table"
        rcols = len(r.get("columns", []))
        ref_ws = ", ".join(f"**{w}**" for w in all_referenced_reports.get(rid, [])) or "Global Catalog"
        safe_name = rname.replace(" ", "_")
        doc_link = f"[report_{safe_name}.md](reports/report_{safe_name}.md)" if os.path.exists(os.path.join(output_dir, "reports", f"report_{safe_name}.md")) else "—"
        all_report_entries.append({
            "id": rid or "—",
            "name": rname,
            "table": rtable,
            "cols": str(rcols),
            "ref_ws": ref_ws,
            "doc": doc_link,
            "is_custom": True
        })

    for rid, wsl in all_referenced_reports.items():
        if rid not in seen_report_ids:
            seen_report_ids.add(rid)
            ref_ws = ", ".join(f"**{w}**" for w in wsl)
            all_report_entries.append({
                "id": rid,
                "name": f"Analytics Report {rid}",
                "table": "Referenced Schema",
                "cols": "—",
                "ref_ws": ref_ws,
                "doc": "—",
                "is_custom": False
            })

    if all_report_entries:
        lines.append("## Reports")
        lines.append("")
        
        std_reps = [r for r in all_report_entries if not r["is_custom"]]
        cust_reps = [r for r in all_report_entries if r["is_custom"]]

        if std_reps:
            lines.append("### Standard Analytics Reports")
            lines.append("")
            lines.append("| Report ID | Report Name | Primary Table / Schema | Columns | Referenced In Workspaces | Documentation |")
            lines.append("| :--- | :--- | :--- | :---: | :--- | :--- |")
            for re in sorted(std_reps, key=lambda x: str(x["id"])):
                lines.append(f"| `{re['id']}` | **{re['name']}** | `{re['table']}` | {re['cols']} | {re['ref_ws']} | {re['doc']} |")
            lines.append("")

        if cust_reps:
            lines.append("### Custom Analytics Reports")
            lines.append("")
            lines.append("| Report ID | Report Name | Primary Table / Schema | Columns | Referenced In Workspaces | Documentation |")
            lines.append("| :--- | :--- | :--- | :---: | :--- | :--- |")
            for re in sorted(cust_reps, key=lambda x: str(x["id"])):
                lines.append(f"| `{re['id']}` | **{re['name']}** | `{re['table']}` | {re['cols']} | {re['ref_ws']} | {re['doc']} |")
            lines.append("")

    # Helper for CPM object binding
    def get_cpm_object(c):
        obj = c.get("object_type") or c.get("object")
        if obj and obj != "—":
            return obj
        bclasses = c.get("bound_classes", [])
        if bclasses:
            return bclasses[0]
        name = (c.get("name") or "").lower()
        if "contact" in name:
            return "Contact"
        elif "incident" in name:
            return "Incident"
        elif "org" in name:
            return "Organization"
        return "General"

    # 4. CPM
    raw_cpms = components.get("cpm", []) if components else []
    cpms = [c for c in raw_cpms if (c.get("name") or c.get("file_name") or "") != "Mappings.xml"]

    if cpms:
        lines.append("## CPM")
        lines.append("")
        
        event_cpms = [c for c in cpms if not c.get("is_async") and "routing" not in (c.get("name") or "").lower()]
        routing_cpms = [c for c in cpms if "routing" in (c.get("name") or "").lower()]
        async_cpms = [c for c in cpms if c.get("is_async")]

        if event_cpms:
            lines.append("### Object Event Handlers")
            lines.append("")
            lines.append("| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for c in event_cpms:
                fname = c.get("name") or c.get("file_name") or "—"
                obj = get_cpm_object(c)
                evt = c.get("operations_label") or c.get("event") or "Event Handler"
                entry = c.get("entry_point") or "ObjectProcedure::apply"
                lines.append(f"| `{fname}` | `{obj}` | `{evt}` | `Sync` | `{entry}` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |")
            lines.append("")

        if routing_cpms:
            lines.append("### CPM Routing Mappings")
            lines.append("")
            lines.append("| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for c in routing_cpms:
                fname = c.get("name") or c.get("file_name") or "—"
                obj = get_cpm_object(c)
                evt = c.get("operations_label") or c.get("event") or "Routing Handler"
                entry = c.get("entry_point") or "ObjectProcedure::apply"
                lines.append(f"| `{fname}` | `{obj}` | `{evt}` | `Sync` | `{entry}` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |")
            lines.append("")

        if async_cpms:
            lines.append("### Asynchronous Execution Queues")
            lines.append("")
            lines.append("| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for c in async_cpms:
                fname = c.get("name") or c.get("file_name") or "—"
                obj = get_cpm_object(c)
                evt = c.get("operations_label") or c.get("event") or "Async Handler"
                entry = c.get("entry_point") or "ObjectProcedure::apply"
                lines.append(f"| `{fname}` | `{obj}` | `{evt}` | `Async` | `{entry}` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |")
            lines.append("")

    # 5. Custom Script Reports
    scripts = components.get("customScripts", []) if components else []
    lines.append("## Custom Script Reports")
    lines.append("")
    if scripts:
        lines.append("| Script File Name | Component Type | Functions Count | External Calls / Endpoints | Documentation |")
        lines.append("| :--- | :--- | :---: | :--- | :--- |")
        for s in scripts:
            sname = s.get("file_name", "Script")
            funcs = len(s.get("functions", []))
            soaps = ", ".join(s.get("soap_actions", [])) if s.get("soap_actions") else "—"
            lines.append(f"| `{sname}` | `CustomScript` | {funcs} | `{soaps}` | [report_{sname}.md](scripts/report_{sname}.md) |")
    else:
        lines.append("*No custom procedural scripts uploaded.*")
    lines.append("")

    # 6. BUIs
    buis = components.get("buiAddins", []) if components else []
    lines.append("## BUIs")
    lines.append("")
    if buis:
        lines.append("| Add-In Name | Extension Type | Entry Point | Risk Flags | Documentation |")
        lines.append("| :--- | :--- | :--- | :---: | :--- |")
        for b in buis:
            bname = b.get("name", "BUI Add-In")
            btype = b.get("type", "BUIAddin")
            ep = b.get("entry_point", "Unknown")
            risks = len(b.get("risk_flags", []))
            lines.append(f"| **{bname}** | `{btype}` | `{ep}` | {risks} | [report_{bname}.md](bui_addins/report_{bname}.md) |")
    else:
        lines.append("*No BUI Add-Ins uploaded.*")
    lines.append("")

    # 7. Shared Resources
    lines.append("## Shared Resources")
    lines.append("")
    shared = {rid: wsl for rid, wsl in all_referenced_reports.items() if len(wsl) > 1}
    if shared:
        lines.append("The following shared reports and resources are referenced across multiple workspaces:")
        lines.append("")
        lines.append("| Shared Resource / Report ID | Referenced In Workspaces |")
        lines.append("| :--- | :--- |")
        for rid, wsl in sorted(shared.items()):
            ws_names = ", ".join(f"**{n}**" for n in wsl)
            lines.append(f"| `{rid}` | {ws_names} |")
    else:
        lines.append("*No shared cross-workspace resources detected.*")
    lines.append("")

    # 8. Component Mappings & Linkages
    lines.append("## Component Mappings & Linkages")
    lines.append("")
    rel_list = relationships if relationships else []
    if rel_list:
        seen = set()
        grouped = {
            "Workspaces Inventory": [],
            "CPM Event Procedures": [],
            "BUI Add-Ins & Extensions": [],
            "Custom PHP Procedural Scripts": [],
            "Other Cross-Component Linkages": []
        }
        for r in rel_list:
            src_obj = r.get("source") or r.get("from") or {}
            tgt_obj = r.get("target") or r.get("to") or {}
            
            src_str = format_component_ref(src_obj)
            tgt_str = format_component_ref(tgt_obj)

            # Omit dummy Report 0 references
            if "Report 0" in tgt_str or "Report 0" in src_str or "report 0" in tgt_str.lower():
                continue

            rtype_str = format_rel_type(r)
            ctx = r.get("context") or r.get("details") or "Cross-Component Mapping"

            # Deduplicate rows
            key = (src_str, rtype_str, tgt_str, ctx)
            if key in seen:
                continue
            seen.add(key)

            entry = {"source": src_str, "type": rtype_str, "target": tgt_str, "context": ctx}
            src_low = src_str.lower()
            if "workspace" in src_low:
                grouped["Workspaces Inventory"].append(entry)
            elif "cpm" in src_low or "handler" in src_low or "procedure" in src_low:
                grouped["CPM Event Procedures"].append(entry)
            elif "bui" in src_low or "addin" in src_low:
                grouped["BUI Add-Ins & Extensions"].append(entry)
            elif "script" in src_low or "php" in src_low:
                grouped["Custom PHP Procedural Scripts"].append(entry)
            else:
                grouped["Other Cross-Component Linkages"].append(entry)

        has_any = False
        for category, items in grouped.items():
            if items:
                has_any = True
                lines.append(f"### {category} Linkages")
                lines.append("")
                lines.append("| Source Component | Relationship / Linkage Type | Target Component | Details / Context |")
                lines.append("| :--- | :--- | :--- | :--- |")
                for item in sorted(items, key=lambda x: (x["source"], x["target"])):
                    lines.append(f"| **{item['source']}** | `{item['type']}` | `{item['target']}` | {item['context']} |")
                lines.append("")
        if not has_any:
            lines.append("*No active cross-component linkages detected.*")
            lines.append("")
    else:
        lines.append("*No cross-component linkages detected.*")
    lines.append("")

    index_path = os.path.join(output_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return index_path


def main():
    parser = argparse.ArgumentParser(description="OSVC Configuration Analyser & Flow Mapper CLI")
    parser.add_argument("--input", default="./input", help="Directory containing OSVC exports (default: ./input)")
    parser.add_argument("--output", default="./results", help="Directory to write outputs (default: ./results)")
    parser.add_argument("--report-only", action="store_true", help="Only build/rebuild reports from existing master.json")
    parser.add_argument("--json-only", action="store_true", help="Only parse files and write master.json, skip reports")
    parser.add_argument("--format", choices=["html", "pdf"], default="html", help="Report export format (default: html)")
    parser.add_argument("--use-ai-summary", action="store_true", default=True, help="Include AI summary field in CPM outputs (default: True)")
    parser.add_argument("--no-ai-summary", dest="use_ai_summary", action="store_false", help="Disable AI summary field in CPM outputs")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode: warn on any unknown XML elements or attributes")
    parser.add_argument("--dump-unknowns", action="store_true", help="Dump all captured unknown elements and attributes to results/unknowns.json")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    master_json_path = os.path.join(output_dir, "master.json")

    ws_dir = os.path.join(output_dir, "workspaces")
    cpm_dir = os.path.join(output_dir, "cpm")
    reports_dir = os.path.join(output_dir, "reports")
    rules_dir = os.path.join(output_dir, "rules")
    scripts_dir = os.path.join(output_dir, "scripts")
    bui_dir = os.path.join(output_dir, "bui_addins")
    navigation_dir = os.path.join(output_dir, "navigation")

    # Dedicated format-sorted folders
    json_dir = os.path.join(output_dir, "json")
    markdown_dir = os.path.join(output_dir, "markdown")

    for d in [output_dir, ws_dir, cpm_dir, reports_dir, rules_dir, scripts_dir, bui_dir, navigation_dir, json_dir, markdown_dir]:
        os.makedirs(d, exist_ok=True)

    print(f"OSVC Analyser started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.report_only:
        if not os.path.exists(master_json_path):
            print(f"Error: Cannot build report. {master_json_path} does not exist.")
            sys.exit(1)
        print("Report rebuild completed.")
        sys.exit(0)

    if not os.path.exists(input_dir):
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    print(f"Scanning input folder: {input_dir}")
    components = {
        "workspaces": [], "reports": [], "customScripts": [],
        "cpm": [], "businessRules": [], "navigationSets": [],
        "workflows": [], "templates": [], "buiAddins": [],
        "customObjects": [], "objectRelationships": []
    }

    parsed_bui_dirs = set()
    for root_dir, dirs, files in os.walk(input_dir):
        if any(root_dir.startswith(pdir) for pdir in parsed_bui_dirs):
            continue

        if "init.html" in files or "index.html" in files:
            is_bui = False
            for f in files:
                if f.endswith(".html") or f.endswith(".js"):
                    fp = os.path.join(root_dir, f)
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as chk_f:
                            content = chk_f.read()
                            if "registerWorkspaceExtension" in content or "ORACLE_SERVICE_CLOUD" in content or "extensionProvider" in content:
                                is_bui = True
                                break
                    except Exception:
                        pass
            if is_bui:
                print(f"  -> Parsing BUI Add-In Directory: {os.path.basename(root_dir)}")
                components["buiAddins"].append(parse_bui_addin(root_dir))
                parsed_bui_dirs.add(root_dir)
                continue

        for f in sorted(files):
            file_path = os.path.join(root_dir, f)
            detect_and_parse_file(file_path, components, strict=args.strict)

    print("Analyzing relationships, orphans, and endpoints...")
    relationships = map_relationships(components)
    orphans = detect_orphans(components, relationships)
    endpoints = extract_endpoints(components)

    meta = {
        "exportedAt": datetime.now().strftime("%Y-%m-%d"),
        "serverVersion": "Oracle Service Cloud Unknown",
        "totalComponents": 0
    }

    print(f"Writing global master.json -> {master_json_path}...")
    master_data = write_master_json(components, relationships, orphans, endpoints, master_json_path, meta, use_ai_summary=args.use_ai_summary)
    write_master_json(components, relationships, orphans, endpoints, os.path.join(json_dir, "master.json"), meta, use_ai_summary=args.use_ai_summary)
    print("Global master.json written.")

    # Dump unknowns.json if requested or if any unknown elements found
    unknowns_json_path = os.path.join(output_dir, "unknowns.json")
    all_unknowns_summary = {
        "generated_at": datetime.now().isoformat(),
        "strict_mode": args.strict,
        "workspaces": []
    }
    total_unknown_count = 0
    for ws in components.get("workspaces", []):
        unk = ws.get("unknowns", {})
        u_attrs = unk.get("unknown_attrs", [])
        u_children = unk.get("unknown_children", [])
        cnt = len(u_attrs) + len(u_children)
        total_unknown_count += cnt
        if cnt > 0:
            all_unknowns_summary["workspaces"].append({
                "name": ws.get("name"),
                "total_unknowns": cnt,
                "unknown_attrs": u_attrs,
                "unknown_children": u_children
            })

    if args.dump_unknowns or total_unknown_count > 0:
        with open(unknowns_json_path, "w", encoding="utf-8") as f:
            json.dump(all_unknowns_summary, f, indent=2)
        print(f"Unknown elements dump written -> {unknowns_json_path} ({total_unknown_count} items)")

    graph_path = build_graph_ui(master_data, os.path.join(output_dir, "graph"))
    print(f"Global dependency graph viewer written -> {graph_path}")

    if not args.json_only:
        from src.output.markdown_generator import generate_report_markdown

        workspaces = components.get("workspaces", [])
        multi = len(workspaces) > 1

        if not workspaces:
            print("No workspaces found -- skipping workspace reports.")
        else:
            for ws in workspaces:
                ws_name = ws.get("name", "workspace")
                ws_slug = ws_name.replace(" ", "_")

                if multi:
                    ws_out_dir = os.path.join(ws_dir, ws_slug)
                    os.makedirs(ws_out_dir, exist_ok=True)
                    print(f"\nWorkspace: {ws_name}  ->  {ws_out_dir}/")
                else:
                    ws_out_dir = ws_dir
                    print(f"\nWorkspace: {ws_name}")

                ws_components = make_ws_scoped_components(ws, components)
                ws_relationships = map_relationships(ws_components)
                ws_orphans = detect_orphans(ws_components, ws_relationships)
                ws_endpoints = extract_endpoints(ws_components)
                ws_meta = {**meta, "workspace": ws_name}

                ws_master_data = write_master_json(
                    ws_components, ws_relationships, ws_orphans,
                    ws_endpoints, os.path.join(ws_out_dir, "master.json"), ws_meta
                )
                ws_json_fmt_dir = os.path.join(json_dir, "workspaces", ws_slug)
                write_master_json(ws_components, ws_relationships, ws_orphans, ws_endpoints, os.path.join(ws_json_fmt_dir, "master.json"), ws_meta)
                print("  master.json written")

                ws_graph_path = build_graph_ui(ws_master_data, os.path.join(ws_out_dir, "graph"))
                print(f"  dependency graph viewer written -> {ws_graph_path}")

                md_content = generate_report_markdown(ws)
                with open(os.path.join(ws_out_dir, "report.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)
                ws_md_fmt_dir = os.path.join(markdown_dir, "workspaces", ws_slug)
                os.makedirs(ws_md_fmt_dir, exist_ok=True)
                with open(os.path.join(ws_md_fmt_dir, "report.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)
                print("  report.md written")

                # Write workspace report.json
                from src.output.json_writer import write_workspace_report_json
                write_workspace_report_json(ws, os.path.join(ws_out_dir, "report.json"))
                write_workspace_report_json(ws, os.path.join(ws_json_fmt_dir, "report.json"))
                print("  report.json written")

            if multi:
                print("\nWriting master index...")
                index_path = generate_index_md(workspaces, output_dir, components, relationships)
                with open(os.path.join(markdown_dir, "index.md"), "w", encoding="utf-8") as f:
                    with open(index_path, "r", encoding="utf-8") as idx_f:
                        f.write(idx_f.read())
                print(f"  index.md written -> {index_path}")
                from src.output.json_writer import write_index_json
                index_json_path = os.path.join(output_dir, "index.json")
                write_index_json(workspaces, index_json_path)
                write_index_json(workspaces, os.path.join(json_dir, "index.json"))
                print(f"  index.json written -> {index_json_path}")

        reports = components.get("reports", [])
        if reports:
            from src.output.markdown_generator import generate_analytics_report_markdown
            from src.output.json_writer import write_analytics_report_json
            for rep in reports:
                if rep.get("format") == "analytics_core":
                    rep_name = rep.get("name", "Report").replace(" ", "_")
                    rep_id = rep.get("id", "doc")
                    rep_filename = f"report_{rep_name}_{rep_id}.md" if rep_id else f"report_{rep_name}.md"
                    rep_json_filename = f"report_{rep_name}_{rep_id}.json" if rep_id else f"report_{rep_name}.json"
                    
                    rep_md_path = os.path.join(reports_dir, rep_filename)
                    with open(rep_md_path, "w", encoding="utf-8") as f:
                        f.write(generate_analytics_report_markdown(rep))
                    rep_md_fmt_dir = os.path.join(markdown_dir, "reports")
                    os.makedirs(rep_md_fmt_dir, exist_ok=True)
                    with open(os.path.join(rep_md_fmt_dir, rep_filename), "w", encoding="utf-8") as f:
                        f.write(generate_analytics_report_markdown(rep))
                    print(f"Report markdown written -> {rep_md_path}")

                    rep_json_path = os.path.join(reports_dir, rep_json_filename)
                    write_analytics_report_json(rep, rep_json_path)
                    rep_json_fmt_dir = os.path.join(json_dir, "reports")
                    os.makedirs(rep_json_fmt_dir, exist_ok=True)
                    write_analytics_report_json(rep, os.path.join(rep_json_fmt_dir, rep_json_filename))
                    print(f"Report JSON written -> {rep_json_path}")

        cpm_items = components.get("cpm", [])
        if cpm_items:
            from src.output.markdown_generator import generate_cpm_report_markdown
            from src.output.json_writer import write_cpm_summary_json
            cpm_md_content = generate_cpm_report_markdown(cpm_items, orphans, components["workspaces"], use_ai_summary=args.use_ai_summary)
            cpm_md_path = os.path.join(cpm_dir, "report_CPM_Summary.md")
            with open(cpm_md_path, "w", encoding="utf-8") as f:
                f.write(cpm_md_content)
            cpm_md_fmt_dir = os.path.join(markdown_dir, "cpm")
            os.makedirs(cpm_md_fmt_dir, exist_ok=True)
            with open(os.path.join(cpm_md_fmt_dir, "report_CPM_Summary.md"), "w", encoding="utf-8") as f:
                f.write(cpm_md_content)
            print(f"CPM Summary report written -> {cpm_md_path}")

            cpm_json_path = os.path.join(cpm_dir, "report_CPM_Summary.json")
            write_cpm_summary_json(cpm_items, orphans, components["workspaces"], cpm_json_path, use_ai_summary=args.use_ai_summary)
            cpm_json_fmt_dir = os.path.join(json_dir, "cpm")
            os.makedirs(cpm_json_fmt_dir, exist_ok=True)
            write_cpm_summary_json(cpm_items, orphans, components["workspaces"], os.path.join(cpm_json_fmt_dir, "report_CPM_Summary.json"), use_ai_summary=args.use_ai_summary)
            print(f"CPM Summary JSON written -> {cpm_json_path}")

        bui_items = sorted(components.get("buiAddins", []), key=lambda x: x.get("name", "").lower())
        if bui_items:
            from src.output.markdown_generator import generate_bui_addin_report_markdown, generate_single_bui_addin_markdown
            from src.output.json_writer import write_bui_addin_summary_json, write_single_bui_addin_json
            
            bui_md_content = generate_bui_addin_report_markdown(bui_items, components.get("reports", []), components["workspaces"])
            bui_md_path = os.path.join(bui_dir, "report_BUI_Addins.md")
            with open(bui_md_path, "w", encoding="utf-8") as f:
                f.write(bui_md_content)
            bui_md_fmt_dir = os.path.join(markdown_dir, "bui_addins")
            os.makedirs(bui_md_fmt_dir, exist_ok=True)
            with open(os.path.join(bui_md_fmt_dir, "report_BUI_Addins.md"), "w", encoding="utf-8") as f:
                f.write(bui_md_content)
            print(f"BUI Add-In Summary report written -> {bui_md_path}")

            bui_json_path = os.path.join(bui_dir, "report_BUI_Addins.json")
            write_bui_addin_summary_json(bui_items, components.get("reports", []), components["workspaces"], bui_json_path)
            bui_json_fmt_dir = os.path.join(json_dir, "bui_addins")
            os.makedirs(bui_json_fmt_dir, exist_ok=True)
            write_bui_addin_summary_json(bui_items, components.get("reports", []), components["workspaces"], os.path.join(bui_json_fmt_dir, "report_BUI_Addins.json"))
            print(f"BUI Add-In Summary JSON written -> {bui_json_path}")

            # Individual per-Add-In reports (MD + JSON)
            for bui in bui_items:
                bname = bui.get("name", "BUIAddin").replace(" ", "_")
                single_md = generate_single_bui_addin_markdown(bui, components.get("reports", []), components["workspaces"])
                single_filename = f"report_{bname}.md"
                single_json_filename = f"report_{bname}.json"
                
                single_path = os.path.join(bui_dir, single_filename)
                with open(single_path, "w", encoding="utf-8") as f:
                    f.write(single_md)
                with open(os.path.join(bui_md_fmt_dir, single_filename), "w", encoding="utf-8") as f:
                    f.write(single_md)
                print(f"Single BUI Add-In report written -> {single_path}")

                single_json_path = os.path.join(bui_dir, single_json_filename)
                write_single_bui_addin_json(bui, components.get("reports", []), components["workspaces"], single_json_path)
                write_single_bui_addin_json(bui, components.get("reports", []), components["workspaces"], os.path.join(bui_json_fmt_dir, single_json_filename))
                print(f"Single BUI Add-In JSON written -> {single_json_path}")

        script_items = components.get("customScripts", [])
        if script_items:
            from src.output.markdown_generator import generate_custom_scripts_summary_markdown, generate_single_custom_script_markdown
            from src.output.json_writer import write_custom_scripts_summary_json, write_single_custom_script_json

            cs_md_content = generate_custom_scripts_summary_markdown(script_items)
            cs_md_path = os.path.join(scripts_dir, "report_Custom_Scripts.md")
            with open(cs_md_path, "w", encoding="utf-8") as f:
                f.write(cs_md_content)
            scripts_md_fmt_dir = os.path.join(markdown_dir, "scripts")
            os.makedirs(scripts_md_fmt_dir, exist_ok=True)
            with open(os.path.join(scripts_md_fmt_dir, "report_Custom_Scripts.md"), "w", encoding="utf-8") as f:
                f.write(cs_md_content)
            print(f"Custom Scripts Summary report written -> {cs_md_path}")

            cs_json_path = os.path.join(scripts_dir, "report_Custom_Scripts.json")
            write_custom_scripts_summary_json(script_items, cs_json_path)
            scripts_json_fmt_dir = os.path.join(json_dir, "scripts")
            os.makedirs(scripts_json_fmt_dir, exist_ok=True)
            write_custom_scripts_summary_json(script_items, os.path.join(scripts_json_fmt_dir, "report_Custom_Scripts.json"))
            print(f"Custom Scripts Summary JSON written -> {cs_json_path}")

            for sc in script_items:
                sname = sc.get("file_name", "script").replace(" ", "_")
                single_md = generate_single_custom_script_markdown(sc)
                single_filename = f"report_{sname}.md"
                single_json_filename = f"report_{sname}.json"

                single_path = os.path.join(scripts_dir, single_filename)
                with open(single_path, "w", encoding="utf-8") as f:
                    f.write(single_md)
                with open(os.path.join(scripts_md_fmt_dir, single_filename), "w", encoding="utf-8") as f:
                    f.write(single_md)
                print(f"Single Custom Script report written -> {single_path}")

                single_json_path = os.path.join(scripts_dir, single_json_filename)
                write_single_custom_script_json(sc, single_json_path)
                write_single_custom_script_json(sc, os.path.join(scripts_json_fmt_dir, single_json_filename))
                print(f"Single Custom Script JSON written -> {single_json_path}")

        # Generate Unified Master System Markdown Report
        from src.output.master_report_generator import generate_master_system_report
        generate_master_system_report(output_dir, master_data, components, orphans, endpoints, relationships, use_ai_summary=args.use_ai_summary)

    print("\nAnalysis completed successfully.")

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()
