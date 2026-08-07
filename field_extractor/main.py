import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from excel_exporter import write_workspaces_excel, write_objects_excel, write_combined_excel

def main():
    parser = argparse.ArgumentParser(description="Standalone OSVC Field Extractor - Excel Output")
    parser.add_argument("--workspace", required=True, help="Path to Workspace XML file or directory")
    parser.add_argument("--object",    required=True, help="Path to Object XML file or directory")
    parser.add_argument("--output",    default="./results", help="Output directory for Excel files")

    args = parser.parse_args()

    workspace_path = os.path.abspath(args.workspace)
    object_path    = os.path.abspath(args.object)
    output_dir     = os.path.abspath(args.output)

    print("==========================================================================")
    print("       OSVC FIELD EXTRACTOR - EXCEL EXPORT ENGINE                ")
    print("==========================================================================")
    print(f"Workspace Input:  {workspace_path}")
    print(f"Object Input:     {object_path}")
    print(f"Output Directory: {output_dir}")
    print("--------------------------------------------------------------------------")

    if not os.path.exists(workspace_path):
        print(f"[ERROR] Workspace path not found: {workspace_path}")
        sys.exit(1)
    if not os.path.exists(object_path):
        print(f"[ERROR] Object path not found: {object_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # 1. Parse all Object XML schemas
    obj_files = []
    if os.path.isdir(object_path):
        for root_dir, _, files in os.walk(object_path):
            for f in sorted(files):
                if f.endswith(".xml") and not f.startswith("."):
                    obj_files.append(os.path.join(root_dir, f))
    else:
        obj_files.append(object_path)

    objects_map = {}
    for o_file in obj_files:
        try:
            o_data = parse_object_xml(o_file)
            obj_n  = o_data.get("object_name", "")
            if obj_n:
                objects_map[obj_n.lower()] = o_data
                print(f"[OK] Object loaded: {obj_n} ({len(o_data.get('fields', []))} fields)")
        except Exception:
            pass

    if not objects_map:
        print("[ERROR] No valid Object XML schemas found. Exiting.")
        sys.exit(1)

    # 2. Parse all Workspace XML files
    ws_files = []
    if os.path.isdir(workspace_path):
        for root_dir, _, files in os.walk(workspace_path):
            for f in sorted(files):
                if f.endswith(".xml"):
                    ws_files.append(os.path.join(root_dir, f))
    else:
        ws_files.append(workspace_path)

    parsed_workspaces = []
    skipped = 0
    for w_file in ws_files:
        try:
            ws_data = parse_workspace_xml(w_file)
            parsed_workspaces.append(ws_data)
            bound = ws_data.get("bound_object", "Unknown")
            count = ws_data.get("total_layout_fields", 0)
            print(f"[OK] Workspace loaded: {ws_data['workspace_name']} (Bound: {bound}, {count} fields)")
        except Exception:
            skipped += 1

    if not parsed_workspaces:
        print("[ERROR] No valid Workspace XML files found. Exiting.")
        sys.exit(1)

    if skipped:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")

    print("--------------------------------------------------------------------------")

    # 3. Write 3 Excel files
    ws_xlsx  = os.path.join(output_dir, "workspaces.xlsx")
    obj_xlsx = os.path.join(output_dir, "objects.xlsx")
    comb_xlsx = os.path.join(output_dir, "combined.xlsx")

    write_workspaces_excel(parsed_workspaces, objects_map, ws_xlsx)
    print(f"[SUCCESS] workspaces.xlsx  -> {ws_xlsx}")
    print(f"          Tabs: {', '.join(ws['workspace_name'] for ws in parsed_workspaces)}")

    write_objects_excel(objects_map, obj_xlsx)
    print(f"[SUCCESS] objects.xlsx     -> {obj_xlsx}")
    print(f"          Tabs: {', '.join(d.get('object_name', k) for k, d in objects_map.items())}")

    write_combined_excel(parsed_workspaces, objects_map, comb_xlsx)
    print(f"[SUCCESS] combined.xlsx    -> {comb_xlsx}")
    print(f"          Tabs: {', '.join(ws['workspace_name'] for ws in parsed_workspaces)}")

    print("==========================================================================")
    print(f"Done. 3 Excel files written to: {output_dir}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
