#!/usr/bin/env python3
"""
Run All Simulators
Executes all traffic pattern simulators to generate comprehensive dataset
"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def clear_existing_data():
    """Clear existing CSV data"""
    csv_file = 'data/simulated_calls.csv'
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"🗑️  Cleared existing data: {csv_file}\n")


def run_all_simulators():
    """Run all simulators in sequence"""
    print("=" * 70)
    print("🚀 RUNNING ALL TRAFFIC PATTERN SIMULATORS")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    # Clear existing data
    clear_existing_data()
    
    simulators = [
        ("Base Traffic Pattern", "simulator.core"),
        ("Seasonal Pattern", "simulator.scenarios.seasonal_pattern"),
        ("Burst Traffic", "simulator.scenarios.burst_traffic"),
        ("Gradual Decline", "simulator.scenarios.gradual_decline"),
    ]
    
    results = []
    
    for name, module_path in simulators:
        print(f"📊 Running: {name}")
        print("-" * 70)
        
        try:
            # Import and run the module
            module = __import__(module_path, fromlist=['main'])
            module.main()
            results.append({'name': name, 'status': 'success'})
            print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({'name': name, 'status': 'error', 'error': str(e)})
            print()
    
    # Summary
    elapsed = time.time() - start_time
    print("=" * 70)
    print("📊 SIMULATION COMPLETE")
    print("=" * 70)
    print()
    print(f"⏱️  Total time: {elapsed:.2f} seconds")
    print(f"✅ Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"❌ Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print()
    
    # Show combined statistics
    csv_file = 'data/simulated_calls.csv'
    if os.path.exists(csv_file):
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            calls = list(reader)
        
        total_calls = len(calls)
        total_cost = sum(float(c['cost_usd']) for c in calls)
        total_tokens = sum(int(c['input_tokens']) + int(c['output_tokens']) for c in calls)
        
        # Count unique customers
        unique_customers = len(set(c['customer_id'] for c in calls))
        
        print("📈 Combined Dataset Statistics:")
        print(f"   Total Calls: {total_calls:,}")
        print(f"   Unique Customers: {unique_customers}")
        print(f"   Total Cost: ${total_cost:,.2f}")
        print(f"   Total Tokens: {total_tokens:,}")
        print(f"   Avg Cost/Call: ${total_cost/total_calls:.4f}")
        print()
    
    print("📁 Data saved to: data/simulated_calls.csv")
    print()
    print("🔄 Next steps:")
    print("   1. Run analyzers: python3 run_all_analyzers.py")
    print("   2. View reports: cd ../viewer && python3 serve.py")
    print()


if __name__ == '__main__':
    run_all_simulators()
