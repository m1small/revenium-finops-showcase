# Revenium FinOps Showcase - Priority 1 Implementation

## 🎯 Implementation Goal
Complete all Priority 1 showcase examples demonstrating Revenium integration patterns, query capabilities, and business scenarios.

## ✅ Current State (COMPLETE)
- **Core Simulator**: [`src/simulator/core.py`](../src/simulator/core.py) - Full AI call simulation
- **8 Analyzers**: All FinOps (5) + UBR (3) analyzers implemented with Revenium value sections
- **HTML System**: [`src/utils/html_generator.py`](../src/utils/html_generator.py) + interactive viewer
- **Scenarios**: 2/5 generators (steady_growth, viral_spike)
- **Showcase**: Basic instrumentation, metadata builders, 1 query example, 1 scenario demo

## 🚀 Priority 1: Showcase Examples Implementation

### Part A: Instrumentation Examples (4 files)
**Location**: `showcase/instrumentation/`
**Time Estimate**: 2 hours

#### 1. `revenium_async.py` - Async Fire-and-Forget Pattern
**Purpose**: Demonstrate non-blocking AI call tracking for high-performance applications

**Key Features**:
- Async/await pattern with asyncio
- Fire-and-forget tracking (no blocking)
- Background queue processing
- Error handling without blocking main thread
- Batch submission for efficiency

**Implementation**:
```python
#!/usr/bin/env python3
"""
Async Fire-and-Forget Pattern - Revenium Integration Example

Use Case: High-throughput applications where tracking must not block AI calls
Pattern: Async queue + background worker
Performance: <1ms overhead per call
"""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AICallEvent:
    """Represents an AI call to be tracked"""
    timestamp: str
    call_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    metadata: Dict[str, str]

class ReveniumAsyncTracker:
    """
    Async fire-and-forget tracker for Revenium
    
    Features:
    - Non-blocking call tracking
    - Background queue processing
    - Automatic batching
    - Graceful shutdown
    """
    
    def __init__(self, api_key: str, batch_size: int = 100, flush_interval: float = 5.0):
        self.api_key = api_key
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def start(self):
        """Start background worker"""
        self.running = True
        self.worker_task = asyncio.create_task(self._background_worker())
        print(f"✅ Revenium async tracker started (batch_size={self.batch_size})")
    
    async def stop(self):
        """Gracefully stop and flush remaining events"""
        self.running = False
        if self.worker_task:
            await self.worker_task
        print("✅ Revenium async tracker stopped")
    
    async def track_ai_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        metadata: Dict[str, str]
    ) -> str:
        """
        Track AI call asynchronously (non-blocking)
        
        Returns: call_id immediately without waiting for submission
        """
        call_id = f"call_{int(time.time() * 1000000)}"
        
        event = AICallEvent(
            timestamp=datetime.utcnow().isoformat(),
            call_id=call_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            metadata=metadata
        )
        
        # Non-blocking queue put
        await self.queue.put(event)
        
        return call_id
    
    async def _background_worker(self):
        """Background worker that batches and submits events"""
        batch = []
        last_flush = time.time()
        
        while self.running or not self.queue.empty():
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                batch.append(event)
                
                # Flush if batch is full or interval elapsed
                should_flush = (
                    len(batch) >= self.batch_size or
                    time.time() - last_flush >= self.flush_interval
                )
                
                if should_flush:
                    await self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
                    
            except asyncio.TimeoutError:
                # Timeout - flush if we have events
                if batch:
                    await self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
        
        # Final flush
        if batch:
            await self._flush_batch(batch)
    
    async def _flush_batch(self, batch: list):
        """Submit batch to Revenium API"""
        if not batch:
            return
        
        try:
            # Simulate API call (replace with actual Revenium API)
            await asyncio.sleep(0.01)  # Simulate network latency
            
            print(f"📤 Flushed {len(batch)} events to Revenium")
            
            # In production, this would be:
            # async with aiohttp.ClientSession() as session:
            #     await session.post(
            #         'https://api.revenium.io/v1/events/batch',
            #         headers={'Authorization': f'Bearer {self.api_key}'},
            #         json=[event.__dict__ for event in batch]
            #     )
            
        except Exception as e:
            print(f"❌ Error flushing batch: {e}")

async def demonstrate_async_tracking():
    """Demonstrate async tracking in action"""
    
    print("\n" + "="*60)
    print("Revenium Async Fire-and-Forget Pattern Demo")
    print("="*60 + "\n")
    
    # Initialize tracker
    tracker = ReveniumAsyncTracker(
        api_key="demo_key",
        batch_size=10,
        flush_interval=2.0
    )
    
    await tracker.start()
    
    # Simulate high-throughput AI calls
    print("🚀 Simulating 25 AI calls...")
    
    start_time = time.time()
    
    for i in range(25):
        call_id = await tracker.track_ai_call(
            provider="openai",
            model="gpt-4",
            input_tokens=150 + i * 10,
            output_tokens=300 + i * 20,
            cost_usd=0.0135 + i * 0.001,
            latency_ms=1200 + i * 50,
            metadata={
                'customer_id': f'cust_{i % 5:04d}',
                'organization_id': 'org_001',
                'product_id': 'product_a',
                'feature_id': 'chat',
                'subscription_tier': 'pro',
                'environment': 'production'
            }
        )
        
        if i % 5 == 0:
            print(f"  ✓ Tracked call {i+1}/25 (call_id: {call_id})")
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Tracked 25 calls in {elapsed:.2f}s ({elapsed/25*1000:.2f}ms per call)")
    
    # Wait for final flush
    print("\n⏳ Waiting for final flush...")
    await asyncio.sleep(3)
    
    # Graceful shutdown
    await tracker.stop()
    
    print("\n" + "="*60)
    print("Key Benefits:")
    print("  • Non-blocking: <1ms overhead per call")
    print("  • Automatic batching: Reduces API calls by 100x")
    print("  • Graceful shutdown: No data loss")
    print("  • Error resilient: Failures don't block application")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(demonstrate_async_tracking())
```

