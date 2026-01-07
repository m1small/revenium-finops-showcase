#!/usr/bin/env python3
"""
Deployment Verification Script

This script verifies that all necessary files for GitHub Pages deployment exist
and are properly formatted.

Usage:
    python3 scripts/verify_deployment.py
"""

import os
import sys
import json

# Define expected files
EXPECTED_REPORTS = [
    'dataset_overview.html',
    'understanding.html',
    'performance.html',
    'realtime.html',
    'optimization.html',
    'alignment.html',
    'profitability.html',
    'pricing.html',
    'features.html',
    'token_economics.html',
    'geographic_latency.html',
    'churn_growth.html',
    'abuse_detection.html',
]

REPORT_DIR = 'reports/html'


def main():
    """Run deployment verification."""
    print("=" * 80)
    print("DEPLOYMENT VERIFICATION")
    print("=" * 80)
    print()

    # Check if report directory exists
    if not os.path.exists(REPORT_DIR):
        print(f"✗ ERROR: Report directory not found: {REPORT_DIR}")
        print("  Run 'python3 src/run_all_analyzers.py' first")
        sys.exit(1)

    print(f"Report directory: {REPORT_DIR}")
    print()

    all_passed = True

    # Check all 13 reports
    print("Checking Reports (13 expected):")
    print("-" * 80)
    for report_file in EXPECTED_REPORTS:
        filepath = os.path.join(REPORT_DIR, report_file)
        if not os.path.exists(filepath):
            print(f"✗ {report_file:40s} NOT FOUND")
            all_passed = False
        else:
            size_kb = os.path.getsize(filepath) / 1024
            print(f"✓ {report_file:40s} {size_kb:>8.1f} KB")

    print()

    # Check index.html
    index_path = os.path.join(REPORT_DIR, 'index.html')
    if not os.path.exists(index_path):
        print(f"✗ index.html NOT FOUND")
        all_passed = False
    else:
        size_kb = os.path.getsize(index_path) / 1024
        with open(index_path) as f:
            content = f.read()
        has_summary = 'Executive Summary' in content and 'starterTierChart' in content
        if has_summary:
            print(f"✓ index.html                             {size_kb:>8.1f} KB (with Executive Summary)")
        else:
            print(f"✗ index.html                             {size_kb:>8.1f} KB (missing Executive Summary)")
            all_passed = False

    # Check manifest.json
    manifest_path = os.path.join(REPORT_DIR, 'manifest.json')
    if not os.path.exists(manifest_path):
        print(f"✗ manifest.json NOT FOUND")
        all_passed = False
    else:
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"✓ manifest.json - {manifest['call_count']:,} calls, {manifest['data_size_mb']} MB")

    print()
    print("=" * 80)

    if all_passed:
        print("✓ ALL CHECKS PASSED - Ready for deployment!")
        sys.exit(0)
    else:
        print("✗ SOME CHECKS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
