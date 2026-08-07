import os
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

HEADER_FILL   = PatternFill("solid", fgColor="1F3864")   # dark navy
ALT_ROW_FILL  = PatternFill("solid", fgColor="EBF0FA")   # light blue-grey
HEADER_FONT   = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
BODY_FONT     = Font(name="Calibri", size=10)
THIN_BORDER   = Border(
    left=Side(style="thin", color="B0B8CC"),
    right=Side(style="thin", color="B0B8CC"),
    top=Side(style="thin", color="B0B8CC"),
    bottom=Side(style="thin", color="B0B8CC"),
)

def _style_sheet(ws, headers):
    """Apply header style and column widths to a worksheet."""
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    ws.row_dimensions[1].height = 30

    # Auto-fit column widths (capped at 45)
    for col_idx, header in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(len(header) + 4, 14), 45)

def _write_rows(ws, rows, headers, start_row=2):
    """Write data rows with alternating row color."""
    for row_idx, row_data in enumerate(rows, start=start_row):
        fill = ALT_ROW_FILL if row_idx % 2 == 0 else None
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = BODY_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=False)
            if fill:
                cell.fill = fill

def _safe_tab_name(name):
    """Sanitize a string to be a valid Excel sheet name (max 31 chars)."""
    name = re.sub(r'[\\/*?:\[\]]', '_', name)
    return name[:31]


# ---------------------------------------------------------------------------
# Field normalisation (for object matching)
# ---------------------------------------------------------------------------

def normalize_field_name(name):
    if not name:
        return ""
    clean = name
    clean = re.sub(r'^(?:[a-zA-Z0-9_]+\.)+', '', clean)
    clean = re.sub(r'^(?:CustomFields\.)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:c\$|c_)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(?:CO\.)', '', clean, flags=re.IGNORECASE)
    return clean.strip().lower()


def _build_obj_index(objects_map):
    indexed = {}
    for oname, odata in objects_map.items():
        lookup = {}
        for of in odata.get("fields", []):
            nn = normalize_field_name(of.get("field_name"))
            nl = normalize_field_name(of.get("field_label"))
            if nn:
                lookup[nn] = of
            if nl and nl not in lookup:
                lookup[nl] = of
        indexed[oname] = lookup
    return indexed


def _enrich_workspace_fields(ws_fields, objects_map, bound_object):
    indexed = _build_obj_index(objects_map)
    enriched = []

    for wf in ws_fields:
        target_obj = wf.get("target_object") or bound_object
        target_key  = target_obj.lower()

        norm_code  = normalize_field_name(wf.get("field_code", ""))
        norm_label = normalize_field_name(wf.get("field_label", ""))

        target_idx = indexed.get(target_key, {})
        if not target_idx and len(indexed) == 1:
            target_idx = list(indexed.values())[0]

        matched = target_idx.get(norm_code) or target_idx.get(norm_label)

        if matched:
            data_type    = matched.get("data_type", "Text")
            is_system    = "Yes" if matched.get("is_system_field") else "No"
            is_nullable  = "Yes" if matched.get("is_nullable")     else "No"
            is_lookup    = "Yes" if matched.get("is_lookup")       else "No"
            max_len      = matched.get("max_length", "-")
            obj_field_id = matched.get("field_id", "-")
        else:
            f_code = wf.get("field_code", "")
            data_type    = "Standard Data Field"
            is_system    = "Yes"
            is_nullable  = "Yes"
            is_lookup    = "Yes" if ("Name" in f_code or "Id" in f_code) else "No"
            max_len      = "-"
            obj_field_id = "-"

        item = dict(wf)
        item.update({
            "target_object": target_obj,
            "object_field_id": obj_field_id,
            "data_type": data_type,
            "is_system_field": is_system,
            "is_nullable": is_nullable,
            "is_lookup": is_lookup,
            "max_length": max_len,
        })
        enriched.append(item)

    return enriched


