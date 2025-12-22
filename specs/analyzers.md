# Analysis Engine Specification

## Overview

The analysis engine transforms raw AI usage data into actionable business intelligence through 8 specialized analyzers covering 5 FinOps domains and 3 Usage-Based Revenue (UBR) analyses.

## Analyzer Architecture

### Common Pattern

All analyzers follow a consistent interface:

```python
class Analyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv')
    def load_data(self) -> None
    def analyze(self) -> Dict
    def generate_html_report(self, output_file: str) -> str
```

### Design Principles

1. **Self-Contained**: Each analyzer <400 lines, runs independently
2. **Consistent Interface**: Standard methods across all analyzers
3. **CSV-Based**: Reads from simulated_calls.csv
4. **HTML Output**: Generates beautiful reports with Chart.js
5. **Business-Focused**: Dollar amounts and actionable recommendations

## FinOps Domain Analyzers

### 1. Understanding Usage & Cost

**File**: `src/analyzers/finops/understanding.py`

**Class**: `UnderstandingAnalyzer`

**Purpose**: Comprehensive cost allocation, forecasting, and token efficiency analysis

#### Analysis Components

**Cost Allocation**:
- Total spend by provider (OpenAI, Anthropic, Bedrock)
- Cost breakdown by model
- Cost per customer
- Cost by organization
- Cost by product
- Cost by feature

**Token Efficiency**:
- Input vs output token ratios
- Cost per 1K tokens by model
- Average tokens per call
- Token distribution by task type

**Forecasting**:
- 30-day projection based on daily averages
- 90-day projection with trend analysis
- Annual cost projection
- Confidence intervals

**Time-Series Analysis**:
- Daily cost trends
- Hourly usage patterns
- Day-of-week patterns
- Cumulative cost over time

#### Key Metrics

- **Total Cost**: Sum of all costs
- **Total Tokens**: Input + output tokens
- **Average Cost per Call**: Total cost / call count
- **Cost per 1K Tokens**: By provider and model
- **Daily Burn Rate**: Average daily spend

#### Recommendations Generated

- Model switching opportunities (e.g., "Use claude-sonnet-4 instead of gpt-4 for simple tasks to save $X/month")
- Provider optimization
- Token efficiency improvements
- Forecast alerts (budget overruns)

#### HTML Report Components

- Executive summary card
- Cost breakdown tables
- Provider comparison chart
- Model efficiency chart
- Forecast visualization
- Recommendations section

---

### 2. Performance Tracking

**File**: `src/analyzers/finops/performance.py`

**Class**: `PerformanceAnalyzer`

**Purpose**: Model efficiency comparison and latency analysis

#### Analysis Components

**Model Efficiency**:
- Cost-performance ratio for each model
- Tokens per second by model
- Cost per token by model
- Efficiency score (composite metric)

**Latency Analysis**:
- P50 (median) latency by model
- P95 latency by model
- P99 latency by model
- Latency distribution

**Cost-Performance Tradeoffs**:
- Models ranked by cost efficiency
- Models ranked by speed
- Models ranked by composite score (cost + speed)

**Task Type Analysis**:
- Optimal model recommendations per task type
- Performance by task complexity

#### Key Metrics

- **Latency Percentiles**: P50, P95, P99
- **Tokens per Second**: output_tokens / (latency_ms / 1000)
- **Cost Efficiency Score**: (tokens/second) / (cost per 1K tokens)
- **SLA Compliance**: % of calls under latency threshold

#### Recommendations Generated

- Optimal model per task type
- SLA violation alerts
- Performance improvement opportunities
- Cost-speed tradeoff suggestions

#### HTML Report Components

- Model comparison table
- Latency percentile charts
- Efficiency score visualization
- Task-to-model mapping recommendations

---

### 3. Real-Time Decision Making

**File**: `src/analyzers/finops/realtime.py`

**Class**: `RealtimeAnalyzer`

**Purpose**: Anomaly detection and immediate optimization opportunities

#### Analysis Components

**Cost Anomaly Detection**:
- Identify calls with unusually high costs
- Detect customers exceeding thresholds
- Find inefficient usage patterns
- Spot provider/model anomalies

**Threshold Violations**:
- Customers exceeding budget caps
- Calls above latency SLAs
- Token usage spikes
- Cost per call outliers

**Inefficient Patterns**:
- High-cost models for simple tasks
- Excessive token usage
- Repeated failed calls
- Suboptimal provider selection

**Real-Time Opportunities**:
- Immediate cost savings available
- Quick wins for optimization
- Urgent actions needed

#### Key Metrics

- **Anomaly Count**: Number of anomalous calls
- **Customers at Risk**: Exceeding budgets
- **Potential Savings**: From fixing inefficiencies
- **Threshold Violations**: Count and severity

