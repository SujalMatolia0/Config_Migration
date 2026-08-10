# OSVC Field Extractor Studio

A high-performance extraction and reporting engine for **Oracle Service Cloud (OSVC / RightNow)**. Extracts standard object schemas, custom object XML definitions, and workspace layout fields into structured, multi-tab Excel workbooks (`.xlsx`).

---

## Key Features

- **Live Standard Object Schema Extraction**: Connects directly to OSVC Connect REST API (`/services/rest/connect/v1.4/metadata-catalog`) via HTTP GET to extract complete standard object field metadata.
- **Strict Read-Only REST Guarantee**: Executes **HTTP GET ONLY**. Zero POST, PATCH, DELETE, or data-mutating requests.
- **Workspace XML Layout Parsing**: Parses OSVC Workspace export XML files to catalog all layout controls, fields, tab locations, and UI rules.
- **Workspace Field ID to REST API Mapping**: Automatically translates legacy workspace control IDs (e.g. `RefNo`, `CId`, `ProdId`, `OrgId`, `SeverityId`) to OSVC REST API metadata catalog field keys (`referenceNumber`, `primaryContact.id`, `product.id`, `organization.id`, `severity`).
- **Ignored & Unmapped Controls Manifest**: Generates an explicit `Ignored_Fields` sheet cataloging all non-schema workspace elements (UI controls, validation flags, business rule context variables, and unmapped legacy fields).
- **Custom Object XML Schema Parsing**: Parses OSVC Custom Object XML exports to extract system and custom fields (`c$`), data types, nullability, lookups, and constraints.
- **Unified Field Catalog**: Generates `Field_Catalog.xlsx`, merging workspace layout positions with full schema metadata (Data Types, REST Availability, Nullability, System vs Custom badges, Max Length, etc.).
- **Interactive Web UI Studio**: Modern web application built on Flask serving a live dashboard at `http://localhost:5055` with real-time log stream, file drag-and-drop, sample data preview, and instant downloads.
- **Headless CLI Support**: Run via terminal for automated build pipelines or scheduled batch extraction tasks.

---

## Output Workbook Specifications

The extractor generates 4 dedicated Excel reports in the `./results` directory:

| Workbook | Description | Primary Key / Index |
|---|---|---|
| `Standard_Objects.xlsx` | Standard object schemas fetched via Live REST API | 1 tab per Standard Object |
| `Custom_Objects.xlsx` | Custom object schemas parsed from XML exports | 1 tab per Custom Object |
| `Workspaces.xlsx` | Workspace layout controls, field tab placements, and `Ignored_Fields` manifest | 1 tab per Workspace + `Ignored_Fields` |
| `Field_Catalog.xlsx` | Combined master report merging workspace layouts with object schema metadata and `Ignored_Fields` manifest | 1 tab per Workspace + `Ignored_Fields` |

---

## Ignored & Unmapped Fields Manifest (`Ignored_Fields` Tab)

Workspace layout XMLs contain UI display controls and Business Rules variables that do not map to underlying database object schemas. To ensure zero silent data loss, these are cataloged into an `Ignored_Fields` sheet with full context:

| Category | Description | Example Field IDs |
|---|---|---|
| **Workspace UI Control** | UI layout indicators, grid display controls, search inputs | `Dormant`, `LinesPerPage`, `SearchText`, `SearchType`, `State`, `PasswordEncrypt` |
| **UI Validation Control** | Checkbox/dropdown indicators for field validity | `Email.Invalid`, `EmailAlt1.Invalid`, `EmailAlt2.Invalid` |
| **Business Rule Context Variable** | Runtime Business Rules escalation levels and state variables | `RuleCtx.Escllevel`, `RuleCtx.State`, `RuleState` |
| **Legacy Workspace Field** | Deprecated or legacy marketing fields | `MaMailType`, `MaOrgName`, `TotRev` |

---

## System Architecture & File Structure

```
field_extractor/
├── main.py                 # Standalone CLI entry point
├── web_ui.py               # Flask Web Application & REST API Server (Port 5055)
├── excel_exporter.py       # OpenPyXL Excel generation engine
├── field_id_mapping.py     # Workspace Field ID to REST API Schema Translation
├── osvc_rest_fetcher.py    # Strict HTTP GET REST API schema extractor
├── object_parser.py        # XML parser for OSVC Custom Objects
├── workspace_parser.py     # XML parser for OSVC Workspace layouts
├── config.py               # Credential configuration store
├── requirements.txt        # Python dependency manifest
├── README.md               # Feature documentation and user guide
├── sample_inputs/          # Pre-packaged sample Workspace & Object XMLs
├── results/                # Target folder for generated Excel reports
└── templates/              # Web UI HTML/CSS templates
    └── index.html          # Web UI Studio single-page application
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- Pip package manager

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start Guide

### Option 1: Run Web UI Dashboard (Recommended)

Launch the web studio interface:

```bash
python web_ui.py 5055
```

Open your browser and navigate to:
```
http://localhost:5055
```

From the dashboard:
1. Click **Load Sample Input** to inspect pre-loaded schemas and layout previews.
2. Or drag and drop your exported Workspace (`.xml`) and Custom Object (`.xml`) files.
3. Use **Fetch Standard Objects via Live OSVC REST API** to pull live schemas.
4. Download individual `.xlsx` workbooks or the full `all_reports.zip` package.

---

### Option 2: Run via Command Line (CLI)

Run full extraction using sample inputs:

```bash
python main.py --workspace sample_inputs --object sample_inputs --output results
```

Extract via Live OSVC REST API:

```bash
python main.py \
  --rest-host "gcb.custhelp.com" \
  --rest-user "your_api_username" \
  --rest-pass "your_api_password" \
  --workspace sample_inputs \
  --output results
```

---

## Security & Read-Only Policy

> [!IMPORTANT]
> The REST API fetcher module (`osvc_rest_fetcher.py`) uses **STRICT HTTP GET ONLY** requests targeting the OSVC Metadata Catalog endpoint:
> `GET /services/rest/connect/v1.4/metadata-catalog`
> It never performs mutating HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`). Your OSVC instance data remains completely untouched.
