# Advanced Analytics Specification

## Analyzer 9: Dataset Overview

Purpose: Comprehensive dataset statistics and distribution metrics.

### File Information Analysis

```
function analyze_file_info(csv_path):
    file_size_bytes = get_file_size(csv_path)
    file_size_gb = file_size_bytes / (1024^3)
    total_records = count_lines(csv_path) - 1  # Exclude header

    return {
        "file_path": csv_path,
        "file_size_bytes": file_size_bytes,
        "file_size_gb": round(file_size_gb, 2),
        "total_records": total_records,
        "analysis_timestamp": current_timestamp()
    }
```

### Scale Metrics

```
function analyze_scale_metrics(calls):
    unique_organizations = unique_count(c["organization_id"] for c in calls)
    unique_customers = unique_count(c["customer_id"] for c in calls)
    unique_products = unique_count(c["product_id"] for c in calls)
    unique_features = unique_count(c["feature_id"] for c in calls)

    return {
        "unique_organizations": unique_organizations,
        "unique_customers": unique_customers,
        "unique_products": unique_products,
        "unique_features": unique_features
    }
```

### Temporal Range Analysis

```
function analyze_temporal_range(calls):
    if not calls:
        return {"start_time": null, "end_time": null, "duration_hours": 0}

    timestamps = [c["timestamp"] for c in calls]
    start_time = min(timestamps)
    end_time = max(timestamps)
    duration = end_time - start_time
    duration_hours = duration.total_seconds() / 3600

    # Human-readable duration
    if duration_hours < 1:
        duration_desc = f"{duration.total_seconds() / 60} minutes"
    elif duration_hours < 24:
        duration_desc = f"{duration_hours:.1f} hours"
    else:
        duration_desc = f"{duration_hours / 24:.1f} days"

    return {
        "start_time": start_time,
        "end_time": end_time,
        "duration_hours": round(duration_hours, 2),
        "duration_description": duration_desc
    }
```

### Quality Metrics

```
function analyze_quality_metrics(calls):
    status_distribution = {}
    for call in calls:
        status = call["status"]
        status_distribution[status] = status_distribution.get(status, 0) + 1

    success_count = status_distribution.get("success", 0)
    total_count = len(calls)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0

    return {
        "total_records": total_count,
        "success_count": success_count,
        "error_count": total_count - success_count,
        "success_rate_percentage": round(success_rate, 2),
        "status_distribution": status_distribution
    }
```

## Analyzer 10: Token Economics

Purpose: Token-level cost analysis and efficiency metrics.

### Token Efficiency by Model

```
function analyze_token_efficiency(calls):
    model_groups = group_by(calls, "provider", "model")
    efficiency_report = []

    for (provider, model), model_calls in model_groups:
        total_tokens = sum(c["total_tokens"] for c in model_calls)
        total_cost = sum(c["cost_usd"] for c in model_calls)

        # Tokens per dollar
        tokens_per_dollar = safe_divide(total_tokens, total_cost)

        # Cost per 1M tokens
        cost_per_1m_tokens = safe_divide(total_cost * 1_000_000, total_tokens)

        # Input/output ratio
        total_input = sum(c["input_tokens"] for c in model_calls)
        total_output = sum(c["output_tokens"] for c in model_calls)
        io_ratio = safe_divide(total_output, total_input)

        efficiency_report.append({
            "provider": provider,
            "model": model,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "tokens_per_dollar": tokens_per_dollar,
            "cost_per_1m_tokens": cost_per_1m_tokens,
            "input_output_ratio": io_ratio,
            "call_count": len(model_calls)
        })

    return sort_by(efficiency_report, "tokens_per_dollar", descending=true)
```

### Wasteful Patterns Detection

