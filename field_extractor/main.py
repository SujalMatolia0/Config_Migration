"""
Standalone OSVC Field Extractor - Excel Export Engine.

Parses OSVC Workspace XML files, Object XML schemas (or live REST API metadata),
and Custom Fields Excel exports (including Menu Custom Fields & Options) to generate multi-tab Excel reports:
- Standard_Objects.xlsx
- Custom_Objects.xlsx
- Workspaces.xlsx & Workspaces_No_Ignored.xlsx
- Field_Catalog.xlsx & Field_Catalog_No_Ignored.xlsx
- Custom_Fields_Mapping.xlsx
"""

import os
import sys
import argparse

try:
    from parsers.workspace_parser import parse_workspace_xml
    from parsers.object_parser import parse_object_xml
    from parsers.custom_field_excel_parser import parse_custom_fields_excel
    from exporters.excel_exporter import (
        write_workspaces_excel, write_objects_excel,
        write_combined_excel, write_custom_fields_mapping_excel
    )
    from fetchers.osvc_rest_fetcher import fetch_standard_objects_via_rest
    from web_ui import load_standard_objects_from_excel, merge_objects_maps
except ImportError:
    from field_extractor.parsers.workspace_parser import parse_workspace_xml
    from field_extractor.parsers.object_parser import parse_object_xml
    from field_extractor.parsers.custom_field_excel_parser import parse_custom_fields_excel
    from field_extractor.exporters.excel_exporter import (
        write_workspaces_excel, write_objects_excel,
        write_combined_excel, write_custom_fields_mapping_excel
    )
    from field_extractor.fetchers.osvc_rest_fetcher import fetch_standard_objects_via_rest
    from field_extractor.web_ui import load_standard_objects_from_excel, merge_objects_maps


def _find_xml_files(target_path):
    """Recursively collects all XML files from a file path or directory."""
    if not target_path or not os.path.exists(target_path):
        return []

    abs_path = os.path.abspath(target_path)
    if not os.path.isdir(abs_path):
        return [abs_path] if abs_path.endswith(".xml") else []

    xml_files = []
    for root_dir, _, files in os.walk(abs_path):
        for fname in sorted(files):
            if fname.endswith(".xml") and not fname.startswith("."):
                xml_files.append(os.path.join(root_dir, fname))
    return xml_files


def _load_custom_fields(args):
    """Parses Custom Fields and Menu Custom Fields Excel exports if available."""
    f1 = None
    f2 = None

    if hasattr(args, 'custom_fields') and args.custom_fields and os.path.exists(args.custom_fields):
        f1 = args.custom_fields
    elif os.path.exists("./input/custom_fields/Custom_Fields.xlsx"):
        f1 = "./input/custom_fields/Custom_Fields.xlsx"

    if hasattr(args, 'custom_menu') and args.custom_menu and os.path.exists(args.custom_menu):
        f2 = args.custom_menu
    elif os.path.exists("./input/custom_fields/Custom_Fields_Type_Menu.xlsx"):
        f2 = "./input/custom_fields/Custom_Fields_Type_Menu.xlsx"

    if f1 or f2:
        print("[INFO] Parsing Custom Fields & Menu Options Excel exports...")
        cf_map = parse_custom_fields_excel(f1, f2)
        unique_cnt = len(set(v['column_name'] for v in cf_map.values()))
        menu_cnt = len([v for v in cf_map.values() if v.get('menu_items')])
        print(f"[OK] Custom Fields loaded: {unique_cnt} fields ({menu_cnt} Menu fields with options)")
        return cf_map

    return {}


