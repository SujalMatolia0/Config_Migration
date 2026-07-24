# BUI Add-In Report: `ContactOrgLookupBUIAddin`

- **Add-In Name**: `ContactOrgLookupBUIAddin`
- **Extension Type**: `BUIAddin`
- **Entry Point**: `init.html`
- **Total Package Files**: 4
- **Risk Findings Count**: 6

---

## Package Structure & Extracted Web Assets

| Asset Filename | Asset Type | Notes |
|---|---|---|
| `ContactOrgDetailsView.html` | `html` | HTML Modal View / UI Page |
| `displayContactOrgResults.js` | `js` | JavaScript Application Logic |
| `init.html` | `html` | Extension Entry Point |
| `logic.js` | `js` | JavaScript Application Logic |

### External Script & Library Dependencies

- **External Add-In Dependencies**: `../../AuthLibraryExtn/AuthLibraryExtn.js`
- **External Libraries (CDNs/Frameworks)**: `jquery-3.5.1.min.js`, `jquery-3.6.0.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js`

---

## OSVC Workspace Interactions

- **Fields Read**: `Contact.OrgId`, `Contact.first_name`, `Contact.last_name`, `Incident.CId`, `Incident.CO$Org`, `Incident.IId`, `Incident.c$org_id_temp`, `Incident.c$org_label_temp`, `Incident.c_id`, `Incident.source`
- **Fields Written**: `Incident.CId`, `Incident.CO$Org`, `Incident.c$org_id_temp`, `Incident.c$org_label_temp`
- **Field Listeners Registered**: `Incident.CO$Org`, `Incident.c_id`

---

## Report Dependencies & REST API Endpoints

- **Report Dependencies**: `100407`
- **API Calls & Web Service Operations**:
  - `POST` `connect/v1.3/analyticsReportResults` [REST API] (Report ID: `100407`) *(from `displayContactOrgResults.js`)*
  - `GET` `connect/v1.3/queryResults` [REST API] (Table: `Organizations`) *(from `logic.js`)*

---

## Static Risk Audit Findings

| Severity | Risk Type | Detail |
|---|---|---|
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in logic.js — blocks browser UI thread |
| Medium | `Custom Field Schema Dependency` | Direct CustomFields.c ROQL LookupName query in logic.js — vulnerable to schema alterations |
| **High** | `Duplicate Library Load` | Duplicate jQuery versions loaded in init.html: https://code.jquery.com/jquery-3.5.1.min.js, https://code.jquery.com/jquery-3.6.0.min.js |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in init.html — will fail if add-in path changes |
| Medium | `Hardcoded Report ID` | Hardcoded Report ID 100407 in BUI Add-In code — risks silent failure if report ID changes |
| Low | `Unused Library Import` | jsPDF / jsPDF-AutoTable loaded in HTML headers but unreferenced in JavaScript |

---

## Dependency Flow Diagram

```mermaid
graph LR
  classDef addin fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
  classDef rep fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;
  classDef api fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;
  classDef field fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;

  BUI_ContactOrgLookupBUIAddin["BUI Add-In: ContactOrgLookupBUIAddin"]:::addin
  REP_100407["Report 100407: Report 100407"]:::rep
  BUI_ContactOrgLookupBUIAddin --> |"Report Dependency"| REP_100407
  API_connectv13analyticsReportResults["API: connect/v1.3/analyticsReportResults"]:::api
  BUI_ContactOrgLookupBUIAddin --> |"POST"| API_connectv13analyticsReportResults
  API_connectv13queryResults["API: connect/v1.3/queryResults"]:::api
  BUI_ContactOrgLookupBUIAddin --> |"GET"| API_connectv13queryResults
  FW_IncidentCId["Field Write: Incident.CId"]:::field
  BUI_ContactOrgLookupBUIAddin -.-> |"Write"| FW_IncidentCId
  FW_IncidentCOOrg["Field Write: Incident.CO$Org"]:::field
  BUI_ContactOrgLookupBUIAddin -.-> |"Write"| FW_IncidentCOOrg
  FW_Incidentcorg_id_temp["Field Write: Incident.c$org_id_temp"]:::field
  BUI_ContactOrgLookupBUIAddin -.-> |"Write"| FW_Incidentcorg_id_temp
  FW_Incidentcorg_label_temp["Field Write: Incident.c$org_label_temp"]:::field
  BUI_ContactOrgLookupBUIAddin -.-> |"Write"| FW_Incidentcorg_label_temp
```
