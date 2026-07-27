import os
import html
import re
from lxml import etree

KNOWN_LABEL_IDS = {
    "6849": "Contact ID",
    "4648": "Created Date",
    "9958": "Updated Date",
    "4790": "First Name",
    "4793": "Last Name",
    "6820": "Login",
    "4547": "Email Address",
    "10664": "SLA Set",
    "13748": "Organization ID",
    "7490": "Display Name",
    "9050": "Audit Log",
    "8014": "Contact Search",
    "9011": "Contacts Report",
    "9029": "Incidents Report"
}

DATA_TYPE_NAMES = {
    "1": "Integer (1)",
    "2": "Float (2)",
    "3": "Integer/ID (3)",
    "4": "DateTime (4)",
    "5": "String (5)",
    "6": "Boolean (6)"
}

VAL_ATTR_NAMES = {
    "1": "Standard (1)",
    "9": "Custom/System Field (9)",
    "32769": "Masked/Login (32769)",
    "131081": "Custom Extended Field (131081)"
}

JOIN_TYPE_NAMES = {
    "1": "INNER JOIN",
    "2": "LEFT OUTER JOIN",
    "3": "RIGHT OUTER JOIN"
}

PERM_TYPE_NAMES = {
    "1": "Read Only",
    "3": "Read + Write"
}

def get_local_tag(elem):
    if elem is None or not hasattr(elem, "tag"):
        return ""
    return str(elem.tag).split("}")[-1]

def ns_find(elem, name):
    if elem is None:
        return None
    for child in elem:
        if get_local_tag(child) == name:
            return child
    return None

def ns_findall(elem, name):
    if elem is None:
        return []
    res = []
    for child in elem:
        if get_local_tag(child) == name:
            res.append(child)
    return res

def ns_find_descendant(elem, name):
    if elem is None:
        return None
    for child in elem.iter():
        if child is not elem and get_local_tag(child) == name:
            return child
    return None

def ns_findall_descendants(elem, name):
    if elem is None:
        return []
    res = []
    for child in elem.iter():
        if child is not elem and get_local_tag(child) == name:
            res.append(child)
    return res

def ns_text(elem, name, default=""):
    child = ns_find(elem, name) if elem is not None else None
    if child is not None and child.text is not None:
        return child.text.strip()
    return default

def parse_join_def_enum(join_enum):
    """
    Parses join_def_enum like 'contacts$2$c_id$$sla_instances$43$owner_id'
    into human-readable condition 'contacts.c_id = sla_instances.owner_id'
    """
    if not join_enum:
        return "—"
    parts = join_enum.split("$$")
    if len(parts) == 2:
        left_parts = parts[0].split("$")
        right_parts = parts[1].split("$")
        if len(left_parts) >= 3 and len(right_parts) >= 3:
            left_table = left_parts[0]
            left_col = left_parts[2]
            right_table = right_parts[0]
            right_col = right_parts[2]
            return f"{left_table}.{left_col} = {right_table}.{right_col}"
    return join_enum.replace("$", " ")

def parse_xml_data_header(raw_xml_data):
    """
    Decodes double-encoded XML string from <xml_data> to extract LabelStr, LabelId, Alignments, and Formats.
    """
    if not raw_xml_data:
        return None, None, None, None, None, None
    clean_xml = html.unescape(raw_xml_data)
    clean_xml = re.sub(r"<\?xml[^\?]*\?>", "", clean_xml).strip()
    if not clean_xml:
        return None, None, None, None, None, None
    try:
        sub_root = etree.fromstring(clean_xml.encode("utf-8"), parser=etree.XMLParser(recover=True))
        lstr_elem = ns_find_descendant(sub_root, "LabelStr")
        lid_elem = ns_find_descendant(sub_root, "LabelId")
        h_align_elem = ns_find_descendant(sub_root, "HeaderAlignment")
        d_align_elem = ns_find_descendant(sub_root, "DataAlignment")
        num_type_elem = ns_find_descendant(sub_root, "NumberType")
        date_type_elem = ns_find_descendant(sub_root, "DateFormatType")

        label_str = lstr_elem.text.strip() if lstr_elem is not None and lstr_elem.text else None
        label_id = lid_elem.text.strip() if lid_elem is not None and lid_elem.text else None
        h_align = h_align_elem.text.strip() if h_align_elem is not None and h_align_elem.text else None
        d_align = d_align_elem.text.strip() if d_align_elem is not None and d_align_elem.text else None
        num_type = num_type_elem.text.strip() if num_type_elem is not None and num_type_elem.text else None
        date_type = date_type_elem.text.strip() if date_type_elem is not None and date_type_elem.text else None

        return label_str, label_id, h_align, d_align, num_type, date_type
    except Exception:
        return None, None, None, None, None, None

