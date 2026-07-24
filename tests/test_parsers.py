import unittest
import os
import sys

# Add project root to python path to allow imports from folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.workspace_parser import parse_workspace_file
from parsers.report_parser import parse_report_file
from parsers.cpm_parser import parse_cpm_file
from parsers.script_parser import parse_script_file
from output.markdown_generator import generate_report_markdown, generate_analytics_report_markdown

class TestOSVCParsers(unittest.TestCase):
    def setUp(self):
        self.workspace_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input", "workspaces", "Contact test.xml")
        self.report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input", "reports", "Contacts 100008.xml")

    def test_analytics_core_report_parser(self):
        if not os.path.exists(self.report_file):
            self.skipTest("Contacts 100008.xml not found in input/")
            
        data = parse_report_file(self.report_file)
        
        self.assertEqual(data["id"], "100008")
        self.assertEqual(data["name"], "Contacts")
        self.assertEqual(data["format"], "analytics_core")
        self.assertTrue(data["ac_public"])
        
        # Verify columns
        self.assertEqual(len(data["columns"]), 13)
        c1 = data["columns"][0]
        self.assertEqual(c1["source_field"], "contacts.c_id")
        self.assertEqual(c1["label"], "Contact ID")
        
        c3 = data["columns"][2]
        self.assertEqual(c3["source_field"], "contacts.updated")
        self.assertEqual(c3["sort_order"], "1")
        self.assertEqual(c3["sort_direction"], "2")
        
        # Verify tables and joins
        self.assertEqual(len(data["tables"]), 3)
        t1 = data["tables"][0]
        self.assertEqual(t1["alias"], "contacts")
        self.assertEqual(t1["join_type"], "Primary")
        
        t2 = data["tables"][1]
        self.assertEqual(t2["alias"], "sla_instances")
        self.assertEqual(t2["join_type"], "LEFT OUTER JOIN")
        self.assertEqual(t2["join_condition"], "contacts.c_id = sla_instances.owner_id")
        
        # Verify permissions
        self.assertEqual(len(data["permissions"]), 27)
        self.assertIn("Read + Write", data["perms_by_type"])
        self.assertIn("Read Only", data["perms_by_type"])
        self.assertIn("22", data["perms_by_type"]["Read Only"])
        
        # Verify table reference verification (val_col_refs)
        for c in data["columns"]:
            self.assertTrue(c["col_rf_verified"], f"Column {c['col_id']} ({c['source_field']}) failed val_col_refs verification")

        # Verify markdown generation
        md = generate_analytics_report_markdown(data)
        self.assertIn("# Report: Contacts (ID: 100008)", md)
        self.assertIn("Primary Table: `contacts`", md)
        self.assertIn("contacts.c_id", md)
        self.assertIn("contacts.c_id = sla_instances.owner_id", md)
        self.assertIn("All 13 columns verified against internal table references (`val_col_refs`).", md)
        
    def test_workspace_parser(self):
        if not os.path.exists(self.workspace_file):
            self.skipTest("Contact test.xml not found in input/")
            
        data = parse_workspace_file(self.workspace_file)
        
        self.assertEqual(data["name"], "Contact test")
        self.assertEqual(data["type"], "Contact")
        
        # Verify fields extraction
        self.assertTrue(len(data["fields"]) > 0)
        field_ids = [f["field_id"] for f in data["fields"]]
        self.assertIn("Title", field_ids)
        self.assertIn("Name.First", field_ids)
        
        # Verify tabs extraction
        self.assertTrue(len(data["tabs"]) > 0)
        tab_names = [t["text"] for t in data["tabs"]]
        self.assertIn("Incidents", tab_names)
        self.assertIn("Customer360", tab_names)
        
        # Verify relationship items (report IDs)
        incidents_tab = next(t for t in data["tabs"] if t["text"] == "Incidents")
        self.assertEqual(incidents_tab["relationship_items"][0]["ac_id"], "9029")
        
        # Verify browsers
        cust_tab = next(t for t in data["tabs"] if t["text"] == "Customer360")
        self.assertTrue(cust_tab["browsers"][0]["suppress_errors"])
        self.assertTrue("gcb_flex.php" in cust_tab["browsers"][0]["url"])

    def test_markdown_generator(self):
        if not os.path.exists(self.workspace_file):
            self.skipTest("Contact test.xml not found in input/")
            
        data = parse_workspace_file(self.workspace_file)
        md = generate_report_markdown(data)
        
        self.assertIn("## System Info", md)
        self.assertIn("Oracle Service Cloud 26A SP2", md)
        self.assertIn("5-column table layout", md)
        self.assertIn("PhOffice", md)
        self.assertIn("Mobile Phone", md)
        self.assertIn("Incidents", md)
        self.assertIn("C$CustomerId", md)
        self.assertIn("Ribbon / Toolbar", md)
        self.assertIn("Key Observations", md)

    def test_script_parser_php(self):
        import tempfile
        code = "<?php\nrequire_once 'helper.php';\n$crm_object = RNCPHP\\Contact::fetch(1);\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".php", delete=False) as f:
            f.write(code)
            tmp_path = f.name
        try:
            res = parse_script_file(tmp_path)
            self.assertEqual(res["file_name"], os.path.basename(tmp_path))
            self.assertIn("helper.php", res["imports"])
            self.assertIn("Contact", res["osvc_objects"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_cpm_parser(self):
        cpm_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input", "cpm")
        mappings_file = os.path.join(cpm_dir, "Mappings.xml")
        async_proc_file = os.path.join(cpm_dir, "ObjectProcedureContactAsync.xml")

        if not os.path.exists(mappings_file) or not os.path.exists(async_proc_file):
            self.skipTest("CPM sample files not found in input/cpm")

        mappings_data = parse_cpm_file(mappings_file)
        self.assertEqual(mappings_data["format"], "cpm_mappings")
        self.assertTrue(len(mappings_data["mappings"]) > 0)
        
        proc_names = [m["procedure"] for m in mappings_data["mappings"]]
        self.assertIn("contact_create", proc_names)
        self.assertIn("contact_update", proc_names)

        proc_data = parse_cpm_file(async_proc_file)
        self.assertEqual(proc_data["format"], "cpm_procedure")
        self.assertEqual(proc_data["name"], "ContactAsync")
        self.assertTrue(proc_data["is_async"])
        self.assertEqual(proc_data["operations_label"], "Update")
        self.assertIn("RegisterContact", proc_data["soap_actions"])
        self.assertTrue(proc_data["has_curl"])

if __name__ == "__main__":
    unittest.main()
