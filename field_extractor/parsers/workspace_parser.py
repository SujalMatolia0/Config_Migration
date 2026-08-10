import os
import xml.etree.ElementTree as ET

def parse_workspace_xml(file_path):
    """
    Parses an OSVC Workspace XML file and extracts all layout fields,
    relationship items, add-in items, and tab locations.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Workspace XML not found: {file_path}")

    tree = ET.parse(file_path)
    root = tree.getroot()

    if root.tag != "Workspace" and root.find(".//TabSet") is None and root.find(".//Table") is None:
        raise ValueError(f"File {file_path} is not a valid Workspace XML.")

    ws_name = os.path.basename(file_path).replace(".xml", "")
    bound_object = root.get("Type") or root.get("UIType") or "Unknown"

    fields = []

    def extract_field_info(f, tab_name):
        obj_id = f.get("ObjectId") or bound_object
        f_code = f.get("FieldId") or f.get("Name") or ""
        if f_code and not f_code.startswith(obj_id + ".") and not f_code.startswith("CustomFields."):
            full_code = f"{obj_id}.{f_code}"
        else:
            full_code = f_code if f_code.startswith(obj_id + ".") else f"{obj_id}.{f_code}"

        return {
            "workspace_name": ws_name,
            "bound_object": bound_object,
            "target_object": obj_id,
            "field_code": full_code,
            "raw_field_id": f_code,
            "field_label": f.get("LabelText") or f.get("Label") or full_code.split(".")[-1],
            "location_tab": tab_name,
            "row": f.get("Row", "0"),
            "column": f.get("Column", "0"),
            "required_option": f.get("RequiredOption", "No"),
            "readonly_option": f.get("ReadOnlyOption", "No"),
            "report_id": f.get("ReportId", "")
        }

    # Walk through TabSet -> Tab structure
    tabs = root.findall(".//Tab")

    if not tabs:
        # Simple form layout without explicit tabs
        for f in root.findall(".//Field"):
            fields.append(extract_field_info(f, "Main Layout"))
    else:
        for tab in tabs:
            tab_name = tab.get("Text") or tab.get("TextLabelName") or "General Tab"
            for f in tab.findall(".//Field"):
                fields.append(extract_field_info(f, tab_name))

        # Also extract top-level form fields outside tabs
        for f in root.findall("./Table/Field"):
            item = extract_field_info(f, "Top Form Layout")
            if not any(existing["field_code"] == item["field_code"] for existing in fields):
                fields.append(item)

    return {
        "workspace_name": ws_name,
        "bound_object": bound_object,
        "total_layout_fields": len(fields),
        "fields": fields
    }
