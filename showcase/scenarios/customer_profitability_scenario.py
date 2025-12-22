"""
Customer Profitability Scenario

Demonstrates how to use Revenium to identify unprofitable customers
and optimize pricing strategy.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from analyzers.common import load_calls_from_csv, group_by, aggregate_metrics


def analyze_customer_profitability(csv_path: str):
    """Identify customers where AI costs exceed subscription revenue.

    Args:
        csv_path: Path to AI call data
    """
    print("=" * 80)
    print("CUSTOMER PROFITABILITY ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    calls = load_calls_from_csv(csv_path)
    print(f"Loaded {len(calls):,} AI calls")
    print()

    # Group by customer
    customer_groups = group_by(calls, 'customer_id')

    unprofitable_customers = []

    for (customer_id,), customer_calls in customer_groups.items():
        # Get customer details
        tier = customer_calls[0]['subscription_tier']
        tier_price = customer_calls[0]['tier_price_usd']

        # Calculate costs
        metrics = aggregate_metrics(customer_calls)
        total_cost = metrics['total_cost']

        # Calculate margin
        margin = tier_price - total_cost
        margin_pct = (margin / tier_price) * 100 if tier_price > 0 else 0

        # Identify unprofitable (cost > 80% of revenue)
        if total_cost > (tier_price * 0.8):
            unprofitable_customers.append({
                'customer_id': customer_id,
                'tier': tier,
                'tier_price': tier_price,
                'total_cost': total_cost,
                'margin': margin,
                'margin_pct': margin_pct,
                'call_count': metrics['call_count'],
                'risk_level': 'HIGH' if margin < 0 else 'MEDIUM'
            })

    # Sort by margin (lowest first)
    unprofitable_customers.sort(key=lambda x: x['margin'])

    # Display results
    print(f"Found {len(unprofitable_customers)} at-risk customers")
    print()
    print("TOP 10 AT-RISK CUSTOMERS:")
    print("-" * 80)
    print(f"{'Customer':<15} {'Tier':<10} {'Revenue':<12} {'Cost':<12} {'Margin':<12} {'Risk'}")
    print("-" * 80)

    for cust in unprofitable_customers[:10]:
        print(f"{cust['customer_id']:<15} "
              f"{cust['tier']:<10} "
              f"${cust['tier_price']:<11.2f} "
              f"${cust['total_cost']:<11.2f} "
              f"${cust['margin']:<11.2f} "
              f"{cust['risk_level']}")

    print("-" * 80)

    # Calculate total at-risk revenue
    total_at_risk = sum(c['tier_price'] for c in unprofitable_customers)
    total_cost_at_risk = sum(c['total_cost'] for c in unprofitable_customers)
    monthly_loss = total_cost_at_risk - total_at_risk

    print()
    print("FINANCIAL IMPACT:")
    print(f"  At-risk revenue:     ${total_at_risk:,.2f}/month")
    print(f"  Actual costs:        ${total_cost_at_risk:,.2f}/month")
    print(f"  Monthly shortfall:   ${monthly_loss:,.2f}/month")
    print()

    # Recommendations
    print("RECOMMENDED ACTIONS:")
    print()

    # Action 1: Tier upgrades
    starter_at_risk = [c for c in unprofitable_customers if c['tier'] == 'starter']
    if starter_at_risk:
        print(f"1. Upgrade {len(starter_at_risk)} Starter customers to Pro tier")
        print(f"   - Current revenue: ${sum(c['tier_price'] for c in starter_at_risk):,.2f}")
        print(f"   - Potential revenue at Pro ($99): ${len(starter_at_risk) * 99:,.2f}")
        print(f"   - Additional revenue: ${(len(starter_at_risk) * 99) - sum(c['tier_price'] for c in starter_at_risk):,.2f}/month")
        print()

    # Action 2: Usage-based pricing
    high_usage = [c for c in unprofitable_customers if c['call_count'] > 1000]
    if high_usage:
        print(f"2. Implement usage-based pricing for {len(high_usage)} high-volume customers")
        print(f"   - Average calls: {sum(c['call_count'] for c in high_usage) / len(high_usage):,.0f}/month")
        print(f"   - Add per-call fee of $0.01 to recover costs")
        print()

    # Action 3: Cost optimization
    print(f"3. Optimize AI model selection for unprofitable customers")
    print(f"   - Switch to more efficient models (Claude Haiku, GPT-4o-mini)")
    print(f"   - Potential cost reduction: 50-70%")
    print()

    print("=" * 80)


if __name__ == '__main__':
    # Use test data if exists, otherwise provide instructions
    csv_path = '../../src/data/test_calls.csv'

    if not os.path.exists(csv_path):
        csv_path = '../../src/data/simulated_calls.csv'

    if not os.path.exists(csv_path):
        print("No data found. Generate data first:")
        print("  cd ../../src")
        print("  python3 run_all_simulators.py")
    else:
        analyze_customer_profitability(csv_path)
