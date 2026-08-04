# BUI (Browser UI) Add-In Summary

- **Total BUI Add-Ins Analyzed**: 2

---

## Overview Table

| Add-In Name | Extension Type | Entry Point | File Count | External Libraries | Risk Audit Count |
|---|---|---|---|---|---|
| **ContactOrgLookupBUIAddin** | `BUIAddin` | `init.html` | 4 | `jquery-3.5.1.min.js`, `jquery-3.6.0.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js` | 6 |
| **SendToSiebelBUIAddin** | `BUIAddin` | `init.html` | 5 | `jquery-3.6.0.min.js`, `jquery-ui.js`, `jquery.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js` | 6 |

---

## Detailed Add-In Breakdowns

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #06b6d4; color: #06b6d4; margin-right: 8px;">BUIAddin</span><b>Add-In: ContactOrgLookupBUIAddin</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Entry: init.html)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Add-In: `ContactOrgLookupBUIAddin`

- **Entry Point**: `init.html`
- **Package Files**: `ContactOrgDetailsView.html`, `displayContactOrgResults.js`, `init.html`, `logic.js`

##### HTML Live Previews

**HTML Asset**: `init.html`
<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KICAgIDxzY3JpcHQgc3JjPSIuLi8uLi9BdXRoTGlicmFyeUV4dG4vQXV0aExpYnJhcnlFeHRuLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS9qcXVlcnktMy41LjEubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS9qcXVlcnktMy42LjAubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9qc3BkZi8xLjUuMS9qc3BkZi5taW4uanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2pzcGRmLWF1dG90YWJsZS8zLjIuNC9qc3BkZi5wbHVnaW4uYXV0b3RhYmxlLm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0ibG9naWMuanMiPjwvc2NyaXB0Pgo8L2hlYWQ+Cjxib2R5PgogICAgPGRpdiBpZD0iY29udGFjdF9uYW1lIj48L2Rpdj4KICAgIDxkaXYgaWQ9Im9yZ19uYW1lIj48L2Rpdj4KICAgIDxkaXYgaWQ9ImN1c3RvbWVyX251bWJlciI+PC9kaXY+CiAgICA8ZGl2IGlkPSJzeXN0ZW1fdHlwZSI+PC9kaXY+CiAgICA8YnV0dG9uIGlkPSJzZWFyY2hfYnRuIj5TZWFyY2ggQ29udGFjdC9BY2NvdW50PC9idXR0b24+CjwvYm9keT4KPC9odG1sPg==" data-title="init.html"></div>

**HTML Asset**: `ContactOrgDetailsView.html`
<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KICAgIDxzY3JpcHQgc3JjPSJkaXNwbGF5Q29udGFjdE9yZ1Jlc3VsdHMuanMiPjwvc2NyaXB0Pgo8L2hlYWQ+Cjxib2R5PgogICAgPHRhYmxlIGlkPSJyZXN1bHRzIj48L3RhYmxlPgo8L2JvZHk+CjwvaHRtbD4=" data-title="ContactOrgDetailsView.html"></div>

- **External Script Dependencies**: `../../AuthLibraryExtn/AuthLibraryExtn.js`
- **External Libraries**: `jquery-3.5.1.min.js`, `jquery-3.6.0.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js`

#### OSVC Workspace Interaction

- **Fields Read**: `Contact.OrgId`, `Contact.first_name`, `Contact.last_name`, `Incident.CId`, `Incident.CO$Org`, `Incident.IId`, `Incident.c$org_id_temp`, `Incident.c$org_label_temp`, `Incident.c_id`, `Incident.source`
- **Fields Written**: `Incident.CId`, `Incident.CO$Org`, `Incident.c$org_id_temp`, `Incident.c$org_label_temp`
- **Field Listeners Registered**: `Incident.CO$Org`, `Incident.c_id`

#### Report Dependencies & API Endpoints

- **Report Dependencies**: `100407`
##### API Call & Web Service Endpoints Table

| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |
|---|---|---|---|---|---|
| `POST` | `connect/v1.3/analyticsReportResults` | `REST API` | — | `100407` | `displayContactOrgResults.js` |
| `GET` | `connect/v1.3/queryResults` | `REST API` | `Organizations` | — | `logic.js` |

