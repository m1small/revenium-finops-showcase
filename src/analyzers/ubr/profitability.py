#!/usr/bin/env python3
"""
UBR Analysis: Customer Profitability
Analyzes cost to serve each customer and identifies margin opportunities
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class CustomerProfitabilityAnalyzer:
    """Analyze customer profitability and margins"""
    
    SUBSCRIPTION_TIERS = {
        'starter': 29,
        'pro': 99,
        'enterprise': 299
    }
    
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        """Load CSV data"""
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            self.calls = list(reader)
        
        for call in self.calls:
            call['cost_usd'] = float(call['cost_usd'])
    
    def analyze(self) -> Dict:
        """Run profitability analysis"""
        return {
            'customer_metrics': self.analyze_customers(),
            'tier_analysis': self.analyze_by_tier(),
            'unprofitable': self.identify_unprofitable(),
            'margin_distribution': self.calculate_margin_distribution(),
            'recommendations': self.generate_recommendations()
        }
    
    def analyze_customers(self) -> List[Dict]:
        """Analyze each customer's profitability"""
        by_customer = defaultdict(lambda: {'cost': 0, 'calls': 0, 'tier': None})
        
        for call in self.calls:
            customer_id = call['customer_id']
            by_customer[customer_id]['cost'] += call['cost_usd']
            by_customer[customer_id]['calls'] += 1
            by_customer[customer_id]['tier'] = call['subscription_tier']
        
        results = []
        for customer_id, data in by_customer.items():
            monthly_revenue = self.SUBSCRIPTION_TIERS[data['tier']]
            monthly_cost = data['cost']
            margin = monthly_revenue - monthly_cost
            margin_pct = (margin / monthly_revenue * 100) if monthly_revenue > 0 else 0
            
            results.append({
                'customer_id': customer_id,
                'tier': data['tier'],
                'revenue': monthly_revenue,
                'cost': monthly_cost,
                'margin': margin,
                'margin_pct': margin_pct,
                'calls': data['calls'],
                'profitable': margin > 0
            })
        
        return sorted(results, key=lambda x: x['margin'])
    
    def analyze_by_tier(self) -> List[Dict]:
        """Analyze profitability by subscription tier"""
        by_tier = defaultdict(lambda: {'customers': 0, 'revenue': 0, 'cost': 0})
        
        customers = self.analyze_customers()
        for customer in customers:
            tier = customer['tier']
            by_tier[tier]['customers'] += 1
            by_tier[tier]['revenue'] += customer['revenue']
            by_tier[tier]['cost'] += customer['cost']
        
        results = []
        for tier, data in by_tier.items():
            margin = data['revenue'] - data['cost']
            margin_pct = (margin / data['revenue'] * 100) if data['revenue'] > 0 else 0
            
            results.append({
                'tier': tier,
                'customers': data['customers'],
                'revenue': data['revenue'],
                'cost': data['cost'],
                'margin': margin,
                'margin_pct': margin_pct
            })
        
        return sorted(results, key=lambda x: x['margin'], reverse=True)
    
    def identify_unprofitable(self) -> Dict:
        """Identify unprofitable customers"""
        customers = self.analyze_customers()
        unprofitable = [c for c in customers if not c['profitable']]
        
        total_loss = sum(abs(c['margin']) for c in unprofitable)
        
        return {
            'count': len(unprofitable),
            'customers': unprofitable[:10],  # Top 10 worst
            'total_loss': total_loss,
            'percentage': (len(unprofitable) / len(customers) * 100) if customers else 0
        }
    
    def calculate_margin_distribution(self) -> Dict:
        """Calculate margin distribution across customers"""
        customers = self.analyze_customers()
        
        high_margin = [c for c in customers if c['margin_pct'] > 50]
        medium_margin = [c for c in customers if 20 <= c['margin_pct'] <= 50]
        low_margin = [c for c in customers if 0 < c['margin_pct'] < 20]
        negative_margin = [c for c in customers if c['margin_pct'] <= 0]
        
        return {
            'high_margin': {'count': len(high_margin), 'avg_margin': sum(c['margin'] for c in high_margin) / len(high_margin) if high_margin else 0},
            'medium_margin': {'count': len(medium_margin), 'avg_margin': sum(c['margin'] for c in medium_margin) / len(medium_margin) if medium_margin else 0},
            'low_margin': {'count': len(low_margin), 'avg_margin': sum(c['margin'] for c in low_margin) / len(low_margin) if low_margin else 0},
            'negative_margin': {'count': len(negative_margin), 'avg_loss': sum(c['margin'] for c in negative_margin) / len(negative_margin) if negative_margin else 0}
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        unprofitable = self.identify_unprofitable()
        
        if unprofitable['count'] > 0:
            recommendations.append(
                f"🚨 {unprofitable['count']} unprofitable customers losing ${unprofitable['total_loss']:,.2f}/month - implement usage caps or tier upgrades"
            )
        
        tier_analysis = self.analyze_by_tier()
        for tier_data in tier_analysis:
            if tier_data['margin_pct'] < 30:
                recommendations.append(
                    f"⚠️ {tier_data['tier'].title()} tier has low margin ({tier_data['margin_pct']:.1f}%) - consider price increase"
                )
        
        return recommendations
    
    def generate_html_report(self, output_file: str = 'reports/html/customer_profitability.html'):
        """Generate HTML report"""
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        # Build report
        content = html.generate_header(
            "Customer Profitability Analysis",
            "Understand cost to serve and identify margin opportunities",
            {
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Data Source': self.csv_file,
                'Customers Analyzed': str(len(analysis['customer_metrics']))
            }
        )
        
        # Key metrics
        total_revenue = sum(c['revenue'] for c in analysis['customer_metrics'])
        total_cost = sum(c['cost'] for c in analysis['customer_metrics'])
        total_margin = total_revenue - total_cost
        margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
        
        content += html.generate_metric_card(
            "Overall Margin",
            f"{margin_pct:.1f}%",
            f"${total_margin:,.2f} profit on ${total_revenue:,.2f} revenue"
        )
        
        # Unprofitable customers alert
        unprofitable = analysis['unprofitable']
        if unprofitable['count'] > 0:
            content += html.generate_alert(
                f"⚠️ {unprofitable['count']} customers ({unprofitable['percentage']:.1f}%) are unprofitable, losing ${unprofitable['total_loss']:,.2f}/month",
                'danger'
            )
        
        # Tier analysis with chart
        content += "<h2>Profitability by Subscription Tier</h2>\n"
        tier_data = analysis['tier_analysis']
        
        # Chart 1: Tier Revenue vs Cost Comparison
        content += '<div class="charts-grid">\n'
        tier_chart_data = {
            'labels': [t['tier'].title() for t in tier_data],
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': [t['revenue'] for t in tier_data],
                    'backgroundColor': 'rgba(102, 126, 234, 0.8)',
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Cost',
                    'data': [t['cost'] for t in tier_data],
                    'backgroundColor': 'rgba(237, 100, 166, 0.8)',
                    'borderColor': 'rgba(237, 100, 166, 1)',
                    'borderWidth': 2
                }
            ]
        }
        content += html.generate_chart('tierRevenueChart', 'bar', tier_chart_data, 'Revenue vs Cost by Tier')
        
        # Chart 2: Margin Percentage by Tier
        margin_chart_data = {
            'labels': [t['tier'].title() for t in tier_data],
            'datasets': [{
                'label': 'Margin %',
                'data': [t['margin_pct'] for t in tier_data],
                'backgroundColor': [
                    'rgba(73, 219, 199, 0.8)' if t['margin_pct'] > 50 else
                    'rgba(255, 195, 113, 0.8)' if t['margin_pct'] > 20 else
                    'rgba(255, 107, 107, 0.8)'
                    for t in tier_data
                ],
                'borderColor': 'rgba(102, 126, 234, 1)',
                'borderWidth': 2
            }]
        }
        content += html.generate_chart('tierMarginChart', 'bar', margin_chart_data, 'Profit Margin % by Tier')
        content += '</div>\n'
        
        content += html.generate_table(
            ['Tier', 'Customers', 'Revenue', 'Cost', 'Margin', 'Margin %'],
            [[t['tier'].title(), str(t['customers']), f"${t['revenue']:,.2f}",
              f"${t['cost']:,.2f}", f"${t['margin']:,.2f}", f"{t['margin_pct']:.1f}%"]
             for t in tier_data]
        )
        
        # Margin distribution with charts
        content += "<h2>Customer Margin Distribution</h2>\n"
        dist = analysis['margin_distribution']
        
        # Chart 3: Margin Distribution Pie Chart
        content += '<div class="charts-grid">\n'
        dist_chart_data = {
            'labels': ['High Margin (>50%)', 'Medium (20-50%)', 'Low (0-20%)', 'Negative'],
            'datasets': [{
                'label': 'Customer Count',
                'data': [
                    dist['high_margin']['count'],
                    dist['medium_margin']['count'],
                    dist['low_margin']['count'],
                    dist['negative_margin']['count']
                ],
                'backgroundColor': [
                    'rgba(73, 219, 199, 0.8)',
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(255, 195, 113, 0.8)',
                    'rgba(255, 107, 107, 0.8)'
                ],
                'borderWidth': 2,
                'borderColor': '#fff'
            }]
        }
        content += html.generate_chart('marginDistChart', 'doughnut', dist_chart_data, 'Customer Distribution by Margin Category')
        
        # Chart 4: Average Margin by Category
        avg_margin_data = {
            'labels': ['High Margin', 'Medium Margin', 'Low Margin', 'Negative Margin'],
            'datasets': [{
                'label': 'Average Margin ($)',
                'data': [
                    dist['high_margin']['avg_margin'],
                    dist['medium_margin']['avg_margin'],
                    dist['low_margin']['avg_margin'],
                    dist['negative_margin']['avg_loss']
                ],
                'backgroundColor': [
                    'rgba(73, 219, 199, 0.8)',
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(255, 195, 113, 0.8)',
                    'rgba(255, 107, 107, 0.8)'
                ],
                'borderColor': 'rgba(102, 126, 234, 1)',
                'borderWidth': 2
            }]
        }
        content += html.generate_chart('avgMarginChart', 'bar', avg_margin_data, 'Average Margin by Category')
        content += '</div>\n'
        
        content += html.generate_metric_grid([
            {'label': 'High Margin (>50%)', 'value': str(dist['high_margin']['count']),
             'subtitle': f"Avg: ${dist['high_margin']['avg_margin']:.2f}"},
            {'label': 'Medium Margin (20-50%)', 'value': str(dist['medium_margin']['count']),
             'subtitle': f"Avg: ${dist['medium_margin']['avg_margin']:.2f}"},
            {'label': 'Low Margin (0-20%)', 'value': str(dist['low_margin']['count']),
             'subtitle': f"Avg: ${dist['low_margin']['avg_margin']:.2f}"},
            {'label': 'Negative Margin', 'value': str(dist['negative_margin']['count']),
             'subtitle': f"Avg Loss: ${dist['negative_margin']['avg_loss']:.2f}"}
        ])
        
        # Top unprofitable customers
        if unprofitable['customers']:
            content += "<h2>Most Unprofitable Customers</h2>\n"
            content += html.generate_table(
                ['Customer', 'Tier', 'Revenue', 'Cost', 'Loss', 'Calls'],
                [[c['customer_id'], c['tier'], f"${c['revenue']:.2f}", 
                  f"${c['cost']:.2f}", f"${abs(c['margin']):.2f}", str(c['calls'])]
                 for c in unprofitable['customers']]
            )
        
        # Recommendations
        content += "<h2>Recommendations</h2>\n"
        for rec in analysis['recommendations']:
            alert_type = 'danger' if '🚨' in rec else 'warning'
            content += html.generate_alert(rec, alert_type)
        
        # Revenium value
        revenium_content = """
        <h2>How Revenium Enables Customer Profitability Analysis</h2>
        <h3>Real-Time Cost Attribution</h3>
        <ul>
            <li><code>customer_id</code> metadata enables per-customer cost tracking</li>
            <li><code>subscription_tier</code> links usage to revenue</li>
            <li>Automatic aggregation across all AI providers</li>
            <li>Real-time margin calculations</li>
        </ul>
        """
        
        without = """
        <ul>
            <li>❌ Manual cost allocation across customers</li>
            <li>❌ Delayed profitability insights</li>
            <li>❌ No real-time margin visibility</li>
            <li>❌ Complex revenue-cost reconciliation</li>
        </ul>
        """
        
        with_rev = """
        <ul>
            <li>✅ Automatic per-customer cost tracking</li>
            <li>✅ Real-time profitability alerts</li>
            <li>✅ Instant margin calculations</li>
            <li>✅ Proactive intervention opportunities</li>
        </ul>
        """
        
        revenium_content += html.generate_comparison(without, with_rev)
        content += html.generate_revenium_value_section(revenium_content)
        
        # Save
        full_html = html.wrap_html(content, "Customer Profitability - Revenium UBR")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    """Run analyzer as standalone script"""
    print("📊 Running Customer Profitability Analysis...")
    analyzer = CustomerProfitabilityAnalyzer()
    analyzer.generate_html_report()
    print("✅ Analysis complete!")


if __name__ == '__main__':
    main()
