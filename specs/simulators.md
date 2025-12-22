# Traffic Simulation Specification

## Overview

The traffic simulation system generates realistic AI API usage data with comprehensive Revenium metadata. It supports multiple traffic patterns to demonstrate diverse real-world scenarios.

## Simulator Architecture

### Base Simulator

**File**: `src/simulator/core.py`

**Class**: `AICallSimulator`

**Purpose**: Generate baseline AI usage with realistic customer archetypes and usage patterns

**Key Features**:
- Multi-provider support (OpenAI, Anthropic, Bedrock)
- Customer archetype modeling (light, power, heavy)
- Subscription tier simulation (starter, pro, enterprise)
- Realistic temporal patterns (business hours, weekends)
- Deterministic with optional seed

### Scenario Simulators

**Location**: `src/simulator/scenarios/`

**Purpose**: Generate specialized traffic patterns for specific business scenarios

**Available Scenarios**:
1. **Seasonal Pattern** - Cyclical usage patterns
2. **Burst Traffic** - Unpredictable traffic spikes
3. **Gradual Decline** - Churn and usage reduction
4. **Steady Growth** - Linear growth (legacy)
5. **Viral Spike** - Exponential growth (legacy)

## Configuration

### Provider and Model Setup

```python
PROVIDERS = {
    'openai': {
        'models': ['gpt-4', 'gpt-4-turbo'],
        'input_cost': {
            'gpt-4': 0.03,        # $0.03 per 1K input tokens
            'gpt-4-turbo': 0.01   # $0.01 per 1K input tokens
        },
        'output_cost': {
            'gpt-4': 0.06,        # $0.06 per 1K output tokens
            'gpt-4-turbo': 0.03   # $0.03 per 1K output tokens
        }
    },
    'anthropic': {
        'models': ['claude-opus-4', 'claude-sonnet-4'],
        'input_cost': {
            'claude-opus-4': 0.015,   # $0.015 per 1K input tokens
            'claude-sonnet-4': 0.003  # $0.003 per 1K input tokens
        },
        'output_cost': {
            'claude-opus-4': 0.075,   # $0.075 per 1K output tokens
            'claude-sonnet-4': 0.015  # $0.015 per 1K output tokens
        }
    },
    'bedrock': {
        'models': ['claude-instant', 'claude-v2'],
        'input_cost': {
            'claude-instant': 0.0008,  # $0.0008 per 1K input tokens
            'claude-v2': 0.008         # $0.008 per 1K input tokens
        },
        'output_cost': {
            'claude-instant': 0.0024,  # $0.0024 per 1K output tokens
            'claude-v2': 0.024         # $0.024 per 1K output tokens
        }
    }
}
```

### Subscription Tiers

```python
SUBSCRIPTION_TIERS = {
    'starter': 29,      # $29/month
    'pro': 99,          # $99/month
    'enterprise': 299   # $299/month
}
```

### Customer Archetypes

```python
CUSTOMER_ARCHETYPES = {
    'light': {
        'calls_per_day': (5, 20),    # 5-20 calls per day
        'weight': 0.70               # 70% of customers
    },
    'power': {
        'calls_per_day': (50, 150),  # 50-150 calls per day
        'weight': 0.20               # 20% of customers
    },
    'heavy': {
        'calls_per_day': (200, 500), # 200-500 calls per day
        'weight': 0.10               # 10% of customers
    }
}
```

### Task Types

```python
TASK_TYPES = [
    'chat',             # Conversational AI
    'summarization',    # Text summarization
    'code_generation',  # Code generation
    'translation',      # Language translation
    'analysis',         # Data/text analysis
    'qa'                # Question answering
]
```

## Base Simulator Details

### Initialization

```python
def __init__(self,
             num_customers: int = 100,
             num_days: int = 30,
             seed: Optional[int] = None)
```

**Parameters**:
- `num_customers`: Number of customers to simulate (default: 100)
- `num_days`: Number of days to simulate (default: 30)
- `seed`: Random seed for reproducibility (default: None)

**Example**:
```python
simulator = AICallSimulator(
    num_customers=200,
    num_days=60,
    seed=42
)
```

### Customer Generation

**Process**:
1. Assign archetype based on weights (70% light, 20% power, 10% heavy)
2. Assign subscription tier based on archetype
3. Assign organization (1-10)
4. Assign product (A or B)

