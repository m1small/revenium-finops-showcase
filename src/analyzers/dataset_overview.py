"""Dataset Overview Analyzer - Comprehensive dataset statistics and analysis."""

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


class DatasetOverviewAnalyzer:
    """Analyzes dataset for comprehensive overview statistics."""

    def __init__(self, csv_path: str):
        """Initialize analyzer with CSV data."""
        self.csv_path = csv_path
        self.calls = load_calls_from_csv(csv_path)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        return {
            'file_info': self._analyze_file_info(),
            'summary': self._generate_summary(),
            'scale_metrics': self._analyze_scale_metrics(),
            'provider_distribution': self._analyze_provider_distribution(),
            'model_distribution': self._analyze_model_distribution(),
            'feature_usage': self._analyze_feature_usage(),
            'subscription_tiers': self._analyze_subscription_tiers(),
            'customer_archetypes': self._analyze_customer_archetypes(),
            'regional_distribution': self._analyze_regional_distribution(),
            'product_distribution': self._analyze_product_distribution(),
            'temporal_analysis': self._analyze_temporal_range(),
            'quality_metrics': self._analyze_quality_metrics(),
            'recommendations': self._generate_recommendations()
        }

    def _analyze_file_info(self) -> Dict[str, Any]:
        """Analyze basic file information."""
        file_size = os.path.getsize(self.csv_path)
        file_size_gb = file_size / (1024**3)

        return {
            'file_path': self.csv_path,
            'file_size_bytes': file_size,
            'file_size_gb': round(file_size_gb, 2),
            'total_records': len(self.calls),
            'analysis_timestamp': datetime.now().isoformat()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary statistics."""
        total_metrics = aggregate_metrics(self.calls)

        return {
            'total_calls': total_metrics['call_count'],
            'total_cost': total_metrics['total_cost'],
            'total_tokens': total_metrics['total_tokens'],
            'total_input_tokens': total_metrics['total_input_tokens'],
            'total_output_tokens': total_metrics['total_output_tokens'],
            'avg_cost_per_call': total_metrics['avg_cost_per_call'],
            'avg_tokens_per_call': total_metrics['avg_tokens_per_call'],
            'avg_latency_ms': total_metrics['avg_latency_ms'],
            'p50_latency_ms': total_metrics['p50_latency_ms'],
            'p95_latency_ms': total_metrics['p95_latency_ms'],
            'p99_latency_ms': total_metrics['p99_latency_ms']
        }

    def _analyze_scale_metrics(self) -> Dict[str, Any]:
        """Analyze unique counts and scale metrics."""
        unique_orgs = len(set(c['organization_id'] for c in self.calls))
        unique_customers = len(set(c['customer_id'] for c in self.calls))
        unique_products = len(set(c['product_id'] for c in self.calls))
        unique_features = len(set(c['feature_id'] for c in self.calls))

        return {
            'unique_organizations': unique_orgs,
            'unique_customers': unique_customers,
            'unique_products': unique_products,
            'unique_features': unique_features
        }

    def _analyze_provider_distribution(self) -> List[Dict[str, Any]]:
        """Analyze distribution across providers."""
        provider_groups = group_by(self.calls, 'provider')

        results = []
        for (provider,), calls in provider_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'provider': provider,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost'],
                'total_tokens': metrics['total_tokens'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_model_distribution(self) -> List[Dict[str, Any]]:
        """Analyze distribution across models."""
        model_groups = group_by(self.calls, 'model')

        results = []
        for (model,), calls in model_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'model': model,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost'],
                'avg_latency_ms': metrics['avg_latency_ms']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_feature_usage(self) -> List[Dict[str, Any]]:
        """Analyze feature usage distribution."""
        feature_groups = group_by(self.calls, 'feature_id')

        results = []
        for (feature,), calls in feature_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'feature': feature,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost'],
                'avg_tokens_per_call': metrics['avg_tokens_per_call']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_subscription_tiers(self) -> List[Dict[str, Any]]:
        """Analyze subscription tier distribution."""
        tier_groups = group_by(self.calls, 'subscription_tier', 'tier_price_usd')

        results = []
        for (tier, price), calls in tier_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'tier': tier,
                'price_usd': price,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_customer_archetypes(self) -> List[Dict[str, Any]]:
        """Analyze customer archetype distribution."""
        archetype_groups = group_by(self.calls, 'customer_archetype')

        results = []
        for (archetype,), calls in archetype_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'archetype': archetype,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'avg_tokens_per_call': metrics['avg_tokens_per_call'],
                'avg_cost_per_call': metrics['avg_cost_per_call']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_regional_distribution(self) -> List[Dict[str, Any]]:
        """Analyze regional distribution."""
        region_groups = group_by(self.calls, 'region')

        results = []
        for (region,), calls in region_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'region': region,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'avg_latency_ms': metrics['avg_latency_ms']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_product_distribution(self) -> List[Dict[str, Any]]:
        """Analyze product distribution."""
        product_groups = group_by(self.calls, 'product_id')

        results = []
        for (product,), calls in product_groups.items():
            metrics = aggregate_metrics(calls)
            results.append({
                'product': product,
                'call_count': metrics['call_count'],
                'percentage': (metrics['call_count'] / len(self.calls)) * 100,
                'total_cost': metrics['total_cost']
            })

        # Sort by call count descending
        results.sort(key=lambda x: x['call_count'], reverse=True)
        return results

    def _analyze_temporal_range(self) -> Dict[str, Any]:
        """Analyze temporal range of the dataset."""
        if not self.calls:
            return {
                'start_time': None,
                'end_time': None,
                'duration_hours': 0,
                'duration_description': 'No data'
            }

        timestamps = [c['timestamp'] for c in self.calls]
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time
        duration_hours = duration.total_seconds() / 3600

        # Create human-readable duration description
        if duration_hours < 1:
            duration_desc = f"{int(duration.total_seconds() / 60)} minutes"
        elif duration_hours < 24:
            duration_desc = f"{duration_hours:.1f} hours"
        else:
            duration_desc = f"{duration_hours / 24:.1f} days"

        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_hours': round(duration_hours, 2),
            'duration_description': duration_desc
        }

    def _analyze_quality_metrics(self) -> Dict[str, Any]:
        """Analyze data quality metrics."""
        # Count status distribution
        status_counts = defaultdict(int)
        for call in self.calls:
            status_counts[call['status']] += 1

        success_count = status_counts.get('success', 0)
        total_count = len(self.calls)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        return {
            'total_records': total_count,
            'success_count': success_count,
            'error_count': total_count - success_count,
            'success_rate_percentage': round(success_rate, 2),
            'status_distribution': dict(status_counts)
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on dataset analysis."""
        recommendations = []

        # Analyze provider diversity
        providers = self._analyze_provider_distribution()
        if providers and providers[0]['percentage'] > 60:
            recommendations.append(
                f"Provider concentration risk: {providers[0]['provider']} accounts for "
                f"{providers[0]['percentage']:.1f}% of calls. Consider diversifying across providers "
                f"to reduce vendor lock-in and improve resilience."
            )

        # Analyze regional distribution
        regions = self._analyze_regional_distribution()
        if regions:
            max_region_pct = max(r['percentage'] for r in regions)
            min_region_pct = min(r['percentage'] for r in regions)
            if max_region_pct - min_region_pct > 20:
                recommendations.append(
                    f"Uneven regional distribution detected (max: {max_region_pct:.1f}%, "
                    f"min: {min_region_pct:.1f}%). Consider load balancing strategies to "
                    f"distribute traffic more evenly."
                )

        # Analyze cost efficiency
        summary = self._generate_summary()
        if summary['avg_cost_per_call'] > 0.01:
            recommendations.append(
                f"Average cost per call is ${summary['avg_cost_per_call']:.6f}. "
                f"Review model selection for cost optimization opportunities, especially for "
                f"high-volume, low-complexity tasks."
            )

        # Analyze latency
        if summary['p99_latency_ms'] > 3000:
            recommendations.append(
                f"P99 latency is {summary['p99_latency_ms']}ms (>{summary['p99_latency_ms']/1000:.1f}s). "
                f"Investigate high-latency calls and consider performance optimizations or "
                f"faster model alternatives for time-sensitive use cases."
            )

        # Analyze feature balance
        features = self._analyze_feature_usage()
        if features:
            max_feature_pct = max(f['percentage'] for f in features)
            if max_feature_pct > 40:
                recommendations.append(
                    f"Feature usage is imbalanced with {features[0]['feature']} at "
                    f"{max_feature_pct:.1f}%. Consider whether product positioning matches "
                    f"actual usage patterns and adjust marketing/pricing accordingly."
                )

        # Analyze tier distribution
        tiers = self._analyze_subscription_tiers()
        if tiers and tiers[0]['tier'].lower() == 'starter':
            recommendations.append(
                f"Starter tier accounts for {tiers[0]['percentage']:.1f}% of usage. "
                f"Focus on conversion strategies to upgrade users to higher-margin "
                f"Pro and Enterprise tiers through feature gating and value demonstration."
            )

        if not recommendations:
            recommendations.append(
                "Dataset shows healthy distribution across all dimensions. Continue monitoring "
                "for changes in usage patterns and cost trends."
            )

        return recommendations
