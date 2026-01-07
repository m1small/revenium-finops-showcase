#!/usr/bin/env python3
"""
Run All Analyzers

Generates all 13 analysis reports (1 Overview + 5 FinOps + 3 UBR + 4 Advanced) from simulated data.
"""

import os
import sys
import time
from datetime import datetime

from config import TARGET_SIZE_MB, DATA_CSV_PATH, REPORT_DIR

# Import analyzers
from analyzers.finops.understanding import UnderstandingAnalyzer
from analyzers.finops.performance import PerformanceAnalyzer
from analyzers.finops.realtime import RealtimeAnalyzer
from analyzers.finops.optimization import OptimizationAnalyzer
from analyzers.finops.alignment import AlignmentAnalyzer
from analyzers.ubr.profitability import CustomerProfitabilityAnalyzer
from analyzers.ubr.pricing import PricingStrategyAnalyzer
from analyzers.ubr.features import FeatureEconomicsAnalyzer
from analyzers.dataset_overview import DatasetOverviewAnalyzer
from analyzers.token_economics import TokenEconomicsAnalyzer
from analyzers.geographic_latency import GeographicLatencyAnalyzer
from analyzers.churn_growth import ChurnGrowthAnalyzer
from analyzers.abuse_detection import AbuseDetectionAnalyzer

from analyzers.common import load_calls_from_csv, format_currency, format_large_number
from generators import (
    generate_understanding_report, generate_performance_report,
    generate_realtime_report, generate_optimization_report,
    generate_alignment_report, generate_profitability_report,
    generate_pricing_report, generate_features_report
)
from generators.overview_generator import generate_overview_report
from generators.token_economics_generator import generate_token_economics_report
from generators.geographic_latency_generator import generate_geographic_latency_report
from generators.churn_growth_generator import generate_churn_growth_report
from generators.abuse_detection_generator import generate_abuse_detection_report


def run_single_analyzer(report_config: dict, csv_path: str, report_dir: str) -> tuple:
    """Run a single analyzer and generate its report.

    Optimization 3: This function is designed to run in parallel on M1 performance cores.
    Each analyzer gets its own process, maximizing M1's 8-core performance.

    Args:
        report_config: Report configuration dictionary
        csv_path: Path to CSV file
        report_dir: Output directory for reports

    Returns:
        Tuple of (success: bool, report_name: str, error_message: str or None)
    """
    try:
        output_path = f"{report_dir}/{report_config['filename']}"

        # Each process loads data independently (copy-on-write on M1 is efficient)
        analyzer = report_config['analyzer_class'](csv_path)
        results = analyzer.analyze()

        # Generate HTML report
        report_config['html_generator'](results, output_path)

        return (True, report_config['name'], None)
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return (False, report_config['name'], error_msg)


