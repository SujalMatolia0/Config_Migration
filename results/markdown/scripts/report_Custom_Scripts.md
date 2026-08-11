# Custom Scripts Analysis Summary

**Total Custom Scripts:** 13

## Overview Table

| Script File | Type | Internal APIs | SOAP APIs | REST APIs | Risk Flags |
| --- | --- | --- | --- | --- | --- |
| `address_validation.php` | Server-side Utility | 9 | 0 | 3 | [RISK: 1] |
| `bluebox_greencart_validation.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `callcheck.php` | Server-side Utility | 4 | 0 | 1 | [OK] |
| `child_incident_create.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `cityworksapicall.php` | Server-side Utility | 3 | 0 | 1 | [OK] |
| `closing_notes.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `daily_dupe_detection_0584.php` | Server-side Utility | 6 | 0 | 0 | [OK] |
| `dupe_detection_8366.php` | Server-side Utility | 6 | 0 | 1 | [OK] |
| `duplicate_contacts.php` | Server-side Utility | 9 | 0 | 0 | [OK] |
| `duplicate_incidents.php` | Server-side Utility | 3 | 0 | 0 | [OK] |
| `eventclock.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `header.inc_4778.php` | Server-side Utility | 0 | 0 | 0 | [OK] |
| `sms_integration 1.php` | Server-side Utility | 5 | 1 | 1 | [RISK: 1] |

---

## Script Details Breakdown

### Script: `address_validation.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 9
- **External SOAP APIs:** 0
- **External REST APIs:** 3
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `ROQL`
- **URLs / Endpoints:** `https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js`, `https://js.arcgis.com/4.20/`, `https://js.arcgis.com/4.20/esri/themes/light/main.css`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

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

### Script: `closing_notes.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 2
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `Account`, `ConnectAPI`, `ConnectAPIErrorBase`

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
- **URLs / Endpoints:** `https://use.fontawesome.com/releases/v5.1.1/css/all.css`, `https://cdn.datatables.net/1.10.20/js/jquery.dataTables.js`, `https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css`

### Script: `duplicate_incidents.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 3
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `ConnectAPIErrorBase`, `ROQL`
- **URLs / Endpoints:** `https://use.fontawesome.com/releases/v5.1.1/css/all.css`, `https://cdn.datatables.net/1.10.20/js/jquery.dataTables.js`, `https://cdn.datatables.net/1.10.20/css/jquery.dataTables.css`

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

### Script: `sms_integration 1.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 5
- **External SOAP APIs:** 1
- **External REST APIs:** 1
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `NamedIDLabel`, `Note`, `NoteArray`, `RNObject`, `ROQL`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)
