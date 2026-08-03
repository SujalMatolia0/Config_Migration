import os
from collections import defaultdict, Counter
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

    # Explicit custom object binding or object type hint
    obj_hint = data.get("object") or data.get("object_type") or data.get("module")
    if obj_hint and isinstance(obj_hint, str) and obj_hint not in ("Other", "None", "Unknown"):
        clean_obj = obj_hint.strip()
        if clean_obj.lower().startswith("object"):
            clean_obj = clean_obj[6:]
        return clean_obj

    # Searchable text dump from data dictionary
    search_text = []
    for key in ["name", "file_name", "id", "label", "url", "entry_point", "script_type", "type"]:
        val = data.get(key)
        if val and isinstance(val, str):
            search_text.append(val.lower())

    for key in ["osvc_objects", "osvc_fields_read", "osvc_fields_written", "custom_fields_read", "custom_fields_written", "bound_classes", "columns", "fields", "imports"]:
        val = data.get(key)
        if val and isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    search_text.append(item.lower())
                elif isinstance(item, dict):
                    search_text.append(str(item).lower())

    full_blob = " ".join(search_text)

    # 1. Contact Module
    if any(k in full_blob for k in ["contact", "rncphp\\contact", "contact.org_id", "contact_create", "contact_update", "contactasync", "duplicate_contacts", "registercontact", "call", "sms"]):
        return "Contact"

    # 2. Incident Module
    if any(k in full_blob for k in ["incident", "rncphp\\incident", "child_incident", "duplicate_incidents", "closing_notes", "bluebox_greencart", "cityworks", "addsr", "sr_number", "incident_create", "incident_routing", "clock", "validation"]):
        return "Incident"

    # 3. Organization Module
    if any(k in full_blob for k in ["organization", "org_id", "rncphp\\organization", "getaccounts", "account", "siebel"]):
        return "Organization"

    # 4. Check for explicit custom object keywords (e.g. test_record)
    if "test_record" in full_blob or "testrecord" in full_blob:
        return "Test_Record"

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
    if data.get("mdPath"):
        light["mdPath"] = data["mdPath"]
    else:
        lower_type = node_type.lower()
        if lower_type == "workspace" and data.get("name"):
            ws_slug = data["name"].replace(" ", "_")
            light["mdPath"] = f"../workspaces/{ws_slug}/report.md"
        elif lower_type == "report":
            rep_name = (data.get("name") or "Report").replace(" ", "_")
            light["mdPath"] = f"../reports/report_{rep_name}.md"
        elif lower_type in ["cpm", "cpmmappings"]:
            light["mdPath"] = "../cpm/report_CPM_Summary.md"
        elif lower_type in ["buiaddin", "bui_addin"] and (data.get("name") or data.get("id")):
            bname = data.get("name") or data.get("id")
            light["mdPath"] = f"../bui_addins/report_{bname}.md"
        elif lower_type in ["customscript", "custom_script", "script"] and (data.get("file_name") or data.get("name")):
            sname = data.get("file_name") or data.get("name")
            light["mdPath"] = f"../scripts/report_{sname}.md"

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
            if "name" not in extra_data:
                extra_data["name"] = label
            if "label" not in extra_data:
                extra_data["label"] = label
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
    seen_edges = set()
    SECONDARY_TYPES = {"osvobject", "osvcobject", "customfield", "configsetting", "reportcolumn"}

    def _get_workspace_fields(ws):
        ws_fields = list(ws.get("fields", []))
        def _scan_tabs(tabs_list):
            for t in tabs_list:
                ws_fields.extend(t.get("fields", []))
                for ts in t.get("nested_tabsets", []):
                    for sub_t in ts.get("sub_tabs", []):
                        _scan_tabs([sub_t])
        _scan_tabs(ws.get("tabs", []))
        return ws_fields

    for ws in components.get("workspaces", []):
        ws_data = dict(ws)
        ws_data["mdPath"] = f"../workspaces/{ws['name'].replace(' ', '_')}/report.md"
        ws_node_id = add_node("Workspace", ws["name"], ws_data)
        ws_mod = ws.get("module") or ws.get("object_type") or ws["name"]

        ws_fields = _get_workspace_fields(ws)
        for f in ws_fields:
            fname = f.get("field_id") or f.get("label") or f.get("name")
            if fname and str(fname).strip():
                field_node_id = add_node("WorkspaceField", fname, {
                    "name": fname,
                    "object": ws_mod,
                    "module": ws_mod,
                    "object_type": ws_mod,
                    "workspace": ws["name"],
                    "field_id": fname,
                    "data": f
                })
                edge_key = (ws_node_id, field_node_id, "field")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({
                        "id": f"edge-ws-field-{len(edges)}",
                        "source": ws_node_id,
                        "target": field_node_id,
                        "label": "field"
                    })

    for rep in components.get("reports", []):
        rep_label = rep.get("name") or f"Report {normalise_id(rep.get('id'))}"
        rep_clean = rep_label.replace(" ", "_")
        rep_data = dict(rep)
        rep_data["mdPath"] = f"../reports/report_{rep_clean}.md"
        add_node("Report", rep_label, rep_data)

    for ns in components.get("navigationSets", []):
        add_node("NavigationSet", ns["name"], ns)

    # Group rules by Object for canvas hub nodes
    object_br_groups = defaultdict(list)
    for br in components.get("businessRules", []):
        for r in br.get("rules", []):
            obj = r.get("object") or "Incident"
            if obj.lower() in ["contacts", "contact"]:
                obj = "Contact"
            elif obj.lower() in ["incidents", "incident"]:
                obj = "Incident"
            elif obj.lower() in ["organizations", "organization", "org"]:
                obj = "Organization"
            object_br_groups[obj].append(r)

    if not object_br_groups and components.get("businessRules"):
        object_br_groups["Incident"] = []

    for obj_name, obj_rules in object_br_groups.items():
        hub_label = f"{obj_name} Business Rules"
        act_type_counts = Counter()
        for r in obj_rules:
            for atype in r.get("actions_by_type", {}):
                act_type_counts[atype] += 1

        add_node("BusinessRule", hub_label, {
            "name": hub_label,
            "type": "BusinessRule",
            "object": obj_name,
            "total_rules": len(obj_rules),
            "action_type_breakdown": dict(act_type_counts),
            "rules": obj_rules,
            "mdPath": f"../rules/report_Business_Rules_{obj_name}.md"
        })

    for script in components.get("customScripts", []):
        s_name = script.get("file_name", "script.php")
        s_data = dict(script)
        s_data["mdPath"] = f"../scripts/report_{s_name}.md"
        add_node("CustomScript", s_name, s_data)

    for cpm in components.get("cpm", []):
        cpm_data = dict(cpm)
        cpm_data["mdPath"] = "../cpm/report_CPM_Summary.md"
        if cpm.get("format") in ("cpm_procedure", "cpm_php"):
            label = cpm.get("name") or cpm.get("display_name") or cpm.get("file_name")
            add_node("CPM", label, cpm_data)
        elif cpm.get("format") == "cpm_mappings":
            add_node("CPMMappings", "Mappings.xml", cpm_data)

    for ep in endpoints:
        add_node("ExternalEndpoint", ep["url"], ep)

    for bui in components.get("buiAddins", []):
        b_name = bui.get("name", "BUI Add-In")
        b_data = dict(bui)
        b_data["mdPath"] = f"../bui_addins/report_{b_name}.md"
        add_node("BUIAddin", b_name, b_data)

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
            add_node(from_type, from_name, {"_fallback": True, "_type_hint": from_type, "name": from_name})
        if to_id not in node_ids:
            add_node(to_type, to_target, {"_fallback": True, "_type_hint": to_type, "name": to_target})

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

    # Filter out unmapped floating BusinessRule nodes that have 0 edges on the graph
    active_edge_node_ids = {e["source"] for e in edges} | {e["target"] for e in edges}
    final_nodes = [
        n for n in nodes
        if n.get("type") != "businessrule"
        or n.get("label") == "Business Rules"
        or n.get("id") in active_edge_node_ids
    ]

    return {
        "nodes": final_nodes,
        "edges": edges
    }
