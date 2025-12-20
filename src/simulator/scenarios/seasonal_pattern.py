#!/usr/bin/env python3
"""
Seasonal Pattern Simulator
Simulates cyclical usage patterns (e.g., business hours, weekly cycles, monthly patterns)
"""

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class SeasonalPatternSimulator(AICallSimulator):
    """Simulates seasonal/cyclical traffic patterns"""
    
    def __init__(self, num_customers: int = 50, num_days: int = 30, seed: int = None):
        """Initialize with seasonal pattern parameters"""
        super().__init__(num_customers, num_days, seed)
        self.pattern_name = "Seasonal Pattern"
    
    def _apply_seasonal_factor(self, day: int, hour: int) -> float:
        """
        Apply seasonal multiplier based on day and hour
        
        Patterns:
        - Weekly cycle: Higher Mon-Wed, lower Thu-Fri, lowest weekends
        - Daily cycle: Peak at 10am and 2pm, low at night
        - Monthly cycle: Higher at month start/end (reporting periods)
        """
        # Weekly cycle (0=Monday, 6=Sunday)
        day_of_week = day % 7
        if day_of_week < 3:  # Mon-Wed
            weekly_factor = 1.3
        elif day_of_week < 5:  # Thu-Fri
            weekly_factor = 1.0
        else:  # Weekend
            weekly_factor = 0.5
        
        # Daily cycle (business hours peak)
        if 9 <= hour <= 11:  # Morning peak
            daily_factor = 1.4
        elif 13 <= hour <= 15:  # Afternoon peak
            daily_factor = 1.3
        elif 16 <= hour <= 18:  # End of day
            daily_factor = 1.1
        elif 19 <= hour <= 20:  # Evening
            daily_factor = 0.8
        else:  # Off hours
            daily_factor = 0.6
        
        # Monthly cycle (sine wave with period of 30 days)
        monthly_factor = 1.0 + 0.2 * math.sin(2 * math.pi * day / 30)
        
        return weekly_factor * daily_factor * monthly_factor
    
    def generate(self):
        """Generate calls with seasonal patterns"""
        import datetime
        import random
        
        start_date = datetime.datetime.now() - datetime.timedelta(days=self.num_days)
        
        for day in range(self.num_days):
            current_date = start_date + datetime.timedelta(days=day)
            
            for customer in self.customers:
                base_calls = customer['calls_per_day']
                
                # Generate calls throughout the day with seasonal factors
                for _ in range(base_calls):
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    # Apply seasonal factor to determine if call happens
                    seasonal_factor = self._apply_seasonal_factor(day, hour)
                    if random.random() < seasonal_factor:
                        timestamp = current_date.replace(
                            hour=hour, minute=minute, second=second
                        )
                        call = self._generate_call(customer, timestamp)
                        self.calls.append(call)
        
        self.calls.sort(key=lambda x: x.timestamp)
        return self.calls


def main():
    """Run seasonal pattern simulator"""
    print("=" * 70)
    print("🌊 SEASONAL PATTERN SIMULATOR")
    print("=" * 70)
    print()
    print("Simulating cyclical usage patterns:")
    print("  • Weekly cycles (Mon-Wed peak, weekend low)")
    print("  • Daily cycles (10am and 2pm peaks)")
    print("  • Monthly cycles (reporting period effects)")
    print()
    
    simulator = SeasonalPatternSimulator(num_customers=50, num_days=30, seed=100)
    
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
    print("📊 Seasonal Pattern Statistics:")
    print(f"   Total Calls: {len(simulator.calls):,}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Avg Cost/Call: ${total_cost/len(simulator.calls):.4f}")
    print()


if __name__ == '__main__':
    main()
