"""Geographic & Latency Intelligence Report Generator."""

import os
from typing import Dict, Any
from generators.shared import (
    format_currency, format_number, get_base_styles,
    build_html_template, build_recommendations_html
)


def generate_geographic_latency_report(data: Dict[str, Any], output_path: str):
    """Generate geographic & latency intelligence HTML report.

    Args:
        data: Analysis results from GeographicLatencyAnalyzer
        output_path: Path to write HTML file
    """
    summary = data['summary']
    by_region = data['by_region']
    heatmap = data['latency_heatmap']
    cost_variance = data['regional_cost_variance']
    provider_by_region = data['provider_by_region']
    cross_region = data['cross_region_issues']
    profitability = data['regional_profitability']
    recommendations = data['recommendations']

    # Build metric cards
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Regions</div>
                <div class="metric-value">{summary['total_regions']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Latency</div>
                <div class="metric-value">{summary['avg_latency_ms']:.0f} ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Regional Balance</div>
                <div class="metric-value">{summary['regional_balance_score']:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cross-Region Issues</div>
                <div class="metric-value">{cross_region['issue_count']}</div>
            </div>
        </div>
    """

    # Regional distribution table
    region_rows = ""
    for r in by_region:
        latency_color = '#43e97b' if r['avg_latency_ms'] < 1000 else '#f57c00' if r['avg_latency_ms'] < 1500 else '#d32f2f'
        region_rows += f"""
            <tr>
                <td><strong>{r['region']}</strong></td>
                <td style="text-align: right;">{format_number(r['call_count'])}</td>
                <td style="text-align: right;">{r['percentage']:.1f}%</td>
                <td style="text-align: right; color: {latency_color}; font-weight: bold;">{r['avg_latency_ms']:.0f} ms</td>
                <td style="text-align: right;">{r['p95_latency_ms']:.0f} ms</td>
                <td style="text-align: right;">{r['p99_latency_ms']:.0f} ms</td>
                <td style="text-align: right;">{format_currency(r['total_cost'])}</td>
            </tr>
        """

    region_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">% of Total</th>
                    <th style="text-align: right;">Avg Latency</th>
                    <th style="text-align: right;">P95 Latency</th>
                    <th style="text-align: right;">P99 Latency</th>
                    <th style="text-align: right;">Total Cost</th>
                </tr>
            </thead>
            <tbody>
                {region_rows}
            </tbody>
        </table>
    """

    # Latency heatmap table (top entries)
    heatmap_rows = ""
    for h in heatmap[:20]:  # Top 20
        heatmap_rows += f"""
            <tr>
                <td>{h['region']}</td>
                <td>{h['provider']}</td>
                <td>{h['model']}</td>
                <td style="text-align: right;">{format_number(h['call_count'])}</td>
                <td style="text-align: right;">{h['avg_latency_ms']:.0f} ms</td>
                <td style="text-align: right;">{h['p95_latency_ms']:.0f} ms</td>
                <td style="text-align: right;">{h['p99_latency_ms']:.0f} ms</td>
            </tr>
        """

    heatmap_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th>Provider</th>
                    <th>Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Avg Latency</th>
                    <th style="text-align: right;">P95</th>
                    <th style="text-align: right;">P99</th>
                </tr>
            </thead>
            <tbody>
                {heatmap_rows}
            </tbody>
        </table>
    """

    # Cost variance table
    variance_rows = ""
    for cv in cost_variance[:10]:  # Top 10
        variance_rows += f"""
            <tr>
                <td><strong>{cv['model']}</strong></td>
                <td style="text-align: right;">{cv['regions_analyzed']}</td>
                <td>{cv['cheapest_region']}</td>
                <td style="text-align: right;">{format_currency(cv['min_cost'], 6)}</td>
                <td>{cv['most_expensive_region']}</td>
                <td style="text-align: right;">{format_currency(cv['max_cost'], 6)}</td>
                <td style="text-align: right; color: #f57c00; font-weight: bold;">{cv['variance_percentage']:.1f}%</td>
                <td style="text-align: right; color: #43e97b; font-weight: bold;">{format_currency(cv['potential_savings'], 6)}</td>
            </tr>
        """

    variance_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th style="text-align: right;">Regions</th>
                    <th>Cheapest Region</th>
                    <th style="text-align: right;">Min Cost</th>
                    <th>Most Expensive</th>
                    <th style="text-align: right;">Max Cost</th>
                    <th style="text-align: right;">Variance %</th>
                    <th style="text-align: right;">Savings/Call</th>
                </tr>
            </thead>
            <tbody>
                {variance_rows}
            </tbody>
        </table>
    """ if cost_variance else "<p style='color: #666;'>No significant cost variance detected across regions.</p>"

    # Regional profitability table
    profit_rows = ""
    for p in profitability:
        margin_color = '#43e97b' if p['margin_percentage'] > 50 else '#f57c00' if p['margin_percentage'] > 0 else '#d32f2f'
        profit_rows += f"""
            <tr>
                <td><strong>{p['region']}</strong></td>
                <td style="text-align: right;">{format_number(p['call_count'])}</td>
                <td style="text-align: right;">{format_currency(p['total_cost'])}</td>
                <td style="text-align: right;">{format_currency(p['estimated_revenue'])}</td>
                <td style="text-align: right;">{format_currency(p['gross_margin'])}</td>
                <td style="text-align: right; color: {margin_color}; font-weight: bold;">{p['margin_percentage']:.1f}%</td>
            </tr>
        """

    profitability_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Est. Revenue</th>
                    <th style="text-align: right;">Gross Margin</th>
                    <th style="text-align: right;">Margin %</th>
                </tr>
            </thead>
            <tbody>
                {profit_rows}
            </tbody>
        </table>
    """

    # Cross-region issues alerts
    issues_html = ""
    if cross_region['issues']:
        for issue in cross_region['issues']:
            severity = 'critical' if issue.get('p99_latency_ms', 0) > 4000 else 'warning'
            issue_desc = issue['issue'].replace('_', ' ').title()

            if issue['issue'] == 'high_p99_latency':
                message = f"P99 latency of {issue['p99_latency_ms']:.0f}ms in {issue['region']} exceeds acceptable threshold"
            else:
                message = f"High variance in {issue['region']} (std dev: {issue.get('std_deviation', 0):.0f}ms)"

            issues_html += f"""
                <div class="alert alert-{severity}">
                    <div class="alert-icon">{'🔴' if severity == 'critical' else '⚠️'}</div>
                    <div class="alert-content">
                        <div class="alert-title">{issue_desc}</div>
                        <div class="alert-description">{message}</div>
                    </div>
                </div>
            """
    else:
        issues_html = """
            <div class="alert alert-success">
                <div class="alert-icon">✅</div>
                <div class="alert-content">
                    <div class="alert-title">No Cross-Region Issues Detected</div>
                    <div class="alert-description">All regions are performing within acceptable parameters.</div>
                </div>
            </div>
        """

    # Charts
    region_labels = [r['region'] for r in by_region]
    region_calls = [r['call_count'] for r in by_region]
    region_latencies = [r['avg_latency_ms'] for r in by_region]

    scripts = f"""
    <script>
        // Regional distribution
        new Chart(document.getElementById('regionDistChart'), {{
            type: 'bar',
            data: {{
                labels: {region_labels},
                datasets: [{{
                    label: 'API Calls by Region',
                    data: {region_calls},
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
                                return value.toLocaleString();
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Regional latency comparison
        new Chart(document.getElementById('latencyComparisonChart'), {{
            type: 'bar',
            data: {{
                labels: {region_labels},
                datasets: [{{
                    label: 'Average Latency (ms)',
                    data: {region_latencies},
                    backgroundColor: 'rgba(240, 147, 251, 0.8)',
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
                                return value + ' ms';
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
        <h1>🌍 Geographic & Latency Intelligence</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px;">
            Regional performance analysis, cost arbitrage, and latency optimization
        </p>

        <h2>Summary Metrics</h2>
        {metric_cards}

        <h2>Regional Distribution</h2>
        <div class="chart-container">
            <canvas id="regionDistChart"></canvas>
        </div>
        {region_table}

        <h2>Regional Latency Comparison</h2>
        <div class="chart-container">
            <canvas id="latencyComparisonChart"></canvas>
        </div>

        <h2>Latency Heatmap (Best Performers)</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Top 20 region-provider-model combinations sorted by lowest average latency.
        </p>
        {heatmap_table}

        <h2>Regional Cost Variance Analysis</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Identify cost arbitrage opportunities by routing traffic to cheaper regions.
        </p>
        {variance_table}

        <h2>Regional Profitability</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Estimated revenue and margins by geographic region.
        </p>
        {profitability_table}

        <h2>Cross-Region Issues</h2>
        {issues_html}

        <h2>Recommendations</h2>
        {build_recommendations_html(recommendations)}
    """

    # Build final HTML
    html = build_html_template("Geographic & Latency Intelligence", content, scripts)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Geographic & latency report generated: {output_path}")
