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

    ws_name = os.path.basename(file_path).replace(".xml", "")
    bound_object = root.get("Type") or root.get("UIType") or "Unknown"

    fields = []
    
    # Process all tabs and layout containers
    def find_parent_tab(elem):
        parent = elem
        while parent is not None:
            if parent.tag == "Tab":
                return parent.get("Text") or parent.get("TextLabelName") or "Layout Tab"
            # ET doesn't store parent pointers, handled below by walking tabs
        return "Top Form Layout"

    # Walk through TabSet -> Tab structure
    tabs = root.findall(".//Tab")
    
    if not tabs:
        # Simple form layout without explicit tabs
        for f in root.findall(".//Field"):
            f_code = f.get("FieldId") or f.get("Name") or ""
            if f_code and not f_code.startswith(bound_object + "."):
                f_code = f"{bound_object}.{f_code}"
            
            fields.append({
                "workspace_name": ws_name,
                "bound_object": bound_object,
                "field_code": f_code,
                "field_label": f.get("LabelText") or f.get("Label") or f_code.split(".")[-1],
                "location_tab": "Main Layout",
                "row": f.get("Row", "0"),
                "column": f.get("Column", "0"),
                "required_option": f.get("RequiredOption", "No"),
                "readonly_option": f.get("ReadOnlyOption", "No"),
                "report_id": f.get("ReportId", "")
            })
    else:
        for tab in tabs:
            tab_name = tab.get("Text") or tab.get("TextLabelName") or "General Tab"
            for f in tab.findall(".//Field"):
                f_code = f.get("FieldId") or f.get("Name") or ""
                if f_code and not f_code.startswith(bound_object + "."):
                    f_code = f"{bound_object}.{f_code}"

                fields.append({
                    "workspace_name": ws_name,
                    "bound_object": bound_object,
                    "field_code": f_code,
                    "field_label": f.get("LabelText") or f.get("Label") or f_code.split(".")[-1],
                    "location_tab": tab_name,
                    "row": f.get("Row", "0"),
                    "column": f.get("Column", "0"),
                    "required_option": f.get("RequiredOption", "No"),
                    "readonly_option": f.get("ReadOnlyOption", "No"),
                    "report_id": f.get("ReportId", "")
                })

        # Also extract top-level form fields outside tabs
        for f in root.findall("./Table/Field"):
            f_code = f.get("FieldId") or f.get("Name") or ""
            if f_code and not f_code.startswith(bound_object + "."):
                f_code = f"{bound_object}.{f_code}"

            if not any(item["field_code"] == f_code for item in fields):
                fields.append({
                    "workspace_name": ws_name,
                    "bound_object": bound_object,
                    "field_code": f_code,
                    "field_label": f.get("LabelText") or f.get("Label") or f_code.split(".")[-1],
                    "location_tab": "Top Form Layout",
                    "row": f.get("Row", "0"),
                    "column": f.get("Column", "0"),
                    "required_option": f.get("RequiredOption", "No"),
                    "readonly_option": f.get("ReadOnlyOption", "No"),
                    "report_id": f.get("ReportId", "")
                })

    return {
        "workspace_name": ws_name,
        "bound_object": bound_object,
        "total_layout_fields": len(fields),
        "fields": fields
    }
