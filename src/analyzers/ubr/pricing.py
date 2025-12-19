#!/usr/bin/env python3
"""UBR Analysis: Pricing Strategy"""

import csv
from collections import defaultdict
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class PricingAnalyzer:
    SUBSCRIPTION_TIERS = {'starter': 29, 'pro': 99, 'enterprise': 299}
    
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r') as f:
            self.calls = [{**row, 'cost_usd': float(row['cost_usd'])} for row in csv.DictReader(f)]
    
    def analyze(self):
        by_customer = defaultdict(lambda: {'cost': 0, 'tier': None})
        
        for call in self.calls:
            by_customer[call['customer_id']]['cost'] += call['cost_usd']
            by_customer[call['customer_id']]['tier'] = call['subscription_tier']
        
        # Calculate revenue under different models
        current_revenue = sum(self.SUBSCRIPTION_TIERS[c['tier']] for c in by_customer.values())
        usage_based_revenue = sum(c['cost'] * 1.5 for c in by_customer.values())  # 50% markup
        
        return {
            'current_model': {'revenue': current_revenue, 'name': 'Flat Subscription'},
            'usage_based': {'revenue': usage_based_revenue, 'name': 'Usage-Based (50% markup)'},
            'improvement': usage_based_revenue - current_revenue
        }
    
    def generate_html_report(self, output_file: str = 'reports/html/pricing_strategy.html'):
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header("Pricing Strategy Analysis", "Compare pricing models and revenue impact")
        
        content += "<h2>Pricing Model Comparison</h2>\n"
        content += html.generate_metric_grid([
            {'label': 'Current (Flat)', 'value': f"${analysis['current_model']['revenue']:,.2f}"},
            {'label': 'Usage-Based', 'value': f"${analysis['usage_based']['revenue']:,.2f}"},
            {'label': 'Potential Increase', 'value': f"${analysis['improvement']:,.2f}",
             'subtitle': f"{(analysis['improvement']/analysis['current_model']['revenue']*100):.1f}% improvement"}
        ])
        
        if analysis['improvement'] > 0:
            content += html.generate_alert(
                f"💡 Switching to usage-based pricing could increase revenue by ${analysis['improvement']:,.2f}/month",
                'success'
            )
        
        full_html = html.wrap_html(content, "Pricing Strategy")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    analyzer = PricingAnalyzer()
    analyzer.generate_html_report()


if __name__ == '__main__':
    main()
