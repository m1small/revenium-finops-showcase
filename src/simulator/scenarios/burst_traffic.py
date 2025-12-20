#!/usr/bin/env python3
"""
Burst Traffic Simulator
Simulates unpredictable burst patterns (e.g., batch processing, API integrations, automated workflows)
"""

import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator
import datetime


class BurstTrafficSimulator(AICallSimulator):
    """Simulates bursty, unpredictable traffic patterns"""
    
    def __init__(self, num_customers: int = 30, num_days: int = 30, seed: int = None):
        """Initialize with burst pattern parameters"""
        super().__init__(num_customers, num_days, seed)
        self.pattern_name = "Burst Traffic"
        self.burst_probability = 0.15  # 15% chance of burst per customer per day
        self.burst_multiplier = (5, 20)  # 5x to 20x normal traffic
    
    def generate(self):
        """Generate calls with burst patterns"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=self.num_days)
        
        for day in range(self.num_days):
            current_date = start_date + datetime.timedelta(days=day)
            
            for customer in self.customers:
                base_calls = customer['calls_per_day']
                
                # Determine if this customer has a burst today
                is_burst_day = random.random() < self.burst_probability
                
                if is_burst_day:
                    # Burst: concentrated in short time window
                    burst_multiplier = random.uniform(*self.burst_multiplier)
                    num_calls = int(base_calls * burst_multiplier)
                    
                    # Burst happens in 1-3 hour window
                    burst_start_hour = random.randint(8, 18)
                    burst_duration_hours = random.randint(1, 3)
                    
                    for _ in range(num_calls):
                        # Concentrate calls in burst window
                        hour = burst_start_hour + random.randint(0, burst_duration_hours)
                        hour = min(hour, 20)  # Cap at 8pm
                        minute = random.randint(0, 59)
                        second = random.randint(0, 59)
                        
                        timestamp = current_date.replace(
                            hour=hour, minute=minute, second=second
                        )
                        call = self._generate_call(customer, timestamp)
                        self.calls.append(call)
                else:
                    # Normal day: very light usage (20% of normal)
                    num_calls = int(base_calls * 0.2)
                    
                    for _ in range(num_calls):
                        hour = random.randint(8, 20)
                        minute = random.randint(0, 59)
                        second = random.randint(0, 59)
                        
                        timestamp = current_date.replace(
                            hour=hour, minute=minute, second=second
                        )
                        call = self._generate_call(customer, timestamp)
                        self.calls.append(call)
        
        self.calls.sort(key=lambda x: x.timestamp)
        return self.calls


def main():
    """Run burst traffic simulator"""
    print("=" * 70)
    print("💥 BURST TRAFFIC SIMULATOR")
    print("=" * 70)
    print()
    print("Simulating unpredictable burst patterns:")
    print("  • Random burst events (15% probability per day)")
    print("  • 5x-20x traffic during bursts")
    print("  • Concentrated in 1-3 hour windows")
    print("  • Light usage on non-burst days")
    print()
    
    simulator = BurstTrafficSimulator(num_customers=30, num_days=30, seed=200)
    
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
    print("📊 Burst Traffic Statistics:")
    print(f"   Total Calls: {len(simulator.calls):,}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Avg Cost/Call: ${total_cost/len(simulator.calls):.4f}")
    print()


if __name__ == '__main__':
    main()
