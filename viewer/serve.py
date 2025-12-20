#!/usr/bin/env python3
"""
Simple HTTP Server for Report Viewer
Serves the HTML reports and viewer interface
Automatically processes all CSV data before serving
"""

import http.server
import socketserver
import os
import sys
import subprocess

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


def check_and_process_data():
    """Check if data exists and process it with analyzers"""
    viewer_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(viewer_dir)
    src_dir = os.path.join(project_root, 'src')
    data_file = os.path.join(src_dir, 'data', 'simulated_calls.csv')
    reports_dir = os.path.join(src_dir, 'reports', 'html')
    manifest_file = os.path.join(reports_dir, 'manifest.json')
    
    # Check if data exists
    if not os.path.exists(data_file):
        print("⚠️  No data found. Please run simulators first:")
        print("   cd src")
        print("   python3 run_all_simulators.py")
        print()
        return False
    
    # Check if reports are up to date
    data_mtime = os.path.getmtime(data_file)
    reports_exist = os.path.exists(manifest_file)
    
    if reports_exist:
        manifest_mtime = os.path.getmtime(manifest_file)
        if manifest_mtime > data_mtime:
            print("✅ Reports are up to date")
            print()
            return True
    
    # Need to generate/regenerate reports
    print("📊 Processing data with analyzers...")
    print()
    
    try:
        # Run analyzers
        result = subprocess.run(
            [sys.executable, 'run_all_analyzers.py'],
            cwd=src_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All data processed successfully")
            print()
            return True
        else:
            print(f"❌ Error processing data: {result.stderr}")
            print()
            return False
    except Exception as e:
        print(f"❌ Error running analyzers: {str(e)}")
        print()
        return False


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
    
    # Check and process data
    if not check_and_process_data():
        print("⚠️  Cannot start server without processed data")
        sys.exit(1)
    
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
