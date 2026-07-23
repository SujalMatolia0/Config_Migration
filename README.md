# OSVC Instance Analyser & Flow Mapper

This accelerator scans exported Oracle Service Cloud (OSVC) configuration files (Workspaces, Reports, Business Rules, Navigation Sets, CPM Handlers, and custom scripts), builds a detailed dependency graph, highlights orphaned components, audits configuration risks, and provides an interactive Next.js flow diagram visualizer.

---

## 📂 Directory Structure

```
.
├── analyser/                 # Analysis and graph building engine
│   ├── endpoint_extractor.py # External API/Browser URL aggregator
│   ├── orphan_detector.py    # Orphaned/inactive rule & script scanner
│   └── relationship_mapper.py# Graph link mapping logic
├── parsers/                  # Parsers for OSVC exports
│   ├── workspace_parser.py   # Workspace XML parser
│   ├── report_parser.py      # Report XML parser
│   ├── rule_parser.py        # Business Rules XML parser
│   ├── nav_parser.py         # Navigation Set XML parser
│   ├── cpm_parser.py         # CPM PHP handler static analyzer
│   └── script_parser.py      # JS/PHP custom script static analyzer
├── output/                   # Report output utilities
│   ├── json_writer.py        # Compiles the Master JSON schema
│   ├── report_builder.py     # HTML/PDF report generators
│   └── templates/
│       └── report.html.j2    # High-aesthetic Jinja2 dashboard template
├── ui/                       # Next.js + React Flow Interactive Dashboard
├── tests/                    # Parser test suite
├── osvc_analyser.py          # Orchestrator CLI entry point
├── schema.json               # Master JSON validation schema
└── README.md
```

---

## 🛠️ Installation & Setup

### 1. Python Parser Environment
Create a virtual environment and install the required dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install lxml jinja2 weasyprint
```

### 2. Next.js Flow UI Environment
Navigate to the `ui` folder and install dependencies:
```bash
cd ui
npm install
```

---

## 🚀 Running the Analyser CLI

Place all OSVC configuration exports (XML, PHP, JS) in an `input` directory.

### Parse exports and generate Master JSON + HTML dashboard:
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results
```

### Build PDF reports (requires weasyprint system dependencies installed):
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --format pdf
```

### Parse only and export JSON:
```bash
.venv/bin/python osvc_analyser.py --input ./input --output ./results --json-only
```

### Rebuild report from existing `master.json`:
```bash
.venv/bin/python osvc_analyser.py --output ./results --report-only
```

---

## 📊 Launching the Interactive Flow Diagram

To start the React Flow visualization UI:

```bash
cd ui
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

- **Interactive Nodes:** Hover and drag nodes. Click any node to open the inspector panel on the right, displaying record types, column fields, rules, parsed endpoint variables, or security risk alerts.
- **Node Filtering:** Select/deselect component types (Workspaces, Reports, Scripts, CPMs, etc.) from the sidebar to control graph size.
- **Orphan / Dead Code Toggle:** Select "Show Orphans Only" to instantly hide active elements and inspect unreferenced components.
- **Direct Sync:** Click the refresh button in the sidebar footer to dynamically fetch changes from the parser output without refreshing your browser page.
