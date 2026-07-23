#!/usr/bin/env python
import os
import sys
import json
import argparse
from datetime import datetime
from lxml import etree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parsers.workspace_parser import parse_workspace_file
from parsers.report_parser import parse_report_file
from parsers.rule_parser import parse_rule_file
from parsers.nav_parser import parse_nav_file
from parsers.cpm_parser import parse_cpm_file
from parsers.script_parser import parse_script_file

from analyser.relationship_mapper import map_relationships
from analyser.orphan_detector import detect_orphans
from analyser.endpoint_extractor import extract_endpoints

from output.json_writer import write_master_json
from output.report_builder import build_html_report, build_pdf_report


def detect_and_parse_file(file_path, components):
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".xml":
        try:
            parser = etree.XMLParser(recover=True, remove_comments=True)
            tree = etree.parse(file_path, parser=parser)
            root = tree.getroot()
            tag = root.tag.split('}')[-1]
            if tag == "Workspace":
                print(f"  -> Parsing Workspace: {os.path.basename(file_path)}")
                components["workspaces"].append(parse_workspace_file(file_path))
            elif tag in ["Report", "Reports"]:
                print(f"  -> Parsing Report: {os.path.basename(file_path)}")
                components["reports"].append(parse_report_file(file_path))
            elif tag in ["Rules", "Rule"]:
                print(f"  -> Parsing Business Rules: {os.path.basename(file_path)}")
                components["businessRules"].append(parse_rule_file(file_path))
            elif tag in ["NavigationSet", "NavSet", "Navigation"]:
                print(f"  -> Parsing Nav Set: {os.path.basename(file_path)}")
                components["navigationSets"].append(parse_nav_file(file_path))
            else:
                if root.find(".//Workspace") is not None:
                    print(f"  -> Parsing Workspace (nested): {os.path.basename(file_path)}")
                    components["workspaces"].append(parse_workspace_file(file_path))
                elif root.find(".//Report") is not None or root.find(".//Column") is not None:
                    print(f"  -> Parsing Report (nested): {os.path.basename(file_path)}")
                    components["reports"].append(parse_report_file(file_path))
                elif root.find(".//Rule") is not None:
                    print(f"  -> Parsing Business Rules (nested): {os.path.basename(file_path)}")
                    components["businessRules"].append(parse_rule_file(file_path))
                elif root.find(".//NavItem") is not None:
                    print(f"  -> Parsing Nav Set (nested): {os.path.basename(file_path)}")
                    components["navigationSets"].append(parse_nav_file(file_path))
                else:
                    print(f"  Warning: Skipping unrecognized XML: {os.path.basename(file_path)} (root tag: {tag})")
        except Exception as e:
            print(f"  Error parsing XML {os.path.basename(file_path)}: {e}")
    elif ext == ".php":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            is_cpm = (
                "implements \\RightNow\\Connect" in content or
                "implements CustomHook" in content or
                "function pre_process" in content or
                "function post_process" in content or
                "function validate" in content
            )
            if is_cpm:
                print(f"  -> Parsing CPM Handler: {os.path.basename(file_path)}")
                components["cpm"].append(parse_cpm_file(file_path))
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


