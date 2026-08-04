# BUI Add-In: `ContactOrgLookupBUIAddin`

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

### HTML Live Previews

#### HTML Asset: `init.html`

<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KICAgIDxzY3JpcHQgc3JjPSIuLi8uLi9BdXRoTGlicmFyeUV4dG4vQXV0aExpYnJhcnlFeHRuLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS9qcXVlcnktMy41LjEubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS9qcXVlcnktMy42LjAubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9qc3BkZi8xLjUuMS9qc3BkZi5taW4uanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2pzcGRmLWF1dG90YWJsZS8zLjIuNC9qc3BkZi5wbHVnaW4uYXV0b3RhYmxlLm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0ibG9naWMuanMiPjwvc2NyaXB0Pgo8L2hlYWQ+Cjxib2R5PgogICAgPGRpdiBpZD0iY29udGFjdF9uYW1lIj48L2Rpdj4KICAgIDxkaXYgaWQ9Im9yZ19uYW1lIj48L2Rpdj4KICAgIDxkaXYgaWQ9ImN1c3RvbWVyX251bWJlciI+PC9kaXY+CiAgICA8ZGl2IGlkPSJzeXN0ZW1fdHlwZSI+PC9kaXY+CiAgICA8YnV0dG9uIGlkPSJzZWFyY2hfYnRuIj5TZWFyY2ggQ29udGFjdC9BY2NvdW50PC9idXR0b24+CjwvYm9keT4KPC9odG1sPg==" data-title="init.html">
  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">
<!DOCTYPE html>
<html>
<head>
    <script src="../../AuthLibraryExtn/AuthLibraryExtn.js"></script>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.1/jspdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.2.4/jspdf.plugin.autotable.min.js"></script>
    <script src="logic.js"></script>
</head>
<body>
    <div id="contact_name"></div>
    <div id="org_name"></div>
    <div id="customer_number"></div>
    <div id="system_type"></div>
    <button id="search_btn">Search Contact/Account</button>
</body>
</html>
    </div>
  </div>
</div>

#### HTML Asset: `ContactOrgDetailsView.html`

<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KICAgIDxzY3JpcHQgc3JjPSJkaXNwbGF5Q29udGFjdE9yZ1Jlc3VsdHMuanMiPjwvc2NyaXB0Pgo8L2hlYWQ+Cjxib2R5PgogICAgPHRhYmxlIGlkPSJyZXN1bHRzIj48L3RhYmxlPgo8L2JvZHk+CjwvaHRtbD4=" data-title="ContactOrgDetailsView.html">
  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">
<!DOCTYPE html>
<html>
<head>
    <script src="displayContactOrgResults.js"></script>
</head>
<body>
    <table id="results"></table>
</body>
</html>
    </div>
  </div>
</div>


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
### API Call & Web Service Endpoints Table

| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |
|---|---|---|---|---|---|
| `POST` | `connect/v1.3/analyticsReportResults` | `REST API` | — | `100407` | `displayContactOrgResults.js` |
| `GET` | `connect/v1.3/queryResults` | `REST API` | `Organizations` | — | `logic.js` |

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
