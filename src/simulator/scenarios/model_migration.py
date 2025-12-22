"""Model Migration Simulator - Gradual provider/model shifts."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class ModelMigrationSimulator(AICallSimulator):
    """Simulates gradual migration from one provider/model to another."""

    def run(self, duration_hours: int = 120, calls_per_hour: int = 90):
        """Generate traffic showing gradual model migration.

        Args:
            duration_hours: How many hours to simulate (default 5 days)
            calls_per_hour: Base number of calls per hour
        """
        print(f"[Model Migration] Generating {duration_hours}h with GPT-4 → Claude migration...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Migration progress: 0% → 100% over duration
            migration_progress = hour / duration_hours

            # Apply time-based multipliers
            hour_calls = self._apply_time_of_day_multiplier(current_time, calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))

                # Override provider/model selection based on migration progress
                if self.rng.random() < migration_progress:
                    # Migrated: Use Anthropic
                    provider = 'anthropic'
                    model = self.rng.choice(['claude-sonnet-4', 'claude-3.5-sonnet'])
                else:
                    # Legacy: Use OpenAI GPT-4
                    provider = 'openai'
                    model = 'gpt-4'

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
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({migration_progress*100:.0f}% migrated)")

        print(f"[Model Migration] Complete. Generated {self.call_count} calls.")
