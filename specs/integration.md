# Revenium SDK Integration Specification

## Overview

The showcase layer demonstrates real-world Revenium SDK integration patterns, metadata builders, query examples, and business scenario walkthroughs. These examples show how customers would integrate Revenium into their production applications.

## Integration Architecture

**Location**: `showcase/`

**Purpose**: Provide reference implementations for Revenium integration

**Components**:
1. **Instrumentation** - Basic tracking patterns
2. **Metadata Builders** - Fluent API for metadata construction
3. **Query Patterns** - Common aggregation queries
4. **Scenarios** - Business use case demonstrations

## Basic Instrumentation

**File**: `showcase/instrumentation/revenium_basic.py`

**Class**: `ReveniumBasicTracker`

**Purpose**: Simplest Revenium integration pattern

### Implementation

```python
class ReveniumBasicTracker:
    """Basic Revenium integration pattern"""

    def __init__(self, api_key: str):
        """
        Initialize Revenium tracker

        Args:
            api_key: Your Revenium API key
        """
        self.api_key = api_key
        self.endpoint = "https://api.revenium.io/v1/track"

    def track_ai_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Track an AI API call with Revenium

        Args:
            provider: AI provider (openai, anthropic, bedrock)
            model: Model name (gpt-4, claude-sonnet-4, etc)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            metadata: Additional metadata for cost allocation

        Returns:
            call_id: Unique identifier for this call
        """
        call_id = str(uuid.uuid4())

        # Build tracking payload
        payload = {
            'call_id': call_id,
            'timestamp': time.time(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost_usd,
            'latency_ms': latency_ms,
            'metadata': metadata
        }

        # In production: POST to Revenium API
        # requests.post(self.endpoint, json=payload, headers={...})

        return call_id
```

### Usage Example

```python
from showcase.instrumentation.revenium_basic import ReveniumBasicTracker

# Initialize tracker
tracker = ReveniumBasicTracker(api_key="your-api-key")

# Track AI call
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
        'subscription_tier': 'pro',
        'environment': 'production'
    }
)

print(f"Tracked call: {call_id}")
```

### Integration Points

**OpenAI Integration**:
```python
import openai
from showcase.instrumentation.revenium_basic import ReveniumBasicTracker

tracker = ReveniumBasicTracker(api_key="...")

# Make OpenAI call
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Track with Revenium
tracker.track_ai_call(
    provider="openai",
    model="gpt-4",
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens,
    cost_usd=calculate_cost(response.usage),
    latency_ms=response.response_time_ms,
    metadata={'customer_id': current_user.id, ...}
)
```

**Anthropic Integration**:
```python
import anthropic
from showcase.instrumentation.revenium_basic import ReveniumBasicTracker

tracker = ReveniumBasicTracker(api_key="...")
client = anthropic.Anthropic(api_key="...")

# Make Anthropic call
message = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

# Track with Revenium
tracker.track_ai_call(
    provider="anthropic",
    model="claude-sonnet-4",
    input_tokens=message.usage.input_tokens,
    output_tokens=message.usage.output_tokens,
    cost_usd=calculate_anthropic_cost(message.usage),
    latency_ms=elapsed_time_ms,
    metadata={'customer_id': current_user.id, ...}
)
```

## OpenTelemetry Integration

**File**: `showcase/instrumentation/revenium_otel.py`

**Purpose**: Leverage existing OpenTelemetry infrastructure for Revenium tracking

**Key Differentiator**: Revenium accepts OTEL AI metrics in JSON format, enabling seamless integration with existing observability stacks. This positions Revenium as a unified observability + FinOps platform, not just a billing tool.

### Benefits for Engineering Teams

- **No Separate Instrumentation**: Leverage existing OTEL investment
- **Unified Platform**: Observability + FinOps in one system
- **Developer-Friendly**: 5-minute integration setup
- **Trace-Level Analytics**: Correlate AI costs with end-to-end request traces
- **Standard Protocol**: Uses OpenTelemetry semantic conventions

### OTEL Integration Pattern

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

