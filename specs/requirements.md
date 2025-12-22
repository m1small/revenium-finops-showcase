# Technical Requirements & Constraints

## Overview

This document specifies all technical requirements, dependencies, constraints, and recommendations for the Revenium FinOps Showcase.

## System Requirements

### Python Version

**Required**: Python 3.7+

**Recommended**: Python 3.11+

**Rationale**:
- Python 3.7+: Minimum for dataclasses, type hints
- Python 3.11+: Performance improvements, better error messages

**Verification**:
```bash
python3 --version
# Should output: Python 3.11.x or higher
```

### Operating System

**Supported**:
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- Windows 10+ (with Python installed)

**Recommended**: macOS or Linux for best compatibility

### Hardware Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 2 GB
- Disk: 500 MB free space

**Recommended**:
- CPU: 4+ cores
- RAM: 8 GB
- Disk: 2 GB free space

**Rationale**:
- Simulation generates 140K+ records in memory
- CSV processing requires proportional memory
- Multiple analyzers run sequentially

### Disk Space Breakdown

```
revenium-flow/
├── Source code: ~50 MB
├── Simulated data (CSV): ~30-50 MB
├── HTML reports: ~1-2 MB
├── Python cache: ~10 MB
└── Total: ~100 MB
```

**Growth**: ~2 MB per 1000 additional calls

## Dependencies

### Python Standard Library Only

**Core Philosophy**: Zero external dependencies for core functionality

**Used Modules**:
- `csv` - CSV file reading/writing
- `datetime` - Date/time handling
- `collections` - defaultdict, Counter
- `dataclasses` - Data structures
- `typing` - Type hints
- `http.server` - Web server
- `json` - JSON parsing/generation
- `random` - Random number generation
- `uuid` - Unique ID generation
- `time` - Timing functions
- `os` - File system operations
- `sys` - System operations

**No pip install required!**

### External Resources (CDN)

**Chart.js**:
- **Version**: 4.4.1
- **Source**: https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js
- **License**: MIT
- **Purpose**: Interactive chart generation
- **Required**: Internet connection for initial load (then cached)

**Alternative (Offline)**:
```bash
# Download Chart.js locally
cd viewer
curl -o chart.js https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js

# Update html_generator.py to reference local file
```

## Browser Requirements

### Supported Browsers

**Modern Browsers Required**:
- **Chrome**: 90+ (Recommended)
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

**Not Supported**:
- Internet Explorer (any version)
- Legacy browsers without ES6 support

### Required Browser Features

**JavaScript**:
- ES6+ (arrow functions, const/let, template literals)
- Canvas API (for Chart.js)
- Fetch API (future feature)

**CSS**:
- Flexbox
- CSS Grid
- CSS Variables
- CSS Animations
- CSS Transforms

**HTML5**:
- Semantic elements
- Local storage (viewer preferences)

### JavaScript Requirements

**Must Be Enabled**: Yes

**Why**: Chart.js requires JavaScript for interactive visualizations

**Fallback**: Static HTML tables still visible without JavaScript

## Network Requirements

### For Development/Demo

**Internet Required**: Yes (for Chart.js CDN)

**Bandwidth**: Minimal
- Chart.js: ~200 KB (one-time download, then cached)
- No other external resources

**Ports**:
- **8000**: HTTP server (viewer)
- Can be changed in `viewer/serve.py`

### For Production Deployment

**Options**:
1. **With Internet**: Use CDN (faster, always latest)
2. **Offline**: Bundle Chart.js locally

**Firewall Rules**:
- Allow outbound HTTPS to cdn.jsdelivr.net (if using CDN)
- Allow inbound HTTP on port 8000 (or custom port)

## File System Requirements

### Permissions

**Read Permission Required**:
- All source files (`src/`, `viewer/`, `showcase/`)
- Data files (`src/data/*.csv`)
- Report files (`src/reports/html/*.html`)

**Write Permission Required**:
- `src/data/` - For CSV generation
- `src/reports/` - For report generation
- `src/reports/html/` - For HTML reports

**Execution Permission Required**:
- All `.py` files

### File System Type

**Compatible**:
- ext4, NTFS, APFS, HFS+, ZFS

**Not Recommended**:
- Network file systems (NFS, SMB) - slower performance
- FAT32 - file size limitations

### Case Sensitivity

**Recommendation**: Case-sensitive file system

**Why**: Python imports are case-sensitive

## Performance Requirements

### Simulation Performance

**Target**:
- Generate 100K calls in <30 seconds
- Process on commodity hardware

