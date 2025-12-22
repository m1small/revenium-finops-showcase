"""Cost Optimization Simulator - Engineering-led cost reductions."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class CostOptimizationSimulator(AICallSimulator):
    """Simulates engineering team implementing cost optimizations."""

    def run(self, duration_hours: int = 120, base_calls_per_hour: int = 110):
        """Generate traffic showing gradual optimization to cheaper models.

        Args:
            duration_hours: How many hours to simulate (default 5 days)
            base_calls_per_hour: Base number of calls per hour
        """
        print(f"[Cost Optimization] Generating {duration_hours}h with model optimization...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Optimization progress: 0% → 80% over duration
            optimization_progress = (hour / duration_hours) * 0.8

            # Apply time-based multipliers
            hour_calls = self._apply_time_of_day_multiplier(current_time, base_calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))

                # Determine if this call uses optimized model
                if self.rng.random() < optimization_progress:
                    # Optimized: Use cheaper models
                    provider_choice = self.rng.choice([
                        ('openai', 'gpt-4o-mini'),
                        ('anthropic', 'claude-haiku-4'),
                        ('google', 'gemini-1.5-flash')
                    ])
                    provider, model = provider_choice
                else:
                    # Unoptimized: Use expensive models
                    provider_choice = self.rng.choice([
                        ('openai', 'gpt-4'),
                        ('anthropic', 'claude-opus-4'),
                        ('google', 'gemini-1.5-pro')
                    ])
                    provider, model = provider_choice

                # Get pricing and generate call
                pricing = self.PROVIDERS[provider]['models'][model]
                archetype = self.CUSTOMER_ARCHETYPES[customer['archetype']]
                input_tokens = self.rng.randint(*archetype['input_tokens_range'])
                output_tokens = self.rng.randint(*archetype['output_tokens_range'])
                total_tokens = input_tokens + output_tokens
                cost_usd = self._calculate_cost(input_tokens, output_tokens, pricing)
                latency_ms = self._generate_latency(total_tokens)

                feature = self.rng.choice(self.FEATURES)
                tier_price = self.SUBSCRIPTION_TIERS[customer['tier']]['price']

                self.call_count += 1

                call = {
                    'call_id': f'call_{self.call_count:08d}',
                    'timestamp': call_time.isoformat(),
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
                self.append_call(call)

            if (hour + 1) % 24 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({optimization_progress*100:.0f}% optimized)")

        print(f"[Cost Optimization] Complete. Generated {self.call_count} calls.")
