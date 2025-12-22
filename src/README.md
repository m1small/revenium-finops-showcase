# Implementation Details

This directory contains the complete Python implementation of the Revenium FinOps Showcase.

## Directory Structure

```
src/
├── simulator/              # AI call simulation
│   ├── core.py            # Base simulator with 7 providers, 20+ models
│   └── scenarios/         # 11 traffic pattern simulators
│       ├── base_traffic.py
│       ├── seasonal_pattern.py
│       ├── burst_traffic.py
│       ├── multi_tenant.py
│       ├── model_migration.py
│       ├── weekend_effect.py
│       ├── timezone_pattern.py
│       ├── feature_launch.py
│       ├── cost_optimization.py
│       ├── gradual_decline.py
│       ├── steady_growth.py
│       └── viral_spike.py
├── analyzers/             # Analysis engines
│   ├── common.py          # Shared utilities
│   └── finops/            # 5 FinOps analyzers
│       └── understanding.py
├── utils/                 # Report generation utilities
├── data/                  # Generated CSV data
├── reports/html/          # Generated HTML reports
├── run_all_simulators.py # Continuous generation orchestrator
└── run_all_analyzers.py  # Analysis report generator
```

## Core Components

### 1. AI Call Simulator (simulator/core.py)

Base simulator class with comprehensive provider/model support:

**7 Providers**:
- OpenAI (40% market share)
- Anthropic (25% market share)
- Google (15% market share)
- AWS Bedrock (10% market share)
- Azure OpenAI (7% market share)
- Mistral (2% market share)
- Cohere (1% market share)

**20+ Models** with realistic pricing:
- Premium: GPT-4, Claude Opus ($0.03-0.075/1K tokens)
- Standard: GPT-4 Turbo, Claude Sonnet ($0.01-0.03/1K tokens)
- Budget: GPT-3.5, Claude Haiku, Gemini Flash ($0.0001-0.005/1K tokens)

**Customer Archetypes**:
- Light users (70%): 5-20 calls/day
- Power users (20%): 50-150 calls/day
- Heavy users (10%): 200-500 calls/day

**Features**:
- Time-of-day multipliers (business hours, evening, night)
- Day-of-week multipliers (weekday/weekend)
- Realistic token distributions
- Latency simulation based on token count

### 2. Traffic Pattern Simulators (simulator/scenarios/)

11 realistic traffic patterns:

1. **Base Traffic**: Standard usage with customer archetypes
2. **Seasonal Pattern**: Cyclical business patterns (quarterly, monthly, weekly)
3. **Burst Traffic**: Unpredictable 5x-20x spikes
4. **Multi-Tenant**: Organization-level variability (3x-10x variance)
5. **Model Migration**: Gradual provider/model shifts (GPT-4 → Claude Sonnet)
6. **Weekend Effect**: Pronounced weekend/holiday reductions
7. **Timezone Pattern**: Global 24-hour coverage (Americas, Europe, Asia-Pacific)
8. **Feature Launch**: Adoption spike with S-curve growth
9. **Cost Optimization**: Engineering-led migration to cheaper models
10. **Gradual Decline**: Customer churn simulation
11. **Steady Growth**: Linear expansion (100% → 200%)
12. **Viral Spike**: Exponential growth event (1x → 50x → 5x)

### 3. Continuous Generation (run_all_simulators.py)

Orchestrates data generation until 50MB target:

- Cycles through all 11 scenarios
- Monitors file size after each scenario
- Stops automatically at 50MB
- Progress bar with percentage tracking
- Generates ~145,000 calls in 8-12 minutes
- ~200-250 calls/second throughput

**Output**: `data/simulated_calls.csv` (50MB)

### 4. Analyzers (analyzers/)

**Common Utilities** (`analyzers/common.py`):
- CSV loading and parsing
- Grouping by multiple dimensions
- Aggregate metrics calculation
- Percentile calculations
- Anomaly detection

**FinOps Analyzers** (`analyzers/finops/`):

