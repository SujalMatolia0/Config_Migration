# graph_ui

A standalone, portable dependency-graph viewer. It has no dependency on the
rest of this repo other than the shape of `master.json` -- point it at any
`master.json` (this project's or another one that follows the same schema)
and it renders an interactive node/link graph.

## Files

- `index.html`, `style.css`, `app.js` -- the viewer itself (plain HTML/CSS/JS,
  no build step, no CDN, no npm).
- `build.py` -- reads a `master.json`'s `graph` and `meta` keys and writes a
  `data.js` next to a copy of the viewer files, producing a self-contained
  output folder you can open directly in a browser.

## Usage

From this project, after running `osvc_analyser.py`, a viewer is already
built automatically at `<output>/graph/index.html`.

To build one yourself from any `master.json` (e.g. a per-workspace one at
`results/<workspace>/master.json`, or one copied to a different machine):

```bash
python graph_ui/build.py path/to/master.json
# writes path/to/graph/index.html (+ style.css, app.js, data.js)

python graph_ui/build.py path/to/master.json path/to/output_dir
# writes to an explicit output_dir instead
```

Then just open `index.html` in any browser -- no server required.

## Using it in another project

Copy the whole `graph_ui/` folder wherever you like and run:

```bash
python graph_ui/build.py /any/path/master.json /any/output/dir
```

The only contract is that `master.json` contains:

```json
{
  "meta": { "serverVersion": "...", "...": "..." },
  "graph": {
    "nodes": [{ "id": "...", "type": "...", "label": "...", "isOrphan": false, "data": {} }],
    "edges": [{ "source": "...", "target": "...", "label": "..." }]
  }
}
```

## Programmatic use

```python
from graph_ui.build import build_graph_ui

build_graph_ui("results/master.json", "results/graph")   # path to master.json
build_graph_ui(master_data_dict, "results/graph")          # already-loaded dict
```
