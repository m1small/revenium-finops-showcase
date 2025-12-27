# Report Generation Specification

## HTML Template System

### Base Template Structure

```
function build_html_template(title, content, scripts):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            {get_base_styles()}
        </style>
    </head>
    <body>
        <div class="container">
            {content}
            <div class="timestamp">
                Generated: {current_timestamp()} |
                <a href="index.html">View All Reports</a>
            </div>
        </div>
        {scripts}
    </body>
    </html>
    """
```

### Base CSS Styles

```
function get_base_styles():
    return """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        margin: 0;
        padding: 20px;
        background: #f5f5f5;
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        background: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    h1 {
        color: #1a1a1a;
        margin-top: 0;
        font-size: 32px;
    }

    h2 {
        color: #333;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 10px;
        margin-top: 40px;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .metric-label {
        font-size: 13px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin-top: 8px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
    }

    th {
        background: #f8f9fa;
        padding: 14px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #e0e0e0;
        font-size: 13px;
        text-transform: uppercase;
        color: #666;
        letter-spacing: 0.5px;
    }

    td {
        padding: 14px;
        border-bottom: 1px solid #e0e0e0;
    }

    tr:hover {
        background: #f8f9fa;
    }

    .chart-container {
        position: relative;
        height: 350px;
        margin: 30px 0;
    }

    .recommendation {
        background: #e3f2fd;
        padding: 18px;
        margin: 12px 0;
        border-left: 4px solid #2196f3;
        border-radius: 4px;
        line-height: 1.6;
    }

    .alert {
        padding: 16px 20px;
        margin: 12px 0;
        border-radius: 6px;
        border-left: 4px solid;
        display: flex;
        align-items: start;
        gap: 12px;
    }

    .alert-critical {
        background: #fef1f1;
        border-color: #d32f2f;
    }

    .alert-warning {
        background: #fff8e1;
        border-color: #f57c00;
    }

    .alert-info {
        background: #e3f2fd;
        border-color: #1976d2;
    }

    .alert-success {
        background: #f1f8f4;
        border-color: #388e3c;
    }
    """
```

## Shared UI Components

### Metric Card

```
function build_metric_card(label, value, gradient_index):
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(135deg, #30cfd0 0%, #330867 100%)"
    ]

    gradient = gradients[gradient_index % len(gradients)]

    return """
    <div class="metric-card" style="background: {gradient};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
```

### Metric Grid

```
function build_metric_grid(metrics):
    cards = ""
    for i, metric in enumerate(metrics):
        cards += build_metric_card(metric["label"], metric["value"], i)

    return """
    <div class="metric-grid">
        {cards}
    </div>
    """
```

### Alert Box

```
function build_alert(level, title, description):
    icons = {
        "critical": "🚨",
        "warning": "⚠️",
        "info": "ℹ️",
        "success": "✓"
    }

    icon = icons.get(level, "•")

    return """
    <div class="alert alert-{level}">
        <div class="alert-icon">{icon}</div>
        <div class="alert-content">
            <div class="alert-title">{title}</div>
            <div class="alert-description">{description}</div>
        </div>
    </div>
    """
```

### Data Table

```
function build_table(headers, rows, row_formatter):
    # Build header
    header_html = "<tr>"
    for header in headers:
        header_html += f"<th>{header}</th>"
    header_html += "</tr>"

    # Build rows
    rows_html = ""
    for row in rows:
        if row_formatter:
            row_data = row_formatter(row)
        else:
            row_data = row if is_list(row) else list(row.values())

        rows_html += "<tr>"
        for cell in row_data:
            rows_html += f"<td>{cell}</td>"
        rows_html += "</tr>"

    return """
    <table>
        <thead>
            {header_html}
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
```

### Recommendations Section

```
function build_recommendations_html(recommendations):
    if not recommendations:
        return '<p style="color: #666;">No recommendations at this time.</p>'

    rec_html = ""
    for i, rec in enumerate(recommendations, start=1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>'

    return rec_html
```

## Chart.js Integration

### Bar Chart

```
function create_bar_chart(element_id, labels, data, options):
    return """
    <script>
    new Chart(document.getElementById('{element_id}'), {
        type: 'bar',
        data: {
            labels: {labels},
            datasets: [{
                label: '{options.label}',
                data: {data},
                backgroundColor: {options.colors},
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    </script>
    """
```

### Line Chart

```
function create_line_chart(element_id, labels, datasets, options):
    return """
    <script>
    new Chart(document.getElementById('{element_id}'), {
        type: 'line',
        data: {
            labels: {labels},
            datasets: {datasets}
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    </script>
    """
```

