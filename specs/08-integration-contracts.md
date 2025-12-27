# Integration Contracts Specification

## Analyzer-Generator Contract

### Analyzer Interface

All analyzers must implement:

```
interface Analyzer:
    method __init__(csv_path: String):
        # Initialize with path to CSV data file
        # Load data into memory
        # Prepare for analysis

    method analyze() -> Dictionary:
        # Perform all analysis
        # Return structured dictionary with results
        # Dictionary must include:
        #   - summary: Dictionary of key metrics
        #   - recommendations: List of strings
        #   - domain-specific sections: varies by analyzer
```

### Analyzer Output Contract

Required fields in all analyzer outputs:

```
{
    "summary": {
        # Minimum required metrics
        "total_calls": Integer,
        "total_cost": Float,
        # Analyzer-specific metrics
        ...
    },
    "recommendations": [
        String,  # Actionable recommendation 1
        String,  # Actionable recommendation 2
        ...
    ],
    # Domain-specific sections
    ...
}
```

### Generator Interface

All generators must implement:

```
function generate_report(data: Dictionary, output_path: String):
    # data: Output from analyzer.analyze()
    # output_path: Where to write HTML file
    # Returns: None (writes to file)
    # Side effects: Creates HTML file at output_path
```

### Generator Input Contract

Generator must handle:
- data dictionary with required sections
- graceful handling of missing optional sections
- validation of required fields
- default values for missing metrics

### Example Contract

```
# Analyzer produces
data = {
    "summary": {
        "total_calls": 50000,
        "total_cost": 1234.56,
        "avg_cost_per_call": 0.024691
    },
    "by_provider": [
        {"provider": "openai", "cost": 500.00, "calls": 20000},
        {"provider": "anthropic", "cost": 734.56, "calls": 30000}
    ],
    "recommendations": [
        "Consider migrating high-volume simple tasks to GPT-3.5",
        "Implement caching to reduce redundant API calls"
    ]
}

# Generator consumes
generate_understanding_report(data, "reports/html/understanding.html")
```

## Simulator-Storage Contract

### CSV Format Contract

Header row (required, exact field names):

```
timestamp,organization_id,product_id,feature_id,customer_id,customer_archetype,subscription_tier,tier_price_usd,provider,model,region,input_tokens,output_tokens,total_tokens,latency_ms,cost_usd,status,error_type,metadata
```

### Field Contracts

```
timestamp:
    Format: ISO 8601 (YYYY-MM-DDTHH:MM:SS.ffffff)
    Example: "2024-01-15T14:23:45.123456"
    Constraint: Must be parseable by datetime parser

organization_id:
    Format: "org-{UUID}"
    Example: "org-a1b2c3d4-e5f6-7890-abcd-ef1234567890"

customer_id:
    Format: "cust-{UUID}"
    Example: "cust-12345678-1234-1234-1234-123456789012"

tier_price_usd:
    Type: Float
    Values: 49.0, 199.0, or 999.0
    Must match subscription_tier

total_tokens:
    Type: Integer
    Constraint: Must equal input_tokens + output_tokens

cost_usd:
    Type: Float
    Constraint: Must be >= 0
    Precision: 6 decimal places

status:
    Type: String
    Values: "success" or "error"
    Constraint: If "error", error_type must be set

error_type:
    Type: String
    Values: "timeout", "rate_limit", "auth_error", "server_error", or empty
    Constraint: Required if status == "error"
```

### Append-Only Contract

```
# Simulator guarantees:
- New records always appended to end
- No modifications to existing records
- Header row written only if file empty
- Atomic writes per batch
- No concurrent writes from multiple simulators
```

## Configuration Contract

### Config Module Interface

```
# All configuration accessed through central module
import config

# Required constants
config.TARGET_SIZE_MB: Float
config.DATA_CSV_PATH: String
config.REPORT_DIR: String
config.VIEWER_PORT: Integer

# Threshold constants
config.SLA_THRESHOLD_MS: Float
config.HIGH_MARGIN_THRESHOLD_PCT: Float
config.ANOMALY_MULTIPLIER: Float

# Distribution constants
config.PROVIDER_WEIGHTS: Dictionary
config.SUBSCRIPTION_TIERS: Dictionary
config.CUSTOMER_ARCHETYPES: Dictionary
```

### Config Modification Contract

```
# Configuration is read-only at runtime
# Changes require:
1. Edit config.py source file
2. Restart all processes
3. Regenerate data if distributions changed
```

## Common Utilities Contract

### Group-By Function

```
function group_by(calls: List[Dictionary], *keys: String) -> Dictionary:
    # Input: List of call dictionaries, variable number of grouping keys
    # Output: Dictionary mapping tuple of key values to list of calls
    # Example:
    #   group_by(calls, "provider")
    #   Returns: {("openai",): [...], ("anthropic",): [...]}
    #
    #   group_by(calls, "provider", "model")
    #   Returns: {("openai", "gpt-4"): [...], ("openai", "gpt-3.5"): [...]}
```

### Aggregate Metrics Function

