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
    # Strip prefix like Contact., Contact.CustomFields., CustomFields.c., c$, CO.
    clean = name
    clean = re.sub(r'^(?:[a-zA-Z0-9_]+\.)+', '', clean)
    clean = re.sub(r'^(?:CustomFields\.)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:c\$|c_)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:CO\.)', '', clean, flags=re.IGNORECASE)
    return clean.strip().lower()

def generate_csv_reports(workspace_data, object_data, output_dir):
    """
    Generates 3 CSV export files based on Workspace XML layout and Object XML schemas:
    1. workspace_fields.csv (Workspace layout fields enriched with Object XML metadata)
    2. object_fields.csv (All fields defined in Object XML schema)
    3. combined_workspace_object_fields.csv (Workspace layout as primary base enriched with Object XML attributes)
    """
    os.makedirs(output_dir, exist_ok=True)

    ws_fields = workspace_data.get("fields", [])
    obj_fields = object_data.get("fields", [])
    ws_name = workspace_data.get("workspace_name", "Workspace")
    obj_name = object_data.get("object_name", "Object")

    # Index object fields by normalized field name and label for instant lookup
    obj_by_name = {}
    for of in obj_fields:
        norm_n = normalize_field_name(of.get("field_name"))
        norm_l = normalize_field_name(of.get("field_label"))
        if norm_n:
            obj_by_name[norm_n] = of
        if norm_l and norm_l not in obj_by_name:
            obj_by_name[norm_l] = of

    # Track which object fields were matched to workspace layout
    matched_object_names = set()

    # Enrich workspace fields with Object XML data
    enriched_ws_fields = []
    for wf in ws_fields:
        f_code = wf.get("field_code", "")
        f_label = wf.get("field_label", "")
        norm_code = normalize_field_name(f_code)
        norm_label = normalize_field_name(f_label)

        matched_of = obj_by_name.get(norm_code) or obj_by_name.get(norm_label)
        
        if matched_of:
            matched_object_names.add(matched_of.get("field_name"))
            data_type = matched_of.get("data_type", "Text")
            is_system = matched_of.get("is_system_field", False)
            is_nullable = matched_of.get("is_nullable", True)
            is_lookup = matched_of.get("is_lookup", False)
            max_len = matched_of.get("max_length", "—")
            obj_field_id = matched_of.get("field_id", "—")
        else:
            # Fallback for standard layout fields not declared in custom object schema
            data_type = "Standard Data Field"
            is_system = True
            is_nullable = True
            is_lookup = "Name" in f_code or "Id" in f_code
            max_len = "—"
            obj_field_id = "—"

        enriched_item = dict(wf)
        enriched_item.update({
            "object_field_id": obj_field_id,
            "data_type": data_type,
            "is_system_field": "Yes" if is_system else "No",
            "is_nullable": "Yes" if is_nullable else "No",
            "is_lookup": "Yes" if is_lookup else "No",
            "max_length": max_len,
            "is_used_in_workspace": "Yes"
        })
        enriched_ws_fields.append(enriched_item)

    # 1. Output workspace_fields.csv (Workspace Layout Base)
    ws_csv_path = os.path.join(output_dir, "workspace_fields.csv")
    ws_headers = [
        "Workspace Name", "Bound Object", "Field Code", "Field Label",
        "Location / Tab", "Row Index", "Column Index", "Required Option",
        "Read Only Option", "Object Field ID", "Data Type", "Is System Field",
        "Is Nullable", "Is Lookup", "Max Length"
    ]
    with open(ws_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(ws_headers)
        for item in enriched_ws_fields:
            writer.writerow([
                item["workspace_name"], item["bound_object"], item["field_code"],
                item["field_label"], item["location_tab"], item["row"], item["column"],
                item["required_option"], item["readonly_option"], item["object_field_id"],
                item["data_type"], item["is_system_field"], item["is_nullable"],
                item["is_lookup"], item["max_length"]
            ])

    # 2. Output object_fields.csv (Object Schema Base)
    obj_csv_path = os.path.join(output_dir, "object_fields.csv")
    obj_headers = [
        "Object Name", "Package Name", "Field ID", "Field Name", "Field Label",
        "Data Type", "Is System Field", "Is Nullable", "Is Lookup", "Is Read Only",
        "Max Length", "Description", "Is Used In Workspace"
    ]
    with open(obj_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(obj_headers)
        for of in obj_fields:
            is_used = "Yes" if of.get("field_name") in matched_object_names else "No"
            writer.writerow([
                of["object_name"], of["package_name"], of["field_id"], of["field_name"],
                of["field_label"], of["data_type"], "Yes" if of["is_system_field"] else "No",
                "Yes" if of["is_nullable"] else "No", "Yes" if of["is_lookup"] else "No",
                "Yes" if of["is_readonly"] else "No", of["max_length"], of["description"],
                is_used
            ])

    # 3. Output combined_workspace_object_fields.csv (Workspace Base Priority)
    combined_csv_path = os.path.join(output_dir, "combined_workspace_object_fields.csv")
    combined_headers = [
        "Workspace Name", "Object Name", "Field Code / Name", "Field Label",
        "Workspace Tab Location", "Grid Position (Row, Col)", "Required Option",
        "Read Only Option", "Object Field ID", "Data Type", "Is System Field",
        "Is Nullable", "Is Lookup", "Max Length", "In Workspace Layout"
    ]
    with open(combined_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(combined_headers)
        
        # Workspace layout rows first (Primary Base)
        for item in enriched_ws_fields:
            grid_pos = f"Row {item['row']}, Col {item['column']}"
            writer.writerow([
                item["workspace_name"], item["bound_object"], item["field_code"],
                item["field_label"], item["location_tab"], grid_pos,
                item["required_option"], item["readonly_option"], item["object_field_id"],
                item["data_type"], item["is_system_field"], item["is_nullable"],
                item["is_lookup"], item["max_length"], "Yes (Layout Used)"
            ])

    return {
        "workspace_fields_csv": ws_csv_path,
        "object_fields_csv": obj_csv_path,
        "combined_csv": combined_csv_path,
        "total_workspace_fields": len(enriched_ws_fields),
        "total_object_fields": len(obj_fields)
    }
