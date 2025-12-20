# Revenium FinOps Showcase

A comprehensive Python-based demonstration system that showcases how **Revenium** enables FinOps domains and usage-based revenue (UBR) analysis for AI costs through realistic simulations, API integration examples, and interactive HTML reports.

## 🎯 Project Overview

This showcase demonstrates Revenium's capabilities across:
- **5 FinOps Domains**: Understanding, Performance, Real-time, Optimization, Alignment
- **3 UBR Analyses**: Customer Profitability, Pricing Strategy, Feature Economics
- **Integration Examples**: Real code showing Revenium SDK usage patterns
- **Scenario Demonstrations**: Business problems solved with Revenium

## 🚀 Quick Start

### 1. Generate Simulated Data

**Option A: Run all traffic patterns (recommended)**
```bash
cd src
python3 run_all_simulators.py
```

This generates comprehensive data with 4 different traffic patterns:
- Base traffic (100 customers)
- Seasonal patterns (50 customers)
- Burst traffic (30 customers)
- Gradual decline (40 customers)

**Option B: Run single simulator**
```bash
cd src
python3 simulator/core.py
```

**Output**: `data/simulated_calls.csv`

### 2. Run All Analyzers

```bash
python3 run_all_analyzers.py
```

Executes all analyzers and generates comprehensive HTML reports.

**Output**: Reports in `reports/html/` directory

### 3. View Interactive Reports

```bash
cd ../viewer
python3 serve.py
```

Then open your browser to **http://localhost:8000**

## 📁 Project Structure

```
revenium-flow/
├── README.md                           # This file
├── specs/                              # Detailed specifications
│   ├── project-spec.md                # Complete project specification
│   └── README.md                      # Specification guide
├── src/                               # Core implementation
│   ├── simulator/                     # AI call simulators
│   │   ├── core.py                   # Base traffic simulator
│   │   └── scenarios/                # Traffic pattern simulators
│   │       ├── seasonal_pattern.py   # Cyclical usage patterns
│   │       ├── burst_traffic.py      # Unpredictable bursts
│   │       ├── gradual_decline.py    # Churn/decline patterns
│   │       ├── steady_growth.py      # Linear growth (legacy)
│   │       ├── viral_spike.py        # Viral growth (legacy)
│   │       └── README.md             # Simulator documentation
│   ├── analyzers/                    # Analysis engines
│   │   ├── finops/                   # 5 FinOps domain analyzers
│   │   │   ├── understanding.py      # Cost allocation & forecasting
│   │   │   ├── performance.py        # Model efficiency
│   │   │   ├── realtime.py          # Anomaly detection
│   │   │   ├── optimization.py      # Rate optimization
│   │   │   └── alignment.py         # Org cost tracking
│   │   └── ubr/                      # 3 UBR analyzers
│   │       ├── profitability.py      # Customer margins
│   │       ├── pricing.py            # Pricing strategy
│   │       └── features.py           # Feature economics
│   ├── utils/                        # Utilities
│   │   └── html_generator.py        # HTML report generation
│   ├── data/                         # Generated data (CSV)
│   ├── reports/html/                 # Generated HTML reports
│   ├── run_all_simulators.py        # Run all traffic simulators
│   └── run_all_analyzers.py         # Run all analyzers
├── showcase/                          # Revenium integration examples
│   ├── instrumentation/
│   │   └── revenium_basic.py        # Basic integration example
│   ├── metadata/
│   │   └── builders.py              # Metadata builder library
│   └── scenarios/
│       └── scenario_unprofitable_customers.py
└── viewer/                           # Web-based report viewer
    ├── index.html                    # Interactive viewer
    └── serve.py                      # HTTP server (auto-processes data)
```

## 🎨 Key Features

### 1. Realistic AI Usage Simulation
- **4 Traffic Patterns**: Base, seasonal, burst, decline
- **Multiple customer archetypes**: Light (70%), power (20%), heavy (10%)
- **3 subscription tiers**: Starter ($29), Pro ($99), Enterprise ($299)
- **Multi-provider support**: OpenAI, Anthropic, Bedrock
- **Realistic patterns**: Weekend effects, business hours, cyclical usage
- **220+ unique customers** across all simulators

### 2. Comprehensive Analysis
- **Cost Allocation**: By provider, model, customer, org, product, feature
- **Token Efficiency**: Input/output ratios and cost per 1K tokens
- **Forecasting**: 30-day, 90-day, and annual projections
- **Profitability**: Customer-level margin analysis
- **Recommendations**: Actionable insights for optimization

### 3. Beautiful HTML Reports
- Modern, responsive design
- Interactive web viewer
- Print-friendly layouts
- No external dependencies
- Embedded CSS/JS

### 4. Revenium Integration Examples
- Basic instrumentation patterns
- Metadata builder library
- Hierarchical tagging strategies
- Real-world scenario demonstrations

## 📊 Generated Reports

### FinOps Domain Reports

1. **Understanding Usage & Cost** - Comprehensive cost allocation, forecasting, and token efficiency
2. **Performance Tracking** - Model efficiency comparison and latency analysis (planned)
3. **Real-Time Decision Making** - Cost anomaly detection and optimization opportunities (planned)
4. **Rate Optimization** - Reserved capacity and model switching analysis (planned)
5. **Organizational Alignment** - Cost by org, product, feature with chargebacks (planned)

