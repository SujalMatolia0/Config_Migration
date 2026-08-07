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
    parser.add_argument("--output", default="./output_csvs", help="Output directory for generated CSV reports")

    args = parser.parse_args()

    workspace_path = os.path.abspath(args.workspace)
    object_path = os.path.abspath(args.object)
    output_dir = os.path.abspath(args.output)

    print("==========================================================================")
    print("           OSVC OBJECT-BASED FIELD EXTRACTOR & CSV ENGINE          ")
    print("==========================================================================")
    print(f"Workspace Input: {workspace_path}")
    print(f"Object Input:    {object_path}")
    print(f"Output Directory: {output_dir}")
    print("--------------------------------------------------------------------------")

    if not os.path.exists(workspace_path):
        print(f"[ERROR] Workspace path not found: {workspace_path}")
        sys.exit(1)

    if not os.path.exists(object_path):
        print(f"[ERROR] Object path not found: {object_path}")
        sys.exit(1)

    # 1. Parse Workspace XML layout fields (file or directory)
    ws_files = []
    if os.path.isdir(workspace_path):
        for root_dir, _, files in os.walk(workspace_path):
            for f in files:
                if f.endswith(".xml"):
                    ws_files.append(os.path.join(root_dir, f))
    else:
        ws_files.append(workspace_path)

    combined_ws_fields = []
    ws_name_list = []
    primary_bound_obj = "Contact"

    for w_file in ws_files:
        try:
            ws_data = parse_workspace_xml(w_file)
            combined_ws_fields.extend(ws_data.get("fields", []))
            ws_name_list.append(ws_data["workspace_name"])
            primary_bound_obj = ws_data.get("bound_object", primary_bound_obj)
        except Exception:
            # Skip XML files that are not valid Workspace XMLs
            pass

    ws_data_aggregated = {
        "workspace_name": ", ".join(ws_name_list),
        "bound_object": primary_bound_obj,
        "fields": combined_ws_fields
    }
    print(f"[SUCCESS] Parsed {len(ws_files)} Workspace layout file(s) -> Aggregated {len(combined_ws_fields)} layout fields.")

    # 2. Parse Object XML schema fields (file or directory)
    obj_files = []
    if os.path.isdir(object_path):
        for root_dir, _, files in os.walk(object_path):
            for f in files:
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
    print(f"[SUCCESS] Parsed {len(objects_map)} Object schema definition(s) -> Found {total_schema_fields} total schema fields.")

    # 3. Match fields on Object-level basis and export 3 CSV reports
    result = generate_csv_reports(ws_data_aggregated, objects_map, output_dir)
    print("--------------------------------------------------------------------------")
    print(f"[SUCCESS] Workspace Layout CSV: {result['workspace_fields_csv']} ({result['total_workspace_fields']} layout rows)")
    print(f"[SUCCESS] Object Schema CSV:   {result['object_fields_csv']} ({result['total_object_fields']} schema rows)")
    print(f"[SUCCESS] Combined Base CSV:   {result['combined_csv']} ({result['total_workspace_fields']} workspace-base rows)")
    print("==========================================================================")
    print("Object-level field extraction and CSV generation completed successfully.")

if __name__ == "__main__":
    main()
