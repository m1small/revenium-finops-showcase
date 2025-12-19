# HTML Reports Guide

## Overview

The Revenium FinOps Showcase now generates beautiful HTML reports alongside the traditional Markdown reports. The HTML reports feature a modern, clean design with interactive navigation through a web-based viewer.

## Features

- **Modern Design**: Clean, professional styling with system fonts and white background
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Viewer**: Web-based navigation between all reports
- **Print-Friendly**: Optimized styles for printing reports
- **No Dependencies**: All CSS and JavaScript embedded, no external libraries needed

## Quick Start

### 1. Generate Reports

```bash
cd src
python3 simulator.py              # Generate simulated data
python3 run_all_analyzers.py     # Generate both MD and HTML reports
```

This will create:
- Markdown reports in `reports/`
- HTML reports in `src/reports/html/`
- Manifest file at `src/reports/html/manifest.json`

### 2. View HTML Reports

```bash
cd viewer
python3 serve.py
```

Then open your browser to: **http://localhost:8000/**

## File Structure

```
revenium-flow/
├── src/
│   ├── utils/
│   │   ├── html_generator.py       # HTML generation utility
│   │   └── manifest_generator.py   # Manifest creation utility
│   ├── reports/
│   │   └── html/
│   │       ├── manifest.json
│   │       ├── finops_understanding.html
│   │       ├── finops_performance.html
│   │       ├── finops_realtime.html
│   │       ├── finops_optimization.html
│   │       ├── finops_alignment.html
│   │       ├── customer_profitability.html
│   │       ├── pricing_strategy.html
│   │       └── feature_economics.html
│   └── analyzers/
│       └── [analyzer files with HTML generation]
└── viewer/
    ├── index.html                  # Report viewer frontend
    └── serve.py                    # Simple HTTP server
```

## HTML Report Components

### HTMLReportGenerator Class

Located in `src/utils/html_generator.py`, this utility provides methods for creating styled HTML reports:

```python
from utils.html_generator import HTMLReportGenerator

# Create generator
generator = HTMLReportGenerator(
    title="My Report",
    description="Report description",
    category="FinOps"
)

# Add sections
generator.add_section("Executive Summary", level=2)

# Add metric cards
generator.add_metric_cards([
    {"label": "Total Spend", "value": "$8,669.89"},
    {"label": "Total Calls", "value": "224,072"}
])

# Add tables
generator.add_table(
    headers=["Column 1", "Column 2"],
    rows=[["Data 1", "Data 2"]]
)

# Add alerts
generator.add_alert("Important message", alert_type='warning')

# Save report
generator.save("output.html")
```

### Available Methods

- `add_section(title, level)` - Add section headers (h2, h3, h4)
- `add_paragraph(text)` - Add paragraph text
- `add_metric_cards(metrics)` - Add grid of metric cards
- `add_table(headers, rows, caption)` - Add data tables
- `add_alert(message, type)` - Add alert boxes (info, warning, success, danger)
- `add_list(items, ordered)` - Add bullet or numbered lists
- `add_html(html)` - Add raw HTML content
- `generate()` - Generate complete HTML string
- `save(filepath)` - Save HTML to file

## Viewer Features

### Navigation

- **Sidebar**: Browse reports by category (FinOps Domains, Usage-Based Revenue)
- **Active State**: Current report highlighted in navigation
- **URL Hash**: Reports bookmarkable via URL hash (e.g., `#finops-understanding`)
- **Mobile Menu**: Responsive hamburger menu for mobile devices

### Report Display

- **Embedded Content**: Reports displayed inline for fast loading
- **Fallback**: iframe fallback if content extraction fails
- **Responsive**: Adapts to screen size
- **Print Support**: Clean print layout

## Customization

### Styling

Edit the CSS in `src/utils/html_generator.py` to customize:

- Colors and fonts
- Layout and spacing
- Table styles
- Card designs
- Alert box styles

### Viewer

Edit `viewer/index.html` to customize:

- Navigation layout
- Color scheme
- Branding
- Additional features

## Adding HTML Generation to Analyzers

To add HTML generation to an analyzer:

1. Import the HTML generator:
```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
```

2. Add HTML generation method:
```python
def generate_html_report(self, output_file='reports/html/my_report.html'):
    from utils.html_generator import HTMLReportGenerator
    
    generator = HTMLReportGenerator(
        title="My Report Title",
        description="Report description",
        category="Category"
    )
    
    # Add content using generator methods
    generator.add_section("Section Title", level=2)
    # ... more content
    
    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    generator.save(output_file)
    print(f"✓ HTML report generated: {output_file}")
```

3. Update main() function:
```python
def main():
    os.makedirs('reports/html', exist_ok=True)
    analyzer = MyAnalyzer()
    
    # Generate markdown
    analyzer.generate_report()
    
    # Generate HTML if requested
    if os.environ.get('GENERATE_HTML'):
        analyzer.generate_html_report()
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, edit `viewer/serve.py` and change the PORT variable:

```python
PORT = 8080  # or any available port
```

### Reports Not Found

Ensure you've run the analyzers from the `src` directory:

```bash
cd src
python3 run_all_analyzers.py
```

### CORS Issues

If viewing reports directly (not via serve.py), you may encounter CORS issues. Always use the HTTP server:

```bash
cd viewer
python3 serve.py
```

### Missing Manifest

If the manifest is missing, generate it manually:

```bash
cd src
python3 -c "from utils.manifest_generator import create_default_manifest; m = create_default_manifest(); m.save()"
```

## Browser Compatibility

The HTML reports and viewer work in all modern browsers:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **Fast Loading**: Embedded CSS/JS, no external dependencies
- **Small File Size**: HTML reports typically 10-20KB each
- **Instant Navigation**: Client-side routing for quick report switching
- **Responsive**: Smooth performance on all devices

## Future Enhancements

Potential improvements for future versions:

1. **Interactive Charts**: Add Chart.js for dynamic visualizations
2. **Dark Mode**: Toggle between light/dark themes
3. **Export to PDF**: Server-side PDF generation
4. **Search**: Full-text search across all reports
5. **Filters**: Dynamic data filtering
6. **Comparison**: Side-by-side report comparison
7. **Real-time Updates**: WebSocket support for live data

## Support

For issues or questions:

1. Check this guide
2. Review the specification: `specs/html-reports-spec.md`
3. Examine example implementation: `src/analyzers/finops/understanding.py`
4. Check the HTML generator source: `src/utils/html_generator.py`
