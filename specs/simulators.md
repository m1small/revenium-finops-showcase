# Traffic Simulation Specification

## Overview

The traffic simulation system generates realistic AI API usage data with comprehensive Revenium metadata. The simulator is designed to showcase Revenium's platform value through **diverse, variable, and continuous** data generation that mirrors real-world AI usage complexity.

## Key Enhancements

**Diversity** - Representing the Modern AI Market:
- **7 Providers**: OpenAI, Anthropic, Google, Bedrock, Azure, Mistral, Cohere
- **20+ Models**: From budget-friendly (gpt-3.5-turbo, gemini-flash) to premium (gpt-4, claude-opus)
- **Varied Pricing**: 200x cost range (Gemini Flash at $0.000075/1K vs Claude Opus at $0.075/1K)
- **Market-Weighted Distribution**: Realistic provider usage (OpenAI 40%, Anthropic 25%, etc.)

**Variability** - Real-World Traffic Patterns:
- **11 Scenario Patterns**: Seasonal, burst, churn, multi-tenant, model migration, weekend effects, time zones, feature launches, cost optimization
- **Temporal Realism**: Business hours, weekends, holidays, global time zones
- **Customer Archetypes**: Light (70%), power (20%), heavy (10%) users
- **Organizational Diversity**: 3x-10x usage variance across organizations

**Continuous Generation** - Size-Limited Data Creation:
- **50MB Target**: Automatically generates until CSV reaches 50MB (~145,000 calls)
- **Automatic Termination**: Stops when size threshold is reached
- **Balanced Mix**: Equal representation from all scenario patterns
- **Progress Monitoring**: Real-time file size and call count tracking
- **Reproducible**: Same seed produces identical 50MB dataset

These enhancements enable Revenium showcase demos to highlight multi-provider cost management, anomaly detection across diverse patterns, and real-time alerting with realistic data complexity.

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

**Available Scenarios** (reflecting real-world variability):
1. **Seasonal Pattern** - Cyclical usage patterns (quarterly reporting, tax season)
2. **Burst Traffic** - Unpredictable traffic spikes (batch jobs, data processing)
3. **Gradual Decline** - Churn and usage reduction (customer attrition)
4. **Multi-Tenant Variability** - Different usage across organizations
5. **Model Migration** - Gradual shift between AI models/providers
6. **Weekend Effect** - Reduced usage on weekends and holidays
7. **Time Zone Patterns** - Usage follows global time zones
8. **Feature Launch** - Spike from new feature adoption
9. **Cost Optimization** - Gradual shift to cheaper models
10. **Steady Growth** - Linear growth (legacy)
11. **Viral Spike** - Exponential growth (legacy)

## Configuration

### Provider and Model Setup

**Diversity Principle**: The simulator reflects the complexity of the modern AI market with 7+ providers, 20+ models, and varied pricing structures to showcase Revenium's multi-provider cost management capabilities.

