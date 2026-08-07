import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from csv_exporter import generate_workspace_csvs, generate_object_csv

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

    # 1. Parse all Object XML schemas into a shared map
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
            pass

    total_schema_fields = sum(len(d.get("fields", [])) for d in objects_map.values())
    print(f"[SUCCESS] Loaded {len(objects_map)} Object schema definition(s) -> {total_schema_fields} total schema fields.")

    # 2. Write a SINGLE shared object_fields.csv at the root output level
    os.makedirs(output_dir, exist_ok=True)
    obj_csv_path = os.path.join(output_dir, "object_fields.csv")
    generate_object_csv(objects_map, obj_csv_path)
    print(f"[SUCCESS] Object Schema CSV -> {obj_csv_path} ({total_schema_fields} rows)")
    print("--------------------------------------------------------------------------")

    # 3. Collect all Workspace XML file paths
    ws_files = []
    if os.path.isdir(workspace_path):
        for root_dir, _, files in os.walk(workspace_path):
            for f in sorted(files):
                if f.endswith(".xml"):
                    ws_files.append(os.path.join(root_dir, f))
    else:
        ws_files.append(workspace_path)

    # 4. Parse each workspace, write its 2 CSVs into workspaces/<workspace_name>/
    workspaces_dir = os.path.join(output_dir, "workspaces")
    os.makedirs(workspaces_dir, exist_ok=True)

    processed = 0
    skipped = 0
    for w_file in ws_files:
        try:
            ws_data = parse_workspace_xml(w_file)
        except Exception:
            skipped += 1
            continue

        ws_name = ws_data["workspace_name"]
        ws_out_dir = os.path.join(workspaces_dir, ws_name)
        os.makedirs(ws_out_dir, exist_ok=True)

        result = generate_workspace_csvs(ws_data, objects_map, ws_out_dir)
        processed += 1

        print(f"Workspace: {ws_name}")
        print(f"  workspace_fields.csv              -> {result['total_workspace_fields']} rows")
        print(f"  combined_workspace_object_fields.csv -> {result['total_workspace_fields']} rows")
        print(f"  Output -> {ws_out_dir}")
        print("")

    if skipped > 0:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")

    print("==========================================================================")
    print(f"Completed. {processed} workspace(s) processed.")
    print(f"  Object CSV  -> {obj_csv_path}")
    print(f"  Workspaces  -> {workspaces_dir}/")
    print("==========================================================================")

if __name__ == "__main__":
    main()
