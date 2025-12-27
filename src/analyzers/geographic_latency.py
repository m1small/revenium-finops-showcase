"""Geographic & Latency Intelligence Analyzer."""

import sys
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics, calculate_percentile,
    format_currency, format_large_number, safe_divide
)


class GeographicLatencyAnalyzer:
    """Analyzes regional performance, cost arbitrage, and latency patterns."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_region': self._analyze_by_region(),
            'latency_heatmap': self._generate_latency_heatmap(),
            'regional_cost_variance': self._analyze_regional_cost_variance(),
            'provider_by_region': self._analyze_provider_by_region(),
            'cross_region_issues': self._detect_cross_region_issues(),
            'regional_profitability': self._analyze_regional_profitability(),
            'optimal_routing': self._find_optimal_routing(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall geographic summary."""
        regions = set(c['region'] for c in self.calls)

        latencies = [c['latency_ms'] for c in self.calls]
        avg_latency = sum(latencies) / len(latencies)

        # Calculate regional distribution
        region_counts = defaultdict(int)
        for call in self.calls:
            region_counts[call['region']] += 1

        max_region = max(region_counts.items(), key=lambda x: x[1])
        min_region = min(region_counts.items(), key=lambda x: x[1])

        balance_score = (min_region[1] / max_region[1]) * 100  # Percentage

        return {
            'total_regions': len(regions),
            'total_calls': len(self.calls),
            'avg_latency_ms': avg_latency,
            'max_region': max_region[0],
            'max_region_calls': max_region[1],
            'min_region': min_region[0],
            'min_region_calls': min_region[1],
            'regional_balance_score': balance_score
        }

    def _analyze_by_region(self) -> List[Dict[str, Any]]:
        """Analyze metrics by region."""
        region_groups = group_by(self.calls, 'region')

        results = []
        for (region,), calls in region_groups.items():
            metrics = aggregate_metrics(calls)

            latencies = [c['latency_ms'] for c in calls]

            results.append({
                'region': region,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost'],
                'avg_cost_per_call': metrics['avg_cost_per_call'],
                'avg_latency_ms': metrics['avg_latency_ms'],
                'p50_latency_ms': metrics['p50_latency_ms'],
                'p95_latency_ms': metrics['p95_latency_ms'],
                'p99_latency_ms': metrics['p99_latency_ms'],
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies)
            })

        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _generate_latency_heatmap(self) -> List[Dict[str, Any]]:
        """Generate latency heatmap data by region, provider, and model."""
        groups = group_by(self.calls, 'region', 'provider', 'model')

        results = []
        for (region, provider, model), calls in groups.items():
            if len(calls) < 10:  # Skip small samples
                continue

            latencies = [c['latency_ms'] for c in calls]

            results.append({
                'region': region,
                'provider': provider,
                'model': model,
                'call_count': len(calls),
                'avg_latency_ms': sum(latencies) / len(latencies),
                'p95_latency_ms': calculate_percentile(latencies, 95),
                'p99_latency_ms': calculate_percentile(latencies, 99)
            })

        results.sort(key=lambda x: x['avg_latency_ms'])
        return results

    def _analyze_regional_cost_variance(self) -> List[Dict[str, Any]]:
        """Analyze cost variance for same model across regions."""
        model_region_groups = group_by(self.calls, 'model', 'region')

        # Group by model to find variance
        model_costs = defaultdict(list)
        for (model, region), calls in model_region_groups.items():
            avg_cost = sum(c['cost_usd'] for c in calls) / len(calls)
            model_costs[model].append({
                'region': region,
                'avg_cost': avg_cost,
                'call_count': len(calls)
            })

        results = []
        for model, regions in model_costs.items():
            if len(regions) < 2:  # Need at least 2 regions for comparison
                continue

            costs = [r['avg_cost'] for r in regions]
            min_cost = min(costs)
            max_cost = max(costs)
            variance_pct = ((max_cost - min_cost) / min_cost) * 100 if min_cost > 0 else 0

            cheapest = min(regions, key=lambda x: x['avg_cost'])
            most_expensive = max(regions, key=lambda x: x['avg_cost'])

            results.append({
                'model': model,
                'regions_analyzed': len(regions),
                'min_cost': min_cost,
                'max_cost': max_cost,
                'variance_percentage': variance_pct,
                'cheapest_region': cheapest['region'],
                'most_expensive_region': most_expensive['region'],
                'potential_savings': max_cost - min_cost
            })

        results.sort(key=lambda x: x['variance_percentage'], reverse=True)
        return results

    def _analyze_provider_by_region(self) -> List[Dict[str, Any]]:
        """Analyze provider performance by region."""
        groups = group_by(self.calls, 'region', 'provider')

        results = []
        for (region, provider), calls in groups.items():
            metrics = aggregate_metrics(calls)

            results.append({
                'region': region,
                'provider': provider,
                'call_count': metrics['call_count'],
                'avg_latency_ms': metrics['avg_latency_ms'],
                'p95_latency_ms': metrics['p95_latency_ms'],
                'total_cost': metrics['total_cost'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        results.sort(key=lambda x: (x['region'], x['avg_latency_ms']))
        return results

    def _detect_cross_region_issues(self) -> Dict[str, Any]:
        """Detect potential cross-region routing issues."""
        # Look for unusually high latencies that might indicate wrong region routing
        issues = []

        region_groups = group_by(self.calls, 'region')

        for (region,), calls in region_groups.items():
            latencies = [c['latency_ms'] for c in calls]
            avg_latency = sum(latencies) / len(latencies)
            p99_latency = calculate_percentile(latencies, 99)

            # Flag regions with P99 > 3000ms
            if p99_latency > 3000:
                issues.append({
                    'region': region,
                    'issue': 'high_p99_latency',
                    'p99_latency_ms': p99_latency,
                    'avg_latency_ms': avg_latency,
                    'call_count': len(calls)
                })

            # Flag regions with high variance (potential routing issues)
            std_dev = (sum((l - avg_latency) ** 2 for l in latencies) / len(latencies)) ** 0.5
            if std_dev > avg_latency * 0.5:  # Std dev > 50% of mean
                issues.append({
                    'region': region,
                    'issue': 'high_latency_variance',
                    'std_deviation': std_dev,
                    'avg_latency_ms': avg_latency,
                    'call_count': len(calls)
                })

        return {
            'issue_count': len(issues),
            'issues': issues
        }

    def _analyze_regional_profitability(self) -> List[Dict[str, Any]]:
        """Analyze profitability by region."""
        region_groups = group_by(self.calls, 'region')

        results = []
        for (region,), calls in region_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)

            # Estimate revenue from subscription tiers
            total_revenue = 0
            for call in calls:
                # Revenue attribution: distribute monthly subscription cost across calls
                # This is simplified - real calculation would need actual billing periods
                tier_price = call['tier_price_usd']
                total_revenue += tier_price / 1000  # Rough approximation

            gross_margin = total_revenue - total_cost
            margin_pct = safe_divide(gross_margin, total_revenue, 0) * 100

            results.append({
                'region': region,
                'call_count': len(calls),
                'total_cost': total_cost,
                'estimated_revenue': total_revenue,
                'gross_margin': gross_margin,
                'margin_percentage': margin_pct
            })

        results.sort(key=lambda x: x['gross_margin'], reverse=True)
        return results

    def _find_optimal_routing(self) -> List[Dict[str, Any]]:
        """Find optimal provider-region combinations."""
        heatmap = self._generate_latency_heatmap()

        # Group by model to find best region/provider
        model_options = defaultdict(list)
        for entry in heatmap:
            model_options[entry['model']].append(entry)

        recommendations = []
        for model, options in model_options.items():
            if len(options) < 2:
                continue

            # Find fastest option
            fastest = min(options, key=lambda x: x['avg_latency_ms'])

            # Find cheapest option (we'd need cost data, using latency as proxy)
            # In real scenario, calculate cost per call for each region

            recommendations.append({
                'model': model,
                'best_for_latency': {
                    'region': fastest['region'],
                    'provider': fastest['provider'],
                    'avg_latency_ms': fastest['avg_latency_ms']
                },
                'options_count': len(options)
            })

        return recommendations

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        summary = self._generate_summary()
        by_region = self._analyze_by_region()
        cost_variance = self._analyze_regional_cost_variance()
        cross_region = self._detect_cross_region_issues()

        # Regional balance
        if summary['regional_balance_score'] < 80:
            recommendations.append(
                f"Regional distribution is unbalanced ({summary['regional_balance_score']:.1f}% balance score). "
                f"{summary['max_region']} has {format_large_number(summary['max_region_calls'])} calls while "
                f"{summary['min_region']} has only {format_large_number(summary['min_region_calls'])}. "
                f"Implement geographic load balancing to distribute traffic more evenly."
            )

        # Latency issues
        high_latency_regions = [r for r in by_region if r['p95_latency_ms'] > 2000]
        if high_latency_regions:
            regions_list = ', '.join(r['region'] for r in high_latency_regions[:3])
            recommendations.append(
                f"High latency detected in {len(high_latency_regions)} regions: {regions_list}. "
                f"Consider deploying edge caching, CDN acceleration, or regional endpoints "
                f"to improve performance."
            )

        # Cost arbitrage opportunities
        if cost_variance:
            top_variance = cost_variance[0]
            if top_variance['variance_percentage'] > 20:
                savings = top_variance['potential_savings']
                recommendations.append(
                    f"Significant cost variance detected for {top_variance['model']}: "
                    f"{top_variance['variance_percentage']:.1f}% difference between regions. "
                    f"Route traffic to {top_variance['cheapest_region']} instead of "
                    f"{top_variance['most_expensive_region']} to save ${savings:.4f} per call."
                )

        # Cross-region issues
        if cross_region['issue_count'] > 0:
            recommendations.append(
                f"Detected {cross_region['issue_count']} potential routing issues. "
                f"Review DNS configuration, load balancer settings, and customer location data "
                f"to ensure requests are routed to optimal regions."
            )

        # Provider-specific recommendations
        provider_analysis = self._analyze_provider_by_region()
        provider_latencies = defaultdict(list)
        for entry in provider_analysis:
            provider_latencies[entry['provider']].append(entry['avg_latency_ms'])

        for provider, latencies in provider_latencies.items():
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency > 1500:
                recommendations.append(
                    f"Provider '{provider}' shows elevated average latency ({avg_latency:.0f}ms) "
                    f"across regions. Consider evaluating alternative providers or optimizing "
                    f"connection pooling and keep-alive settings."
                )

        if not recommendations:
            recommendations.append(
                "Geographic distribution and latency performance are well-optimized. "
                "Continue monitoring for changes in traffic patterns."
            )

        return recommendations