**Tier Assignment Logic**:
- **Light users**: 60% starter, 35% pro, 5% enterprise
- **Power users**: 10% starter, 70% pro, 20% enterprise
- **Heavy users**: 0% starter, 20% pro, 80% enterprise

**Output**: List of customer profiles with archetype, tier, org, product

### Call Generation

**For each customer, for each day**:
1. Determine number of calls based on archetype range
2. Apply temporal patterns (business hours, weekends)
3. Generate call at random time during day
4. Select provider and model
5. Generate token counts
6. Calculate cost
7. Generate latency
8. Add metadata fields

**Temporal Patterns**:
- **Business Hours (8am-8pm)**: 85% of calls
- **Off Hours (8pm-8am)**: 15% of calls
- **Weekends**: 70% of weekday volume

### Token Generation

**Input Tokens**:
- Range: 100 - 2000 tokens
- Distribution: Weighted toward medium (500-1000)
- Varies by task type

**Output Tokens**:
- Range: 50 - 1500 tokens
- Ratio to input: 0.5 - 2.5x
- Varies by task type and model

**Task Type Patterns**:
- **Chat**: Medium input, medium output
- **Summarization**: High input, low output
- **Code Generation**: Low input, high output
- **Translation**: Medium input, medium output
- **Analysis**: High input, medium output
- **Q&A**: Low input, low output

### Cost Calculation

```python
def calculate_cost(provider: str, model: str,
                   input_tokens: int, output_tokens: int) -> float:
    input_cost = PROVIDERS[provider]['input_cost'][model]
    output_cost = PROVIDERS[provider]['output_cost'][model]

    cost = (input_tokens * input_cost / 1000) + \
           (output_tokens * output_cost / 1000)

    return round(cost, 6)
```

### Latency Simulation

**Base Latency**:
- Proportional to total tokens
- Model-dependent (faster models have lower latency)
- Random variation ±30%

**Formula**:
```python
base_latency = total_tokens * 2  # ~2ms per token
model_multiplier = {
    'gpt-4': 1.5,
    'gpt-4-turbo': 1.0,
    'claude-opus-4': 1.4,
    'claude-sonnet-4': 0.9,
    'claude-instant': 0.6,
    'claude-v2': 1.2
}
latency = base_latency * model_multiplier * random(0.7, 1.3)
```

### Metadata Enrichment

**Automatically Generated**:
- `timestamp`: Current time in simulation
- `call_id`: Unique ID with timestamp
- `request_id`: Random request ID
- `trace_id`: Random trace ID
- `session_id`: Random session ID (reused within customer/day)
- `user_agent`: "ReveniumSDK/1.0 Python/3.11"
- `environment`: "production" (95%), "staging" (4%), "development" (1%)

### Output

**File**: `data/simulated_calls.csv`

**Mode**: Overwrite (base simulator) or Append (scenario simulators)

**Format**: CSV with 19 fields (see `data-schema.md`)

**Statistics Printed**:
- Total calls generated
- Date range
- Unique customers
- Total cost
- Total tokens
- Average cost per call

## Scenario Simulators

### 1. Seasonal Pattern Simulator

**File**: `src/simulator/scenarios/seasonal_pattern.py`

**Class**: `SeasonalPatternSimulator`

**Purpose**: Simulate cyclical usage patterns for enterprise SaaS scenarios

**Patterns**:
- **Weekly Cycle**: Higher usage mid-week, lower on weekends
- **Daily Cycle**: Peak hours 10am-2pm, 6pm-8pm
- **Monthly Cycle**: Higher usage at month-end (reporting periods)

**Amplitude**:
- Weekly variation: ±30%
- Daily variation: ±50%
- Monthly variation: ±20%

**Configuration**:
```python
def __init__(self,
             num_customers: int = 50,
             num_days: int = 30,
             seed: Optional[int] = None):
    # Inherits from AICallSimulator
    self.weekly_amplitude = 0.3
    self.daily_amplitude = 0.5
    self.monthly_amplitude = 0.2
```

**Call Multiplier Formula**:
```python
multiplier = (
    1.0 +
    weekly_amplitude * sin(2π * day_of_week / 7) +
    daily_amplitude * sin(2π * hour / 24) +
    monthly_amplitude * sin(2π * day_of_month / 30)
)
calls_today = base_calls * multiplier
```

