#!/usr/bin/env python3
"""
AI Call Simulator - Generates realistic AI API usage data with Revenium metadata
"""

import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict

# Provider and model pricing (input/output per 1K tokens)
PRICING = {
    'openai': {
        'gpt-4': (0.03, 0.06),
        'gpt-4-turbo': (0.01, 0.03)
    },
    'anthropic': {
        'claude-opus-4': (0.015, 0.075),
        'claude-sonnet-4': (0.003, 0.015)
    },
    'bedrock': {
        'claude-instant': (0.0008, 0.0024),
        'claude-v2': (0.008, 0.024)
    }
}

# Customer archetypes
ARCHETYPES = {
    'light': {'weight': 0.7, 'calls_per_day': (5, 20), 'monthly_cost': (3, 12)},
    'power': {'weight': 0.2, 'calls_per_day': (50, 150), 'monthly_cost': (35, 85)},
    'heavy': {'weight': 0.1, 'calls_per_day': (200, 500), 'monthly_cost': (150, 450)}
}

# Subscription tiers
SUBSCRIPTION_TIERS = {
    'starter': 29,
    'pro': 99,
    'enterprise': 299
}

# Task types
TASK_TYPES = ['chat', 'summarization', 'code_generation', 'translation', 'analysis', 'qa']

# Organizations and products
ORGANIZATIONS = ['org-alpha', 'org-beta', 'org-gamma']
PRODUCTS = ['product-ai-chat', 'product-doc-analyzer', 'product-code-assistant']
FEATURES = ['feature-chat', 'feature-summarize', 'feature-code', 'feature-translate', 'feature-analyze']


class Customer:
    """Represents a customer with usage patterns"""
    
    def __init__(self, customer_id: str, archetype: str):
        self.customer_id = customer_id
        self.archetype = archetype
        self.calls_per_day = random.randint(*ARCHETYPES[archetype]['calls_per_day'])
        self.subscription_tier = self._assign_tier(archetype)
        self.monthly_fee = SUBSCRIPTION_TIERS[self.subscription_tier]
        self.signup_date = datetime.now() - timedelta(days=random.randint(30, 365))
        self.organization_id = random.choice(ORGANIZATIONS)
        self.product_id = random.choice(PRODUCTS)
        
    def _assign_tier(self, archetype: str) -> str:
        """Assign subscription tier based on archetype"""
        if archetype == 'light':
            return random.choice(['starter', 'starter', 'pro'])
        elif archetype == 'power':
            return random.choice(['pro', 'pro', 'enterprise'])
        else:  # heavy
            return 'enterprise'


class AICallSimulator:
    """Simulates AI API calls with realistic patterns"""
    
    def __init__(self, num_customers: int = 100, num_days: int = 30):
        self.num_customers = num_customers
        self.num_days = num_days
        self.customers = self._generate_customers()
        self.start_date = datetime.now() - timedelta(days=num_days)
        
    def _generate_customers(self) -> List[Customer]:
        """Generate customer profiles based on archetype distribution"""
        customers = []
        for i in range(self.num_customers):
            # Weighted random selection of archetype
            rand = random.random()
            if rand < 0.7:
                archetype = 'light'
            elif rand < 0.9:
                archetype = 'power'
            else:
                archetype = 'heavy'
            
            customers.append(Customer(f'cust-{i+1:04d}', archetype))
        return customers
    
    def _generate_call(self, customer: Customer, timestamp: datetime) -> Dict:
        """Generate a single AI call record"""
        # Select provider and model
        provider = random.choice(list(PRICING.keys()))
        model = random.choice(list(PRICING[provider].keys()))
        input_price, output_price = PRICING[provider][model]
        
        # Generate token counts (varies by task type)
        task_type = random.choice(TASK_TYPES)
        if task_type in ['chat', 'qa']:
            input_tokens = random.randint(50, 500)
            output_tokens = random.randint(100, 800)
        elif task_type in ['summarization', 'analysis']:
            input_tokens = random.randint(1000, 5000)
            output_tokens = random.randint(200, 1000)
        elif task_type == 'code_generation':
            input_tokens = random.randint(100, 800)
            output_tokens = random.randint(500, 2000)
        else:  # translation
            input_tokens = random.randint(200, 1500)
            output_tokens = random.randint(200, 1500)
        
        # Calculate cost
        cost = (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
        
        # Generate latency (varies by model complexity)
        if 'gpt-4' in model or 'opus' in model:
            latency_ms = random.randint(800, 3000)
        elif 'turbo' in model or 'sonnet' in model:
            latency_ms = random.randint(400, 1500)
        else:  # instant/v2
            latency_ms = random.randint(200, 800)
        
        return {
            'timestamp': timestamp.isoformat(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': round(cost, 6),
            'latency_ms': latency_ms,
            'customer_id': customer.customer_id,
            'organization_id': customer.organization_id,
            'product_id': customer.product_id,
            'feature_id': random.choice(FEATURES),
            'task_type': task_type,
            'subscription_tier': customer.subscription_tier
        }
    
    def generate_calls(self) -> List[Dict]:
        """Generate all AI calls for the simulation period"""
        all_calls = []
        
        for day in range(self.num_days):
            current_date = self.start_date + timedelta(days=day)
            
            for customer in self.customers:
                # Generate calls for this customer today
                num_calls = customer.calls_per_day
                
                # Add some daily variance (±30%)
                variance = random.uniform(0.7, 1.3)
                num_calls = int(num_calls * variance)
                
                for _ in range(num_calls):
                    # Random time during the day
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    timestamp = current_date.replace(hour=hour, minute=minute, second=second)
                    
                    call = self._generate_call(customer, timestamp)
                    all_calls.append(call)
        
        return all_calls
    
    def save_to_csv(self, filename: str = 'data/simulated_calls.csv'):
        """Generate calls and save to CSV file"""
        print(f"Generating {self.num_days} days of AI calls for {self.num_customers} customers...")
        calls = self.generate_calls()
        
        # Sort by timestamp
        calls.sort(key=lambda x: x['timestamp'])
        
        # Write to CSV
        fieldnames = ['timestamp', 'provider', 'model', 'input_tokens', 'output_tokens', 
                     'cost_usd', 'latency_ms', 'customer_id', 'organization_id', 
                     'product_id', 'feature_id', 'task_type', 'subscription_tier']
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(calls)
        
        # Print summary
        total_calls = len(calls)
        total_cost = sum(call['cost_usd'] for call in calls)
        
        print(f"\n✓ Generated {total_calls:,} AI calls")
        print(f"✓ Total simulated cost: ${total_cost:,.2f}")
        print(f"✓ Average cost per call: ${total_cost/total_calls:.4f}")
        print(f"✓ Data saved to: {filename}")
        
        # Customer summary
        print(f"\nCustomer Distribution:")
        for archetype in ['light', 'power', 'heavy']:
            count = sum(1 for c in self.customers if c.archetype == archetype)
            print(f"  {archetype.capitalize()}: {count} customers ({count/self.num_customers*100:.0f}%)")


def main():
    """Main execution"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run simulation
    simulator = AICallSimulator(num_customers=100, num_days=30)
    simulator.save_to_csv()
    
    print("\n✓ Simulation complete! Run analyzers to generate insights.")


if __name__ == '__main__':
    main()
