import os
from lxml import etree

def parse_report_file(file_path):
    """
    Parses an OSVC Report XML export file and returns structured metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Report file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    # Try to get report name and ID from root attributes or child elements
    report_id = root.get("Id") or root.get("id")
    report_name = root.get("Name") or root.get("name")
    object_type = root.get("ObjectType") or root.get("object_type")

    # Fallback to searching tags if not in root attributes
    if not report_id:
        id_elem = root.find(".//ReportId") or root.find(".//id")
        if id_elem is not None:
            report_id = id_elem.text
            
    if not report_name:
        name_elem = root.find(".//ReportName") or root.find(".//name")
        if name_elem is not None:
            report_name = name_elem.text
        else:
            report_name = os.path.basename(file_path).replace(".xml", "")

    if not object_type:
        obj_elem = root.find(".//ObjectType") or root.find(".//object_type")
        if obj_elem is not None:
            object_type = obj_elem.text

    # Extract Columns and their source fields
    columns = []
    for col in root.findall(".//Column"):
        col_name = col.get("Name") or col.get("name")
        source = col.find("Source")
        source_field = source.text if source is not None else col.get("Source")
        
        # Fallback search if elements nested
        if not col_name:
            label_elem = col.find(".//Label") or col.find(".//Heading")
            if label_elem is not None:
                col_name = label_elem.text

        columns.append({
            "name": col_name,
            "source_field": source_field
        })

    # Extract Filters
    filters = []
    for filt in root.findall(".//Filter"):
        filt_name = filt.get("Name") or filt.get("name")
        field = filt.find("Field")
        field_val = field.text if field is not None else filt.get("Field")
        oper = filt.find("Operator")
        oper_val = oper.text if oper is not None else filt.get("Operator")

        filters.append({
            "name": filt_name,
            "field": field_val,
            "operator": oper_val
        })

    # Extract Linked Reports / Sub-reports
    sub_reports = []
    # Search for attributes or nodes referencing sub-report IDs (like SubReportId, AcId)
    for sr in root.findall(".//*[@SubReportId]") + root.findall(".//SubReport") + root.findall(".//*[@AcId]"):
        sr_id = sr.get("SubReportId") or sr.get("AcId") or sr.get("id")
        sr_name = sr.get("Name") or sr.get("name")
        
        if sr_id and sr_id not in sub_reports:
            sub_reports.append({
                "id": sr_id,
                "name": sr_name
            })

    return {
        "id": report_id,
        "name": report_name,
        "object_type": object_type,
        "columns": columns,
        "filters": filters,
        "sub_reports": sub_reports
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_report_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python report_parser.py <path_to_report_xml>")