# ---------------------------------------------------------------------------
# Public Excel writers
# ---------------------------------------------------------------------------

def write_workspaces_excel(parsed_workspaces, objects_map, output_path):
    """
    workspaces.xlsx
    One tab per workspace (tab name = workspace name).
    Columns do NOT include a 'Workspace Name' column.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)   # Remove default empty sheet

    headers = [
        "Bound Object", "Target Object", "Field Code", "Field Label",
        "Location / Tab", "Row", "Column", "Required", "Read Only",
        "Object Field ID", "Data Type", "Is System Field", "Is Nullable",
        "Is Lookup", "Max Length"
    ]

    for ws_data in parsed_workspaces:
        ws_name      = ws_data["workspace_name"]
        bound_object = ws_data.get("bound_object", "Contact")
        enriched     = _enrich_workspace_fields(ws_data.get("fields", []), objects_map, bound_object)

        sheet = wb.create_sheet(title=_safe_tab_name(ws_name))
        _style_sheet(sheet, headers)

        rows = []
        for item in enriched:
            rows.append([
                item["bound_object"], item["target_object"],
                item["field_code"], item["field_label"],
                item["location_tab"], item["row"], item["column"],
                item["required_option"], item["readonly_option"],
                item["object_field_id"], item["data_type"],
                item["is_system_field"], item["is_nullable"],
                item["is_lookup"], item["max_length"]
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path


def write_objects_excel(objects_map, output_path):
    """
    objects.xlsx
    One tab per object (tab name = object name).
    Columns do NOT include an 'Object Name' column.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = [
        "Package Name", "Field ID", "Field Name", "Field Label",
        "Data Type", "Is System Field", "Is Nullable", "Is Lookup",
        "Is Read Only", "Max Length", "Description"
    ]

    for obj_name, obj_data in objects_map.items():
        display_name = obj_data.get("object_name", obj_name)
        sheet = wb.create_sheet(title=_safe_tab_name(display_name))
        _style_sheet(sheet, headers)

        rows = []
        for of in obj_data.get("fields", []):
            rows.append([
                of.get("package_name", ""),
                of.get("field_id", ""),
                of.get("field_name", ""),
                of.get("field_label", ""),
                of.get("data_type", ""),
                "Yes" if of.get("is_system_field") else "No",
                "Yes" if of.get("is_nullable")     else "No",
                "Yes" if of.get("is_lookup")       else "No",
                "Yes" if of.get("is_readonly")     else "No",
                of.get("max_length", "-"),
                of.get("description", "")
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path


def write_combined_excel(parsed_workspaces, objects_map, output_path):
    """
    combined.xlsx
    One tab per workspace (tab name = workspace name).
    Fields are enriched with object schema data.
    Columns do NOT include 'Workspace Name' or 'Object Name'.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = [
        "Bound Object", "Target Object", "Field Code", "Field Label",
        "Workspace Tab", "Grid Position", "Required", "Read Only",
        "Object Field ID", "Data Type", "Is System Field",
        "Is Nullable", "Is Lookup", "Max Length", "In Workspace Layout"
    ]

    for ws_data in parsed_workspaces:
        ws_name      = ws_data["workspace_name"]
        bound_object = ws_data.get("bound_object", "Contact")
        enriched     = _enrich_workspace_fields(ws_data.get("fields", []), objects_map, bound_object)

        sheet = wb.create_sheet(title=_safe_tab_name(ws_name))
        _style_sheet(sheet, headers)

        rows = []
        for item in enriched:
            grid = f"Row {item['row']}, Col {item['column']}"
            rows.append([
                item["bound_object"], item["target_object"],
                item["field_code"], item["field_label"],
                item["location_tab"], grid,
                item["required_option"], item["readonly_option"],
                item["object_field_id"], item["data_type"],
                item["is_system_field"], item["is_nullable"],
                item["is_lookup"], item["max_length"],
                "Yes (Layout Used)"
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path
