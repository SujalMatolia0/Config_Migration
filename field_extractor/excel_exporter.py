import os
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Styling constants
# ---------------------------------------------------------------------------

HEADER_FILL  = PatternFill("solid", fgColor="2E75B6")   # professional blue
ALT_ROW_FILL = PatternFill("solid", fgColor="DEEAF1")   # light blue-grey
HEADER_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
BODY_FONT    = Font(name="Calibri", size=10)
THIN_BORDER  = Border(
    left=Side(style="thin", color="9DC3E6"),
    right=Side(style="thin", color="9DC3E6"),
    top=Side(style="thin", color="9DC3E6"),
    bottom=Side(style="thin", color="9DC3E6"),
)

def _style_sheet(ws, headers):
    """Apply header style, freeze the top row, and add auto-filter to a worksheet."""
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    # Keep header visible when scrolling
    ws.freeze_panes = "A2"

    # Add filter dropdowns on all header columns
    last_col = get_column_letter(len(headers))
    ws.auto_filter.ref = f"A1:{last_col}1"

    ws.row_dimensions[1].height = 34

    # Auto-fit column widths (capped at 50)
    for col_idx, header in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(len(header) + 4, 14), 50)

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
# Option value formatting
# ---------------------------------------------------------------------------

_TRIGGER_MAP = {
    "onnew":    "New",
    "onedit":   "Edit",
    "onsave":   "Save",
    "onalways": "Always",
    "ondelete": "Delete",
}

def _format_option(raw):
    """
    Converts OSVC workspace option strings to clean readable values.
    Examples:
      ""                            -> No
      "OnNew:~any~;OnEdit:~any~"   -> Yes (New + Edit)
      "OnEdit:~any~"               -> Yes (Edit Only)
      "OnNew:~any~"                -> Yes (New Only)
      "True"                       -> Yes
      "False"                      -> No
    """
    if not raw or raw.strip() == "":
        return "No"

    raw = raw.strip()

    # Simple boolean-style values
    if raw.lower() in ("true", "yes", "1"):
        return "Yes"
    if raw.lower() in ("false", "no", "0"):
        return "No"

    # Parse segment list like OnNew:~any~;OnEdit:~any~
    segments = raw.split(";")
    triggers = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if ":" in seg:
            trigger, condition = seg.split(":", 1)
            trigger   = trigger.strip().lower()
            condition = condition.strip().strip("~")
            label = _TRIGGER_MAP.get(trigger, trigger.capitalize())
            if condition == "any":
                triggers.append(label)
            else:
                triggers.append(f"{label} ({condition})")
        else:
            triggers.append(seg)

    if not triggers:
        return "No"
    if len(triggers) == 1:
        return f"Yes ({triggers[0]} Only)"
    return "Yes (" + " + ".join(triggers) + ")"


# ---------------------------------------------------------------------------
# Field key builder (PackageName$Name)
# ---------------------------------------------------------------------------

_SYSTEM_PACKAGES = {"oracleservicecloud", "rightnow", ""}

def _field_type_from_obj(field_dict):
    """
    Determines Field Type from the Object XML field definition.
    Primary signal: PackageName attribute — if it is a non-system package, the field is Custom.
    Secondary signal: whether the Name itself contains '$'.
    Falls back to IsSystemField attribute.

    Values returned:
      'Custom (PackageName)' — field created by the org (e.g. C, CO, MY_PKG)
      'System Field'         — built-in OSVC system field (IsSystemField=True)
      'OSVC Standard'        — built-in OSVC platform field (IsSystemField=False)
    """
    pkg  = (field_dict.get("package_name") or "").strip()
    name = (field_dict.get("field_name")   or "").strip()

    # Package name is the clearest signal
    if pkg and pkg.lower() not in _SYSTEM_PACKAGES:
        return f"Custom ({pkg})"

    # If the name itself contains $ it is a custom field (e.g. C$FieldName in raw XML)
    if "$" in name:
        pkg_part = name.split("$", 1)[0]
        return f"Custom ({pkg_part})"

    # Fall back to the IsSystemField flag from the XML
    return "System Field" if field_dict.get("is_system_field", False) else "OSVC Standard"


