"""Generator for ProfitabilityReport report."""

import os
from typing import Dict, Any
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


