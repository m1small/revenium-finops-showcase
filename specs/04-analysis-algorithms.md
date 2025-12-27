# Analysis Algorithms Specification

## Common Analysis Utilities

### Data Loading

```
function load_calls_from_csv(csv_path):
    calls = []
    with open(csv_path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            call = parse_row(row)
            calls.append(call)
    return calls
```

### Type Conversion

```
function parse_row(row):
    return {
        "timestamp": parse_datetime(row["timestamp"]),
        "organization_id": row["organization_id"],
        "product_id": row["product_id"],
        "feature_id": row["feature_id"],
        "customer_id": row["customer_id"],
        "customer_archetype": row["customer_archetype"],
        "subscription_tier": row["subscription_tier"],
        "tier_price_usd": float(row["tier_price_usd"]),
        "provider": row["provider"],
        "model": row["model"],
        "region": row["region"],
        "input_tokens": int(row["input_tokens"]),
        "output_tokens": int(row["output_tokens"]),
        "total_tokens": int(row["total_tokens"]),
        "latency_ms": float(row["latency_ms"]),
        "cost_usd": float(row["cost_usd"]),
        "status": row["status"],
        "error_type": row["error_type"],
        "metadata": row["metadata"]
    }
```

### Grouping

```
function group_by(calls, *keys):
    groups = {}
    for call in calls:
        key_values = tuple(call[k] for k in keys)
        if key_values not in groups:
            groups[key_values] = []
        groups[key_values].append(call)
    return groups
```

### Metric Aggregation

```
function aggregate_metrics(calls):
    if not calls:
        return empty_metrics()

    total_cost = sum(c["cost_usd"] for c in calls)
    total_tokens = sum(c["total_tokens"] for c in calls)
    total_input_tokens = sum(c["input_tokens"] for c in calls)
    total_output_tokens = sum(c["output_tokens"] for c in calls)

    latencies = sorted(c["latency_ms"] for c in calls)

    return {
        "call_count": len(calls),
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "avg_cost_per_call": total_cost / len(calls),
        "avg_tokens_per_call": total_tokens / len(calls),
        "avg_latency_ms": sum(latencies) / len(latencies),
        "p50_latency_ms": percentile(latencies, 0.50),
        "p95_latency_ms": percentile(latencies, 0.95),
        "p99_latency_ms": percentile(latencies, 0.99)
    }
```

### Percentile Calculation

```
function percentile(sorted_values, percentile):
    if not sorted_values:
        return 0
    index = int(len(sorted_values) * percentile)
    index = min(index, len(sorted_values) - 1)
    return sorted_values[index]
```

### Safe Division

```
function safe_divide(numerator, denominator, default=0):
    if denominator == 0:
        return default
    return numerator / denominator
```

## FinOps Domain Analyzers

### Analyzer 1: Understanding Usage & Cost

Purpose: Cost allocation, forecasting, and efficiency analysis.

#### Cost by Provider

```
function analyze_by_provider(calls):
    groups = group_by(calls, "provider")
    results = []

    for (provider,), provider_calls in groups:
        metrics = aggregate_metrics(provider_calls)
        results.append({
            "provider": provider,
            "call_count": metrics["call_count"],
            "total_cost": metrics["total_cost"],
            "total_tokens": metrics["total_tokens"],
            "avg_cost_per_call": metrics["avg_cost_per_call"]
        })

    return sort_by(results, "total_cost", descending=true)
```

#### Cost by Model

```
function analyze_by_model(calls):
    groups = group_by(calls, "provider", "model")
    results = []

    for (provider, model), model_calls in groups:
        metrics = aggregate_metrics(model_calls)
        cost_per_1k_tokens = safe_divide(
            metrics["total_cost"] * 1000,
            metrics["total_tokens"]
        )

        results.append({
            "provider": provider,
            "model": model,
            "call_count": metrics["call_count"],
            "total_cost": metrics["total_cost"],
            "cost_per_1k_tokens": cost_per_1k_tokens
        })

    return sort_by(results, "total_cost", descending=true)
```

