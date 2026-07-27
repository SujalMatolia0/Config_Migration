import os
try:
    from .utils import normalise_id
except ImportError:
    from utils import normalise_id


def build_graph(components, relationships, orphans, endpoints):
    """
    Translates parsed components, relationships, endpoints, and orphans
    into a node-and-edge layout for React Flow rendering.

    Fixes vs previous version:
    - Node ID uses "Type:name" as the dedup key, preventing cross-type collisions
    - orphans_map keyed by (type, name.lower()) tuple for accurate matching
    - CPM node label uses cpm.get('name') or cpm.get('display_name'), not missing 'class_name'
    - Report node ID normalised to str consistently
    - Fallback nodes from edge loop include a type hint in data dict
    - ReportColumn nodes added for CPM cross-ref relationships

    Enhancements:
    - ConfigSetting nodes for CPM config_vars
    - CustomField nodes aggregated from all CPM read/write relationships
    - Node data includes orphan reason inline for UI tooltip
    - Edge label truncated to 80 chars for UI readability
    - Async CPM procedures get distinct 'asynccpm' type for UI styling
    """
    nodes    = []
    edges    = []
    node_ids = set()   # stores "type:name" lowercase keys

    # FIX: orphans_map keyed by (type.lower(), name.lower()) tuple
    orphans_map = {}
    for o in orphans:
        key = (o.get("type", "").lower(), (o.get("name") or "").lower())
        orphans_map[key] = o

    def _orphan_info(node_type, label):
        """Check if a node is orphaned by type+name lookup."""
        key = (node_type.lower(), label.lower())
        o = orphans_map.get(key)
        if o:
            return True, o.get("reason")
        return False, None

    def add_node(node_type, label, extra_data=None):
        """
        Add a node with dedup key = "type:label" (lowercased).
        Returns the node_id string.
        """
        node_id = f"{node_type.lower()}:{label.lower()}"
        if node_id in node_ids:
            return node_id

        is_orphan, orphan_reason = _orphan_info(node_type, label)

        # Determine render type — async CPM gets own class for diagram styling
        render_type = node_type.lower()
        if node_type == "CPM" and extra_data and extra_data.get("is_async"):
            render_type = "asynccpm"

        node_ids.add(node_id)
        nodes.append({
            "id":          node_id,
            "type":        render_type,
            "label":       label,
            "isOrphan":    is_orphan,
            "orphanReason": orphan_reason,
            "data":        extra_data or {"_fallback": True}
        })
        return node_id

    # ── Component Nodes ────────────────────────────────────────────────────

    for ws in components.get("workspaces", []):
        add_node("Workspace", ws["name"], ws)

    for rep in components.get("reports", []):
        # FIX: normalise ID to str for label
        rep_label = rep.get("name") or f"Report {normalise_id(rep.get('id'))}"
        add_node("Report", rep_label, rep)

    for ns in components.get("navigationSets", []):
        add_node("NavigationSet", ns["name"], ns)

    for br in components.get("businessRules", []):
        for r in br.get("rules", []):
            add_node("BusinessRule", r["name"], r)

    for script in components.get("customScripts", []):
        add_node("CustomScript", script["file_name"], script)

    for cpm in components.get("cpm", []):
        if cpm.get("format") in ("cpm_procedure", "cpm_php"):
            # FIX: use name/display_name, not missing 'class_name'
            label = cpm.get("name") or cpm.get("display_name") or cpm.get("file_name")
            add_node("CPM", label, cpm)
        elif cpm.get("format") == "cpm_mappings":
            add_node("CPMMappings", "Mappings.xml", cpm)

    for ep in endpoints:
        add_node("ExternalEndpoint", ep["url"], ep)

    for bui in components.get("buiAddins", []):
        add_node("BUIAddin", bui.get("name", "BUI Add-In"), bui)

    # ── Relationship-derived Nodes ─────────────────────────────────────────
    for rel in relationships:
        to_type = rel["to"]["type"]
        to_name = rel["to"].get("name") or normalise_id(rel["to"].get("id")) or "Unknown"

        if to_type == "OSVCObject":
            add_node("OSVCObject", to_name)
        elif to_type == "CustomField":
            add_node("CustomField", to_name)
        elif to_type == "ConfigSetting":
            add_node("ConfigSetting", to_name)
        elif to_type == "ReportColumn":
            add_node("ReportColumn", to_name)

    # ── Edges ──────────────────────────────────────────────────────────────
    seen_edges = set()

    for idx, rel in enumerate(relationships):
        from_type = rel["from"]["type"]
        from_name = rel["from"]["name"]
        from_id   = f"{from_type.lower()}:{from_name.lower()}"

        to_type   = rel["to"]["type"]
        to_target = rel["to"].get("name") or normalise_id(rel["to"].get("id")) or "Unknown"
        to_id     = f"{to_type.lower()}:{to_target.lower()}"

        # Add fallback nodes for anything not yet in the graph
        if from_id not in node_ids:
            add_node(from_type, from_name, {"_fallback": True, "_type_hint": from_type})
        if to_id not in node_ids:
            add_node(to_type, to_target, {"_fallback": True, "_type_hint": to_type})

        # Deduplicate edges by (source, target, label) to avoid visual clutter
        edge_key = (from_id, to_id, rel["via"][:40])
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        # Truncate label for UI readability
        via_label = rel["via"]
        if len(via_label) > 80:
            via_label = via_label[:77] + "..."

        edges.append({
            "id":     f"edge-{idx}",
            "source": from_id,
            "target": to_id,
            "label":  via_label
        })

    return {
        "nodes": nodes,
        "edges": edges
    }
