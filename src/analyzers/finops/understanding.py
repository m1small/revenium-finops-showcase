"""Understanding Usage & Cost Analyzer - FinOps Domain 1."""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class UnderstandingAnalyzer:
    """Analyzes cost allocation, forecasting, and efficiency."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_provider': self._analyze_by_provider(),
            'by_model': self._analyze_by_model(),
            'by_customer': self._analyze_by_customer(),
            'by_feature': self._analyze_by_feature(),
            'by_organization': self._analyze_by_organization(),
            'forecast': self._generate_forecast(),
            'efficiency': self._analyze_efficiency(),
            'top_spenders': self._identify_top_spenders(limit=10),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary statistics."""
        total_metrics = aggregate_metrics(self.calls)

        # Calculate unique counts
        unique_customers = len(set(c['customer_id'] for c in self.calls))
        unique_orgs = len(set(c['organization_id'] for c in self.calls))
        unique_models = len(set(c['model'] for c in self.calls))

        return {
            'total_calls': total_metrics['call_count'],
            'total_cost': total_metrics['total_cost'],
            'total_tokens': total_metrics['total_tokens'],
            'unique_customers': unique_customers,
            'unique_organizations': unique_orgs,
            'unique_models': unique_models,
            'avg_cost_per_call': total_metrics['avg_cost_per_call'],
            'avg_tokens_per_call': total_metrics['avg_tokens_per_call']
        }

    def _analyze_by_provider(self) -> List[Dict[str, Any]]:
        """Analyze costs by AI provider."""
        provider_groups = group_by(self.calls, 'provider')

        results = []
        for provider, calls in provider_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'provider': provider[0],
                'call_count': metrics['call_count'],
                'total_cost': metrics['total_cost'],
                'total_tokens': metrics['total_tokens'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        # Sort by cost descending
        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_model(self) -> List[Dict[str, Any]]:
        """Analyze costs by model."""
        model_groups = group_by(self.calls, 'provider', 'model')

        results = []
        for (provider, model), calls in model_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'provider': provider,
                'model': model,
                'call_count': metrics['call_count'],
                'total_cost': metrics['total_cost'],
                'total_tokens': metrics['total_tokens'],
                'avg_cost_per_call': metrics['avg_cost_per_call'],
                'cost_per_1k_tokens': safe_divide(metrics['total_cost'] * 1000, metrics['total_tokens'])
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_customer(self) -> List[Dict[str, Any]]:
        """Analyze costs by customer."""
        customer_groups = group_by(self.calls, 'customer_id')

        results = []
        for (customer_id,), calls in customer_groups.items():
            metrics = aggregate_metrics(calls)
            tier = calls[0]['subscription_tier']
            tier_price = calls[0]['tier_price_usd']

            results.append({
                'customer_id': customer_id,
                'tier': tier,
                'tier_price': tier_price,
                'call_count': metrics['call_count'],
                'total_cost': metrics['total_cost'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_feature(self) -> List[Dict[str, Any]]:
        """Analyze costs by feature."""
        feature_groups = group_by(self.calls, 'feature_id')

        results = []
        for (feature,), calls in feature_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'feature': feature,
                'call_count': metrics['call_count'],
                'total_cost': metrics['total_cost'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_organization(self) -> List[Dict[str, Any]]:
        """Analyze costs by organization."""
        org_groups = group_by(self.calls, 'organization_id')

        results = []
        for (org_id,), calls in org_groups.items():
            metrics = aggregate_metrics(calls)
            unique_customers = len(set(c['customer_id'] for c in calls))

            results.append({
                'organization_id': org_id,
                'customer_count': unique_customers,
                'call_count': metrics['call_count'],
                'total_cost': metrics['total_cost'],
                'avg_cost_per_customer': safe_divide(metrics['total_cost'], unique_customers)
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _generate_forecast(self) -> Dict[str, Any]:
        """Generate 30-day cost forecast based on recent data."""
        if not self.calls:
            return {'forecast_30_day': 0.0, 'daily_rate': 0.0}

        # Calculate date range
        timestamps = [c['timestamp'] for c in self.calls]
        min_date = min(timestamps)
        max_date = max(timestamps)
        days_in_data = (max_date - min_date).days + 1

        # Calculate total cost
        total_cost = sum(c['cost_usd'] for c in self.calls)

        # Calculate daily rate
        daily_rate = total_cost / days_in_data if days_in_data > 0 else 0.0

        # Forecast 30 days
        forecast_30_day = daily_rate * 30

        return {
            'forecast_30_day': forecast_30_day,
            'daily_rate': daily_rate,
            'days_in_dataset': days_in_data
        }

    def _analyze_efficiency(self) -> Dict[str, Any]:
        """Analyze token efficiency across providers/models."""
        if not self.calls:
            return {}

        total_cost = sum(c['cost_usd'] for c in self.calls)
        total_tokens = sum(c['total_tokens'] for c in self.calls)

        # Overall efficiency
        overall_cost_per_1k = safe_divide(total_cost * 1000, total_tokens)

        # Most efficient model
        model_groups = group_by(self.calls, 'provider', 'model')
        model_efficiency = []

        for (provider, model), calls in model_groups.items():
            metrics = aggregate_metrics(calls)
            cost_per_1k = safe_divide(metrics['total_cost'] * 1000, metrics['total_tokens'])
            model_efficiency.append({
                'provider': provider,
                'model': model,
                'cost_per_1k_tokens': cost_per_1k,
                'total_cost': metrics['total_cost'],
                'call_count': metrics['call_count']
            })

        # Sort by efficiency (lowest cost per 1k tokens)
        model_efficiency.sort(key=lambda x: x['cost_per_1k_tokens'])

        return {
            'overall_cost_per_1k_tokens': overall_cost_per_1k,
            'most_efficient': model_efficiency[0] if model_efficiency else None,
            'least_efficient': model_efficiency[-1] if model_efficiency else None
        }

    def _identify_top_spenders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify top spending customers."""
        customer_analysis = self._analyze_by_customer()
        return customer_analysis[:limit]

    def _generate_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []

        # Analyze provider distribution
        provider_analysis = self._analyze_by_provider()
        total_cost = sum(p['total_cost'] for p in provider_analysis)

        # Recommendation: Provider concentration
        if provider_analysis:
            top_provider_pct = (provider_analysis[0]['total_cost'] / total_cost) * 100
            if top_provider_pct > 70:
                recommendations.append(
                    f"Consider diversifying from {provider_analysis[0]['provider']} "
                    f"({top_provider_pct:.0f}% of costs) to reduce vendor lock-in"
                )

        # Recommendation: Model efficiency
        efficiency = self._analyze_efficiency()
        if efficiency and efficiency['most_efficient'] and efficiency['least_efficient']:
            most_eff = efficiency['most_efficient']
            least_eff = efficiency['least_efficient']
            savings_ratio = least_eff['cost_per_1k_tokens'] / most_eff['cost_per_1k_tokens']

            if savings_ratio > 5:
                recommendations.append(
                    f"Switch from {least_eff['model']} to {most_eff['model']} for "
                    f"{savings_ratio:.0f}x cost reduction per token"
                )

        # Recommendation: High-cost customers
        top_spenders = self._identify_top_spenders(limit=5)
        if top_spenders:
            top_5_cost = sum(c['total_cost'] for c in top_spenders)
            top_5_pct = (top_5_cost / total_cost) * 100
            if top_5_pct > 50:
                recommendations.append(
                    f"Top 5 customers account for {top_5_pct:.0f}% of costs. "
                    f"Implement usage-based pricing for high-usage tiers"
                )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = UnderstandingAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Understanding Usage & Cost Analysis")
    print("=" * 60)
    print(f"Total Calls:        {format_large_number(summary['total_calls'])}")
    print(f"Total Cost:         {format_currency(summary['total_cost'])}")
    print(f"Total Tokens:       {format_large_number(summary['total_tokens'])}")
    print(f"Unique Customers:   {summary['unique_customers']}")
    print(f"Avg Cost/Call:      {format_currency(summary['avg_cost_per_call'])}")
    print()

    # Print forecast
    forecast = results['forecast']
    print("30-Day Forecast")
    print("-" * 60)
    print(f"Daily Rate:         {format_currency(forecast['daily_rate'])}")
    print(f"30-Day Forecast:    {format_currency(forecast['forecast_30_day'])}")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/understanding_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
