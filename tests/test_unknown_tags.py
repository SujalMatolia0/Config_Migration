import os
import sys
import json
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    import pytest
except ImportError:
    pytest = None
from lxml import etree

from src.parsers.workspace_parser import parse_workspace_file
from src.parsers.report_parser import parse_report_file
from src.parsers.cpm_parser import parse_cpm_file
from src.parsers.rule_parser import parse_rule_file
from src.parsers.nav_parser import parse_nav_file
from src.parsers.bui_addin_parser import parse_bui_addin

def test_workspace_parser_captures_injected_unknown():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Workspace Name="TestWS" Type="1" ServerVersion="24" ClientVersion="24" InjectedUnknownAttr="true">
    <InjectedFakeTag>Custom Content</InjectedFakeTag>
</Workspace>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        path = f.name
    try:
        data = parse_workspace_file(path)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_report_parser_captures_injected_unknown():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<analytics_core Name="TestReport" Id="99999" InjectedUnknownAttr="true">
    <InjectedFakeTag>Report Data</InjectedFakeTag>
</analytics_core>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        path = f.name
    try:
        data = parse_report_file(path)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_cpm_parser_captures_injected_unknown():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<ObjectProcedure Name="TestProc" Id="888" InjectedUnknownAttr="true">
    <InjectedFakeTag>CPM Data</InjectedFakeTag>
    <Content>&lt;?php echo "test"; ?&gt;</Content>
</ObjectProcedure>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        path = f.name
    try:
        data = parse_cpm_file(path)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_rule_parser_captures_injected_unknown():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Rule Name="TestRule" Active="True" InjectedUnknownAttr="true">
    <InjectedFakeTag>Rule Data</InjectedFakeTag>
</Rule>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        path = f.name
    try:
        data = parse_rule_file(path)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_nav_parser_captures_injected_unknown():
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<NavigationSet Name="TestNav" InjectedUnknownAttr="true">
    <InjectedFakeTag>Nav Data</InjectedFakeTag>
</NavigationSet>"""
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        path = f.name
    try:
        data = parse_nav_file(path)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_bui_addin_parser_captures_injected_unknown():
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_xml = """<manifest name="TestBUI" InjectedUnknownAttr="true"><InjectedFakeTag>Addin</InjectedFakeTag></manifest>"""
        with open(os.path.join(tmp_dir, "manifest.xml"), "w") as f:
            f.write(manifest_xml)
        data = parse_bui_addin(tmp_dir)
        unk = data.get("unknowns", {})
        children = [c.get("tag") for c in unk.get("unknown_children", [])]
        attrs = [a.get("attribute") for a in unk.get("unknown_attrs", [])]
        assert "InjectedFakeTag" in children
        assert "InjectedUnknownAttr" in attrs
        attr_entry = next(a for a in unk.get("unknown_attrs", []) if a.get("attribute") == "InjectedUnknownAttr")
        assert attr_entry.get("value") == "true"

def test_e2e_unknown_tags_pipeline():
    with tempfile.TemporaryDirectory() as tmp_dir:
        input_dir = os.path.join(tmp_dir, "input")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(os.path.join(input_dir, "workspaces"))
        os.makedirs(os.path.join(input_dir, "reports"))
        os.makedirs(os.path.join(input_dir, "cpm"))
        os.makedirs(os.path.join(input_dir, "rules"))
        os.makedirs(os.path.join(input_dir, "navigation"))
        os.makedirs(os.path.join(input_dir, "bui_addins", "TestBUIAddin"))

        # 1. Workspace
        ws_xml = """<?xml version="1.0" encoding="utf-8"?>
<Workspace Name="E2E_WS" Type="1" ServerVersion="24" ClientVersion="24">
    <InjectedWSUnknown>WS Data</InjectedWSUnknown>
</Workspace>"""
        with open(os.path.join(input_dir, "workspaces", "E2E_WS.xml"), "w") as f:
            f.write(ws_xml)

        # 2. Report
        rep_xml = """<?xml version="1.0" encoding="utf-8"?>
<analytics_core Name="E2E_Report" Id="777">
    <InjectedReportUnknown>Report Data</InjectedReportUnknown>
</analytics_core>"""
        with open(os.path.join(input_dir, "reports", "E2E_Report.xml"), "w") as f:
            f.write(rep_xml)

        # 3. CPM
        cpm_xml = """<?xml version="1.0" encoding="utf-8"?>
<ObjectProcedure Name="E2E_CPM" Id="555">
    <InjectedCPMUnknown>CPM Data</InjectedCPMUnknown>
    <Content>&lt;?php // test ?&gt;</Content>