def _load_objects(args):
    """Loads standard object schemas via REST API / schemas folder, and custom objects via XML files."""
    std_map = {}
    cst_map = {}

    # 1. Option A: Fetch standard object schemas via REST API (STRICT HTTP GET ONLY)
    if args.rest_host and args.rest_user and args.rest_pass:
        print("[MODE] REST API Live Extraction (STRICT READ-ONLY GET)")
        std_map = fetch_standard_objects_via_rest(
            host=args.rest_host,
            username=args.rest_user,
            password=args.rest_pass,
            include_custom=True
        )
    else:
        # Fallback to pre-extracted standard objects from schemas/Standard_Objects.xlsx
        std_map = load_standard_objects_from_excel() or {}

    # 2. Parse Custom Object XML files
    if args.object:
        obj_files = _find_xml_files(args.object)
        for o_file in obj_files:
            try:
                res = parse_object_xml(o_file)
                o_items = res if isinstance(res, list) else ([res] if res else [])
                for o_data in o_items:
                    obj_name = o_data.get("object_name", "")
                    if obj_name:
                        cst_map[obj_name.lower()] = o_data
                        field_cnt = len(o_data.get("fields", []))
                        print(f"[OK] Custom Object loaded from XML: {obj_name} ({field_cnt} fields)")
            except Exception:
                pass

    # 3. Fallback: Config credentials if no standard objects loaded
    if not std_map:
        try:
            from config import BASE_URL, USERNAME, PASSWORD
            if BASE_URL and USERNAME and PASSWORD:
                print("[INFO] Auto-fetching standard object schemas via REST API using config.py credentials...")
                std_map = fetch_standard_objects_via_rest(
                    host=BASE_URL,
                    username=USERNAME,
                    password=PASSWORD,
                    include_custom=True
                )
        except ImportError:
            pass

    return std_map, cst_map


def _load_workspaces(args):
    """Parses workspace XML files."""
    parsed_workspaces = []
    skipped = 0

    if args.workspace:
        ws_files = _find_xml_files(args.workspace)
        for w_file in ws_files:
            try:
                ws_data = parse_workspace_xml(w_file)
                parsed_workspaces.append(ws_data)
                bound = ws_data.get("bound_object", "Unknown")
                count = ws_data.get("total_layout_fields", 0)
                ws_name = ws_data.get("workspace_name", "Workspace")
                print(f"[OK] Workspace loaded: {ws_name} (Bound: {bound}, {count} fields)")
            except Exception:
                skipped += 1

    if skipped:
        print(f"[WARNING] Skipped {skipped} non-Workspace XML file(s).")

    return parsed_workspaces


