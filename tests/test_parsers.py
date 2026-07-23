import unittest
import os
import sys

# Add project root to python path to allow imports from folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.workspace_parser import parse_workspace_file
from parsers.cpm_parser import parse_cpm_file
from parsers.script_parser import parse_script_file
from output.markdown_generator import generate_report_markdown

class TestOSVCParsers(unittest.TestCase):
    def setUp(self):
        self.workspace_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Contact.xml")
        
    def test_workspace_parser(self):
        if not os.path.exists(self.workspace_file):
            self.skipTest("Contact.xml not found at root")
            
        data = parse_workspace_file(self.workspace_file)
        
        self.assertEqual(data["name"], "Contact")
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
            self.skipTest("Contact.xml not found at root")
            
        data = parse_workspace_file(self.workspace_file)
        md = generate_report_markdown(data)
        
        self.assertIn("## System Info", md)
        self.assertIn("Oracle Service Cloud 26A SP2", md)
        self.assertIn("2-column table layout", md)
        self.assertIn("PhOffice", md)
        self.assertIn("Mobile Phone", md)
        self.assertIn("Incidents", md)
        self.assertIn("C$CustomerId", md)
        self.assertIn("Business Rule", md)
        self.assertIn("Ribbon / Toolbar", md)
        self.assertIn("Key Observations", md)

    def test_script_parser_php(self):
        # Create a temp php script file for testing
        test_script_path = "test_script.php"
        with open(test_script_path, "w", encoding="utf-8") as f:
            f.write(r"""<?php
            require_once 'helper.php';
            $crm_object = RNCPHP\Contact::fetch(1);
            $url = 'https://api.external-service.com/v1/update';
            $ch = curl_init($url);
            curl_exec($ch);
            ?>""")
            
        try:
            data = parse_script_file(test_script_path)
            self.assertEqual(data["file_name"], "test_script.php")
            self.assertIn("helper.php", data["imports"])
            self.assertIn("Contact", data["osvc_objects"])
            self.assertIn("https://api.external-service.com/v1/update", data["urls"])
            self.assertIn("cURL client invocation", data["external_calls"])
        finally:
            if os.path.exists(test_script_path):
                os.remove(test_script_path)

if __name__ == "__main__":
    unittest.main()
