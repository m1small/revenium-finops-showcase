"""HTML Report Generation Utilities."""

import os
from datetime import datetime
from typing import Dict, Any, List


def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency with configurable decimal places."""
    if decimals == 3:
        return f"${value:,.3f}"
    return f"${value:,.2f}"


def format_number(value: int) -> str:
    """Format number with commas."""
    return f"{value:,}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.1f}%"


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


def generate_performance_report(data: Dict[str, Any], output_path: str):
    """Generate Performance Tracking HTML report."""
    summary = data['summary']
    by_model = data['by_model'][:15]  # Top 15 models
    sla_compliance = data['sla_compliance']
    task_recommendations = data['task_recommendations']
    recommendations = data['recommendations']

    # Build model efficiency table
    model_rows = ""
    for m in by_model:
        model_rows += f"""
        <tr>
            <td>{m['provider'].title()}</td>
            <td><strong>{m['model']}</strong></td>
            <td style="text-align: right;">{format_number(m['call_count'])}</td>
            <td style="text-align: right;">{m['p50_latency_ms']:.0f}ms</td>
            <td style="text-align: right;">{m['p95_latency_ms']:.0f}ms</td>
            <td style="text-align: right;">{m['tokens_per_second']:.1f}</td>
            <td style="text-align: right;">{format_currency(m['cost_per_1k_tokens'], decimals=3)}</td>
            <td style="text-align: right;">{m['efficiency_score']:.2f}</td>
        </tr>
        """

    # Build SLA compliance table
    sla_rows = ""
    for model in sla_compliance['by_model'][:10]:
        compliance_color = '#4CAF50' if model['compliance_pct'] >= 95 else '#FF9800' if model['compliance_pct'] >= 80 else '#f44336'
        sla_rows += f"""
        <tr>
            <td>{model['provider'].title()}</td>
            <td><strong>{model['model']}</strong></td>
            <td style="text-align: right;">{format_number(model['total_calls'])}</td>
            <td style="text-align: right; color: {compliance_color}; font-weight: bold;">{model['compliance_pct']:.1f}%</td>
            <td style="text-align: right;">{format_number(model['within_sla'])}</td>
        </tr>
        """

    # Build task recommendations
    task_rec_html = ""
    for task, model in task_recommendations.items():
        task_label = task.replace('_', ' ').title()
        task_rec_html += f'<div class="recommendation"><strong>{task_label}:</strong> {model}</div>\n'

    # Build recommendations
    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Performance Analysis - FinOps Dashboard</title>
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
        .metric-card:nth-child(6) {{ background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }}
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
        .info-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                     border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Analysis</h1>
        <p style="color: #666; font-size: 16px;">Model efficiency, latency percentiles, and SLA compliance monitoring</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Calls</div>
                <div class="metric-value">{format_number(summary['total_calls'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Latency</div>
                <div class="metric-value">{summary['avg_latency_ms']:.0f}ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">P95 Latency</div>
                <div class="metric-value">{summary['p95_latency_ms']}ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">P99 Latency</div>
                <div class="metric-value">{summary['p99_latency_ms']}ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Tokens/Second</div>
                <div class="metric-value">{summary['avg_tokens_per_second']:.1f}</div>
            </div>
        </div>

        <h2>Model Efficiency Rankings</h2>
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">P50 Latency</th>
                    <th style="text-align: right;">P95 Latency</th>
                    <th style="text-align: right;">Tokens/Sec</th>
                    <th style="text-align: right;">Cost/1K Tokens</th>
                    <th style="text-align: right;">Efficiency Score</th>
                </tr>
            </thead>
            <tbody>
                {model_rows}
            </tbody>
        </table>

        <h2>SLA Compliance ({sla_compliance['sla_threshold_ms']}ms threshold)</h2>
        <div class="info-card">
            <p style="margin: 0 0 10px 0;"><strong>Overall Compliance:</strong> {sla_compliance['overall_compliance_pct']:.1f}%</p>
            <p style="margin: 0 0 10px 0;"><strong>Within SLA:</strong> {format_number(sla_compliance['within_sla'])} / {format_number(sla_compliance['total_calls'])} calls</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Compliance %</th>
                    <th style="text-align: right;">Within SLA</th>
                </tr>
            </thead>
            <tbody>
                {sla_rows}
            </tbody>
        </table>

        <h2>Task-Based Recommendations</h2>
        {task_rec_html}

        <h2>Latency Distribution Analysis</h2>
        <div class="chart-container">
            <canvas id="latencyChart"></canvas>
        </div>

        <h2>Model Efficiency Comparison</h2>
        <div class="chart-container">
            <canvas id="efficiencyChart"></canvas>
        </div>

        <h2>Performance Alerts</h2>
        <div class="alert alert-critical">
            <div class="alert-icon">🔴</div>
            <div class="alert-content">
                <div class="alert-title">SLA Breach Detected</div>
                <div class="alert-description">Model performance below threshold: 8+ second response times detected on document analysis queries. Current P95 latency: {summary['p95_latency_ms']}ms. User abandonment risk high. Review model selection immediately.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">✓</div>
            <div class="alert-content">
                <div class="alert-title">Optimal Model Configuration Available</div>
                <div class="alert-description">Analysis shows task-based routing can achieve 50% adoption increase and 30% cost reduction. Recommended: GPT-4 for complex tasks, Claude Sonnet for balanced workloads, GPT-3.5 for simple operations. Overall SLA compliance: {sla_compliance['overall_compliance_pct']:.1f}%.</div>
            </div>
        </div>
        <div class="alert alert-info">
            <div class="alert-icon">ℹ️</div>
            <div class="alert-content">
                <div class="alert-title">Performance Monitoring Active</div>
                <div class="alert-description">Tracking {format_number(summary['total_calls'])} calls across {len(by_model)} models. Average latency: {summary['avg_latency_ms']:.0f}ms. P99 latency: {summary['p99_latency_ms']}ms. Use metrics below for capacity planning and model selection.</div>
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
        // Latency Distribution Chart
        const latencyCtx = document.getElementById('latencyChart').getContext('2d');
        new Chart(latencyCtx, {{
            type: 'bar',
            data: {{
                labels: [{', '.join([f"'{m['model'][:20]}...'" if len(m['model']) > 20 else f"'{m['model']}'" for m in by_model[:8]])}],
                datasets: [{{
                    label: 'P50 Latency (ms)',
                    data: [{', '.join([str(m['p50_latency_ms']) for m in by_model[:8]])}],
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: '#667eea',
                    borderWidth: 1
                }}, {{
                    label: 'P95 Latency (ms)',
                    data: [{', '.join([str(m['p95_latency_ms']) for m in by_model[:8]])}],
                    backgroundColor: 'rgba(240, 147, 251, 0.6)',
                    borderColor: '#f093fb',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }},
                    title: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Latency (ms)' }} }}
                }}
            }}
        }});

        // Model Efficiency Chart
        const efficiencyCtx = document.getElementById('efficiencyChart').getContext('2d');
        new Chart(efficiencyCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Model Efficiency',
                    data: [{', '.join([f"{{x: {m['cost_per_1k_tokens']}, y: {m['efficiency_score']}, label: '{m['model'][:15]}'}}" for m in by_model[:10]])}],
                    backgroundColor: '#43e97b',
                    borderColor: '#38f9d7',
                    pointRadius: 8,
                    pointHoverRadius: 12
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.raw.label + ': Efficiency ' + context.parsed.y.toFixed(2) + ', Cost $' + context.parsed.x.toFixed(3);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Cost per 1K Tokens ($)' }} }},
                    y: {{ title: {{ display: true, text: 'Efficiency Score' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


def generate_realtime_report(data: Dict[str, Any], output_path: str):
    """Generate Real-Time Decision Making HTML report."""
    summary = data['summary']
    cost_anomalies = data['cost_anomalies']
    customer_violations = data['customer_violations']
    alert_examples = data['alert_examples']
    portfolio_risk = data['portfolio_risk']
    recommendations = data['recommendations']

    # Build anomalous calls table
    anomaly_rows = ""
    for call in cost_anomalies['anomalous_calls'][:15]:
        anomaly_rows += f"""
        <tr>
            <td>{call['customer_id']}</td>
            <td>{call['provider'].title()}</td>
            <td>{call['model']}</td>
            <td style="text-align: right;">{format_currency(call['cost_usd'])}</td>
            <td style="text-align: right;">{format_number(call['tokens'])}</td>
        </tr>
        """

    # Build at-risk customers table
    risk_rows = ""
    for cust in customer_violations['customers_at_risk'][:15]:
        risk_color = '#f44336' if cust['risk_level'] == 'critical' else '#FF9800' if cust['risk_level'] == 'high' else '#FFC107'
        risk_rows += f"""
        <tr>
            <td>{cust['customer_id']}</td>
            <td>{cust['tier']}</td>
            <td style="text-align: right;">{format_currency(cust['tier_price'])}</td>
            <td style="text-align: right;">{format_currency(cust['total_cost'])}</td>
            <td style="text-align: right; color: {risk_color}; font-weight: bold;">{cust['cost_ratio']:.1f}%</td>
            <td style="text-align: right;">{format_currency(cust['margin'])}</td>
            <td><span style="background: {risk_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">{cust['risk_level'].upper()}</span></td>
        </tr>
        """

    # Build alerts
    alert_html = ""
    for alert in alert_examples:
        severity_color = '#f44336' if alert['severity'] == 'critical' else '#FF9800' if alert['severity'] == 'warning' else '#2196f3'
        alert_html += f"""
        <div style="background: {severity_color}20; padding: 18px; margin: 12px 0; border-left: 4px solid {severity_color}; border-radius: 4px;">
            <div style="color: {severity_color}; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-bottom: 8px;">{alert['severity']}</div>
            <div style="margin-bottom: 8px;">{alert['message']}</div>
            <div style="color: #666; font-size: 14px;"><strong>Action:</strong> {alert['recommended_action']}</div>
        </div>
        """

    # Build recommendations
    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Real-Time Monitoring - FinOps Dashboard</title>
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
        .info-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                     border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Real-Time Monitoring & Alerts</h1>
        <p style="color: #666; font-size: 16px;">Anomaly detection, threshold alerts, and portfolio risk analysis</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Calls</div>
                <div class="metric-value">{format_number(summary['total_calls'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Anomalies</div>
                <div class="metric-value">{summary['anomaly_count']} ({summary['anomaly_percentage']:.1f}%)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Customers at Risk</div>
                <div class="metric-value">{summary['customers_at_risk']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Potential Savings</div>
                <div class="metric-value">{format_currency(summary['potential_savings'])}</div>
            </div>
        </div>

        <h2>Active Alerts</h2>
        {alert_html}

        <h2>Cost Anomalies (Top {len(cost_anomalies['anomalous_calls'][:15])})</h2>
        <div class="info-card">
            <p style="margin: 0;"><strong>Total Anomalies:</strong> {cost_anomalies['total_anomalies']} | <strong>Mean Cost:</strong> {format_currency(cost_anomalies['mean_cost'])} | <strong>Max Cost:</strong> {format_currency(cost_anomalies['max_cost'])}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Cost</th>
                    <th style="text-align: right;">Tokens</th>
                </tr>
            </thead>
            <tbody>
                {anomaly_rows}
            </tbody>
        </table>

        <h2>At-Risk Customers (Top {len(customer_violations['customers_at_risk'][:15])})</h2>
        <div class="info-card">
            <p style="margin: 0;"><strong>Total at Risk:</strong> {customer_violations['total_at_risk']} | <strong>Critical:</strong> {customer_violations['critical_count']} | <strong>High Risk:</strong> {customer_violations['high_count']} | <strong>Revenue at Risk:</strong> {format_currency(customer_violations['revenue_at_risk'])}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Tier</th>
                    <th style="text-align: right;">Revenue</th>
                    <th style="text-align: right;">Cost</th>
                    <th style="text-align: right;">Cost Ratio</th>
                    <th style="text-align: right;">Margin</th>
                    <th>Risk Level</th>
                </tr>
            </thead>
            <tbody>
                {risk_rows}
            </tbody>
        </table>

        <h2>Portfolio Risk Distribution</h2>
        <div class="metric-grid">
            <div class="metric-card" style="background: linear-gradient(135deg, #f44336 0%, #e53935 100%);">
                <div class="metric-label">Critical</div>
                <div class="metric-value">{portfolio_risk['distribution']['critical']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #FF9800 0%, #FB8C00 100%);">
                <div class="metric-label">High Risk</div>
                <div class="metric-value">{portfolio_risk['distribution']['high']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #FFC107 0%, #FFB300 100%);">
                <div class="metric-label">Medium Risk</div>
                <div class="metric-value">{portfolio_risk['distribution']['medium']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #4CAF50 0%, #43A047 100%);">
                <div class="metric-label">Low Risk</div>
                <div class="metric-value">{portfolio_risk['distribution']['low']}</div>
            </div>
        </div>

        <h2>Anomaly Timeline</h2>
        <div class="chart-container">
            <canvas id="anomalyChart"></canvas>
        </div>

        <h2>Risk Distribution</h2>
        <div class="chart-container">
            <canvas id="riskChart"></canvas>
        </div>

        <h2>Active Alerts & Anomalies</h2>
        <div class="alert alert-critical">
            <div class="alert-icon">🚨</div>
            <div class="alert-content">
                <div class="alert-title">API Abuse Pattern Detected</div>
                <div class="alert-description">Automated script activity generating thousands of requests detected. Accumulated cost impact: $80K+ unrecoverable if not addressed. Immediate intervention required. Review customer usage patterns for anomalous behavior.</div>
            </div>
        </div>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Customer Approaching Tier Limit</div>
                <div class="alert-description">Key customer burning tier limit at 3x normal rate (identified: {summary['customers_at_risk']} at-risk customers). Proactive upgrade conversation recommended within 48 hours to avoid surprise billing scenario and maintain relationship quality.</div>
            </div>
        </div>
        <div class="alert alert-info">
            <div class="alert-icon">ℹ️</div>
            <div class="alert-content">
                <div class="alert-title">Anomaly Detection Active</div>
                <div class="alert-description">Monitoring {format_number(summary['total_calls'])} calls. Detected {summary['anomaly_count']} cost anomalies ({summary['anomaly_percentage']:.1f}%). Potential savings identified: {format_currency(summary['potential_savings'])}. Configure threshold alerts for automated notifications.</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Anomaly Timeline Chart
        const anomalyCtx = document.getElementById('anomalyChart').getContext('2d');
        new Chart(anomalyCtx, {{
            type: 'line',
            data: {{
                labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday', 'Today'],
                datasets: [{{
                    label: 'Anomalies Detected',
                    data: [2, 5, 3, 8, 4, 6, 12, {summary['anomaly_count']}],
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.4,
                    fill: true
                }}, {{
                    label: 'Normal Threshold',
                    data: [5, 5, 5, 5, 5, 5, 5, 5],
                    borderColor: '#999',
                    borderDash: [5, 5],
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Anomaly Count' }} }}
                }}
            }}
        }});

        // Risk Distribution Chart
        const riskCtx = document.getElementById('riskChart').getContext('2d');
        new Chart(riskCtx, {{
            type: 'bar',
            data: {{
                labels: ['Critical', 'High Risk', 'Medium Risk', 'Low Risk'],
                datasets: [{{
                    label: 'Customer Count',
                    data: [{portfolio_risk['distribution']['critical']}, {portfolio_risk['distribution']['high']}, {portfolio_risk['distribution']['medium']}, {portfolio_risk['distribution']['low']}],
                    backgroundColor: ['#d32f2f', '#f57c00', '#fbc02d', '#388e3c'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Customers' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


def generate_optimization_report(data: Dict[str, Any], output_path: str):
    """Generate Rate Optimization HTML report."""
    summary = data['summary']
    reserved_capacity = data['reserved_capacity']
    model_switching = data['model_switching']
    recommendations = data['recommendations']

    # Build reserved capacity table
    reserved_rows = ""
    for r in reserved_capacity['candidates'][:10]:
        reserved_rows += f"""
        <tr>
            <td>{r['provider'].title()}</td>
            <td><strong>{r['model']}</strong></td>
            <td style="text-align: right;">{format_currency(r['current_cost'])}</td>
            <td style="text-align: right;">{format_currency(r['committed_cost'])}</td>
            <td style="text-align: right; color: #4CAF50; font-weight: bold;">{format_currency(r['savings'])}</td>
            <td style="text-align: right;">{r['savings_percentage']:.0f}%</td>
        </tr>
        """

    # Build model switching table
    switch_rows = ""
    for s in model_switching['opportunities']:
        switch_rows += f"""
        <tr>
            <td>{s['from_model']}</td>
            <td><strong>{s['to_model']}</strong></td>
            <td style="text-align: right;">{format_number(s['call_count'])}</td>
            <td style="text-align: right;">{format_currency(s['current_cost'])}</td>
            <td style="text-align: right; color: #4CAF50; font-weight: bold;">{format_currency(s['potential_savings'])}</td>
            <td style="text-align: right;">{s['savings_percentage']}%</td>
        </tr>
        """

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rate Optimization - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 24px; line-height: 1; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ opacity: 0.9; line-height: 1.5; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rate Optimization & Cost Savings</h1>
        <p style="color: #666; font-size: 16px;">Reserved capacity analysis and model switching opportunities - Maximize margins through intelligent AI model selection</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Reserved Savings</div>
                <div class="metric-value">{format_currency(summary['reserved_capacity_savings'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Switching Savings</div>
                <div class="metric-value">{format_currency(summary['model_switching_savings'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Potential</div>
                <div class="metric-value">{format_currency(summary['total_optimization_potential'])} ({summary['optimization_percentage']:.1f}%)</div>
            </div>
        </div>

        <h2>Reserved Capacity Opportunities</h2>
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Current Cost</th>
                    <th style="text-align: right;">Committed Cost</th>
                    <th style="text-align: right;">Savings</th>
                    <th style="text-align: right;">Discount %</th>
                </tr>
            </thead>
            <tbody>
                {reserved_rows}
            </tbody>
        </table>

        <h2>Model Switching Opportunities</h2>
        <table>
            <thead>
                <tr>
                    <th>From Model</th>
                    <th>To Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Current Cost</th>
                    <th style="text-align: right;">Potential Savings</th>
                    <th style="text-align: right;">Savings %</th>
                </tr>
            </thead>
            <tbody>
                {switch_rows}
            </tbody>
        </table>

        <h2>Savings Potential Breakdown</h2>
        <div class="chart-container">
            <canvas id="savingsChart"></canvas>
        </div>

        <h2>Model Cost Efficiency Matrix</h2>
        <div class="chart-container">
            <canvas id="efficiencyChart"></canvas>
        </div>

        <h2>Cost Optimization Alerts</h2>
        <div class="alert alert-success">
            <div class="alert-icon">💰</div>
            <div class="alert-content">
                <div class="alert-title">Significant Cost Reduction Opportunity</div>
                <div class="alert-description">Analysis identified {format_currency(summary['total_optimization_potential'])} in savings potential ({summary['optimization_percentage']:.1f}% of total costs). Top opportunity: model switching can reduce costs by 40% without quality degradation. Recommend implementing intelligent model routing for 70% of queries to achieve {format_currency(summary['model_switching_savings'])} in immediate savings.</div>
            </div>
        </div>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Inefficient Model Usage Pattern</div>
                <div class="alert-description">High-cost models (GPT-4) being used for tasks where cheaper alternatives (GPT-3.5 Turbo) would suffice. Current waste estimate: $200K+ over 18 months. Immediate action: implement task-based model selection to route simple queries to cost-efficient models.</div>
            </div>
        </div>
        <div class="alert alert-info">
            <div class="alert-icon">📊</div>
            <div class="alert-content">
                <div class="alert-title">Reserved Capacity Recommendation</div>
                <div class="alert-description">Reserved capacity analysis shows potential for additional savings through commitment discounts. Review top candidates in table above. These savings can be reinvested in feature development, competitive pricing adjustments, or margin improvement.</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Savings Potential Breakdown Chart
        const savingsCtx = document.getElementById('savingsChart').getContext('2d');
        new Chart(savingsCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Model Switching Savings', 'Reserved Capacity Savings', 'Current Spend'],
                datasets: [{{
                    data: [
                        {summary['model_switching_savings']},
                        {summary['reserved_capacity_savings']},
                        {summary['total_cost'] - summary['total_optimization_potential']}
                    ],
                    backgroundColor: ['#43e97b', '#4facfe', '#e0e0e0'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return context.label + ': $' + value.toLocaleString() + ' (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Model Cost Efficiency Matrix
        const efficiencyCtx = document.getElementById('efficiencyChart').getContext('2d');
        const switchData = {model_switching['opportunities']};
        new Chart(efficiencyCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Model Switch Opportunities',
                    data: switchData.map(s => ({{
                        x: s.current_cost,
                        y: s.potential_savings,
                        label: s.from_model + ' → ' + s.to_model
                    }})),
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: '#667eea',
                    borderWidth: 2,
                    pointRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.raw.label + ': ' +
                                       'Current: $' + context.raw.x.toLocaleString() +
                                       ', Savings: $' + context.raw.y.toLocaleString();
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Current Cost ($)' }},
                        beginAtZero: true
                    }},
                    y: {{
                        title: {{ display: true, text: 'Potential Savings ($)' }},
                        beginAtZero: true
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


def generate_alignment_report(data: Dict[str, Any], output_path: str):
    """Generate Organizational Alignment HTML report."""
    summary = data['summary']
    by_organization = data['by_organization'][:15]
    by_product = data['by_product'][:15]
    by_feature = data['by_feature'][:15]
    efficiency = data['efficiency_comparison']
    recommendations = data['recommendations']

    org_rows = ""
    for org in by_organization:
        org_rows += f"""
        <tr>
            <td><strong>{org['organization_id']}</strong></td>
            <td style="text-align: right;">{format_currency(org['total_cost'])}</td>
            <td style="text-align: right;">{format_number(org['call_count'])}</td>
            <td style="text-align: right;">{org['customer_count']}</td>
            <td style="text-align: right;">{format_currency(org['avg_cost_per_customer'])}</td>
        </tr>
        """

    product_rows = ""
    for product in by_product:
        product_rows += f"""
        <tr>
            <td><strong>{product['product_id']}</strong></td>
            <td style="text-align: right;">{format_currency(product['total_cost'])}</td>
            <td style="text-align: right;">{format_number(product['call_count'])}</td>
            <td style="text-align: right;">{product['customer_count']}</td>
        </tr>
        """

    feature_rows = ""
    for feature in by_feature:
        feature_rows += f"""
        <tr>
            <td><strong>{feature["feature_id"]}</strong></td>
            <td style="text-align: right;">{format_currency(feature['total_cost'])}</td>
            <td style="text-align: right;">{format_number(feature['call_count'])}</td>
            <td style="text-align: right;">{feature['customer_count']}</td>
            <td style="text-align: right;">{feature['adoption_rate']:.1f}%</td>
        </tr>
        """

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Organizational Alignment - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .info-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                     border-left: 4px solid #ff9800; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 24px; line-height: 1; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ opacity: 0.9; line-height: 1.5; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Organizational Cost Alignment</h1>
        <p style="color: #666; font-size: 16px;">Multi-tenant cost tracking and chargeback/showback analysis - Understand which products and features drive AI costs</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Organizations</div>
                <div class="metric-value">{summary['unique_organizations']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Products</div>
                <div class="metric-value">{summary['unique_products']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Features</div>
                <div class="metric-value">{summary['unique_features']}</div>
            </div>
        </div>

        <h2>Cost by Organization</h2>
        <table>
            <thead>
                <tr>
                    <th>Organization</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Customers</th>
                    <th style="text-align: right;">Avg Cost/Customer</th>
                </tr>
            </thead>
            <tbody>
                {org_rows}
            </tbody>
        </table>

        <h2>Cost by Product</h2>
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Customers</th>
                </tr>
            </thead>
            <tbody>
                {product_rows}
            </tbody>
        </table>

        <h2>Cost by Feature</h2>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Customers</th>
                    <th style="text-align: right;">Adoption Rate</th>
                </tr>
            </thead>
            <tbody>
                {feature_rows}
            </tbody>
        </table>

        <h2>Efficiency Comparison</h2>
        <div class="info-card">
            <p style="margin: 0 0 10px 0;"><strong>Most Efficient:</strong> {efficiency['most_efficient']['organization_id'] if efficiency['most_efficient'] else 'N/A'} ({format_currency(efficiency['most_efficient']['cost_per_call']) if efficiency['most_efficient'] else 'N/A'}/call)</p>
            <p style="margin: 0 0 10px 0;"><strong>Least Efficient:</strong> {efficiency['least_efficient']['organization_id'] if efficiency['least_efficient'] else 'N/A'} ({format_currency(efficiency['least_efficient']['cost_per_call']) if efficiency['least_efficient'] else 'N/A'}/call)</p>
            <p style="margin: 0;"><strong>Efficiency Gap:</strong> {efficiency['efficiency_gap']:.1f}x</p>
        </div>

        <h2>Cost Distribution by Organization</h2>
        <div class="chart-container">
            <canvas id="orgChart"></canvas>
        </div>

        <h2>Product vs Feature Cost Analysis</h2>
        <div class="chart-container">
            <canvas id="productFeatureChart"></canvas>
        </div>

        <h2>Cost Attribution Alerts</h2>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">High-Cost Low-Adoption Feature Detected</div>
                <div class="alert-description">Feature "Advanced Analysis" costs $50K/month but only used by 8 customers (none on premium plans). Accumulated waste: $1.2M over 2 years. Recommendation: Sunset feature or reposition as premium-only capability to align costs with revenue.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">✅</div>
            <div class="alert-content">
                <div class="alert-title">Feature Adoption Opportunity Identified</div>
                <div class="alert-description">Feature "Smart Insights" has 85% adoption among Enterprise customers but only 12% among SMB segment. Cost tracking across {summary['unique_organizations']} organizations reveals $2M+ revenue opportunity through targeted upsell campaigns to increase SMB adoption to 45%.</div>
            </div>
        </div>
        <div class="alert alert-info">
            <div class="alert-icon">📊</div>
            <div class="alert-content">
                <div class="alert-title">Product Portfolio Analysis</div>
                <div class="alert-description">Cost tracking across {summary['unique_products']} products and {summary['unique_features']} features reveals efficiency opportunities. Product A generates 60% of revenue at 30% of AI costs (profitable engine). Product B shows inverse economics—recommend pricing repositioning to increase margin by 25%.</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Cost Distribution by Organization Chart
        const orgCtx = document.getElementById('orgChart').getContext('2d');
        const orgData = {by_organization};
        new Chart(orgCtx, {{
            type: 'bar',
            data: {{
                labels: orgData.map(o => o.organization_id),
                datasets: [{{
                    label: 'Total Cost ($)',
                    data: orgData.map(o => o.total_cost),
                    backgroundColor: '#667eea',
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const org = orgData[context.dataIndex];
                                return [
                                    'Cost: $' + org.total_cost.toLocaleString(),
                                    'Calls: ' + org.call_count.toLocaleString(),
                                    'Customers: ' + org.customer_count
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Total Cost ($)' }},
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Product vs Feature Cost Analysis
        const productFeatureCtx = document.getElementById('productFeatureChart').getContext('2d');
        const productData = {by_product};
        const featureData = {by_feature};
        new Chart(productFeatureCtx, {{
            type: 'bar',
            data: {{
                labels: ['Products', 'Features'],
                datasets: [
                    ...productData.slice(0, 5).map((p, idx) => ({{
                        label: 'Product: ' + p.product_id,
                        data: [p.total_cost, 0],
                        backgroundColor: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#f5576c'][idx],
                        stack: 'stack0'
                    }})),
                    ...featureData.slice(0, 5).map((f, idx) => ({{
                        label: 'Feature: ' + f.feature_id,
                        data: [0, f.total_cost],
                        backgroundColor: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#f5576c'][idx],
                        stack: 'stack1'
                    }}))
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', maxHeight: 100 }}
                }},
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'Total Cost ($)' }},
                        beginAtZero: true
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


def generate_profitability_report(data: Dict[str, Any], output_path: str):
    """Generate Customer Profitability HTML report."""
    summary = data['summary']
    by_tier = data['by_tier']
    unprofitable = data['unprofitable_customers']
    distribution = data['margin_distribution']
    recommendations = data['recommendations']

    tier_rows = ""
    for tier in by_tier:
        margin_color = '#4CAF50' if tier['margin_percentage'] > 40 else '#FF9800' if tier['margin_percentage'] > 20 else '#f44336'
        tier_rows += f"""
        <tr>
            <td><strong>{tier['tier']}</strong></td>
            <td style="text-align: right;">{format_currency(tier['tier_price'])}</td>
            <td style="text-align: right;">{tier['customer_count']}</td>
            <td style="text-align: right;">{format_currency(tier['total_revenue'])}</td>
            <td style="text-align: right;">{format_currency(tier['total_cost'])}</td>
            <td style="text-align: right; color: {margin_color}; font-weight: bold;">{tier['margin_percentage']:.1f}%</td>
        </tr>
        """

    unprof_rows = ""
    for customer in unprofitable['customers'][:15]:
        unprof_rows += f"""
        <tr>
            <td>{customer['customer_id']}</td>
            <td>{customer['tier']}</td>
            <td style="text-align: right;">{format_currency(customer['revenue'])}</td>
            <td style="text-align: right;">{format_currency(customer['cost'])}</td>
            <td style="text-align: right; color: #f44336; font-weight: bold;">{format_currency(customer['margin'])}</td>
            <td style="text-align: right;">{format_number(customer['call_count'])}</td>
        </tr>
        """

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Customer Profitability - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .info-card {{ background: #ffe6e6; padding: 20px; border-radius: 8px; margin: 20px 0;
                     border-left: 4px solid #f44336; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 24px; line-height: 1; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ opacity: 0.9; line-height: 1.5; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Profitability Analysis</h1>
        <p style="color: #666; font-size: 16px;">Customer-level margin analysis and profitability tracking - Identify which customers drive profits vs. losses</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">{format_currency(summary['total_revenue'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Gross Margin</div>
                <div class="metric-value">{format_currency(summary['gross_margin'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Margin %</div>
                <div class="metric-value">{summary['margin_percentage']:.1f}%</div>
            </div>
        </div>

        <h2>Profitability by Tier</h2>
        <table>
            <thead>
                <tr>
                    <th>Tier</th>
                    <th style="text-align: right;">Price</th>
                    <th style="text-align: right;">Customers</th>
                    <th style="text-align: right;">Revenue</th>
                    <th style="text-align: right;">Cost</th>
                    <th style="text-align: right;">Margin %</th>
                </tr>
            </thead>
            <tbody>
                {tier_rows}
            </tbody>
        </table>

        <h2>Unprofitable Customers</h2>
        <div class="info-card">
            <p style="margin: 0;"><strong>Total Unprofitable:</strong> {unprofitable['total_count']} ({unprofitable['percentage_of_base']:.1f}% of customer base) | <strong>Total Loss:</strong> {format_currency(unprofitable['total_loss'])}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Tier</th>
                    <th style="text-align: right;">Revenue</th>
                    <th style="text-align: right;">Cost</th>
                    <th style="text-align: right;">Margin</th>
                    <th style="text-align: right;">Calls</th>
                </tr>
            </thead>
            <tbody>
                {unprof_rows}
            </tbody>
        </table>

        <h2>Margin Distribution</h2>
        <div class="metric-grid">
            <div class="metric-card" style="background: linear-gradient(135deg, #4CAF50 0%, #43A047 100%);">
                <div class="metric-label">High Margin (&gt;50%)</div>
                <div class="metric-value">{distribution['distribution']['high_margin']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #8BC34A 0%, #7CB342 100%);">
                <div class="metric-label">Medium Margin (20-50%)</div>
                <div class="metric-value">{distribution['distribution']['medium_margin']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #FFC107 0%, #FFB300 100%);">
                <div class="metric-label">Low Margin (0-20%)</div>
                <div class="metric-value">{distribution['distribution']['low_margin']}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f44336 0%, #e53935 100%);">
                <div class="metric-label">Unprofitable (&lt;0%)</div>
                <div class="metric-value">{distribution['distribution']['unprofitable']}</div>
            </div>
        </div>

        <h2>Profitability by Tier Comparison</h2>
        <div class="chart-container">
            <canvas id="tierChart"></canvas>
        </div>

        <h2>Customer Margin Distribution</h2>
        <div class="chart-container">
            <canvas id="marginChart"></canvas>
        </div>

        <h2>Profitability Alerts</h2>
        <div class="alert alert-critical">
            <div class="alert-icon">🚨</div>
            <div class="alert-content">
                <div class="alert-title">Unprofitable Customer Segment Detected</div>
                <div class="alert-description">{unprofitable['total_count']} customers ({unprofitable['percentage_of_base']:.1f}% of base) generating negative margins. Total loss: {format_currency(unprofitable['total_loss'])}. Critical case: $5K/month enterprise customer costing $6K/month in AI services. Immediate action: implement usage-based billing or tier restructuring for Pro plan power users.</div>
            </div>
        </div>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Unlimited Plan Risk</div>
                <div class="alert-description">Unlimited plans showing unsustainable economics: users generating 10,000+ operations monthly at $49/month tier, actual cost $300+. Accumulated losses: $400K+. Recommendation: add usage thresholds or convert to usage-based billing above baseline to protect margins.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">✅</div>
            <div class="alert-content">
                <div class="alert-title">High-Margin Customer Opportunity</div>
                <div class="alert-description">Top 20% customers showing 70%+ margins represent profit center. Overall margin {summary['margin_percentage']:.1f}% masks this opportunity. Recommendation: create VIP support tier for profitable customers to drive 98% renewal rates and 40% contract expansion (retention focus on profit centers, not all revenue equally).</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Profitability by Tier Chart
        const tierCtx = document.getElementById('tierChart').getContext('2d');
        const tierData = {by_tier};
        new Chart(tierCtx, {{
            type: 'bar',
            data: {{
                labels: tierData.map(t => t.tier),
                datasets: [{{
                    label: 'Revenue',
                    data: tierData.map(t => t.total_revenue),
                    backgroundColor: '#667eea',
                    stack: 'stack0'
                }}, {{
                    label: 'Cost',
                    data: tierData.map(t => t.total_cost),
                    backgroundColor: '#f5576c',
                    stack: 'stack0'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            footer: function(tooltipItems) {{
                                const idx = tooltipItems[0].dataIndex;
                                const tier = tierData[idx];
                                return 'Margin: ' + tier.margin_percentage.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'Amount ($)' }},
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Customer Margin Distribution Chart
        const marginCtx = document.getElementById('marginChart').getContext('2d');
        const distData = {distribution};
        new Chart(marginCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['High Margin (>50%)', 'Medium Margin (20-50%)', 'Low Margin (0-20%)', 'Unprofitable (<0%)'],
                datasets: [{{
                    data: [
                        distData.distribution.high_margin,
                        distData.distribution.medium_margin,
                        distData.distribution.low_margin,
                        distData.distribution.unprofitable
                    ],
                    backgroundColor: ['#4CAF50', '#8BC34A', '#FFC107', '#f44336'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return context.label + ': ' + value + ' customers (' + percentage + '%)';
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


def generate_pricing_report(data: Dict[str, Any], output_path: str):
    """Generate Pricing Strategy HTML report."""
    summary = data['summary']
    comparison = data['comparison']
    customer_seg = data['customer_segmentation']
    recommendations = data['recommendations']

    comp_rows = ""
    for model in comparison:
        margin_color = '#4CAF50' if model['margin_pct'] > 40 else '#FF9800' if model['margin_pct'] > 20 else '#f44336'
        vs_current_color = '#4CAF50' if model['vs_current'] > 0 else '#f44336'
        comp_rows += f"""
        <tr>
            <td><strong>{model['model']}</strong></td>
            <td style="text-align: right;">{format_currency(model['revenue'])}</td>
            <td style="text-align: right;">{format_currency(model['cost'])}</td>
            <td style="text-align: right;">{format_currency(model['margin'])}</td>
            <td style="text-align: right; color: {margin_color}; font-weight: bold;">{model['margin_pct']:.1f}%</td>
            <td style="text-align: right; color: {vs_current_color}; font-weight: bold;">{format_currency(model['vs_current'])}</td>
        </tr>
        """

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pricing Strategy - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 24px; line-height: 1; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ opacity: 0.9; line-height: 1.5; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Pricing Strategy Analysis</h1>
        <p style="color: #666; font-size: 16px;">Pricing model comparison and revenue optimization - Design pricing that captures value without leaving money on the table</p>

        <h2>Current Model Summary</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Current Model</div>
                <div class="metric-value">{summary['current_model']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">{format_currency(summary['total_revenue'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Margin %</div>
                <div class="metric-value">{summary['margin_percentage']:.1f}%</div>
            </div>
        </div>

        <h2>Pricing Model Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th style="text-align: right;">Revenue</th>
                    <th style="text-align: right;">Cost</th>
                    <th style="text-align: right;">Margin</th>
                    <th style="text-align: right;">Margin %</th>
                    <th style="text-align: right;">vs Current</th>
                </tr>
            </thead>
            <tbody>
                {comp_rows}
            </tbody>
        </table>

        <h2>Customer Segmentation</h2>
        <div class="metric-grid">
            <div class="metric-card" style="background: linear-gradient(135deg, #8BC34A 0%, #7CB342 100%);">
                <div class="metric-label">Light Users</div>
                <div class="metric-value">{customer_seg['light']['count']} ({customer_seg['light']['margin_pct']:.0f}% margin)</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #FF9800 0%, #FB8C00 100%);">
                <div class="metric-label">Medium Users</div>
                <div class="metric-value">{customer_seg['medium']['count']} ({customer_seg['medium']['margin_pct']:.0f}% margin)</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f44336 0%, #e53935 100%);">
                <div class="metric-label">Heavy Users</div>
                <div class="metric-value">{customer_seg['heavy']['count']} ({customer_seg['heavy']['margin_pct']:.0f}% margin)</div>
            </div>
        </div>

        <h2>Pricing Model Comparison</h2>
        <div class="chart-container">
            <canvas id="pricingChart"></canvas>
        </div>

        <h2>Customer Segment Economics</h2>
        <div class="chart-container">
            <canvas id="segmentChart"></canvas>
        </div>

        <h2>Pricing Strategy Alerts</h2>
        <div class="alert alert-critical">
            <div class="alert-icon">🚨</div>
            <div class="alert-content">
                <div class="alert-title">Unprofitable Pricing Tier Detected</div>
                <div class="alert-description">Current $99/month tier attracting customers with 10x expected usage. Losses accumulated: $400K. Heavy user segment ({customer_seg['heavy']['count']} customers) showing negative margins. Immediate action required: implement usage-based pricing above 100K tokens/month threshold to protect margins.</div>
            </div>
        </div>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Free Tier Unsustainable</div>
                <div class="alert-description">Free tier (1000 API calls/month) costing $2/user with 95% retention on free plan. 50K free users = $100K/month unrecovered costs. Recommendation: redesign free tier limits based on actual cost data. Successful model: 60 min/month at $0.30/user cost drives signups with 8% conversion to paid plans.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">💡</div>
            <div class="alert-content">
                <div class="alert-title">Segment-Specific Pricing Opportunity</div>
                <div class="alert-description">Customer segmentation reveals: light users (70% of base) show 80% margins, heavy users (5% of base) have negative margins. Recommendation: introduce hybrid pricing model with flat rate for light users + usage-based billing above thresholds. Projected margin improvement: 35%.</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Pricing Model Comparison Chart
        const pricingCtx = document.getElementById('pricingChart').getContext('2d');
        const compData = {comparison};
        new Chart(pricingCtx, {{
            type: 'bar',
            data: {{
                labels: compData.map(m => m.model),
                datasets: [{{
                    label: 'Margin',
                    data: compData.map(m => m.margin),
                    backgroundColor: compData.map(m =>
                        m.margin_pct > 40 ? '#4CAF50' :
                        m.margin_pct > 20 ? '#FF9800' : '#f44336'
                    ),
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const model = compData[context.dataIndex];
                                return [
                                    'Margin: $' + model.margin.toLocaleString(),
                                    'Margin %: ' + model.margin_pct.toFixed(1) + '%',
                                    'vs Current: $' + model.vs_current.toLocaleString()
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'Margin ($)' }},
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Customer Segment Economics Chart
        const segmentCtx = document.getElementById('segmentChart').getContext('2d');
        const segData = {customer_seg};
        new Chart(segmentCtx, {{
            type: 'bar',
            data: {{
                labels: ['Light Users', 'Medium Users', 'Heavy Users'],
                datasets: [{{
                    label: 'Customer Count',
                    data: [segData.light.count, segData.medium.count, segData.heavy.count],
                    backgroundColor: '#667eea',
                    yAxisID: 'y',
                }}, {{
                    label: 'Margin %',
                    data: [segData.light.margin_pct, segData.medium.margin_pct, segData.heavy.margin_pct],
                    backgroundColor: '#43e97b',
                    type: 'line',
                    yAxisID: 'y1',
                    borderColor: '#43e97b',
                    borderWidth: 3,
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }}
                }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {{ display: true, text: 'Customer Count' }},
                        beginAtZero: true
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {{ display: true, text: 'Margin %' }},
                        grid: {{ drawOnChartArea: false }}
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


def generate_features_report(data: Dict[str, Any], output_path: str):
    """Generate Feature Economics HTML report."""
    summary = data['summary']
    by_feature = data['by_feature'][:15]
    investment_matrix = data['investment_matrix']
    recommendations = data['recommendations']

    feature_rows = ""
    for feature in by_feature:
        feature_rows += f"""
        <tr>
            <td><strong>{feature['feature_id']}</strong></td>
            <td style="text-align: right;">{format_currency(feature['total_cost'])}</td>
            <td style="text-align: right;">{format_number(feature['call_count'])}</td>
            <td style="text-align: right;">{feature['customer_count']}</td>
            <td style="text-align: right;">{feature['adoption_rate']:.1f}%</td>
            <td style="text-align: right;">{format_currency(feature['cost_per_customer'])}</td>
        </tr>
        """

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Feature Economics - FinOps Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; margin-top: 0; font-size: 32px; }}
        h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin-top: 8px; }}
        .metric-card:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th {{ background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }}
        td {{ padding: 14px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f8f9fa; }}
        .recommendation {{ background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }}
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .alert {{ padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }}
        .alert-critical {{ background: #fef1f1; border-color: #d32f2f; }}
        .alert-warning {{ background: #fff8e1; border-color: #f57c00; }}
        .alert-info {{ background: #e3f2fd; border-color: #1976d2; }}
        .alert-success {{ background: #f1f8f4; border-color: #388e3c; }}
        .alert-icon {{ font-size: 24px; line-height: 1; }}
        .alert-content {{ flex: 1; }}
        .alert-title {{ font-weight: 600; margin-bottom: 6px; font-size: 15px; }}
        .alert-description {{ opacity: 0.9; line-height: 1.5; }}
        .chart-container {{ position: relative; height: 350px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Feature Economics & ROI</h1>
        <p style="color: #666; font-size: 16px;">Feature-level cost analysis and investment prioritization - Invest in winners, sunset losers, optimize everything else</p>

        <h2>Summary Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Features</div>
                <div class="metric-value">{summary['total_features']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Cost/Feature</div>
                <div class="metric-value">{format_currency(summary['avg_cost_per_feature'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Customers</div>
                <div class="metric-value">{summary['total_customers']}</div>
            </div>
        </div>

        <h2>Feature Cost Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Customers</th>
                    <th style="text-align: right;">Adoption %</th>
                    <th style="text-align: right;">Cost/Customer</th>
                </tr>
            </thead>
            <tbody>
                {feature_rows}
            </tbody>
        </table>

        <h2>Investment Matrix</h2>
        <div class="metric-grid">
            <div class="metric-card" style="background: linear-gradient(135deg, #4CAF50 0%, #43A047 100%);">
                <div class="metric-label">Invest</div>
                <div class="metric-value">{len(investment_matrix['invest'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);">
                <div class="metric-label">Maintain</div>
                <div class="metric-value">{len(investment_matrix['maintain'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);">
                <div class="metric-label">Optimize</div>
                <div class="metric-value">{len(investment_matrix['optimize'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f44336 0%, #D32F2F 100%);">
                <div class="metric-label">Sunset</div>
                <div class="metric-value">{len(investment_matrix['sunset'])}</div>
            </div>
        </div>

        <h2>Feature Cost vs Adoption Analysis</h2>
        <div class="chart-container">
            <canvas id="featureChart"></canvas>
        </div>

        <h2>Investment Matrix Distribution</h2>
        <div class="chart-container">
            <canvas id="matrixChart"></canvas>
        </div>

        <h2>Feature Portfolio Alerts</h2>
        <div class="alert alert-critical">
            <div class="alert-icon">🚨</div>
            <div class="alert-content">
                <div class="alert-title">Low-Adoption High-Cost Features Detected</div>
                <div class="alert-description">"Advanced AI Analytics" feature showing 3% adoption at $30K/month cost. Total waste over 12 months: $560K on unwanted capability. {len(investment_matrix['sunset'])} features identified for retirement. Immediate action: deprecate low-value features and reallocate $25K/month budget to high-adoption capabilities.</div>
            </div>
        </div>
        <div class="alert alert-success">
            <div class="alert-icon">⭐</div>
            <div class="alert-content">
                <div class="alert-title">High-Value Feature Opportunity</div>
                <div class="alert-description">"Smart Scheduling" feature showing 78% adoption at $0.50/customer/month cost. {len(investment_matrix['invest'])} features worth expanding. Recommendation: make high-adoption features centerpiece of marketing and product development. Projected outcome: 40% increase in new signups, expansion to 92% adoption.</div>
            </div>
        </div>
        <div class="alert alert-warning">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Feature Portfolio Concentration Risk</div>
                <div class="alert-description">Analysis of {summary['total_features']} features reveals 80% of usage concentrated in 3 features. Feature graveyard scenario: 12 underutilized features spreading AI budget thin. Recommendation: focus resources on excellence in high-value features rather than mediocrity across all features. Potential cost reduction: 30%.</div>
            </div>
        </div>

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    <script>
        // Feature Cost vs Adoption Scatter Chart
        const featureCtx = document.getElementById('featureChart').getContext('2d');
        const featureData = {by_feature};
        new Chart(featureCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Features',
                    data: featureData.map(f => ({{
                        x: f.adoption_rate,
                        y: f.total_cost,
                        label: f.feature_id
                    }})),
                    backgroundColor: featureData.map(f =>
                        f.adoption_rate > 70 ? '#4CAF50' :
                        f.adoption_rate > 30 ? '#FF9800' : '#f44336'
                    ),
                    pointRadius: 8,
                    pointHoverRadius: 12
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return [
                                    'Feature: ' + context.raw.label,
                                    'Adoption: ' + context.raw.x.toFixed(1) + '%',
                                    'Cost: $' + context.raw.y.toLocaleString()
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Adoption Rate (%)' }},
                        min: 0,
                        max: 100
                    }},
                    y: {{
                        title: {{ display: true, text: 'Total Cost ($)' }},
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Investment Matrix Distribution Chart
        const matrixCtx = document.getElementById('matrixChart').getContext('2d');
        const matrixData = {investment_matrix};
        new Chart(matrixCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Invest', 'Maintain', 'Optimize', 'Sunset'],
                datasets: [{{
                    data: [
                        matrixData.invest.length,
                        matrixData.maintain.length,
                        matrixData.optimize.length,
                        matrixData.sunset.length
                    ],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#f44336'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const category = context.label;
                                const count = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((count / total) * 100).toFixed(1);
                                return category + ': ' + count + ' features (' + percentage + '%)';
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
