# CPM (Custom Process Model) Summary Report

- **Total Procedures Analyzed**: 8
- **Objects Covered**: `Contact`, `Incident`
- **Execution Breakdown**: 6 Synchronous, 2 Asynchronous
- **Orphan Procedures**: 0 unmapped

---

## Mappings Routing Table (`Mappings.xml`)

| Interface | Object | Event | Procedure | Execution Mode | Mapped Status | Suppress Flag |
|---|---|---|---|---|---|---|
| `scriptpro` | `Contact` | `Create` | `contact_create` | Sync | Active | Yes |
| `scriptpro` | `Contact` | `Update` | `contact_update` | Sync | Active | Yes |
| `scriptpro_customerservice_2` | `Contact` | `Create` | `contact_create_internal` | Sync | Active | Yes |
| `scriptpro_customerservice_2` | `Contact` | `Update` | `contact_update_internal` | Sync | Active | Yes |
| `scriptpro` | `Incident` | `Create` | `incident_create` | Sync | Active | Yes |
| `scriptpro` | `Incident` | `Update` | `incident_back_in_stock_sync` | Sync | Active | Yes |

> **Note on Suppress Flag (`SuppressFlagMapping`)**: In OSVC CPM context, `SuppressFlagMapping` indicates whether recursive event handler execution is suppressed for this object/interface mapping when CPM operations make cascading updates to the same object type.

---

## Cross-Reference Table (CPM Custom Fields ↔ Workspace Fields)

## Object Procedures Breakdown

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #ec4899; color: #ec4899; margin-right: 8px;">Asynchronous</span><b>Procedure: ContactAsync</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100007 | Bound: Contact)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `ContactAsync`

- **ID**: `100007` | **Version**: `100300 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Asynchronous`
- **Operations Bitmask**: `Update (code: 2)`
- **Bound Classes**: `Contact`
- **Mapped Event**: *Unmapped (Orphan Procedure — not found in Mappings.xml)*
- **Key Logic Summary**: This Oracle Service Cloud CPM PHP custom procedure code primarily handles the registration of contacts in Siebel through a SOAP request, and it logs and handles any errors that occur during this process. The code uses the Connect PHP API to interact with the Oracle Service Cloud and implements an object event handler to update contacts, sending a SOAP request to Siebel to register the contact and handling any exceptions or errors that may arise.
- **SOAP Actions / Web Services**: `RegisterContact`
- **Config Settings / Variables**: `CUSTOM_CFG_SIEBEL_PASSWORD`, `CUSTOM_CFG_SIEBEL_URL`, `CUSTOM_CFG_SIEBEL_USERNAME`, `CUSTOM_CFG_WEB_SERVICE_ERROR_EMAIL`

#### Custom Field Workspace Mappings for `ContactAsync`

*No custom fields accessed by this procedure (operates via standard Connect API object properties).*

