"""Token Economics & Efficiency Analyzer."""

import sys
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class TokenEconomicsAnalyzer:
    """Analyzes token usage patterns and cost efficiency."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_model': self._analyze_by_model(),
            'by_feature': self._analyze_by_feature(),
            'by_archetype': self._analyze_by_archetype(),
            'io_ratio_analysis': self._analyze_io_ratio(),
            'efficiency_rankings': self._rank_efficiency(),
            'wasteful_patterns': self._detect_wasteful_patterns(),
            'optimization_opportunities': self._find_optimization_opportunities(),
            'cost_per_token_trends': self._analyze_cost_per_token(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall token economics summary."""
        total_input = sum(c['input_tokens'] for c in self.calls)
        total_output = sum(c['output_tokens'] for c in self.calls)
        total_tokens = sum(c['total_tokens'] for c in self.calls)
        total_cost = sum(c['cost_usd'] for c in self.calls)

        avg_io_ratio = safe_divide(total_input, total_output, 1.0)
        cost_per_1k_tokens = safe_divide(total_cost, total_tokens / 1000, 0)

        return {
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_tokens,
            'avg_io_ratio': avg_io_ratio,
            'total_cost': total_cost,
            'cost_per_1k_tokens': cost_per_1k_tokens,
            'avg_input_per_call': total_input / len(self.calls),
            'avg_output_per_call': total_output / len(self.calls)
        }

    def _analyze_by_model(self) -> List[Dict[str, Any]]:
        """Analyze token economics by model."""
        model_groups = group_by(self.calls, 'provider', 'model')

        results = []
        for (provider, model), calls in model_groups.items():
            metrics = aggregate_metrics(calls)

            total_input = sum(c['input_tokens'] for c in calls)
            total_output = sum(c['output_tokens'] for c in calls)
            io_ratio = safe_divide(total_input, total_output, 1.0)

            cost_per_1k = safe_divide(metrics['total_cost'], metrics['total_tokens'] / 1000, 0)

            results.append({
                'provider': provider,
                'model': model,
                'call_count': metrics['call_count'],
                'total_tokens': metrics['total_tokens'],
                'total_input_tokens': total_input,
                'total_output_tokens': total_output,
                'io_ratio': io_ratio,
                'avg_tokens_per_call': metrics['avg_tokens_per_call'],
                'total_cost': metrics['total_cost'],
                'cost_per_1k_tokens': cost_per_1k,
                'efficiency_score': self._calculate_efficiency_score(cost_per_1k, io_ratio)
            })

        # Sort by total tokens descending
        results.sort(key=lambda x: x['total_tokens'], reverse=True)
        return results

    def _analyze_by_feature(self) -> List[Dict[str, Any]]:
        """Analyze token usage by feature."""
        feature_groups = group_by(self.calls, 'feature_id')

        results = []
        for (feature,), calls in feature_groups.items():
            metrics = aggregate_metrics(calls)

            total_input = sum(c['input_tokens'] for c in calls)
            total_output = sum(c['output_tokens'] for c in calls)
            io_ratio = safe_divide(total_input, total_output, 1.0)

            cost_per_1k = safe_divide(metrics['total_cost'], metrics['total_tokens'] / 1000, 0)

            results.append({
                'feature': feature,
                'call_count': metrics['call_count'],
                'total_tokens': metrics['total_tokens'],
                'avg_input_tokens': total_input / len(calls),
                'avg_output_tokens': total_output / len(calls),
                'io_ratio': io_ratio,
                'total_cost': metrics['total_cost'],
                'cost_per_1k_tokens': cost_per_1k,
                'cost_per_call': metrics['avg_cost_per_call']
            })

        results.sort(key=lambda x: x['total_cost'], reverse=True)
        return results

    def _analyze_by_archetype(self) -> List[Dict[str, Any]]:
        """Analyze token efficiency by customer archetype."""
        archetype_groups = group_by(self.calls, 'customer_archetype')

        results = []
        for (archetype,), calls in archetype_groups.items():
            metrics = aggregate_metrics(calls)

            total_input = sum(c['input_tokens'] for c in calls)
            total_output = sum(c['output_tokens'] for c in calls)
            io_ratio = safe_divide(total_input, total_output, 1.0)

            cost_per_1k = safe_divide(metrics['total_cost'], metrics['total_tokens'] / 1000, 0)

            results.append({
                'archetype': archetype,
                'call_count': metrics['call_count'],
                'avg_tokens_per_call': metrics['avg_tokens_per_call'],
                'avg_input_per_call': total_input / len(calls),
                'avg_output_per_call': total_output / len(calls),
                'io_ratio': io_ratio,
                'total_cost': metrics['total_cost'],
                'cost_per_1k_tokens': cost_per_1k,
                'efficiency_score': self._calculate_efficiency_score(cost_per_1k, io_ratio)
            })

        results.sort(key=lambda x: x['total_cost'], reverse=True)
        return results

    def _analyze_io_ratio(self) -> Dict[str, Any]:
        """Analyze input/output token ratios across dimensions."""
        # Calculate distribution of I/O ratios
        ratios = []
        for call in self.calls:
            ratio = safe_divide(call['input_tokens'], call['output_tokens'], 1.0)
            ratios.append(ratio)

        ratios_sorted = sorted(ratios)

        return {
            'min_ratio': min(ratios),
            'max_ratio': max(ratios),
            'median_ratio': ratios_sorted[len(ratios_sorted) // 2],
            'p25_ratio': ratios_sorted[len(ratios_sorted) // 4],
            'p75_ratio': ratios_sorted[3 * len(ratios_sorted) // 4],
            'avg_ratio': sum(ratios) / len(ratios),
            'balanced_calls': sum(1 for r in ratios if 0.5 <= r <= 2.0),
            'input_heavy_calls': sum(1 for r in ratios if r > 2.0),
            'output_heavy_calls': sum(1 for r in ratios if r < 0.5)
        }

    def _rank_efficiency(self) -> Dict[str, Any]:
        """Rank models and features by efficiency."""
        # Model efficiency
        models = self._analyze_by_model()
        top_efficient_models = sorted(models, key=lambda x: x['efficiency_score'], reverse=True)[:10]
        least_efficient_models = sorted(models, key=lambda x: x['efficiency_score'])[:10]

        # Feature efficiency
        features = self._analyze_by_feature()
        feature_efficiency = sorted(features, key=lambda x: x['cost_per_1k_tokens'])

        return {
            'most_efficient_models': top_efficient_models,
            'least_efficient_models': least_efficient_models,
            'most_efficient_feature': feature_efficiency[0] if feature_efficiency else None,
            'least_efficient_feature': feature_efficiency[-1] if feature_efficiency else None
        }

    def _detect_wasteful_patterns(self) -> Dict[str, Any]:
        """Detect wasteful token usage patterns."""
        wasteful_calls = []

        for call in self.calls:
            issues = []

            # High input, low output (potential prompt engineering issue)
            io_ratio = safe_divide(call['input_tokens'], call['output_tokens'], 1.0)
            if io_ratio > 5.0 and call['input_tokens'] > 500:
                issues.append('excessive_input_tokens')

            # Very high cost per call for simple features
            if call['cost_usd'] > 0.05 and call['feature_id'] in ['chat', 'translate']:
                issues.append('expensive_simple_task')

            # High tokens but low output (wasted processing)
            if call['total_tokens'] > 2000 and call['output_tokens'] < 100:
                issues.append('low_output_high_cost')

            if issues:
                wasteful_calls.append({
                    'call_id': call.get('call_id', 'unknown'),
                    'customer_id': call['customer_id'],
                    'feature': call['feature_id'],
                    'model': call['model'],
                    'input_tokens': call['input_tokens'],
                    'output_tokens': call['output_tokens'],
                    'cost_usd': call['cost_usd'],
                    'issues': issues
                })

        # Group by issue type
        issue_counts = defaultdict(int)
        for wc in wasteful_calls:
            for issue in wc['issues']:
                issue_counts[issue] += 1

        # Calculate total waste
        total_wasted_cost = sum(wc['cost_usd'] for wc in wasteful_calls)

        return {
            'wasteful_call_count': len(wasteful_calls),
            'total_wasted_cost': total_wasted_cost,
            'issue_breakdown': dict(issue_counts),
            'top_wasteful_calls': sorted(wasteful_calls, key=lambda x: x['cost_usd'], reverse=True)[:20]
        }

    def _find_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Find specific optimization opportunities."""
        opportunities = []

        # Find customers using expensive models for simple tasks
        customer_feature_model = group_by(self.calls, 'customer_id', 'feature_id', 'model')

        for (customer, feature, model), calls in customer_feature_model.items():
            if feature in ['chat', 'translate'] and 'opus' in model.lower():
                metrics = aggregate_metrics(calls)
                avg_tokens = metrics['avg_tokens_per_call']

                # If average tokens is low, suggest cheaper model
                if avg_tokens < 500:
                    potential_savings = metrics['total_cost'] * 0.7  # Assume 70% savings

                    opportunities.append({
                        'customer_id': customer,
                        'feature': feature,
                        'current_model': model,
                        'call_count': metrics['call_count'],
                        'avg_tokens': avg_tokens,
                        'current_cost': metrics['total_cost'],
                        'suggested_model': model.replace('opus', 'sonnet'),
                        'potential_savings': potential_savings,
                        'reason': 'Low token usage on premium model'
                    })

        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
        return opportunities[:50]  # Top 50 opportunities

    def _analyze_cost_per_token(self) -> List[Dict[str, Any]]:
        """Analyze cost per token by provider and model."""
        model_groups = group_by(self.calls, 'provider', 'model')

        results = []
        for (provider, model), calls in model_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)
            total_tokens = sum(c['total_tokens'] for c in calls)

            cost_per_1k = safe_divide(total_cost, total_tokens / 1000, 0)

            results.append({
                'provider': provider,
                'model': model,
                'cost_per_1k_tokens': cost_per_1k,
                'total_cost': total_cost,
                'total_tokens': total_tokens
            })

        results.sort(key=lambda x: x['cost_per_1k_tokens'])
        return results

    def _calculate_efficiency_score(self, cost_per_1k: float, io_ratio: float) -> float:
        """Calculate efficiency score (0-100) based on cost and I/O ratio."""
        # Lower cost per 1k tokens is better
        # I/O ratio close to 1.0 is ideal
        cost_score = max(0, 100 - (cost_per_1k * 1000))  # Normalize

        # Penalize extreme I/O ratios
        io_penalty = abs(io_ratio - 1.0) * 10
        io_score = max(0, 100 - io_penalty)

        return (cost_score * 0.7 + io_score * 0.3)  # Weighted average

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        summary = self._generate_summary()
        wasteful = self._detect_wasteful_patterns()
        opportunities = self._find_optimization_opportunities()

        # I/O ratio recommendations
        if summary['avg_io_ratio'] > 2.0:
            recommendations.append(
                f"Average I/O ratio is {summary['avg_io_ratio']:.2f} (input-heavy). "
                f"Review prompt engineering to reduce input tokens. Consider implementing "
                f"prompt templates and caching strategies to reduce repetitive input."
            )

        # Wasteful patterns
        if wasteful['wasteful_call_count'] > 0:
            waste_pct = (wasteful['wasteful_call_count'] / len(self.calls)) * 100
            recommendations.append(
                f"Detected {wasteful['wasteful_call_count']:,} wasteful calls ({waste_pct:.1f}% of total) "
                f"costing ${wasteful['total_wasted_cost']:,.2f}. Top issues: "
                f"{', '.join(f'{k} ({v:,} calls)' for k, v in list(wasteful['issue_breakdown'].items())[:3])}. "
                f"Implement token usage guardrails and model selection logic."
            )

        # Optimization opportunities
        if opportunities:
            total_savings = sum(opp['potential_savings'] for opp in opportunities[:10])
            recommendations.append(
                f"Identified {len(opportunities)} optimization opportunities. "
                f"Top 10 could save ${total_savings:,.2f}/period by switching customers "
                f"from premium to mid-tier models for simple tasks."
            )

        # Cost per token analysis
        cost_analysis = self._analyze_cost_per_token()
        if len(cost_analysis) > 1:
            cheapest = cost_analysis[0]
            most_expensive = cost_analysis[-1]
            cost_diff = most_expensive['cost_per_1k_tokens'] / cheapest['cost_per_1k_tokens']

            recommendations.append(
                f"Cost per 1K tokens varies {cost_diff:.1f}x across models "
                f"(${cheapest['cost_per_1k_tokens']:.4f} for {cheapest['model']} vs "
                f"${most_expensive['cost_per_1k_tokens']:.4f} for {most_expensive['model']}). "
                f"Implement intelligent model routing based on task complexity."
            )

        # Feature-specific recommendations
        features = self._analyze_by_feature()
        for feature in features:
            if feature['cost_per_1k_tokens'] > 0.015 and feature['feature'] in ['chat', 'translate']:
                recommendations.append(
                    f"Feature '{feature['feature']}' has high cost per 1K tokens "
                    f"(${feature['cost_per_1k_tokens']:.4f}). Review model selection "
                    f"and consider using faster, cheaper models for this use case."
                )

        if not recommendations:
            recommendations.append(
                "Token usage appears optimized. Continue monitoring for changes in usage patterns."
            )

        return recommendations
