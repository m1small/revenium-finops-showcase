# Simulation Engine Specification

## Core Simulator

### Base Functionality

The traffic simulator generates realistic AI API call patterns with configurable scenarios.

#### Initialization

Required parameters:
- csv_path: Output file path
- seed: Random number generator seed for reproducibility

Core data structures:
- Providers: List of (name, weight) tuples for selection
- Models: Dictionary mapping provider to list of (model, input_price, output_price) tuples
- Customers: Dictionary tracking customer metadata
- Organizations: Dictionary tracking organization metadata

#### Provider Selection Algorithm

```
function select_provider(providers):
    total_weight = sum(weight for name, weight in providers)
    random_value = random() * total_weight
    cumulative = 0
    for name, weight in providers:
        cumulative += weight
        if random_value <= cumulative:
            return name
```

#### Model Selection Algorithm

```
function select_model(provider, models):
    model_list = models[provider]
    return random_choice(model_list)
```

#### Customer Generation

Customer ID format: cust-{uuid}

Archetype assignment:
```
random_value = random()
if random_value < 0.70:
    archetype = "light"
elif random_value < 0.90:
    archetype = "power"
else:
    archetype = "heavy"
```

Tier assignment:
```
random_value = random()
if random_value < 0.40:
    tier = "starter", price = 49.0
elif random_value < 0.85:
    tier = "pro", price = 199.0
else:
    tier = "enterprise", price = 999.0
```

#### Token Generation

Input tokens:
```
mean = 500
std_dev = 400
value = clamp(normal_distribution(mean, std_dev), min=50, max=2000)
return int(value)
```

Output tokens:
```
mean = 300
std_dev = 200
value = clamp(normal_distribution(mean, std_dev), min=50, max=1000)
return int(value)
```

#### Latency Calculation

```
function calculate_latency(total_tokens, region):
    base_latency = (total_tokens / 10) + random(50, 200)

    region_multiplier = {
        "us-east": 1.0,
        "us-west": 1.1,
        "eu-west": 1.3,
        "ap-southeast": 1.5
    }[region]

    provider_variance = uniform(0.8, 1.2)

    return base_latency * region_multiplier * provider_variance
```

#### Cost Calculation

```
function calculate_cost(input_tokens, output_tokens, model_pricing):
    input_cost = (input_tokens / 1000) * model_pricing.input_price
    output_cost = (output_tokens / 1000) * model_pricing.output_price
    return input_cost + output_cost
```

#### Status and Error Generation

```
function determine_status():
    if random() < 0.95:
        return "success", None
    else:
        error_types = ["timeout", "rate_limit", "auth_error", "server_error"]
        error_weights = [0.40, 0.30, 0.15, 0.15]
        return "error", weighted_choice(error_types, error_weights)
```

### Batch Writing

Performance optimization for large datasets:

```
function run_with_batching(duration_hours, calls_per_hour, batch_size=5000):
    total_calls = duration_hours * calls_per_hour
    batches = total_calls / batch_size

    buffer = []
    for i in range(total_calls):
        call = generate_call()
        buffer.append(call)

        if len(buffer) >= batch_size:
            write_batch_to_csv(buffer)
            buffer.clear()

    if buffer:
        write_batch_to_csv(buffer)
```

## Scenario Simulators

### Scenario 1: Base Traffic

Steady, predictable traffic pattern.

Configuration:
- duration_hours: Simulation time span
- calls_per_hour: Constant rate

Multiplier: 1.0 (no variation)

### Scenario 2: Seasonal Pattern

Cyclical variation over time.

```
function seasonal_multiplier(hour_offset):
    cycle_hours = 168  # One week
    position = (hour_offset % cycle_hours) / cycle_hours
    multiplier = 0.5 + 0.5 * sin(2 * pi * position)
    return multiplier
```

### Scenario 3: Burst Traffic

Unpredictable spikes in traffic.

```
function burst_multiplier():
    if random() < 0.05:  # 5% chance of burst
        return random(5, 20)  # 5x to 20x multiplier
    else:
        return 1.0
```

### Scenario 4: Multi-Tenant

Organization-level traffic variation.

```
function multi_tenant_multiplier(organization_id):
    org_sizes = {
        "small": 0.3,
        "medium": 1.0,
        "large": 3.0
    }

    # Assign organization size (persistent)
    if organization_id not in org_cache:
        weights = [0.50, 0.35, 0.15]  # 50% small, 35% medium, 15% large
        org_cache[organization_id] = weighted_choice(org_sizes.keys(), weights)

    return org_sizes[org_cache[organization_id]]
```