**Actual** (on M1 Mac):
- 142K calls in ~10 seconds
- ~14,000 calls/second

**Bottlenecks**:
- Random number generation
- CSV writing
- Token calculation

### Analysis Performance

**Target**:
- Process 100K calls in <10 seconds per analyzer
- All 8 analyzers in <60 seconds

**Actual** (on M1 Mac):
- 142K calls in ~4.5 seconds total
- ~18 seconds for full analysis suite

**Bottlenecks**:
- CSV parsing
- Dictionary aggregations
- HTML generation

### Viewer Performance

**Target**:
- Page load <1 second
- Chart rendering <500ms

**Actual**:
- Initial load: ~300ms
- Chart rendering: ~200ms per chart
- Navigation: <50ms

## Scalability Limits

### Current Architecture

**Optimal Range**:
- Customers: 100-500
- Days: 7-90
- Total calls: 10K-500K

**Maximum Tested**:
- Customers: 1000
- Days: 180
- Total calls: 1M+

**Performance Degradation**:
- >500K calls: Noticeably slower analysis
- >1M calls: Significant memory usage (>4GB)

### Scaling Strategies

**For >1M calls**:

1. **Stream Processing**:
```python
def stream_csv():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row
```

2. **Chunked Processing**:
```python
def process_in_chunks(csv_file, chunk_size=100000):
    chunk = []
    for row in stream_csv():
        chunk.append(row)
        if len(chunk) >= chunk_size:
            process_chunk(chunk)
            chunk = []
```

3. **Database Backend**:
- SQLite for local
- PostgreSQL for production
- Partitioned tables for large datasets

## Security Requirements

### Current Security Posture

**Demo/Showcase System**:
- No authentication required
- No sensitive data (all simulated)
- Local-only by default (localhost:8000)
- Read-only data access

**Not Production-Ready For**:
- Public internet exposure
- Real customer data
- Multi-tenant environments

### Production Security Recommendations

**Authentication**:
```python
# Add basic auth to viewer
from http.server import BaseHTTPRequestHandler
import base64

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get('Authorization')
        if not self.check_auth(auth_header):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Reports"')
            self.end_headers()
            return

        # Serve content
        super().do_GET()

    def check_auth(self, auth_header):
        if not auth_header:
            return False

        auth_decoded = base64.b64decode(auth_header.split()[1]).decode()
        username, password = auth_decoded.split(':')
        return username == 'admin' and password == 'secure_password'
```

**HTTPS**:
```bash
# Use reverse proxy (nginx, Caddy)
server {
    listen 443 ssl;
    server_name reports.company.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

**Input Validation**:
```python
def validate_csv_row(row):
    """Validate CSV data before processing"""
    required_fields = ['timestamp', 'cost_usd', 'customer_id']

    for field in required_fields:
        if field not in row or not row[field]:
            raise ValueError(f"Missing required field: {field}")

    # Type validation
    try:
        float(row['cost_usd'])
        int(row['input_tokens'])
        int(row['output_tokens'])
    except ValueError as e:
        raise ValueError(f"Invalid numeric field: {e}")

    return True