```python
PROVIDERS = {
    'openai': {
        'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'],
        'input_cost': {
            'gpt-4': 0.03,           # $0.03 per 1K input tokens
            'gpt-4-turbo': 0.01,     # $0.01 per 1K input tokens
            'gpt-3.5-turbo': 0.0005, # $0.0005 per 1K input tokens
            'gpt-4o': 0.0025,        # $0.0025 per 1K input tokens
            'gpt-4o-mini': 0.00015   # $0.00015 per 1K input tokens
        },
        'output_cost': {
            'gpt-4': 0.06,           # $0.06 per 1K output tokens
            'gpt-4-turbo': 0.03,     # $0.03 per 1K output tokens
            'gpt-3.5-turbo': 0.0015, # $0.0015 per 1K output tokens
            'gpt-4o': 0.01,          # $0.01 per 1K output tokens
            'gpt-4o-mini': 0.0006    # $0.0006 per 1K output tokens
        }
    },
    'anthropic': {
        'models': ['claude-opus-4', 'claude-sonnet-4', 'claude-3.5-sonnet', 'claude-haiku-4'],
        'input_cost': {
            'claude-opus-4': 0.015,      # $0.015 per 1K input tokens
            'claude-sonnet-4': 0.003,    # $0.003 per 1K input tokens
            'claude-3.5-sonnet': 0.003,  # $0.003 per 1K input tokens
            'claude-haiku-4': 0.00025    # $0.00025 per 1K input tokens
        },
        'output_cost': {
            'claude-opus-4': 0.075,      # $0.075 per 1K output tokens
            'claude-sonnet-4': 0.015,    # $0.015 per 1K output tokens
            'claude-3.5-sonnet': 0.015,  # $0.015 per 1K output tokens
            'claude-haiku-4': 0.00125    # $0.00125 per 1K output tokens
        }
    },
    'bedrock': {
        'models': ['claude-instant', 'claude-v2', 'titan-text-express', 'titan-text-lite'],
        'input_cost': {
            'claude-instant': 0.0008,    # $0.0008 per 1K input tokens
            'claude-v2': 0.008,          # $0.008 per 1K input tokens
            'titan-text-express': 0.0002,# $0.0002 per 1K input tokens
            'titan-text-lite': 0.00015   # $0.00015 per 1K input tokens
        },
        'output_cost': {
            'claude-instant': 0.0024,    # $0.0024 per 1K output tokens
            'claude-v2': 0.024,          # $0.024 per 1K output tokens
            'titan-text-express': 0.0006,# $0.0006 per 1K output tokens
            'titan-text-lite': 0.0002    # $0.0002 per 1K output tokens
        }
    },
    'google': {
        'models': ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash'],
        'input_cost': {
            'gemini-pro': 0.00025,       # $0.00025 per 1K input tokens
            'gemini-1.5-pro': 0.00125,   # $0.00125 per 1K input tokens
            'gemini-1.5-flash': 0.000075 # $0.000075 per 1K input tokens
        },
        'output_cost': {
            'gemini-pro': 0.0005,        # $0.0005 per 1K output tokens
            'gemini-1.5-pro': 0.00375,   # $0.00375 per 1K output tokens
            'gemini-1.5-flash': 0.0003   # $0.0003 per 1K output tokens
        }
    },
    'cohere': {
        'models': ['command', 'command-light', 'command-r'],
        'input_cost': {
            'command': 0.001,            # $0.001 per 1K input tokens
            'command-light': 0.0003,     # $0.0003 per 1K input tokens
            'command-r': 0.0005          # $0.0005 per 1K input tokens
        },
        'output_cost': {
            'command': 0.002,            # $0.002 per 1K output tokens
            'command-light': 0.0006,     # $0.0006 per 1K output tokens
            'command-r': 0.0015          # $0.0015 per 1K output tokens
        }
    },
    'mistral': {
        'models': ['mistral-large', 'mistral-medium', 'mistral-small'],
        'input_cost': {
            'mistral-large': 0.004,      # $0.004 per 1K input tokens
            'mistral-medium': 0.0027,    # $0.0027 per 1K input tokens
            'mistral-small': 0.0001      # $0.0001 per 1K input tokens
        },
        'output_cost': {
            'mistral-large': 0.012,      # $0.012 per 1K output tokens
            'mistral-medium': 0.0081,    # $0.0081 per 1K output tokens
            'mistral-small': 0.0003      # $0.0003 per 1K output tokens
        }
    },
    'azure': {
        'models': ['gpt-4-azure', 'gpt-35-turbo-azure'],
        'input_cost': {
            'gpt-4-azure': 0.03,         # $0.03 per 1K input tokens
            'gpt-35-turbo-azure': 0.0005 # $0.0005 per 1K input tokens
        },
        'output_cost': {
            'gpt-4-azure': 0.06,         # $0.06 per 1K output tokens
            'gpt-35-turbo-azure': 0.0015 # $0.0015 per 1K output tokens
        }
    }
}
```

