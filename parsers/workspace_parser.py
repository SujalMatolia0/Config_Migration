import os
from lxml import etree
from parsers.utils import capture_unknown

KNOWN_WORKSPACE_ATTRS = {
    "Type", "UIType", "ServerVersion", "ClientVersion", "IsMultiEdit", "Id", "Name",
    "BrowserCompatibilityMode", "SpellCheckAllowCancel", "SpellCheckOnSave"
}

KNOWN_WORKSPACE_CHILDREN = {
    "Table", "TabSet", "RecordTypes", "RecordType", "Info", "InfoItem", "Rules", "Rule",
    "Triggers", "Trigger", "Conditions", "Condition", "Then", "Else", "Action", "Field",
    "Menu", "Browser", "RelationshipItem", "Report", "AddinItem", "AddInItem", "TitleBar",
    "Spacer", "Links", "LinkItem", "Flag", "QuickAccessToolbar", "Ribbon", "Tab"
}

KNOWN_TABSET_ATTRS = {
    "Id", "Row", "Column", "RowSpan", "ColumnSpan", "SummaryPanelHeight", "SummaryPanelAlignment",
    "CanReorderTabs", "WrapTabs", "SummaryTab", "ThresholdHeight", "TabDisplayStyle", "Margin", "TabIndex"
}
KNOWN_TABSET_CHILDREN = {"Tab"}

KNOWN_TAB_ATTRS = {"Text", "TextLabelName", "Id", "Row", "Column", "TextColor"}
KNOWN_TAB_CHILDREN = {
    "Table", "Field", "RelationshipItem", "Report", "Browser", "AddinItem", "AddInItem",
    "Menu", "TitleBar", "Spacer", "TabSet"
}

KNOWN_FIELD_ATTRS = {
    "ObjectId", "FieldId", "LabelText", "Id", "Row", "Column", "DefaultPhoneType", "DefaultValue",
    "InitialValue", "Value", "ReportId", "ReadOnlyOption", "HiddenOption", "RequiredOption",
    "AcceptsReturn", "BooleanRenderView", "Height", "LayoutLabelAlignment", "Multiline",
    "RequiredForSolved", "RowSpan", "ColumnSpan", "ShowParent", "SpellCheck", "TabIndex", "TrimTextWhitespace"
}
KNOWN_FIELD_CHILDREN = set()

KNOWN_RELATIONSHIP_ATTRS = {
    "ItemType", "AcId", "Id", "Row", "Column", "ExecuteOnNew", "ShowReadTransactions",
    "DefaultChannelForNote", "SearchReportId", "CanSendOnSave", "CanUseSmartAssistant",
    "DefaultChannelForCustomerEntry", "DefaultThreadOnNew", "StatusChangeOnResponse",
    "AlwaysShowEmailHeader", "AlwaysUsePlainText", "CanAddBCC", "CanAddCC", "CanAddCustomerEntry",
    "CanAddNote", "CanAddResponse", "CanFollowIncidentLinks", "CanFollowLinks", "CanSearchKb",
    "CanToggleToPlainText", "CommitResponseOnSave", "ConfirmResponse", "DefaultThreadOnEdit",
    "DefaultToPlainText", "DelayReportExecution", "Font", "IsUsingDefaultEmailFont", "Margin",
    "Padding", "ReassignOnResponse", "ResponsePanelCoupled", "SendResponseDefault", "ShowRowCount",
    "ThreadOrientation", "ThumbnailsEnabled", "ThumbnailsThreshold", "FilterOnPrimaryKeyOnly",
    "RefreshReportOnDataChange", "TabIndex"
}
KNOWN_RELATIONSHIP_CHILDREN = set()

KNOWN_BROWSER_ATTRS = {
    "Url", "SuppressErrors", "Id", "Height", "Width", "Row", "Column", "DelayPageLoad",
    "SendUrlAsPostData", "SetFixedHeight", "ChildBrowsers", "TabIndex", "HttpMethod", "PostData"
}
KNOWN_BROWSER_CHILDREN = set()

