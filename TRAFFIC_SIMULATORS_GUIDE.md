# Traffic Simulators Implementation Guide

## Overview

This document describes the new traffic pattern simulators added to the Revenium FinOps Showcase, enabling comprehensive demonstration of diverse real-world usage scenarios.

## What Was Added

### 3 New Traffic Pattern Simulators

1. **Seasonal Pattern Simulator** ([`src/simulator/scenarios/seasonal_pattern.py`](src/simulator/scenarios/seasonal_pattern.py))
   - Cyclical usage patterns (weekly, daily, monthly)
   - 50 customers, 30 days
   - Perfect for enterprise SaaS demonstrations

2. **Burst Traffic Simulator** ([`src/simulator/scenarios/burst_traffic.py`](src/simulator/scenarios/burst_traffic.py))
   - Unpredictable burst patterns (5x-20x normal)
   - 30 customers, 30 days
   - Models batch processing and API integrations

3. **Gradual Decline Simulator** ([`src/simulator/scenarios/gradual_decline.py`](src/simulator/scenarios/gradual_decline.py))
   - Decreasing usage with churn simulation
   - 40 customers, 30 days
   - Demonstrates retention analysis

### Master Simulator Runner

**File**: [`src/run_all_simulators.py`](src/run_all_simulators.py)

Orchestrates all 4 simulators (base + 3 new patterns):
- Clears existing data
- Runs simulators in sequence
- Appends all data to single CSV
- Displays combined statistics

### Auto-Processing Viewer

**File**: [`viewer/serve.py`](viewer/serve.py)

Enhanced to automatically:
- Check if data exists
- Detect if data has changed
- Run analyzers before serving
- Ensure reports are always up-to-date

### Documentation

1. **Simulator Documentation**: [`src/simulator/scenarios/README.md`](src/simulator/scenarios/README.md)
   - Detailed description of each simulator
   - Usage instructions
   - Customization examples
   - Troubleshooting guide

2. **Updated Main README**: [`README.md`](README.md)
   - New traffic pattern section
   - Updated project structure
   - Enhanced feature list

3. **Updated Quick Start**: [`QUICKSTART.md`](QUICKSTART.md)
   - New workflow with all simulators
   - Auto-processing viewer instructions
   - Individual simulator examples

## Key Features

### 1. Append Mode
All simulators append to the same CSV file (`data/simulated_calls.csv`), creating a comprehensive dataset with multiple traffic patterns.

### 2. Unique Customer IDs
Each simulator uses different seed values to ensure unique customer IDs:
- Base: seed=42 (100 customers)
- Seasonal: seed=100 (50 customers)
- Burst: seed=200 (30 customers)
- Decline: seed=300 (40 customers)

**Total: 220 unique customers**

### 3. Diverse Patterns
The combined dataset includes:
- Steady baseline usage
- Cyclical patterns (weekly, daily, monthly)
- Unpredictable bursts
- Gradual decline with churn

### 4. Automatic Processing
The viewer now automatically:
- Detects new or changed data
- Runs all analyzers
- Regenerates reports
- Serves updated content

## Usage Workflows

### Workflow 1: Complete Dataset (Recommended)

```bash
# Generate all traffic patterns
cd src
python3 run_all_simulators.py

# View reports (auto-processes data)
cd ../viewer
python3 serve.py
# Open http://localhost:8000/viewer/index.html
```

### Workflow 2: Individual Patterns

```bash
cd src

# Run specific simulator
python3 simulator/scenarios/seasonal_pattern.py

# Run analyzers manually
python3 run_all_analyzers.py

# View reports
cd ../viewer
python3 serve.py
```

### Workflow 3: Custom Mix

```bash
cd src

# Clear existing data
rm data/simulated_calls.csv

# Run selected simulators
python3 simulator/core.py
python3 simulator/scenarios/burst_traffic.py

# Viewer auto-processes
cd ../viewer
python3 serve.py
```

## Technical Implementation

### Simulator Architecture

All simulators inherit from `AICallSimulator` base class:

```python
class SeasonalPatternSimulator(AICallSimulator):
    def __init__(self, num_customers, num_days, seed):
        super().__init__(num_customers, num_days, seed)
    
    def generate(self):
        # Custom pattern logic
        # Returns list of AICall objects
```

### CSV Append Logic

```python
csv_file = 'data/simulated_calls.csv'
file_exists = os.path.exists(csv_file)

mode = 'a' if file_exists else 'w'  # Append or write
with open(csv_file, mode, newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[...])
    if not file_exists:
        writer.writeheader()  # Only write header for new file
    for call in simulator.calls:
        writer.writerow(asdict(call))
```

### Auto-Processing Logic