def _export_reports(std_map, cst_map, parsed_workspaces, output_dir, custom_fields_map=None):
    """Generates all Excel report files."""
    std_xlsx            = os.path.join(output_dir, "Standard_Objects.xlsx")
    cst_xlsx            = os.path.join(output_dir, "Custom_Objects.xlsx")
    ws_xlsx             = os.path.join(output_dir, "Workspaces.xlsx")
    ws_no_ignored_xlsx  = os.path.join(output_dir, "Workspaces_No_Ignored.xlsx")
    ws_simplified_xlsx  = os.path.join(output_dir, "Workspaces_Simplified.xlsx")
    comb_xlsx           = os.path.join(output_dir, "Field_Catalog.xlsx")
    comb_no_ignored_xlsx= os.path.join(output_dir, "Field_Catalog_No_Ignored.xlsx")
    comb_simplified_xlsx= os.path.join(output_dir, "Field_Catalog_Simplified.xlsx")
    cf_xlsx             = os.path.join(output_dir, "Custom_Fields_Mapping.xlsx")

    combined_map = merge_objects_maps(std_map, cst_map)

    if std_map:
        write_objects_excel(std_map, std_xlsx, custom_fields_map=custom_fields_map)
        print(f"[SUCCESS] Standard_Objects.xlsx          -> {std_xlsx}")

    if cst_map:
        write_objects_excel(cst_map, cst_xlsx, custom_fields_map=custom_fields_map)
        print(f"[SUCCESS] Custom_Objects.xlsx            -> {cst_xlsx}")

    if custom_fields_map:
        write_custom_fields_mapping_excel(custom_fields_map, cf_xlsx)
        print(f"[SUCCESS] Custom_Fields_Mapping.xlsx     -> {cf_xlsx}")

    write_workspaces_excel(parsed_workspaces, combined_map, ws_xlsx, include_ignored_tab=True, custom_fields_map=custom_fields_map)
    print(f"[SUCCESS] Workspaces.xlsx                -> {ws_xlsx}")

    write_workspaces_excel(parsed_workspaces, combined_map, ws_no_ignored_xlsx, include_ignored_tab=False, custom_fields_map=custom_fields_map)
    print(f"[SUCCESS] Workspaces_No_Ignored.xlsx     -> {ws_no_ignored_xlsx}")

    write_workspaces_excel(parsed_workspaces, combined_map, ws_simplified_xlsx, include_ignored_tab=False, custom_fields_map=custom_fields_map, simplify_attributes=True)
    print(f"[SUCCESS] Workspaces_Simplified.xlsx     -> {ws_simplified_xlsx}")

    write_combined_excel(parsed_workspaces, combined_map, comb_xlsx, include_ignored_tab=True, custom_fields_map=custom_fields_map)
    print(f"[SUCCESS] Field_Catalog.xlsx             -> {comb_xlsx}")

    write_combined_excel(parsed_workspaces, combined_map, comb_no_ignored_xlsx, include_ignored_tab=False, custom_fields_map=custom_fields_map)
    print(f"[SUCCESS] Field_Catalog_No_Ignored.xlsx  -> {comb_no_ignored_xlsx}")

    write_combined_excel(parsed_workspaces, combined_map, comb_simplified_xlsx, include_ignored_tab=False, custom_fields_map=custom_fields_map, simplify_attributes=True)
    print(f"[SUCCESS] Field_Catalog_Simplified.xlsx -> {comb_simplified_xlsx}")


def main():
    parser = argparse.ArgumentParser(description="Standalone OSVC Field Extractor - Excel Output")
    parser.add_argument("--workspace",     required=False, help="Path to Workspace XML file or directory")
    parser.add_argument("--object",        required=False, help="Path to Object XML file or directory")
    parser.add_argument("--custom-fields", required=False, help="Path to Custom Fields export Excel file")
    parser.add_argument("--custom-menu",   required=False, help="Path to Custom Fields of Type Menu export Excel file")
    default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    parser.add_argument("--output", default=default_out, help="Output directory for Excel files")
    parser.add_argument("--rest-host",     help="OSVC Host URL for live REST API metadata extraction (HTTP GET only)")
    parser.add_argument("--rest-user",     help="OSVC REST API Username")
    parser.add_argument("--rest-pass",     help="OSVC REST API Password")

    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    print("==========================================================================")
    print("       OSVC FIELD EXTRACTOR - EXCEL EXPORT ENGINE                ")
    print("==========================================================================")
    print(f"Output Directory: {output_dir}")
    print("--------------------------------------------------------------------------")

    # 1. Load Custom Fields mappings if available
    custom_fields_map = _load_custom_fields(args)

    # 2. Load Object schemas
    std_map, cst_map = _load_objects(args)
    if not std_map and not cst_map and not custom_fields_map:
        print("[ERROR] No valid Object schemas loaded from REST or XML files. Exiting.")
        sys.exit(1)

    if cst_map:
        from field_extractor.parsers.custom_field_excel_parser import enrich_custom_fields_with_custom_objects
        custom_fields_map = enrich_custom_fields_with_custom_objects(custom_fields_map, cst_map)

    # 3. Load Workspace definitions
    parsed_workspaces = _load_workspaces(args)

    print("--------------------------------------------------------------------------")

    # 4. Export all Excel reports
    _export_reports(std_map, cst_map, parsed_workspaces, output_dir, custom_fields_map=custom_fields_map)

    print("==========================================================================")
    print(f"Done. Reports written to: {output_dir}")
    print("==========================================================================")

    print("==========================================================================")
    print(f"Done. Reports written to: {output_dir}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
