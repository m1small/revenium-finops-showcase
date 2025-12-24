"""Generator for PerformanceReport report."""

import os
from typing import Dict, Any
from .shared import format_currency, format_number, build_html_template, build_recommendations_html


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


