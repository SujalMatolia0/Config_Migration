#!/usr/bin/env python
import os
import sys
import webbrowser
import http.server
import socketserver
import threading
import time

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    # Allow port reuse to avoid 'address already in use' errors on quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"\n[SERVER] OSVC Dependency Graph Visualizer is running at:")
            print(f"         👉 http://localhost:{PORT}/results/graph/index.html\n")
            print("Press Ctrl+C to stop the server.\n")
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Start server in a background daemon thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Open browser automatically
    url = f"http://localhost:{PORT}/results/graph/index.html"
    print(f"[LAUNCH] Opening browser at {url}...")
    webbrowser.open(url)
    
    # Keep the main thread running to serve requests
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server. Goodbye!")
        sys.exit(0)
