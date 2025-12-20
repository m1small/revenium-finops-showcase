# Revenium FinOps Showcase - Quick Start Guide

Get up and running with the Revenium FinOps Showcase in 5 minutes!

## 🚀 Quick Start (3 Steps)

### Step 1: Generate Simulated Data

**Option A: All Traffic Patterns (Recommended)**
```bash
cd src
python3 run_all_simulators.py
```

**What this does:**
- Runs 4 different traffic pattern simulators
- Generates comprehensive dataset with 220+ customers
- Creates diverse usage patterns (base, seasonal, burst, decline)
- Outputs to `data/simulated_calls.csv`

**Expected output:**
```
🚀 RUNNING ALL TRAFFIC PATTERN SIMULATORS
======================================================================

📊 Running: Base Traffic Pattern
----------------------------------------------------------------------
✅ Generated 45,234 calls and saved to data/simulated_calls.csv

📊 Running: Seasonal Pattern
----------------------------------------------------------------------
✅ Appended to data/simulated_calls.csv

📊 Running: Burst Traffic
----------------------------------------------------------------------
✅ Appended to data/simulated_calls.csv

📊 Running: Gradual Decline
----------------------------------------------------------------------
   Churned Customers: 8 (20.0%)
✅ Appended to data/simulated_calls.csv

======================================================================
📊 SIMULATION COMPLETE
======================================================================

📈 Combined Dataset Statistics:
   Total Calls: 120,456
   Unique Customers: 220
   Total Cost: $22,345.67
   Total Tokens: 34,567,890
   Avg Cost/Call: $0.1854
```

**Option B: Single Pattern (Quick Test)**
```bash
cd src
python3 simulator/core.py
```

### Step 2: Run Analyzers

```bash
python3 run_all_analyzers.py
```

**What this does:**
- Runs all 8 analyzers (5 FinOps + 3 UBR)
- Processes all CSV data regardless of traffic pattern
- Generates beautiful HTML reports
- Creates a manifest for the web viewer

**Expected output:**
```
======================================================================
🚀 REVENIUM FINOPS SHOWCASE - RUNNING ALL ANALYZERS
======================================================================

✅ Found existing data: data/simulated_calls.csv

📊 Running: FinOps: Understanding Usage & Cost
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_understanding.html

📊 Running: FinOps: Performance Tracking
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_performance.html

📊 Running: FinOps: Real-Time Decision Making
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_realtime.html

📊 Running: FinOps: Rate Optimization
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_optimization.html

📊 Running: FinOps: Organizational Alignment
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_alignment.html

📊 Running: UBR: Customer Profitability
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/customer_profitability.html

📊 Running: UBR: Pricing Strategy
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/pricing_strategy.html

📊 Running: UBR: Feature Economics
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/feature_economics.html

======================================================================
📊 ANALYSIS COMPLETE
======================================================================

⏱️  Total time: 4.56 seconds
✅ Successful: 8
❌ Failed: 0
```

### Step 3: View Reports

```bash
cd ../viewer
python3 serve.py
```

**What this does:**
- Checks if data exists and is processed
- Automatically runs analyzers if data changed
- Starts a local web server on port 8000
- Serves the interactive report viewer

**Expected output:**
```
======================================================================
🌐 REVENIUM FINOPS SHOWCASE - REPORT VIEWER
======================================================================

📊 Processing data with analyzers...

✅ All data processed successfully

🚀 Starting server on port 8000...

📊 Open your browser to: http://localhost:8000/viewer/index.html

Press Ctrl+C to stop the server
======================================================================
```

Then open your browser to **http://localhost:8000/viewer/index.html** and explore the reports!

**Note**: The viewer automatically processes any new or updated data before serving reports.

## 📚 What's Next?

### Explore Traffic Patterns

Run individual simulators to see specific patterns:

```bash
cd src

# Seasonal patterns (business cycles)
python3 simulator/scenarios/seasonal_pattern.py

# Burst traffic (batch processing)
python3 simulator/scenarios/burst_traffic.py

# Gradual decline (churn analysis)
python3 simulator/scenarios/gradual_decline.py
```