```
function detect_wasteful_patterns(calls):
    patterns = []

    # Pattern 1: High input/low output (inefficient prompts)
    for call in calls:
        input_tokens = call["input_tokens"]
        output_tokens = call["output_tokens"]
        io_ratio = safe_divide(output_tokens, input_tokens)

        if input_tokens > 1000 and io_ratio < 0.1:
            patterns.append({
                "type": "inefficient_prompt",
                "customer_id": call["customer_id"],
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "waste_score": input_tokens * 0.9  # 90% of input wasted
            })

    # Pattern 2: Expensive model for simple tasks
    simple_call_threshold = 200  # Total tokens
    for call in calls:
        if call["total_tokens"] < simple_call_threshold:
            # Check if using expensive model
            model_cost_per_1k = calculate_model_cost_per_1k(call["model"])
            if model_cost_per_1k > 5.0:  # Expensive model
                patterns.append({
                    "type": "overpriced_simple_task",
                    "customer_id": call["customer_id"],
                    "model": call["model"],
                    "total_tokens": call["total_tokens"],
                    "cost": call["cost_usd"]
                })

    return patterns
```

### Optimization Opportunities

```
function identify_optimization_opportunities(calls):
    opportunities = []

    # Group by customer and model
    customer_model_groups = group_by(calls, "customer_id", "model")

    for (customer_id, current_model), usage_calls in customer_model_groups:
        current_cost = sum_cost(usage_calls)
        total_tokens = sum(c["total_tokens"] for c in usage_calls)

        # Find cheaper alternatives with similar capabilities
        for alternative_model in get_similar_models(current_model):
            alternative_cost = estimate_cost_with_model(
                usage_calls, alternative_model
            )

            savings = current_cost - alternative_cost
            if savings > 1.0:  # Minimum $1 savings
                opportunities.append({
                    "customer_id": customer_id,
                    "current_model": current_model,
                    "alternative_model": alternative_model,
                    "current_cost": current_cost,
                    "alternative_cost": alternative_cost,
                    "savings": savings,
                    "savings_percent": (savings / current_cost) * 100
                })

    return sort_by(opportunities, "savings", descending=true)
```

## Analyzer 11: Geographic Latency

Purpose: Regional performance and latency analysis.

### Regional Latency Analysis

```
function analyze_regional_latency(calls):
    region_groups = group_by(calls, "region")
    regional_analysis = []

    for (region,), region_calls in region_groups:
        latencies = [c["latency_ms"] for c in region_calls]
        sorted_latencies = sorted(latencies)

        regional_analysis.append({
            "region": region,
            "call_count": len(region_calls),
            "avg_latency_ms": average(latencies),
            "p50_latency_ms": percentile(sorted_latencies, 0.50),
            "p95_latency_ms": percentile(sorted_latencies, 0.95),
            "p99_latency_ms": percentile(sorted_latencies, 0.99),
            "sla_violations": count(l > SLA_THRESHOLD_MS for l in latencies)
        })

    return sort_by(regional_analysis, "avg_latency_ms", ascending=true)
```

### Provider-Region Performance

```
function analyze_provider_region_performance(calls):
    provider_region_groups = group_by(calls, "provider", "region")
    performance_matrix = []

    for (provider, region), calls in provider_region_groups:
        latencies = [c["latency_ms"] for c in calls]

        performance_matrix.append({
            "provider": provider,
            "region": region,
            "avg_latency_ms": average(latencies),
            "p95_latency_ms": percentile(sorted(latencies), 0.95),
            "call_count": len(calls)
        })

    return performance_matrix
```

### Routing Recommendations

```
function generate_routing_recommendations(performance_matrix):
    recommendations = []

    # Group by region to find best provider per region
    region_groups = group_by(performance_matrix, "region")

    for (region,), region_data in region_groups:
        # Find provider with lowest average latency
        best_provider = min(region_data, key=lambda x: x["avg_latency_ms"])

        # Find providers exceeding SLA
        poor_performers = filter(
            data for data in region_data
            if data["avg_latency_ms"] > SLA_THRESHOLD_MS
        )

        if poor_performers:
            for poor in poor_performers:
                latency_improvement = poor["avg_latency_ms"] - best_provider["avg_latency_ms"]

                recommendations.append({
                    "region": region,
                    "current_provider": poor["provider"],
                    "recommended_provider": best_provider["provider"],
                    "current_latency": poor["avg_latency_ms"],
                    "recommended_latency": best_provider["avg_latency_ms"],
                    "improvement_ms": latency_improvement,
                    "improvement_percent": (latency_improvement / poor["avg_latency_ms"]) * 100
                })

    return recommendations
```

