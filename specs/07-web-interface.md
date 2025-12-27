# Web Interface Specification

## HTTP Server

### Server Initialization

```
function initialize_server(csv_path, report_dir, port):
    server = StatusViewerServer(csv_path, report_dir, port)
    server.start()
```

### Server Configuration

```
class StatusViewerServer:
    csv_path: Path to CSV file for monitoring
    report_dir: Directory containing HTML reports
    port: HTTP server port (default: 8000)
    target_size_mb: Target data size for progress tracking (from config)
    analyzer_status: Dictionary tracking running analyzers
    status_lock: Thread-safe lock for status updates
```

### Request Routing

```
function handle_request(path, query_params):
    if path == "/":
        return serve_index_page()

    elif path == "/api/status":
        return serve_status_json()

    elif path == "/api/run-analyzer":
        analyzer_id = query_params.get("id")
        return run_analyzer_async(analyzer_id)

    elif path.endswith(".html"):
        return serve_html_file(path)

    elif path.endswith(".json"):
        return serve_json_file(path)

    else:
        return 404_not_found()
```

## Status API

### Status JSON Structure

```
function get_status_json():
    csv_size_mb = get_csv_size_mb()

    return {
        "timestamp": current_timestamp(),
        "csv": {
            "size_mb": round(csv_size_mb, 2),
            "target_mb": TARGET_SIZE_MB,
            "progress_pct": min((csv_size_mb / TARGET_SIZE_MB) * 100, 100),
            "line_count": get_csv_line_count(),
            "complete": csv_size_mb >= TARGET_SIZE_MB
        },
        "reports": check_report_status(),
        "analyzer_status": get_analyzer_status()
    }
```

### Report Status Check

```
function check_report_status():
    reports = {
        "understanding.html": "Understanding Usage & Cost",
        "performance.html": "Performance Tracking",
        "realtime.html": "Real-Time Decision Making",
        "optimization.html": "Rate Optimization",
        "alignment.html": "Organizational Alignment",
        "profitability.html": "Customer Profitability",
        "pricing.html": "Pricing Strategy",
        "features.html": "Feature Economics",
        "dataset_overview.html": "Dataset Overview",
        "token_economics.html": "Token Economics",
        "geographic_latency.html": "Geographic Latency",
        "churn_growth.html": "Churn & Growth",
        "abuse_detection.html": "Abuse Detection"
    }

    status = {}
    for filename, name in reports.items():
        filepath = join(report_dir, filename)
        status[filename] = {
            "name": name,
            "exists": file_exists(filepath),
            "size_kb": get_file_size_kb(filepath) if file_exists(filepath) else 0
        }

    return status
```

### CSV Metrics

```
function get_csv_size_mb():
    if not file_exists(csv_path):
        return 0.0
    return get_file_size(csv_path) / (1024 * 1024)

function get_csv_line_count():
    if not file_exists(csv_path):
        return 0
    return count_lines(csv_path) - 1  # Exclude header
```

## Background Monitoring

### Monitor Thread

```
function start_background_monitor():
    monitor_thread = Thread(target=monitor_and_regenerate)
    monitor_thread.daemon = True
    monitor_thread.start()
```

### Monitoring Loop

```
function monitor_and_regenerate():
    last_size = 0
    last_regeneration = current_time()

    while true:
        sleep(10)  # Check every 10 seconds

        current_size = get_csv_size_mb()

        # Regenerate if significant growth
        if current_size > last_size + 5:  # 5MB threshold
            time_since_last = current_time() - last_regeneration

            if time_since_last > 30:  # At least 30 seconds between regenerations
                print(f"Dataset grew to {current_size:.2f} MB, regenerating reports...")
                regenerate_all_reports()
                last_regeneration = current_time()

            last_size = current_size
```

### Report Regeneration

```
function regenerate_all_reports():
    try:
        # Run all analyzers
        execute("python src/run_all_analyzers.py")
        print("Reports regenerated successfully")
    except Exception as e:
        print(f"Error regenerating reports: {e}")
```

## Analyzer Execution API

### Run Analyzer Endpoint

```
function run_analyzer_async(analyzer_id):
    if analyzer_id not in ANALYZER_REGISTRY:
        return {
            "success": false,
            "error": "Unknown analyzer ID"
        }

    # Check if already running
    with status_lock:
        if analyzer_id in analyzer_status and analyzer_status[analyzer_id]["status"] == "running":
            return {
                "success": false,
                "error": "Analyzer already running"
            }

        # Mark as running
        analyzer_status[analyzer_id] = {
            "status": "running",
            "started_at": current_timestamp()
        }

    # Run in background thread
    thread = Thread(target=execute_analyzer, args=(analyzer_id,))
    thread.daemon = True
    thread.start()

    return {
        "success": true,
        "message": f"Analyzer {analyzer_id} started"
    }
```

### Analyzer Execution

