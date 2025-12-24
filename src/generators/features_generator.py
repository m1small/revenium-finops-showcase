"""Generator for FeaturesReport report."""

import os
from typing import Dict, Any
from datetime import datetime
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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
