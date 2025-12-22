# Data Schema Specification

## Overview

The Revenium FinOps Showcase uses a comprehensive 19-field metadata schema designed to enable multi-dimensional analysis of AI API usage costs. All data is stored in CSV format for portability and simplicity.

## CSV Schema

### Field Definitions

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `timestamp` | ISO 8601 | When the AI call was made | `2025-11-19T08:00:03.794387` |
| `call_id` | String | Unique identifier for this call | `call_20251119080003_7722` |
| `provider` | String | AI provider name | `openai`, `anthropic`, `bedrock` |
| `model` | String | Model identifier | `gpt-4`, `claude-sonnet-4` |
| `input_tokens` | Integer | Number of input tokens | `451` |
| `output_tokens` | Integer | Number of output tokens | `555` |
| `cost_usd` | Float | Cost in USD | `0.016928` |
| `latency_ms` | Integer | Latency in milliseconds | `199` |
| `customer_id` | String | Customer identifier | `cust_0075` |
| `subscription_tier` | String | Subscription tier | `starter`, `pro`, `enterprise` |
| `organization_id` | String | Organization identifier | `org_008` |
| `product_id` | String | Product identifier | `product_a`, `product_b` |
| `feature_id` | String | Feature identifier | `chat`, `code_generation`, `summarization` |
| `task_type` | String | Type of AI task | `chat`, `summarization`, `qa`, etc. |
| `environment` | String | Deployment environment | `production`, `staging`, `development` |
| `request_id` | String | Request tracking ID | `req_147328` |
| `trace_id` | String | Distributed trace ID | `trace_256234` |
| `session_id` | String | User session ID | `sess_41253` |
| `user_agent` | String | Client user agent | `ReveniumSDK/1.0 Python/3.11` |

### Complete Schema Definition

```python
@dataclass
class AICall:
    """Represents a single AI API call with Revenium metadata"""
    timestamp: str           # ISO 8601 timestamp
    call_id: str            # Unique call identifier
    provider: str           # AI provider (openai, anthropic, bedrock)
    model: str              # Model name
    input_tokens: int       # Input token count
    output_tokens: int      # Output token count
    cost_usd: float         # Cost in USD
    latency_ms: int         # Latency in milliseconds
    customer_id: str        # Customer identifier
    subscription_tier: str  # Tier (starter, pro, enterprise)
    organization_id: str    # Organization identifier
    product_id: str         # Product identifier
    feature_id: str         # Feature identifier
    task_type: str          # Task type
    environment: str        # Environment (production, staging, dev)
    request_id: str         # Request tracking ID
    trace_id: str           # Distributed trace ID
    session_id: str         # Session ID
    user_agent: str         # Client user agent
```

## CSV Format

### Example CSV Row

```csv
timestamp,call_id,provider,model,input_tokens,output_tokens,cost_usd,latency_ms,customer_id,subscription_tier,organization_id,product_id,feature_id,task_type,environment,request_id,trace_id,session_id,user_agent
2025-11-19T08:00:03.794387,call_20251119080003_7722,bedrock,claude-v2,451,555,0.016928,199,cust_0075,enterprise,org_008,product_a,chat,chat,production,req_147328,trace_256234,sess_41253,ReveniumSDK/1.0 Python/3.11
```

### File Characteristics