def parse_analytics_core_report(root, file_path):
    report_id = ns_text(root, "ac_id")
    ac_public = ns_text(root, "ac_public").lower() == "true"
    ac_type = ns_text(root, "ac_type", "1")
    created = ns_text(root, "created")
    updated = ns_text(root, "updated")
    folder_id = ns_text(root, "folder_id")
    owner_acct_id = ns_text(root, "owner_acct_id")
    interface_id = ns_text(root, "interface_id")
    image = ns_text(root, "image")
    time_zone = ns_text(root, "time_zone")
    version = ns_text(root, "version")
    opts = ns_text(root, "opts")
    aux = ns_text(root, "aux")

    # Report Name
    report_name = ""
    label_elem = ns_find(root, "label")
    if label_elem is not None:
        lbl_item = ns_find(label_elem, "lbl_item")
        if lbl_item is not None:
            report_name = ns_text(lbl_item, "label")
    if not report_name:
        report_name = os.path.basename(file_path).replace(".xml", "")

    # Tables and Joins
    tables = []
    tables_by_tbl_id = {}
    tables_by_tbl = {}
    tables_container = ns_find(root, "tables")
    if tables_container is not None:
        for t_item in ns_findall(tables_container, "table_item"):
            tbl_id = ns_text(t_item, "tbl_id")
            tbl_enum = ns_text(t_item, "tbl")
            alias = ns_text(t_item, "alias")
            join_type_code = ns_text(t_item, "join_type")
            join_def_enum = ns_text(t_item, "join_def_enum")
            join_def_idx = ns_text(t_item, "join_def_idx")

            join_type_label = JOIN_TYPE_NAMES.get(join_type_code, "Primary") if join_type_code else "Primary"
            join_condition = parse_join_def_enum(join_def_enum) if join_def_enum else "—"

            table_entry = {
                "tbl_id": tbl_id,
                "tbl_enum": tbl_enum,
                "alias": alias,
                "join_type": join_type_label,
                "join_type_code": join_type_code,
                "join_def_enum": join_def_enum,
                "join_def_idx": join_def_idx,
                "join_condition": join_condition
            }
            tables.append(table_entry)
            if tbl_id:
                tables_by_tbl_id[str(tbl_id)] = alias
            if tbl_enum:
                tables_by_tbl[str(tbl_enum)] = alias
            if tbl_id and str(tbl_id) not in tables_by_tbl:
                tables_by_tbl[str(tbl_id)] = alias

    # Extract sub-report drilldown target IDs
    sub_reports = []
    sub_report_ids_set = set()
    for child in root.iter():
        if isinstance(child.tag, str):
            tag_name = get_local_tag(child)
            if tag_name in ["sub_report_id", "sub_rpt_id", "drilldown_ac_id", "sub_id"]:
                sr_text = child.text.strip() if child.text else None
                if sr_text and sr_text != "0" and sr_text not in sub_report_ids_set:
                    sub_report_ids_set.add(sr_text)
                    sub_reports.append({"id": sr_text, "name": None})

    # Nodes count and section visibilities
    nodes_container = ns_find(root, "nodes")
    node_items = ns_findall(nodes_container, "node_item") if nodes_container is not None else []
    node_count = len(node_items)
    
    node_details = []
    for n_item in node_items:
        n_id = ns_text(n_item, "n_id")
        group_type = ns_text(n_item, "group_type")
        style_id = ns_text(n_item, "style_id")
        row_limit = ns_text(n_item, "row_limit")
        
        node_xml_elem = ns_find(n_item, "xml_data")
        raw_node_xml = node_xml_elem.text if node_xml_elem is not None else None
        hidden_sections = []
        display_options = []
        if raw_node_xml:
            clean_node_xml = html.unescape(raw_node_xml)
            clean_node_xml = re.sub(r"<\?xml[^\?]*\?>", "", clean_node_xml).strip()
            if clean_node_xml:
                try:
                    n_sub_root = etree.fromstring(clean_node_xml.encode("utf-8"), parser=etree.XMLParser(recover=True))
                    for sec in ns_findall_descendants(n_sub_root, "ReportSection"):
                        type_elem = ns_find_descendant(sec, "Type") or ns_find_descendant(sec, "SectionType")
                        vis_elem = ns_find_descendant(sec, "Visible")
                        sec_type = type_elem.text.strip() if type_elem is not None and type_elem.text else None
                        vis_val = vis_elem.text.strip().lower() if vis_elem is not None and vis_elem.text else "true"
                        if vis_val == "false" and sec_type:
                            hidden_sections.append(sec_type)

                    disp_opt_elem = ns_find_descendant(n_sub_root, "DisplayOptions")
                    if disp_opt_elem is not None and disp_opt_elem.text:
                        display_options.append(disp_opt_elem.text.strip())
                except Exception:
                    pass

        node_details.append({
            "n_id": n_id,
            "group_type": group_type,
            "style_id": style_id,
            "row_limit": row_limit or "None",
            "hidden_sections": hidden_sections,
            "display_options": display_options
        })

    # Columns
    columns = []
    if nodes_container is not None:
        for node_item in node_items:
            cols_container = ns_find(node_item, "cols")
            if cols_container is not None:
                for c_item in ns_findall(cols_container, "cols_item"):
                    col_id = ns_text(c_item, "col_id")
                    col_self_ref = ns_text(c_item, "col_rf")
                    val_col_refs = ns_text(c_item, "val_col_refs")
                    val_attrs_code = ns_text(c_item, "val_attrs")
                    val_attrs_label = VAL_ATTR_NAMES.get(val_attrs_code, f"Attrs {val_attrs_code}") if val_attrs_code else "—"

                    display_order = int(ns_text(c_item, "display_order", "9999") or "9999")
                    val = ns_text(c_item, "val")
                    data_type_code = ns_text(c_item, "data_type")
                    data_type_name = DATA_TYPE_NAMES.get(data_type_code, f"Type {data_type_code}")
                    sort_order = ns_text(c_item, "sort_order")
                    sort_direction_code = ns_text(c_item, "sort_direction")

                    sort_info = ""
                    if sort_order:
                        rank_names = {"1": "primary", "2": "secondary", "3": "tertiary"}
                        rank_name = rank_names.get(sort_order, f"rank {sort_order}")
                        arrow = "↑" if sort_direction_code == "1" else ("↓" if sort_direction_code == "2" else "")
                        sort_info = f"Sort #{sort_order} {arrow} ({rank_name})"

                    # Decode <xml_data>
                    xml_data_elem = ns_find(c_item, "xml_data")
                    raw_xml_data = xml_data_elem.text if xml_data_elem is not None else None
                    label_str, label_id, h_align, d_align, num_type, date_type = parse_xml_data_header(raw_xml_data)

                    label_display = "—"
                    label_source = "none"
                    label_tag = ""
                    if label_str:
                        label_display = label_str
                        label_source = "literal"
                        label_tag = "`[literal]`"
                    elif label_id:
                        if label_id in KNOWN_LABEL_IDS:
                            label_display = KNOWN_LABEL_IDS[label_id]
                            label_source = "dict"
                            label_tag = f"`[dict: {label_id}]`"
                        else:
                            label_display = f"System Label {label_id}"
                            label_source = "system_id"
                            label_tag = f"`[system: {label_id}]`"

                    # Extract table alias from val (e.g. 'contacts.first_name' -> 'contacts')
                    table_alias = val.split(".")[0] if "." in val else "—"

                    # Cross-check val_col_refs (authoritative table reference, e.g. "contacts.first_name;2") with table_alias
                    col_rf_verified = True
                    col_rf_mismatch_detail = None
                    col_rf_table = None

                    if val_col_refs and ";" in val_col_refs:
                        ref_tbl_num = val_col_refs.split(";")[1]
                        col_rf_table = tables_by_tbl.get(ref_tbl_num)
                        if col_rf_table and table_alias != "—":
                            col_rf_verified = (col_rf_table.lower() == table_alias.lower())
                            if not col_rf_verified:
                                col_rf_mismatch_detail = f"field prefix = `{table_alias}`, `val_col_refs` table = `{col_rf_table}` (tbl {ref_tbl_num})"

                    columns.append({
                        "col_id": col_id,
                        "col_self_ref": col_self_ref,
                        "val_col_refs": val_col_refs,
                        "val_attrs": val_attrs_label,
                        "val_attrs_code": val_attrs_code,
                        "col_rf_table": col_rf_table,
                        "col_rf_verified": col_rf_verified,
                        "col_rf_mismatch_detail": col_rf_mismatch_detail,
                        "display_order": display_order,
                        "val": val,
                        "source_field": val,
                        "table_alias": table_alias,
                        "label": label_display,
                        "label_str": label_str,
                        "label_id": label_id,
                        "label_source": label_source,
                        "label_tag": label_tag,
                        "data_type": data_type_name,
                        "data_type_code": data_type_code,
                        "header_align": h_align,
                        "data_align": d_align,
                        "number_type": num_type,
                        "date_format_type": date_type,
                        "sort_order": sort_order,
                        "sort_direction": sort_direction_code,
                        "sort_info": sort_info
                    })

    columns.sort(key=lambda x: x["display_order"])

    # Permissions
    permissions = []
    perms_container = ns_find(root, "perms")
    if perms_container is not None:
        for p_item in ns_findall(perms_container, "perm_item"):
            profile_id = ns_text(p_item, "profile_id")
            perm_code = ns_text(p_item, "perms")
            perm_label = PERM_TYPE_NAMES.get(perm_code, f"Perm {perm_code}")
            if profile_id:
                permissions.append({
                    "profile_id": profile_id,
                    "perm_code": perm_code,
                    "perm_label": perm_label
                })

    # Group permissions by type
    perms_by_type = {}
    for p in permissions:
        perms_by_type.setdefault(p["perm_label"], []).append(p["profile_id"])

    # Filters
    filters = []
    filters_container = ns_find(root, "filters")
    has_filters_container = filters_container is not None
    if filters_container is not None:
        for f_item in ns_findall(filters_container, "fltr_item"):
            f_id = ns_text(f_item, "fltr_id")
            val = ns_text(f_item, "val")
            filters.append({
                "id": f_id,
                "val": val
            })

    RECOGNIZED_REPORT_TAGS = {
        "ac_id", "ac_public", "ac_type", "created", "updated", "folder_id",
        "owner_acct_id", "interface_id", "image", "time_zone", "version",
        "opts", "aux", "label", "tables", "nodes", "cols", "filters", "perms"
    }

    raw_unhandled_tags = []
    for child in root:
        local_t = get_local_tag(child)
        if local_t and local_t not in RECOGNIZED_REPORT_TAGS:
            try:
                raw_snippet = etree.tostring(child, encoding="unicode").strip()
                if len(raw_snippet) > 300:
                    raw_snippet = raw_snippet[:300] + "... [truncated]"
                raw_unhandled_tags.append({
                    "tag": local_t,
                    "raw_xml": raw_snippet
                })
            except Exception:
                pass

    return {
        "id": report_id,
        "name": report_name,
        "format": "analytics_core",
        "ac_type": ac_type,
        "ac_public": ac_public,
        "created": created,
        "updated": updated,
        "folder_id": folder_id,
        "owner_acct_id": owner_acct_id,
        "interface_id": interface_id,
        "image": image,
        "time_zone": time_zone,
        "version": version,
        "opts": opts,
        "aux": aux,
        "node_count": node_count,
        "node_details": node_details,
        "has_filters_container": has_filters_container,
        "tables": tables,
        "columns": columns,
        "permissions": permissions,
        "perms_by_type": perms_by_type,
        "filters": filters,
        "sub_reports": sub_reports,
        "raw_unhandled_tags": raw_unhandled_tags
    }

