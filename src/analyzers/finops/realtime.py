#!/usr/bin/env python3
"""
FinOps Domain: Real-Time Decision Making
Detects anomalies and provides immediate optimization opportunities
"""

import csv
from collections import defaultdict
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class RealtimeAnalyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        with open(self.csv_file, 'r') as f:
            self.calls = [{**row, 'cost_usd': float(row['cost_usd'])} for row in csv.DictReader(f)]
    
    def analyze(self):
        avg_cost = sum(c['cost_usd'] for c in self.calls) / len(self.calls)
        anomalies = [c for c in self.calls if c['cost_usd'] > avg_cost * 3]
        
        return {
            'anomalies': len(anomalies),
            'avg_cost': avg_cost,
            'high_cost_calls': anomalies[:10]
        }
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_realtime.html'):
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header("Real-Time Decision Making", "Cost anomaly detection and alerts")
        content += html.generate_metric_card("Anomalies Detected", str(analysis['anomalies']))
        content += html.generate_alert(f"Found {analysis['anomalies']} high-cost calls requiring attention", 'warning')
        
        full_html = html.wrap_html(content, "Real-Time Decisions")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    analyzer = RealtimeAnalyzer()
    analyzer.generate_html_report()


if __name__ == '__main__':
    main()
