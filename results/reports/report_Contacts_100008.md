# Report: Contacts (ID: 100008)

- Type: **Grid Report** (ac_type=1, public)
- Primary Table: `contacts`
- Created: `2015-12-08T22:59:56Z` | Last Updated: `2016-02-26T04:18:42Z`
- Folder ID: `100692` | Owner Account ID: 4 `[unresolved account ID]` | Interface ID: `1` | Image Icon: `6`
- Nodes (1): `Node #1 (style_id=12, row_limit=None)`
- Display Layout: `ShowDataAreaAsGrid` | Hidden Sections: `Charts`, `Exceptions`, `ReportFooter`, `ReportHeader`, `SearchCriteria`
- Options & Aux: `opts=4 `[unresolved bitmask]``, `time_zone=0` | `aux=1.0.2,1.31.2,1.0.43,1.0.3,1.32.3`
- Export Signature: `Version: 26.2.0.326 | 2.JJfk3KZO5EXP+QKvd7LS0RNgyb/cDHjJTmcYJKAF+zBkAjT1`
- Sort: `contacts.updated — Descending (primary)`
- Filters: None configured (empty `<filters/>` in source XML)

---

### Columns (13)

| # | Source Field | Table | Label | Data Type | Column Attrs | Sort |
|---|---|---|---|---|---|---|
| 1 | `contacts.c_id` | `contacts` | Contact ID | Integer/ID (3) | Standard (1) | — |
| 2 | `contacts.created` | `contacts` | Created Date | DateTime (4) | Standard (1) | — |
| 3 | `contacts.updated` | `contacts` | Updated Date | DateTime (4) | Standard (1) | Sort #1 ↓ (primary) |
| 4 | `contacts.first_name` | `contacts` | First Name | String (5) | Standard (1) | — |
| 5 | `contacts.last_name` | `contacts` | Last Name | String (5) | Standard (1) | — |
| 6 | `contacts.login` | `contacts` | Login | String (5) | Masked/Login (32769) | — |
| 7 | `contacts.email` | `contacts` | Email Address | String (5) | Standard (1) | — |
| 8 | `contacts.c$is_internal` | `contacts` | IsInternal | Integer (1) | Custom Extended Field (131081) | — |
| 9 | `contacts.c$is_manual` | `contacts` | IsManual | Integer (1) | Custom Extended Field (131081) | — |
| 10 | `sla_instances.sla_set` | `sla_instances` | SLA Set | Integer/ID (3) | Standard (1) | — |
| 11 | `contacts.c$org_id_temp` | `contacts` | Org ID Temp | Integer/ID (3) | Custom/System Field (9) | — |
| 12 | `contacts.org_id` | `contacts` | Organization ID | Integer/ID (3) | Standard (1) | — |
| 13 | `sss_users.display_name` | `sss_users` | Display Name | String (5) | Standard (1) | — |

*Column sequence is ordered by `display_order` from XML.*

> **Attribute Footnote**: `Masked/Login (32769)` indicates column value represents user credential or login identity (partially masked/hashed in UI). `Custom/System Field (9)` indicates custom field or primary system identifier.

> **Column Validation Note**: All 13 columns verified against internal table references (`val_col_refs`).

---

### Table Joins (3)

| Table | Alias | Join Type | Join Def Index | Join Condition |
|---|---|---|---|---|
| `contacts (tbl 2)` | `contacts` | Primary | `—` | `—` |
| `sla_instances (tbl 43)` | `sla_instances` | LEFT OUTER JOIN | `15` | `contacts.c_id = sla_instances.owner_id` |
| `sss_users (tbl 623)` | `sss_users` | LEFT OUTER JOIN | `69` | `contacts.common_user_id = sss_users.common_user_id` |

---

### Permissions (27 profiles)

- **Read + Write:** profiles `2`, `4`, `7`, `8`, `9`, `10`, `11`, `14`, `15`, `16`, `27`, `28`, `30`, `31`, `32`, `33`, `34`, `35`, `37`, `39`, `40`, `41`, `42`, `43`, `44`
- **Read Only:** profiles `22`, `36`

---

## Flow Diagram

```mermaid
graph LR
  classDef report fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
  classDef table fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;
  classDef field fill:#f1f5f9,stroke:#64748b,stroke-width:1px,color:#334155;
  classDef perm fill:#e0f2fe,stroke:#0284c7,stroke-width:1px,color:#0369a1;
  classDef warning fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;

  subgraph Report_Layer["Report Definition"]
    R_100008["Report: Contacts (100008)"]:::report
  end

  subgraph Tables_Layer["Queried Tables"]
    T_contacts["Table: contacts (Primary)"]:::table
    T_sla_instances["Table: sla_instances (LEFT OUTER JOIN, idx=15)"]:::table
    T_sss_users["Table: sss_users (LEFT OUTER JOIN, idx=69)"]:::table
  end

  subgraph Fields_Layer["Report Columns"]
    F_1_contactsc_id["Contact ID (contacts.c_id)"]:::field
    F_2_contactscreated["Created Date (contacts.created)"]:::field
    F_3_contactsupdated["Updated Date (contacts.updated)"]:::field
    F_4_contactsfirst_name["First Name (contacts.first_name)"]:::field
    F_5_contactslast_name["Last Name (contacts.last_name)"]:::field
    F_6_contactslogin["Login (contacts.login) [Masked/Login (32769)]"]:::field
    F_7_contactsemail["Email Address (contacts.email)"]:::field
    F_8_contactscis_internal["IsInternal (contacts.c$is_internal) [Custom Extended Field (131081)]"]:::field
    F_9_contactscis_manual["IsManual (contacts.c$is_manual) [Custom Extended Field (131081)]"]:::field
    F_10_sla_instancessla_set["SLA Set (sla_instances.sla_set)"]:::field
    F_11_contactscorg_id_temp["Org ID Temp (contacts.c$org_id_temp) [Custom/System Field (9)]"]:::field
    F_12_contactsorg_id["Organization ID (contacts.org_id)"]:::field
    F_13_sss_usersdisplay_name["Display Name (sss_users.display_name)"]:::field
  end

  subgraph Perms_Layer["Access Permissions"]
    P_0["Read + Write (25 profiles)"]:::perm
    P_1["Read Only (2 profiles)"]:::perm
  end

  R_100008 --> T_contacts
  R_100008 --> T_sla_instances
  R_100008 --> T_sss_users
  T_contacts --> F_1_contactsc_id
  T_contacts --> F_2_contactscreated
  T_contacts --> F_3_contactsupdated
  T_contacts --> F_4_contactsfirst_name
  T_contacts --> F_5_contactslast_name
  T_contacts --> F_6_contactslogin
  T_contacts --> F_7_contactsemail
  T_contacts --> F_8_contactscis_internal
  T_contacts --> F_9_contactscis_manual
  T_sla_instances --> F_10_sla_instancessla_set
  T_contacts --> F_11_contactscorg_id_temp
  T_contacts --> F_12_contactsorg_id
  T_sss_users --> F_13_sss_usersdisplay_name
  R_100008 -.-> P_0
  R_100008 -.-> P_1
```
