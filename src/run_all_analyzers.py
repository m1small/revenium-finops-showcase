#!/usr/bin/env python3
"""
Run All Analyzers
Executes all FinOps and UBR analyzers and generates comprehensive reports
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import analyzers
from analyzers.finops.understanding import UnderstandingAnalyzer
from analyzers.finops.performance import PerformanceAnalyzer
from analyzers.finops.realtime import RealtimeAnalyzer
from analyzers.finops.optimization import OptimizationAnalyzer
from analyzers.finops.alignment import AlignmentAnalyzer
from analyzers.ubr.profitability import CustomerProfitabilityAnalyzer
from analyzers.ubr.pricing import PricingAnalyzer
from analyzers.ubr.features import FeatureAnalyzer


def ensure_data_exists():
    """Ensure simulated data exists, generate if not"""
    data_file = 'data/simulated_calls.csv'
    
    if not os.path.exists(data_file):
        print("📊 No data found. Generating simulated data...")
        from simulator.core import AICallSimulator
        simulator = AICallSimulator(num_customers=100, num_days=30, seed=42)
        simulator.save_to_csv(data_file)
        print()
    else:
        print(f"✅ Found existing data: {data_file}\n")


def run_all_analyzers():
    """Run all analyzers and generate reports"""
    print("=" * 70)
    print("🚀 REVENIUM FINOPS SHOWCASE - RUNNING ALL ANALYZERS")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    # Ensure data exists
    ensure_data_exists()
    
    # List of analyzers to run
    analyzers = [
        ("FinOps: Understanding Usage & Cost", UnderstandingAnalyzer),
        ("FinOps: Performance Tracking", PerformanceAnalyzer),
        ("FinOps: Real-Time Decision Making", RealtimeAnalyzer),
        ("FinOps: Rate Optimization", OptimizationAnalyzer),
        ("FinOps: Organizational Alignment", AlignmentAnalyzer),
        ("UBR: Customer Profitability", CustomerProfitabilityAnalyzer),
        ("UBR: Pricing Strategy", PricingAnalyzer),
        ("UBR: Feature Economics", FeatureAnalyzer),
    ]
    
    results = []
    
    for name, AnalyzerClass in analyzers:
        print(f"📊 Running: {name}")
        print("-" * 70)
        
        try:
            analyzer = AnalyzerClass()
            output_file = analyzer.generate_html_report()
            results.append({
                'name': name,
                'status': 'success',
                'output': output_file
            })
            print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'name': name,
                'status': 'error',
                'error': str(e)
            })
            print()
    
    # Generate manifest
    generate_manifest(results)
    
    # Summary
    elapsed = time.time() - start_time
    print("=" * 70)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print(f"⏱️  Total time: {elapsed:.2f} seconds")
    print(f"✅ Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"❌ Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print()
    print("📁 Reports generated in: reports/html/")
    print()
    print("🌐 To view reports, run:")
    print("   cd ../viewer")
    print("   python3 serve.py")
    print("   Then open: http://localhost:8000")
    print()


def generate_manifest(results):
    """Generate manifest file for web viewer"""
    import json
    
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'reports': []
    }
    
    for result in results:
        if result['status'] == 'success':
            # Extract filename from path
            filename = os.path.basename(result['output'])
            
            # Determine category
            if 'finops' in filename:
                category = 'FinOps Domains'
            elif 'customer' in filename or 'pricing' in filename or 'feature' in filename:
                category = 'Usage-Based Revenue'
            else:
                category = 'Other'
            
            manifest['reports'].append({
                'title': result['name'],
                'filename': filename,
                'category': category,
                'path': result['output']
            })
    
    manifest_path = 'reports/html/manifest.json'
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Generated manifest: {manifest_path}")


if __name__ == '__main__':
    run_all_analyzers()
