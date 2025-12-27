"""Token Economics Report Generator."""

import os
from typing import Dict, Any
from generators.shared import (
    format_currency, format_number, get_base_styles,
    build_html_template, build_recommendations_html
)


def generate_token_economics_report(data: Dict[str, Any], output_path: str):
    """Generate token economics HTML report.

    Args:
        data: Analysis results from TokenEconomicsAnalyzer
        output_path: Path to write HTML file
    """
    summary = data['summary']
    by_model = data['by_model']
    by_feature = data['by_feature']
    by_archetype = data['by_archetype']
    io_ratio = data['io_ratio_analysis']
    rankings = data['efficiency_rankings']
    wasteful = data['wasteful_patterns']
    opportunities = data['optimization_opportunities']
    recommendations = data['recommendations']

    # Build metric cards
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{format_number(summary['total_tokens'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">{format_currency(summary['total_cost'])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cost per 1K Tokens</div>
                <div class="metric-value">{format_currency(summary['cost_per_1k_tokens'], 4)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg I/O Ratio</div>
                <div class="metric-value">{summary['avg_io_ratio']:.2f}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="metric-label">Wasteful Calls</div>
                <div class="metric-value">{format_number(wasteful['wasteful_call_count'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">Wasted Cost</div>
                <div class="metric-value">{format_currency(wasteful['total_wasted_cost'])}</div>
            </div>
        </div>
    """

    # I/O Ratio Analysis
    io_analysis_html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #333;">Input/Output Token Distribution</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <strong>Median I/O Ratio:</strong><br>
                    <span style="font-size: 24px; color: #667eea;">{io_ratio['median_ratio']:.2f}</span>
                </div>
                <div>
                    <strong>Balanced Calls:</strong><br>
                    <span style="font-size: 20px; color: #43e97b;">{format_number(io_ratio['balanced_calls'])}</span>
                    <span style="color: #666; font-size: 13px;"> (0.5-2.0 ratio)</span>
                </div>
                <div>
                    <strong>Input-Heavy:</strong><br>
                    <span style="font-size: 20px; color: #f57c00;">{format_number(io_ratio['input_heavy_calls'])}</span>
                    <span style="color: #666; font-size: 13px;"> (&gt;2.0 ratio)</span>
                </div>
                <div>
                    <strong>Output-Heavy:</strong><br>
                    <span style="font-size: 20px; color: #1976d2;">{format_number(io_ratio['output_heavy_calls'])}</span>
                    <span style="color: #666; font-size: 13px;"> (&lt;0.5 ratio)</span>
                </div>
            </div>
        </div>
    """

    # Model efficiency table
    model_rows = ""
    for m in by_model[:15]:  # Top 15 models
        efficiency_color = '#43e97b' if m['efficiency_score'] > 70 else '#f57c00' if m['efficiency_score'] > 40 else '#d32f2f'
        model_rows += f"""
            <tr>
                <td><strong>{m['model']}</strong></td>
                <td style="text-align: right;">{format_number(m['call_count'])}</td>
                <td style="text-align: right;">{format_number(m['total_tokens'])}</td>
                <td style="text-align: right;">{m['io_ratio']:.2f}</td>
                <td style="text-align: right;">{format_currency(m['cost_per_1k_tokens'], 4)}</td>
                <td style="text-align: right; color: {efficiency_color}; font-weight: bold;">{m['efficiency_score']:.1f}</td>
            </tr>
        """

    model_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Total Tokens</th>
                    <th style="text-align: right;">I/O Ratio</th>
                    <th style="text-align: right;">Cost/1K Tokens</th>
                    <th style="text-align: right;">Efficiency Score</th>
                </tr>
            </thead>
            <tbody>
                {model_rows}
            </tbody>
        </table>
    """

    # Feature analysis table
    feature_rows = ""
    for f in by_feature:
        feature_rows += f"""
            <tr>
                <td><strong>{f['feature']}</strong></td>
                <td style="text-align: right;">{format_number(f['call_count'])}</td>
                <td style="text-align: right;">{f['avg_input_tokens']:.0f}</td>
                <td style="text-align: right;">{f['avg_output_tokens']:.0f}</td>
                <td style="text-align: right;">{f['io_ratio']:.2f}</td>
                <td style="text-align: right;">{format_currency(f['cost_per_1k_tokens'], 4)}</td>
                <td style="text-align: right;">{format_currency(f['cost_per_call'], 6)}</td>
            </tr>
        """

    feature_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Avg Input</th>
                    <th style="text-align: right;">Avg Output</th>
                    <th style="text-align: right;">I/O Ratio</th>
                    <th style="text-align: right;">Cost/1K Tokens</th>
                    <th style="text-align: right;">Avg Cost/Call</th>
                </tr>
            </thead>
            <tbody>
                {feature_rows}
            </tbody>
        </table>
    """

    # Archetype analysis table
    archetype_rows = ""
    for a in by_archetype:
        archetype_rows += f"""
            <tr>
                <td><strong>{a['archetype'].title()}</strong></td>
                <td style="text-align: right;">{format_number(a['call_count'])}</td>
                <td style="text-align: right;">{a['avg_tokens_per_call']:.1f}</td>
                <td style="text-align: right;">{a['io_ratio']:.2f}</td>
                <td style="text-align: right;">{format_currency(a['cost_per_1k_tokens'], 4)}</td>
                <td style="text-align: right;">{a['efficiency_score']:.1f}</td>
            </tr>
        """

    archetype_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer Archetype</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Avg Tokens/Call</th>
                    <th style="text-align: right;">I/O Ratio</th>
                    <th style="text-align: right;">Cost/1K Tokens</th>
                    <th style="text-align: right;">Efficiency Score</th>
                </tr>
            </thead>
            <tbody>
                {archetype_rows}
            </tbody>
        </table>
    """

    # Wasteful patterns breakdown
    wasteful_breakdown = ""
    for issue, count in wasteful['issue_breakdown'].items():
        issue_label = issue.replace('_', ' ').title()
        wasteful_breakdown += f"""
            <div class="alert alert-warning">
                <div class="alert-icon">⚠️</div>
                <div class="alert-content">
                    <div class="alert-title">{issue_label}</div>
                    <div class="alert-description">{format_number(count)} calls detected with this issue</div>
                </div>
            </div>
        """

    # Optimization opportunities table
    opp_rows = ""
    for opp in opportunities[:15]:  # Top 15
        opp_rows += f"""
            <tr>
                <td>{opp['customer_id']}</td>
                <td>{opp['feature']}</td>
                <td>{opp['current_model']}</td>
                <td style="text-align: right;">{format_number(opp['call_count'])}</td>
                <td style="text-align: right;">{opp['avg_tokens']:.0f}</td>
                <td style="text-align: right;">{format_currency(opp['current_cost'])}</td>
                <td style="text-align: right; color: #43e97b; font-weight: bold;">{format_currency(opp['potential_savings'])}</td>
            </tr>
        """

    opportunities_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Feature</th>
                    <th>Current Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Avg Tokens</th>
                    <th style="text-align: right;">Current Cost</th>
                    <th style="text-align: right;">Potential Savings</th>
                </tr>
            </thead>
            <tbody>
                {opp_rows}
            </tbody>
        </table>
    """ if opportunities else "<p style='color: #666;'>No optimization opportunities identified.</p>"

    # Charts
    model_labels = [m['model'] for m in by_model[:10]]
    model_costs = [m['cost_per_1k_tokens'] for m in by_model[:10]]
    model_efficiency = [m['efficiency_score'] for m in by_model[:10]]

    feature_labels = [f['feature'] for f in by_feature]
    feature_costs = [f['cost_per_1k_tokens'] for f in by_feature]

    scripts = f"""
    <script>
        // Cost per 1K tokens by model
        new Chart(document.getElementById('modelCostChart'), {{
            type: 'bar',
            data: {{
                labels: {model_labels},
                datasets: [{{
                    label: 'Cost per 1K Tokens (USD)',
                    data: {model_costs},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
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
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toFixed(4);
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Efficiency scores
        new Chart(document.getElementById('efficiencyChart'), {{
            type: 'bar',
            data: {{
                labels: {model_labels},
                datasets: [{{
                    label: 'Efficiency Score',
                    data: {model_efficiency},
                    backgroundColor: 'rgba(67, 233, 123, 0.8)',
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
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});

        // Feature cost comparison
        new Chart(document.getElementById('featureCostChart'), {{
            type: 'doughnut',
            data: {{
                labels: {feature_labels},
                datasets: [{{
                    data: {feature_costs},
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(250, 112, 154, 0.8)'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': $' + context.parsed.toFixed(4) + '/1K tokens';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    """

    # Build complete content
    content = f"""
        <h1>💰 Token Economics & Efficiency Analysis</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px;">
            Deep dive into token usage patterns and cost optimization opportunities
        </p>

        <h2>Summary Metrics</h2>
        {metric_cards}

        {io_analysis_html}

        <h2>Model Token Economics</h2>
        <div class="chart-container">
            <canvas id="modelCostChart"></canvas>
        </div>
        {model_table}

        <h2>Model Efficiency Rankings</h2>
        <div class="chart-container">
            <canvas id="efficiencyChart"></canvas>
        </div>

        <h2>Feature Token Analysis</h2>
        <div class="chart-container">
            <canvas id="featureCostChart"></canvas>
        </div>
        {feature_table}

        <h2>Customer Archetype Efficiency</h2>
        {archetype_table}

        <h2>Wasteful Usage Patterns</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Detected {format_number(wasteful['wasteful_call_count'])} calls with inefficient token usage,
            costing {format_currency(wasteful['total_wasted_cost'])} in wasted spend.
        </p>
        {wasteful_breakdown}

        <h2>Top Optimization Opportunities</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Potential savings from model optimization and better token management.
        </p>
        {opportunities_table}

        <h2>Recommendations</h2>
        {build_recommendations_html(recommendations)}
    """

    # Build final HTML
    html = build_html_template("Token Economics & Efficiency Analysis", content, scripts)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Token economics report generated: {output_path}")
