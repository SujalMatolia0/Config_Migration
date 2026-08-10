import os
import xml.etree.ElementTree as ET

def parse_object_xml(file_path):
    """
    Parses an OSVC Object Definition XML file (or multi-object container XML)
    and extracts all defined fields along with data types, nullability, lookup attributes, system flags, etc.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Object XML not found: {file_path}")

    tree = ET.parse(file_path)
    root = tree.getroot()

    custom_objects = root.findall(".//CustomObject")
    if root.tag == "CustomObject" and root not in custom_objects:
        custom_objects = [root]
    elif not custom_objects and root.find(".//Fields") is None:
        raise ValueError(f"File {file_path} is not a valid CustomObject XML.")
    elif not custom_objects:
        custom_objects = [root]

    results = []
    for c_obj in custom_objects:
        obj_name = c_obj.get("Name") or c_obj.get("CoLabel") or os.path.basename(file_path).replace(".xml", "")
        package_elem = c_obj.find("Package")
        package_name = package_elem.get("Name") if package_elem is not None else "CO"

        fields = []
        for f in c_obj.findall(".//Fields/Field"):
            f_id = f.get("Id") or ""
            f_name = f.get("Name") or ""
            f_label = f.get("Label") or f_name
            data_type = f.get("DataTypeName") or f.get("DataType") or "Text"
            is_nullable = f.get("IsNullable", "True").lower() in ("true", "1")
            is_list = f.get("IsList", "False").lower() in ("true", "1")
            is_lookup = f.get("IsLookup", "False").lower() in ("true", "1")
            is_readonly = f.get("IsCoReadOnly", "False").lower() in ("true", "1")
            is_autoupdate = f.get("IsAutoUpdate", "False").lower() in ("true", "1")
            is_sequence = f.get("IsSequence", "False").lower() in ("true", "1")
            is_system = f.get("IsSystemField", "False").lower() in ("true", "1")
            max_len_val = (
                f.get("MaxLength") or f.get("Size") or f.get("MaxLen") or f.get("Length") or
                (f.find("TextLength").text if f.find("TextLength") is not None else None) or
                (f.find("Size").text if f.find("Size") is not None else None) or
                "-"
            )

            f_pkg = f.get("PackageName") or f.get("Package") or package_name
            desc = f.get("Description") or ""
            pattern = f.get("Pattern") or "-"
            usage = f.get("Usage") or "-"

            fields.append({
                "object_name": obj_name,
                "package_name": f_pkg,
                "field_id": f_id,
                "field_name": f_name,
                "field_label": f_label,
                "data_type": data_type,
                "is_system_field": is_system,
                "is_nullable": is_nullable,
                "is_list": is_list,
                "is_lookup": is_lookup,
                "is_readonly": is_readonly,
                "is_autoupdate": is_autoupdate,
                "is_sequence": is_sequence,
                "max_length": max_len_val,
                "description": desc,
                "pattern": pattern,
                "usage": usage
            })

        results.append({
            "object_name": obj_name,
            "package_name": package_name,
            "total_object_fields": len(fields),
            "fields": fields
        })

    return results if len(results) > 1 else (results[0] if results else {})
