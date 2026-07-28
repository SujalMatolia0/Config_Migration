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
def get_detail_filename(node_id):
    safe_name = node_id.replace(":", "_").replace(" ", "_").replace("/", "_").replace("\\", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ("_", "-", "."))
    return f"{safe_name}.json"


def determine_node_module(node_type, data):
    if not data:
        return "Other"
    
    node_type_lower = node_type.lower()
    
    # 1. Check workspace type or name
    if node_type_lower == "workspace":
        t = (data.get("type") or "").lower()
        if "contact" in t: return "Contact"
        if "incident" in t: return "Incident"
        if "org" in t or "organization" in t: return "Organization"
        if "answer" in t: return "Answer"
        
        name = (data.get("name") or "").lower()
        if "contact" in name: return "Contact"
        if "incident" in name: return "Incident"
        if "org" in name or "organization" in name: return "Organization"
        if "answer" in name: return "Answer"
        return "Other"
        
    # 2. Check CPM bindings or osvc_objects
    if node_type_lower == "cpm":
        bound = [str(b).lower() for b in data.get("bound_classes", [])]
        for b in bound:
            if "contact" in b: return "Contact"
            if "incident" in b: return "Incident"
            if "org" in b or "organization" in b: return "Organization"
            if "answer" in b: return "Answer"
            
        objects = [str(o).lower() for o in data.get("osvc_objects", [])]
        for o in objects:
            if "contact" in o: return "Contact"
            if "incident" in o: return "Incident"
            if "org" in o or "organization" in o: return "Organization"
            if "answer" in o: return "Answer"
            
        name = (data.get("name") or data.get("display_name") or data.get("file_name") or "").lower()
        if "contact" in name: return "Contact"
        if "incident" in name: return "Incident"
        if "org" in name or "organization" in name: return "Organization"
        if "answer" in name: return "Answer"
        return "Other"
        
    # 3. Check BUI Add-in fields read/written
    if node_type_lower == "buiaddin":
        fields = [str(f).lower() for f in data.get("osvc_fields_read", []) + data.get("osvc_fields_written", [])]
        for f in fields:
            if f.startswith("contact."): return "Contact"
            if f.startswith("incident."): return "Incident"
            if f.startswith("org.") or f.startswith("organization."): return "Organization"
            if f.startswith("answer."): return "Answer"
            
        name = (data.get("name") or "").lower()
        if "contact" in name: return "Contact"
        if "incident" in name: return "Incident"
        if "org" in name or "organization" in name: return "Organization"
        if "answer" in name: return "Answer"
        return "Other"
        
    # 4. Check Report name or fields
    if node_type_lower == "report":
        name = (data.get("name") or "").lower()
        if "contact" in name: return "Contact"
        if "incident" in name: return "Incident"
        if "org" in name or "organization" in name: return "Organization"
        if "answer" in name: return "Answer"
        
        cols = [str(col.get("field", "")).lower() for col in data.get("columns", [])]
        for col in cols:
            if "contact" in col: return "Contact"
            if "incident" in col: return "Incident"
            if "org" in col or "organization" in col: return "Organization"
            if "answer" in col: return "Answer"
        return "Other"
        
    return "Other"


def make_lightweight_node_data(node_type, data):
    if not data:
        return {}
    if data.get("_fallback"):
        return data

    light = {
        "name": data.get("name"),
        "type": data.get("type"),
        "id": data.get("id"),
        "object_type": data.get("object_type"),
        "script_type": data.get("script_type"),
        "php_version": data.get("php_version"),
        "is_async": data.get("is_async"),
        "operations_label": data.get("operations_label"),
        "entry_point": data.get("entry_point"),
        "module": determine_node_module(node_type, data)
    }

    # Add relative path to report markdown
    lower_type = node_type.lower()
    if lower_type == "workspace" and data.get("name"):
        ws_slug = data["name"].replace(" ", "_")
        light["mdPath"] = f"../workspaces/{ws_slug}/report.md"
    elif lower_type == "report":
        rep_name = (data.get("name") or "Report").replace(" ", "_")
        rep_id = data.get("id") or "doc"
        light["mdPath"] = f"../reports/report_{rep_name}_{rep_id}.md"
    elif lower_type == "cpm":
        light["mdPath"] = "../cpm/report_CPM_Summary.md"
    elif lower_type == "buiaddin" and data.get("name"):
        bname = data["name"].replace(" ", "_")
        light["mdPath"] = f"../scripts/report_{bname}.md"

    # Counts of nested objects for summary UI
    for key in ["tabs", "fields", "rules", "columns", "filters", "soap_actions", "custom_fields_read", "custom_fields_written", "config_vars", "osvc_fields_read", "osvc_fields_written", "api_calls", "modal_views", "lifecycle_listeners", "external_libraries", "hooks", "osvc_objects"]:
        val = data.get(key)
        if val is not None:
            if isinstance(val, list):
                if key in ["hooks", "osvc_objects", "soap_actions", "custom_fields_read", "custom_fields_written", "config_vars", "osvc_fields_read", "osvc_fields_written", "modal_views", "lifecycle_listeners", "external_libraries"]:
                    light[key] = [str(x) for x in val]
                else:
                    light[key] = [None] * len(val)

    if data.get("risk_flags"):
        light["risk_flags"] = [
            r if isinstance(r, str) else (r.get("type") or r.get("detail") or str(r))
            for r in data["risk_flags"]
        ]

    return light


def build_graph(components, relationships, orphans, endpoints):
    """
    Translates parsed components, relationships, endpoints, and orphans
    into a node-and-edge layout for React Flow rendering.
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

        light_data = None
        if extra_data:
            light_data = make_lightweight_node_data(node_type, extra_data)
            if not extra_data.get("_fallback"):
                light_data["detailsPath"] = f"details/{get_detail_filename(node_id)}"

        node_ids.add(node_id)
        nodes.append({
            "id":          node_id,
            "type":        render_type,
            "label":       label,
            "isOrphan":    is_orphan,
            "orphanReason": orphan_reason,
            "data":        light_data or {"_fallback": True}
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

    # ── Edges ──────────────────────────────────────────────────────────────
    SECONDARY_TYPES = {"osvobject", "osvcobject", "customfield", "configsetting", "reportcolumn"}
    seen_edges = set()

    for idx, rel in enumerate(relationships):
        from_type = rel["from"]["type"]
        from_name = rel["from"]["name"]
        from_id   = f"{from_type.lower()}:{from_name.lower()}"

        to_type   = rel["to"]["type"]
        to_target = rel["to"].get("name") or normalise_id(rel["to"].get("id")) or "Unknown"
        to_id     = f"{to_type.lower()}:{to_target.lower()}"

        # Exclude secondary relationship nodes from the global core graph view
        if from_type.lower() in SECONDARY_TYPES or to_type.lower() in SECONDARY_TYPES:
            continue

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
