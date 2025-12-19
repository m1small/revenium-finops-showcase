#!/usr/bin/env python3
"""FinOps Domain: Organizational Alignment"""

import csv
from collections import defaultdict
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class AlignmentAnalyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r') as f:
            self.calls = [{**row, 'cost_usd': float(row['cost_usd'])} for row in csv.DictReader(f)]
    
    def analyze(self):
        by_org = defaultdict(float)
        by_product = defaultdict(float)
        
        for call in self.calls:
            by_org[call['organization_id']] += call['cost_usd']
            by_product[call['product_id']] += call['cost_usd']
        
        return {
            'by_org': dict(by_org),
            'by_product': dict(by_product)
        }
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_alignment.html'):
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header("Organizational Alignment", "Cost by organization, product, and feature")
        
        content += "<h2>Cost by Organization</h2>\n"
        org_items = [{'label': org, 'value': cost, 'display': f"${cost:,.2f}"} 
                     for org, cost in sorted(analysis['by_org'].items(), key=lambda x: x[1], reverse=True)]
        content += html.generate_bar_chart(org_items[:10])
        
        content += "<h2>Cost by Product</h2>\n"
        prod_items = [{'label': prod, 'value': cost, 'display': f"${cost:,.2f}"} 
                      for prod, cost in sorted(analysis['by_product'].items(), key=lambda x: x[1], reverse=True)]
        content += html.generate_bar_chart(prod_items)
        
        full_html = html.wrap_html(content, "Organizational Alignment")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    analyzer = AlignmentAnalyzer()
    analyzer.generate_html_report()


if __name__ == '__main__':
    main()