**Use Cases**:
- Enterprise SaaS with business cycles
- Reporting period analysis
- Capacity planning for predictable patterns

### 2. Burst Traffic Simulator

**File**: `src/simulator/scenarios/burst_traffic.py`

**Class**: `BurstTrafficSimulator`

**Purpose**: Simulate unpredictable traffic spikes for batch processing scenarios

**Burst Characteristics**:
- **Frequency**: 5-10% of days have bursts
- **Multiplier**: 5x - 20x normal traffic
- **Duration**: 1-3 hour windows
- **Randomness**: Completely unpredictable timing

**Configuration**:
```python
def __init__(self,
             num_customers: int = 30,
             num_days: int = 30,
             seed: Optional[int] = None):
    self.burst_probability = 0.08     # 8% of days
    self.burst_multiplier = (5, 20)   # 5x to 20x
    self.burst_duration_hours = (1, 3) # 1-3 hours
```

**Burst Generation**:
```python
if random() < burst_probability:
    burst_multiplier = randint(5, 20)
    burst_start_hour = randint(0, 21)
    burst_duration = randint(1, 3)

    # Apply burst to affected hours
    for hour in range(burst_start_hour, burst_start_hour + burst_duration):
        calls_this_hour *= burst_multiplier
```

**Use Cases**:
- Batch processing workloads
- API integrations with scheduled jobs
- Event-driven architectures
- Cost anomaly detection testing

### 3. Gradual Decline Simulator

**File**: `src/simulator/scenarios/gradual_decline.py`

**Class**: `GradualDeclineSimulator`

**Purpose**: Simulate customer churn and declining usage patterns

**Decline Characteristics**:
- **Daily Decline Rate**: 1-3% per day
- **Customer Churn**: 15-25% of customers over period
- **Usage Reduction**: Gradual decrease for remaining customers

**Configuration**:
```python
def __init__(self,
             num_customers: int = 40,
             num_days: int = 30,
             seed: Optional[int] = None):
    self.daily_decline_rate = 0.02    # 2% daily decline
    self.churn_probability = 0.20     # 20% churn over period
```

**Churn Modeling**:
```python
# Mark customers for churn at random days
churn_day = randint(1, num_days)
for customer in sample_customers(num_customers * 0.20):
    customer.churn_day = churn_day

# Stop generating calls after churn
if current_day >= customer.churn_day:
    continue  # Skip this customer
```

**Usage Decline**:
```python
# For non-churned customers, reduce usage over time
decline_multiplier = (1 - daily_decline_rate) ** day_number
calls_today = base_calls * decline_multiplier
```

**Statistics Tracked**:
- Churned customer count
- Churn percentage
- Average usage decline
- Revenue impact

**Use Cases**:
- Churn analysis
- Retention program effectiveness
- At-risk customer identification
- Revenue forecasting under churn

### 4. Steady Growth Simulator (Legacy)

**File**: `src/simulator/scenarios/steady_growth.py`

**Purpose**: Linear growth pattern

**Status**: Legacy - use for historical comparison

**Growth Rate**: 2-5% daily increase

### 5. Viral Spike Simulator (Legacy)

**File**: `src/simulator/scenarios/viral_spike.py`

**Purpose**: Exponential growth (viral/launch scenarios)

**Status**: Legacy - use for historical comparison

**Growth Rate**: Exponential with 10-30% daily compound

## Master Simulator Runner

**File**: `src/run_all_simulators.py`

**Purpose**: Execute all active simulators in sequence to create comprehensive dataset

**Execution Order**:
1. **Base Traffic** (core.py) - Overwrites CSV
2. **Seasonal Pattern** - Appends to CSV
3. **Burst Traffic** - Appends to CSV
4. **Gradual Decline** - Appends to CSV

**Combined Statistics**:
- Total calls across all patterns
- Unique customers (220+)
- Total cost
- Total tokens
- Average cost per call
- Date range coverage

**Usage**:
```bash
cd src
python3 run_all_simulators.py
```

