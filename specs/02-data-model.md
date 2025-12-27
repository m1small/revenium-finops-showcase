# Data Model Specification

## CSV Schema

### Record Structure

Each API call record contains 19 fields representing a complete transaction.

#### Field Definitions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| timestamp | ISO 8601 DateTime | When the API call occurred | Required, sortable |
| organization_id | String | Unique organization identifier | Format: org-{uuid} |
| product_id | String | Product making the API call | One of: saas-platform, api-service, mobile-app |
| feature_id | String | Specific feature using AI | One of: chat, summarization, translation, code-generation, analysis |
| customer_id | String | End customer identifier | Format: cust-{uuid} |
| customer_archetype | String | Customer usage profile | One of: light, power, heavy |
| subscription_tier | String | Customer pricing tier | One of: starter, pro, enterprise |
| tier_price_usd | Float | Monthly subscription price | 49.0, 199.0, or 999.0 |
| provider | String | AI API provider | One of: openai, anthropic, google, aws-bedrock, azure, mistral, cohere |
| model | String | Specific model used | Provider-dependent, 20+ options |
| region | String | Geographic region | One of: us-east, us-west, eu-west, ap-southeast |
| input_tokens | Integer | Tokens in request | Range: 50-2000 |
| output_tokens | Integer | Tokens in response | Range: 50-1000 |
| total_tokens | Integer | Sum of input + output | Computed field |
| latency_ms | Float | Request duration | Range: 50-5000 milliseconds |
| cost_usd | Float | API call cost | Computed from tokens * model rate |
| status | String | Call outcome | One of: success, error |
| error_type | String | Error classification | When status=error: timeout, rate_limit, auth_error, server_error |
| metadata | String | Additional context | JSON string, optional |

### Data Generation Rules

#### Timestamp Generation
- Sequential timestamps with realistic gaps
- Time-based multipliers for business hours
- Weekend reduction factors
- Timezone-aware patterns for global distribution

#### Token Distribution
Input tokens:
- Mean: 500 tokens
- Standard deviation: 400 tokens
- Minimum: 50 tokens
- Maximum: 2000 tokens
- Distribution: Normal (clamped)

Output tokens:
- Mean: 300 tokens
- Standard deviation: 200 tokens
- Minimum: 50 tokens
- Maximum: 1000 tokens
- Distribution: Normal (clamped)

#### Cost Calculation
```
cost_usd = (input_tokens / 1000) * input_price + (output_tokens / 1000) * output_price
```

Model pricing (per 1K tokens):
- Input range: $0.000075 to $0.015
- Output range: $0.0003 to $0.075
- 200x variance between cheapest and most expensive

#### Latency Simulation
Base latency calculation:
```
base_latency = (total_tokens / 10) + random(50, 200)
```

Regional multipliers:
- us-east: 1.0x (baseline)
- us-west: 1.1x
- eu-west: 1.3x
- ap-southeast: 1.5x

Provider variance: +/- 20% random variation

#### Error Rate
- Default success rate: 95%
- Error distribution:
  - timeout: 40%
  - rate_limit: 30%
  - auth_error: 15%
  - server_error: 15%

## Configuration Model

### System Constants

```
TARGET_SIZE_MB = 50.0
DATA_CSV_PATH = "data/simulated_calls.csv"
REPORT_DIR = "reports/html"
VIEWER_PORT = 8000
```

### Performance Thresholds

```
SLA_THRESHOLD_MS = 2000
P95_THRESHOLD_MS = 1500
P99_THRESHOLD_MS = 2500
```

### Profitability Thresholds

```
HIGH_MARGIN_THRESHOLD_PCT = 50.0
MEDIUM_MARGIN_THRESHOLD_PCT = 20.0
LOW_MARGIN_THRESHOLD_PCT = 0.0
UNPROFITABLE_THRESHOLD_PCT = 0.0
```

### Cost Analysis Thresholds

```
HIGH_COST_THRESHOLD_USD = 100.0
ANOMALY_MULTIPLIER = 3.0
```

### Efficiency Thresholds

```
EFFICIENCY_HIGH_THRESHOLD = 0.8
EFFICIENCY_MEDIUM_THRESHOLD = 0.6
```

### Customer Archetypes Distribution

```
light: 70% of customers
power: 20% of customers
heavy: 10% of customers
```

Archetype multipliers for call volume:
- light: 0.3x
- power: 1.0x (baseline)
- heavy: 3.0x

### Subscription Tiers

| Tier | Monthly Price | Expected Distribution |
|------|---------------|----------------------|
| starter | $49 | 40% |
| pro | $199 | 45% |
| enterprise | $999 | 15% |

### Provider Distribution

Market share simulation:
- openai: 40%
- anthropic: 25%
- google: 15%
- aws-bedrock: 10%
- azure: 7%
- mistral: 2%
- cohere: 1%

### Model Catalog

#### OpenAI
- gpt-4: $0.03/$0.06 (input/output per 1K tokens)
- gpt-4-turbo: $0.01/$0.03
- gpt-3.5-turbo: $0.0005/$0.0015

#### Anthropic
- claude-3-opus: $0.015/$0.075
- claude-3-sonnet: $0.003/$0.015
- claude-3-haiku: $0.00025/$0.00125

#### Google
- gemini-pro: $0.00025/$0.0005
- gemini-ultra: $0.001/$0.002

#### AWS Bedrock
- claude-v2: $0.008/$0.024
- titan-text: $0.0008/$0.0016

#### Azure OpenAI
- gpt-4-azure: $0.03/$0.06
- gpt-35-turbo-azure: $0.0005/$0.0015

#### Mistral
- mistral-medium: $0.0027/$0.0081

#### Cohere
- command: $0.001/$0.002

## Analysis Data Structures

### Aggregated Metrics

Common structure returned by aggregate_metrics():
```
{
    "call_count": Integer,
    "total_cost": Float,
    "total_tokens": Integer,
    "total_input_tokens": Integer,
    "total_output_tokens": Integer,
    "avg_cost_per_call": Float,
    "avg_tokens_per_call": Float,
    "avg_latency_ms": Float,
    "p50_latency_ms": Float,
    "p95_latency_ms": Float,
    "p99_latency_ms": Float
}
```

### Grouping Keys

Common grouping dimensions:
- By provider: Single field
- By model: (provider, model) tuple
- By customer: (customer_id,) tuple
- By feature: (feature_id,) tuple
- By organization: (organization_id,) tuple
- By tier: (subscription_tier, tier_price_usd) tuple
- By region: (region,) tuple
- By archetype: (customer_archetype,) tuple

### Time-Based Analysis

Time series buckets:
- Hourly: Group by hour truncation
- Daily: Group by date
- Weekly: Group by week number
- Monthly: Group by month

Trend calculation:
```
change_percent = ((current - previous) / previous) * 100
```

### Percentile Calculation

For latency analysis:
- Sort latencies ascending
- P50: value at position (count * 0.50)
- P95: value at position (count * 0.95)
- P99: value at position (count * 0.99)

## Constraint Validation

### Required Validations

1. Timestamp must be parseable ISO 8601 format
2. All numeric fields must be non-negative
3. total_tokens must equal input_tokens + output_tokens
4. Subscription tier must match tier_price_usd
5. Provider must have corresponding model
6. Region must be from defined set
7. Customer archetype must be from defined set

### Business Rule Validations

1. Cost must be reasonable given tokens and model
2. Latency should correlate with token count
3. Error status must have error_type
4. Success status must not have error_type
