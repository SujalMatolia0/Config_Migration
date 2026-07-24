try:
    from .utils import get_all_tabs_flat, normalise_id, is_custom_script_url, safe_basename
except ImportError:
    from utils import get_all_tabs_flat, normalise_id, is_custom_script_url, safe_basename


def map_relationships(components):
    """
    Maps relationships between all parsed OSVC components.

    Returns a list of relationship dicts:
    [
      {
        "from": { "type": str, "name": str },
        "to":   { "type": str, "id": str|None, "name": str },
        "via":  str   # human-readable description of the link
      }
    ]

    Enhancements vs previous version:
    - All report ID lookups normalised to str (fixes silent int/str mismatch)
    - CPM bound_classes uses list truthiness correctly ([] vs None distinction)
    - CPM custom_fields_read relationships added (not just written)
    - CPM custom fields linked to matching analytics report columns (cross-ref)
    - safe_basename() used for custom-script URL extraction
    - No duplicate get_all_tabs_flat — uses shared utils
    - Tab field traversal deduplicated (was double-traversing tabs)
    - CPM config_vars exposed as relationships to ConfigSetting nodes
    - SOAP endpoints include procedure name in relationship label
    """
    relationships = []

    workspaces   = components.get("workspaces", [])
    reports      = components.get("reports", [])
    scripts      = components.get("customScripts", [])
    cpm_handlers = components.get("cpm", [])
    business_rules_list = components.get("businessRules", [])
    nav_sets     = components.get("navigationSets", [])

    # ── Index lookups (all IDs normalised to str) ─────────────────────────
    reports_by_id   = {normalise_id(r.get("id")): r for r in reports if r.get("id") is not None}
    reports_by_name = {r.get("name", "").lower(): r for r in reports if r.get("name")}
    workspaces_by_name = {w.get("name", "").lower(): w for w in workspaces if w.get("name")}
    scripts_by_name    = {s.get("file_name", "").lower(): s for s in scripts if s.get("file_name")}

    # Build a map: custom_field_name -> list of {col_id, label, table, display_order}
    # from analytics reports so CPM writes/reads can be cross-referenced
    cf_to_report_cols = {}   # e.g. "c$org_id_temp" -> [{"report_name":..., "col":...}]
    for rep in reports:
        rep_name = rep.get("name", f"Report {rep.get('id')}")
        for col in rep.get("columns", []):
            field = col.get("field", "")            # e.g. "contacts.c$org_id_temp"
            # Extract the c$ part
            if "c$" in field:
                cf_name = "c$" + field.split("c$", 1)[1]
                cf_to_report_cols.setdefault(cf_name, []).append({
                    "report_name": rep_name,
                    "report_id":   normalise_id(rep.get("id")),
                    "col_id":      col.get("col_id"),
                    "label":       col.get("label"),
                    "table":       col.get("table"),
                    "display_order": col.get("display_order"),
                })

    def _rep_ref(rep_id_raw):
        """Return (normalised_id, name) for a report ID, with fallback label."""
        nid = normalise_id(rep_id_raw)
        rep = reports_by_id.get(nid)
        return nid, (rep.get("name") if rep else f"Report {nid}")

    # ── 1. Workspaces ──────────────────────────────────────────────────────
    for ws in workspaces:
        ws_name = ws.get("name")
        all_tabs = get_all_tabs_flat(ws.get("tabs", []))

        # 1a. Tab relationship items → Reports
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            for ri in tab.get("relationship_items", []):
                for id_key, label in [("ac_id", "AcId"), ("search_report_id", "SearchReportId")]:
                    raw_id = ri.get(id_key)
                    if raw_id is not None:
                        nid, rep_name = _rep_ref(raw_id)
                        relationships.append({
                            "from": {"type": "Workspace", "name": ws_name},
                            "to":   {"type": "Report", "id": nid, "name": rep_name},
                            "via":  f"Tab '{tab_text}' → RelationshipItem {label}: {nid}"
                        })

        # 1b. Workspace-level fields → Reports
        for f in ws.get("fields", []):
            raw_id = f.get("report_id")
            if raw_id is not None:
                nid, rep_name = _rep_ref(raw_id)
                relationships.append({
                    "from": {"type": "Workspace", "name": ws_name},
                    "to":   {"type": "Report", "id": nid, "name": rep_name},
                    "via":  f"Field '{f.get('field_id')}' → ReportId {nid}"
                })

        # 1c. Tab-level fields → Reports  (single traversal, not double)
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            for f in tab.get("fields", []):
                raw_id = f.get("report_id")
                if raw_id is not None:
                    nid, rep_name = _rep_ref(raw_id)
                    relationships.append({
                        "from": {"type": "Workspace", "name": ws_name},
                        "to":   {"type": "Report", "id": nid, "name": rep_name},
                        "via":  f"Tab '{tab_text}' → Field '{f.get('field_id')}' → ReportId {nid}"
                    })

        # 1d. Embedded browsers → CustomScript or ExternalEndpoint
        for tab in all_tabs:
            tab_text = tab.get("text", "")
            for br in tab.get("browsers", []):
                url = br.get("url")
                if not url:
                    continue
                if is_custom_script_url(url):
                    script_name = safe_basename(url)
                    relationships.append({
                        "from": {"type": "Workspace", "name": ws_name},
                        "to":   {"type": "CustomScript", "name": script_name},
                        "via":  f"Tab '{tab_text}' → Browser → Custom PHP Script ({url})"
                    })
                else:
                    relationships.append({
                        "from": {"type": "Workspace", "name": ws_name},
                        "to":   {"type": "ExternalEndpoint", "name": url},
                        "via":  f"Tab '{tab_text}' → Browser → External Endpoint"
                    })

        # 1e. Ribbon links → CustomScript or ExternalEndpoint
        for link in ws.get("ribbon_links", []):
            url = link.get("url")
            if not url:
                continue
            if is_custom_script_url(url):
                script_name = safe_basename(url)
                relationships.append({
                    "from": {"type": "Workspace", "name": ws_name},
                    "to":   {"type": "CustomScript", "name": script_name},
                    "via":  f"Ribbon Link '{link.get('title')}' → Custom PHP Script"
                })
            else:
                relationships.append({
                    "from": {"type": "Workspace", "name": ws_name},
                    "to":   {"type": "ExternalEndpoint", "name": url},
                    "via":  f"Ribbon Link '{link.get('title')}' → External Endpoint"
                })

        # 1f. Workspace rules → Scripts
        for rule in ws.get("rules", []):
            rule_name = rule.get("name")
            for action in rule.get("actions", []):
                script_path = action.get("script_path") or (
                    action.get("value") if action.get("type") == "RunScript" else None
                )
                if script_path:
                    script_base = os.path.basename(script_path).lower()
                    ref = scripts_by_name.get(script_base)
                    script_name = ref.get("file_name") if ref else script_path
                    relationships.append({
                        "from": {"type": "Workspace", "name": ws_name},
                        "to":   {"type": "CustomScript", "name": script_name},
                        "via":  f"Rule '{rule_name}' → Action: RunScript"
                    })

    # ── 2. Business Rules → Scripts ────────────────────────────────────────
    for br_file in business_rules_list:
        file_name = br_file.get("file_name")
        for rule in br_file.get("rules", []):
            rule_name = rule.get("name")
            for action in rule.get("actions", []):
                script_path = action.get("script_path") or (
                    action.get("value") if action.get("type") == "RunScript" else None
                )
                if script_path:
                    script_base = os.path.basename(script_path).lower()
                    ref = scripts_by_name.get(script_base)
                    script_name = ref.get("file_name") if ref else script_path
                    relationships.append({
                        "from": {"type": "BusinessRule", "name": rule_name},
                        "to":   {"type": "CustomScript", "name": script_name},
                        "via":  f"Business Rule File '{file_name}' → RunScript"
                    })

    # ── 3. Navigation Sets → Workspaces / Reports ──────────────────────────
    for ns in nav_sets:
        ns_name = ns.get("name")
        for item in ns.get("items", []):
            label     = item.get("label")
            item_type = item.get("type")
            ws_ref    = item.get("workspace")
            rep_raw   = item.get("report_id")

            if ws_ref:
                ref_ws = workspaces_by_name.get(ws_ref.lower())
                ws_actual = ref_ws.get("name") if ref_ws else ws_ref
                relationships.append({
                    "from": {"type": "NavigationSet", "name": ns_name},
                    "to":   {"type": "Workspace", "name": ws_actual},
                    "via":  f"Nav Item '{label}' ({item_type})"
                })

            if rep_raw is not None:
                nid, rep_name = _rep_ref(rep_raw)
                relationships.append({
                    "from": {"type": "NavigationSet", "name": ns_name},
                    "to":   {"type": "Report", "id": nid, "name": rep_name},
                    "via":  f"Nav Item '{label}' ({item_type})"
                })

    # ── 4. Custom Scripts → Other Custom Scripts ───────────────────────────
    for script in scripts:
        script_name = script.get("file_name")
        for imp in script.get("imports", []):
            imp_base = os.path.basename(imp).lower()
            ref = scripts_by_name.get(imp_base)
            imported = ref.get("file_name") if ref else imp
            relationships.append({
                "from": {"type": "CustomScript", "name": script_name},
                "to":   {"type": "CustomScript", "name": imported},
                "via":  f"import/require: '{imp}'"
            })

    # ── 5. CPM Procedures ──────────────────────────────────────────────────
    for cpm in cpm_handlers:
        cpm_name   = cpm.get("name") or cpm.get("file_name")
        cpm_format = cpm.get("format")

        if cpm_format in ("cpm_procedure", "cpm_php", None):
            ops_label = cpm.get("operations_label", "Event")

            # 5a. Bound classes → OSVCObject
            # FIX: use `is None` check, not truthiness, so empty list [] is handled correctly
            bound = cpm.get("bound_classes")
            if bound is None:
                bound = cpm.get("osvc_objects", [])
            for bcls in bound:
                relationships.append({
                    "from": {"type": "CPM", "name": cpm_name},
                    "to":   {"type": "OSVCObject", "name": bcls},
                    "via":  f"ObjectProcedure bound class ({ops_label})"
                })

            # 5b. SOAP actions → ExternalEndpoint
            for soap in cpm.get("soap_actions", []):
                relationships.append({
                    "from": {"type": "CPM", "name": cpm_name},
                    "to":   {"type": "ExternalEndpoint", "name": f"SOAP: {soap}"},
                    "via":  f"Siebel SOAP invocation: {soap}"
                })

            # 5c. Config vars → ConfigSetting nodes (NEW)
            for cfg in cpm.get("config_vars", []):
                relationships.append({
                    "from": {"type": "CPM", "name": cpm_name},
                    "to":   {"type": "ConfigSetting", "name": cfg},
                    "via":  "Config variable reference"
                })

            # 5d. Custom fields written → CustomField nodes
            for cf in cpm.get("custom_fields_written", []):
                relationships.append({
                    "from": {"type": "CPM", "name": cpm_name},
                    "to":   {"type": "CustomField", "name": cf},
                    "via":  "Custom Field Write"
                })
                # 5d-i. Cross-ref: link to matching analytics report column (NEW)
                for match in cf_to_report_cols.get(cf, []):
                    relationships.append({
                        "from": {"type": "CPM", "name": cpm_name},
                        "to":   {
                            "type": "ReportColumn",
                            "id":   match["report_id"],
                            "name": f"{match['report_name']} → Col {match['col_id']}: {match['label']}"
                        },
                        "via":  f"Custom Field '{cf}' written by CPM → matches report column"
                    })

            # 5e. Custom fields read → CustomField nodes (NEW — was missing entirely)
            for cf in cpm.get("custom_fields_read", []):
                relationships.append({
                    "from": {"type": "CPM", "name": cpm_name},
                    "to":   {"type": "CustomField", "name": cf},
                    "via":  "Custom Field Read"
                })
                # Cross-ref to report columns (NEW)
                for match in cf_to_report_cols.get(cf, []):
                    relationships.append({
                        "from": {"type": "CPM", "name": cpm_name},
                        "to":   {
                            "type": "ReportColumn",
                            "id":   match["report_id"],
                            "name": f"{match['report_name']} → Col {match['col_id']}: {match['label']}"
                        },
                        "via":  f"Custom Field '{cf}' read by CPM → matches report column"
                    })

        elif cpm_format == "cpm_mappings":
            for m in cpm.get("mappings", []):
                p_name   = m.get("procedure")
                obj_name = m.get("object")
                if p_name:
                    relationships.append({
                        "from": {"type": "CPMMappings", "name": "Mappings.xml"},
                        "to":   {"type": "CPM", "name": p_name},
                        "via":  f"Event Routing: {obj_name} ({m.get('interface')} / {m.get('operation')})"
                    })

    # ── 6. Reports → OSVC Tables ───────────────────────────────────────────
    for rep in reports:
        rep_id   = normalise_id(rep.get("id"))
        rep_name = rep.get("name") or f"Report {rep_id}"
        for tbl in rep.get("tables", []):
            alias = tbl.get("alias")
            if alias:
                relationships.append({
                    "from": {"type": "Report", "id": rep_id, "name": rep_name},
                    "to":   {"type": "OSVCObject", "name": alias},
                    "via":  f"Report Table Query ({tbl.get('join_type', 'Primary')})"
                })

    # ── 7. BUI Add-Ins ──────────────────────────────────────────────────
    bui_addins = components.get("buiAddins", [])
    for bui in bui_addins:
        bui_name = bui.get("name", "BUI Add-In")
        for rid in bui.get("report_ids", []):
            str_rid = str(rid)
            ref_rep = reports_by_id.get(str_rid)
            rep_name = ref_rep.get("name") if ref_rep else f"Report {rid}"
            relationships.append({
                "from": {"type": "BUIAddin", "name": bui_name},
                "to":   {"type": "Report", "id": str_rid, "name": rep_name},
                "via":  f"BUI Add-In '{bui_name}' -> Report Dependency (Report ID: {rid})"
            })

        for f in bui.get("osvc_fields_read", []):
            relationships.append({
                "from": {"type": "BUIAddin", "name": bui_name},
                "to":   {"type": "WorkspaceField", "name": f},
                "via":  f"BUI Add-In '{bui_name}' -> Read Field ({f})"
            })

        for f in bui.get("osvc_fields_written", []):
            relationships.append({
                "from": {"type": "BUIAddin", "name": bui_name},
                "to":   {"type": "WorkspaceField", "name": f},
                "via":  f"BUI Add-In '{bui_name}' -> Write Field ({f})"
            })

        for dep in bui.get("external_dependencies", []):
            relationships.append({
                "from": {"type": "BUIAddin", "name": bui_name},
                "to":   {"type": "CustomScript", "name": dep},
                "via":  f"BUI Add-In '{bui_name}' -> Relative Script Dependency ({dep})"
            })

    return relationships