class ReveniumOTELIntegration:
    """
    OpenTelemetry integration for Revenium

    Demonstrates:
    - OTEL AI metrics in JSON format
    - Trace-level analytics for detailed observability
    - Distributed trace ID correlation
    - Seamless integration with existing spans
    """

    def __init__(self, revenium_endpoint: str, api_key: str):
        """
        Initialize OTEL integration with Revenium

        Args:
            revenium_endpoint: Revenium OTEL collector endpoint
            api_key: Revenium API key for authentication
        """
        # Configure OTEL to send to Revenium
        self.tracer_provider = TracerProvider()

        # Revenium OTEL collector endpoint
        otlp_exporter = OTLPSpanExporter(
            endpoint=revenium_endpoint,
            headers={"Authorization": f"Bearer {api_key}"}
        )

        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )

        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)

    def track_ai_completion(
        self,
        ai_response,
        context: Dict[str, Any]
    ) -> str:
        """
        Track AI completion using OpenTelemetry spans

        Args:
            ai_response: Response object from AI provider
            context: Request context with customer/product metadata

        Returns:
            trace_id: Distributed trace ID for correlation
        """
        with self.tracer.start_as_current_span("ai.completion") as span:
            # Standard OTEL AI semantic conventions
            span.set_attribute("ai.system", "openai")  # or "anthropic", "bedrock"
            span.set_attribute("ai.request.model", ai_response.model)
            span.set_attribute("ai.usage.prompt_tokens", ai_response.usage.prompt_tokens)
            span.set_attribute("ai.usage.completion_tokens", ai_response.usage.completion_tokens)
            span.set_attribute("ai.usage.total_tokens", ai_response.usage.total_tokens)

            # Revenium-specific attributes for cost allocation
            span.set_attribute("revenium.customer_id", context.get('customer_id'))
            span.set_attribute("revenium.organization_id", context.get('organization_id'))
            span.set_attribute("revenium.product_id", context.get('product_id'))
            span.set_attribute("revenium.feature_id", context.get('feature_id'))
            span.set_attribute("revenium.subscription_tier", context.get('subscription_tier'))
            span.set_attribute("revenium.environment", context.get('environment', 'production'))

            # Cost calculation
            cost_usd = self._calculate_cost(
                provider=ai_response.model.split('-')[0],
                model=ai_response.model,
                input_tokens=ai_response.usage.prompt_tokens,
                output_tokens=ai_response.usage.completion_tokens
            )
            span.set_attribute("revenium.cost_usd", cost_usd)

            # Trace correlation
            span_context = span.get_span_context()
            return format(span_context.trace_id, '032x')

    def _calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider pricing"""
        # Simplified cost calculation
        pricing = {
            'openai': {'gpt-4': {'input': 0.03, 'output': 0.06}},
            'anthropic': {'claude-sonnet-4': {'input': 0.003, 'output': 0.015}}
        }

        rates = pricing.get(provider, {}).get(model, {'input': 0, 'output': 0})
        return (input_tokens * rates['input'] + output_tokens * rates['output']) / 1000
```

### Usage Example with OpenAI

```python
from opentelemetry import trace
import openai

# Initialize Revenium OTEL integration
revenium_otel = ReveniumOTELIntegration(
    revenium_endpoint="https://otel.revenium.io/v1/traces",
    api_key="your-revenium-api-key"
)

# Make AI call within OTEL context
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("user.request") as parent_span:
    # Parent span tracks entire user request
    parent_span.set_attribute("user.id", "user_123")
    parent_span.set_attribute("request.path", "/api/chat")

    # Make OpenAI call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Explain quantum computing"}]
    )

    # Track with Revenium (creates child span)
    trace_id = revenium_otel.track_ai_completion(
        ai_response=response,
        context={
            'customer_id': 'cust_0001',
            'organization_id': 'org_001',
            'product_id': 'product_a',
            'feature_id': 'chat',
            'subscription_tier': 'pro',
            'environment': 'production'
        }
    )

    print(f"Trace ID: {trace_id}")
    # Revenium automatically correlates AI costs with distributed trace
```

### Trace-Level Analytics Capabilities

**End-to-End Request Correlation**:
```
User Request (trace_id: abc123)
├─ API Gateway (span_id: 001)
├─ Authentication (span_id: 002)
├─ Business Logic (span_id: 003)
│  ├─ Database Query (span_id: 004)
│  └─ AI Completion (span_id: 005) ← Revenium cost tracking
└─ Response Formatting (span_id: 006)
```

With OTEL integration, Revenium provides:

1. **Cost Attribution to Customer Journeys**:
   - Link AI expenses to specific user workflows
   - Understand which user actions trigger expensive AI calls
   - Optimize high-cost user paths

2. **Performance + Cost Analysis**:
   - Correlate latency with cost
   - Identify slow AND expensive operations
   - Optimize for both speed and budget

3. **Debug Cost Issues with Full Context**:
   - "Why did this request cost $5?" → See full trace
   - Identify cascading AI calls in distributed workflows
   - Root cause analysis with complete observability

4. **Distributed Workflow Analysis**:
   - Track AI costs across microservices
   - Multi-service AI orchestration costs
   - End-to-end cost of complex workflows

### Automatic Model Detection

Revenium's OTEL integration automatically detects AI model usage from span attributes:

```python
# Revenium automatically extracts:
# - Provider: From ai.system attribute
# - Model: From ai.request.model attribute
# - Tokens: From ai.usage.* attributes
# - Cost: Calculated using built-in pricing tables

# No manual instrumentation needed beyond standard OTEL conventions
```

### Integration with Existing OTEL Collectors

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:

exporters:
  # Send to Revenium for cost tracking
  otlp/revenium:
    endpoint: "https://otel.revenium.io"
    headers:
      Authorization: "Bearer ${REVENIUM_API_KEY}"

  # Also send to existing observability platform
  jaeger:
    endpoint: "jaeger:14250"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/revenium, jaeger]  # Dual export
```

### Business Value

**For Engineering Teams**:
- No new instrumentation libraries to learn
- Reuse existing OTEL investment
- Single source of truth for observability + costs
- Standard protocol (no vendor lock-in)

**For FinOps Teams**:
- Cost data automatically includes trace context
- Debug expensive requests with full observability
- Link costs to specific customer actions
- No dependency on engineering for cost tracking

**For Product Teams**:
- Understand cost-per-feature with real usage patterns
- Identify expensive user workflows
- Optimize product features based on cost + usage data

## Metadata Builders

**File**: `showcase/metadata/builders.py`

**Purpose**: Fluent API for constructing Revenium metadata

### Fluent Builder Pattern

```python
class ReveniumMetadataBuilder:
    """Fluent API for building Revenium metadata"""

    def __init__(self):
        self._metadata = {}

    def customer(self, customer_id: str):
        """Set customer ID"""
        self._metadata['customer_id'] = customer_id
        return self

    def organization(self, org_id: str):
        """Set organization ID"""
        self._metadata['organization_id'] = org_id
        return self

    def product(self, product_id: str):
        """Set product ID"""
        self._metadata['product_id'] = product_id
        return self

    def feature(self, feature_id: str):
        """Set feature ID"""
        self._metadata['feature_id'] = feature_id
        return self

    def tier(self, tier: str):
        """Set subscription tier"""
        self._metadata['subscription_tier'] = tier
        return self

    def environment(self, env: str):
        """Set environment (production, staging, development)"""
        self._metadata['environment'] = env
        return self

    def task_type(self, task_type: str):
        """Set task type"""
        self._metadata['task_type'] = task_type
        return self

    def session(self, session_id: str):
        """Set session ID"""
        self._metadata['session_id'] = session_id
        return self

    def trace(self, trace_id: str):
        """Set distributed trace ID"""
        self._metadata['trace_id'] = trace_id
        return self

    def request(self, request_id: str):
        """Set request ID"""
        self._metadata['request_id'] = request_id
        return self

    def custom(self, key: str, value: Any):
        """Add custom metadata field"""
        self._metadata[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return metadata dictionary"""
        return self._metadata.copy()
