#!/usr/bin/env python3
"""
Gradual Decline Simulator
Simulates decreasing usage over time (e.g., churn, feature deprecation, seasonal downturn)
"""

import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator
import datetime


class GradualDeclineSimulator(AICallSimulator):
    """Simulates gradual decline in usage patterns"""
    
    def __init__(self, num_customers: int = 40, num_days: int = 30, seed: int = None):
        """Initialize with decline pattern parameters"""
        super().__init__(num_customers, num_days, seed)
        self.pattern_name = "Gradual Decline"
        self.decline_rate = 0.03  # 3% decline per week (~0.43% per day)
        self.churn_probability = 0.02  # 2% chance customer churns each day
    
    def generate(self):
        """Generate calls with gradual decline pattern"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=self.num_days)
        
        # Track which customers have churned
        churned_customers = set()
        
        for day in range(self.num_days):
            current_date = start_date + datetime.timedelta(days=day)
            
            # Calculate decline factor for this day
            decline_factor = (1 - self.decline_rate / 7) ** day
            
            for customer in self.customers:
                customer_id = customer['customer_id']
                
                # Skip if customer has churned
                if customer_id in churned_customers:
                    continue
                
                # Check if customer churns today
                if day > 5 and random.random() < self.churn_probability:
                    churned_customers.add(customer_id)
                    continue
                
                # Apply decline factor to usage
                base_calls = customer['calls_per_day']
                daily_calls = int(base_calls * decline_factor * random.uniform(0.8, 1.2))
                
                # Some customers decline faster than others
                customer_decline_multiplier = random.uniform(0.7, 1.0)
                daily_calls = int(daily_calls * customer_decline_multiplier)
                
                # Ensure at least some minimal usage
                daily_calls = max(1, daily_calls)
                
                for _ in range(daily_calls):
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    timestamp = current_date.replace(
                        hour=hour, minute=minute, second=second
                    )
                    call = self._generate_call(customer, timestamp)
                    self.calls.append(call)
        
        self.calls.sort(key=lambda x: x.timestamp)
        
        # Print churn statistics
        churn_rate = len(churned_customers) / len(self.customers) * 100
        print(f"   Churned Customers: {len(churned_customers)} ({churn_rate:.1f}%)")
        
        return self.calls


def main():
    """Run gradual decline simulator"""
    print("=" * 70)
    print("📉 GRADUAL DECLINE SIMULATOR")
    print("=" * 70)
    print()
    print("Simulating decreasing usage patterns:")
    print("  • 3% weekly decline in usage")
    print("  • 2% daily churn probability")
    print("  • Variable decline rates per customer")
    print("  • Realistic downturn scenario")
    print()
    
    simulator = GradualDeclineSimulator(num_customers=40, num_days=30, seed=300)
    
    # Append to existing CSV
    import csv
    from dataclasses import asdict
    
    csv_file = 'data/simulated_calls.csv'
    file_exists = os.path.exists(csv_file)
    
    if not simulator.calls:
        simulator.generate()
    
    mode = 'a' if file_exists else 'w'
    with open(csv_file, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'call_id', 'provider', 'model', 
            'input_tokens', 'output_tokens', 'cost_usd', 'latency_ms',
            'customer_id', 'subscription_tier', 'organization_id', 
            'product_id', 'feature_id', 'task_type', 'environment',
            'request_id', 'trace_id', 'session_id', 'user_agent'
        ])
        
        if not file_exists:
            writer.writeheader()
        
        for call in simulator.calls:
            writer.writerow(asdict(call))
    
    total_cost = sum(call.cost_usd for call in simulator.calls)
    total_tokens = sum(call.input_tokens + call.output_tokens for call in simulator.calls)
    
    action = "Appended to" if file_exists else "Created"
    print(f"✅ {action} {csv_file}")
    print()
    print("📊 Gradual Decline Statistics:")
    print(f"   Total Calls: {len(simulator.calls):,}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Avg Cost/Call: ${total_cost/len(simulator.calls):.4f}")
    print()


if __name__ == '__main__':
    main()
