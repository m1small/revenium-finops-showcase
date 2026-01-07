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
from pathlib import Path

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

REQUIRED_FILES = [
    'index.html',
    'manifest.json',
]

REPORT_DIR = 'reports/html'


def check_file_exists(filepath):
    """Check if a file exists and return its size."""
    if not os.path.exists(filepath):
        return False, 0
    return True, os.path.getsize(filepath)


def verify_html_file(filepath):
    """Verify that an HTML file is valid and contains required elements."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for basic HTML structure
        required_tags = ['<!DOCTYPE html>', '<html>', '<head>', '<body>', '</html>']
        missing_tags = [tag for tag in required_tags if tag.lower() not in content.lower()]

        if missing_tags:
            return False, f"Missing tags: {', '.join(missing_tags)}"

        return True, "Valid HTML"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_manifest(filepath):
    """Verify that manifest.json is valid JSON with required fields."""
    try:
        with open(filepath, 'r') as f:
            manifest = json.load(f)

        required_fields = ['generated_at', 'call_count', 'data_size_mb']
        missing_fields = [field for field in required_fields if field not in manifest]

        if missing_fields:
            return False, f"Missing fields: {', '.join(missing_fields)}"

        return True, f"Valid manifest: {manifest['call_count']:,} calls, {manifest['data_size_mb']} MB"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def verify_index_has_executive_summary(filepath):
    """Verify that index.html contains the Executive Summary section."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for Executive Summary indicators
        indicators = [
            'Executive Summary',
            'insight-card',
            'Starter Tier Paradox',
            'Portfolio Misallocation',
            'Free-Tier-to-Paid Conversion',
            'starterTierChart',
            'portfolioChart',
            'freeTierChart',
        ]

        missing_indicators = [ind for ind in indicators if ind not in content]

        if missing_indicators:
            return False, f"Missing Executive Summary elements: {', '.join(missing_indicators)}"

        return True, "Contains Executive Summary with 3 insights and charts"
    except Exception as e:
        return False, f"Error reading file: {e}"


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

    # Track results
    all_passed = True

    # Check all 13 reports
    print("Checking Reports (13 expected):")
    print("-" * 80)
    for report_file in EXPECTED_REPORTS:
        filepath = os.path.join(REPORT_DIR, report_file)
        exists, size = check_file_exists(filepath)

        if not exists:
            print(f"✗ {report_file:40s} NOT FOUND")
            all_passed = False
        else:
            size_kb = size / 1024
            is_valid, message = verify_html_file(filepath)
            status = "✓" if is_valid else "✗"
            print(f"{status} {report_file:40s} {size_kb:>8.1f} KB - {message}")
            if not is_valid:
                all_passed = False

    print()

    # Check required files
    print("Checking Required Files:")
    print("-" * 80)

    # Check index.html
    index_path = os.path.join(REPORT_DIR, 'index.html')
    exists, size = check_file_exists(index_path)
    if not exists:
        print(f"✗ index.html                                  NOT FOUND")
        all_passed = False
    else:
        size_kb = size / 1024
        is_valid, message = verify_html_file(index_path)
        if is_valid:
            has_summary, summary_msg = verify_index_has_executive_summary(index_path)
            status = "✓" if has_summary else "✗"
            print(f"{status} index.html                             {size_kb:>8.1f} KB - {summary_msg}")
            if not has_summary:
                all_passed = False
        else:
            print(f"✗ index.html                             {size_kb:>8.1f} KB - {message}")
            all_passed = False

    # Check manifest.json
    manifest_path = os.path.join(REPORT_DIR, 'manifest.json')
    exists, size = check_file_exists(manifest_path)
    if not exists:
        print(f"✗ manifest.json                               NOT FOUND")
        all_passed = False
    else:
        size_kb = size / 1024
        is_valid, message = verify_manifest(manifest_path)
        status = "✓" if is_valid else "✗"
        print(f"{status} manifest.json                          {size_kb:>8.1f} KB - {message}")
        if not is_valid:
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print()
        print("Ready for deployment!")
        print("Next steps:")
        print("  1. Review changes: git diff reports/html/")
        print("  2. Commit:         git add reports/html/ && git commit -m 'Update reports'")
        print("  3. Deploy:         git push")
        print()
        sys.exit(0)
    else:
        print("✗ SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before deploying.")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
