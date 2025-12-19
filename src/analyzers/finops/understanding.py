#!/usr/bin/env python3
"""
FinOps Domain: Understanding Usage & Cost
Analyzes cost allocation, forecasting, and token efficiency
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class UnderstandingAnalyzer:
    """Analyze AI usage and cost patterns"""
    
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []
        self.load_data()
    
    def load_data(self):
        """Load CSV data"""
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            self.calls = list(reader)
        
        # Convert numeric fields
        for call in self.calls:
            call['cost_usd'] = float(call['cost_usd'])
            call['input_tokens'] = int(call['input_tokens'])
            call['output_tokens'] = int(call['output_tokens'])
            call['latency_ms'] = int(call['latency_ms'])
    
    def analyze(self) -> Dict:
        """Run all analyses"""
        return {
            'total_metrics': self.calculate_total_metrics(),
            'by_provider': self.analyze_by_provider(),
            'by_model': self.analyze_by_model(),
            'by_customer': self.analyze_by_customer(),
            'by_organization': self.analyze_by_organization(),
            'by_product': self.analyze_by_product(),
            'by_feature': self.analyze_by_feature(),
            'token_efficiency': self.analyze_token_efficiency(),
            'forecast': self.forecast_costs()
        }
    
    def calculate_total_metrics(self) -> Dict:
        """Calculate overall metrics"""
        total_cost = sum(c['cost_usd'] for c in self.calls)
        total_calls = len(self.calls)
        total_input_tokens = sum(c['input_tokens'] for c in self.calls)
        total_output_tokens = sum(c['output_tokens'] for c in self.calls)
        
        return {
            'total_cost': total_cost,
            'total_calls': total_calls,
            'total_tokens': total_input_tokens + total_output_tokens,
            'avg_cost_per_call': total_cost / total_calls if total_calls > 0 else 0,
            'avg_tokens_per_call': (total_input_tokens + total_output_tokens) / total_calls if total_calls > 0 else 0
        }
    
    def analyze_by_provider(self) -> List[Dict]:
        """Analyze costs by provider"""
        by_provider = defaultdict(lambda: {'cost': 0, 'calls': 0, 'tokens': 0})
        
        for call in self.calls:
            provider = call['provider']
            by_provider[provider]['cost'] += call['cost_usd']
            by_provider[provider]['calls'] += 1
            by_provider[provider]['tokens'] += call['input_tokens'] + call['output_tokens']
        
        results = []
        for provider, data in by_provider.items():
            results.append({
                'provider': provider,
                'cost': data['cost'],
                'calls': data['calls'],
                'tokens': data['tokens'],
                'avg_cost': data['cost'] / data['calls']
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)
    
    def analyze_by_model(self) -> List[Dict]:
        """Analyze costs by model"""
        by_model = defaultdict(lambda: {'cost': 0, 'calls': 0, 'tokens': 0})
        
        for call in self.calls:
            model = call['model']
            by_model[model]['cost'] += call['cost_usd']
            by_model[model]['calls'] += 1
            by_model[model]['tokens'] += call['input_tokens'] + call['output_tokens']
        
        results = []
        for model, data in by_model.items():
            results.append({
                'model': model,
                'cost': data['cost'],
                'calls': data['calls'],
                'tokens': data['tokens'],
                'cost_per_1k_tokens': (data['cost'] / data['tokens'] * 1000) if data['tokens'] > 0 else 0
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)
    
    def analyze_by_customer(self) -> List[Dict]:
        """Analyze costs by customer"""
        by_customer = defaultdict(lambda: {'cost': 0, 'calls': 0, 'tier': None})
        
        for call in self.calls:
            customer_id = call['customer_id']
            by_customer[customer_id]['cost'] += call['cost_usd']
            by_customer[customer_id]['calls'] += 1
            by_customer[customer_id]['tier'] = call['subscription_tier']
        
        results = []
        for customer_id, data in by_customer.items():
            results.append({
                'customer_id': customer_id,
                'cost': data['cost'],
                'calls': data['calls'],
                'tier': data['tier']
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)[:20]  # Top 20
    
    def analyze_by_organization(self) -> List[Dict]:
        """Analyze costs by organization"""
        by_org = defaultdict(lambda: {'cost': 0, 'calls': 0})
        
        for call in self.calls:
            org_id = call['organization_id']
            by_org[org_id]['cost'] += call['cost_usd']
            by_org[org_id]['calls'] += 1
        
        results = []
        for org_id, data in by_org.items():
            results.append({
                'organization_id': org_id,
                'cost': data['cost'],
                'calls': data['calls']
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)[:10]  # Top 10
    
    def analyze_by_product(self) -> List[Dict]:
        """Analyze costs by product"""
        by_product = defaultdict(lambda: {'cost': 0, 'calls': 0})
        
        for call in self.calls:
            product_id = call['product_id']
            by_product[product_id]['cost'] += call['cost_usd']
            by_product[product_id]['calls'] += 1
        
        results = []
        for product_id, data in by_product.items():
            results.append({
                'product_id': product_id,
                'cost': data['cost'],
                'calls': data['calls']
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)
    
    def analyze_by_feature(self) -> List[Dict]:
        """Analyze costs by feature"""
        by_feature = defaultdict(lambda: {'cost': 0, 'calls': 0})
        
        for call in self.calls:
            feature_id = call['feature_id']
            by_feature[feature_id]['cost'] += call['cost_usd']
            by_feature[feature_id]['calls'] += 1
        
        results = []
        for feature_id, data in by_feature.items():
            results.append({
                'feature_id': feature_id,
                'cost': data['cost'],
                'calls': data['calls']
            })
        
        return sorted(results, key=lambda x: x['cost'], reverse=True)
    
    def analyze_token_efficiency(self) -> Dict:
        """Analyze token usage efficiency"""
        total_input = sum(c['input_tokens'] for c in self.calls)
        total_output = sum(c['output_tokens'] for c in self.calls)
        total_cost = sum(c['cost_usd'] for c in self.calls)
        
        return {
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'input_output_ratio': total_input / total_output if total_output > 0 else 0,
            'cost_per_1k_tokens': (total_cost / (total_input + total_output) * 1000) if (total_input + total_output) > 0 else 0
        }
    
    def forecast_costs(self) -> Dict:
        """Forecast next 30 days based on current trend"""
        total_cost = sum(c['cost_usd'] for c in self.calls)
        
        # Simple linear forecast (assume same rate continues)
        forecast_30_days = total_cost  # Current 30 days
        forecast_90_days = total_cost * 3
        forecast_annual = total_cost * 12
        
        return {
            'next_30_days': forecast_30_days,
            'next_90_days': forecast_90_days,
            'annual': forecast_annual
        }
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_understanding.html'):
        """Generate HTML report"""
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        # Build report content
        content = html.generate_header(
            "Understanding Usage & Cost",
            "Comprehensive analysis of AI spending patterns and cost allocation",
            {
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Data Source': self.csv_file,
                'Total Calls': f"{analysis['total_metrics']['total_calls']:,}"
            }
        )
        
        # Total metrics
        metrics = analysis['total_metrics']
        content += html.generate_metric_card(
            "Total AI Spend",
            f"${metrics['total_cost']:,.2f}",
            f"Across {metrics['total_calls']:,} API calls"
        )
        
        content += html.generate_metric_grid([
            {'label': 'Average Cost per Call', 'value': f"${metrics['avg_cost_per_call']:.4f}"},
            {'label': 'Total Tokens Processed', 'value': f"{metrics['total_tokens']:,}"},
            {'label': 'Average Tokens per Call', 'value': f"{metrics['avg_tokens_per_call']:.0f}"}
        ])
        
        # Cost by Provider
        content += "<h2>Cost by Provider</h2>\n"
        provider_data = analysis['by_provider']
        content += html.generate_table(
            ['Provider', 'Total Cost', 'Calls', 'Tokens', 'Avg Cost/Call'],
            [[p['provider'], f"${p['cost']:,.2f}", f"{p['calls']:,}", 
              f"{p['tokens']:,}", f"${p['avg_cost']:.4f}"] for p in provider_data]
        )
        
        # Cost by Model
        content += "<h2>Cost by Model</h2>\n"
        model_data = analysis['by_model']
        content += html.generate_bar_chart([
            {'label': m['model'], 'value': m['cost'], 'display': f"${m['cost']:,.2f}"}
            for m in model_data
        ])
        
        # Top Customers
        content += "<h2>Top 20 Customers by Cost</h2>\n"
        customer_data = analysis['by_customer']
        content += html.generate_table(
            ['Customer ID', 'Subscription Tier', 'Total Cost', 'Calls'],
            [[c['customer_id'], c['tier'], f"${c['cost']:,.2f}", f"{c['calls']:,}"] 
             for c in customer_data]
        )
        
        # Cost Hierarchy
        content += "<h2>Cost Allocation Hierarchy</h2>\n"
        content += "<h3>By Organization</h3>\n"
        org_data = analysis['by_organization']
        content += html.generate_table(
            ['Organization', 'Total Cost', 'Calls'],
            [[o['organization_id'], f"${o['cost']:,.2f}", f"{o['calls']:,}"] for o in org_data]
        )
        
        content += "<h3>By Product</h3>\n"
        product_data = analysis['by_product']
        content += html.generate_table(
            ['Product', 'Total Cost', 'Calls'],
            [[p['product_id'], f"${p['cost']:,.2f}", f"{p['calls']:,}"] for p in product_data]
        )
        
        content += "<h3>By Feature</h3>\n"
        feature_data = analysis['by_feature']
        content += html.generate_table(
            ['Feature', 'Total Cost', 'Calls'],
            [[f['feature_id'], f"${f['cost']:,.2f}", f"{f['calls']:,}"] for f in feature_data]
        )
        
        # Token Efficiency
        content += "<h2>Token Efficiency</h2>\n"
        efficiency = analysis['token_efficiency']
        content += html.generate_metric_grid([
            {'label': 'Input Tokens', 'value': f"{efficiency['total_input_tokens']:,}"},
            {'label': 'Output Tokens', 'value': f"{efficiency['total_output_tokens']:,}"},
            {'label': 'Input/Output Ratio', 'value': f"{efficiency['input_output_ratio']:.2f}"},
            {'label': 'Cost per 1K Tokens', 'value': f"${efficiency['cost_per_1k_tokens']:.4f}"}
        ])
        
        # Forecast
        content += "<h2>Cost Forecast</h2>\n"
        forecast = analysis['forecast']
        content += html.generate_metric_grid([
            {'label': 'Next 30 Days', 'value': f"${forecast['next_30_days']:,.2f}"},
            {'label': 'Next 90 Days', 'value': f"${forecast['next_90_days']:,.2f}"},
            {'label': 'Annual Projection', 'value': f"${forecast['annual']:,.2f}"}
        ])
        
        # Revenium Value Section
        revenium_content = """
        <h2>How Revenium Enables This Analysis</h2>
        <h3>Metadata-Driven Allocation</h3>
        <ul>
            <li><code>organization_id</code> → Org-level cost rollups</li>
            <li><code>product_id</code> → Product attribution</li>
            <li><code>customer_id</code> → Customer profitability</li>
            <li><code>feature_id</code> → Feature-level economics</li>
        </ul>
        
        <h3>Real-Time Tracking</h3>
        <ul>
            <li>Async middleware captures every call</li>
            <li>Zero performance impact on AI requests</li>
            <li>Automatic cost calculation</li>
            <li>Multi-provider support (OpenAI, Anthropic, Bedrock)</li>
        </ul>
        """
        
        without = """
        <ul>
            <li>❌ Manual log parsing from multiple sources</li>
            <li>❌ Delayed cost visibility (hours/days)</li>
            <li>❌ Complex ETL pipelines</li>
            <li>❌ No standardized metadata schema</li>
            <li>❌ Provider-specific integration code</li>
        </ul>
        """
        
        with_rev = """
        <ul>
            <li>✅ Automatic capture of all AI calls</li>
            <li>✅ Real-time cost visibility</li>
            <li>✅ Standardized metadata across providers</li>
            <li>✅ Single integration point</li>
            <li>✅ Built-in aggregation and analysis</li>
        </ul>
        """
        
        revenium_content += html.generate_comparison(without, with_rev)
        content += html.generate_revenium_value_section(revenium_content)
        
        # Wrap and save
        full_html = html.wrap_html(content, "Understanding Usage & Cost - Revenium FinOps")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    """Run analyzer as standalone script"""
    print("📊 Running Understanding Usage & Cost Analysis...")
    analyzer = UnderstandingAnalyzer()
    analyzer.generate_html_report()
    print("✅ Analysis complete!")


if __name__ == '__main__':
    main()