```python
def check_and_process_data():
    data_mtime = os.path.getmtime(data_file)
    manifest_mtime = os.path.getmtime(manifest_file)
    
    if manifest_mtime < data_mtime:
        # Data is newer, regenerate reports
        subprocess.run([sys.executable, 'run_all_analyzers.py'])
```

## Pattern Characteristics

### Seasonal Pattern
- **Weekly**: Mon-Wed (1.3x), Thu-Fri (1.0x), Weekend (0.5x)
- **Daily**: 10am peak (1.4x), 2pm peak (1.3x), night (0.6x)
- **Monthly**: Sine wave with 30-day period

### Burst Traffic
- **Probability**: 15% chance per customer per day
- **Intensity**: 5x-20x normal traffic
- **Duration**: 1-3 hour windows
- **Baseline**: 20% of normal on non-burst days

### Gradual Decline
- **Decline rate**: 3% per week
- **Churn**: 2% probability per customer per day
- **Variability**: 0.7x-1.0x multiplier per customer
- **Minimum**: At least 1 call per active customer

## Benefits

### For Demonstrations
- **Comprehensive**: Shows Revenium handling diverse scenarios
- **Realistic**: Patterns mirror real-world usage
- **Flexible**: Easy to run specific patterns or combinations

### For Analysis
- **Rich dataset**: 220+ customers with varied behaviors
- **Pattern detection**: Analyzers can identify different traffic types
- **Anomaly testing**: Burst and decline patterns test edge cases

### For Development
- **Modular**: Easy to add new patterns
- **Extensible**: Base class provides common functionality
- **Testable**: Fixed seeds ensure reproducibility

## Customization Examples

### Increase Burst Intensity
```python
simulator = BurstTrafficSimulator(num_customers=50, num_days=30, seed=200)
simulator.burst_multiplier = (10, 30)  # 10x-30x instead of 5x-20x
simulator.burst_probability = 0.25     # 25% instead of 15%
```

### Adjust Seasonal Peaks
```python
class CustomSeasonalSimulator(SeasonalPatternSimulator):
    def _apply_seasonal_factor(self, day, hour):
        # Custom peak hours
        if 14 <= hour <= 16:  # 2pm-4pm peak
            daily_factor = 2.0
        # ... rest of logic
```

### Modify Decline Rate
```python
simulator = GradualDeclineSimulator(num_customers=40, num_days=30, seed=300)
simulator.decline_rate = 0.05  # 5% per week instead of 3%
simulator.churn_probability = 0.03  # 3% instead of 2%
```

## Testing

### Verify Data Generation
```bash
cd src
python3 run_all_simulators.py

# Check output
wc -l data/simulated_calls.csv  # Should show ~120K+ lines
```

### Verify Auto-Processing
```bash
# Generate new data
cd src
python3 run_all_simulators.py

# Start viewer (should auto-process)
cd ../viewer
python3 serve.py
# Look for "Processing data with analyzers..." message
```

### Verify Reports
```bash
# Check all reports exist
ls -la src/reports/html/
# Should show 8 HTML files + manifest.json
```

## Troubleshooting

### Issue: Duplicate Customer IDs
**Cause**: Same seed used in multiple simulators
**Solution**: Each simulator has unique seed (42, 100, 200, 300)

### Issue: CSV File Locked
**Cause**: File open in Excel or other program
**Solution**: Close all programs accessing the CSV

### Issue: Reports Not Updating
**Cause**: Viewer not detecting data changes
**Solution**: Delete `src/reports/html/manifest.json` to force regeneration

### Issue: Out of Memory
**Cause**: Too many customers or days
**Solution**: Reduce parameters in simulator initialization

## Future Enhancements

### Potential New Patterns
1. **A/B Test Pattern**: Different usage for control vs variant groups
2. **Geographic Pattern**: Time zone-based usage distribution
3. **Feature Launch Pattern**: Spike followed by sustained increase
4. **Seasonal Spike**: Combination of seasonal + viral patterns

### Advanced Features
1. **Pattern Mixing**: Apply multiple patterns to same customer
2. **Correlation**: Link patterns across customers (viral effects)
3. **Real Data Import**: Replace simulated with actual API logs
4. **ML-Based Generation**: Learn patterns from historical data

## Summary

The new traffic simulators provide:
- ✅ **4 distinct traffic patterns** (base, seasonal, burst, decline)
- ✅ **220+ unique customers** across all patterns
- ✅ **Single CSV output** for unified analysis
- ✅ **Auto-processing viewer** ensures reports stay current
- ✅ **Comprehensive documentation** for usage and customization
- ✅ **Modular architecture** for easy extension

This enhancement demonstrates Revenium's ability to handle diverse real-world scenarios and provide actionable insights regardless of traffic pattern complexity.

---

**For detailed simulator documentation, see [`src/simulator/scenarios/README.md`](src/simulator/scenarios/README.md)**