- **Extracted Functions**: `apply()`, `setRegisterinSiebel()`, `getSoapTop()`, `sendSoapRequest()`, `sendSiebelExceptionEmail()`
- **Message Templates**: `CUSTOM_MSG_WEB_SERVICE_ERROR_BODY`, `CUSTOM_MSG_WEB_SERVICE_ERROR_SUBJECT`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for ContactAsync"]
  START --> CALL_1["self::sendSiebelExceptionEmail()"]
  CALL_1 --> CALL_2["self::setRegisterinSiebel()"]
  CALL_2 --> SAVE_4["Save Record"]
  CALL_2 -.->|Exception| ERR_EX_3["Catch ConnectAPIError"]
  ERR_EX_3 --> SAVE_4
  SAVE_4 --> EXIT_5["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: contact_create</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100001 | Bound: Contact)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `contact_create`

- **ID**: `100001` | **Version**: `100300 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Create (code: 1)`
- **Bound Classes**: `Contact`
- **Mapped Event**: `Contact` on `scriptpro` interface (Create)
- **Key Logic Summary**: This Oracle Service Cloud CPM PHP custom procedure code is designed to handle the creation of new contacts, setting the contact's login to their primary email address and creating a social user account with a display name based on the contact's first name or email address. The code includes error handling and a test harness to validate the functionality of the contact creation process.
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `contact_create`

*No custom fields accessed by this procedure (operates via standard Connect API object properties).*

- **Extracted Functions**: `apply()`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for contact_create"]
  START --> SAVE_1["Save Record"]
  START -.->|Exception| ERR_EX_2["Catch ConnectAPIError"]
  ERR_EX_2 --> SAVE_1
  SAVE_1 --> EXIT_3["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: contact_create_internal</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100004 | Bound: Contact)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `contact_create_internal`

- **ID**: `100004` | **Version**: `100300 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Create (code: 1)`
- **Bound Classes**: `Contact`
- **Mapped Event**: `Contact` on `scriptpro_customerservice_2` interface (Create)
- **Key Logic Summary**: Instantiates and updates OSVC Connect API objects (`Contact`, `PersonName`, `SocialUser`).
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `contact_create_internal`

*No custom fields accessed by this procedure (operates via standard Connect API object properties).*

- **Extracted Functions**: `apply()`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for contact_create_internal"]
  START --> SAVE_1["Save Record"]
  START -.->|Exception| ERR_EX_2["Catch ConnectAPIError"]
  ERR_EX_2 --> SAVE_1
  SAVE_1 --> EXIT_3["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: contact_update</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100002 | Bound: Contact)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `contact_update`

- **ID**: `100002` | **Version**: `100300 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Update (code: 2)`
- **Bound Classes**: `Contact`
- **Mapped Event**: `Contact` on `scriptpro` interface (Update)
- **Key Logic Summary**: Executes ROQL queries against OSVC tables (`CO.ContactOrgJoin`, `Contact`). Instantiates and updates OSVC Connect API objects (`CO\ContactOrgJoin`, `Contact`, `Organization`, `PersonName`, ...).
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `contact_update`

| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |
|---|---|---|---|---|---|---|
| `c$org_id_temp` | **Write** | **Contact test** | Top Form Layout | Row 5, Col 0 | OrgId (Account Lookup) | Temporary Org ID used to populate Contact Organization linkage |

- **Extracted Functions**: `apply()`, `setPrimaryOrgId()`, `updateContactOrgJoin()`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for contact_update"]
  START --> CALL_SET_ORG_1["self::setPrimaryOrgId() - ROQL Query Contact org_id_temp and CO.ContactOrgJoin"]
  CALL_SET_ORG_1 --> CALL_UPD_COJ_2["self::updateContactOrgJoin()"]
  CALL_UPD_COJ_2 --> SAVE_3["Save Record"]
  SAVE_3 --> EXIT_4["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: contact_update_internal</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100005 | Bound: Contact)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `contact_update_internal`

- **ID**: `100005` | **Version**: `100300 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Update (code: 2)`
- **Bound Classes**: `Contact`
- **Mapped Event**: `Contact` on `scriptpro_customerservice_2` interface (Update)
- **Key Logic Summary**: Executes ROQL queries against OSVC tables (`CO.ContactOrgJoin`, `Contact`). Instantiates and updates OSVC Connect API objects (`CO\ContactOrgJoin`, `Contact`, `Organization`, `PersonName`, ...).
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `contact_update_internal`

| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |
|---|---|---|---|---|---|---|
| `c$org_id_temp` | **Read** | **Contact test** | Top Form Layout | Row 5, Col 0 | OrgId (Account Lookup) | Temporary Org ID used to populate Contact Organization linkage |

- **Extracted Functions**: `apply()`, `setPrimaryOrgId()`, `updateContactOrgJoin()`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for contact_update_internal"]
  START --> CALL_SET_ORG_1["self::setPrimaryOrgId() - ROQL Query Contact org_id_temp and CO.ContactOrgJoin"]
  CALL_SET_ORG_1 --> CALL_UPD_COJ_2["self::updateContactOrgJoin()"]
  CALL_UPD_COJ_2 --> SAVE_3["Save Record"]
  SAVE_3 --> EXIT_4["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: incident_back_in_stock_sync</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100099 | Bound: Incident)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `incident_back_in_stock_sync`

- **ID**: `100099` | **Version**: `100400 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Create (code: 1)`
- **Bound Classes**: `Incident`
- **Mapped Event**: `Incident` on `scriptpro` interface (Update)
- **Key Logic Summary**: Executes static custom handler logic for `incident_back_in_stock_sync`.
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `incident_back_in_stock_sync`

| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |
|---|---|---|---|---|---|---|
| `c$oos_status` | **Write** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |

- **Extracted Functions**: `apply()`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for incident_back_in_stock_sync"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #6366f1; color: #6366f1; margin-right: 8px;">Synchronous</span><b>Procedure: incident_create</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100003 | Bound: Incident)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `incident_create`

- **ID**: `100003` | **Version**: `100400 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Synchronous`
- **Operations Bitmask**: `Create (code: 1)`
- **Bound Classes**: `Incident`
- **Mapped Event**: `Incident` on `scriptpro` interface (Create)
- **Key Logic Summary**: Processes Techmail-originated incoming records. Parses email headers and subject lines for reference numbers and customer identifiers via regex. Executes ROQL queries against OSVC tables (`Incident`). Instantiates and updates OSVC Connect API objects (`Incident`, `MailMessage`, `MessageBase`, `NamedIDOptList`, ...).
- **SOAP Actions**: None

#### Custom Field Workspace Mappings for `incident_create`

| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |
|---|---|---|---|---|---|---|
| `c$change_request_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$customer_email_address` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$customer_name` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$customer_phone` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$drug_code` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$drug_distributor` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$drug_dosage` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$drug_name` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$drug_part_number` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$incident_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$move_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$mp_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$new_vpn_setup` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$org_id_temp` | **Read** | **Contact test** | Top Form Layout | Row 5, Col 0 | OrgId (Account Lookup) | Temporary Org ID used to populate Contact Organization linkage |
| `c$testing_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$token` | **Write** | **Incident** | Tab: Details | *(Custom Field)* | c$token | [Audit Flag: verify security/session token written on incident create] |
| `c$user_profile` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$user_request_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |

- **Extracted Functions**: `apply()`, `getRandomString()`, `sendEmail()`
- **Constants Defined**: `CSC_USER_MANAGMENT:53`, `VPN_REQUEST:74`, `EQUIPMENT_RELOCATION_REQUEST:54`, `VIAL_CONVERSION_PROCESS_REQUEST:55`, `CASSETTE_TESTING_SUPPORT:76`, `INTERFACE_EVALUATION:79`, `THREAD_ENTRY_TYPE_PRIVATE_NOTE:1`, `THREAD_ENTRY_TYPE_CUSTOMER:3`, `THREAD_CONTENT_TYPE_HTML:2`
- **Message Templates**: `CUSTOM_MSG_ACCOUNT_QUESTIONS_LBL`, `CUSTOM_MSG_ADDITIONAL_DETAILS_LBL`, `CUSTOM_MSG_CC_EMAIL`, `CUSTOM_MSG_CC_SUBJECT`, `CUSTOM_MSG_CURRENT_MANUFACTURER_LBL`, `CUSTOM_MSG_EQUIPMENT_LBL`, `CUSTOM_MSG_NEW_MANUFACTURER_LBL`, `CUSTOM_MSG_PARTY_RESPONSIBLE_LBL`, `CUSTOM_MSG_TESTING_DETAILS_LBL`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for incident_create"]
  START --> SRC_DECISION_1{"Check Entry Source"}
  SRC_DECISION_1 -->|Techmail Source| PROC_TECHMAIL_2["Parse Mail Header and Subject - ROQL Lookup Org by Customer or Ref Number"]
  PROC_TECHMAIL_2 --> SAVE_T_3["Save Record"]
  SAVE_T_3 --> EXIT_T_4["Exit"]
  SRC_DECISION_1 -->|AAQ or Portal Source| PROC_AAQ_5["ROQL Lookup Org ID from Incident"]
  PROC_AAQ_5 --> REQ_DECISION_6{"Fork on request_type"}
  REQ_DECISION_6 -->|CSC_USER_MANAGEMENT| BRANCH_7["Process CSC User Management Logic"]
  BRANCH_7 --> CALL_EMAIL_8["self::sendEmail()"]
  CALL_EMAIL_8 --> SAVE_B_9["Save Record"]
  SAVE_B_9 --> EXIT_B_10["Exit"]
  REQ_DECISION_6 -->|VPN_REQUEST| BRANCH_11["Process VPN Request Logic"]
  BRANCH_11 --> CALL_EMAIL_12["self::sendEmail()"]
  CALL_EMAIL_12 --> SAVE_B_13["Save Record"]
  SAVE_B_13 --> EXIT_B_14["Exit"]
  REQ_DECISION_6 -->|EQUIPMENT_RELOCATION| BRANCH_15["Process Equipment Relocation Logic"]
  BRANCH_15 --> CALL_EMAIL_16["self::sendEmail()"]
  CALL_EMAIL_16 --> SAVE_B_17["Save Record"]
  SAVE_B_17 --> EXIT_B_18["Exit"]
  REQ_DECISION_6 -->|VIAL_CONVERSION| BRANCH_19["Process Vial Conversion Process Logic"]
  BRANCH_19 --> CALL_EMAIL_20["self::sendEmail()"]
  CALL_EMAIL_20 --> SAVE_B_21["Save Record"]
  SAVE_B_21 --> EXIT_B_22["Exit"]
  REQ_DECISION_6 -->|CASSETTE_TESTING| BRANCH_23["Process Cassette Testing Support Logic"]
  BRANCH_23 --> CALL_EMAIL_24["self::sendEmail()"]
  CALL_EMAIL_24 --> SAVE_B_25["Save Record"]
  SAVE_B_25 --> EXIT_B_26["Exit"]
  REQ_DECISION_6 -->|INTERFACE_EVALUATION| BRANCH_27["Process Interface Evaluation Logic"]
  BRANCH_27 --> CALL_EMAIL_28["self::sendEmail()"]
  CALL_EMAIL_28 --> SAVE_B_29["Save Record"]
  SAVE_B_29 --> EXIT_B_30["Exit"]
  REQ_DECISION_6 -->|Default Fallback| SAVE_GEN_31["Save Record"]
  SAVE_GEN_31 --> EXIT_GEN_32["Exit"]
  SRC_DECISION_1 -->|Other Direct Source| DEFAULT_33["Save Record"]
  DEFAULT_33 --> EXIT_DEF_34["Exit"]
```

</div>

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #ec4899; color: #ec4899; margin-right: 8px;">Asynchronous</span><b>Procedure: incident_routing</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(ID: 100006 | Bound: Incident)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Procedure: `incident_routing`

- **ID**: `100006` | **Version**: `100400 [internal version stamp]` | **PHP Version**: `5.6.0 (50600)`
- **Execution Mode**: `Asynchronous`
- **Operations Bitmask**: `Create, Update (code: 3)`
- **Bound Classes**: `Incident`
- **Mapped Event**: *Unmapped (Orphan Procedure — not found in Mappings.xml)*
- **Key Logic Summary**: Processes Techmail-originated incoming records. Parses email headers and subject lines for reference numbers and customer identifiers via regex. Queries external Siebel SOAP web services (`GetAccounts`). Executes ROQL queries against OSVC tables (`Incident`, `Organization`). Instantiates and updates OSVC Connect API objects (`CO\ContactOrgJoin`, `Configuration`, `Contact`, `GroupAccount`, ...). Evaluates customer eligibility and dispatches rejection notification emails for unregistered or invalid accounts.
- **SOAP Actions / Web Services**: `GetAccounts`
- **Config Settings / Variables**: `CUSTOM_CFG_MAILBOX_ACCOUNT_MANAGEMENT`, `CUSTOM_CFG_MAILBOX_TECH_SUPPORT`, `CUSTOM_CFG_SIEBEL_PASSWORD`, `CUSTOM_CFG_SIEBEL_URL`, `CUSTOM_CFG_SIEBEL_USERNAME`

#### Custom Field Workspace Mappings for `incident_routing`

| CPM Custom Field | Access Mode | Target Workspace | Location / Tab | Grid Position | Field Label | Audit / Relationship Note |
|---|---|---|---|---|---|---|
| `c$change_request_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$customer_number` | **Write** | **Contact test** | Top Form Layout | Row 7, Col 0 | C$CustomerId | Matches customer number / ID field |
| `c$customer_number` | **Write** | **New Workspace** | Tab: Customer 360 | Row 0, Col 0 | C$AccountNumber | Matches customer account identifier |
| `c$force_update` | **Write** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$incident_routing_outcome` | **Write** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$incident_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$is_admin` | **Write** | **Contact test** | Tab: Contact Fields | Row 10, Col 0 | c$is_admin | Updated by incident_routing handler |
| `c$is_manual` | **Write** | **Contact test** | Tab: Contact Fields | Row 9, Col 0 (Col 9) | c$is_manual | Expected write from contact_create_internal — not detected in exported Content |
| `c$no_chat` | **Write** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$org_id_temp` | **Write** | **Contact test** | Top Form Layout | Row 5, Col 0 | OrgId (Account Lookup) | Temporary Org ID used to populate Contact Organization linkage |
| `c$org_label_temp` | **Write** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$siebel_status` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$sp_system_type` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |
| `c$type_name` | **Read** | ***(Background Logic)*** | — | — | — | Operated purely via Connect API / CPM script logic |

- **Extracted Functions**: `apply()`, `handleRejects()`, `sendEmail()`, `getAccounts()`, `getSoapTop()`, `sendSoapRequest()`, `createUpdateOrg()`, `getOrgId()`, `updateContact()`, `createContactOrgJoin()`
- **Message Templates**: `CUSTOM_MSG_REJECT_BOTH`, `CUSTOM_MSG_REJECT_CUSTOMER_NUMBER`, `CUSTOM_MSG_REJECT_EMAIL`, `CUSTOM_MSG_REJECT_MISMATCH`, `CUSTOM_MSG_REJECT_SIEBEL_300`, `CUSTOM_MSG_REJECT_SP_TYPE`, `CUSTOM_MSG_REJECT_SUBJECT`, `CUSTOM_MSG_REJECT_SUPPORT_HOLD`, `CUSTOM_MSG_REJECT_TEMPLATE`

**Logic Flow Diagram**:
<div align="center">

```mermaid
graph TD
  START["apply() called for incident_routing"]
  START --> SRC_DECISION_1{"Check Entry Source"}
  SRC_DECISION_1 -->|Techmail Source| PROC_TECHMAIL_2["Parse Mail Header and Subject - ROQL Lookup Org by Customer or Ref Number"]
  PROC_TECHMAIL_2 --> GET_ACC_3["self::getAccounts()"]
  GET_ACC_3 -.->|Error or Invalid| REJ_ERR_4["self::handleRejects() Rejection Path"]
  REJ_ERR_4 --> EXIT_REJ_5["Exit"]
  GET_ACC_3 -->|Valid Account| CREATE_ORG_6["self::createUpdateOrg() - self::createContactOrgJoin() - self::updateContact()"]
  CREATE_ORG_6 --> ROUTE_QUEUE_7["Route Queue by System Type - PMS WF SA HMS TPMS"]
  ROUTE_QUEUE_7 --> SAVE_T_8["Save Record"]
  SAVE_T_8 --> EXIT_T_9["Exit"]
  SRC_DECISION_1 -->|AAQ or Portal Source| PROC_AAQ_10["ROQL Lookup Org ID from Incident"]
  PROC_AAQ_10 --> GET_ACC_AAQ_11["self::getAccounts()"]
  GET_ACC_AAQ_11 -.->|Error| REJ_AAQ_12["self::handleRejects()"]
  REJ_AAQ_12 --> EXIT_REJ_A_13["Exit"]
  GET_ACC_AAQ_11 -->|Valid| ROUTE_AAQ_14["Route Queue by Incident or Change Type"]
  ROUTE_AAQ_14 --> SAVE_A_15["Save Record"]
  SAVE_A_15 --> EXIT_A_16["Exit"]
  SRC_DECISION_1 -->|Other Direct Source| DEFAULT_17["Save Record"]
  DEFAULT_17 --> EXIT_DEF_18["Exit"]
```

</div>

  </div>
</details>

---

## Flow Diagram

<div align="center">

```mermaid
graph LR
  classDef mapping fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
  classDef proc fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;
  classDef asyncProc fill:#ec4899,stroke:#be185d,stroke-width:1px,color:#fff;
  classDef soap fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;
  classDef orphan fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
  classDef obj fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;

  subgraph Mappings_Layer
    M_MAP["Mappings.xml"]:::mapping
  end

  subgraph Objects_Layer
    O_Contact["OSVC Object: Contact"]:::obj
    O_Incident["OSVC Object: Incident"]:::obj
  end

  subgraph Procedures_Layer
    P_ContactAsync["ContactAsync (Async)"]:::asyncProc
    P_contact_create["contact_create (Sync)"]:::proc
    P_contact_create_internal["contact_create_internal (Sync)"]:::proc
    P_contact_update["contact_update (Sync)"]:::proc
    P_contact_update_internal["contact_update_internal (Sync)"]:::proc
    P_incident_back_in_stock_sync["incident_back_in_stock_sync (Sync)"]:::proc
    P_incident_create["incident_create (Sync)"]:::proc
    P_incident_routing["incident_routing (Async)"]:::asyncProc
  end

  subgraph Endpoints_Layer
    SOAP_RegisterContact["SOAP Action: RegisterContact"]:::soap
    SOAP_GetAccounts["SOAP Action: GetAccounts"]:::soap
  end

  M_MAP --> |"scriptpro / Contact / Create"| P_contact_create
  M_MAP --> |"scriptpro / Contact / Update"| P_contact_update
  M_MAP --> |"scriptpro_customerservice_2 / Contact / Create"| P_contact_create_internal
  M_MAP --> |"scriptpro_customerservice_2 / Contact / Update"| P_contact_update_internal
  M_MAP --> |"scriptpro / Incident / Create"| P_incident_create
  M_MAP --> |"scriptpro / Incident / Update"| P_incident_back_in_stock_sync
  P_ContactAsync -.-> SOAP_RegisterContact
  P_ContactAsync -.-> |"Target Object"| O_Contact
  P_contact_create -.-> |"Target Object"| O_Contact
  P_contact_create_internal -.-> |"Target Object"| O_Contact
  P_contact_update -.-> |"Target Object"| O_Contact
  P_contact_update_internal -.-> |"Target Object"| O_Contact
  P_incident_back_in_stock_sync -.-> |"Target Object"| O_Incident
  P_incident_create -.-> |"Target Object"| O_Incident
  P_incident_routing -.-> SOAP_GetAccounts
  P_incident_routing -.-> |"Target Object"| O_Incident
```

</div>