#### Recommendations Generated

- Immediate actions (e.g., "Contact cust_0042 - usage spike detected")
- Threshold adjustments
- Automated policy suggestions
- Alert configurations

#### HTML Report Components

- Anomaly summary cards
- Top violators table
- Inefficiency analysis
- Action items list

---

### 4. Rate Optimization

**File**: `src/analyzers/finops/optimization.py`

**Class**: `OptimizationAnalyzer`

**Purpose**: Reserved capacity analysis and model switching opportunities

#### Analysis Components

**Reserved Capacity Analysis**:
- Calculate potential savings with reserved instances
- Identify candidates for commitments
- ROI analysis for different commitment levels
- Breakeven analysis

**Model Switching Opportunities**:
- Identify overpowered model usage
- Suggest cheaper alternatives for simple tasks
- Calculate savings from switching
- Risk assessment

**Volume Discount Analysis**:
- Project savings at higher volumes
- Threshold analysis for discount tiers
- Bulk commitment recommendations

**Rate Optimization Strategies**:
- Spot vs on-demand comparison
- Provider arbitrage opportunities
- Geographic pricing differences

#### Key Metrics

- **Reserved Instance Savings**: 20-40% typical
- **Model Switch Savings**: Up to 90% for certain switches
- **Volume Discount Potential**: Based on current usage
- **Total Optimization Potential**: Combined savings

#### Recommendations Generated

- Specific reserved capacity purchases
- Model switching matrix (from → to)
- Commitment amounts and terms
- Implementation priorities

#### HTML Report Components

- Savings potential summary
- Reserved capacity calculator
- Model switching matrix
- ROI charts

---

### 5. Organizational Alignment

**File**: `src/analyzers/finops/alignment.py`

**Class**: `AlignmentAnalyzer`

**Purpose**: Multi-tenant cost tracking and chargeback/showback

#### Analysis Components

**Organization Cost Allocation**:
- Cost by organization
- Product-level breakdown
- Feature-level allocation
- Environment segregation (prod/staging/dev)

**Chargeback Reports**:
- Detailed cost attribution
- Allocation methodology
- Supporting evidence
- Invoice-ready format

**Showback Reports**:
- Cost visibility without billing
- Educational reporting
- Budget awareness
- Optimization opportunities per org

**Cross-Team Efficiency**:
- Compare efficiency across organizations
- Identify best practices
- Share optimization learnings
- Standardization opportunities

#### Key Metrics

- **Cost per Organization**: Total and breakdown
- **Cost per Product**: P&L attribution
- **Cost per Feature**: Investment allocation
- **Efficiency Scores**: By team/org

#### Recommendations Generated

- Chargeback amounts and methodology
- Cross-team optimization opportunities
- Standardization recommendations
- Budget allocation guidance

#### HTML Report Components

- Organization summary table
- Product cost breakdown
- Feature allocation chart
- Chargeback invoices

---

## UBR (Usage-Based Revenue) Analyzers

### 6. Customer Profitability

**File**: `src/analyzers/ubr/profitability.py`

**Class**: `CustomerProfitabilityAnalyzer`

**Purpose**: Customer-level margin analysis and unprofitable customer identification

#### Analysis Components

**Customer Metrics**:
- Revenue (subscription tier)
- Cost to serve (AI usage costs)
- Gross margin (revenue - cost)
- Margin percentage
- Call volume
- Profitability status

**Tier Analysis**:
- Profitability by subscription tier
- Customers per tier
- Average margin per tier
- Tier efficiency

**Unprofitable Customer Identification**:
- Customers with negative margins
- Total loss amount
- Percentage of customer base
- Top 10 worst performers

**Margin Distribution**:
- High margin customers (>50%)
- Medium margin customers (20-50%)
- Low margin customers (0-20%)
- Negative margin customers (<0%)

#### Key Metrics

- **Total Revenue**: Sum of subscription fees
- **Total Cost**: Sum of AI usage costs
- **Gross Margin**: Revenue - Cost
- **Margin Percentage**: (Margin / Revenue) × 100
- **Unprofitable Count**: Customers with margin < 0

#### Recommendations Generated

- Unprofitable customer interventions (caps, upgrades, offboarding)
- Tier upgrade suggestions
- Usage cap implementations
- Pricing adjustments

#### HTML Report Components

- Profitability summary cards
- Customer margin distribution chart (4 interactive charts)
- Unprofitable customer table
- Tier analysis table
- Margin by tier chart
- Customer distribution pie chart

---

### 7. Pricing Strategy

**File**: `src/analyzers/ubr/pricing.py`

**Class**: `PricingStrategyAnalyzer`

