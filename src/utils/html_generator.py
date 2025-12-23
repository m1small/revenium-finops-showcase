"""HTML Report Generation Utilities."""

import os
from datetime import datetime
from typing import Dict, Any, List


def format_currency(value: float) -> str:
    """Format value as currency."""
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
            <td style="text-align: right;">{format_currency(m['cost_per_1k_tokens'])}</td>
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
    <title>Understanding Usage & Cost - Revenium FinOps</title>
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
        .section {{ margin: 40px 0; }}
        .efficiency-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                           border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Understanding Usage & Cost</h1>
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
            <p style="margin: 0 0 10px 0;"><strong>Average Cost per 1K Tokens:</strong> {format_currency(efficiency['overall_cost_per_1k_tokens'])}</p>
            {f'<p style="margin: 0 0 5px 0;"><strong>Most Efficient:</strong> {efficiency["most_efficient"]["model"]} at {format_currency(efficiency["most_efficient"]["cost_per_1k_tokens"])}/1K tokens</p>' if efficiency.get('most_efficient') else ''}
            {f'<p style="margin: 0; color: #666;"><strong>Least Efficient:</strong> {efficiency["least_efficient"]["model"]} at {format_currency(efficiency["least_efficient"]["cost_per_1k_tokens"])}/1K tokens</p>' if efficiency.get('least_efficient') else ''}
        </div>

        <h2>Optimization Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
            <td style="text-align: right;">{format_currency(m['cost_per_1k_tokens'])}</td>
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
    <title>Performance Tracking - Revenium FinOps</title>
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
        .timestamp {{ color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .info-card {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;
                     border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Tracking</h1>
        <p style="color: #666; font-size: 16px;">Model efficiency, latency percentiles, and SLA compliance analysis</p>

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

        <h2>Optimization Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Real-Time Decision Making - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Real-Time Decision Making</h1>
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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Rate Optimization - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Rate Optimization</h1>
        <p style="color: #666; font-size: 16px;">Reserved capacity analysis and model switching opportunities</p>

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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Organizational Alignment - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Organizational Alignment</h1>
        <p style="color: #666; font-size: 16px;">Multi-tenant cost tracking and chargeback/showback analysis</p>

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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Customer Profitability - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Profitability</h1>
        <p style="color: #666; font-size: 16px;">Customer-level margin analysis and profitability tracking</p>

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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Pricing Strategy - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Pricing Strategy</h1>
        <p style="color: #666; font-size: 16px;">Pricing model comparison and revenue optimization</p>

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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
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
    <title>Feature Economics - Revenium FinOps</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Feature Economics</h1>
        <p style="color: #666; font-size: 16px;">Feature-level cost analysis and investment prioritization</p>

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

        <h2>Recommendations</h2>
        {rec_html if rec_html else '<p style="color: #666;">No recommendations at this time.</p>'}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
