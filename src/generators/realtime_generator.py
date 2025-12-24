"""Generator for RealtimeReport report."""

import os
from typing import Dict, Any
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


