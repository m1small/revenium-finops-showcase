# Quick Start Guide

Get the Revenium FinOps Showcase running in 3 steps.

## Prerequisites

- Python 3.7 or higher
- No external dependencies required (stdlib only)

## Step 1: Generate Continuous Data (50MB Target)

```bash
cd src
python3 run_all_simulators.py
```

This will:
- Cycle through all 11 traffic pattern simulators
- Generate realistic AI API calls across 7 providers and 20+ models
- Monitor file size and stop automatically at 50MB
- Create ~145,000 calls with 500+ unique customers
- Take approximately 8-12 minutes

Output: `data/simulated_calls.csv` (50MB)

## Step 2: Start Live-Updating Viewer

```bash
cd viewer
python3 serve.py
```

Then open your browser to: **http://localhost:8000**

The viewer will:
- Display live progress (0 MB → 50 MB)
- Auto-refresh reports every 15 seconds
- Show toast notifications when reports update
- Regenerate analysis every 10 seconds as data grows

## Step 3: Explore Reports

The viewer displays 8 comprehensive reports:

### FinOps Domain Reports

1. **Understanding Usage & Cost**
   - Cost allocation across providers, models, customers
   - 30-day forecasting
   - Token efficiency analysis

2. **Performance Tracking**
   - Model efficiency comparisons
   - Latency percentiles (P50, P95, P99)
   - SLA compliance metrics

3. **Real-Time Decision Making**
   - Anomaly detection
   - Budget threshold alerts
   - Portfolio risk assessment

4. **Rate Optimization**
   - Reserved capacity opportunities
   - Model switching recommendations
   - Cost reduction strategies

5. **Organizational Alignment**
   - Multi-tenant cost tracking
   - Chargeback/showback reports
   - Organization-level analysis

### Usage-Based Revenue Reports

6. **Customer Profitability**
   - Margin analysis per customer
   - Unprofitable customer detection
   - Revenue vs. cost comparison

7. **Pricing Strategy**
   - 4 pricing model comparisons
   - Revenue projections
   - Optimal pricing recommendations

8. **Feature Economics**
   - Feature profitability analysis
   - Adoption vs. cost metrics
   - Investment ROI recommendations

## Advanced Usage

### Run Individual Scenario

```bash
cd src
python3 -c "
from simulator.scenarios.burst_traffic import BurstTrafficSimulator
sim = BurstTrafficSimulator(output_path='data/burst_test.csv')
sim.write_csv_header()
sim.run(duration_hours=24, base_calls_per_hour=100)
"
```

### Run Single Analyzer

```bash
cd src
python3 -c "
from analyzers.finops.understanding import UnderstandingAnalyzer
analyzer = UnderstandingAnalyzer('data/simulated_calls.csv')
results = analyzer.analyze()
print(results['summary'])
"
```

### Integration Examples

See `showcase/` directory for:
- Basic instrumentation (`showcase/instrumentation/revenium_basic.py`)
- OpenTelemetry integration (`showcase/instrumentation/revenium_otel.py`)
- Chart Builder (`showcase/queries/chart_builder.py`)

## Troubleshooting

### No data file found

Run Step 1 first to generate data.

### Port 8000 already in use

Change port in `viewer/serve.py`:
```python
port = 8080  # Or any available port
```

### Reports not updating

Check that:
- Simulator is running in `src/` directory
- CSV file is growing in `src/data/simulated_calls.csv`
- Viewer server is running with monitoring thread active

## What's Next

- Review generated reports in browser
- Explore integration examples in `showcase/`
- Read detailed specifications in `specs/`
- Customize simulators for your use case

## Support

For questions or issues:
- Check `specs/README.md` for detailed documentation
- Review `README.md` for complete feature overview
- Visit https://revenium.io for production platform details
