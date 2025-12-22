"""Viral Spike Simulator - Sudden exponential growth."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class ViralSpikeSimulator(AICallSimulator):
    """Simulates viral growth event with exponential spike."""

    def run(self, duration_hours: int = 72, base_calls_per_hour: int = 50):
        """Generate viral spike traffic pattern.

        Args:
            duration_hours: How many hours to simulate (default 3 days)
            base_calls_per_hour: Pre-spike calls per hour
        """
        print(f"[Viral Spike] Generating {duration_hours}h with viral growth event...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        # Viral event starts at hour 24
        viral_start_hour = 24
        viral_peak_hour = 48  # 24 hours later

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Calculate viral multiplier
            if hour < viral_start_hour:
                # Pre-viral: baseline
                viral_multiplier = 1.0
            elif hour < viral_peak_hour:
                # Exponential growth to 50x peak
                hours_into_viral = hour - viral_start_hour
                viral_duration = viral_peak_hour - viral_start_hour
                progress = hours_into_viral / viral_duration
                # Exponential curve
                viral_multiplier = 1.0 + 49.0 * pow(progress, 2)
            else:
                # Post-peak: exponential decay back to 5x baseline
                hours_after_peak = hour - viral_peak_hour
                decay_duration = duration_hours - viral_peak_hour
                decay_progress = hours_after_peak / decay_duration
                # Decay from 50x to 5x
                viral_multiplier = 5.0 + 45.0 * pow(1.0 - decay_progress, 2)

            # Apply all multipliers
            hour_calls = int(base_calls_per_hour * viral_multiplier)
            hour_calls = self._apply_time_of_day_multiplier(current_time, hour_calls)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 12 == 0:
                status = "baseline" if hour < viral_start_hour else f"{viral_multiplier:.1f}x"
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({status})")

        print(f"[Viral Spike] Complete. Generated {self.call_count} calls.")