#### Forecasting

```
function generate_forecast(calls):
    # Group by day
    daily_costs = group_by_day(calls)

    # Calculate daily average
    days_with_data = len(daily_costs)
    total_cost_to_date = sum(costs for day, costs in daily_costs)
    avg_daily_cost = total_cost_to_date / days_with_data

    # Project 30-day forecast
    forecast_30_days = avg_daily_cost * 30

    # Calculate trend
    if days_with_data >= 7:
        recent_avg = average(daily_costs[-7:])
        older_avg = average(daily_costs[:-7]) if days_with_data > 7 else recent_avg
        trend_percent = ((recent_avg - older_avg) / older_avg) * 100
    else:
        trend_percent = 0

    return {
        "forecast_30_days": forecast_30_days,
        "avg_daily_cost": avg_daily_cost,
        "trend_percent": trend_percent
    }
```

#### Cost Efficiency

```
function analyze_efficiency(calls):
    groups = group_by(calls, "provider", "model")
    efficiency_scores = []

    for (provider, model), model_calls in groups:
        metrics = aggregate_metrics(model_calls)

        # Efficiency = tokens per dollar
        efficiency = safe_divide(
            metrics["total_tokens"],
            metrics["total_cost"]
        )

        efficiency_scores.append({
            "provider": provider,
            "model": model,
            "efficiency": efficiency,
            "total_cost": metrics["total_cost"]
        })

    return sort_by(efficiency_scores, "efficiency", descending=true)
```

### Analyzer 2: Performance Tracking

Purpose: Model efficiency, latency percentiles, SLA compliance.

#### Latency Analysis

```
function analyze_latency(calls):
    latencies = [c["latency_ms"] for c in calls]
    sorted_latencies = sorted(latencies)

    return {
        "mean": average(latencies),
        "median": percentile(sorted_latencies, 0.50),
        "p95": percentile(sorted_latencies, 0.95),
        "p99": percentile(sorted_latencies, 0.99),
        "max": max(latencies),
        "sla_violations": count(l > SLA_THRESHOLD_MS for l in latencies)
    }
```

#### Model Efficiency Ranking

```
function rank_model_efficiency(calls):
    groups = group_by(calls, "provider", "model")
    rankings = []

    for (provider, model), model_calls in groups:
        metrics = aggregate_metrics(model_calls)

        # Tokens per second efficiency
        total_tokens = metrics["total_tokens"]
        total_time_seconds = sum(c["latency_ms"] for c in model_calls) / 1000
        tokens_per_second = safe_divide(total_tokens, total_time_seconds)

        rankings.append({
            "provider": provider,
            "model": model,
            "tokens_per_second": tokens_per_second,
            "avg_latency_ms": metrics["avg_latency_ms"],
            "p95_latency_ms": metrics["p95_latency_ms"]
        })

    return sort_by(rankings, "tokens_per_second", descending=true)
```

#### SLA Compliance

```
function calculate_sla_compliance(calls):
    by_provider = group_by(calls, "provider")
    compliance_report = []

    for (provider,), provider_calls in by_provider:
        total_calls = len(provider_calls)
        compliant_calls = count(
            c for c in provider_calls
            if c["latency_ms"] <= SLA_THRESHOLD_MS
        )

        compliance_rate = (compliant_calls / total_calls) * 100

        compliance_report.append({
            "provider": provider,
            "total_calls": total_calls,
            "compliant_calls": compliant_calls,
            "compliance_rate": compliance_rate,
            "violations": total_calls - compliant_calls
        })

    return sort_by(compliance_report, "compliance_rate", descending=true)
```

### Analyzer 3: Real-Time Decision Making

Purpose: Anomaly detection, threshold alerts, portfolio risk.

#### Anomaly Detection

