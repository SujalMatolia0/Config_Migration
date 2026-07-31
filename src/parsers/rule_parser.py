import os
from lxml import etree
from src.parsers.utils import capture_unknown
from src.parsers.known_tags_registry import KNOWN_RULE_ATTRS, KNOWN_RULE_CHILDREN

def parse_rule_file(file_path):
    """
    Parses an OSVC Business Rules XML export file and returns structured metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Rules file not found: {file_path}")

    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    rules = []
    unhandled_elements = []

    # Check root for unhandled attributes or tags
    root_unk = capture_unknown(root, KNOWN_RULE_ATTRS, KNOWN_RULE_CHILDREN, "Business Rule Root")
    if root_unk and "unknown_children" in root_unk:
        for child in root_unk["unknown_children"]:
            unhandled_elements.append({
                "tag": child["tag"],
                "raw_xml": child["raw"]
            })

    # If the root element itself is a <Rule>, wrap it, otherwise find all <Rule> descendants
    rule_nodes = [root] if root.tag == "Rule" else root.findall(".//Rule")

    for rule in rule_nodes:
        name_attr = rule.get("Name")
        active_str = rule.get("Active", "True")
        is_active = active_str.lower() == "true"
        rule_notes = rule.get("Notes")
        
        triggers = []
        for trigger in rule.findall(".//Trigger"):
            trig_type = trigger.get("Type")
            if trig_type:
                triggers.append(trig_type)
                
        conditions = []
        for cond in rule.findall(".//Condition"):
            source = cond.find("Source")
            source_val = source.text if source is not None else cond.get("Source")
            op = cond.find("Operator")
            op_val = op.text if op is not None else cond.get("Operator")
            val = cond.find("Value")
            val_val = val.text if val is not None else cond.get("Value")
            prop = cond.find("Property")
            prop_val = prop.text if prop is not None else cond.get("Property")
            
            conditions.append({
                "source": source_val,
                "operator": op_val,
                "value": val_val,
                "property": prop_val
            })
            
        actions = []
        for act in rule.findall(".//Action"):
            act_type = act.get("Type")
            obj = act.find("Object")
            obj_type = obj.get("Type") if obj is not None else None
            oper = act.find("Operation")
            oper_val = oper.text if oper is not None else None
            val = act.find("Value")
            val_val = val.text if val is not None else None
            
            # Extract script path / custom action details if RunScript is the action
            script_path = None
            if act_type == "RunScript" or (oper_val and "script" in oper_val.lower()):
                script_path = act.get("ScriptPath") or act.get("Script") or val_val
            
            actions.append({
                "type": act_type,
                "object": obj_type,
                "operation": oper_val,
                "value": val_val,
                "script_path": script_path
            })
            
        rules.append({
            "name": name_attr,
            "active": is_active,
            "notes": rule_notes,
            "triggers": triggers,
            "conditions": conditions,
            "actions": actions
        })

    u_attrs = root_unk.get("unknown_attrs", {}) if root_unk else {}
    u_children = root_unk.get("unknown_children", []) if root_unk else []
    unknown_attrs_list = [{"attribute": k, "value": str(v.get("value") if isinstance(v, dict) else v)} for k, v in u_attrs.items()]
    unknown_children_list = u_children

    return {
        "file_name": os.path.basename(file_path),
        "format": "business_rule",
        "rules": rules,
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
        data = parse_rule_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python rule_parser.py <path_to_rule_xml>")
