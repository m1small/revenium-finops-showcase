"""Pricing Strategy Analyzer - UBR Domain 2."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class PricingStrategyAnalyzer:
    """Analyzes pricing model alternatives and revenue optimization."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'current_model': self._analyze_current_model(),
            'alternative_models': self._simulate_pricing_models(),
            'customer_segmentation': self._segment_customers(),
            'comparison': self._compare_models(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall pricing summary."""
        customer_groups = group_by(self.calls, 'customer_id')

        total_revenue = 0
        total_cost = 0

        for (customer_id,), calls in customer_groups.items():
            tier_price = calls[0]['tier_price_usd']
            total_revenue += tier_price
            total_cost += sum(c['cost_usd'] for c in calls)

        return {
            'current_model': 'Flat Pricing',
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'gross_margin': total_revenue - total_cost,
            'margin_percentage': safe_divide((total_revenue - total_cost) * 100, total_revenue),
            'customer_count': len(customer_groups)
        }

    def _analyze_current_model(self) -> Dict[str, Any]:
        """Analyze current flat pricing model."""
        customer_groups = group_by(self.calls, 'customer_id')

        # Categorize customers by usage
        light_users = []
        medium_users = []
        heavy_users = []

        for (customer_id,), calls in customer_groups.items():
            tier_price = calls[0]['tier_price_usd']
            customer_cost = sum(c['cost_usd'] for c in calls)

            # Usage category based on cost/revenue ratio
            usage_ratio = safe_divide(customer_cost, tier_price)

            customer_data = {
                'customer_id': customer_id,
                'tier': calls[0]['subscription_tier'],
                'revenue': tier_price,
                'cost': customer_cost,
                'usage_ratio': usage_ratio
            }

            if usage_ratio < 0.3:
                light_users.append(customer_data)
            elif usage_ratio < 0.7:
                medium_users.append(customer_data)
            else:
                heavy_users.append(customer_data)

        return {
            'model_name': 'Flat Pricing',
            'description': 'Fixed monthly fee with unlimited usage',
            'light_users': len(light_users),
            'medium_users': len(medium_users),
            'heavy_users': len(heavy_users),
            'pros': ['Simple for customers', 'Predictable revenue', 'Low billing complexity'],
            'cons': ['High variance in profitability', 'Heavy users subsidized by light users', 'Revenue not aligned with value']
        }

    def _simulate_pricing_models(self) -> Dict[str, Any]:
        """Simulate alternative pricing models."""
        customer_groups = group_by(self.calls, 'customer_id')

        models = {}

        # Model 1: Current Flat Pricing (baseline)
        flat_revenue = sum(calls[0]['tier_price_usd'] for calls in customer_groups.values())
        flat_cost = sum(sum(c['cost_usd'] for c in calls) for calls in customer_groups.values())

        models['flat'] = {
            'name': 'Flat Pricing (Current)',
            'revenue': flat_revenue,
            'cost': flat_cost,
            'margin': flat_revenue - flat_cost,
            'margin_pct': safe_divide((flat_revenue - flat_cost) * 100, flat_revenue)
        }

        # Model 2: Tiered with Overages
        # Base tier price + $0.01 per 1000 tokens over allocation
        tiered_revenue = 0
        for (customer_id,), calls in customer_groups.items():
            base_price = calls[0]['tier_price_usd']
            total_tokens = sum(c['total_tokens'] for c in calls)

            # Assume 100K tokens included per $10 of base price
            included_tokens = (base_price / 10) * 100000
            overage_tokens = max(0, total_tokens - included_tokens)
            overage_charge = (overage_tokens / 1000) * 0.01

            tiered_revenue += base_price + overage_charge

        models['tiered'] = {
            'name': 'Tiered with Overages',
            'revenue': tiered_revenue,
            'cost': flat_cost,
            'margin': tiered_revenue - flat_cost,
            'margin_pct': safe_divide((tiered_revenue - flat_cost) * 100, tiered_revenue),
            'vs_flat': tiered_revenue - flat_revenue
        }

        # Model 3: Pure Usage-Based
        # No base fee, $0.015 per 1000 tokens
        usage_revenue = 0
        total_tokens = sum(sum(c['total_tokens'] for c in calls) for calls in customer_groups.values())
        usage_revenue = (total_tokens / 1000) * 0.015

        models['usage'] = {
            'name': 'Pure Usage-Based',
            'revenue': usage_revenue,
            'cost': flat_cost,
            'margin': usage_revenue - flat_cost,
            'margin_pct': safe_divide((usage_revenue - flat_cost) * 100, usage_revenue),
            'vs_flat': usage_revenue - flat_revenue
        }

        # Model 4: Hybrid (Base + Cost-Plus Margin)
        # 50% of tier price as base + actual cost * 1.5x
        hybrid_revenue = 0
        for (customer_id,), calls in customer_groups.items():
            base_price = calls[0]['tier_price_usd']
            customer_cost = sum(c['cost_usd'] for c in calls)

            hybrid_price = (base_price * 0.5) + (customer_cost * 1.5)
            hybrid_revenue += hybrid_price

        models['hybrid'] = {
            'name': 'Hybrid (Base + Cost-Plus)',
            'revenue': hybrid_revenue,
            'cost': flat_cost,
            'margin': hybrid_revenue - flat_cost,
            'margin_pct': safe_divide((hybrid_revenue - flat_cost) * 100, hybrid_revenue),
            'vs_flat': hybrid_revenue - flat_revenue
        }

        return models

    def _segment_customers(self) -> Dict[str, Any]:
        """Segment customers by usage patterns."""
        customer_groups = group_by(self.calls, 'customer_id')

        segments = {
            'light': {'count': 0, 'revenue': 0, 'cost': 0},
            'medium': {'count': 0, 'revenue': 0, 'cost': 0},
            'heavy': {'count': 0, 'revenue': 0, 'cost': 0}
        }

        for (customer_id,), calls in customer_groups.items():
            tier_price = calls[0]['tier_price_usd']
            customer_cost = sum(c['cost_usd'] for c in calls)
            usage_ratio = safe_divide(customer_cost, tier_price)

            if usage_ratio < 0.3:
                segment = 'light'
            elif usage_ratio < 0.7:
                segment = 'medium'
            else:
                segment = 'heavy'

            segments[segment]['count'] += 1
            segments[segment]['revenue'] += tier_price
            segments[segment]['cost'] += customer_cost

        # Calculate margins
        for segment in segments.values():
            segment['margin'] = segment['revenue'] - segment['cost']
            segment['margin_pct'] = safe_divide((segment['revenue'] - segment['cost']) * 100, segment['revenue'])

        return segments

    def _compare_models(self) -> List[Dict[str, Any]]:
        """Compare all pricing models side-by-side."""
        models = self._simulate_pricing_models()

        comparison = []
        for model_key, model_data in models.items():
            comparison.append({
                'model': model_data['name'],
                'revenue': model_data['revenue'],
                'cost': model_data['cost'],
                'margin': model_data['margin'],
                'margin_pct': model_data['margin_pct'],
                'vs_current': model_data.get('vs_flat', 0)
            })

        # Sort by margin percentage
        return sorted(comparison, key=lambda x: x['margin_pct'], reverse=True)

    def _generate_recommendations(self) -> List[str]:
        """Generate pricing strategy recommendations."""
        recommendations = []

        # Compare models
        models = self._simulate_pricing_models()
        comparison = self._compare_models()

        # Best model
        best_model = comparison[0]
        current_model = models['flat']

        if best_model['margin_pct'] > current_model['margin_pct']:
            improvement = best_model['margin_pct'] - current_model['margin_pct']
            revenue_increase = best_model['vs_current']

            recommendations.append(
                f"Switch to {best_model['model']} for {improvement:.1f}pp margin improvement "
                f"({format_currency(revenue_increase)} additional revenue)"
            )

        # Segment-specific recommendations
        segments = self._segment_customers()

        if segments['heavy']['margin_pct'] < 20:
            recommendations.append(
                f"Heavy users ({segments['heavy']['count']} customers) have {segments['heavy']['margin_pct']:.1f}% margin. "
                f"Implement usage-based pricing or caps."
            )

        if segments['light']['margin_pct'] > 70:
            recommendations.append(
                f"Light users ({segments['light']['count']} customers) are highly profitable ({segments['light']['margin_pct']:.1f}% margin). "
                f"Focus acquisition on similar usage profiles."
            )

        # Hybrid model recommendation
        hybrid = models['hybrid']
        if hybrid['margin_pct'] > current_model['margin_pct'] * 1.1:
            recommendations.append(
                f"Hybrid pricing model increases margin to {hybrid['margin_pct']:.1f}% "
                f"while maintaining base revenue predictability."
            )

        # Migration strategy
        recommendations.append(
            "Recommended migration: Grandfather existing customers, apply new pricing to new customers, "
            "offer opt-in migration with 3-month lock-in incentive."
        )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = PricingStrategyAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Pricing Strategy Analysis")
    print("=" * 60)
    print(f"Current Model:         {summary['current_model']}")
    print(f"Total Revenue:         {format_currency(summary['total_revenue'])}")
    print(f"Total Cost:            {format_currency(summary['total_cost'])}")
    print(f"Margin:                {summary['margin_percentage']:.1f}%")
    print()

    # Print model comparison
    print("Model Comparison")
    print("-" * 60)
    for model in results['comparison']:
        print(f"{model['model']:30} Margin: {model['margin_pct']:5.1f}%  "
              f"Revenue: {format_currency(model['revenue'])}")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/pricing_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