**Provider Distribution** (weighted by market share and realistic usage):
- **OpenAI**: 40% (dominant market share)
- **Anthropic**: 25% (growing enterprise adoption)
- **Google**: 15% (Gemini adoption)
- **Bedrock**: 10% (AWS enterprise customers)
- **Azure**: 5% (Microsoft enterprise customers)
- **Mistral**: 3% (European/open-source preference)
- **Cohere**: 2% (specialized use cases)

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

### 4. Multi-Tenant Variability Simulator

**File**: `src/simulator/scenarios/multi_tenant.py`

**Class**: `MultiTenantSimulator`

**Purpose**: Simulate realistic variability across different organizations and products

**Variability Characteristics**:
- **Organization-Level**: Different base usage rates per org (3x-10x variance)
- **Product-Level**: Different feature adoption within each org
- **Tier Distribution**: Realistic tier distribution per organization
- **Provider Preference**: Different orgs prefer different providers

**Configuration**:
```python
def __init__(self,
             num_organizations: int = 10,
             customers_per_org: int = 20,
             num_days: int = 30,
             seed: Optional[int] = None):
    # Organization characteristics
    self.org_usage_multipliers = {
        'org_001': 5.0,   # High usage enterprise
        'org_002': 1.2,   # Small business
        'org_003': 8.5,   # Very high usage
        # ... dynamically generated
    }
    self.org_provider_preference = {
        'org_001': 'openai',    # OpenAI preference
        'org_002': 'anthropic', # Anthropic preference
        'org_003': 'google',    # Multi-cloud strategy
    }
```

**Use Cases**:
- Multi-tenant SaaS cost allocation
- Organization-level profitability
- Provider consolidation analysis
- Chargeback/showback reporting

### 5. Model Migration Simulator

**File**: `src/simulator/scenarios/model_migration.py`

**Class**: `ModelMigrationSimulator`

**Purpose**: Simulate gradual migration between AI models/providers over time

**Migration Characteristics**:
- **Timeline**: 7-30 days for complete migration
- **Pattern**: Gradual shift with overlap period
- **Common Migrations**:
  - GPT-4 → GPT-4-turbo (cost optimization)
  - GPT-4 → Claude Sonnet (quality + cost)
  - Single provider → Multi-provider (risk reduction)

**Configuration**:
```python
def __init__(self,
             num_customers: int = 40,
             num_days: int = 30,
             migration_start_day: int = 10,
             migration_duration: int = 14,
             source_model: str = 'gpt-4',
             target_model: str = 'claude-sonnet-4',
             seed: Optional[int] = None):
    self.source_model = source_model
    self.target_model = target_model
    self.migration_start = migration_start_day
    self.migration_duration = migration_duration
```

**Migration Curve**:
```python
# S-curve migration pattern (slow start, fast middle, slow end)
progress = (current_day - migration_start) / migration_duration
target_percentage = 1 / (1 + exp(-10 * (progress - 0.5)))

# Mix calls between source and target
if random() < target_percentage:
    use_target_model()
else:
    use_source_model()
```

**Use Cases**:
- Model evaluation and A/B testing
- Cost optimization tracking
- Provider negotiation leverage
- Migration impact analysis

### 6. Weekend Effect Simulator

**File**: `src/simulator/scenarios/weekend_effect.py`

**Class**: `WeekendEffectSimulator`

**Purpose**: Realistic weekend and holiday usage reduction

**Weekend Characteristics**:
- **Saturday**: 40-60% of weekday volume
- **Sunday**: 30-50% of weekday volume
- **Holidays**: 20-40% of weekday volume
- **Friday afternoon**: 70% taper after 3pm

**Configuration**:
```python
def __init__(self,
             num_customers: int = 50,
             num_days: int = 30,
             weekend_reduction: float = 0.55,  # 55% reduction
             holiday_dates: List[int] = [7, 21],
             seed: Optional[int] = None):
    self.weekend_reduction = weekend_reduction
    self.holiday_dates = holiday_dates
```

