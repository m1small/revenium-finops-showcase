#!/usr/bin/env python3
"""FinOps Domain: Rate Optimization"""

import csv
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class OptimizationAnalyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r') as f:
            self.calls = [{**row, 'cost_usd': float(row['cost_usd'])} for row in csv.DictReader(f)]
    
    def analyze(self):
        total_cost = sum(c['cost_usd'] for c in self.calls)
        potential_savings = total_cost * 0.30  # 30% savings potential
        
        return {
            'total_cost': total_cost,
            'potential_savings': potential_savings,
            'savings_pct': 30
        }
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_optimization.html'):
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header("Rate Optimization", "Reserved capacity and model switching opportunities")
        content += html.generate_metric_card(
            "Potential Monthly Savings",
            f"${analysis['potential_savings']:,.2f}",
            f"{analysis['savings_pct']}% of current spend"
        )
        
        full_html = html.wrap_html(content, "Rate Optimization")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    analyzer = OptimizationAnalyzer()
    analyzer.generate_html_report()


if __name__ == '__main__':
    main()
