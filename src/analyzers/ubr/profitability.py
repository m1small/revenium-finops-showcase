"""Customer Profitability Analyzer - UBR Domain 1."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class CustomerProfitabilityAnalyzer:
    """Analyzes customer-level profitability and margins."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_customer': self._analyze_by_customer(),
            'by_tier': self._analyze_by_tier(),
            'unprofitable_customers': self._identify_unprofitable_customers(),
            'margin_distribution': self._analyze_margin_distribution(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall profitability summary."""
        # Group by customer to calculate totals
        customer_groups = group_by(self.calls, 'customer_id')

        total_revenue = 0
        total_cost = 0
        customer_count = len(customer_groups)

        for (customer_id,), calls in customer_groups.items():
            # Revenue is subscription tier price
            tier_price = calls[0]['tier_price_usd']
            total_revenue += tier_price

            # Cost is sum of all AI usage
            customer_cost = sum(c['cost_usd'] for c in calls)
            total_cost += customer_cost

        total_margin = total_revenue - total_cost
        margin_percentage = (total_margin / total_revenue * 100) if total_revenue > 0 else 0

        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'gross_margin': total_margin,
            'margin_percentage': margin_percentage,
            'customer_count': customer_count,
            'avg_revenue_per_customer': safe_divide(total_revenue, customer_count),
            'avg_cost_per_customer': safe_divide(total_cost, customer_count)
        }

    def _analyze_by_customer(self) -> List[Dict[str, Any]]:
        """Analyze profitability by customer."""
        customer_groups = group_by(self.calls, 'customer_id')

        results = []
        for (customer_id,), calls in customer_groups.items():
            tier = calls[0]['subscription_tier']
            tier_price = calls[0]['tier_price_usd']

            customer_cost = sum(c['cost_usd'] for c in calls)
            margin = tier_price - customer_cost
            margin_pct = (margin / tier_price * 100) if tier_price > 0 else 0

            # Profitability status
            if margin_pct > 50:
                status = 'high_margin'
            elif margin_pct > 20:
                status = 'medium_margin'
            elif margin_pct > 0:
                status = 'low_margin'
            else:
                status = 'unprofitable'

            results.append({
                'customer_id': customer_id,
                'tier': tier,
                'revenue': tier_price,
                'cost': customer_cost,
                'margin': margin,
                'margin_percentage': margin_pct,
                'call_count': len(calls),
                'status': status
            })

        return sorted(results, key=lambda x: x['margin'], reverse=True)

    def _analyze_by_tier(self) -> List[Dict[str, Any]]:
        """Analyze profitability by subscription tier."""
        tier_groups = group_by(self.calls, 'subscription_tier')

        results = []
        for (tier,), calls in tier_groups.items():
            tier_price = calls[0]['tier_price_usd']

            # Count unique customers in this tier
            unique_customers = len(set(c['customer_id'] for c in calls))

            total_revenue = tier_price * unique_customers
            total_cost = sum(c['cost_usd'] for c in calls)
            total_margin = total_revenue - total_cost
            margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0

            results.append({
                'tier': tier,
                'tier_price': tier_price,
                'customer_count': unique_customers,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'margin': total_margin,
                'margin_percentage': margin_pct,
                'avg_cost_per_customer': safe_divide(total_cost, unique_customers)
            })

        return sorted(results, key=lambda x: x['total_revenue'], reverse=True)

    def _identify_unprofitable_customers(self) -> Dict[str, Any]:
        """Identify customers with negative margins."""
        customer_analysis = self._analyze_by_customer()

        unprofitable = [c for c in customer_analysis if c['margin'] < 0]

        # Calculate total loss
        total_loss = sum(abs(c['margin']) for c in unprofitable)

        # Sort by worst performers
        unprofitable.sort(key=lambda x: x['margin'])

        return {
            'customers': unprofitable[:20],  # Top 20 worst
            'total_count': len(unprofitable),
            'total_loss': total_loss,
            'percentage_of_base': (len(unprofitable) / len(customer_analysis) * 100) if customer_analysis else 0
        }

    def _analyze_margin_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of customer margins."""
        customer_analysis = self._analyze_by_customer()

        distribution = {
            'high_margin': [],      # >50%
            'medium_margin': [],    # 20-50%
            'low_margin': [],       # 0-20%
            'unprofitable': []      # <0%
        }

        for customer in customer_analysis:
            margin_pct = customer['margin_percentage']

            if margin_pct > 50:
                distribution['high_margin'].append(customer)
            elif margin_pct > 20:
                distribution['medium_margin'].append(customer)
            elif margin_pct >= 0:
                distribution['low_margin'].append(customer)
            else:
                distribution['unprofitable'].append(customer)

        return {
            'distribution': {k: len(v) for k, v in distribution.items()},
            'total_customers': len(customer_analysis),
            'high_margin_customers': distribution['high_margin'][:10],
            'unprofitable_customers': distribution['unprofitable'][:10]
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate profitability optimization recommendations."""
        recommendations = []

        # Unprofitable customers
        unprofitable = self._identify_unprofitable_customers()
        if unprofitable['total_count'] > 0:
            recommendations.append(
                f"{unprofitable['total_count']} customers ({unprofitable['percentage_of_base']:.1f}%) "
                f"are unprofitable, losing {format_currency(unprofitable['total_loss'])}. "
                f"Implement usage caps or upgrade prompts."
            )

        # Tier analysis
        tier_analysis = self._analyze_by_tier()
        for tier in tier_analysis:
            if tier['margin_percentage'] < 20:
                recommendations.append(
                    f"{tier['tier']} tier shows low margin ({tier['margin_percentage']:.1f}%). "
                    f"Consider price increase or usage limits."
                )

        # Margin distribution
        distribution = self._analyze_margin_distribution()
        low_margin_count = distribution['distribution']['low_margin']
        total_count = distribution['total_customers']

        if low_margin_count > total_count * 0.3:
            recommendations.append(
                f"{low_margin_count} customers ({low_margin_count/total_count*100:.1f}%) "
                f"have margins below 20%. Review pricing strategy."
            )

        # High performers
        high_margin_count = distribution['distribution']['high_margin']
        if high_margin_count > 0:
            recommendations.append(
                f"{high_margin_count} customers have >50% margins. "
                f"These are ideal customer profiles - focus acquisition on similar segments."
            )

        # Summary recommendation
        summary = self._generate_summary()
        recommendations.append(
            f"Overall margin: {summary['margin_percentage']:.1f}%. "
            f"Target: >40% for healthy SaaS business."
        )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = CustomerProfitabilityAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Customer Profitability Analysis")
    print("=" * 60)
    print(f"Total Revenue:         {format_currency(summary['total_revenue'])}")
    print(f"Total Cost:            {format_currency(summary['total_cost'])}")
    print(f"Gross Margin:          {format_currency(summary['gross_margin'])}")
    print(f"Margin %:              {summary['margin_percentage']:.1f}%")
    print(f"Customers:             {summary['customer_count']}")
    print()

    # Print unprofitable customers
    unprofitable = results['unprofitable_customers']
    print("Unprofitable Customers")
    print("-" * 60)
    print(f"Count:                 {unprofitable['total_count']}")
    print(f"Total Loss:            {format_currency(unprofitable['total_loss'])}")
    print(f"% of Base:             {unprofitable['percentage_of_base']:.1f}%")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/profitability_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