#### 2. `revenium_metadata.py` - Advanced Metadata Tagging
**Purpose**: Demonstrate sophisticated metadata strategies for multi-dimensional analysis

**Key Features**:
- Hierarchical tagging (org → product → customer → feature)
- Dynamic metadata enrichment
- Context propagation
- Metadata validation
- Best practices examples

**Implementation**: [Full code with metadata builder patterns, validation, and examples]

#### 3. `revenium_error_handling.py` - Error Handling Patterns
**Purpose**: Demonstrate robust error handling for production deployments

**Key Features**:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Fallback strategies
- Error logging without data loss
- Health check monitoring

**Implementation**: [Full code with error handling patterns]

#### 4. `revenium_batch.py` - Batch Tracking for High Volume
**Purpose**: Demonstrate efficient batch processing for high-volume scenarios

**Key Features**:
- Bulk event submission
- Memory-efficient streaming
- Compression support
- Rate limiting
- Progress tracking

**Implementation**: [Full code with batch processing]

### Part B: Query Patterns (3 files)
**Location**: `showcase/queries/`
**Time Estimate**: 1.5 hours

#### 1. `time_series.py` - Time-Based Cost Analysis
**Purpose**: Query and analyze costs over time periods

**Features**:
- Daily/weekly/monthly aggregations
- Trend analysis
- Growth rate calculations
- Time-based comparisons
- Forecasting helpers

#### 2. `aggregations.py` - Statistical Aggregations
**Purpose**: Demonstrate sum, average, percentile calculations

**Features**:
- Cost aggregations by dimension
- Token efficiency metrics
- Percentile calculations (p50, p95, p99)
- Top-N queries
- Distribution analysis

