"""Common utilities for all analyzers."""

import csv
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


def load_calls_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load all calls from CSV into memory.

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of call dictionaries
    """
    calls = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['input_tokens'] = int(row['input_tokens'])
            row['output_tokens'] = int(row['output_tokens'])
            row['total_tokens'] = int(row['total_tokens'])
            row['cost_usd'] = float(row['cost_usd'])
            row['latency_ms'] = int(row['latency_ms'])
            row['tier_price_usd'] = int(row['tier_price_usd'])
            row['timestamp'] = datetime.fromisoformat(row['timestamp'])
            calls.append(row)
    return calls


def group_by(calls: List[Dict[str, Any]], *keys) -> Dict[tuple, List[Dict[str, Any]]]:
    """Group calls by one or more keys.

    Args:
        calls: List of call dictionaries
        *keys: Field names to group by

    Returns:
        Dictionary mapping key tuple to list of calls
    """
    groups = defaultdict(list)
    for call in calls:
        group_key = tuple(call[k] for k in keys)
        groups[group_key].append(call)
    return dict(groups)


def aggregate_metrics(calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate metrics for a list of calls.

    Args:
        calls: List of call dictionaries

    Returns:
        Dictionary with aggregated metrics
    """
    if not calls:
        return {
            'call_count': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'avg_cost_per_call': 0.0,
            'avg_tokens_per_call': 0.0,
            'avg_latency_ms': 0.0,
            'p50_latency_ms': 0,
            'p95_latency_ms': 0,
            'p99_latency_ms': 0
        }

    call_count = len(calls)
    total_cost = sum(c['cost_usd'] for c in calls)
    total_tokens = sum(c['total_tokens'] for c in calls)
    total_input_tokens = sum(c['input_tokens'] for c in calls)
    total_output_tokens = sum(c['output_tokens'] for c in calls)

    latencies = sorted(c['latency_ms'] for c in calls)
    p50_index = int(len(latencies) * 0.50)
    p95_index = int(len(latencies) * 0.95)
    p99_index = int(len(latencies) * 0.99)

    return {
        'call_count': call_count,
        'total_cost': total_cost,
        'total_tokens': total_tokens,
        'total_input_tokens': total_input_tokens,
        'total_output_tokens': total_output_tokens,
        'avg_cost_per_call': total_cost / call_count,
        'avg_tokens_per_call': total_tokens / call_count,
        'avg_latency_ms': sum(c['latency_ms'] for c in calls) / call_count,
        'p50_latency_ms': latencies[p50_index],
        'p95_latency_ms': latencies[p95_index],
        'p99_latency_ms': latencies[p99_index]
    }


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile of a list of values.

    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)

    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100.0))
    return sorted_values[min(index, len(sorted_values) - 1)]


def detect_anomalies(values: List[float], threshold_std: float = 2.0) -> List[int]:
    """Detect anomalies using standard deviation.

    Args:
        values: List of numeric values
        threshold_std: Number of standard deviations for anomaly threshold

    Returns:
        List of indices of anomalous values
    """
    if len(values) < 10:
        return []

    # Calculate mean and std dev
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5

    # Find anomalies
    anomalies = []
    for i, value in enumerate(values):
        if abs(value - mean) > (threshold_std * std_dev):
            anomalies.append(i)

    return anomalies


def format_currency(amount: float) -> str:
    """Format amount as USD currency."""
    return f"${amount:,.2f}"


def format_large_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
