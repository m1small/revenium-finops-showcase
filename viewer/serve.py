#!/usr/bin/env python3
"""
Live-Updating Viewer Server

Serves HTML reports and monitors CSV file for changes.
Auto-regenerates reports when data size increases.
"""

import http.server
import socketserver
import threading
import time
import os
import sys
import subprocess
from datetime import datetime


class ContinuousReportServer:
    """Server with background monitoring for continuous report updates."""

    def __init__(self, csv_path: str, report_dir: str, port: int = 8000):
        """Initialize the continuous report server.

        Args:
            csv_path: Path to the CSV file to monitor
            report_dir: Directory containing HTML reports
            port: HTTP server port
        """
        self.csv_path = csv_path
        self.report_dir = report_dir
        self.port = port
        self.last_size_mb = 0.0
        self.monitoring = True
        self.monitor_thread = None

    def get_csv_size_mb(self) -> float:
        """Get current size of CSV file in MB."""
        if not os.path.exists(self.csv_path):
            return 0.0
        return os.path.getsize(self.csv_path) / (1024 * 1024)

    def run_analyzers(self):
        """Run all analyzers to regenerate reports."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running analyzers...")

        try:
            # Run the analyzer script
            result = subprocess.run(
                [sys.executable, 'run_all_analyzers.py'],
                cwd='../src',
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Reports updated successfully")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error updating reports:")
                print(result.stderr)

        except subprocess.TimeoutExpired:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzer timeout (>5 minutes)")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error running analyzers: {e}")

    def monitor_and_analyze(self):
        """Background thread that monitors CSV and triggers analysis."""
        print(f"[Monitor] Starting background monitor...")

        while self.monitoring:
            try:
                current_size = self.get_csv_size_mb()

                # Check if size has increased
                if current_size > self.last_size_mb:
                    size_increase = current_size - self.last_size_mb
                    print(f"\n[Monitor] CSV size increased: +{size_increase:.2f} MB (now {current_size:.2f} MB)")

                    # Run analyzers
                    self.run_analyzers()

                    # Update last size
                    self.last_size_mb = current_size

                    # Check if target reached
                    if current_size >= 50.0:
                        print(f"\n[Monitor] Target size reached ({current_size:.2f} MB). Stopping monitoring.")
                        self.monitoring = False
                        break

                # Wait 10 seconds before next check
                time.sleep(10)

            except Exception as e:
                print(f"[Monitor] Error: {e}")
                time.sleep(10)

        print(f"[Monitor] Background monitor stopped")

    def start_monitor_thread(self):
        """Start the background monitoring thread."""
        self.monitor_thread = threading.Thread(target=self.monitor_and_analyze, daemon=True)
        self.monitor_thread.start()

    def serve(self):
        """Start the HTTP server."""
        # Change to report directory
        os.chdir(self.report_dir)

        # Start monitoring thread
        self.start_monitor_thread()

        # Create HTTP server
        Handler = http.server.SimpleHTTPRequestHandler

        # Add custom headers for no-cache
        class NoCacheHandler(Handler):
            def end_headers(self):
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                super().end_headers()

        with socketserver.TCPServer(("", self.port), NoCacheHandler) as httpd:
            print()
            print("=" * 80)
            print("REVENIUM FINOPS SHOWCASE - LIVE VIEWER")
            print("=" * 80)
            print(f"Server running at http://localhost:{self.port}")
            print(f"Monitoring: {self.csv_path}")
            print(f"Reports: {self.report_dir}")
            print()
            print("The viewer will auto-refresh every 15 seconds.")
            print("Reports regenerate automatically when data grows.")
            print()
            print("Press Ctrl+C to stop")
            print("=" * 80)
            print()

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\nShutting down server...")
                self.monitoring = False
                if self.monitor_thread:
                    self.monitor_thread.join(timeout=2)
                print("Server stopped.")


def main():
    """Start the live-updating viewer server."""
    # Paths relative to viewer directory
    csv_path = '../src/data/simulated_calls.csv'
    report_dir = '../src/reports/html'
    port = 8000

    # Check if CSV exists
    if not os.path.exists(csv_path):
        print("=" * 80)
        print("No data file found!")
        print("=" * 80)
        print()
        print("Please generate data first:")
        print("  1. cd ../src")
        print("  2. python3 run_all_simulators.py")
        print()
        print("Then start this viewer again.")
        print("=" * 80)
        sys.exit(1)

    # Ensure report directory exists
    os.makedirs(report_dir, exist_ok=True)

    # Run initial analysis if no reports exist
    if not os.path.exists(os.path.join(report_dir, 'index.html')):
        print("Generating initial reports...")
        subprocess.run(
            [sys.executable, 'run_all_analyzers.py'],
            cwd='../src'
        )
        print()

    # Create and start server
    server = ContinuousReportServer(csv_path, report_dir, port)
    server.serve()


if __name__ == '__main__':
    main()
