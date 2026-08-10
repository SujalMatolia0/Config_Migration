#!/usr/bin/env python3
import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIELD_EXTRACTOR_DIR = os.path.join(BASE_DIR, "field_extractor")
WEB_UI_PATH = os.path.join(FIELD_EXTRACTOR_DIR, "web_ui.py")
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "bin", "python")

if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

def main():
    port = "5055"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    print("==========================================================================")
    print("      LAUNCHING OSVC FIELD EXTRACTOR WEB STUDIO SERVER                   ")
    print("==========================================================================")
    print(f"Server URL: http://localhost:{port}")
    print("Press Ctrl+C to stop server.")
    print("--------------------------------------------------------------------------")

    cmd = [VENV_PYTHON, WEB_UI_PATH, port]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nField Extractor Web UI server stopped.")

if __name__ == "__main__":
    main()
