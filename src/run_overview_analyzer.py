#!/usr/bin/env python3
"""
Standalone runner for Dataset Overview Analyzer.

Usage:
    python run_overview_analyzer.py [csv_path] [output_dir]

Examples:
    python run_overview_analyzer.py
    python run_overview_analyzer.py data/simulated_calls.csv
    python run_overview_analyzer.py data/simulated_calls.csv reports/html
"""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from analyzers.dataset_overview import DatasetOverviewAnalyzer
from generators.overview_generator import generate_overview_report


def main():
    """Run the dataset overview analyzer and generate report."""
    # Parse arguments
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'data/simulated_calls.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'reports/html'

    # Check if CSV exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        print("Please provide a valid path to the simulated_calls.csv file.")
        sys.exit(1)

    print("=" * 80)
    print("DATASET OVERVIEW ANALYZER")
    print("=" * 80)
    print(f"\nInput CSV: {csv_path}")
    print(f"Output Directory: {output_dir}")
    print(f"Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run analyzer
    print("Loading and analyzing dataset...")
    analyzer = DatasetOverviewAnalyzer(csv_path)
    results = analyzer.analyze()

    # Display summary to console
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS SUMMARY")
    print("=" * 80)

    file_info = results['file_info']
    summary = results['summary']
    scale = results['scale_metrics']
    quality = results['quality_metrics']

    print(f"\nFile Information:")
    print(f"  • File Size: {file_info['file_size_gb']} GB")
    print(f"  • Total Records: {file_info['total_records']:,}")

    print(f"\nKey Metrics:")
    print(f"  • Total API Calls: {summary['total_calls']:,}")
    print(f"  • Total Cost: ${summary['total_cost']:,.2f}")
    print(f"  • Total Tokens: {summary['total_tokens']:,}")
    print(f"  • Avg Cost per Call: ${summary['avg_cost_per_call']:.6f}")
    print(f"  • Avg Latency: {summary['avg_latency_ms']:.0f} ms")

    print(f"\nScale Metrics:")
    print(f"  • Organizations: {scale['unique_organizations']:,}")
    print(f"  • Customers: {scale['unique_customers']:,}")
    print(f"  • Products: {scale['unique_products']:,}")
    print(f"  • Features: {scale['unique_features']:,}")

    print(f"\nQuality Metrics:")
    print(f"  • Success Rate: {quality['success_rate_percentage']:.2f}%")
    print(f"  • Error Count: {quality['error_count']:,}")

    # Generate HTML report
    print("\n" + "=" * 80)
    print("GENERATING HTML REPORT")
    print("=" * 80)

    output_path = os.path.join(output_dir, 'dataset_overview.html')
    generate_overview_report(results, output_path)

    print(f"\n✓ Report generated successfully!")
    print(f"  Location: {output_path}")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
