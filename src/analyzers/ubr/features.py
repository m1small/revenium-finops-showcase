"""Feature Economics Analyzer - UBR Domain 3."""

import sys
import os
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class FeatureEconomicsAnalyzer:
    """Analyzes feature-level costs, adoption, and investment priorities."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'by_feature': self._analyze_by_feature(),
            'adoption_analysis': self._analyze_adoption(),
            'investment_matrix': self._create_investment_matrix(),
            'bundle_opportunities': self._analyze_bundles(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall feature economics summary."""
        total_cost = sum(c['cost_usd'] for c in self.calls)
        unique_features = len(set(c['feature_id'] for c in self.calls))
        unique_customers = len(set(c['customer_id'] for c in self.calls))

        return {
            'total_cost': total_cost,
            'total_features': unique_features,
            'total_customers': unique_customers,
            'avg_cost_per_feature': safe_divide(total_cost, unique_features),
            'total_calls': len(self.calls)
        }

    def _analyze_by_feature(self) -> List[Dict[str, Any]]:
        """Analyze costs and metrics by feature."""
        feature_groups = group_by(self.calls, 'feature_id')
        total_customers = len(set(c['customer_id'] for c in self.calls))

        results = []
        for (feature_id,), calls in feature_groups.items():
            metrics = aggregate_metrics(calls)

            # Customer adoption
            unique_customers = len(set(c['customer_id'] for c in calls))
            adoption_rate = (unique_customers / total_customers * 100) if total_customers > 0 else 0

            # Cost metrics
            cost_per_customer = safe_divide(metrics['total_cost'], unique_customers)

            results.append({
                'feature_id': feature_id,
                'total_cost': metrics['total_cost'],
                'call_count': metrics['call_count'],
                'customer_count': unique_customers,
                'adoption_rate': adoption_rate,
                'cost_per_customer': cost_per_customer,
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        return sorted(results, key=lambda x: x['total_cost'], reverse=True)

    def _analyze_adoption(self) -> Dict[str, Any]:
        """Detailed adoption analysis."""
        features = self._analyze_by_feature()

        # Categorize by adoption
        categories = {
            'high_adoption': [],    # >60%
            'medium_adoption': [],  # 30-60%
            'low_adoption': []      # <30%
        }

        for feature in features:
            adoption_rate = feature['adoption_rate']

            if adoption_rate > 60:
                categories['high_adoption'].append(feature)
            elif adoption_rate > 30:
                categories['medium_adoption'].append(feature)
            else:
                categories['low_adoption'].append(feature)

        return {
            'high_adoption': categories['high_adoption'],
            'medium_adoption': categories['medium_adoption'],
            'low_adoption': categories['low_adoption'],
            'distribution': {
                'high': len(categories['high_adoption']),
                'medium': len(categories['medium_adoption']),
                'low': len(categories['low_adoption'])
            }
        }

    def _create_investment_matrix(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create investment decision matrix based on cost and adoption."""
        features = self._analyze_by_feature()

        # Calculate median cost to determine high/low
        costs = [f['total_cost'] for f in features]
        median_cost = sorted(costs)[len(costs) // 2] if costs else 0

        matrix = {
            'invest': [],      # High adoption, high cost
            'maintain': [],    # High adoption, low cost
            'optimize': [],    # Low adoption, high cost
            'sunset': []       # Low adoption, low cost
        }

        for feature in features:
            is_high_adoption = feature['adoption_rate'] > 40
            is_high_cost = feature['total_cost'] > median_cost

            feature_copy = feature.copy()

            if is_high_adoption and is_high_cost:
                feature_copy['strategy'] = 'Invest'
                feature_copy['rationale'] = 'High usage and high value - core feature'
                matrix['invest'].append(feature_copy)
            elif is_high_adoption and not is_high_cost:
                feature_copy['strategy'] = 'Maintain'
                feature_copy['rationale'] = 'Popular but low cost - efficient feature'
                matrix['maintain'].append(feature_copy)
            elif not is_high_adoption and is_high_cost:
                feature_copy['strategy'] = 'Optimize'
                feature_copy['rationale'] = 'Expensive but underutilized - improve or sunset'
                matrix['optimize'].append(feature_copy)
            else:
                feature_copy['strategy'] = 'Sunset'
                feature_copy['rationale'] = 'Low adoption and low cost - consider removal'
                matrix['sunset'].append(feature_copy)

        return matrix

    def _analyze_bundles(self) -> List[Dict[str, Any]]:
        """Identify features commonly used together for bundling opportunities."""
        # Track which features each customer uses
        customer_features = defaultdict(set)

        for call in self.calls:
            customer_features[call['customer_id']].add(call['feature_id'])

        # Find feature co-occurrence
        feature_pairs = defaultdict(int)

        for features in customer_features.values():
            feature_list = sorted(features)
            for i, f1 in enumerate(feature_list):
                for f2 in feature_list[i+1:]:
                    pair = (f1, f2)
                    feature_pairs[pair] += 1

        # Convert to list and sort by frequency
        bundles = []
        for (f1, f2), count in feature_pairs.items():
            total_customers = len(customer_features)
            bundle_rate = (count / total_customers * 100) if total_customers > 0 else 0

            # Only include pairs used by >20% of customers
            if bundle_rate > 20:
                bundles.append({
                    'feature_1': f1,
                    'feature_2': f2,
                    'customer_count': count,
                    'bundle_rate': bundle_rate,
                    'opportunity': 'Create bundle pricing'
                })

        bundles.sort(key=lambda x: x['bundle_rate'], reverse=True)

        return bundles[:10]  # Top 10

    def _generate_recommendations(self) -> List[str]:
        """Generate feature investment recommendations."""
        recommendations = []

        # Investment matrix insights
        matrix = self._create_investment_matrix()

        if matrix['invest']:
            top_invest = matrix['invest'][0]
            recommendations.append(
                f"Invest in {top_invest['feature_id']} - {top_invest['adoption_rate']:.0f}% adoption, "
                f"{format_currency(top_invest['total_cost'])} cost. {top_invest['rationale']}"
            )

        if matrix['optimize']:
            recommendations.append(
                f"{len(matrix['optimize'])} features need optimization - "
                f"high cost but low adoption. Review for efficiency improvements or deprecation."
            )

        if matrix['sunset']:
            recommendations.append(
                f"{len(matrix['sunset'])} features are sunset candidates - "
                f"low adoption and low cost. Consider removal to reduce complexity."
            )

        # Adoption insights
        adoption = self._analyze_adoption()
        if adoption['distribution']['low'] > adoption['distribution']['high']:
            recommendations.append(
                f"{adoption['distribution']['low']} features have <30% adoption. "
                f"Focus on feature discovery and onboarding improvements."
            )

        # Bundle opportunities
        bundles = self._analyze_bundles()
        if bundles:
            top_bundle = bundles[0]
            recommendations.append(
                f"Bundle opportunity: {top_bundle['feature_1']} + {top_bundle['feature_2']} "
                f"used together by {top_bundle['bundle_rate']:.0f}% of customers"
            )

        # Cost concentration
        features = self._analyze_by_feature()
        if features:
            top_3_cost = sum(f['total_cost'] for f in features[:3])
            total_cost = sum(f['total_cost'] for f in features)
            top_3_pct = (top_3_cost / total_cost * 100) if total_cost > 0 else 0

            if top_3_pct > 50:
                recommendations.append(
                    f"Top 3 features account for {top_3_pct:.0f}% of costs. "
                    f"Optimize these for maximum impact."
                )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = FeatureEconomicsAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Feature Economics Analysis")
    print("=" * 60)
    print(f"Total Cost:            {format_currency(summary['total_cost'])}")
    print(f"Total Features:        {summary['total_features']}")
    print(f"Total Customers:       {summary['total_customers']}")
    print(f"Avg Cost/Feature:      {format_currency(summary['avg_cost_per_feature'])}")
    print()

    # Print investment matrix
    matrix = results['investment_matrix']
    print("Investment Matrix")
    print("-" * 60)
    print(f"Invest:                {len(matrix['invest'])} features")
    print(f"Maintain:              {len(matrix['maintain'])} features")
    print(f"Optimize:              {len(matrix['optimize'])} features")
    print(f"Sunset:                {len(matrix['sunset'])} features")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/features_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
