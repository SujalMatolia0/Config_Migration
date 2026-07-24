import json
import os
from analyser.graph_builder import build_graph

def write_master_json(components, relationships, orphans, endpoints, output_file, meta=None):
    """
    Assembles and writes the master JSON representing the OSVC configuration state.
    """
    if meta is None:
        meta = {
            "exportedAt": "2026-07-22",
            "serverVersion": "Oracle Service Cloud Unknown",
            "totalComponents": 0
        }
        
    # Count totals
    total_comps = (
        len(components.get("workspaces", [])) +
        len(components.get("reports", [])) +
        len(components.get("customScripts", [])) +
        len(components.get("cpm", [])) +
        len(components.get("businessRules", [])) +
        len(components.get("navigationSets", [])) +
        len(components.get("workflows", [])) +
        len(components.get("templates", []))
    )
    meta["totalComponents"] = total_comps

    # Try to extract actual server version from parsed workspaces
    if components.get("workspaces"):
        for ws in components["workspaces"]:
            if ws.get("server_version"):
                meta["serverVersion"] = ws["server_version"]
                break

    summary = {
        "workspaces": len(components.get("workspaces", [])),
        "reports": len(components.get("reports", [])),
        "customScripts": len(components.get("customScripts", [])),
        "cpmHandlers": len(components.get("cpm", [])),
        "businessRules": len(components.get("businessRules", [])),
        "navigationSets": len(components.get("navigationSets", [])),
        "orphanedComponents": [f"{o.get('type')}: {o.get('name')}" for o in orphans],
        "externalEndpoints": [e.get("url") for e in endpoints]
    }

    graph_data = build_graph(components, relationships, orphans, endpoints)

    master_data = {
        "meta": meta,
        "summary": summary,
        "components": {
            "workspaces": components.get("workspaces", []),
            "reports": components.get("reports", []),
            "customScripts": components.get("customScripts", []),
            "cpm": components.get("cpm", []),
            "businessRules": components.get("businessRules", []),
            "navigationSets": components.get("navigationSets", []),
            "workflows": components.get("workflows", []),
            "templates": components.get("templates", [])
        },
        "relationships": relationships,
        "orphans": orphans,
        "endpoints": endpoints,
        "graph": graph_data
    }

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)

    return master_data


def write_index_json(workspaces, output_file, shared_reports=None):
    """
    Writes structured JSON representation of the Workspace Index.
    """
    ws_items = []
    for ws in workspaces:
        ws_name = ws.get("name", "Unknown")
        ws_slug = ws_name.replace(" ", "_")
        ws_items.append({
            "name": ws_name,
            "slug": ws_slug,
            "tabsCount": len(ws.get("tabs", [])),
            "fieldsCount": len(ws.get("fields", [])),
            "rulesCount": len(ws.get("rules", [])),
            "reportMarkdownPath": f"workspaces/{ws_slug}/report.md",
            "reportJsonPath": f"workspaces/{ws_slug}/report.json",
            "reportHtmlPath": f"workspaces/{ws_slug}/report.html"
        })

    index_data = {
        "title": "OSVC Configuration Workspace Index",
        "totalWorkspaces": len(workspaces),
        "workspaces": ws_items,
        "sharedReports": shared_reports or []
    }

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    return index_data


def write_cpm_summary_json(cpm_items, orphans, workspaces, output_file):
    """
    Writes structured JSON representation of the CPM Summary Report.
    """
    objects_covered = set()
    sync_cnt = 0
    async_cnt = 0

    for p in cpm_items:
        for b in p.get("bound_classes", []):
            objects_covered.add(b)
        if p.get("is_async"):
            async_cnt += 1
        else:
            sync_cnt += 1

    cpm_data = {
        "title": "CPM Custom Process Model Summary Report",
        "summary": {
            "totalProcedures": len(cpm_items),
            "objectsCovered": sorted(list(objects_covered)),
            "synchronousProcedures": sync_cnt,
            "asynchronousProcedures": async_cnt,
            "orphanProcedures": len(orphans)
        },
        "procedures": cpm_items
    }

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cpm_data, f, indent=2, ensure_ascii=False)

    return cpm_data


def write_bui_addin_summary_json(bui_addins, reports, workspaces, output_file):
    """
    Writes structured JSON representation of all BUI Add-Ins Summary Report.
    """
    bui_summary_data = {
        "title": "BUI Browser UI Add-In Summary Report",
        "totalAddinsAnalyzed": len(bui_addins),
        "addins": bui_addins
    }

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bui_summary_data, f, indent=2, ensure_ascii=False)

    return bui_summary_data


def write_single_bui_addin_json(bui, reports, workspaces, output_file):
    """
    Writes structured JSON representation for a single BUI Add-In.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bui, f, indent=2, ensure_ascii=False)

    return bui


def write_analytics_report_json(report_item, output_file):
    """
    Writes structured JSON representation for an Analytics Core report.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report_item, f, indent=2, ensure_ascii=False)

    return report_item


def write_workspace_report_json(ws_item, output_file):
    """
    Writes structured JSON representation for a single Workspace.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ws_item, f, indent=2, ensure_ascii=False)

    return ws_item
