"""Dataset Overview Report Generator."""

import os
from datetime import datetime
from typing import Dict, Any
from generators.shared import (
    format_currency, format_number, get_base_styles,
    build_html_template, build_recommendations_html
)


def generate_overview_report(data: Dict[str, Any], output_path: str):
    """Generate comprehensive dataset overview HTML report.

    Args:
        data: Analysis results from DatasetOverviewAnalyzer
        output_path: Path to write HTML file
    """
    # Extract data sections
    file_info = data['file_info']
    summary = data['summary']
    scale_metrics = data['scale_metrics']
    providers = data['provider_distribution']
    models = data['model_distribution']
    features = data['feature_usage']
    tiers = data['subscription_tiers']
    archetypes = data['customer_archetypes']
    regions = data['regional_distribution']
    products = data['product_distribution']
    temporal = data['temporal_analysis']
    quality = data['quality_metrics']
    recommendations = data['recommendations']

    # Build file info section
    file_info_html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #333;">Dataset Information</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div>
                    <strong>File Path:</strong><br>
                    <code style="font-size: 12px; background: white; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-top: 4px;">
                        {file_info['file_path']}
                    </code>
                </div>
                <div>
                    <strong>File Size:</strong><br>
                    <span style="font-size: 20px; color: #667eea;">{file_info['file_size_gb']} GB</span>
                    <span style="color: #666; font-size: 13px;">({format_number(file_info['file_size_bytes'])} bytes)</span>
                </div>
                <div>
                    <strong>Total Records:</strong><br>
                    <span style="font-size: 20px; color: #667eea;">{format_number(file_info['total_records'])}</span>
                </div>
                <div>
                    <strong>Date Range:</strong><br>
                    <span style="font-size: 14px; color: #666;">{temporal['duration_description']}</span>
                </div>
            </div>
        </div>
    """

    # Build metric cards
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total API Calls</div>
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
                <div class="metric-label">Avg Cost per Call</div>
                <div class="metric-value">{format_currency(summary['avg_cost_per_call'], 6)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="metric-label">Avg Tokens per Call</div>
                <div class="metric-value">{summary['avg_tokens_per_call']:.2f}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">Avg Latency</div>
                <div class="metric-value">{summary['avg_latency_ms']:.0f} ms</div>
            </div>
        </div>
    """

    # Build scale metrics section
    scale_cards = f"""
        <div class="metric-grid">
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="metric-label">Organizations</div>
                <div class="metric-value">{format_number(scale_metrics['unique_organizations'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="metric-label">Customers</div>
                <div class="metric-value">{format_number(scale_metrics['unique_customers'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <div class="metric-label">Products</div>
                <div class="metric-value">{format_number(scale_metrics['unique_products'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
                <div class="metric-label">Features</div>
                <div class="metric-value">{format_number(scale_metrics['unique_features'])}</div>
            </div>
        </div>
    """

    # Build quality metrics
    quality_html = f"""
        <div style="background: {'#f1f8f4' if quality['success_rate_percentage'] > 99 else '#fff8e1'};
                    padding: 20px; border-radius: 8px; margin: 20px 0;
                    border-left: 4px solid {'#388e3c' if quality['success_rate_percentage'] > 99 else '#f57c00'};">
            <h3 style="margin-top: 0; color: #333;">Data Quality Metrics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <strong>Success Rate:</strong><br>
                    <span style="font-size: 24px; color: {'#388e3c' if quality['success_rate_percentage'] > 99 else '#f57c00'};">
                        {quality['success_rate_percentage']:.2f}%
                    </span>
                </div>
                <div>
                    <strong>Successful Calls:</strong><br>
                    <span style="font-size: 20px;">{format_number(quality['success_count'])}</span>
                </div>
                <div>
                    <strong>Error Count:</strong><br>
                    <span style="font-size: 20px; color: {'#666' if quality['error_count'] == 0 else '#d32f2f'};">
                        {format_number(quality['error_count'])}
                    </span>
                </div>
            </div>
        </div>
    """

    # Build provider distribution table
    provider_rows = ""
    for p in providers[:10]:  # Top 10 providers
        provider_rows += f"""
            <tr>
                <td><strong>{p['provider']}</strong></td>
                <td style="text-align: right;">{format_number(p['call_count'])}</td>
                <td style="text-align: right;">{p['percentage']:.1f}%</td>
                <td style="text-align: right;">{format_currency(p['total_cost'])}</td>
                <td style="text-align: right;">{format_number(p['total_tokens'])}</td>
                <td style="text-align: right;">{format_currency(p['avg_cost_per_call'], 6)}</td>
            </tr>
        """

    provider_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Provider</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Total Tokens</th>
                    <th style="text-align: right;">Avg Cost/Call</th>
                </tr>
            </thead>
            <tbody>
                {provider_rows}
            </tbody>
        </table>
    """

    # Build model distribution table (top 10)
    model_rows = ""
    for m in models[:10]:
        model_rows += f"""
            <tr>
                <td><strong>{m['model']}</strong></td>
                <td style="text-align: right;">{format_number(m['call_count'])}</td>
                <td style="text-align: right;">{m['percentage']:.2f}%</td>
                <td style="text-align: right;">{format_currency(m['total_cost'])}</td>
                <td style="text-align: right;">{m['avg_latency_ms']:.0f} ms</td>
            </tr>
        """

    model_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Avg Latency</th>
                </tr>
            </thead>
            <tbody>
                {model_rows}
            </tbody>
        </table>
    """

    # Build feature usage table
    feature_rows = ""
    for f in features:
        feature_rows += f"""
            <tr>
                <td><strong>{f['feature']}</strong></td>
                <td style="text-align: right;">{format_number(f['call_count'])}</td>
                <td style="text-align: right;">{f['percentage']:.1f}%</td>
                <td style="text-align: right;">{format_currency(f['total_cost'])}</td>
                <td style="text-align: right;">{f['avg_tokens_per_call']:.1f}</td>
            </tr>
        """

    feature_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Avg Tokens/Call</th>
                </tr>
            </thead>
            <tbody>
                {feature_rows}
            </tbody>
        </table>
    """

    # Build subscription tier table
    tier_rows = ""
    for t in tiers:
        tier_rows += f"""
            <tr>
                <td><strong>{t['tier'].title()}</strong></td>
                <td style="text-align: right;">{format_currency(t['price_usd'], 0)}/mo</td>
                <td style="text-align: right;">{format_number(t['call_count'])}</td>
                <td style="text-align: right;">{t['percentage']:.1f}%</td>
                <td style="text-align: right;">{format_currency(t['total_cost'])}</td>
            </tr>
        """

    tier_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Tier</th>
                    <th style="text-align: right;">Price</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Total Cost</th>
                </tr>
            </thead>
            <tbody>
                {tier_rows}
            </tbody>
        </table>
    """

    # Build customer archetype table
    archetype_rows = ""
    for a in archetypes:
        archetype_rows += f"""
            <tr>
                <td><strong>{a['archetype'].title()}</strong></td>
                <td style="text-align: right;">{format_number(a['call_count'])}</td>
                <td style="text-align: right;">{a['percentage']:.1f}%</td>
                <td style="text-align: right;">{a['avg_tokens_per_call']:.1f}</td>
                <td style="text-align: right;">{format_currency(a['avg_cost_per_call'], 6)}</td>
            </tr>
        """

    archetype_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Archetype</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Avg Tokens/Call</th>
                    <th style="text-align: right;">Avg Cost/Call</th>
                </tr>
            </thead>
            <tbody>
                {archetype_rows}
            </tbody>
        </table>
    """

    # Build regional distribution table
    region_rows = ""
    for r in regions:
        region_rows += f"""
            <tr>
                <td><strong>{r['region']}</strong></td>
                <td style="text-align: right;">{format_number(r['call_count'])}</td>
                <td style="text-align: right;">{r['percentage']:.1f}%</td>
                <td style="text-align: right;">{r['avg_latency_ms']:.0f} ms</td>
            </tr>
        """

    region_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Avg Latency</th>
                </tr>
            </thead>
            <tbody>
                {region_rows}
            </tbody>
        </table>
    """

    # Build product distribution table
    product_rows = ""
    for p in products:
        product_rows += f"""
            <tr>
                <td><strong>{p['product']}</strong></td>
                <td style="text-align: right;">{format_number(p['call_count'])}</td>
                <td style="text-align: right;">{p['percentage']:.1f}%</td>
                <td style="text-align: right;">{format_currency(p['total_cost'])}</td>
            </tr>
        """

    product_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th style="text-align: right;">Calls</th>
                    <th style="text-align: right;">Percentage</th>
                    <th style="text-align: right;">Total Cost</th>
                </tr>
            </thead>
            <tbody>
                {product_rows}
            </tbody>
        </table>
    """

    # Build Chart.js visualizations
    provider_labels = [p['provider'] for p in providers[:7]]
    provider_values = [p['call_count'] for p in providers[:7]]

    feature_labels = [f['feature'] for f in features]
    feature_values = [f['call_count'] for f in features]

    tier_labels = [t['tier'].title() for t in tiers]
    tier_values = [t['call_count'] for t in tiers]

    scripts = f"""
    <script>
        // Provider distribution chart
        new Chart(document.getElementById('providerChart'), {{
            type: 'bar',
            data: {{
                labels: {provider_labels},
                datasets: [{{
                    label: 'API Calls by Provider',
                    data: {provider_values},
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(250, 112, 154, 0.8)',
                        'rgba(48, 207, 208, 0.8)',
                        'rgba(254, 225, 64, 0.8)'
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

        // Feature usage chart
        new Chart(document.getElementById('featureChart'), {{
            type: 'doughnut',
            data: {{
                labels: {feature_labels},
                datasets: [{{
                    data: {feature_values},
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
                    }}
                }}
            }}
        }});

        // Subscription tier chart
        new Chart(document.getElementById('tierChart'), {{
            type: 'pie',
            data: {{
                labels: {tier_labels},
                datasets: [{{
                    data: {tier_values},
                    backgroundColor: [
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(240, 147, 251, 0.8)'
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
        <h1>📊 Dataset Overview Analysis</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px;">
            Comprehensive statistical analysis and distribution metrics
        </p>

        {file_info_html}

        <h2>Summary Metrics</h2>
        {metric_cards}

        <h2>Scale Metrics</h2>
        {scale_cards}

        {quality_html}

        <h2>Provider Distribution</h2>
        <div class="chart-container">
            <canvas id="providerChart"></canvas>
        </div>
        {provider_table}

        <h2>Top Models (by Call Volume)</h2>
        {model_table}

        <h2>Feature Usage Distribution</h2>
        <div class="chart-container">
            <canvas id="featureChart"></canvas>
        </div>
        {feature_table}

        <h2>Subscription Tier Distribution</h2>
        <div class="chart-container">
            <canvas id="tierChart"></canvas>
        </div>
        {tier_table}

        <h2>Customer Archetypes</h2>
        {archetype_table}

        <h2>Regional Distribution</h2>
        {region_table}

        <h2>Product Distribution</h2>
        {product_table}

        <h2>Key Insights & Recommendations</h2>
        {build_recommendations_html(recommendations)}
    """

    # Build final HTML
    html = build_html_template("Dataset Overview Analysis", content, scripts)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Dataset overview report generated: {output_path}")
