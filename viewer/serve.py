#!/usr/bin/env python3
"""
Simple HTTP Server for Report Viewer
Serves the HTML reports and viewer interface
"""

import http.server
import socketserver
import os
import sys

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from multiple directories"""
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    """Start the HTTP server"""
    # Change to project root directory (parent of viewer)
    viewer_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(viewer_dir)
    os.chdir(project_root)
    
    print("=" * 70)
    print("🌐 REVENIUM FINOPS SHOWCASE - REPORT VIEWER")
    print("=" * 70)
    print()
    print(f"🚀 Starting server on port {PORT}...")
    print()
    print(f"📊 Open your browser to: http://localhost:{PORT}/viewer/index.html")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("👋 Server stopped")
        print("=" * 70)
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use")
            print(f"   Try a different port or stop the other server")
            sys.exit(1)
        else:
            raise


if __name__ == '__main__':
    main()