#### Risk Audit Findings

| Severity | Risk Type | Detail |
|---|---|---|
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in logic.js — blocks browser UI thread |
| Medium | `Custom Field Schema Dependency` | Direct CustomFields.c ROQL LookupName query in logic.js — vulnerable to schema alterations |
| **High** | `Duplicate Library Load` | Duplicate jQuery versions loaded in init.html: https://code.jquery.com/jquery-3.5.1.min.js, https://code.jquery.com/jquery-3.6.0.min.js |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in init.html — will fail if add-in path changes |
| Medium | `Hardcoded Report ID` | Hardcoded Report ID 100407 in BUI Add-In code — risks silent failure if report ID changes |
| Low | `Unused Library Import` | jsPDF / jsPDF-AutoTable loaded in HTML headers but unreferenced in JavaScript |

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #06b6d4; color: #06b6d4; margin-right: 8px;">BUIAddin</span><b>Add-In: SendToSiebelBUIAddin</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Entry: init.html)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Add-In: `SendToSiebelBUIAddin`

- **Entry Point**: `init.html`
- **Package Files**: `askForSiebelNumber.html`, `askForSiebelNumber.js`, `init.html`, `logic.js`, `successMessage.html`

##### HTML Live Previews

**HTML Asset**: `init.html`
<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KCjxoZWFkPgogIDxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEuMCI+CiAgPHRpdGxlPlNlbmQgdG8gU2llYmVsPC90aXRsZT4KICA8c3R5bGU+CiAgICAuYnV0dG9uLWNvbnRhaW5lciB7CiAgICAgIGRpc3BsYXk6IGZsZXg7CiAgICAgIGp1c3RpZnktY29udGVudDogY2VudGVyOwogICAgICBtYXJnaW4tdG9wOiAyMHB4OwogICAgfQoKICAgIC5jdXN0b20tYnV0dG9uIHsKICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzJkNDE5YTsKICAgICAgY29sb3I6IHdoaXRlOwogICAgICBib3JkZXI6IG5vbmU7CiAgICAgIHBhZGRpbmc6IDE1cHg7CiAgICAgIGJvcmRlci1yYWRpdXM6IDEycHg7CiAgICAgIGhlaWdodDogNjVweDsKICAgICAgd2lkdGg6IDE4MHB4OwogICAgICBjdXJzb3I6IHBvaW50ZXI7CiAgICAgIGRpc3BsYXk6IGZsZXg7CiAgICAgIGp1c3RpZnktY29udGVudDogY2VudGVyOwogICAgICBhbGlnbi1pdGVtczogY2VudGVyOwogICAgICBtYXJnaW4tcmlnaHQ6IDEwcHg7CiAgICB9CgogICAgLmN1c3RvbS1idXR0b246aG92ZXIgewogICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjVhYWVhOwogICAgfQogIDwvc3R5bGU+CjwvaGVhZD4KCjxib2R5PgogIDxkaXYgY2xhc3M9ImJ1dHRvbi1jb250YWluZXIiPgogICAgPGJ1dHRvbiBpZD0ibmV3X3NpZWJlbF9idXR0b24iIGNsYXNzPSJjdXN0b20tYnV0dG9uIj5BZGQgTmV3IFNpZWJlbCBTUjwvYnV0dG9uPgogICAgPGJ1dHRvbiBpZD0iZXhpc3Rpbmdfc2llYmVsX2J1dHRvbiIgY2xhc3M9ImN1c3RvbS1idXR0b24iPkFkZCB0byBFeGlzdGluZyBTaWViZWwgU1I8L2J1dHRvbj4KICA8L2Rpdj4KCiAgPCEtLSBBZGQgeW91ciBzY3JpcHRzIGJlbG93IHRoaXMgbGluZSAtLT4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9hamF4Lmdvb2dsZWFwaXMuY29tL2FqYXgvbGlicy9qcXVlcnkvMy41LjEvanF1ZXJ5Lm1pbi5qcyI+PC9zY3JpcHQ+CiAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY29kZS5qcXVlcnkuY29tL2pxdWVyeS0zLjYuMC5taW4uanMiPjwvc2NyaXB0PgogIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS91aS8xLjEyLjEvanF1ZXJ5LXVpLmpzIj48L3NjcmlwdD4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYvMS41LjEvanNwZGYubWluLmpzIj48L3NjcmlwdD4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYtYXV0b3RhYmxlLzMuMi40L2pzcGRmLnBsdWdpbi5hdXRvdGFibGUubWluLmpzIj48L3NjcmlwdD4KICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Ii8vY29kZS5qcXVlcnkuY29tL3VpLzEuMTIuMS90aGVtZXMvYmFzZS9qcXVlcnktdWkuY3NzIj4KCiAgPHNjcmlwdCBzcmM9Ii4uLy4uL0F1dGhMaWJyYXJ5RXh0bi9BdXRoTGlicmFyeUV4dG4uanMiPjwvc2NyaXB0PgogIDwhLS1UaGlzIGlzIGxpYnJhcnkgYWRkLWluIHVzZWQgdG8gZmV0Y2ggc2Vzc2lvbiBhbmQgb3RoZXIgYXBwbGljYXRpb24gZGV0YWlscy0tPgogIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9ImxvZ2ljLmpzIj48L3NjcmlwdD4KICA8IS0tVGhpcyBoYXMgbG9naWMgdG8gc2VuZCBJbmNpZGVudCBkZXRhaWxzIHRvIFNpZWJlbCBmb3IgY3JlYXRpbmcgYSBOZXcgU1Igb3IgYXNzb2NpYXRpbmcgd2l0aCBhbiBleGlzdGluZyBTUi0tPgo8L2JvZHk+Cgo8L2h0bWw+" data-title="init.html"></div>

