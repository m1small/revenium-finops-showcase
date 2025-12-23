"""Rate Optimization Analyzer - FinOps Domain 4."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class OptimizationAnalyzer:
    """Analyzes reserved capacity, model switching, and rate optimization opportunities."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'reserved_capacity': self._analyze_reserved_capacity(),
            'model_switching': self._analyze_model_switching(),
            'volume_discounts': self._analyze_volume_discounts(),
            'provider_arbitrage': self._analyze_provider_arbitrage(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall optimization summary."""
        total_cost = sum(c['cost_usd'] for c in self.calls)

        # Calculate potential savings from all optimization strategies
        reserved_savings = self._analyze_reserved_capacity()['total_savings']
        switching_savings = self._analyze_model_switching()['total_potential_savings']

        total_optimization_potential = reserved_savings + switching_savings

        return {
            'total_cost': total_cost,
            'reserved_capacity_savings': reserved_savings,
            'model_switching_savings': switching_savings,
            'total_optimization_potential': total_optimization_potential,
            'optimization_percentage': (total_optimization_potential / total_cost * 100) if total_cost > 0 else 0
        }

    def _analyze_reserved_capacity(self) -> Dict[str, Any]:
        """Analyze potential savings from reserved capacity commitments."""
        # Typical reserved instance discounts: 20-40% for 1-year, 30-50% for 3-year
        # Assume 30% savings for monthly commitments

        model_groups = group_by(self.calls, 'provider', 'model')

        candidates = []
        for (provider, model), calls in model_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)
            call_count = len(calls)

            # Consider models with >$100 monthly spend
            if total_cost > 100:
                # Calculate savings with 30% discount
                savings = total_cost * 0.30

                # Calculate breakeven: cost of commitment vs on-demand
                monthly_commitment = total_cost * 0.70  # 30% discount

                candidates.append({
                    'provider': provider,
                    'model': model,
                    'current_cost': total_cost,
                    'committed_cost': monthly_commitment,
                    'savings': savings,
                    'savings_percentage': 30.0,
                    'call_count': call_count,
                    'recommendation': 'High usage - excellent candidate for reserved capacity'
                })

        # Sort by savings potential
        candidates.sort(key=lambda x: x['savings'], reverse=True)

        total_savings = sum(c['savings'] for c in candidates)

        return {
            'candidates': candidates[:10],  # Top 10
            'total_candidates': len(candidates),
            'total_savings': total_savings
        }

    def _analyze_model_switching(self) -> Dict[str, Any]:
        """Identify opportunities to switch to cheaper models."""
        # Define model switching opportunities (expensive -> cheaper alternative)
        switching_map = {
            'gpt-4': {'alternative': 'claude-sonnet-4', 'savings_pct': 60},
            'gpt-4-32k': {'alternative': 'claude-sonnet-4', 'savings_pct': 75},
            'claude-opus-4': {'alternative': 'claude-sonnet-4', 'savings_pct': 50},
            'gemini-pro-1.5': {'alternative': 'gemini-flash-1.5', 'savings_pct': 80},
        }

        opportunities = []
        for call in self.calls:
            model = call['model']
            if model in switching_map:
                alternative = switching_map[model]
                potential_savings = call['cost_usd'] * (alternative['savings_pct'] / 100.0)

                opportunities.append({
                    'call_id': call['call_id'],
                    'customer_id': call['customer_id'],
                    'current_model': model,
                    'alternative_model': alternative['alternative'],
                    'current_cost': call['cost_usd'],
                    'potential_savings': potential_savings,
                    'savings_percentage': alternative['savings_pct']
                })

        # Aggregate by model switch
        switch_summary = defaultdict(lambda: {
            'count': 0,
            'total_cost': 0.0,
            'total_savings': 0.0,
            'alternative': '',
            'savings_pct': 0
        })

        for opp in opportunities:
            key = f"{opp['current_model']} -> {opp['alternative_model']}"
            switch_summary[key]['count'] += 1
            switch_summary[key]['total_cost'] += opp['current_cost']
            switch_summary[key]['total_savings'] += opp['potential_savings']
            switch_summary[key]['alternative'] = opp['alternative_model']
            switch_summary[key]['savings_pct'] = opp['savings_percentage']

        # Convert to list
        summary_list = []
        for switch, data in switch_summary.items():
            from_model, to_model = switch.split(' -> ')
            summary_list.append({
                'from_model': from_model,
                'to_model': to_model,
                'call_count': data['count'],
                'current_cost': data['total_cost'],
                'potential_savings': data['total_savings'],
                'savings_percentage': data['savings_pct']
            })

        summary_list.sort(key=lambda x: x['potential_savings'], reverse=True)

        return {
            'opportunities': summary_list,
            'total_opportunities': len(opportunities),
            'total_potential_savings': sum(o['potential_savings'] for o in opportunities)
        }

    def _analyze_volume_discounts(self) -> Dict[str, Any]:
        """Analyze potential volume discount opportunities."""
        # Calculate total usage by provider
        provider_groups = group_by(self.calls, 'provider')

        volume_analysis = []
        for (provider,), calls in provider_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)
            total_tokens = sum(c['total_tokens'] for c in calls)

            # Assume volume discounts at certain thresholds
            # $1000/mo = 5%, $5000/mo = 10%, $10000/mo = 15%
            if total_cost >= 10000:
                discount_pct = 15
            elif total_cost >= 5000:
                discount_pct = 10
            elif total_cost >= 1000:
                discount_pct = 5
            else:
                discount_pct = 0

            potential_savings = total_cost * (discount_pct / 100.0)

            volume_analysis.append({
                'provider': provider,
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'current_discount': discount_pct,
                'potential_savings': potential_savings,
                'next_threshold': self._get_next_threshold(total_cost)
            })

        volume_analysis.sort(key=lambda x: x['total_cost'], reverse=True)

        return {
            'by_provider': volume_analysis,
            'total_potential_savings': sum(v['potential_savings'] for v in volume_analysis)
        }

    def _get_next_threshold(self, current_cost: float) -> Dict[str, Any]:
        """Get next volume discount threshold."""
        if current_cost < 1000:
            return {'amount': 1000, 'discount': '5%'}
        elif current_cost < 5000:
            return {'amount': 5000, 'discount': '10%'}
        elif current_cost < 10000:
            return {'amount': 10000, 'discount': '15%'}
        else:
            return {'amount': None, 'discount': 'Maximum tier reached'}

    def _analyze_provider_arbitrage(self) -> Dict[str, Any]:
        """Identify provider pricing differences for similar capabilities."""
        # Compare similar models across providers
        # This is a simplified version - in reality would need semantic matching

        comparisons = [
            {
                'capability': 'High-end reasoning',
                'models': ['gpt-4', 'claude-opus-4', 'gemini-pro-1.5'],
                'recommendation': 'claude-opus-4 offers best price/performance for complex tasks'
            },
            {
                'capability': 'Fast, balanced performance',
                'models': ['gpt-3.5-turbo', 'claude-sonnet-4', 'gemini-flash-1.5'],
                'recommendation': 'gemini-flash-1.5 offers 80% cost savings vs competitors'
            },
            {
                'capability': 'Long context processing',
                'models': ['gpt-4-32k', 'claude-opus-4', 'gemini-pro-1.5'],
                'recommendation': 'claude-opus-4 provides best value for 100K+ token contexts'
            }
        ]

        # Calculate actual cost differences
        model_groups = group_by(self.calls, 'model')
        for comparison in comparisons:
            costs = {}
            for model in comparison['models']:
                if (model,) in model_groups:
                    calls = model_groups[(model,)]
                    metrics = aggregate_metrics(calls)
                    costs[model] = safe_divide(metrics['total_cost'] * 1000, metrics['total_tokens'])

            comparison['costs'] = costs

        return {
            'comparisons': comparisons,
            'summary': 'Significant savings available by choosing optimal provider per use case'
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate rate optimization recommendations."""
        recommendations = []

        # Reserved capacity
        reserved = self._analyze_reserved_capacity()
        if reserved['total_savings'] > 100:
            top_candidate = reserved['candidates'][0] if reserved['candidates'] else None
            if top_candidate:
                recommendations.append(
                    f"Purchase reserved capacity for {top_candidate['model']} to save "
                    f"{format_currency(reserved['total_savings'])}/month "
                    f"({reserved['total_candidates']} total opportunities)"
                )

        # Model switching
        switching = self._analyze_model_switching()
        if switching['total_potential_savings'] > 50:
            if switching['opportunities']:
                top_switch = switching['opportunities'][0]
                recommendations.append(
                    f"Switch from {top_switch['from_model']} to {top_switch['to_model']} "
                    f"for {top_switch['savings_percentage']}% savings "
                    f"({format_currency(switching['total_potential_savings'])} total potential)"
                )

        # Volume discounts
        volume = self._analyze_volume_discounts()
        if volume['total_potential_savings'] > 0:
            recommendations.append(
                f"Negotiate volume discounts to save {format_currency(volume['total_potential_savings'])}/month"
            )

        # Total optimization
        summary = self._generate_summary()
        if summary['total_optimization_potential'] > 0:
            recommendations.append(
                f"Total optimization potential: {format_currency(summary['total_optimization_potential'])} "
                f"({summary['optimization_percentage']:.1f}% of current spend)"
            )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = OptimizationAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Rate Optimization Analysis")
    print("=" * 60)
    print(f"Total Cost:                    {format_currency(summary['total_cost'])}")
    print(f"Reserved Capacity Savings:     {format_currency(summary['reserved_capacity_savings'])}")
    print(f"Model Switching Savings:       {format_currency(summary['model_switching_savings'])}")
    print(f"Total Optimization Potential:  {format_currency(summary['total_optimization_potential'])}")
    print(f"                               ({summary['optimization_percentage']:.1f}% of spend)")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/optimization_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
