#!/usr/bin/env python3
"""
Master script to run all FinOps and UBR analyzers
"""

import os
import sys
from datetime import datetime

# Set environment variable to enable HTML generation
os.environ['GENERATE_HTML'] = '1'


def run_analyzer(script_path: str, name: str) -> bool:
    """Run an analyzer script and report status"""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")
    
    try:
        # Import and run the analyzer
        if 'finops' in script_path:
            if 'understanding' in script_path:
                from analyzers.finops.understanding import main
            elif 'performance' in script_path:
                from analyzers.finops.performance import main
            elif 'realtime' in script_path:
                from analyzers.finops.realtime import main
            elif 'optimization' in script_path:
                from analyzers.finops.optimization import main
            elif 'alignment' in script_path:
                from analyzers.finops.alignment import main
        elif 'ubr' in script_path:
            if 'profitability' in script_path:
                from analyzers.ubr.profitability import main
            elif 'pricing' in script_path:
                from analyzers.ubr.pricing import main
            elif 'features' in script_path:
                from analyzers.ubr.features import main
        
        main()
        return True
    except Exception as e:
        print(f"❌ Error running {name}: {e}")
        return False


def main():
    """Run all analyzers in sequence"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         Revenium FinOps Showcase - Analysis Suite           ║
╚══════════════════════════════════════════════════════════════╝

Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # Check if data file exists
    if not os.path.exists('data/simulated_calls.csv'):
        print("❌ Error: data/simulated_calls.csv not found!")
        print("Please run simulator.py first to generate data.")
        sys.exit(1)
    
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    
    # Define analyzers to run
    analyzers = [
        ('analyzers/finops/understanding.py', 'FinOps: Understanding Usage & Cost'),
        ('analyzers/finops/performance.py', 'FinOps: Performance Tracking'),
        ('analyzers/finops/realtime.py', 'FinOps: Real-Time Decision Making'),
        ('analyzers/finops/optimization.py', 'FinOps: Rate Optimization'),
        ('analyzers/finops/alignment.py', 'FinOps: Organizational Alignment'),
        ('analyzers/ubr/profitability.py', 'UBR: Customer Profitability'),
        ('analyzers/ubr/pricing.py', 'UBR: Pricing Strategy'),
        ('analyzers/ubr/features.py', 'UBR: Feature Economics'),
    ]
    
    # Run all analyzers
    results = []
    for script_path, name in analyzers:
        success = run_analyzer(script_path, name)
        results.append((name, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}\n")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Results: {successful}/{total} analyzers completed successfully\n")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print("Generated Reports:")
    print(f"{'='*60}\n")
    
    reports = [
        'reports/finops_understanding.md',
        'reports/finops_performance.md',
        'reports/finops_realtime.md',
        'reports/finops_optimization.md',
        'reports/finops_alignment.md',
        'reports/customer_profitability.md',
        'reports/pricing_strategy.md',
        'reports/feature_economics.md'
    ]
    
    for report in reports:
        if os.path.exists(report):
            size = os.path.getsize(report)
            print(f"✓ {report} ({size:,} bytes)")
        else:
            print(f"✗ {report} (not found)")
    
    # Generate HTML reports list
    html_reports = [
        'reports/html/finops_understanding.html',
        'reports/html/finops_performance.html',
        'reports/html/finops_realtime.html',
        'reports/html/finops_optimization.html',
        'reports/html/finops_alignment.html',
        'reports/html/customer_profitability.html',
        'reports/html/pricing_strategy.html',
        'reports/html/feature_economics.html'
    ]
    
    print(f"\n{'='*60}")
    print("HTML Reports:")
    print(f"{'='*60}\n")
    
    for report in html_reports:
        if os.path.exists(report):
            size = os.path.getsize(report)
            print(f"✓ {report} ({size:,} bytes)")
        else:
            print(f"✗ {report} (not found)")
    
    # Generate manifest
    print(f"\n{'='*60}")
    print("Generating Manifest:")
    print(f"{'='*60}\n")
    
    try:
        from utils.manifest_generator import create_default_manifest
        manifest = create_default_manifest()
        manifest.save()
    except Exception as e:
        print(f"⚠️  Warning: Could not generate manifest: {e}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎉 All analyses complete!")
    print("\n📊 Markdown reports: reports/")
    print("🌐 HTML reports: reports/html/")
    print("\nTo view HTML reports:")
    print("  cd viewer")
    print("  python serve.py")
    print("  Open http://localhost:8000/\n")


if __name__ == '__main__':
    main()