- **Encoding**: UTF-8
- **Line Ending**: Unix (LF)
- **Header**: First row contains field names
- **Delimiter**: Comma (,)
- **Quote Character**: Double quote (") when needed
- **Escape Character**: Backslash (\)

## Metadata Hierarchy

The schema supports hierarchical cost allocation:

```
Organization (org_001, org_002, ...)
  └─ Product (product_a, product_b)
      └─ Feature (chat, code_generation, summarization, ...)
          └─ Customer (cust_0001, cust_0002, ...)
              └─ Subscription Tier (starter, pro, enterprise)
```

This enables queries like:
- "Show me all costs for org_001"
- "What's the cost breakdown by product?"
- "Which features are most expensive per customer?"
- "Compare costs across subscription tiers"

## Field Details

### Core Metrics

#### `timestamp`
- **Format**: ISO 8601 with microseconds
- **Timezone**: UTC assumed
- **Sortable**: Yes (lexicographic)
- **Use Cases**: Time-series analysis, trend detection, forecasting

#### `call_id`
- **Format**: `call_YYYYMMDDHHMMSS_XXXX`
- **Uniqueness**: Guaranteed unique per call
- **Use Cases**: Debugging, correlation, deduplication

#### `cost_usd`
- **Precision**: Up to 6 decimal places
- **Currency**: Always USD
- **Calculation**: `(input_tokens * input_rate + output_tokens * output_rate) / 1000`
- **Use Cases**: Cost analysis, forecasting, profitability

### Provider & Model

#### `provider`
**Valid Values**:
- `openai` - OpenAI API
- `anthropic` - Anthropic API
- `bedrock` - AWS Bedrock

**Use Cases**: Cost comparison, provider optimization, multi-cloud strategy

#### `model`
**Valid Values per Provider**:
- **OpenAI**: `gpt-4`, `gpt-4-turbo`
- **Anthropic**: `claude-opus-4`, `claude-sonnet-4`
- **Bedrock**: `claude-instant`, `claude-v2`

**Use Cases**: Model performance comparison, cost optimization, model switching

### Token Metrics

#### `input_tokens`
- **Range**: 10 - 2000 (typical)
- **Distribution**: Varies by task type
- **Use Cases**: Prompt optimization, cost prediction

#### `output_tokens`
- **Range**: 50 - 1500 (typical)
- **Distribution**: Varies by task type and model
- **Use Cases**: Response optimization, cost analysis

**Total Tokens**: `input_tokens + output_tokens`

**Token Efficiency Metrics**:
- Input/Output Ratio: `input_tokens / output_tokens`
- Cost per 1K tokens: `cost_usd / (total_tokens / 1000)`

### Performance Metrics

#### `latency_ms`
- **Range**: 50 - 5000ms (typical)
- **Distribution**: Varies by model and token count
- **Use Cases**: SLA monitoring, user experience optimization

**Latency Percentiles** (calculated in analysis):
- P50: Median latency
- P95: 95th percentile
- P99: 99th percentile

### Business Dimensions

#### `customer_id`
- **Format**: `cust_XXXX` (4 digits, zero-padded)
- **Cardinality**: 100-220+ unique customers
- **Use Cases**: Customer profitability, usage patterns, churn analysis

#### `subscription_tier`
**Valid Values**:
- `starter` - $29/month
- `pro` - $99/month
- `enterprise` - $299/month

**Use Cases**: Tier profitability, upgrade recommendations, pricing optimization

#### `organization_id`
- **Format**: `org_XXX` (3 digits, zero-padded)
- **Cardinality**: ~10 organizations
- **Use Cases**: Multi-tenant cost allocation, chargeback/showback

#### `product_id`
**Valid Values**:
- `product_a` - Primary product
- `product_b` - Secondary product

**Use Cases**: Product cost allocation, ROI analysis

#### `feature_id`
**Valid Values**:
- `chat` - Chat/conversation features
- `code_generation` - Code generation
- `summarization` - Text summarization
- `translation` - Language translation
- `analysis` - Data/text analysis
- `qa` - Question answering

**Use Cases**: Feature economics, investment decisions, sunset analysis

#### `task_type`
**Valid Values**: Same as `feature_id` (may differ in practice)
- `chat`
- `summarization`
- `code_generation`
- `translation`
- `analysis`
- `qa`

**Difference from `feature_id`**:
- `feature_id`: User-facing feature
- `task_type`: Technical task classification

### Technical Metadata

#### `environment`
**Valid Values**:
- `production` - Production environment (majority)
- `staging` - Staging environment
- `development` - Development environment

**Use Cases**: Environment cost segregation, testing cost tracking

#### `request_id`
- **Format**: `req_XXXXXX` (6 digits)
- **Purpose**: Request-level tracking
- **Use Cases**: Debugging, request correlation

#### `trace_id`
- **Format**: `trace_XXXXXX` (6 digits)
- **Purpose**: Distributed tracing
- **Use Cases**: Multi-service correlation, debugging

#### `session_id`
- **Format**: `sess_XXXXX` (5 digits)
- **Purpose**: User session tracking
- **Use Cases**: Session-based analysis, user journey

#### `user_agent`
- **Format**: `ReveniumSDK/1.0 Python/3.11`
- **Purpose**: Client identification
- **Use Cases**: SDK version tracking, client analytics

## Data Validation Rules

### Required Fields
All 19 fields are required for every record. No null/empty values permitted.

### Type Validation
- **Strings**: Non-empty, reasonable length (<256 chars)
- **Integers**: Positive values only
- **Floats**: Non-negative, reasonable precision
- **Timestamps**: Valid ISO 8601 format

### Range Validation
- `input_tokens`: 1 - 10,000
- `output_tokens`: 1 - 10,000
- `cost_usd`: 0.00001 - 100.00
- `latency_ms`: 10 - 30,000

### Referential Integrity
- `model` must match valid models for `provider`
- `subscription_tier` must be starter/pro/enterprise
- `environment` must be production/staging/development

## Data Generation Patterns

### Customer Archetypes

**Light Users** (70% of customers):
- Calls per day: 5-20
- Typical cost: $3-12/month
- Token usage: Lower
- Subscription: Mostly starter/pro

**Power Users** (20% of customers):
- Calls per day: 50-150
- Typical cost: $35-85/month
- Token usage: Medium
- Subscription: Mostly pro

**Heavy Users** (10% of customers):
- Calls per day: 200-500
- Typical cost: $150-450/month
- Token usage: High
- Subscription: Mostly enterprise

### Temporal Patterns

**Business Hours Effect**:
- Peak usage: 8am - 8pm
- Reduced usage: 8pm - 8am
- Weekend reduction: ~30% lower

**Seasonal Patterns** (in seasonal simulator):
- Weekly cycles
- Monthly trends
- Quarterly variations

## Analysis Dimensions

The schema supports analysis across multiple dimensions:

### Cost Dimensions
- By provider (OpenAI vs Anthropic vs Bedrock)
- By model (gpt-4 vs claude-sonnet-4 vs ...)
- By customer (individual profitability)
- By tier (tier economics)
- By organization (multi-tenant allocation)
- By product (product P&L)
- By feature (feature economics)
- By environment (prod vs staging costs)

### Performance Dimensions
- Latency by model
- Latency by provider
- Tokens per call
- Cost per 1K tokens
- Input/output ratio

### Usage Dimensions
- Calls per customer
- Calls per day/hour
- Task type distribution
- Feature adoption
- Active users

### Time Dimensions
- Hourly patterns
- Daily patterns
- Weekly patterns
- Monthly trends
- Forecasting periods

## Schema Evolution

### Version 1.0 (Current)
- 19 fields as documented
- CSV format
- UTF-8 encoding

### Future Considerations

**Potential New Fields**:
- `error_code` - Track failures
- `retry_count` - Retry attempts
- `cache_hit` - Caching effectiveness
- `model_version` - Specific model versions
- `region` - Geographic region
- `user_id` - Individual user (vs customer)
- `endpoint` - API endpoint called
- `status_code` - HTTP status

**Backward Compatibility**:
- Add new fields to end
- Provide default values
- Update analyzers incrementally
- Maintain v1 support

## Data Quality

### Expected Quality Metrics
- **Completeness**: 100% (no missing fields)
- **Accuracy**: High (simulated but realistic)
- **Consistency**: High (validated rules)
- **Timeliness**: Real-time generation
- **Uniqueness**: No duplicate call_ids

### Data Validation Process
1. Type checking during generation
2. Range validation
3. Referential integrity checks
4. Duplicate detection
5. Statistical sanity checks

## Storage Considerations

### File Size Estimates
- **Per Row**: ~350 bytes average
- **1K calls**: ~350 KB
- **10K calls**: ~3.5 MB
- **100K calls**: ~35 MB
- **1M calls**: ~350 MB

### CSV Performance
- **Read Speed**: ~100K rows/second
- **Write Speed**: ~50K rows/second
- **Memory Usage**: Proportional to dataset size

### Scaling Recommendations
- **< 100K rows**: CSV is optimal
- **100K - 1M rows**: CSV still viable
- **> 1M rows**: Consider Parquet, database

## Related Specifications

- **Architecture**: See `architecture.md`
- **Simulators**: See `simulators.md` for data generation
- **Analyzers**: See `analyzers.md` for data consumption