1. **Understanding Usage & Cost** (`understanding.py`):
   - Cost allocation (provider, model, customer, feature, organization)
   - 30-day forecasting based on daily rate
   - Token efficiency analysis
   - Top spender identification
   - Optimization recommendations

2. **Performance Tracking** (placeholder):
   - Model efficiency comparisons
   - Latency percentiles (P50, P95, P99)
   - SLA compliance metrics

3. **Real-Time Decision Making** (placeholder):
   - Anomaly detection
   - Budget threshold alerts
   - Portfolio risk assessment

4. **Rate Optimization** (placeholder):
   - Reserved capacity opportunities
   - Model switching recommendations

5. **Organizational Alignment** (placeholder):
   - Multi-tenant cost tracking
   - Chargeback/showback reports

**UBR Analyzers** (`analyzers/ubr/`, placeholders):
6. Customer Profitability
7. Pricing Strategy
8. Feature Economics

### 5. Report Generation (run_all_analyzers.py)

Generates 8 HTML reports with:
- Simple, clean design
- Metric cards and data tables
- Recommendations
- Auto-refresh meta tag (15 seconds)
- Links to other reports

**Index Page** (`reports/html/index.html`):
- Progress bar (0 MB → 50 MB)
- Report cards with descriptions
- Auto-refresh via JavaScript (15 seconds)
- Toast notifications on updates

**Manifest File** (`reports/html/manifest.json`):
- Current data size
- Call count
- Generation timestamp
- Progress percentage

## Usage

### Quick Start

```bash
# Generate data
python3 run_all_simulators.py

# Generate reports
python3 run_all_analyzers.py

# View reports
cd ../viewer
python3 serve.py
# Open http://localhost:8000
```

### Individual Scenarios

```python
from simulator.scenarios.burst_traffic import BurstTrafficSimulator

sim = BurstTrafficSimulator(output_path='data/burst.csv', seed=42)
sim.write_csv_header()
sim.run(duration_hours=48, base_calls_per_hour=60)
```

### Custom Analysis

```python
from analyzers.finops.understanding import UnderstandingAnalyzer

analyzer = UnderstandingAnalyzer('data/simulated_calls.csv')
results = analyzer.analyze()

print(f"Total cost: ${results['summary']['total_cost']:.2f}")
print(f"Top provider: {results['by_provider'][0]['provider']}")
```

## Data Schema

19-field CSV format:

**Core Fields**:
- call_id, timestamp, status, environment, region

**AI Metrics**:
- provider, model, input_tokens, output_tokens, total_tokens, cost_usd, latency_ms

**Business Metadata**:
- customer_id, organization_id, product_id, feature_id, subscription_tier, tier_price_usd, customer_archetype

## Performance

**Generation**:
- ~200-250 calls/second sustained
- ~145,000 calls to reach 50MB
- 8-12 minutes total time
- Memory: 200-300MB peak

**Analysis**:
- Loads full CSV into memory
- 2-5 seconds per report regeneration
- All 8 reports in ~20 seconds

## Extension Points

### Add New Traffic Pattern

1. Create file in `simulator/scenarios/`
2. Inherit from `AICallSimulator`
3. Implement `run()` method
4. Add to `run_all_simulators.py` scenarios list

### Add New Analyzer

1. Create file in `analyzers/finops/` or `analyzers/ubr/`
2. Use `analyzers.common` utilities
3. Return structured results dictionary
4. Add to `run_all_analyzers.py` reports list

### Customize Providers/Models

Edit `simulator/core.py`:
```python
PROVIDERS = {
    'my_provider': {
        'models': {
            'my_model': {'input': 0.01, 'output': 0.02}
        },
        'weight': 0.10
    }
}
```

## Testing

Run validation tests:

```bash
cd ..
python3 test_workflow.py
```

Tests:
- Simulator can generate data
- Analyzer can process data
- Integration examples work

## Dependencies

Pure Python stdlib implementation:
- csv, random, time, datetime
- http.server, socketserver, threading
- subprocess, os, sys, uuid
- collections.defaultdict

External (CDN only):
- Chart.js 4.4.1 (for HTML reports)

No pip install required.
