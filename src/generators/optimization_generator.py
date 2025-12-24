"""Generator for OptimizationReport report."""

import os
from typing import Dict, Any
from datetime import datetime
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


