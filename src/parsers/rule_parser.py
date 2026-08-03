import os
from lxml import etree
from src.parsers.utils import capture_unknown
from src.parsers.known_tags_registry import KNOWN_RULE_ATTRS, KNOWN_RULE_CHILDREN

def parse_rule_file(file_path):
    """
    Parses an OSVC Business Rules export file (.xml or .csv) and returns structured metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Rules file not found: {file_path}")

    if file_path.lower().endswith(".csv"):
        return parse_rule_csv_file(file_path)

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

def parse_rule_csv_file(file_path):
    """
    Parses an OSVC Business Rules CSV export file and extracts rules, conditions, actions,
    invoked CPM handlers, state transitions, and custom fields referenced.
    """
    import csv
    import re

    rules = []
    cpm_handlers_set = set()
    process_scripts_set = set()
    custom_fields_set = set()
    states_set = set()
    functions_set = set()

    enabled_count = 0
    disabled_count = 0

    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        
        for row_idx, row in enumerate(reader, start=1):
            if not row or len(row) < 4:
                continue
            
            gtype = row[0].strip() if len(row) > 0 else ""
            gname = row[1].strip() if len(row) > 1 else ""
            is_enabled_str = row[2].strip() if len(row) > 2 else "Yes"
            rname = row[3].strip() if len(row) > 3 else f"Rule {row_idx}"
            desc = row[4].strip() if len(row) > 4 else ""
            vtype = row[5].strip() if len(row) > 5 else ""
            vdef = row[6].strip() if len(row) > 6 else ""
            deployed_str = row[7].strip() if len(row) > 7 else "Yes"
            cond_raw = row[8].strip() if len(row) > 8 else ""
            act_cols = [c.strip() for c in row[9:] if c.strip()]
            act_raw = " ".join(act_cols)

            is_active = is_enabled_str.lower() in ["yes", "true", "1"]
            if is_active:
                enabled_count += 1
            else:
                disabled_count += 1

            if gtype.lower() == "state" and gname:
                states_set.add(gname)
            elif gtype.lower() == "function" and gname:
                functions_set.add(gname)

            # Extract CPM Object Event Handlers: "Execute Object Event Handler (\w+)"
            cpm_handlers = []
            for m in re.finditer(r"Execute Object Event Handler\s+([\w_]+)", act_raw, re.IGNORECASE):
                h_name = m.group(1).strip()
                cpm_handlers.append(h_name)
                cpm_handlers_set.add(h_name)

            # Extract Process Scripts: "Execute Process Script (\w+)"
            process_scripts = []
            for m in re.finditer(r"Execute Process Script\s+([\w_]+)", act_raw, re.IGNORECASE):
                s_name = m.group(1).strip()
                process_scripts.append(s_name)
                process_scripts_set.add(s_name)

            # Extract State Transitions: "Transition State (?:And \w+\s+)?([^\n]+)"
            state_transitions = []
            for m in re.finditer(r"Transition State\s+(?:And\s+\w+\s+)?([^\d\n\.]+[\w\s-]+?)(?:\s+\d+\.|$)", act_raw, re.IGNORECASE):
                st_name = m.group(1).strip()
                state_transitions.append(st_name)

            # Extract Custom Fields: "Custom Field > ([^=><\n]+)"
            custom_fields = []
            for m in re.finditer(r"Custom Field\s*>\s*([^\s=><][^=><\n]+?)(?:\s+equals|\s+contains|\s+assign|\s+AND|\s+OR|\s+not|\s+match|$)", cond_raw + " " + act_raw, re.IGNORECASE):
                cf_name = m.group(1).strip()
                if cf_name and len(cf_name) < 80:
                    custom_fields.append(cf_name)
                    custom_fields_set.add(cf_name)

            # Determine OSVC Target Object (Incident, Contact, Organization, etc.)
            full_rule_text = f"{gname} {cond_raw} {act_raw}".lower()
            if "contacts >" in full_rule_text or "contact >" in full_rule_text or "contact" in gname.lower():
                target_obj = "Contact"
            elif "organizations >" in full_rule_text or "org >" in full_rule_text or "organization" in gname.lower():
                target_obj = "Organization"
            elif "opportunities >" in full_rule_text or "opportunity >" in full_rule_text:
                target_obj = "Opportunity"
            else:
                target_obj = "Incident"

            # Categorize actions by Action Type
            actions_by_type = {}
            primary_action_type = "Other"
            for act in act_cols:
                sub_acts = re.split(r"\s+\d+\.\s+", act)
                for sa in sub_acts:
                    sa_clean = sa.replace("Then >", "").replace("Else >", "").strip()
                    if not sa_clean:
                        continue
                    if sa_clean.startswith("Set Field"):
                        atype = "SetField"
                    elif "Transition State And Stop" in sa_clean:
                        atype = "TransitionState_Stop"
                    elif "Transition State And Continue" in sa_clean:
                        atype = "TransitionState_Continue"
                    elif "Execute Object Event Handler" in sa_clean:
                        atype = "CPMCall"
                    elif "Call Function" in sa_clean:
                        atype = "FunctionCall"
                    elif "Stop Processing" in sa_clean:
                        atype = "StopProcessing"
                    elif "Clear Escalation" in sa_clean:
                        atype = "ClearEscalation"
                    elif "Escalation" in sa_clean or "Revalidate" in sa_clean:
                        atype = "Escalation"
                    elif "Append Response Template" in sa_clean:
                        atype = "AppendTemplate"
                    elif "Send Marketing Email" in sa_clean:
                        atype = "SendMarketingEmail"
                    elif "Send Email" in sa_clean or "Email Incident" in sa_clean:
                        atype = "SendEmail"
                    else:
                        atype = "Other"

                    actions_by_type.setdefault(atype, []).append(sa_clean)
                    if primary_action_type == "Other" and atype != "Other":
                        primary_action_type = atype

            rules.append({
                "id": f"CSV_Rule_{row_idx}",
                "name": rname,
                "object": target_obj,
                "group_type": gtype,
                "group_name": gname,
                "active": is_active,
                "deployed": deployed_str.lower() in ["yes", "true", "1"],
                "description": desc,
                "variable_type": vtype,
                "variable_default": vdef,
                "condition_raw": cond_raw,
                "actions_raw": act_cols,
                "primary_action_type": primary_action_type,
                "actions_by_type": actions_by_type,
                "cpm_handlers_invoked": sorted(list(set(cpm_handlers))),
                "process_scripts_invoked": sorted(list(set(process_scripts))),
                "state_transitions": sorted(list(set(state_transitions))),
                "custom_fields_referenced": sorted(list(set(custom_fields)))
            })

    return {
        "file_name": os.path.basename(file_path),
        "format": "business_rules_csv",
        "name": os.path.basename(file_path).replace(".csv", ""),
        "total_rules": len(rules),
        "enabled_count": enabled_count,
        "disabled_count": disabled_count,
        "states": sorted(list(states_set)),
        "functions": sorted(list(functions_set)),
        "cpm_handlers_invoked": sorted(list(cpm_handlers_set)),
        "process_scripts_invoked": sorted(list(process_scripts_set)),
        "custom_fields_referenced": sorted(list(custom_fields_set)),
        "rules": rules,
        "unhandled_elements": [],
        "unknowns": {
            "unknown_attrs": [],
            "unknown_children": []
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