## Analyzer 12: Churn & Growth

Purpose: Customer lifecycle patterns and growth trends.

### Churn Analysis

```
function analyze_churn_patterns(calls):
    # Group calls by customer and day
    customer_daily_activity = {}

    for call in calls:
        customer_id = call["customer_id"]
        day = call["timestamp"].date()

        if customer_id not in customer_daily_activity:
            customer_daily_activity[customer_id] = []
        customer_daily_activity[customer_id].append(day)

    # Identify churned customers (no activity in last 30 days)
    latest_date = max(call["timestamp"].date() for call in calls)
    churn_threshold_days = 30

    churned_customers = []
    for customer_id, activity_days in customer_daily_activity.items():
        last_activity = max(activity_days)
        days_inactive = (latest_date - last_activity).days

        if days_inactive >= churn_threshold_days:
            churned_customers.append({
                "customer_id": customer_id,
                "last_activity_date": last_activity,
                "days_inactive": days_inactive
            })

    churn_rate = (len(churned_customers) / len(customer_daily_activity)) * 100

    return {
        "total_customers": len(customer_daily_activity),
        "churned_customers": len(churned_customers),
        "churn_rate_percent": churn_rate,
        "churned_customer_list": churned_customers
    }
```

### Growth Trends

```
function analyze_growth_trends(calls):
    # Group by week
    weekly_groups = group_by_week(calls)

    weekly_metrics = []
    for week, week_calls in weekly_groups:
        unique_customers = unique_count(c["customer_id"] for c in week_calls)
        total_calls = len(week_calls)
        total_cost = sum_cost(week_calls)

        weekly_metrics.append({
            "week": week,
            "customer_count": unique_customers,
            "call_count": total_calls,
            "total_cost": total_cost
        })

    # Calculate week-over-week growth
    growth_analysis = []
    for i in range(1, len(weekly_metrics)):
        current = weekly_metrics[i]
        previous = weekly_metrics[i-1]

        customer_growth = ((current["customer_count"] - previous["customer_count"]) /
                          previous["customer_count"]) * 100
        call_growth = ((current["call_count"] - previous["call_count"]) /
                       previous["call_count"]) * 100
        revenue_growth = ((current["total_cost"] - previous["total_cost"]) /
                          previous["total_cost"]) * 100

        growth_analysis.append({
            "week": current["week"],
            "customer_growth_percent": customer_growth,
            "call_growth_percent": call_growth,
            "revenue_growth_percent": revenue_growth
        })

    return {
        "weekly_metrics": weekly_metrics,
        "growth_analysis": growth_analysis
    }
```

### Cohort Analysis

```
function analyze_cohorts(calls):
    # Group customers by first activity week
    customer_first_week = {}
    for call in calls:
        customer_id = call["customer_id"]
        week = get_week_number(call["timestamp"])

        if customer_id not in customer_first_week:
            customer_first_week[customer_id] = week

    # Create cohorts
    cohorts = {}
    for customer_id, first_week in customer_first_week.items():
        if first_week not in cohorts:
            cohorts[first_week] = []
        cohorts[first_week].append(customer_id)

    # Analyze cohort retention
    cohort_analysis = []
    for cohort_week, customer_list in cohorts.items():
        # Calculate retention over subsequent weeks
        retention_data = calculate_cohort_retention(
            customer_list, cohort_week, calls
        )

        cohort_analysis.append({
            "cohort_week": cohort_week,
            "cohort_size": len(customer_list),
            "retention_data": retention_data
        })

    return cohort_analysis
```

## Analyzer 13: Abuse Detection

Purpose: Anomaly and abuse pattern detection.

### Unusual Usage Patterns

