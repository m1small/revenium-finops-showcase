"""Real-Time Decision Making Analyzer - FinOps Domain 3."""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics, detect_anomalies,
    format_currency, format_large_number, safe_divide
)


class RealtimeAnalyzer:
    """Analyzes anomalies, threshold violations, and real-time alerts."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'cost_anomalies': self._detect_cost_anomalies(),
            'customer_violations': self._detect_customer_violations(),
            'inefficient_patterns': self._detect_inefficient_patterns(),
            'portfolio_risk': self._analyze_portfolio_risk(),
            'alert_examples': self._generate_alert_examples(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall anomaly summary."""
        total_calls = len(self.calls)

        # Detect cost anomalies
        cost_anomalies = self._detect_cost_anomalies()
        anomaly_count = len(cost_anomalies['anomalous_calls'])

        # Customer violations
        violations = self._detect_customer_violations()
        customers_at_risk = len(violations['customers_at_risk'])

        # Calculate potential savings
        inefficient = self._detect_inefficient_patterns()
        potential_savings = sum(p['potential_savings'] for p in inefficient['patterns'])

        return {
            'total_calls': total_calls,
            'anomaly_count': anomaly_count,
            'anomaly_percentage': (anomaly_count / total_calls * 100) if total_calls > 0 else 0,
            'customers_at_risk': customers_at_risk,
            'potential_savings': potential_savings
        }

    def _detect_cost_anomalies(self) -> Dict[str, Any]:
        """Detect unusually expensive calls."""
        costs = [call['cost_usd'] for call in self.calls]
        anomaly_indices = detect_anomalies(costs, threshold_std=2.0)

        anomalous_calls = []
        for idx in anomaly_indices:
            call = self.calls[idx]
            anomalous_calls.append({
                'call_id': call['call_id'],
                'customer_id': call['customer_id'],
                'provider': call['provider'],
                'model': call['model'],
                'cost_usd': call['cost_usd'],
                'tokens': call['total_tokens'],
                'timestamp': call['timestamp']
            })

        # Sort by cost descending
        anomalous_calls.sort(key=lambda x: x['cost_usd'], reverse=True)

        # Calculate statistics
        if costs:
            mean_cost = sum(costs) / len(costs)
            max_cost = max(costs)
        else:
            mean_cost = 0
            max_cost = 0

        return {
            'anomalous_calls': anomalous_calls[:50],  # Top 50
            'total_anomalies': len(anomaly_indices),
            'mean_cost': mean_cost,
            'max_cost': max_cost
        }

    def _detect_customer_violations(self) -> Dict[str, Any]:
        """Detect customers exceeding budget thresholds."""
        # Group by customer
        customer_groups = group_by(self.calls, 'customer_id')

        customers_at_risk = []
        for (customer_id,), calls in customer_groups.items():
            # Calculate customer metrics
            total_cost = sum(c['cost_usd'] for c in calls)
            tier = calls[0]['subscription_tier']
            tier_price = calls[0]['tier_price_usd']

            # Calculate usage vs revenue ratio
            cost_ratio = (total_cost / tier_price * 100) if tier_price > 0 else 0

            # Risk classification
            if cost_ratio > 100:
                risk_level = 'critical'
            elif cost_ratio > 80:
                risk_level = 'high'
            elif cost_ratio > 50:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # Add if at risk (>50% of revenue)
            if cost_ratio > 50:
                customers_at_risk.append({
                    'customer_id': customer_id,
                    'tier': tier,
                    'tier_price': tier_price,
                    'total_cost': total_cost,
                    'cost_ratio': cost_ratio,
                    'margin': tier_price - total_cost,
                    'risk_level': risk_level,
                    'call_count': len(calls)
                })

        # Sort by cost ratio descending
        customers_at_risk.sort(key=lambda x: x['cost_ratio'], reverse=True)

        # Calculate revenue at risk
        revenue_at_risk = sum(c['tier_price'] for c in customers_at_risk if c['risk_level'] in ['critical', 'high'])

        return {
            'customers_at_risk': customers_at_risk[:25],  # Top 25
            'total_at_risk': len(customers_at_risk),
            'revenue_at_risk': revenue_at_risk,
            'critical_count': sum(1 for c in customers_at_risk if c['risk_level'] == 'critical'),
            'high_count': sum(1 for c in customers_at_risk if c['risk_level'] == 'high')
        }

    def _detect_inefficient_patterns(self) -> Dict[str, Any]:
        """Detect inefficient usage patterns."""
        patterns = []

        # Pattern 1: Expensive models for simple tasks (low token count)
        expensive_simple = []
        for call in self.calls:
            # Define "expensive" as > $0.01 per call and "simple" as < 500 tokens
            if call['cost_usd'] > 0.01 and call['total_tokens'] < 500:
                expensive_simple.append(call)

        if expensive_simple:
            total_waste = sum(c['cost_usd'] for c in expensive_simple)
            # Assume 80% savings by switching to cheaper model
            potential_savings = total_waste * 0.8

            patterns.append({
                'pattern': 'Expensive models for simple tasks',
                'occurrences': len(expensive_simple),
                'total_cost': total_waste,
                'potential_savings': potential_savings,
                'recommendation': 'Use cheaper models for tasks under 500 tokens'
            })

        # Pattern 2: High latency with high cost
        slow_expensive = []
        for call in self.calls:
            if call['latency_ms'] > 5000 and call['cost_usd'] > 0.05:
                slow_expensive.append(call)

        if slow_expensive:
            patterns.append({
                'pattern': 'High latency with high cost',
                'occurrences': len(slow_expensive),
                'total_cost': sum(c['cost_usd'] for c in slow_expensive),
                'potential_savings': sum(c['cost_usd'] for c in slow_expensive) * 0.5,
                'recommendation': 'Review prompt optimization or switch to faster models'
            })

        # Pattern 3: Repeated calls from same customer (possible retry loops)
        customer_call_counts = defaultdict(int)
        for call in self.calls:
            customer_call_counts[call['customer_id']] += 1

        avg_calls = sum(customer_call_counts.values()) / len(customer_call_counts) if customer_call_counts else 0
        high_volume_customers = [(k, v) for k, v in customer_call_counts.items() if v > avg_calls * 3]

        if high_volume_customers:
            patterns.append({
                'pattern': 'Abnormally high call volume from specific customers',
                'occurrences': len(high_volume_customers),
                'total_cost': 0,  # Would need to calculate
                'potential_savings': 0,
                'recommendation': 'Investigate potential retry loops or inefficient implementations'
            })

        return {
            'patterns': patterns,
            'total_potential_savings': sum(p['potential_savings'] for p in patterns)
        }

    def _analyze_portfolio_risk(self) -> Dict[str, Any]:
        """Analyze overall portfolio risk across all customers."""
        customer_groups = group_by(self.calls, 'customer_id')

        risk_distribution = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for (customer_id,), calls in customer_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)
            tier_price = calls[0]['tier_price_usd']
            cost_ratio = (total_cost / tier_price * 100) if tier_price > 0 else 0

            # Classify risk
            if cost_ratio > 100:
                risk_level = 'critical'
            elif cost_ratio > 80:
                risk_level = 'high'
            elif cost_ratio > 50:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            risk_distribution[risk_level].append({
                'customer_id': customer_id,
                'cost_ratio': cost_ratio,
                'total_cost': total_cost,
                'tier_price': tier_price
            })

        return {
            'distribution': {k: len(v) for k, v in risk_distribution.items()},
            'total_customers': sum(len(v) for v in risk_distribution.values()),
            'critical_customers': risk_distribution['critical'][:10],
            'health_score': safe_divide(len(risk_distribution['low']), sum(len(v) for v in risk_distribution.values())) * 100
        }

    def _generate_alert_examples(self) -> List[Dict[str, str]]:
        """Generate example alerts based on analysis."""
        alerts = []

        # Budget threshold alerts
        violations = self._detect_customer_violations()
        for customer in violations['customers_at_risk'][:3]:
            if customer['risk_level'] == 'critical':
                alerts.append({
                    'type': 'budget_exceeded',
                    'severity': 'critical',
                    'message': f"Customer {customer['customer_id']} has exceeded their {customer['tier']} "
                               f"tier budget: ${customer['total_cost']:.2f} spent vs ${customer['tier_price']} revenue "
                               f"({customer['cost_ratio']:.0f}% ratio)",
                    'recommended_action': 'Contact customer immediately for tier upgrade or usage reduction'
                })

        # Anomaly alerts
        anomalies = self._detect_cost_anomalies()
        if anomalies['anomalous_calls']:
            top_anomaly = anomalies['anomalous_calls'][0]
            alerts.append({
                'type': 'cost_anomaly',
                'severity': 'warning',
                'message': f"Unusual spending spike detected: {top_anomaly['customer_id']} spent "
                           f"${top_anomaly['cost_usd']:.4f} in a single call using {top_anomaly['model']} "
                           f"({top_anomaly['cost_usd'] / anomalies['mean_cost']:.1f}x average)",
                'recommended_action': 'Review call for efficiency optimization opportunities'
            })

        # Portfolio risk alerts
        portfolio = self._analyze_portfolio_risk()
        if portfolio['distribution']['critical'] > 0:
            alerts.append({
                'type': 'portfolio_risk',
                'severity': 'high',
                'message': f"{portfolio['distribution']['critical']} customers in critical state "
                           f"(costs > 100% of revenue). Total revenue at risk: "
                           f"${sum(c['tier_price'] for c in portfolio['critical_customers']):.2f}",
                'recommended_action': 'Immediate review of unprofitable customers required'
            })

        return alerts

    def _generate_recommendations(self) -> List[str]:
        """Generate real-time optimization recommendations."""
        recommendations = []

        # Customer risk recommendations
        violations = self._detect_customer_violations()
        if violations['total_at_risk'] > 0:
            recommendations.append(
                f"Monitor {violations['total_at_risk']} at-risk customers "
                f"({violations['critical_count']} critical, {violations['high_count']} high). "
                f"Revenue at risk: {format_currency(violations['revenue_at_risk'])}"
            )

        # Inefficiency recommendations
        inefficient = self._detect_inefficient_patterns()
        if inefficient['total_potential_savings'] > 0:
            recommendations.append(
                f"Identified {format_currency(inefficient['total_potential_savings'])} in potential savings "
                f"from fixing {len(inefficient['patterns'])} inefficient patterns"
            )

        # Anomaly recommendations
        anomalies = self._detect_cost_anomalies()
        if anomalies['total_anomalies'] > 10:
            recommendations.append(
                f"Detected {anomalies['total_anomalies']} cost anomalies. "
                f"Implement automated alerts for calls exceeding 2x average cost"
            )

        # Portfolio health
        portfolio = self._analyze_portfolio_risk()
        if portfolio['health_score'] < 50:
            recommendations.append(
                f"Portfolio health score: {portfolio['health_score']:.1f}%. "
                f"Consider implementing usage caps or tiered pricing adjustments"
            )

        return recommendations


def main():
    """Run analyzer and generate report."""
    import json

    csv_path = 'data/simulated_calls.csv'
    analyzer = RealtimeAnalyzer(csv_path)
    results = analyzer.analyze()

    # Print summary
    summary = results['summary']
    print("Real-Time Decision Making Analysis")
    print("=" * 60)
    print(f"Total Calls:           {format_large_number(summary['total_calls'])}")
    print(f"Anomalies:             {summary['anomaly_count']} ({summary['anomaly_percentage']:.1f}%)")
    print(f"Customers at Risk:     {summary['customers_at_risk']}")
    print(f"Potential Savings:     {format_currency(summary['potential_savings'])}")
    print()

    # Print alerts
    print("Sample Alerts")
    print("-" * 60)
    for alert in results['alert_examples'][:3]:
        print(f"[{alert['severity'].upper()}] {alert['message']}")
    print()

    # Print recommendations
    print("Recommendations")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")

    # Save full results
    output_path = 'reports/html/realtime_analysis.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == '__main__':
    main()