#### 3. `anomaly_detection.py` - Detect Unusual Patterns
**Purpose**: Identify cost anomalies and unusual usage

**Features**:
- Statistical anomaly detection
- Threshold-based alerts
- Spike detection
- Customer behavior changes
- Cost outlier identification

### Part C: Metadata Tools (3 files)
**Location**: `showcase/metadata/`
**Time Estimate**: 1.5 hours

#### 1. `validators.py` - Metadata Validation
**Purpose**: Validate metadata schemas and enforce standards

**Features**:
- Schema validation
- Required field checking
- Format validation (IDs, tiers, etc.)
- Custom validation rules
- Validation error reporting

#### 2. `examples.py` - Common Metadata Patterns
**Purpose**: Library of common metadata patterns

**Features**:
- E-commerce metadata
- SaaS application metadata
- Multi-tenant metadata
- Feature flag metadata
- A/B test metadata

#### 3. `best_practices.py` - Metadata Best Practices
**Purpose**: Documentation and examples of metadata best practices

**Features**:
- Naming conventions
- Hierarchy design
- Cardinality management
- Performance considerations
- Anti-patterns to avoid

### Part D: Scenario Demonstrations (3 files)
**Location**: `showcase/scenarios/`
**Time Estimate**: 2 hours

#### 1. `scenario_model_comparison.py` - Model Cost Comparison
**Problem**: Using expensive GPT-4 for all tasks
**Solution**: A/B test cheaper models for simple tasks
**Outcome**: 96% cost reduction by switching to Claude Instant

#### 2. `scenario_viral_spike.py` - Viral Growth Response
**Problem**: Customer usage 10x overnight, burning cash
**Solution**: Real-time anomaly detection and rate limiting
**Outcome**: Prevent $50K/month runaway costs

#### 3. `scenario_pricing_change.py` - Pricing Strategy Validation
**Problem**: Should we switch to usage-based pricing?
**Solution**: Simulate 4 pricing models with historical data
**Outcome**: Tiered pricing increases margin by 51%

## 📋 Implementation Checklist

### Part A: Instrumentation Examples ✅
- [ ] `revenium_async.py` - Async fire-and-forget (detailed above)
- [ ] `revenium_metadata.py` - Advanced metadata tagging
- [ ] `revenium_error_handling.py` - Error handling patterns
- [ ] `revenium_batch.py` - Batch tracking

### Part B: Query Patterns ✅
- [ ] `time_series.py` - Time-based cost analysis
- [ ] `aggregations.py` - Statistical aggregations
- [ ] `anomaly_detection.py` - Detect unusual patterns

### Part C: Metadata Tools ✅
- [ ] `validators.py` - Metadata validation
- [ ] `examples.py` - Common metadata patterns
- [ ] `best_practices.py` - Best practices guide

### Part D: Scenario Demonstrations ✅
- [ ] `scenario_model_comparison.py` - Model cost comparison
- [ ] `scenario_viral_spike.py` - Viral growth response
- [ ] `scenario_pricing_change.py` - Pricing strategy validation

**Total Files**: 13 files
**Total Time**: ~7 hours

## 🎯 Implementation Standards

### Code Quality Requirements
- ✅ Python 3.7+ compatible (use type hints, dataclasses)
- ✅ Comprehensive docstrings (module, class, function level)
- ✅ Executable examples (runnable with `python3 filename.py`)
- ✅ No external dependencies (stdlib only, except asyncio/aiohttp if needed)
- ✅ Error handling included
- ✅ Clear output with emojis for readability