```

### Usage Examples

**Simple Metadata**:
```python
from showcase.metadata.builders import ReveniumMetadataBuilder

metadata = (ReveniumMetadataBuilder()
    .customer('cust_0001')
    .feature('chat')
    .environment('production')
    .build())

# Result:
# {
#     'customer_id': 'cust_0001',
#     'feature_id': 'chat',
#     'environment': 'production'
# }
```

**Complete Metadata**:
```python
metadata = (ReveniumMetadataBuilder()
    .customer('cust_0001')
    .organization('org_001')
    .product('product_a')
    .feature('chat')
    .tier('pro')
    .environment('production')
    .task_type('qa')
    .session('sess_12345')
    .trace('trace_67890')
    .request('req_11111')
    .build())
```

**Context Manager Pattern**:
```python
class ReveniumContext:
    """Context manager for Revenium tracking"""

    def __init__(self, tracker, metadata_builder):
        self.tracker = tracker
        self.builder = metadata_builder

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Auto-track on exit if needed
        pass

# Usage
with ReveniumContext(tracker, metadata_builder) as ctx:
    response = call_ai_model()
    ctx.track(response)
```

## Hierarchical Tagging Strategies

### Multi-Tenant Architecture

```python
# Organization → Product → Customer → Feature
metadata = (ReveniumMetadataBuilder()
    .organization('org_acme')      # Top-level tenant
    .product('product_crm')        # Product line
    .customer('cust_0001')         # End customer
    .feature('email_assistant')    # Specific feature
    .build())

