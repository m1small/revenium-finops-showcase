#!/usr/bin/env python3
"""
Run Individual Analyzer

Module for running a single analyzer and generating its HTML report.
Used by the Viewer UI to regenerate individual reports on demand.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Import analyzers
from analyzers.finops.understanding import UnderstandingAnalyzer
from analyzers.finops.performance import PerformanceAnalyzer
from analyzers.finops.realtime import RealtimeAnalyzer
from analyzers.finops.optimization import OptimizationAnalyzer
from analyzers.finops.alignment import AlignmentAnalyzer
from analyzers.ubr.profitability import CustomerProfitabilityAnalyzer
from analyzers.ubr.pricing import PricingStrategyAnalyzer
from analyzers.ubr.features import FeatureEconomicsAnalyzer
from analyzers.dataset_overview import DatasetOverviewAnalyzer
from analyzers.token_economics import TokenEconomicsAnalyzer
from analyzers.geographic_latency import GeographicLatencyAnalyzer
from analyzers.churn_growth import ChurnGrowthAnalyzer
from analyzers.abuse_detection import AbuseDetectionAnalyzer

from generators import (
    generate_understanding_report, generate_performance_report,
    generate_realtime_report, generate_optimization_report,
    generate_alignment_report, generate_profitability_report,
    generate_pricing_report, generate_features_report
)
from generators.overview_generator import generate_overview_report
from generators.token_economics_generator import generate_token_economics_report
from generators.geographic_latency_generator import generate_geographic_latency_report
from generators.churn_growth_generator import generate_churn_growth_report
from generators.abuse_detection_generator import generate_abuse_detection_report


# Registry of all available analyzers
ANALYZER_REGISTRY = {
    'understanding': {
        'name': 'Understanding Usage & Cost',
        'filename': 'understanding.html',
        'description': 'Cost allocation, forecasting, and efficiency analysis',
        'analyzer_class': UnderstandingAnalyzer,
        'html_generator': generate_understanding_report
    },
    'performance': {
        'name': 'Performance Tracking',
        'filename': 'performance.html',
        'description': 'Model efficiency, latency percentiles, SLA compliance',
        'analyzer_class': PerformanceAnalyzer,
        'html_generator': generate_performance_report
    },
    'realtime': {
        'name': 'Real-Time Decision Making',
        'filename': 'realtime.html',
        'description': 'Anomaly detection, threshold alerts, portfolio risk',
        'analyzer_class': RealtimeAnalyzer,
        'html_generator': generate_realtime_report
    },
    'optimization': {
        'name': 'Rate Optimization',
        'filename': 'optimization.html',
        'description': 'Reserved capacity, model switching opportunities',
        'analyzer_class': OptimizationAnalyzer,
        'html_generator': generate_optimization_report
    },
    'alignment': {
        'name': 'Organizational Alignment',
        'filename': 'alignment.html',
        'description': 'Multi-tenant tracking, chargeback/showback',
        'analyzer_class': AlignmentAnalyzer,
        'html_generator': generate_alignment_report
    },
    'profitability': {
        'name': 'Customer Profitability',
        'filename': 'profitability.html',
        'description': 'Margin analysis, unprofitable customer detection',
        'analyzer_class': CustomerProfitabilityAnalyzer,
        'html_generator': generate_profitability_report
    },
    'pricing': {
        'name': 'Pricing Strategy',
        'filename': 'pricing.html',
        'description': '4 pricing model comparisons, revenue projections',
        'analyzer_class': PricingStrategyAnalyzer,
        'html_generator': generate_pricing_report
    },
    'features': {
        'name': 'Feature Economics',
        'filename': 'features.html',
        'description': 'Feature profitability, investment recommendations',
        'analyzer_class': FeatureEconomicsAnalyzer,
        'html_generator': generate_features_report
    },
    'dataset_overview': {
        'name': 'Dataset Overview',
        'filename': 'dataset_overview.html',
        'description': 'Comprehensive dataset statistics and analysis',
        'analyzer_class': DatasetOverviewAnalyzer,
        'html_generator': generate_overview_report
    },
    'token_economics': {
        'name': 'Token Economics',
        'filename': 'token_economics.html',
        'description': 'Token usage patterns and cost efficiency analysis',
        'analyzer_class': TokenEconomicsAnalyzer,
        'html_generator': generate_token_economics_report
    },
    'geographic_latency': {
        'name': 'Geographic Latency',
        'filename': 'geographic_latency.html',
        'description': 'Regional performance and latency analysis',
        'analyzer_class': GeographicLatencyAnalyzer,
        'html_generator': generate_geographic_latency_report
    },
    'churn_growth': {
        'name': 'Churn & Growth',
        'filename': 'churn_growth.html',
        'description': 'Customer lifecycle patterns and growth trends',
        'analyzer_class': ChurnGrowthAnalyzer,
        'html_generator': generate_churn_growth_report
    },
    'abuse_detection': {
        'name': 'Abuse Detection',
        'filename': 'abuse_detection.html',
        'description': 'Anomaly and abuse pattern detection',
        'analyzer_class': AbuseDetectionAnalyzer,
        'html_generator': generate_abuse_detection_report
    }
}


def run_analyzer(analyzer_id: str, csv_path: str = 'data/simulated_calls.csv',
                 report_dir: str = 'reports/html') -> Dict[str, Any]:
    """Run a single analyzer and generate its HTML report.

    Args:
        analyzer_id: ID of the analyzer to run (e.g., 'understanding', 'performance')
        csv_path: Path to the CSV file containing call data
        report_dir: Directory where HTML reports should be saved

    Returns:
        Dict with status and result information

    Raises:
        ValueError: If analyzer_id is not recognized
        FileNotFoundError: If CSV file doesn't exist
    """
    # Validate analyzer ID
    if analyzer_id not in ANALYZER_REGISTRY:
        raise ValueError(f"Unknown analyzer: {analyzer_id}. Valid options: {', '.join(ANALYZER_REGISTRY.keys())}")

    # Check CSV exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Get analyzer configuration
    config = ANALYZER_REGISTRY[analyzer_id]

    # Build output path
    output_path = os.path.join(report_dir, config['filename'])

    try:
        # Initialize and run analyzer
        print(f"Running {config['name']}...")
        analyzer = config['analyzer_class'](csv_path)
        results = analyzer.analyze()

        # Generate HTML report
        print(f"Generating report: {output_path}")
        config['html_generator'](results, output_path)

        # Get file size
        file_size_kb = os.path.getsize(output_path) / 1024

        return {
            'success': True,
            'analyzer_id': analyzer_id,
            'name': config['name'],
            'filename': config['filename'],
            'output_path': output_path,
            'size_kb': round(file_size_kb, 2),
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        return {
            'success': False,
            'analyzer_id': analyzer_id,
            'name': config['name'],
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def list_analyzers() -> Dict[str, Dict[str, str]]:
    """Get a list of all available analyzers.

    Returns:
        Dict mapping analyzer IDs to their metadata
    """
    return {
        analyzer_id: {
            'name': config['name'],
            'filename': config['filename'],
            'description': config['description']
        }
        for analyzer_id, config in ANALYZER_REGISTRY.items()
    }


def main():
    """CLI interface for running individual analyzers."""
    if len(sys.argv) < 2:
        print("Usage: python run_analyzer.py <analyzer_id> [csv_path] [report_dir]")
        print()
        print("Available analyzers:")
        for analyzer_id, info in list_analyzers().items():
            print(f"  {analyzer_id:15} - {info['name']}")
        print()
        print("Examples:")
        print("  python run_analyzer.py understanding")
        print("  python run_analyzer.py performance data/calls.csv reports/html")
        sys.exit(1)

    analyzer_id = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else 'data/simulated_calls.csv'
    report_dir = sys.argv[3] if len(sys.argv) > 3 else 'reports/html'

    result = run_analyzer(analyzer_id, csv_path, report_dir)

    if result['success']:
        print(f"✓ Success: {result['filename']} ({result['size_kb']:.1f} KB)")
        print(f"  Path: {result['output_path']}")
    else:
        print(f"✗ Error: {result['error']}")
        print()
        print(result['traceback'])
        sys.exit(1)


if __name__ == '__main__':
    main()
