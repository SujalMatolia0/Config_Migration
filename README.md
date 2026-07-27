# OSVC Instance Analyser & Configuration Accelerator Platform

An enterprise-grade analysis platform for Oracle Service Cloud (OSVC) that parses exported XML, PHP, JS, and HTML configuration packages (Workspaces, Analytics Reports, Business Rules, Navigation Sets, CPM Event Handlers, and BUI Add-Ins), builds detailed dependency graphs, highlights orphaned components, audits configuration risks, and provides interactive Markdown, JSON, HTML, and web dashboard reports.

---

## Key Features

- **Web Accelerator Platform & Dashboard**: Includes an interactive Flask-based web application (`web_platform.py`) running on `http://127.0.0.1:5050` with a Crimson Red & Off-White / Cream aesthetic theme.
- **85% / 15% Split Dashboard Architecture**:
  - **Main Panel (85% Width)**: Features the Smart Drag-and-Drop Uploader, 2-Tier Classified Input Inventory, Generated Results & Report Portal, and System Execution Log Console.
  - **Sticky Sidebar (15% Width)**: Houses instant controls for AI Summaries, Strict Auditing Mode, Unknown Elements Dumping, and Output Report Formats alongside the primary execution button.
- **2-Tier Hierarchy File Input System**:
  - **Tier 1 (Top-Level Component Accordions)**: Collapsible containers per OSVC export component (`Workspaces`, `Analytics Reports`, `CPM Procedures`, `BUI Add-Ins`).
  - **Tier 2 (Sub-Group Labeled Dividers)**: Categorized file tables grouping items by schema domain (e.g. `Standard Object Workspaces`, `Custom & Edge Layout Workspaces`, `Object Event Handlers`, `CPM Routing Mappings`, `BUI Extension Packages`).
- **Content Schema Auto-Classifier**: Inspects XML root schemas (`<analytics_core>`, `<TabSet>`, `<ObjectProcedure>`, `<Rule>`, `<nav_set>`) and ZIP manifests (`init.html`, `manifest.json`), auto-categorizes exports, and routes files into designated subfolders (`workspaces/`, `reports/`, `cpm/`, `scripts/`).
- **CPM Analysis & AI Summaries**: Analyzes Custom Process Model (CPM) PHP handlers and XML exports. Integrates Groq AI API (`llama-3.3-70b-versatile`) for automatic logic summaries with rule-based regex fallback.
- **Strict Mode Element Auditing**: Captures and logs all unhandled OSVC XML tags and attributes into `results/unknowns.json` to eliminate silent data loss.
- **BUI Add-In & Extension Auditing**: Performs static analysis for Browser UI (BUI) JavaScript/HTML Add-In packages, extracting field reads/writes, lifecycle hooks, external API endpoints, and security findings.
- **Center-Aligned Mermaid Flowcharts**: Generates Mermaid flow diagrams formatted for clean rendering.

---

## Directory Structure

```
.
├── web_platform.py           # Flask web accelerator application & API backend
├── templates/
│   └── index.html            # Crimson & Cream 85/15 web platform UI template
├── analyser/                 # Analysis and graph building engine
│   ├── endpoint_extractor.py # External API/Browser URL aggregator
│   ├── orphan_detector.py    # Orphaned/inactive rule & script scanner
│   └── relationship_mapper.py# Graph link mapping logic
├── parsers/                  # Parsers for OSVC exports
│   ├── workspace_parser.py   # Workspace XML parser
│   ├── report_parser.py      # Report XML parser
│   ├── rule_parser.py        # Business Rules XML parser
│   ├── nav_parser.py         # Navigation Set XML parser
│   ├── cpm_parser.py         # CPM PHP handler parser & Groq AI summarizer
│   ├── bui_parser.py         # BUI Add-In package parser
│   └── script_parser.py      # JS/PHP custom script static analyzer
├── output/                   # Report output utilities
│   ├── markdown_generator.py # Theme-agnostic Markdown report generator
│   ├── json_writer.py        # Master JSON & summary JSON schema writers
│   └── report_builder.py     # HTML/PDF report generators
├── input/                    # Organized input OSVC exports
│   ├── workspaces/           # Workspace XML files
│   ├── cpm/                  # CPM PHP handlers & Mappings.xml
│   ├── reports/              # Report XML files
│   ├── rules/                # Business Rules XML files
│   ├── scripts/              # Custom PHP/JS scripts & BUI packages
│   └── navigation/           # Navigation Set XML files
├── results/                  # Generated reports and analysis outputs
│   ├── master.json           # Global master JSON data schema
│   ├── report.html           # Global interactive HTML dashboard
│   ├── index.md              # Global cross-workspace index
│   ├── unknowns.json         # Coverage gaps and unhandled element inventory
│   ├── json/                 # Format-sorted JSON files
│   ├── markdown/             # Format-sorted Markdown reports
│   ├── html/                 # Format-sorted HTML dashboards
│   ├── workspaces/           # Per-workspace reports
│   ├── cpm/                  # CPM procedure summaries (MD + JSON)
│   └── scripts/              # BUI Add-In summaries (MD + JSON)
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
- **Interactive Control Sidebar**: Toggle AI Summaries, Strict Auditing Mode, or Unknowns Dumping, and select output formats.
- **One-Click Execution**: Click `RUN ACCELERATOR` to execute analysis and open interactive HTML/Markdown report viewers in the portal.

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

### Build PDF reports:
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --format pdf
```

---

## Launching the Flow Diagram Visualizer

To start the React Flow visualization UI:

```bash
cd ui
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.