**Purpose**: Pricing model comparison and revenue optimization

#### Analysis Components

**Pricing Model Simulations**:

1. **Flat Pricing** (Current):
   - Fixed monthly fee
   - Unlimited usage
   - Simple for customers
   - High variance in profitability

2. **Tiered Pricing**:
   - Base fee + overage charges
   - Included usage allowance
   - Additional per-token pricing
   - Balanced risk/reward

3. **Pure Usage-Based**:
   - No base fee
   - Pay per token consumed
   - Perfect cost alignment
   - Variable revenue

4. **Hybrid Model**:
   - Base fee + cost-plus margin
   - Guarantees minimum margin
   - Scales with usage
   - Best margin protection

**Revenue Projections**:
- Model revenue under each pricing strategy
- Customer segment impact
- Churn risk assessment
- Implementation complexity

**Customer Segmentation**:
- Low-usage customers
- Medium-usage customers
- High-usage customers
- Impact per segment

#### Key Metrics

- **Revenue per Model**: Total revenue under each strategy
- **Margin per Model**: Gross margin percentage
- **Customer Impact**: Winners and losers per model
- **Churn Risk**: Customers likely to churn

#### Recommendations Generated

- Optimal pricing model selection
- Migration strategy
- Customer communication approach
- Grandfathering policies

#### HTML Report Components

- Pricing model comparison table
- Revenue projection chart
- Customer impact analysis
- Migration roadmap

---

### 8. Feature Economics

**File**: `src/analyzers/ubr/features.py`

**Class**: `FeatureEconomicsAnalyzer`

**Purpose**: Feature-level cost analysis and investment prioritization

#### Analysis Components

**Feature Cost Analysis**:
- Total cost per feature
- Cost per customer per feature
- Feature adoption rate
- Feature usage frequency

**Feature Profitability**:
- Revenue attribution per feature
- Cost to provide feature
- Feature margin
- ROI calculation

**Adoption Analysis**:
- Customers using each feature
- Adoption percentage
- Power users per feature
- Feature stickiness

**Investment Recommendations**:
- **Invest**: High margin, high adoption
- **Maintain**: Medium margin, medium adoption
- **Optimize**: Low margin, high adoption
- **Sunset**: Low margin, low adoption

**Bundle Opportunities**:
- Features commonly used together
- Cross-sell opportunities
- Package pricing ideas

#### Key Metrics

- **Cost per Feature**: Total AI costs attributed
- **Adoption Rate**: % of customers using
- **Cost per Customer**: Average cost per adopting customer
- **Feature Margin**: If feature-specific pricing exists
- **Feature Efficiency**: Cost relative to value

#### Recommendations Generated

- Investment priorities (invest, maintain, optimize, sunset)
- Feature bundling strategies
- Pricing adjustments per feature
- Development roadmap guidance

#### HTML Report Components

- Feature cost summary card
- Feature cost breakdown chart (2 interactive charts)
- Adoption analysis table
- Investment matrix
- Bundle recommendations
- Cost per customer chart

---

## Master Analyzer Runner

**File**: `src/run_all_analyzers.py`

**Purpose**: Execute all analyzers in sequence and generate comprehensive reports

### Execution Order

1. FinOps: Understanding Usage & Cost
2. FinOps: Performance Tracking
3. FinOps: Real-Time Decision Making
4. FinOps: Rate Optimization
5. FinOps: Organizational Alignment
6. UBR: Customer Profitability
7. UBR: Pricing Strategy
8. UBR: Feature Economics

### Workflow

```python
1. Check for data/simulated_calls.csv
2. For each analyzer:
   a. Initialize analyzer
   b. Run analysis
   c. Generate HTML report
   d. Save to reports/html/
   e. Print status
3. Update manifest.json with metadata
4. Print summary statistics
```

### Output

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

... (continues for all 8 analyzers)

======================================================================
📊 ANALYSIS COMPLETE
======================================================================

⏱️  Total time: 4.56 seconds
✅ Successful: 8
❌ Failed: 0
```

### Manifest Generation

**File**: `reports/html/manifest.json`

**Purpose**: Metadata for web viewer navigation

**Structure**:
```json
{
  "generated_at": "2025-12-19T10:30:00",
  "reports": [
    {
      "id": "finops_understanding",
      "title": "FinOps: Understanding Usage & Cost",
      "category": "finops",
      "filename": "finops_understanding.html",
      "description": "Cost allocation, forecasting, and token efficiency"
    },
    ...
  ],
  "categories": {
    "finops": "FinOps Domain Analysis",
    "ubr": "Usage-Based Revenue Analysis"
  }
}
```

## Common Utilities

### CSV Loading

```python
def load_data(self):
    """Load and parse CSV data"""
    with open(self.csv_file, 'r') as f:
        reader = csv.DictReader(f)
        self.calls = list(reader)

    # Type conversions
    for call in self.calls:
        call['cost_usd'] = float(call['cost_usd'])
        call['input_tokens'] = int(call['input_tokens'])
        call['output_tokens'] = int(call['output_tokens'])
        call['latency_ms'] = int(call['latency_ms'])
