#!/usr/bin/env python3
"""
Unified OSVC Metadata & System Menu Extractor Runner.

Executes both extraction suites:
1. Standard Object Fields Extractor (standalone_field_fetcher.py) -> results/Fetched_Fields.xlsx
2. System Menu Fields Extractor (standalone_menu_fetcher.py)  -> results/Standard_Menu_Fields.xlsx

Usage:
    python scripts/fetcher/run_all.py
"""

import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from standalone_field_fetcher import main as run_field_fetcher
from standalone_menu_fetcher import main as run_menu_fetcher


def main():
    parser = argparse.ArgumentParser(description="Unified OSVC Metadata & System Menu Extractor")
    parser.add_argument("--host", help="OSVC Host domain or full endpoint URL")
    parser.add_argument("--username", help="OSVC REST API Username")
    parser.add_argument("--password", help="OSVC REST API Password")

    args, unknown = parser.parse_known_args()

    print("[START] Running Unified OSVC Metadata Extraction Suite...")
    print("=" * 60)

    # 1. Run Standard Objects Field Extractor
    print("\n[STEP 1/2] Fetching Standard Object Fields...")
    field_sys_args = sys.argv[0:1]
    if args.host:
        field_sys_args.extend(["--host", args.host])
    if args.username:
        field_sys_args.extend(["--username", args.username])
    if args.password:
        field_sys_args.extend(["--password", args.password])

    orig_argv = list(sys.argv)
    try:
        sys.argv = field_sys_args
        run_field_fetcher()
    except SystemExit as e:
        if e.code != 0:
            print(f"[WARNING] Standard Object Field Extractor exited with code {e.code}")
    finally:
        sys.argv = orig_argv

    print("\n" + "=" * 60)

    # 2. Run System Menu Fields Extractor
    print("[STEP 2/2] Fetching System Menu Fields...")
    menu_sys_args = sys.argv[0:1]
    if args.host:
        menu_sys_args.extend(["--host", args.host])
    if args.username:
        menu_sys_args.extend(["--username", args.username])
    if args.password:
        menu_sys_args.extend(["--password", args.password])

    try:
        sys.argv = menu_sys_args
        run_menu_fetcher()
    except SystemExit as e:
        if e.code != 0:
            print(f"[WARNING] System Menu Extractor exited with code {e.code}")
    finally:
        sys.argv = orig_argv

    print("\n" + "=" * 60)
    print("[DONE] Unified extraction complete! All Excel reports generated in scripts/fetcher/results/")


if __name__ == "__main__":
    main()
