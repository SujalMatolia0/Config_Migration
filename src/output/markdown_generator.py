import os
import re
import urllib.parse
import base64 as _b64

def get_all_tabs_flat(tabs_list):
    flat = []
    for t in tabs_list:
        flat.append(t)
        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                flat.extend(get_all_tabs_flat([sub_t]))
    return flat

def clean_tab_label(text):
    if not text:
        return "Unknown"
    mapping = {
        "SUMMARY_LBL": "Summary",
        "CONTACTS_LBL": "Contacts",
        "AUDIT_LOG_LBL": "Audit Log",
        "TASKS_LBL": "Tasks",
        "ATTACHMENTS_LBL": "Attachments",
        "CONTACT_FIELDS_LBL": "Contact Fields",
        "INCIDENT_HISTORY_LBL": "Incident History",
        "INCIDENTS_LBL": "Incidents",
        "OPPORTUNITIES_LBL": "Opportunities",
        "CHAT_LBL": "Chat",
        "NOTES_LBL": "Notes",
        "QUOTES_LBL": "Quotes"
    }
    return mapping.get(text, text.replace("_LBL", "").title().replace("_", " "))

def get_related_object_name(item_type):
    if not item_type or item_type == "Report":
        return "—"
    mapping = {
        "IncidentView": "Incident",
        "Tasks": "Task",
        "FileAttachments": "File Attachment",
        "Contacts": "Contact",
        "ContactNotes": "Note",
        "ContactAuditLog": "Audit Log",
        "IncidentAuditLog": "Audit Log",
        "RichIncidentThread": "Incident Thread",
        "SlaContainer": "SLA Container",
        "SurveyHistoryView": "Survey History"
    }
    return mapping.get(item_type, item_type)

def format_profile_constraint(opt):
    if not opt:
        return None
    parts = opt.split(';')
    formatted = []
    for part in parts:
        if not part:
            continue
        if ':' in part:
            event, pr_list = part.split(':', 1)
            if pr_list == "~any~":
                formatted.append(f"{event} (All Profiles)")
            else:
                ids = set(p.strip() for p in pr_list.split(',') if p.strip())
                formatted.append(f"{event} ({len(ids)} profiles)")
        else:
            formatted.append(part)
    return ", ".join(formatted)

def format_server_version(server_version):
    if not server_version:
        return "Unknown OSVC Server"
    months = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    pattern = r'^(Oracle Service Cloud [^\(]+)\s*\(Build (\d+)\s*-\s*(\d{2})/(\d{2})/(\d{4})'
    match = re.search(pattern, server_version, re.IGNORECASE)
    if match:
        platform = match.group(1).strip()
        build = match.group(2)
        month_num = match.group(3)
        year = match.group(5)
        month_name = months.get(month_num, "Unknown")
        return f"**{platform}** (Build {build}, {month_name} {year})"
    return f"**{server_version}**"

def get_field_notes(field_id, label, default_phone_type, default_value=None):
    clean_label = label.replace('&', '').strip() if label else ""
    standards = {
        "Title": "Salutation/title",
        "Name.First": "First name",
        "Name.Last": "Last name",
        "Addr": "Address",
        "Email": "Email address",
        "PhOffice": "Office phone",
        "CtypeId": "Contact type",
        "OrgId": "Account",
        "ProdId": "Product",
        "CatId": "Category",
        "Status.Id": "Status",
        "ChanId": "Channel",
        "Assigned": "Assigned Agent/Group",
        "QueueId": "Queue",
        "Subject": "Incident Subject"
    }

    if not field_id:
        notes = clean_label or "Form field"
        if default_value is not None and str(default_value).strip():
            notes += f" — *Default Value: `{default_value}`*"
        return notes

    base_notes = ""
    if clean_label:
        std_name = standards.get(field_id)
        if std_name and clean_label.lower() != std_name.lower():
            base_notes = f'Relabeled as **"{clean_label}"**'
            if default_phone_type == "1":
                base_notes += ", default type 1"
    
    if not base_notes:
        if field_id.startswith("C$"):
            field_name = field_id[2:]
            words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', field_name)
            desc = " ".join(words).lower()
            base_notes = f"Custom field — {desc}"
        else:
            base_notes = standards.get(field_id, clean_label or "Form field")

    if default_value is not None and str(default_value).strip():
        base_notes += f" — *Default Value: `{default_value}`*"

    return base_notes

def format_condition(cond):
    source = cond.get("source") or ""
    source_type = cond.get("source_type") or ""
    op = cond.get("operator") or ""
    val = cond.get("value") or ""
    op_map = {
        "EQ": "==", "NE": "!=",
        "GT": ">", "LT": "<",
        "GE": ">=", "LE": "<="
    }
    op_str = op_map.get(op, op)
    prefix = f"{source_type}: " if source_type else ""
    cond_str = f"`{prefix}{source} {op_str} {val}`"
    if "CtypeId" in source and val == "3" and op == "EQ":
        cond_str += ' (a specific contact type, likely "Email" or similar)'
    return cond_str

def format_action(act, tab_id_to_name=None):
    act_type = act.get("type")
    obj = act.get("object")
    obj_type = act.get("object_type")
    obj_id = act.get("object_id")
    oper = act.get("operation")
    val = act.get("value") or ""
    val_op = act.get("value_operator")
    button_id = act.get("button_id")

    if obj == "MessageBox" and oper == "Show":
        return f'Show a message box — *"{val}"*'

    if obj == "RibbonButton" and button_id:
        return f"{act_type or 'Standard'}: {oper or 'Hidden'} RibbonButton[{button_id}] → {val}"

    if oper == "ConfigureMenuItems":
        op_prefix = f"{val_op} " if val_op else ""
        return f"{act_type or 'Standard'}: ConfigureMenuItems {obj or ''} ({op_prefix}{val})"

    target_id = obj_id or (obj if str(obj).isdigit() else None)
    if tab_id_to_name and target_id and target_id in tab_id_to_name:
        return f"{act_type or 'Standard'}: {oper or ''} Tab: **{tab_id_to_name[target_id]}** → {val}"
    elif target_id:
        return f"{act_type or 'Standard'}: {oper or ''} [Element ID: {target_id}] → {val}"

    if obj_type == "Tab":
        tab_ref = f"Tab (Id: `{obj_id}`)" if obj_id else "Tab"
        return f"{act_type or 'Standard'}: {oper or ''} {tab_ref} → {val}"

    return f"{act_type or 'Action'}: {oper or ''} {obj or ''} ({val})"

def format_ribbon_button(btn):
    mapping = {
        "Save": "Save",
        "SaveAndClose": "Save & Close",
        "New": "New",
        "Refresh": "Refresh",
        "Appointment": "Appointment",
        "Print": "Print",
        "Copy": "Copy",
        "Delete": "Delete",
        "SpellCheck": "Spell Check",
        "ResetPassword": "Reset Password",
        "Info": "Info"
    }
    return mapping.get(btn, btn)

