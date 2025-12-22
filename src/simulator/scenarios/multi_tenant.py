"""Multi-Tenant Simulator - Organization-level variability."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class MultiTenantSimulator(AICallSimulator):
    """Generates traffic with organization-level variability (3x-10x variance)."""

    def run(self, duration_hours: int = 72, base_calls_per_hour: int = 100):
        """Generate multi-tenant traffic with per-organization multipliers.

        Args:
            duration_hours: How many hours to simulate
            base_calls_per_hour: Base number of calls per hour
        """
        print(f"[Multi-Tenant] Generating {duration_hours}h with org-level variance...")

        # Assign random multipliers to organizations
        org_multipliers = {}
        for org in self.ORGANIZATIONS:
            # Some orgs are 3x-10x more active
            org_multipliers[org] = self.rng.uniform(0.5, 10.0)

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Apply time-based multipliers
            hour_calls = self._apply_time_of_day_multiplier(current_time, base_calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls with org-specific multipliers
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                org_multiplier = org_multipliers[customer['organization']]

                # Probabilistic call generation based on org multiplier
                if self.rng.random() < (org_multiplier / 10.0):
                    call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                    call = self.generate_call(customer, call_time)
                    self.append_call(call)

            if (hour + 1) % 24 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours")

        print(f"[Multi-Tenant] Complete. Generated {self.call_count} calls.")
