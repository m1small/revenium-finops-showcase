"""Weekend Effect Simulator - Realistic weekend/holiday reductions."""

from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from simulator.core import AICallSimulator


class WeekendEffectSimulator(AICallSimulator):
    """Generates traffic with pronounced weekend and holiday reductions."""

    def run(self, duration_hours: int = 168, base_calls_per_hour: int = 100):
        """Generate traffic with strong weekend effect.

        Args:
            duration_hours: How many hours to simulate (default 1 week)
            base_calls_per_hour: Base number of calls per hour (weekday)
        """
        print(f"[Weekend Effect] Generating {duration_hours}h with weekend reduction...")

        start_time = datetime.now() - timedelta(hours=duration_hours)

        for hour in range(duration_hours):
            current_time = start_time + timedelta(hours=hour)

            # Strong weekend reduction (already built into base class)
            hour_calls = self._apply_time_of_day_multiplier(current_time, base_calls_per_hour)
            hour_calls = self._apply_day_of_week_multiplier(current_time, hour_calls)

            # Additional reduction for late Friday and early Monday
            day_of_week = current_time.weekday()
            hour_of_day = current_time.hour

            if day_of_week == 4 and hour_of_day >= 15:  # Friday afternoon
                hour_calls = int(hour_calls * 0.6)
            elif day_of_week == 0 and hour_of_day < 10:  # Monday morning
                hour_calls = int(hour_calls * 0.7)

            # Generate calls
            for i in range(hour_calls):
                customer = self.rng.choice(self.customers)
                call_time = current_time + timedelta(minutes=self.rng.randint(0, 59))
                call = self.generate_call(customer, call_time)
                self.append_call(call)

            if (hour + 1) % 24 == 0:
                day_name = current_time.strftime('%A')
                print(f"  Progress: {hour + 1}/{duration_hours} hours ({day_name})")

        print(f"[Weekend Effect] Complete. Generated {self.call_count} calls.")
