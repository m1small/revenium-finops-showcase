#!/usr/bin/env python3
"""
Simple HTTP Server for viewing Revenium FinOps Reports
"""

import http.server
import socketserver
import os
import sys


PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ReportHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and CORS headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        sys.stdout.write("%s - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format % args))


def main():
    """Start the HTTP server"""
    
    # Check if reports exist
    reports_dir = os.path.join(os.path.dirname(DIRECTORY), 'reports', 'html')
    if not os.path.exists(reports_dir):
        print("⚠️  Warning: reports/html/ directory not found!")
        print("   Please run the analyzers first to generate reports:")
        print("   cd src && python run_all_analyzers.py")
        print()
    
    try:
        with socketserver.TCPServer(("", PORT), ReportHandler) as httpd:
            print("=" * 60)
            print("Revenium FinOps Report Viewer")
            print("=" * 60)
            print(f"\n✓ Server running at http://localhost:{PORT}/")
            print(f"✓ Serving from: {DIRECTORY}")
            print("\nPress Ctrl+C to stop the server\n")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Port {PORT} is already in use")
            print(f"   Try a different port or stop the other server")
            sys.exit(1)
        else:
            raise


if __name__ == '__main__':
    main()
