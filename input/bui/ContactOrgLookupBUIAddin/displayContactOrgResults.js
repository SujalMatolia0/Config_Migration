
var ContactLookupSearchReportID = 100407;

function searchCurrentContact() {
    $.ajax({
        url: "connect/v1.3/analyticsReportResults",
        type: "POST",
        data: JSON.stringify({
            id: 100407,
            filters: []
        }),
        success: function(res) {
            workspaceRecord.updateField("Incident.c$org_id_temp", selectedOrgId);
            workspaceRecord.updateField("Incident.c$org_label_temp", labelStr);
            workspaceRecord.updateField("Incident.CO$Org", selectedOrgId);
            workspaceRecord.updateField("Incident.CId", selectedContactId);
        }
    });
}
