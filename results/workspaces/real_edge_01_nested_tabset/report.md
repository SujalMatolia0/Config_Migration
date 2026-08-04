## System Info

- Platform: **Oracle Service Cloud 26A SP2** (Build 326, June 2026)
- Client Version: `26.2.0.326`
- Workspace Type: **Incident** (single record, not multi-edit)

> [!WARNING] Unhandled Schema Elements Detected in Source Export
> The following 3 raw XML element(s)/attribute(s) were present in the export and captured via fallback handling:
> - Element `<Triggers>`: `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit">                 <Trigger Type="EditorLoaded"/>       `
> - Element `<Triggers>`: `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit">                 <Trigger Type="EditorLoaded"/>       `
> - Attribute `CanUseStandardText`: `True`

---

## Layout Structure

The workspace layout is structured as a root **TabSet** containing 7 tabs.

---

## Layout & Tab Details

Below is the detailed content breakdown of each tab:

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Summary</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(10 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Summary`

> **Multi-Component Tab** — 10 controls across 1 types: 10 Form Fields

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
## Workspace Rules

### Event: Editor Initialized (On Load)

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Hide Customer360 for Email Contacts</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Hide Customer360 for Email Contacts` (Active)
- **Condition:** `Field: Contact.CtypeId == 3` (a specific contact type, likely "Email" or similar)
- **Then:**
  - Standard: Hidden [Element ID: 636632404590473054] → True
  - Show a message box — *"This contact is created through email and may not hold sufficient information in the system"*

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Filter Products for Segment</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Filter Products for Segment` (Active)
- **Condition:** `Profile: Current LIST 7;8;2;6`
- **Then:**
  - Standard: ConfigureMenuItems Incident.ProdId (EQ u0;383)
  - Standard: ConfigureMenuItems Incident.CatId (EQ 384;385;386)

  </div>
</details>

---

## Ribbon / Toolbar

Standard actions: BestAnswer, Copy, Delete, Forward, Info, New, Print, Propose, Refresh, Save, Save & Close, SaveAndSend.

---

## Key Observations

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
  subgraph Workspace_Layer["real_edge_01_nested_tabset Workspace"]
    WS_real_edge_01_nested_tabset["real_edge_01_nested_tabset"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Summary"]:::tab
    Tab_1["Tab: Contacts"]:::tab
    SubTab_2["Sub-Tab: Contacts"]:::tab
    SubTab_3["Sub-Tab: Contact Fields"]:::tab
    SubTab_4["Sub-Tab: Incident History"]:::tab
    Tab_5["Tab: Other Info"]:::tab
    Tab_6["Tab: Incident Details"]:::tab
    Tab_7["Tab: Tasks"]:::tab
    Tab_8["Tab: Attachments"]:::tab
    Tab_9["Tab: Audit Log"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: Hide Customer360 for Email Contacts (Active)"]:::rule
    Rule_1["Rule: Filter Products for Segment (Active)"]:::rule
  end

  subgraph Fields_Layer["Lookup Fields"]
    Field_0_CId["Field: CId"]:::field
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_2_Contacts["Related Object: Contact"]:::object
    Obj_6_RichIncidentThread["Related Object: Incident Thread"]:::object
    Obj_7_Tasks["Related Object: Task"]:::object
    Obj_8_FileAttachments["Related Object: File Attachment"]:::object
    Obj_9_IncidentAuditLog["Related Object: Audit Log"]:::object
  end

  subgraph Reports_Layer["Target Reports"]
    R_8014["Report: 8014"]:::report
    R_9011["Report: 9011"]:::report
    R_9029["Report: 9029"]:::report
    R_125["Report: 125"]:::report
    R_9018["Report: 9018"]:::report
    R_8010["Report: 8010"]:::report
    R_9041["Report: 9041"]:::report
  end

  WS_real_edge_01_nested_tabset --> Tab_0
  WS_real_edge_01_nested_tabset --> Tab_1
  WS_real_edge_01_nested_tabset --> Tab_5
  WS_real_edge_01_nested_tabset --> Tab_6
  WS_real_edge_01_nested_tabset --> Tab_7
  WS_real_edge_01_nested_tabset --> Tab_8
  WS_real_edge_01_nested_tabset --> Tab_9
  Tab_1 --> |"Nested TabSet"| SubTab_2
  Tab_1 --> |"Nested TabSet"| SubTab_3
  Tab_1 --> |"Nested TabSet"| SubTab_4
  WS_real_edge_01_nested_tabset --> |"Trig: Editor loads"| Rule_0
  WS_real_edge_01_nested_tabset --> |"Trig: Editor loads"| Rule_1
  Tab_0 --> |"Form Field"| Field_0_CId
  SubTab_2 --> |"Related Object"| Obj_2_Contacts
  SubTab_4 --> |"Primary Report (AcId)"| R_9029
  Tab_6 --> |"Related Object"| Obj_6_RichIncidentThread
  Tab_7 --> |"Related Object"| Obj_7_Tasks
  Tab_8 --> |"Related Object"| Obj_8_FileAttachments
  Tab_9 --> |"Related Object"| Obj_9_IncidentAuditLog
  Field_0_CId --> |"Lookup Report"| R_8014
  Obj_2_Contacts --> |"Primary Report (AcId)"| R_9011
  Obj_2_Contacts --> |"Secondary Report (SearchId)"| R_8014
  Obj_6_RichIncidentThread --> |"Secondary Report (SearchId)"| R_125
  Obj_7_Tasks --> |"Primary Report (AcId)"| R_9018
  Obj_7_Tasks --> |"Secondary Report (SearchId)"| R_8010
  Obj_9_IncidentAuditLog --> |"Primary Report (AcId)"| R_9041
```

---

## Parser Coverage Gaps

The following elements were found in this workspace XML but are not fully parsed by the current accelerator. Raw data is preserved in `master.json` under `unknowns`.

| Location | Element / Attribute | Raw Value / XML |
|---|---|---|
| Tab: Incident Details RelationshipItem: RichIncidentThread | Attribute: `CanUseStandardText` | `"True"` |
| Rule: Hide Customer360 for Email Contacts | Element: `<Triggers>` | `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit">
                <Trigger Type="EditorLoaded"/>
            </Triggers>` |
| Rule: Filter Products for Segment | Element: `<Triggers>` | `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit">
                <Trigger Type="EditorLoaded"/>
            </Triggers>` |
