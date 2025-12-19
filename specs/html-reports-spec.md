# HTML Reports & Viewer Specification

## Overview

Extend the Revenium FinOps Showcase to generate HTML reports instead of Markdown, with a simple web-based viewer frontend for easy navigation and viewing.

---

## Design Requirements

### Visual Style
- **Simple, Modern Design**
- **System Font Stack**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **White Background**: Clean, professional appearance
- **Minimal Color Palette**: 
  - Primary: `#2563eb` (blue)
  - Success: `#16a34a` (green)
  - Warning: `#ea580c` (orange)
  - Danger: `#dc2626` (red)
  - Text: `#1f2937` (dark gray)
  - Secondary Text: `#6b7280` (medium gray)
  - Border: `#e5e7eb` (light gray)

---

## Components to Build

### 1. HTML Report Generator Module

**File**: `src/utils/html_generator.py`

**Purpose**: Utility class to generate HTML reports with consistent styling

**Features**:
- Generate complete HTML documents with embedded CSS
- Support for common report elements:
  - Headers and sections
  - Tables with sorting capability
  - Metrics cards/tiles
  - Charts (text-based or simple SVG)
  - Alert boxes (info, warning, error, success)
  - Lists and hierarchies
- Responsive design (mobile-friendly)
- Print-friendly styles

**Key Methods**:
```python
class HTMLReportGenerator:
    def __init__(self, title: str, description: str)
    def add_section(self, title: str, level: int = 2)
    def add_metric_card(self, label: str, value: str, trend: str = None)
    def add_table(self, headers: List[str], rows: List[List], sortable: bool = True)
    def add_alert(self, message: str, type: str = 'info')
    def add_chart(self, data: Dict, chart_type: str = 'bar')
    def generate(self) -> str
    def save(self, filepath: str)
```

### 2. Update Analyzers to Generate HTML

**Modify**: All 8 analyzer files

**Changes**:
- Import `HTMLReportGenerator`
- Replace markdown generation with HTML generation
- Maintain same data analysis logic
- Output to `reports/html/` directory
- Keep markdown generation as fallback option (via flag)

**Example Structure**:
```python
def generate_report(self, output_file: str = 'reports/html/finops_understanding.html'):
    generator = HTMLReportGenerator(
        title="FinOps: Understanding Usage & Cost",
        description="Cost allocation, spend breakdowns, and forecasting analysis"
    )
    
    # Add executive summary
    generator.add_section("Executive Summary", level=2)
    generator.add_metric_card("Total AI Spend", f"${total_spend:,.2f}")
    # ... more content
    
    generator.save(output_file)
```

### 3. Report Viewer Frontend

**File**: `viewer/index.html`

**Purpose**: Single-page application to view all reports

**Features**:
- Navigation sidebar with report categories
  - FinOps Domain Reports (5)
  - Usage-Based Revenue Reports (3)
- Main content area displaying selected report
- Report metadata (generated date, summary stats)
- Search/filter functionality
- Export options (print, PDF)
- Responsive layout

**Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Revenium FinOps Reports</title>
    <style>/* Embedded CSS */</style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <header>
                <h1>Revenium FinOps</h1>
                <p>Analysis Reports</p>
            </header>
            <nav>
                <section>
                    <h3>FinOps Domains</h3>
                    <ul id="finops-reports"></ul>
                </section>
                <section>
                    <h3>Usage-Based Revenue</h3>
                    <ul id="ubr-reports"></ul>
                </section>
            </nav>
        </aside>
        <main class="content">
            <div id="report-container"></div>
        </main>
    </div>
    <script>/* Embedded JavaScript */</script>
