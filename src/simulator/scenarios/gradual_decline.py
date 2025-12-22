"""Gradual Decline Simulator - Customer churn simulation."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class GradualDeclineSimulator(AICallSimulator):
    """Simulates gradual customer churn and usage decline."""

    def run(self, duration_hours: int = 168, base_calls_per_hour: int = 100):
        """Generate declining traffic pattern.

        Args:
            duration_hours: How many hours to simulate (default 1 week)
            base_calls_per_hour: Initial calls per hour
        """
        print(f"[Gradual Decline] Generating {duration_hours}h with churn pattern...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Linear decline: 100% → 40% over duration
            decline_factor = 1.0 - (0.6 * (hour / duration_hours))

            # Apply all multipliers
            hour_calls = int(base_calls_per_hour * decline_factor)
            hour_calls = self._apply_time_of_day_multiplier(current_time, hour_calls)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 24 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({decline_factor*100:.0f}% of baseline)")

        print(f"[Gradual Decline] Complete. Generated {self.call_count} calls.")
