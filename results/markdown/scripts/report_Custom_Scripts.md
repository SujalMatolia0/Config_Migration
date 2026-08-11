# Custom Scripts Analysis Summary

**Total Custom Scripts:** 26

## Overview Table

| Script File | Type | Internal APIs | SOAP APIs | REST APIs | Risk Flags |
| --- | --- | --- | --- | --- | --- |
| `ExtendedSample.php` | Controller Endpoint | 0 | 0 | 0 | [OK] |
| `MySocialSearch.php` | Controller Endpoint | 0 | 0 | 0 | [OK] |
| `ParameterTrimSample.php` | Server-side Utility | 0 | 0 | 0 | [OK] |
| `Sample.php` | Controller Endpoint | 0 | 0 | 0 | [OK] |
| `address_validation.php` | Server-side Utility | 9 | 0 | 3 | [RISK: 1] |
| `answer_model.php` | Model Helper | 11 | 0 | 0 | [RISK: 1] |
| `answerfeedback_model.php` | Model Helper | 3 | 0 | 0 | [OK] |
| `bluebox_greencart_validation.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `callcheck.php` | Server-side Utility | 4 | 0 | 1 | [OK] |
| `child_incident_create.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `cityworksapicall.php` | Server-side Utility | 3 | 0 | 1 | [OK] |
| `clickstream_model.php` | Model Helper | 2 | 0 | 0 | [OK] |
| `closing_notes.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `contact_model.php` | Model Helper | 23 | 0 | 0 | [OK] |
| `customChat.php` | Server-side Utility | 0 | 0 | 0 | [OK] |
| `customfield_model.php` | Model Helper | 1 | 0 | 0 | [RISK: 1] |
| `daily_dupe_detection_0584.php` | Server-side Utility | 6 | 0 | 0 | [OK] |
| `dupe_detection_8366.php` | Server-side Utility | 6 | 0 | 1 | [OK] |
| `duplicate_contacts.php` | Server-side Utility | 9 | 0 | 0 | [OK] |
| `duplicate_incidents.php` | Server-side Utility | 3 | 0 | 0 | [OK] |
| `eventclock.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `header.inc_4778.php` | Server-side Utility | 0 | 0 | 0 | [OK] |
| `incident_model.php` | Model Helper | 9 | 0 | 0 | [RISK: 1] |
| `report_model.php` | Controller Endpoint | 5 | 0 | 0 | [RISK: 1] |
| `sample_model.php` | Model Helper | 0 | 0 | 0 | [OK] |
| `sms_integration 1.php` | Server-side Utility | 5 | 1 | 1 | [RISK: 1] |

---

## Script Details Breakdown

### Script: `ExtendedSample.php` (Controller Endpoint)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `MySocialSearch.php` (Controller Endpoint)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `ParameterTrimSample.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `Sample.php` (Controller Endpoint)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `address_validation.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 9
- **External SOAP APIs:** 0
- **External REST APIs:** 3
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `ROQL`
- **URLs / Endpoints:** `https://js.arcgis.com/4.20/`, `https://js.arcgis.com/4.20/esri/themes/light/main.css`, `https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### Script: `answer_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 11
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### Script: `answerfeedback_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 3
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `Contact`

### Script: `bluebox_greencart_validation.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 1
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `ConnectAPIErrorBase`

### Script: `callcheck.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 4
- **External SOAP APIs:** 0
- **External REST APIs:** 1
- **OSVC Objects:** `Account`, `Configuration`
- **URLs / Endpoints:** `http://209.91.135.228/api/listactivecalls/`

### Script: `child_incident_create.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 1
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **Imports:** `include/init.phph`
- **OSVC Objects:** `Banner`, `ConnectAPI`, `GroupAccount`, `Incident`, `NamedIDLabel`, `NamedIDOptList`, `RNObject`, `StatusWithType`

### Script: `cityworksapicall.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 3
- **External SOAP APIs:** 0
- **External REST APIs:** 1
- **Imports:** `include/init.phph`
- **OSVC Objects:** `Configuration`, `ConnectAPI`

### Script: `clickstream_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 2
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `closing_notes.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 2
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `Account`, `ConnectAPI`, `ConnectAPIErrorBase`

### Script: `contact_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 23
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `customChat.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `customfield_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 1
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### Script: `daily_dupe_detection_0584.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 6
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **Imports:** `header.inc.php`
- **OSVC Objects:** `Contact`, `Incident`, `RNObject`, `ROQL`

### Script: `dupe_detection_8366.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 6
- **External SOAP APIs:** 0
- **External REST APIs:** 1
- **Imports:** `header.inc.php`
- **OSVC Objects:** `Contact`, `Incident`, `RNObject`, `ROQL`

### Script: `duplicate_contacts.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 9
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **Imports:** `address_validation.php`
- **OSVC Objects:** `AnalyticsReport`, `CO`, `ConnectAPIErrorBase`, `Contact`, `ROQL`
- **URLs / Endpoints:** `https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css`, `https://cdn.datatables.net/1.10.20/js/jquery.dataTables.js`, `https://use.fontawesome.com/releases/v5.1.1/css/all.css`

### Script: `duplicate_incidents.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 3
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `ConnectAPIErrorBase`, `ROQL`
- **URLs / Endpoints:** `https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css`, `https://cdn.datatables.net/1.10.20/js/jquery.dataTables.js`, `https://use.fontawesome.com/releases/v5.1.1/css/all.css`

### Script: `eventclock.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 2
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `ConnectAPIErrorBase`, `ROQL`

### Script: `header.inc_4778.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `ConnectAPI`

### Script: `incident_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 9
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### Script: `report_model.php` (Controller Endpoint)

- **Internal APIs (ROQL/Connect):** 5
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 5)

### Script: `sample_model.php` (Model Helper)

- **Internal APIs (ROQL/Connect):** 0
- **External SOAP APIs:** 0
- **External REST APIs:** 0

### Script: `sms_integration 1.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 5
- **External SOAP APIs:** 1
- **External REST APIs:** 1
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `NamedIDLabel`, `Note`, `NoteArray`, `RNObject`, `ROQL`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)