def generate_index_md(workspaces, output_dir):
    lines = []
    lines.append("# OSVC Configuration -- Workspace Index")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Workspaces Overview")
    lines.append("")
    lines.append("| Workspace | Tabs | Fields | Rules | Referenced Reports | Output Folder |")
    lines.append("|---|---|---|---|---|---|")

    all_referenced_reports = {}

    for ws in workspaces:
        ws_name = ws.get("name", "Unknown")
        ws_slug = ws_name.replace(" ", "_")
        tabs = ws.get("tabs", [])
        fields = ws.get("fields", [])
        rules = ws.get("rules", [])
        ref_ids = collect_ws_referenced_report_ids(ws)
        for rid in ref_ids:
            all_referenced_reports.setdefault(rid, []).append(ws_name)
        ref_ids_str = ", ".join(f"`{r}`" for r in sorted(ref_ids)) if ref_ids else "--"
        folder_link = f"[{ws_slug}/report.md]({ws_slug}/report.md)"
        lines.append(f"| **{ws_name}** | {len(tabs)} | {len(fields)} | {len(rules)} | {ref_ids_str} | {folder_link} |")

    lines.append("")

    shared = {rid: wsl for rid, wsl in all_referenced_reports.items() if len(wsl) > 1}
    if shared:
        lines.append("---")
        lines.append("")
        lines.append("## Shared Resources")
        lines.append("")
        lines.append("The following reports are referenced by more than one workspace.")
        lines.append("Changes to these reports may affect multiple workspaces simultaneously.")
        lines.append("")
        lines.append("| Report ID | Used By |")
        lines.append("|---|---|")
        for rid, wsl in sorted(shared.items()):
            ws_names = ", ".join(f"**{n}**" for n in wsl)
            lines.append(f"| `{rid}` | {ws_names} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Quick Links")
    lines.append("")
    for ws in workspaces:
        ws_name = ws.get("name", "Unknown")
        ws_slug = ws_name.replace(" ", "_")
        lines.append(
            f"- **{ws_name}**: "
            f"[report.md]({ws_slug}/report.md) | "
            f"[master.json]({ws_slug}/master.json) | "
            f"[report.html]({ws_slug}/report.html)"
        )
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
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    master_json_path = os.path.join(output_dir, "master.json")

    print(f"OSVC Analyser started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.report_only:
        if not os.path.exists(master_json_path):
            print(f"Error: Cannot build report. {master_json_path} does not exist.")
            sys.exit(1)
        print(f"Loading existing data from {master_json_path}...")
        with open(master_json_path, "r", encoding="utf-8") as f:
            master_data = json.load(f)
        html_path = os.path.join(output_dir, "report.html")
        build_html_report(master_data, html_path)
        print(f"HTML report rebuilt: {html_path}")
        if args.format == "pdf":
            build_pdf_report(html_path, os.path.join(output_dir, "report.pdf"))
        sys.exit(0)

    if not os.path.exists(input_dir):
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    print(f"Scanning input folder: {input_dir}")
    components = {
        "workspaces": [], "reports": [], "customScripts": [],
        "cpm": [], "businessRules": [], "navigationSets": [],
        "workflows": [], "templates": []
    }

    for root_dir, _, files in os.walk(input_dir):
        for f in sorted(files):
            detect_and_parse_file(os.path.join(root_dir, f), components)

    print("Analyzing relationships, orphans, and endpoints...")
    relationships = map_relationships(components)
    orphans = detect_orphans(components, relationships)
    endpoints = extract_endpoints(components)

    meta = {
        "exportedAt": datetime.now().strftime("%Y-%m-%d"),
        "serverVersion": "Oracle Service Cloud Unknown",
        "totalComponents": 0
    }

    os.makedirs(output_dir, exist_ok=True)

    print(f"Writing global master.json -> {master_json_path}...")
    master_data = write_master_json(components, relationships, orphans, endpoints, master_json_path, meta)
    print("Global master.json written.")

    if not args.json_only:
        from output.markdown_generator import generate_report_markdown

        workspaces = components.get("workspaces", [])
        multi = len(workspaces) > 1

        if not workspaces:
            print("No workspaces found -- skipping workspace reports.")
        else:
            for ws in workspaces:
                ws_name = ws.get("name", "workspace")
                ws_slug = ws_name.replace(" ", "_")

                if multi:
                    ws_out_dir = os.path.join(output_dir, ws_slug)
                    os.makedirs(ws_out_dir, exist_ok=True)
                    print(f"\nWorkspace: {ws_name}  ->  {ws_out_dir}/")
                else:
                    ws_out_dir = output_dir
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
                print("  master.json written")

                md_content = generate_report_markdown(ws)
                with open(os.path.join(ws_out_dir, "report.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)
                print("  report.md written")

                # Backwards-compat root-level report_<Name>.md
                with open(os.path.join(output_dir, f"report_{ws_slug}.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)

                build_html_report(ws_master_data, os.path.join(ws_out_dir, "report.html"))
                print("  report.html written")

                if args.format == "pdf":
                    build_pdf_report(
                        os.path.join(ws_out_dir, "report.html"),
                        os.path.join(ws_out_dir, "report.pdf")
                    )
                    print("  report.pdf written")

            if not multi:
                with open(os.path.join(output_dir, "report.md"), "w", encoding="utf-8") as f:
                    f.write(generate_report_markdown(workspaces[0]))

            if multi:
                print("\nWriting cross-workspace index...")
                index_path = generate_index_md(workspaces, output_dir)
                print(f"  index.md written -> {index_path}")

        build_html_report(master_data, os.path.join(output_dir, "report.html"))
        print("\nGlobal report.html written.")

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()