```
function detect_anomalies(calls):
    # Calculate baseline by hour
    hourly_groups = group_by_hour(calls)
    hourly_costs = {hour: sum_cost(calls) for hour, calls in hourly_groups}

    # Calculate mean and standard deviation
    mean_cost = average(hourly_costs.values())
    std_dev = standard_deviation(hourly_costs.values())

    # Detect anomalies (3 standard deviations)
    threshold = mean_cost + (ANOMALY_MULTIPLIER * std_dev)

    anomalies = [
        {
            "hour": hour,
            "cost": cost,
            "deviation": (cost - mean_cost) / std_dev
        }
        for hour, cost in hourly_costs
        if cost > threshold
    ]

    return sort_by(anomalies, "deviation", descending=true)
```

#### Cost Alerts

```
function generate_cost_alerts(calls):
    alerts = []

    # Daily cost threshold
    daily_costs = group_by_day(calls)
    for day, day_calls in daily_costs:
        daily_cost = sum_cost(day_calls)
        if daily_cost > HIGH_COST_THRESHOLD_USD:
            alerts.append({
                "type": "high_daily_cost",
                "severity": "critical",
                "day": day,
                "cost": daily_cost,
                "threshold": HIGH_COST_THRESHOLD_USD
            })

    # Error rate threshold
    error_rate = calculate_error_rate(calls)
    if error_rate > 0.10:  # 10% error rate
        alerts.append({
            "type": "high_error_rate",
            "severity": "warning",
            "error_rate": error_rate,
            "threshold": 0.10
        })

    return alerts
```

#### Portfolio Risk Analysis

```
function analyze_portfolio_risk(calls):
    provider_groups = group_by(calls, "provider")

    # Calculate concentration risk
    total_cost = sum_cost(calls)
    provider_costs = {
        provider: sum_cost(provider_calls)
        for (provider,), provider_calls in provider_groups
    }

    max_concentration = max(cost / total_cost for cost in provider_costs.values())

    # Calculate diversity score (inverse of Herfindahl index)
    herfindahl = sum((cost / total_cost) ** 2 for cost in provider_costs.values())
    diversity_score = 1 - herfindahl

    return {
        "max_provider_concentration": max_concentration,
        "diversity_score": diversity_score,
        "provider_count": len(provider_groups),
        "risk_level": "high" if max_concentration > 0.60 else
                     "medium" if max_concentration > 0.40 else "low"
    }
```

### Analyzer 4: Rate Optimization

Purpose: Reserved capacity analysis, model switching opportunities.

#### Reserved Capacity Analysis

```
function analyze_reserved_capacity(calls):
    # Calculate baseline usage
    daily_usage = group_by_day(calls)
    daily_call_counts = [len(calls) for day, calls in daily_usage]

    # Determine steady-state usage (25th percentile)
    sorted_daily_counts = sorted(daily_call_counts)
    baseline_daily_calls = percentile(sorted_daily_counts, 0.25)

    # Estimate savings with reserved capacity
    # Assumption: 40% discount for committed usage
    total_cost = sum_cost(calls)
    baseline_cost_fraction = baseline_daily_calls / len(calls)
    committed_cost = total_cost * baseline_cost_fraction * 0.60  # 40% discount
    on_demand_cost = total_cost * (1 - baseline_cost_fraction)
    optimized_total = committed_cost + on_demand_cost

    savings = total_cost - optimized_total
    savings_percent = (savings / total_cost) * 100

    return {
        "current_cost": total_cost,
        "optimized_cost": optimized_total,
        "savings": savings,
        "savings_percent": savings_percent,
        "recommended_commitment": baseline_daily_calls
    }
```

#### Model Switching Opportunities

```
function identify_model_switches(calls):
    opportunities = []

    # Group by feature
    feature_groups = group_by(calls, "feature_id")

    for (feature,), feature_calls in feature_groups:
        # Get current model distribution
        model_usage = group_by(feature_calls, "model")

        for (current_model,), model_calls in model_usage:
            current_metrics = aggregate_metrics(model_calls)

            # Find cheaper alternatives
            for alternative_model in get_alternative_models(current_model):
                # Estimate cost with alternative
                cost_ratio = get_model_cost_ratio(alternative_model, current_model)
                estimated_savings = current_metrics["total_cost"] * (1 - cost_ratio)

                if estimated_savings > 0:
                    opportunities.append({
                        "feature": feature,
                        "current_model": current_model,
                        "alternative_model": alternative_model,
                        "current_cost": current_metrics["total_cost"],
                        "estimated_savings": estimated_savings,
                        "savings_percent": (1 - cost_ratio) * 100
                    })

    return sort_by(opportunities, "estimated_savings", descending=true)
```

