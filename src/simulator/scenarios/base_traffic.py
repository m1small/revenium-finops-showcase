"""Base Traffic Simulator - Standard usage patterns."""

from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class BaseTrafficSimulator(AICallSimulator):
    """Generates standard baseline traffic with customer archetypes."""

    def run(self, duration_hours: int = 24, calls_per_hour: int = 100):
        """Generate baseline traffic.

        Args:
            duration_hours: How many hours of traffic to simulate
            calls_per_hour: Base number of calls per hour
        """
        print(f"[Base Traffic] Generating {duration_hours}h of baseline traffic...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Apply time-of-day and day-of-week multipliers
            hour_calls = self._apply_time_of_day_multiplier(current_time, calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls for this hour
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 6 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours")

        print(f"[Base Traffic] Complete. Generated {self.call_count} calls.")
