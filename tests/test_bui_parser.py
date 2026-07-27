import unittest
import os
import shutil
import tempfile
import zipfile
from src.parsers.bui_addin_parser import parse_bui_addin

class TestBUIAddinParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
        self.init_html = """<!DOCTYPE html>
<html>
<head>
    <script src="../../AuthLibraryExtn/AuthLibraryExtn.js"></script>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.1/jspdf.min.js"></script>
    <script src="logic.js"></script>
</head>
<body>
    <div id="contact_name"></div>
    <div id="org_name"></div>
    <button id="search_btn">Search Contact/Account</button>
</body>
</html>"""

        self.logic_js = """
function initAddin(extensionProvider) {
    extensionProvider.registerWorkspaceExtension(function(workspaceRecord) {
        workspaceRecord.getFieldValues(['Incident.IId', 'Incident.CO$Org', 'Incident.c$org_id_temp', 'Incident.c_id', 'Incident.source']);
        workspaceRecord.getFieldValues(['Contact.first_name', 'Contact.last_name', 'Contact.OrgId']);
        
        workspaceRecord.addFieldValueListener('Incident.CO$Org', triggerOrgChange);
        workspaceRecord.addFieldValueListener('Incident.c_id', triggerContactChange);
        workspaceRecord.addRecordSavedListener(function() { console.log('Saved'); });
        workspaceRecord.executeEditorCommand('Save');
        
        function fetchOrgDetails(orgId) {
            $.ajax({
                url: 'connect/v1.3/queryResults?query=SELECT Name as OrganizationName, CustomFields.c.sp_system_type.LookupName SystemType FROM Organizations WHERE ID = ' + orgId,
                async: false,
                type: 'GET',
                success: function(res) {}
            });
        }

        function openModal() {
            extensionProvider.createModalWindow('askForSiebelNumber.html', { width: 300, height: 150 });
        }
    }, 'SEND_TO_SIEBEL');
}
"""

        self.view_html = """<!DOCTYPE html>
<html>
<head>
    <script src="../../AuthLibraryExtn/AuthLibraryExtn.js"></script>
    <script src="displayContactOrgResults.js"></script>
</head>
<body>
    <table id="results"></table>
</body>
</html>"""

        self.display_js = """
var ContactLookupSearchReportID = 100407;

function searchCurrentContact() {
    $.ajax({
        url: '/cc/ajaxCustom/addSrToSiebel',
        type: 'POST',
        data: JSON.stringify({
            id: 100407,
            filters: []
        }),
        success: function(res) {
            workspaceRecord.updateField('Incident.c$org_id_temp', selectedOrgId);
            workspaceRecord.updateField('Incident.C$org_id_temp', selectedOrgId);
            workspaceRecord.updateField('Incident.CO$Org', selectedOrgId);
            workspaceRecord.updateField('Incident.CId', selectedContactId);
            extensionProvider.closeModalWindow('CUSTOM_APP_ID');
        }
    });
}
"""

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_bui_addin_directory(self):
        addin_folder = os.path.join(self.test_dir, "ContactOrgLookupBUIAddin")
        os.makedirs(addin_folder)
        
        with open(os.path.join(addin_folder, "init.html"), "w") as f:
            f.write(self.init_html)
        with open(os.path.join(addin_folder, "logic.js"), "w") as f:
            f.write(self.logic_js)
        with open(os.path.join(addin_folder, "ContactOrgDetailsView.html"), "w") as f:
            f.write(self.view_html)
        with open(os.path.join(addin_folder, "displayContactOrgResults.js"), "w") as f:
            f.write(self.display_js)

        result = parse_bui_addin(addin_folder)

        self.assertEqual(result["name"], "ContactOrgLookupBUIAddin")
        self.assertEqual(result["entry_point"], "init.html")
        self.assertIn("100407", [str(r) for r in result["report_ids"]])
        self.assertIn("Incident.c$org_id_temp", result["osvc_fields_written"])
        
        # Deduplication check: Incident.c$org_id_temp and Incident.C$org_id_temp normalized
        self.assertEqual(len([f for f in result["osvc_fields_written"] if f.lower() == "incident.c$org_id_temp"]), 1)

        self.assertIn("RecordSaved", result["lifecycle_listeners"])
        self.assertIn("Save", result["editor_commands"])
        self.assertIn("../../AuthLibraryExtn/AuthLibraryExtn.js", result["external_dependencies"])

        # CP Controller endpoint check
        cp_endpoints = [c["endpoint"] for c in result["api_calls"] if c.get("type") == "CP Controller Endpoint"]
        self.assertIn("/cc/ajaxCustom/addSrToSiebel", cp_endpoints)

        # Risk flags check
        risk_types = [r["type"] for r in result["risk_flags"]]
        self.assertIn("Relative Path Dependency", risk_types)
        self.assertIn("Duplicate Library Load", risk_types)
        self.assertIn("Hardcoded Report ID", risk_types)
        self.assertIn("Synchronous AJAX", risk_types)
        self.assertIn("Extension ID Mismatch", risk_types)

    def test_parse_bui_addin_zip(self):
        zip_path = os.path.join(self.test_dir, "ContactOrgLookupBUIAddin.zip")
        with zipfile.ZipFile(zip_path, 'w') as z:
            z.writestr("init.html", self.init_html)
            z.writestr("logic.js", self.logic_js)
            z.writestr("ContactOrgDetailsView.html", self.view_html)
            z.writestr("displayContactOrgResults.js", self.display_js)

        result = parse_bui_addin(zip_path)

        self.assertEqual(result["name"], "ContactOrgLookupBUIAddin")
        self.assertEqual(result["entry_point"], "init.html")
        self.assertEqual(len(result["files"]), 4)
        self.assertIn(100407, result["report_ids"])

if __name__ == '__main__':
    unittest.main()
