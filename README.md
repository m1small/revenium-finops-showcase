# Revenium FinOps Showcase

A comprehensive Python-based demonstration system showcasing how Revenium enables FinOps domains and usage-based revenue analysis for AI costs through realistic simulations, continuous data generation, and live-updating reports.

## Project Overview

This showcase demonstrates Revenium's capabilities across:
- **5 FinOps Domains**: Understanding, Performance, Real-time, Optimization, Alignment
- **3 UBR Analyses**: Customer Profitability, Pricing Strategy, Feature Economics
- **Real-Time Alerting**: Budget thresholds, portfolio risk assessment, proactive notifications
- **Multi-Dimensional Analysis**: Cross-functional cost/performance insights with Chart Builder
- **OpenTelemetry Integration**: Unified observability and FinOps platform

## Key Enhancements

**Diverse Multi-Provider Coverage**:
- 7 AI providers (OpenAI, Anthropic, Google, Bedrock, Azure, Mistral, Cohere)
- 20+ models with 200x pricing variance
- Market-weighted distribution (OpenAI 40%, Anthropic 25%, Google 15%)

**Variable Real-World Patterns**:
- 11 traffic scenarios (seasonal, burst, multi-tenant, model migration, time zones, feature launches, cost optimization)
- Global time zone patterns with 24-hour coverage
- Weekend/holiday effects and business hour cycles

**Continuous Generation**:
- Automatic data generation to 50MB (~145,000 calls)
- Live-updating viewer with progress tracking
- Auto-regenerating reports every 10 seconds
- Real-time notifications and visual progress bar

## Quick Start

### 1. Generate Continuous Data (Target: 50MB)

```bash
cd src
python3 run_all_simulators.py
```

The simulator continuously generates diverse traffic patterns until reaching 50MB:
- Cycles through all 10 scenario simulators
- Monitors file size and stops at 50MB
- Generates ~145,000 calls with 500+ unique customers
- Takes approximately 8-12 minutes

Output: `data/simulated_calls.csv` (50MB with comprehensive metadata)

### 2. Start Live-Updating Viewer

```bash
cd viewer
python3 serve.py
```

Then open browser to **http://localhost:8000**

The viewer continuously updates as data grows:
- Server monitors CSV every 10 seconds
- Auto-runs analyzers when size increases
- Client polls for updates every 15 seconds
- Progress bar shows 0-50MB status
- Toast notifications on report updates

### 3. View Interactive Reports

Browser displays:
- Live progress indicator (X MB / 50 MB)
- Auto-refreshing report cards
- Real-time update notifications
- 8 comprehensive analysis reports

## Project Structure

```
revenium-flow/
├── README.md                          # This file
├── specs/                             # Detailed specifications
│   ├── README.md                      # Specification guide
│   ├── architecture.md                # System design & continuous updates
│   ├── simulators.md                  # Traffic simulation (7 providers, 11 patterns)
│   ├── analyzers.md                   # Analysis engines & real-time alerting
│   ├── integration.md                 # OTEL & Chart Builder integration
│   ├── reports.md                     # Continuous viewer & UI design
│   ├── data-schema.md                 # 19-field metadata schema
│   ├── workflows.md                   # User workflows
│   └── requirements.md                # Technical requirements
├── src/                               # Implementation (deleted in current state)
│   ├── simulator/                     # AI call simulators
│   │   ├── core.py                   # Base simulator
│   │   └── scenarios/                # 11 traffic patterns
│   ├── analyzers/                     # 8 analysis engines
│   │   ├── finops/                   # 5 FinOps analyzers
│   │   └── ubr/                      # 3 UBR analyzers
│   ├── utils/                        # HTML report generation
│   ├── data/                         # Generated CSV (50MB)
│   └── reports/html/                 # Generated reports
├── showcase/                          # Integration examples
│   ├── instrumentation/              # Basic & OTEL tracking
│   ├── metadata/                     # Metadata builders
│   ├── queries/                      # Chart Builder examples
│   └── scenarios/                    # Business scenarios
└── viewer/                           # Live-updating web viewer
    ├── index.html                    # Interactive UI
    └── serve.py                      # Continuous monitoring server
```

## Key Features

