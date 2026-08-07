import os
import xml.etree.ElementTree as ET

def parse_object_xml(file_path):
    """
    Parses an OSVC Object Definition XML file and extracts all defined fields
    along with data types, nullability, lookup attributes, system flags, etc.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Object XML not found: {file_path}")

    tree = ET.parse(file_path)
    root = tree.getroot()

    obj_name = root.get("Name") or root.get("CoLabel") or os.path.basename(file_path).replace(".xml", "")
    package_elem = root.find("Package")
    package_name = package_elem.get("Name") if package_elem is not None else "CO"

    fields = []
    
    for f in root.findall(".//Fields/Field"):
        f_id = f.get("Id") or ""
        f_name = f.get("Name") or ""
        f_label = f.get("Label") or f_name
        data_type = f.get("DataTypeName") or f.get("DataType") or "Text"
        is_nullable = f.get("IsNullable", "True").lower() in ("true", "1")
        is_lookup = f.get("IsLookup", "False").lower() in ("true", "1")
        is_readonly = f.get("IsCoReadOnly", "False").lower() in ("true", "1")
        is_system = f.get("IsSystemField", "False").lower() in ("true", "1")
        max_length = f.get("MaxLength") or "—"
        desc = f.get("Description") or ""

        fields.append({
            "object_name": obj_name,
            "package_name": package_name,
            "field_id": f_id,
            "field_name": f_name,
            "field_label": f_label,
            "data_type": data_type,
            "is_system_field": is_system,
            "is_nullable": is_nullable,
            "is_lookup": is_lookup,
            "is_readonly": is_readonly,
            "max_length": max_length,
            "description": desc
        })

    return {
        "object_name": obj_name,
        "package_name": package_name,
        "total_object_fields": len(fields),
        "fields": fields
    }