# Enables queries like:
# - "Show all costs for org_acme"
# - "Breakdown costs by product within org_acme"
# - "Which customers are most expensive in product_crm?"
# - "What features drive costs for cust_0001?"
```

### Cost Center Allocation

```python
# Department → Team → Project
metadata = (ReveniumMetadataBuilder()
    .organization('dept_engineering')
    .product('team_backend')
    .feature('project_api_v2')
    .custom('cost_center', 'CC-1234')
    .build())

# Enables chargeback/showback:
# - Monthly invoice per department
# - Team-level cost tracking
# - Project budget monitoring
```

### SaaS Application Pattern

```python
# Application → Customer → Subscription Tier → Feature
metadata = (ReveniumMetadataBuilder()
    .product('app_main')
    .customer(current_user.customer_id)
    .tier(current_user.subscription_tier)
    .feature(current_feature)
    .environment('production')
    .build())

# Enables analysis:
# - Customer profitability
# - Tier economics
# - Feature adoption and costs
```

## Query Patterns

**File**: `showcase/queries/cost_allocation.py`

**Purpose**: Common query patterns for cost analysis

### Query Examples

**Total Cost by Provider**:
```python
def cost_by_provider(calls: List[Dict]) -> Dict[str, float]:
    """Aggregate cost by AI provider"""
    by_provider = defaultdict(float)
    for call in calls:
        by_provider[call['provider']] += call['cost_usd']
    return dict(by_provider)

# Result:
# {
#     'openai': 12345.67,
#     'anthropic': 8901.23,
#     'bedrock': 456.78
# }
```

**Cost by Customer**:
```python
def cost_by_customer(calls: List[Dict]) -> Dict[str, float]:
    """Aggregate cost by customer"""
    by_customer = defaultdict(float)
    for call in calls:
        customer_id = call.get('metadata', {}).get('customer_id')
        if customer_id:
            by_customer[customer_id] += call['cost_usd']
    return dict(by_customer)
```

**Cost by Organization and Product**:
```python
def cost_by_org_and_product(calls: List[Dict]) -> Dict[tuple, float]:
    """Hierarchical cost allocation"""
    by_org_product = defaultdict(float)
    for call in calls:
        org = call.get('metadata', {}).get('organization_id')
        product = call.get('metadata', {}).get('product_id')
        if org and product:
            by_org_product[(org, product)] += call['cost_usd']
    return dict(by_org_product)

# Result:
# {
#     ('org_001', 'product_a'): 5432.10,
#     ('org_001', 'product_b'): 1234.56,
#     ('org_002', 'product_a'): 3456.78
# }
```

**Time-Series Query**:
```python
def daily_cost_trend(calls: List[Dict]) -> Dict[str, float]:
    """Daily cost aggregation"""
    by_date = defaultdict(float)
    for call in calls:
        date = call['timestamp'].split('T')[0]  # YYYY-MM-DD
        by_date[date] += call['cost_usd']
    return dict(sorted(by_date.items()))