### 1. Diverse Multi-Provider Simulation
- **7 Providers**: OpenAI, Anthropic, Google, Bedrock, Azure, Mistral, Cohere
- **20+ Models**: From budget (Gemini Flash $0.000075/1K) to premium (Claude Opus $0.075/1K)
- **Market-Realistic Distribution**: Weighted by actual market share
- **500+ Customers** across organizations, tiers, and products

### 2. Variable Traffic Patterns
- **Base Traffic**: Standard usage with customer archetypes
- **Seasonal Pattern**: Cyclical business cycles (quarterly, monthly, weekly)
- **Burst Traffic**: Unpredictable 5x-20x spikes
- **Multi-Tenant**: Organization-level variability (3x-10x variance)
- **Model Migration**: Gradual provider/model shifts
- **Weekend Effect**: Realistic weekend/holiday reductions
- **Time Zone Patterns**: Global 24-hour coverage
- **Feature Launch**: Adoption spike patterns
- **Cost Optimization**: Engineering-led cost reductions
- **Gradual Decline**: Customer churn simulation

### 3. Continuous Generation & Monitoring
- **Size-Limited**: Automatically stops at 50MB
- **Progress Tracking**: Real-time file size monitoring
- **Balanced Mix**: Equal representation from all patterns
- **Reproducible**: Same seed produces identical dataset

### 4. Live-Updating Viewer
- **Server Monitoring**: Background thread checks CSV every 10 seconds
- **Auto-Regeneration**: Runs analyzers when data grows
- **Client Polling**: JavaScript checks manifest every 15 seconds
- **Progress Bar**: Visual 0-50MB indicator with color changes
- **Toast Notifications**: Updates appear automatically
- **Non-Blocking**: Browse reports while new ones generate

### 5. Comprehensive Analysis
**FinOps Analyzers**:
- Understanding: Cost allocation, forecasting, token efficiency
- Performance: Model efficiency, latency analysis
- Real-Time: Anomaly detection, threshold alerts, portfolio risk
- Optimization: Reserved capacity, model switching
- Alignment: Multi-tenant cost tracking, chargeback

**UBR Analyzers**:
- Profitability: Customer margins, unprofitable detection
- Pricing: 4 pricing model comparisons
- Features: Feature economics, ROI analysis

### 6. Real-Time Alerting
- Budget threshold alerts (e.g., "usage > 30% of revenue")
- Portfolio risk assessment with trending indicators
- Multi-channel notifications (Email, Slack, Webhook)
- Bulk anomaly queries (up to 50 IDs)
- Proactive cost management

### 7. Advanced Integration Patterns
**OpenTelemetry Integration**:
- OTEL AI metrics in JSON format
- Trace-level analytics with cost correlation
- Distributed workflow cost tracking
- 5-minute integration setup

**Multi-Dimensional Analysis**:
- Chart Builder for reusable configurations
- Cross-functional insights (cost + performance + usage)
- Workspace collaboration with custom display names
- Team-wide chart sharing

## Generated Reports

### FinOps Domain Reports
1. **Understanding Usage & Cost**: Comprehensive allocation, forecasting, efficiency
2. **Performance Tracking**: Model efficiency, latency percentiles, SLA compliance
3. **Real-Time Decision Making**: Anomaly detection, threshold alerts, portfolio risk
4. **Rate Optimization**: Reserved capacity, model switching opportunities
5. **Organizational Alignment**: Multi-tenant tracking, chargeback/showback

### Usage-Based Revenue Reports
6. **Customer Profitability**: Margin analysis, unprofitable customer detection
7. **Pricing Strategy**: 4 pricing model comparisons, revenue projections
8. **Feature Economics**: Feature profitability, investment recommendations

## Integration Examples

### Basic Instrumentation
```python
from showcase.instrumentation.revenium_basic import ReveniumBasicTracker

tracker = ReveniumBasicTracker(api_key="your-api-key")
call_id = tracker.track_ai_call(
    provider="openai",
    model="gpt-4",
    input_tokens=150,
    output_tokens=300,
    cost_usd=0.0135,
    latency_ms=1250,
    metadata={
        'customer_id': 'cust_0001',
        'organization_id': 'org_001',
        'product_id': 'product_a',
        'feature_id': 'chat'
    }
)
```

### OpenTelemetry Integration
```python
from showcase.instrumentation.revenium_otel import ReveniumOTELIntegration

revenium_otel = ReveniumOTELIntegration(
    revenium_endpoint="https://otel.revenium.io/v1/traces",
    api_key="your-api-key"
)

trace_id = revenium_otel.track_ai_completion(
    ai_response=response,
    context={'customer_id': 'cust_0001', 'feature_id': 'chat'}
)
```