### Analyzer 5: Organizational Alignment

Purpose: Multi-tenant tracking, chargeback, showback.

#### Chargeback Calculation

```
function calculate_chargeback(calls):
    org_groups = group_by(calls, "organization_id")
    chargeback_report = []

    for (org_id,), org_calls in org_groups:
        # Aggregate by product within organization
        product_breakdown = {}
        product_groups = group_by(org_calls, "product_id")

        for (product,), product_calls in product_groups:
            metrics = aggregate_metrics(product_calls)
            product_breakdown[product] = {
                "cost": metrics["total_cost"],
                "call_count": metrics["call_count"]
            }

        total_org_cost = sum_cost(org_calls)

        chargeback_report.append({
            "organization_id": org_id,
            "total_cost": total_org_cost,
            "product_breakdown": product_breakdown,
            "call_count": len(org_calls)
        })

    return sort_by(chargeback_report, "total_cost", descending=true)
```

#### Fair-Share Allocation

```
function calculate_fair_share(calls):
    # Calculate total cost
    total_cost = sum_cost(calls)

    # Group by organization
    org_groups = group_by(calls, "organization_id")

    allocations = []
    for (org_id,), org_calls in org_groups:
        org_cost = sum_cost(org_calls)
        org_share_percent = (org_cost / total_cost) * 100

        allocations.append({
            "organization_id": org_id,
            "cost": org_cost,
            "share_percent": org_share_percent,
            "call_count": len(org_calls)
        })

    return sort_by(allocations, "share_percent", descending=true)
```

## UBR Domain Analyzers

### Analyzer 6: Customer Profitability

Purpose: Margin analysis, unprofitable customer detection.

#### Profitability Calculation

```
function analyze_customer_profitability(calls):
    customer_groups = group_by(calls, "customer_id")
    profitability_report = []

    for (customer_id,), customer_calls in customer_groups:
        # Get customer tier price (monthly revenue)
        tier_price = customer_calls[0]["tier_price_usd"]
        tier = customer_calls[0]["subscription_tier"]

        # Calculate costs
        total_cost = sum_cost(customer_calls)
        call_count = len(customer_calls)

        # Monthly revenue = tier price
        monthly_revenue = tier_price

        # Calculate margin
        monthly_margin = monthly_revenue - total_cost
        margin_percent = safe_divide(monthly_margin, monthly_revenue) * 100

        # Classify profitability
        if margin_percent >= HIGH_MARGIN_THRESHOLD_PCT:
            category = "high_margin"
        elif margin_percent >= MEDIUM_MARGIN_THRESHOLD_PCT:
            category = "medium_margin"
        elif margin_percent >= LOW_MARGIN_THRESHOLD_PCT:
            category = "low_margin"
        else:
            category = "unprofitable"

        profitability_report.append({
            "customer_id": customer_id,
            "tier": tier,
            "monthly_revenue": monthly_revenue,
            "monthly_cost": total_cost,
            "monthly_margin": monthly_margin,
            "margin_percent": margin_percent,
            "category": category,
            "call_count": call_count
        })

    return sort_by(profitability_report, "margin_percent", ascending=true)
```

#### Unprofitable Customer Detection

```
function identify_unprofitable_customers(profitability_report):
    unprofitable = filter(
        report for report in profitability_report
        if report["margin_percent"] < UNPROFITABLE_THRESHOLD_PCT
    )

    total_loss = sum(report["monthly_margin"] for report in unprofitable)

    return {
        "count": len(unprofitable),
        "total_monthly_loss": total_loss,
        "customers": unprofitable
    }
```

