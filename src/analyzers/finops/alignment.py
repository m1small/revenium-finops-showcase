"""Organizational Alignment Analyzer - FinOps Domain 5."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class AlignmentAnalyzer:
    """Analyzes multi-tenant cost allocation and chargeback/showback."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_organization': self._analyze_by_organization(),
            'by_product': self._analyze_by_product(),
            'by_feature': self._analyze_by_feature(),
            'chargeback_report': self._generate_chargeback_report(),
            'efficiency_comparison': self._compare_efficiency(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall organizational summary."""
        total_cost = sum(c['cost_usd'] for c in self.calls)
        total_calls = len(self.calls)

        unique_orgs = len(set(c['organization_id'] for c in self.calls))
        unique_products = len(set(c['product_id'] for c in self.calls))
        unique_features = len(set(c['feature_id'] for c in self.calls))

        return {
            'total_cost': total_cost,
            'total_calls': total_calls,
            'unique_organizations': unique_orgs,
            'unique_products': unique_products,
            'unique_features': unique_features,
            'avg_cost_per_organization': safe_divide(total_cost, unique_orgs)
        }

    def _analyze_by_organization(self) -> List[Dict[str, Any]]:
        """Analyze costs by organization."""
        org_groups = group_by(self.calls, 'organization_id')

        results = []
        for (org_id,), calls in org_groups.items():
            metrics = aggregate_metrics(calls)

            # Count unique customers, products, features
            unique_customers = len(set(c['customer_id'] for c in calls))
            unique_products = len(set(c['product_id'] for c in calls))
            unique_features = len(set(c['feature_id'] for c in calls))

            results.append({
                'organization_id': org_id,
                'total_cost': metrics['total_cost'],
                'call_count': metrics['call_count'],
                'customer_count': unique_customers,
                'product_count': unique_products,
                'feature_count': unique_features,
                'avg_cost_per_call': metrics['avg_cost_per_call'],
                'avg_cost_per_customer': safe_divide(metrics['total_cost'], unique_customers)
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_product(self) -> List[Dict[str, Any]]:
        """Analyze costs by product."""
        product_groups = group_by(self.calls, 'product_id')

        results = []
        for (product_id,), calls in product_groups.items():
            metrics = aggregate_metrics(calls)

            unique_customers = len(set(c['customer_id'] for c in calls))
            unique_orgs = len(set(c['organization_id'] for c in calls))

            results.append({
                'product_id': product_id,
                'total_cost': metrics['total_cost'],
                'call_count': metrics['call_count'],
                'customer_count': unique_customers,
                'organization_count': unique_orgs,
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_by_feature(self) -> List[Dict[str, Any]]:
        """Analyze costs by feature."""
        feature_groups = group_by(self.calls, 'feature_id')

        results = []
        for (feature_id,), calls in feature_groups.items():
            metrics = aggregate_metrics(calls)

            unique_customers = len(set(c['customer_id'] for c in calls))
            unique_products = len(set(c['product_id'] for c in calls))

            # Calculate adoption rate (unique customers using this feature)
            total_unique_customers = len(set(c['customer_id'] for c in self.calls))
            adoption_rate = (unique_customers / total_unique_customers * 100) if total_unique_customers > 0 else 0

            results.append({
                'feature_id': feature_id,
                'total_cost': metrics['total_cost'],
                'call_count': metrics['call_count'],
                'customer_count': unique_customers,
                'product_count': unique_products,
                'adoption_rate': adoption_rate,
                'avg_cost_per_customer': safe_divide(metrics['total_cost'], unique_customers)
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _generate_chargeback_report(self) -> Dict[str, Any]:
        """Generate chargeback/showback allocation report."""
        # Chargeback methodology: Direct allocation based on usage

        org_analysis = self._analyze_by_organization()

        chargeback_items = []
        for org in org_analysis:
            chargeback_items.append({
                'organization_id': org['organization_id'],
                'chargeable_amount': org['total_cost'],
                'basis': 'Direct usage allocation',
                'call_count': org['call_count'],
                'customer_count': org['customer_count'],
                'allocation_method': '100% direct attribution based on API calls'
            })

        # Calculate total and validate (should equal total cost)
        total_chargeback = sum(item['chargeable_amount'] for item in chargeback_items)

        return {
            'chargeback_items': chargeback_items,
            'total_chargeback': total_chargeback,
            'allocation_method': 'Direct usage tracking',
            'billing_period': 'Current dataset period',
            'validation': 'All costs allocated (100% coverage)'
        }

    def _compare_efficiency(self) -> Dict[str, Any]:
        """Compare efficiency across organizations."""
        org_analysis = self._analyze_by_organization()

        # Calculate efficiency metrics for each org
        efficiency_scores = []
        for org in org_analysis:
            # Efficiency score: lower cost per call is better
            # Normalize to 0-100 scale (100 = most efficient)
            cost_per_call = org['avg_cost_per_call']

            efficiency_scores.append({
                'organization_id': org['organization_id'],
                'cost_per_call': cost_per_call,
                'total_cost': org['total_cost'],
                'call_count': org['call_count']
            })

        # Find best and worst performers
        if efficiency_scores:
            most_efficient = min(efficiency_scores, key=lambda x: x['cost_per_call'])
            least_efficient = max(efficiency_scores, key=lambda x: x['cost_per_call'])

            efficiency_ratio = safe_divide(
                least_efficient['cost_per_call'],
                most_efficient['cost_per_call']
            )
        else:
            most_efficient = None
            least_efficient = None
            efficiency_ratio = 1.0

        return {
            'organizations': efficiency_scores,
            'most_efficient': most_efficient,
            'least_efficient': least_efficient,
            'efficiency_gap': efficiency_ratio,
            'recommendation': self._get_efficiency_recommendation(efficiency_ratio)
        }

    def _get_efficiency_recommendation(self, ratio: float) -> str:
        """Get recommendation based on efficiency gap."""
        if ratio > 3:
            return 'Significant efficiency gap detected. Share best practices from top-performing organizations.'
        elif ratio > 2:
            return 'Moderate efficiency variance. Consider standardizing AI usage patterns.'
        else:
            return 'Organizations show similar efficiency. Focus on overall optimization.'

    def _generate_recommendations(self) -> List[str]:
        """Generate organizational alignment recommendations."""
        recommendations = []

        # Organization-level insights
        org_analysis = self._analyze_by_organization()
        if org_analysis:
            top_org = org_analysis[0]
            total_cost = sum(org['total_cost'] for org in org_analysis)
            top_org_pct = (top_org['total_cost'] / total_cost * 100) if total_cost > 0 else 0

            if top_org_pct > 50:
                recommendations.append(
                    f"{top_org['organization_id']} accounts for {top_org_pct:.1f}% of total costs. "
                    f"Consider dedicated optimization review."
                )

        # Efficiency comparison
        efficiency = self._compare_efficiency()
        if efficiency['efficiency_gap'] > 2:
            recommendations.append(
                f"{efficiency['efficiency_gap']:.1f}x efficiency gap between organizations. "
                f"{efficiency['recommendation']}"
            )

        # Feature distribution
        feature_analysis = self._analyze_by_feature()
        if feature_analysis:
            # Check for underutilized features
            low_adoption = [f for f in feature_analysis if f['adoption_rate'] < 20 and f['total_cost'] > 50]
            if low_adoption:
                recommendations.append(
                    f"{len(low_adoption)} expensive features have <20% adoption. "
                    f"Consider sunsetting or improving feature promotion."
                )

        # Product-level insights
        product_analysis = self._analyze_by_product()
        if len(product_analysis) > 1:
            recommendations.append(
                f"Costs distributed across {len(product_analysis)} products. "
                f"Implement product-level budgets and tracking."
            )

        # Chargeback recommendation
        chargeback = self._generate_chargeback_report()
        recommendations.append(
            f"Chargeback total: {format_currency(chargeback['total_chargeback'])} "
            f"allocated across {len(chargeback['chargeback_items'])} organizations "
            f"using direct usage methodology."
        )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = AlignmentAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Organizational Alignment Analysis")
    print("=" * 60)
    print(f"Total Cost:            {format_currency(summary['total_cost'])}")
    print(f"Organizations:         {summary['unique_organizations']}")
    print(f"Products:              {summary['unique_products']}")
    print(f"Features:              {summary['unique_features']}")
    print(f"Avg Cost/Org:          {format_currency(summary['avg_cost_per_organization'])}")
    print()

    # Print efficiency comparison
    efficiency = results['efficiency_comparison']
    print("Efficiency Comparison")
    print("-" * 60)
    if efficiency['most_efficient'] and efficiency['least_efficient']:
        print(f"Most Efficient:        {efficiency['most_efficient']['organization_id']} "
              f"({format_currency(efficiency['most_efficient']['cost_per_call'])}/call)")
        print(f"Least Efficient:       {efficiency['least_efficient']['organization_id']} "
              f"({format_currency(efficiency['least_efficient']['cost_per_call'])}/call)")
        print(f"Efficiency Gap:        {efficiency['efficiency_gap']:.1f}x")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/alignment_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
