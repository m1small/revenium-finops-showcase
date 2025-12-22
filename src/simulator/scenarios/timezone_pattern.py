"""Timezone Pattern Simulator - Global 24-hour coverage."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class TimezonePatternSimulator(AICallSimulator):
    """Generates traffic reflecting global time zone distribution."""

    # Time zone weights (representing customer distribution)
    TIMEZONE_REGIONS = {
        'americas': {'weight': 0.40, 'peak_hour_utc': 14},  # 9am EST
        'europe': {'weight': 0.30, 'peak_hour_utc': 9},     # 9am CET
        'asia_pacific': {'weight': 0.30, 'peak_hour_utc': 1}  # 9am JST
    }

    def run(self, duration_hours: int = 72, base_calls_per_hour: int = 120):
        """Generate traffic with global time zone patterns.

        Args:
            duration_hours: How many hours to simulate
            base_calls_per_hour: Base number of calls per hour (global total)
        """
        print(f"[Timezone Pattern] Generating {duration_hours}h with global distribution...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)
            hour_utc = current_time.hour

            # Calculate traffic for each region
            total_hour_calls = 0

            for region_name, region_config in self.TIMEZONE_REGIONS.items():
                region_weight = region_config['weight']
                peak_hour = region_config['peak_hour_utc']

                # Calculate distance from peak hour (0-12 hours)
                hour_distance = min(abs(hour_utc - peak_hour), 24 - abs(hour_utc - peak_hour))

                # Peak at 9am local time, 30% at midnight local time
                region_multiplier = 1.0 - (0.7 * (hour_distance / 12.0))

                region_calls = int(base_calls_per_hour * region_weight * region_multiplier)
                total_hour_calls += region_calls

            # Generate calls
            for i in range(total_hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 12 == 0:
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({total_hour_calls} calls/hr)")

        print(f"[Timezone Pattern] Complete. Generated {self.call_count} calls.")
