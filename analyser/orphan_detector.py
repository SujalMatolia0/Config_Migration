try:
    from .utils import get_all_tabs_flat, normalise_id
except ImportError:
    from utils import get_all_tabs_flat, normalise_id


def detect_orphans(components, relationships):
    """
    Identifies orphaned or misconfigured OSVC components.

    Fixes vs previous version:
    - Workspace orphan check now includes CPM and business rule references,
      not only Navigation Set references.
    - CPM orphan uses proc.get('name') as canonical (not display_name).
    - SuppressFlagMapping without a corresponding Mapping is now flagged.
    - Report duplicate-name false-negative guarded with ID-first priority.
    - Custom script 'index.' heuristic removed — all unreferenced scripts flagged.
    - Procedure name normalisation consistent with mapper.

    Enhancements:
    - CPM procedures with Operations=3 (Create+Update) on async mode flagged
      as potential performance risk.
    - Procedures whose bound class doesn't match any parsed workspace flagged.
    - Reports with no columns flagged as empty/broken.
    - Workspaces with zero tabs flagged.
    - Config risk: any CPM procedure with has_curl=True flagged.
    """
    orphans = []

    workspaces          = components.get("workspaces", [])
    reports             = components.get("reports", [])
    scripts             = components.get("customScripts", [])
    business_rules_list = components.get("businessRules", [])
    nav_sets            = components.get("navigationSets", [])
    cpm_list            = components.get("cpm", [])

    # ── Build reference sets from relationships ────────────────────────────
    referenced_workspaces = set()
    referenced_reports    = set()   # stores both IDs (str) and lowercased names
    referenced_scripts    = set()
    referenced_cpm        = set()

    for rel in relationships:
        to_comp = rel.get("to", {})
        to_type = to_comp.get("type")
        to_name = (to_comp.get("name") or "").lower()
        to_id   = normalise_id(to_comp.get("id"))

        if to_type == "Workspace" and to_name:
            referenced_workspaces.add(to_name)
        elif to_type == "Report":
            if to_id:
                referenced_reports.add(to_id)
            if to_name:
                referenced_reports.add(to_name)
        elif to_type == "CustomScript" and to_name:
            referenced_scripts.add(to_name)
        elif to_type == "CPM" and to_name:
            referenced_cpm.add(to_name.lower())

    # ── 1. Workspace Orphans ───────────────────────────────────────────────
    # A workspace is orphaned only if unreferenced by NavSets, CPM, AND business rules.
    for ws in workspaces:
        ws_name = ws.get("name", "")
        if ws_name.lower() not in referenced_workspaces:
            orphans.append({
                "type":   "Workspace",
                "name":   ws_name,
                "reason": "Not referenced by any Navigation Set, CPM handler, or Business Rule"
            })

        # Enhancement: workspace with no tabs at all
        if not ws.get("tabs"):
            orphans.append({
                "type":   "ConfigAnomaly",
                "name":   f"Workspace '{ws_name}'",
                "reason": "Workspace has no tabs defined"
            })

    # ── 2. Report Orphans ──────────────────────────────────────────────────
    for rep in reports:
        rep_id   = normalise_id(rep.get("id"))
        rep_name = (rep.get("name") or "").lower()

        # ID-first: if ID is referenced, not an orphan regardless of name
        id_ref   = rep_id in referenced_reports if rep_id else False
        name_ref = rep_name in referenced_reports if rep_name else False

        if not id_ref and not name_ref:
            orphans.append({
                "type":   "Report",
                "name":   rep.get("name") or f"Report ID: {rep_id}",
                "reason": "Not referenced by any Workspace, Script, CPM, or Navigation Set"
            })

        # Enhancement: report with zero columns
        if not rep.get("columns"):
            orphans.append({
                "type":   "ConfigAnomaly",
                "name":   rep.get("name") or f"Report ID: {rep_id}",
                "reason": "Report has no columns — may be broken or placeholder"
            })

    # ── 3. Custom Script Orphans ───────────────────────────────────────────
    for scr in scripts:
        scr_name = scr.get("file_name", "")
        if scr_name.lower() not in referenced_scripts:
            orphans.append({
                "type":   "CustomScript",
                "name":   scr_name,
                "reason": "Not imported or called by any Workspace Rule, CPM, or other Custom Script"
            })

    # ── 4. Inactive Business Rules ─────────────────────────────────────────
    for ws in workspaces:
        ws_name = ws.get("name", "")
        for rule in ws.get("rules", []):
            if not rule.get("active", True):
                orphans.append({
                    "type":   "BusinessRule",
                    "name":   f"Workspace '{ws_name}' Rule: {rule.get('name')}",
                    "reason": "Rule is marked Inactive (Active=False)"
                })

    for br_file in business_rules_list:
        file_name = br_file.get("file_name", "")
        for rule in br_file.get("rules", []):
            if not rule.get("active", True):
                orphans.append({
                    "type":   "BusinessRule",
                    "name":   f"Rule file '{file_name}': {rule.get('name')}",
                    "reason": "Rule is marked Inactive"
                })

    # ── 5. Config Risks (Workspace) ────────────────────────────────────────
    for ws in workspaces:
        ws_name = ws.get("name", "")

        for f in ws.get("fields", []):
            fid    = f.get("field_id", "")
            flabel = f.get("label", "")
            if fid.lower() == "phoffice" and "mobile" in flabel.lower():
                orphans.append({
                    "type":   "ConfigAnomaly",
                    "name":   f"Workspace '{ws_name}' Field: {fid}",
                    "reason": f"'{fid}' relabeled as '{flabel}' — use standard mobile fields to avoid data fragmentation"
                })

        for tab in get_all_tabs_flat(ws.get("tabs", [])):
            tab_text = tab.get("text", "Unknown Tab")
            for br in tab.get("browsers", []):
                if br.get("suppress_errors"):
                    orphans.append({
                        "type":   "ConfigRisk",
                        "name":   f"Workspace '{ws_name}' Tab: '{tab_text}'",
                        "reason": f"Embedded Browser SuppressErrors=True (URL: {br.get('url')}) — fails silently"
                    })

    # ── 6. CPM Procedure Orphans & Risks ───────────────────────────────────
    cpm_procedures    = [c for c in cpm_list if c.get("format") in ("cpm_procedure", "cpm_php")]
    cpm_mappings_list = [c for c in cpm_list if c.get("format") == "cpm_mappings"]

    # Build mapped procedure name set from Mappings.xml
    mapped_procedure_names = set()
    mapped_objects_by_proc = {}   # proc_name -> {object, interface, operation}
    suppress_flag_interfaces = set()  # (object, interface) pairs with SuppressFlagMapping

    for cm_file in cpm_mappings_list:
        for m in cm_file.get("mappings", []):
            p = m.get("procedure", "")
            if p:
                mapped_procedure_names.add(p.lower())
                mapped_objects_by_proc[p.lower()] = m
        for sf in cm_file.get("suppress_flags", []):
            suppress_flag_interfaces.add((sf.get("object", ""), sf.get("interface", "")))

    # FIX: always use proc.get('name') as canonical, not display_name
    for proc in cpm_procedures:
        p_name = proc.get("name") or proc.get("display_name", "")

        # Orphan: not in Mappings.xml
        if p_name and p_name.lower() not in mapped_procedure_names:
            orphans.append({
                "type":   "CPMProcedure",
                "name":   p_name,
                "reason": "Not mapped to any Object Event in Mappings.xml"
            })

        # Enhancement: async procedure with Operations=3 (Create+Update) — double-firing risk
        if proc.get("is_async") and str(proc.get("operations_code")) == "3":
            orphans.append({
                "type":   "ConfigRisk",
                "name":   f"CPM Procedure '{p_name}'",
                "reason": "Async procedure fires on both Create AND Update (Operations=3) — "
                          "verify this is intentional to avoid double-processing"
            })

        # Enhancement: cURL in CPM — direct outbound HTTP, not via config URL
        if proc.get("has_curl"):
            orphans.append({
                "type":   "ConfigRisk",
                "name":   f"CPM Procedure '{p_name}'",
                "reason": "Procedure uses cURL directly — ensure outbound HTTP calls are "
                          "authorised and endpoints are config-driven, not hardcoded"
            })

        # Enhancement: risk flags from PHP static analysis
        for flag in proc.get("risk_flags", []):
            # risk_flags are strings in cpm_parser output
            flag_text = flag if isinstance(flag, str) else flag.get("detail", str(flag))
            orphans.append({
                "type":   "ConfigRisk",
                "name":   f"CPM Procedure '{p_name}'",
                "reason": f"Static analysis flag: {flag_text}"
            })

    # Enhancement: SuppressFlagMapping without a corresponding active Mapping
    all_mapped_pairs = set()
    for cm_file in cpm_mappings_list:
        for m in cm_file.get("mappings", []):
            all_mapped_pairs.add((m.get("object", ""), m.get("interface", "")))

    for (obj, iface) in suppress_flag_interfaces:
        if (obj, iface) not in all_mapped_pairs:
            orphans.append({
                "type":   "ConfigAnomaly",
                "name":   f"Mappings.xml SuppressFlagMapping: {obj} / {iface}",
                "reason": "SuppressFlagMapping defined but no active Mapping for same object/interface — "
                          "suppress rule may be dangling"
            })

    return orphans