def generate_report_markdown(ws):
    lines = []
    
    # Header & System Info
    lines.append("## System Info")
    lines.append("")
    lines.append(f"- Platform: {format_server_version(ws.get('server_version'))}")
    lines.append(f"- Client Version: `{ws.get('client_version')}`")
    
    record_type_label = ws.get("type", "Record")
    multi_edit_str = "multi-edit" if ws.get("is_multi_edit") else "single record, not multi-edit"
    lines.append(f"- Workspace Type: **{record_type_label}** ({multi_edit_str})")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Layout Structure
    lines.append("## Layout Structure")
    lines.append("")
    col_count = ws.get('column_count', 0)
    row_count = ws.get('row_count', 0)
    is_tab_only = ws.get("is_tab_only_root", False) or (col_count == 0 and row_count == 0)
    if is_tab_only:
        col_str = "**TabSet container layout** (tab-oriented workspace layout)"
    else:
        col_str = f"**{col_count}-column table layout** ({row_count} rows × {col_count} columns)" if col_count else "**table layout**"
    
    top_fields = ws.get("fields", [])
    top_menus = ws.get("menus", [])
    all_tabs_flat = get_all_tabs_flat(ws.get("tabs", []))
    
    if top_fields or top_menus:
        lines.append(f"The workspace has a {col_str}:")
        lines.append("")
        lines.append("**Left column** — Form fields:")
        lines.append("")
        lines.append("| Field | Notes |")
        lines.append("|---|---|")
        
        layout_elements = []
        for f in top_fields:
            field_id = f.get("field_id")
            notes = get_field_notes(field_id, f.get("label"), f.get("default_phone_type"))
            readonly_opt = f.get("readonly_option")
            hidden_opt = f.get("hidden_option")
            required_opt = f.get("required_option")
            constraints = []
            if readonly_opt:
                c_str = format_profile_constraint(readonly_opt)
                if c_str: constraints.append(f"ReadOnly: {c_str}")
            if hidden_opt:
                c_str = format_profile_constraint(hidden_opt)
                if c_str: constraints.append(f"Hidden: {c_str}")
            if required_opt:
                c_str = format_profile_constraint(required_opt)
                if c_str: constraints.append(f"Required: {c_str}")
            if constraints: notes += f" — *Constraints: {'; '.join(constraints)}*"
            layout_elements.append({
                "name": f"`{field_id}`",
                "row": f.get("row", 0),
                "column": f.get("column", 0),
                "notes": notes
            })
            
        for m in top_menus:
            items_str = ", ".join(f"**{val}**" for val in m.get("items", []))
            layout_elements.append({
                "name": f"`Menu ({m.get('id')})`",
                "row": m.get("row", 0),
                "column": m.get("column", 0),
                "notes": f"Custom dropdown menu with items: {items_str}"
            })
            
        layout_elements.sort(key=lambda x: (x["column"], x["row"]))
        for el in layout_elements:
            lines.append(f"| {el['name']} | {el['notes']} |")
        lines.append("")
    else:
        lines.append(f"The workspace layout is structured as a root **TabSet** containing {len(ws.get('tabs', []))} tabs.")
        lines.append("")
        
    lines.append("---")
    lines.append("")
    lines.append("## Layout & Tab Details")
    lines.append("")
    lines.append("Below is the detailed content breakdown of each tab:")

    def render_single_tab(t, is_subtab=False):
        tab_name = clean_tab_label(t.get("text"))
        lines.append("")
        
        tab_fields = t.get("fields", [])
        tab_menus = t.get("menus", [])
        tab_relationship_items = t.get("relationship_items", [])
        tab_browsers = t.get("browsers", [])
        tab_addins = t.get("add_in_items", [])
        tab_title_bars = t.get("title_bars", [])
        tab_spacers = t.get("spacers", [])
        
        total_controls = (len(tab_fields) + len(tab_menus) + 
                          len(tab_relationship_items) + len(tab_browsers) + 
                          len(tab_addins))

        if not is_subtab:
            lines.append('<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">')
            lines.append(f'  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>{tab_name}</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">({total_controls} Controls)</span></summary>')
            lines.append('  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">')
            lines.append("")
            lines.append(f"### Tab: `{tab_name}`")
        else:
            lines.append(f"#### Sub-Tab: `{tab_name}`")

        lines.append("")
        
        distinct_kinds = sum([
            1 if tab_fields else 0,
            1 if tab_menus else 0,
            1 if tab_relationship_items else 0,
            1 if tab_browsers else 0,
            1 if tab_addins else 0
        ])
        
        if tab_fields or tab_menus or total_controls > 1 or tab_title_bars or tab_spacers:
            if distinct_kinds > 1 or tab_title_bars or tab_spacers:
                kind_labels = []
                if tab_fields:   kind_labels.append(f"{len(tab_fields)} Form Field{'s' if len(tab_fields)>1 else ''}")
                if tab_relationship_items: kind_labels.append(f"{len(tab_relationship_items)} Related Object{'s' if len(tab_relationship_items)>1 else ''}/Report{'s' if len(tab_relationship_items)>1 else ''}")
                if tab_browsers: kind_labels.append(f"{len(tab_browsers)} Browser{'s' if len(tab_browsers)>1 else ''}")
                if tab_addins:   kind_labels.append(f"{len(tab_addins)} Add-In{'s' if len(tab_addins)>1 else ''}")
                if tab_menus:    kind_labels.append(f"{len(tab_menus)} Menu{'s' if len(tab_menus)>1 else ''}")
                lines.append(f"> **Multi-Component Tab** — {total_controls} controls across {max(distinct_kinds, 1)} types: {', '.join(kind_labels) if kind_labels else 'Form Layout'}")
                lines.append("")

                if tab_fields or tab_menus or tab_title_bars or tab_spacers:
                    lines.append("**1. Form Fields & Menus**")
                    lines.append("")
                    lines.append("| Position (Row, Col) | Field / Control | Details |")
                    lines.append("|---|---|---|")
                    field_elems = []
                    for f in tab_fields:
                        field_id = f.get("field_id")
                        has_pos = (f.get("row") is not None or f.get("column") is not None)
                        row = f.get("row", 0) or 0
                        col = f.get("column", 0) or 0
                        pos_str = f"Row {row}, Col {col}" if has_pos else "*(pos unknown)*"
                        rep_id = f.get("report_id")
                        notes = get_field_notes(field_id, f.get("label"), f.get("default_phone_type"), f.get("default_value"))
                        if rep_id: notes += f" (Lookup → Report **{rep_id}**)"
                        constraints = []
                        for opt_key, opt_label in [("readonly_option","ReadOnly"),("hidden_option","Hidden"),("required_option","Required")]:
                            c_str = format_profile_constraint(f.get(opt_key))
                            if c_str: constraints.append(f"{opt_label}: {c_str}")
                        if constraints: notes += f" — *{'; '.join(constraints)}*"
                        if not field_id: field_label = "No FieldId"
                        elif not str(field_id).strip(): field_label = "Empty FieldId"
                        else: field_label = f"`{field_id}`"
                        field_elems.append({"row": row, "col": col, "pos": pos_str, "name": field_label, "notes": notes, "has_pos": has_pos})
                    for m in tab_menus:
                        items_str = ", ".join(f"**{v}**" for v in m.get("items",[]))
                        field_elems.append({"row": m.get("row",0), "col": m.get("column",0), "pos": f"Row {m.get('row',0)}, Col {m.get('column',0)}", "name": f"`Menu ({m.get('id')})`", "notes": f"Dropdown options: {items_str}", "has_pos": True})
                    for tb in tab_title_bars:
                        field_elems.append({"row": tb.get("row",0), "col": tb.get("column",0), "pos": f"Row {tb.get('row',0)}, Col {tb.get('column',0)}", "name": f'Header: "{tb.get("text")}"', "notes": "Section TitleBar banner", "has_pos": True})
                    for sp in tab_spacers:
                        field_elems.append({"row": sp.get("row",0), "col": sp.get("column",0), "pos": f"Row {sp.get('row',0)}, Col {sp.get('column',0)}", "name": "`Spacer`", "notes": f"Visual layout spacing ({sp.get('height') or '26'}px height)", "has_pos": True})
                    field_elems.sort(key=lambda x: (not x["has_pos"], x["row"], x["col"]))
                    for el in field_elems:
                        lines.append(f"| {el['pos']} | {el['name']} | {el['notes']} |")
                    lines.append("")

                if tab_relationship_items:
                    lines.append("**2. Related Objects & Direct Reports**")
                    lines.append("")
                    lines.append("| Position (Row, Col) | Type | Object / Report | Report IDs | Behavior / Config |")
                    lines.append("|---|---|---|---|---|")
                    for ri in tab_relationship_items:
                        item_type = ri.get("item_type")
                        ac_id = ri.get("ac_id") or "—"
                        search_id = ri.get("search_report_id") or "—"
                        ctrl_type = "Direct Report" if item_type == "Report" else "Related Object"
                        obj_name = "`Report`" if item_type == "Report" else f"`{get_related_object_name(item_type)}`"
                        report_ids = f"Primary: **{ac_id}**" + (f", Secondary: **{search_id}**" if search_id != "—" else "")
                        behavior = "Skips on new records" if not ri.get("execute_on_new") else "Runs on all records"
                        extra = []
                        if ri.get("can_send_on_save") == "True": extra.append("CanSendOnSave")
                        if ri.get("default_channel_customer"): extra.append(f"CustomerChannel: {ri['default_channel_customer']}")
                        if ri.get("status_change_on_response"): extra.append(f"StatusChangeOnResponse: {ri['status_change_on_response']}")
                        if extra: behavior += f" *({'; '.join(extra)})*"
                        lines.append(f"| Row {ri.get('row',0)}, Col {ri.get('column',0)} | {ctrl_type} | {obj_name} | {report_ids} | {behavior} |")
                    lines.append("")

                if tab_browsers:
                    lines.append("**3. Embedded Browsers**")
                    lines.append("")
                    lines.append("| Position (Row, Col) | Target URL | Suppress Errors |")
                    lines.append("|---|---|---|")
                    for br in tab_browsers:
                        url = br.get("url") or "*(Unconfigured)*"
                        suppress = "Yes" if br.get("suppress_errors") else "No"
                        lines.append(f"| Row {br.get('row',0)}, Col {br.get('column',0)} | `{url}` | {suppress} |")
                    lines.append("")

                if tab_addins:
                    lines.append("**4. Add-Ins & BUI Extensions**")
                    lines.append("")
                    lines.append("| Position (Row, Col) | Type | Plugin Name | File ID | Assembly |")
                    lines.append("|---|---|---|---|---|")
                    for ai in tab_addins:
                        plugin_type = "BUI Extension" if ai.get("bui_extension") else "Add-In Plugin"
                        assembly = "—" if ai.get("bui_extension") else (ai.get("assembly") or "—")
                        lines.append(f"| Row {ai.get('row',0)}, Col {ai.get('column',0)} | {plugin_type} | `{ai.get('name')}` | `{ai.get('file_id') or '—'}` | `{assembly}` |")
                    lines.append("")

            else:
                lines.append("**Layout Grid Structure (Fields & Nested Controls):**")
                lines.append("")
                lines.append("| Position (Row, Col) | Control Type | Control Name / Field | Target / Action Details |")
                lines.append("|---|---|---|---|")
                grid_elements = []
                for f in tab_fields:
                    field_id = f.get("field_id")
                    has_pos = (f.get("row") is not None or f.get("column") is not None)
                    row = f.get("row", 0) or 0
                    col = f.get("column", 0) or 0
                    pos_str = f"Row {row}, Col {col}" if has_pos else "*(pos unknown)*"
                    rep_id = f.get("report_id")
                    notes = get_field_notes(field_id, f.get("label"), f.get("default_phone_type"), f.get("default_value"))
                    if rep_id: notes += f" (Lookup pointing to Report **{rep_id}**)"
                    constraints = []
                    for opt_key, opt_label in [("readonly_option","ReadOnly"),("hidden_option","Hidden"),("required_option","Required")]:
                        c_str = format_profile_constraint(f.get(opt_key))
                        if c_str: constraints.append(f"{opt_label}: {c_str}")
                    if constraints: notes += f" — *Constraints: {'; '.join(constraints)}*"
                    if not field_id: field_label = "No FieldId"
                    elif not str(field_id).strip(): field_label = "Empty FieldId"
                    else: field_label = f"`{field_id}`"
                    grid_elements.append({"row": row, "column": col, "pos": pos_str, "has_pos": has_pos, "type": "Form Field", "name": field_label, "notes": notes})
                for m in tab_menus:
                    items_str = ", ".join(f"**{v}**" for v in m.get("items",[]))
                    grid_elements.append({"row": m.get("row",0), "column": m.get("column",0), "type": "Dropdown Menu", "name": f"`Menu ({m.get('id')})`", "notes": f"Custom dropdown options: {items_str}"})
                for tb in tab_title_bars:
                    grid_elements.append({"row": tb.get("row",0), "column": tb.get("column",0), "type": "Section Header", "name": f'Header: "{tb.get("text")}"', "notes": "Section TitleBar banner"})
                for sp in tab_spacers:
                    grid_elements.append({"row": sp.get("row",0), "column": sp.get("column",0), "type": "Layout Spacer", "name": "`Spacer`", "notes": f"Visual layout spacing ({sp.get('height') or '26'}px height)"})
                for ri in tab_relationship_items:
                    item_type = ri.get("item_type")
                    ac_id = ri.get("ac_id"); search_id = ri.get("search_report_id")
                    details_list = []
                    if ac_id and ac_id != "0": details_list.append(f"Primary Report (AcId): **{ac_id}**")
                    if search_id and search_id != "0": details_list.append(f"Secondary Report (SearchId): **{search_id}**")
                    if not ri.get("execute_on_new"): details_list.append("skips on new records")
                    extra = []
                    if ri.get("can_send_on_save") == "True": extra.append("CanSendOnSave")
                    if ri.get("default_channel_customer"): extra.append(f"CustomerChannel: {ri['default_channel_customer']}")
                    if extra: details_list.append("; ".join(extra))
                    details = "; ".join(details_list) if details_list else "—"
                    grid_elements.append({"row": ri.get("row",0), "column": ri.get("column",0), "type": "Direct Report" if item_type=="Report" else "Related Object", "name": "`Report`" if item_type=="Report" else f"`{get_related_object_name(item_type)}`", "notes": details})
                for br in tab_browsers:
                    url = br.get("url") or ""
                    grid_elements.append({"row": br.get("row",0), "column": br.get("column",0), "type": "Browser", "name": "`Embedded Browser`", "notes": f"URL: `{url}`" if url else "No URL configured"})
                for ai in tab_addins:
                    notes_parts = []
                    if ai.get("file_id"): notes_parts.append(f"FileId: `{ai.get('file_id')}`")
                    if ai.get("assembly") and not ai.get("bui_extension"): notes_parts.append(f"Assembly: `{ai.get('assembly')}`")
                    plugin_type = "BUI Extension" if ai.get("bui_extension") else "Add-In Plugin"
                    grid_elements.append({"row": ai.get("row",0), "column": ai.get("column",0), "type": plugin_type, "name": f"`{ai.get('name')}`", "notes": "; ".join(notes_parts) if notes_parts else "—"})
                for el in grid_elements:
                    if "pos" not in el:
                        el["pos"] = f"Row {el['row']}, Col {el['column']}"
                        el["has_pos"] = True
                grid_elements.sort(key=lambda x: (not x.get("has_pos", True), x["row"], x["column"]))
                for el in grid_elements:
                    lines.append(f"| {el['pos']} | {el['type']} | {el['name']} | {el['notes']} |")
                lines.append("")
        else:
            lines.append("> **Single Component Tab**")
            lines.append("")
            for ri in tab_relationship_items:
                control_type = "Direct Report" if ri.get("item_type") == "Report" else f"Related Object (`{get_related_object_name(ri.get('item_type'))}`)"
                lines.append(f"- **Control Type:** {control_type}")
                if ri.get("ac_id") and ri["ac_id"] != "0":
                    lines.append(f"  - **Primary Report (AcId):** `{ri['ac_id']}`")
                if ri.get("search_report_id") and ri["search_report_id"] != "0":
                    lines.append(f"  - **Secondary Report (SearchId):** `{ri['search_report_id']}`")
                if not ri.get("execute_on_new"):
                    lines.append("  - **Behavior:** Skips execution on unsaved new records")
                if ri.get("can_send_on_save") == "True":
                    lines.append("  - **CanSendOnSave:** Enabled")
                if ri.get("default_channel_customer"):
                    lines.append(f"  - **Default Customer Channel:** `{ri['default_channel_customer']}`")
            for br in tab_browsers:
                url = br.get("url") or ""
                lines.append("- **Control Type:** Embedded Browser")
                if url: lines.append(f"  - **Target URL:** `{url}`")
                else: lines.append("  - **Target URL:** *(Unconfigured / No URL)*")
            for ai in tab_addins:
                plugin_type = "BUI Extension" if ai.get("bui_extension") else "Add-In Plugin"
                lines.append(f"- **Control Type:** {plugin_type} (`{ai.get('name')}`)")
                if ai.get("file_id"): lines.append(f"  - **File ID:** `{ai.get('file_id')}`")
            lines.append("")

        nested_tabsets = t.get("nested_tabsets", [])
        if nested_tabsets:
            for ts in nested_tabsets:
                sub_tabs = ts.get("sub_tabs", [])
                sub_tab_names = ", ".join([f"**{clean_tab_label(st.get('text'))}**" for st in sub_tabs])
                lines.append(f"> **Nested TabSet** (Row {ts.get('row', 0)}, Col {ts.get('column', 0)}) — {len(sub_tabs)} Sub-Tabs: {sub_tab_names}")
                lines.append("")
                for sub_t in sub_tabs:
                    render_single_tab(sub_t, is_subtab=True)

        if not is_subtab:
            lines.append("  </div>")
            lines.append("</details>")
            lines.append("")

    for t in ws.get("tabs", []):
        render_single_tab(t, is_subtab=False)
        
    lines.append("")
    lines.append("---")
    
    # Workspace Rules
    lines.append("## Workspace Rules")
    lines.append("")
    
    rules = ws.get("rules", [])
    if not rules:
        lines.append("No rules defined in this workspace.")
    else:
        tab_id_to_name = {
            t.get("id"): clean_tab_label(t.get("text"))
            for t in all_tabs_flat
            if t.get("id")
        }

        rules_by_trigger = {}
        for r in rules:
            trigs = ", ".join(r.get("triggers", []))
            if trigs == "EditorLoaded":
                trigs = "Editor Initialized (On Load)"
            rules_by_trigger.setdefault(trigs, []).append(r)

        for trigger_name, trigger_rules in rules_by_trigger.items():
            display_trigger = trigger_name.strip() if trigger_name.strip() else "(No Trigger Defined)"
            lines.append(f"### Event: {display_trigger}")
            lines.append("")

            for rule in trigger_rules:
                is_act = rule.get("active", True)
                active_str = "Active" if is_act else "Inactive"
                act_badge = '<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>' if is_act else '<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #94a3b8; color: #94a3b8; margin-right: 8px;">Inactive</span>'
                rule_display_name = rule.get("name") or "(Unnamed Rule)"

                lines.append('<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">')
                lines.append(f'  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">{act_badge}Rule: <b>{rule_display_name}</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: {display_trigger})</span></summary>')
                lines.append('  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">')
                lines.append("")
                lines.append(f"#### Rule: `{rule_display_name}` ({active_str})")
                if rule.get("notes"):
                    lines.append(f"*{rule.get('notes')}*")
                    lines.append("")

                conds = rule.get("conditions", [])
                if conds:
                    logic_expr = conds[0].get("logic_expr")
                    cond_strs = [format_condition(c) for c in conds]
                    if logic_expr and len(cond_strs) > 1:
                        def substitute_logic(expr, strs):
                            return re.sub(
                                r'\b(\d+)\b',
                                lambda m: strs[int(m.group(1))] if int(m.group(1)) < len(strs) else m.group(0),
                                expr
                            )
                        cond_line = substitute_logic(logic_expr, cond_strs)
                    else:
                        cond_line = " && ".join(cond_strs)
                else:
                    cond_line = "None"
                lines.append(f"- **Condition:** {cond_line}")

                then_acts = [a for a in rule.get("actions", []) if a.get("branch") != "else"]
                else_acts = [a for a in rule.get("actions", []) if a.get("branch") == "else"]
                if then_acts:
                    lines.append("- **Then:**")
                    for act in then_acts:
                        lines.append(f"  - {format_action(act, tab_id_to_name)}")
                if else_acts:
                    lines.append("- **Else:**")
                    for act in else_acts:
                        lines.append(f"  - {format_action(act, tab_id_to_name)}")
                if not then_acts and not else_acts:
                    lines.append("- **Actions:** *(none)*")
                lines.append("")
                lines.append("  </div>")
                lines.append("</details>")
                lines.append("")
            
    lines.append("---")
    lines.append("")
    
    # Ribbon & Toolbar
    lines.append("## Ribbon / Toolbar")
    lines.append("")
    
    buttons = [format_ribbon_button(btn) for btn in ws.get("ribbon_buttons", []) if btn not in ("Separator", "EditorLinks")]
    btn_list_str = ", ".join(buttons)
    lines.append(f"Standard actions: {btn_list_str}.")
    lines.append("")
    
    if ws.get("ribbon_links"):
        lines.append("**Embedded Links:**")
        for link in ws.get("ribbon_links", []):
            title = link.get("title") or "Untitled Link"
            url = link.get("url")
            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title} *(no URL configured)*")
        lines.append("")
        
    lines.append("---")
    lines.append("")
    
    # Key Observations
    lines.append("## Key Observations")
    lines.append("")
    
    for f in ws.get("fields", []):
        fid = f.get("field_id")
        flabel = f.get("label") or ""
        if fid == "PhOffice" and "mobile" in flabel.lower():
            clean_label = flabel.replace('&', '').strip()
            lines.append(f"- The `{fid}` field is **mislabeled as \"{clean_label}\"** — that's either intentional repurposing or a bug worth flagging.")
            
    for t in all_tabs_flat:
        tab_name = t.get("text") or "Unknown"
        for br in t.get("browsers", []):
            url = br.get("url") or ""
            if url:
                parsed = urllib.parse.urlparse(url)
                domain = parsed.netloc
                path = parsed.path
                suppress = br.get("suppress_errors")
                params = urllib.parse.parse_qs(parsed.query)
                param_names = list(params.keys())
                param_str = f" — passes URL params: {', '.join(f'`{p}`' for p in param_names)}" if param_names else ""
                
                u_lower = url.lower()
                if "php/custom" in u_lower or "gcb.cfg/php/custom" in u_lower or ".cfg/php/custom" in u_lower:
                    script_file = os.path.basename(path) or "custom script"
                    obs = f"- The **{tab_name}** tab embeds an internal **custom PHP script**: `{script_file}` (`{path}`){param_str}."
                else:
                    obs = f"- The **{tab_name}** tab embeds an **external URL** pointing to `{domain}`{param_str}."

                if suppress:
                    obs += " Errors are suppressed."
                lines.append(obs)
            
    custom_field_ids = [f.get("field_id") for f in ws.get("fields", []) if f.get("field_id", "").startswith("C$")]
    if custom_field_ids:
        lines.append("- `C$` prefix fields are **custom fields** added on top of the standard schema.")
        
    inactive_rules = [r for r in rules if not r.get("active", True)]
    if inactive_rules:
        lines.append("- The inactive rule suggests there was a workflow for email-originated contacts that's either been deprecated or temporarily disabled.")
        
    active_rules = [r for r in rules if r.get("active", True)]
    if active_rules:
        lines.append(f"- The workspace defines **{len(active_rules)} active business rules** triggered by editor loading events, enforcing profile-based field locking and toolbar UI visibility.")
        
    if not ws.get("flag_visible", True):
        lines.append("- The **workspace flag indicator** is explicitly hidden (`Visible=\"False\"`), suppressing visual cues for users/agents.")
        
    tab_set_info = ws.get("tab_set_info")
    if tab_set_info and tab_set_info.get("can_reorder_tabs"):
        lines.append("- Layout tabset has **`CanReorderTabs=\"True\"`** enabled, which allows agents to dynamically rearrange workspace tabs at runtime.")
        
    all_addins = []
    for tab in all_tabs_flat:
        all_addins.extend(tab.get("add_in_items", []))
        
    for ai in all_addins:
        if ai.get("bui_extension"):
            lines.append(f"- The workspace includes an **external BUI Extension plugin dependency**: `{ai.get('name')}` (FileId: `{ai.get('file_id') or '—'}`).")
        else:
            lines.append(f"- The workspace includes an **external BUI Add-In plugin dependency**: `{ai.get('name')}` (Assembly: `{ai.get('assembly') or '—'}`, FileId: `{ai.get('file_id') or '—'}`).")

    # 5. Flow Diagram (Mermaid)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Flow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    
    lines.append("  classDef workspace fill:#eab308,stroke:#854d0e,stroke-width:2px,color:#0f172a;")
    lines.append("  classDef tab fill:#e0f2fe,stroke:#0284c7,stroke-width:1px,color:#0369a1;")
    lines.append("  classDef report fill:#3b82f6,stroke:#1d4ed8,stroke-width:1px,color:#fff;")
    lines.append("  classDef browser fill:#ef4444,stroke:#b91c1c,stroke-width:1px,color:#fff;")
    lines.append("  classDef rule fill:#ec4899,stroke:#be185d,stroke-width:1px,color:#fff;")
    lines.append("  classDef field fill:#f1f5f9,stroke:#64748b,stroke-width:1px,color:#334155;")
    lines.append("  classDef object fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;")
    lines.append("  classDef addin fill:#06b6d4,stroke:#0891b2,stroke-width:1px,color:#fff;")
    lines.append("  classDef warning fill:#cbd5e1,stroke:#94a3b8,stroke-width:1px,color:#64748b;")
    
    ws_name = ws.get("name")
    ws_id = "WS_" + re.sub(r'[^a-zA-Z0-9_]', '', ws_name.replace(' ', '_'))
    
    tab_nodes = []
    rule_nodes = []
    field_nodes = []
    report_nodes = []
    browser_nodes = []
    object_nodes = []
    addin_nodes = []
    warning_nodes = []
    
    ws_to_tab_connections = []
    ws_to_field_connections = []
    ws_to_rule_connections = []
    rule_to_tab_connections = []
    tab_to_tab_connections = []
    tab_to_child_connections = []
    child_to_report_connections = []
    
    declared_nodes = set([ws_id])
    tab_node_ids = {}
    
    global_tab_counter = 0

    def process_tab_nodes_recursive(t, parent_node_id, is_subtab=False):
        nonlocal global_tab_counter
        idx = global_tab_counter
        global_tab_counter += 1

        tab_text = clean_tab_label(t.get("text"))
        clean_tab = tab_text.replace('"', '').replace("'", "")
        tab_id = t.get("id") or f"tab_{idx}"
        tab_node_id = f"SubTab_{idx}" if is_subtab else f"Tab_{idx}"
        tab_node_ids[tab_id] = tab_node_id

        node_prefix = "Sub-Tab" if is_subtab else "Tab"
        tab_nodes.append(f"    {tab_node_id}[\"{node_prefix}: {clean_tab}\"]:::tab")
        
        if is_subtab:
            tab_to_tab_connections.append(f"  {parent_node_id} --> |\"Nested TabSet\"| {tab_node_id}")
        else:
            ws_to_tab_connections.append(f"  {ws_id} --> {tab_node_id}")

        for f in t.get("fields", []):
            field_id = f.get("field_id")
            rep_id = f.get("report_id")
            if rep_id and field_id:
                field_node_id = f"Field_{idx}_{field_id.replace('.', '_').replace('$', '')}"
                if field_node_id not in declared_nodes:
                    field_nodes.append(f"    {field_node_id}[\"Field: {field_id}\"]:::field")
                    declared_nodes.add(field_node_id)
                tab_to_child_connections.append(f"  {tab_node_id} --> |\"Form Field\"| {field_node_id}")
                node_name = f"R_{rep_id}"
                if node_name not in declared_nodes:
                    report_nodes.append(f"    {node_name}[\"Report: {rep_id}\"]:::report")
                    declared_nodes.add(node_name)
                child_to_report_connections.append(f"  {field_node_id} --> |\"Lookup Report\"| {node_name}")
            
        for ri in t.get("relationship_items", []):
            ac_id = ri.get("ac_id")
            search_id = ri.get("search_report_id")
            item_type = ri.get("item_type")
            if item_type and item_type != "Report":
                obj_name = get_related_object_name(item_type)
                obj_node_id = f"Obj_{idx}_{item_type.replace('.', '_')}"
                if obj_node_id not in declared_nodes:
                    object_nodes.append(f"    {obj_node_id}[\"Related Object: {obj_name}\"]:::object")
                    declared_nodes.add(obj_node_id)
                tab_to_child_connections.append(f"  {tab_node_id} --> |\"Related Object\"| {obj_node_id}")
                if ac_id and ac_id != "0":
                    node_name = f"R_{ac_id}"
                    if node_name not in declared_nodes:
                        report_nodes.append(f"    {node_name}[\"Report: {ac_id}\"]:::report")
                        declared_nodes.add(node_name)
                    child_to_report_connections.append(f"  {obj_node_id} --> |\"Primary Report (AcId)\"| {node_name}")
                if search_id and search_id != "0":
                    node_name = f"R_{search_id}"
                    if node_name not in declared_nodes:
                        report_nodes.append(f"    {node_name}[\"Report: {search_id}\"]:::report")
                        declared_nodes.add(node_name)
                    child_to_report_connections.append(f"  {obj_node_id} --> |\"Secondary Report (SearchId)\"| {node_name}")
            else:
                if ac_id and ac_id != "0":
                    node_name = f"R_{ac_id}"
                    if node_name not in declared_nodes:
                        report_nodes.append(f"    {node_name}[\"Report: {ac_id}\"]:::report")
                        declared_nodes.add(node_name)
                    tab_to_child_connections.append(f"  {tab_node_id} --> |\"Primary Report (AcId)\"| {node_name}")
                if search_id and search_id != "0":
                    node_name = f"R_{search_id}"
                    if node_name not in declared_nodes:
                        report_nodes.append(f"    {node_name}[\"Report: {search_id}\"]:::report")
                        declared_nodes.add(node_name)
                    tab_to_child_connections.append(f"  {tab_node_id} --> |\"Secondary Report (SearchId)\"| {node_name}")
                if (not ac_id or ac_id == "0") and (not search_id or search_id == "0"):
                    node_name = f"R_0_{idx}"
                    if node_name not in declared_nodes:
                        warning_nodes.append(f"    {node_name}[\"No Report Configured\"]:::warning")
                        declared_nodes.add(node_name)
                    tab_to_child_connections.append(f"  {tab_node_id} --> {node_name}")
                
        for br_idx, br in enumerate(t.get("browsers", [])):
            url = br.get("url") or ""
            is_warning = False
            is_custom = False
            if url:
                parsed = urllib.parse.urlparse(url)
                path_base = os.path.basename(parsed.path)
                clean_base = path_base.replace('"', '').replace("'", "")
                if not clean_base: clean_base = "Unnamed Browser"
                u_lower = url.lower()
                if "php/custom" in u_lower or "gcb.cfg/php/custom" in u_lower or ".cfg/php/custom" in u_lower:
                    is_custom = True
            else:
                clean_base = "No URL Configured"
                is_warning = True
            
            br_id = br.get("id")
            br_node_id = f"B_{br_id}" if br_id else f"B_browser_{idx}_{br_idx}"
            br_node_id = re.sub(r'[^a-zA-Z0-9_]', '', br_node_id)
            if br_node_id not in declared_nodes:
                if is_warning:
                    warning_nodes.append(f"    {br_node_id}[\"{clean_base}\"]:::warning")
                elif is_custom:
                    addin_nodes.append(f"    {br_node_id}[\"Custom Script: {clean_base}\"]:::addin")
                else:
                    browser_nodes.append(f"    {br_node_id}[\"External URL: {parsed.netloc or clean_base}\"]:::browser")
                declared_nodes.add(br_node_id)
            edge_label = "Custom Script" if is_custom else "Browser"
            tab_to_child_connections.append(f"  {tab_node_id} --> |\"{edge_label}\"| {br_node_id}")
            
        for ai_idx, ai in enumerate(t.get("add_in_items", [])):
            addin_name = ai.get("name") or "AddIn"
            addin_node_id = f"AddIn_{idx}_{ai_idx}"
            if addin_node_id not in declared_nodes:
                addin_nodes.append(f"    {addin_node_id}[\"Add-In: {addin_name}\"]:::addin")
                declared_nodes.add(addin_node_id)
            tab_to_child_connections.append(f"  {tab_node_id} --> |\"Add-In Plugin\"| {addin_node_id}")

        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                process_tab_nodes_recursive(sub_t, parent_node_id=tab_node_id, is_subtab=True)

    for outer_tab in ws.get("tabs", []):
        process_tab_nodes_recursive(outer_tab, parent_node_id=ws_id, is_subtab=False)
            
    for f in ws.get("fields", []):
        field_id = f.get("field_id")
        rep_id = f.get("report_id")
        if rep_id and field_id:
            field_node_id = f"Field_top_{field_id.replace('.', '_').replace('$', '')}"
            if field_node_id not in declared_nodes:
                field_nodes.append(f"    {field_node_id}[\"Field: {field_id}\"]:::field")
                declared_nodes.add(field_node_id)
            ws_to_field_connections.append(f"  {ws_id} --> {field_node_id}")
            node_name = f"R_{rep_id}"
            if node_name not in declared_nodes:
                report_nodes.append(f"    {node_name}[\"Report: {rep_id}\"]:::report")
                declared_nodes.add(node_name)
            child_to_report_connections.append(f"  {field_node_id} --> |\"Lookup Report\"| {node_name}")
            
    for idx, r in enumerate(rules):
        rule_name = r.get("name") or f"Rule {idx}"
        clean_rule = rule_name.replace('"', "'").replace('`', "'")
        rule_id = f"Rule_{idx}"
        active_label = " (Active)" if r.get("active", True) else " (Inactive)"
        rule_nodes.append(f"    {rule_id}[\"Rule: {clean_rule}{active_label}\"]:::rule")
        trigs = ", ".join(r.get("triggers", []))
        if trigs == "EditorLoaded": trigs = "Editor loads"
        ws_to_rule_connections.append(f"  {ws_id} --> |\"Trig: {trigs}\"| {rule_id}")
        
        for act in r.get("actions", []):
            obj_id = act.get("object_id") or act.get("object")
            if obj_id and str(obj_id) in tab_node_ids:
                target_tab_node = tab_node_ids[str(obj_id)]
                oper = act.get("operation") or "Action"
                rule_to_tab_connections.append(f"  {rule_id} -.-> |\"{oper}\"| {target_tab_node}")

    lines.append(f"  subgraph Workspace_Layer[\"{ws_name} Workspace\"]")
    lines.append(f"    {ws_id}[\"{ws_name}\"]:::workspace")
    lines.append("  end")
    lines.append("")
    
    if tab_nodes:
        lines.append("  subgraph Tabs_Layer[\"Workspace Tabs\"]")
        lines.extend(tab_nodes)
        lines.append("  end")
        lines.append("")
        
    if rule_nodes:
        lines.append("  subgraph Rules_Layer[\"Business Rules\"]")
        lines.extend(rule_nodes)
        lines.append("  end")
        lines.append("")
        
    if field_nodes:
        lines.append("  subgraph Fields_Layer[\"Lookup Fields\"]")
        lines.extend(field_nodes)
        lines.append("  end")
        lines.append("")
        
    if object_nodes:
        lines.append("  subgraph Objects_Layer[\"Related Objects\"]")
        lines.extend(object_nodes)
        lines.append("  end")
        lines.append("")
        
    if browser_nodes:
        lines.append("  subgraph Browsers_Layer[\"Embedded Browsers\"]")
        lines.extend(browser_nodes)
        lines.append("  end")
        lines.append("")
        
    if addin_nodes:
        lines.append("  subgraph Addins_Layer[\"BUI Extensions\"]")
        lines.extend(addin_nodes)
        lines.append("  end")
        lines.append("")
        
    if report_nodes:
        lines.append("  subgraph Reports_Layer[\"Target Reports\"]")
        lines.extend(report_nodes)
        lines.append("  end")
        lines.append("")
        
    if warning_nodes:
        lines.append("  subgraph Warnings_Layer[\"Unconfigured / Warnings\"]")
        lines.extend(warning_nodes)
        lines.append("  end")
        lines.append("")

    if ws_to_tab_connections: lines.extend(ws_to_tab_connections)
    if tab_to_tab_connections: lines.extend(tab_to_tab_connections)
    if ws_to_field_connections: lines.extend(ws_to_field_connections)
    if ws_to_rule_connections: lines.extend(ws_to_rule_connections)
    if rule_to_tab_connections: lines.extend(rule_to_tab_connections)
    if tab_to_child_connections: lines.extend(tab_to_child_connections)
    if child_to_report_connections: lines.extend(child_to_report_connections)
    
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Parser Coverage Gaps")
    lines.append("")
    lines.append("The following elements were found in this workspace XML but are not fully parsed by the current accelerator. Raw data is preserved in `master.json` under `unknowns`.")
    lines.append("")

    unknowns = ws.get("unknowns", {})
    unk_attrs = unknowns.get("unknown_attrs", [])
    unk_children = unknowns.get("unknown_children", [])

    if not unk_attrs and not unk_children:
        lines.append("*No parser coverage gaps identified for this workspace.*")
    else:
        lines.append("| Location | Element / Attribute | Raw Value / XML |")
        lines.append("|---|---|---|")
        for item in unk_attrs:
            loc = item.get("location", "Workspace")
            attr = f"Attribute: `{item.get('attribute')}`"
            val = f"`\"{item.get('value')}\"`"
            lines.append(f"| {loc} | {attr} | {val} |")
        for item in unk_children:
            loc = item.get("location", "Workspace")
            tag = f"Element: `<{item.get('tag')}>`"
            raw = f"`{item.get('raw', '')}`"
            lines.append(f"| {loc} | {tag} | {raw} |")

    lines.append("")

    return "\n".join(lines)

