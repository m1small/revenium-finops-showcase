#!/usr/bin/env python3
"""
Run All Analyzers

Generates all 8 analysis reports (5 FinOps + 3 UBR) from simulated data.
"""

import os
import sys
import time
from datetime import datetime

# Import analyzer and HTML generator
from analyzers.finops.understanding import UnderstandingAnalyzer
from analyzers.common import load_calls_from_csv, format_currency, format_large_number
from utils.html_generator import generate_understanding_report


def generate_placeholder_report(title: str, description: str, output_path: str):
    """Generate a placeholder HTML report for non-implemented analyzers."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - Revenium FinOps</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                      text-align: center; }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        .placeholder {{ background: #f8f9fa; padding: 40px; border-radius: 8px; margin: 30px 0;
                       border: 2px dashed #e0e0e0; }}
        .icon {{ font-size: 64px; margin-bottom: 20px; }}
        p {{ color: #666; font-size: 16px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; }}
        a {{ color: #2196f3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="placeholder">
            <div class="icon">📊</div>
            <p><strong>{description}</strong></p>
            <p>This analyzer is planned for future implementation.</p>
            <p>The specification is complete and ready for development.</p>
        </div>
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
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
            'description': 'Cost allocation, forecasting, and efficiency analysis',
            'implemented': True
        },
        {
            'name': 'Performance Tracking',
            'filename': 'performance.html',
            'description': 'Model efficiency, latency percentiles, SLA compliance',
            'implemented': False
        },
        {
            'name': 'Real-Time Decision Making',
            'filename': 'realtime.html',
            'description': 'Anomaly detection, threshold alerts, portfolio risk',
            'implemented': False
        },
        {
            'name': 'Rate Optimization',
            'filename': 'optimization.html',
            'description': 'Reserved capacity, model switching opportunities',
            'implemented': False
        },
        {
            'name': 'Organizational Alignment',
            'filename': 'alignment.html',
            'description': 'Multi-tenant tracking, chargeback/showback',
            'implemented': False
        },
        {
            'name': 'Customer Profitability',
            'filename': 'profitability.html',
            'description': 'Margin analysis, unprofitable customer detection',
            'implemented': False
        },
        {
            'name': 'Pricing Strategy',
            'filename': 'pricing.html',
            'description': '4 pricing model comparisons, revenue projections',
            'implemented': False
        },
        {
            'name': 'Feature Economics',
            'filename': 'features.html',
            'description': 'Feature profitability, investment recommendations',
            'implemented': False
        }
    ]

    # Generate each report
    for i, report in enumerate(reports, 1):
        print(f"[{i}/8] Generating: {report['name']}...")

        output_path = f"reports/html/{report['filename']}"

        if report['implemented']:
            # Use actual analyzer
            analyzer = UnderstandingAnalyzer(csv_path)
            results = analyzer.analyze()
            generate_understanding_report(results, output_path)
        else:
            # Generate placeholder
            generate_placeholder_report(report['name'], report['description'], output_path)

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
        status_badge = '✓ Complete' if report['implemented'] else '📋 Planned'
        badge_color = '#4CAF50' if report['implemented'] else '#FF9800'

        report_cards += f"""
        <div class="report-card">
            <div class="status-badge" style="background: {badge_color};">{status_badge}</div>
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
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #1a1a1a; font-size: 32px; margin-bottom: 10px; }}
        .subtitle {{ color: #666; font-size: 18px; margin-bottom: 30px; }}
        .data-info {{ background: white; padding: 20px; border-radius: 8px;
                      margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .data-info h3 {{ margin-top: 0; }}
        .data-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                       gap: 15px; margin-top: 15px; }}
        .stat {{ background: #f8f9fa; padding: 15px; border-radius: 6px; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #1a1a1a; margin-top: 5px; }}
        .report-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                       gap: 20px; }}
        .report-card {{ background: white; padding: 25px; border-radius: 8px; position: relative;
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .report-card:hover {{ transform: translateY(-4px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
        .report-card h3 {{ margin-top: 0; color: #1a1a1a; }}
        .report-card p {{ color: #666; font-size: 14px; line-height: 1.6; }}
        .status-badge {{ position: absolute; top: 15px; right: 15px; padding: 5px 12px;
                        border-radius: 12px; font-size: 11px; color: white; font-weight: 600; }}
        .view-button {{ display: inline-block; background: #2196f3; color: white; padding: 10px 20px;
                       text-decoration: none; border-radius: 4px; margin-top: 10px;
                       transition: background 0.2s; }}
        .view-button:hover {{ background: #1976d2; }}
    </style>
    <script>
        // Load and display data stats
        fetch('manifest.json?_=' + Date.now())
            .then(r => r.json())
            .then(manifest => {{
                document.getElementById('call-count').textContent = manifest.call_count.toLocaleString();
                document.getElementById('data-size').textContent = manifest.data_size_mb.toFixed(2) + ' MB';
                document.getElementById('completion').textContent = manifest.progress_pct.toFixed(1) + '%';
            }})
            .catch(e => console.log('Loading manifest...'));
    </script>
</head>
<body>
    <div class="container">
        <h1>Revenium FinOps Showcase</h1>
        <div class="subtitle">AI Cost Management & Usage-Based Revenue Analysis</div>

        <div class="data-info">
            <h3>Dataset Information</h3>
            <div class="data-stats">
                <div class="stat">
                    <div class="stat-label">Total Calls</div>
                    <div class="stat-value" id="call-count">-</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Data Size</div>
                    <div class="stat-value" id="data-size">-</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Completion</div>
                    <div class="stat-value" id="completion">-</div>
                </div>
            </div>
        </div>

        <h2>Analysis Reports</h2>
        <div class="report-grid">
            {report_cards}
        </div>

        <div style="margin-top: 40px; text-align: center; color: #666; font-size: 14px;">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
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
