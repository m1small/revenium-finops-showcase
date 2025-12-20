# Traffic Pattern Simulators

This directory contains specialized simulators that generate different traffic patterns to demonstrate various real-world scenarios.

## Available Simulators

### 1. Seasonal Pattern (`seasonal_pattern.py`)
**Purpose**: Simulates cyclical usage patterns common in business applications

**Characteristics**:
- **Weekly cycles**: Higher usage Mon-Wed (1.3x), normal Thu-Fri (1.0x), lower weekends (0.5x)
- **Daily cycles**: Peak at 10am (1.4x) and 2pm (1.3x), lower at night (0.6x)
- **Monthly cycles**: Sine wave pattern reflecting reporting periods
- **Use cases**: Business analytics tools, reporting systems, enterprise applications

**Run**:
```bash
cd src
python3 simulator/scenarios/seasonal_pattern.py
```

**Parameters**:
- 50 customers
- 30 days simulation
- Seed: 100

---

### 2. Burst Traffic (`burst_traffic.py`)
**Purpose**: Simulates unpredictable burst patterns from batch processing or automated workflows

**Characteristics**:
- **Burst probability**: 15% chance per customer per day
- **Burst intensity**: 5x-20x normal traffic during bursts
- **Burst duration**: Concentrated in 1-3 hour windows
- **Baseline**: 20% of normal usage on non-burst days
- **Use cases**: Batch processing, API integrations, automated data pipelines

**Run**:
```bash
cd src
python3 simulator/scenarios/burst_traffic.py
```

**Parameters**:
- 30 customers
- 30 days simulation
- Seed: 200

---

### 3. Gradual Decline (`gradual_decline.py`)
**Purpose**: Simulates decreasing usage over time due to churn or seasonal downturn

**Characteristics**:
- **Decline rate**: 3% per week (~0.43% per day)
- **Churn probability**: 2% chance per customer per day
- **Variable decline**: Different customers decline at different rates (0.7x-1.0x)
- **Minimum usage**: Ensures at least 1 call per day per active customer
- **Use cases**: Churn analysis, feature deprecation, seasonal downturn scenarios

**Run**:
```bash
cd src
python3 simulator/scenarios/gradual_decline.py
```

**Parameters**:
- 40 customers
- 30 days simulation
- Seed: 300

---

### 4. Base Traffic Pattern (`../core.py`)
**Purpose**: Standard baseline traffic with realistic customer archetypes

**Characteristics**:
- **Customer archetypes**: Light (70%), Power (20%), Heavy (10%)
- **Weekend effect**: 30% reduction in usage
- **Business hours**: 8am-8pm
- **Subscription tiers**: Starter ($29), Pro ($99), Enterprise ($299)
- **Use cases**: Baseline comparison, standard usage patterns

**Run**:
```bash
cd src
python3 simulator/core.py
```

**Parameters**:
- 100 customers
- 30 days simulation
- Seed: 42

---

## Running All Simulators

To generate a comprehensive dataset with all traffic patterns:

```bash
cd src
python3 run_all_simulators.py
```

This will:
1. Clear existing data
2. Run all 4 simulators in sequence
3. Append all data to the same CSV file
4. Display combined statistics

**Total dataset**:
- ~220 unique customers (100 + 50 + 30 + 40)
- Multiple traffic patterns
- Comprehensive coverage of real-world scenarios

---

## Data Output

All simulators append to the same CSV file: `src/data/simulated_calls.csv`

**CSV Schema**:
```
timestamp, call_id, provider, model, input_tokens, output_tokens, 
cost_usd, latency_ms, customer_id, subscription_tier, organization_id, 
product_id, feature_id, task_type, environment, request_id, trace_id, 
session_id, user_agent
```

---

## Analysis Workflow

After generating data with simulators:

1. **Run analyzers** to process all data:
   ```bash
   python3 run_all_analyzers.py
   ```

2. **View reports** in browser:
   ```bash
   cd ../viewer
   python3 serve.py
   # Open http://localhost:8000/viewer/index.html
   ```

The viewer automatically detects and processes any new data before serving reports.

---

## Customization

Each simulator can be customized by modifying parameters:

```python
# Example: Increase burst intensity
simulator = BurstTrafficSimulator(
    num_customers=50,      # More customers
    num_days=60,           # Longer period
    seed=200               # Reproducible results
)
simulator.burst_multiplier = (10, 30)  # 10x-30x bursts
```

---

## Use Cases by Simulator

| Simulator | Best For | Key Insight |
|-----------|----------|-------------|
| **Seasonal** | Enterprise SaaS | Predictable patterns enable capacity planning |
| **Burst** | API platforms | Burst detection prevents cost overruns |
| **Decline** | Churn analysis | Early warning signals for retention efforts |
| **Base** | General usage | Baseline for comparison and benchmarking |

---

## Technical Notes

- **Append mode**: All simulators append to existing CSV (except first run)
- **Unique IDs**: Each simulator uses different seed for unique customer IDs
- **Timestamp ordering**: All calls are sorted by timestamp after generation
- **Memory efficient**: Streaming CSV writes, no full dataset in memory
- **Reproducible**: Fixed seeds ensure consistent results across runs

---

## Troubleshooting

**Issue**: Duplicate customer IDs across simulators
- **Solution**: Each simulator uses different seed values (42, 100, 200, 300)

**Issue**: CSV file locked
- **Solution**: Close any programs (Excel, etc.) that have the CSV open

**Issue**: Out of memory
- **Solution**: Reduce `num_customers` or `num_days` parameters

**Issue**: Reports not updating
- **Solution**: The viewer automatically regenerates reports when data changes

---

## Next Steps

1. **Add more patterns**: Create new simulators for specific scenarios
2. **Combine patterns**: Mix multiple patterns for single customer
3. **Real data**: Replace simulated data with actual API logs
4. **Advanced analysis**: Add ML-based anomaly detection

---

**Built to demonstrate Revenium's ability to handle diverse traffic patterns and provide actionable insights across all scenarios.**
