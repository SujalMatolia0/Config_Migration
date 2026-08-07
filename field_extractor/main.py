import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from csv_exporter import generate_csv_reports

def main():
    parser = argparse.ArgumentParser(description="Standalone OSVC Field Extractor & CSV Generator")
    parser.add_argument("--workspace", required=True, help="Path to Workspace XML file or directory")
    parser.add_argument("--object", required=True, help="Path to Object XML file or directory")
    parser.add_argument("--output", default="./results", help="Output directory for generated CSV reports")

    args = parser.parse_args()

    workspace_path = os.path.abspath(args.workspace)
    object_path = os.path.abspath(args.object)
    output_dir = os.path.abspath(args.output)

    print("==========================================================================")
    print("           OSVC OBJECT-BASED FIELD EXTRACTOR & CSV ENGINE          ")
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

    # 1. Collect all Workspace XML file paths
    ws_files = []
    if os.path.isdir(workspace_path):
        for root_dir, _, files in os.walk(workspace_path):
            for f in sorted(files):
                if f.endswith(".xml"):
                    ws_files.append(os.path.join(root_dir, f))
    else:
        ws_files.append(workspace_path)

    # 2. Parse all Object XML schemas into a shared map
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
            obj_n = o_data.get("object_name", "")
            if obj_n:
                objects_map[obj_n.lower()] = o_data
        except Exception:
            # Skip XML files that are not valid Object schema XMLs
            pass

    total_schema_fields = sum(len(d.get("fields", [])) for d in objects_map.values())
    print(f"[SUCCESS] Loaded {len(objects_map)} Object schema definition(s) -> {total_schema_fields} total schema fields.")
    print("--------------------------------------------------------------------------")

    # 3. Process each Workspace file separately -> own subfolder of CSVs
    parsed_workspaces = []
    skipped = 0
    for w_file in ws_files:
        try:
            ws_data = parse_workspace_xml(w_file)
            parsed_workspaces.append(ws_data)
        except Exception:
            # Skip XML files that are not valid Workspace XMLs
            skipped += 1

    if not parsed_workspaces:
        print("[ERROR] No valid Workspace XML files found. Exiting.")
        sys.exit(1)

    print(f"[SUCCESS] Found {len(parsed_workspaces)} valid Workspace(s) to process.")
    if skipped > 0:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")
    print("--------------------------------------------------------------------------")

    all_results = []
    for ws_data in parsed_workspaces:
        ws_name = ws_data["workspace_name"]

        # Each workspace gets its own output subfolder
        ws_output_dir = os.path.join(output_dir, ws_name)
        os.makedirs(ws_output_dir, exist_ok=True)

        result = generate_csv_reports(ws_data, objects_map, ws_output_dir)
        all_results.append((ws_name, result))

        print(f"Workspace: {ws_name}")
        print(f"  workspace_fields.csv  -> {result['total_workspace_fields']} rows")
        print(f"  object_fields.csv     -> {result['total_object_fields']} rows")
        print(f"  combined_...csv       -> {result['total_workspace_fields']} rows")
        print(f"  Output folder         -> {ws_output_dir}")
        print("")

    print("==========================================================================")
    print(f"Completed. {len(all_results)} workspace(s) exported to: {output_dir}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
