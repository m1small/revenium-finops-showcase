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

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import TARGET_SIZE_MB, DATA_CSV_PATH, REPORT_DIR, VIEWER_PORT


class StatusViewerServer:
    """Server that displays live status of data generation and report availability."""

    def __init__(self, csv_path: str = None, report_dir: str = None, port: int = None):
        """Initialize the status viewer server.

        Args:
            csv_path: Path to the CSV file to monitor (defaults to config.DATA_CSV_PATH)
            report_dir: Directory containing HTML reports (defaults to config.REPORT_DIR)
            port: HTTP server port (defaults to config.VIEWER_PORT)
        """
        self.csv_path = csv_path or DATA_CSV_PATH
        self.report_dir = report_dir or REPORT_DIR
        self.port = port or VIEWER_PORT
        self.target_size_mb = TARGET_SIZE_MB  # From config (50 MB)
        self.analyzer_status = {}  # Track status of running analyzers
        self.status_lock = threading.Lock()  # Thread-safe status updates

        # Performance: Cache line count to avoid re-reading large files
        self.line_count_cache = None
        self.line_count_mtime = None
        self.last_file_position = 0  # For incremental counting

        # Performance: Cache report status
        self.report_status_cache = None
        self.report_cache_time = None
        self.REPORT_CACHE_TTL = 5  # Cache reports for 5 seconds

        # Progress tracking for long-running operations
        self.simulator_status = {
            'status': 'idle',  # idle, running, complete, error
            'message': '',
            'started_at': None,
            'completed_at': None
        }
        self.all_analyzers_status = {
            'status': 'idle',  # idle, running, complete, error
            'current': None,  # Currently running analyzer
            'completed': 0,
            'total': 8,
            'message': '',
            'started_at': None,
            'completed_at': None
        }

    def get_csv_size_mb(self) -> float:
        """Get current size of CSV file in MB."""
        try:
            return os.path.getsize(self.csv_path) / (1024 * 1024)
        except (FileNotFoundError, OSError):
            return 0.0

    def _get_incremental_line_count(self, current_size: int) -> int | None:
        """Count only new lines added since last check (for growing files).

        Args:
            current_size: Current file size in bytes

        Returns:
            Updated line count, or None if incremental counting not possible
        """
        # Only works if file has grown (not shrunk or replaced)
        if current_size < self.last_file_position:
            return None

        # If file hasn't grown, return cached count
        if current_size == self.last_file_position:
            return self.line_count_cache

        try:
            with open(self.csv_path, 'r') as f:
                # Seek to last known position
                f.seek(self.last_file_position)

                # Count new lines only
                new_lines = sum(1 for _ in f)

                # Update position
                self.last_file_position = current_size

                # Return updated count
                return self.line_count_cache + new_lines

        except Exception:
            # If incremental fails, return None to trigger full count
            return None

    def get_csv_line_count(self) -> int:
        """Get number of lines in CSV file (excluding header).

        Uses intelligent caching to avoid re-reading large files:
        - Returns cached value if file hasn't been modified (based on mtime)
        - For actively growing files, uses incremental counting
        - Falls back to full count only when necessary
        """
        if not os.path.exists(self.csv_path):
            return 0

        try:
            # Get current file modification time and size
            stat_info = os.stat(self.csv_path)
            current_mtime = stat_info.st_mtime
            current_size = stat_info.st_size

            # If file hasn't changed, return cached value
            if (self.line_count_cache is not None and
                self.line_count_mtime is not None and
                self.line_count_mtime == current_mtime):
                return self.line_count_cache

            # File has changed - need to recalculate
            # For large files (>100MB), try incremental counting first
            if current_size > 100 * 1024 * 1024 and self.line_count_cache is not None:
                # Try incremental counting for growing files
                try:
                    new_count = self._get_incremental_line_count(current_size)
                    if new_count is not None:
                        self.line_count_cache = new_count
                        self.line_count_mtime = current_mtime
                        return new_count
                except Exception as e:
                    print(f"[PERF] Incremental count failed, falling back to full count: {e}")

            # Full file count (for small files or when incremental fails)
            with open(self.csv_path, 'r') as f:
                count = sum(1 for _ in f) - 1  # Subtract header

            # Update cache
            self.line_count_cache = count
            self.line_count_mtime = current_mtime
            self.last_file_position = current_size  # Track position for next incremental

            return count

        except Exception as e:
            # On error, return cached value if available
            print(f"[ERROR] Line count failed: {e}")
            return self.line_count_cache if self.line_count_cache is not None else 0

    def check_report_status(self) -> dict:
        """Check which reports exist in the report directory.

        Uses caching to avoid repeated filesystem checks (reports don't change frequently).
        Cache is valid for REPORT_CACHE_TTL seconds.
        """
        # Return cached value if still valid
        current_time = time.time()
        if (self.report_status_cache is not None and
            self.report_cache_time is not None and
            current_time - self.report_cache_time < self.REPORT_CACHE_TTL):
            return self.report_status_cache

        # Cache expired or doesn't exist - check filesystem
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
            # Use try/except to batch the exists/size check
            try:
                size_kb = os.path.getsize(filepath) / 1024
                status[filename] = {
                    'name': name,
                    'exists': True,
                    'size_kb': size_kb
                }
            except FileNotFoundError:
                status[filename] = {
                    'name': name,
                    'exists': False,
                    'size_kb': 0
                }

        # Update cache
        self.report_status_cache = status
        self.report_cache_time = current_time

        return status

    def get_status_json(self) -> dict:
        """Get current status as JSON.

        Optimized to minimize filesystem calls by batching operations.
        """
        # Get CSV stats efficiently (line_count internally uses stat, no need for separate call)
        line_count = self.get_csv_line_count()
        csv_size_mb = self.get_csv_size_mb()

        with self.status_lock:
            analyzer_status_copy = self.analyzer_status.copy()
            simulator_status_copy = self.simulator_status.copy()
            all_analyzers_status_copy = self.all_analyzers_status.copy()

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
            'analyzer_status': analyzer_status_copy,
            'simulator_status': simulator_status_copy,
            'all_analyzers_status': all_analyzers_status_copy
        }

    def list_csv_files(self) -> dict:
        """List all CSV files in the src/data directory.

        Returns:
            dict with list of CSV files and their metadata
        """
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')

            # Check if data directory exists
            if not os.path.exists(data_dir):
                return {
                    'success': False,
                    'error': 'Data directory not found',
                    'files': []
                }

            # List all CSV files
            csv_files = []
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        stat_info = os.stat(filepath)
                        size_mb = stat_info.st_size / (1024 * 1024)
                        mtime = datetime.fromtimestamp(stat_info.st_mtime)

                        csv_files.append({
                            'filename': filename,
                            'size_mb': round(size_mb, 2),
                            'modified': mtime.isoformat(),
                            'modified_display': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                            'is_current': os.path.abspath(filepath) == os.path.abspath(self.csv_path)
                        })
                    except Exception as e:
                        print(f"[WARNING] Failed to get stats for {filename}: {e}")

            # Sort by modification time (newest first)
            csv_files.sort(key=lambda x: x['modified'], reverse=True)

            print(f"[INFO] Found {len(csv_files)} CSV files in {data_dir}")

            return {
                'success': True,
                'files': csv_files,
                'data_dir': data_dir
            }

        except Exception as e:
            print(f"[ERROR] Failed to list CSV files: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

    def update_csv_path(self, csv_filename: str) -> dict:
        """Update the CSV path to load a different file.

        Args:
            csv_filename: Name of the CSV file (with extension) in src/data folder

        Returns:
            dict with success status and message
        """
        # Construct path to CSV in src/data folder
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')
        new_csv_path = os.path.join(data_dir, csv_filename)

        # Check if file exists
        if not os.path.exists(new_csv_path):
            error_msg = f'CSV file not found: {csv_filename}'
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Searched in: {data_dir}")
            return {
                'success': False,
                'error': error_msg
            }

        # Update the CSV path
        old_path = self.csv_path
        self.csv_path = new_csv_path

        # Reset caches when loading new CSV
        self.line_count_cache = None
        self.line_count_mtime = None
        self.last_file_position = 0
        self.report_status_cache = None
        self.report_cache_time = None

        # Log success
        print(f"[INFO] CSV loaded successfully: {csv_filename}")
        print(f"[INFO] Previous path: {old_path}")
        print(f"[INFO] New path: {new_csv_path}")

        # Get and log initial stats
        size_mb = self.get_csv_size_mb()
        line_count = self.get_csv_line_count()
        print(f"[INFO] CSV size: {size_mb:.2f} MB, Lines: {line_count:,}")

        return {
            'success': True,
            'message': f'Loaded CSV: {csv_filename}',
            'csv_path': new_csv_path
        }

    def run_simulators_async(self):
        """Run all simulators in a background thread."""
        def run():
            print(f"[INFO] Starting all simulators")

            # Update status to running
            with self.status_lock:
                self.simulator_status = {
                    'status': 'running',
                    'message': 'Running data simulators...',
                    'started_at': datetime.now().isoformat(),
                    'completed_at': None
                }

            try:
                # Get the path to run_all_simulators.py
                src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
                run_simulators_path = os.path.join(src_dir, 'run_all_simulators.py')

                print(f"[INFO] Executing: {sys.executable} {run_simulators_path}")
                print(f"[INFO] Working directory: {src_dir}")

                # Run the simulators script
                result = subprocess.run(
                    [sys.executable, run_simulators_path],
                    cwd=src_dir,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                if result.returncode == 0:
                    print(f"[SUCCESS] Simulators completed")
                    if result.stdout:
                        print(f"[OUTPUT] {result.stdout.strip()}")

                    # Update status to complete
                    with self.status_lock:
                        self.simulator_status = {
                            'status': 'complete',
                            'message': 'Simulators completed successfully',
                            'started_at': self.simulator_status['started_at'],
                            'completed_at': datetime.now().isoformat()
                        }
                else:
                    print(f"[ERROR] Simulators failed (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"[STDERR] {result.stderr.strip()}")
                    if result.stdout:
                        print(f"[STDOUT] {result.stdout.strip()}")

                    # Update status to error
                    with self.status_lock:
                        self.simulator_status = {
                            'status': 'error',
                            'message': f'Simulators failed: {result.stderr[:100] if result.stderr else "Unknown error"}',
                            'started_at': self.simulator_status['started_at'],
                            'completed_at': datetime.now().isoformat()
                        }

            except subprocess.TimeoutExpired:
                print(f"[ERROR] Simulators timed out after 10 minutes")
                with self.status_lock:
                    self.simulator_status = {
                        'status': 'error',
                        'message': 'Simulators timed out after 10 minutes',
                        'started_at': self.simulator_status['started_at'],
                        'completed_at': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"[ERROR] Exception running simulators: {str(e)}")
                print(f"[ERROR] Exception type: {type(e).__name__}")
                with self.status_lock:
                    self.simulator_status = {
                        'status': 'error',
                        'message': f'Error: {str(e)}',
                        'started_at': self.simulator_status.get('started_at'),
                        'completed_at': datetime.now().isoformat()
                    }

        # Start simulators in background thread
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def run_all_analyzers_async(self):
        """Run all analyzers in a background thread with progress tracking."""
        def run():
            print(f"[INFO] Starting all analyzers")

            # Update status to running
            with self.status_lock:
                self.all_analyzers_status = {
                    'status': 'running',
                    'current': 'Initializing...',
                    'completed': 0,
                    'total': 8,
                    'message': 'Starting all analyzers...',
                    'started_at': datetime.now().isoformat(),
                    'completed_at': None
                }

            try:
                # Get the path to run_all_analyzers.py
                src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
                run_all_analyzers_path = os.path.join(src_dir, 'run_all_analyzers.py')

                print(f"[INFO] Executing: {sys.executable} {run_all_analyzers_path}")
                print(f"[INFO] Working directory: {src_dir}")

                # Run the analyzers script
                result = subprocess.run(
                    [sys.executable, run_all_analyzers_path],
                    cwd=src_dir,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                if result.returncode == 0:
                    print(f"[SUCCESS] All analyzers completed")
                    if result.stdout:
                        print(f"[OUTPUT] {result.stdout.strip()}")

                    # Update status to complete
                    with self.status_lock:
                        self.all_analyzers_status = {
                            'status': 'complete',
                            'current': None,
                            'completed': 8,
                            'total': 8,
                            'message': 'All analyzers completed successfully',
                            'started_at': self.all_analyzers_status['started_at'],
                            'completed_at': datetime.now().isoformat()
                        }
                else:
                    print(f"[ERROR] Analyzers failed (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"[STDERR] {result.stderr.strip()}")
                    if result.stdout:
                        print(f"[STDOUT] {result.stdout.strip()}")

                    # Update status to error
                    with self.status_lock:
                        self.all_analyzers_status = {
                            'status': 'error',
                            'current': None,
                            'completed': self.all_analyzers_status.get('completed', 0),
                            'total': 8,
                            'message': f'Analyzers failed: {result.stderr[:100] if result.stderr else "Unknown error"}',
                            'started_at': self.all_analyzers_status['started_at'],
                            'completed_at': datetime.now().isoformat()
                        }

            except subprocess.TimeoutExpired:
                print(f"[ERROR] Analyzers timed out after 10 minutes")
                with self.status_lock:
                    self.all_analyzers_status = {
                        'status': 'error',
                        'current': None,
                        'completed': self.all_analyzers_status.get('completed', 0),
                        'total': 8,
                        'message': 'Analyzers timed out after 10 minutes',
                        'started_at': self.all_analyzers_status['started_at'],
                        'completed_at': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"[ERROR] Exception running analyzers: {str(e)}")
                print(f"[ERROR] Exception type: {type(e).__name__}")
                with self.status_lock:
                    self.all_analyzers_status = {
                        'status': 'error',
                        'current': None,
                        'completed': self.all_analyzers_status.get('completed', 0),
                        'total': 8,
                        'message': f'Error: {str(e)}',
                        'started_at': self.all_analyzers_status.get('started_at'),
                        'completed_at': datetime.now().isoformat()
                    }

        # Start analyzers in background thread
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def run_analyzer_async(self, analyzer_id: str):
        """Run an analyzer in a background thread.

        Args:
            analyzer_id: ID of the analyzer to run (e.g., 'understanding')
        """
        def run():
            print(f"[INFO] Starting analyzer: {analyzer_id}")

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

                print(f"[INFO] Executing: {sys.executable} {run_analyzer_path} {analyzer_id}")
                print(f"[INFO] Working directory: {src_dir}")

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
                    print(f"[SUCCESS] Analyzer completed: {analyzer_id}")
                    if result.stdout:
                        print(f"[OUTPUT] {result.stdout.strip()}")

                    with self.status_lock:
                        self.analyzer_status[analyzer_id] = {
                            'status': 'complete',
                            'completed_at': datetime.now().isoformat()
                        }
                else:
                    # Error
                    print(f"[ERROR] Analyzer failed: {analyzer_id} (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"[STDERR] {result.stderr.strip()}")
                    if result.stdout:
                        print(f"[STDOUT] {result.stdout.strip()}")

                    with self.status_lock:
                        self.analyzer_status[analyzer_id] = {
                            'status': 'error',
                            'error': result.stderr,
                            'failed_at': datetime.now().isoformat()
                        }

            except subprocess.TimeoutExpired:
                error_msg = 'Analyzer timed out after 5 minutes'
                print(f"[ERROR] {error_msg}: {analyzer_id}")

                with self.status_lock:
                    self.analyzer_status[analyzer_id] = {
                        'status': 'error',
                        'error': error_msg,
                        'failed_at': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"[ERROR] Exception running analyzer {analyzer_id}: {str(e)}")
                print(f"[ERROR] Exception type: {type(e).__name__}")

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
                    try:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Expires', '0')
                        self.end_headers()

                        status = parent.get_status_json()
                        self.wfile.write(json.dumps(status, indent=2).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Client closed connection - ignore
                        pass
                    return

                # List CSV files endpoint
                if self.path.startswith('/api/list_csv_files'):
                    try:
                        print(f"[API] GET /api/list_csv_files")

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Expires', '0')
                        self.end_headers()

                        result = parent.list_csv_files()
                        self.wfile.write(json.dumps(result, indent=2).encode())

                        print(f"[API] Returned {len(result.get('files', []))} CSV files")
                    except (BrokenPipeError, ConnectionResetError):
                        # Client closed connection - ignore
                        print(f"[API WARNING] Client closed connection during CSV list")
                        pass
                    except Exception as e:
                        print(f"[API ERROR] Exception in list_csv_files: {str(e)}")
                        print(f"[API ERROR] Exception type: {type(e).__name__}")
                    return

                # Serve files from report directory
                self.directory = parent.report_dir

                # Add no-cache headers for HTML files
                super().do_GET()

            def do_POST(self):
                # Load CSV endpoint
                if self.path.startswith('/api/load_csv'):
                    try:
                        # Parse csv_filename from query string
                        parsed = urlparse(self.path)
                        params = parse_qs(parsed.query)
                        csv_filename = params.get('csv_filename', [None])[0]

                        print(f"[API] POST /api/load_csv - Filename: {csv_filename}")

                        if not csv_filename:
                            print(f"[API ERROR] Missing csv_filename parameter")
                            self.send_response(400)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                'success': False,
                                'error': 'Missing csv_filename parameter'
                            }).encode())
                            return

                        # Update CSV path
                        result = parent.update_csv_path(csv_filename)

                        # Return response
                        status_code = 200 if result['success'] else 404
                        print(f"[API] Response status: {status_code}, Success: {result.get('success', False)}")

                        self.send_response(status_code)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Client closed connection - ignore
                        print(f"[API WARNING] Client closed connection during CSV load")
                        pass
                    except Exception as e:
                        print(f"[API ERROR] Exception in load_csv: {str(e)}")
                        print(f"[API ERROR] Exception type: {type(e).__name__}")
                    return

                # Run simulators endpoint
                if self.path.startswith('/api/run_simulators'):
                    try:
                        print(f"[API] POST /api/run_simulators")

                        # Start simulators in background
                        parent.run_simulators_async()

                        print(f"[API] Simulators background thread started")

                        # Return immediate response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'message': 'Simulators started'
                        }).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        print(f"[API WARNING] Client closed connection during simulators start")
                        pass
                    except Exception as e:
                        print(f"[API ERROR] Exception in run_simulators: {str(e)}")
                        print(f"[API ERROR] Exception type: {type(e).__name__}")
                    return

                # Run all analyzers endpoint
                if self.path.startswith('/api/run_all_analyzers'):
                    try:
                        print(f"[API] POST /api/run_all_analyzers")

                        # Start all analyzers in background
                        parent.run_all_analyzers_async()

                        print(f"[API] All analyzers background thread started")

                        # Return immediate response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'message': 'All analyzers started'
                        }).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        print(f"[API WARNING] Client closed connection during all analyzers start")
                        pass
                    except Exception as e:
                        print(f"[API ERROR] Exception in run_all_analyzers: {str(e)}")
                        print(f"[API ERROR] Exception type: {type(e).__name__}")
                    return

                # Run analyzer endpoint
                if self.path.startswith('/api/run_analyzer'):
                    try:
                        # Parse analyzer_id from query string
                        parsed = urlparse(self.path)
                        params = parse_qs(parsed.query)
                        analyzer_id = params.get('analyzer_id', [None])[0]

                        print(f"[API] POST /api/run_analyzer - Analyzer ID: {analyzer_id}")

                        if not analyzer_id:
                            print(f"[API ERROR] Missing analyzer_id parameter")
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

                        print(f"[API] Analyzer background thread started: {analyzer_id}")

                        # Return immediate response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'analyzer_id': analyzer_id,
                            'message': 'Analyzer started'
                        }).encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Client closed connection - ignore
                        print(f"[API WARNING] Client closed connection during analyzer start")
                        pass
                    except Exception as e:
                        print(f"[API ERROR] Exception in run_analyzer: {str(e)}")
                        print(f"[API ERROR] Exception type: {type(e).__name__}")
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

        # Always generate fresh index.html on server start
        index_path = os.path.join(self.report_dir, 'index.html')
        self.create_status_page(index_path)
        print(f"[INFO] Generated index.html at {index_path}")

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
                # Clean up index.html on server stop
                if os.path.exists(index_path):
                    os.remove(index_path)
                    print(f"[INFO] Deleted index.html at {index_path}")
                print("Server stopped.")

    def create_static_index(self, output_path: str):
        """Create a static index page for AWS Amplify hosting (no API calls, no live updates)."""
        import json

        # Find all HTML reports in the report directory
        report_configs = [
            {'filename': 'dataset_overview.html', 'title': 'Dataset Overview', 'description': 'Comprehensive statistical analysis and distribution metrics', 'category': 'Core Analytics'},
            {'filename': 'understanding.html', 'title': 'Understanding Usage & Cost', 'description': 'High-level cost and usage patterns across the platform', 'category': 'Core Analytics'},
            {'filename': 'performance.html', 'title': 'Performance Tracking', 'description': 'Latency analysis and SLA compliance monitoring', 'category': 'Core Analytics'},
            {'filename': 'profitability.html', 'title': 'Customer Profitability', 'description': 'Revenue vs cost analysis by customer segment', 'category': 'Financial & Revenue Analytics'},
            {'filename': 'pricing.html', 'title': 'Pricing Strategy', 'description': 'Pricing model effectiveness and optimization opportunities', 'category': 'Financial & Revenue Analytics'},
            {'filename': 'features.html', 'title': 'Feature Economics', 'description': 'Cost and usage analysis by product feature', 'category': 'Financial & Revenue Analytics'},
            {'filename': 'realtime.html', 'title': 'Real-Time Decision Making', 'description': 'Live monitoring and immediate cost visibility', 'category': 'Operational Insights'},
            {'filename': 'optimization.html', 'title': 'Rate Optimization', 'description': 'Model selection and cost reduction opportunities', 'category': 'Operational Insights'},
            {'filename': 'alignment.html', 'title': 'Organizational Alignment', 'description': 'Cross-team visibility and cost attribution', 'category': 'Operational Insights'},
            {'filename': 'token_economics.html', 'title': 'Token Economics & Efficiency', 'description': 'Token usage patterns and optimization metrics', 'category': 'Advanced Analytics'},
            {'filename': 'geographic_latency.html', 'title': 'Geographic & Latency Intelligence', 'description': 'Regional performance and infrastructure optimization', 'category': 'Advanced Analytics'},
            {'filename': 'churn_growth.html', 'title': 'Churn Risk & Growth Signals', 'description': 'Customer health and expansion opportunities', 'category': 'Advanced Analytics'},
            {'filename': 'abuse_detection.html', 'title': 'Abuse Detection & Security', 'description': 'Anomaly detection and usage pattern analysis', 'category': 'Advanced Analytics'}
        ]

        # Check which reports exist
        available_reports = []
        for config in report_configs:
            filepath = os.path.join(self.report_dir, config['filename'])
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                available_reports.append({
                    **config,
                    'size_kb': size_kb
                })

        # Read manifest if available
        manifest_path = os.path.join(self.report_dir, 'manifest.json')
        manifest = {}
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
            except Exception:
                pass

        generation_time = manifest.get('generated_at', 'Unknown')
        data_size_mb = manifest.get('data_size_mb', 'Unknown')
        total_calls_raw = manifest.get('total_calls') or manifest.get('call_count', 'Unknown')

        # Format total_calls with commas if it's a number
        if isinstance(total_calls_raw, (int, float)):
            total_calls = f"{int(total_calls_raw):,}"
        else:
            total_calls = total_calls_raw

        # Group reports by category
        categories = {}
        for report in available_reports:
            cat = report['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(report)

        # Build report cards HTML with proper emoji prefixes
        category_emojis = {
            'Core Analytics': '📊',
            'Financial & Revenue Analytics': '💰',
            'Operational Insights': '🚀',
            'Advanced Analytics': '🔬'
        }

        report_cards_html = ''
        for category, reports in categories.items():
            emoji = category_emojis.get(category, '📈')
            report_cards_html += f'<h3 class="category-header">{emoji} {category}</h3>\n'
            report_cards_html += '<div class="report-grid">\n'
            for report in reports:
                description = report.get('description', f'{report["size_kb"]:.1f} KB')
                report_cards_html += f'''
                <div class="report-card">
                    <div class="status-badge complete">✓ Available</div>
                    <h4>{report['title']}</h4>
                    <p>{description}</p>
                    <a href="{report['filename']}" class="view-button">View Report →</a>
                </div>
'''
            report_cards_html += '</div>\n\n'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Revenium FinOps Showcase - Analysis Reports</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.8;
        }}
        .content {{
            padding: 40px;
        }}
        .info-box {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            margin-bottom: 30px;
        }}
        .info-box h3 {{
            color: #1976d2;
            margin-bottom: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
        }}
        .info-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .info-value {{
            font-size: 20px;
            font-weight: bold;
            color: #1a1a1a;
            margin-top: 5px;
        }}
        .category-header {{
            color: #1a1a1a;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
            font-size: 20px;
        }}
        .category-header:first-of-type {{
            margin-top: 0;
        }}
        .report-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .report-card {{
            background: #f1f8f4;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
            position: relative;
        }}
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .status-badge {{
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            color: white;
            background: #4CAF50;
        }}
        .report-card h4 {{
            margin-bottom: 10px;
            color: #1a1a1a;
            padding-right: 80px;
            font-size: 16px;
        }}
        .report-card p {{
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }}
        .view-button {{
            display: inline-block;
            background: #2196f3;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
            font-size: 14px;
        }}
        .view-button:hover {{
            background: #1976d2;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
        .github-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .github-link:hover {{
            text-decoration: underline;
        }}
        /* Executive Summary Styles */
        .executive-summary {{
            display: flex;
            flex-direction: column;
            gap: 30px;
            margin: 40px 0;
        }}
        .insight-card {{
            background: white;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            overflow: hidden;
            transition: all 0.3s;
        }}
        .insight-card:hover {{
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: #667eea;
        }}
        .insight-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .insight-number {{
            background: rgba(255,255,255,0.2);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .insight-header h3 {{
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            line-height: 1.3;
        }}
        .insight-content {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 30px;
            padding: 30px;
        }}
        @media (max-width: 1024px) {{
            .insight-content {{
                grid-template-columns: 1fr;
            }}
        }}
        .insight-text {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .insight-finding {{
            padding: 16px;
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            border-radius: 4px;
            line-height: 1.6;
        }}
        .insight-detail {{
            padding: 16px;
            background: #f5f5f5;
            border-radius: 4px;
            line-height: 1.6;
        }}
        .insight-action {{
            padding: 16px;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            border-radius: 4px;
            line-height: 1.6;
        }}
        .insight-visual {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .insight-visual canvas {{
            max-width: 100%;
            max-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Revenium FinOps Showcase</h1>
            <p>AI Cost Management & Usage-Based Revenue Analysis</p>
        </div>

        <div class="content">
            <div class="info-box">
                <h3>Dataset Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Generated At</div>
                        <div class="info-value">{generation_time}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Data Size</div>
                        <div class="info-value">{data_size_mb} MB</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Total API Calls</div>
                        <div class="info-value">{total_calls}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Reports Available</div>
                        <div class="info-value">{len(available_reports)}</div>
                    </div>
                </div>
            </div>

            <h2 style="color: #1a1a1a; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #e0e0e0;">Executive Summary</h2>
            <div class="executive-summary">
                <!-- Insight 1: Starter Tier Paradox -->
                <div class="insight-card">
                    <div class="insight-header">
                        <div class="insight-number">1</div>
                        <h3>The "Starter Tier Paradox": Inverse Economics at Scale</h3>
                    </div>
                    <div class="insight-content">
                        <div class="insight-text">
                            <div class="insight-finding">
                                <strong>Key Metric:</strong> Starter tier ($29/month) operates at -264.6% margin with 418 expansion-ready customers representing $51,100 in untapped monthly revenue.
                            </div>
                            <div class="insight-detail">
                                <strong>Business Impact:</strong> Your worst-performing segment is simultaneously your highest-value expansion pipeline. 482 starter customers generating 196-222% growth rates consume $106/customer in AI costs while paying $29—a deliberate arbitrage, not accidental usage.
                            </div>
                            <div class="insight-action">
                                <strong>Recommended Action:</strong> Implement hybrid pricing: $29 base tier with ~20K token allowance, then graduated usage pricing beyond threshold. This preserves acquisition while automatically capturing value as customers scale—converting the loss center into a self-correcting revenue engine without disrupting the funnel.
                            </div>
                        </div>
                        <div class="insight-visual">
                            <canvas id="starterTierChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Insight 2: Portfolio Misallocation Crisis -->
                <div class="insight-card">
                    <div class="insight-header">
                        <div class="insight-number">2</div>
                        <h3>The Portfolio Misallocation Crisis: $400K+ in Accumulated Losses from "Power User" Subsidy</h3>
                    </div>
                    <div class="insight-content">
                        <div class="insight-text">
                            <div class="insight-finding">
                                <strong>Key Metric:</strong> 459 heavy users (92% of base) at -185% margins vs. 1 light user at 72% margin. 426 unprofitable customers losing $68K monthly ($819K annually).
                            </div>
                            <div class="insight-detail">
                                <strong>Business Impact:</strong> Customer acquisition strategy systematically attracts unprofitable profiles. Marketing positions "unlimited AI for $99/month" when unit economics require &lt;5K tokens/month usage. Current funnel selects against profitable customers.
                            </div>
                            <div class="insight-action">
                                <strong>Recommended Action:</strong> Reverse-engineer the 23 high-margin customers (&gt;50% margins)—teams using AI for bounded workflows vs. replacing job functions. Rebuild acquisition to attract 100 customers matching this profile. Prioritize margin quality over volume scale.
                            </div>
                        </div>
                        <div class="insight-visual">
                            <canvas id="portfolioChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Insight 3: Free-Tier-to-Paid Conversion Illusion -->
                <div class="insight-card">
                    <div class="insight-header">
                        <div class="insight-number">3</div>
                        <h3>The Free-Tier-to-Paid Conversion Illusion: 95% Retention on Free = 95% Revenue Leakage</h3>
                    </div>
                    <div class="insight-content">
                        <div class="insight-text">
                            <div class="insight-finding">
                                <strong>Key Metric:</strong> 50K free users at $2/user cost = $100K/month in unrecovered expenses. 95% retention on free tier with &lt;5% conversion to paid. "Advanced AI Analytics" costs $30K/month with 3% adoption ($560K annual waste).
                            </div>
                            <div class="insight-detail">
                                <strong>Business Impact:</strong> Free tier is too generous—users love the product at $0 but won't upgrade. Paid tiers bloated with 12 underutilized features justify discounting. Creates vicious cycle: generous free tier → low conversion → add unused features → worse margins → more discounting.
                            </div>
                            <div class="insight-action">
                                <strong>Recommended Action:</strong> Redesign free tier to create intentional friction (60 min/month at $0.30/user, targeting 8% conversion). Sunset 12 underutilized features. Rebuild paid tiers around the 3 high-adoption features (61% of costs, ~100% usage). Clear value prop: pay to remove limits on features you already use.
                            </div>
                        </div>
                        <div class="insight-visual">
                            <canvas id="freeTierChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            {report_cards_html}

            <div class="footer">
                <p>This is a static showcase deployment hosted on GitHub Pages</p>
                <p>For the live local version with data generation and real-time analysis, see the <a href="https://github.com/revenium/finops-showcase" class="github-link">GitHub repository</a></p>
            </div>
        </div>
    </div>
    <script>
        // Initialize Executive Summary Charts
        function initExecutiveSummaryCharts() {{
            // Chart 1: Starter Tier Paradox - Margin vs Expansion Potential
            const starterTierCtx = document.getElementById('starterTierChart');
            if (starterTierCtx) {{
                new Chart(starterTierCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Current Margin', 'AI Cost per Customer', 'Expansion Potential'],
                        datasets: [{{
                            label: 'Starter Tier Economics',
                            data: [-264.6, 106, 51100/482],
                            backgroundColor: [
                                'rgba(244, 67, 54, 0.7)',
                                'rgba(255, 152, 0, 0.7)',
                                'rgba(76, 175, 80, 0.7)'
                            ],
                            borderColor: [
                                'rgba(244, 67, 54, 1)',
                                'rgba(255, 152, 0, 1)',
                                'rgba(76, 175, 80, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            title: {{
                                display: true,
                                text: 'Starter Tier: Loss vs Expansion Value',
                                font: {{
                                    size: 16,
                                    weight: 'bold'
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        let label = context.dataset.label || '';
                                        if (label) {{
                                            label += ': ';
                                        }}
                                        if (context.dataIndex === 0) {{
                                            label += context.parsed.y + '% margin';
                                        }} else if (context.dataIndex === 1) {{
                                            label += '$' + context.parsed.y + ' per customer';
                                        }} else {{
                                            label += '$' + context.parsed.y.toFixed(0) + ' per customer';
                                        }}
                                        return label;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Value ($)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // Chart 2: Portfolio Misallocation - Customer Distribution
            const portfolioCtx = document.getElementById('portfolioChart');
            if (portfolioCtx) {{
                new Chart(portfolioCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: [
                            'Heavy Users (-185% margin)',
                            'Unprofitable Customers',
                            'High-Margin Customers',
                            'Light Users (72% margin)'
                        ],
                        datasets: [{{
                            data: [459, 426, 23, 1],
                            backgroundColor: [
                                'rgba(244, 67, 54, 0.7)',
                                'rgba(255, 152, 0, 0.7)',
                                'rgba(76, 175, 80, 0.7)',
                                'rgba(33, 150, 243, 0.7)'
                            ],
                            borderColor: [
                                'rgba(244, 67, 54, 1)',
                                'rgba(255, 152, 0, 1)',
                                'rgba(76, 175, 80, 1)',
                                'rgba(33, 150, 243, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 15,
                                    font: {{
                                        size: 11
                                    }}
                                }}
                            }},
                            title: {{
                                display: true,
                                text: 'Customer Profitability Distribution',
                                font: {{
                                    size: 16,
                                    weight: 'bold'
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        let label = context.label || '';
                                        let value = context.parsed;
                                        let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        let percentage = ((value / total) * 100).toFixed(1);
                                        return label + ': ' + value + ' customers (' + percentage + '%)';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // Chart 3: Free Tier Conversion - Retention vs Revenue
            const freeTierCtx = document.getElementById('freeTierChart');
            if (freeTierCtx) {{
                new Chart(freeTierCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Free Tier Retention', 'Conversion to Paid', 'Feature Waste', 'Cost Recovery'],
                        datasets: [{{
                            label: 'Percentage',
                            data: [95, 5, 75, 5],
                            backgroundColor: [
                                'rgba(244, 67, 54, 0.7)',
                                'rgba(255, 152, 0, 0.7)',
                                'rgba(156, 39, 176, 0.7)',
                                'rgba(76, 175, 80, 0.7)'
                            ],
                            borderColor: [
                                'rgba(244, 67, 54, 1)',
                                'rgba(255, 152, 0, 1)',
                                'rgba(156, 39, 176, 1)',
                                'rgba(76, 175, 80, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            title: {{
                                display: true,
                                text: 'Free Tier Economics',
                                font: {{
                                    size: 16,
                                    weight: 'bold'
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.label + ': ' + context.parsed.y + '%';
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: 'Percentage (%)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        // Initialize charts when DOM is ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initExecutiveSummaryCharts);
        }} else {{
            initExecutiveSummaryCharts();
        }}
    </script>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

    def create_status_page(self, output_path: str, static_mode: bool = False):
        """Create the main status/index page.

        Args:
            output_path: Path to write the HTML file
            static_mode: If True, generate a static page for hosting (no API calls, no live updates)
        """

        # If static mode, use the simplified static index
        if static_mode:
            return self.create_static_index(output_path)

        # Otherwise, generate the full dynamic page for local server
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
        /* Admin Panel - macOS Light Mode Style */
        .admin-panel {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        .admin-section {
            margin-bottom: 30px;
        }
        .admin-section:last-child {
            margin-bottom: 0;
        }
        .admin-section h3 {
            color: #1a1a1a;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .admin-controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .control-group {
            flex: 1;
            min-width: 300px;
        }
        .control-group label {
            display: block;
            color: #666;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        .input-group input[type="text"] {
            flex: 1;
            background: #ffffff;
            border: 1px solid #d0d0d0;
            color: #1a1a1a;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.2s;
        }
        .input-group input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .input-group input[type="text"]::placeholder {
            color: #999;
        }
        .csv-select {
            flex: 1;
            background: #ffffff;
            border: 1px solid #d0d0d0;
            color: #1a1a1a;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.2s;
            cursor: pointer;
        }
        .csv-select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .csv-select option {
            background: #ffffff;
            color: #1a1a1a;
            padding: 8px;
        }
        .csv-info {
            margin-top: 8px;
            font-size: 12px;
            color: #666;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }
        .csv-info.current {
            color: #28a745;
            font-weight: 600;
        }
        .btn-secondary {
            background: #f0f0f0;
            border: 1px solid #d0d0d0;
            color: #1a1a1a;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-secondary:hover {
            background: #e8e8e8;
            border-color: #667eea;
        }
        .btn-secondary:active {
            transform: scale(0.95);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:active {
            transform: translateY(0);
        }
        .btn-primary:disabled {
            background: #444;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
        .btn-action {
            flex: 1;
            min-width: 200px;
            background: #ffffff;
            border: 2px solid #d0d0d0;
            color: #1a1a1a;
            padding: 16px 24px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn-action:hover {
            background: #f8f9fa;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }
        .btn-action:active {
            transform: translateY(0);
        }
        .btn-action:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .btn-icon {
            font-size: 14px;
        }
        .status-message {
            margin-top: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            display: none;
        }
        .status-message.success {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
            display: block;
        }
        .status-message.error {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            border: 1px solid rgba(220, 53, 69, 0.3);
            display: block;
        }
        .status-message.info {
            background: rgba(0, 123, 255, 0.1);
            color: #007bff;
            border: 1px solid rgba(0, 123, 255, 0.3);
            display: block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #ffffff;
            padding: 16px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        .stat-card .stat-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .stat-card .stat-value {
            font-size: 22px;
            font-weight: bold;
            color: #1a1a1a;
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
                <h2>Admin Panel</h2>
                <div class="admin-panel">
                    <div class="admin-section">
                        <h3>Data Management</h3>
                        <div class="admin-controls">
                            <div class="control-group">
                                <label>Load CSV File</label>
                                <div class="input-group">
                                    <select id="csv-selector" class="csv-select">
                                        <option value="">Loading CSV files...</option>
                                    </select>
                                    <button onclick="refreshCSVList()" class="btn-secondary" title="Refresh CSV list">⟳</button>
                                    <button onclick="loadSelectedCSV()" class="btn-primary">Load CSV</button>
                                </div>
                                <div id="csv-info" class="csv-info"></div>
                                <div id="csv-loader-message" class="status-message"></div>
                            </div>
                        </div>
                    </div>

                    <div class="admin-section">
                        <h3>Pipeline Actions</h3>
                        <div class="admin-controls">
                            <button onclick="runSimulators()" id="run-simulators-btn" class="btn-action">
                                <span class="btn-icon">▶</span>
                                <span class="btn-label">Run Simulators</span>
                            </button>
                            <button onclick="runAllAnalyzers()" id="run-all-analyzers-btn" class="btn-action">
                                <span class="btn-icon">▶</span>
                                <span class="btn-label">Run All Analyzers</span>
                            </button>
                        </div>
                        <div id="pipeline-status" class="status-message"></div>
                    </div>

                    <div class="admin-section">
                        <h3>CSV Statistics</h3>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-label">CSV Size</div>
                                <div class="stat-value" id="csv-size">-</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Target Size</div>
                                <div class="stat-value" id="csv-target">2048 MB</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Progress</div>
                                <div class="stat-value" id="csv-progress">0%</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">Total Calls</div>
                                <div class="stat-value" id="csv-lines">-</div>
                            </div>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" id="progress-bar" style="width: 0%">
                                <span id="progress-text">0%</span>
                            </div>
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

        function populateCSVList() {
            const selector = document.getElementById('csv-selector');
            const infoDiv = document.getElementById('csv-info');

            fetch('/api/list_csv_files?_=' + Date.now())
                .then(r => r.json())
                .then(data => {
                    if (data.success && data.files.length > 0) {
                        // Clear existing options
                        selector.innerHTML = '';

                        // Add CSV files as options
                        data.files.forEach(file => {
                            const option = document.createElement('option');
                            option.value = file.filename;
                            option.textContent = `${file.filename} (${file.size_mb} MB)`;
                            if (file.is_current) {
                                option.selected = true;
                            }
                            selector.appendChild(option);
                        });

                        // Update info with selected file details
                        updateCSVInfo();
                    } else if (data.success && data.files.length === 0) {
                        selector.innerHTML = '<option value="">No CSV files found</option>';
                        infoDiv.textContent = '';
                    } else {
                        selector.innerHTML = '<option value="">Error loading CSV files</option>';
                        infoDiv.textContent = data.error || 'Unknown error';
                        infoDiv.className = 'csv-info';
                    }
                })
                .catch(e => {
                    console.error('Error listing CSV files:', e);
                    selector.innerHTML = '<option value="">Failed to load CSV files</option>';
                    infoDiv.textContent = e.message;
                    infoDiv.className = 'csv-info';
                });
        }

        function updateCSVInfo() {
            const selector = document.getElementById('csv-selector');
            const infoDiv = document.getElementById('csv-info');
            const selectedFilename = selector.value;

            if (!selectedFilename) {
                infoDiv.textContent = '';
                return;
            }

            // Fetch file details
            fetch('/api/list_csv_files?_=' + Date.now())
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        const file = data.files.find(f => f.filename === selectedFilename);
                        if (file) {
                            infoDiv.textContent = `Modified: ${file.modified_display} | Size: ${file.size_mb} MB`;
                            infoDiv.className = file.is_current ? 'csv-info current' : 'csv-info';
                        }
                    }
                })
                .catch(e => {
                    console.error('Error getting CSV info:', e);
                });
        }

        function refreshCSVList() {
            populateCSVList();
        }

        function loadSelectedCSV() {
            const selector = document.getElementById('csv-selector');
            const messageDiv = document.getElementById('csv-loader-message');
            const csvFilename = selector.value;

            if (!csvFilename) {
                messageDiv.className = 'status-message error';
                messageDiv.textContent = 'Please select a CSV file';
                return;
            }

            // Reset message
            messageDiv.className = 'status-message info';
            messageDiv.textContent = 'Loading...';

            // Send POST request to load CSV
            fetch('/api/load_csv?csv_filename=' + encodeURIComponent(csvFilename), {
                method: 'POST'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    messageDiv.className = 'status-message success';
                    messageDiv.textContent = data.message;
                    // Refresh CSV list to update current file indicator
                    populateCSVList();
                    // Trigger immediate status update
                    updateStatus();
                } else {
                    messageDiv.className = 'status-message error';
                    messageDiv.textContent = 'Error: ' + data.error;
                }
            })
            .catch(e => {
                console.error('Error loading CSV:', e);
                messageDiv.className = 'status-message error';
                messageDiv.textContent = 'Failed to load CSV: ' + e.message;
            });
        }

        function runSimulators() {
            const button = document.getElementById('run-simulators-btn');
            const messageDiv = document.getElementById('pipeline-status');

            button.disabled = true;
            button.querySelector('.btn-label').textContent = 'Running...';
            messageDiv.className = 'status-message info';
            messageDiv.textContent = 'Starting simulators...';

            fetch('/api/run_simulators', {
                method: 'POST'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    messageDiv.className = 'status-message success';
                    messageDiv.textContent = data.message;
                    // Re-enable after a delay
                    setTimeout(() => {
                        button.disabled = false;
                        button.querySelector('.btn-label').textContent = 'Run Simulators';
                    }, 3000);
                } else {
                    messageDiv.className = 'status-message error';
                    messageDiv.textContent = 'Error: ' + data.error;
                    button.disabled = false;
                    button.querySelector('.btn-label').textContent = 'Run Simulators';
                }
            })
            .catch(e => {
                console.error('Error running simulators:', e);
                messageDiv.className = 'status-message error';
                messageDiv.textContent = 'Failed to start simulators: ' + e.message;
                button.disabled = false;
                button.querySelector('.btn-label').textContent = 'Run Simulators';
            });
        }

        function runAllAnalyzers() {
            const button = document.getElementById('run-all-analyzers-btn');
            const messageDiv = document.getElementById('pipeline-status');

            button.disabled = true;
            button.querySelector('.btn-label').textContent = 'Running...';
            messageDiv.className = 'status-message info';
            messageDiv.textContent = 'Starting all analyzers...';

            fetch('/api/run_all_analyzers', {
                method: 'POST'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    messageDiv.className = 'status-message success';
                    messageDiv.textContent = data.message;
                    // Re-enable after a delay
                    setTimeout(() => {
                        button.disabled = false;
                        button.querySelector('.btn-label').textContent = 'Run All Analyzers';
                    }, 3000);
                } else {
                    messageDiv.className = 'status-message error';
                    messageDiv.textContent = 'Error: ' + data.error;
                    button.disabled = false;
                    button.querySelector('.btn-label').textContent = 'Run All Analyzers';
                }
            })
            .catch(e => {
                console.error('Error running analyzers:', e);
                messageDiv.className = 'status-message error';
                messageDiv.textContent = 'Failed to start analyzers: ' + e.message;
                button.disabled = false;
                button.querySelector('.btn-label').textContent = 'Run All Analyzers';
            });
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

                    // Update pipeline status based on simulator/analyzer progress
                    const pipelineMessage = document.getElementById('pipeline-status');
                    const simulatorBtn = document.getElementById('run-simulators-btn');
                    const analyzerBtn = document.getElementById('run-all-analyzers-btn');

                    // Handle simulator status
                    if (data.simulator_status && data.simulator_status.status === 'running') {
                        pipelineMessage.className = 'status-message info';
                        pipelineMessage.textContent = data.simulator_status.message;
                        simulatorBtn.disabled = true;
                        simulatorBtn.querySelector('.btn-label').textContent = 'Running...';
                    } else if (data.simulator_status && data.simulator_status.status === 'complete') {
                        pipelineMessage.className = 'status-message success';
                        pipelineMessage.textContent = data.simulator_status.message;
                        simulatorBtn.disabled = false;
                        simulatorBtn.querySelector('.btn-label').textContent = 'Run Simulators';
                    } else if (data.simulator_status && data.simulator_status.status === 'error') {
                        pipelineMessage.className = 'status-message error';
                        pipelineMessage.textContent = data.simulator_status.message;
                        simulatorBtn.disabled = false;
                        simulatorBtn.querySelector('.btn-label').textContent = 'Run Simulators';
                    }

                    // Handle all analyzers status
                    if (data.all_analyzers_status && data.all_analyzers_status.status === 'running') {
                        pipelineMessage.className = 'status-message info';
                        const progress = `${data.all_analyzers_status.completed}/${data.all_analyzers_status.total}`;
                        const current = data.all_analyzers_status.current ? ` - ${data.all_analyzers_status.current}` : '';
                        pipelineMessage.textContent = `Running analyzers (${progress})${current}`;
                        analyzerBtn.disabled = true;
                        analyzerBtn.querySelector('.btn-label').textContent = 'Running...';
                    } else if (data.all_analyzers_status && data.all_analyzers_status.status === 'complete') {
                        pipelineMessage.className = 'status-message success';
                        pipelineMessage.textContent = data.all_analyzers_status.message;
                        analyzerBtn.disabled = false;
                        analyzerBtn.querySelector('.btn-label').textContent = 'Run All Analyzers';
                    } else if (data.all_analyzers_status && data.all_analyzers_status.status === 'error') {
                        pipelineMessage.className = 'status-message error';
                        pipelineMessage.textContent = data.all_analyzers_status.message;
                        analyzerBtn.disabled = false;
                        analyzerBtn.querySelector('.btn-label').textContent = 'Run All Analyzers';
                    }

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

        // Add change listener to CSV selector
        document.getElementById('csv-selector').addEventListener('change', updateCSVInfo);

        // Initialize CSV dropdown
        populateCSVList();

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