</ObjectProcedure>"""
        with open(os.path.join(input_dir, "cpm", "E2E_CPM.xml"), "w") as f:
            f.write(cpm_xml)

        # 4. Business Rule
        rule_xml = """<?xml version="1.0" encoding="utf-8"?>
<Rule Name="E2E_Rule" Active="True">
    <InjectedRuleUnknown>Rule Data</InjectedRuleUnknown>
</Rule>"""
        with open(os.path.join(input_dir, "rules", "E2E_Rule.xml"), "w") as f:
            f.write(rule_xml)

        # 5. Navigation Set
        nav_xml = """<?xml version="1.0" encoding="utf-8"?>
<NavigationSet Name="E2E_Nav">
    <InjectedNavUnknown>Nav Data</InjectedNavUnknown>
</NavigationSet>"""
        with open(os.path.join(input_dir, "navigation", "E2E_Nav.xml"), "w") as f:
            f.write(nav_xml)

        # 6. BUI Add-In
        bui_manifest = """<manifest name="TestBUIAddin"><InjectedBUIUnknown>BUI Data</InjectedBUIUnknown></manifest>"""
        with open(os.path.join(input_dir, "bui_addins", "TestBUIAddin", "manifest.xml"), "w") as f:
            f.write(bui_manifest)
        with open(os.path.join(input_dir, "bui_addins", "TestBUIAddin", "init.html"), "w") as f:
            f.write("<html><body>ORACLE_SERVICE_CLOUD.extensionProvider.registerWorkspaceExtension</body></html>")

        # Run osvc_analyser.py CLI end-to-end
        cmd = f".venv/bin/python osvc_analyser.py --input '{input_dir}' --output '{output_dir}' --dump-unknowns"
        res = os.system(cmd)
        assert res == 0

        # Assert unknowns.json exists and contains all SIX injected tag names in their categories
        unknowns_file = os.path.join(output_dir, "unknowns.json")
        assert os.path.exists(unknowns_file)
        with open(unknowns_file, "r") as f:
            unk_data = json.load(f)

        comps = unk_data.get("components", {})
        ws_tags = [c["tag"] for item in comps.get("workspaces", []) for c in item.get("unknown_children", [])]
        rep_tags = [c["tag"] for item in comps.get("reports", []) for c in item.get("unknown_children", [])]
        cpm_tags = [c["tag"] for item in comps.get("cpm", []) for c in item.get("unknown_children", [])]
        rule_tags = [c["tag"] for item in comps.get("rules", []) for c in item.get("unknown_children", [])]
        nav_tags = [c["tag"] for item in comps.get("navigation", []) for c in item.get("unknown_children", [])]
        bui_tags = [c["tag"] for item in comps.get("bui_addins", []) for c in item.get("unknown_children", [])]

        assert "InjectedWSUnknown" in ws_tags
        assert "InjectedReportUnknown" in rep_tags
        assert "InjectedCPMUnknown" in cpm_tags
        assert "InjectedRuleUnknown" in rule_tags
        assert "InjectedNavUnknown" in nav_tags
        assert "InjectedBUIUnknown" in bui_tags

        # Assert COMPLETE_SYSTEM_MAPPING.md contains all SIX injected tags as literal text in table
        master_md = os.path.join(output_dir, "COMPLETE_SYSTEM_MAPPING.md")
        assert os.path.exists(master_md)
        with open(master_md, "r") as f:
            master_content = f.read()

        assert "InjectedWSUnknown" in master_content
        assert "InjectedReportUnknown" in master_content
        assert "InjectedCPMUnknown" in master_content
        assert "InjectedRuleUnknown" in master_content
        assert "InjectedNavUnknown" in master_content
        assert "InjectedBUIUnknown" in master_content

        # Assert per-component Markdown report for BUI contains its injected tag name
        bui_md = os.path.join(output_dir, "bui_addins", "report_TestBUIAddin.md")
        assert os.path.exists(bui_md)
        with open(bui_md, "r") as f:
            bui_md_content = f.read()
        assert "InjectedBUIUnknown" in bui_md_content

def test_real_file_deep_injection_pipeline():
    with tempfile.TemporaryDirectory() as tmp_dir:
        input_dir = os.path.join(tmp_dir, "input")
        output_dir = os.path.join(tmp_dir, "output")
        os.makedirs(os.path.join(input_dir, "reports"))
        os.makedirs(os.path.join(input_dir, "cpm"))
        os.makedirs(os.path.join(input_dir, "objects"))

        # 1. Deep Report XML: inject tag deeply inside <nodes><node_item><cols><cols_item>
        deep_rep_xml = """<?xml version="1.0" encoding="utf-8"?>
