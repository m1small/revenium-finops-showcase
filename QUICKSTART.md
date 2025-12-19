# Revenium FinOps Showcase - Quick Start Guide

Get up and running with the Revenium FinOps Showcase in 5 minutes!

## 🚀 Quick Start (3 Steps)

### Step 1: Generate Simulated Data

```bash
cd src
python3 simulator/core.py
```

**What this does:**
- Generates 30 days of realistic AI usage data
- Creates 100 customer profiles across 3 subscription tiers
- Simulates calls to OpenAI, Anthropic, and Bedrock
- Outputs to `data/simulated_calls.csv`

**Expected output:**
```
🚀 Starting AI Call Simulator...
   Customers: 100
   Days: 30

✅ Generated 45,234 calls and saved to data/simulated_calls.csv

📊 Summary Statistics:
   Total Calls: 45,234
   Total Cost: $8,456.78
   Total Tokens: 12,345,678
   Avg Cost/Call: $0.1870
```

### Step 2: Run Analyzers

```bash
python3 run_all_analyzers.py
```

**What this does:**
- Runs all FinOps and UBR analyzers
- Generates beautiful HTML reports
- Creates a manifest for the web viewer

**Expected output:**
```
======================================================================
🚀 REVENIUM FINOPS SHOWCASE - RUNNING ALL ANALYZERS
======================================================================

📊 Running: FinOps: Understanding Usage & Cost
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/finops_understanding.html

📊 Running: UBR: Customer Profitability
----------------------------------------------------------------------
✅ Generated HTML report: reports/html/customer_profitability.html

======================================================================
📊 ANALYSIS COMPLETE
======================================================================

⏱️  Total time: 2.34 seconds
✅ Successful: 2
❌ Failed: 0
```

### Step 3: View Reports

```bash
cd ../viewer
python3 serve.py
```

**What this does:**
- Starts a local web server on port 8000
- Serves the interactive report viewer

**Expected output:**
```
======================================================================
🌐 REVENIUM FINOPS SHOWCASE - REPORT VIEWER
======================================================================

🚀 Starting server on port 8000...

📊 Open your browser to: http://localhost:8000

Press Ctrl+C to stop the server
======================================================================
```

Then open your browser to **http://localhost:8000** and explore the reports!

## 📚 What's Next?

### Explore Integration Examples

```bash
# Basic Revenium instrumentation
cd ../showcase/instrumentation
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
cd ../scenarios
python3 scenario_unprofitable_customers.py
```

### Customize the Simulation

Edit `src/simulator/core.py` to adjust:
- Number of customers
- Simulation period
- Customer archetypes
- Subscription pricing
- Provider/model mix

Example:
```python
simulator = AICallSimulator(
    num_customers=200,  # More customers
    num_days=60,        # Longer period
    seed=42             # Reproducible results
)
```

## 🎯 Key Files to Explore

| File | Description |
|------|-------------|
| [`src/simulator/core.py`](src/simulator/core.py) | AI call simulator |
| [`src/analyzers/finops/understanding.py`](src/analyzers/finops/understanding.py) | Cost allocation analyzer |
| [`src/analyzers/ubr/profitability.py`](src/analyzers/ubr/profitability.py) | Customer profitability analyzer |
| [`showcase/instrumentation/revenium_basic.py`](showcase/instrumentation/revenium_basic.py) | Basic integration example |
| [`showcase/metadata/builders.py`](showcase/metadata/builders.py) | Metadata builder library |
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

1. **Start Fresh**: Delete `data/simulated_calls.csv` to regenerate with different seed
2. **Compare Scenarios**: Run simulator with different parameters and compare results
3. **Custom Analysis**: Modify analyzers to focus on specific metrics
4. **Export Data**: CSV files can be opened in Excel/Google Sheets for additional analysis

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