```

**Rate Limiting**:
```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def allow_request(self, client_ip):
        now = time.time()
        # Clean old requests
        self.requests[client_ip] = [
            req for req in self.requests[client_ip]
            if now - req < self.window
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        self.requests[client_ip].append(now)
        return True
```

## Data Requirements

### Data Format

**Primary Format**: CSV (UTF-8)

**Alternative Formats** (future):
- JSON (for API integration)
- Parquet (for large datasets)
- PostgreSQL (for production)

### Data Quality

**Required Quality**:
- No missing fields (all 19 fields present)
- Valid data types
- No duplicate call_ids
- Timestamps in ISO 8601 format
- Costs non-negative

**Validation**:
```python
def validate_dataset(csv_file):
    """Validate entire dataset"""
    seen_ids = set()
    errors = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            # Check for duplicates
            if row['call_id'] in seen_ids:
                errors.append(f"Line {i}: Duplicate call_id {row['call_id']}")

            seen_ids.add(row['call_id'])

            # Validate row
            try:
                validate_csv_row(row)
            except ValueError as e:
                errors.append(f"Line {i}: {e}")

    return errors
```

### Data Retention

**Simulated Data**: No retention requirements

**Production Data**: Recommend 13+ months for year-over-year analysis

## Compatibility Matrix

### Python Versions

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.7 | Supported | Minimum version |
| 3.8 | Supported | |
| 3.9 | Supported | |
| 3.10 | Supported | |
| 3.11 | Recommended | Best performance |
| 3.12 | Supported | Latest stable |
| 3.13+ | Untested | Should work |

### Operating Systems

| OS | Status | Notes |
|-----|--------|-------|
| macOS 10.15+ | Fully Supported | Primary dev platform |
| Ubuntu 20.04+ | Fully Supported | Recommended for production |
| Debian 11+ | Supported | |
| RHEL 8+ | Supported | |
| Windows 10+ | Supported | May need path adjustments |
| Windows WSL | Recommended | Better than native Windows |

### Browsers

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | Fully Supported |
| Firefox | 88+ | Fully Supported |
| Safari | 14+ | Supported |
| Edge | 90+ | Supported |
| IE 11 | N/A | Not Supported |

## Development Requirements

### For Contributors

**Tools Required**:
- Git
- Python 3.11+
- Text editor or IDE (VS Code, PyCharm)

**Recommended**:
- VS Code with Python extension
- Black (code formatter)
- Pylint (linter)
- MyPy (type checker)

**Setup**:
```bash
# Clone repo
git clone https://github.com/company/revenium-flow.git
cd revenium-flow

# No pip install needed!

# Run tests
cd src
python3 simulator/core.py
python3 run_all_analyzers.py
```

### Code Style

**Standard**: PEP 8

**Type Hints**: Required for all functions

**Docstrings**: Required for all classes and public methods

**Example**:
```python
def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_rate: float,
    output_rate: float
) -> float:
    """
    Calculate cost of AI call

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        input_rate: Cost per 1K input tokens
        output_rate: Cost per 1K output tokens

    Returns:
        Total cost in USD
    """
    return (input_tokens * input_rate / 1000) + \
           (output_tokens * output_rate / 1000)
```

## Testing Requirements

### Unit Tests (Future)

**Framework**: pytest

**Coverage Target**: 80%+

**Example**:
```python
def test_calculate_cost():
    cost = calculate_cost(1000, 1000, 0.03, 0.06)
    assert cost == 0.09
```

### Integration Tests (Future)

**Scenarios**:
- Full simulation → analysis → report generation
- Individual analyzers
- Report viewer

### Performance Tests (Future)

**Benchmarks**:
- Simulation: <1 second per 10K calls
- Analysis: <5 seconds per 100K calls
- Report generation: <1 second per report

## Deployment Requirements

### Containerization

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy source
COPY src/ ./src/
COPY viewer/ ./viewer/
COPY showcase/ ./showcase/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run viewer
CMD ["python3", "viewer/serve.py"]
```

**Build**:
```bash
docker build -t revenium-showcase:latest .
```

**Run**:
```bash
docker run -p 8000:8000 revenium-showcase:latest
```

### Cloud Deployment

**AWS**:
- ECS/Fargate (recommended)
- EC2 (simple)
- Lambda (for API-based)

**GCP**:
- Cloud Run (recommended)
- Compute Engine
- Cloud Functions

**Azure**:
- Container Instances
- App Service
- Functions

## Monitoring Requirements

### Metrics to Track

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

**Application Metrics**:
- Simulation runtime
- Analysis runtime
- Report generation time
- CSV size
- Report count

**User Metrics** (production):
- Page views
- Report views
- Average session duration

### Logging

**Log Levels**:
- INFO: Normal operations
- WARNING: Unusual but handled
- ERROR: Failures requiring attention
- DEBUG: Detailed troubleshooting

**Log Format**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Starting simulation...")
```

## Documentation Requirements

### User Documentation

**Required**:
- README.md (overview)
- QUICKSTART.md (3-step guide)
- specs/ (detailed specifications)

**Recommended**:
- CONTRIBUTING.md
- CHANGELOG.md
- FAQ.md

### Code Documentation

**Required**:
- Docstrings for all classes
- Docstrings for all public methods
- Type hints throughout

**Recommended**:
- Inline comments for complex logic
- Architecture diagrams
- API documentation

## Licensing Requirements

**Project License**: Not specified (internal/demo)

**Dependencies**:
- Python: PSF License (permissive)
- Chart.js: MIT License (permissive)

**Recommendations**:
- Add LICENSE file
- Specify usage terms
- Credit Chart.js in documentation

## Related Specifications

- **Architecture**: See `architecture.md`
- **Workflows**: See `workflows.md` for operational procedures
- **Data Schema**: See `data-schema.md` for data requirements
