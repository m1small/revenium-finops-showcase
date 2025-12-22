"""Seasonal Pattern Simulator - Cyclical business patterns."""

from datetime import datetime, timedelta
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class SeasonalPatternSimulator(AICallSimulator):
    """Generates traffic with seasonal cyclical patterns."""

    def run(self, duration_hours: int = 168, base_calls_per_hour: int = 80):
        """Generate seasonal traffic with quarterly, monthly, and weekly cycles.

        Args:
            duration_hours: How many hours to simulate (default 1 week)
            base_calls_per_hour: Base number of calls per hour
        """
        print(f"[Seasonal Pattern] Generating {duration_hours}h with cyclical patterns...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Weekly cycle (peaks mid-week)
            week_position = (hour % 168) / 168.0  # Position within week
            weekly_multiplier = 1.0 + 0.3 * math.sin(week_position * 2 * math.pi)

            # Monthly cycle simulation (using hour position)
            month_position = (hour % 720) / 720.0  # Approximate month
            monthly_multiplier = 1.0 + 0.2 * math.sin(month_position * 2 * math.pi)

            # Combined seasonal effect
            seasonal_multiplier = weekly_multiplier * monthly_multiplier

            # Apply all multipliers
            hour_calls = int(base_calls_per_hour * seasonal_multiplier)
            hour_calls = self._apply_time_of_day_multiplier(current_time, hour_calls)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 24 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours")

        print(f"[Seasonal Pattern] Complete. Generated {self.call_count} calls.")
