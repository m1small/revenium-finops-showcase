#!/usr/bin/env python3
"""
Scenario: Unprofitable Customer Detection
Demonstrates how Revenium identifies customers costing more to serve than revenue
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from simulator.core import AICallSimulator
from analyzers.ubr.profitability import CustomerProfitabilityAnalyzer


def run_scenario():
    """Run the unprofitable customer scenario"""
    
    print("=" * 70)
    print("🎯 SCENARIO: UNPROFITABLE CUSTOMER DETECTION")
    print("=" * 70)
    print()
    
    print("📖 Business Problem:")
    print("   A SaaS company suspects some customers are unprofitable")
    print("   High AI usage on low-tier subscriptions is burning cash")
    print("   Need to identify and address these customers quickly")
    print()
    
    print("🔍 Revenium Solution:")
    print("   Track per-customer AI costs with customer_id metadata")
    print("   Compare costs against subscription revenue")
    print("   Generate real-time profitability alerts")
    print()
    
    input("Press Enter to generate simulation data...")
    print()
    
    # Generate simulation with some heavy users on starter tier
    print("📊 Generating 30 days of usage data...")
    simulator = AICallSimulator(num_customers=100, num_days=30, seed=42)
    
    # Add 15 heavy users on starter tier (unprofitable scenario)
    print("   Adding 15 high-usage customers on starter tier...")
    simulator.add_heavy_users(count=15, archetype='heavy')
    
    # Save data
    data_file = 'data/scenario_unprofitable.csv'
    simulator.save_to_csv(data_file)
    print()
    
    input("Press Enter to analyze profitability...")
    print()
    
    # Run profitability analysis
    print("📈 Running profitability analysis...")
    analyzer = CustomerProfitabilityAnalyzer(data_file)
    analysis = analyzer.analyze()
    
    # Display results
    print()
    print("=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    unprofitable = analysis['unprofitable']
    
    print(f"🚨 PROBLEM IDENTIFIED:")
    print(f"   Unprofitable Customers: {unprofitable['count']}")
    print(f"   Percentage: {unprofitable['percentage']:.1f}%")
    print(f"   Monthly Loss: ${unprofitable['total_loss']:,.2f}")
    print()
    
    print("📋 Top 5 Most Unprofitable Customers:")
    print("-" * 70)
    for i, customer in enumerate(unprofitable['customers'][:5], 1):
        print(f"{i}. {customer['customer_id']}")
        print(f"   Tier: {customer['tier']} (${customer['revenue']:.2f}/month)")
        print(f"   Cost: ${customer['cost']:.2f}/month")
        print(f"   Loss: ${abs(customer['margin']):.2f}/month")
        print(f"   Calls: {customer['calls']:,}")
        print()
    
    print("=" * 70)
    print("💡 RECOMMENDED ACTIONS")
    print("=" * 70)
    print()
    
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    print()
    
    print("✅ Specific Actions:")
    print("   1. Implement usage caps for starter tier")
    print("   2. Offer tier upgrades to heavy users")
    print("   3. Add overage charges for excess usage")
    print("   4. Set up real-time alerts for high-cost customers")
    print()
    
    # Calculate potential savings
    potential_savings = unprofitable['total_loss']
    print(f"💰 Potential Monthly Savings: ${potential_savings:,.2f}")
    print(f"💰 Annual Impact: ${potential_savings * 12:,.2f}")
    print()
    
    # Generate HTML report
    print("📄 Generating detailed HTML report...")
    report_file = analyzer.generate_html_report('reports/html/scenario_unprofitable.html')
    print()
    
    print("=" * 70)
    print("🎯 SCENARIO COMPLETE")
    print("=" * 70)
    print()
    print(f"📊 View detailed report: {report_file}")
    print()
    print("🔑 Key Takeaway:")
    print("   Revenium's customer_id metadata enables real-time profitability")
    print("   tracking, allowing you to identify and address unprofitable")
    print("   customers before they significantly impact your bottom line.")
    print()
    print("=" * 70)


if __name__ == '__main__':
    run_scenario()
