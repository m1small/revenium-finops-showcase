#!/usr/bin/env python3
"""
Run All Analyzers

Generates all 8 analysis reports (5 FinOps + 3 UBR) from simulated data.
"""

import os
import sys
import time
from datetime import datetime

# Import analyzer (we'll use the understanding analyzer as a template)
from analyzers.finops.understanding import UnderstandingAnalyzer
from analyzers.common import load_calls_from_csv, format_currency, format_large_number


def generate_simple_html_report(title: str, data: dict, output_path: str):
    """Generate a simple HTML report from analysis data."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - Revenium FinOps</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white;
                      padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #1a1a1a; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 15px; margin: 10px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; }}
        .timestamp {{ color: #666; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-d %H:%M:%S')}</div>

        <h2>Summary</h2>
        <pre style="background: #f8f9fa; padding: 20px; border-radius: 6px; overflow-x: auto;">
{str(data)[:5000]}
        </pre>

        <div class="timestamp">
            Part of Revenium FinOps Showcase |
            <a href="index.html">View All Reports</a>
        </div>
    </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


def main():
    """Run all analyzers and generate reports."""
    csv_path = 'data/simulated_calls.csv'

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run run_all_simulators.py first.")
        sys.exit(1)

    print("=" * 80)
    print("REVENIUM FINOPS SHOWCASE - ANALYSIS GENERATION")
    print("=" * 80)
    print()

    # Load calls once for all analyzers
    print("Loading data...")
    calls = load_calls_from_csv(csv_path)
    print(f"Loaded {len(calls):,} calls")
    print()

    # Define all 8 reports
    reports = [
        {
            'name': 'Understanding Usage & Cost',
            'filename': 'understanding.html',
            'description': 'Cost allocation, forecasting, and efficiency analysis'
        },
        {
            'name': 'Performance Tracking',
            'filename': 'performance.html',
            'description': 'Model efficiency, latency percentiles, SLA compliance'
        },
        {
            'name': 'Real-Time Decision Making',
            'filename': 'realtime.html',
            'description': 'Anomaly detection, threshold alerts, portfolio risk'
        },
        {
            'name': 'Rate Optimization',
            'filename': 'optimization.html',
            'description': 'Reserved capacity, model switching opportunities'
        },
        {
            'name': 'Organizational Alignment',
            'filename': 'alignment.html',
            'description': 'Multi-tenant tracking, chargeback/showback'
        },
        {
            'name': 'Customer Profitability',
            'filename': 'profitability.html',
            'description': 'Margin analysis, unprofitable customer detection'
        },
        {
            'name': 'Pricing Strategy',
            'filename': 'pricing.html',
            'description': '4 pricing model comparisons, revenue projections'
        },
        {
            'name': 'Feature Economics',
            'filename': 'features.html',
            'description': 'Feature profitability, investment recommendations'
        }
    ]

    # Generate each report
    for i, report in enumerate(reports, 1):
        print(f"[{i}/8] Generating: {report['name']}...")

        # For demonstration, use the Understanding analyzer as template
        # In full implementation, each would have its own analyzer
        if 'Understanding' in report['name']:
            analyzer = UnderstandingAnalyzer(csv_path)
            results = analyzer.analyze()
        else:
            # Placeholder analysis for other reports
            results = {
                'report_name': report['name'],
                'description': report['description'],
                'total_calls': len(calls),
                'generated_at': datetime.now().isoformat(),
                'note': 'This is a simplified report. Full implementation would include detailed analysis.'
            }

        # Generate HTML report
        output_path = f"reports/html/{report['filename']}"
        generate_simple_html_report(report['name'], results, output_path)
        print(f"  Generated: {output_path}")

    # Generate index page
    print()
    print("Generating index page...")
    generate_index_page(reports)
    print("  Generated: reports/html/index.html")

    # Generate manifest for viewer
    print()
    print("Generating manifest...")
    generate_manifest(calls)
    print("  Generated: reports/html/manifest.json")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Reports generated: {len(reports)}")
    print("Output directory: reports/html/")
    print()


def generate_index_page(reports):
    """Generate main index page listing all reports."""
    report_cards = ""
    for report in reports:
        report_cards += f"""
        <div class="report-card">
            <h3>{report['name']}</h3>
            <p>{report['description']}</p>
            <a href="{report['filename']}" class="view-button">View Report →</a>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Revenium FinOps Showcase - Reports</title>
    <meta http-equiv="refresh" content="15">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #1a1a1a; font-size: 32px; margin-bottom: 10px; }}
        .subtitle {{ color: #666; font-size: 18px; margin-bottom: 30px; }}
        .progress-container {{ background: white; padding: 20px; border-radius: 8px;
                              margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .progress-bar {{ width: 100%; height: 30px; background: #e0e0e0; border-radius: 15px;
                        overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #4CAF50, #45a049);
                         transition: width 0.3s ease; }}
        .progress-text {{ text-align: center; margin-top: 10px; font-size: 14px; color: #666; }}
        .report-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                       gap: 20px; }}
        .report-card {{ background: white; padding: 25px; border-radius: 8px;
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .report-card:hover {{ transform: translateY(-4px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
        .report-card h3 {{ margin-top: 0; color: #1a1a1a; }}
        .report-card p {{ color: #666; font-size: 14px; line-height: 1.6; }}
        .view-button {{ display: inline-block; background: #2196f3; color: white; padding: 10px 20px;
                       text-decoration: none; border-radius: 4px; margin-top: 10px;
                       transition: background 0.2s; }}
        .view-button:hover {{ background: #1976d2; }}
        .update-notification {{ display: none; position: fixed; top: 20px; right: 20px;
                               background: #4CAF50; color: white; padding: 15px 25px;
                               border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                               animation: slideIn 0.3s ease; }}
        @keyframes slideIn {{ from {{ transform: translateX(400px); }} to {{ transform: translateX(0); }} }}
    </style>
    <script>
        let lastUpdate = Date.now();

        function checkForUpdates() {{
            fetch('manifest.json?_=' + Date.now())
                .then(r => r.json())
                .then(manifest => {{
                    const manifestTime = new Date(manifest.generated_at).getTime();
                    if (manifestTime > lastUpdate) {{
                        showUpdateNotification();
                        updateProgress(manifest.data_size_mb);
                        lastUpdate = manifestTime;
                    }}
                }})
                .catch(e => console.log('Waiting for data...'));
        }}

        function showUpdateNotification() {{
            const notification = document.querySelector('.update-notification');
            notification.style.display = 'block';
            setTimeout(() => {{ notification.style.display = 'none'; }}, 3000);
        }}

        function updateProgress(sizeMb) {{
            const targetMb = 50;
            const progress = Math.min((sizeMb / targetMb) * 100, 100);
            document.querySelector('.progress-fill').style.width = progress + '%';
            document.querySelector('.progress-text').textContent =
                `${{sizeMb.toFixed(2)}} MB / ${{targetMb}} MB (${{progress.toFixed(1)}}%)`;
        }}

        setInterval(checkForUpdates, 15000);  // Check every 15 seconds
        checkForUpdates();  // Initial check
    </script>
</head>
<body>
    <div class="container">
        <h1>Revenium FinOps Showcase</h1>
        <div class="subtitle">AI Cost Management & Usage-Based Revenue Analysis</div>

        <div class="progress-container">
            <h3 style="margin-top: 0;">Data Generation Progress</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%;"></div>
            </div>
            <div class="progress-text">Loading...</div>
        </div>

        <h2>Analysis Reports</h2>
        <div class="report-grid">
            {report_cards}
        </div>

        <div style="margin-top: 40px; text-align: center; color: #666; font-size: 14px;">
            Auto-refreshing every 15 seconds | Last update: <span id="timestamp">{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    </div>

    <div class="update-notification">
        Reports updated!
    </div>
</body>
</html>"""

    os.makedirs('reports/html', exist_ok=True)
    with open('reports/html/index.html', 'w') as f:
        f.write(html)


def generate_manifest(calls):
    """Generate manifest file for viewer."""
    import json

    # Get CSV file size
    csv_path = 'data/simulated_calls.csv'
    file_size_mb = os.path.getsize(csv_path) / (1024 * 1024) if os.path.exists(csv_path) else 0

    manifest = {
        'generated_at': datetime.now().isoformat(),
        'call_count': len(calls),
        'data_size_mb': round(file_size_mb, 2),
        'target_size_mb': 50,
        'progress_pct': min((file_size_mb / 50) * 100, 100)
    }

    os.makedirs('reports/html', exist_ok=True)
    with open('reports/html/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)


if __name__ == '__main__':
    main()
