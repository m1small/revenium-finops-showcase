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
        .metric-card:nth-child(5) {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
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
        .value-highlight {{ background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;
                           border-left: 4px solid #4CAF50; }}
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Understanding Usage & Cost</h1>
        <p style="color: #666; font-size: 16px;">Comprehensive cost allocation, forecasting, and efficiency analysis - Track every AI service call to maximize profitability</p>

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

        <h2>AI Monetization Value - How Revenium Helps</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Track Every Dollar of AI Service Costs</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">With precise cost tracking across {format_number(summary['total_calls'])} calls and {format_number(summary['unique_customers'])} customers, Revenium enables you to allocate AI costs to specific products, features, and customers. This granular visibility is essential for building profitable AI applications and setting data-driven pricing strategies.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Proactive Cost Management</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">A SaaS company using Revenium discovered that their "Basic" tier customers were consuming 3x more AI tokens than expected. By identifying this pattern early through cost-per-customer analysis, they adjusted their pricing model before losses accumulated, preserving customer relationships while maintaining profitability.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Flying Blind Without Cost Visibility</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without Revenium's detailed cost tracking, companies often discover unprofitable customers only after months of losses. One AI startup lost $50K in uncaptured costs because they couldn't attribute model usage to specific customer accounts, leading to customer churn when forced to implement emergency price increases.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Data-Driven Feature Rollout</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI-powered analytics platform used Revenium's 30-day forecasting ({format_currency(forecast['forecast_30_day'])} projected) to confidently price their new AI summarization feature. They knew exact model costs per customer segment, enabling them to launch with sustainable pricing that drove 40% feature adoption while maintaining healthy margins.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Underpriced Premium Features</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Companies that can't track AI costs per feature often underprice premium AI capabilities. Without Revenium's model-level cost breakdown, one company offered "unlimited AI chat" and quickly discovered some power users were costing $200/month in GPT-4 calls while paying only $49/month—a recipe for failure.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Tracking</h1>
        <p style="color: #666; font-size: 16px;">Model efficiency, latency percentiles, and SLA compliance - Optimize AI service performance for better customer experiences</p>

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

        <h2>AI Service Performance Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Balance Speed, Cost, and Quality</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">Revenium tracks latency, throughput, and SLA compliance across all AI models ({sla_compliance['overall_compliance_pct']:.1f}% overall compliance). This data enables you to choose the right model for each use case—fast models for real-time features, cost-efficient models for batch processing, and premium models where quality justifies the cost.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: SLA-Driven Model Selection</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">A customer support AI chatbot needed sub-second responses. Using Revenium's P95 latency tracking, the team identified Claude Haiku with {summary['p95_latency_ms']}ms P95 latency as the ideal balance of speed and cost. Customer satisfaction scores increased by 25% while staying within budget.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Slow AI Ruins User Experience</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without performance monitoring, a document analysis tool unknowingly used a slow model that took 8+ seconds for simple queries. Users abandoned the feature, and the company didn't realize the performance issue until after losing 60% of their user base. Revenium's latency tracking would have caught this immediately.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Right Model for the Right Task</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI writing assistant used Revenium's efficiency scores to route tasks: GPT-4 for complex creative writing (high quality), Claude Sonnet for editing (balanced), and GPT-3.5 for simple grammar checks (fast and cheap). This intelligent routing increased feature adoption by 50% while reducing costs by 30%.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: One-Size-Fits-All Model Strategy</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Companies that use the same model for all tasks waste money on overkill or deliver poor results with underpowered models. One startup used GPT-4 for everything—including simple keyword extraction—burning $15K/month unnecessarily. Revenium's task-based recommendations prevent this waste.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Real-Time Decision Making</h1>
        <p style="color: #666; font-size: 16px;">Anomaly detection, threshold alerts, and portfolio risk analysis - Catch cost overruns before they impact profitability</p>

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

        <h2>Real-Time AI Cost Control Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Stop Profit Leaks Before They Become Losses</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">Revenium detected {summary['anomaly_count']} cost anomalies and identified {summary['customers_at_risk']} at-risk customers, potentially saving {format_currency(summary['potential_savings'])}. Real-time alerts enable you to intervene before unprofitable usage patterns destroy margins or force difficult conversations with customers.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Early Intervention Saves Customer Relationship</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">When Revenium alerted a B2B SaaS company that a key customer was burning through their tier limit at 3x the normal rate, they proactively reached out to discuss upgrading. The customer appreciated the heads-up, upgraded to Enterprise, and both parties avoided the awkward "surprise bill" scenario.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Surprise Bills Kill Trust</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without real-time monitoring, companies discover cost overruns only at month-end. One platform had to hit customers with $5K+ surprise bills for AI usage, causing immediate churn and reputation damage on social media. Revenium's alerts would have enabled proactive communication instead of reactive damage control.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Usage-Based Alerts Drive Upgrades</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI code assistant used Revenium's threshold alerts to identify power users approaching their limits. They sent timely upgrade prompts with 48-hour warnings, converting 35% of free users to paid plans with zero friction—users felt helped, not pressured.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Uncontrolled API Abuse</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI image generation API without anomaly detection was exploited by users running automated scripts to generate thousands of images. By the time the abuse was discovered, the company had accumulated $80K in unrecoverable OpenAI costs. Revenium's anomaly detection would have flagged this within hours.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rate Optimization</h1>
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

        <h2>Cost Optimization Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Turn AI Spending Into Competitive Advantage</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">Revenium identified {format_currency(summary['total_optimization_potential'])} in potential savings ({summary['optimization_percentage']:.1f}% of total costs) through model switching and reserved capacity. These savings can be reinvested in product development, passed to customers as competitive pricing, or dropped straight to your bottom line.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Transparent Cost Reductions</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">A document AI service used Revenium's model switching analysis to reduce costs by 40% without degrading quality. They passed half the savings to customers through a price cut and kept the other half as margin improvement—winning on both customer satisfaction and profitability.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Hidden Cost Inefficiencies</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Companies that don't analyze model costs often use expensive models for tasks where cheaper alternatives would work fine. One AI startup spent 18 months using GPT-4 for all queries before realizing GPT-3.5 Turbo could handle 70% of requests at 1/10th the cost—wasting over $200K in unnecessary spending.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Cost Savings Fund Feature Expansion</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI email assistant saved {format_currency(summary['model_switching_savings'])} through intelligent model routing. Instead of raising prices, they reinvested the savings into developing new AI features, increasing customer lifetime value by 60% and expanding their product moat against competitors.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Unsustainable Pricing Strategy</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without Revenium's optimization insights, companies often lock in pricing based on inefficient model usage. When competitors launch with optimized costs, these companies face a painful choice: cut prices and lose margin, or maintain prices and lose market share. Both scenarios could have been avoided with proper cost optimization from day one.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Organizational Alignment</h1>
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

        <h2>Product & Feature Intelligence Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Know What's Profitable, What's Not</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">With cost tracking across {summary['unique_organizations']} organizations, {summary['unique_products']} products, and {summary['unique_features']} features, Revenium reveals which parts of your AI portfolio are profitable engines and which are hidden cost centers. This granularity enables data-driven decisions about where to invest and what to sunset.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Feature Adoption Drives Revenue</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">A B2B platform tracked AI feature costs by customer segment and discovered their "Smart Insights" feature had 85% adoption among Enterprise customers but only 12% among SMB customers. They created targeted upsell campaigns for SMB customers, increasing feature adoption to 45% and boosting revenue by $2M annually.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Subsidizing Low-Value Features</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without feature-level cost tracking, companies often subsidize expensive AI features that few customers use. One platform discovered—after 2 years—that their "Advanced Analysis" feature cost $50K/month but was only used by 8 customers, none of whom were on premium plans. That's $1.2M in wasted investment.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Data-Driven Product Strategy</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Using Revenium's product-level cost breakdown, a multi-product AI company identified that "Product A" generated 60% of revenue but only 30% of AI costs, while "Product B" had inverse economics. They doubled down on Product A's roadmap and repositioned Product B at higher prices, increasing overall margin by 25%.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Building in the Dark</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Companies that can't track costs by feature often build expensive capabilities that nobody wants. One startup spent 6 months building an AI-powered recommendation engine that cost $30K/month to run, only to discover users ignored it. With Revenium's adoption rate tracking, they would have validated demand before building.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Profitability</h1>
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

        <h2>Customer-Level Margin Intelligence Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Every Customer's True Profitability, Revealed</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">With {summary['margin_percentage']:.1f}% overall margin but {unprofitable['total_count']} unprofitable customers ({unprofitable['percentage_of_base']:.1f}% of base), Revenium shows that aggregate metrics hide critical details. Customer-level margin tracking enables surgical interventions: upgrade conversations with high-usage customers, usage limits for unprofitable accounts, and retention focus on your profit centers.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: VIP Treatment for Profitable Customers</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI SaaS company used Revenium to identify their top 20% most profitable customers (70%+ margins) and created a VIP support tier with dedicated success managers. These customers renewed at 98% and expanded contracts by an average of 40%, while the company avoided wasting premium support resources on break-even accounts.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Treating All Revenue Equally</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without margin visibility, companies often invest equally in all customers. One platform spent heavily on "enterprise" support for a customer paying $5K/month who was actually costing $6K/month in AI services. They retained an unprofitable customer while neglecting a $2K/month customer with 80% margins who churned to a competitor.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Tier Optimization Based on Usage Patterns</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Using Revenium's profitability data, a chatbot platform discovered their $99/month "Pro" tier attracted power users who cost $150/month in AI services. They restructured pricing with usage-based billing above certain thresholds, converting unprofitable customers to profitable ones and increasing monthly revenue by $80K.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Unlimited Plans Become Unlimited Losses</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Many AI companies launch "unlimited" plans without understanding usage distribution. One startup offered unlimited AI image generation for $49/month and attracted users who generated 10,000+ images monthly, costing $300+ in API fees. Without Revenium's customer margin tracking, they didn't discover the problem until they'd accumulated $400K in losses.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Pricing Strategy</h1>
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

        <h2>Pricing Model Intelligence Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Price Based on Real Costs, Not Guesswork</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">With actual usage data across light, medium, and heavy users showing wildly different margin profiles, Revenium enables you to design pricing tiers that align with actual AI service costs. You can confidently set prices knowing exactly where break-even occurs and which pricing model—subscription, usage-based, or hybrid—maximizes both revenue and margin.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Segment-Specific Pricing Wins Everyone</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI writing tool used Revenium's customer segmentation to discover light users (70% of customers) had 80% margins, while heavy users (5% of customers) had negative margins. They introduced usage-based pricing above 100K tokens/month. Light users loved the simple flat rate, heavy users appreciated fair metering, and the company increased margins by 35%.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: One-Size-Fits-All Pricing Fails</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Many AI companies price based on competitors or gut feeling. One startup copied a competitor's $99/month tier without understanding their own costs. They attracted customers who used 10x more than expected, burning through $400K before they realized the tier was fundamentally unprofitable. Revenium's cost modeling would have caught this before launch.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Free Tier That Actually Works</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">A transcription service used Revenium data to design a free tier with 60 minutes/month that cost them only $0.30/user in AI services. This generous-seeming limit drove 50K signups, converted 8% to paid ($120 MRR), and the "cost" of free users was actually profitable customer acquisition spending with measurable ROI.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Freemium Becomes Free-hemorrhaging</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without cost visibility, companies set free tier limits based on "what feels right." One AI app offered 1000 free API calls/month, thinking users would upgrade. Instead, 95% of users stayed on the free tier, each costing $2/month in OpenAI fees. 50K free users meant $100K/month in unrecovered costs—a death spiral for a startup.</p>
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
        .scenario-card {{ background: white; border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .scenario-success {{ border-left: 4px solid #4CAF50; background: #f1f8f4; }}
        .scenario-failure {{ border-left: 4px solid #f44336; background: #fef1f1; }}
        .scenario-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; }}
        .monetization-insight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 25px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Feature Economics</h1>
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

        <h2>Feature Portfolio Intelligence Value</h2>
        <div class="monetization-insight">
            <p style="margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Build a Roadmap Driven by Economics, Not Guesses</p>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">Across {summary['total_features']} features with adoption rates ranging from near-zero to universal, Revenium reveals which AI capabilities drive customer value and which are expensive science experiments. With {len(investment_matrix['invest'])} features worth investing in and {len(investment_matrix['sunset'])} candidates for retirement, you can allocate development resources with confidence instead of hope.</p>
        </div>

        <h2>Customer Experience Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Double Down on High-Adoption Features</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">An AI productivity suite used Revenium's adoption tracking to discover their "Smart Scheduling" feature had 78% adoption while costing only $0.50/customer/month. They made it the centerpiece of their marketing, built related features around it, and saw the feature become their primary differentiator—driving 40% of new signups and expanding to 92% adoption.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: Investing in Ghost Features</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Without adoption metrics, product teams build features based on loud feedback from a vocal minority. One company spent $200K building an "Advanced AI Analytics" feature that 3% of customers used and cost $30K/month to run. They discovered the problem only after a year—wasting $560K on a feature almost nobody wanted.</p>
        </div>

        <h2>Product Adoption Scenarios</h2>
        <div class="scenario-card scenario-success">
            <div class="scenario-title" style="color: #4CAF50;">✓ Success: Sunset Losers, Fund Winners</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Using Revenium's investment matrix, a document AI platform identified 3 features with &lt;5% adoption costing $25K/month combined. They deprecated these features and reinvested the AI budget into their top 2 features (85%+ adoption). Customer satisfaction increased, costs dropped 30%, and they focused their roadmap on features customers actually valued.</p>
        </div>
        <div class="scenario-card scenario-failure">
            <div class="scenario-title" style="color: #f44336;">✗ Failure: The Feature Graveyard</div>
            <p style="margin: 10px 0 0 0; line-height: 1.6;">Many AI products accumulate features that nobody uses but everyone pays for. One platform had 15 AI features but 80% of usage concentrated in 3 features. Without Revenium's cost and adoption data, they kept maintaining all 15, spreading their AI budget thin and delivering mediocre performance across the board instead of excellence where it mattered.</p>
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