**Output**:
```
🚀 RUNNING ALL TRAFFIC PATTERN SIMULATORS
======================================================================

📊 Running: Base Traffic Pattern
----------------------------------------------------------------------
✅ Generated 45,234 calls and saved to data/simulated_calls.csv

📊 Running: Seasonal Pattern
----------------------------------------------------------------------
✅ Appended to data/simulated_calls.csv

📊 Running: Burst Traffic
----------------------------------------------------------------------
✅ Appended to data/simulated_calls.csv

📊 Running: Gradual Decline
----------------------------------------------------------------------
   Churned Customers: 8 (20.0%)
✅ Appended to data/simulated_calls.csv

======================================================================
📊 SIMULATION COMPLETE
======================================================================

📈 Combined Dataset Statistics:
   Total Calls: 142,126
   Unique Customers: 220
   Total Cost: $22,345.67
   Total Tokens: 34,567,890
   Avg Cost/Call: $0.1854
```

## Customization Guide

### Changing Customer Count

```python
# More customers
simulator = AICallSimulator(num_customers=200)

# Fewer customers (faster testing)
simulator = AICallSimulator(num_customers=20)
```

### Changing Time Period

```python
# Longer simulation
simulator = AICallSimulator(num_days=60)

# Shorter simulation
simulator = AICallSimulator(num_days=7)
```

### Reproducibility

```python
# Deterministic output
simulator = AICallSimulator(seed=42)

# Run multiple times with same seed = same data
```

### Adjusting Pricing

```python
# Update provider costs (in simulator/core.py)
PROVIDERS['openai']['input_cost']['gpt-4'] = 0.025  # New price
PROVIDERS['openai']['output_cost']['gpt-4'] = 0.050
```

### Adjusting Customer Mix

```python
# More heavy users (in simulator/core.py)
CUSTOMER_ARCHETYPES = {
    'light': {'calls_per_day': (5, 20), 'weight': 0.50},   # 50%
    'power': {'calls_per_day': (50, 150), 'weight': 0.30}, # 30%
    'heavy': {'calls_per_day': (200, 500), 'weight': 0.20} # 20%
}
```

### Creating Custom Scenarios

```python
# Example: Holiday spike scenario
class HolidaySpike(AICallSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.holiday_dates = [5, 25]  # Days 5 and 25
        self.holiday_multiplier = 3.0

    def generate_calls_for_day(self, day):
        multiplier = 1.0
        if day in self.holiday_dates:
            multiplier = self.holiday_multiplier

        # Generate with multiplier
        calls = super().generate_calls_for_day(day)
        return calls * multiplier
```

## Performance Characteristics

### Generation Speed
- **Base Simulator**: ~10,000 calls/second
- **Scenario Simulators**: ~8,000 calls/second
- **Full Suite**: ~5 minutes for 140K+ calls

### Memory Usage
- **Peak Memory**: ~200MB for 100K calls
- **Scales Linearly**: ~2MB per 1K calls

### Disk Usage
- **CSV Size**: ~350 bytes per call
- **100K calls**: ~35MB
- **140K calls**: ~50MB

## Validation

### Automatic Validation During Generation

**Type Checking**:
- All fields have correct types
- No null/empty values

**Range Checking**:
- Token counts within realistic ranges
- Costs calculated correctly
- Latencies realistic for token counts

**Referential Integrity**:
- Models match providers
- Tiers are valid
- Timestamps sequential

### Post-Generation Validation

```python
# Check for duplicates
call_ids = set()
for call in calls:
    assert call.call_id not in call_ids
    call_ids.add(call.call_id)

# Check cost calculations
for call in calls:
    expected_cost = calculate_cost(
        call.provider, call.model,
        call.input_tokens, call.output_tokens
    )
    assert abs(call.cost_usd - expected_cost) < 0.000001
```

## Best Practices

1. **Use Master Runner**: Run `run_all_simulators.py` for comprehensive datasets
2. **Set Seeds for Testing**: Use deterministic seeds during development
3. **Validate Output**: Check CSV statistics after generation
4. **Archive Data**: Keep generated data for reproducibility
5. **Document Changes**: Note any customizations to default parameters

## Troubleshooting

### Low Call Counts
- Check `num_customers` and `num_days` parameters
- Verify archetype weights sum to 1.0
- Check for filtering logic removing calls

### Unexpected Costs
- Verify provider pricing configuration
- Check token generation ranges
- Validate cost calculation formula

### Performance Issues
- Reduce `num_customers` or `num_days`
- Use profiling to identify bottlenecks
- Consider chunked CSV writing

## Related Specifications

- **Data Schema**: See `data-schema.md`
- **Architecture**: See `architecture.md`
- **Analyzers**: See `analyzers.md` for data consumption