### Explore Integration Examples

```bash
# Basic Revenium instrumentation
cd showcase/instrumentation
python3 revenium_basic.py

# Metadata builder patterns
cd ../metadata
python3 builders.py

# Query pattern examples
cd ../queries
python3 cost_allocation.py
```

### Run Scenario Demonstrations

```bash
# Unprofitable customer detection scenario
cd showcase/scenarios
python3 scenario_unprofitable_customers.py
```

### Customize the Simulation

Each simulator can be customized:

```python
# Example: Increase burst intensity
simulator = BurstTrafficSimulator(
    num_customers=50,      # More customers
    num_days=60,           # Longer period
    seed=200               # Reproducible results
)
simulator.burst_multiplier = (10, 30)  # 10x-30x bursts
```

See [`src/simulator/scenarios/README.md`](src/simulator/scenarios/README.md) for detailed customization options.

## 🎯 Key Files to Explore

| File | Description |
|------|-------------|
| [`src/run_all_simulators.py`](src/run_all_simulators.py) | Master simulator runner |
| [`src/simulator/core.py`](src/simulator/core.py) | Base traffic simulator |
| [`src/simulator/scenarios/seasonal_pattern.py`](src/simulator/scenarios/seasonal_pattern.py) | Seasonal traffic patterns |
| [`src/simulator/scenarios/burst_traffic.py`](src/simulator/scenarios/burst_traffic.py) | Burst traffic patterns |
| [`src/simulator/scenarios/gradual_decline.py`](src/simulator/scenarios/gradual_decline.py) | Decline/churn patterns |
| [`src/run_all_analyzers.py`](src/run_all_analyzers.py) | Master analyzer runner |
| [`src/analyzers/finops/understanding.py`](src/analyzers/finops/understanding.py) | Cost allocation analyzer |
| [`src/analyzers/ubr/profitability.py`](src/analyzers/ubr/profitability.py) | Customer profitability analyzer |
| [`showcase/instrumentation/revenium_basic.py`](showcase/instrumentation/revenium_basic.py) | Basic integration example |
| [`showcase/metadata/builders.py`](showcase/metadata/builders.py) | Metadata builder library |
| [`viewer/serve.py`](viewer/serve.py) | Auto-processing report server |
| [`viewer/index.html`](viewer/index.html) | Interactive report viewer |

## 🔧 Troubleshooting

### Port 8000 already in use?

```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port by editing viewer/serve.py
```

### No data found?

```bash
# Make sure you're in the src directory
cd src
python3 simulator/core.py
```

### Import errors?

```bash
# Make sure you're running from the correct directory
# Simulator should be run from src/
# Viewer should be run from viewer/
```

## 💡 Tips

1. **Start Fresh**: Run `run_all_simulators.py` to clear and regenerate all data
2. **Mix Patterns**: All simulators append to same CSV for comprehensive analysis
3. **Compare Patterns**: Run individual simulators to see specific traffic behaviors
4. **Auto-Processing**: Viewer automatically detects and processes new data
5. **Custom Analysis**: Modify analyzers to focus on specific metrics
6. **Export Data**: CSV files can be opened in Excel/Google Sheets for additional analysis

## 📖 Full Documentation

- [`README.md`](README.md) - Complete project overview
- [`specs/project-spec.md`](specs/project-spec.md) - Detailed specification
- [`src/README.md`](src/README.md) - Implementation details

## 🎓 Learning Path

1. ✅ **Quick Start** (you are here)
2. 📊 **Explore Reports** - View generated HTML reports
3. 🔧 **Try Examples** - Run integration and query examples
4. 🎯 **Run Scenarios** - Execute business scenario demonstrations
5. 📚 **Read Specs** - Understand the full architecture
6. 🚀 **Customize** - Adapt for your use case

## 🤝 Need Help?

- Check the main [`README.md`](README.md) for detailed information
- Review [`specs/project-spec.md`](specs/project-spec.md) for architecture details
- Explore code examples in `showcase/` directory

---

**Ready to see Revenium in action? Start with Step 1 above! 🚀**
