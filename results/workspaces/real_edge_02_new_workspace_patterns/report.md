## System Info

- Platform: **Oracle Service Cloud 26A SP2** (Build 326, June 2026)
- Client Version: `26.2.0.326`
- Workspace Type: **Contact** (single record, not multi-edit)

---

## Layout Structure

The workspace layout is structured as a root **TabSet** containing 5 tabs.

---

## Layout & Tab Details

Below is the detailed content breakdown of each tab:

### Tab: Summary

> **Multi-Component Tab** — 7 controls across 2 types: 6 Form Fields, 1 Menu

**1. Form Fields & Menus**

| Position (Row, Col) | Field / Control | Details |
|---|---|---|
| Row 0, Col 0 | `C$AccountNumber` | Custom field — account number |
| Row 1, Col 0 | `PhOffice` | Office phone |
| Row 2, Col 0 | `Menu (639203177532626906)` | Dropdown options: **Menu Item #1**, **Menu Item #2**, **Menu Item #3**, **Anurag**, **Monish** |
| Row 3, Col 0 | `OrgId` | Account (Lookup → Report **8001**) |
| Row 4, Col 0 | `Addr` | Address |
| Row 5, Col 0 | `C$Gender` | Custom field — gender |
| Row 6, Col 0 | `Email` | Email address |


### Tab: New Tab 1

> **Single Component Tab**

- **Control Type:** Embedded Browser
  - **Target URL:** *(Unconfigured / No URL)*


### Tab: New Tab 2

> **Single Component Tab**

- **Control Type:** Direct Report
  - **Behavior:** Skips execution on unsaved new records


### Tab: New Tab 3

> **Single Component Tab**

- **Control Type:** Related Object (`Task`)
  - **Primary Report (AcId):** `9016`
  - **Secondary Report (SearchId):** `8012`
  - **Behavior:** Skips execution on unsaved new records


### Tab: New Tab 4

> **Single Component Tab**

- **Control Type:** Related Object (`File Attachment`)


---
## Workspace Rules

### Event: Editor Initialized (On Load)

#### Rule: New Rule (Inactive)
- **Condition:** `Field: Contact.CtypeId == 3` (a specific contact type, likely "Email" or similar)
- **Then:**
  - Show a message box — *"This contact is created through email and may not hold sufficient information in the system"*

---

## Ribbon / Toolbar

Standard actions: Save, Save & Close, New, Refresh, Appointment, Print, Copy, Delete, Reset Password, Spell Check, Info.

**Embedded Links:**
- [Oracle Service Cloud](http://cloud.oracle.com/service)

---

## Key Observations

- The inactive rule suggests there was a workflow for email-originated contacts that's either been deprecated or temporarily disabled.
- Layout tabset has **`CanReorderTabs="True"`** enabled, which allows agents to dynamically rearrange workspace tabs at runtime.

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
  subgraph Workspace_Layer["real_edge_02_new_workspace_patterns Workspace"]
    WS_real_edge_02_new_workspace_patterns["real_edge_02_new_workspace_patterns"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Summary"]:::tab
    Tab_1["Tab: New Tab 1"]:::tab
    Tab_2["Tab: New Tab 2"]:::tab
    Tab_3["Tab: New Tab 3"]:::tab
    Tab_4["Tab: New Tab 4"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: New Rule (Inactive)"]:::rule
  end

  subgraph Fields_Layer["Lookup Fields"]
    Field_0_OrgId["Field: OrgId"]:::field
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_3_Tasks["Related Object: Task"]:::object
    Obj_4_FileAttachments["Related Object: File Attachment"]:::object
  end

  subgraph Reports_Layer["Target Reports"]
    R_8001["Report: 8001"]:::report
    R_9016["Report: 9016"]:::report
    R_8012["Report: 8012"]:::report
  end

  subgraph Warnings_Layer["Unconfigured / Warnings"]
    B_browser_1_0["No URL Configured"]:::warning
    R_0_2["No Report Configured"]:::warning
  end

  WS_real_edge_02_new_workspace_patterns --> Tab_0
  WS_real_edge_02_new_workspace_patterns --> Tab_1
  WS_real_edge_02_new_workspace_patterns --> Tab_2
  WS_real_edge_02_new_workspace_patterns --> Tab_3
  WS_real_edge_02_new_workspace_patterns --> Tab_4
  WS_real_edge_02_new_workspace_patterns --> |"Trig: Editor loads"| Rule_0
  Tab_0 --> |"Form Field"| Field_0_OrgId
  Tab_1 --> |"Browser"| B_browser_1_0
  Tab_2 --> R_0_2
  Tab_3 --> |"Related Object"| Obj_3_Tasks
  Tab_4 --> |"Related Object"| Obj_4_FileAttachments
  Field_0_OrgId --> |"Lookup Report"| R_8001
  Obj_3_Tasks --> |"Primary Report (AcId)"| R_9016
  Obj_3_Tasks --> |"Secondary Report (SearchId)"| R_8012
```