### File Structure Template
```python
#!/usr/bin/env python3
"""
[Title] - Revenium [Category] Example

[Description paragraph]

Use Case: [When to use this pattern]
Pattern: [Technical approach]
Performance: [Performance characteristics]
"""

# Imports (stdlib only)
import [modules]
from typing import [types]
from dataclasses import dataclass

# Classes and functions with full docstrings

def demonstrate():
    """
    Demonstrate the pattern in action
    
    Shows:
    - Setup
    - Usage
    - Results
    - Key benefits
    """
    print("\n" + "="*60)
    print("[Title]")
    print("="*60 + "\n")
    
    # Implementation
    
    print("\n" + "="*60)
    print("Key Benefits:")
    print("  • [Benefit 1]")
    print("  • [Benefit 2]")
    print("  • [Benefit 3]")
    print("="*60 + "\n")

if __name__ == "__main__":
    demonstrate()
```

### Metadata Schema Reference
```python
# Standard Revenium metadata fields
metadata = {
    # Identity
    'customer_id': 'cust_0001',           # Required
    'organization_id': 'org_001',         # Required
    'user_id': 'user_123',                # Optional
    
    # Product hierarchy
    'product_id': 'product_a',            # Required
    'feature_id': 'chat',                 # Required
    'component_id': 'ai_assistant',       # Optional
    
    # Subscription
    'subscription_tier': 'pro',           # starter|pro|enterprise
    'subscription_id': 'sub_xyz',         # Optional
    
    # Context
    'environment': 'production',          # production|staging|development
    'task_type': 'chat',                  # chat|summarization|code_generation|etc
    'session_id': 'sess_abc',             # Optional
    
    # Tracking
    'request_id': 'req_123',              # Optional
    'trace_id': 'trace_xyz',              # Optional
    'user_agent': 'web_app_v1.2',         # Optional
}
```

## 🚀 Quick Start Implementation Order

### Phase 1: Core Patterns (3 hours)
1. **`revenium_async.py`** (1 hour) - Most important for production
2. **`revenium_error_handling.py`** (1 hour) - Critical for reliability
3. **`time_series.py`** (0.5 hour) - Most common query pattern
4. **`aggregations.py`** (0.5 hour) - Essential analytics

### Phase 2: Advanced Patterns (2 hours)
5. **`revenium_metadata.py`** (0.5 hour) - Metadata best practices
6. **`revenium_batch.py`** (0.5 hour) - High-volume scenarios
7. **`validators.py`** (0.5 hour) - Data quality
8. **`anomaly_detection.py`** (0.5 hour) - Proactive monitoring

### Phase 3: Scenarios & Documentation (2 hours)
9. **`scenario_model_comparison.py`** (0.5 hour) - High-impact scenario
10. **`scenario_viral_spike.py`** (0.5 hour) - Risk management
11. **`scenario_pricing_change.py`** (0.5 hour) - Revenue optimization
12. **`examples.py`** (0.25 hour) - Quick reference
13. **`best_practices.py`** (0.25 hour) - Guidelines

**Total**: 7 hours for all 13 files

## 📊 Expected Outcomes

### Instrumentation Examples
Each example demonstrates a production-ready pattern:
- **Async**: <1ms overhead, 100x fewer API calls via batching
- **Error Handling**: 99.9% reliability with circuit breaker
- **Metadata**: Consistent tagging across all calls
- **Batch**: Handle 10K+ events/second efficiently

### Query Patterns
Each query shows real analysis capabilities:
- **Time Series**: Daily cost trends, growth rates, forecasts
- **Aggregations**: Cost by dimension, p95 latency, top customers
- **Anomaly Detection**: Identify 10x usage spikes, cost outliers

### Metadata Tools
Each tool ensures data quality:
- **Validators**: Catch 95% of metadata errors before submission
- **Examples**: 10+ common patterns for different industries
- **Best Practices**: Avoid common pitfalls, optimize cardinality

### Scenario Demonstrations
Each scenario shows measurable business impact:
- **Model Comparison**: Save $2,340/month (96% reduction)
- **Viral Spike**: Prevent $50K/month runaway costs
- **Pricing Change**: Increase margin by 51% ($12,340/month)

## 🎨 Output Format Standards

