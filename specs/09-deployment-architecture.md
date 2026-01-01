# Specification 09: Deployment Architecture

**Version:** 1.0
**Last Updated:** 2026-01-01

## Overview

Two deployment modes: local HTTP server with live updates, and AWS Amplify static hosting with pre-generated reports.

---

## Local Development

**Server:** Python `http.server` + `socketserver` (viewer/serve.py)
**Port:** 8000 (configurable)
**Index:** Dynamic HTML with JavaScript API polling (1s interval)

**Endpoints:**
- `GET /api/status` - CSV progress, report status
- `POST /api/run_simulators` - Background data generation
- `POST /api/run_all_analyzers` - Background analysis execution
- `POST /api/run_analyzer?analyzer_id=<id>` - Single analyzer
- `POST /api/load_csv?csv_filename=<name>` - Switch CSV file
- `GET /api/list_csv_files` - List available CSVs

**Features:**
- Real-time progress monitoring
- On-demand analyzer execution
- CSV file management
- Background threading for long operations

**Startup:**
```bash
cd viewer && python3 serve.py
```

---

## AWS Amplify Static Hosting

**Build Process (amplify.yml):**

```yaml
version: 1
frontend:
  phases:
    build:
      - cd src
      - python3 run_all_simulators.py 2048  # Generate 2GB CSV
      - python3 run_all_analyzers.py        # Run all 13 analyzers
      - cd ..
      - python3 -c "..."                     # Generate static index.html
  artifacts:
    baseDirectory: reports/html
    files: '**/*'
  cache:
    paths:
      - src/data/simulated_calls.csv
```

**Static Index Generation:**

Method: `StatusViewerServer.create_static_index(output_path)`

**Implementation:**
1. Scan `reports/html/` for existing HTML files
2. Match to 13 report configurations with categories
3. Read `manifest.json` for metadata (timestamp, size, call count)
4. Group by category: FinOps, Usage-Based Revenue, Advanced Analytics
5. Generate HTML with embedded CSS, no JavaScript
6. Direct `<a href>` links to report files

**Output Structure:**
```
reports/html/
├── index.html                          (static navigation)
├── understanding_cost_usage.html
├── performance_tracking.html
├── realtime_decision_making.html
├── optimization_opportunities.html
├── organizational_alignment.html
├── customer_profitability.html
├── pricing_strategy.html
├── feature_economics.html
├── dataset_overview.html
├── token_economics.html
├── geographic_latency.html
├── churn_growth.html
├── abuse_detection.html
└── manifest.json
```

**Deployment:**
- Push to GitHub → Amplify auto-builds → Deploys to CloudFront
- Build time: ~15-20 minutes (2GB CSV generation + analysis)
- CSV cached between builds (via `cache.paths`)

**Key Differences from Local:**

| Feature | Local | Amplify |
|---------|-------|---------|
| Index page | Dynamic (API calls) | Static (direct links) |
| Data generation | On-demand | Build-time only |
| Analyzers | On-demand | Build-time only |
| CSV management | Runtime switching | Static 2GB |
| Updates | Live polling | Rebuild required |

---

## Static Index HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>/* Inline CSS */</style>
</head>
<body>
  <div class="container">
    <header>Revenium FinOps Showcase</header>

    <section class="info-box">
      <!-- Dataset metadata from manifest.json -->
      Generated At: {timestamp}
      Data Size: {size_mb} MB
      Total Calls: {count}
      Reports: {report_count}
    </section>

    <section>
      <h3>FinOps</h3>
      <div class="report-grid">
        <a href="understanding_cost_usage.html">...</a>
        <a href="performance_tracking.html">...</a>
        ...
      </div>
    </section>

    <section>
      <h3>Usage-Based Revenue</h3>
      ...
    </section>

    <section>
      <h3>Advanced Analytics</h3>
      ...
    </section>
  </div>
</body>
</html>
```

**No JavaScript:** All links are static `<a href>` elements.

---

## Report Compatibility

All 13 HTML reports are static-compatible:
- Data embedded in JavaScript variables
- Chart.js via CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0`
- No backend API calls
- Self-contained CSS

No generator modifications required.

---

## Implementation Details

### Static Mode Flag

```python
def create_status_page(self, output_path: str, static_mode: bool = False):
    if static_mode:
        return self.create_static_index(output_path)
    # Otherwise: dynamic page with API calls
```

### Report Discovery

```python
report_configs = [
    {'filename': 'understanding_cost_usage.html', 'title': '...', 'category': 'FinOps'},
    {'filename': 'performance_tracking.html', 'title': '...', 'category': 'FinOps'},
    # ... 11 more
]

available_reports = []
for config in report_configs:
    if os.path.exists(os.path.join(report_dir, config['filename'])):
        available_reports.append({**config, 'size_kb': ...})
```

### Manifest Reading

```python
manifest = {}
if os.path.exists('reports/html/manifest.json'):
    with open(...) as f:
        manifest = json.load(f)

generation_time = manifest.get('generated_at', 'Unknown')
data_size_mb = manifest.get('data_size_mb', 'Unknown')
total_calls = manifest.get('total_calls', 'Unknown')
```

---

## Performance

### Local
- Server startup: <1s
- API response: 10-50ms
- Status polling: 1s interval
- Memory: 50-500MB (depends on CSV size)

### Amplify
- Build: 15-20 minutes (2GB dataset)
- CloudFront response: 10-200ms (cached)
- Static index: ~10KB
- Total artifacts: ~2-5MB

---

## File Exclusions (.gitignore)

```
# Generated data
src/data/*.csv

# Generated reports (built on Amplify)
reports/html/*.html
reports/html/manifest.json

# Preserve structure
!reports/html/.gitkeep
```

---

**End of Specification**