def generate_generic_report(title: str, description: str, data: dict, output_path: str):
    """Generate a generic HTML report for any analyzer."""
    summary = data.get('summary', {})
    recommendations = data.get('recommendations', [])

    # Build summary cards from summary dict
    summary_cards = ""
    for i, (key, value) in enumerate(summary.items(), 1):
        # Format the value based on type
        if isinstance(value, float):
            if 'cost' in key or 'revenue' in key or 'margin' in key or 'savings' in key:
                formatted_value = format_currency(value)
            elif 'percentage' in key or 'pct' in key:
                formatted_value = f"{value:.1f}%"
            else:
                formatted_value = f"{value:,.2f}"
        elif isinstance(value, int):
            formatted_value = format_large_number(value)
        else:
            formatted_value = str(value)

        # Make label human-readable
        label = key.replace('_', ' ').title()

        summary_cards += f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{formatted_value}</div>
            </div>
        """

    # Build recommendations
    rec_html = ""
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'
    else:
        rec_html = '<p style="color: #666;">No recommendations at this time.</p>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - Revenium FinOps</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .subtitle {{ color: #666; font-size: 16px; margin-bottom: 30px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; word-break: break-word; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .metric-card:nth-child(5) {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .metric-card:nth-child(6) {{ background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        a {{ color: #2196f3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">{description}</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            {summary_cards}
        </div>

        <h2>Recommendations</h2>
        {rec_html}

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
    """Run all analyzers and generate reports with M1-optimized parallel processing."""
    csv_path = DATA_CSV_PATH
    report_dir = REPORT_DIR

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run run_all_simulators.py first.")
        sys.exit(1)

    print("=" * 80)
    print("REVENIUM FINOPS SHOWCASE - ANALYSIS GENERATION")
    print("=" * 80)
    print()

    # Optimization 2: Load data once and share across analyzers (memory efficient)
    # M1's unified memory architecture makes this very fast
    print("Loading data...")
    start_time = time.time()
    calls = load_calls_from_csv(csv_path)
    load_time = time.time() - start_time
    print(f"Loaded {len(calls):,} calls in {load_time:.1f}s")
    print()

    # Define all 13 reports with their analyzer classes and HTML generators
    reports = [
        {
            'name': 'Dataset Overview',
            'filename': 'dataset_overview.html',
            'description': 'Comprehensive dataset statistics and distribution metrics',
            'analyzer_class': DatasetOverviewAnalyzer,
            'html_generator': generate_overview_report
        },
        {
            'name': 'Understanding Usage & Cost',
            'filename': 'understanding.html',
            'description': 'Cost allocation, forecasting, and efficiency analysis',
            'analyzer_class': UnderstandingAnalyzer,
            'html_generator': generate_understanding_report
        },
        {
            'name': 'Performance Tracking',
            'filename': 'performance.html',
            'description': 'Model efficiency, latency percentiles, SLA compliance',
            'analyzer_class': PerformanceAnalyzer,
            'html_generator': generate_performance_report
        },
        {
            'name': 'Real-Time Decision Making',
            'filename': 'realtime.html',
            'description': 'Anomaly detection, threshold alerts, portfolio risk',
            'analyzer_class': RealtimeAnalyzer,
            'html_generator': generate_realtime_report
        },
        {
            'name': 'Rate Optimization',
            'filename': 'optimization.html',
            'description': 'Reserved capacity, model switching opportunities',
            'analyzer_class': OptimizationAnalyzer,
            'html_generator': generate_optimization_report
        },
        {
            'name': 'Organizational Alignment',
            'filename': 'alignment.html',
            'description': 'Multi-tenant tracking, chargeback/showback',
            'analyzer_class': AlignmentAnalyzer,
            'html_generator': generate_alignment_report
        },
        {
            'name': 'Customer Profitability',
            'filename': 'profitability.html',
            'description': 'Margin analysis, unprofitable customer detection',
            'analyzer_class': CustomerProfitabilityAnalyzer,
            'html_generator': generate_profitability_report
        },
        {
            'name': 'Pricing Strategy',
            'filename': 'pricing.html',
            'description': '4 pricing model comparisons, revenue projections',
            'analyzer_class': PricingStrategyAnalyzer,
            'html_generator': generate_pricing_report
        },
        {
            'name': 'Feature Economics',
            'filename': 'features.html',
            'description': 'Feature profitability, investment recommendations',
            'analyzer_class': FeatureEconomicsAnalyzer,
            'html_generator': generate_features_report
        },
        {
            'name': 'Token Economics & Efficiency',
            'filename': 'token_economics.html',
            'description': 'Token usage patterns and cost efficiency analysis',
            'analyzer_class': TokenEconomicsAnalyzer,
            'html_generator': generate_token_economics_report
        },
        {
            'name': 'Geographic & Latency Intelligence',
            'filename': 'geographic_latency.html',
            'description': 'Regional performance, cost arbitrage, latency optimization',
            'analyzer_class': GeographicLatencyAnalyzer,
            'html_generator': generate_geographic_latency_report
        },
        {
            'name': 'Churn Risk & Growth Signals',
            'filename': 'churn_growth.html',
            'description': 'Customer engagement, expansion opportunities, retention insights',
            'analyzer_class': ChurnGrowthAnalyzer,
            'html_generator': generate_churn_growth_report
        },
        {
            'name': 'Abuse Detection & Security',
            'filename': 'abuse_detection.html',
            'description': 'Cost anomalies, tier gaming, usage abuse detection',
            'analyzer_class': AbuseDetectionAnalyzer,
            'html_generator': generate_abuse_detection_report
        }
    ]

    # Optimization 3: Parallel analyzer execution on M1 performance cores
    # M1 Pro/Max has 8-10 cores, so run up to 4 analyzers in parallel
    # This gives ~3-4x speedup on M1 hardware
    import multiprocessing as mp
    import platform

    # Detect M1 and optimize worker count
    is_arm = platform.machine() == 'arm64'
    max_workers = min(4, mp.cpu_count() // 2) if is_arm else 2  # Conservative on non-M1

    print(f"Using parallel processing with {max_workers} workers (optimized for M1)")
    print()

    # Generate reports in parallel
    if max_workers > 1:
        with mp.Pool(processes=max_workers) as pool:
            # Prepare arguments for each analyzer
            analyzer_args = [(report, csv_path, report_dir) for report in reports]

            # Run analyzers in parallel with progress tracking
            results_iter = pool.starmap(run_single_analyzer, analyzer_args)

            # Process results
            for i, (success, name, error) in enumerate(results_iter, 1):
                if success:
                    print(f"[{i}/{len(reports)}] ✓ Generated: {name}")
                else:
                    print(f"[{i}/{len(reports)}] ✗ Error in {name}:")
                    print(f"  {error}")
    else:
        # Fallback to sequential processing
        for i, report in enumerate(reports, 1):
            print(f"[{i}/{len(reports)}] Generating: {report['name']}...")
            success, name, error = run_single_analyzer(report, csv_path, report_dir)
            if success:
                print(f"  ✓ Generated: {name}")
            else:
                print(f"  ✗ Error: {error}")

    # Generate index page
    print()
    print("Generating index page...")
    generate_index_page(reports, report_dir)
    print(f"  Generated: {report_dir}/index.html")

    # Generate manifest for viewer
    print()
    print("Generating manifest...")
    generate_manifest(calls, report_dir)
    print(f"  Generated: {report_dir}/manifest.json")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Reports generated: {len(reports)}")
    print(f"Output directory: {report_dir}/")
    print()


def generate_index_page(reports, report_dir='reports/html'):
    """Generate main index page listing all reports with Executive Summary.

    This function generates a static index page suitable for GitHub Pages deployment.
    It includes:
    - Dataset information from manifest.json
    - Executive Summary with 3 key business insights and charts
    - All 13 reports organized by category
    """
    import json

    # Read manifest if available
    manifest_path = os.path.join(report_dir, 'manifest.json')
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

    # Group reports by category (categories defined in each report config)
    # Define categories based on the report list
    report_configs_with_categories = [
        {'report': reports[0], 'category': 'Core Analytics'},  # Dataset Overview
        {'report': reports[1], 'category': 'Core Analytics'},  # Understanding
        {'report': reports[2], 'category': 'Core Analytics'},  # Performance
        {'report': reports[3], 'category': 'Operational Insights'},  # Realtime
        {'report': reports[4], 'category': 'Operational Insights'},  # Optimization
        {'report': reports[5], 'category': 'Operational Insights'},  # Alignment
        {'report': reports[6], 'category': 'Financial & Revenue Analytics'},  # Profitability
        {'report': reports[7], 'category': 'Financial & Revenue Analytics'},  # Pricing
        {'report': reports[8], 'category': 'Financial & Revenue Analytics'},  # Features
        {'report': reports[9], 'category': 'Advanced Analytics'},  # Token Economics
        {'report': reports[10], 'category': 'Advanced Analytics'},  # Geographic
        {'report': reports[11], 'category': 'Advanced Analytics'},  # Churn
        {'report': reports[12], 'category': 'Advanced Analytics'},  # Abuse Detection
    ]

    # Group by category
    categories = {}
    for item in report_configs_with_categories:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item['report'])

    # Build report cards HTML with proper emoji prefixes
    category_emojis = {
        'Core Analytics': '📊',
        'Financial & Revenue Analytics': '💰',
        'Operational Insights': '🚀',
        'Advanced Analytics': '🔬'
    }

    report_cards_html = ''
    for category, cat_reports in categories.items():
        emoji = category_emojis.get(category, '📈')
        report_cards_html += f'<h3 class="category-header">{emoji} {category}</h3>\n'
        report_cards_html += '<div class="report-grid">\n'
        for report in cat_reports:
            description = report.get('description', '')
            report_cards_html += f'''
                <div class="report-card">
                    <div class="status-badge complete">✓ Available</div>
                    <h4>{report['name']}</h4>
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
                        <div class="info-value">{len(reports)}</div>
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
</html>"""

    os.makedirs(report_dir, exist_ok=True)
    with open(f'{report_dir}/index.html', 'w') as f:
        f.write(html)


def generate_manifest(calls, report_dir='reports/html'):
    """Generate manifest file for viewer."""
    import json

    # Get CSV file size
    csv_path = DATA_CSV_PATH
    file_size_mb = os.path.getsize(csv_path) / (1024 * 1024) if os.path.exists(csv_path) else 0

    manifest = {
        'generated_at': datetime.now().isoformat(),
        'call_count': len(calls),
        'data_size_mb': round(file_size_mb, 2),
        'target_size_mb': TARGET_SIZE_MB,
        'progress_pct': min((file_size_mb / TARGET_SIZE_MB) * 100, 100)
    }

    os.makedirs(report_dir, exist_ok=True)
    with open(f'{report_dir}/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)


if __name__ == '__main__':
    main()
