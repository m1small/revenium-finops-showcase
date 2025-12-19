#!/usr/bin/env python3
"""
FinOps Domain: Performance Tracking
Analyzes model efficiency, latency, and cost-performance tradeoffs
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from utils.html_generator import HTMLReportGenerator


class PerformanceAnalyzer:
    """Analyze AI model performance and efficiency"""
    
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
            call['input_tokens'] = int(call['input_tokens'])
            call['output_tokens'] = int(call['output_tokens'])
            call['latency_ms'] = int(call['latency_ms'])
    
    def analyze(self) -> Dict:
        """Run performance analysis"""
        return {
            'model_efficiency': self.analyze_model_efficiency(),
            'latency_analysis': self.analyze_latency(),
            'cost_performance': self.analyze_cost_performance()
        }
    
    def analyze_model_efficiency(self) -> List[Dict]:
        """Analyze efficiency by model"""
        by_model = defaultdict(lambda: {'cost': 0, 'tokens': 0, 'calls': 0, 'latency': []})
        
        for call in self.calls:
            model = call['model']
            tokens = call['input_tokens'] + call['output_tokens']
            by_model[model]['cost'] += call['cost_usd']
            by_model[model]['tokens'] += tokens
            by_model[model]['calls'] += 1
            by_model[model]['latency'].append(call['latency_ms'])
        
        results = []
        for model, data in by_model.items():
            avg_latency = sum(data['latency']) / len(data['latency'])
            cost_per_1k = (data['cost'] / data['tokens'] * 1000) if data['tokens'] > 0 else 0
            
            results.append({
                'model': model,
                'cost': data['cost'],
                'tokens': data['tokens'],
                'calls': data['calls'],
                'cost_per_1k_tokens': cost_per_1k,
                'avg_latency_ms': avg_latency,
                'efficiency_score': (1000 / cost_per_1k) if cost_per_1k > 0 else 0
            })
        
        return sorted(results, key=lambda x: x['efficiency_score'], reverse=True)
    
    def analyze_latency(self) -> Dict:
        """Analyze latency patterns"""
        latencies = [c['latency_ms'] for c in self.calls]
        latencies.sort()
        
        n = len(latencies)
        return {
            'p50': latencies[n // 2],
            'p95': latencies[int(n * 0.95)],
            'p99': latencies[int(n * 0.99)],
            'min': latencies[0],
            'max': latencies[-1],
            'avg': sum(latencies) / n
        }
    
    def analyze_cost_performance(self) -> List[Dict]:
        """Analyze cost vs performance tradeoffs"""
        by_task = defaultdict(lambda: defaultdict(lambda: {'cost': 0, 'latency': [], 'calls': 0}))
        
        for call in self.calls:
            task = call['task_type']
            model = call['model']
            by_task[task][model]['cost'] += call['cost_usd']
            by_task[task][model]['latency'].append(call['latency_ms'])
            by_task[task][model]['calls'] += 1
        
        results = []
        for task, models in by_task.items():
            for model, data in models.items():
                avg_latency = sum(data['latency']) / len(data['latency'])
                avg_cost = data['cost'] / data['calls']
                
                results.append({
                    'task_type': task,
                    'model': model,
                    'avg_cost': avg_cost,
                    'avg_latency': avg_latency,
                    'calls': data['calls']
                })
        
        return results
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_performance.html'):
        """Generate HTML report"""
        analysis = self.analyze()
        html = HTMLReportGenerator()
        
        content = html.generate_header(
            "Performance Tracking",
            "Model efficiency, latency analysis, and cost-performance tradeoffs",
            {
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Data Source': self.csv_file
            }
        )
        
        # Model Efficiency
        content += "<h2>Model Efficiency Comparison</h2>\n"
        efficiency_data = analysis['model_efficiency']
        content += html.generate_table(
            ['Model', 'Efficiency Score', 'Cost/1K Tokens', 'Avg Latency', 'Total Cost', 'Calls'],
            [[e['model'], f"{e['efficiency_score']:.2f}", f"${e['cost_per_1k_tokens']:.4f}",
              f"{e['avg_latency_ms']:.0f}ms", f"${e['cost']:.2f}", str(e['calls'])]
             for e in efficiency_data]
        )
        
        # Latency Analysis
        content += "<h2>Latency Analysis</h2>\n"
        latency = analysis['latency_analysis']
        content += html.generate_metric_grid([
            {'label': 'P50 Latency', 'value': f"{latency['p50']}ms"},
            {'label': 'P95 Latency', 'value': f"{latency['p95']}ms"},
            {'label': 'P99 Latency', 'value': f"{latency['p99']}ms"},
            {'label': 'Average Latency', 'value': f"{latency['avg']:.0f}ms"}
        ])
        
        # Revenium Value
        revenium_content = """
        <h2>How Revenium Enables Performance Tracking</h2>
        <p>Revenium automatically captures latency and cost metrics for every AI call, enabling real-time performance analysis.</p>
        """
        content += html.generate_revenium_value_section(revenium_content)
        
        full_html = html.wrap_html(content, "Performance Tracking - Revenium FinOps")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(full_html)
        
        print(f"✅ Generated HTML report: {output_file}")
        return output_file


def main():
    """Run analyzer as standalone script"""
    print("📊 Running Performance Tracking Analysis...")
    analyzer = PerformanceAnalyzer()
    analyzer.generate_html_report()
    print("✅ Analysis complete!")


if __name__ == '__main__':
    main()
