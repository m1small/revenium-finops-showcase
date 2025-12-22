#!/usr/bin/env python3
"""
Test Workflow

Validates that all components work end-to-end.
Generates a small dataset and runs analysis.
"""

import os
import sys

def test_simulator():
    """Test that simulators can generate data."""
    print("Testing Simulator...")
    print("-" * 60)

    sys.path.insert(0, 'src')
    from simulator.scenarios.base_traffic import BaseTrafficSimulator

    # Create test CSV
    test_csv = 'src/data/test_calls.csv'
    os.makedirs('src/data', exist_ok=True)

    sim = BaseTrafficSimulator(output_path=test_csv, seed=42)
    sim.write_csv_header()

    # Generate small batch
    sim.run(duration_hours=1, calls_per_hour=50)

    # Verify file was created
    if not os.path.exists(test_csv):
        print("ERROR: CSV file not created")
        return False

    # Count lines
    with open(test_csv, 'r') as f:
        line_count = sum(1 for line in f)

    if line_count < 2:  # At least header + 1 row
        print("ERROR: No data generated")
        return False

    print(f"SUCCESS: Generated {line_count - 1} calls")
    print()
    return True


def test_analyzer():
    """Test that analyzer can process data."""
    print("Testing Analyzer...")
    print("-" * 60)

    sys.path.insert(0, 'src')
    from analyzers.finops.understanding import UnderstandingAnalyzer

    test_csv = 'src/data/test_calls.csv'

    if not os.path.exists(test_csv):
        print("ERROR: Test CSV not found. Run test_simulator first.")
        return False

    analyzer = UnderstandingAnalyzer(test_csv)
    results = analyzer.analyze()

    # Verify results structure
    if 'summary' not in results:
        print("ERROR: Missing summary in results")
        return False

    summary = results['summary']
    print(f"Analyzed {summary['total_calls']} calls")
    print(f"Total cost: ${summary['total_cost']:.4f}")
    print(f"Unique customers: {summary['unique_customers']}")

    print("SUCCESS: Analysis complete")
    print()
    return True


def test_integration_examples():
    """Test integration examples."""
    print("Testing Integration Examples...")
    print("-" * 60)

    # Test basic tracker
    sys.path.insert(0, 'showcase')
    from instrumentation.revenium_basic import ReveniumBasicTracker

    tracker = ReveniumBasicTracker(api_key="test-key")
    call_id = tracker.track_ai_call(
        provider="openai",
        model="gpt-4",
        input_tokens=100,
        output_tokens=200,
        cost_usd=0.009,
        latency_ms=1000,
        metadata={'customer_id': 'test_001'}
    )

    if not call_id:
        print("ERROR: Failed to track call")
        return False

    print(f"Basic tracker: {call_id}")

    # Test OTEL integration
    from instrumentation.revenium_otel import ReveniumOTELIntegration

    otel = ReveniumOTELIntegration(
        revenium_endpoint="https://test.io",
        api_key="test-key"
    )
    trace_id = otel.track_ai_completion(None, {'customer_id': 'test_001'})

    if not trace_id:
        print("ERROR: Failed to create trace")
        return False

    print(f"OTEL integration: {trace_id}")

    # Test Chart Builder
    from queries.chart_builder import ReveniumChartBuilder

    builder = ReveniumChartBuilder(api_key="test-key")
    chart_id = builder.build_multi_dimensional_chart(
        dimensions=['organization_id', 'product_id'],
        metrics=['cost_usd'],
        filters={},
        visualization_type='treemap',
        name='Test Chart'
    )

    if not chart_id:
        print("ERROR: Failed to create chart")
        return False

    print(f"Chart Builder: {chart_id}")

    print("SUCCESS: All integration examples working")
    print()
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("REVENIUM FINOPS SHOWCASE - WORKFLOW VALIDATION")
    print("=" * 60)
    print()

    tests = [
        ("Simulator", test_simulator),
        ("Analyzer", test_analyzer),
        ("Integration Examples", test_integration_examples)
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{name:30} {status}")
        if not success:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\nAll tests passed!")
        print("\nNext steps:")
        print("  1. cd src")
        print("  2. python3 run_all_simulators.py")
        print("  3. cd ../viewer")
        print("  4. python3 serve.py")
        print("  5. Open http://localhost:8000")
        return 0
    else:
        print("\nSome tests failed. Please check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