**HTML Asset**: `successMessage.html`
<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgoKPGhlYWQ+CiAgICA8c3R5bGU+CiAgICAgICAgYm9keSB7CiAgICAgICAgICAgIG1hcmdpbjogMDsKICAgICAgICAgICAgZm9udC1mYW1pbHk6IEFyaWFsLCBzYW5zLXNlcmlmOwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzJkNDE5YTsKICAgICAgICAgICAgY29sb3I6IHdoaXRlOwogICAgICAgICAgICBib3JkZXI6IG5vbmU7CiAgICAgICAgICAgIHBhZGRpbmc6IDhweDsKICAgICAgICAgICAgZGlzcGxheTogYmxvY2s7CiAgICAgICAgICAgIGN1cnNvcjogcG9pbnRlcjsKICAgICAgICAgICAgbWFyZ2luLXRvcDogNXB4OwogICAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAgZm9udC1zaXplOiAxNXB4OwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uOmhvdmVyIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzI1YWFlYTsKICAgICAgICB9CiAgICA8L3N0eWxlPgo8L2hlYWQ+Cgo8Ym9keT4KICAgIDxkaXY+CiAgICAgICAgPGRpdiBpZD0ic3VjY2Vzcy1tc2ciPjwvZGl2PgogICAgICAgIDxidXR0b24gaWQ9Im9rX2J0biI+T0s8L2J1dHRvbj4KICAgIDwvZGl2PgoKICAgIDxzY3JpcHQ+CiAgICAgICAgZG9jdW1lbnQuYWRkRXZlbnRMaXN0ZW5lcignRE9NQ29udGVudExvYWRlZCcsIGZ1bmN0aW9uICgpIHsKICAgICAgICAgICAgY29uc3QgcXVlcnlTdHJpbmcgPSB3aW5kb3cubG9jYXRpb24uc2VhcmNoOwogICAgICAgICAgICBjb25zdCBwYXJhbXMgPSB7fTsKICAgICAgICAgICAgcXVlcnlTdHJpbmcuc2xpY2UoMSkuc3BsaXQoJyYnKS5mb3JFYWNoKHBhcmFtID0+IHsKICAgICAgICAgICAgICAgIGNvbnN0IFtrZXksIHZhbHVlXSA9IHBhcmFtLnNwbGl0KCc9Jyk7CiAgICAgICAgICAgICAgICBwYXJhbXNba2V5XSA9IGRlY29kZVVSSUNvbXBvbmVudCh2YWx1ZSk7CiAgICAgICAgICAgIH0pOwogICAgICAgICAgICB2YXIgc2llYmVsX251bV92YWwgPSBwYXJhbXNbJ3NpZWJlbF9udW0nXTsKCiAgICAgICAgICAgIGNvbnN0IHN1Y2Nlc3NNc2cgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnc3VjY2Vzcy1tc2cnKTsKICAgICAgICAgICAgc3VjY2Vzc01zZy5pbm5lckhUTUwgPSAiU3VjY2Vzc2Z1bGx5IGFkZGVkIFNSOjxicj5TUiBOdW1iZXIocyk6IiArIHNpZWJlbF9udW1fdmFsOwogICAgICAgICAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnb2tfYnRuJykuYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLAogICAgICAgICAgICAgICAgZnVuY3Rpb24gKCkgewogICAgICAgICAgICAgICAgICAgIE9SQUNMRV9TRVJWSUNFX0NMT1VELmV4dGVuc2lvbl9sb2FkZXIubG9hZCgiQ1VTVE9NX0FQUF9JRCIsICIxIikKICAgICAgICAgICAgICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24gKGV4dGVuc2lvblByb3ZpZGVyKSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBleHRlbnNpb25Qcm92aWRlci5yZWdpc3RlclVzZXJJbnRlcmZhY2VFeHRlbnNpb24oZnVuY3Rpb24gKElVc2VySW50ZXJmYWNlQ29udGV4dCkgewogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIElVc2VySW50ZXJmYWNlQ29udGV4dC5nZXRNb2RhbFdpbmRvd0NvbnRleHQoKS50aGVuKGZ1bmN0aW9uIChJTW9kYWxXaW5kb3dDb250ZXh0KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIElNb2RhbFdpbmRvd0NvbnRleHQuZ2V0Q3VycmVudE1vZGFsV2luZG93KCkudGhlbihmdW5jdGlvbiAoSU1vZGFsV2luZG93KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAoSU1vZGFsV2luZG93KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgSU1vZGFsV2luZG93LmNsb3NlKCk7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgfSk7CiAgICAgICAgfSk7CgogICAgPC9zY3JpcHQ+CjwvYm9keT4KCjwvaHRtbD4=" data-title="successMessage.html"></div>