**Use Cases**:
- Capacity planning
- Reserved instance optimization
- Cost forecasting
- Anomaly detection (unexpected weekend spikes)

### 7. Time Zone Patterns Simulator

**File**: `src/simulator/scenarios/timezone_patterns.py`

**Class**: `TimeZoneSimulator`

**Purpose**: Simulate global usage following time zones (24-hour coverage)

**Time Zone Distribution**:
- **US East (EST)**: 30% of customers, peak 9am-5pm EST
- **US West (PST)**: 20% of customers, peak 9am-5pm PST
- **Europe (GMT/CET)**: 25% of customers, peak 9am-5pm CET
- **Asia Pacific (IST/JST)**: 25% of customers, peak 9am-5pm local

**Configuration**:
```python
def __init__(self,
             num_customers: int = 100,
             num_days: int = 30,
             timezone_distribution: Dict[str, float] = {
                 'US/Eastern': 0.30,
                 'US/Pacific': 0.20,
                 'Europe/London': 0.15,
                 'Europe/Paris': 0.10,
                 'Asia/Tokyo': 0.15,
                 'Asia/Kolkata': 0.10
             },
             seed: Optional[int] = None):
    self.timezone_distribution = timezone_distribution
```

**Use Cases**:
- Global SaaS platforms
- Follow-the-sun support patterns
- Regional cost analysis
- Peak load distribution

### 8. Feature Launch Simulator

**File**: `src/simulator/scenarios/feature_launch.py`

**Class**: `FeatureLaunchSimulator`

**Purpose**: Simulate adoption spike from new feature launch

**Launch Characteristics**:
- **Pre-Launch**: Baseline usage
- **Launch Day**: 3-5x spike in specific feature
- **First Week**: Gradual adoption curve
- **Steady State**: 2x baseline (40% adoption)

**Configuration**:
```python
def __init__(self,
             num_customers: int = 60,
             num_days: int = 30,
             launch_day: int = 10,
             feature_id: str = 'ai_assistant',
             adoption_rate: float = 0.40,  # 40% adoption
             seed: Optional[int] = None):
    self.launch_day = launch_day
    self.feature_id = feature_id
    self.adoption_rate = adoption_rate
```

**Use Cases**:
- Feature cost impact analysis
- Adoption tracking
- Capacity planning for launches
- ROI calculation for new features

### 9. Cost Optimization Simulator

**File**: `src/simulator/scenarios/cost_optimization.py`

**Class**: `CostOptimizationSimulator`

**Purpose**: Simulate engineering-led cost optimization efforts

**Optimization Actions**:
- **Days 1-10**: Baseline (expensive models)
- **Days 11-20**: Gradual migration to cheaper models
- **Days 21-30**: Optimized state (70% cost reduction for simple tasks)

**Optimizations Simulated**:
1. **Task Routing**: Route simple tasks to cheap models
2. **Model Downgrade**: GPT-4 → GPT-3.5-turbo for appropriate tasks
3. **Provider Arbitrage**: Switch to lowest-cost provider per task
4. **Caching**: Reduce duplicate calls by 30%

**Configuration**:
```python
def __init__(self,
             num_customers: int = 50,
             num_days: int = 30,
             optimization_start_day: int = 10,
             cost_reduction_target: float = 0.70,  # 70% reduction
             seed: Optional[int] = None):
    self.optimization_start = optimization_start_day
    self.target_reduction = cost_reduction_target
```

**Use Cases**:
- Demonstrate cost reduction impact
- Optimization ROI calculation
- Model selection strategy validation
- Engineering efficiency metrics

### 10. Steady Growth Simulator (Legacy)

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

**Purpose**: Continuously generate diverse AI traffic data until 50MB CSV size limit is reached