def _field_type_from_ws_id(raw_field_id):
    """
    Determines Field Type from the raw workspace FieldId string alone.
    If the FieldId contains '$' it is a custom field.
    Examples:
      'C$PhoneExt'                  -> Custom (C)
      'CustomFields.c$org_id_temp'  -> Custom (c)
      'Name.First'                  -> System Field
      'OrgId'                       -> System Field
    """
    if not raw_field_id:
        return "System Field"
    # Strip object and CustomFields prefix to get the bare field token
    token = re.sub(r'^[^.]+\.', '', raw_field_id)           # remove e.g. "Contact."
    token = re.sub(r'^CustomFields\.', '', token, flags=re.IGNORECASE)
    if "$" in token:
        pkg_part = token.split("$", 1)[0]
        return f"Custom ({pkg_part})"
    return "System Field"

def _obj_field_key(field_dict):
    """
    Builds a lookup key for an object field as PackageName$Name.
    System fields (OracleServiceCloud package) use just the field Name.
    Custom package fields use PackageName$Name (e.g. C$org_id_temp).
    """
    pkg  = (field_dict.get("package_name") or "").strip()
    name = (field_dict.get("field_name")   or "").strip()
    if pkg.lower() in _SYSTEM_PACKAGES:
        return name.lower()
    return f"{pkg}${name}".lower()


def _ws_field_key(raw_field_id):
    """
    Normalizes a workspace FieldId into the same key format used by _obj_field_key.
    Examples:
      "Name.First"                     -> "name.first"
      "C$PhoneExt"                     -> "c$phoneext"
      "CustomFields.c$org_id_temp"     -> "c$org_id_temp"
      "OrgId"                          -> "orgid"
    """
    if not raw_field_id:
        return ""
    key = raw_field_id.strip()
    # Strip leading ObjectId prefix (e.g. "Contact." when already prefixed)
    key = re.sub(r'^[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.', '', key)  # e.g. Contact.CustomFields.
    # Collapse CustomFields. prefix
    key = re.sub(r'^CustomFields\.', '', key, flags=re.IGNORECASE)
    return key.lower()


# ---------------------------------------------------------------------------
# Object index builder
# ---------------------------------------------------------------------------

def _build_obj_index(objects_map):
    """
    Returns dict keyed by lowercase object name ->
    {field_key: field_dict} where field_key = PackageName$Name or just Name.
    """
    indexed = {}
    for oname, odata in objects_map.items():
        lookup = {}
        for of in odata.get("fields", []):
            key = _obj_field_key(of)
            if key:
                lookup[key] = of
            # Also index by plain lowercased field name as secondary fallback
            plain = (of.get("field_name") or "").lower()
            if plain and plain not in lookup:
                lookup[plain] = of
        indexed[oname] = lookup
    return indexed


# ---------------------------------------------------------------------------
# Workspace field enrichment
# ---------------------------------------------------------------------------

