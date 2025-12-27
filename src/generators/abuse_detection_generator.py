"""Multi-Tenant Cost Anomaly & Abuse Detection Report Generator."""

import os
from typing import Dict, Any
from generators.shared import (
    format_currency, format_number, get_base_styles,
    build_html_template, build_recommendations_html
)


def generate_abuse_detection_report(data: Dict[str, Any], output_path: str):
    """Generate abuse detection HTML report.

    Args:
        data: Analysis results from AbuseDetectionAnalyzer
        output_path: Path to write HTML file
    """
    summary = data['summary']
    cost_anomalies = data['cost_anomalies']
    spikes = data['usage_spikes']
    gaming = data['tier_gaming']
    patterns = data['suspicious_patterns']
    concurrent = data['concurrent_abuse']
    outliers = data['outlier_customers']
    security_flags = data['security_flags']
    recommendations = data['recommendations']

    # Build metric cards
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Calls Analyzed</div>
                <div class="metric-value">{format_number(summary['total_calls'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">Cost Anomalies</div>
                <div class="metric-value">{format_number(cost_anomalies['anomaly_count'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #d32f2f 0%, #f57c00 100%);">
                <div class="metric-label">Estimated Waste</div>
                <div class="metric-value">{format_currency(cost_anomalies['estimated_waste'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);">
                <div class="metric-label">Tier Gaming Cases</div>
                <div class="metric-value">{len(gaming)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="metric-label">Security Flags</div>
                <div class="metric-value">{len(security_flags)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="metric-label">Anomaly Rate</div>
                <div class="metric-value">{summary['anomaly_rate']:.2f}%</div>
            </div>
        </div>
    """

    # Security flags
    flags_html = ""
    if security_flags:
        for flag in security_flags:
            severity_class = f"alert-{'critical' if flag['severity'] == 'critical' else 'warning' if flag['severity'] in ['high', 'medium'] else 'info'}"
            severity_icon = '🔴' if flag['severity'] == 'critical' else '⚠️' if flag['severity'] == 'high' else '🟡' if flag['severity'] == 'medium' else 'ℹ️'

            impact_str = f"Estimated impact: {format_currency(flag['estimated_impact'])}" if flag['estimated_impact'] > 0 else ""

            flags_html += f"""
                <div class="alert {severity_class}">
                    <div class="alert-icon">{severity_icon}</div>
                    <div class="alert-content">
                        <div class="alert-title">{flag['severity'].upper()}: {flag['type'].replace('_', ' ').title()}</div>
                        <div class="alert-description">{flag['message']}. {impact_str}</div>
                    </div>
                </div>
            """
    else:
        flags_html = """
            <div class="alert alert-success">
                <div class="alert-icon">✅</div>
                <div class="alert-content">
                    <div class="alert-title">No Critical Security Flags</div>
                    <div class="alert-description">System monitoring shows normal usage patterns.</div>
                </div>
            </div>
        """

    # Cost anomalies table
    anomaly_rows = ""
    for a in cost_anomalies['top_anomalies'][:15]:
        anomaly_rows += f"""
            <tr>
                <td>{a['customer_id']}</td>
                <td>{a['model']}</td>
                <td>{a['feature']}</td>
                <td style="text-align: right; color: #d32f2f; font-weight: bold;">{format_currency(a['cost_usd'])}</td>
                <td style="text-align: right;">{format_number(a['tokens'])}</td>
                <td style="font-size: 12px;">{a['timestamp'][:19]}</td>
            </tr>
        """

    anomaly_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Model</th>
                    <th>Feature</th>
                    <th style="text-align: right;">Cost (Anomalous)</th>
                    <th style="text-align: right;">Tokens</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {anomaly_rows}
            </tbody>
        </table>
    """ if cost_anomalies['top_anomalies'] else "<p style='color: #666;'>No cost anomalies detected.</p>"

    # Usage spikes table
    spike_rows = ""
    for s in spikes[:15]:
        spike_rows += f"""
            <tr>
                <td>{s['customer_id']}</td>
                <td>{s['tier'].title()}</td>
                <td style="font-size: 12px;">{s['spike_hour'][:19]}</td>
                <td style="text-align: right; color: #d32f2f; font-weight: bold;">{format_number(s['spike_count'])}</td>
                <td style="text-align: right;">{s['avg_hourly_count']:.1f}</td>
                <td style="text-align: right; color: #f57c00; font-weight: bold;">{s['spike_multiplier']:.1f}x</td>
            </tr>
        """

    spike_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Tier</th>
                    <th>Spike Time</th>
                    <th style="text-align: right;">Calls in Hour</th>
                    <th style="text-align: right;">Avg Hourly</th>
                    <th style="text-align: right;">Multiplier</th>
                </tr>
            </thead>
            <tbody>
                {spike_rows}
            </tbody>
        </table>
    """ if spikes else "<p style='color: #666;'>No unusual usage spikes detected.</p>"

    # Tier gaming table
    gaming_rows = ""
    for g in gaming[:15]:
        flags_str = ', '.join(f.replace('_', ' ') for f in g['flags'][:3])
        gaming_rows += f"""
            <tr>
                <td>{g['customer_id']}</td>
                <td>{g['tier'].title()}</td>
                <td style="text-align: right; color: #d32f2f; font-weight: bold;">{g['gaming_score']}</td>
                <td style="text-align: right;">{format_number(g['call_count'])}</td>
                <td style="text-align: right;">{format_currency(g['total_cost'])}</td>
                <td style="text-align: right; color: #f57c00;">{g['cost_to_price_ratio']:.1f}x</td>
                <td style="font-size: 12px;">{flags_str}</td>
            </tr>
        """

    gaming_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Tier</th>
                    <th style="text-align: right;">Gaming Score</th>
                    <th style="text-align: right;">Call Count</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Cost/Price Ratio</th>
                    <th>Red Flags</th>
                </tr>
            </thead>
            <tbody>
                {gaming_rows}
            </tbody>
        </table>
    """ if gaming else "<p style='color: #666;'>No tier gaming detected.</p>"

    # Concurrent abuse table
    concurrent_rows = ""
    for c in concurrent['cases'][:15]:
        concurrent_rows += f"""
            <tr>
                <td>{c['customer_id']}</td>
                <td>{c['tier'].title()}</td>
                <td style="text-align: right; color: #d32f2f; font-weight: bold;">{format_number(c['max_calls_per_minute'])}</td>
                <td style="text-align: right;">{format_number(c['total_calls'])}</td>
            </tr>
        """

    concurrent_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Tier</th>
                    <th style="text-align: right;">Max Calls/Minute</th>
                    <th style="text-align: right;">Total Calls</th>
                </tr>
            </thead>
            <tbody>
                {concurrent_rows}
            </tbody>
        </table>
    """ if concurrent['cases'] else "<p style='color: #666;'>No concurrent abuse detected.</p>"

    # Suspicious patterns summary
    patterns_html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #333;">Suspicious Pattern Detection</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div>
                    <strong>Batch Processing Abuse:</strong><br>
                    <span style="font-size: 24px; color: {'#d32f2f' if len(patterns['batch_processing_abuse']) > 0 else '#666'};">
                        {len(patterns['batch_processing_abuse'])}
                    </span>
                    <span style="color: #666; font-size: 13px;"> cases</span>
                </div>
                <div>
                    <strong>Off-Hours Spikes:</strong><br>
                    <span style="font-size: 24px; color: {'#f57c00' if len(patterns['off_hours_spikes']) > 0 else '#666'};">
                        {len(patterns['off_hours_spikes'])}
                    </span>
                    <span style="color: #666; font-size: 13px;"> cases</span>
                </div>
                <div>
                    <strong>Model Hopping:</strong><br>
                    <span style="font-size: 24px; color: {'#ff9800' if len(patterns['model_hopping']) > 0 else '#666'};">
                        {len(patterns['model_hopping'])}
                    </span>
                    <span style="color: #666; font-size: 13px;"> cases</span>
                </div>
                <div>
                    <strong>Feature Spam:</strong><br>
                    <span style="font-size: 24px; color: {'#f57c00' if len(patterns['feature_spam']) > 0 else '#666'};">
                        {len(patterns['feature_spam'])}
                    </span>
                    <span style="color: #666; font-size: 13px;"> cases</span>
                </div>
            </div>
        </div>
    """

    # Outliers table
    outlier_rows = ""
    for o in outliers[:15]:
        reasons_str = ', '.join(o['reasons'][:3])
        outlier_rows += f"""
            <tr>
                <td>{o['customer_id']}</td>
                <td style="text-align: right; color: #d32f2f; font-weight: bold;">{o['outlier_score']}</td>
                <td style="text-align: right;">{format_number(o['call_count'])}</td>
                <td style="text-align: right;">{format_currency(o['total_cost'])}</td>
                <td style="text-align: right;">{o['avg_latency_ms']:.0f} ms</td>
                <td style="font-size: 12px;">{reasons_str}</td>
            </tr>
        """

    outlier_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th style="text-align: right;">Outlier Score</th>
                    <th style="text-align: right;">Call Count</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Avg Latency</th>
                    <th>Outlier Reasons</th>
                </tr>
            </thead>
            <tbody>
                {outlier_rows}
            </tbody>
        </table>
    """ if outliers else "<p style='color: #666;'>No statistical outliers detected.</p>"

    # Charts
    scripts = f"""
    <script>
        // Security flags by severity
        var criticalCount = {len([f for f in security_flags if f['severity'] == 'critical'])};
        var highCount = {len([f for f in security_flags if f['severity'] == 'high'])};
        var mediumCount = {len([f for f in security_flags if f['severity'] == 'medium'])};
        var lowCount = {len([f for f in security_flags if f['severity'] == 'low'])};

        new Chart(document.getElementById('flagsChart'), {{
            type: 'bar',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{{
                    label: 'Security Flags by Severity',
                    data: [criticalCount, highCount, mediumCount, lowCount],
                    backgroundColor: [
                        'rgba(211, 47, 47, 0.8)',
                        'rgba(245, 124, 0, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
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
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Abuse types distribution
        new Chart(document.getElementById('abuseTypesChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Cost Anomalies', 'Usage Spikes', 'Tier Gaming', 'Concurrent Abuse'],
                datasets: [{{
                    data: [
                        {cost_anomalies['anomaly_count']},
                        {len(spikes)},
                        {len(gaming)},
                        {concurrent['abuse_count']}
                    ],
                    backgroundColor: [
                        'rgba(211, 47, 47, 0.8)',
                        'rgba(245, 124, 0, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(102, 126, 234, 0.8)'
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
                    }}
                }}
            }}
        }});
    </script>
    """

    # Build complete content
    content = f"""
        <h1>🔒 Multi-Tenant Cost Anomaly & Abuse Detection</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px;">
            Security monitoring, abuse detection, and cost protection analysis
        </p>

        <h2>Summary Metrics</h2>
        {metric_cards}

        <h2>Security Flags</h2>
        {flags_html}

        <h2>Flag Distribution</h2>
        <div class="chart-container">
            <canvas id="flagsChart"></canvas>
        </div>

        <h2>Abuse Types Overview</h2>
        <div class="chart-container">
            <canvas id="abuseTypesChart"></canvas>
        </div>

        <h2>Cost Anomalies</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Detected {format_number(cost_anomalies['anomaly_count'])} anomalous calls with
            {format_currency(cost_anomalies['estimated_waste'])} in estimated waste.
        </p>
        {anomaly_table}

        <h2>Usage Spikes</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Customers with sudden 10x+ usage increases indicating potential abuse or automation.
        </p>
        {spike_table}

        <h2>Tier Gaming Detection</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Customers potentially exploiting lower-tier pricing for enterprise-level usage.
        </p>
        {gaming_table}

        <h2>Concurrent Usage Abuse</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Accounts showing excessive concurrent API calls (potential scripted abuse).
        </p>
        {concurrent_table}

        {patterns_html}

        <h2>Statistical Outliers</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Customers with usage patterns significantly deviating from normal distribution.
        </p>
        {outlier_table}

        <h2>Recommendations</h2>
        {build_recommendations_html(recommendations)}
    """

    # Build final HTML
    html = build_html_template("Multi-Tenant Cost Anomaly & Abuse Detection", content, scripts)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Abuse detection report generated: {output_path}")
