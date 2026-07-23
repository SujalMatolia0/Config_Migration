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