### Analyzer 7: Pricing Strategy

Purpose: Pricing model comparison, revenue projections.

#### Pricing Models

```
function compare_pricing_models(calls):
    customer_usage = group_by(calls, "customer_id")

    models = {
        "flat_rate": calculate_flat_rate_revenue(customer_usage),
        "usage_based": calculate_usage_based_revenue(customer_usage),
        "tiered": calculate_tiered_revenue(customer_usage),
        "hybrid": calculate_hybrid_revenue(customer_usage)
    }

    return models
```

#### Flat Rate Model

```
function calculate_flat_rate_revenue(customer_usage):
    total_revenue = 0

    for (customer_id,), customer_calls in customer_usage:
        tier_price = customer_calls[0]["tier_price_usd"]
        total_revenue += tier_price

    return {
        "model": "flat_rate",
        "total_revenue": total_revenue,
        "avg_revenue_per_customer": total_revenue / len(customer_usage)
    }
```

#### Usage-Based Model

```
function calculate_usage_based_revenue(customer_usage):
    # Price per 1000 calls
    price_per_1k_calls = 100.0
    total_revenue = 0

    for (customer_id,), customer_calls in customer_usage:
        call_count = len(customer_calls)
        usage_revenue = (call_count / 1000) * price_per_1k_calls
        total_revenue += usage_revenue

    return {
        "model": "usage_based",
        "total_revenue": total_revenue,
        "price_per_1k_calls": price_per_1k_calls
    }
```

#### Tiered Model

```
function calculate_tiered_revenue(customer_usage):
    tiers = [
        {"max_calls": 1000, "price": 49},
        {"max_calls": 10000, "price": 199},
        {"max_calls": Infinity, "price": 999}
    ]

    total_revenue = 0

    for (customer_id,), customer_calls in customer_usage:
        call_count = len(customer_calls)

        # Find appropriate tier
        for tier in tiers:
            if call_count <= tier["max_calls"]:
                total_revenue += tier["price"]
                break

    return {
        "model": "tiered",
        "total_revenue": total_revenue,
        "tiers": tiers
    }
```

#### Hybrid Model

```
function calculate_hybrid_revenue(customer_usage):
    # Base subscription + usage overage
    base_price = 99.0
    overage_threshold = 5000
    overage_price_per_1k = 50.0

    total_revenue = 0

    for (customer_id,), customer_calls in customer_usage:
        call_count = len(customer_calls)

        # Base subscription
        revenue = base_price

        # Overage charges
        if call_count > overage_threshold:
            overage_calls = call_count - overage_threshold
            overage_revenue = (overage_calls / 1000) * overage_price_per_1k
            revenue += overage_revenue

        total_revenue += revenue

    return {
        "model": "hybrid",
        "total_revenue": total_revenue,
        "base_price": base_price,
        "overage_threshold": overage_threshold
    }
```

### Analyzer 8: Feature Economics

Purpose: Feature profitability, investment recommendations.

#### Feature ROI Analysis

```
function analyze_feature_roi(calls):
    feature_groups = group_by(calls, "feature_id")
    roi_analysis = []

    for (feature,), feature_calls in feature_groups:
        # Calculate costs
        total_cost = sum_cost(feature_calls)

        # Count unique customers using feature
        unique_customers = unique_count(c["customer_id"] for c in feature_calls)

        # Estimate revenue attribution
        # Assume feature contributes proportionally to customer subscription
        total_revenue = sum(c["tier_price_usd"] for c in feature_calls)
        feature_revenue = total_revenue / count_unique_features_per_customer(calls)

        # Calculate ROI
        roi = safe_divide(feature_revenue - total_cost, total_cost) * 100

        roi_analysis.append({
            "feature": feature,
            "cost": total_cost,
            "revenue": feature_revenue,
            "roi_percent": roi,
            "customer_count": unique_customers,
            "call_count": len(feature_calls)
        })

    return sort_by(roi_analysis, "roi_percent", descending=true)
```

## Continued in next specification file...