# Result:
# {
#     '2025-11-19': 745.32,
#     '2025-11-20': 823.45,
#     '2025-11-21': 912.67
# }
```

**Feature Economics Query**:
```python
def feature_metrics(calls: List[Dict]) -> Dict[str, Dict]:
    """Comprehensive feature analysis"""
    by_feature = defaultdict(lambda: {
        'cost': 0,
        'calls': 0,
        'customers': set(),
        'total_tokens': 0
    })

    for call in calls:
        feature = call.get('metadata', {}).get('feature_id')
        if feature:
            by_feature[feature]['cost'] += call['cost_usd']
            by_feature[feature]['calls'] += 1
            by_feature[feature]['customers'].add(
                call.get('metadata', {}).get('customer_id')
            )
            by_feature[feature]['total_tokens'] += (
                call['input_tokens'] + call['output_tokens']
            )

    # Convert sets to counts
    result = {}
    for feature, data in by_feature.items():
        result[feature] = {
            'cost': data['cost'],
            'calls': data['calls'],
            'customers': len(data['customers']),
            'total_tokens': data['total_tokens'],
            'avg_cost_per_call': data['cost'] / data['calls']
        }

    return result
```

## Advanced Multi-Dimensional Analysis

**Purpose**: Showcase Revenium's sophisticated multi-dimensional grouping and Chart Builder capabilities for collaborative, reusable analysis.

**Key Differentiator**: Unlike simple query patterns, Revenium enables teams to build custom analysis views once and reuse them forever, with cross-functional insights combining cost, performance, and usage metrics.

### Multi-Dimensional Grouping

Revenium supports simultaneous grouping across multiple dimensions for comprehensive analysis:

**Available Grouping Dimensions**:
- **Organizational**: Agents, teams, organizations, products
- **Technical**: AI models, providers, API keys, credentials
- **Behavioral**: Task/trace types, workspaces (with custom display names)
- **Financial**: Subscription tiers, cost centers, billing entities
- **Operational**: Environments, regions, availability zones

### Chart Builder Pattern

**File**: `showcase/queries/chart_builder.py`

Revenium's Chart Builder enables saving and reusing chart configurations across teams:

```python
class ReveniumChartBuilder:
    """
    Build and save reusable chart configurations

    Demonstrates Revenium's Chart Builder capability:
    - Save chart configurations for recurring analysis
    - Query against completion metrics
    - Multiple visualization options
    - Team-wide sharing and collaboration
    """

    def __init__(self, revenium_api_key: str):
        self.api_key = revenium_api_key
        self.endpoint = "https://api.revenium.io/v1/charts"

    def build_multi_dimensional_chart(
        self,
        dimensions: List[str],
        metrics: List[str],
        filters: Dict[str, Any],
        visualization_type: str,
        name: str
    ) -> str:
        """
        Create and save a multi-dimensional chart configuration

        Args:
            dimensions: Grouping dimensions (e.g., ['organization_id', 'product_id', 'model'])
            metrics: Metrics to analyze (e.g., ['cost_usd', 'tokens', 'latency_ms'])
            filters: Filter criteria (e.g., {'environment': 'production'})
            visualization_type: Chart type ('stacked_bar', 'line', 'heatmap', 'treemap')
            name: Descriptive name for saved chart

        Returns:
            chart_id: Unique identifier for reusing this configuration
        """
        config = {
            'name': name,
            'dimensions': dimensions,
            'metrics': metrics,
            'filters': filters,
            'visualization': visualization_type,
            'aggregation': 'sum',  # or 'avg', 'count', 'min', 'max'
            'time_range': 'last_30_days',
            'refresh_interval': 'hourly'
        }

        # Save to Revenium for team-wide access
        # In production: POST to Revenium API
        # response = requests.post(self.endpoint, json=config, headers={...})
        # return response.json()['chart_id']

        return f"chart_{hash(str(config))}"
```

### Multi-Dimensional Query Examples

**Example 1: Organization → Product → Model Cost Breakdown**
```python
# Build a 3-dimensional cost analysis
chart_id = builder.build_multi_dimensional_chart(
    dimensions=['organization_id', 'product_id', 'model'],
    metrics=['cost_usd', 'total_tokens', 'call_count'],
    filters={'environment': 'production'},
    visualization_type='treemap',
    name='Org-Product-Model Cost Hierarchy'
)

