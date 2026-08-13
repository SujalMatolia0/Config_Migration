import os
import json
from datetime import datetime

def canonical_module_name(name):
    """Normalizes object module names into canonical primary entity roots."""
    if not name:
        return "General / Unassigned"
    s = str(name).strip()
    if s.startswith("../../"):
        return "General / Unassigned"
    parts = s.split(".")
    base = parts[0]
    if base.lower().startswith("c$"):
        base = base[2:]
    low = base.lower()
    if low in ["contact", "contacts"]:
        return "Contact"
    elif low in ["incident", "incidents"]:
        return "Incident"
    elif low in ["organization", "organizations", "org"]:
        return "Organization"
    elif low in ["test_record", "testrecord"]:
        return "Test_Record"
    elif low in ["other", "unknown", "none"]:
        return "General / Unassigned"
    return base.capitalize() if len(base) > 2 else base

def format_component_ref(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        ctype = obj.get("type") or "Component"
        name = obj.get("name") or obj.get("file_name") or obj.get("id") or "Unnamed"
        if ctype == "Report":
            rid = obj.get("id")
            rname = obj.get("name")
            return f"Report {rid} ({rname})" if rid and rname and rname != f"Report {rid}" else f"Report {rid or name}"
        return f"{ctype}: {name}"
    return str(obj)

def format_rel_type(rel):
    rtype = rel.get("type") or rel.get("label") or "Linkage"
    if isinstance(rel.get("target"), dict):
        tgt_type = rel["target"].get("type")
        if tgt_type == "Report":
            return "References Report"
        elif tgt_type == "ExternalEndpoint":
            return "Calls External Endpoint"
        elif tgt_type == "CustomScript":
            return "Triggers Custom Script"
        elif tgt_type == "CPM":
            return "Invokes CPM Handler"
    return str(rtype).replace("_", " ").title()

def build_details_summary(node, use_ai_summary=True):
    """Builds a rich, descriptive details summary string for any component node."""
    ntype = (node.get("type") or "").lower()
    data = node.get("data") or {}
    label = node.get("label") or ""

    if ntype == "workspace":
        tabs = len(data.get("tabs", []))
        fields = len(data.get("fields", []))
        rules = len(data.get("rules", []))
        obj = data.get("object_type") or data.get("module") or "Unknown"
        return f"Bound Object: `{obj}` | {fields} fields, {tabs} tabs, {rules} rules"

    elif ntype == "report":
        ac_id = data.get("ac_id") or data.get("id") or "-"
        cols = len(data.get("columns", []))
        tables = len(data.get("tables", []))
        return f"Report AC_ID: `{ac_id}` | {cols} columns, {tables} tables joined"

    elif ntype in ["cpm", "asynccpm"]:
        ops = data.get("operations_label") or data.get("script_type") or "Event Handler"
        is_async = "Async Execution" if data.get("is_async") or ntype == "asynccpm" else "Synchronous Execution"
        entry = data.get("entry_point") or "ObjectProcedure::apply"
        res = f"Trigger: `{ops}` | {is_async} | Entry: `{entry}`"
        if use_ai_summary and data.get("key_logic"):
            res += f" | **AI Logic Summary**: {data.get('key_logic')}"
        return res

    elif ntype == "customscript":
        fname = data.get("file_name") or label
        funcs = len(data.get("functions", []))
        soaps = ", ".join(data.get("soap_actions", [])) if data.get("soap_actions") else ""
        soap_str = f" | SOAP: `{soaps}`" if soaps else ""
        return f"PHP Script: `{fname}` | {funcs} functions{soap_str}"

    elif ntype == "buiaddin":
        bname = data.get("name") or label
        entry = data.get("entry_point") or "main.js"
        reads = len(data.get("osvc_fields_read", []))
        writes = len(data.get("osvc_fields_written", []))
        return f"BUI Extension: `{bname}` | Entry: `{entry}` | Reads: {reads}, Writes: {writes}"

    elif ntype in ["workspacefield", "customfield"]:
        is_custom = "Custom Field (c$)" if "c$" in label.lower() or ntype == "customfield" else "Standard Field"
        ftype = data.get("type") or "Data Field"
        return f"{is_custom} | Data Type: `{ftype}`"

    elif ntype in ["object", "module_root"]:
        return "Primary OSVC Entity Module Schema Root"

    return f"OSVC Component ID: `{node.get('id', '')}`"


def generate_mermaid_for_module(mod_name, mod_nodes, degree_map):
    """Generates a structured Mermaid flowchart for a specific module."""
    import re
    safe_m = "MOD_" + re.sub(r'[^a-zA-Z0-9_]', '_', str(mod_name))
    lines = ["```mermaid", "flowchart TD"]
    lines.append(f'  subgraph Sub_{safe_m} ["Entity Module: {mod_name}"]')
    
    # Filter key nodes (limit to top 12 for clean visual layout)
    key_nodes = mod_nodes[:12]
    node_id_map = {}
    for n in key_nodes:
        nid = "N_" + re.sub(r'[^a-zA-Z0-9_]', '_', str(n.get("id", "")))
        nlabel = str(n.get("label", "")).replace('"', "'")
        ntype = n.get("type", "")
        node_id_map[n.get("id")] = nid
        lines.append(f'    {nid}["{nlabel} ({ntype})"]')

    # Add edges between key nodes in module
    for n in key_nodes:
        nid = node_id_map.get(n.get("id"))
        for out_edge in n.get("out", []):
            tgt_id = out_edge.get("target")
            if tgt_id in node_id_map:
                tgt_nid = node_id_map[tgt_id]
                elbl = out_edge.get("label", "")
                lbl_str = f'|"{elbl}"|' if elbl else ""
                lines.append(f'    {nid} -->{lbl_str} {tgt_nid}')

    lines.append("  end")
    lines.append("```")
    return "\n".join(lines)


def generate_master_system_report(results_dir, master_data, components=None, orphans=None, endpoints=None, relationships=None, use_ai_summary=True):
    """
    Generates a single, unified master system mapping markdown report (system_mappings/report_Master_System_Mapping.md)
    consolidating all workspaces, objects, CPMs, scripts, BUI add-ins, and cross-component mappings.
    """
    mappings_dir = os.path.join(results_dir, "system_mappings")
    os.makedirs(mappings_dir, exist_ok=True)
    report_path = os.path.join(mappings_dir, "report_Master_System_Mapping.md")
    
    meta = master_data.get("metadata", {}) or master_data.get("meta", {})
    nodes = master_data.get("graph", {}).get("nodes", [])
    edges = master_data.get("graph", {}).get("edges", [])
    
    # Calculate degree linkage counts for nodes
    degree_map = {}
    node_by_id = {}
    for n in nodes:
        node_by_id[n.get("id")] = n
        n["inc"] = []
        n["out"] = []

    for e in edges:
        s, t = e.get("source"), e.get("target")
        degree_map.setdefault(s, {"in": 0, "out": 0})["out"] += 1
        degree_map.setdefault(t, {"in": 0, "out": 0})["in"] += 1
        if s in node_by_id: node_by_id[s]["out"].append(e)
        if t in node_by_id: node_by_id[t]["inc"].append(e)

    all_orphans = orphans or master_data.get("orphans", [])
    all_endpoints = endpoints or master_data.get("endpoints", [])

    if not all_endpoints and components:
        all_endpoints = []
        for cs in components.get("customScripts", []):
            for url in cs.get("endpoints", []):
                all_endpoints.append({
                    "url": url,
                    "source_file": f"customscript:{cs.get('file_name', 'script.php')}",
                    "context": f"cURL / HTTP REST Request in {cs.get('file_name')}"
                })
        for bui in components.get("buiAddins", []):
            for call in bui.get("api_calls", []):
                all_endpoints.append({
                    "url": str(call),
                    "source_file": f"buiaddin:{bui.get('name', 'BUIAddin')}",
                    "context": f"BUI Extension API Integration in {bui.get('name')}"
                })

    lines = []
    lines.append("# Complete System Architecture & Component Mapping")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Source Data Path**: `{meta.get('source_path', 'input')}`  ")
    lines.append("")
    
    # 1. Executive Summary Table
    num_ws = len([n for n in nodes if n.get("type") == "workspace"])
    num_rep = len([n for n in nodes if n.get("type") == "report"])
    num_cpm = len([n for n in nodes if n.get("type") in ["cpm", "asynccpm"]])
    num_scr = len([n for n in nodes if n.get("type") == "customscript"])
    num_bui = len([n for n in nodes if n.get("type") == "buiaddin"])
    num_obj = len([n for n in nodes if n.get("type") in ["object", "module_root"]])
    num_br = len(components.get("businessRules", [])) if components else 0
    total_br_rules = sum(b.get("total_rules", len(b.get("rules", []))) for b in components.get("businessRules", [])) if components else 0

    lines.append("## Executive System Summary & Risk Overview")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> **System Mapping Overview**: Structured inventory of all parsed Oracle Service Cloud workspaces, analytics reports, CPM procedures, business rules, custom scripts, and external REST/SOAP integration endpoints.")
    lines.append("")

    lines.append("| Component Category | Total Discovered Count | Status |")
    lines.append("| :--- | :---: | :--- |")
    lines.append(f"| Workspaces | {num_ws} | Parsed & Mapped |")
    lines.append(f"| Analytics Reports | {num_rep} | Parsed & Mapped |")
    lines.append(f"| Business Rules Sets | {num_br} ({total_br_rules} Rules) | Parsed & Policy Mapped |")
    lines.append(f"| CPM Procedures & Handlers | {num_cpm} | Parsed & Event Mapped |")
    lines.append(f"| PHP Custom Scripts | {num_scr} | Analyzed |")
    lines.append(f"| BUI Add-Ins | {num_bui} | Archive Extracted |")
    lines.append(f"| Custom Objects & Entities | {num_obj} | Schema Mapped |")
    lines.append(f"| External Integration Endpoints | {len(all_endpoints)} | Endpoint Extracted |")
    lines.append(f"| Orphaned Components | {len(all_orphans)} | Audit Flagged |")
    lines.append("")

    # Aggregate Unhandled XML Elements across all components
    master_unhandled = []
    if components:
        for cat in ["workspaces", "reports", "cpm", "businessRules", "navigationSets", "buiAddins", "customObjects", "objectRelationships"]:
            for item in components.get(cat, []):
                unk = item.get("unknowns", {})
                u_children = unk.get("unknown_children", []) or item.get("unhandled_elements", []) or item.get("raw_unhandled_tags", [])
                u_attrs = unk.get("unknown_attrs", [])
                iname = item.get("name") or item.get("file_name") or "Component"
                for ch in u_children:
                    master_unhandled.append({
                        "comp": iname,
                        "tag": ch.get("tag") or "unknown",
                        "snippet": ch.get("raw") or ch.get("raw_xml") or ch.get("snippet") or ""
                    })
                for at in u_attrs:
                    master_unhandled.append({
                        "comp": iname,
                        "tag": f"attr:{at.get('attribute')}",
                        "snippet": str(at.get("value"))
                    })

    # Structured Alert Boxes
    if master_unhandled:
        seen_master_map = {}
        for item in master_unhandled:
            comp_name = item.get("comp") or "Component"
            tag_str = item.get("tag") or "unknown"
            snip_str = (item.get("snippet") or "").replace("\n", " ").replace("\r", "").strip()[:100]
            key = (comp_name, tag_str, snip_str)
            seen_master_map[key] = seen_master_map.get(key, 0) + 1

        lines.append("> [!WARNING]")
        lines.append(f"> **{len(seen_master_map)} Unique Unhandled Schema Element(s) Captured**: Raw XML elements/attributes present in source export were preserved via universal fallback handling.")
        lines.append("")
        lines.append("| Component | Tag / Attribute | Raw Snippet / Value | Occurrences |")
        lines.append("| :--- | :--- | :--- | :---: |")
        for (comp_name, tag_str, snip_str), count in seen_master_map.items():
            lines.append(f"| `{comp_name}` | `<{tag_str}>` | `{snip_str}` | `{count}` |")
        lines.append("")
    if all_orphans:
        lines.append("> [!WARNING]")
        lines.append(f"> **{len(all_orphans)} Orphaned Component(s) Flagged**: Custom scripts or components exist in dataset with zero active workspace or CPM bindings.")
        lines.append("")
    if all_endpoints:
        lines.append("> [!IMPORTANT]")
        lines.append(f"> **{len(all_endpoints)} External HTTP Integration Endpoints Detected**: Outbound web calls to external REST/SOAP servers require security verification.")
        lines.append("")

    lines.append("> [!TIP]")
    lines.append("> **Optimization Recommendation**: Review orphaned scripts to reclaim workspace performance and audit outbound endpoints for TLS verification.")
    lines.append("")

    # 2. Audit-Critical Orphaned Components Section
    lines.append("## Audit-Critical Orphaned Components")
    lines.append("")
    if all_orphans:
        lines.append("| Component Name / ID | Type | Associated Object | Linkage Count | Audit Risk Flag & Reason |")
        lines.append("| :--- | :--- | :--- | :---: | :--- |")
        for o in all_orphans:
            oname = o.get("name") or o.get("id") or o.get("file_name") or "Unnamed"
            otype = o.get("type") or "Component"
            oobj = canonical_module_name(o.get("object") or o.get("module") or "General")
            oreason = o.get("reason") or "Zero active inbound/outbound references detected"
            deg = degree_map.get(o.get("id", ""), {"in": 0, "out": 0})
            link_str = f"{deg['in']} in, {deg['out']} out"
            lines.append(f"| `{oname}` | `{otype}` | **{oobj}** | `{link_str}` | `{oreason}` |")
    else:
        lines.append("*No orphaned components detected. All components are actively referenced.*")
    lines.append("")

    # 3. Consolidated Entity Module Inventory
    lines.append("## Consolidated Entity Module Inventory")
    lines.append("")
    
    grouped_modules = {}
    for n in nodes:
        raw_mod = n.get("module") or n.get("data", {}).get("module") or n.get("data", {}).get("object") or n.get("label")
        cmod = canonical_module_name(raw_mod)
        if cmod not in grouped_modules:
            grouped_modules[cmod] = []
        grouped_modules[cmod].append(n)
        
    for mod_name, mod_nodes in sorted(grouped_modules.items()):
        lines.append(f"### Entity Module: {mod_name} ({len(mod_nodes)} Mapped Components)")
        lines.append("")
        
        # Only generate flowchart diagram if module contains more than 1 component node
        if len(mod_nodes) > 1:
            lines.append(f"#### Module Flowchart: {mod_name}")
            lines.append("")
            lines.append("```mermaid")
            lines.append("flowchart LR")
            safe_m = "MOD_" + "".join([c if c.isalnum() else "_" for c in mod_name])
            lines.append(f'  subgraph {safe_m} ["Module: {mod_name}"]')
            
            key_nodes = mod_nodes[:6]
            n_id_map = {}
            for kn in key_nodes:
                knid = "N_" + "".join([c if c.isalnum() else "_" for c in str(kn.get("id", ""))])
                knlbl = str(kn.get("label", "")).replace('"', "'")
                kntype = kn.get("type", "")
                n_id_map[kn.get("id")] = knid
                lines.append(f'    {knid}["{knlbl} ({kntype})"]')

            for kn in key_nodes:
                knid = n_id_map.get(kn.get("id"))
                for out_e in kn.get("out", []):
                    tgt_id = out_e.get("target")
                    if tgt_id in n_id_map:
                        tgt_knid = n_id_map[tgt_id]
                        elbl = out_e.get("label", "")
                        lbl_s = f'|"{elbl}"|' if elbl else ""
                        lines.append(f'    {knid} -->{lbl_s} {tgt_knid}')
            lines.append("  end")
            lines.append("```")
            lines.append("")

        lines.append("| Component ID / Name | Type | Dependencies (In -> Out) | Details & Execution Context |")
        lines.append("| :--- | :--- | :---: | :--- |")
        
        type_order = {"object": 0, "module_root": 0, "workspace": 1, "report": 2, "cpm": 3, "asynccpm": 3, "customscript": 4, "buiaddin": 5, "workspacefield": 6, "customfield": 7}
        sorted_nodes = sorted(mod_nodes, key=lambda x: (type_order.get((x.get("type") or "").lower(), 99), str(x.get("label")).lower()))
        
        for n in sorted_nodes:
            nid = n.get("id", "")
            ntype = n.get("type", "")
            nlabel = n.get("label", "")
            deg = degree_map.get(nid, {"in": 0, "out": 0})
            dep_str = f"`{deg['in']} in -> {deg['out']} out`"
            details = build_details_summary(n, use_ai_summary=use_ai_summary)
            lines.append(f"| `{nlabel}` | `{ntype}` | {dep_str} | {details} |")
        
        lines.append("")

    # 4. Workspaces & Field Mapping Matrix
    lines.append("## Workspaces & Field Mapping Matrix")
    lines.append("")
    ws_items = components.get("workspaces", []) if components else []
    if not ws_items:
        ws_nodes = [n for n in nodes if n.get("type") == "workspace"]
        ws_items = [n.get("data", {}) for n in ws_nodes if n.get("data")]

    from src.output.markdown_generator import collect_all_workspace_fields

    if ws_items:
        for ws in sorted(ws_items, key=lambda x: x.get("name", "")):
            wname = ws.get("name") or "Workspace"
            wobj = canonical_module_name(ws.get("object_type") or ws.get("module"))
            fields = collect_all_workspace_fields(ws)
            tabs = len(ws.get("tabs", []))
            rules = len(ws.get("rules", []))
            
            lines.append(f"### Workspace: {wname}")
            lines.append(f"- **Primary Object Binding**: **{wobj}**")
            lines.append(f"- **Layout Summary**: {len(fields)} form fields used across {tabs} tabsets ({rules} rules)")
            lines.append("")
            if fields:
                lines.append("| Field Name / ID | Custom Field (c$) | Parent Location / Tab | Dependencies |")
                lines.append("| :--- | :---: | :--- | :---: |")
                for f in fields:
                    fid = f.get("field_id") or f.get("label") or "Unnamed"
                    is_c = "Yes (c$)" if f.get("is_custom") else "No"
                    tab_name = f.get("location") or "Top-level Layout"
                    f_node_id = f"workspacefield:{str(fid).lower()}"
                    f_deg = degree_map.get(f_node_id, {"in": 0, "out": 0})
                    f_link = f"`{f_deg['in']} in -> {f_deg['out']} out`"
                    lines.append(f"| `{fid}` | {is_c} | {tab_name} | {f_link} |")
            lines.append("")
    else:
        lines.append("*No Workspace XML configuration files detected in dataset.*")
    lines.append("")

    # 5. CPM Event Handlers & Procedures Matrix
    lines.append("## CPM Event Handlers & Procedures Matrix")
    lines.append("")
    cpm_items = components.get("cpm", []) if components else []
    if not cpm_items:
        cpm_nodes = [n for n in nodes if n.get("type") in ["cpm", "asynccpm"]]
        cpm_items = [n.get("data", {}) for n in cpm_nodes if n.get("data")]

    if cpm_items:
        lines.append("| CPM Handler / XML | Object Binding | Event Trigger | Execution Mode | Entry Point Method | Dependencies |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :---: |")
        for c in cpm_items:
            name = c.get("name") or c.get("file_name") or "Unnamed"
            obj = canonical_module_name(c.get("object_type") or c.get("module"))
            evt = c.get("operations_label") or c.get("script_type") or "Event Handler"
            is_a = "Async Execution" if c.get("is_async") else "Synchronous Execution"
            entry = c.get("entry_point") or "ObjectProcedure::apply"
            c_id = f"cpm:{str(name).lower()}"
            c_deg = degree_map.get(c_id, {"in": 0, "out": 0})
            c_link = f"`{c_deg['in']} in -> {c_deg['out']} out`"
            lines.append(f"| `{name}` | **{obj}** | `{evt}` | {is_a} | `{entry}` | {c_link} |")
    else:
        lines.append("*No CPM Procedures or Handlers detected in dataset.*")
    lines.append("")

    # 6. Consolidated Integration Endpoints Catalog
    lines.append("## Consolidated Integration Endpoints Catalog")
    lines.append("")
    if all_endpoints:
        lines.append("| Target Endpoint URL | Source Component / File | HTTP / Protocol Context | Extracted Code Snippet / Detail |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for ep in all_endpoints:
            url = ep.get("url") or ep.get("endpoint") or ""
            src = ep.get("source_file") or ep.get("file") or "Unknown Script"
            ctx = ep.get("context") or ep.get("protocol") or "REST API / HTTP Call"
            code_ctx = ep.get("code_snippet") or ep.get("detail") or "cURL Outbound Request"
            lines.append(f"| `{url}` | `{src}` | `{ctx}` | {code_ctx} |")
    else:
        lines.append("*No external HTTP/REST API endpoints detected in custom scripts.*")
    lines.append("")

    # 7. System Component Mappings & Linkages Matrix
    lines.append("## System Component Mappings & Linkages Matrix")
    lines.append("")
    rel_list = relationships if relationships else []
    if rel_list:
        seen = set()
        grouped = {
            "Workspaces Inventory": [],
            "CPM Event Procedures": [],
            "BUI Add-Ins & Extensions": [],
            "Custom PHP Procedural Scripts": [],
            "Other Cross-Component Linkages": []
        }
        for r in rel_list:
            src_obj = r.get("source") or r.get("from") or {}
            tgt_obj = r.get("target") or r.get("to") or {}
            
            src_str = format_component_ref(src_obj)
            tgt_str = format_component_ref(tgt_obj)

            # Omit dummy Report 0 references
            if "Report 0" in tgt_str or "Report 0" in src_str or "report 0" in tgt_str.lower():
                continue

            rtype_str = format_rel_type(r)
            ctx = r.get("context") or r.get("details") or "Cross-Component Mapping"

            # Deduplicate rows
            key = (src_str, rtype_str, tgt_str, ctx)
            if key in seen:
                continue
            seen.add(key)

            entry = {"source": src_str, "type": rtype_str, "target": tgt_str, "context": ctx}
            src_low = src_str.lower()
            if "workspace" in src_low:
                grouped["Workspaces Inventory"].append(entry)
            elif "cpm" in src_low or "handler" in src_low or "procedure" in src_low:
                grouped["CPM Event Procedures"].append(entry)
            elif "bui" in src_low or "addin" in src_low:
                grouped["BUI Add-Ins & Extensions"].append(entry)
            elif "script" in src_low or "php" in src_low:
                grouped["Custom PHP Procedural Scripts"].append(entry)
            else:
                grouped["Other Cross-Component Linkages"].append(entry)

        has_any = False
        for category, items in grouped.items():
            if items:
                has_any = True
                lines.append(f"### {category} Linkages")
                lines.append("")
                lines.append("| Source Component | Relationship / Linkage Type | Target Component | Details / Context |")
                lines.append("| :--- | :--- | :--- | :--- |")
                for item in sorted(items, key=lambda x: (x["source"], x["target"])):
                    lines.append(f"| **{item['source']}** | `{item['type']}` | `{item['target']}` | {item['context']} |")
                lines.append("")
        if not has_any:
            lines.append("*No active cross-component mappings detected in current dataset.*")
            lines.append("")
    else:
        lines.append("*No active cross-component mappings detected in current dataset.*")
    lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"Master System Mapping written -> {report_path}")

    # Generate Per-Object Master Architecture Reports (e.g. COMPLETE_SYSTEM_MAPPING_Contact.md)
    for obj_name in sorted(grouped_modules.keys()):
        if obj_name and obj_name != "General / Unassigned":
            generate_single_object_master_report(obj_name, results_dir, master_data, components, orphans, endpoints, relationships, use_ai_summary)

    return report_path


def generate_single_object_master_report(obj_name, results_dir, master_data, components=None, orphans=None, endpoints=None, relationships=None, use_ai_summary=True):
    """
    Generates a dedicated master architecture mapping report for a specific OSVC object entity (e.g., COMPLETE_SYSTEM_MAPPING_Contact.md).
    Filters all workspaces, reports, CPMs, business rules, scripts, BUI add-ins, orphans, and linkages to only include those belonging to obj_name.
    """
    clean_obj = "".join(c if c.isalnum() else "_" for c in str(obj_name))
    mappings_dir = os.path.join(results_dir, "system_mappings")
    os.makedirs(mappings_dir, exist_ok=True)
    report_filename = f"report_Mapping_{clean_obj}.md"
    report_path = os.path.join(mappings_dir, report_filename)
    
    meta = master_data.get("metadata", {}) or master_data.get("meta", {})
    all_nodes = master_data.get("graph", {}).get("nodes", [])
    all_edges = master_data.get("graph", {}).get("edges", [])

    nodes = [
        n for n in all_nodes
        if canonical_module_name(n.get("module") or n.get("data", {}).get("module") or n.get("data", {}).get("object") or n.get("label")) == obj_name
    ]

    node_id_set = set(n.get("id") for n in nodes)
    edges = [
        e for e in all_edges
        if e.get("source") in node_id_set or e.get("target") in node_id_set
    ]

    degree_map = {}
    node_by_id = {}
    for n in nodes:
        node_by_id[n.get("id")] = n
        n["inc"] = []
        n["out"] = []

    for e in edges:
        s, t = e.get("source"), e.get("target")
        degree_map.setdefault(s, {"in": 0, "out": 0})["out"] += 1
        degree_map.setdefault(t, {"in": 0, "out": 0})["in"] += 1
        if s in node_by_id: node_by_id[s]["out"].append(e)
        if t in node_by_id: node_by_id[t]["inc"].append(e)

    all_orphans = [
        o for o in (orphans or master_data.get("orphans", []))
        if canonical_module_name(o.get("object") or o.get("module")) == obj_name
    ]

    all_endpoints = []
    for ep in (endpoints or master_data.get("endpoints", [])):
        src = str(ep.get("source_file") or "").lower()
        ctx = str(ep.get("context") or "").lower()
        if obj_name.lower() in src or obj_name.lower() in ctx:
            all_endpoints.append(ep)

    if not all_endpoints and components:
        for cs in components.get("customScripts", []):
            cs_mod = canonical_module_name(cs.get("module") or cs.get("object"))
            if cs_mod == obj_name:
                for url in cs.get("endpoints", []):
                    all_endpoints.append({
                        "url": url,
                        "source_file": f"customscript:{cs.get('file_name', 'script.php')}",
                        "context": f"cURL / HTTP REST Request in {cs.get('file_name')}"
                    })
        for bui in components.get("buiAddins", []):
            bui_mod = canonical_module_name(bui.get("module") or bui.get("object_type"))
            if bui_mod == obj_name:
                for call in bui.get("api_calls", []):
                    all_endpoints.append({
                        "url": str(call),
                        "source_file": f"buiaddin:{bui.get('name', 'BUIAddin')}",
                        "context": f"BUI Extension API Integration in {bui.get('name')}"
                    })

    lines = []
    lines.append(f"# {obj_name} Master System Architecture & Component Mapping")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Target OSVC Entity Object**: `{obj_name}`  ")
    lines.append(f"**Source Data Path**: `{meta.get('source_path', 'input')}`  ")
    lines.append("")

    num_ws = len([n for n in nodes if n.get("type") == "workspace"])
    num_rep = len([n for n in nodes if n.get("type") == "report"])
    num_cpm = len([n for n in nodes if n.get("type") in ["cpm", "asynccpm"]])
    num_scr = len([n for n in nodes if n.get("type") == "customscript"])
    num_bui = len([n for n in nodes if n.get("type") == "buiaddin"])

    obj_ws_items = [ws for ws in (components.get("workspaces", []) if components else []) if canonical_module_name(ws.get("object_type") or ws.get("module")) == obj_name]
    obj_br_items = [br for br in (components.get("businessRules", []) if components else []) if canonical_module_name(br.get("object") or br.get("module")) == obj_name]
    total_br_rules = sum(b.get("total_rules", len(b.get("rules", []))) for b in obj_br_items)

    lines.append(f"## Executive {obj_name} Summary & Risk Overview")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> **{obj_name} Mapping Overview**: Structured inventory of all parsed Oracle Service Cloud workspaces, analytics reports, CPM procedures, business rules, custom scripts, and external REST/SOAP integration endpoints associated with the `{obj_name}` entity.")
    lines.append("")

    lines.append("| Component Category | Total Discovered Count | Status |")
    lines.append("| :--- | :---: | :--- |")
    lines.append(f"| {obj_name} Workspaces | {num_ws} | Parsed & Mapped |")
    lines.append(f"| {obj_name} Analytics Reports | {num_rep} | Parsed & Mapped |")
    lines.append(f"| {obj_name} Business Rules Sets | {len(obj_br_items)} ({total_br_rules} Rules) | Parsed & Policy Mapped |")
    lines.append(f"| {obj_name} CPM Procedures & Handlers | {num_cpm} | Parsed & Event Mapped |")
    lines.append(f"| {obj_name} Custom Scripts | {num_scr} | Analyzed |")
    lines.append(f"| {obj_name} BUI Add-Ins | {num_bui} | Archive Extracted |")
    lines.append(f"| {obj_name} External Integration Endpoints | {len(all_endpoints)} | Endpoint Extracted |")
    lines.append(f"| {obj_name} Orphaned Components | {len(all_orphans)} | Audit Flagged |")
    lines.append("")

    if all_orphans:
        lines.append("> [!WARNING]")
        lines.append(f"> **{len(all_orphans)} Orphaned Component(s) Flagged for {obj_name}**: Custom scripts or components exist for `{obj_name}` with zero active workspace or CPM bindings.")
        lines.append("")
    if all_endpoints:
        lines.append("> [!IMPORTANT]")
        lines.append(f"> **{len(all_endpoints)} External HTTP Integration Endpoints Detected for {obj_name}**: Outbound web calls to external REST/SOAP servers require security verification.")
        lines.append("")

    lines.append("> [!TIP]")
    lines.append(f"> **Optimization Recommendation**: Audit `{obj_name}` orphaned scripts and verify outbound integration endpoints for TLS compliance.")
    lines.append("")

    lines.append(f"## Audit-Critical Orphaned Components for {obj_name}")
    lines.append("")
    if all_orphans:
        lines.append("| Component Name / ID | Type | Associated Object | Linkage Count | Audit Risk Flag & Reason |")
        lines.append("| :--- | :--- | :--- | :---: | :--- |")
        for o in all_orphans:
            oname = o.get("name") or o.get("id") or o.get("file_name") or "Unnamed"
            otype = o.get("type") or "Component"
            oobj = canonical_module_name(o.get("object") or o.get("module") or "General")
            oreason = o.get("reason") or "Zero active inbound/outbound references detected"
            deg = degree_map.get(o.get("id", ""), {"in": 0, "out": 0})
            link_str = f"{deg['in']} in, {deg['out']} out"
            lines.append(f"| `{oname}` | `{otype}` | **{oobj}** | `{link_str}` | `{oreason}` |")
    else:
        lines.append(f"*No orphaned components detected for {obj_name}. All components are actively referenced.*")
    lines.append("")

    lines.append(f"## Consolidated Entity Module Inventory for {obj_name}")
    lines.append("")
    lines.append(f"### Entity Module: {obj_name} ({len(nodes)} Mapped Components)")
    lines.append("")

    if len(nodes) > 1:
        lines.append(generate_mermaid_for_module(obj_name, nodes, degree_map))
        lines.append("")

    lines.append("| Component ID / Name | Type | Dependencies (In -> Out) | Details & Execution Context |")
    lines.append("| :--- | :--- | :---: | :--- |")
    type_order = {"object": 0, "module_root": 0, "workspace": 1, "report": 2, "cpm": 3, "asynccpm": 3, "customscript": 4, "buiaddin": 5, "workspacefield": 6, "customfield": 7}
    sorted_nodes = sorted(nodes, key=lambda x: (type_order.get((x.get("type") or "").lower(), 99), str(x.get("label")).lower()))
    for n in sorted_nodes:
        nid = n.get("id", "")
        ntype = n.get("type", "")
        nlabel = n.get("label", "")
        deg = degree_map.get(nid, {"in": 0, "out": 0})
        dep_str = f"`{deg['in']} in -> {deg['out']} out`"
        details = build_details_summary(n, use_ai_summary=use_ai_summary)
        lines.append(f"| `{nlabel}` | `{ntype}` | {dep_str} | {details} |")
    lines.append("")

    lines.append(f"## Workspaces & Field Mapping Matrix for {obj_name}")
    lines.append("")
    if obj_ws_items:
        for ws in sorted(obj_ws_items, key=lambda x: x.get("name", "")):
            wname = ws.get("name") or "Workspace"
            wobj = canonical_module_name(ws.get("object_type") or ws.get("module"))
            fields = collect_all_workspace_fields(ws)
            tabs = len(ws.get("tabs", []))
            rules = len(ws.get("rules", []))

            lines.append(f"### Workspace: {wname}")
            lines.append(f"- **Primary Object Binding**: **{wobj}**")
            lines.append(f"- **Layout Summary**: {len(fields)} form fields used across {tabs} tabsets ({rules} rules)")
            lines.append("")
            if fields:
                lines.append("| Field Name / ID | Custom Field (c$) | Parent Location / Tab | Dependencies |")
                lines.append("| :--- | :---: | :--- | :---: |")
                for f in fields:
                    fid = f.get("field_id") or f.get("label") or "Unnamed"
                    is_c = "Yes (c$)" if f.get("is_custom") else "No"
                    tab_name = f.get("location") or "Top-level Layout"
                    f_node_id = f"workspacefield:{str(fid).lower()}"
                    f_deg = degree_map.get(f_node_id, {"in": 0, "out": 0})
                    f_link = f"`{f_deg['in']} in -> {f_deg['out']} out`"
                    lines.append(f"| `{fid}` | {is_c} | {tab_name} | {f_link} |")
            lines.append("")
    else:
        lines.append(f"*No Workspaces detected for {obj_name}.*")
    lines.append("")

    lines.append(f"## CPM Event Handlers & Procedures Matrix for {obj_name}")
    lines.append("")
    obj_cpm_items = [c for c in (components.get("cpm", []) if components else []) if canonical_module_name(c.get("object_type") or c.get("module") or c.get("object")) == obj_name]
    if obj_cpm_items:
        lines.append("| CPM Handler / XML | Object Binding | Event Trigger | Execution Mode | Entry Point Method | Dependencies |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :---: |")
        for c in obj_cpm_items:
            name = c.get("name") or c.get("file_name") or "Unnamed"
            obj = canonical_module_name(c.get("object_type") or c.get("module"))
            evt = c.get("operations_label") or c.get("script_type") or "Event Handler"
            is_a = "Async Execution" if c.get("is_async") else "Synchronous Execution"
            entry = c.get("entry_point") or "ObjectProcedure::apply"
            c_id = f"cpm:{str(name).lower()}"
            c_deg = degree_map.get(c_id, {"in": 0, "out": 0})
            c_link = f"`{c_deg['in']} in -> {c_deg['out']} out`"
            lines.append(f"| `{name}` | **{obj}** | `{evt}` | {is_a} | `{entry}` | {c_link} |")
    else:
        lines.append(f"*No CPM Procedures detected for {obj_name}.*")
    lines.append("")

    lines.append(f"## System Component Linkages for {obj_name}")
    lines.append("")
    rel_list = relationships if relationships else []
    if rel_list:
        seen = set()
        obj_rel_items = []
        for r in rel_list:
            src_obj = r.get("source") or r.get("from") or {}
            tgt_obj = r.get("target") or r.get("to") or {}
            src_str = format_component_ref(src_obj)
            tgt_str = format_component_ref(tgt_obj)
            if "Report 0" in tgt_str or "Report 0" in src_str:
                continue

            if obj_name.lower() in src_str.lower() or obj_name.lower() in tgt_str.lower():
                rtype_str = format_rel_type(r)
                ctx = r.get("context") or r.get("details") or "Cross-Component Mapping"
                key = (src_str, rtype_str, tgt_str, ctx)
                if key not in seen:
                    seen.add(key)
                    obj_rel_items.append({"source": src_str, "type": rtype_str, "target": tgt_str, "context": ctx})

        if obj_rel_items:
            lines.append("| Source Component | Linkage Type | Target Component | Details / Context |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for item in sorted(obj_rel_items, key=lambda x: (x["source"], x["target"])):
                lines.append(f"| **{item['source']}** | `{item['type']}` | `{item['target']}` | {item['context']} |")
            lines.append("")
        else:
            lines.append(f"*No active linkages detected for {obj_name}.*")
            lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    fmt_dir = os.path.join(results_dir, "markdown")
    if os.path.exists(fmt_dir):
        with open(os.path.join(fmt_dir, report_filename), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    print(f"Single Object Master System Mapping written -> {report_path}")
    return report_path