def _enrich_workspace_fields(ws_fields, objects_map, bound_object):
    indexed = _build_obj_index(objects_map)
    enriched = []

    for wf in ws_fields:
        target_obj = wf.get("target_object") or bound_object
        target_key = target_obj.lower()

        raw_id     = wf.get("raw_field_id", "") or wf.get("field_code", "")
        ws_key     = _ws_field_key(raw_id)
        ws_key_alt = _ws_field_key(wf.get("field_code", ""))

        target_idx = indexed.get(target_key, {})
        if not target_idx and len(indexed) == 1:
            target_idx = list(indexed.values())[0]

        matched = target_idx.get(ws_key) or target_idx.get(ws_key_alt)

        if matched:
            data_type   = matched.get("data_type", "Text")
            ftype       = _field_type_from_obj(matched)
            is_nullable = "Yes" if matched.get("is_nullable") else "No"
            is_lookup   = "Yes" if matched.get("is_lookup")   else "No"
            max_len     = matched.get("max_length", "-")
            # Build the display field name: PackageName$Name
            pkg   = (matched.get("package_name") or "").strip()
            fname = matched.get("field_name", "")
            if pkg.lower() in _SYSTEM_PACKAGES:
                obj_field_key = fname
            else:
                obj_field_key = f"{pkg}${fname}"
        else:
            f_code        = wf.get("field_code", "")
            data_type     = "Standard Data Field"
            # Determine type from the raw workspace field ID name ($ = custom)
            ftype         = _field_type_from_ws_id(raw_id or f_code)
            is_nullable   = "Yes"
            is_lookup     = "Yes" if ("Name" in f_code or "Id" in f_code) else "No"
            max_len       = "-"
            obj_field_key = raw_id

        item = dict(wf)
        item.update({
            "target_object":  target_obj,
            "obj_field_key":  obj_field_key,
            "data_type":      data_type,
            "field_type":     ftype,
            "is_nullable":    is_nullable,
            "is_lookup":      is_lookup,
            "max_length":     max_len,
            "required_fmt":   _format_option(wf.get("required_option", "")),
            "readonly_fmt":   _format_option(wf.get("readonly_option", "")),
        })
        enriched.append(item)

    return enriched


# ---------------------------------------------------------------------------
# Public Excel writers
# ---------------------------------------------------------------------------

def write_workspaces_excel(parsed_workspaces, objects_map, output_path):
    """
    workspaces.xlsx — one tab per workspace.
    Tab name = workspace name. No 'Workspace Name' column.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = [
        "Bound Object", "Target Object", "Object Field Name",
        "Field Label", "Location / Tab", "Required", "Read Only",
        "Data Type", "Field Type", "Is Nullable", "Is Lookup", "Max Length"
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
                item["bound_object"],
                item["target_object"],
                item["obj_field_key"],
                item["field_label"],
                item["location_tab"],
                item["required_fmt"],
                item["readonly_fmt"],
                item["data_type"],
                item["field_type"],
                item["is_nullable"],
                item["is_lookup"],
                item["max_length"],
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path


def write_objects_excel(objects_map, output_path):
    """
    objects.xlsx — one tab per object.
    Tab name = object name. No 'Object Name' column.
    Field key shown as PackageName$Name.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = [
        "Field Key (Package$Name)", "Field Label",
        "Data Type", "Field Type", "Is Nullable", "Is Lookup",
        "Is Read Only", "Max Length", "Description"
    ]

    for obj_name, obj_data in objects_map.items():
        display_name = obj_data.get("object_name", obj_name)
        sheet = wb.create_sheet(title=_safe_tab_name(display_name))
        _style_sheet(sheet, headers)

        rows = []
        for of in obj_data.get("fields", []):
            key = _obj_field_key(of)
            rows.append([
                key,
                of.get("field_label", ""),
                of.get("data_type", ""),
                _field_type_from_obj(of),
                "Yes" if of.get("is_nullable") else "No",
                "Yes" if of.get("is_lookup")   else "No",
                "Yes" if of.get("is_readonly") else "No",
                of.get("max_length", "-"),
                of.get("description", "")
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path


def write_combined_excel(parsed_workspaces, objects_map, output_path):
    """
    combined.xlsx — one tab per workspace.
    Tab name = workspace name. Fields enriched with object schema data.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    headers = [
        "Bound Object", "Target Object", "Object Field Name",
        "Field Label", "Workspace Tab", "Required", "Read Only",
        "Data Type", "Field Type", "Is Nullable",
        "Is Lookup", "Max Length", "In Workspace Layout"
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
                item["bound_object"],
                item["target_object"],
                item["obj_field_key"],
                item["field_label"],
                item["location_tab"],
                item["required_fmt"],
                item["readonly_fmt"],
                item["data_type"],
                item["field_type"],
                item["is_nullable"],
                item["is_lookup"],
                item["max_length"],
                "Yes",
            ])

        _write_rows(sheet, rows, headers)

    wb.save(output_path)
    return output_path
