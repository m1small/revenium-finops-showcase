#!/usr/bin/env python3
"""
Live-Updating Viewer Server

Serves HTML reports and monitors status:
- CSV file size progress toward 2GB target
- Report availability (checks file existence)
"""

import http.server
import socketserver
import json
import time
import os
import sys
import threading
import subprocess
from datetime import datetime
from urllib.parse import parse_qs, urlparse


class StatusViewerServer:
    """Server that displays live status of data generation and report availability."""

    def __init__(self, csv_path: str, report_dir: str, port: int = 8000):
        """Initialize the status viewer server.

        Args:
            csv_path: Path to the CSV file to monitor
            report_dir: Directory containing HTML reports
            port: HTTP server port
        """
        self.csv_path = csv_path
        self.report_dir = report_dir
        self.port = port
        self.target_size_mb = 2048.0  # 2GB target
        self.analyzer_status = {}  # Track status of running analyzers
        self.status_lock = threading.Lock()  # Thread-safe status updates

    def get_csv_size_mb(self) -> float:
        """Get current size of CSV file in MB."""
        if not os.path.exists(self.csv_path):
            return 0.0
        return os.path.getsize(self.csv_path) / (1024 * 1024)

    def get_csv_line_count(self) -> int:
        """Get number of lines in CSV file (excluding header)."""
        if not os.path.exists(self.csv_path):
            return 0
        try:
            with open(self.csv_path, 'r') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except:
            return 0

    def check_report_status(self) -> dict:
        """Check which reports exist in the report directory."""
        reports = {
            'understanding.html': 'Understanding Usage & Cost',
            'performance.html': 'Performance Tracking',
            'realtime.html': 'Real-Time Decision Making',
            'optimization.html': 'Rate Optimization',
            'alignment.html': 'Organizational Alignment',
            'profitability.html': 'Customer Profitability',
            'pricing.html': 'Pricing Strategy',
            'features.html': 'Feature Economics'
        }

        status = {}
        for filename, name in reports.items():
            filepath = os.path.join(self.report_dir, filename)
            status[filename] = {
                'name': name,
                'exists': os.path.exists(filepath),
                'size_kb': os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
            }
        return status

    def get_status_json(self) -> dict:
        """Get current status as JSON."""
        csv_size_mb = self.get_csv_size_mb()
        line_count = self.get_csv_line_count()

        with self.status_lock:
            analyzer_status_copy = self.analyzer_status.copy()

        return {
            'timestamp': datetime.now().isoformat(),
            'csv': {
                'size_mb': round(csv_size_mb, 2),
                'target_mb': self.target_size_mb,
                'progress_pct': min((csv_size_mb / self.target_size_mb) * 100, 100),
                'line_count': line_count,
                'complete': csv_size_mb >= self.target_size_mb
            },
            'reports': self.check_report_status(),
            'analyzer_status': analyzer_status_copy
        }

    def run_analyzer_async(self, analyzer_id: str):
        """Run an analyzer in a background thread.

        Args:
            analyzer_id: ID of the analyzer to run (e.g., 'understanding')
        """
        def run():
            # Update status to reprocessing
            with self.status_lock:
                self.analyzer_status[analyzer_id] = {
                    'status': 'reprocessing',
                    'started_at': datetime.now().isoformat()
                }

            try:
                # Get the path to run_analyzer.py (one level up from viewer/)
                src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
                run_analyzer_path = os.path.join(src_dir, 'run_analyzer.py')

                # Run the analyzer script
                result = subprocess.run(
                    [sys.executable, run_analyzer_path, analyzer_id],
                    cwd=src_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    # Success
                    with self.status_lock:
                        self.analyzer_status[analyzer_id] = {
                            'status': 'complete',
                            'completed_at': datetime.now().isoformat()
                        }
                else:
                    # Error
                    with self.status_lock:
                        self.analyzer_status[analyzer_id] = {
                            'status': 'error',
                            'error': result.stderr,
                            'failed_at': datetime.now().isoformat()
                        }

            except subprocess.TimeoutExpired:
                with self.status_lock:
                    self.analyzer_status[analyzer_id] = {
                        'status': 'error',
                        'error': 'Analyzer timed out after 5 minutes',
                        'failed_at': datetime.now().isoformat()
                    }
            except Exception as e:
                with self.status_lock:
                    self.analyzer_status[analyzer_id] = {
                        'status': 'error',
                        'error': str(e),
                        'failed_at': datetime.now().isoformat()
                    }

        # Start analyzer in background thread
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def serve(self):
        """Start the HTTP server."""
        # Create custom handler that serves status API
        parent = self

        class StatusHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                # Status API endpoint
                if self.path.startswith('/api/status'):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                    self.end_headers()

                    status = parent.get_status_json()
                    self.wfile.write(json.dumps(status, indent=2).encode())
                    return

                # Serve files from report directory
                self.directory = parent.report_dir

                # Add no-cache headers for HTML files
                super().do_GET()

            def do_POST(self):
                # Run analyzer endpoint
                if self.path.startswith('/api/run_analyzer'):
                    # Parse analyzer_id from query string
                    parsed = urlparse(self.path)
                    params = parse_qs(parsed.query)
                    analyzer_id = params.get('analyzer_id', [None])[0]

                    if not analyzer_id:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': False,
                            'error': 'Missing analyzer_id parameter'
                        }).encode())
                        return

                    # Start analyzer in background
                    parent.run_analyzer_async(analyzer_id)

                    # Return immediate response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True,
                        'analyzer_id': analyzer_id,
                        'message': 'Analyzer started'
                    }).encode())
                    return

                # Method not allowed for other paths
                self.send_response(405)
                self.end_headers()

            def end_headers(self):
                # No-cache headers for all responses
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                super().end_headers()

            def log_message(self, format, *args):
                # Suppress access logs for cleaner output
                pass

        # Ensure report directory exists
        os.makedirs(self.report_dir, exist_ok=True)

        # Create status page if index.html doesn't exist
        index_path = os.path.join(self.report_dir, 'index.html')
        if not os.path.exists(index_path):
            self.create_status_page(index_path)

        with socketserver.TCPServer(("", self.port), StatusHandler) as httpd:
            print()
            print("=" * 80)
            print("REVENIUM FINOPS SHOWCASE - STATUS VIEWER")
            print("=" * 80)
            print(f"Server running at http://localhost:{self.port}")
            print(f"Monitoring CSV: {self.csv_path}")
            print(f"Report directory: {self.report_dir}")
            print()
            print("The viewer displays live status:")
            print("  - CSV data generation progress (toward 2GB)")
            print("  - Report availability (file existence)")
            print()
            print("Workflow:")
            print("  1. Run simulator: cd ../src && python3 run_all_simulators.py")
            print("  2. Run analyzers: cd ../src && python3 run_all_analyzers.py")
            print("  3. View reports: Refresh browser to see updated status")
            print()
            print("Press Ctrl+C to stop")
            print("=" * 80)
            print()

            # Print initial status
            status = self.get_status_json()
            print(f"CSV Status: {status['csv']['size_mb']:.2f} MB / {status['csv']['target_mb']:.0f} MB ({status['csv']['progress_pct']:.1f}%)")
            reports_ready = sum(1 for r in status['reports'].values() if r['exists'])
            print(f"Reports Ready: {reports_ready}/8")
            print()

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\nShutting down server...")
                print("Server stopped.")

    def create_status_page(self, output_path: str):
        """Create the main status/index page."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Revenium FinOps Showcase - Status Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 36px;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 16px;
            opacity: 0.8;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #1a1a1a;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }
        .progress-container {
            background: #f5f5f5;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .progress-bar-container {
            background: #e0e0e0;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            margin: 20px 0;
        }
        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        .progress-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #1a1a1a;
            margin-top: 5px;
        }
        .report-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .report-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
            position: relative;
        }
        .report-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .report-card.available {
            border-color: #4CAF50;
            background: #f1f8f4;
        }
        .report-card.unavailable {
            border-color: #ff9800;
            background: #fff8f0;
            opacity: 0.7;
        }
        .status-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: white;
        }
        .status-badge.complete {
            background: #4CAF50;
        }
        .status-badge.pending {
            background: #ff9800;
        }
        .status-badge.reprocessing {
            background: #2196f3;
            animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        .report-card h3 {
            margin-bottom: 10px;
            color: #1a1a1a;
            padding-right: 80px;
        }
        .report-card p {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .run-button, .view-button {
            display: inline-block;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-family: inherit;
        }
        .run-button {
            background: #9C27B0;
            flex: 0 0 auto;
        }
        .run-button:hover {
            background: #7B1FA2;
        }
        .run-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .view-button {
            background: #2196f3;
            flex: 1;
        }
        .view-button:hover {
            background: #1976d2;
        }
        .view-button.disabled {
            background: #ccc;
            pointer-events: none;
        }
        .auto-refresh {
            text-align: center;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            margin-top: 20px;
            color: #666;
        }
        .workflow {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            margin-bottom: 30px;
        }
        .workflow h3 {
            color: #1976d2;
            margin-bottom: 10px;
        }
        .workflow ol {
            margin-left: 20px;
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Revenium FinOps Showcase</h1>
            <p>AI Cost Management & Usage-Based Revenue Analysis</p>
        </div>

        <div class="content">
            <div class="workflow">
                <h3>Workflow</h3>
                <ol>
                    <li><strong>Run simulator:</strong> <code>cd ../src && python3 run_all_simulators.py</code></li>
                    <li><strong>Run analyzers:</strong> <code>cd ../src && python3 run_all_analyzers.py</code></li>
                    <li><strong>View reports:</strong> Refresh browser to see updated status</li>
                </ol>
            </div>

            <div class="section">
                <h2>Data Generation Progress</h2>
                <div class="progress-container">
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="progress-bar" style="width: 0%">
                            <span id="progress-text">0%</span>
                        </div>
                    </div>
                    <div class="progress-stats">
                        <div class="stat">
                            <div class="stat-label">CSV Size</div>
                            <div class="stat-value" id="csv-size">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Target</div>
                            <div class="stat-value" id="csv-target">2048 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Progress</div>
                            <div class="stat-value" id="csv-progress">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Calls</div>
                            <div class="stat-value" id="csv-lines">-</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Analysis Reports</h2>
                <div class="report-grid" id="report-grid">
                    <!-- Reports will be populated by JavaScript -->
                </div>
            </div>

            <div class="auto-refresh">
                Last updated: <span id="last-update">-</span> |
                Auto-refresh every 1 second
            </div>
        </div>
    </div>

    <script>
        // Map filenames to analyzer IDs
        const ANALYZER_IDS = {
            'understanding.html': 'understanding',
            'performance.html': 'performance',
            'realtime.html': 'realtime',
            'optimization.html': 'optimization',
            'alignment.html': 'alignment',
            'profitability.html': 'profitability',
            'pricing.html': 'pricing',
            'features.html': 'features'
        };

        function formatSize(mb) {
            if (mb < 1) {
                return (mb * 1024).toFixed(1) + ' KB';
            } else if (mb >= 1024) {
                return (mb / 1024).toFixed(2) + ' GB';
            }
            return mb.toFixed(2) + ' MB';
        }

        function formatNumber(num) {
            return num.toLocaleString();
        }

        function runAnalyzer(analyzerId, button) {
            // Disable the button
            button.disabled = true;
            button.textContent = 'Running...';

            // Send POST request to run analyzer
            fetch('/api/run_analyzer?analyzer_id=' + analyzerId, {
                method: 'POST'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    console.log('Analyzer started:', analyzerId);
                } else {
                    alert('Failed to start analyzer: ' + data.error);
                    button.disabled = false;
                    button.textContent = '⟳ Run';
                }
            })
            .catch(e => {
                console.error('Error starting analyzer:', e);
                alert('Failed to start analyzer');
                button.disabled = false;
                button.textContent = '⟳ Run';
            });
        }

        function updateStatus() {
            fetch('/api/status?_=' + Date.now())
                .then(r => r.json())
                .then(data => {
                    // Update CSV progress
                    const csv = data.csv;
                    document.getElementById('csv-size').textContent = formatSize(csv.size_mb);
                    document.getElementById('csv-progress').textContent = csv.progress_pct.toFixed(1) + '%';
                    document.getElementById('csv-lines').textContent = formatNumber(csv.line_count);

                    const progressBar = document.getElementById('progress-bar');
                    progressBar.style.width = csv.progress_pct + '%';
                    document.getElementById('progress-text').textContent = csv.progress_pct.toFixed(1) + '%';

                    // Update report grid
                    const reportGrid = document.getElementById('report-grid');
                    reportGrid.innerHTML = '';

                    const analyzerStatus = data.analyzer_status || {};

                    for (const [filename, info] of Object.entries(data.reports)) {
                        const analyzerId = ANALYZER_IDS[filename];
                        const status = analyzerStatus[analyzerId];
                        const isReprocessing = status && status.status === 'reprocessing';

                        const card = document.createElement('div');
                        card.className = 'report-card ' + (info.exists ? 'available' : 'unavailable');

                        let statusBadge;
                        if (isReprocessing) {
                            statusBadge = '<div class="status-badge reprocessing">⟳ Reprocessing</div>';
                        } else if (info.exists) {
                            statusBadge = '<div class="status-badge complete">✓ Complete</div>';
                        } else {
                            statusBadge = '<div class="status-badge pending">⋯ Pending</div>';
                        }

                        const viewButton = info.exists ?
                            `<a href="${filename}" class="view-button">View Report →</a>` :
                            '<span class="view-button disabled">Not Generated</span>';

                        const runButton = `<button class="run-button" onclick="runAnalyzer('${analyzerId}', this)" ${isReprocessing ? 'disabled' : ''}>⟳ Run</button>`;

                        card.innerHTML = `
                            ${statusBadge}
                            <h3>${info.name}</h3>
                            <p>${info.exists ? 'Report available (' + info.size_kb.toFixed(1) + ' KB)' : 'Run analyzers to generate'}</p>
                            <div class="button-group">
                                ${runButton}
                                ${viewButton}
                            </div>
                        `;

                        reportGrid.appendChild(card);
                    }

                    // Update timestamp
                    document.getElementById('last-update').textContent =
                        new Date(data.timestamp).toLocaleTimeString();
                })
                .catch(e => {
                    console.log('Status update failed:', e);
                });
        }

        // Update immediately and then every 1 second
        updateStatus();
        setInterval(updateStatus, 1000);
    </script>
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html)


def main():
    """Start the status viewer server."""
    # Paths relative to viewer directory
    csv_path = '../src/data/simulated_calls.csv'
    report_dir = '../src/reports/html'
    port = 8000

    # CSV doesn't need to exist yet - viewer will show 0% progress
    # This allows starting viewer before running simulator

    # Create server instance
    server = StatusViewerServer(csv_path, report_dir, port)

    # Start server
    server.serve()


if __name__ == '__main__':
    main()
