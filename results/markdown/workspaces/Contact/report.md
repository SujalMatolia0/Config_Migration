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

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Contact Report Summary</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Contact Report Summary`

> **Single Component Tab**

- **Control Type:** Related Object (`Incident`)
  - **Primary Report (AcId):** `100008`
  - **Secondary Report (SearchId):** `100008`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Incidents</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Incidents`

> **Single Component Tab**

- **Control Type:** Related Object (`Incident`)
  - **Primary Report (AcId):** `9029`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Address Validation</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Address Validation`

> **Single Component Tab**

- **Control Type:** Embedded Browser
  - **Target URL:** `https://gcb.custhelp.com/cgi-bin/gcb.cfg/php/custom/address_validation.php`

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Contact Org Lookup Extension</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Contact Org Lookup Extension`

> **Single Component Tab**

- **Control Type:** BUI Extension (`ContactOrgLookupBUIAddin`)
  - **File ID:** `7`

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Customer360</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Customer360`

> **Single Component Tab**

- **Control Type:** Embedded Browser
  - **Target URL:** `https://gcb.custhelp.com/cgi-bin/gcb.cfg/php/custom/gcb_flex.php?mobile=$contact.phmobile`

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
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Notes</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Notes`

> **Single Component Tab**

- **Control Type:** Related Object (`Note`)

  </div>
</details>


<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;">Tab: <b>Audit</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(1 Controls)</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

### Tab: `Audit`

> **Single Component Tab**

- **Control Type:** Related Object (`Audit Log`)
  - **Primary Report (AcId):** `9050`
  - **Behavior:** Skips execution on unsaved new records

  </div>
</details>


---

## Workspace Fields Inventory

Total Fields Used in Workspace: **9** (Standard Schema Fields: **7** | Custom Fields (`c$`): **2**)

| Field ID / Reference | Field Label | Field Type | Location / Tab | Options & Constraints |
|---|---|---|---|---|
| `Title` | — | Standard Schema | Top-level Layout | — |
| `Name.First` | — | Standard Schema | Top-level Layout | — |
| `Name.Last` | — | Standard Schema | Top-level Layout | — |
| `Addr` | — | Standard Schema | Top-level Layout | — |
| `PhOffice` | &Mobile Phone | Standard Schema | Top-level Layout | Default: `1` |
| `C$CustomerId` | — | Custom (`c$`) | Top-level Layout | — |
| `Email` | — | Standard Schema | Top-level Layout | — |
| `CtypeId` | — | Standard Schema | Top-level Layout | — |
| `C$Gender` | — | Custom (`c$`) | Top-level Layout | — |

---
## Workspace Rules

### Event: Editor Initialized (On Load)

<details style="border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 16px; padding: 12px 16px;">
  <summary style="font-weight: 600; font-size: 15px; cursor: pointer;"><span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; border: 1px solid #10b981; color: #10b981; margin-right: 8px;">Active</span>Rule: <b>Check Contact Duplicates</b> <span style="font-size: 13px; font-weight: 400; opacity: 0.8; margin-left: 6px;">(Event: Editor Initialized (On Load))</span></summary>
  <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(148, 163, 184, 0.25);">

#### Rule: `Check Contact Duplicates` (Active)
- **Condition:** `Field: Contact.CtypeId == 3` (a specific contact type, likely "Email" or similar)
- **Then:**
  - RunScript:   (duplicate_contacts.php)

  </div>
</details>

---

## Ribbon / Toolbar

Standard actions: Appointment, Copy, Delete, Info, New, Print, Refresh, Save, Save & Close, Spell Check.

---

## Key Observations

- The `PhOffice` field is **mislabeled as "Mobile Phone"** — that's either intentional repurposing or a bug worth flagging.
- The **Address Validation** tab embeds an internal **custom PHP script**: `address_validation.php` (`/cgi-bin/gcb.cfg/php/custom/address_validation.php`). Errors are suppressed.
- The **Customer360** tab embeds an internal **custom PHP script**: `gcb_flex.php` (`/cgi-bin/gcb.cfg/php/custom/gcb_flex.php`) — passes URL params: `mobile`. Errors are suppressed.
- `C$` prefix fields are **custom fields** added on top of the standard schema.
- The workspace defines **1 active business rules** triggered by editor loading events, enforcing profile-based field locking and toolbar UI visibility.
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
  subgraph Workspace_Layer["Contact Workspace"]
    WS_Contact["Contact"]:::workspace
  end

  subgraph Tabs_Layer["Workspace Tabs"]
    Tab_0["Tab: Contact Report Summary"]:::tab
    Tab_1["Tab: Incidents"]:::tab
    Tab_2["Tab: Address Validation"]:::tab
    Tab_3["Tab: Contact Org Lookup Extension"]:::tab
    Tab_4["Tab: Customer360"]:::tab
    Tab_5["Tab: Attachments"]:::tab
    Tab_6["Tab: Notes"]:::tab
    Tab_7["Tab: Audit"]:::tab
  end

  subgraph Rules_Layer["Business Rules"]
    Rule_0["Rule: Check Contact Duplicates (Active)"]:::rule
  end

  subgraph Objects_Layer["Related Objects"]
    Obj_0_IncidentView["Related Object: Incident"]:::object
    Obj_1_IncidentView["Related Object: Incident"]:::object
    Obj_5_FileAttachments["Related Object: File Attachment"]:::object
    Obj_6_ContactNotes["Related Object: Note"]:::object
    Obj_7_ContactAuditLog["Related Object: Audit Log"]:::object
  end

  subgraph Addins_Layer["BUI Extensions"]
    B_636908689046358799["Custom Script: address_validation.php"]:::addin
    AddIn_3_0["Add-In: ContactOrgLookupBUIAddin"]:::addin
    B_636908689046358732["Custom Script: gcb_flex.php"]:::addin
  end

  subgraph Reports_Layer["Target Reports"]
    R_100008["Report: 100008"]:::report
    R_9029["Report: 9029"]:::report
    R_9050["Report: 9050"]:::report
  end

  WS_Contact --> Tab_0
  WS_Contact --> Tab_1
  WS_Contact --> Tab_2
  WS_Contact --> Tab_3
  WS_Contact --> Tab_4
  WS_Contact --> Tab_5
  WS_Contact --> Tab_6
  WS_Contact --> Tab_7
  WS_Contact --> |"Trig: Editor loads"| Rule_0
  Tab_0 --> |"Related Object"| Obj_0_IncidentView
  Tab_1 --> |"Related Object"| Obj_1_IncidentView
  Tab_2 --> |"Custom Script"| B_636908689046358799
  Tab_3 --> |"Add-In Plugin"| AddIn_3_0
  Tab_4 --> |"Custom Script"| B_636908689046358732
  Tab_5 --> |"Related Object"| Obj_5_FileAttachments
  Tab_6 --> |"Related Object"| Obj_6_ContactNotes
  Tab_7 --> |"Related Object"| Obj_7_ContactAuditLog
  Obj_0_IncidentView --> |"Primary Report (AcId)"| R_100008
  Obj_0_IncidentView --> |"Secondary Report (SearchId)"| R_100008
  Obj_1_IncidentView --> |"Primary Report (AcId)"| R_9029
  Obj_7_ContactAuditLog --> |"Primary Report (AcId)"| R_9050
```

---

## Parser Coverage Gaps

The following elements were found in this workspace XML but are not fully parsed by the current accelerator. Raw data is preserved in `master.json` under `unknowns`.

*No parser coverage gaps identified for this workspace.*
