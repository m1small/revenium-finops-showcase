"""
Core AI Call Simulator

Generates realistic AI API call data with comprehensive metadata across 7 providers
and 20+ models representing the modern AI market.
"""

import csv
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class AICallSimulator:
    """Base simulator for generating AI API call data."""

    # 7 AI Providers with 20+ models and realistic pricing
    PROVIDERS = {
        'openai': {
            'models': {
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
                'gpt-4o': {'input': 0.005, 'output': 0.015},
                'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
                'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015}
            },
            'weight': 0.40  # 40% market share
        },
        'anthropic': {
            'models': {
                'claude-opus-4': {'input': 0.015, 'output': 0.075},
                'claude-sonnet-4': {'input': 0.003, 'output': 0.015},
                'claude-3.5-sonnet': {'input': 0.003, 'output': 0.015},
                'claude-haiku-4': {'input': 0.0008, 'output': 0.004}
            },
            'weight': 0.25  # 25% market share
        },
        'google': {
            'models': {
                'gemini-pro': {'input': 0.00125, 'output': 0.00375},
                'gemini-1.5-pro': {'input': 0.00125, 'output': 0.005},
                'gemini-1.5-flash': {'input': 0.000075, 'output': 0.0003}
            },
            'weight': 0.15  # 15% market share
        },
        'bedrock': {
            'models': {
                'bedrock-claude-opus': {'input': 0.015, 'output': 0.075},
                'bedrock-claude-sonnet': {'input': 0.003, 'output': 0.015},
                'bedrock-claude-haiku': {'input': 0.0008, 'output': 0.004}
            },
            'weight': 0.10  # 10% market share
        },
        'azure': {
            'models': {
                'azure-gpt-4': {'input': 0.03, 'output': 0.06},
                'azure-gpt-4-turbo': {'input': 0.01, 'output': 0.03},
                'azure-gpt-35-turbo': {'input': 0.0005, 'output': 0.0015}
            },
            'weight': 0.07  # 7% market share
        },
        'mistral': {
            'models': {
                'mistral-large': {'input': 0.004, 'output': 0.012},
                'mistral-medium': {'input': 0.00275, 'output': 0.0081}
            },
            'weight': 0.02  # 2% market share
        },
        'cohere': {
            'models': {
                'command-r-plus': {'input': 0.003, 'output': 0.015},
                'command-r': {'input': 0.0005, 'output': 0.0015}
            },
            'weight': 0.01  # 1% market share
        }
    }

    # Customer archetypes with realistic usage patterns
    CUSTOMER_ARCHETYPES = {
        'light': {
            'calls_per_day_range': (5, 20),
            'input_tokens_range': (50, 300),
            'output_tokens_range': (50, 200),
            'weight': 0.70  # 70% of customers
        },
        'power': {
            'calls_per_day_range': (50, 150),
            'input_tokens_range': (200, 800),
            'output_tokens_range': (150, 600),
            'weight': 0.20  # 20% of customers
        },
        'heavy': {
            'calls_per_day_range': (200, 500),
            'input_tokens_range': (500, 2000),
            'output_tokens_range': (400, 1500),
            'weight': 0.10  # 10% of customers
        }
    }

    # Subscription tiers
    SUBSCRIPTION_TIERS = {
        'starter': {'price': 29, 'weight': 0.50},
        'pro': {'price': 99, 'weight': 0.35},
        'enterprise': {'price': 299, 'weight': 0.15}
    }

    # Product features
    PRODUCTS = ['product_a', 'product_b', 'product_c']
    FEATURES = ['chat', 'code', 'search', 'summarize', 'translate']
    ORGANIZATIONS = [f'org_{i:03d}' for i in range(1, 51)]  # 50 organizations

    # CSV field names (defined once for reuse)
    CSV_FIELDNAMES = [
        'call_id', 'timestamp', 'customer_id', 'organization_id', 'product_id',
        'feature_id', 'provider', 'model', 'input_tokens', 'output_tokens',
        'total_tokens', 'cost_usd', 'latency_ms', 'status', 'environment',
        'region', 'subscription_tier', 'tier_price_usd', 'customer_archetype'
    ]

    def __init__(self, output_path: str = 'data/simulated_calls.csv', seed: int = 42, batch_size: int = 5000):
        """Initialize the simulator.

        Args:
            output_path: Path to output CSV file
            seed: Random seed for reproducibility
            batch_size: Number of calls to accumulate before writing to disk (default: 5000)
        """
        self.output_path = output_path
        self.rng = random.Random(seed)
        self.customers = self._generate_customers(500)  # 500 unique customers
        self.call_count = 0
        self.batch_size = batch_size
        self.batch_buffer = []  # Buffer for batch writing

    def _generate_customers(self, count: int) -> List[Dict[str, Any]]:
        """Generate customer profiles with assigned archetypes and tiers.

        Ensures all combinations of archetypes, tiers, and products are represented,
        then fills remaining slots with weighted random selection.
        """
        customers = []
        customer_num = 1

        # First, ensure we have at least one customer for each combination
        # of archetype, tier, and product to guarantee complete coverage
        archetypes = list(self.CUSTOMER_ARCHETYPES.keys())
        tiers = list(self.SUBSCRIPTION_TIERS.keys())
        products = self.PRODUCTS

        # Create one customer for each archetype/tier/product combination
        for archetype in archetypes:
            for tier in tiers:
                for product in products:
                    if customer_num <= count:
                        customers.append({
                            'customer_id': f'cust_{customer_num:04d}',
                            'archetype': archetype,
                            'tier': tier,
                            'organization': self.rng.choice(self.ORGANIZATIONS),
                            'product': product
                        })
                        customer_num += 1

        # Fill remaining customers with weighted random selection
        for i in range(customer_num, count + 1):
            # Assign archetype based on weights
            archetype = self.rng.choices(
                archetypes,
                weights=[a['weight'] for a in self.CUSTOMER_ARCHETYPES.values()]
            )[0]

            # Assign tier based on weights
            tier = self.rng.choices(
                tiers,
                weights=[t['weight'] for t in self.SUBSCRIPTION_TIERS.values()]
            )[0]

            customers.append({
                'customer_id': f'cust_{i:04d}',
                'archetype': archetype,
                'tier': tier,
                'organization': self.rng.choice(self.ORGANIZATIONS),
                'product': self.rng.choice(self.PRODUCTS)
            })

        return customers

    def _select_provider_and_model(self) -> tuple[str, str, Dict[str, float]]:
        """Select provider and model based on market weights."""
        provider = self.rng.choices(
            list(self.PROVIDERS.keys()),
            weights=[p['weight'] for p in self.PROVIDERS.values()]
        )[0]

        models = self.PROVIDERS[provider]['models']
        model = self.rng.choice(list(models.keys()))
        pricing = models[model]

        return provider, model, pricing

    def _calculate_cost(self, input_tokens: int, output_tokens: int, pricing: Dict[str, float]) -> float:
        """Calculate cost based on token usage and pricing."""
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        return round(input_cost + output_cost, 6)

    def _generate_latency(self, total_tokens: int) -> int:
        """Generate realistic latency based on token count."""
        # Base latency + per-token processing time
        base_latency = self.rng.randint(200, 500)
        token_latency = total_tokens * self.rng.uniform(0.5, 2.0)
        return int(base_latency + token_latency)

    def _apply_time_of_day_multiplier(self, timestamp: datetime, base_calls: int) -> int:
        """Apply realistic business hours multiplier."""
        hour = timestamp.hour

        # Business hours (9am-5pm): 1.0x
        # Early morning (6am-9am): 0.6x
        # Evening (5pm-10pm): 0.8x
        # Night (10pm-6am): 0.3x
        if 9 <= hour < 17:
            multiplier = 1.0
        elif 6 <= hour < 9:
            multiplier = 0.6
        elif 17 <= hour < 22:
            multiplier = 0.8
        else:
            multiplier = 0.3

        # Add some randomness
        multiplier *= self.rng.uniform(0.8, 1.2)
        return max(1, int(base_calls * multiplier))

    def _apply_day_of_week_multiplier(self, timestamp: datetime, base_calls: int) -> int:
        """Apply weekend/weekday multiplier."""
        # Monday-Friday: 1.0x
        # Saturday: 0.4x
        # Sunday: 0.3x
        day_of_week = timestamp.weekday()

        if day_of_week < 5:  # Monday-Friday
            multiplier = 1.0
        elif day_of_week == 5:  # Saturday
            multiplier = 0.4
        else:  # Sunday
            multiplier = 0.3

        return max(1, int(base_calls * multiplier))

    def generate_call(self, customer: Dict[str, Any], timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate a single AI call with full metadata.

        Args:
            customer: Customer profile dictionary
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Dictionary with all 19 fields of call metadata
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Select provider and model
        provider, model, pricing = self._select_provider_and_model()

        # Generate token counts based on customer archetype
        archetype = self.CUSTOMER_ARCHETYPES[customer['archetype']]
        input_tokens = self.rng.randint(*archetype['input_tokens_range'])
        output_tokens = self.rng.randint(*archetype['output_tokens_range'])
        total_tokens = input_tokens + output_tokens

        # Calculate cost and latency
        cost_usd = self._calculate_cost(input_tokens, output_tokens, pricing)
        latency_ms = self._generate_latency(total_tokens)

        # Generate metadata
        feature = self.rng.choice(self.FEATURES)
        tier_price = self.SUBSCRIPTION_TIERS[customer['tier']]['price']

        self.call_count += 1

        return {
            'call_id': f'call_{self.call_count:08d}',
            'timestamp': timestamp.isoformat(),
            'customer_id': customer['customer_id'],
            'organization_id': customer['organization'],
            'product_id': customer['product'],
            'feature_id': feature,
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'cost_usd': cost_usd,
            'latency_ms': latency_ms,
            'status': 'success',
            'environment': 'production',
            'region': self.rng.choice(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']),
            'subscription_tier': customer['tier'],
            'tier_price_usd': tier_price,
            'customer_archetype': customer['archetype']
        }

    def write_csv_header(self):
        """Write CSV header with all 19 fields."""
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDNAMES)
            writer.writeheader()

    def append_call(self, call: Dict[str, Any]):
        """Append a call to the CSV file (batched for performance).

        Calls are buffered and written in batches to minimize file I/O overhead.
        Call flush_batch() to write any remaining buffered calls.
        """
        self.batch_buffer.append(call)

        # Write batch when buffer is full
        if len(self.batch_buffer) >= self.batch_size:
            self.flush_batch()

    def append_batch(self, calls: List[Dict[str, Any]]):
        """Append multiple calls efficiently in a single write operation.

        Args:
            calls: List of call dictionaries to write
        """
        if not calls:
            return

        with open(self.output_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDNAMES)
            writer.writerows(calls)

    def flush_batch(self):
        """Flush any remaining calls in the batch buffer to disk."""
        if self.batch_buffer:
            self.append_batch(self.batch_buffer)
            self.batch_buffer = []

    def generate_batch(self, num_calls: int, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate a batch of calls.

        Args:
            num_calls: Number of calls to generate
            start_time: Starting timestamp (defaults to now)

        Returns:
            List of call dictionaries
        """
        if start_time is None:
            start_time = datetime.now()

        calls = []
        for i in range(num_calls):
            customer = self.rng.choice(self.customers)
            # Spread calls over time (up to 1 hour)
            timestamp = start_time + timedelta(seconds=self.rng.randint(0, 3600))
            call = self.generate_call(customer, timestamp)
            calls.append(call)

        return calls
