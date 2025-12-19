#!/usr/bin/env python3
"""
FinOps Domain: Performance Tracking
Analyzes model efficiency, latency, and cost-performance tradeoffs
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class PerformanceTrackingAnalyzer:
    """Analyzes model performance and efficiency"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
    def _load_data(self) -> List[Dict]:
        """Load AI call data from CSV"""
        calls = []
        with open(self.data_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['cost_usd'] = float(row['cost_usd'])
                row['input_tokens'] = int(row['input_tokens'])
                row['output_tokens'] = int(row['output_tokens'])
                row['latency_ms'] = int(row['latency_ms'])
                calls.append(row)
        return calls
    
    def model_efficiency_comparison(self) -> Dict:
        """Compare cost efficiency across models"""
        model_stats = defaultdict(lambda: {
            'total_cost': 0,
            'total_calls': 0,
            'total_tokens': 0,
            'total_latency': 0,
            'task_types': defaultdict(int)
        })
        
        for call in self.calls:
            model = call['model']
            stats = model_stats[model]
            stats['total_cost'] += call['cost_usd']
            stats['total_calls'] += 1
            stats['total_tokens'] += call['input_tokens'] + call['output_tokens']
            stats['total_latency'] += call['latency_ms']
            stats['task_types'][call['task_type']] += 1
        
        # Calculate averages
        results = {}
        for model, stats in model_stats.items():
            results[model] = {
                'avg_cost_per_call': stats['total_cost'] / stats['total_calls'],
                'avg_cost_per_1k_tokens': (stats['total_cost'] / (stats['total_tokens'] / 1000)),
                'avg_latency_ms': stats['total_latency'] / stats['total_calls'],
                'total_calls': stats['total_calls'],
                'total_cost': stats['total_cost'],
                'primary_task': max(stats['task_types'].items(), key=lambda x: x[1])[0]
            }
        
        return results
    
    def latency_analysis(self) -> Dict:
        """Analyze latency patterns by model and task"""
        latency_by_model = defaultdict(list)
        latency_by_task = defaultdict(list)
        
        for call in self.calls:
            latency_by_model[call['model']].append(call['latency_ms'])
            latency_by_task[call['task_type']].append(call['latency_ms'])
        
        def calc_percentiles(values):
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                'p50': sorted_vals[n//2],
                'p95': sorted_vals[int(n*0.95)],
                'p99': sorted_vals[int(n*0.99)],
                'avg': sum(values) / len(values)
            }
        
        return {
            'by_model': {model: calc_percentiles(latencies) 
                        for model, latencies in latency_by_model.items()},
            'by_task': {task: calc_percentiles(latencies) 
                       for task, latencies in latency_by_task.items()}
        }
    
    def cost_performance_tradeoff(self) -> Dict:
        """Analyze cost vs performance tradeoffs"""
        model_metrics = defaultdict(lambda: {
            'costs': [],
            'latencies': [],
            'tokens': []
        })
        
        for call in self.calls:
            model = call['model']
            model_metrics[model]['costs'].append(call['cost_usd'])
            model_metrics[model]['latencies'].append(call['latency_ms'])
            model_metrics[model]['tokens'].append(call['input_tokens'] + call['output_tokens'])
        
        results = {}
        for model, metrics in model_metrics.items():
            avg_cost = sum(metrics['costs']) / len(metrics['costs'])
            avg_latency = sum(metrics['latencies']) / len(metrics['latencies'])
            avg_tokens = sum(metrics['tokens']) / len(metrics['tokens'])
            
            # Calculate efficiency score (lower is better)
            # Normalized: cost weight 60%, latency weight 40%
            cost_norm = avg_cost / 0.1  # Normalize to ~$0.10 baseline
            latency_norm = avg_latency / 1000  # Normalize to 1000ms baseline
            efficiency_score = (cost_norm * 0.6) + (latency_norm * 0.4)
            
            results[model] = {
                'avg_cost': avg_cost,
                'avg_latency': avg_latency,
                'avg_tokens': avg_tokens,
                'efficiency_score': efficiency_score,
                'cost_per_second': avg_cost / (avg_latency / 1000)
            }
        
        return results
    
    def recommend_optimal_model(self) -> Dict:
        """Recommend optimal model per use case"""
        task_model_performance = defaultdict(lambda: defaultdict(lambda: {
            'total_cost': 0,
            'total_latency': 0,
            'count': 0
        }))
        
        for call in self.calls:
            task = call['task_type']
            model = call['model']
            perf = task_model_performance[task][model]
            perf['total_cost'] += call['cost_usd']
            perf['total_latency'] += call['latency_ms']
            perf['count'] += 1
        
        recommendations = {}
        for task, models in task_model_performance.items():
            model_scores = {}
            for model, perf in models.items():
                avg_cost = perf['total_cost'] / perf['count']
                avg_latency = perf['total_latency'] / perf['count']
                
                # Score: balance cost and speed
                score = (avg_cost * 100) + (avg_latency / 10)  # Lower is better
                model_scores[model] = {
                    'score': score,
                    'avg_cost': avg_cost,
                    'avg_latency': avg_latency,
                    'sample_size': perf['count']
                }
            
            # Find best model
            best_model = min(model_scores.items(), key=lambda x: x[1]['score'])
            recommendations[task] = {
                'recommended_model': best_model[0],
                'metrics': best_model[1],
                'alternatives': dict(sorted(model_scores.items(), key=lambda x: x[1]['score'])[:3])
            }
        
        return recommendations
    
    def generate_report(self, output_file: str = 'reports/finops_performance.md'):
        """Generate markdown report"""
        
        efficiency = self.model_efficiency_comparison()
        latency = self.latency_analysis()
        tradeoff = self.cost_performance_tradeoff()
        recommendations = self.recommend_optimal_model()
        
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        report = f"""# FinOps Domain: Performance Tracking

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report analyzes model performance, efficiency, and cost-performance tradeoffs to identify optimization opportunities.

---

## Model Efficiency Comparison

| Model | Avg Cost/Call | Cost/1K Tokens | Avg Latency | Total Calls | Total Cost |
|-------|---------------|----------------|-------------|-------------|------------|
"""
        
        for model, stats in sorted(efficiency.items(), key=lambda x: x[1]['total_cost'], reverse=True):
            report += f"| {model} | ${stats['avg_cost_per_call']:.4f} | "
            report += f"${stats['avg_cost_per_1k_tokens']:.4f} | "
            report += f"{stats['avg_latency_ms']:.0f}ms | "
            report += f"{stats['total_calls']:,} | ${stats['total_cost']:,.2f} |\n"
        
        report += "\n---\n\n## Latency Analysis by Model\n\n"
        report += "| Model | P50 | P95 | P99 | Average |\n"
        report += "|-------|-----|-----|-----|----------|\n"
        
        for model, stats in sorted(latency['by_model'].items()):
            report += f"| {model} | {stats['p50']}ms | {stats['p95']}ms | "
            report += f"{stats['p99']}ms | {stats['avg']:.0f}ms |\n"
        
        report += "\n---\n\n## Latency Analysis by Task Type\n\n"
        report += "| Task Type | P50 | P95 | P99 | Average |\n"
        report += "|-----------|-----|-----|-----|----------|\n"
        
        for task, stats in sorted(latency['by_task'].items()):
            report += f"| {task} | {stats['p50']}ms | {stats['p95']}ms | "
            report += f"{stats['p99']}ms | {stats['avg']:.0f}ms |\n"
        
        report += "\n---\n\n## Cost-Performance Tradeoff Analysis\n\n"
        report += "| Model | Avg Cost | Avg Latency | Efficiency Score | Cost/Second |\n"
        report += "|-------|----------|-------------|------------------|-------------|\n"
        
        for model, metrics in sorted(tradeoff.items(), key=lambda x: x[1]['efficiency_score']):
            report += f"| {model} | ${metrics['avg_cost']:.4f} | "
            report += f"{metrics['avg_latency']:.0f}ms | "
            report += f"{metrics['efficiency_score']:.2f} | "
            report += f"${metrics['cost_per_second']:.4f} |\n"
        
        report += "\n*Lower efficiency score is better (weighted: 60% cost, 40% latency)*\n"
        
        report += "\n---\n\n## Optimal Model Recommendations by Task\n\n"
        
        for task, rec in sorted(recommendations.items()):
            report += f"### {task.replace('_', ' ').title()}\n\n"
            report += f"**Recommended**: `{rec['recommended_model']}`\n\n"
            report += f"- Average Cost: ${rec['metrics']['avg_cost']:.4f}\n"
            report += f"- Average Latency: {rec['metrics']['avg_latency']:.0f}ms\n"
            report += f"- Sample Size: {rec['metrics']['sample_size']:,} calls\n\n"
            
            if len(rec['alternatives']) > 1:
                report += "**Alternatives**:\n"
                for alt_model, alt_metrics in list(rec['alternatives'].items())[1:]:
                    report += f"- `{alt_model}`: ${alt_metrics['avg_cost']:.4f}, "
                    report += f"{alt_metrics['avg_latency']:.0f}ms\n"
            report += "\n"
        
        report += "---\n\n## Key Insights\n\n"
        
        # Most efficient model
        best_efficiency = min(tradeoff.items(), key=lambda x: x[1]['efficiency_score'])
        report += f"1. **Most Efficient Model**: `{best_efficiency[0]}` "
        report += f"(efficiency score: {best_efficiency[1]['efficiency_score']:.2f})\n"
        
        # Fastest model
        fastest = min(latency['by_model'].items(), key=lambda x: x[1]['avg'])
        report += f"2. **Fastest Model**: `{fastest[0]}` (avg: {fastest[1]['avg']:.0f}ms)\n"
        
        # Most cost-effective
        cheapest = min(efficiency.items(), key=lambda x: x[1]['avg_cost_per_call'])
        report += f"3. **Most Cost-Effective**: `{cheapest[0]}` "
        report += f"(${cheapest[1]['avg_cost_per_call']:.4f} per call)\n"
        
        # Calculate potential savings
        current_cost = sum(eff['total_cost'] for eff in efficiency.values())
        
        # Estimate savings if all tasks used optimal model
        potential_savings = 0
        for task, rec in recommendations.items():
            task_calls = [c for c in self.calls if c['task_type'] == task]
            current_task_cost = sum(c['cost_usd'] for c in task_calls)
            optimal_cost = rec['metrics']['avg_cost'] * len(task_calls)
            potential_savings += max(0, current_task_cost - optimal_cost)
        
        report += f"4. **Optimization Potential**: ${potential_savings:,.2f} monthly savings "
        report += f"({potential_savings/current_cost*100:.1f}% reduction)\n"
        
        report += "\n---\n\n## Recommendations\n\n"
        
        report += "### Immediate Actions\n\n"
        report += f"1. **Model Migration**: Switch to optimal models per task type (save ${potential_savings:,.2f}/month)\n"
        report += f"2. **Performance Monitoring**: Set up P95 latency alerts (threshold: {max(l['p95'] for l in latency['by_model'].values())}ms)\n"
        report += "3. **Cost Optimization**: Review high-cost models for potential alternatives\n"
        
        report += "\n### Long-term Strategy\n\n"
        report += "1. **A/B Testing**: Validate model quality before full migration\n"
        report += "2. **Dynamic Routing**: Route tasks to optimal models automatically\n"
        report += "3. **SLA Definition**: Set latency and cost targets per task type\n"
        report += "4. **Continuous Monitoring**: Track efficiency scores monthly\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Performance Tracking report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = PerformanceTrackingAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
