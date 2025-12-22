"""Steady Growth Simulator - Consistent expansion pattern."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class SteadyGrowthSimulator(AICallSimulator):
    """Simulates steady linear growth in usage."""

    def run(self, duration_hours: int = 120, base_calls_per_hour: int = 60):
        """Generate steadily growing traffic.

        Args:
            duration_hours: How many hours to simulate (default 5 days)
            base_calls_per_hour: Initial calls per hour
        """
        print(f"[Steady Growth] Generating {duration_hours}h with linear growth...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Linear growth: 100% → 200% over duration
            growth_factor = 1.0 + (1.0 * (hour / duration_hours))

            # Apply all multipliers
            hour_calls = int(base_calls_per_hour * growth_factor)
            hour_calls = self._apply_time_of_day_multiplier(current_time, hour_calls)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 24 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({growth_factor*100:.0f}% of baseline)")

        print(f"[Steady Growth] Complete. Generated {self.call_count} calls.")
