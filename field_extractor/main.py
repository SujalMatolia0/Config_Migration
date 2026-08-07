import os
import sys
import argparse
from workspace_parser import parse_workspace_xml
from object_parser import parse_object_xml
from csv_exporter import generate_csv_reports

def main():
    parser = argparse.ArgumentParser(description="Standalone OSVC Field Extractor & CSV Generator")
    parser.add_argument("--workspace", required=True, help="Path to Workspace XML file")
    parser.add_argument("--object", required=True, help="Path to Object XML file")
    parser.add_argument("--output", default="./output_csvs", help="Output directory for generated CSV reports")

    args = parser.parse_args()

    workspace_path = os.path.abspath(args.workspace)
    object_path = os.path.abspath(args.object)
    output_dir = os.path.abspath(args.output)

    print("==========================================================================")
    print("           OSVC FIELD EXTRACTOR & CSV GENERATOR ENGINE           ")
    print("==========================================================================")
    print(f"Workspace Input File: {workspace_path}")
    print(f"Object Input File:    {object_path}")
    print(f"Output Directory:     {output_dir}")
    print("--------------------------------------------------------------------------")

    if not os.path.exists(workspace_path):
        print(f"[ERROR] Workspace file not found: {workspace_path}")
        sys.exit(1)

    if not os.path.exists(object_path):
        print(f"[ERROR] Object file not found: {object_path}")
        sys.exit(1)

    # 1. Parse Workspace XML layout fields
    ws_data = parse_workspace_xml(workspace_path)
    print(f"[SUCCESS] Parsed Workspace '{ws_data['workspace_name']}' layout base -> Found {ws_data['total_layout_fields']} fields in layout.")

    # 2. Parse Object XML schema fields
    obj_data = parse_object_xml(object_path)
    print(f"[SUCCESS] Parsed Object '{obj_data['object_name']}' schema definition -> Found {obj_data['total_object_fields']} total defined fields.")

    # 3. Match fields and export 3 CSV reports
    result = generate_csv_reports(ws_data, obj_data, output_dir)
    print("--------------------------------------------------------------------------")
    print(f"[SUCCESS] Workspace Layout CSV: {result['workspace_fields_csv']} ({result['total_workspace_fields']} layout rows)")
    print(f"[SUCCESS] Object Schema CSV:   {result['object_fields_csv']} ({result['total_object_fields']} schema rows)")
    print(f"[SUCCESS] Combined Base CSV:   {result['combined_csv']} ({result['total_workspace_fields']} workspace-base rows)")
    print("==========================================================================")
    print("Field extraction and CSV generation completed successfully.")

if __name__ == "__main__":
    main()