**Key Features**:
- **Continuous Generation**: Runs until CSV reaches 50MB (approximately 140,000-150,000 calls)
- **Size Monitoring**: Checks file size after each simulator iteration
- **Automatic Termination**: Stops when 50MB threshold is reached
- **Progress Reporting**: Real-time updates on file size and call count
- **Diverse Patterns**: Cycles through all scenario simulators for maximum variability

**Size Limit Configuration**:
```python
MAX_CSV_SIZE_MB = 50
MAX_CSV_SIZE_BYTES = MAX_CSV_SIZE_MB * 1024 * 1024  # 52,428,800 bytes

# Estimated bytes per call
BYTES_PER_CALL = 350  # ~350 bytes per CSV row with 19 fields

# Estimated total calls at 50MB
ESTIMATED_MAX_CALLS = MAX_CSV_SIZE_BYTES // BYTES_PER_CALL  # ~149,796 calls
```

**Execution Strategy**:
1. **Initialize**: Clear existing data, start with empty CSV
2. **Cycle Through Scenarios**: Run each simulator in rotation
3. **Check Size**: After each scenario, check CSV file size
4. **Continue or Stop**: If < 50MB, run next scenario; if >= 50MB, stop
5. **Final Report**: Display comprehensive statistics

**Execution Order (Rotating)**:
```python
SCENARIO_ROTATION = [
    ('Base Traffic', AICallSimulator, {'num_customers': 100, 'num_days': 10}),
    ('Seasonal Pattern', SeasonalPatternSimulator, {'num_customers': 50, 'num_days': 10}),
    ('Burst Traffic', BurstTrafficSimulator, {'num_customers': 30, 'num_days': 10}),
    ('Multi-Tenant', MultiTenantSimulator, {'num_organizations': 10, 'customers_per_org': 20}),
    ('Model Migration', ModelMigrationSimulator, {'num_customers': 40, 'num_days': 10}),
    ('Weekend Effect', WeekendEffectSimulator, {'num_customers': 50, 'num_days': 10}),
    ('Time Zone Patterns', TimeZoneSimulator, {'num_customers': 100, 'num_days': 10}),
    ('Feature Launch', FeatureLaunchSimulator, {'num_customers': 60, 'num_days': 10}),
    ('Cost Optimization', CostOptimizationSimulator, {'num_customers': 50, 'num_days': 10}),
    ('Gradual Decline', GradualDeclineSimulator, {'num_customers': 40, 'num_days': 10}),
]
```

**Size Monitoring Logic**:
```python
import os

def get_csv_size_mb(csv_path: str) -> float:
    """Get CSV file size in megabytes"""
    if not os.path.exists(csv_path):
        return 0.0
    size_bytes = os.path.getsize(csv_path)
    return size_bytes / (1024 * 1024)

def run_until_size_limit():
    csv_path = 'data/simulated_calls.csv'
    max_size_mb = 50
    iteration = 0

    while True:
        # Run next scenario in rotation
        scenario_idx = iteration % len(SCENARIO_ROTATION)
        scenario_name, SimulatorClass, config = SCENARIO_ROTATION[scenario_idx]

        print(f"\n📊 Running: {scenario_name} (Iteration {iteration + 1})")
        simulator = SimulatorClass(**config)
        simulator.generate(append=iteration > 0)

        # Check file size
        current_size = get_csv_size_mb(csv_path)
        print(f"   Current CSV Size: {current_size:.2f} MB / {max_size_mb} MB")

        if current_size >= max_size_mb:
            print(f"\n✅ Size limit reached: {current_size:.2f} MB")
            break

        iteration += 1

        # Safety limit to prevent infinite loops
        if iteration > 100:
            print(f"\n⚠️  Safety limit: Stopping after 100 iterations")
            break
```

**Usage**:
```bash
cd src
python3 run_all_simulators.py
```