### Usage-Based Revenue Reports

6. **Customer Profitability** - Cost to serve, margin analysis, unprofitable customer identification
7. **Pricing Strategy** - Pricing model comparison and revenue projections (planned)
8. **Feature Economics** - Feature profitability and investment recommendations (planned)

## 🔧 Revenium Integration Examples

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
        'feature_id': 'chat',
        'subscription_tier': 'pro'
    }
)
```

### Metadata Builder

```python
from showcase.metadata.builders import ReveniumMetadataBuilder

metadata = (ReveniumMetadataBuilder()
    .customer('cust_0001')
    .organization('org_001')
    .product('product_a')
    .feature('chat')
    .tier('pro')
    .environment('production')
    .build())
```

## 🎯 Scenario Demonstrations

### Unprofitable Customer Detection

```bash
cd showcase/scenarios
python3 scenario_unprofitable_customers.py
```

Demonstrates how Revenium identifies customers costing more to serve than subscription revenue, enabling proactive intervention.

## 💡 Key Insights Examples

- **Cost Optimization**: "Switch to claude-sonnet-4 for simple tasks to save $2,340/month"
- **Revenue Protection**: "$18,450/month at risk from 15 unprofitable customers"
- **Pricing Impact**: "Hybrid pricing model increases margin by $12,340/month"
- **Feature Strategy**: "Invest in Code feature (85% margin, 72% adoption)"

## 🛠️ Technical Details

### Requirements
- Python 3.7+
- No external dependencies (uses only Python standard library)

### Data Format
- CSV files for portability and simplicity
- Comprehensive metadata schema
- Git-friendly format

### Simulation Parameters

**Customer Archetypes**:
- Light Users (70%): 5-20 calls/day
- Power Users (20%): 50-150 calls/day
- Heavy Users (10%): 200-500 calls/day

**Subscription Tiers**:
- Starter: $29/month
- Pro: $99/month
- Enterprise: $299/month

**AI Providers & Models**:
- OpenAI: gpt-4, gpt-4-turbo
- Anthropic: claude-opus-4, claude-sonnet-4
- Bedrock: claude-instant, claude-v2

## 📚 Documentation

- [`specs/project-spec.md`](specs/project-spec.md) - Complete project specification
- [`specs/README.md`](specs/README.md) - Specification navigation guide
- [`src/README.md`](src/README.md) - Implementation details

## 🎓 Use Cases

This showcase demonstrates how Revenium enables:

1. **FinOps Practitioners**: Understand AI costs, optimize spending, forecast budgets
2. **Product Managers**: Analyze feature economics, prioritize investments
3. **Finance Teams**: Track profitability, implement chargebacks, optimize pricing
4. **Engineering Teams**: Choose optimal models, detect anomalies, improve efficiency
5. **Executives**: Understand total AI spend, margin impact, strategic opportunities

## 🎯 Traffic Pattern Simulators

### Base Traffic (`simulator/core.py`)
Standard baseline with realistic customer archetypes and subscription tiers.

### Seasonal Pattern (`scenarios/seasonal_pattern.py`)
Cyclical usage with weekly, daily, and monthly patterns. Perfect for enterprise SaaS.

### Burst Traffic (`scenarios/burst_traffic.py`)
Unpredictable bursts (5x-20x) concentrated in short windows. Models batch processing and API integrations.

### Gradual Decline (`scenarios/gradual_decline.py`)
Decreasing usage with churn simulation. Demonstrates retention analysis scenarios.

**See [`src/simulator/scenarios/README.md`](src/simulator/scenarios/README.md) for detailed documentation.**

---

## 🔑 Key Differentiators

### Without Revenium
❌ Manual log parsing from multiple sources
❌ Delayed cost visibility (hours/days)
❌ Complex ETL pipelines
❌ No standardized metadata schema
❌ Provider-specific integration code

### With Revenium
✅ Automatic capture of all AI calls
✅ Real-time cost visibility
✅ Standardized metadata across providers
✅ Single integration point
✅ Built-in aggregation and analysis
✅ Handles diverse traffic patterns automatically

## 🚧 Current Implementation Status

**Completed**:
- ✅ 4 traffic pattern simulators (base, seasonal, burst, decline)
- ✅ Master simulator runner (`run_all_simulators.py`)
- ✅ 8 comprehensive analyzers (5 FinOps + 3 UBR)
- ✅ HTML report generation utilities
- ✅ Interactive web viewer with auto-processing
- ✅ Revenium integration examples
- ✅ Metadata builder library
- ✅ Scenario demonstrations
- ✅ Comprehensive documentation

**Available Analyzers**:
- ✅ FinOps: Understanding, Performance, Real-time, Optimization, Alignment
- ✅ UBR: Customer Profitability, Pricing Strategy, Feature Economics

## 📝 License

This is a demonstration project for showcasing Revenium's FinOps and UBR capabilities.

## 🤝 Contributing

This is a showcase project. For questions or feedback about Revenium, visit [revenium.io](https://revenium.io)

---

**Built with ❤️ to demonstrate Revenium's AI Cost Intelligence Platform**
