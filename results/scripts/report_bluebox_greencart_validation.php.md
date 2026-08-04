# Custom Script Analysis: `bluebox_greencart_validation.php`
## Executive Functional Summary

> [!NOTE]
> This script validates **Municipal Waste & Recycling Collection Schedules (Blue Box / Green Cart)**. It queries address custom fields, checks collection calendars, and returns schedule lookup responses.

## Script Overview & Attributes

| Attribute | Value |
| --- | --- |
| **File Name** | `bluebox_greencart_validation.php` |
| **Script Type** | Server-side Utility |
| **Contains JavaScript Code** | Yes |
| **Contains HTML UI Markup** | No |
| **Code Imports** | 0 |
| **OSVC Data Objects** | 1 |
| **Internal APIs (ROQL / Connect)** | 1 |
| **External SOAP APIs** | 0 |
| **External REST APIs** | 0 |
| **Risk Flags** | 0 |

## OSVC Data Objects Referenced

- `ConnectAPIErrorBase`

## Categorized API Breakdown

### 1. Internal APIs (ROQL & Native OSVC Objects)

| API Type | Operation | Details |
| --- | --- | --- |
| `Agent Authenticator` | Validate Agent Session | `AgentAuthenticator::authenticateSessionID($session_id)` |

### 2. External APIs (SOAP)

*No External SOAP Web Service integrations detected.*

### 3. External APIs (REST)

*No External REST HTTP API integrations detected.*

## Execution Flow Diagram

```mermaid
sequenceDiagram
  autonumber
  participant Client as Client / Trigger
  participant Script as Script (bluebox_greencart_validation.php)
  participant OSVC as OSVC Connect API / DB
  Client->>Script: Execute / Invoke Request
  Script->>OSVC: Validate Agent Session ID
  OSVC-->>Script: Return Data / Context
  Script-->>Client: Return Script Execution Response
```

## Client-Side JavaScript Logic & UI Behavior Summary

The script incorporates client-side JavaScript execution logic with the following UI behaviors and event handlers:

- Registers BUI Extension Loader hooks (`ORACLE_SERVICE_CLOUD.extension_loader`) and binds workspace record events.
- Attaches dynamic workspace field value change listeners to trigger real-time search and validation as fields are edited.
- Loads ArcGIS JavaScript API components for map rendering and geocoding coordinate selection.