KNOWN_ADDIN_ATTRS = {
    "ItemType", "AddInName", "FileId", "BuiExtension", "Id", "Row", "Column", "Height",
    "Width", "AssemblyName", "Assembly"
}
KNOWN_ADDIN_CHILDREN = set()

KNOWN_RULE_ATTRS = {"Name", "Active", "Id"}
KNOWN_RULE_CHILDREN = {"Trigger", "Conditions", "Condition", "Then", "Else", "Action"}

KNOWN_CONDITION_ATTRS = {"LogicalExpression", "Operator", "Value", "Type"}
KNOWN_CONDITION_CHILDREN = {"Source", "Operator", "Value"}

KNOWN_ACTION_ATTRS = {"Type"}
KNOWN_ACTION_CHILDREN = {"Object", "Operation", "Value"}

def get_closest_tab(element):
    parent = element.getparent()
    while parent is not None:
        if parent.tag == "Tab":
            return parent
        parent = parent.getparent()
    return None

def is_inside_tab(element):
    return get_closest_tab(element) is not None

def parse_workspace_file(file_path, strict=False):
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

    ws_unknown_attrs = []
    ws_unknown_children = []

    def record_unknown(ctx, unk):
        if not unk:
            return
        if "unknown_attrs" in unk:
            for k, v in unk["unknown_attrs"].items():
                entry = {"location": ctx, "attribute": k, "value": str(v)}
                ws_unknown_attrs.append(entry)
                if strict:
                    print(f"[WARNING] Strict Mode: Unknown attribute on {ctx} -> {k}=\"{v}\"")
        if "unknown_children" in unk:
            for child in unk["unknown_children"]:
                entry = {"location": ctx, "tag": child["tag"], "attrs": child["attrs"], "raw": child["raw"]}
                ws_unknown_children.append(entry)
                if strict:
                    print(f"[WARNING] Strict Mode: Unknown element on {ctx} -> <{child['tag']} />")

    # Root unknown check
    root_unk = capture_unknown(root, KNOWN_WORKSPACE_ATTRS, KNOWN_WORKSPACE_CHILDREN, "Workspace Root")
    record_unknown("Workspace Root", root_unk)

    # Extract layout metrics from the main Table tag
    table_elem = None
    for tbl in root.findall(".//Table"):
        if not is_inside_tab(tbl):
            table_elem = tbl
            break
            
    row_count = int(table_elem.get("RowCount", 0)) if table_elem is not None else 0
    column_count = int(table_elem.get("ColumnCount", 0)) if table_elem is not None else 0
    is_tab_only_root = (table_elem is None) or (row_count == 0 and column_count == 0)

    # Check for TabSet coordinates
    tab_set_elem = root.find(".//TabSet")
    tab_set_info = None
    if tab_set_elem is not None:
        ts_unk = capture_unknown(tab_set_elem, KNOWN_TABSET_ATTRS, KNOWN_TABSET_CHILDREN, "TabSet")
        record_unknown("TabSet", ts_unk)
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
        if item_id and item_id not in ["Separator", "EditorLinks"]:
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
        name_attr = rule.get("Name") or "Rule"
        active_str = rule.get("Active", "True")
        is_active = active_str.lower() == "true"
        rule_notes = rule.get("Notes")
        
        rule_unk = capture_unknown(rule, KNOWN_RULE_ATTRS, KNOWN_RULE_CHILDREN, f"Rule: {name_attr}")
        record_unknown(f"Rule: {name_attr}", rule_unk)
        
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
                cond_unk = capture_unknown(cond, KNOWN_CONDITION_ATTRS, KNOWN_CONDITION_CHILDREN, f"Condition in Rule: {name_attr}")
                record_unknown(f"Condition in Rule: {name_attr}", cond_unk)

                source = cond.find("Source")
                source_val = source.text if source is not None else None
                source_type = source.get("Type") if source is not None else None
                op = cond.find("Operator")
                op_val = op.text if op is not None else cond.get("Operator")
                val = cond.find("Value")
                val_val = val.text if val is not None else cond.get("Value")
                prop = cond.find("Property")
                prop_val = prop.text if prop is not None else cond.get("Property")
                conditions.append({
                    "source": source_val,
                    "source_type": source_type,
                    "operator": op_val,
                    "value": val_val,
                    "property": prop_val,
                    "logic_expr": logic_expr  # shared across all conditions in this block
                })
        # Fallback: bare <Condition> tags not wrapped in <Conditions>
        if not conditions:
            for cond in rule.findall(".//Condition"):
                cond_unk = capture_unknown(cond, KNOWN_CONDITION_ATTRS, KNOWN_CONDITION_CHILDREN, f"Condition in Rule: {name_attr}")
                record_unknown(f"Condition in Rule: {name_attr}", cond_unk)

                source = cond.find("Source")
                source_val = source.text if source is not None else None
                source_type = source.get("Type") if source is not None else None
                op = cond.find("Operator")
                op_val = op.text if op is not None else cond.get("Operator")
                val = cond.find("Value")
                val_val = val.text if val is not None else cond.get("Value")
                prop = cond.find("Property")
                prop_val = prop.text if prop is not None else cond.get("Property")
                conditions.append({
                    "source": source_val,
                    "source_type": source_type,
                    "operator": op_val,
                    "value": val_val,
                    "property": prop_val,
                    "logic_expr": None
                })
            
        def parse_actions(action_elements, branch):
            """Parse a list of <Action> elements and tag with branch (then/else)."""
            result = []
            for act in action_elements:
                act_unk = capture_unknown(act, KNOWN_ACTION_ATTRS, KNOWN_ACTION_CHILDREN, f"Action in Rule: {name_attr}")
                record_unknown(f"Action in Rule: {name_attr}", act_unk)

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
            "notes": rule_notes,
            "triggers": triggers,
            "conditions": conditions,
            "actions": actions
        })

    # 5. Tabs (recursive parser for Tab elements)
    def parse_tab_element(tab_elem):
        tab_text = tab_elem.get("Text") or tab_elem.get("TextLabelName") or "Unknown"
        tab_id = tab_elem.get("Id")

        tab_unk = capture_unknown(tab_elem, KNOWN_TAB_ATTRS, KNOWN_TAB_CHILDREN, f"Tab: {tab_text}")
        record_unknown(f"Tab: {tab_text}", tab_unk)
        
        relationship_items = []
        for ri in tab_elem.findall(".//RelationshipItem"):
            if get_closest_tab(ri) == tab_elem:
                ri_unk = capture_unknown(ri, KNOWN_RELATIONSHIP_ATTRS, KNOWN_RELATIONSHIP_CHILDREN, f"Tab: {tab_text} RelationshipItem: {ri.get('ItemType')}")
                record_unknown(f"Tab: {tab_text} RelationshipItem: {ri.get('ItemType')}", ri_unk)
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
                    "status_change_on_response": ri.get("StatusChangeOnResponse"),
                    "can_use_standard_text": ri.get("CanUseStandardText"),
                    "thread_orientation": ri.get("ThreadOrientation"),
                    "commit_response_on_save": ri.get("CommitResponseOnSave"),
                    "always_show_email_header": ri.get("AlwaysShowEmailHeader"),
                    "always_use_plain_text": ri.get("AlwaysUsePlainText"),
                    "can_add_bcc": ri.get("CanAddBCC"),
                    "can_add_cc": ri.get("CanAddCC"),
                    "can_add_customer_entry": ri.get("CanAddCustomerEntry"),
                    "can_add_note": ri.get("CanAddNote"),
                    "can_add_response": ri.get("CanAddResponse"),
                    "can_follow_incident_links": ri.get("CanFollowIncidentLinks"),
                    "can_follow_links": ri.get("CanFollowLinks"),
                    "can_search_kb": ri.get("CanSearchKb"),
                    "can_toggle_to_plain_text": ri.get("CanToggleToPlainText"),
                    "default_thread_on_edit": ri.get("DefaultThreadOnEdit"),
                    "default_to_plain_text": ri.get("DefaultToPlainText"),
                    "delay_report_execution": ri.get("DelayReportExecution"),
                    "font": ri.get("Font"),
                    "is_using_default_email_font": ri.get("IsUsingDefaultEmailFont"),
                    "margin": ri.get("Margin"),
                    "padding": ri.get("Padding"),
                    "reassign_on_response": ri.get("ReassignOnResponse"),
                    "response_panel_coupled": ri.get("ResponsePanelCoupled"),
                    "send_response_default": ri.get("SendResponseDefault"),
                    "show_row_count": ri.get("ShowRowCount"),
                    "thumbnails_enabled": ri.get("ThumbnailsEnabled"),
                    "thumbnails_threshold": ri.get("ThumbnailsThreshold")
                })
            
        for rep in tab_elem.findall(".//Report"):
            if get_closest_tab(rep) == tab_elem:
                rep_unk = capture_unknown(rep, KNOWN_RELATIONSHIP_ATTRS, KNOWN_RELATIONSHIP_CHILDREN, f"Tab: {tab_text} Report: {rep.get('AcId')}")
                record_unknown(f"Tab: {tab_text} Report: {rep.get('AcId')}", rep_unk)
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
                br_unk = capture_unknown(br, KNOWN_BROWSER_ATTRS, KNOWN_BROWSER_CHILDREN, f"Tab: {tab_text} Browser: {br.get('Id')}")
                record_unknown(f"Tab: {tab_text} Browser: {br.get('Id')}", br_unk)
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
        for ai in tab_elem.findall(".//AddinItem") + tab_elem.findall(".//AddInItem"):
            if get_closest_tab(ai) == tab_elem:
                ai_unk = capture_unknown(ai, KNOWN_ADDIN_ATTRS, KNOWN_ADDIN_CHILDREN, f"Tab: {tab_text} AddIn: {ai.get('ItemType') or ai.get('AddInName')}")
                record_unknown(f"Tab: {tab_text} AddIn: {ai.get('ItemType') or ai.get('AddInName')}", ai_unk)
                add_in_items.append({
                    "name": ai.get("ItemType") or ai.get("AddInName") or "Unknown",
                    "file_id": ai.get("FileId"),
                    "bui_extension": ai.get("BuiExtension", "False").lower() == "true",
                    "id": ai.get("Id"),
                    "row": int(ai.get("Row", 0)) if ai.get("Row") else 0,
                    "column": int(ai.get("Column", 0)) if ai.get("Column") else 0,
                    "height": ai.get("Height"),
                    "width": ai.get("Width"),
                    "assembly": ai.get("AssemblyName") or ai.get("Assembly")
                })
            
        tab_fields = []
        for field in tab_elem.findall(".//Field"):
            if get_closest_tab(field) == tab_elem:
                f_unk = capture_unknown(field, KNOWN_FIELD_ATTRS, KNOWN_FIELD_CHILDREN, f"Tab: {tab_text} Field: {field.get('FieldId') or field.get('LabelText')}")
                record_unknown(f"Tab: {tab_text} Field: {field.get('FieldId') or field.get('LabelText')}", f_unk)
                tab_fields.append({
                    "object_id": field.get("ObjectId"),
                    "field_id": field.get("FieldId"),
                    "label": field.get("LabelText"),
                    "id": field.get("Id"),
                    "row": int(field.get("Row")) if field.get("Row") else 0,
                    "column": int(field.get("Column")) if field.get("Column") else 0,
                    "default_phone_type": field.get("DefaultPhoneType"),
                    "default_value": field.get("DefaultValue") or field.get("InitialValue") or field.get("Value"),
                    "report_id": field.get("ReportId"),
                    "readonly_option": field.get("ReadOnlyOption"),
                    "hidden_option": field.get("HiddenOption"),
                    "required_option": field.get("RequiredOption"),
                    "row_span": int(field.get("RowSpan")) if field.get("RowSpan") else None,
                    "layout_label_alignment": field.get("LayoutLabelAlignment"),
                    "required_for_solved": field.get("RequiredForSolved"),
                    "show_parent": field.get("ShowParent")
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
                ts_unk = capture_unknown(ts, KNOWN_TABSET_ATTRS, KNOWN_TABSET_CHILDREN, f"Tab: {tab_text} Nested TabSet")
                record_unknown(f"Tab: {tab_text} Nested TabSet", ts_unk)
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
            f_unk = capture_unknown(field, KNOWN_FIELD_ATTRS, KNOWN_FIELD_CHILDREN, f"Top-level Field: {field.get('FieldId') or field.get('LabelText')}")
            record_unknown(f"Top-level Field: {field.get('FieldId') or field.get('LabelText')}", f_unk)
            fields.append({
                "object_id": field.get("ObjectId"),
                "field_id": field.get("FieldId"),
                "label": field.get("LabelText"),
                "id": field.get("Id"),
                "row": int(field.get("Row")) if field.get("Row") else 0,
                "column": int(field.get("Column")) if field.get("Column") else 0,
                "default_phone_type": field.get("DefaultPhoneType"),
                "default_value": field.get("DefaultValue") or field.get("InitialValue") or field.get("Value"),
                "report_id": field.get("ReportId"),
                "readonly_option": field.get("ReadOnlyOption"),
                "hidden_option": field.get("HiddenOption"),
                "required_option": field.get("RequiredOption"),
                "row_span": int(field.get("RowSpan")) if field.get("RowSpan") else None,
                "layout_label_alignment": field.get("LayoutLabelAlignment"),
                "required_for_solved": field.get("RequiredForSolved"),
                "show_parent": field.get("ShowParent")
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

    # 8. QuickAccessToolbar Items
    quick_access_items = []
    for q_item in root.findall(".//QuickAccessToolbarItem"):
        item_id = q_item.get("ItemId")
        if item_id:
            quick_access_items.append(item_id)

    # 9. Ribbon Structure
    ribbon_structure = []
    for r_tab in root.findall(".//RibbonTab"):
        tab_name = r_tab.get("TextLabelName", "Tab")
        groups = []
        for r_grp in r_tab.findall("./RibbonGroup"):
            grp_name = r_grp.get("TextLabelName", "Group")
            btn_items = [btn.get("ItemId") for btn in r_grp.findall("./RibbonButtonItem") if btn.get("ItemId")]
            groups.append({
                "group_name": grp_name,
                "buttons": btn_items
            })
        ribbon_structure.append({
            "tab_name": tab_name,
            "groups": groups
        })

    # 10. Ribbon Links
    ribbon_links = []
    for link in root.findall(".//LinkItem"):
        ribbon_links.append({
            "title": link.get("Title"),
            "url": link.get("Url")
        })

    # 11. Flag element
    flag_elem = root.find(".//Flag")
    flag_visible = True
    if flag_elem is not None:
        flag_visible = flag_elem.get("Visible", "True").lower() == "true"

    # 12. Fallback: Catch-All for Raw Unhandled Tags
    RERECOGNIZED_TAGS = {
        "Workspace", "Table", "TabSet", "Tab", "RecordTypes", "RecordType",
        "Info", "InfoItem", "Rules", "Rule", "Triggers", "Trigger",
        "Conditions", "Condition", "Source", "Operator", "Value",
        "Then", "Else", "Action", "Object", "Operation", "Field",
        "Menu", "Items", "Item", "Browser", "RelationshipItem", "Report",
        "AddinItem", "AddInItem", "TitleBar", "Spacer", "Links", "LinkItem", "Flag",
        "QuickAccessToolbar", "QuickAccessToolbarItem", "Ribbon",
        "RibbonTab", "RibbonGroup", "RibbonButtonItem"
    }

    raw_unhandled_tags = []
    for elem in root.iter():
        if isinstance(elem.tag, str):
            tag_name = elem.tag.split("}")[-1]
            if tag_name not in RERECOGNIZED_TAGS:
                raw_xml = etree.tostring(elem, encoding="unicode").strip()
                if len(raw_xml) > 300:
                    raw_xml = raw_xml[:300] + "... [truncated]"
                raw_unhandled_tags.append({
                    "tag": tag_name,
                    "raw_xml": raw_xml
                })

    # 13. Audit Traceability: Document Known Ignored UI Attributes
    known_ignored_attributes = {
        "Workspace": ["BrowserCompatibilityMode", "SpellCheckAllowCancel", "SpellCheckOnSave"],
        "Table": ["BackColor", "ForeColor", "Padding", "AutoScroll"],
        "TabSet": ["Margin", "TabDisplayStyle", "TabIndex", "ColumnSpan", "RowSpan", "SummaryPanelAlignment", "SummaryPanelHeight", "SummaryTab", "ThresholdHeight", "WrapTabs"],
        "Tab": ["TextColor"],
        "TitleBar": ["BackColor", "Font", "ForeColor", "Margin", "TextAlign", "ColumnSpan", "Height"],
        "Spacer": ["ColumnSpan", "Id"],
        "Field": ["AcceptsReturn", "BooleanRenderView", "Height", "LayoutLabelAlignment", "Multiline", "RequiredForSolved", "RowSpan", "ShowParent", "SpellCheck", "TabIndex", "TrimTextWhitespace"],
        "Browser": ["ChildBrowsers", "DelayPageLoad", "SendUrlAsPostData", "SetFixedHeight", "TabIndex"],
        "RelationshipItem": ["AlwaysShowEmailHeader", "AlwaysUsePlainText", "CanAddBCC", "CanAddCC", "CanAddCustomerEntry", "CanAddNote", "CanAddResponse", "CanFollowIncidentLinks", "CanFollowLinks", "CanSearchKb", "CanToggleToPlainText", "CommitResponseOnSave", "ConfirmResponse", "DefaultThreadOnEdit", "DefaultToPlainText", "DelayReportExecution", "Font", "IsUsingDefaultEmailFont", "Margin", "Padding", "ReassignOnResponse", "ResponsePanelCoupled", "SendResponseDefault", "ShowRowCount", "ThreadOrientation", "ThumbnailsEnabled", "ThumbnailsThreshold"],
        "Report": ["FilterOnPrimaryKeyOnly", "RefreshReportOnDataChange", "ShowRowCount", "TabIndex"]
    }

    return {
        "name": name,
        "format": "workspace",
        "type": workspace_type,
        "ui_type": ui_type,
        "server_version": server_version,
        "client_version": client_version,
        "is_multi_edit": is_multi_edit,
        "row_count": row_count,
        "column_count": column_count,
        "is_tab_only_root": is_tab_only_root,
        "tab_set_info": tab_set_info,
        "record_types": record_types,
        "quick_access_toolbar": quick_access_items,
        "ribbon_buttons": sorted(list(set(ribbon_buttons))),
        "ribbon_structure": ribbon_structure,
        "info_items": info_items,
        "rules": rules,
        "tabs": tabs,
        "fields": fields,
        "menus": menus,
        "title_bars": title_bars,
        "spacers": spacers,
        "ribbon_links": ribbon_links,
        "flag_visible": flag_visible,
        "raw_unhandled_tags": raw_unhandled_tags,
        "known_ignored_attributes": known_ignored_attributes,
        "unknowns": {
            "unknown_attrs": ws_unknown_attrs,
            "unknown_children": ws_unknown_children
        }
    }


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_workspace_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python workspace_parser.py <path_to_workspace_xml>")