**HTML Asset**: `askForSiebelNumber.html`
<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgoKPGhlYWQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jb2RlLmpxdWVyeS5jb20vanF1ZXJ5LTMuNi4wLm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jb2RlLmpxdWVyeS5jb20vdWkvMS4xMi4xL2pxdWVyeS11aS5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYvMS41LjEvanNwZGYubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9qc3BkZi1hdXRvdGFibGUvMy4yLjQvanNwZGYucGx1Z2luLmF1dG90YWJsZS5taW4uanMiPjwvc2NyaXB0PgogICAgPHN0eWxlPgogICAgICAgIGJvZHkgewogICAgICAgICAgICBtYXJnaW46IDA7CiAgICAgICAgICAgIGZvbnQtZmFtaWx5OiBBcmlhbCwgc2Fucy1zZXJpZjsKICAgICAgICB9CgogICAgICAgICNhc2stc2llYmVsLW51bWJlciB7CiAgICAgICAgICAgIG1hcmdpbjogMjBweDsKICAgICAgICB9CgogICAgICAgIGxhYmVsIHsKICAgICAgICAgICAgZGlzcGxheTogYmxvY2s7CiAgICAgICAgICAgIG1hcmdpbi1ib3R0b206IDVweDsKICAgICAgICB9CgogICAgICAgIGlucHV0W3R5cGU9InRleHQiXSB7CiAgICAgICAgICAgIHdpZHRoOiAxMDAlOwogICAgICAgICAgICBwYWRkaW5nOiA4cHg7CiAgICAgICAgICAgIG1hcmdpbi1ib3R0b206IDEwcHg7CiAgICAgICAgfQoKICAgICAgICBidXR0b24gewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMmQ0MTlhOwogICAgICAgICAgICBjb2xvcjogd2hpdGU7CiAgICAgICAgICAgIGJvcmRlcjogbm9uZTsKICAgICAgICAgICAgcGFkZGluZzogMTBweDsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAgbWFyZ2luLXJpZ2h0OiAxMHB4OwoKICAgICAgICB9CgogICAgICAgIGJ1dHRvbjpub3QoW2Rpc2FibGVkXSk6aG92ZXIgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjVhYWVhOwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uOmRpc2FibGVkIHsKICAgICAgICAgICAgb3BhY2l0eTogMC41OwogICAgICAgICAgICBjdXJzb3I6IG5vdC1hbGxvd2VkOwogICAgICAgIH0KICAgIDwvc3R5bGU+CjwvaGVhZD4KCjxib2R5PgogICAgPGRpdiBpZD0iYXNrLXNpZWJlbC1udW1iZXIiPgogICAgICAgIDxsYWJlbCBmb3I9InNpZWJlbF9udW1iZXIiPkVudGVyIFNpZWJlbCBTUiBOdW1iZXI8L2xhYmVsPgogICAgICAgIDxpbnB1dCB0eXBlPSJ0ZXh0IiBpZD0ic2llYmVsX251bWJlciI+CiAgICAgICAgPGJ1dHRvbiBpZD0ic3VibWl0X2J0biIgZGlzYWJsZWQ+T2s8L2J1dHRvbj4KICAgICAgICA8YnV0dG9uIGlkPSJjYW5jZWxfYnRuIj5DYW5jZWw8L2J1dHRvbj4KICAgICAgICA8ZGl2IGNsYXNzPSJsb2FkZXIiIGlkPSJsb2FkZXIiIHN0eWxlPSJkaXNwbGF5OiBub25lIj48L2Rpdj4KICAgIDwvZGl2PgogICAgPHNjcmlwdCBzcmM9Ii4uLy4uL0F1dGhMaWJyYXJ5RXh0bi9BdXRoTGlicmFyeUV4dG4uanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiIHNyYz0ibG9naWMuanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiIHNyYz0iYXNrRm9yU2llYmVsTnVtYmVyLmpzIj48L3NjcmlwdD4KPC9ib2R5PgoKPC9odG1sPg==" data-title="askForSiebelNumber.html"></div>

