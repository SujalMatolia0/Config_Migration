## System Info

- Platform: **Oracle Service Cloud 26A SP2** (Build 326, June 2026)
- Client Version: `26.2.0.326`
- Workspace Type: **Contact** (single record, not multi-edit)

> [!WARNING] Unhandled Schema Elements Detected in Source Export
> The following 10 raw XML element(s)/attribute(s) were present in the export and captured via fallback handling:
> - Element `<Triggers>`: `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>`
> - Element `<Triggers>`: `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>`
> - Element `<Triggers>`: `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>`
> - Attribute `LayoutLabelAlignment`: `Right`
> - Attribute `LayoutLabelPosition`: `Left`
> - Attribute `ReadOnlyOption`: `OnNew:~any~;OnEdit:~any~`
> - Attribute `DisableEmailIcon`: `True`
> - Attribute `HideReportCommands`: `True`
> - Attribute `Anchor`: `Top, Left`
> - Attribute `AutoSize`: `False`

---

## Layout Structure

The workspace layout is structured as a root **TabSet** containing 6 tabs.

---

## Layout & Tab Details

Below is the detailed content breakdown of each tab:

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Summary</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(8 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Summary`

> **Multi-Component Tab** — 8 controls across 2 types: 7 Form Fields, 1 Related Object/Report

**1. Form Fields & Menus**

| Position (Row, Col) | Field / Control | Details |
|---|---|---|
| Row 0, Col 0 | `Name.First` | First name — *ReadOnly: OnNew (All Profiles), OnEdit (All Profiles)* |
| Row 0, Col 1 | `Name.Last` | Last name — *ReadOnly: OnNew (All Profiles), OnEdit (All Profiles)* |
| Row 1, Col 0 | `Email` | Email address — *ReadOnly: OnNew (All Profiles), OnEdit (All Profiles)* |
| Row 1, Col 1 | `OrgId` | Account (Lookup → Report **8001**) |
| Row 2, Col 0 | `C$IsRegistered` | Custom field — is registered — *ReadOnly: OnNew (27 profiles), OnEdit (27 profiles)* |
| Row 3, Col 0 | `Disabled` | Form field — *ReadOnly: OnNew (29 profiles), OnEdit (29 profiles); Hidden: OnNew (29 profiles), OnEdit (29 profiles)* |
| Row 3, Col 1 | `CId` | Form field |

**2. Related Objects & Direct Reports**

| Position (Row, Col) | Type | Object / Report | Report IDs | Behavior / Config |
|---|---|---|---|---|
| Row 2, Col 1 | Related Object | `SLA Container` | Primary: **—** | Runs on all records |

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Incidents</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Incidents`

> **Single Component Tab**

- **Control Type:** Related Object (`Incident`)
  - **Primary Report (AcId):** `100038`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Accounts</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Accounts`

> **Single Component Tab**

- **Control Type:** Direct Report
  - **Primary Report (AcId):** `100015`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Surveys</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Surveys`

> **Single Component Tab**

- **Control Type:** Related Object (`Survey History`)
  - **Primary Report (AcId):** `10012`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Audit Log</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Audit Log`

> **Single Component Tab**

- **Control Type:** Related Object (`Audit Log`)
  - **Primary Report (AcId):** `9050`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>New Tab 1</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `New Tab 1`

> **Single Component Tab**

- **Control Type:** BUI Extension (`ContactOrgLookupBUIAddin`)
  - **File ID:** `7`

  </div>
</details>


---

## Workspace Fields Inventory

Total Fields Used in Workspace: **7** (Standard Schema Fields: **6** | Custom Fields (`c$`): **1**)

| Field ID / Reference | Field Label | Field Type | Location / Tab | Options & Constraints |
|---|---|---|---|---|
| `Name.First` | — | Standard Schema | Tab: Summary | ReadOnly: OnNew (All Profiles), OnEdit (All Profiles) |
| `Name.Last` | — | Standard Schema | Tab: Summary | ReadOnly: OnNew (All Profiles), OnEdit (All Profiles) |
| `Email` | — | Standard Schema | Tab: Summary | ReadOnly: OnNew (All Profiles), OnEdit (All Profiles) |
| `OrgId` | &Account | Standard Schema | Tab: Summary | — |
| `C$IsRegistered` | — | Custom (`c$`) | Tab: Summary | ReadOnly: OnNew (27 profiles), OnEdit (27 profiles) |
| `Disabled` | — | Standard Schema | Tab: Summary | ReadOnly: OnNew (29 profiles), OnEdit (29 profiles); Hidden: OnNew (29 profiles), OnEdit (29 profiles) |
| `CId` | — | Standard Schema | Tab: Summary | — |

---
## Workspace Rules

### Event: Editor Initialized (On Load)

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Admin Fields</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Admin Fields` (Active)
- **Condition:** `Profile: Current LIST 11;14;2`
- **Then:**
  - Standard: ReadOnly Contact.Name.First (False)
  - Standard: ReadOnly Contact.Name.Last (False)
  - Standard: ReadOnly Contact.Email (False)
  - Standard: ReadOnly Contact.OrgId (False)
  - Standard: Required Contact.Name.First (True)
  - Standard: Required Contact.Name.Last (True)

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Admin Fields - Support Supervisors</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Admin Fields - Support Supervisors` (Active)
- **Condition:** `Profile: Current LIST 33;7;15;37;16;44`
- **Then:**
  - Standard: ReadOnly Contact.Name.First (False)
  - Standard: ReadOnly Contact.Name.Last (False)
  - Standard: ReadOnly Contact.Email (False)
  - Standard: Required Contact.Name.First (True)
  - Standard: Required Contact.Name.Last (True)
  - Standard: Hidden RibbonButton[Delete] → True

  </div>
</details>

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Hide Delete and New button</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Hide Delete and New button` (Active)
- **Condition:** `Profile: Current LIST 11;14;2`
- **Then:**
  - Standard: Hidden RibbonButton[Delete] → True
  - Standard: Hidden RibbonButton[New] → True

  </div>
</details>

---

## Ribbon / Toolbar

Standard actions: Delete, Info, New, Print, Refresh, Save, Save & Close, Spell Check.

**Embedded Links:**
- [Oracle Service Cloud](http://cloud.oracle.com/service)

---

## Key Observations

- The workspace defines **3 active business rules** triggered by editor loading events, enforcing profile-based field locking and toolbar UI visibility.
- The **workspace flag indicator** is explicitly hidden (`Visible="False"`), suppressing visual cues for users/agents.
- Layout tabset has **`CanReorderTabs="True"`** enabled, which allows agents to dynamically rearrange workspace tabs at runtime.
- The workspace includes an **external BUI Extension plugin dependency**: `ContactOrgLookupBUIAddin` (FileId: `7`).

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
  subgraph Workspace_Layer["Contact test Workspace"]
    WS_Contact_test["Contact test"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Summary"]:::tab
    Tab_1["Tab: Incidents"]:::tab
    Tab_2["Tab: Accounts"]:::tab
    Tab_3["Tab: Surveys"]:::tab
    Tab_4["Tab: Audit Log"]:::tab
    Tab_5["Tab: New Tab 1"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: Admin Fields (Active)"]:::rule
    Rule_1["Rule: Admin Fields - Support Supervisors (Active)"]:::rule
    Rule_2["Rule: Hide Delete and New button (Active)"]:::rule
  end

  subgraph Fields_Layer["Lookup Fields"]
    Field_0_OrgId["Field: OrgId"]:::field
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_0_SlaContainer["Related Object: SLA Container"]:::object
    Obj_1_IncidentView["Related Object: Incident"]:::object
    Obj_3_SurveyHistoryView["Related Object: Survey History"]:::object
    Obj_4_ContactAuditLog["Related Object: Audit Log"]:::object
  end

  subgraph Addins_Layer["BUI Extensions"]
    AddIn_5_0["Add-In: ContactOrgLookupBUIAddin"]:::addin
  end

  subgraph Reports_Layer["Target Reports"]
    R_8001["Report: 8001"]:::report
    R_100038["Report: 100038"]:::report
    R_100015["Report: 100015"]:::report
    R_10012["Report: 10012"]:::report
    R_9050["Report: 9050"]:::report
  end

  WS_Contact_test --> Tab_0
  WS_Contact_test --> Tab_1
  WS_Contact_test --> Tab_2
  WS_Contact_test --> Tab_3
  WS_Contact_test --> Tab_4
  WS_Contact_test --> Tab_5
  WS_Contact_test --> |"Trig: Editor loads"| Rule_0
  WS_Contact_test --> |"Trig: Editor loads"| Rule_1
  WS_Contact_test --> |"Trig: Editor loads"| Rule_2
  Tab_0 --> |"Form Field"| Field_0_OrgId
  Tab_0 --> |"Related Object"| Obj_0_SlaContainer
  Tab_1 --> |"Related Object"| Obj_1_IncidentView
  Tab_2 --> |"Primary Report (AcId)"| R_100015
  Tab_3 --> |"Related Object"| Obj_3_SurveyHistoryView
  Tab_4 --> |"Related Object"| Obj_4_ContactAuditLog
  Tab_5 --> |"Add-In Plugin"| AddIn_5_0
  Field_0_OrgId --> |"Lookup Report"| R_8001
  Obj_1_IncidentView --> |"Primary Report (AcId)"| R_100038
  Obj_3_SurveyHistoryView --> |"Primary Report (AcId)"| R_10012
  Obj_4_ContactAuditLog --> |"Primary Report (AcId)"| R_9050
```

---

## Parser Coverage Gaps

The following elements were found in this workspace XML but are not fully parsed by the current accelerator. Raw data is preserved in `master.json` under `unknowns`.

| Location | Element / Attribute | Raw Value / XML |
|---|---|---|
| Tab: SUMMARY_LBL RelationshipItem: SlaContainer | Attribute: `LayoutLabelAlignment` | `Right` |
| Tab: SUMMARY_LBL RelationshipItem: SlaContainer | Attribute: `LayoutLabelPosition` | `Left` |
| Tab: SUMMARY_LBL RelationshipItem: SlaContainer | Attribute: `ReadOnlyOption` | `OnNew:~any~;OnEdit:~any~` |
| Tab: SUMMARY_LBL Field: Email | Attribute: `DisableEmailIcon` | `True` |
| Tab: Surveys RelationshipItem: SurveyHistoryView | Attribute: `HideReportCommands` | `True` |
| Tab: New Tab 1 AddIn: ContactOrgLookupBUIAddin | Attribute: `Anchor` | `Top, Left` |
| Tab: New Tab 1 AddIn: ContactOrgLookupBUIAddin | Attribute: `AutoSize` | `False` |
| Rule: Admin Fields | Element: `<Triggers>` | `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>` |
| Rule: Admin Fields - Support Supervisors | Element: `<Triggers>` | `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>` |
| Rule: Hide Delete and New button | Element: `<Triggers>` | `<Triggers xmlns:dbaudit="http://www.rightnow.com/schemas/dbaudit"><Trigger Type="EditorLoaded"/></Triggers>` |
