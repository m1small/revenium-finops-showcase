#!/usr/bin/env python3
"""
Continuous Data Generation Orchestrator

Cycles through all 11 scenario simulators, generating traffic until
the CSV file reaches 50MB, then stops automatically.
"""

import os
import sys
import time
from datetime import datetime

# Import all scenario simulators
from simulator.scenarios.base_traffic import BaseTrafficSimulator
from simulator.scenarios.seasonal_pattern import SeasonalPatternSimulator
from simulator.scenarios.burst_traffic import BurstTrafficSimulator
from simulator.scenarios.multi_tenant import MultiTenantSimulator
from simulator.scenarios.model_migration import ModelMigrationSimulator
from simulator.scenarios.weekend_effect import WeekendEffectSimulator
from simulator.scenarios.timezone_pattern import TimezonePatternSimulator
from simulator.scenarios.feature_launch import FeatureLaunchSimulator
from simulator.scenarios.cost_optimization import CostOptimizationSimulator
from simulator.scenarios.gradual_decline import GradualDeclineSimulator
from simulator.scenarios.steady_growth import SteadyGrowthSimulator
from simulator.scenarios.viral_spike import ViralSpikeSimulator


def get_csv_size_mb(csv_path: str) -> float:
    """Get size of CSV file in megabytes."""
    if not os.path.exists(csv_path):
        return 0.0
    return os.path.getsize(csv_path) / (1024 * 1024)


def format_size(size_mb: float) -> str:
    """Format size for display."""
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    return f"{size_mb:.2f} MB"


def draw_progress_bar(current_mb: float, target_mb: float, width: int = 50) -> str:
    """Draw a text progress bar."""
    progress = min(current_mb / target_mb, 1.0)
    filled = int(width * progress)
    bar = '=' * filled + '-' * (width - filled)
    percentage = progress * 100
    return f"[{bar}] {percentage:.1f}% ({format_size(current_mb)} / {format_size(target_mb)})"


def main():
    """Run continuous generation until 50MB."""
    csv_path = 'data/simulated_calls.csv'
    target_size_mb = 50.0
    seed = 42

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # All scenario simulators with their configurations
    scenarios = [
        ('Base Traffic', BaseTrafficSimulator, {'duration_hours': 24, 'calls_per_hour': 100}),
        ('Seasonal Pattern', SeasonalPatternSimulator, {'duration_hours': 168, 'base_calls_per_hour': 80}),
        ('Burst Traffic', BurstTrafficSimulator, {'duration_hours': 48, 'base_calls_per_hour': 60}),
        ('Multi-Tenant', MultiTenantSimulator, {'duration_hours': 72, 'base_calls_per_hour': 100}),
        ('Model Migration', ModelMigrationSimulator, {'duration_hours': 120, 'calls_per_hour': 90}),
        ('Weekend Effect', WeekendEffectSimulator, {'duration_hours': 168, 'base_calls_per_hour': 100}),
        ('Timezone Pattern', TimezonePatternSimulator, {'duration_hours': 72, 'base_calls_per_hour': 120}),
        ('Feature Launch', FeatureLaunchSimulator, {'duration_hours': 96, 'base_calls_per_hour': 70}),
        ('Cost Optimization', CostOptimizationSimulator, {'duration_hours': 120, 'base_calls_per_hour': 110}),
        ('Gradual Decline', GradualDeclineSimulator, {'duration_hours': 168, 'base_calls_per_hour': 100}),
        ('Steady Growth', SteadyGrowthSimulator, {'duration_hours': 120, 'base_calls_per_hour': 60}),
        ('Viral Spike', ViralSpikeSimulator, {'duration_hours': 72, 'base_calls_per_hour': 50})
    ]

    # Initialize CSV with header
    print("=" * 80)
    print("REVENIUM FINOPS SHOWCASE - CONTINUOUS DATA GENERATION")
    print("=" * 80)
    print(f"Target: {format_size(target_size_mb)}")
    print(f"Output: {csv_path}")
    print(f"Scenarios: {len(scenarios)} traffic patterns")
    print("=" * 80)
    print()

    # Create initial CSV
    initial_sim = BaseTrafficSimulator(output_path=csv_path, seed=seed)
    initial_sim.write_csv_header()
    print(f"Created CSV with header at {csv_path}")
    print()

    start_time = time.time()
    cycle_count = 0

    # Cycle through scenarios until target size reached
    while True:
        current_size = get_csv_size_mb(csv_path)

        if current_size >= target_size_mb:
            print()
            print("=" * 80)
            print(f"TARGET REACHED: {format_size(current_size)} >= {format_size(target_size_mb)}")
            print("=" * 80)
            break

        cycle_count += 1
        print(f"\n{'='*80}")
        print(f"CYCLE {cycle_count}")
        print(f"{'='*80}")
        print(draw_progress_bar(current_size, target_size_mb))
        print()

        # Run each scenario in sequence
        for scenario_name, simulator_class, config in scenarios:
            # Check size before each scenario
            current_size = get_csv_size_mb(csv_path)
            if current_size >= target_size_mb:
                print(f"\nTarget reached during cycle. Stopping.")
                break

            print(f"\n--- Running: {scenario_name} ---")

            # Create simulator instance
            # Use different seed for each scenario to get variety
            scenario_seed = seed + hash(scenario_name) % 1000
            simulator = simulator_class(output_path=csv_path, seed=scenario_seed)

            # Run the scenario
            simulator.run(**config)

            # Show progress after each scenario
            new_size = get_csv_size_mb(csv_path)
            size_increase = new_size - current_size
            print(f"Size increased by {format_size(size_increase)} (now {format_size(new_size)})")

        # After full cycle, show summary
        cycle_end_size = get_csv_size_mb(csv_path)
        print(f"\nCycle {cycle_count} complete: {format_size(cycle_end_size)}")

    # Final summary
    end_time = time.time()
    elapsed_seconds = end_time - start_time
    elapsed_minutes = elapsed_seconds / 60

    final_size = get_csv_size_mb(csv_path)

    # Count lines in file
    with open(csv_path, 'r') as f:
        line_count = sum(1 for line in f) - 1  # Subtract header

    print()
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Final Size:        {format_size(final_size)}")
    print(f"Total Calls:       {line_count:,}")
    print(f"Time Elapsed:      {elapsed_minutes:.1f} minutes")
    print(f"Throughput:        {line_count / elapsed_seconds:.0f} calls/second")
    print(f"Cycles Completed:  {cycle_count}")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. cd ../viewer")
    print("  2. python3 serve.py")
    print("  3. Open http://localhost:8000")
    print()


if __name__ == '__main__':
    main()
