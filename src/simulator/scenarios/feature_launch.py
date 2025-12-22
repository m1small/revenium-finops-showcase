"""Feature Launch Simulator - Adoption spike patterns."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class FeatureLaunchSimulator(AICallSimulator):
    """Simulates new feature launch with adoption curve."""

    def run(self, duration_hours: int = 96, base_calls_per_hour: int = 70):
        """Generate traffic showing feature launch adoption.

        Args:
            duration_hours: How many hours to simulate (default 4 days)
            base_calls_per_hour: Base number of calls per hour
        """
        print(f"[Feature Launch] Generating {duration_hours}h with 'code' feature adoption...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        # Feature launch at hour 24 (day 2)
        launch_hour = 24

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Apply time-based multipliers
            hour_calls = self._apply_time_of_day_multiplier(current_time, base_calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Calculate adoption rate
            if hour < launch_hour:
                # Pre-launch: no 'code' feature usage
                code_adoption_rate = 0.0
            else:
                # Post-launch: S-curve adoption (0% → 60% over remaining time)
                hours_since_launch = hour - launch_hour
                max_hours = duration_hours - launch_hour
                adoption_progress = hours_since_launch / max_hours
                # S-curve: slow start, rapid middle, plateau
                code_adoption_rate = 0.6 / (1.0 + pow(2.71828, -5 * (adoption_progress - 0.5)))

            # Additional traffic from new feature usage
            if code_adoption_rate > 0:
                additional_calls = int(hour_calls * code_adoption_rate * 0.8)
                hour_calls += additional_calls

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))

                # Override feature selection based on adoption
                if hour >= launch_hour and self.rng.random() < code_adoption_rate:
                    # Force 'code' feature
                    call = self.generate_call(customer, call_time)
                    # Modify the feature after generation (hacky but effective)
                    call['feature_id'] = 'code'
                    self.append_call(call)
                else:
                    # Normal feature distribution
                    call = self.generate_call(customer, call_time)
                    self.append_call(call)

            if (hour + 1) % 24 == 0:
                status = "pre-launch" if hour < launch_hour else f"{code_adoption_rate*100:.0f}% adoption"
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({status})")

        print(f"[Feature Launch] Complete. Generated {self.call_count} calls.")
