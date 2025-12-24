"""Performance Tracking Analyzer - FinOps Domain 2."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class PerformanceAnalyzer:
    """Analyzes model efficiency, latency, and cost-performance tradeoffs."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_model': self._analyze_by_model(),
            'latency_analysis': self._analyze_latency(),
            'efficiency_rankings': self._rank_efficiency(),
            'sla_compliance': self._analyze_sla_compliance(),
            'task_recommendations': self._generate_task_recommendations(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall performance summary."""
        total_metrics = aggregate_metrics(self.calls)

        # Calculate tokens per second
        tokens_per_second = []
        for call in self.calls:
            if call['latency_ms'] > 0:
                tps = (call['output_tokens'] / (call['latency_ms'] / 1000.0))
                tokens_per_second.append(tps)

        avg_tps = sum(tokens_per_second) / len(tokens_per_second) if tokens_per_second else 0

        return {
            'total_calls': total_metrics['call_count'],
            'avg_latency_ms': total_metrics['avg_latency_ms'],
            'p50_latency_ms': total_metrics['p50_latency_ms'],
            'p95_latency_ms': total_metrics['p95_latency_ms'],
            'p99_latency_ms': total_metrics['p99_latency_ms'],
            'avg_tokens_per_second': avg_tps
        }

    def _analyze_by_model(self) -> List[Dict[str, Any]]:
        """Analyze performance metrics by model."""
        model_groups = group_by(self.calls, 'provider', 'model')

        results = []
        for (provider, model), calls in model_groups.items():
            metrics = aggregate_metrics(calls)

            # Calculate tokens per second
            tps_values = []
            for call in calls:
                if call['latency_ms'] > 0:
                    tps = call['output_tokens'] / (call['latency_ms'] / 1000.0)
                    tps_values.append(tps)

            avg_tps = sum(tps_values) / len(tps_values) if tps_values else 0

            # Cost per 1K tokens
            cost_per_1k = safe_divide(metrics['total_cost'] * 1000, metrics['total_tokens'])

            # Efficiency score: tokens per second per dollar (higher is better)
            efficiency_score = safe_divide(avg_tps, cost_per_1k) if cost_per_1k > 0 else 0

            results.append({
                'provider': provider,
                'model': model,
                'call_count': metrics['call_count'],
                'avg_latency_ms': metrics['avg_latency_ms'],
                'p50_latency_ms': metrics['p50_latency_ms'],
                'p95_latency_ms': metrics['p95_latency_ms'],
                'p99_latency_ms': metrics['p99_latency_ms'],
                'tokens_per_second': avg_tps,
                'cost_per_1k_tokens': cost_per_1k,
                'efficiency_score': efficiency_score,
                'total_cost': metrics['total_cost']
            })

        return sorted(results, key=lambda x: x['efficiency_score'], reverse=True)

    def _analyze_latency(self) -> Dict[str, Any]:
        """Detailed latency analysis."""
        latencies = [call['latency_ms'] for call in self.calls]

        # Distribution buckets
        buckets = {
            'under_500ms': sum(1 for l in latencies if l < 500),
            '500ms_to_1s': sum(1 for l in latencies if 500 <= l < 1000),
            '1s_to_2s': sum(1 for l in latencies if 1000 <= l < 2000),
            '2s_to_5s': sum(1 for l in latencies if 2000 <= l < 5000),
            'over_5s': sum(1 for l in latencies if l >= 5000)
        }

        total = len(latencies)
        distribution = {k: (v / total * 100) for k, v in buckets.items()}

        return {
            'distribution': distribution,
            'buckets': buckets,
            'min_latency': min(latencies) if latencies else 0,
            'max_latency': max(latencies) if latencies else 0
        }

    def _rank_efficiency(self) -> Dict[str, List[Dict[str, Any]]]:
        """Rank models by different criteria."""
        models = self._analyze_by_model()

        return {
            'by_speed': sorted(models, key=lambda x: x['avg_latency_ms'])[:10],
            'by_cost': sorted(models, key=lambda x: x['cost_per_1k_tokens'])[:10],
            'by_efficiency': sorted(models, key=lambda x: x['efficiency_score'], reverse=True)[:10]
        }

    def _analyze_sla_compliance(self, sla_threshold_ms: int = 2000) -> Dict[str, Any]:
        """Analyze SLA compliance for latency targets."""
        total_calls = len(self.calls)
        within_sla = sum(1 for call in self.calls if call['latency_ms'] <= sla_threshold_ms)
        compliance_pct = (within_sla / total_calls * 100) if total_calls > 0 else 0

        # By model
        model_groups = group_by(self.calls, 'provider', 'model')
        by_model = []

        for (provider, model), calls in model_groups.items():
            model_total = len(calls)
            model_within = sum(1 for c in calls if c['latency_ms'] <= sla_threshold_ms)
            model_compliance = (model_within / model_total * 100) if model_total > 0 else 0

            by_model.append({
                'provider': provider,
                'model': model,
                'compliance_pct': model_compliance,
                'within_sla': model_within,
                'total_calls': model_total
            })

        return {
            'sla_threshold_ms': sla_threshold_ms,
            'overall_compliance_pct': compliance_pct,
            'within_sla': within_sla,
            'total_calls': total_calls,
            'by_model': sorted(by_model, key=lambda x: x['compliance_pct'], reverse=True)
        }

    def _generate_task_recommendations(self) -> Dict[str, str]:
        """Recommend optimal models for different task types."""
        models = self._analyze_by_model()

        recommendations = {}

        # Fast tasks: prioritize speed
        if models:
            fastest = min(models, key=lambda x: x['avg_latency_ms'])
            recommendations['fast_response_needed'] = f"{fastest['model']} (avg {fastest['avg_latency_ms']:.0f}ms)"

        # Cost-sensitive tasks: prioritize cost
        if models:
            cheapest = min(models, key=lambda x: x['cost_per_1k_tokens'])
            recommendations['cost_sensitive'] = f"{cheapest['model']} ({format_currency(cheapest['cost_per_1k_tokens'])}/1K tokens)"

        # Balanced tasks: highest efficiency score
        if models:
            most_efficient = max(models, key=lambda x: x['efficiency_score'])
            recommendations['balanced'] = f"{most_efficient['model']} (efficiency score: {most_efficient['efficiency_score']:.2f})"

        return recommendations

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # SLA compliance check
        sla = self._analyze_sla_compliance()
        if sla['overall_compliance_pct'] < 95:
            recommendations.append(
                f"SLA compliance is {sla['overall_compliance_pct']:.1f}% (target: 95%). "
                f"Consider switching to faster models or optimizing prompts."
            )

        # Model efficiency
        models = self._analyze_by_model()
        if len(models) >= 2:
            most_efficient = models[0]
            least_efficient = models[-1]

            if least_efficient['efficiency_score'] > 0:
                efficiency_ratio = most_efficient['efficiency_score'] / least_efficient['efficiency_score']
                if efficiency_ratio > 3:
                    recommendations.append(
                        f"{most_efficient['model']} is {efficiency_ratio:.1f}x more efficient than "
                        f"{least_efficient['model']}. Consider migrating workloads."
                    )

        # Latency distribution
        latency = self._analyze_latency()
        if latency['distribution']['over_5s'] > 5:
            recommendations.append(
                f"{latency['distribution']['over_5s']:.1f}% of calls exceed 5 seconds. "
                f"Investigate slow queries and consider timeout optimization."
            )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = PerformanceAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Performance Tracking Analysis")
    print("=" * 60)
    print(f"Total Calls:           {format_large_number(summary['total_calls'])}")
    print(f"Avg Latency:           {summary['avg_latency_ms']:.0f}ms")
    print(f"P95 Latency:           {summary['p95_latency_ms']}ms")
    print(f"P99 Latency:           {summary['p99_latency_ms']}ms")
    print(f"Avg Tokens/Second:     {summary['avg_tokens_per_second']:.1f}")
    print()

    # Print SLA compliance
    sla = results['sla_compliance']
    print("SLA Compliance")
    print("-" * 60)
    print(f"Threshold:             {sla['sla_threshold_ms']}ms")
    print(f"Compliance:            {sla['overall_compliance_pct']:.1f}%")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/performance_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