```

### Aggregation Helpers

```python
from collections import defaultdict

# Group by provider
by_provider = defaultdict(lambda: {'cost': 0, 'calls': 0})
for call in self.calls:
    provider = call['provider']
    by_provider[provider]['cost'] += call['cost_usd']
    by_provider[provider]['calls'] += 1

# Group by customer
by_customer = defaultdict(lambda: {'cost': 0, 'tier': None})
for call in self.calls:
    customer = call['customer_id']
    by_customer[customer]['cost'] += call['cost_usd']
    by_customer[customer]['tier'] = call['subscription_tier']
```

### Statistical Functions

```python
def percentile(data: List[float], p: int) -> float:
    """Calculate percentile"""
    sorted_data = sorted(data)
    index = int(len(sorted_data) * p / 100)
    return sorted_data[index]

# Usage
latencies = [call['latency_ms'] for call in calls]
p50 = percentile(latencies, 50)
p95 = percentile(latencies, 95)
p99 = percentile(latencies, 99)
```

## Error Handling

### Data Validation

```python
def validate_data(self):
    """Validate loaded data"""
    if not self.calls:
        raise ValueError("No data loaded")

    required_fields = ['timestamp', 'cost_usd', 'customer_id', ...]
    for call in self.calls:
        for field in required_fields:
            if field not in call:
                raise ValueError(f"Missing field: {field}")

    # Type validation
    for call in self.calls:
        if call['cost_usd'] < 0:
            raise ValueError("Negative cost detected")
```

### Graceful Degradation

```python
try:
    result = self.analyze()
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    result = {"error": str(e)}
    # Continue with partial results
```

## Performance Optimization

### Single-Pass Processing

```python
# Instead of multiple loops
for call in calls:
    # Calculate all metrics in one pass
    total_cost += call['cost_usd']
    by_provider[call['provider']]['cost'] += call['cost_usd']
    by_customer[call['customer_id']]['cost'] += call['cost_usd']
```

### Memory Efficiency

```python
# Use generators for large datasets
def iter_calls():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Process in chunks
for call in iter_calls():
    process(call)
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(customer_id):
    # Cached per customer
    return result
```

## Testing

### Unit Tests

```python
def test_analyzer():
    analyzer = UnderstandingAnalyzer('test_data.csv')
    result = analyzer.analyze()

    assert 'total_cost' in result
    assert result['total_cost'] > 0
    assert len(result['by_provider']) == 3  # OpenAI, Anthropic, Bedrock
```

### Integration Tests

```python
def test_full_workflow():
    # Generate test data
    simulator = AICallSimulator(num_customers=10, num_days=7)
    simulator.run()

    # Run analyzer
    analyzer = UnderstandingAnalyzer()
    result = analyzer.analyze()

    # Validate report generation
    html = analyzer.generate_html_report('test_report.html')
    assert os.path.exists('test_report.html')
```

## Best Practices

1. **Consistent Patterns**: All analyzers follow same structure
2. **Comprehensive Docs**: Each method has docstring
3. **Type Hints**: Use type annotations throughout
4. **Error Handling**: Validate inputs, handle edge cases
5. **Performance**: Single-pass processing where possible
6. **Modularity**: Each analyzer is self-contained
7. **Business Focus**: Output dollar amounts and recommendations
8. **Visualization**: Include charts in HTML reports

## Extensibility

### Adding a New Analyzer

1. Create file in `analyzers/finops/` or `analyzers/ubr/`
2. Implement standard interface
3. Add business logic in `analyze()`
4. Generate HTML with charts
5. Add to `run_all_analyzers.py`
6. Update manifest categories

### Example Template

```python
class NewAnalyzer:
    def __init__(self, csv_file: str = 'data/simulated_calls.csv'):
        self.csv_file = csv_file
        self.calls = []

    def load_data(self):
        # Standard CSV loading
        pass

    def analyze(self) -> Dict:
        # Your analysis logic
        return {
            'metric1': value1,
            'metric2': value2,
            'recommendations': [...]
        }

    def generate_html_report(self, output_file: str) -> str:
        # Use HTMLReportGenerator
        pass
```

## Related Specifications

- **Data Schema**: See `data-schema.md`
- **Reports**: See `reports.md`
- **Architecture**: See `architecture.md`
