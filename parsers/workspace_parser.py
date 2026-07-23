import os
from lxml import etree

def get_closest_tab(element):
    parent = element.getparent()
    while parent is not None:
        if parent.tag == "Tab":
            return parent
        parent = parent.getparent()
    return None

def is_inside_tab(element):
    return get_closest_tab(element) is not None

def parse_workspace_file(file_path):
    """
    Parses an OSVC Workspace XML file and returns structured metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Workspace file not found: {file_path}")

    # Use lxml to parse the XML
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.parse(file_path, parser=parser)
    root = tree.getroot()

    # Extract top-level attributes
    workspace_type = root.get("Type")
    ui_type = root.get("UIType")
    server_version = root.get("ServerVersion", "").strip()
    client_version = root.get("ClientVersion")
    is_multi_edit = root.get("IsMultiEdit", "False").lower() == "true"
    name = os.path.basename(file_path).replace(".xml", "")

    # Extract layout metrics from the main Table tag
    table_elem = None
    for tbl in root.findall(".//Table"):
        if not is_inside_tab(tbl):
            table_elem = tbl
            break
            
    row_count = int(table_elem.get("RowCount", 0)) if table_elem is not None else 0
    column_count = int(table_elem.get("ColumnCount", 0)) if table_elem is not None else 0

    # Check for TabSet coordinates
    tab_set_elem = root.find(".//TabSet")
    tab_set_info = None
    if tab_set_elem is not None:
        tab_set_info = {
            "row": int(tab_set_elem.get("Row")) if tab_set_elem.get("Row") else None,
            "column": int(tab_set_elem.get("Column")) if tab_set_elem.get("Column") else None,
            "row_span": int(tab_set_elem.get("RowSpan")) if tab_set_elem.get("RowSpan") else None,
            "column_span": int(tab_set_elem.get("ColumnSpan")) if tab_set_elem.get("ColumnSpan") else None,
            "summary_panel_height": tab_set_elem.get("SummaryPanelHeight"),
            "summary_panel_alignment": tab_set_elem.get("SummaryPanelAlignment"),
            "can_reorder_tabs": tab_set_elem.get("CanReorderTabs", "False").lower() == "true",
            "wrap_tabs": tab_set_elem.get("WrapTabs", "False").lower() == "true",
            "summary_tab_index": tab_set_elem.get("SummaryTab"),
            "threshold_height": tab_set_elem.get("ThresholdHeight")
        }

    # 1. Record Types
    record_types = []
    for rt in root.findall(".//RecordType"):
        record_types.append({
            "id": rt.get("Id"),
            "name": rt.get("Name")
        })

    # 2. Ribbon Buttons
    ribbon_buttons = []
    for btn in root.findall(".//RibbonButtonItem"):
        item_id = btn.get("ItemId")
        if item_id:
            ribbon_buttons.append(item_id)

    # 3. Info Items
    info_items = []
    for info in root.findall(".//InfoItem"):
        info_items.append({
            "object_id": info.get("ObjectId"),
            "field_id": info.get("FieldId")
        })

    # 4. Rules
    rules = []
    for rule in root.findall(".//Rule"):
        name_attr = rule.get("Name")
        active_str = rule.get("Active", "True")
        is_active = active_str.lower() == "true"
        
        triggers = []
        for trigger in rule.findall(".//Trigger"):
            trig_type = trigger.get("Type")
            if trig_type:
                trig_field = trigger.get("Field")  # e.g. on FieldValueChanged
                if trig_field:
                    triggers.append(f"{trig_type} (Field: {trig_field})")
                else:
                    triggers.append(trig_type)
                
        conditions = []
        for cond_block in rule.findall(".//Conditions"):
            logic_expr = cond_block.get("LogicalExpression")  # e.g. "0 AND 1" or "0 OR 1"
            for cond in cond_block.findall("Condition"):
                source = cond.find("Source")
                source_val = source.text if source is not None else None
                source_type = source.get("Type") if source is not None else None
                op = cond.find("Operator")
                op_val = op.text if op is not None else cond.get("Operator")
                val = cond.find("Value")
                val_val = val.text if val is not None else cond.get("Value")
                conditions.append({
                    "source": source_val,
                    "source_type": source_type,
                    "operator": op_val,
                    "value": val_val,
                    "logic_expr": logic_expr  # shared across all conditions in this block
                })
        # Fallback: bare <Condition> tags not wrapped in <Conditions>
        if not conditions:
            for cond in rule.findall(".//Condition"):
                source = cond.find("Source")
                source_val = source.text if source is not None else None
                source_type = source.get("Type") if source is not None else None
                op = cond.find("Operator")
                op_val = op.text if op is not None else cond.get("Operator")
                val = cond.find("Value")
                val_val = val.text if val is not None else cond.get("Value")
                conditions.append({
                    "source": source_val,
                    "source_type": source_type,
                    "operator": op_val,
                    "value": val_val,
                    "logic_expr": None
                })
            
        def parse_actions(action_elements, branch):
            """Parse a list of <Action> elements and tag with branch (then/else)."""
            result = []
            for act in action_elements:
                act_type = act.get("Type")
                obj = act.find("Object")
                obj_val = None
                obj_type = None
                obj_id = None
                if obj is not None:
                    obj_type = obj.get("Type")
                    obj_id = obj.get("Id") or (obj.text.strip() if obj.text and obj.text.strip().isdigit() else None)
                    obj_val = (obj.text.strip() if obj.text else None) or obj_type
                oper = act.find("Operation")
                oper_val = oper.text if oper is not None else None
                val = act.find("Value")
                val_val = val.text if val is not None else None
                val_op = val.get("Operator") if val is not None else None
                button_id = val.get("ButtonId") if val is not None else None
                result.append({
                    "type": act_type,
                    "object": obj_val,
                    "object_type": obj_type,
                    "object_id": obj_id,
                    "operation": oper_val,
                    "value": val_val,
                    "value_operator": val_op,
                    "button_id": button_id,
                    "branch": branch  # "then" or "else"
                })
            return result

        actions = []
        then_el = rule.find(".//Then")
        else_el = rule.find(".//Else")
        if then_el is not None:
            actions += parse_actions(then_el.findall("Action"), "then")
        if else_el is not None:
            actions += parse_actions(else_el.findall("Action"), "else")
        # Fallback: bare <Action> tags not inside Then/Else
        if not actions:
            actions += parse_actions(rule.findall(".//Action"), "then")

        rules.append({
            "name": name_attr,
            "active": is_active,
            "triggers": triggers,
            "conditions": conditions,
            "actions": actions
        })

    # 5. Tabs (recursive parser for Tab elements)
    def parse_tab_element(tab_elem):
        tab_text = tab_elem.get("Text") or tab_elem.get("TextLabelName") or "Unknown"
        tab_id = tab_elem.get("Id")
        
        relationship_items = []
        for ri in tab_elem.findall(".//RelationshipItem"):
            if get_closest_tab(ri) == tab_elem:
                relationship_items.append({
                    "item_type": ri.get("ItemType"),
                    "ac_id": ri.get("AcId"),
                    "id": ri.get("Id"),
                    "row": int(ri.get("Row", 0)) if ri.get("Row") else 0,
                    "column": int(ri.get("Column", 0)) if ri.get("Column") else 0,
                    "execute_on_new": ri.get("ExecuteOnNew", "True").lower() == "true",
                    "show_read_transactions": ri.get("ShowReadTransactions", "True").lower() == "true",
                    "default_channel": ri.get("DefaultChannelForNote"),
                    "search_report_id": ri.get("SearchReportId"),
                    "can_send_on_save": ri.get("CanSendOnSave"),
                    "can_use_smart_assistant": ri.get("CanUseSmartAssistant"),
                    "default_channel_customer": ri.get("DefaultChannelForCustomerEntry"),
                    "default_thread_on_new": ri.get("DefaultThreadOnNew"),
                    "status_change_on_response": ri.get("StatusChangeOnResponse")
                })
            
        for rep in tab_elem.findall(".//Report"):
            if get_closest_tab(rep) == tab_elem:
                relationship_items.append({
                    "item_type": "Report",
                    "ac_id": rep.get("AcId"),
                    "id": rep.get("Id"),
                    "row": int(rep.get("Row", 0)) if rep.get("Row") else 0,
                    "column": int(rep.get("Column", 0)) if rep.get("Column") else 0,
                    "execute_on_new": rep.get("ExecuteOnNew", "True").lower() == "true",
                    "show_read_transactions": True,
                    "default_channel": None,
                    "search_report_id": rep.get("SearchReportId")
                })
            
        browsers = []
        for br in tab_elem.findall(".//Browser"):
            if get_closest_tab(br) == tab_elem:
                suppress_errors = br.get("SuppressErrors", "False").lower() == "true"
                browsers.append({
                    "url": br.get("Url"),
                    "suppress_errors": suppress_errors,
                    "id": br.get("Id"),
                    "height": br.get("Height"),
                    "row": int(br.get("Row", 0)) if br.get("Row") else 0,
                    "column": int(br.get("Column", 0)) if br.get("Column") else 0
                })
            
        add_in_items = []
        for ai in tab_elem.findall(".//AddinItem"):
            if get_closest_tab(ai) == tab_elem:
                add_in_items.append({
                    "name": ai.get("ItemType") or ai.get("AddInName") or "Unknown",
                    "file_id": ai.get("FileId"),
                    "bui_extension": ai.get("BuiExtension", "False").lower() == "true",
                    "id": ai.get("Id"),
                    "row": int(ai.get("Row", 0)) if ai.get("Row") else 0,
                    "column": int(ai.get("Column", 0)) if ai.get("Column") else 0,
                    "height": ai.get("Height"),
                    "width": ai.get("Width"),
                    "assembly": ai.get("AssemblyName")
                })
            
        tab_fields = []
        for field in tab_elem.findall(".//Field"):
            if get_closest_tab(field) == tab_elem:
                tab_fields.append({
                    "object_id": field.get("ObjectId"),
                    "field_id": field.get("FieldId"),
                    "label": field.get("LabelText"),
                    "id": field.get("Id"),
                    "row": int(field.get("Row")) if field.get("Row") else 0,
                    "column": int(field.get("Column")) if field.get("Column") else 0,
                    "default_phone_type": field.get("DefaultPhoneType"),
                    "report_id": field.get("ReportId"),
                    "readonly_option": field.get("ReadOnlyOption"),
                    "hidden_option": field.get("HiddenOption"),
                    "required_option": field.get("RequiredOption")
                })

        tab_menus = []
        for menu in tab_elem.findall(".//Menu"):
            if get_closest_tab(menu) == tab_elem:
                items_list = [item.get("Value") for item in menu.findall(".//Item")]
                tab_menus.append({
                    "id": menu.get("Id"),
                    "row": int(menu.get("Row")) if menu.get("Row") else 0,
                    "column": int(menu.get("Column")) if menu.get("Column") else 0,
                    "items": items_list
                })

        tab_title_bars = []
        for tb in tab_elem.findall(".//TitleBar"):
            if get_closest_tab(tb) == tab_elem:
                tab_title_bars.append({
                    "text": tb.get("Text"),
                    "row": int(tb.get("Row", 0)) if tb.get("Row") else 0,
                    "column": int(tb.get("Column", 0)) if tb.get("Column") else 0
                })

        tab_spacers = []
        for sp in tab_elem.findall(".//Spacer"):
            if get_closest_tab(sp) == tab_elem:
                tab_spacers.append({
                    "height": sp.get("Height"),
                    "row": int(sp.get("Row", 0)) if sp.get("Row") else 0,
                    "column": int(sp.get("Column", 0)) if sp.get("Column") else 0
                })

        nested_tabsets = []
        for ts in tab_elem.findall(".//TabSet"):
            if get_closest_tab(ts) == tab_elem:
                sub_tabs = []
                for child_tab in ts.findall("./Tab"):
                    sub_tabs.append(parse_tab_element(child_tab))
                nested_tabsets.append({
                    "id": ts.get("Id"),
                    "row": int(ts.get("Row", 0)) if ts.get("Row") else 0,
                    "column": int(ts.get("Column", 0)) if ts.get("Column") else 0,
                    "can_reorder_tabs": ts.get("CanReorderTabs", "False").lower() == "true",
                    "sub_tabs": sub_tabs
                })

        return {
            "text": tab_text,
            "id": tab_id,
            "relationship_items": relationship_items,
            "browsers": browsers,
            "add_in_items": add_in_items,
            "fields": tab_fields,
            "menus": tab_menus,
            "title_bars": tab_title_bars,
            "spacers": tab_spacers,
            "nested_tabsets": nested_tabsets
        }

    tabs = [parse_tab_element(t) for t in root.findall(".//Tab") if get_closest_tab(t) is None]

    # 6. Fields (top-level outside tabs)
    fields = []
    for field in root.findall(".//Field"):
        if not is_inside_tab(field):
            fields.append({
                "object_id": field.get("ObjectId"),
                "field_id": field.get("FieldId"),
                "label": field.get("LabelText"),
                "id": field.get("Id"),
                "row": int(field.get("Row")) if field.get("Row") else 0,
                "column": int(field.get("Column")) if field.get("Column") else 0,
                "default_phone_type": field.get("DefaultPhoneType"),
                "report_id": field.get("ReportId"),
                "readonly_option": field.get("ReadOnlyOption"),
                "hidden_option": field.get("HiddenOption"),
                "required_option": field.get("RequiredOption")
            })

    # 7. Menus (top-level outside tabs)
    menus = []
    for menu in root.findall(".//Menu"):
        if not is_inside_tab(menu):
            items_list = [item.get("Value") for item in menu.findall(".//Item")]
            menus.append({
                "id": menu.get("Id"),
                "row": int(menu.get("Row")) if menu.get("Row") else 0,
                "column": int(menu.get("Column")) if menu.get("Column") else 0,
                "items": items_list
            })

    title_bars = []
    for tb in root.findall(".//TitleBar"):
        if not is_inside_tab(tb):
            title_bars.append({
                "text": tb.get("Text"),
                "row": int(tb.get("Row", 0)) if tb.get("Row") else 0,
                "column": int(tb.get("Column", 0)) if tb.get("Column") else 0
            })

    spacers = []
    for sp in root.findall(".//Spacer"):
        if not is_inside_tab(sp):
            spacers.append({
                "height": sp.get("Height"),
                "row": int(sp.get("Row", 0)) if sp.get("Row") else 0,
                "column": int(sp.get("Column", 0)) if sp.get("Column") else 0
            })

    # 8. Ribbon Links
    ribbon_links = []
    for link in root.findall(".//LinkItem"):
        ribbon_links.append({
            "title": link.get("Title"),
            "url": link.get("Url")
        })

    # 9. Flag element
    flag_elem = root.find(".//Flag")
    flag_visible = True
    if flag_elem is not None:
        flag_visible = flag_elem.get("Visible", "True").lower() == "true"

    return {
        "name": name,
        "type": workspace_type,
        "ui_type": ui_type,
        "server_version": server_version,
        "client_version": client_version,
        "is_multi_edit": is_multi_edit,
        "row_count": row_count,
        "column_count": column_count,
        "tab_set_info": tab_set_info,
        "record_types": record_types,
        "ribbon_buttons": ribbon_buttons,
        "info_items": info_items,
        "rules": rules,
        "tabs": tabs,
        "fields": fields,
        "menus": menus,
        "title_bars": title_bars,
        "spacers": spacers,
        "ribbon_links": ribbon_links,
        "flag_visible": flag_visible
    }


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_workspace_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python workspace_parser.py <path_to_workspace_xml>")
