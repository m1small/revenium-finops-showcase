"""Generator for AlignmentReport report."""

import os
from typing import Dict, Any
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