- **External Script Dependencies**: `../../AuthLibraryExtn/AuthLibraryExtn.js`
- **External Libraries**: `jquery-3.6.0.min.js`, `jquery-ui.js`, `jquery.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js`

#### OSVC Workspace Interaction

- **Fields Read**: `Incident.Created`, `Incident.IId`, `Incident.c$siebel_sr_number`
- **Fields Written**: `Incident.c$siebel_sr_number`
- **Field Listeners Registered**: `Incident.c$siebel_sr_number`
- **Workspace Lifecycle Hooks**: `RecordSaved`
- **Programmatic Editor Commands**: `Save`
- **Modal View Windows**: `askForSiebelNumber.html` (300x150px in `logic.js`), `successMessage.html?siebel_num=` (250x100px in `logic.js`)

#### Report Dependencies & API Endpoints

- **Report Dependencies**: None
##### API Call & Web Service Endpoints Table

| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |
|---|---|---|---|---|---|
| `POST` | `/cc/ajaxCustom/addSrToSiebel` | `CP Controller Endpoint` | — | — | `logic.js` |

#### Risk Audit Findings

| Severity | Risk Type | Detail |
|---|---|---|
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in logic.js — blocks browser UI thread |
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in askForSiebelNumber.js — blocks browser UI thread |
| **High** | `Duplicate Library Load` | Duplicate jQuery versions loaded in init.html: https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js, https://code.jquery.com/jquery-3.6.0.min.js |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in init.html — will fail if add-in path changes |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in askForSiebelNumber.html — will fail if add-in path changes |
| Low | `Unused Library Import` | jsPDF / jsPDF-AutoTable loaded in HTML headers but unreferenced in JavaScript |

  </div>
</details>

## BUI Add-In Flow Diagram

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
  BUI_SendToSiebelBUIAddin["BUI Add-In: SendToSiebelBUIAddin"]:::addin
  API_ccajaxCustomaddSrToSiebel["API: /cc/ajaxCustom/addSrToSiebel"]:::api
  BUI_SendToSiebelBUIAddin --> |"POST"| API_ccajaxCustomaddSrToSiebel
  FW_Incidentcsiebel_sr_number["Field Write: Incident.c$siebel_sr_number"]:::field
  BUI_SendToSiebelBUIAddin -.-> |"Write"| FW_Incidentcsiebel_sr_number
```
