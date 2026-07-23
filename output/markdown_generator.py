import os
import re
import urllib.parse

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

def get_field_notes(field_id, label, default_phone_type):
    if not field_id:
        return label or "Form field"
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
    if clean_label:
        std_name = standards.get(field_id)
        if std_name and clean_label.lower() != std_name.lower():
            notes = f'Relabeled as **"{clean_label}"**'
            if default_phone_type == "1":
                notes += ", default type 1"
            return notes
    if field_id.startswith("C$"):
        field_name = field_id[2:]
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', field_name)
        desc = " ".join(words).lower()
        return f"Custom field — {desc}"
    return standards.get(field_id, clean_label or "Form field")

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
    col_str = f"**{col_count}-column table layout**" if col_count else "**table layout**"
    
    top_fields = ws.get("fields", [])
    top_menus = ws.get("menus", [])
    all_tabs_flat = get_all_tabs_flat(ws.get("tabs", []))
    
    if top_fields or top_menus:
        lines.append(f"The workspace has a {col_str} ({ws.get('row_count')} rows × {col_count} columns):")
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
        if is_subtab:
            lines.append(f"#### Sub-Tab: {tab_name}")
        else:
            lines.append(f"### Tab: {tab_name}")
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
                        notes = get_field_notes(field_id, f.get("label"), f.get("default_phone_type"))
                        if rep_id: notes += f" (Lookup → Report **{rep_id}**)"
                        constraints = []
                        for opt_key, opt_label in [("readonly_option","ReadOnly"),("hidden_option","Hidden"),("required_option","Required")]:
                            c_str = format_profile_constraint(f.get(opt_key))
                            if c_str: constraints.append(f"{opt_label}: {c_str}")
                        if constraints: notes += f" — *{'; '.join(constraints)}*"
                        if not field_id: field_label = "⚠ No FieldId"
                        elif not str(field_id).strip(): field_label = "⚠ Empty FieldId"
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
                    notes = get_field_notes(field_id, f.get("label"), f.get("default_phone_type"))
                    if rep_id: notes += f" (Lookup pointing to Report **{rep_id}**)"
                    constraints = []
                    for opt_key, opt_label in [("readonly_option","ReadOnly"),("hidden_option","Hidden"),("required_option","Required")]:
                        c_str = format_profile_constraint(f.get(opt_key))
                        if c_str: constraints.append(f"{opt_label}: {c_str}")
                    if constraints: notes += f" — *Constraints: {'; '.join(constraints)}*"
                    if not field_id: field_label = "⚠ No FieldId"
                    elif not str(field_id).strip(): field_label = "⚠ Empty FieldId"
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
                lines.append(f"> 📂 **Nested TabSet** (Row {ts.get('row', 0)}, Col {ts.get('column', 0)}) — {len(sub_tabs)} Sub-Tabs: {sub_tab_names}")
                lines.append("")
                for sub_t in sub_tabs:
                    render_single_tab(sub_t, is_subtab=True)

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
                active_str = "Active" if rule.get("active", True) else "Inactive"
                rule_display_name = rule.get("name") or "(Unnamed Rule)"
                lines.append(f"#### Rule: {rule_display_name} ({active_str})")
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
        tab_node_id = f"Tab_{idx}"
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

    return "\n".join(lines)
