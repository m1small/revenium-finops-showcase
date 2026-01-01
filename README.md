# Revenium FinOps Showcase

## Purpose

This system demonstrates AI cost management and financial operations analysis through realistic data simulation and multi-dimensional reporting. The application generates simulated AI API usage data, analyzes costs across multiple perspectives, and produces interactive HTML reports with actionable insights.

## System Overview

The showcase implements three core capabilities:

**Data Simulation**: Generates realistic AI API call patterns across 7 providers (OpenAI, Anthropic, Google, AWS Bedrock, Azure, Mistral, Cohere) with 20+ models. Includes 12 traffic scenarios simulating real-world patterns such as seasonal variation, burst traffic, multi-tenant usage, and model migration.

**Analysis Engine**: Processes simulated data through 13 specialized analyzers organized into three domains: FinOps (5 analyzers), Usage-Based Revenue (3 analyzers), and Advanced Analytics (5 analyzers). Each analyzer produces structured data and actionable recommendations.

**Report Generation**: Converts analysis results into interactive HTML reports with Chart.js visualizations. Includes a live web interface for monitoring data generation progress and viewing reports.

## Technical Architecture

The system uses a zero-dependency architecture built entirely on Python standard library. Data storage uses CSV format for git-friendly, human-readable persistence. Components are stateless and can run independently. The web viewer provides real-time monitoring and on-demand report regeneration.

**Key Components**:
- Configuration: Centralized constants in `src/config.py`
- Simulator: Traffic generation engine in `src/simulator/`
- Analyzers: Business logic in `src/analyzers/`
- Generators: HTML report creation in `src/generators/`
- Viewer: HTTP server in `viewer/serve.py`

## Quick Start

### Prerequisites

Python 3.7 or later. No external dependencies required beyond Python standard library.

### Generate Data

```bash
cd src
python3 run_all_simulators.py
```

This generates continuous traffic data until reaching the configured target size (default: 50MB, approximately 145,000 API calls). The simulator cycles through all 12 scenarios, creating realistic patterns with market-weighted provider distribution. Output file: `data/simulated_calls.csv`

Optional: Specify custom target size in megabytes:
```bash
python3 run_all_simulators.py 100
```

### Run Analysis

```bash
python3 run_all_analyzers.py
```

This executes all 13 analyzers sequentially, generating HTML reports in `reports/html/`. Creates an index page listing all reports and a manifest file with generation metadata.

### Start Viewer

```bash
cd ../viewer
python3 serve.py
```

Access the web interface at `http://localhost:8000`. The viewer monitors CSV file growth, displays generation progress, and provides links to all generated reports. Background monitoring automatically regenerates reports as data grows.

### Run Individual Analyzer

```bash
cd src
python3 run_analyzer.py <analyzer_id>
```

Available analyzer IDs: understanding, performance, realtime, optimization, alignment, profitability, pricing, features, dataset_overview, token_economics, geographic_latency, churn_growth, abuse_detection.

## Analysis Domains

### FinOps Domain

**Understanding Usage & Cost**: Cost allocation by provider, model, customer, and feature. Includes forecasting and efficiency analysis.

**Performance Tracking**: Latency analysis with percentiles, model efficiency ranking, and SLA compliance tracking.

**Real-Time Decision Making**: Anomaly detection, cost threshold alerts, and portfolio risk assessment.

**Rate Optimization**: Reserved capacity recommendations and model switching opportunities for cost reduction.

**Organizational Alignment**: Multi-tenant cost tracking, chargeback calculations, and fair-share allocation.

### Usage-Based Revenue Domain

**Customer Profitability**: Margin analysis per customer with profitability categorization and unprofitable customer detection.

**Pricing Strategy**: Comparison of four pricing models (flat rate, usage-based, tiered, hybrid) with revenue projections.

**Feature Economics**: Feature-level cost analysis, ROI calculation, and investment prioritization recommendations.

### Advanced Analytics Domain

**Dataset Overview**: Comprehensive statistics including file information, scale metrics, temporal range, and quality metrics.

**Token Economics**: Token-level efficiency analysis, wasteful pattern detection, and optimization opportunities by model.

**Geographic Latency**: Regional performance analysis, provider-region performance matrix, and routing recommendations.

**Churn & Growth**: Customer lifecycle analysis, weekly growth trends, and cohort retention tracking.

**Abuse Detection**: Unusual usage pattern detection, rate limit abuse identification, cost spike alerts, and suspicious access patterns.

## Data Model