### Scenario 5: Model Migration

Gradual shift from one model to another.

```
function migration_model_selection(hour_offset, duration_hours):
    progress = hour_offset / duration_hours

    if random() < progress:
        return new_model
    else:
        return old_model
```

### Scenario 6: Weekend Effect

Reduced traffic on weekends.

```
function weekend_multiplier(timestamp):
    day_of_week = timestamp.day_of_week

    if day_of_week in [0, 6]:  # Sunday, Saturday
        return 0.3
    else:
        return 1.0
```

### Scenario 7: Timezone Pattern

24-hour usage pattern following global timezones.

```
function timezone_multiplier(hour_of_day):
    # Peak hours: 9 AM - 5 PM
    if 9 <= hour_of_day < 17:
        return 1.5
    # Off hours: 11 PM - 6 AM
    elif hour_of_day < 6 or hour_of_day >= 23:
        return 0.3
    else:
        return 1.0
```

### Scenario 8: Feature Launch

Adoption spike followed by stabilization.

```
function feature_launch_multiplier(hour_offset, duration_hours):
    peak_time = duration_hours * 0.2  # Peak at 20% through simulation

    if hour_offset < peak_time:
        # Growth phase
        return 1.0 + (hour_offset / peak_time) * 2.0
    else:
        # Decay to steady state
        time_since_peak = hour_offset - peak_time
        decay_rate = 0.01
        return 3.0 * exp(-decay_rate * time_since_peak) + 1.0
```

### Scenario 9: Cost Optimization

Gradual reduction in costs through efficiency improvements.

```
function cost_optimization_multiplier(hour_offset, duration_hours):
    progress = hour_offset / duration_hours
    cost_reduction = 0.5  # 50% cost reduction target

    return 1.0 - (progress * cost_reduction)
```

Model migration during optimization:
```
function optimization_model_shift(progress):
    if progress < 0.3:
        return expensive_models  # GPT-4, Claude Opus
    elif progress < 0.7:
        return mid_tier_models   # GPT-3.5 Turbo, Claude Sonnet
    else:
        return efficient_models  # Gemini Pro, Claude Haiku
```

### Scenario 10: Gradual Decline

Customer churn simulation.

```
function churn_multiplier(hour_offset, duration_hours):
    progress = hour_offset / duration_hours
    max_decline = 0.7  # 70% reduction

    return 1.0 - (progress * max_decline)
```

### Scenario 11: Steady Growth

Linear traffic increase.

```
function growth_multiplier(hour_offset, duration_hours):
    progress = hour_offset / duration_hours
    growth_factor = 3.0  # 3x growth over period

    return 1.0 + (progress * (growth_factor - 1.0))
```

### Scenario 12: Viral Spike

Exponential growth followed by plateau.

```
function viral_multiplier(hour_offset, duration_hours):
    viral_peak_time = duration_hours * 0.3

    if hour_offset < viral_peak_time:
        # Exponential growth
        growth_rate = 0.05
        return exp(growth_rate * hour_offset)
    else:
        # Plateau at peak
        max_multiplier = exp(growth_rate * viral_peak_time)
        return max_multiplier
```

## Execution Flow

### Continuous Generation

```
function run_continuous_simulation(target_size_mb, scenarios):
    current_size = get_file_size(csv_path)
    scenario_index = 0

    while current_size < target_size_mb:
        scenario = scenarios[scenario_index % len(scenarios)]
        run_scenario(scenario)

        current_size = get_file_size(csv_path)
        display_progress(current_size, target_size_mb)
        scenario_index += 1

    print("Target size reached")
```

### Progress Display

```
function display_progress(current_mb, target_mb):
    progress_percent = (current_mb / target_mb) * 100
    bar_width = 50
    filled = int(bar_width * (current_mb / target_mb))

    bar = "=" * filled + "-" * (bar_width - filled)
    print(f"[{bar}] {progress_percent:.1f}% ({current_mb:.2f} MB / {target_mb:.2f} MB)")
```

## Data Quality Assurance

### Validation Rules

1. Ensure timestamp monotonically increases
2. Verify all required fields present
3. Check numeric fields within valid ranges
4. Validate foreign key relationships (provider-model)
5. Confirm calculated fields match source data

### Performance Targets

- Generation rate: 1000+ calls per second
- Memory usage: Linear with batch size
- Disk I/O: Optimized through batching
- Target size accuracy: +/- 1%
