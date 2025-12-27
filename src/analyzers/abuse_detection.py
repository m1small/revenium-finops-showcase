"""Multi-Tenant Cost Anomaly & Abuse Detection Analyzer."""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from analyzers.common import (
    load_calls_from_csv, group_by, aggregate_metrics, detect_anomalies,
    format_currency, format_large_number, safe_divide
)


class AbuseDetectionAnalyzer:
    """Analyzes usage patterns for abuse, anomalies, and security issues."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'summary': self._generate_summary(),
            'cost_anomalies': self._detect_cost_anomalies(),
            'usage_spikes': self._detect_usage_spikes(),
            'tier_gaming': self._detect_tier_gaming(),
            'suspicious_patterns': self._detect_suspicious_patterns(),
            'concurrent_abuse': self._detect_concurrent_abuse(),
            'outlier_customers': self._identify_outliers(),
            'security_flags': self._generate_security_flags(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall abuse detection summary."""
        unique_customers = len(set(c['customer_id'] for c in self.calls))
        unique_orgs = len(set(c['organization_id'] for c in self.calls))

        # Calculate cost distribution
        costs = [c['cost_usd'] for c in self.calls]
        avg_cost = sum(costs) / len(costs)

        # Calculate z-scores for anomaly detection
        std_dev = (sum((c - avg_cost) ** 2 for c in costs) / len(costs)) ** 0.5
        anomaly_threshold = avg_cost + (2 * std_dev)

        anomalous_calls = sum(1 for c in costs if c > anomaly_threshold)

        return {
            'total_calls': len(self.calls),
            'total_customers': unique_customers,
            'total_organizations': unique_orgs,
            'avg_cost_per_call': avg_cost,
            'cost_std_dev': std_dev,
            'anomaly_threshold': anomaly_threshold,
            'anomalous_calls': anomalous_calls,
            'anomaly_rate': (anomalous_calls / len(self.calls)) * 100
        }

    def _detect_cost_anomalies(self) -> Dict[str, Any]:
        """Detect cost anomalies using statistical methods."""
        costs = [c['cost_usd'] for c in self.calls]
        anomaly_indices = detect_anomalies(costs, threshold_std=2.5)

        anomalous_calls = []
        for idx in anomaly_indices:
            call = self.calls[idx]
            anomalous_calls.append({
                'customer_id': call['customer_id'],
                'model': call['model'],
                'feature': call['feature_id'],
                'cost_usd': call['cost_usd'],
                'tokens': call['total_tokens'],
                'timestamp': call['timestamp'].isoformat()
            })

        # Calculate total wasted cost
        avg_cost = sum(costs) / len(costs)
        total_anomaly_cost = sum(c['cost_usd'] for c in anomalous_calls)
        estimated_waste = total_anomaly_cost - (avg_cost * len(anomalous_calls))

        return {
            'anomaly_count': len(anomalous_calls),
            'total_anomaly_cost': total_anomaly_cost,
            'estimated_waste': max(0, estimated_waste),
            'top_anomalies': sorted(anomalous_calls, key=lambda x: x['cost_usd'], reverse=True)[:20]
        }

    def _detect_usage_spikes(self) -> List[Dict[str, Any]]:
        """Detect sudden usage spikes by customer."""
        # Sort by timestamp
        sorted_calls = sorted(self.calls, key=lambda x: x['timestamp'])

        # Group by customer and hour
        customer_hourly = defaultdict(lambda: defaultdict(int))

        for call in sorted_calls:
            hour_key = call['timestamp'].replace(minute=0, second=0, microsecond=0)
            customer_hourly[call['customer_id']][hour_key] += 1

        spikes = []
        for customer, hourly_counts in customer_hourly.items():
            if len(hourly_counts) < 2:
                continue

            counts = list(hourly_counts.values())
            avg_hourly = sum(counts) / len(counts)
            max_hourly = max(counts)

            # Spike = 10x or more than average
            if max_hourly > avg_hourly * 10 and max_hourly > 100:
                spike_hour = max(hourly_counts.items(), key=lambda x: x[1])

                # Get customer info
                customer_calls = [c for c in self.calls if c['customer_id'] == customer]
                tier = customer_calls[0]['subscription_tier']

                spikes.append({
                    'customer_id': customer,
                    'tier': tier,
                    'spike_hour': spike_hour[0].isoformat(),
                    'spike_count': spike_hour[1],
                    'avg_hourly_count': avg_hourly,
                    'spike_multiplier': max_hourly / avg_hourly
                })

        spikes.sort(key=lambda x: x['spike_multiplier'], reverse=True)
        return spikes

    def _detect_tier_gaming(self) -> List[Dict[str, Any]]:
        """Detect potential tier gaming (starter tier with enterprise usage)."""
        customer_groups = group_by(self.calls, 'customer_id')

        gaming_suspects = []
        for (customer_id,), calls in customer_groups.items():
            tier = calls[0]['subscription_tier']
            tier_price = calls[0]['tier_price_usd']

            # Calculate usage metrics
            total_cost = sum(c['cost_usd'] for c in calls)
            call_count = len(calls)
            avg_cost_per_call = total_cost / call_count

            # Red flags for tier gaming
            gaming_score = 0
            flags = []

            # Starter tier with very high volume
            if tier == 'starter' and call_count > 2000:
                gaming_score += 40
                flags.append('high_volume_starter')

            # Starter tier with high total cost
            if tier == 'starter' and total_cost > tier_price * 3:
                gaming_score += 30
                flags.append('cost_exceeds_subscription_3x')

            # Pro tier with enterprise-level automation
            if tier == 'pro' and call_count > 5000:
                gaming_score += 25
                flags.append('enterprise_volume_on_pro')

            # Very uniform call patterns (automation)
            timestamps = [c['timestamp'] for c in calls]
            if len(timestamps) > 10:
                time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds()
                             for i in range(min(100, len(timestamps)-1))]
                avg_diff = sum(time_diffs) / len(time_diffs)
                std_diff = (sum((d - avg_diff) ** 2 for d in time_diffs) / len(time_diffs)) ** 0.5

                # Very consistent timing = likely automation
                if std_diff < avg_diff * 0.1 and tier in ['starter', 'pro']:
                    gaming_score += 20
                    flags.append('automated_pattern')

            if gaming_score >= 30:
                gaming_suspects.append({
                    'customer_id': customer_id,
                    'tier': tier,
                    'tier_price': tier_price,
                    'gaming_score': gaming_score,
                    'flags': flags,
                    'call_count': call_count,
                    'total_cost': total_cost,
                    'cost_to_price_ratio': total_cost / (tier_price / 30)  # Daily ratio
                })

        gaming_suspects.sort(key=lambda x: x['gaming_score'], reverse=True)
        return gaming_suspects

    def _detect_suspicious_patterns(self) -> Dict[str, Any]:
        """Detect various suspicious usage patterns."""
        patterns = {
            'batch_processing_abuse': [],
            'off_hours_spikes': [],
            'model_hopping': [],
            'feature_spam': []
        }

        customer_groups = group_by(self.calls, 'customer_id')

        for (customer_id,), calls in customer_groups.items():
            # Batch processing abuse (very large batches)
            token_sizes = [c['total_tokens'] for c in calls]
            if any(t > 10000 for t in token_sizes):
                large_batch_count = sum(1 for t in token_sizes if t > 10000)
                if large_batch_count > 5:
                    patterns['batch_processing_abuse'].append({
                        'customer_id': customer_id,
                        'large_batch_count': large_batch_count,
                        'max_tokens': max(token_sizes)
                    })

            # Off-hours spikes (potential mining/abuse)
            off_hours_calls = [c for c in calls if c['timestamp'].hour < 6 or c['timestamp'].hour > 22]
            if len(off_hours_calls) > len(calls) * 0.7:  # >70% off-hours
                patterns['off_hours_spikes'].append({
                    'customer_id': customer_id,
                    'off_hours_percentage': (len(off_hours_calls) / len(calls)) * 100,
                    'total_calls': len(calls)
                })

            # Model hopping (trying many different models)
            unique_models = len(set(c['model'] for c in calls))
            if unique_models > 10 and len(calls) > 100:
                patterns['model_hopping'].append({
                    'customer_id': customer_id,
                    'unique_models': unique_models,
                    'total_calls': len(calls)
                })

            # Feature spam (one feature, very high volume)
            feature_counts = defaultdict(int)
            for call in calls:
                feature_counts[call['feature_id']] += 1

            if feature_counts:
                max_feature = max(feature_counts.items(), key=lambda x: x[1])
                if max_feature[1] > len(calls) * 0.95 and len(calls) > 1000:
                    patterns['feature_spam'].append({
                        'customer_id': customer_id,
                        'dominant_feature': max_feature[0],
                        'feature_percentage': (max_feature[1] / len(calls)) * 100,
                        'total_calls': len(calls)
                    })

        return patterns

    def _detect_concurrent_abuse(self) -> Dict[str, Any]:
        """Detect potential concurrent session abuse."""
        # Group by customer and minute
        customer_minute_counts = defaultdict(lambda: defaultdict(int))

        for call in self.calls:
            minute_key = call['timestamp'].replace(second=0, microsecond=0)
            customer_minute_counts[call['customer_id']][minute_key] += 1

        abuse_cases = []
        for customer, minute_counts in customer_minute_counts.items():
            max_concurrent = max(minute_counts.values())

            # Flag if >50 calls per minute (likely scripted)
            if max_concurrent > 50:
                customer_calls = [c for c in self.calls if c['customer_id'] == customer]
                tier = customer_calls[0]['subscription_tier']

                abuse_cases.append({
                    'customer_id': customer,
                    'tier': tier,
                    'max_calls_per_minute': max_concurrent,
                    'total_calls': len(customer_calls)
                })

        abuse_cases.sort(key=lambda x: x['max_calls_per_minute'], reverse=True)

        return {
            'abuse_count': len(abuse_cases),
            'cases': abuse_cases[:20]  # Top 20
        }

    def _identify_outliers(self) -> List[Dict[str, Any]]:
        """Identify statistical outliers across multiple dimensions."""
        customer_groups = group_by(self.calls, 'customer_id')

        # Calculate overall statistics
        all_customer_costs = []
        all_customer_counts = []

        for (customer_id,), calls in customer_groups.items():
            all_customer_costs.append(sum(c['cost_usd'] for c in calls))
            all_customer_counts.append(len(calls))

        avg_cost = sum(all_customer_costs) / len(all_customer_costs)
        avg_count = sum(all_customer_counts) / len(all_customer_counts)

        # Identify outliers
        outliers = []
        for (customer_id,), calls in customer_groups.items():
            total_cost = sum(c['cost_usd'] for c in calls)
            call_count = len(calls)

            outlier_score = 0
            outlier_reasons = []

            # Cost outlier
            if total_cost > avg_cost * 5:
                outlier_score += 50
                outlier_reasons.append(f'cost_{int(total_cost/avg_cost)}x_avg')

            # Volume outlier
            if call_count > avg_count * 5:
                outlier_score += 40
                outlier_reasons.append(f'volume_{int(call_count/avg_count)}x_avg')

            # Latency outlier (suspicious if consistently fast - potential cached abuse)
            latencies = [c['latency_ms'] for c in calls]
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency < 300:  # Suspiciously fast
                outlier_score += 10
                outlier_reasons.append('unusually_fast_responses')

            if outlier_score >= 40:
                outliers.append({
                    'customer_id': customer_id,
                    'outlier_score': outlier_score,
                    'reasons': outlier_reasons,
                    'total_cost': total_cost,
                    'call_count': call_count,
                    'avg_latency_ms': avg_latency
                })

        outliers.sort(key=lambda x: x['outlier_score'], reverse=True)
        return outliers

    def _generate_security_flags(self) -> List[Dict[str, Any]]:
        """Generate security flags for immediate attention."""
        flags = []

        # Check all detection results
        cost_anomalies = self._detect_cost_anomalies()
        spikes = self._detect_usage_spikes()
        gaming = self._detect_tier_gaming()
        concurrent = self._detect_concurrent_abuse()

        # High-severity flags
        if cost_anomalies['anomaly_count'] > 100:
            flags.append({
                'severity': 'high',
                'type': 'cost_anomalies',
                'message': f"{cost_anomalies['anomaly_count']} cost anomalies detected",
                'estimated_impact': cost_anomalies['estimated_waste']
            })

        if len(spikes) > 10:
            flags.append({
                'severity': 'medium',
                'type': 'usage_spikes',
                'message': f"{len(spikes)} customers with suspicious usage spikes",
                'estimated_impact': 0
            })

        if len(gaming) > 5:
            flags.append({
                'severity': 'high',
                'type': 'tier_gaming',
                'message': f"{len(gaming)} potential tier gaming cases",
                'estimated_impact': sum(g['total_cost'] for g in gaming[:10])
            })

        if concurrent['abuse_count'] > 5:
            flags.append({
                'severity': 'critical',
                'type': 'concurrent_abuse',
                'message': f"{concurrent['abuse_count']} cases of excessive concurrent usage",
                'estimated_impact': 0
            })

        flags.sort(key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x['severity']], reverse=True)
        return flags

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable security recommendations."""
        recommendations = []

        summary = self._generate_summary()
        cost_anomalies = self._detect_cost_anomalies()
        gaming = self._detect_tier_gaming()
        concurrent = self._detect_concurrent_abuse()
        security_flags = self._generate_security_flags()

        # Cost anomalies
        if cost_anomalies['anomaly_count'] > 0:
            recommendations.append(
                f"🔴 CRITICAL: {cost_anomalies['anomaly_count']:,} cost anomalies detected "
                f"with ${cost_anomalies['estimated_waste']:,.2f} in estimated waste. "
                f"Implement real-time cost monitoring and automatic circuit breakers."
            )

        # Tier gaming
        if gaming:
            recommendations.append(
                f"⚠️ {len(gaming)} customers flagged for potential tier gaming. "
                f"Top offender has {gaming[0]['gaming_score']} gaming score. "
                f"Enforce usage quotas and implement tier-based rate limiting."
            )

        # Concurrent abuse
        if concurrent['abuse_count'] > 0:
            recommendations.append(
                f"🚨 {concurrent['abuse_count']} accounts show excessive concurrent usage "
                f"(max {concurrent['cases'][0]['max_calls_per_minute']} calls/minute). "
                f"Implement rate limiting and CAPTCHA challenges for high-velocity patterns."
            )

        # Anomaly rate
        if summary['anomaly_rate'] > 5:
            recommendations.append(
                f"Anomaly rate is {summary['anomaly_rate']:.1f}% (threshold: 5%). "
                f"Review pricing model and implement dynamic pricing based on usage patterns."
            )

        # Security flags
        critical_flags = [f for f in security_flags if f['severity'] == 'critical']
        if critical_flags:
            recommendations.append(
                f"⛔ {len(critical_flags)} CRITICAL security flags require immediate investigation. "
                f"Consider temporary suspension of flagged accounts pending review."
            )

        if not recommendations:
            recommendations.append(
                "✅ No significant abuse patterns detected. Continue monitoring with current thresholds."
            )

        return recommendations
