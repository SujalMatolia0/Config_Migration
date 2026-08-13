# OSVC Field & System Menu Fetcher Suite

Standalone Python scripts to query Oracle Service Cloud (OSVC) Connect REST API metadata endpoints and export multi-tab Excel reports (`.xlsx`).

---

## Directory Organization

```text
scripts/fetcher/
├── README.md                     # Suite documentation & usage guide
├── __init__.py                   # Package initialization
├── osvc_rest_fetcher.py          # Core REST API connection & metadata catalog module
├── standalone_field_fetcher.py   # Extractor for Standard Object Fields
├── standalone_menu_fetcher.py    # Extractor for System Menus & NamedIDs
├── run_all.py                    # Unified runner script for all extractions
└── results/                      # Output directory for generated Excel reports
    ├── Fetched_Fields.xlsx       # Output report for Standard Object Fields
    └── Standard_Menu_Fields.xlsx # Output report for System Menu Fields
```

---

## Script Modules & Usage

### 1. Unified Extraction (Run All)

Executes both the Standard Objects field extractor and the System Menu fields extractor in sequence:

```bash
python scripts/fetcher/run_all.py
```

### 2. Standard Object Fields Extractor

Queries OSVC Connect REST API metadata catalog for standard objects (`contacts`, `incidents`, `organizations`, `answers`, `tasks`, `opportunities`, `assets`, etc.) and extracts field definitions, data types, system flags, lookups, and descriptions:

```bash
python scripts/fetcher/standalone_field_fetcher.py
```

Optional Arguments:
- `--host`: OSVC domain or full REST endpoint URL
- `--username`: OSVC REST API Username
- `--password`: OSVC REST API Password
- `--output`: Custom output Excel file path (default: `results/Fetched_Fields.xlsx`)
- `--objects`: Specific object schemas to fetch (e.g. `--objects contacts incidents`)
- `--include-custom`: Include custom fields and custom object schemas

### 3. System Menu Fields Extractor

Targets OSVC System Menus highlighted in OSVC BUI / Agent Console (`Answer Access Levels`, `Answer Statuses`, `Channel Types`, `Chat Agent Statuses`, `Chat Queues`, `Contact Roles`, `Contact Types`, `Incident Queues`, `Incident Severities`, `Incident Statuses`, `Organization Address Types`, etc.) and fetches configured option values via `/services/rest/connect/v1.4/namedIDs/...` endpoints:

```bash
python scripts/fetcher/standalone_menu_fetcher.py
```

Optional Arguments:
- `--host`: OSVC domain or full REST endpoint URL
- `--username`: OSVC REST API Username
- `--password`: OSVC REST API Password
- `--output`: Custom output Excel file path (default: `results/Standard_Menu_Fields.xlsx`)
- `--endpoints`: Additional namedIDs endpoints to fetch (e.g. `--endpoints namedIDs/incidents/assignedTo/staffGroup`)

---

## Output Reports (`results/`)

- **`results/Fetched_Fields.xlsx`**:
  - `Summary`: Metrics, object breakdown table, total fields, system vs custom field counts.
  - `All_Fields`: Master consolidated field catalog table.
  - `[Object_Tabs]`: Dedicated worksheets for each extracted standard object.

- **`results/Standard_Menu_Fields.xlsx`**:
  - `Summary`: Overview metrics for extracted System Menus and option counts.
  - `System_Menus_Overview`: Overview table of highlighted System Menus and REST paths.
  - `All_Menu_Options`: Consolidated catalog of all extracted menu option values.
  - `[Menu_Tabs]`: Individual worksheets for each highlighted System Menu listing option IDs, lookup names, and resource links.
