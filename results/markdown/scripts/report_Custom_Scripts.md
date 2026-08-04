# Custom Scripts Analysis Summary

**Total Custom Scripts:** 10

## Overview Table

| Script File | Type | Internal APIs | SOAP APIs | REST APIs | Risk Flags |
| --- | --- | --- | --- | --- | --- |
| `address_validation.php` | Server-side Utility | 9 | 0 | 3 | [RISK: 1] |
| `bluebox_greencart_validation.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `callcheck.php` | Server-side Utility | 4 | 0 | 1 | [OK] |
| `child_incident_create.php` | Server-side Utility | 1 | 0 | 0 | [OK] |
| `cityworksapicall.php` | Server-side Utility | 3 | 0 | 1 | [OK] |
| `closing_notes.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `duplicate_contacts.php` | Server-side Utility | 8 | 0 | 0 | [OK] |
| `duplicate_incidents.php` | Server-side Utility | 3 | 0 | 0 | [OK] |
| `eventclock.php` | Server-side Utility | 2 | 0 | 0 | [OK] |
| `sms_integration 1.php` | Server-side Utility | 5 | 1 | 1 | [RISK: 1] |

---

## Script Details Breakdown

### Script: `address_validation.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 9
- **External SOAP APIs:** 0
- **External REST APIs:** 3
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `ROQL`
- **URLs / Endpoints:** `https://js.arcgis.com/4.20/esri/themes/light/main.css`, `https://js.arcgis.com/4.20/`, `https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js`
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

### Script: `duplicate_contacts.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 8
- **External SOAP APIs:** 0
- **External REST APIs:** 0
- **OSVC Objects:** `CO`, `ConnectAPIErrorBase`, `Contact`, `ROQL`
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

### Script: `sms_integration 1.php` (Server-side Utility)

- **Internal APIs (ROQL/Connect):** 5
- **External SOAP APIs:** 1
- **External REST APIs:** 1
- **OSVC Objects:** `Configuration`, `ConnectAPIErrorBase`, `NamedIDLabel`, `Note`, `NoteArray`, `RNObject`, `ROQL`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)