# Result enables queries like:
# - "Which organization spends most on AI?"
# - "What models does product_a use across all orgs?"
# - "Compare model costs within org_001's product_b"
```

**Example 2: Customer Profitability by Tier and Feature**
```python
chart_id = builder.build_multi_dimensional_chart(
    dimensions=['subscription_tier', 'feature_id', 'customer_id'],
    metrics=['cost_usd', 'revenue_attributed'],
    filters={'environment': 'production'},
    visualization_type='stacked_bar',
    name='Customer Profitability by Tier and Feature'
)

# Insights:
# - Which features are profitable per tier?
# - Which customers within each tier are unprofitable?
# - Feature adoption patterns by tier
```

**Example 3: Cross-Functional Performance Analysis**
```python
chart_id = builder.build_multi_dimensional_chart(
    dimensions=['model', 'task_type', 'provider'],
    metrics=['cost_usd', 'latency_ms', 'tokens_per_second'],
    filters={
        'environment': 'production',
        'latency_ms': {'$lt': 5000}  # Only successful, fast calls
    },
    visualization_type='heatmap',
    name='Model Performance Matrix'
)

# Combines cost + performance + usage:
# - Most cost-efficient model per task type
# - Latency vs cost tradeoffs
# - Provider performance comparison
```

**Example 4: Workspace-Level Cost Allocation**
```python
chart_id = builder.build_multi_dimensional_chart(
    dimensions=['workspace', 'agent_type', 'api_credential'],
    metrics=['cost_usd', 'call_count'],
    filters={'environment': 'production'},
    visualization_type='stacked_bar',
    name='Workspace Cost Allocation (Custom Display Names)'
)

# Use custom workspace display names for readability:
# - "Engineering Team A" instead of "workspace_123"
# - "Customer Success Bot" instead of "agent_cs_001"
# - Clear cost center allocation for chargeback
```

### Reusing Saved Charts

```python
def load_and_execute_chart(chart_id: str, date_range: Dict) -> Dict:
    """
    Load a saved chart configuration and execute with new parameters

    Args:
        chart_id: Previously saved chart ID
        date_range: Override time range (e.g., {'start': '2025-11-01', 'end': '2025-11-30'})

    Returns:
        Chart data ready for visualization
    """
    # Load saved configuration
    config = revenium.charts.get(chart_id)

    # Override time range for this execution
    config['time_range'] = date_range

    # Execute query
    results = revenium.query.execute(config)

    return results

# Team collaboration:
# - Finance team saves monthly profitability charts
# - Engineering team reuses with different date ranges
# - Executives get consistent reporting across months
```

### Business Impact

**Collaboration Benefits**:
- **Save Once, Reuse Forever**: Build complex analysis views and share across teams
- **Consistency**: Everyone uses same definitions and groupings
- **Efficiency**: No need to rebuild queries monthly
- **Self-Service**: Non-technical teams can run saved charts with different parameters

**Cross-Functional Analysis**:
- Combine cost (FinOps) + performance (Engineering) + usage (Product) in single view
- Unified metrics across organizational boundaries
- Data-driven decision making with complete context

**Workspace Collaboration**:
- Custom display names for readability
- Team-specific views and filters
- Shared dashboards for stakeholder reporting

## Business Scenarios

**File**: `showcase/scenarios/scenario_unprofitable_customers.py`

**Purpose**: Demonstrate business use cases enabled by Revenium

### Scenario: Unprofitable Customer Detection

**Business Problem**:
Identify customers whose AI usage costs exceed their subscription revenue, enabling proactive intervention.

**Implementation**:
```python
def identify_unprofitable_customers(
    calls: List[Dict],
    subscription_tiers: Dict[str, float]
) -> List[Dict]:
    """
    Identify customers costing more to serve than subscription revenue

    Args:
        calls: List of AI calls
        subscription_tiers: Tier pricing (e.g., {'pro': 99, ...})

    Returns:
        List of unprofitable customers with details
    """
    # Aggregate cost by customer
    customer_costs = defaultdict(lambda: {
        'cost': 0,
        'tier': None,
        'calls': 0
    })

    for call in calls:
        customer_id = call.get('metadata', {}).get('customer_id')
        tier = call.get('metadata', {}).get('subscription_tier')

        if customer_id:
            customer_costs[customer_id]['cost'] += call['cost_usd']
            customer_costs[customer_id]['tier'] = tier
            customer_costs[customer_id]['calls'] += 1

    # Identify unprofitable
    unprofitable = []
    for customer_id, data in customer_costs.items():
        tier = data['tier']
        if tier and tier in subscription_tiers:
            revenue = subscription_tiers[tier]
            cost = data['cost']
            margin = revenue - cost

            if margin < 0:
                unprofitable.append({
                    'customer_id': customer_id,
                    'tier': tier,
                    'revenue': revenue,
                    'cost': cost,
                    'loss': abs(margin),
                    'calls': data['calls']
                })

    # Sort by biggest losses
    unprofitable.sort(key=lambda x: x['loss'], reverse=True)

    return unprofitable