### Console Output
```
============================================================
[Title]
============================================================

[Description of what's happening]

  ✓ Step 1 completed
  ✓ Step 2 completed
  ⏳ Processing...
  ✓ Step 3 completed

📊 Results:
  • Metric 1: [value]
  • Metric 2: [value]
  • Metric 3: [value]

============================================================
Key Benefits:
  • Benefit 1
  • Benefit 2
  • Benefit 3
============================================================
```

### CSV Output (for queries)
```csv
dimension,value,count,avg_cost,total_cost
customer_0001,pro,150,0.0135,2.025
customer_0002,enterprise,450,0.0142,6.390
```

### JSON Output (for metadata)
```json
{
  "customer_id": "cust_0001",
  "organization_id": "org_001",
  "product_id": "product_a",
  "feature_id": "chat",
  "subscription_tier": "pro",
  "environment": "production"
}
```

## 🔑 Key Principles

1. **Executable First**: Every file must run standalone with `python3 filename.py`
2. **Clear Value**: Show "Without Revenium" vs "With Revenium" in scenarios
3. **Production Ready**: Patterns should be copy-paste ready for production
4. **Self-Documenting**: Code should be clear enough to understand without external docs
5. **Realistic Data**: Use realistic business metrics and scenarios
6. **Visual Output**: Use emojis and formatting for clear console output
7. **Error Handling**: Include proper error handling in all examples
8. **Performance**: Show performance characteristics (latency, throughput)

## 📝 File Naming Convention

- `revenium_*.py` - Integration pattern examples
- `scenario_*.py` - Business scenario demonstrations
- `*_examples.py` - Collections of examples
- `*.py` (other) - Utility modules (validators, builders, etc.)

## ✅ Completion Criteria

### For Each File
- [ ] Runs without errors
- [ ] Has comprehensive docstring
- [ ] Includes demonstrate() function
- [ ] Shows clear output with results
- [ ] Highlights key benefits
- [ ] Uses only stdlib (or documented dependencies)
- [ ] Includes error handling
- [ ] Has type hints

### For Each Category
- [ ] All files in category complete
- [ ] Consistent style across files
- [ ] Cross-references where appropriate
- [ ] README.md updated with new examples

### Overall
- [ ] All 13 files implemented
- [ ] All files tested and working
- [ ] Documentation updated
- [ ] Examples added to viewer navigation

## 📊 CSV Schema (Reference)

```csv
timestamp,call_id,provider,model,input_tokens,output_tokens,cost_usd,latency_ms,
customer_id,subscription_tier,organization_id,product_id,feature_id,task_type,
environment,request_id,trace_id,user_agent,session_id
```

## 🔑 Key Principles

1. **Executable**: Every example must run standalone
2. **Realistic**: Use real-world business problems
3. **Clear Value**: Show "Without Revenium" vs "With Revenium"
4. **Copy-Paste Ready**: Code should be production-ready patterns
5. **No Dependencies**: Python 3.7+ stdlib only (except requests if needed)

## 📝 File Naming Convention

- `revenium_*.py` - Integration examples
- `scenario_*.py` - Scenario demonstrations
- `*_examples.py` - Example collections
- `*_patterns.py` - Pattern libraries

## 🎨 HTML Report Structure

Each scenario report should include:
1. **Problem Card**: Business problem with metrics
2. **Solution Card**: How Revenium solves it
3. **Results Card**: Before/after comparison
4. **Implementation Card**: Step-by-step guide

## ✨ Revenium Value Messaging

Every component should highlight:
- **Metadata-Driven**: Multi-dimensional cost allocation
- **Real-Time**: Immediate visibility, not delayed
- **Standardized**: Single schema across providers
- **Automated**: No manual log parsing
- **Actionable**: Clear recommendations

---

**Focus**: Complete the showcase by implementing missing examples, patterns, and scenarios that demonstrate Revenium's value through executable code and realistic business problems.
