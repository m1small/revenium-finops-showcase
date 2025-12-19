#!/usr/bin/env python3
"""UBR Analysis: Feature Economics"""

import csv
from collections import defaultdict
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class FeatureAnalyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r') as f:
            self.calls = [{**row, 'cost_usd': float(row['cost_usd'])} for row in csv.DictReader(f)]
    
    def analyze(self):
        by_feature = defaultdict(lambda: {'cost': 0, 'calls': 0, 'customers': set()})
        
        for call in self.calls:
            feature = call['feature_id']
            by_feature[feature]['cost'] += call['cost_usd']
            by_feature[feature]['calls'] += 1
            by_feature[feature]['customers'].add(call['customer_id'])
        
        results = []
        for feature, data in by_feature.items():
            results.append({
                'feature': feature,
                'cost': data['cost'],
                'calls': data['calls'],
                'customers': len(data['customers']),
                'cost_per_customer': data['cost'] / len(data['customers']) if data['customers'] else 0
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)
    
    def generate_html_report(self, output_file: str = 'reports/html/feature_economics.html'):
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header("Feature Economics", "Feature profitability and investment recommendations")
        
        content += "<h2>Feature Cost Analysis</h2>\n"
        content += html.generate_table(
            ['Feature', 'Total Cost', 'Calls', 'Customers', 'Cost/Customer'],
            [[f['feature'], f"${f['cost']:,.2f}", f"{f['calls']:,}", 
              str(f['customers']), f"${f['cost_per_customer']:.2f}"]
             for f in analysis]
        )
        
        # Feature recommendations
        content += "<h2>Investment Recommendations</h2>\n"
        top_feature = analysis[0]
        content += html.generate_alert(
            f"💡 {top_feature['feature']} is your highest-cost feature at ${top_feature['cost']:,.2f}/month with {top_feature['customers']} customers",
            'info'
        )
        
        full_html = html.wrap_html(content, "Feature Economics")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    analyzer = FeatureAnalyzer()
    analyzer.generate_html_report()


if __name__ == '__main__':
    main()
