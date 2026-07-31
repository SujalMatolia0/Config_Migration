import os
from lxml import etree
from src.parsers.utils import capture_unknown
from src.parsers.known_tags_registry import KNOWN_NAV_ATTRS, KNOWN_NAV_CHILDREN

def parse_nav_file(file_path):
    """
    Parses an OSVC Navigation Set XML export file and returns structured metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Navigation Set file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    nav_set_name = root.get("Name") or root.get("name") or os.path.basename(file_path).replace(".xml", "")
    
    unhandled_elements = []
    root_unk = capture_unknown(root, KNOWN_NAV_ATTRS, KNOWN_NAV_CHILDREN, "Navigation Set Root")
    if root_unk and "unknown_children" in root_unk:
        for child in root_unk["unknown_children"]:
            unhandled_elements.append({
                "tag": child["tag"],
                "raw_xml": child["raw"]
            })

    # Navigation items list
    items = []
    # Search for all item-like nodes (e.g., NavItem, Item, MenuItem)
    item_nodes = root.findall(".//NavItem") + root.findall(".//Item") + root.findall(".//MenuItem")
    
    for item in item_nodes:
        text = item.get("Text") or item.get("Label") or item.get("name")
        item_type = item.get("Type") or item.get("item_type")
        workspace = item.get("Workspace") or item.get("WorkspaceName") or item.get("workspace")
        report_id = item.get("ReportId") or item.get("AcId") or item.get("report_id")
        
        # Fallback to check children if attributes don't exist
        if not text:
            text_node = item.find("Text") or item.find("Label")
            if text_node is not None:
                text = text_node.text

        if not item_type:
            type_node = item.find("Type")
            if type_node is not None:
                item_type = type_node.text

        if workspace or report_id or text:
            items.append({
                "label": text,
                "type": item_type or "Unknown",
                "workspace": workspace,
                "report_id": report_id
            })



    # Profiles referenced in this navigation set
    profiles = []
    profile_nodes = root.findall(".//Profile") + root.findall(".//AllowedProfile")
    for prof in profile_nodes:
        prof_name = prof.get("Name") or prof.get("name") or prof.text
        if prof_name and prof_name not in profiles:
            profiles.append(prof_name)

    u_attrs = root_unk.get("unknown_attrs", {}) if root_unk else {}
    u_children = root_unk.get("unknown_children", []) if root_unk else []
    unknown_attrs_list = [{"attribute": k, "value": str(v.get("value") if isinstance(v, dict) else v)} for k, v in u_attrs.items()]
    unknown_children_list = u_children

    return {
        "name": nav_set_name,
        "items": items,
        "profiles": profiles,
        "unhandled_elements": unknown_children_list,
        "unknowns": {
            "unknown_attrs": unknown_attrs_list,
            "unknown_children": unknown_children_list
        }
    }

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_nav_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python nav_parser.py <path_to_nav_xml>")
