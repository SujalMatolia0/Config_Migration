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

    if root.tag != "CustomObject" and root.find(".//Fields") is None:
        raise ValueError(f"File {file_path} is not a valid CustomObject XML.")

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
        max_len_val = (
            f.get("MaxLength") or f.get("Size") or f.get("MaxLen") or f.get("Length") or
            (f.find("TextLength").text if f.find("TextLength") is not None else None) or
            (f.find("Size").text if f.find("Size") is not None else None) or
            "-"
        )

        f_pkg = f.get("PackageName") or f.get("Package") or package_name
        
        desc = f.get("Description") or ""

        fields.append({
            "object_name": obj_name,
            "package_name": f_pkg,
            "field_id": f_id,
            "field_name": f_name,
            "field_label": f_label,
            "data_type": data_type,
            "is_system_field": is_system,
            "is_nullable": is_nullable,
            "is_lookup": is_lookup,
            "is_readonly": is_readonly,
            "max_length": max_len_val,
            "description": desc
        })

    return {
        "object_name": obj_name,
        "package_name": package_name,
        "total_object_fields": len(fields),
        "fields": fields
    }