```
function detect_unusual_usage(calls):
    # Calculate baseline usage per customer
    customer_groups = group_by(calls, "customer_id")
    customer_baselines = {}

    for (customer_id,), customer_calls in customer_groups:
        daily_call_counts = calculate_daily_call_counts(customer_calls)
        mean_daily_calls = average(daily_call_counts)
        std_dev_daily_calls = standard_deviation(daily_call_counts)

        customer_baselines[customer_id] = {
            "mean": mean_daily_calls,
            "std_dev": std_dev_daily_calls
        }

    # Detect anomalies
    anomalies = []
    for (customer_id,), customer_calls in customer_groups:
        baseline = customer_baselines[customer_id]
        daily_calls = calculate_daily_call_counts(customer_calls)

        for day, call_count in daily_calls:
            # Flag if > 3 standard deviations from mean
            if baseline["std_dev"] > 0:
                z_score = (call_count - baseline["mean"]) / baseline["std_dev"]
                if abs(z_score) > 3:
                    anomalies.append({
                        "customer_id": customer_id,
                        "date": day,
                        "call_count": call_count,
                        "baseline_mean": baseline["mean"],
                        "z_score": z_score,
                        "severity": "high" if abs(z_score) > 5 else "medium"
                    })

    return anomalies
```

### Rate Limit Abuse Detection

```
function detect_rate_limit_abuse(calls):
    # Group by customer and hour
    customer_hourly_groups = group_by(calls, "customer_id", "hour")

    abusive_patterns = []
    for (customer_id, hour), hour_calls in customer_hourly_groups:
        call_count = len(hour_calls)
        error_count = count(c for c in hour_calls if c["status"] == "error")
        rate_limit_errors = count(
            c for c in hour_calls
            if c["error_type"] == "rate_limit"
        )

        # Flag if excessive rate limit errors
        if rate_limit_errors > 10:  # Threshold: 10 rate limit errors per hour
            error_rate = (error_count / call_count) * 100

            abusive_patterns.append({
                "customer_id": customer_id,
                "hour": hour,
                "total_calls": call_count,
                "rate_limit_errors": rate_limit_errors,
                "error_rate_percent": error_rate,
                "severity": "critical" if rate_limit_errors > 50 else "warning"
            })

    return abusive_patterns
```

### Cost Spike Detection

```
function detect_cost_spikes(calls):
    # Group by customer and day
    customer_daily_costs = {}

    for call in calls:
        customer_id = call["customer_id"]
        day = call["timestamp"].date()
        cost = call["cost_usd"]

        if customer_id not in customer_daily_costs:
            customer_daily_costs[customer_id] = {}
        if day not in customer_daily_costs[customer_id]:
            customer_daily_costs[customer_id][day] = 0

        customer_daily_costs[customer_id][day] += cost

    # Detect spikes
    cost_spikes = []
    for customer_id, daily_costs in customer_daily_costs.items():
        costs = list(daily_costs.values())
        mean_cost = average(costs)
        std_dev = standard_deviation(costs)

        for day, cost in daily_costs.items():
            # Spike if > 3x mean
            if cost > mean_cost * 3 and std_dev > 0:
                z_score = (cost - mean_cost) / std_dev

                cost_spikes.append({
                    "customer_id": customer_id,
                    "date": day,
                    "cost": cost,
                    "baseline_mean": mean_cost,
                    "multiplier": cost / mean_cost,
                    "z_score": z_score
                })

    return sort_by(cost_spikes, "multiplier", descending=true)
```

### Suspicious Access Patterns

```
function detect_suspicious_access(calls):
    suspicious_patterns = []

    # Pattern 1: Multiple regions in short time
    customer_region_times = {}
    for call in calls:
        customer_id = call["customer_id"]
        region = call["region"]
        timestamp = call["timestamp"]

        if customer_id not in customer_region_times:
            customer_region_times[customer_id] = []

        customer_region_times[customer_id].append((region, timestamp))

    for customer_id, region_times in customer_region_times.items():
        # Sort by timestamp
        sorted_times = sorted(region_times, key=lambda x: x[1])

        # Check for region switches within 1 hour
        for i in range(1, len(sorted_times)):
            prev_region, prev_time = sorted_times[i-1]
            curr_region, curr_time = sorted_times[i]

            if prev_region != curr_region:
                time_diff = (curr_time - prev_time).total_seconds() / 3600

                if time_diff < 1:  # Less than 1 hour between regions
                    suspicious_patterns.append({
                        "type": "rapid_region_switch",
                        "customer_id": customer_id,
                        "from_region": prev_region,
                        "to_region": curr_region,
                        "time_between_hours": time_diff
                    })

    return suspicious_patterns
```
