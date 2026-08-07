# OSVC Configuration Master Index

**Generated**: 2026-08-07 13:48:18  
**Primary System Mapping**: [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md)  

> [!NOTE]
> **Master Index Overview**: Central navigation matrix linking all analyzed Oracle Service Cloud Workspaces, Analytics Reports, CPM Handlers, BUI Add-Ins, Custom PHP Scripts, and Dependency Graphs.

## Objects

| Primary OSVC Object | Bound Workspaces | Event Handlers (CPM) | Analytics Reports | Custom Fields (c$) | Master Mapping |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Contact** | 2 | 3 | 5 | 8 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-contact-29-mapped-components) |
| **Incident** | 2 | 2 | 4 | 5 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-incident-16-mapped-components) |
| **Organization** | 1 | 0 | 2 | 3 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-organization-6-mapped-components) |
| **Test_Record** | 1 | 0 | 1 | 0 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-test_record-3-mapped-components) |
| **General / Shared** | 1 | 1 | 2 | 0 | [COMPLETE_SYSTEM_MAPPING.md](COMPLETE_SYSTEM_MAPPING.md#entity-module-general--unassigned-12-mapped-components) |

## Workspaces

### Standard Object Workspaces

| Workspace Name | Primary Object | Tabs | Fields | Rules | Unknowns | Referenced Reports | Documentation |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **Contact** | `Contact` | 7 | 9 | 1 | 0 | `100008`, `9029`, `9050` | [report.md](workspaces/Contact/report.md) |
| **Incident** | `Incident` | 8 | 0 | 2 | 0 | `125`, `8010`, `8014`, `9011`, `9018`, `9029`, `9041` | [report.md](workspaces/Incident/report.md) |

### Custom & Edge Layout Workspaces

| Workspace Name | Primary Object | Tabs | Fields | Rules | Unknowns | Referenced Reports | Documentation |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **Contact test** | `Contact` | 6 | 0 | 3 | 0 | `100015`, `100038`, `10012`, `8001`, `9050` | [report.md](workspaces/Contact_test/report.md) |
| **New Workspace** | `General` | 5 | 0 | 0 | 0 | `8001`, `8012`, `9016` | [report.md](workspaces/New_Workspace/report.md) |
| **real_edge_01_nested_tabset** | `General` | 7 | 0 | 2 | 0 | `125`, `8010`, `8014`, `9011`, `9018`, `9029`, `9041` | [report.md](workspaces/real_edge_01_nested_tabset/report.md) |
| **real_edge_02_new_workspace_patterns** | `General` | 5 | 0 | 1 | 0 | `8001`, `8012`, `9016` | [report.md](workspaces/real_edge_02_new_workspace_patterns/report.md) |
| **real_edge_03_split_panel_contact** | `Contact` | 5 | 9 | 1 | 0 | `9029`, `9050` | [report.md](workspaces/real_edge_03_split_panel_contact/report.md) |

## Reports

### Standard Analytics Reports

| Report ID | Report Name | Primary Table / Schema | Columns | Referenced In Workspaces | Documentation |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `100015` | **Analytics Report 100015** | `Referenced Schema` | — | **Contact test** | — |
| `100038` | **Analytics Report 100038** | `Referenced Schema` | — | **Contact test** | — |
| `10012` | **Analytics Report 10012** | `Referenced Schema` | — | **Contact test** | — |
| `125` | **Analytics Report 125** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `8001` | **Analytics Report 8001** | `Referenced Schema` | — | **Contact test**, **New Workspace**, **real_edge_02_new_workspace_patterns** | — |
| `8010` | **Analytics Report 8010** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `8012` | **Analytics Report 8012** | `Referenced Schema` | — | **New Workspace**, **real_edge_02_new_workspace_patterns** | — |
| `8014` | **Analytics Report 8014** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `9011` | **Analytics Report 9011** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `9016` | **Analytics Report 9016** | `Referenced Schema` | — | **New Workspace**, **real_edge_02_new_workspace_patterns** | — |
| `9018` | **Analytics Report 9018** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `9029` | **Analytics Report 9029** | `Referenced Schema` | — | **Contact**, **Incident**, **real_edge_01_nested_tabset**, **real_edge_03_split_panel_contact** | — |
| `9041` | **Analytics Report 9041** | `Referenced Schema` | — | **Incident**, **real_edge_01_nested_tabset** | — |
| `9050` | **Analytics Report 9050** | `Referenced Schema` | — | **Contact test**, **Contact**, **real_edge_03_split_panel_contact** | — |

### Custom Analytics Reports

| Report ID | Report Name | Primary Table / Schema | Columns | Referenced In Workspaces | Documentation |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `100008` | **Contacts** | `Standard Table` | 13 | **Contact** | — |
| `122026` | **VSP Routing Table** | `Standard Table` | 10 | Global Catalog | — |

## CPM

### Object Event Handlers

| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `contact_create` | `Contact` | `Create` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `contact_create_internal` | `Contact` | `Create` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `contact_update` | `Contact` | `Update` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `contact_update_internal` | `Contact` | `Update` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `incident_back_in_stock_sync` | `Incident` | `Create` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `incident_create` | `Incident` | `Create` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |

### CPM Routing Mappings

| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `incident_routing` | `Incident` | `Create, Update` | `Sync` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |

### Asynchronous Execution Queues

| Handler Name | Bound Object | Event Trigger | Mode | Entry Point | CPM Summary Document |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ContactAsync` | `Contact` | `Update` | `Async` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |
| `incident_routing` | `Incident` | `Create, Update` | `Async` | `ObjectProcedure::apply` | [report_CPM_Summary.md](cpm/report_CPM_Summary.md) |

## Custom Script Reports

| Script File Name | Component Type | Functions Count | External Calls / Endpoints | Documentation |
| :--- | :--- | :---: | :--- | :--- |
| `address_validation.php` | `CustomScript` | 0 | `—` | [report_address_validation.php.md](scripts/report_address_validation.php.md) |
| `bluebox_greencart_validation.php` | `CustomScript` | 0 | `—` | [report_bluebox_greencart_validation.php.md](scripts/report_bluebox_greencart_validation.php.md) |
| `callcheck.php` | `CustomScript` | 0 | `—` | [report_callcheck.php.md](scripts/report_callcheck.php.md) |
| `child_incident_create.php` | `CustomScript` | 0 | `—` | [report_child_incident_create.php.md](scripts/report_child_incident_create.php.md) |
| `cityworksapicall.php` | `CustomScript` | 0 | `—` | [report_cityworksapicall.php.md](scripts/report_cityworksapicall.php.md) |
| `closing_notes.php` | `CustomScript` | 0 | `—` | [report_closing_notes.php.md](scripts/report_closing_notes.php.md) |
| `duplicate_contacts.php` | `CustomScript` | 0 | `—` | [report_duplicate_contacts.php.md](scripts/report_duplicate_contacts.php.md) |
| `duplicate_incidents.php` | `CustomScript` | 0 | `—` | [report_duplicate_incidents.php.md](scripts/report_duplicate_incidents.php.md) |
| `eventclock.php` | `CustomScript` | 0 | `—` | [report_eventclock.php.md](scripts/report_eventclock.php.md) |
| `sms_integration 1.php` | `CustomScript` | 0 | `—` | [report_sms_integration 1.php.md](scripts/report_sms_integration 1.php.md) |

## BUIs

| Add-In Name | Extension Type | Entry Point | Risk Flags | Documentation |
| :--- | :--- | :--- | :---: | :--- |
| **ContactOrgLookupBUIAddin** | `BUIAddin` | `init.html` | 6 | [report_ContactOrgLookupBUIAddin.md](bui_addins/report_ContactOrgLookupBUIAddin.md) |
| **SendToSiebelBUIAddin** | `BUIAddin` | `init.html` | 6 | [report_SendToSiebelBUIAddin.md](bui_addins/report_SendToSiebelBUIAddin.md) |

## Business Rules Reports

| Rule Set / Source File | Format | Total Rules | Enabled Rules | Invoked CPM Handlers | Documentation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Business_Rules.csv` | `business_rules_csv` | 1209 | 1057 | 47 | [report_Business_Rules.md](rules/report_Business_Rules.md) |

## Shared Resources

The following shared reports and resources are referenced across multiple workspaces:

| Shared Resource / Report ID | Referenced In Workspaces |
| :--- | :--- |
| `125` | **Incident**, **real_edge_01_nested_tabset** |
| `8001` | **Contact test**, **New Workspace**, **real_edge_02_new_workspace_patterns** |
| `8010` | **Incident**, **real_edge_01_nested_tabset** |
| `8012` | **New Workspace**, **real_edge_02_new_workspace_patterns** |
| `8014` | **Incident**, **real_edge_01_nested_tabset** |
| `9011` | **Incident**, **real_edge_01_nested_tabset** |
| `9016` | **New Workspace**, **real_edge_02_new_workspace_patterns** |
| `9018` | **Incident**, **real_edge_01_nested_tabset** |
| `9029` | **Contact**, **Incident**, **real_edge_01_nested_tabset**, **real_edge_03_split_panel_contact** |
| `9041` | **Incident**, **real_edge_01_nested_tabset** |
| `9050` | **Contact test**, **Contact**, **real_edge_03_split_panel_contact** |

## Component Mappings & Linkages

### Workspaces Inventory Linkages

| Source Component | Relationship / Linkage Type | Target Component | Details / Context |
| :--- | :--- | :--- | :--- |
| **Workspace: Contact** | `Linkage` | `CustomScript: address_validation.php` | Cross-Component Mapping |
| **Workspace: Contact** | `Linkage` | `CustomScript: duplicate_contacts.php` | Cross-Component Mapping |
| **Workspace: Contact** | `Linkage` | `CustomScript: gcb_flex.php` | Cross-Component Mapping |
| **Workspace: Contact** | `Linkage` | `Report 100008 (Contacts)` | Cross-Component Mapping |
| **Workspace: Contact** | `Linkage` | `Report 9029` | Cross-Component Mapping |
| **Workspace: Contact** | `Linkage` | `Report 9050` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `ExternalEndpoint: http://cloud.oracle.com/service` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `Report 100015` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `Report 100038` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `Report 10012` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `Report 8001` | Cross-Component Mapping |
| **Workspace: Contact test** | `Linkage` | `Report 9050` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `CustomScript: gcb_flex.php` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 125` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 8010` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 8014` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 9011` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 9018` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 9029` | Cross-Component Mapping |
| **Workspace: Incident** | `Linkage` | `Report 9041` | Cross-Component Mapping |
| **Workspace: New Workspace** | `Linkage` | `ExternalEndpoint: http://cloud.oracle.com/service` | Cross-Component Mapping |
| **Workspace: New Workspace** | `Linkage` | `Report 8001` | Cross-Component Mapping |
| **Workspace: New Workspace** | `Linkage` | `Report 8012` | Cross-Component Mapping |
| **Workspace: New Workspace** | `Linkage` | `Report 9016` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 125` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 8010` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 8014` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 9011` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 9018` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 9029` | Cross-Component Mapping |
| **Workspace: real_edge_01_nested_tabset** | `Linkage` | `Report 9041` | Cross-Component Mapping |
| **Workspace: real_edge_02_new_workspace_patterns** | `Linkage` | `ExternalEndpoint: http://cloud.oracle.com/service` | Cross-Component Mapping |
| **Workspace: real_edge_02_new_workspace_patterns** | `Linkage` | `Report 8001` | Cross-Component Mapping |
| **Workspace: real_edge_02_new_workspace_patterns** | `Linkage` | `Report 8012` | Cross-Component Mapping |
| **Workspace: real_edge_02_new_workspace_patterns** | `Linkage` | `Report 9016` | Cross-Component Mapping |
| **Workspace: real_edge_03_split_panel_contact** | `Linkage` | `CustomScript: gcb_flex.php` | Cross-Component Mapping |
| **Workspace: real_edge_03_split_panel_contact** | `Linkage` | `Report 9029` | Cross-Component Mapping |
| **Workspace: real_edge_03_split_panel_contact** | `Linkage` | `Report 9050` | Cross-Component Mapping |

### CPM Event Procedures Linkages

| Source Component | Relationship / Linkage Type | Target Component | Details / Context |
| :--- | :--- | :--- | :--- |
| **CPM: ContactAsync** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_PASSWORD` | Cross-Component Mapping |
| **CPM: ContactAsync** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_URL` | Cross-Component Mapping |
| **CPM: ContactAsync** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_USERNAME` | Cross-Component Mapping |
| **CPM: ContactAsync** | `Linkage` | `ConfigSetting: CUSTOM_CFG_WEB_SERVICE_ERROR_EMAIL` | Cross-Component Mapping |
| **CPM: ContactAsync** | `Linkage` | `ExternalEndpoint: SOAP: RegisterContact` | Cross-Component Mapping |
| **CPM: ContactAsync** | `Linkage` | `OSVCObject: Contact` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `ConfigSetting: CUSTOM_CFG_API_KEY` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_HOST` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `CustomField: c$loyalty_tier` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `CustomField: c$org_id_temp` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `CustomField: c$vip_status` | Cross-Component Mapping |
| **CPM: contact_create** | `Linkage` | `OSVCObject: Contact` | Cross-Component Mapping |
| **CPM: contact_create_internal** | `Linkage` | `OSVCObject: Contact` | Cross-Component Mapping |
| **CPM: contact_update** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_HOST` | Cross-Component Mapping |
| **CPM: contact_update** | `Linkage` | `CustomField: c$org_id_temp` | Cross-Component Mapping |
| **CPM: contact_update** | `Linkage` | `CustomField: c$vip_status` | Cross-Component Mapping |
| **CPM: contact_update** | `Linkage` | `OSVCObject: Contact` | Cross-Component Mapping |
| **CPM: contact_update_internal** | `Linkage` | `CustomField: c$org_id_temp` | Cross-Component Mapping |
| **CPM: contact_update_internal** | `Linkage` | `OSVCObject: Contact` | Cross-Component Mapping |
| **CPM: incident_back_in_stock_sync** | `Linkage` | `CustomField: c$oos_status` | Cross-Component Mapping |
| **CPM: incident_back_in_stock_sync** | `Linkage` | `OSVCObject: Incident` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$change_request_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$customer_email_address` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$customer_name` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$customer_phone` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$drug_code` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$drug_distributor` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$drug_dosage` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$drug_name` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$drug_part_number` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$incident_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$move_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$mp_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$new_vpn_setup` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$org_id_temp` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$testing_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$token` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$user_profile` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `CustomField: c$user_request_type` | Cross-Component Mapping |
| **CPM: incident_create** | `Linkage` | `OSVCObject: Incident` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ConfigSetting: CUSTOM_CFG_MAILBOX_ACCOUNT_MANAGEMENT` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ConfigSetting: CUSTOM_CFG_MAILBOX_TECH_SUPPORT` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_PASSWORD` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_URL` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ConfigSetting: CUSTOM_CFG_SIEBEL_USERNAME` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$change_request_type` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$customer_number` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$force_update` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$incident_routing_outcome` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$incident_type` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$is_admin` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$is_manual` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$no_chat` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$org_id_temp` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$org_label_temp` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$siebel_status` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$sp_system_type` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `CustomField: c$type_name` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `ExternalEndpoint: SOAP: GetAccounts` | Cross-Component Mapping |
| **CPM: incident_routing** | `Linkage` | `OSVCObject: Incident` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: contact_create` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: contact_create_internal` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: contact_update` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: contact_update_internal` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: incident_back_in_stock_sync` | Cross-Component Mapping |
| **CPMMappings: Mappings.xml** | `Linkage` | `CPM: incident_create` | Cross-Component Mapping |

### BUI Add-Ins & Extensions Linkages

| Source Component | Relationship / Linkage Type | Target Component | Details / Context |
| :--- | :--- | :--- | :--- |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `CustomScript: ../../AuthLibraryExtn/AuthLibraryExtn.js` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `Report 100008 (Contacts)` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `Report 100407` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Contact.CId` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Contact.CustomFields.c$org_id_temp` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Contact.Email` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Incident.CId` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Incident.CO$Org` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Incident.c$org_id_temp` | Cross-Component Mapping |
| **BUIAddin: ContactOrgLookupBUIAddin** | `Linkage` | `WorkspaceField: Incident.c$org_label_temp` | Cross-Component Mapping |
| **BUIAddin: SendToSiebelBUIAddin** | `Linkage` | `CustomScript: ../../AuthLibraryExtn/AuthLibraryExtn.js` | Cross-Component Mapping |
| **BUIAddin: SendToSiebelBUIAddin** | `Linkage` | `WorkspaceField: Incident.Created` | Cross-Component Mapping |
| **BUIAddin: SendToSiebelBUIAddin** | `Linkage` | `WorkspaceField: Incident.IId` | Cross-Component Mapping |
| **BUIAddin: SendToSiebelBUIAddin** | `Linkage` | `WorkspaceField: Incident.c$siebel_sr_number` | Cross-Component Mapping |

### Custom PHP Procedural Scripts Linkages

| Source Component | Relationship / Linkage Type | Target Component | Details / Context |
| :--- | :--- | :--- | :--- |
| **CustomScript: child_incident_create.php** | `Linkage` | `CustomScript: include/init.phph` | Cross-Component Mapping |
| **CustomScript: cityworksapicall.php** | `Linkage` | `CustomScript: include/init.phph` | Cross-Component Mapping |

### Other Cross-Component Linkages Linkages

| Source Component | Relationship / Linkage Type | Target Component | Details / Context |
| :--- | :--- | :--- | :--- |
| **BusinessRule: Contact Business Rules** | `Linkage` | `CPM: ContactAsync` | Cross-Component Mapping |
| **BusinessRule: Contact Business Rules** | `Linkage` | `CPM: contact_create` | Cross-Component Mapping |
| **BusinessRule: Contact Business Rules** | `Linkage` | `CPM: contact_update` | Cross-Component Mapping |
| **BusinessRule: Contact Business Rules** | `Linkage` | `CPM: inc_cancelOrderProcessStart` | Cross-Component Mapping |
| **BusinessRule: Contact Business Rules** | `Linkage` | `CPM: ocr_get_fax_number` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: IncidentFCR` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: dedup_rx_incidents_sync` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: gbl_con_region_assoc` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_b2b_entity_status_update` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_cancelOrderProcessStart` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_customer_routing` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_genesys_conv_SendAdminMsg` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_genesys_conv_createUpdate` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_kyrios_shipper_request` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_notif_rx_pet_not_found_v2` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_notif_rx_pickup_script` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_notif_rx_vet_see_pet` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_notif_vd_warn_48hr` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_notif_vd_warn_contact_vet` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_om_status_update_retry` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_pro_sync_dispo_to_status` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_releaseOrderProcessStart` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_resolveBlockProcessStart` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_send_refax` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_send_rxs_to_clinic` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_sync_contact` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_sync_rhapsody_task` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: inc_vet_diet_cancellation` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_Rx_cancel` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_Rx_cancel_v2` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_back_in_stock_sync` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_get_order_number` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_rxm_transmission` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_set_parent_child` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: incident_verify_parent_close` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: object_detail_logging_inc` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: ocr_get_fax_number` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: petscription_link_auth_sync` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: post_askavet_chat_notification` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: rx_notification_3_day_reminder` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: rx_notification_7_day_reminder` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_autoresponse` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_csat_email` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_depricated_autorespond` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_esclation_email` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_post_reopen` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_reopen` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_router` | Cross-Component Mapping |
| **BusinessRule: Incident Business Rules** | `Linkage` | `CPM: vsp_inc_unassigned` | Cross-Component Mapping |
| **Report 100008 (Contacts)** | `Linkage` | `OSVCObject: contacts` | Cross-Component Mapping |
| **Report 100008 (Contacts)** | `Linkage` | `OSVCObject: sla_instances` | Cross-Component Mapping |
| **Report 100008 (Contacts)** | `Linkage` | `OSVCObject: sss_users` | Cross-Component Mapping |
| **Report 122026 (VSP Routing Table)** | `Linkage` | `OSVCObject: VSP$RoutingTable` | Cross-Component Mapping |

