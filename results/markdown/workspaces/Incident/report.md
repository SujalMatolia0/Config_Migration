## System Info

- Platform: **Oracle Service Cloud 26A SP2** (Build 326, June 2026)
- Client Version: `26.2.0.326`
- Workspace Type: **Incident** (single record, not multi-edit)

---

## Layout Structure

The workspace layout is structured as a root **TabSet** containing 8 tabs.

---

## Layout & Tab Details

Below is the detailed content breakdown of each tab:

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Incident Details</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Incident Details`

> **Single Component Tab**

- **Control Type:** Related Object (`Incident Thread`)
  - **Secondary Report (SearchId):** `125`
  - **CanSendOnSave:** Enabled
  - **Default Customer Channel:** `Phone`

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Customer 360</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Customer 360`

> **Single Component Tab**

- **Control Type:** Embedded Browser
  - **Target URL:** `https://gcb.custhelp.com/cgi-bin/gcb.cfg/php/custom/gcb_flex.php?mobile=$contact.phmobile`

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Summary</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(11 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Summary`

> **Multi-Component Tab** — 11 controls across 1 types: 11 Form Fields

**1. Form Fields & Menus**

| Position (Row, Col) | Field / Control | Details |
|---|---|---|
| Row 0, Col 1 | Header: "Details" | Section TitleBar banner |
| Row 0, Col 2 | Header: "Contact Details" | Section TitleBar banner |
| Row 0, Col 3 | Header: "Categorization" | Section TitleBar banner |
| Row 1, Col 1 | `ProdId` | Product — *Required: OnNew (All Profiles), OnEdit (All Profiles)* |
| Row 1, Col 2 | `CId` | Form field (Lookup → Report **8014**) |
| Row 1, Col 3 | `Status.Id` | Status |
| Row 2, Col 1 | `Subject` | Incident Subject |
| Row 2, Col 2 | `ChanId` | Channel |
| Row 2, Col 3 | `CatId` | Category — *Required: OnNew (All Profiles), OnEdit (All Profiles)* |
| Row 3, Col 0 | `RefNo` | Form field |
| Row 3, Col 1 | `Assigned` | Assigned Agent/Group |
| Row 3, Col 2 | `PhOffice` | Relabeled as **"Mobile Phone"**, default type 1 |
| Row 3, Col 3 | `QueueId` | Queue |
| Row 4, Col 2 | `C$Gender` | Custom field — gender — *Required: OnNew (All Profiles), OnEdit (All Profiles)* |

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Contacts</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(5 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Contacts`

> **Multi-Component Tab** — 5 controls across 1 types: 5 Form Fields

**1. Form Fields & Menus**

| Position (Row, Col) | Field / Control | Details |
|---|---|---|
| Row 0, Col 0 | Header: "Primary Contact Information" | Section TitleBar banner |
| Row 1, Col 0 | `Name.First` | First name |
| Row 1, Col 1 | `Name.Last` | Last name |
| Row 2, Col 0 | `Email` | Email address |
| Row 2, Col 1 | `Addr` | Address |
| Row 3, Col 0 | `PhOffice` | Office phone |

> **Nested TabSet** (Row 4, Col 0) — 3 Sub-Tabs: **Contacts**, **Contact Fields**, **Incident History**


#### Sub-Tab: `Contacts`

> **Single Component Tab**

- **Control Type:** Related Object (`Contact`)
  - **Primary Report (AcId):** `9011`
  - **Secondary Report (SearchId):** `8014`
  - **Behavior:** Skips execution on unsaved new records


#### Sub-Tab: `Contact Fields`

**Layout Grid Structure (Fields & Nested Controls):**

| Position (Row, Col) | Control Type | Control Name / Field | Target / Action Details |
|---|---|---|---|
| Row 0, Col 0 | Form Field | `Login` | Form field |
| Row 0, Col 1 | Form Field | `MaOptIn` | Form field |
| Row 0, Col 2 | Form Field | `State` | Form field |
| Row 1, Col 1 | Form Field | `MaMailType` | Form field |
| Row 1, Col 2 | Form Field | `Source` | Form field |


#### Sub-Tab: `Incident History`

> **Single Component Tab**

- **Control Type:** Direct Report
  - **Primary Report (AcId):** `9029`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Other Info</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(5 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Other Info`

> **Multi-Component Tab** — 5 controls across 1 types: 5 Form Fields

**1. Form Fields & Menus**

| Position (Row, Col) | Field / Control | Details |
|---|---|---|
| Row 0, Col 0 | `Spacer` | Visual layout spacing (26px height) |
| Row 1, Col 0 | `MailboxId` | Form field |
| Row 1, Col 1 | `InterfaceId` | Form field |
| Row 1, Col 2 | `SlaiId` | Form field |
| Row 2, Col 0 | `Source` | Form field |
| Row 2, Col 1 | `LangId` | Form field |

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Tasks</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Tasks`

> **Single Component Tab**

- **Control Type:** Related Object (`Task`)
  - **Primary Report (AcId):** `9018`
  - **Secondary Report (SearchId):** `8010`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Attachments</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Attachments`

> **Single Component Tab**

- **Control Type:** Related Object (`File Attachment`)

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Audit Log</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Audit Log`

> **Single Component Tab**

- **Control Type:** Related Object (`Audit Log`)
  - **Primary Report (AcId):** `9041`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


---

## Workspace Fields Inventory

Total Fields Used in Workspace: **26** (Standard Schema Fields: **25** | Custom Fields (`c$`): **1**)

| Field ID / Reference | Field Label | Field Type | Location / Tab | Options & Constraints |
|---|---|---|---|---|
| `ProdId` | — | Standard Schema | Tab: Summary | Required: OnNew (All Profiles), OnEdit (All Profiles) |
| `CId` | — | Standard Schema | Tab: Summary | — |
| `Status.Id` | — | Standard Schema | Tab: Summary | — |
| `Subject` | — | Standard Schema | Tab: Summary | — |
| `ChanId` | — | Standard Schema | Tab: Summary | — |
| `CatId` | — | Standard Schema | Tab: Summary | Required: OnNew (All Profiles), OnEdit (All Profiles) |
| `RefNo` | — | Standard Schema | Tab: Summary | — |
| `Assigned` | — | Standard Schema | Tab: Summary | — |
| `PhOffice` | &Mobile Phone | Standard Schema | Tab: Summary | Default: `1` |
| `QueueId` | — | Standard Schema | Tab: Summary | — |
| `C$Gender` | — | Custom (`c$`) | Tab: Summary | Required: OnNew (All Profiles), OnEdit (All Profiles) |
| `Name.First` | — | Standard Schema | Tab: Contacts | — |
| `Name.Last` | — | Standard Schema | Tab: Contacts | — |
| `Email` | — | Standard Schema | Tab: Contacts | — |
| `Addr` | — | Standard Schema | Tab: Contacts | — |
| `PhOffice` | — | Standard Schema | Tab: Contacts | Default: `0` |
| `Login` | — | Standard Schema | Tab: Contacts -> Tab: Contact Fields | — |
| `MaOptIn` | — | Standard Schema | Tab: Contacts -> Tab: Contact Fields | — |
| `State` | — | Standard Schema | Tab: Contacts -> Tab: Contact Fields | — |
| `MaMailType` | — | Standard Schema | Tab: Contacts -> Tab: Contact Fields | — |
| `Source` | — | Standard Schema | Tab: Contacts -> Tab: Contact Fields | — |
| `MailboxId` | — | Standard Schema | Tab: Other Info | — |
| `InterfaceId` | — | Standard Schema | Tab: Other Info | — |
| `SlaiId` | — | Standard Schema | Tab: Other Info | — |
| `Source` | — | Standard Schema | Tab: Other Info | — |
| `LangId` | — | Standard Schema | Tab: Other Info | — |

---
## Workspace Rules

### Event: Editor Initialized (On Load)

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>New Rule</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `New Rule` (Active)
- **Condition:** `Field: Contact.CtypeId == 3` (a specific contact type, likely "Email" or similar)
- **Then:**
  - Standard: Hidden Tab: **Customer 360** → True
  - Show a message box — *"This contact is created through email and may not hold sufficient information in the system"*

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Show Gmoney related product and categories</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Show Gmoney related product and categories` (Active)
*This rule is to show only the gmoney related product and categories for GMoney Incidents*

- **Condition:** `Profile: Current LIST 7;8;2;6`
- **Then:**
  - Standard: ConfigureMenuItems Incident.ProdId (EQ u0;383)
  - Standard: ConfigureMenuItems Incident.CatId (EQ 384;385)

  </div>
</details>

---

## Ribbon / Toolbar

Standard actions: Appointment, BestAnswer, Copy, Delete, Forward, Info, New, Print, Propose, Refresh, Save, Save & Close, SaveAndSend, Spell Check.

---

## Key Observations

- The **Customer 360** tab embeds an internal **custom PHP script**: `gcb_flex.php` (`/cgi-bin/gcb.cfg/php/custom/gcb_flex.php`) — passes URL params: `mobile`. Errors are suppressed.
- The workspace defines **2 active business rules** triggered by editor loading events, enforcing profile-based field locking and toolbar UI visibility.
- The **workspace flag indicator** is explicitly hidden (`Visible="False"`), suppressing visual cues for users/agents.

---

## Flow Diagram

```mermaid
graph LR
  classDef workspace fill:#eab308,stroke:#854d0e,stroke-width:2px,color:#0f172a;
  classDef tab fill:#e0f2fe,stroke:#0284c7,stroke-width:1px,color:#0369a1;
  classDef report fill:#3b82f6,stroke:#1d4ed8,stroke-width:1px,color:#fff;
  classDef browser fill:#ef4444,stroke:#b91c1c,stroke-width:1px,color:#fff;
  classDef rule fill:#ec4899,stroke:#be185d,stroke-width:1px,color:#fff;
  classDef field fill:#f1f5f9,stroke:#64748b,stroke-width:1px,color:#334155;
  classDef object fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;
  classDef addin fill:#06b6d4,stroke:#0891b2,stroke-width:1px,color:#fff;
  classDef warning fill:#cbd5e1,stroke:#94a3b8,stroke-width:1px,color:#64748b;
  subgraph Workspace_Layer["Incident Workspace"]
    WS_Incident["Incident"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Incident Details"]:::tab
    Tab_1["Tab: Customer 360"]:::tab
    Tab_2["Tab: Summary"]:::tab
    Tab_3["Tab: Contacts"]:::tab
    SubTab_4["Sub-Tab: Contacts"]:::tab
    SubTab_5["Sub-Tab: Contact Fields"]:::tab
    SubTab_6["Sub-Tab: Incident History"]:::tab
    Tab_7["Tab: Other Info"]:::tab
    Tab_8["Tab: Tasks"]:::tab
    Tab_9["Tab: Attachments"]:::tab
    Tab_10["Tab: Audit Log"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: New Rule (Active)"]:::rule
    Rule_1["Rule: Show Gmoney related product and categories (Active)"]:::rule
  end

  subgraph Fields_Layer["Lookup Fields"]
    Field_2_CId["Field: CId"]:::field
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_0_RichIncidentThread["Related Object: Incident Thread"]:::object
    Obj_4_Contacts["Related Object: Contact"]:::object
    Obj_8_Tasks["Related Object: Task"]:::object
    Obj_9_FileAttachments["Related Object: File Attachment"]:::object
    Obj_10_IncidentAuditLog["Related Object: Audit Log"]:::object
  end

  subgraph Addins_Layer["BUI Extensions"]
    B_636951502718023384["Custom Script: gcb_flex.php"]:::addin
  end

  subgraph Reports_Layer["Target Reports"]
    R_125["Report: 125"]:::report
    R_8014["Report: 8014"]:::report
    R_9011["Report: 9011"]:::report
    R_9029["Report: 9029"]:::report
    R_9018["Report: 9018"]:::report
    R_8010["Report: 8010"]:::report
    R_9041["Report: 9041"]:::report
  end

  WS_Incident --> Tab_0
  WS_Incident --> Tab_1
  WS_Incident --> Tab_2
  WS_Incident --> Tab_3
  WS_Incident --> Tab_7
  WS_Incident --> Tab_8
  WS_Incident --> Tab_9
  WS_Incident --> Tab_10
  Tab_3 --> |"Nested TabSet"| SubTab_4
  Tab_3 --> |"Nested TabSet"| SubTab_5
  Tab_3 --> |"Nested TabSet"| SubTab_6
  WS_Incident --> |"Trig: Editor loads"| Rule_0
  WS_Incident --> |"Trig: Editor loads"| Rule_1
  Rule_0 -.-> |"Hidden"| Tab_1
  Tab_0 --> |"Related Object"| Obj_0_RichIncidentThread
  Tab_1 --> |"Custom Script"| B_636951502718023384
  Tab_2 --> |"Form Field"| Field_2_CId
  SubTab_4 --> |"Related Object"| Obj_4_Contacts
  SubTab_6 --> |"Primary Report (AcId)"| R_9029
  Tab_8 --> |"Related Object"| Obj_8_Tasks
  Tab_9 --> |"Related Object"| Obj_9_FileAttachments
  Tab_10 --> |"Related Object"| Obj_10_IncidentAuditLog
  Obj_0_RichIncidentThread --> |"Secondary Report (SearchId)"| R_125
  Field_2_CId --> |"Lookup Report"| R_8014
  Obj_4_Contacts --> |"Primary Report (AcId)"| R_9011
  Obj_4_Contacts --> |"Secondary Report (SearchId)"| R_8014
  Obj_8_Tasks --> |"Primary Report (AcId)"| R_9018
  Obj_8_Tasks --> |"Secondary Report (SearchId)"| R_8010
  Obj_10_IncidentAuditLog --> |"Primary Report (AcId)"| R_9041
```

---

## Parser Coverage Gaps

The following elements were found in this workspace XML but are not fully parsed by the current accelerator. Raw data is preserved in `master.json` under `unknowns`.

*No parser coverage gaps identified for this workspace.*