```

**Usage**:
```python
subscription_tiers = {
    'starter': 29,
    'pro': 99,
    'enterprise': 299
}

unprofitable = identify_unprofitable_customers(calls, subscription_tiers)

print(f"Found {len(unprofitable)} unprofitable customers")
print(f"Total monthly loss: ${sum(c['loss'] for c in unprofitable):.2f}")

# Take action
for customer in unprofitable[:10]:  # Top 10 worst
    print(f"Customer {customer['customer_id']}")
    print(f"  Loss: ${customer['loss']:.2f}/month")
    print(f"  Recommendation: Implement usage cap or upgrade to higher tier")
```

**Business Impact**:
- Prevent revenue leakage
- Proactive customer engagement
- Data-driven tier recommendations
- Usage cap policy enforcement

### Other Scenarios

**Scenario: Model Optimization**:
```python
# Identify customers using expensive models for simple tasks
def find_optimization_opportunities(calls):
    # Look for gpt-4 usage with low token counts
    # Suggest switching to gpt-4-turbo or claude-sonnet-4
    pass
```

**Scenario: Seasonal Capacity Planning**:
```python
# Analyze historical patterns to predict peak usage
def forecast_capacity_needs(calls, forecast_days=30):
    # Time-series analysis
    # Predict peak usage windows
    # Recommend reserved capacity purchases
    pass
```

**Scenario: Feature Sunset Analysis**:
```python
# Identify low-adoption, high-cost features
def evaluate_feature_sunset(calls):
    # Calculate adoption rates
    # Calculate costs per feature
    # Recommend investment vs sunset decisions
    pass
```

## Error Handling Patterns

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff=2):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def track_with_retry(tracker, **kwargs):
    """Track AI call with automatic retry"""
    return tracker.track_ai_call(**kwargs)
```

### Circuit Breaker

```python
class CircuitBreaker:
    """Prevent cascading failures"""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = 'closed'

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = 'open'
```

## Best Practices

### 1. Always Include Core Metadata

Minimum required fields:
- `customer_id` - For customer profitability
- `feature_id` - For feature economics
- `environment` - For cost segregation

### 2. Use Consistent ID Formats

```python
# Good: Consistent prefixes
customer_id = 'cust_0001'
organization_id = 'org_001'
product_id = 'product_a'

# Bad: Inconsistent formats
customer_id = '0001'
organization_id = 'organization_001'
product_id = 'a'
```

### 3. Track Immediately After AI Call

```python
# Good: Track right after call
response = ai_api.call()
tracker.track_ai_call(...)

# Bad: Track later (risk of data loss)
response = ai_api.call()
# ... lots of code ...
tracker.track_ai_call(...)  # Might not execute if error above
```

### 4. Use Async Tracking for Performance

```python
import asyncio

async def track_async(tracker, **kwargs):
    """Non-blocking tracking"""
    # Fire and forget
    asyncio.create_task(tracker.track_ai_call(**kwargs))
```

### 5. Include Request Context

```python
# Capture request context for debugging
metadata = (ReveniumMetadataBuilder()
    .customer(request.user.customer_id)
    .request(request.id)
    .trace(request.trace_id)
    .session(request.session_id)
    .custom('ip_address', request.ip)
    .custom('user_agent', request.headers['User-Agent'])
    .build())
```

## Related Specifications

- **Data Schema**: See `data-schema.md` for metadata field definitions
- **Architecture**: See `architecture.md` for integration points
- **Simulators**: See `simulators.md` for data generation using these patterns
