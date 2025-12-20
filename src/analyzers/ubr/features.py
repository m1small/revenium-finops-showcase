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
        
        content = html.generate_header(
            "Feature Economics Analysis",
            "Feature profitability and investment recommendations",
            {
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Data Source': self.csv_file,
                'Features Analyzed': str(len(analysis))
            }
        )
        
        # Key metrics
        total_cost = sum(f['cost'] for f in analysis)
        total_calls = sum(f['calls'] for f in analysis)
        
        content += html.generate_metric_card(
            "Total Feature Costs",
            f"${total_cost:,.2f}",
            f"{total_calls:,} total API calls across all features"
        )
        
        # Feature cost analysis with charts
        content += "<h2>Feature Cost Analysis</h2>\n"
        
        # Chart 1: Feature Cost Distribution
        content += '<div class="charts-grid">\n'
        cost_chart_data = {
            'labels': [f['feature'] for f in analysis],
            'datasets': [{
                'label': 'Total Cost ($)',
                'data': [f['cost'] for f in analysis],
                'backgroundColor': [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(237, 100, 166, 0.8)',
                    'rgba(255, 154, 158, 0.8)',
                    'rgba(73, 219, 199, 0.8)',
                    'rgba(255, 195, 113, 0.8)'
                ][:len(analysis)],
                'borderColor': 'rgba(102, 126, 234, 1)',
                'borderWidth': 2
            }]
        }
        content += html.generate_chart('featureCostChart', 'bar', cost_chart_data, 'Total Cost by Feature')
        
        # Chart 2: Customer Adoption by Feature
        adoption_chart_data = {
            'labels': [f['feature'] for f in analysis],
            'datasets': [{
                'label': 'Customer Count',
                'data': [f['customers'] for f in analysis],
                'backgroundColor': [
                    'rgba(73, 219, 199, 0.8)',
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(255, 195, 113, 0.8)',
                    'rgba(237, 100, 166, 0.8)',
                    'rgba(165, 177, 194, 0.8)',
                    'rgba(255, 107, 107, 0.8)'
                ][:len(analysis)],
                'borderColor': 'rgba(73, 219, 199, 1)',
                'borderWidth': 2
            }]
        }
        content += html.generate_chart('featureAdoptionChart', 'bar', adoption_chart_data, 'Customer Adoption by Feature')
        content += '</div>\n'
        
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
        
        # Find most efficient feature
        most_efficient = min(analysis, key=lambda x: x['cost_per_customer'])
        content += html.generate_alert(
            f"⭐ {most_efficient['feature']} is most cost-efficient at ${most_efficient['cost_per_customer']:.2f} per customer",
            'success'
        )
        
        # Revenium value proposition
        revenium_content = """
        <h2>How Revenium Enables Feature Economics Analysis</h2>
        <h3>Granular Feature Tracking</h3>
        <ul>
            <li><code>feature_id</code> metadata enables per-feature cost attribution</li>
            <li>Real-time cost tracking across all AI providers</li>
            <li>Customer adoption metrics by feature</li>
            <li>Investment ROI calculations</li>
        </ul>
        """
        
        without = """
        <ul>
            <li>❌ No visibility into feature-level costs</li>
            <li>❌ Manual cost allocation guesswork</li>
            <li>❌ Delayed investment decisions</li>
            <li>❌ Unknown feature profitability</li>
        </ul>
        """
        
        with_rev = """
        <ul>
            <li>✅ Automatic feature cost tracking</li>
            <li>✅ Real-time profitability insights</li>
            <li>✅ Data-driven investment decisions</li>
            <li>✅ Clear feature ROI visibility</li>
        </ul>
        """
        
        revenium_content += html.generate_comparison(without, with_rev)
        content += html.generate_revenium_value_section(revenium_content)
        
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
