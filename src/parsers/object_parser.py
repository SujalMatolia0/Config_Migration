import os
from lxml import etree

def parse_custom_object_file(file_path):
    """
    Parses a CustomObject XML export (e.g. ObjectContact_1.xml or ObjectTest_Record_2.xml)
    and extracts custom object attributes, fields, keys, and packages.
    """
    try:
        parser = etree.XMLParser(recover=True, remove_comments=True)
        tree = etree.parse(file_path, parser=parser)
        root = tree.getroot()
        
        obj_id = root.get("Id")
        obj_name = root.get("Name")
        co_label = root.get("CoLabel") or obj_name
        description = root.get("Description") or ""
        
        # Package info
        pkg_elem = root.find("Package")
        pkg_name = pkg_elem.get("Name") if pkg_elem is not None else "CO"
        pkg_id = pkg_elem.get("Id") if pkg_elem is not None else ""
        
        fields = []
        fields_elem = root.find("Fields")
        if fields_elem is not None:
            for f in fields_elem.findall("Field"):
                fields.append({
                    "id": f.get("Id"),
                    "name": f.get("Name"),
                    "label": f.get("Label") or f.get("Name"),
                    "data_type": f.get("DataTypeName") or f.get("DataType"),
                    "is_nullable": f.get("IsNullable") == "True",
                    "is_system": f.get("IsSystemField") == "True",
                    "package_name": f.get("PackageName") or pkg_name,
                    "description": f.get("Description") or ""
                })
                
        keys = []
        keys_elem = root.find("Keys")
        if keys_elem is not None:
            for k in keys_elem.findall("Key"):
                k_fields = [f.get("Id") for f in k.findall(".//Field") if f.get("Id")]
                keys.append({
                    "id": k.get("Id"),
                    "type": k.get("KeyType"),
                    "fields": k_fields
                })
                
        from src.parsers.utils import capture_unknown_recursive
        from src.parsers.known_tags_registry import KNOWN_OBJECT_ALL_TAGS, KNOWN_OBJECT_ALL_ATTRS
        unk = capture_unknown_recursive(root, KNOWN_OBJECT_ALL_TAGS, KNOWN_OBJECT_ALL_ATTRS, f"CustomObject: {obj_name}")
        u_attrs = unk.get("unknown_attrs", {})
        u_children = unk.get("unknown_children", [])
        unknown_attrs_list = [{"attribute": item.get("attribute"), "path": item.get("path"), "value": item.get("value")} for item in u_attrs.values()] if isinstance(u_attrs, dict) else u_attrs
        unknown_children_list = u_children

        return {
            "format": "custom_object",
            "type": "CustomObject",
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "id": obj_id,
            "name": obj_name,
            "label": co_label,
            "package": pkg_name,
            "package_id": pkg_id,
            "description": description,
            "is_agent_visible": root.get("IsAgentVisible") == "True",
            "is_analytics_visible": root.get("IsAnalyticsVisible") == "True",
            "fields": fields,
            "keys": keys,
            "unhandled_elements": unknown_children_list,
            "unknowns": {
                "unknown_attrs": unknown_attrs_list,
                "unknown_children": unknown_children_list
            }
        }
    except Exception as e:
        return {
            "format": "custom_object",
            "type": "CustomObject",
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "error": str(e)
        }

def parse_relationship_file(file_path):
    """
    Parses a Relationship XML export (e.g. Relationship10001_2.xml)
    and extracts parent/child class links and cardinality.
    """
    try:
        parser = etree.XMLParser(recover=True, remove_comments=True)
        tree = etree.parse(file_path, parser=parser)
        root = tree.getroot()
        
        from src.parsers.utils import capture_unknown_recursive
        from src.parsers.known_tags_registry import KNOWN_OBJECT_ALL_TAGS, KNOWN_OBJECT_ALL_ATTRS
        
        unk = capture_unknown_recursive(root, KNOWN_OBJECT_ALL_TAGS, KNOWN_OBJECT_ALL_ATTRS, f"Relationship: {os.path.basename(file_path)}")
        u_attrs = unk.get("unknown_attrs", {})
        u_children = unk.get("unknown_children", [])
        unknown_attrs_list = [{"attribute": item.get("attribute"), "path": item.get("path"), "value": item.get("value")} for item in u_attrs.values()] if isinstance(u_attrs, dict) else u_attrs
        unknown_children_list = u_children

        return {
            "format": "relationship",
            "type": "Relationship",
            "name": os.path.basename(file_path).replace(".xml", ""),
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "id": root.get("Id"),
            "parent_class_id": root.get("ParentClassId"),
            "child_class_id": root.get("ChildClassId"),
            "child_key_id": root.get("ChildKeyId"),
            "relationship_type": root.get("RelationshipType"),
            "parent_cardinality": root.get("ParentCardinality"),
            "child_cardinality": root.get("ChildCardinality"),
            "unhandled_elements": unknown_children_list,
            "unknowns": {
                "unknown_attrs": unknown_attrs_list,
                "unknown_children": unknown_children_list
            }
        }
    except Exception as e:
        return {
            "format": "relationship",
            "type": "Relationship",
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "error": str(e)
        }
