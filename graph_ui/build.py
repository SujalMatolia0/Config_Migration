#!/usr/bin/env python
"""
Standalone builder for the OSVC dependency graph viewer.

Decoupled from the analyser pipeline: it only needs a master.json (the file
osvc_analyser.py already writes to <output>/master.json or
<output>/<workspace>/master.json). Point it at any master.json -- from this
project or copied elsewhere -- and it produces a self-contained, portable
viewer folder with no server or build step required to open it.

Usage:
    python build.py path/to/master.json [output_dir]

If output_dir is omitted, a "graph" folder is created next to master.json.
"""
import argparse
import json
import os
import shutil

_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS = ["index.html", "style.css", "app.js"]


def _load_master(master_json):
    """Accepts either a path to master.json or an already-loaded dict."""
    if isinstance(master_json, dict):
        return master_json
    with open(master_json, "r", encoding="utf-8") as f:
        return json.load(f)


def build_graph_ui(master_json, output_dir):
    """
    Renders a portable graph viewer into output_dir from a master.json
    (path or dict). Copies index.html/style.css/app.js from this folder
    alongside a generated data.js holding the graph + meta payload, so
    output_dir becomes fully self-contained and drop-in-anywhere -- just
    open index.html in a browser.
    """
    master_data = _load_master(master_json)
    graph_data = master_data.get("graph", {"nodes": [], "edges": []})
    meta = master_data.get("meta", {})

    os.makedirs(output_dir, exist_ok=True)

    for asset in _ASSETS:
        shutil.copyfile(os.path.join(_DIR, asset), os.path.join(output_dir, asset))

    data_js = (
        f"window.GRAPH_DATA = {json.dumps(graph_data)};\n"
        f"window.GRAPH_META = {json.dumps(meta)};\n"
    )
    with open(os.path.join(output_dir, "data.js"), "w", encoding="utf-8") as f:
        f.write(data_js)

    return os.path.join(output_dir, "index.html")


def main():
    parser = argparse.ArgumentParser(
        description="Build a portable OSVC dependency graph viewer from a master.json export."
    )
    parser.add_argument("master_json", help="Path to a master.json produced by osvc_analyser.py")
    parser.add_argument(
        "output_dir", nargs="?", default=None,
        help="Directory to write the viewer into (default: a 'graph' folder next to master.json)"
    )
    args = parser.parse_args()

    output_dir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(args.master_json)), "graph"
    )
    index_path = build_graph_ui(args.master_json, output_dir)
    print(f"Graph viewer written -> {index_path}")
    print("Open it directly in any browser (no server needed).")


if __name__ == "__main__":
    main()
