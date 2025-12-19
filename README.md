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

```bash
cd src
python3 simulator/core.py
```

This creates 30 days of AI call data for 100 customers across multiple providers (OpenAI, Anthropic, Bedrock).

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
│   ├── simulator/                     # AI call simulator
│   │   ├── core.py                   # Main simulator
│   │   └── scenarios/                # Scenario generators
│   │       ├── steady_growth.py
│   │       └── viral_spike.py
│   ├── analyzers/                    # Analysis engines
│   │   ├── finops/
│   │   │   └── understanding.py      # Cost allocation & forecasting
│   │   └── ubr/
│   │       └── profitability.py      # Customer margin analysis
│   ├── utils/                        # Utilities
│   │   └── html_generator.py        # HTML report generation
│   ├── data/                         # Generated data (CSV)
│   ├── reports/html/                 # Generated HTML reports
│   └── run_all_analyzers.py         # Main runner script
├── showcase/                          # Revenium integration examples
│   ├── instrumentation/
│   │   └── revenium_basic.py        # Basic integration example
│   ├── metadata/
│   │   └── builders.py              # Metadata builder library
│   └── scenarios/
│       └── scenario_unprofitable_customers.py
└── viewer/                           # Web-based report viewer
    ├── index.html                    # Interactive viewer
    └── serve.py                      # HTTP server
```

## 🎨 Key Features

### 1. Realistic AI Usage Simulation
- Multiple customer archetypes (light, power, heavy users)
- 3 subscription tiers (starter, pro, enterprise)
- Multi-provider support (OpenAI, Anthropic, Bedrock)
- Realistic token distributions and costs
- Weekend/weekday patterns

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

## 🚧 Current Implementation Status

**Completed**:
- ✅ Core simulator with realistic data generation
- ✅ Scenario generators (steady growth, viral spike)
- ✅ HTML report generation utilities
- ✅ FinOps: Understanding Usage & Cost analyzer
- ✅ UBR: Customer Profitability analyzer
- ✅ Interactive web viewer
- ✅ Revenium integration examples
- ✅ Metadata builder library
- ✅ Scenario demonstrations

**Planned** (see specs for details):
- 🔄 Additional FinOps analyzers (4 more)
- 🔄 Additional UBR analyzers (2 more)
- 🔄 More integration examples
- 🔄 Query pattern examples
- 🔄 Additional scenarios

## 📝 License

This is a demonstration project for showcasing Revenium's FinOps and UBR capabilities.

## 🤝 Contributing

This is a showcase project. For questions or feedback about Revenium, visit [revenium.io](https://revenium.io)

---

**Built with ❤️ to demonstrate Revenium's AI Cost Intelligence Platform**