```
function aggregate_metrics(calls: List[Dictionary]) -> Dictionary:
    # Input: List of call dictionaries
    # Output: Dictionary with standard metrics:
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
    # Guarantees: All values non-null, safe for zero-length input
```

### Safe Division Function

```
function safe_divide(numerator: Float, denominator: Float, default: Float = 0) -> Float:
    # Contract: Never raises division by zero
    # Returns default if denominator == 0
    # Otherwise returns numerator / denominator
```

## Orchestration Contracts

### Simulator Orchestration

```
# run_all_simulators.py contract
function main(target_size_mb: Float = TARGET_SIZE_MB):
    # Guarantees:
    - Creates data directory if not exists
    - Writes CSV header if file new
    - Cycles through scenarios until target reached
    - Progress updates every scenario
    - Stops automatically when target_size_mb reached
    - Returns exit code 0 on success
```

### Analyzer Orchestration

```
# run_all_analyzers.py contract
function main():
    # Pre-conditions:
    - CSV file must exist
    - CSV must have data

    # Guarantees:
    - Runs all 13 analyzers in sequence
    - Generates HTML for each analyzer
    - Creates index.html listing all reports
    - Creates manifest.json with status
    - Prints progress for each analyzer
    - Continues on individual analyzer failures
    - Returns exit code 0 if any reports generated

    # Post-conditions:
    - report_dir contains HTML files
    - index.html created
    - manifest.json created
```

### Individual Analyzer Execution

```
# run_analyzer.py contract
function run_analyzer(analyzer_id: String, csv_path: String, report_dir: String) -> Dictionary:
    # Pre-conditions:
    - analyzer_id must be in ANALYZER_REGISTRY
    - csv_path file must exist

    # Returns:
    {
        "success": Boolean,
        "analyzer_id": String,
        "name": String,
        "filename": String,
        "output_path": String,  # If success
        "size_kb": Float,       # If success
        "generated_at": String, # If success
        "error": String,        # If not success
        "traceback": String     # If not success
    }

    # Guarantees:
    - Always returns dictionary
    - Never raises exceptions
    - Writes HTML file on success
    - Prints error details on failure
```

## Web Server Contracts

### Status API Contract

```
# GET /api/status
# Returns:
{
    "timestamp": String,  # ISO 8601
    "csv": {
        "size_mb": Float,
        "target_mb": Float,
        "progress_pct": Float,  # 0-100
        "line_count": Integer,
        "complete": Boolean
    },
    "reports": {
        "understanding.html": {
            "name": String,
            "exists": Boolean,
            "size_kb": Float
        },
        # ... 12 more reports
    },
    "analyzer_status": {
        "analyzer_id": {
            "status": String,  # "running", "complete", "error", "timeout"
            "started_at": String,    # If running
            "completed_at": String,  # If complete/error/timeout
            "success": Boolean,      # If complete
            "error": String          # If error
        }
    }
}

# Guarantees:
- Always returns 200 OK
- JSON always well-formed
- All fields always present
- Updates every 10 seconds server-side
```

### Run Analyzer API Contract

```
# POST /api/run-analyzer?id={analyzer_id}
# Returns:
{
    "success": Boolean,
    "message": String,  # If success
    "error": String     # If not success
}

# Guarantees:
- Validates analyzer_id
- Returns immediately (non-blocking)
- Analyzer runs in background
- Status available via /api/status
- Maximum 5-minute timeout per analyzer
- Thread-safe status updates
```

## Error Handling Contracts

### Analyzer Errors

```
# All analyzers must handle:
- Empty CSV file: Return empty metrics, no crash
- Missing fields: Skip invalid records, continue
- Malformed data: Log error, skip record
- Division by zero: Use safe_divide utility
- File I/O errors: Propagate to caller

# Analyzers must NOT:
- Modify CSV file
- Write to arbitrary paths
- Make network requests
- Execute system commands
```

### Generator Errors

```
# All generators must handle:
- Missing optional data sections: Use defaults
- Invalid data types: Coerce or skip
- File write failures: Propagate exception
- Template errors: Propagate exception

# Generators must NOT:
- Modify input data dictionary
- Make network requests (except Chart.js CDN in output)
- Execute system commands
```

### Server Errors

```
# Server must handle:
- Missing CSV file: Report 0 size
- Missing reports: Report as not available
- Analyzer failures: Return error in status
- Network errors: Log and continue
- Concurrent requests: Thread-safe handling

# Server must NOT:
- Crash on client disconnect
- Expose internal paths in errors
- Execute arbitrary commands
- Allow directory traversal
```

## Versioning Contract

### Data Format Versioning

```
# CSV format version: 1.0
# Changes require:
- Version increment
- Migration script for existing data
- Backward compatibility layer in analyzers
```

### API Versioning

```
# Status API version: 1.0
# Breaking changes require:
- Version increment in URL (/api/v2/status)
- Maintain previous version for compatibility
- Document migration path
```

### Configuration Versioning

```
# Config version: 1.0
# Breaking changes require:
- Rename old config to config_v1.py
- Create new config.py
- Update all imports
- Document changes
```