</body>
</html>
```

**JavaScript Functionality**:
- Load report list from `reports/html/manifest.json`
- Handle navigation clicks
- Fetch and display report content
- Implement search/filter
- Handle responsive menu toggle

### 4. Report Manifest Generator

**File**: `src/utils/manifest_generator.py`

**Purpose**: Generate manifest file listing all available reports

**Output**: `reports/html/manifest.json`

**Structure**:
```json
{
  "generated": "2025-12-19T06:15:00Z",
  "reports": [
    {
      "id": "finops-understanding",
      "category": "finops",
      "title": "Understanding Usage & Cost",
      "description": "Cost allocation and forecasting",
      "file": "finops_understanding.html",
      "generated": "2025-12-19T06:15:00Z",
      "metrics": {
        "total_spend": 8669.89,
        "total_calls": 224072
      }
    }
  ]
}
```

### 5. Simple HTTP Server Script

**File**: `viewer/serve.py`

**Purpose**: Launch local web server to view reports

**Implementation**:
```python
#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        httpd.serve_forever()
```

---

## File Structure

```
revenium-flow/
├── src/
│   ├── simulator.py
│   ├── run_all_analyzers.py
│   ├── utils/
│   │   ├── html_generator.py       # NEW
│   │   └── manifest_generator.py   # NEW
│   ├── analyzers/
│   │   ├── finops/
│   │   │   ├── understanding.py    # MODIFIED
│   │   │   ├── performance.py      # MODIFIED
│   │   │   ├── realtime.py         # MODIFIED
│   │   │   ├── optimization.py     # MODIFIED
│   │   │   └── alignment.py        # MODIFIED
│   │   └── ubr/
│   │       ├── profitability.py    # MODIFIED
│   │       ├── pricing.py          # MODIFIED
│   │       └── features.py         # MODIFIED
│   └── data/
│       └── simulated_calls.csv
├── reports/
│   ├── html/                        # NEW
│   │   ├── manifest.json           # NEW
│   │   ├── finops_understanding.html
│   │   ├── finops_performance.html
│   │   ├── finops_realtime.html
│   │   ├── finops_optimization.html
│   │   ├── finops_alignment.html
│   │   ├── customer_profitability.html
│   │   ├── pricing_strategy.html
│   │   └── feature_economics.html
│   └── [existing markdown files]
├── viewer/                          # NEW
│   ├── index.html                  # NEW
│   └── serve.py                    # NEW
└── specs/
    ├── project-spec.md
    └── html-reports-spec.md        # THIS FILE
```

---

## HTML Report Template Structure

### Base Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title} - Revenium FinOps</title>
    <style>
        /* CSS embedded here */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #ffffff;
            color: #1f2937;
            line-height: 1.6;
            padding: 2rem;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .report-header {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }
        
        h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .report-meta {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #1f2937;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .metric-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.25rem;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 1.75rem;
            font-weight: 600;
            color: #1f2937;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }
        
        th {
            background: #f9fafb;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
        }
        
        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr:hover {
            background: #f9fafb;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        
        .alert-info {
            background: #eff6ff;
            border-color: #2563eb;
            color: #1e40af;
        }
        
        .alert-warning {
            background: #fff7ed;
            border-color: #ea580c;
            color: #c2410c;
        }
        
        .alert-success {
            background: #f0fdf4;
            border-color: #16a34a;
            color: #15803d;
        }
        
        .alert-danger {
            background: #fef2f2;
            border-color: #dc2626;
            color: #b91c1c;
        }
        
        @media print {
            body {
                padding: 0;
            }
            .no-print {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="report-container">
        <header class="report-header">
            <h1>{report_title}</h1>
            <div class="report-meta">
                Generated: {generated_date} | Category: {category}
            </div>
        </header>
        
        <main>
            {report_content}
        </main>
    </div>
</body>
</html>
```

---

## Usage Flow

### 1. Generate Reports

```bash
cd src
python simulator.py              # Generate data
python run_all_analyzers.py     # Generate HTML reports
```

### 2. View Reports

```bash
cd viewer
python serve.py                  # Start web server
# Open browser to http://localhost:8000/
```

### 3. Alternative: Direct File Access

Open `viewer/index.html` directly in browser (may have CORS limitations)

---

## Implementation Priority

### Phase 1: Core HTML Generation
1. Create `HTMLReportGenerator` class
2. Update one analyzer (e.g., `understanding.py`) as proof of concept
3. Test HTML output quality

### Phase 2: Complete Analyzer Updates
4. Update remaining 7 analyzers
5. Create manifest generator
6. Test all reports

### Phase 3: Viewer Frontend
7. Create viewer HTML/CSS/JS
8. Implement navigation and report loading
9. Add search/filter functionality
10. Create simple HTTP server

### Phase 4: Polish
11. Add responsive design
12. Implement print styles
13. Add export options
14. Documentation updates

---

## Success Criteria

- [ ] All 8 reports generate valid HTML
- [ ] Reports display correctly in modern browsers
- [ ] Viewer provides easy navigation between reports
- [ ] Design is clean, modern, and professional
- [ ] Reports are print-friendly
- [ ] Mobile responsive (works on tablets/phones)
- [ ] No external dependencies (embedded CSS/JS)
- [ ] Fast load times (<1s per report)

---

## Future Enhancements

1. **Interactive Charts**: Add Chart.js or similar for dynamic visualizations
2. **Dark Mode**: Toggle between light/dark themes
3. **Export to PDF**: Server-side PDF generation
4. **Real-time Updates**: WebSocket support for live data
5. **Comparison View**: Side-by-side report comparison
6. **Custom Filters**: User-defined data filtering
7. **Bookmarks**: Save favorite reports/sections
8. **Sharing**: Generate shareable links with specific views
