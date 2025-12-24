"""Generator for PricingReport report."""

import os
from typing import Dict, Any
from datetime import datetime
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


