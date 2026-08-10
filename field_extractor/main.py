import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from excel_exporter import write_workspaces_excel, write_objects_excel, write_combined_excel
from osvc_rest_fetcher import fetch_standard_objects_via_rest

def main():
    parser = argparse.ArgumentParser(description="Standalone OSVC Field Extractor - Excel Output")
    parser.add_argument("--workspace", required=False, help="Path to Workspace XML file or directory")
    parser.add_argument("--object",    required=False, help="Path to Object XML file or directory")
    parser.add_argument("--output",    default="./results", help="Output directory for Excel files")
    parser.add_argument("--rest-host", help="OSVC Host URL for live REST API metadata extraction (HTTP GET only)")
    parser.add_argument("--rest-user", help="OSVC REST API Username")
    parser.add_argument("--rest-pass", help="OSVC REST API Password")

    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    print("==========================================================================")
    print("       OSVC FIELD EXTRACTOR - EXCEL EXPORT ENGINE                ")
    print("==========================================================================")
    print(f"Output Directory: {output_dir}")
    print("--------------------------------------------------------------------------")

    objects_map = {}

    # 1. Option A: Fetch standard object schemas via REST API (STRICT HTTP GET ONLY)
    if args.rest_host and args.rest_user and args.rest_pass:
        print(f"[MODE] REST API Live Extraction (STRICT READ-ONLY GET)")
        objects_map = fetch_standard_objects_via_rest(
            host=args.rest_host,
            username=args.rest_user,
            password=args.rest_pass,
            include_custom=False
        )

    # 2. Option B: Parse Object XML files
    if args.object and os.path.exists(args.object):
        object_path = os.path.abspath(args.object)
        obj_files = []
        if os.path.isdir(object_path):
            for root_dir, _, files in os.walk(object_path):
                for f in sorted(files):
                    if f.endswith(".xml") and not f.startswith("."):
                        obj_files.append(os.path.join(root_dir, f))
        else:
            obj_files.append(object_path)

        for o_file in obj_files:
            try:
                o_data = parse_object_xml(o_file)
                obj_n  = o_data.get("object_name", "")
                if obj_n:
                    objects_map[obj_n.lower()] = o_data
                    print(f"[OK] Object loaded from XML: {obj_n} ({len(o_data.get('fields', []))} fields)")
            except Exception:
                pass

    if not objects_map:
        print("[ERROR] No valid Object schemas loaded from REST or XML files. Exiting.")
        sys.exit(1)

    # 3. Parse Workspace XML files
    parsed_workspaces = []
    skipped = 0
    if args.workspace and os.path.exists(args.workspace):
        workspace_path = os.path.abspath(args.workspace)
        ws_files = []
        if os.path.isdir(workspace_path):
            for root_dir, _, files in os.walk(workspace_path):
                for f in sorted(files):
                    if f.endswith(".xml"):
                        ws_files.append(os.path.join(root_dir, f))
        else:
            ws_files.append(workspace_path)

        for w_file in ws_files:
            try:
                ws_data = parse_workspace_xml(w_file)
                parsed_workspaces.append(ws_data)
                bound = ws_data.get("bound_object", "Unknown")
                count = ws_data.get("total_layout_fields", 0)
                print(f"[OK] Workspace loaded: {ws_data['workspace_name']} (Bound: {bound}, {count} fields)")
            except Exception:
                skipped += 1

    if skipped:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")

    print("--------------------------------------------------------------------------")

    # 4. Write Excel files
    std_xlsx  = os.path.join(output_dir, "standard_objects.xlsx")
    cst_xlsx  = os.path.join(output_dir, "custom_objects.xlsx")
    ws_xlsx   = os.path.join(output_dir, "workspaces.xlsx")
    comb_xlsx = os.path.join(output_dir, "combined.xlsx")

    # Separate standard objects and custom objects maps
    std_map = {k: v for k, v in objects_map.items() if '.' not in k}
    cst_map = {k: v for k, v in objects_map.items() if '.' in k or any(f.get("is_system_field") is False for f in v.get("fields", []))}

    if std_map:
        write_objects_excel(std_map, std_xlsx)
        print(f"[SUCCESS] standard_objects.xlsx -> {std_xlsx}")

    if cst_map:
        write_objects_excel(cst_map, cst_xlsx)
        print(f"[SUCCESS] custom_objects.xlsx   -> {cst_xlsx}")

    write_workspaces_excel(parsed_workspaces, objects_map, ws_xlsx)
    print(f"[SUCCESS] workspaces.xlsx       -> {ws_xlsx}")

    write_combined_excel(parsed_workspaces, objects_map, comb_xlsx)
    print(f"[SUCCESS] combined.xlsx         -> {comb_xlsx}")

    print("==========================================================================")
    print(f"Done. Reports written to: {output_dir}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
