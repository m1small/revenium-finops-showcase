"""Churn Risk & Growth Signals Report Generator."""

import os
from typing import Dict, Any
from generators.shared import (
    format_currency, format_number, get_base_styles,
    build_html_template, build_recommendations_html
)


def generate_churn_growth_report(data: Dict[str, Any], output_path: str):
    """Generate churn risk & growth signals HTML report.

    Args:
        data: Analysis results from ChurnGrowthAnalyzer
        output_path: Path to write HTML file
    """
    summary = data['summary']
    velocity = data['usage_velocity']
    churn_risk = data['churn_risk_customers']
    expansion = data['expansion_opportunities']
    feature_adoption = data['feature_adoption']
    engagement = data['engagement_scores']
    tier_mismatch = data['tier_mismatch']
    cohorts = data['cohort_analysis']
    recommendations = data['recommendations']

    # Calculate some aggregates
    total_at_risk_revenue = sum(c['monthly_revenue'] for c in churn_risk) if churn_risk else 0
    total_expansion_revenue = sum(e['potential_expansion_revenue'] for e in expansion) if expansion else 0

    # Build metric cards
    metric_cards = f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Customers</div>
                <div class="metric-value">{format_number(summary['total_customers'])}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">At-Risk Customers</div>
                <div class="metric-value">{len(churn_risk)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #d32f2f 0%, #f57c00 100%);">
                <div class="metric-label">Revenue at Risk</div>
                <div class="metric-value">{format_currency(total_at_risk_revenue, 0)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="metric-label">Expansion Opps</div>
                <div class="metric-value">{len(expansion)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="metric-label">Expansion Revenue</div>
                <div class="metric-value">{format_currency(total_expansion_revenue, 0)}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="metric-label">Avg Features/Customer</div>
                <div class="metric-value">{feature_adoption['avg_features_per_customer']:.1f}</div>
            </div>
        </div>
    """

    # Churn risk table
    churn_rows = ""
    for c in churn_risk[:20]:  # Top 20 at-risk
        risk_color = '#d32f2f' if c['risk_score'] >= 70 else '#f57c00' if c['risk_score'] >= 50 else '#ff9800'
        risk_factors_str = ', '.join(f.replace('_', ' ') for f in c['risk_factors'][:3])

        churn_rows += f"""
            <tr>
                <td>{c['customer_id']}</td>
                <td>{c['tier'].title()}</td>
                <td style="text-align: right; color: {risk_color}; font-weight: bold;">{c['risk_score']}</td>
                <td style="text-align: right; color: #d32f2f;">{c['growth_rate']:.0f}%</td>
                <td style="text-align: right;">{format_number(c['total_calls'])}</td>
                <td style="text-align: right;">{format_currency(c['monthly_revenue'], 0)}</td>
                <td style="font-size: 12px;">{risk_factors_str}</td>
            </tr>
        """

    churn_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Tier</th>
                    <th style="text-align: right;">Risk Score</th>
                    <th style="text-align: right;">Growth Rate</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Monthly Revenue</th>
                    <th>Risk Factors</th>
                </tr>
            </thead>
            <tbody>
                {churn_rows}
            </tbody>
        </table>
    """ if churn_risk else "<p style='color: #666;'>No customers at significant churn risk.</p>"

    # Expansion opportunities table
    expansion_rows = ""
    for e in expansion[:20]:  # Top 20 opportunities
        expansion_color = '#43e97b' if e['expansion_score'] >= 70 else '#4facfe'
        signals_str = ', '.join(s.replace('_', ' ') for s in e['signals'][:3])

        expansion_rows += f"""
            <tr>
                <td>{e['customer_id']}</td>
                <td>{e['current_tier'].title()}</td>
                <td style="text-align: right; color: {expansion_color}; font-weight: bold;">{e['expansion_score']}</td>
                <td style="text-align: right; color: #43e97b;">{e['growth_rate']:.0f}%</td>
                <td style="text-align: right;">{format_number(e['total_calls'])}</td>
                <td style="text-align: right;">{format_currency(e['current_monthly_revenue'], 0)}</td>
                <td style="text-align: right; color: #43e97b; font-weight: bold;">{format_currency(e['potential_expansion_revenue'], 0)}</td>
                <td style="font-size: 12px;">{signals_str}</td>
            </tr>
        """

    expansion_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Current Tier</th>
                    <th style="text-align: right;">Expansion Score</th>
                    <th style="text-align: right;">Growth Rate</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Current Revenue</th>
                    <th style="text-align: right;">Expansion Revenue</th>
                    <th>Growth Signals</th>
                </tr>
            </thead>
            <tbody>
                {expansion_rows}
            </tbody>
        </table>
    """ if expansion else "<p style='color: #666;'>No expansion opportunities identified.</p>"

    # Engagement scores table
    engagement_rows = ""
    for e in engagement[:15]:  # Top 15
        level_color = '#43e97b' if e['engagement_level'] == 'high' else '#f57c00' if e['engagement_level'] == 'medium' else '#d32f2f'

        engagement_rows += f"""
            <tr>
                <td>{e['customer_id']}</td>
                <td style="text-align: right;">{e['engagement_score']:.1f}</td>
                <td style="color: {level_color}; font-weight: bold;">{e['engagement_level'].upper()}</td>
                <td style="text-align: right;">{format_number(e['call_count'])}</td>
                <td style="text-align: right;">{e['unique_features']}</td>
                <td style="text-align: right;">{format_currency(e['total_spend'])}</td>
            </tr>
        """

    engagement_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th style="text-align: right;">Engagement Score</th>
                    <th>Level</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Features Used</th>
                    <th style="text-align: right;">Total Spend</th>
                </tr>
            </thead>
            <tbody>
                {engagement_rows}
            </tbody>
        </table>
    """

    # Tier mismatch table
    mismatch_rows = ""
    for m in tier_mismatch[:15]:
        mismatch_type_label = "Oversubscribed" if m['mismatch_type'] == 'oversubscribed' else "Undersubscribed"
        mismatch_color = '#f57c00' if m['mismatch_type'] == 'oversubscribed' else '#43e97b'

        mismatch_rows += f"""
            <tr>
                <td>{m['customer_id']}</td>
                <td>{m['current_tier'].title()}</td>
                <td style="color: {mismatch_color}; font-weight: bold;">{mismatch_type_label}</td>
                <td style="text-align: right;">{format_number(m['call_count'])}</td>
                <td style="text-align: right;">{format_currency(m['total_cost'])}</td>
                <td style="text-align: right;">{'🔴' if m['severity'] >= 3 else '⚠️'}</td>
            </tr>
        """

    mismatch_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Customer ID</th>
                    <th>Current Tier</th>
                    <th>Mismatch Type</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Total Cost</th>
                    <th style="text-align: right;">Severity</th>
                </tr>
            </thead>
            <tbody>
                {mismatch_rows}
            </tbody>
        </table>
    """ if tier_mismatch else "<p style='color: #666;'>No significant tier mismatches detected.</p>"

    # Cohort analysis table
    cohort_rows = ""
    for c in cohorts['cohorts']:
        cohort_rows += f"""
            <tr>
                <td>{c['tier'].title()}</td>
                <td>{c['archetype'].title()}</td>
                <td style="text-align: right;">{format_number(c['customer_count'])}</td>
                <td style="text-align: right;">{format_number(c['total_calls'])}</td>
                <td style="text-align: right;">{c['avg_calls_per_customer']:.0f}</td>
                <td style="text-align: right;">{format_currency(c['total_cost'])}</td>
            </tr>
        """

    cohort_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Tier</th>
                    <th>Archetype</th>
                    <th style="text-align: right;">Customers</th>
                    <th style="text-align: right;">Total Calls</th>
                    <th style="text-align: right;">Avg Calls/Customer</th>
                    <th style="text-align: right;">Total Cost</th>
                </tr>
            </thead>
            <tbody>
                {cohort_rows}
            </tbody>
        </table>
    """

    # Feature adoption breakdown
    feature_adoption_html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #333;">Feature Adoption Metrics</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div>
                    <strong>Single-Feature Customers:</strong><br>
                    <span style="font-size: 24px; color: #667eea;">{format_number(feature_adoption['single_feature_customers'])}</span>
                    <span style="color: #666; font-size: 13px;"> ({(feature_adoption['single_feature_customers'] / feature_adoption['total_customers'] * 100):.1f}%)</span>
                </div>
                <div>
                    <strong>Multi-Feature Customers:</strong><br>
                    <span style="font-size: 24px; color: #43e97b;">{format_number(feature_adoption['multi_feature_customers'])}</span>
                    <span style="color: #666; font-size: 13px;"> ({(feature_adoption['multi_feature_customers'] / feature_adoption['total_customers'] * 100):.1f}%)</span>
                </div>
                <div>
                    <strong>Avg Features per Customer:</strong><br>
                    <span style="font-size: 24px; color: #4facfe;">{feature_adoption['avg_features_per_customer']:.2f}</span>
                </div>
            </div>
        </div>
    """

    # Charts
    velocity_growing = len([v for v in velocity if v['trend'] == 'growing'])
    velocity_stable = len([v for v in velocity if v['trend'] == 'stable'])
    velocity_declining = len([v for v in velocity if v['trend'] == 'declining'])

    scripts = f"""
    <script>
        // Usage velocity distribution
        new Chart(document.getElementById('velocityChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Growing', 'Stable', 'Declining'],
                datasets: [{{
                    data: [{velocity_growing}, {velocity_stable}, {velocity_declining}],
                    backgroundColor: [
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(211, 47, 47, 0.8)'
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

        // Engagement level distribution
        var engagementHigh = {len([e for e in engagement if e['engagement_level'] == 'high'])};
        var engagementMedium = {len([e for e in engagement if e['engagement_level'] == 'medium'])};
        var engagementLow = {len([e for e in engagement if e['engagement_level'] == 'low'])};

        new Chart(document.getElementById('engagementChart'), {{
            type: 'bar',
            data: {{
                labels: ['High', 'Medium', 'Low'],
                datasets: [{{
                    label: 'Customers by Engagement Level',
                    data: [engagementHigh, engagementMedium, engagementLow],
                    backgroundColor: [
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(211, 47, 47, 0.8)'
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
    </script>
    """

    # Build complete content
    content = f"""
        <h1>📈 Churn Risk & Growth Signals</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px;">
            Customer engagement analysis, expansion opportunities, and retention insights
        </p>

        <h2>Summary Metrics</h2>
        {metric_cards}

        <h2>Usage Velocity Trends</h2>
        <div class="chart-container">
            <canvas id="velocityChart"></canvas>
        </div>
        <p style="color: #666; margin-top: 20px;">
            Customer usage trends over the analysis period: {summary['analysis_period']}.
            Growing customers show &gt;20% increase, declining show &gt;20% decrease.
        </p>

        <h2>Churn Risk Customers</h2>
        <div class="alert alert-critical" style="margin-bottom: 20px;">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <div class="alert-title">Action Required</div>
                <div class="alert-description">
                    {len(churn_risk)} customers at churn risk representing {format_currency(total_at_risk_revenue, 0)} in monthly revenue.
                    Immediate customer success intervention recommended.
                </div>
            </div>
        </div>
        {churn_table}

        <h2>Expansion Opportunities</h2>
        <div class="alert alert-success" style="margin-bottom: 20px;">
            <div class="alert-icon">💰</div>
            <div class="alert-content">
                <div class="alert-title">Revenue Growth Potential</div>
                <div class="alert-description">
                    {len(expansion)} customers ready for tier upgrades with {format_currency(total_expansion_revenue, 0)} in potential monthly expansion revenue.
                </div>
            </div>
        </div>
        {expansion_table}

        <h2>Customer Engagement Scores</h2>
        <div class="chart-container">
            <canvas id="engagementChart"></canvas>
        </div>
        {engagement_table}

        {feature_adoption_html}

        <h2>Tier Mismatch Analysis</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Customers on the wrong tier for their usage patterns - both upgrade and downgrade opportunities.
        </p>
        {mismatch_table}

        <h2>Cohort Analysis</h2>
        <p style="color: #666; margin-bottom: 20px;">
            Customer segmentation by subscription tier and usage archetype.
        </p>
        {cohort_table}

        <h2>Recommendations</h2>
        {build_recommendations_html(recommendations)}
    """

    # Build final HTML
    html = build_html_template("Churn Risk & Growth Signals", content, scripts)

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Churn & growth report generated: {output_path}")