Each API call record contains 19 fields: timestamp, organization_id, product_id, feature_id, customer_id, customer_archetype, subscription_tier, tier_price_usd, provider, model, region, input_tokens, output_tokens, total_tokens, latency_ms, cost_usd, status, error_type, metadata.

Provider distribution follows market share: OpenAI 40%, Anthropic 25%, Google 15%, AWS Bedrock 10%, Azure 7%, Mistral 2%, Cohere 1%. Model pricing ranges from $0.000075 to $0.075 per 1K tokens, representing 200x variance.

Customer archetypes: Light (70%), Power (20%), Heavy (10%). Subscription tiers: Starter $49/month (40%), Pro $199/month (45%), Enterprise $999/month (15%).

## Configuration

All system constants are defined in `src/config.py`:
- Target data size: 50 MB
- Data file path: data/simulated_calls.csv
- Report directory: reports/html
- Viewer port: 8000
- Performance thresholds (SLA, latency percentiles)
- Profitability thresholds (margin categories)
- Cost analysis thresholds (anomaly detection)

Modify this file to adjust system behavior. Changes require process restart.

## File Structure

```
/
├── data/                   Generated CSV files
├── reports/html/           Generated HTML reports
├── src/                    Source code
│   ├── config.py          Configuration constants
│   ├── analyzers/         Analysis engines (13 analyzers)
│   ├── generators/        HTML report generators
│   ├── simulator/         Data generation (core + 12 scenarios)
│   ├── utils/             Shared utilities
│   └── run_*.py           Orchestration scripts
├── viewer/                Web interface
│   └── serve.py           HTTP server with monitoring
├── specs/                 Technical specifications
└── tests/                 Test files
```

## Specifications

Complete technical specifications are available in `specs/` directory. These provide language-agnostic descriptions suitable for reimplementation:

- 00-overview.md: System summary and implementation guidelines
- 01-system-architecture.md: Component design and interactions
- 02-data-model.md: CSV schema and configuration model
- 03-simulation-engine.md: Traffic generation algorithms
- 04-analysis-algorithms.md: FinOps and UBR analysis logic
- 05-advanced-analytics.md: Advanced analyzer algorithms
- 06-report-generation.md: HTML template system
- 07-web-interface.md: HTTP server and APIs
- 08-integration-contracts.md: Component contracts

Specifications use pseudocode and mathematical notation to enable reproduction in any programming language.

## Extending the System

### Add New Analyzer

1. Create analyzer class in `src/analyzers/` implementing standard interface
2. Create generator function in `src/generators/` following template
3. Add entry to ANALYZER_REGISTRY in `src/run_analyzer.py`
4. Update orchestration in `src/run_all_analyzers.py`

### Add New Scenario

1. Create scenario class in `src/simulator/scenarios/`
2. Implement scenario-specific multiplier logic
3. Add to scenarios list in `src/run_all_simulators.py`

### Add New Provider

1. Update PROVIDER_WEIGHTS in `src/config.py`
2. Add model catalog with pricing in simulator core
3. No other code changes required

## Performance Characteristics

Data generation: 1000+ calls per second with batch writing (5000 records per batch). Analysis time scales with dataset size: small datasets (<10MB) analyze in under 1 second per analyzer, large datasets (2GB) take up to 30 seconds per analyzer. Memory usage is linear with batch size. Report generation produces 50-200 KB HTML files with embedded visualizations.

The system has been tested with datasets up to 2GB containing millions of API call records.

## Deployment

### Local Development

```bash
cd viewer
python3 serve.py
# Access at http://localhost:8000
```

### GitHub Pages Static Hosting

The application automatically deploys to GitHub Pages via GitHub Actions when code is pushed to the `main` branch.

**Deployment Process:**
1. GitHub Actions workflow (`.github/workflows/deploy-github-pages.yml`) triggers on push to main
2. Workflow executes:
   - Generates 2GB CSV dataset (via `run_all_simulators.py 2048`)
   - Runs all 13 analyzers (via `run_all_analyzers.py`)
   - Creates static index.html for GitHub Pages hosting
3. Deploys `reports/html/` directory to GitHub Pages

**Build artifacts:** `reports/html/` (all HTML reports + index)
**Build time:** ~15-20 minutes

**Setup Requirements:**
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Workflow will run automatically on push to main

**Manual Deployment:**
You can also trigger deployment manually via the GitHub Actions tab in your repository.

## License

This is a demonstration system for showcasing Revenium FinOps capabilities.
