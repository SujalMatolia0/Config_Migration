try:
    from .utils import get_all_tabs_flat, normalise_id
except ImportError:
    from utils import get_all_tabs_flat, normalise_id


def detect_orphans(components, relationships):
    """
    Identifies true orphaned OSVC components by cross-referencing against:
    - Graph edges (relationships list: source & target components)
    - Navigation sets
    - CPM Class Mappings
    - BUI Add-Ins (field reads/writes, report dependencies, API calls)
    - Workspace Rules and Custom Scripts
    """
    orphans = []

    workspaces          = components.get("workspaces", [])
    reports             = components.get("reports", [])
    scripts             = components.get("customScripts", [])
    business_rules_list = components.get("businessRules", [])
    nav_sets            = components.get("navigationSets", [])
    cpm_list            = components.get("cpm", [])
    bui_addins          = components.get("buiAddins", [])

    # ── 1. Build comprehensive reference sets ──────────────────────────────
    referenced_workspaces = set()
    referenced_reports    = set()
    referenced_scripts    = set()
    referenced_cpm        = set()

    # From graph edges (both source and target)
    for rel in (relationships or []):
        for comp_key in ["from", "to"]:
            comp = rel.get(comp_key, {})
            c_type = comp.get("type")
            c_name = (comp.get("name") or "").lower()
            c_id   = normalise_id(comp.get("id"))

            if c_type == "Workspace" and c_name:
                referenced_workspaces.add(c_name)
            elif c_type == "Report":
                if c_id: referenced_reports.add(c_id)
                if c_name: referenced_reports.add(c_name)
            elif c_type == "CustomScript" and c_name:
                referenced_scripts.add(c_name)
            elif c_type in ("CPM", "CPMProcedure") and c_name:
                referenced_cpm.add(c_name)

    # From BUI Add-Ins
    for bui in bui_addins:
        for rid in bui.get("report_ids", []):
            referenced_reports.add(str(rid))
        for script_dep in bui.get("external_dependencies", []):
            referenced_scripts.add(script_dep.lower())

    # From CPM Mappings
    cpm_procedures    = [c for c in cpm_list if c.get("format") in ("cpm_procedure", "cpm_php")]
    cpm_mappings_list = [c for c in cpm_list if c.get("format") == "cpm_mappings"]

    mapped_procedure_names = set()
    for cm_file in cpm_mappings_list:
        for m in cm_file.get("mappings", []):
            p = m.get("procedure", "")
            if p:
                mapped_procedure_names.add(p.lower())

    # ── 2. True Workspace Orphans ───────────────────────────────────────────
    # Workspaces in OSVC are primary UI objects. A workspace is an orphan only if unreferenced in multi-workspace instances where Navigation Sets exist.
    if len(workspaces) > 1 and nav_sets:
        for ws in workspaces:
            ws_name = ws.get("name", "")
            if ws_name.lower() not in referenced_workspaces:
                orphans.append({
                    "type":   "Workspace",
                    "name":   ws_name,
                    "reason": "Not referenced by any Navigation Set, CPM handler, or Business Rule"
                })

    # ── 3. True Report Orphans ─────────────────────────────────────────────
    for rep in reports:
        rep_id   = normalise_id(rep.get("id"))
        rep_name = (rep.get("name") or "").lower()

        id_ref   = rep_id in referenced_reports if rep_id else False
        name_ref = rep_name in referenced_reports if rep_name else False

        if not id_ref and not name_ref:
            orphans.append({
                "type":   "Report",
                "name":   rep.get("name") or f"Report ID: {rep_id}",
                "reason": "Not referenced by any Workspace, Script, BUI Add-In, CPM, or Navigation Set"
            })

    # ── 4. True Custom Script Orphans ──────────────────────────────────────
    for scr in scripts:
        scr_name = scr.get("file_name", "")
        if scr_name.lower() not in referenced_scripts:
            orphans.append({
                "type":   "CustomScript",
                "name":   scr_name,
                "reason": "Not imported or called by any Workspace Rule, BUI Add-In, CPM, or Custom Script"
            })

    # ── 5. True CPM Procedure Orphans ──────────────────────────────────────
    for proc in cpm_procedures:
        p_name = proc.get("name") or proc.get("display_name", "")
        if p_name and p_name.lower() not in mapped_procedure_names and p_name.lower() not in referenced_cpm:
            orphans.append({
                "type":   "CPMProcedure",
                "name":   p_name,
                "reason": "Not mapped to any Object Event in Mappings.xml and not referenced in dependency graph"
            })

    return orphans
