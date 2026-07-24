
function initAddin(extensionProvider) {
    extensionProvider.registerWorkspaceExtension(function(workspaceRecord) {
        workspaceRecord.getFieldValues(["Incident.IId", "Incident.CO$Org", "Incident.c$org_id_temp", "Incident.c_id", "Incident.source"]);
        workspaceRecord.getFieldValues(["Contact.first_name", "Contact.last_name", "Contact.OrgId"]);
        
        workspaceRecord.addFieldValueListener("Incident.CO$Org", triggerOrgChange);
        workspaceRecord.addFieldValueListener("Incident.c_id", triggerContactChange);
        
        function fetchOrgDetails(orgId) {
            $.ajax({
                url: "connect/v1.3/queryResults?query=SELECT Name as OrganizationName, CustomFields.c.customer_number as customer_number, CustomFields.c.sp_system_type.LookupName SystemType FROM Organizations WHERE ID = " + orgId,
                async: false,
                type: "GET",
                success: function(res) {}
            });
        }
    });
}