<analytics_core Name="DeepReport" Id="122026">
    <nodes>
        <node_item>
            <cols>
                <cols_item>
                    <col_id>1</col_id>
                    <DeepReportInjectedTag>Deep Value</DeepReportInjectedTag>
                </cols_item>
            </cols>
        </node_item>
    </nodes>
</analytics_core>"""
        with open(os.path.join(input_dir, "reports", "DeepReport.xml"), "w") as f:
            f.write(deep_rep_xml)

        # 2. Deep CPM XML: inject tag deeply inside <Classes><Class><SuppressFlagMapping>
        deep_cpm_xml = """<?xml version="1.0" encoding="utf-8"?>
<ObjectProcedure Name="DeepCPM" Id="999">
    <Classes>
        <Class ClassName="Contact">
            <SuppressFlagMapping>
                <DeepCPMInjectedTag>CPM Deep</DeepCPMInjectedTag>
            </SuppressFlagMapping>
        </Class>
    </Classes>
    <Content>&lt;?php // code ?&gt;</Content>
</ObjectProcedure>"""
        with open(os.path.join(input_dir, "cpm", "DeepCPM.xml"), "w") as f:
            f.write(deep_cpm_xml)

        # 3. Relationship XML: inject unknown attribute
        rel_xml = """<?xml version="1.0" encoding="utf-8"?>
<Relationship Id="10001" ParentClassId="1" ChildClassId="2" InjectedRelAttr="true">
    <InjectedRelTag>Rel Data</InjectedRelTag>
</Relationship>"""
        with open(os.path.join(input_dir, "objects", "Relationship10001_2.xml"), "w") as f:
            f.write(rel_xml)

        # Run CLI
        cmd = f".venv/bin/python osvc_analyser.py --input '{input_dir}' --output '{output_dir}' --dump-unknowns"
        res = os.system(cmd)
        assert res == 0

        # Assert unknowns.json
        unknowns_file = os.path.join(output_dir, "unknowns.json")
        assert os.path.exists(unknowns_file)
        with open(unknowns_file, "r") as f:
            unk_data = json.load(f)

        comps = unk_data.get("components", {})
        
        # Verify category keys exist
        assert "customObjects" in comps
        assert "objectRelationships" in comps

        # Verify deep report tag & path
        rep_unknowns = comps.get("reports", [])
        rep_children = [c for item in rep_unknowns for c in item.get("unknown_children", [])]
        deep_rep_item = next(c for c in rep_children if c.get("tag") == "DeepReportInjectedTag")
        assert deep_rep_item.get("path") == "analytics_core > nodes > node_item > cols > cols_item > DeepReportInjectedTag"
        print(f"[TEST VERIFIED] Deep Report Injected Tag: {deep_rep_item.get('tag')} at path: {deep_rep_item.get('path')}")

        # Verify deep CPM tag & path
        cpm_unknowns = comps.get("cpm", [])
        cpm_children = [c for item in cpm_unknowns for c in item.get("unknown_children", [])]
        deep_cpm_item = next(c for c in cpm_children if c.get("tag") == "DeepCPMInjectedTag")
        assert "DeepCPMInjectedTag" in deep_cpm_item.get("path")
        print(f"[TEST VERIFIED] Deep CPM Injected Tag: {deep_cpm_item.get('tag')} at path: {deep_cpm_item.get('path')}")

        # Verify relationship attribute & tag
        rel_unknowns = comps.get("objectRelationships", [])
        rel_attrs = [a for item in rel_unknowns for a in item.get("unknown_attrs", [])]
        rel_attr_item = next(a for a in rel_attrs if a.get("attribute") == "InjectedRelAttr")
        assert rel_attr_item.get("value") == "true"
        print(f"[TEST VERIFIED] Relationship Injected Attribute: {rel_attr_item.get('attribute')} = {rel_attr_item.get('value')}")

if __name__ == "__main__":
    print("Running test_workspace_parser_captures_injected_unknown...")
    test_workspace_parser_captures_injected_unknown()
    print("Running test_report_parser_captures_injected_unknown...")
    test_report_parser_captures_injected_unknown()
    print("Running test_cpm_parser_captures_injected_unknown...")
    test_cpm_parser_captures_injected_unknown()
    print("Running test_rule_parser_captures_injected_unknown...")
    test_rule_parser_captures_injected_unknown()
    print("Running test_nav_parser_captures_injected_unknown...")
    test_nav_parser_captures_injected_unknown()
    print("Running test_bui_addin_parser_captures_injected_unknown...")
    test_bui_addin_parser_captures_injected_unknown()
    print("Running test_e2e_unknown_tags_pipeline...")
    test_e2e_unknown_tags_pipeline()
    print("Running test_real_file_deep_injection_pipeline...")
    test_real_file_deep_injection_pipeline()
    print("[SUCCESS] All 8 regression & integration tests passed!")