**Output**:
```
🚀 CONTINUOUS TRAFFIC GENERATION (Target: 50 MB)
======================================================================

📊 Running: Base Traffic (Iteration 1)
   Generated 45,234 calls
   Current CSV Size: 15.82 MB / 50 MB

📊 Running: Seasonal Pattern (Iteration 2)
   Appended 18,456 calls
   Current CSV Size: 22.29 MB / 50 MB

📊 Running: Burst Traffic (Iteration 3)
   Appended 12,345 calls
   Current CSV Size: 26.61 MB / 50 MB

📊 Running: Multi-Tenant (Iteration 4)
   Appended 22,100 calls
   Current CSV Size: 34.35 MB / 50 MB

📊 Running: Model Migration (Iteration 5)
   Appended 15,890 calls
   Current CSV Size: 39.91 MB / 50 MB

📊 Running: Weekend Effect (Iteration 6)
   Appended 13,200 calls
   Current CSV Size: 44.53 MB / 50 MB

📊 Running: Time Zone Patterns (Iteration 7)
   Appended 17,800 calls
   Current CSV Size: 50.77 MB / 50 MB

✅ Size limit reached: 50.77 MB

======================================================================
📊 GENERATION COMPLETE
======================================================================

📈 Final Dataset Statistics:
   Total Calls: 145,025
   Unique Customers: 480+
   Unique Organizations: 30+
   Providers: 7 (OpenAI, Anthropic, Google, Bedrock, Azure, Mistral, Cohere)
   Models: 20+
   Total Cost: $38,492.18
   Total Tokens: 72,345,678
   Avg Cost/Call: $0.2654
   CSV Size: 50.77 MB
   Date Range: 30+ days with overlapping patterns

📊 Traffic Pattern Mix:
   - Base Traffic: 31.2%
   - Seasonal Patterns: 12.7%
   - Burst Spikes: 8.5%
   - Multi-Tenant: 15.2%
   - Model Migrations: 11.0%
   - Weekend Effect: 9.1%
   - Time Zones: 12.3%

🎯 Dataset Characteristics:
   ✓ Diverse: 7 providers, 20+ models
   ✓ Variable: 10 different traffic patterns
   ✓ Realistic: Time zones, weekends, holidays
   ✓ Complete: Organization → Product → Feature → Customer hierarchy
```

**Advantages of Continuous Generation**:
1. **Comprehensive Dataset**: Maximum variability and pattern coverage
2. **Consistent Size**: Always generates to 50MB limit (±1%)
3. **Reproducible**: Same seed produces same 50MB dataset
4. **Automatic**: No manual tuning of customer counts or days
5. **Balanced**: Equal representation from all scenario patterns

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
- **Continuous Generation to 50MB**: ~8-12 minutes for 145,000+ calls
- **Throughput**: ~200-250 calls/second sustained

### Memory Usage
- **Peak Memory**: ~200-300MB for continuous generation
- **Scales Linearly**: ~2MB per 1K calls
- **CSV Streaming**: Writes incrementally to avoid loading entire dataset

### Disk Usage
- **CSV Size**: ~350 bytes per call (average)
- **50MB Target**: ~145,000 calls
- **Actual Range**: 140,000-150,000 calls depending on pattern mix
- **Field Overhead**: 19 fields × ~18 chars average per field

### Generation Time Estimates
| Target Size | Estimated Calls | Estimated Time | Unique Customers |
|-------------|-----------------|----------------|------------------|
| 10 MB       | ~29,000         | ~2 minutes     | ~100             |
| 25 MB       | ~72,000         | ~5 minutes     | ~250             |
| 50 MB       | ~145,000        | ~10 minutes    | ~500             |
| 100 MB      | ~290,000        | ~20 minutes    | ~1,000           |

### Scalability Considerations
- **Linear Scaling**: Generation time scales linearly with target size
- **No Memory Bloat**: CSV append mode prevents memory accumulation
- **Batch Writing**: Writes in batches of 1,000 calls for efficiency
- **Progress Reporting**: Real-time updates every 5,000 calls

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