```
function execute_analyzer(analyzer_id):
    timeout = 300  # 5 minutes

    try:
        result = run_command_with_timeout(
            f"python src/run_analyzer.py {analyzer_id}",
            timeout=timeout
        )

        with status_lock:
            analyzer_status[analyzer_id] = {
                "status": "complete",
                "completed_at": current_timestamp(),
                "success": result.success
            }

    except TimeoutError:
        with status_lock:
            analyzer_status[analyzer_id] = {
                "status": "timeout",
                "completed_at": current_timestamp(),
                "success": false
            }

    except Exception as e:
        with status_lock:
            analyzer_status[analyzer_id] = {
                "status": "error",
                "completed_at": current_timestamp(),
                "error": str(e),
                "success": false
            }
```

### Get Analyzer Status

```
function get_analyzer_status():
    with status_lock:
        return copy(analyzer_status)
```

## File Serving

### Static HTML Files

```
function serve_html_file(path):
    filepath = join(report_dir, path)

    if not file_exists(filepath):
        return {
            "status": 404,
            "body": "Report not found"
        }

    content = read_file(filepath)
    return {
        "status": 200,
        "headers": {"Content-Type": "text/html"},
        "body": content
    }
```

### JSON Files

```
function serve_json_file(path):
    filepath = join(report_dir, path)

    if not file_exists(filepath):
        return {
            "status": 404,
            "body": json.dumps({"error": "File not found"})
        }

    content = read_file(filepath)
    return {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": content
    }
```

## Client-Side Status Polling

### JavaScript Polling

```
function poll_status():
    setInterval(async function() {
        try:
            response = await fetch("/api/status")
            data = await response.json()

            update_progress_bar(data.csv)
            update_report_list(data.reports)
            update_analyzer_status(data.analyzer_status)

        except error:
            console.error("Failed to fetch status:", error)

    }, 15000)  # Poll every 15 seconds
```

### Progress Bar Update

```
function update_progress_bar(csv_data):
    progress_bar = document.getElementById("progress-bar")
    progress_text = document.getElementById("progress-text")

    progress_percent = csv_data.progress_pct
    progress_bar.style.width = `${progress_percent}%`

    progress_text.textContent = `${csv_data.size_mb} MB / ${csv_data.target_mb} MB (${progress_percent.toFixed(1)}%)`

    if csv_data.complete:
        progress_bar.classList.add("complete")
```

### Report List Update

```
function update_report_list(reports):
    for filename, report_data in reports.items():
        report_element = document.getElementById(`report-${filename}`)

        if report_data.exists:
            report_element.classList.add("available")
            report_element.querySelector(".size").textContent = `${report_data.size_kb.toFixed(1)} KB`
        else:
            report_element.classList.remove("available")
```

## Error Handling

### Server Errors

```
function handle_server_error(error):
    log_error(error)

    return {
        "status": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "error": "Internal server error",
            "message": str(error)
        })
    }
```

### Network Errors

```
function handle_network_error(error):
    # Graceful degradation
    if error.type == "connection_reset":
        print("Client connection reset, continuing...")
        return

    if error.type == "broken_pipe":
        print("Broken pipe, continuing...")
        return

    # Log other errors
    log_error(error)
```

## Server Lifecycle

### Start Server

```
function start():
    print(f"Starting viewer server on port {port}...")
    print(f"Monitoring: {csv_path}")
    print(f"Serving reports from: {report_dir}")

    # Start background monitor
    start_background_monitor()

    # Start HTTP server
    httpd = socketserver.TCPServer(("", port), request_handler)
    print(f"Server ready at http://localhost:{port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
```

### Graceful Shutdown

```
function shutdown():
    # Stop accepting new requests
    httpd.shutdown()

    # Wait for running analyzers to complete (with timeout)
    wait_for_analyzers(timeout=30)

    # Cleanup
    print("Server stopped")
```

## Security Considerations

### Local-Only Access

- Server binds to localhost (127.0.0.1) only
- No external network access
- No authentication required (demo system)

### Input Validation

```
function validate_analyzer_id(analyzer_id):
    # Whitelist validation
    if analyzer_id not in ANALYZER_REGISTRY:
        return false

    # No special characters
    if not is_alphanumeric_with_underscore(analyzer_id):
        return false

    return true
```

### File Path Validation

```
function validate_file_path(path):
    # Prevent directory traversal
    if ".." in path:
        return false

    # Whitelist extensions
    allowed_extensions = [".html", ".json"]
    if not any(path.endswith(ext) for ext in allowed_extensions):
        return false

    return true
```

## Performance Optimization

### Caching

```
# Cache report status for short duration
report_status_cache = {
    "data": null,
    "timestamp": 0,
    "ttl": 5  # 5 seconds
}

function get_cached_report_status():
    now = current_time()

    if (now - report_status_cache["timestamp"]) < report_status_cache["ttl"]:
        return report_status_cache["data"]

    # Cache miss, regenerate
    status = check_report_status()
    report_status_cache["data"] = status
    report_status_cache["timestamp"] = now

    return status
```

### Concurrent Request Handling

- Use threaded HTTP server
- Non-blocking analyzer execution
- Thread-safe status updates with locks

### Resource Limits

- Maximum 5 concurrent analyzer executions
- 5-minute timeout per analyzer
- Request queue size: 100
