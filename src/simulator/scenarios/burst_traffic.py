"""Burst Traffic Simulator - Unpredictable spikes."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class BurstTrafficSimulator(AICallSimulator):
    """Generates traffic with unpredictable 5x-20x spikes."""

    def run(self, duration_hours: int = 48, base_calls_per_hour: int = 60):
        """Generate burst traffic with random spikes.

        Args:
            duration_hours: How many hours to simulate
            base_calls_per_hour: Base number of calls per hour
        """
        print(f"[Burst Traffic] Generating {duration_hours}h with random spikes...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Random burst: 10% chance of 5x-20x spike
            if self.rng.random() < 0.10:
                burst_multiplier = self.rng.uniform(5.0, 20.0)
                print(f"  Burst at hour {hour}: {burst_multiplier:.1f}x spike")
            else:
                burst_multiplier = 1.0

            # Apply multipliers
            hour_calls = int(base_calls_per_hour * burst_multiplier)
            hour_calls = self._apply_time_of_day_multiplier(current_time, hour_calls)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 12 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours")

        print(f"[Burst Traffic] Complete. Generated {self.call_count} calls.")