### Chart Builder
```python
from showcase.queries.chart_builder import ReveniumChartBuilder

builder = ReveniumChartBuilder(api_key="your-api-key")
chart_id = builder.build_multi_dimensional_chart(
    dimensions=['organization_id', 'product_id', 'model'],
    metrics=['cost_usd', 'total_tokens'],
    filters={'environment': 'production'},
    visualization_type='treemap',
    name='Org-Product-Model Cost Hierarchy'
)
```

## Key Insights Examples

- **Cost Optimization**: "Switch to claude-sonnet-4 for simple tasks to save $2,340/month"
- **Revenue Protection**: "$18,450/month at risk from 15 unprofitable customers"
- **Real-Time Alert**: "Customer cust_0042 at 89% of Pro tier allocation with 10 days remaining"
- **Pricing Impact**: "Hybrid pricing model increases margin by $12,340/month"
- **Feature Strategy**: "Invest in Code feature (85% margin, 72% adoption)"
- **Migration ROI**: "GPT-4 to Claude Sonnet migration saves $15,200/month"

## Technical Details

### Requirements
- Python 3.7+
- No external dependencies (stdlib only)
- Chart.js 4.4.1 (loaded via CDN)

### Data Format
- CSV with 19-field metadata schema
- ~350 bytes per call
- 50MB target = ~145,000 calls
- Git-friendly text format

### Performance
- **Generation**: ~8-12 minutes to 50MB
- **Throughput**: ~200-250 calls/second sustained
- **Memory**: ~200-300MB peak
- **Report Updates**: ~2-5 seconds per regeneration

### Customer Archetypes
- Light Users (70%): 5-20 calls/day
- Power Users (20%): 50-150 calls/day
- Heavy Users (10%): 200-500 calls/day

### Subscription Tiers
- Starter: $29/month
- Pro: $99/month
- Enterprise: $299/month

## Use Cases by Role

**FinOps Practitioners**: Understand AI costs across 7 providers, optimize spending, forecast budgets, set threshold alerts

**Product Managers**: Analyze feature economics, track adoption patterns, prioritize investments with ROI data

**Finance Teams**: Track customer profitability, implement chargebacks, optimize pricing with 4 model comparisons

**Engineering Teams**: Choose optimal models, detect anomalies in real-time, improve efficiency with OTEL integration

**Executives**: Understand total AI spend, margin impact, strategic opportunities with portfolio risk assessment

## Documentation

- [`specs/README.md`](specs/README.md) - Specification navigation guide
- [`specs/architecture.md`](specs/architecture.md) - System design & continuous updates
- [`specs/simulators.md`](specs/simulators.md) - Traffic simulation (7 providers, 11 patterns)
- [`specs/analyzers.md`](specs/analyzers.md) - Analysis engines & real-time alerting
- [`specs/integration.md`](specs/integration.md) - OTEL & Chart Builder integration
- [`specs/reports.md`](specs/reports.md) - Continuous viewer & UI design

## Key Differentiators

### Without Revenium
- Manual log parsing from multiple sources
- Delayed cost visibility (hours/days)
- Complex ETL pipelines for each provider
- No standardized metadata schema
- Provider-specific integration code
- Static reports requiring manual refresh

### With Revenium
- Automatic capture across 7 providers
- Real-time cost visibility with live updates
- Standardized metadata (19 fields)
- Single integration point (5-minute setup)
- Built-in aggregation and analysis
- Live-updating reports with progress tracking
- OTEL integration for unified observability
- Proactive alerting before cost overruns

## Implementation Status

Current state: **Specifications Complete, Implementation Deleted**

The repository contains comprehensive specifications for:
- 7-provider simulator with 11 traffic patterns
- 8 analysis engines (5 FinOps + 3 UBR)
- Continuous monitoring server with live updates
- Real-time alerting system
- OTEL integration patterns
- Multi-dimensional Chart Builder
- Interactive web viewer with auto-refresh

Ready for implementation from detailed specifications.

## License

Demonstration project for showcasing Revenium's FinOps and UBR capabilities.

## Contact

For questions about Revenium, visit [revenium.io](https://revenium.io)
