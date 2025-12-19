#!/usr/bin/env python3
"""
Core AI Call Simulator
Generates realistic AI usage data with Revenium metadata
"""

import csv
import random
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AICall:
    """Represents a single AI API call with Revenium metadata"""
    timestamp: str
    call_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    customer_id: str
    subscription_tier: str
    organization_id: str
    product_id: str
    feature_id: str
    task_type: str
    environment: str
    request_id: str
    trace_id: str
    session_id: str
    user_agent: str


class AICallSimulator:
    """Simulates AI API calls with realistic patterns and Revenium metadata"""
    
    # Provider and model configurations
    PROVIDERS = {
        'openai': {
            'models': ['gpt-4', 'gpt-4-turbo'],
            'input_cost': {'gpt-4': 0.03, 'gpt-4-turbo': 0.01},
            'output_cost': {'gpt-4': 0.06, 'gpt-4-turbo': 0.03}
        },
        'anthropic': {
            'models': ['claude-opus-4', 'claude-sonnet-4'],
            'input_cost': {'claude-opus-4': 0.015, 'claude-sonnet-4': 0.003},
            'output_cost': {'claude-opus-4': 0.075, 'claude-sonnet-4': 0.015}
        },
        'bedrock': {
            'models': ['claude-instant', 'claude-v2'],
            'input_cost': {'claude-instant': 0.0008, 'claude-v2': 0.008},
            'output_cost': {'claude-instant': 0.0024, 'claude-v2': 0.024}
        }
    }
    
    SUBSCRIPTION_TIERS = {
        'starter': 29,
        'pro': 99,
        'enterprise': 299
    }
    
    TASK_TYPES = [
        'chat', 'summarization', 'code_generation', 
        'translation', 'analysis', 'qa'
    ]
    
    CUSTOMER_ARCHETYPES = {
        'light': {'calls_per_day': (5, 20), 'weight': 0.70},
        'power': {'calls_per_day': (50, 150), 'weight': 0.20},
        'heavy': {'calls_per_day': (200, 500), 'weight': 0.10}
    }
    
    def __init__(self, num_customers: int = 100, num_days: int = 30, seed: Optional[int] = None):
        """Initialize simulator with customer count and time period"""
        self.num_customers = num_customers
        self.num_days = num_days
        self.calls: List[AICall] = []
        
        if seed:
            random.seed(seed)
        
        # Generate customer profiles
        self.customers = self._generate_customers()
        
    def _generate_customers(self) -> List[Dict[str, Any]]:
        """Generate customer profiles with archetypes and tiers"""
        customers = []
        
        for i in range(self.num_customers):
            # Assign archetype based on weights
            rand = random.random()
            if rand < 0.70:
                archetype = 'light'
            elif rand < 0.90:
                archetype = 'power'
            else:
                archetype = 'heavy'
            
            # Assign subscription tier (correlated with archetype)
            if archetype == 'light':
                tier = random.choice(['starter'] * 7 + ['pro'] * 3)
            elif archetype == 'power':
                tier = random.choice(['pro'] * 6 + ['enterprise'] * 4)
            else:
                tier = random.choice(['enterprise'] * 7 + ['pro'] * 3)
            
            customers.append({
                'customer_id': f'cust_{i+1:04d}',
                'archetype': archetype,
                'subscription_tier': tier,
                'organization_id': f'org_{(i // 10) + 1:03d}',
                'calls_per_day': random.randint(*self.CUSTOMER_ARCHETYPES[archetype]['calls_per_day'])
            })
        
        return customers
    
    def _generate_call(self, customer: Dict[str, Any], timestamp: datetime.datetime) -> AICall:
        """Generate a single AI call with realistic parameters"""
        
        # Select provider and model
        provider = random.choice(list(self.PROVIDERS.keys()))
        model = random.choice(self.PROVIDERS[provider]['models'])
        
        # Generate token counts (varies by task type)
        task_type = random.choice(self.TASK_TYPES)
        
        if task_type == 'chat':
            input_tokens = random.randint(50, 500)
            output_tokens = random.randint(100, 800)
        elif task_type == 'summarization':
            input_tokens = random.randint(1000, 5000)
            output_tokens = random.randint(100, 500)
        elif task_type == 'code_generation':
            input_tokens = random.randint(100, 800)
            output_tokens = random.randint(200, 1500)
        else:
            input_tokens = random.randint(100, 1000)
            output_tokens = random.randint(100, 1000)
        
        # Calculate cost
        input_cost_per_1k = self.PROVIDERS[provider]['input_cost'][model]
        output_cost_per_1k = self.PROVIDERS[provider]['output_cost'][model]
        cost_usd = (input_tokens / 1000 * input_cost_per_1k) + \
                   (output_tokens / 1000 * output_cost_per_1k)
        
        # Generate latency (correlated with tokens and model)
        base_latency = 200 if 'gpt-4' in model or 'opus' in model else 100
        latency_ms = base_latency + (output_tokens // 10) + random.randint(-50, 100)
        
        # Generate IDs
        call_id = f"call_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        request_id = f"req_{random.randint(100000, 999999)}"
        trace_id = f"trace_{random.randint(100000, 999999)}"
        session_id = f"sess_{random.randint(10000, 99999)}"
        
        # Select product and feature
        products = ['product_a', 'product_b', 'product_c']
        features = ['chat', 'summarize', 'code', 'translate', 'analyze', 'qa']
        
        return AICall(
            timestamp=timestamp.isoformat(),
            call_id=call_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round(cost_usd, 6),
            latency_ms=latency_ms,
            customer_id=customer['customer_id'],
            subscription_tier=customer['subscription_tier'],
            organization_id=customer['organization_id'],
            product_id=random.choice(products),
            feature_id=random.choice(features),
            task_type=task_type,
            environment='production',
            request_id=request_id,
            trace_id=trace_id,
            session_id=session_id,
            user_agent=f"ReveniumSDK/1.0 Python/3.{random.randint(8, 11)}"
        )
    
    def generate(self) -> List[AICall]:
        """Generate all AI calls for the simulation period"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=self.num_days)
        
        for day in range(self.num_days):
            current_date = start_date + datetime.timedelta(days=day)
            
            # Weekend effect (30% less usage)
            is_weekend = current_date.weekday() >= 5
            weekend_factor = 0.7 if is_weekend else 1.0
            
            for customer in self.customers:
                # Determine number of calls for this customer today
                base_calls = customer['calls_per_day']
                daily_calls = int(base_calls * weekend_factor * random.uniform(0.8, 1.2))
                
                for _ in range(daily_calls):
                    # Random time during business hours (8am-8pm)
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    timestamp = current_date.replace(
                        hour=hour, minute=minute, second=second
                    )
                    
                    call = self._generate_call(customer, timestamp)
                    self.calls.append(call)
        
        # Sort by timestamp
        self.calls.sort(key=lambda x: x.timestamp)
        return self.calls
    
    def save_to_csv(self, filepath: str = 'data/simulated_calls.csv'):
        """Save generated calls to CSV file"""
        if not self.calls:
            self.generate()
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'call_id', 'provider', 'model', 
                'input_tokens', 'output_tokens', 'cost_usd', 'latency_ms',
                'customer_id', 'subscription_tier', 'organization_id', 
                'product_id', 'feature_id', 'task_type', 'environment',
                'request_id', 'trace_id', 'session_id', 'user_agent'
            ])
            writer.writeheader()
            
            for call in self.calls:
                writer.writerow(asdict(call))
        
        print(f"✅ Generated {len(self.calls)} calls and saved to {filepath}")
        return filepath
    
    def add_heavy_users(self, count: int = 15, archetype: str = 'heavy'):
        """Add specific heavy users for scenario testing"""
        for i in range(count):
            customer_id = f'cust_heavy_{i+1:04d}'
            self.customers.append({
                'customer_id': customer_id,
                'archetype': archetype,
                'subscription_tier': 'starter',  # Unprofitable: high usage, low tier
                'organization_id': f'org_heavy_{i+1:03d}',
                'calls_per_day': random.randint(300, 600)
            })


def main():
    """Run simulator as standalone script"""
    print("🚀 Starting AI Call Simulator...")
    print(f"   Customers: 100")
    print(f"   Days: 30")
    print()
    
    simulator = AICallSimulator(num_customers=100, num_days=30, seed=42)
    simulator.save_to_csv('data/simulated_calls.csv')
    
    # Print summary statistics
    total_cost = sum(call.cost_usd for call in simulator.calls)
    total_tokens = sum(call.input_tokens + call.output_tokens for call in simulator.calls)
    
    print()
    print("📊 Summary Statistics:")
    print(f"   Total Calls: {len(simulator.calls):,}")
    print(f"   Total Cost: ${total_cost:,.2f}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Avg Cost/Call: ${total_cost/len(simulator.calls):.4f}")
    print()


if __name__ == '__main__':
    main()
