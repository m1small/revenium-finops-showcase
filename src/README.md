# Revenium FinOps Showcase

A Python-based demonstration system that simulates AI API usage and analyzes costs through FinOps domains and usage-based revenue (UBR) perspectives.

## Overview

This showcase generates realistic AI usage data and produces comprehensive business insights across:
- **5 FinOps Domains**: Understanding, Performance, Real-time, Optimization, Alignment
- **3 UBR Analyses**: Profitability, Pricing Strategy, Feature Economics

## Quick Start

### 1. Generate Simulated Data

```bash
cd src
python simulator.py
```

This creates 30 days of AI call data for 100 customers across multiple providers (OpenAI, Anthropic, Bedrock).

**Output**: `data/simulated_calls.csv`

### 2. Run All Analyzers

```bash
python run_all_analyzers.py
```

This executes all 8 analyzers and generates comprehensive reports.

**Output**: 8 markdown reports in `reports/` directory

### 3. Run Individual Analyzers

You can also run analyzers individually:

```bash
# FinOps Analyzers
python analyzers/finops/understanding.py
python analyzers/finops/performance.py
python analyzers/finops/realtime.py
python analyzers/finops/optimization.py
python analyzers/finops/alignment.py

# UBR Analyzers
python analyzers/ubr/profitability.py
python analyzers/ubr/pricing.py
python analyzers/ubr/features.py
```

## Project Structure

```
src/
├── simulator.py                    # Generate AI call data
├── run_all_analyzers.py           # Run all analyzers at once
├── analyzers/
│   ├── finops/
│   │   ├── understanding.py       # Cost allocation & forecasting
│   │   ├── performance.py         # Model efficiency analysis
│   │   ├── realtime.py           # Anomaly detection & alerts
│   │   ├── optimization.py       # Rate optimization opportunities
│   │   └── alignment.py          # Organizational cost tracking
│   └── ubr/
│       ├── profitability.py      # Customer margin analysis
│       ├── pricing.py            # Pricing model simulation
│       └── features.py           # Feature economics & ROI
├── data/
│   └── simulated_calls.csv       # Generated usage data
└── reports/
    ├── finops_understanding.md
    ├── finops_performance.md
    ├── finops_realtime.md
    ├── finops_optimization.md
    ├── finops_alignment.md
    ├── customer_profitability.md
    ├── pricing_strategy.md
    └── feature_economics.md
```

## Generated Reports

### FinOps Domain Reports

1. **Understanding Usage & Cost** (`finops_understanding.md`)
   - Total spend by provider, model, customer
   - Cost allocation hierarchy (org → product → customer)
   - Token efficiency metrics
   - 30-day cost forecast

2. **Performance Tracking** (`finops_performance.md`)
   - Model efficiency comparison
   - Latency analysis (P50, P95, P99)
   - Cost-performance tradeoffs
   - Optimal model recommendations per task

3. **Real-Time Decision Making** (`finops_realtime.md`)
   - Cost anomaly detection
   - Customer threshold violations
   - Inefficient usage patterns
   - Immediate optimization opportunities

4. **Rate Optimization** (`finops_optimization.md`)
   - Reserved capacity analysis (30% savings potential)
   - Model switching opportunities
   - Commitment recommendations
   - Volume discount analysis

5. **Organizational Alignment** (`finops_alignment.md`)
   - Cost by organization, product, feature
   - Chargeback/showback reports
   - Budget vs actual tracking
   - Cross-team efficiency comparison

### Usage-Based Revenue Reports

6. **Customer Profitability** (`customer_profitability.md`)
   - Cost to serve each customer
   - Margin analysis and distribution
   - Unprofitable customer identification
   - Customer lifetime value projections

7. **Pricing Strategy** (`pricing_strategy.md`)
   - Comparison of 4 pricing models:
     - Flat pricing (current)
     - Tiered pricing (base + overage)
     - Pure usage-based
     - Hybrid (base + cost-plus)
   - Revenue impact projections
   - Customer segment analysis

8. **Feature Economics** (`feature_economics.md`)
   - Cost per feature
   - Feature profitability analysis
   - Usage distribution and adoption rates
   - Investment recommendations (invest/maintain/sunset)
   - Bundle opportunities

## Simulation Parameters

### Customer Archetypes
- **Light Users** (70%): 5-20 calls/day, $3-12/month cost
- **Power Users** (20%): 50-150 calls/day, $35-85/month cost
- **Heavy Users** (10%): 200-500 calls/day, $150-450/month cost

### Subscription Tiers
- **Starter**: $29/month
- **Pro**: $99/month
- **Enterprise**: $299/month

### AI Providers & Models
- **OpenAI**: gpt-4, gpt-4-turbo
- **Anthropic**: claude-opus-4, claude-sonnet-4
- **Bedrock**: claude-instant, claude-v2

### Task Types
- Chat, Summarization, Code Generation, Translation, Analysis, Q&A

## Key Insights Examples

Each report provides quantified business insights such as:

- **Cost Optimization**: "Switch to claude-sonnet-4 for simple tasks to save $2,340/month"
- **Revenue Protection**: "$18,450/month at risk from 15 unprofitable customers"
- **Pricing Impact**: "Hybrid pricing model increases margin by $12,340/month"
- **Feature Strategy**: "Invest in Code feature (85% margin, 72% adoption)"

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)

## Use Cases

This showcase demonstrates how Revenium enables:

1. **FinOps Practitioners**: Understand AI costs, optimize spending, forecast budgets
2. **Product Managers**: Analyze feature economics, prioritize investments
3. **Finance Teams**: Track profitability, implement chargebacks, optimize pricing
4. **Engineering Teams**: Choose optimal models, detect anomalies, improve efficiency
5. **Executives**: Understand total AI spend, margin impact, strategic opportunities

## Customization

You can customize the simulation by editing parameters in `simulator.py`:

```python
# Change customer count and simulation period
simulator = AICallSimulator(num_customers=200, num_days=60)

# Modify pricing models
SUBSCRIPTION_TIERS = {
    'starter': 49,
    'pro': 149,
    'enterprise': 499
}
```

## Notes

- All data is simulated - no real API calls are made
- No database required - uses CSV files
- Reports are markdown files for easy sharing
- Each script is self-contained and <300 lines
- Focus on business insights over technical implementation

## License

This is a demonstration project for showcasing Revenium's FinOps and UBR capabilities.
