"""Churn Risk & Growth Signals Analyzer."""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics,
    format_currency, format_large_number, safe_divide
)


class ChurnGrowthAnalyzer:
    """Analyzes customer engagement, churn risk, and expansion opportunities."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'usage_velocity': self._analyze_usage_velocity(),
            'churn_risk_customers': self._identify_churn_risk(),
            'expansion_opportunities': self._identify_expansion_opportunities(),
            'feature_adoption': self._analyze_feature_adoption(),
            'engagement_scores': self._calculate_engagement_scores(),
            'tier_mismatch': self._detect_tier_mismatch(),
            'cohort_analysis': self._analyze_cohorts(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall churn/growth summary."""
        unique_customers = len(set(c['customer_id'] for c in self.calls))

        # Calculate time range
        timestamps = [c['timestamp'] for c in self.calls]
        date_range_days = (max(timestamps) - min(timestamps)).days

        # Customer segmentation
        customer_calls = defaultdict(int)
        for call in self.calls:
            customer_calls[call['customer_id']] += 1

        avg_calls_per_customer = sum(customer_calls.values()) / len(customer_calls)

        return {
            'total_customers': unique_customers,
            'total_calls': len(self.calls),
            'date_range_days': date_range_days,
            'avg_calls_per_customer': avg_calls_per_customer,
            'analysis_period': f"{date_range_days} days"
        }

    def _analyze_usage_velocity(self) -> List[Dict[str, Any]]:
        """Analyze usage trends for each customer."""
        # Sort calls by timestamp
        sorted_calls = sorted(self.calls, key=lambda x: x['timestamp'])

        # Get time range
        min_time = min(c['timestamp'] for c in sorted_calls)
        max_time = max(c['timestamp'] for c in sorted_calls)
        total_days = (max_time - min_time).days

        if total_days < 2:
            return []

        # Split into two periods for trend analysis
        midpoint = min_time + timedelta(days=total_days / 2)

        customer_groups = group_by(self.calls, 'customer_id')

        results = []
        for (customer_id,), calls in customer_groups.items():
            # Split into first and second half
            first_half = [c for c in calls if c['timestamp'] < midpoint]
            second_half = [c for c in calls if c['timestamp'] >= midpoint]

            first_half_calls = len(first_half)
            second_half_calls = len(second_half)

            # Calculate velocity (growth rate)
            if first_half_calls > 0:
                growth_rate = ((second_half_calls - first_half_calls) / first_half_calls) * 100
            else:
                growth_rate = 100 if second_half_calls > 0 else 0

            # Classify trend
            if growth_rate > 20:
                trend = 'growing'
            elif growth_rate < -20:
                trend = 'declining'
            else:
                trend = 'stable'

            # Get tier info
            tier = calls[0]['subscription_tier']
            archetype = calls[0]['customer_archetype']

            results.append({
                'customer_id': customer_id,
                'tier': tier,
                'archetype': archetype,
                'total_calls': len(calls),
                'first_period_calls': first_half_calls,
                'second_period_calls': second_half_calls,
                'growth_rate': growth_rate,
                'trend': trend
            })

        results.sort(key=lambda x: x['growth_rate'])
        return results

    def _identify_churn_risk(self) -> List[Dict[str, Any]]:
        """Identify customers at risk of churning."""
        velocity = self._analyze_usage_velocity()

        at_risk = []
        for customer in velocity:
            risk_score = 0
            risk_factors = []

            # Declining usage
            if customer['growth_rate'] < -30:
                risk_score += 40
                risk_factors.append('steep_usage_decline')
            elif customer['growth_rate'] < -10:
                risk_score += 20
                risk_factors.append('usage_decline')

            # Low overall engagement
            if customer['total_calls'] < 100:
                risk_score += 15
                risk_factors.append('low_engagement')

            # Tier mismatch (paying for more than using)
            if customer['tier'] == 'enterprise' and customer['total_calls'] < 200:
                risk_score += 25
                risk_factors.append('tier_oversubscribed')

            # Light archetype with declining usage
            if customer['archetype'] == 'light' and customer['growth_rate'] < 0:
                risk_score += 10
                risk_factors.append('light_user_declining')

            # Only flag if risk score is significant
            if risk_score >= 30:
                # Get cost/revenue info
                customer_calls = [c for c in self.calls if c['customer_id'] == customer['customer_id']]
                total_cost = sum(c['cost_usd'] for c in customer_calls)
                tier_price = customer_calls[0]['tier_price_usd']

                at_risk.append({
                    'customer_id': customer['customer_id'],
                    'tier': customer['tier'],
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'growth_rate': customer['growth_rate'],
                    'total_calls': customer['total_calls'],
                    'monthly_revenue': tier_price,
                    'total_cost': total_cost
                })

        at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
        return at_risk

    def _identify_expansion_opportunities(self) -> List[Dict[str, Any]]:
        """Identify customers ready for tier upgrades."""
        velocity = self._analyze_usage_velocity()

        opportunities = []
        for customer in velocity:
            expansion_score = 0
            signals = []

            # Strong growth
            if customer['growth_rate'] > 50:
                expansion_score += 40
                signals.append('strong_growth')
            elif customer['growth_rate'] > 20:
                expansion_score += 20
                signals.append('moderate_growth')

            # High usage on lower tier
            if customer['tier'] == 'starter' and customer['total_calls'] > 500:
                expansion_score += 40
                signals.append('starter_power_user')
            elif customer['tier'] == 'pro' and customer['total_calls'] > 2000:
                expansion_score += 30
                signals.append('pro_enterprise_usage')

            # Heavy archetype on lower tier
            if customer['archetype'] == 'heavy' and customer['tier'] in ['starter', 'pro']:
                expansion_score += 25
                signals.append('heavy_user_low_tier')

            # Only flag if expansion score is significant
            if expansion_score >= 30:
                customer_calls = [c for c in self.calls if c['customer_id'] == customer['customer_id']]
                total_cost = sum(c['cost_usd'] for c in customer_calls)
                current_tier_price = customer_calls[0]['tier_price_usd']

                # Estimate next tier price
                tier_map = {'starter': 99, 'pro': 299, 'enterprise': 299}
                next_tier_price = tier_map.get(customer['tier'], current_tier_price)
                potential_expansion_revenue = next_tier_price - current_tier_price

                opportunities.append({
                    'customer_id': customer['customer_id'],
                    'current_tier': customer['tier'],
                    'expansion_score': expansion_score,
                    'signals': signals,
                    'growth_rate': customer['growth_rate'],
                    'total_calls': customer['total_calls'],
                    'current_monthly_revenue': current_tier_price,
                    'potential_expansion_revenue': potential_expansion_revenue
                })

        opportunities.sort(key=lambda x: x['expansion_score'], reverse=True)
        return opportunities

    def _analyze_feature_adoption(self) -> Dict[str, Any]:
        """Analyze feature adoption patterns."""
        customer_features = defaultdict(set)

        for call in self.calls:
            customer_features[call['customer_id']].add(call['feature_id'])

        # Count customers by feature diversity
        diversity_counts = defaultdict(int)
        for customer, features in customer_features.items():
            diversity_counts[len(features)] += 1

        # Identify expansion path features
        feature_sequences = defaultdict(lambda: defaultdict(int))
        for customer, features in customer_features.items():
            if len(features) > 1:
                for feature in features:
                    feature_sequences[feature]['adopted_with_multi'] += 1

        return {
            'total_customers': len(customer_features),
            'avg_features_per_customer': sum(len(f) for f in customer_features.values()) / len(customer_features),
            'single_feature_customers': diversity_counts.get(1, 0),
            'multi_feature_customers': sum(count for features, count in diversity_counts.items() if features > 1),
            'diversity_distribution': dict(diversity_counts)
        }

    def _calculate_engagement_scores(self) -> List[Dict[str, Any]]:
        """Calculate engagement score for each customer."""
        customer_groups = group_by(self.calls, 'customer_id')

        results = []
        for (customer_id,), calls in customer_groups.items():
            # Calculate various engagement metrics
            call_count = len(calls)
            unique_features = len(set(c['feature_id'] for c in calls))
            total_cost = sum(c['cost_usd'] for c in calls)

            # Calculate score (0-100)
            score = 0

            # Volume score (max 40 points)
            score += min(40, (call_count / 50) * 40)

            # Feature diversity score (max 30 points)
            score += min(30, (unique_features / 5) * 30)

            # Spend score (max 30 points)
            score += min(30, (total_cost / 10) * 30)

            # Classify engagement level
            if score >= 70:
                level = 'high'
            elif score >= 40:
                level = 'medium'
            else:
                level = 'low'

            results.append({
                'customer_id': customer_id,
                'engagement_score': score,
                'engagement_level': level,
                'call_count': call_count,
                'unique_features': unique_features,
                'total_spend': total_cost
            })

        results.sort(key=lambda x: x['engagement_score'], reverse=True)
        return results

    def _detect_tier_mismatch(self) -> List[Dict[str, Any]]:
        """Detect customers on wrong tier for their usage."""
        customer_groups = group_by(self.calls, 'customer_id')

        mismatches = []
        for (customer_id,), calls in customer_groups.items():
            tier = calls[0]['subscription_tier']
            archetype = calls[0]['customer_archetype']
            call_count = len(calls)
            total_cost = sum(c['cost_usd'] for c in calls)

            mismatch_type = None
            severity = 0

            # Oversubscribed (paying too much)
            if tier == 'enterprise' and call_count < 300:
                mismatch_type = 'oversubscribed'
                severity = 3
            elif tier == 'pro' and call_count < 100:
                mismatch_type = 'oversubscribed'
                severity = 2

            # Undersubscribed (should upgrade)
            elif tier == 'starter' and call_count > 1000:
                mismatch_type = 'undersubscribed'
                severity = 3
            elif tier == 'pro' and call_count > 3000:
                mismatch_type = 'undersubscribed'
                severity = 2

            if mismatch_type:
                mismatches.append({
                    'customer_id': customer_id,
                    'current_tier': tier,
                    'archetype': archetype,
                    'call_count': call_count,
                    'total_cost': total_cost,
                    'mismatch_type': mismatch_type,
                    'severity': severity
                })

        mismatches.sort(key=lambda x: x['severity'], reverse=True)
        return mismatches

    def _analyze_cohorts(self) -> Dict[str, Any]:
        """Analyze customer cohorts by tier and archetype."""
        cohorts = defaultdict(lambda: {
            'customers': set(),
            'total_calls': 0,
            'total_cost': 0
        })

        for call in self.calls:
            key = f"{call['subscription_tier']}_{call['customer_archetype']}"
            cohorts[key]['customers'].add(call['customer_id'])
            cohorts[key]['total_calls'] += 1
            cohorts[key]['total_cost'] += call['cost_usd']

        results = []
        for cohort_name, data in cohorts.items():
            tier, archetype = cohort_name.split('_')
            customer_count = len(data['customers'])

            results.append({
                'tier': tier,
                'archetype': archetype,
                'customer_count': customer_count,
                'total_calls': data['total_calls'],
                'avg_calls_per_customer': data['total_calls'] / customer_count if customer_count > 0 else 0,
                'total_cost': data['total_cost']
            })

        results.sort(key=lambda x: x['total_calls'], reverse=True)
        return {'cohorts': results}

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        churn_risk = self._identify_churn_risk()
        expansion = self._identify_expansion_opportunities()
        feature_adoption = self._analyze_feature_adoption()
        tier_mismatch = self._detect_tier_mismatch()

        # Churn risk
        if churn_risk:
            high_risk = [c for c in churn_risk if c['risk_score'] >= 60]
            total_at_risk_revenue = sum(c['monthly_revenue'] for c in churn_risk)

            recommendations.append(
                f"⚠️ URGENT: {len(high_risk)} high-risk customers ({len(churn_risk)} total at-risk) "
                f"representing ${total_at_risk_revenue:,.0f}/month in revenue. "
                f"Immediate customer success outreach required. Top risk factors: "
                f"{', '.join(set(f for c in churn_risk[:5] for f in c['risk_factors']))}."
            )

        # Expansion opportunities
        if expansion:
            high_potential = [e for e in expansion if e['expansion_score'] >= 60]
            total_expansion_revenue = sum(e['potential_expansion_revenue'] for e in expansion)

            recommendations.append(
                f"💰 OPPORTUNITY: {len(high_potential)} customers ready for tier upgrade "
                f"({len(expansion)} total). Potential expansion revenue: ${total_expansion_revenue:,.0f}/month. "
                f"Prioritize accounts showing {expansion[0]['signals'][0].replace('_', ' ')}."
            )

        # Feature adoption
        single_feature_pct = (feature_adoption['single_feature_customers'] / feature_adoption['total_customers']) * 100
        if single_feature_pct > 40:
            recommendations.append(
                f"📊 {single_feature_pct:.0f}% of customers use only one feature. "
                f"Implement cross-sell campaigns to drive multi-feature adoption. "
                f"Average features per customer: {feature_adoption['avg_features_per_customer']:.1f}."
            )

        # Tier mismatches
        if tier_mismatch:
            oversubscribed = [t for t in tier_mismatch if t['mismatch_type'] == 'oversubscribed']
            undersubscribed = [t for t in tier_mismatch if t['mismatch_type'] == 'undersubscribed']

            if oversubscribed:
                recommendations.append(
                    f"💸 {len(oversubscribed)} customers are oversubscribed (paying for unused capacity). "
                    f"Proactively offer downgrades to prevent churn and build trust."
                )

            if undersubscribed:
                recommendations.append(
                    f"📈 {len(undersubscribed)} customers are undersubscribed (heavy usage on low tier). "
                    f"These are ideal expansion candidates—reach out before competitors do."
                )

        if not recommendations:
            recommendations.append(
                "Customer health metrics are stable. Continue monitoring engagement trends and usage patterns."
            )

        return recommendations
