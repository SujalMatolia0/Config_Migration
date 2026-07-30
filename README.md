# OSVC Instance Analyser & Configuration Accelerator Platform

An enterprise-grade analysis platform for Oracle Service Cloud (OSVC) that parses exported XML, PHP, JS, and HTML configuration packages (Workspaces, Analytics Reports, Business Rules, Navigation Sets, CPM Event Handlers, and BUI Add-Ins), builds detailed dependency graphs, highlights orphaned components, audits configuration risks, and provides interactive Markdown, JSON, HTML, and web dashboard reports.

---

## Key Features

- **Web Accelerator Platform & Dashboard**: Interactive Flask-based web application (`web_platform.py`) running on `http://127.0.0.1:5050` with a high-contrast Crimson Red & Off-White / Cream aesthetic theme.
- **Unified Master System Architecture Report (`COMPLETE_SYSTEM_MAPPING.md`)**:
  - **Entity Module Consolidation**: Rolls up fragmented sub-components under canonical primary object headers (`Contact`, `Incident`, `Organization`, `Test_Record`, `General`).
  - **Populated Execution Context & Linkages**: Renders non-empty details (fields, tabs, business rules, report columns, entry points) and linkage counts (`In -> Out`) for every component.
  - **Audit-Critical Orphaned Components**: Explicitly flags unreferenced custom scripts, workspace layouts, and CPM procedures with audit risk reasons.
  - **Consolidated Integration Endpoints Catalog**: Maps outbound REST API endpoints and SOAP services to their exact source script files.
  - **Executive Risk Signals**: Highlights orphaned components, unverified HTTP endpoints, and custom field references using structured callout alerts (`> [!WARNING]`, `> [!IMPORTANT]`, `> [!TIP]`).
- **Interactive Dependency Graph Viewer**:
  - **Universal Double-Click Inspector**: Double-clicking any graph node opens the 3-tab inspector sidebar (`Details`, `Documentation`, `Architecture`).
  - **Layered Architecture Flowcharts**: Renders end-to-end data pipeline flowcharts connecting Workspaces, CPM Event Handlers, Custom Scripts, BUI Add-Ins, and External API Endpoints.
  - **Smart Graph Search & Auto-Focus**: Real-time auto-zoom and node/edge highlighting when typing in the search bar.
  - **Bulk Selection Toggles**: `Select All` and `Deselect All` object filter controls.
  - **High-Contrast Color System**: Deep Purple (`#9333EA`) for Workspaces, Sky Blue (`#0284C7`) for Standard Fields, Bright Emerald (`#10B981`) for Custom Fields (`c$`).
- **High-DPI SVG & PNG Vector Export Engine**:
  - **Self-Contained SVG Export**: Embeds style blocks, background canvas (`#FAF8F5`), and explicit presentation attributes to ensure SVG files render with 100% fidelity in any viewer.
  - **Preserved Arrowhead Markers**: Preserves vector arrowheads (`#arrow`, `#arrow-mapping`, `#arrow-cross`) for edge directions.
  - **2x Resolution PNG Export**: Exports high-DPI raster images with smoothing enabled.
- **2-Tier Hierarchy File Input System**:
  - **Tier 1 (Top-Level Component Accordions)**: Collapsible containers per OSVC export component (`Workspaces`, `Analytics Reports`, `CPM Procedures`, `BUI Add-Ins`).
  - **Tier 2 (Sub-Group Labeled Dividers)**: Categorized file tables grouping items by schema domain (`Standard Object Workspaces`, `Custom & Edge Layout Workspaces`, `Object Event Handlers`, `CPM Routing Mappings`, `BUI Extension Packages`).
- **Content Schema Auto-Classifier**: Inspects XML root schemas (`<analytics_core>`, `<TabSet>`, `<ObjectProcedure>`, `<Rule>`, `<nav_set>`) and ZIP manifests (`init.html`, `manifest.json`), auto-categorizing exports into designated subfolders.
- **CPM Analysis & AI Summaries**: Analyzes Custom Process Model (CPM) PHP handlers and XML exports, integrating Groq AI API (`llama-3.3-70b-versatile`) with static rule-based fallback.
- **Strict Mode Element Auditing**: Captures and logs all unhandled OSVC XML tags and attributes into `results/unknowns.json`.

---

## Directory Structure

