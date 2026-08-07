import os
import csv
import re

def normalize_field_name(name):
    """
    Normalizes OSVC field names for cross-matching between workspace layout codes
    and object schema definition fields.
    """
    if not name:
        return ""
    clean = name
    clean = re.sub(r'^(?:[a-zA-Z0-9_]+\.)+', '', clean)
    clean = re.sub(r'^(?:CustomFields\.)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:c\$|c_)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:CO\.)', '', clean, flags=re.IGNORECASE)
    return clean.strip().lower()


def _build_obj_index(objects_map):
    """
    Builds per-object normalized field lookup indices from the shared objects_map.
    Returns dict keyed by lowercase object name -> {normalized_field_name: field_dict}
    """
    obj_fields_indexed = {}
    for oname, odata in objects_map.items():
        obj_by_name = {}
        for of in odata.get("fields", []):
            norm_n = normalize_field_name(of.get("field_name"))
            norm_l = normalize_field_name(of.get("field_label"))
            if norm_n:
                obj_by_name[norm_n] = of
            if norm_l and norm_l not in obj_by_name:
                obj_by_name[norm_l] = of
        obj_fields_indexed[oname] = obj_by_name
    return obj_fields_indexed


def _enrich_workspace_fields(ws_fields, objects_map, bound_object):
    """
    Matches each workspace layout field against its target Object XML schema and
    returns a list of enriched field dicts.
    """
    obj_fields_indexed = _build_obj_index(objects_map)
    matched_object_fields = set()
    enriched = []

    for wf in ws_fields:
        target_obj = wf.get("target_object") or bound_object
        target_obj_key = target_obj.lower()

        f_code = wf.get("field_code", "")
        f_label = wf.get("field_label", "")
        norm_code = normalize_field_name(f_code)
        norm_label = normalize_field_name(f_label)

        target_index = obj_fields_indexed.get(target_obj_key, {})
        if not target_index and len(obj_fields_indexed) == 1:
            target_index = list(obj_fields_indexed.values())[0]

        matched_of = target_index.get(norm_code) or target_index.get(norm_label)

        if matched_of:
            matched_object_fields.add((matched_of.get("object_name", target_obj), matched_of.get("field_name")))
            data_type = matched_of.get("data_type", "Text")
            is_system = matched_of.get("is_system_field", False)
            is_nullable = matched_of.get("is_nullable", True)
            is_lookup = matched_of.get("is_lookup", False)
            max_len = matched_of.get("max_length", "-")
            obj_field_id = matched_of.get("field_id", "-")
        else:
            data_type = "Standard Data Field"
            is_system = True
            is_nullable = True
            is_lookup = "Name" in f_code or "Id" in f_code
            max_len = "-"
            obj_field_id = "-"

        enriched_item = dict(wf)
        enriched_item.update({
            "target_object": target_obj,
            "object_field_id": obj_field_id,
            "data_type": data_type,
            "is_system_field": "Yes" if is_system else "No",
            "is_nullable": "Yes" if is_nullable else "No",
            "is_lookup": "Yes" if is_lookup else "No",
            "max_length": max_len,
        })
        enriched.append(enriched_item)

    return enriched, matched_object_fields


def generate_object_csv(objects_map, output_path):
    """
    Writes a single shared object_fields.csv from all parsed Object XML schemas.
    All object fields are included with an 'Is Used In Workspace' flag.
    Note: usage flag defaults to 'Unknown' when written standalone without workspace context.
    Call generate_workspace_csvs to get accurate per-workspace usage flagging.
    """
    all_obj_fields = []
    for odata in objects_map.values():
        all_obj_fields.extend(odata.get("fields", []))

    headers = [
        "Object Name", "Package Name", "Field ID", "Field Name", "Field Label",
        "Data Type", "Is System Field", "Is Nullable", "Is Lookup", "Is Read Only",
        "Max Length", "Description"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for of in all_obj_fields:
            writer.writerow([
                of["object_name"], of["package_name"], of["field_id"], of["field_name"],
                of["field_label"], of["data_type"],
                "Yes" if of["is_system_field"] else "No",
                "Yes" if of["is_nullable"] else "No",
                "Yes" if of["is_lookup"] else "No",
                "Yes" if of["is_readonly"] else "No",
                of["max_length"], of["description"]
            ])

    return output_path


def generate_workspace_csvs(workspace_data, objects_map, output_dir):
    """
    Writes 2 CSVs for a single workspace into its dedicated output_dir:
    1. workspace_fields.csv  - Layout fields enriched with Object XML metadata
    2. combined_workspace_object_fields.csv - Workspace-as-base merged with Object metadata
    """
    os.makedirs(output_dir, exist_ok=True)

    ws_fields = workspace_data.get("fields", [])
    ws_name = workspace_data.get("workspace_name", "Workspace")
    bound_object = workspace_data.get("bound_object", "Contact")

    enriched_ws_fields, _ = _enrich_workspace_fields(ws_fields, objects_map, bound_object)

    # 1. workspace_fields.csv
    ws_csv_path = os.path.join(output_dir, "workspace_fields.csv")
    ws_headers = [
        "Workspace Name", "Bound Object", "Target Object", "Field Code", "Field Label",
        "Location / Tab", "Row Index", "Column Index", "Required Option",
        "Read Only Option", "Object Field ID", "Data Type", "Is System Field",
        "Is Nullable", "Is Lookup", "Max Length"
    ]
    with open(ws_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(ws_headers)
        for item in enriched_ws_fields:
            writer.writerow([
                item["workspace_name"], item["bound_object"], item["target_object"],
                item["field_code"], item["field_label"], item["location_tab"],
                item["row"], item["column"], item["required_option"], item["readonly_option"],
                item["object_field_id"], item["data_type"], item["is_system_field"],
                item["is_nullable"], item["is_lookup"], item["max_length"]
            ])

    # 2. combined_workspace_object_fields.csv
    combined_csv_path = os.path.join(output_dir, "combined_workspace_object_fields.csv")
    combined_headers = [
        "Workspace Name", "Bound Object", "Target Object", "Field Code / Name", "Field Label",
        "Workspace Tab Location", "Grid Position (Row, Col)", "Required Option",
        "Read Only Option", "Object Field ID", "Data Type", "Is System Field",
        "Is Nullable", "Is Lookup", "Max Length", "In Workspace Layout"
    ]
    with open(combined_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(combined_headers)
        for item in enriched_ws_fields:
            grid_pos = f"Row {item['row']}, Col {item['column']}"
            writer.writerow([
                item["workspace_name"], item["bound_object"], item["target_object"],
                item["field_code"], item["field_label"], item["location_tab"],
                grid_pos, item["required_option"], item["readonly_option"],
                item["object_field_id"], item["data_type"], item["is_system_field"],
                item["is_nullable"], item["is_lookup"], item["max_length"],
                "Yes (Layout Used)"
            ])

    return {
        "workspace_fields_csv": ws_csv_path,
        "combined_csv": combined_csv_path,
        "total_workspace_fields": len(enriched_ws_fields)
    }