### Pie Chart

```
function create_pie_chart(element_id, labels, data, options):
    return """
    <script>
    new Chart(document.getElementById('{element_id}'), {
        type: 'pie',
        data: {
            labels: {labels},
            datasets: [{
                data: {data},
                backgroundColor: {options.colors},
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    </script>
    """
```

### Doughnut Chart

```
function create_doughnut_chart(element_id, labels, data, options):
    return """
    <script>
    new Chart(document.getElementById('{element_id}'), {
        type: 'doughnut',
        data: {
            labels: {labels},
            datasets: [{
                data: {data},
                backgroundColor: {options.colors},
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
    </script>
    """
```

## Formatting Utilities

### Currency Formatting

```
function format_currency(value, decimals):
    if decimals == 3:
        return f"${value:,.3f}"
    elif decimals == 6:
        return f"${value:,.6f}"
    else:
        return f"${value:,.2f}"
```

### Number Formatting

```
function format_number(value):
    return f"{value:,}"
```

### Large Number Formatting

```
function format_large_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(value)
```

### Percentage Formatting

```
function format_percentage(value, decimals):
    return f"{value:.{decimals}f}%"
```

## Report Generation Flow

### Standard Report Generation

```
function generate_report(analyzer_data, output_path):
    # Extract data sections
    sections = extract_sections(analyzer_data)

    # Build content
    content = ""
    content += build_title_section(sections.title, sections.description)
    content += build_metrics_section(sections.metrics)

    for section in sections.data_sections:
        content += build_data_section(section)

    content += build_recommendations_section(sections.recommendations)

    # Build charts
    scripts = build_chart_scripts(sections.charts)

    # Generate HTML
    html = build_html_template(
        title=sections.title,
        content=content,
        scripts=scripts
    )

    # Write to file
    write_file(output_path, html)
```

### Index Page Generation

```
function generate_index_page(reports, report_dir):
    report_cards = ""

    for report in reports:
        status_badge = "✓ Complete"
        status_class = "complete"

        report_cards += """
        <div class="report-card">
            <h3>{report.name}</h3>
            <p class="description">{report.description}</p>
            <div class="status {status_class}">{status_badge}</div>
            <a href="{report.filename}" class="view-button">View Report</a>
        </div>
        """

    html = build_html_template(
        title="Revenium FinOps Showcase - Reports",
        content=build_index_content(report_cards),
        scripts=""
    )

    write_file(f"{report_dir}/index.html", html)
```

### Manifest Generation

```
function generate_manifest(calls, report_dir):
    csv_size_mb = get_file_size(DATA_CSV_PATH) / (1024 * 1024)

    manifest = {
        "generated_at": current_timestamp(),
        "call_count": len(calls),
        "data_size_mb": round(csv_size_mb, 2),
        "target_size_mb": TARGET_SIZE_MB,
        "progress_pct": min((csv_size_mb / TARGET_SIZE_MB) * 100, 100)
    }

    write_json(f"{report_dir}/manifest.json", manifest)
```

## Report Customization

### Color Schemes

Default gradient colors:
```
gradients = [
    "#667eea → #764ba2",  # Purple
    "#f093fb → #f5576c",  # Pink
    "#4facfe → #00f2fe",  # Blue
    "#43e97b → #38f9d7",  # Green
    "#fa709a → #fee140",  # Orange
    "#30cfd0 → #330867"   # Teal
]
```

### Chart Colors

```
chart_colors = [
    "rgba(102, 126, 234, 0.8)",  # Purple
    "rgba(240, 147, 251, 0.8)",  # Pink
    "rgba(79, 172, 254, 0.8)",   # Blue
    "rgba(67, 233, 123, 0.8)",   # Green
    "rgba(250, 112, 154, 0.8)",  # Orange
    "rgba(48, 207, 208, 0.8)",   # Teal
    "rgba(254, 225, 64, 0.8)"    # Yellow
]
```

## Performance Considerations

### Report Generation Time

Target performance:
- Small dataset (< 10MB): < 1 second per report
- Medium dataset (10-100MB): < 5 seconds per report
- Large dataset (100MB-2GB): < 30 seconds per report

### Memory Usage

- Load data once, share across generators
- Stream large tables if needed
- Limit chart data points to 1000 max

### File Size

Target report sizes:
- Simple report: 20-50 KB
- Report with charts: 50-100 KB
- Complex report with multiple charts: 100-200 KB
