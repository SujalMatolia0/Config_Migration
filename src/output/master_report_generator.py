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
    Generates a single, unified master system mapping markdown report (COMPLETE_SYSTEM_MAPPING.md)
    consolidating all workspaces, objects, CPMs, scripts, BUI add-ins, and cross-component mappings.
    """
    report_path = os.path.join(results_dir, "COMPLETE_SYSTEM_MAPPING.md")
    
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

    lines.append("## Executive System Summary & Risk Overview")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> **System Mapping Overview**: Structured inventory of all parsed Oracle Service Cloud workspaces, analytics reports, CPM procedures, custom scripts, and external REST/SOAP integration endpoints.")
    lines.append("")

    lines.append("| Component Category | Total Discovered Count | Status |")
    lines.append("| :--- | :---: | :--- |")
    lines.append(f"| Workspaces | {num_ws} | Parsed & Mapped |")
    lines.append(f"| Analytics Reports | {num_rep} | Parsed & Mapped |")
    lines.append(f"| CPM Procedures & Handlers | {num_cpm} | Parsed & Event Mapped |")
    lines.append(f"| PHP Custom Scripts | {num_scr} | Analyzed |")
    lines.append(f"| BUI Add-Ins | {num_bui} | Archive Extracted |")
    lines.append(f"| Custom Objects & Entities | {num_obj} | Schema Mapped |")
    lines.append(f"| External Integration Endpoints | {len(all_endpoints)} | Endpoint Extracted |")
    lines.append(f"| Orphaned Components | {len(all_orphans)} | Audit Flagged |")
    lines.append("")

    # Structured Alert Boxes
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

    if ws_items:
        for ws in sorted(ws_items, key=lambda x: x.get("name", "")):
            wname = ws.get("name") or "Workspace"
            wobj = canonical_module_name(ws.get("object_type") or ws.get("module"))
            fields = ws.get("fields", [])
            tabs = len(ws.get("tabs", []))
            rules = len(ws.get("rules", []))
            
            lines.append(f"### Workspace: {wname}")
            lines.append(f"- **Primary Object Binding**: **{wobj}**")
            lines.append(f"- **Layout Summary**: {len(fields)} fields rendered across {tabs} tabsets ({rules} rules)")
            lines.append("")
            if fields:
                lines.append("| Field Name / ID | Data Type | Custom Field (c$) | Parent Tab | Dependencies |")
                lines.append("| :--- | :--- | :---: | :--- | :---: |")
                for f in fields:
                    fid = f.get("field_id") or f.get("label") or f.get("name") or "Unnamed"
                    ftype = f.get("type") or "Standard"
                    is_c = "Yes (c$)" if "c$" in str(fid).lower() else "No"
                    tab_name = f.get("tab") or "Main Tab"
                    f_node_id = f"workspacefield:{str(fid).lower()}"
                    f_deg = degree_map.get(f_node_id, {"in": 0, "out": 0})
                    f_link = f"`{f_deg['in']} in -> {f_deg['out']} out`"
                    lines.append(f"| `{fid}` | `{ftype}` | {is_c} | {tab_name} | {f_link} |")
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

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"Master System Mapping written -> {report_path}")
    return report_path
