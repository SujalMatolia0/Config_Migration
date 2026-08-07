import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from csv_exporter import generate_object_csv, generate_workspace_csvs

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

    # 1. Parse all Object XML schemas -> each object gets its own folder under objects/
    obj_files = []
    if os.path.isdir(object_path):
        for root_dir, _, files in os.walk(object_path):
            for f in sorted(files):
                if f.endswith(".xml") and not f.startswith("."):
                    obj_files.append(os.path.join(root_dir, f))
    else:
        obj_files.append(object_path)

    objects_map = {}  # Keyed by lowercase object name -> object schema dict
    objects_dir = os.path.join(output_dir, "objects")

    for o_file in obj_files:
        try:
            o_data = parse_object_xml(o_file)
            obj_n = o_data.get("object_name", "")
            if not obj_n:
                continue
            objects_map[obj_n.lower()] = o_data

            # Write this object's CSV into objects/<ObjectName>/object_fields.csv
            obj_out_dir = os.path.join(objects_dir, obj_n)
            os.makedirs(obj_out_dir, exist_ok=True)
            obj_csv_path = os.path.join(obj_out_dir, "object_fields.csv")
            generate_object_csv({obj_n.lower(): o_data}, obj_csv_path)
            field_count = len(o_data.get("fields", []))
            print(f"[SUCCESS] Object: {obj_n} -> {obj_csv_path} ({field_count} fields)")
        except Exception:
            pass

    if not objects_map:
        print("[ERROR] No valid Object XML schemas found. Exiting.")
        sys.exit(1)

    print("--------------------------------------------------------------------------")

    # 2. Collect all Workspace XML file paths
    ws_files = []
    if os.path.isdir(workspace_path):
        for root_dir, _, files in os.walk(workspace_path):
            for f in sorted(files):
                if f.endswith(".xml"):
                    ws_files.append(os.path.join(root_dir, f))
    else:
        ws_files.append(workspace_path)

    # 3. Process each workspace -> write its 2 CSVs into workspaces/<WorkspaceName>/
    #    Mapping: workspace bound_object (e.g. "Contact") -> contact object schema
    workspaces_dir = os.path.join(output_dir, "workspaces")
    os.makedirs(workspaces_dir, exist_ok=True)

    processed = 0
    skipped = 0
    unmatched = []

    for w_file in ws_files:
        try:
            ws_data = parse_workspace_xml(w_file)
        except Exception:
            skipped += 1
            continue

        ws_name = ws_data["workspace_name"]
        bound_obj = ws_data.get("bound_object", "").lower()

        # Find the matching object schema for this workspace's bound object
        if bound_obj in objects_map:
            matched_objects = {bound_obj: objects_map[bound_obj]}
        elif len(objects_map) == 1:
            # Only one object schema available: use it as fallback
            matched_objects = objects_map
        else:
            # No exact match found — use all schemas for best-effort matching
            matched_objects = objects_map
            unmatched.append(ws_name)

        ws_out_dir = os.path.join(workspaces_dir, ws_name)
        os.makedirs(ws_out_dir, exist_ok=True)

        result = generate_workspace_csvs(ws_data, matched_objects, ws_out_dir)
        processed += 1

        bound_label = ws_data.get("bound_object", "Unknown")
        print(f"Workspace: {ws_name}  (Bound Object: {bound_label})")
        print(f"  workspace_fields.csv                 -> {result['total_workspace_fields']} rows")
        print(f"  combined_workspace_object_fields.csv -> {result['total_workspace_fields']} rows")
        print(f"  Output -> {ws_out_dir}")
        print("")

    if skipped > 0:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")
    if unmatched:
        print(f"[WARNING] No exact object schema found for workspace(s): {', '.join(unmatched)}")

    print("==========================================================================")
    print(f"Completed. {processed} workspace(s) processed.")
    print(f"  Objects    -> {objects_dir}/")
    print(f"  Workspaces -> {workspaces_dir}/")
    print("==========================================================================")

if __name__ == "__main__":
    main()