def parse_standard_report(root, file_path):
    report_id = root.get("Id") or root.get("id") or ns_text(root, "ReportId")
    report_name = root.get("Name") or root.get("name") or ns_text(root, "ReportName")
    object_type = root.get("ObjectType") or root.get("object_type") or ns_text(root, "ObjectType")

    if not report_name:
        report_name = os.path.basename(file_path).replace(".xml", "")

    columns = []
    for col in ns_findall_descendants(root, "Column"):
        col_name = col.get("Name") or col.get("name") or ns_text(col, "Label") or ns_text(col, "Heading")
        source = ns_find(col, "Source")
        source_field = source.text.strip() if source is not None and source.text else (col.get("Source") or "—")
        columns.append({
            "col_id": str(len(columns) + 1),
            "col_self_ref": "—",
            "val_col_refs": "—",
            "val_attrs": "Standard (1)",
            "val_attrs_code": "1",
            "col_rf_table": None,
            "col_rf_verified": True,
            "col_rf_mismatch_detail": None,
            "display_order": len(columns) + 1,
            "name": col_name or source_field,
            "source_field": source_field,
            "table_alias": source_field.split(".")[0] if "." in source_field else "—",
            "label": col_name or source_field,
            "label_source": "literal",
            "label_tag": "`[literal]`",
            "data_type": "String (5)",
            "header_align": "Near",
            "data_align": "Near",
            "number_type": None,
            "date_format_type": None,
            "sort_order": None,
            "sort_direction": None,
            "sort_info": "—"
        })

    filters = []
    for filt in ns_findall_descendants(root, "Filter"):
        filt_name = filt.get("Name") or filt.get("name")
        field_val = ns_text(filt, "Field", filt.get("Field") or "—")
        oper_val = ns_text(filt, "Operator", filt.get("Operator") or "—")
        filters.append({
            "name": filt_name,
            "field": field_val,
            "operator": oper_val
        })

    sub_reports = []
    for sr in root.findall(".//*[@SubReportId]") + root.findall(".//SubReport") + root.findall(".//*[@AcId]"):
        sr_id = sr.get("SubReportId") or sr.get("AcId") or sr.get("id")
        sr_name = sr.get("Name") or sr.get("name")
        if sr_id and sr_id not in [r["id"] for r in sub_reports]:
            sub_reports.append({"id": sr_id, "name": sr_name})

    return {
        "id": report_id,
        "name": report_name,
        "format": "standard",
        "object_type": object_type,
        "node_count": 1,
        "node_details": [],
        "has_filters_container": bool(filters),
        "columns": columns,
        "filters": filters,
        "sub_reports": sub_reports,
        "tables": [],
        "permissions": [],
        "perms_by_type": {}
    }

def parse_report_file(file_path):
    """
    Parses an OSVC Report XML export file (analytics_core or standard) and returns structured metadata.
    Strips trailing signature/version lines if present.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Report file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_content = f.read()

    export_signature = None
    if "</analytics_core>" in raw_content:
        parts = raw_content.split("</analytics_core>")
        xml_content = parts[0] + "</analytics_core>"
        trailing = parts[1].strip()
        if trailing:
            export_signature = trailing.replace("\n", " | ")
    else:
        xml_content = raw_content

    parser = etree.XMLParser(recover=True, remove_comments=True)
    root = etree.fromstring(xml_content.encode("utf-8"), parser=parser)

    root_tag = get_local_tag(root)
    if root_tag == "analytics_core" or ns_find(root, "ac_id") is not None:
        rep_data = parse_analytics_core_report(root, file_path)
        if export_signature:
            rep_data["export_signature"] = export_signature
        return rep_data
    else:
        return parse_standard_report(root, file_path)

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        data = parse_report_file(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python report_parser.py <path_to_report_xml>")
