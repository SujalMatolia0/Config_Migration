## System Info

- Platform: **Oracle Service Cloud 26A SP2** (Build 326, June 2026)
- Client Version: `26.2.0.326`
- Workspace Type: **Contact** (single record, not multi-edit)

---

## Layout Structure

The workspace has a **5-column table layout** (11 rows × 5 columns):

**Left column** — Form fields:

| Field | Notes |
|---|---|
| `Title` | Salutation/title |
| `Name.First` | First name |
| `Name.Last` | Last name |
| `Addr` | Address |
| `PhOffice` | Relabeled as **"Mobile Phone"**, default type 1 |
| `C$CustomerId` | Custom field — customer id |
| `Email` | Email address |
| `CtypeId` | Contact type |
| `C$Gender` | Custom field — gender |

---

## Layout & Tab Details

Below is the detailed content breakdown of each tab:

### Tab: Incidents

> **Single Component Tab**

- **Control Type:** Related Object (`Incident`)
  - **Primary Report (AcId):** `9029`
  - **Behavior:** Skips execution on unsaved new records


### Tab: Customer360

> **Single Component Tab**

- **Control Type:** Embedded Browser
  - **Target URL:** `https://gcb.custhelp.com/cgi-bin/gcb.cfg/php/custom/gcb_flex.php?mobile=$contact.phmobile`


### Tab: Attachments

> **Single Component Tab**

- **Control Type:** Related Object (`File Attachment`)


### Tab: Notes

> **Single Component Tab**

- **Control Type:** Related Object (`Note`)


### Tab: Audit

> **Single Component Tab**

- **Control Type:** Related Object (`Audit Log`)
  - **Primary Report (AcId):** `9050`
  - **Behavior:** Skips execution on unsaved new records


---
## Workspace Rules

### Event: Editor Initialized (On Load)

#### Rule: New Rule (Inactive)
- **Condition:** `Field: Contact.CtypeId == 3` (a specific contact type, likely "Email" or similar)
- **Then:**
  - Show a message box — *"This contact is created through email and may not hold sufficient information in the system"*

---

## Ribbon / Toolbar

Standard actions: Save, Save & Close, New, Refresh, Appointment, Print, Copy, Delete, Spell Check, Info.

---

## Key Observations

- The `PhOffice` field is **mislabeled as "Mobile Phone"** — that's either intentional repurposing or a bug worth flagging.
- The **Customer360** tab embeds an internal **custom PHP script**: `gcb_flex.php` (`/cgi-bin/gcb.cfg/php/custom/gcb_flex.php`) — passes URL params: `mobile`. Errors are suppressed.
- `C$` prefix fields are **custom fields** added on top of the standard schema.
- The inactive rule suggests there was a workflow for email-originated contacts that's either been deprecated or temporarily disabled.

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
  subgraph Workspace_Layer["real_edge_03_split_panel_contact Workspace"]
    WS_real_edge_03_split_panel_contact["real_edge_03_split_panel_contact"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Incidents"]:::tab
    Tab_1["Tab: Customer360"]:::tab
    Tab_2["Tab: Attachments"]:::tab
    Tab_3["Tab: Notes"]:::tab
    Tab_4["Tab: Audit"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: New Rule (Inactive)"]:::rule
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_0_IncidentView["Related Object: Incident"]:::object
    Obj_2_FileAttachments["Related Object: File Attachment"]:::object
    Obj_3_ContactNotes["Related Object: Note"]:::object
    Obj_4_ContactAuditLog["Related Object: Audit Log"]:::object
  end

  subgraph Addins_Layer["BUI Extensions"]
    B_636908689046358732["Custom Script: gcb_flex.php"]:::addin
  end

  subgraph Reports_Layer["Target Reports"]
    R_9029["Report: 9029"]:::report
    R_9050["Report: 9050"]:::report
  end

  WS_real_edge_03_split_panel_contact --> Tab_0
  WS_real_edge_03_split_panel_contact --> Tab_1
  WS_real_edge_03_split_panel_contact --> Tab_2
  WS_real_edge_03_split_panel_contact --> Tab_3
  WS_real_edge_03_split_panel_contact --> Tab_4
  WS_real_edge_03_split_panel_contact --> |"Trig: Editor loads"| Rule_0
  Tab_0 --> |"Related Object"| Obj_0_IncidentView
  Tab_1 --> |"Custom Script"| B_636908689046358732
  Tab_2 --> |"Related Object"| Obj_2_FileAttachments
  Tab_3 --> |"Related Object"| Obj_3_ContactNotes
  Tab_4 --> |"Related Object"| Obj_4_ContactAuditLog
  Obj_0_IncidentView --> |"Primary Report (AcId)"| R_9029
  Obj_4_ContactAuditLog --> |"Primary Report (AcId)"| R_9050
```
