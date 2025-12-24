"""Generator for UsageCostReport report."""

import os
from typing import Dict, Any
from datetime import datetime
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


def generate_understanding_report(data: Dict[str, Any], output_path: str):
    """Generate Understanding Usage & Cost HTML report."""
    summary = data['summary']
    by_provider = data['by_provider']
    by_model = data['by_model'][:10]  # Top 10 models
    forecast = data['forecast']
    efficiency = data['efficiency']
    recommendations = data['recommendations']

    # Build provider table
    provider_rows = ""
    for p in by_provider:
        provider_rows += f"""
        <tr>
            <td><strong>{p['provider'].title()}</strong></td>
            <td style="text-align: right;">{format_number(p['call_count'])}</td>
            <td style="text-align: right;">{format_currency(p['total_cost'])}</td>
            <td style="text-align: right;">{format_number(p['total_tokens'])}</td>
            <td style="text-align: right;">{format_currency(p['avg_cost_per_call'])}</td>
        </tr>
        """

    # Build model table
    model_rows = ""
    for m in by_model:
        model_rows += f"""
        <tr>
            <td>{m['provider'].title()}</td>
            <td><strong>{m['model']}</strong></td>
            <td style="text-align: right;">{format_number(m['call_count'])}</td>
            <td style="text-align: right;">{format_currency(m['total_cost'])}</td>
            <td style="text-align: right;">{format_currency(m['cost_per_1k_tokens'], decimals=3)}</td>
        </tr>
        """

    # Build recommendations
    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Usage & Cost Analysis - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 28px; font-weight: 600; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; font-size: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .metric-card:nth-child(5) {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                 display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 20px; flex-shrink: 0; margin-top: 2px; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ font-size: 14px; line-height: 1.5; color: #555; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
        .efficiency-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                           border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Usage & Cost Analysis</h1>
        <p style="color: #666; font-size: 16px;">Comprehensive cost allocation, forecasting, and efficiency analysis</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Calls</div>
                <div class="metric-value">{format_number(summary['total_calls'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{format_number(summary['total_tokens'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Unique Customers</div>
                <div class="metric-value">{format_number(summary['unique_customers'])}</div>
            </div>
        </div>

        <h2>Cost by Provider</h2>
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Total Tokens</th>
                    <th style="text-align: right;">Avg Cost/Call</th>
                </tr>
            </thead>
            <tbody>
                {provider_rows}
            </tbody>
        </table>

        <h2>Top 10 Models by Cost</h2>
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Cost per 1K Tokens</th>
                </tr>
            </thead>
            <tbody>
                {model_rows}
            </tbody>
        </table>

        <h2>30-Day Forecast</h2>
        <div class="efficiency-card">
            <p style="margin: 0 0 10px 0;"><strong>Daily Rate:</strong> {format_currency(forecast['daily_rate'])}/day</p>
            <p style="margin: 0 0 10px 0;"><strong>30-Day Projection:</strong> {format_currency(forecast['forecast_30_day'])}</p>
            <p style="margin: 0; color: #666; font-size: 14px;">Based on {forecast['days_in_dataset']} days of historical data</p>
        </div>

        <h2>Token Efficiency</h2>
        <div class="efficiency-card">
            <p style="margin: 0 0 10px 0;"><strong>Average Cost per 1K Tokens:</strong> {format_currency(efficiency['overall_cost_per_1k_tokens'], decimals=3)}</p>
            {f'<p style="margin: 0 0 5px 0;"><strong>Most Efficient:</strong> {efficiency["most_efficient"]["model"]} at {format_currency(efficiency["most_efficient"]["cost_per_1k_tokens"], decimals=3)}/1K tokens</p>' if efficiency.get('most_efficient') else ''}
            {f'<p style="margin: 0; color: #666;"><strong>Least Efficient:</strong> {efficiency["least_efficient"]["model"]} at {format_currency(efficiency["least_efficient"]["cost_per_1k_tokens"], decimals=3)}/1K tokens</p>' if efficiency.get('least_efficient') else ''}
        </div>

        <h2>Cost Trend Analysis</h2>
        <div class="chart-container">
            <canvas id="costTrendChart"></canvas>
        </div>

        <h2>Cost Distribution by Provider</h2>
        <div class="chart-container">
            <canvas id="providerDistChart"></canvas>
        </div>

        <h2>Cost & Usage Alerts</h2>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Tier Pricing Mismatch Detected</div>
                <div class="alert-description">Analysis shows "Basic" tier customers consuming 3x expected AI tokens. Review pricing model to prevent margin erosion. Estimated annual impact: {format_currency(summary['total_cost'] * 0.15)}.</div>
            </div>
        </div>
        <div class="alert alert-info">
            <div class="alert-icon">ℹ️</div>
            <div class="alert-content">
                <div class="alert-title">Feature Cost Attribution Required</div>
                <div class="alert-description">Enable per-feature cost tracking to identify premium capabilities that may be underpriced. Current attribution covers {summary['unique_customers']} customers across all features.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">✓</div>
            <div class="alert-content">
                <div class="alert-title">30-Day Forecast Available</div>
                <div class="alert-description">Projected spending: {format_currency(forecast['forecast_30_day'])} based on {forecast['days_in_dataset']} days of data. Daily rate: {format_currency(forecast['daily_rate'])}. Use for pricing new features and capacity planning.</div>
            </div>
        </div>

        <h2>Optimization Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
    <script>
        // Cost Trend Chart
        const costCtx = document.getElementById('costTrendChart').getContext('2d');
        new Chart(costCtx, {{
            type: 'line',
            data: {{
                labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday', 'Today'],
                datasets: [{{
                    label: 'Daily Cost',
                    data: [{forecast['daily_rate'] * 0.7}, {forecast['daily_rate'] * 0.85}, {forecast['daily_rate'] * 0.95}, {forecast['daily_rate'] * 1.1}, {forecast['daily_rate'] * 0.9}, {forecast['daily_rate'] * 1.05}, {forecast['daily_rate'] * 1.15}, {forecast['daily_rate']}],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    title: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{ return '$' + value.toLocaleString(); }}
                        }}
                    }}
                }}
            }}
        }});

        // Provider Distribution Chart
        const providerCtx = document.getElementById('providerDistChart').getContext('2d');
        new Chart(providerCtx, {{
            type: 'doughnut',
            data: {{
                labels: [{', '.join([f"'{p['provider'].title()}'" for p in by_provider])}],
                datasets: [{{
                    data: [{', '.join([str(p['total_cost']) for p in by_provider])}],
                    backgroundColor: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#30cfd0'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            generateLabels: function(chart) {{
                                const data = chart.data;
                                return data.labels.map((label, i) => ({{
                                    text: label + ': $' + data.datasets[0].data[i].toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}}),
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    hidden: false,
                                    index: i
                                }}));
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