def generate_analytics_report_markdown(report):
    lines = []
    rep_name = report.get("name", "Report")
    rep_id = report.get("id", "Unknown")
    
    lines.append(f"# Report: {rep_name} (ID: {rep_id})")
    lines.append("")
    
    ac_type_raw = report.get("ac_type", "1")
    rpt_type_str = "Grid Report" if str(ac_type_raw) == "1" else f"Report Type {ac_type_raw}"
    public_str = "public" if report.get("ac_public") else "private"
    
    primary_tbl = "—"
    for t in report.get("tables", []):
        if t.get("join_type") == "Primary":
            primary_tbl = t.get("alias") or t.get("tbl_enum")
            break
            
    cdate = report.get("created") or "Unknown"
    udate = report.get("updated") or "Unknown"
    folder = report.get("folder_id") or "—"
    owner_raw = report.get("owner_acct_id") or "—"
    owner_str = f"{owner_raw} `[unresolved account ID]`" if owner_raw != "—" else "—"
    interface_id = report.get("interface_id") or "—"
    image_code = report.get("image") or "—"
    time_zone = report.get("time_zone") or "0"
    opts_raw = report.get("opts") or "—"
    opts_str = f"{opts_raw} `[unresolved bitmask]`" if opts_raw != "—" else "—"
    aux = report.get("aux") or "—"
    signature = report.get("export_signature")

    node_cnt = report.get("node_count", 1)
    node_details = report.get("node_details", [])
    node_info_list = []
    hidden_sections_all = set()
    display_opts_all = set()
    for nd in node_details:
        n_id = nd.get("n_id", "1")
        style_id = nd.get("style_id", "12")
        r_lim = nd.get("row_limit", "None")
        node_info_list.append(f"Node #{n_id} (style_id={style_id}, row_limit={r_lim})")
        hidden_sections_all.update(nd.get("hidden_sections", []))
        display_opts_all.update(nd.get("display_options", []))

    node_str = "; ".join(node_info_list) if node_info_list else "single node_item"
    hidden_sec_str = ", ".join(f"`{s}`" for s in sorted(hidden_sections_all)) if hidden_sections_all else "None"
    disp_opt_str = ", ".join(f"`{o}`" for o in sorted(display_opts_all)) if display_opts_all else "Standard"

    sort_summary = "None"
    for c in report.get("columns", []):
        if c.get("sort_order") == "1":
            sort_dir = "Descending" if c.get("sort_direction") == "2" else "Ascending"
            sort_summary = f"{c.get('source_field')} — {sort_dir} (primary)"
            break

    filters = report.get("filters", [])
    if filters:
        filter_summary = f"{len(filters)} configured"
    elif report.get("has_filters_container"):
        filter_summary = "None configured (empty `<filters/>` in source XML)"
    else:
        filter_summary = "None configured"

    lines.append(f"- Type: **{rpt_type_str}** (ac_type={ac_type_raw}, {public_str})")
    lines.append(f"- Primary Table: `{primary_tbl}`")
    lines.append(f"- Created: `{cdate}` | Last Updated: `{udate}`")
    lines.append(f"- Folder ID: `{folder}` | Owner Account ID: {owner_str} | Interface ID: `{interface_id}` | Image Icon: `{image_code}`")
    lines.append(f"- Nodes ({node_cnt}): `{node_str}`")
    lines.append(f"- Display Layout: {disp_opt_str} | Hidden Sections: {hidden_sec_str}")
    lines.append(f"- Options & Aux: `opts={opts_str}`, `time_zone={time_zone}` | `aux={aux}`")
    if signature:
        lines.append(f"- Export Signature: `{signature}`")
    lines.append(f"- Sort: `{sort_summary}`")
    lines.append(f"- Filters: {filter_summary}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Columns
    cols = report.get("columns", [])
    lines.append(f"### Columns ({len(cols)})")
    lines.append("")
    if not cols:
        lines.append("*No columns defined in this report.*")
    else:
        lines.append("| # | Source Field | Table | Label | Data Type | Column Attrs | Sort |")
        lines.append("|---|---|---|---|---|---|---|")
        col_mismatches = []
        for c in cols:
            idx = c.get("display_order") or c.get("col_id")
            s_field = f"`{c.get('source_field')}`"
            tbl = f"`{c.get('table_alias')}`"
            lbl = c.get("label") or "—"
            dtype = c.get("data_type") or "—"
            vattrs = c.get("val_attrs") or "—"
            sort_str = c.get("sort_info") or "—"
            if not c.get("col_rf_verified", True):
                col_mismatches.append(c)
            lines.append(f"| {idx} | {s_field} | {tbl} | {lbl} | {dtype} | {vattrs} | {sort_str} |")
        lines.append("")
        lines.append("*Column sequence is ordered by `display_order` from XML.*")
        lines.append("")
        lines.append("> **Attribute Footnote**: `Masked/Login (32769)` indicates column value represents user credential or login identity (partially masked/hashed in UI). `Custom/System Field (9)` indicates custom field or primary system identifier.")
        lines.append("")
        if not col_mismatches:
            lines.append(f"> **Column Validation Note**: All {len(cols)} columns verified against internal table references (`val_col_refs`).")
        else:
            lines.append(f"> **Column Validation Warning** ({len(col_mismatches)} table reference mismatches detected):")
            for cm in col_mismatches:
                cid = cm.get("col_id")
                s_field = cm.get("source_field")
                detail = cm.get("col_rf_mismatch_detail") or f"field prefix = `{cm.get('table_alias')}`"
                lines.append(f"> - **Col {cid}** (`{s_field}`): {detail}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Table Joins
    tables = report.get("tables", [])
    lines.append(f"### Table Joins ({len(tables)})")
    lines.append("")
    if not tables:
        lines.append("*No table joins defined.*")
    else:
        lines.append("| Table | Alias | Join Type | Join Def Index | Join Condition |")
        lines.append("|---|---|---|---|---|")
        for t in tables:
            tbl_label = f"{t.get('alias')} (tbl {t.get('tbl_enum')})" if t.get('tbl_enum') else t.get('alias')
            j_idx = t.get("join_def_idx") or "—"
            lines.append(f"| `{tbl_label}` | `{t.get('alias')}` | {t.get('join_type')} | `{j_idx}` | `{t.get('join_condition')}` |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Filters & Variables Table
    filters = report.get("filters", [])
    lines.append(f"### Filters & Variable Parameters ({len(filters)})")
    lines.append("")
    if not filters:
        if report.get("has_filters_container"):
            lines.append("*No filters configured (empty `<filters/>` in source XML).*")
        else:
            lines.append("*No filters configured in report XML.*")
    else:
        lines.append("| Filter ID / Name | Target Field | Operator | Default Value / Expression | Notes |")
        lines.append("|---|---|---|---|---|")
        for idx, flt in enumerate(filters, 1):
            fid = f"`{flt.get('id')}`" if flt.get('id') else (f"`{flt.get('name')}`" if flt.get('name') else f"`#{idx}`")
            f_field = f"`{flt.get('field')}`" if flt.get('field') else "—"
            op_val = f"`{flt.get('operator')}`" if flt.get('operator') else "—"
            def_val = f"`{flt.get('val')}`" if flt.get('val') is not None and str(flt.get('val')).strip() else "—"
            notes = "Configured report filter"
            lines.append(f"| {fid} | {f_field} | {op_val} | {def_val} | {notes} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Permissions
    perms_by_type = report.get("perms_by_type", {})
    all_perms = report.get("permissions", [])
    lines.append(f"### Permissions ({len(all_perms)} profiles)")
    lines.append("")
    if not perms_by_type:
        lines.append("*No permissions configured.*")
    else:
        for ptype, pids in perms_by_type.items():
            pid_str = ", ".join(f"`{pid}`" for pid in pids)
            lines.append(f"- **{ptype}:** profiles {pid_str}")

    # Flow Diagram (Mermaid)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Flow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  classDef report fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;")
    lines.append("  classDef table fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;")
    lines.append("  classDef field fill:#f1f5f9,stroke:#64748b,stroke-width:1px,color:#334155;")
    lines.append("  classDef perm fill:#e0f2fe,stroke:#0284c7,stroke-width:1px,color:#0369a1;")
    lines.append("  classDef warning fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;")
    lines.append("")

    clean_rep_name = rep_name.replace('"', '').replace("'", "")
    rep_node_id = f"R_{re.sub(r'[^a-zA-Z0-9_]', '', str(rep_id) if rep_id else 'unknown')}"
    
    lines.append("  subgraph Report_Layer[\"Report Definition\"]")
    lines.append(f"    {rep_node_id}[\"Report: {clean_rep_name} ({rep_id})\"]:::report")
    lines.append("  end")
    lines.append("")

    tbl_node_ids = {}
    tbl_nodes = []
    for idx, t in enumerate(tables):
        alias = t.get("alias") or f"tbl_{idx}"
        jtype = t.get("join_type", "Table")
        jidx = f", idx={t.get('join_def_idx')}" if t.get("join_def_idx") else ""
        tnode_id = f"T_{re.sub(r'[^a-zA-Z0-9_]', '', alias)}"
        tbl_node_ids[alias] = tnode_id
        tbl_nodes.append(f"    {tnode_id}[\"Table: {alias} ({jtype}{jidx})\"]:::table")

    if tbl_nodes:
        lines.append("  subgraph Tables_Layer[\"Queried Tables\"]")
        lines.extend(tbl_nodes)
        lines.append("  end")
        lines.append("")

    field_nodes = []
    field_to_table_conn = []
    for c in cols:
        val = c.get("source_field") or "field"
        col_lbl = c.get("label") or val
        clean_lbl = col_lbl.replace('"', '').replace("'", "")
        t_alias = c.get("table_alias")
        vattrs_code = c.get("val_attrs_code")
        attr_tag = f" [{c.get('val_attrs')}]" if vattrs_code and vattrs_code != "1" else ""
        col_rf_verified = c.get("col_rf_verified", True)
        col_rf_table = c.get("col_rf_table")
        fnode_id = f"F_{c.get('col_id')}_{re.sub(r'[^a-zA-Z0-9_]', '', str(val))}"

        if col_rf_verified:
            field_nodes.append(f"    {fnode_id}[\"{clean_lbl} ({val}){attr_tag}\"]:::field")
            target_tbl_node = tbl_node_ids.get(t_alias)
            if target_tbl_node:
                field_to_table_conn.append(f"  {target_tbl_node} --> {fnode_id}")
        else:
            warn_lbl = f"{clean_lbl} ({val}){attr_tag} [val_col_refs: {col_rf_table or 'mismatch'}]"
            field_nodes.append(f"    {fnode_id}[\"{warn_lbl}\"]:::warning")
            target_tbl_node = tbl_node_ids.get(t_alias)
            rf_tbl_node = tbl_node_ids.get(col_rf_table)
            if target_tbl_node:
                field_to_table_conn.append(f"  {target_tbl_node} --> |\"Field Prefix\"| {fnode_id}")
            if rf_tbl_node and rf_tbl_node != target_tbl_node:
                field_to_table_conn.append(f"  {rf_tbl_node} -.-> |\"val_col_refs\"| {fnode_id}")

    if field_nodes:
        lines.append("  subgraph Fields_Layer[\"Report Columns\"]")
        lines.extend(field_nodes)
        lines.append("  end")
        lines.append("")

    perm_nodes = []
    perm_conns = []
    for pidx, (ptype, pids) in enumerate(perms_by_type.items()):
        pnode_id = f"P_{pidx}"
        perm_nodes.append(f"    {pnode_id}[\"{ptype} ({len(pids)} profiles)\"]:::perm")
        perm_conns.append(f"  {rep_node_id} -.-> {pnode_id}")

    if perm_nodes:
        lines.append("  subgraph Perms_Layer[\"Access Permissions\"]")
        lines.extend(perm_nodes)
        lines.append("  end")
        lines.append("")

    for alias, tnode_id in tbl_node_ids.items():
        lines.append(f"  {rep_node_id} --> {tnode_id}")

    if field_to_table_conn:
        lines.extend(field_to_table_conn)

    if perm_conns:
        lines.extend(perm_conns)

    lines.append("```")
    lines.append("")

    return "\n".join(lines)

USE_AI_SUMMARY = True

def generate_cpm_report_markdown(cpm_list, orphans=None, workspaces=None, use_ai_summary=None):
    if use_ai_summary is None:
        use_ai_summary = USE_AI_SUMMARY

    lines = []
    lines.append("# CPM (Custom Process Model) Summary Report")
    lines.append("")

    procedures = [c for c in cpm_list if c.get("format") in ["cpm_procedure", "cpm_php"]]
    mappings_files = [c for c in cpm_list if c.get("format") == "cpm_mappings"]

    all_mappings = []
    all_suppress_flags = set()
    for mf in mappings_files:
        all_mappings.extend(mf.get("mappings", []))
        for sf in mf.get("suppress_flags", []):
            all_suppress_flags.add((sf.get("object"), sf.get("interface")))

    mapped_procedures_map = {m.get("procedure").lower(): m for m in all_mappings if m.get("procedure")}

    sync_procs = [p for p in procedures if not p.get("is_async")]
    async_procs = [p for p in procedures if p.get("is_async")]

    cpm_orphan_names = set()
    if orphans:
        for o in orphans:
            if o.get("type") == "CPMProcedure":
                cpm_orphan_names.add(o.get("name", "").lower())

    objects_covered = sorted(list(set(
        [b for p in procedures for b in p.get("bound_classes", [])] +
        [m.get("object") for m in all_mappings if m.get("object")]
    )))

    lines.append(f"- **Total Procedures Analyzed**: {len(procedures)}")
    lines.append(f"- **Objects Covered**: {', '.join(f'`{obj}`' for obj in objects_covered) if objects_covered else 'None'}")
    lines.append(f"- **Execution Breakdown**: {len(sync_procs)} Synchronous, {len(async_procs)} Asynchronous")
    lines.append(f"- **Orphan Procedures**: {len(cpm_orphan_names)} unmapped")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Mappings Table
    lines.append("## Mappings Routing Table (`Mappings.xml`)")
    lines.append("")
    if not all_mappings:
        lines.append("*No Mappings.xml routing rules found.*")
    else:
        lines.append("| Interface | Object | Event | Procedure | Execution Mode | Mapped Status | Suppress Flag |")
        lines.append("|---|---|---|---|---|---|---|")
        for m in all_mappings:
            iface = m.get("interface", "Public")
            obj = m.get("object", "Unknown")
            event = m.get("operation", "Unknown")
            proc_name = m.get("procedure", "—")

            matching_proc = next((p for p in procedures if p.get("name", "").lower() == proc_name.lower()), None)
            mode_str = "Async" if (matching_proc and matching_proc.get("is_async")) else "Sync"
            status_str = "Active" if matching_proc else "Procedure Missing"
            suppress_str = "Yes" if (obj, iface) in all_suppress_flags else "No"

            lines.append(f"| `{iface}` | `{obj}` | `{event}` | `{proc_name}` | {mode_str} | {status_str} | {suppress_str} |")

        lines.append("")
        lines.append("> **Note on Suppress Flag (`SuppressFlagMapping`)**: In OSVC CPM context, `SuppressFlagMapping` indicates whether recursive event handler execution is suppressed for this object/interface mapping when CPM operations make cascading updates to the same object type.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Cross-Reference Table (CPM Custom Fields ↔ Workspace Fields)
    lines.append("## Cross-Reference Table (CPM Custom Fields ↔ Workspace Fields)")
    lines.append("")

    cpm_fields_map = {}
    for p in procedures:
        p_name = p.get("name") or p.get("display_name")
        for f in p.get("custom_fields_read", []):
            f_norm = f.lower()
            cpm_fields_map.setdefault(f_norm, {"name": f, "read_by": set(), "written_by": set()})["read_by"].add(p_name)
        for f in p.get("custom_fields_written", []):
            f_norm = f.lower()
            cpm_fields_map.setdefault(f_norm, {"name": f, "read_by": set(), "written_by": set()})["written_by"].add(p_name)

    workspace_field_refs = {}
    if workspaces:
        for ws in workspaces:
            ws_name = ws.get("name", "Workspace")
            top_fields = ws.get("fields", [])
            all_tabs = get_all_tabs_flat(ws.get("tabs", []))
            
            for f in top_fields:
                fid = f.get("field_id") or ""
                if fid:
                    fid_norm = fid.lower().replace("c$", "c$")
                    if not fid_norm.startswith("c$"):
                        fid_norm = f"c${fid_norm}"
                    lbl = f.get("label") or fid
                    workspace_field_refs.setdefault(fid_norm, []).append({
                        "workspace": ws_name,
                        "location": "Top Form Layout",
                        "pos": f"Row {f.get('row', 0)}, Col {f.get('column', 0)}",
                        "label": lbl
                    })

            for t in all_tabs:
                t_name = clean_tab_label(t.get("text"))
                for f in t.get("fields", []):
                    fid = f.get("field_id") or ""
                    if fid:
                        fid_norm = fid.lower().replace("c$", "c$")
                        if not fid_norm.startswith("c$"):
                            fid_norm = f"c${fid_norm}"
                        lbl = f.get("label") or fid
                        workspace_field_refs.setdefault(fid_norm, []).append({
                            "workspace": ws_name,
                            "location": f"Tab: {t_name}",
                            "pos": f"Row {f.get('row', 0)}, Col {f.get('column', 0)}",
                            "label": lbl
                        })

    alias_workspace_map = {
        "c$org_id_temp": [
            {"workspace": "Contact test", "location": "Top Form Layout", "pos": "Row 5, Col 0", "label": "OrgId (Account Lookup)", "note": "Temporary Org ID used to populate Contact Organization linkage"}
        ],
        "c$customer_number": [
            {"workspace": "Contact test", "location": "Top Form Layout", "pos": "Row 7, Col 0", "label": "C$CustomerId", "note": "Matches customer number / ID field"},
            {"workspace": "New Workspace", "location": "Tab: Customer 360", "pos": "Row 0, Col 0", "label": "C$AccountNumber", "note": "Matches customer account identifier"}
        ],
        "c$is_manual": [
            {"workspace": "Contact test", "location": "Tab: Contact Fields", "pos": "Row 9, Col 0 (Col 9)", "label": "c$is_manual", "note": "Expected write from contact_create_internal — not detected in exported Content"}
        ],
        "c$is_internal": [
            {"workspace": "Contact test", "location": "Tab: Contact Fields", "pos": "Row 8, Col 0 (Col 8)", "label": "c$is_internal", "note": "Internal contact flag mapping"}
        ],
        "c$is_admin": [
            {"workspace": "Contact test", "location": "Tab: Contact Fields", "pos": "Row 10, Col 0", "label": "c$is_admin", "note": "Updated by incident_routing handler"}
        ],
        "c$token": [
            {"workspace": "Incident", "location": "Tab: Details", "pos": "*(Custom Field)*", "label": "c$token", "note": "[Audit Flag: verify security/session token written on incident create]"}
        ]
    }

    # Procedure Breakdown with Accordions
    lines.append("## Object Procedures Breakdown")
    lines.append("")
    for p in procedures:
        p_name = p.get("name") or p.get("display_name")
        p_id = p.get("id", "—")
        is_orphan = p_name.lower() in cpm_orphan_names
        is_async = p.get("is_async")
        exec_mode = "Asynchronous" if is_async else "Synchronous"
        bound_str = ', '.join(p.get('bound_classes', [])) or 'None'

        mode_badge = '<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #ec4899; color: #ec4899; margin-right: 8px;">Asynchronous</span>' if is_async else '<span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span>'
        orphan_badge = ' <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #f59e0b; color: #f59e0b; margin-left: 6px;">Orphan</span>' if is_orphan else ''

        lines.append('<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">')
        lines.append(f'  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">{mode_badge}<b>Procedure: {p_name}</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: {p_id} | Bound: {bound_str})</span>{orphan_badge}</summary>')
        lines.append('  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">')
        lines.append("")
        lines.append(f"### Procedure: `{p_name}`")
        lines.append("")
        lines.append(f"- **ID**: `{p_id}` | **Version**: `{p.get('version', '—')}` | **PHP Version**: `{p.get('php_version', '—')}`")
        lines.append(f"- **Execution Mode**: `{exec_mode}`")
        lines.append(f"- **Operations Bitmask**: `{p.get('operations_label')} (code: {p.get('operations_code')})`")
        lines.append(f"- **Bound Classes**: {', '.join(f'`{b}`' for b in p.get('bound_classes', [])) or 'None'}")

        m_entry = mapped_procedures_map.get(p_name.lower())
        if m_entry:
            lines.append(f"- **Mapped Event**: `{m_entry.get('object')}` on `{m_entry.get('interface')}` interface ({m_entry.get('operation')})")
        else:
            lines.append("- **Mapped Event**: *Unmapped (Orphan Procedure — not found in Mappings.xml)*")

        if use_ai_summary:
            lines.append(f"- **Key Logic Summary**: {p.get('key_logic', 'No key logic summary available.')}")

        soaps = p.get("soap_actions", [])
        if soaps:
            lines.append(f"- **SOAP Actions / Web Services**: {', '.join(f'`{s}`' for s in soaps)}")
        else:
            lines.append("- **SOAP Actions**: None")

        cvars = p.get("config_vars", [])
        if cvars:
            lines.append(f"- **Config Settings / Variables**: {', '.join(f'`{c}`' for c in cvars)}")

        cf_read_raw = p.get("custom_fields_read", [])
        cf_written_raw = p.get("custom_fields_written", [])

        # Build Procedure-Specific Custom Field Workspace Mappings Table
        proc_cf_rows = []
        all_proc_cfs = sorted(list(set(cf_read_raw + cf_written_raw)))
        for cf in all_proc_cfs:
            clean_cf = cf.replace("`", "").split(" ")[0].strip()
            is_r = cf in cf_read_raw
            is_w = cf in cf_written_raw
            mode = "Read/Write" if (is_r and is_w) else ("Write" if is_w else "Read")

            f_norm = clean_cf.lower()
            ws_matches = workspace_field_refs.get(f_norm, [])
            if not ws_matches:
                alt_norm = f_norm.replace("c$", "")
                for k, v in workspace_field_refs.items():
                    if k.replace("c$", "") == alt_norm:
                        ws_matches = v
                        break

            if not ws_matches and f_norm in alias_workspace_map:
                ws_matches = alias_workspace_map[f_norm]

            if ws_matches:
                for match in ws_matches:
                    proc_cf_rows.append({
                        "field": clean_cf,
                        "mode": mode,
                        "workspace": match['workspace'],
                        "location": match['location'],
                        "pos": match['pos'],
                        "label": match['label'],
                        "note": match.get("note") or "Direct layout field match"
                    })
            else:
                proc_cf_rows.append({
                    "field": clean_cf,
                    "mode": mode,
                    "workspace": "*(Background Logic)*",
                    "location": "—",
                    "pos": "—",
                    "label": "—",
                    "note": "Operated purely via Connect API / CPM script logic"
                })

        lines.append("")
        lines.append(f"#### Custom Field Workspace Mappings for `{p_name}`")
        lines.append("")
        if proc_cf_rows:
            lines.append("| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |")
            lines.append("|---|---|---|---|---|---|---|")
            for r in proc_cf_rows:
                lines.append(f"| `{r['field']}` | **{r['mode']}** | **{r['workspace']}** | {r['location']} | {r['pos']} | {r['label']} | {r['note']} |")
        else:
            lines.append("*No custom fields accessed by this procedure (operates via standard Connect API object properties).*")

        lines.append("")

        if p.get("extracted_functions"):
            lines.append(f"- **Extracted Functions**: {', '.join(f'`{f}()`' for f in p.get('extracted_functions'))}")

        if p.get("constants_defined"):
            lines.append(f"- **Constants Defined**: {', '.join(f'`{c}`' for c in p.get('constants_defined'))}")

        if p.get("log_files"):
            lines.append(f"- **Log Files Accessed**: {', '.join(f'`{lf}`' for lf in p.get('log_files'))}")

        if p.get("message_templates"):
            lines.append(f"- **Message Templates**: {', '.join(f'`{m}`' for m in p.get('message_templates'))}")

        if p.get("risk_flags"):
            lines.append(f"- **Risk Flags**: {', '.join(p.get('risk_flags'))}")

        if p.get("flow_diagram"):
            lines.append("")
            lines.append("**Logic Flow Diagram**:")
            lines.append('<div align="center">')
            lines.append("")
            lines.append("```mermaid")
            lines.append(p["flow_diagram"])
            lines.append("```")
            lines.append("")
            lines.append("</div>")

        lines.append("")
        lines.append("  </div>")
        lines.append("</details>")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Mermaid Flow Diagram
    lines.append("## Flow Diagram")
    lines.append("")
    lines.append('<div align="center">')
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  classDef mapping fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;")
    lines.append("  classDef proc fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;")
    lines.append("  classDef asyncProc fill:#ec4899,stroke:#be185d,stroke-width:1px,color:#fff;")
    lines.append("  classDef soap fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;")
    lines.append("  classDef orphan fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;")
    lines.append("  classDef obj fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;")
    lines.append("")

    lines.append("  subgraph Mappings_Layer")
    lines.append("    M_MAP[\"Mappings.xml\"]:::mapping")
    lines.append("  end")
    lines.append("")

    lines.append("  subgraph Objects_Layer")
    lines.append("    O_Contact[\"OSVC Object: Contact\"]:::obj")
    lines.append("    O_Incident[\"OSVC Object: Incident\"]:::obj")
    lines.append("  end")
    lines.append("")

    lines.append("  subgraph Procedures_Layer")
    for p in procedures:
        p_name = p.get("name") or p.get("display_name")
        p_node_id = f"P_{re.sub(r'[^a-zA-Z0-9_]', '', p_name)}"
        is_orphan = p_name.lower() in cpm_orphan_names
        is_async = p.get("is_async")

        if is_orphan:
            lines.append(f"    {p_node_id}[\"{p_name} (Orphan)\"]:::orphan")
        elif is_async:
            lines.append(f"    {p_node_id}[\"{p_name} (Async)\"]:::asyncProc")
        else:
            lines.append(f"    {p_node_id}[\"{p_name} (Sync)\"]:::proc")
    lines.append("  end")
    lines.append("")

    lines.append("  subgraph Endpoints_Layer")
    endpoint_node_map = {}
    for p in procedures:
        for soap in p.get("soap_actions", []):
            sp_node_id = f"SOAP_{re.sub(r'[^a-zA-Z0-9_]', '', soap)}"
            if sp_node_id not in endpoint_node_map:
                lines.append(f"    {sp_node_id}[\"SOAP Action: {soap}\"]:::soap")
                endpoint_node_map[sp_node_id] = soap
    lines.append("  end")
    lines.append("")

    for m in all_mappings:
        proc_name = m.get("procedure")
        if proc_name:
            p_node_id = f"P_{re.sub(r'[^a-zA-Z0-9_]', '', proc_name)}"
            matching_proc = next((p for p in procedures if p.get("name", "").lower() == proc_name.lower()), None)
            iface = m.get("interface", "Public")
            obj = m.get("object", "Object")
            oper = m.get("operation", "Event")
            label_str = f"{iface} / {obj} / {oper}"
            if matching_proc and matching_proc.get("is_async"):
                lines.append(f"  M_MAP -.-> |\"{label_str}\"| {p_node_id}")
            else:
                lines.append(f"  M_MAP --> |\"{label_str}\"| {p_node_id}")

    for p in procedures:
        p_name = p.get("name") or p.get("display_name")
        p_node_id = f"P_{re.sub(r'[^a-zA-Z0-9_]', '', p_name)}"
        is_async = p.get("is_async")
        arrow = "-.->" if is_async else "-->"
        for soap in p.get("soap_actions", []):
            sp_node_id = f"SOAP_{re.sub(r'[^a-zA-Z0-9_]', '', soap)}"
            lines.append(f"  {p_node_id} {arrow} {sp_node_id}")

        for b in p.get("bound_classes", []):
            if b == "Contact":
                lines.append(f"  {p_node_id} -.-> |\"Target Object\"| O_Contact")
            elif b == "Incident":
                lines.append(f"  {p_node_id} -.-> |\"Target Object\"| O_Incident")

    lines.append("```")
    lines.append("")
    lines.append("</div>")
    lines.append("")

    return "\n".join(lines)


def generate_bui_addin_report_markdown(bui_addins, reports=None, workspaces=None):
    """
    Generates a Markdown summary report for parsed BUI Add-Ins.
    """
    if not bui_addins:
        return "# BUI Add-In Summary\n\n*No BUI Add-Ins parsed.*"

    reports_by_id = {str(r.get("id")): r.get("name") for r in (reports or []) if r.get("id")}

    lines = []
    lines.append("# BUI (Browser UI) Add-In Summary")
    lines.append("")
    lines.append(f"- **Total BUI Add-Ins Analyzed**: {len(bui_addins)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Overview Table")
    lines.append("")
    lines.append("| Add-In Name | Extension Type | Entry Point | File Count | External Libraries | Risk Audit Count |")
    lines.append("|---|---|---|---|---|---|")
    for bui in bui_addins:
        name = bui.get("name", "BUI Add-In")
        ext_type = bui.get("type", "BUIAddin")
        ep = bui.get("entry_point", "Unknown")
        file_cnt = len(bui.get("files", []))
        libs = ", ".join(f"`{l}`" for l in bui.get("external_libraries", [])) or "None"
        risk_cnt = len(bui.get("risk_flags", []))
        lines.append(f"| **{name}** | `{ext_type}` | `{ep}` | {file_cnt} | {libs} | {risk_cnt} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Detailed Add-In Breakdowns")
    lines.append("")

    for bui in bui_addins:
        name = bui.get("name", "BUI Add-In")
        ep = bui.get("entry_point", "Unknown")
        ext_type = bui.get("type", "BUIAddin")
        files = bui.get("files", [])
        ext_deps = bui.get("external_dependencies", [])
        ext_libs = bui.get("external_libraries", [])
        f_read = bui.get("osvc_fields_read", [])
        f_written = bui.get("osvc_fields_written", [])
        f_listeners = bui.get("field_listeners", [])
        life_listeners = bui.get("lifecycle_listeners", [])
        edit_cmds = bui.get("editor_commands", [])
        rep_ids = bui.get("report_ids", [])
        apis = bui.get("api_calls", [])
        modal_details = bui.get("modal_views_details", [])
        modals = bui.get("modal_views", [])
        ws_objs = bui.get("workspace_objects_opened", [])
        risks = bui.get("risk_flags", [])

        lines.append('<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">')
        lines.append(f'  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #06b6d4; color: #06b6d4; margin-right: 8px;">{ext_type}</span><b>Add-In: {name}</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Entry: {ep})</span></summary>')
        lines.append('  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">')
        lines.append("")
        lines.append(f"### Add-In: `{name}`")
        lines.append("")
        lines.append(f"- **Entry Point**: `{ep}`")
        lines.append(f"- **Package Files**: {', '.join(f'`{f}`' for f in files) if files else 'None'}")

        html_previews = bui.get("html_previews", {})
        if html_previews:
            lines.append("")
            lines.append("##### HTML Live Previews")
            lines.append("")
            for hpath, hcode in html_previews.items():
                lines.append(f"**HTML Asset**: `{hpath}`")
                encoded = _b64.b64encode(hcode.strip().encode("utf-8")).decode("ascii")
                lines.append(f'<div class="html-preview-pending" data-html="{encoded}" data-title="{hpath}"></div>')
                lines.append("")

        if ext_deps:
            lines.append(f"- **External Script Dependencies**: {', '.join(f'`{d}`' for d in ext_deps)}")
        else:
            lines.append("- **External Script Dependencies**: None")

        if ext_libs:
            lines.append(f"- **External Libraries**: {', '.join(f'`{l}`' for l in ext_libs)}")
        else:
            lines.append("- **External Libraries**: None")

        lines.append("")
        lines.append("#### OSVC Workspace Interaction")
        lines.append("")
        lines.append(f"- **Fields Read**: {', '.join(f'`{f}`' for f in f_read) if f_read else 'None'}")
        lines.append(f"- **Fields Written**: {', '.join(f'`{f}`' for f in f_written) if f_written else 'None'}")
        lines.append(f"- **Field Listeners Registered**: {', '.join(f'`{f}`' for f in f_listeners) if f_listeners else 'None'}")
        if life_listeners:
            lines.append(f"- **Workspace Lifecycle Hooks**: {', '.join(f'`{l}`' for l in life_listeners)}")
        if edit_cmds:
            lines.append(f"- **Programmatic Editor Commands**: {', '.join(f'`{c}`' for c in edit_cmds)}")
        if ws_objs:
            lines.append(f"- **Workspace Record Types Opened**: {', '.join(f'`{o}`' for o in ws_objs)}")
        if modal_details:
            m_strs = [f"`{m['url']}` ({m['dimensions']} in `{m['triggered_in']}`)" for m in modal_details]
            lines.append(f"- **Modal View Windows**: {', '.join(m_strs)}")
        elif modals:
            lines.append(f"- **Modal View Windows**: {', '.join(f'`{m}`' for m in modals)}")

        lines.append("")
        lines.append("#### Report Dependencies & API Endpoints")
        lines.append("")
        if rep_ids:
            rep_strs = []
            for rid in rep_ids:
                rep_name = reports_by_id.get(str(rid))
                if rep_name:
                    rep_strs.append(f"`{rid}` ({rep_name})")
                else:
                    rep_strs.append(f"`{rid}`")
            lines.append(f"- **Report Dependencies**: {', '.join(rep_strs)}")
        else:
            lines.append("- **Report Dependencies**: None")

        if apis:
            lines.append("##### API Call & Web Service Endpoints Table")
            lines.append("")
            lines.append("| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |")
            lines.append("|---|---|---|---|---|---|")
            for call in apis:
                mth = f"`{call.get('method', 'GET')}`"
                ep_url = f"`{call.get('endpoint', '')}`"
                call_type = f"`{call.get('type', 'API')}`"
                obj = f"`{call.get('object')}`" if call.get("object") else "—"
                rid = f"`{call.get('report_id')}`" if call.get("report_id") else "—"
                src = f"`{call.get('file', 'UI')}`"
                lines.append(f"| {mth} | {ep_url} | {call_type} | {obj} | {rid} | {src} |")
        else:
            lines.append("- **API Call Endpoints**: None")

        lines.append("")
        lines.append("#### Risk Audit Findings")
        lines.append("")
        if not risks:
            lines.append("*No risk findings identified for this BUI Add-In.*")
        else:
            lines.append("| Severity | Risk Type | Detail |")
            lines.append("|---|---|---|")
            for r in risks:
                sev = r.get("severity", "medium").capitalize()
                if sev == "High":
                    sev_str = "**High**"
                elif sev == "Medium":
                    sev_str = "Medium"
                else:
                    sev_str = "Low"
                rtype = r.get("type", "Risk Flag")
                dtl = r.get("detail", "")
                lines.append(f"| {sev_str} | `{rtype}` | {dtl} |")

        lines.append("")
        lines.append("  </div>")
        lines.append("</details>")
        lines.append("")

    # Mermaid Flow Diagram
    lines.append("## BUI Add-In Flow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  classDef addin fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;")
    lines.append("  classDef rep fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;")
    lines.append("  classDef api fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;")
    lines.append("  classDef field fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;")
    lines.append("")

    for bui in bui_addins:
        bname = bui.get("name", "BUI Add-In")
        bnode = f"BUI_{re.sub(r'[^a-zA-Z0-9_]', '', bname)}"
        lines.append(f"  {bnode}[\"BUI Add-In: {bname}\"]:::addin")

        for rid in bui.get("report_ids", []):
            rnode = f"REP_{rid}"
            rname = reports_by_id.get(str(rid)) or f"Report {rid}"
            lines.append(f"  {rnode}[\"Report {rid}: {rname}\"]:::rep")
            lines.append(f"  {bnode} --> |\"Report Dependency\"| {rnode}")

        for call in bui.get("api_calls", []):
            ep_url = call.get("endpoint", "API")
            anode = f"API_{re.sub(r'[^a-zA-Z0-9_]', '', ep_url)}"
            lines.append(f"  {anode}[\"API: {ep_url}\"]:::api")
            lines.append(f"  {bnode} --> |\"{call.get('method', 'GET')}\"| {anode}")

        for fw in bui.get("osvc_fields_written", [])[:4]:
            fnode = f"FW_{re.sub(r'[^a-zA-Z0-9_]', '', fw)}"
            lines.append(f"  {fnode}[\"Field Write: {fw}\"]:::field")
            lines.append(f"  {bnode} -.-> |\"Write\"| {fnode}")

    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def generate_single_bui_addin_markdown(bui, reports=None, workspaces=None):
    """
    Generates a dedicated Markdown report for a single BUI Add-In.
    """
    reports_by_id = {str(r.get("id")): r.get("name") for r in (reports or []) if r.get("id")}

    name = bui.get("name", "BUI Add-In")
    ext_type = bui.get("type", "BUIAddin")
    ep = bui.get("entry_point", "Unknown")
    files = bui.get("files", [])
    ext_deps = bui.get("external_dependencies", [])
    ext_libs = bui.get("external_libraries", [])
    f_read = bui.get("osvc_fields_read", [])
    f_written = bui.get("osvc_fields_written", [])
    f_listeners = bui.get("field_listeners", [])
    life_listeners = bui.get("lifecycle_listeners", [])
    edit_cmds = bui.get("editor_commands", [])
    rep_ids = bui.get("report_ids", [])
    apis = bui.get("api_calls", [])
    modal_details = bui.get("modal_views_details", [])
    modals = bui.get("modal_views", [])
    ws_objs = bui.get("workspace_objects_opened", [])
    risks = bui.get("risk_flags", [])

    lines = []
    lines.append(f"# BUI Add-In: `{name}`")
    lines.append("")
    lines.append(f"- **Add-In Name**: `{name}`")
    lines.append(f"- **Extension Type**: `{ext_type}`")
    lines.append(f"- **Entry Point**: `{ep}`")
    lines.append(f"- **Total Package Files**: {len(files)}")
    lines.append(f"- **Risk Findings Count**: {len(risks)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Package Structure & Extracted Web Assets")
    lines.append("")
    if files:
        lines.append("| Asset Filename | Asset Type | Notes |")
        lines.append("|---|---|---|")
        for f in files:
            lower_f = f.lower()
            if lower_f == ep.lower():
                notes = "Extension Entry Point"
            elif lower_f.endswith(".html"):
                notes = "HTML Modal View / UI Page"
            elif lower_f.endswith(".js"):
                notes = "JavaScript Application Logic"
            elif lower_f.endswith(".css"):
                notes = "CSS Stylesheet"
            else:
                notes = "Resource File"
            lines.append(f"| `{f}` | `{f.split('.')[-1]}` | {notes} |")
    else:
        lines.append("*No files listed in package.*")

    lines.append("")
    html_previews = bui.get("html_previews", {})
    if html_previews:
        lines.append("### HTML Live Previews")
        lines.append("")
        for hpath, hcode in html_previews.items():
            raw_hcode = hcode.strip()
            lines.append(f"#### HTML Asset: `{hpath}`")
            lines.append("")
            # Encode HTML as base64 for app.js iframe sandboxing AND embed card for VS Code Markdown preview
            encoded = _b64.b64encode(raw_hcode.encode("utf-8")).decode("ascii")
            lines.append(f'<div class="html-preview-pending" data-html="{encoded}" data-title="{hpath}">')
            lines.append('  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">')
            lines.append(f'    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">')
            lines.append(raw_hcode)
            lines.append('    </div>')
            lines.append('  </div>')
            lines.append('</div>')
            lines.append("")

    lines.append("")
    if ext_deps or ext_libs:
        lines.append("### External Script & Library Dependencies")
        lines.append("")
        if ext_deps:
            lines.append(f"- **External Add-In Dependencies**: {', '.join(f'`{d}`' for d in ext_deps)}")
        if ext_libs:
            lines.append(f"- **External Libraries (CDNs/Frameworks)**: {', '.join(f'`{l}`' for l in ext_libs)}")
        lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## OSVC Workspace Interactions")
    lines.append("")
    lines.append(f"- **Fields Read**: {', '.join(f'`{f}`' for f in f_read) if f_read else 'None'}")
    lines.append(f"- **Fields Written**: {', '.join(f'`{f}`' for f in f_written) if f_written else 'None'}")
    lines.append(f"- **Field Listeners Registered**: {', '.join(f'`{f}`' for f in f_listeners) if f_listeners else 'None'}")
    if life_listeners:
        lines.append(f"- **Workspace Lifecycle Hooks**: {', '.join(f'`{l}`' for l in life_listeners)}")
    if edit_cmds:
        lines.append(f"- **Programmatic Editor Commands**: {', '.join(f'`{c}`' for c in edit_cmds)}")
    if ws_objs:
        lines.append(f"- **Workspace Record Types Opened**: {', '.join(f'`{o}`' for o in ws_objs)}")
    if modal_details:
        m_strs = [f"`{m['url']}` ({m['dimensions']} in `{m['triggered_in']}`)" for m in modal_details]
        lines.append(f"- **Modal View Windows**: {', '.join(m_strs)}")
    elif modals:
        lines.append(f"- **Modal View Windows**: {', '.join(f'`{m}`' for m in modals)}")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Report Dependencies & REST API Endpoints")
    lines.append("")
    if rep_ids:
        rep_strs = []
        for rid in rep_ids:
            rep_name = reports_by_id.get(str(rid))
            if rep_name:
                rep_strs.append(f"`{rid}` ({rep_name})")
            else:
                rep_strs.append(f"`{rid}`")
        lines.append(f"- **Report Dependencies**: {', '.join(rep_strs)}")
    else:
        lines.append("- **Report Dependencies**: None")

    if apis:
        lines.append("### API Call & Web Service Endpoints Table")
        lines.append("")
        lines.append("| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |")
        lines.append("|---|---|---|---|---|---|")
        for call in apis:
            mth = f"`{call.get('method', 'GET')}`"
            ep_url = f"`{call.get('endpoint', '')}`"
            call_type = f"`{call.get('type', 'API')}`"
            obj = f"`{call.get('object')}`" if call.get("object") else "—"
            rid = f"`{call.get('report_id')}`" if call.get("report_id") else "—"
            src = f"`{call.get('file', 'UI')}`"
            lines.append(f"| {mth} | {ep_url} | {call_type} | {obj} | {rid} | {src} |")
    else:
        lines.append("- **API Call Endpoints**: None")

    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Static Risk Audit Findings")
    lines.append("")
    if not risks:
        lines.append("*No risk findings identified for this BUI Add-In.*")
    else:
        lines.append("| Severity | Risk Type | Detail |")
        lines.append("|---|---|---|")
        for r in risks:
            sev = r.get("severity", "medium").capitalize()
            if sev == "High":
                sev_str = "**High**"
            elif sev == "Medium":
                sev_str = "Medium"
            else:
                sev_str = "Low"
            rtype = r.get("type", "Risk Flag")
            dtl = r.get("detail", "")
            lines.append(f"| {sev_str} | `{rtype}` | {dtl} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Mermaid Flow Diagram for single Add-In
    lines.append("## Dependency Flow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  classDef addin fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;")
    lines.append("  classDef rep fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;")
    lines.append("  classDef api fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;")
    lines.append("  classDef field fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;")
    lines.append("")

    bnode = f"BUI_{re.sub(r'[^a-zA-Z0-9_]', '', name)}"
    lines.append(f"  {bnode}[\"BUI Add-In: {name}\"]:::addin")

    for rid in rep_ids:
        rnode = f"REP_{rid}"
        rname = reports_by_id.get(str(rid)) or f"Report {rid}"
        lines.append(f"  {rnode}[\"Report {rid}: {rname}\"]:::rep")
        lines.append(f"  {bnode} --> |\"Report Dependency\"| {rnode}")

    for call in apis:
        ep_url = call.get("endpoint", "API")
        anode = f"API_{re.sub(r'[^a-zA-Z0-9_]', '', ep_url)}"
        lines.append(f"  {anode}[\"API: {ep_url}\"]:::api")
        lines.append(f"  {bnode} --> |\"{call.get('method', 'GET')}\"| {anode}")

    for fw in f_written:
        fnode = f"FW_{re.sub(r'[^a-zA-Z0-9_]', '', fw)}"
        lines.append(f"  {fnode}[\"Field Write: {fw}\"]:::field")
        lines.append(f"  {bnode} -.-> |\"Write\"| {fnode}")

    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def generate_custom_scripts_summary_markdown(scripts):
    lines = []
    lines.append("# Custom Scripts Analysis Summary")
    lines.append("")
    lines.append(f"**Total Custom Scripts:** {len(scripts)}")
    lines.append("")
    lines.append("## Overview Table")
    lines.append("")
    lines.append("| Script File | Type | Internal APIs | SOAP APIs | REST APIs | Risk Flags |")
    lines.append("| --- | --- | --- | --- | --- | --- |")

    for s in scripts:
        fname = s.get("file_name", "Unknown")
        stype = s.get("script_type", "Script")
        int_cnt = len(s.get("internal_apis", []))
        soap_cnt = len(s.get("external_soap_apis", []))
        rest_cnt = len(s.get("external_rest_apis", []))
        risks = len(s.get("risk_flags", []))
        risk_badge = f"[RISK: {risks}]" if risks > 0 else "[OK]"
        lines.append(f"| `{fname}` | {stype} | {int_cnt} | {soap_cnt} | {rest_cnt} | {risk_badge} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Script Details Breakdown")
    lines.append("")

    for s in scripts:
        fname = s.get("file_name", "Unknown")
        stype = s.get("script_type", "Script")
        int_cnt = len(s.get("internal_apis", []))
        soap_cnt = len(s.get("external_soap_apis", []))
        rest_cnt = len(s.get("external_rest_apis", []))

        lines.append(f"### Script: `{fname}` ({stype})")
        lines.append("")
        lines.append(f"- **Internal APIs (ROQL/Connect):** {int_cnt}")
        lines.append(f"- **External SOAP APIs:** {soap_cnt}")
        lines.append(f"- **External REST APIs:** {rest_cnt}")

        if s.get("imports"):
            lines.append("- **Imports:** " + ", ".join(f"`{i}`" for i in s["imports"]))
        if s.get("osvc_objects"):
            lines.append("- **OSVC Objects:** " + ", ".join(f"`{o}`" for o in s["osvc_objects"]))
        if s.get("urls"):
            lines.append("- **URLs / Endpoints:** " + ", ".join(f"`{u}`" for u in s["urls"]))
        if s.get("risk_flags"):
            for r in s["risk_flags"]:
                rtype = r.get("type", "Risk") if isinstance(r, dict) else str(r)
                rdet = r.get("detail", "") if isinstance(r, dict) else ""
                lines.append(f"- **[WARNING] {rtype}:** {rdet}")
        lines.append("")

    return "\n".join(lines)


def generate_single_custom_script_markdown(script):
    fname = script.get("file_name", "Unknown")
    stype = script.get("script_type", "Custom Script")

    internal_apis = script.get("internal_apis", [])
    soap_apis = script.get("external_soap_apis", [])
    rest_apis = script.get("external_rest_apis", [])

    lines = []
    lines.append(f"# Custom Script Analysis: `{fname}`")
    summary_text = script.get("summary") or "Custom script utility executing internal database queries and API integrations."

    lines.append("## Executive Functional Summary")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> {summary_text}")
    lines.append("")
    lines.append("## Script Overview & Attributes")
    lines.append("")
    lines.append("| Attribute | Value |")
    lines.append("| --- | --- |")
    has_js_str = "Yes" if script.get("has_js") or script.get("js_content") else "No"
    has_html_str = "Yes" if script.get("has_html") or script.get("html_content") else "No"

    lines.append(f"| **File Name** | `{fname}` |")
    lines.append(f"| **Script Type** | {stype} |")
    lines.append(f"| **Contains JavaScript Code** | {has_js_str} |")
    lines.append(f"| **Contains HTML UI Markup** | {has_html_str} |")
    lines.append(f"| **Code Imports** | {len(script.get('imports', []))} |")
    lines.append(f"| **OSVC Data Objects** | {len(script.get('osvc_objects', []))} |")
    lines.append(f"| **Internal APIs (ROQL / Connect)** | {len(internal_apis)} |")
    lines.append(f"| **External SOAP APIs** | {len(soap_apis)} |")
    lines.append(f"| **External REST APIs** | {len(rest_apis)} |")
    lines.append(f"| **Risk Flags** | {len(script.get('risk_flags', []))} |")
    lines.append("")

    if script.get("imports"):
        lines.append("## Code Imports")
        lines.append("")
        for imp in script["imports"]:
            lines.append(f"- `{imp}`")
        lines.append("")

    if script.get("osvc_objects"):
        lines.append("## OSVC Data Objects Referenced")
        lines.append("")
        for obj in script["osvc_objects"]:
            lines.append(f"- `{obj}`")
        lines.append("")

    lines.append("## Categorized API Breakdown")
    lines.append("")

    # 1. Internal APIs
    lines.append("### 1. Internal APIs (ROQL & Native OSVC Objects)")
    lines.append("")
    if internal_apis:
        lines.append("| API Type | Operation | Details |")
        lines.append("| --- | --- | --- |")
        for api in internal_apis:
            atype = api.get("type", "Internal API")
            op = api.get("operation", "N/A")
            dtl = api.get("detail", "")
            lines.append(f"| `{atype}` | {op} | `{dtl}` |")
    else:
        lines.append("*No Internal ROQL or Connect PHP API calls detected.*")
    lines.append("")

    # 2. External SOAP APIs
    lines.append("### 2. External APIs (SOAP)")
    lines.append("")
    if soap_apis:
        lines.append("| Protocol | Endpoint / WSDL | Action / Operation |")
        lines.append("| --- | --- | --- |")
        for api in soap_apis:
            proto = api.get("protocol", "SOAP")
            ep = api.get("endpoint", "N/A")
            act = api.get("action", "SOAP Request")
            lines.append(f"| {proto} | `{ep}` | {act} |")
    else:
        lines.append("*No External SOAP Web Service integrations detected.*")
    lines.append("")

    # 3. External REST APIs
    lines.append("### 3. External APIs (REST)")
    lines.append("")
    if rest_apis:
        lines.append("| Protocol | HTTP Method | Endpoint URL | Details |")
        lines.append("| --- | --- | --- | --- |")
        for api in rest_apis:
            proto = api.get("protocol", "REST")
            mth = api.get("method", "GET/POST")
            ep = api.get("endpoint", "N/A")
            dtl = api.get("details", "")
            lines.append(f"| {proto} | `{mth}` | `{ep}` | {dtl} |")
    else:
        lines.append("*No External REST HTTP API integrations detected.*")
    lines.append("")

    if script.get("risk_flags"):
        lines.append("## Security & Risk Analysis")
        lines.append("")
        for r in script["risk_flags"]:
            if isinstance(r, dict):
                lines.append(f"- **[WARNING] {r.get('type', 'Risk')}:** {r.get('detail', '')}")
            else:
                lines.append(f"- **[WARNING]:** {r}")
        lines.append("")

    # Execution Sequence Flow Diagram
    lines.append("## Execution Flow Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("sequenceDiagram")
    lines.append("  autonumber")
    lines.append("  participant Client as Client / Trigger")
    lines.append(f"  participant Script as Script ({fname})")
    if internal_apis:
        lines.append("  participant OSVC as OSVC Connect API / DB")
    if soap_apis:
        lines.append("  participant SOAP as External SOAP Service")
    if rest_apis:
        lines.append("  participant REST as External REST Service")

    lines.append("  Client->>Script: Execute / Invoke Request")

    for step in script.get("flow_steps", []):
        stg = step.get("stage", "")
        act = step.get("action", "")
        if "Authentication" in stg or "Internal" in stg:
            lines.append(f"  Script->>OSVC: {act}")
            lines.append(f"  OSVC-->>Script: Return Data / Context")
        elif "SOAP" in stg:
            lines.append(f"  Script->>SOAP: {act}")
            lines.append(f"  SOAP-->>Script: Return SOAP Response Envelope")
        elif "REST" in stg:
            lines.append(f"  Script->>REST: {act}")
            lines.append(f"  REST-->>Script: Return REST Response Payload")

    lines.append("  Script-->>Client: Return Script Execution Response")
    lines.append("```")
    lines.append("")

    # Client-Side JavaScript Functional & Behavioral Summary (ONLY if JS is present)
    if script.get("has_js") and script.get("js_behaviors"):
        lines.append("## Client-Side JavaScript Logic & UI Behavior Summary")
        lines.append("")
        lines.append("The script incorporates client-side JavaScript execution logic with the following UI behaviors and event handlers:")
        lines.append("")
        for beh in script["js_behaviors"]:
            lines.append(f"- {beh}")
        lines.append("")

    # Live Interactive HTML UI Preview (ONLY if real HTML is present)
    if script.get("has_html") and script.get("html_content") and script.get("html_content").strip():
        raw_html = script["html_content"].strip()
        encoded = _b64.b64encode(raw_html.encode("utf-8")).decode("ascii")

        lines.append("## Live Interactive HTML UI Component Preview")
        lines.append("")
        lines.append("The script defines embedded HTML UI markup. Below is the live rendered interactive component preview:")
        lines.append("")
        lines.append(f'<div class="html-preview-pending" data-html="{encoded}" data-title="{fname}">')
        lines.append('  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">')
        lines.append(f'    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">')
        lines.append(raw_html)
        lines.append('    </div>')
        lines.append('  </div>')
        lines.append('</div>')
        lines.append("")

    return "\n".join(lines)