```
.
├── web_platform.py           # Flask web accelerator application & API backend
├── templates/
│   └── index.html            # Crimson & Cream 85/15 web platform UI template
├── graph_ui/                 # D3 & Mermaid dependency graph visualization suite
│   ├── index.html            # Standalone graph viewer template
│   ├── app.js                # Graph engine, node inspector & vector export handlers
│   └── style.css             # High-contrast graph styling & theme tokens
├── src/
│   ├── analyser/             # Analysis and graph building engine
│   │   ├── endpoint_extractor.py # External API/Browser URL aggregator
│   │   ├── orphan_detector.py    # Orphaned/inactive rule & script scanner
│   │   ├── relationship_mapper.py# Graph link mapping logic
│   │   └── graph_builder.py     # Graph node & edge schema builder
│   ├── parsers/              # Parsers for OSVC exports
│   │   ├── workspace_parser.py   # Workspace XML parser
│   │   ├── report_parser.py      # Report XML parser
│   │   ├── rule_parser.py        # Business Rules XML parser
│   │   ├── nav_parser.py         # Navigation Set XML parser
│   │   ├── cpm_parser.py         # CPM PHP handler parser & Groq AI summarizer
│   │   ├── bui_parser.py         # BUI Add-In package parser
│   │   └── script_parser.py      # JS/PHP custom script static analyzer
│   └── output/               # Report output utilities
│       ├── master_report_generator.py # Complete master system report generator
│       ├── markdown_generator.py # Theme-agnostic Markdown report generator
│       ├── json_writer.py        # Master JSON & summary JSON schema writers
│       └── report_builder.py     # HTML/PDF report generators
├── input/                    # Organized input OSVC exports
│   ├── workspaces/           # Workspace XML files
│   ├── cpm/                  # CPM PHP handlers & Mappings.xml
│   ├── reports/              # Report XML files
│   ├── rules/                # Business Rules XML files
│   ├── scripts/              # Custom PHP/JS scripts & BUI packages
│   └── navigation/           # Navigation Set XML files
├── results/                  # Generated reports and analysis outputs
│   ├── COMPLETE_SYSTEM_MAPPING.md # Unified Master System Architecture Report
│   ├── master.json           # Global master JSON data schema
│   ├── index.md              # Global cross-workspace index
│   ├── unknowns.json         # Coverage gaps and unhandled element inventory
│   ├── graph/                # Generated interactive graph viewer
│   ├── json/                 # Format-sorted JSON files
│   ├── markdown/             # Format-sorted Markdown reports
│   └── workspaces/           # Per-workspace reports & graphs
├── osvc_analyser.py          # Orchestrator CLI entry point
├── schema.json               # Master JSON validation schema
└── README.md
```

---

## Installation & Setup

### 1. Python Environment
Create a virtual environment and install required dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install lxml jinja2 flask
```

### 2. Groq AI Integration (Optional)
To enable LLM-generated summaries for CPM procedures using Groq API:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   ```

*(If no key is set, the analyzer automatically uses static rule-based extraction).*

---

## Running the Web Accelerator Platform

Start the Flask web server:
```bash
.venv/bin/python web_platform.py
```

Open `http://127.0.0.1:5050` in your web browser.

- **Drag-and-Drop Uploads**: Drag OSVC XML, PHP, or ZIP files directly into the Smart Dropzone. The Auto-Classifier inspects schema headers, categorizes files, and routes them automatically.
- **Grouped 2-Tier Inventory**: Expand top-level component accordions (`Workspaces`, `Reports`, `CPM`, `BUI`) to view sub-group labeled tables (`Standard Object Workspaces`, `Object Event Handlers`, `Routing Mappings`).
- **Interactive Control Sidebar**: Toggle AI Summaries, Strict Auditing Mode, or Unknowns Dumping.
- **One-Click Execution**: Click `RUN ACCELERATOR` to execute analysis, generate global graph visualizations, and compile `COMPLETE_SYSTEM_MAPPING.md`.

---

## Running via Command Line (CLI)

Place OSVC configuration exports in the `input/` directory and run the orchestrator script:

### Parse exports and generate all reports:
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results
```

### Enable Strict Mode (warns on console for unhandled proprietary XML tags/attributes):
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --strict
```

### Export Unknown Elements Inventory (`results/unknowns.json`):
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --dump-unknowns
```

### Disable AI logic summaries in CPM reports:
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --no-ai-summary
```

---

## Vector & Image Exporting

From the interactive graph viewer (`/results/graph/index.html`):
- Click **Export SVG** to download a self-contained vector graphic with embedded style blocks and preserved arrowheads.
- Click **Export PNG** to save a crisp 2x resolution High-DPI raster image.
