# User Workflows & Operations

## Overview

This document describes all user workflows, operational procedures, and usage patterns for the Revenium FinOps Showcase.

## Quick Start Workflow

### 3-Step Quick Start

**Time Required**: ~5 minutes

**Steps**:

#### Step 1: Generate Simulated Data

**Command**:
```bash
cd src
python3 run_all_simulators.py
```

**What This Does**:
- Runs 4 traffic pattern simulators sequentially
- Generates comprehensive dataset with 220+ customers
- Creates 140K+ simulated AI calls
- Outputs to `data/simulated_calls.csv`

**Expected Output**:
```
🚀 RUNNING ALL TRAFFIC PATTERN SIMULATORS
======================================================================

📊 Running: Base Traffic Pattern
----------------------------------------------------------------------
✅ Generated 45,234 calls and saved to data/simulated_calls.csv

📊 Running: Seasonal Pattern
----------------------------------------------------------------------
✅ Appended 32,567 calls to data/simulated_calls.csv

📊 Running: Burst Traffic
----------------------------------------------------------------------
✅ Appended 28,901 calls to data/simulated_calls.csv

📊 Running: Gradual Decline
----------------------------------------------------------------------
   Churned Customers: 8 (20.0%)
✅ Appended 35,424 calls to data/simulated_calls.csv

======================================================================
📊 SIMULATION COMPLETE
======================================================================

📈 Combined Dataset Statistics:
   Total Calls: 142,126
   Unique Customers: 220
   Total Cost: $22,345.67
   Total Tokens: 34,567,890
   Avg Cost/Call: $0.1854
   Date Range: 2025-11-19 to 2025-12-19
```

#### Step 2: Run All Analyzers

**Command**:
```bash
python3 run_all_analyzers.py
```

**What This Does**:
- Executes all 8 analyzers (5 FinOps + 3 UBR)
- Processes CSV data
- Generates HTML reports with charts
- Updates manifest.json

**Expected Output**:
```
======================================================================
🚀 REVENIUM FINOPS SHOWCASE - RUNNING ALL ANALYZERS
======================================================================

✅ Found existing data: data/simulated_calls.csv
📊 Data contains 142,126 calls

📊 Running: FinOps: Understanding Usage & Cost
----------------------------------------------------------------------
   Processing 142,126 calls...
   Analyzed: 3 providers, 7 models, 220 customers
✅ Generated HTML report: reports/html/finops_understanding.html

📊 Running: FinOps: Performance Tracking
----------------------------------------------------------------------
   Calculating latency percentiles...
   Analyzing model efficiency...
✅ Generated HTML report: reports/html/finops_performance.html

... (continues for all 8 analyzers)

======================================================================
📊 ANALYSIS COMPLETE
======================================================================

⏱️  Total time: 4.56 seconds
✅ Successful: 8
❌ Failed: 0
📁 Reports saved to: reports/html/
```

#### Step 3: View Reports

**Command**:
```bash
cd ../viewer
python3 serve.py
```

**What This Does**:
- Checks data freshness
- Auto-runs analyzers if data changed
- Starts HTTP server on port 8000
- Serves interactive report viewer

**Expected Output**:
```
======================================================================
🌐 REVENIUM FINOPS SHOWCASE - REPORT VIEWER
======================================================================

📊 Checking data freshness...
✅ Reports are up to date

🚀 Starting server on port 8000...

📊 Open your browser to: http://localhost:8000

Press Ctrl+C to stop the server
======================================================================
```

**Browser**:
1. Open `http://localhost:8000`
2. See modern animated landing page
3. Browse reports by category (FinOps vs UBR)
4. Click report cards to view detailed analysis

---

## Alternative Workflows

### Workflow: Single Traffic Pattern

**Use Case**: Quick testing, specific pattern demonstration

**Steps**:
```bash
cd src
python3 simulator/core.py           # Base pattern only
python3 run_all_analyzers.py
cd ../viewer && python3 serve.py
```

**Time**: ~2 minutes

**Output**: ~45K calls, 100 customers

### Workflow: Individual Analyzer

**Use Case**: Focus on specific analysis

**Steps**:
```bash
cd src
python3 simulator/core.py           # Generate data
python3 analyzers/ubr/profitability.py  # Run specific analyzer
```

**Output**: Single HTML report

**View Directly**:
```bash
open reports/html/customer_profitability.html
```

### Workflow: Custom Simulation

**Use Case**: Testing with specific parameters

**Steps**:

1. **Modify simulator parameters**:
```python
# Edit simulator/core.py
simulator = AICallSimulator(
    num_customers=200,  # More customers
    num_days=60,        # Longer period
    seed=42             # Reproducible
)
```

2. **Run simulation**:
```bash
python3 simulator/core.py
```

3. **Analyze**:
```bash
python3 run_all_analyzers.py
```

### Workflow: Explore Specific Traffic Patterns

**Use Case**: Understand individual traffic behaviors

**Steps**:
```bash
cd src

# Seasonal patterns
python3 simulator/scenarios/seasonal_pattern.py

# Burst traffic
python3 simulator/scenarios/burst_traffic.py

# Gradual decline
python3 simulator/scenarios/gradual_decline.py
```

**Note**: These append to existing CSV, so clear data first if needed:
```bash
rm data/simulated_calls.csv
```

---

## Integration Workflows

### Workflow: Run Integration Examples

**Use Case**: Learn Revenium SDK usage

**Steps**:
```bash
cd showcase/instrumentation
python3 revenium_basic.py

cd ../metadata
python3 builders.py

cd ../queries
python3 cost_allocation.py

cd ../scenarios
python3 scenario_unprofitable_customers.py
```

**Output**: Console demonstrations of integration patterns

### Workflow: Test Metadata Builders

**Use Case**: Experiment with metadata construction

**Steps**:
```python
from showcase.metadata.builders import ReveniumMetadataBuilder

# Build metadata interactively
metadata = (ReveniumMetadataBuilder()
    .customer('cust_test')
    .feature('my_feature')
    .environment('staging')
    .build())

print(metadata)
```

---

## Operational Workflows

### Workflow: Daily Report Generation

**Use Case**: Regular reporting cadence

**Schedule**: Daily cron job

**Script**:
```bash
#!/bin/bash
# daily_reports.sh

cd /path/to/revenium-flow/src

# Generate fresh data
python3 run_all_simulators.py > /tmp/sim.log 2>&1

# Run analyzers
python3 run_all_analyzers.py > /tmp/analyze.log 2>&1

# Archive reports
timestamp=$(date +%Y%m%d)
cp -r reports/html/ /archives/reports_${timestamp}/

echo "Reports generated: $(date)" >> /var/log/revenium_reports.log
```

**Crontab**:
```cron
0 2 * * * /path/to/daily_reports.sh
```

### Workflow: Continuous Monitoring

**Use Case**: Real-time data processing and reporting

**Implementation**:
```bash
#!/bin/bash
# watch_and_process.sh

while true; do
    # Check if new data exists
    if [ data/simulated_calls.csv -nt reports/html/manifest.json ]; then
        echo "New data detected, running analyzers..."
        python3 run_all_analyzers.py
    fi

    sleep 300  # Check every 5 minutes
done
```

### Workflow: Report Distribution

**Use Case**: Share reports with stakeholders

**Email Distribution**:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_report_email(recipients, report_path):
    """Send HTML report via email"""
    msg = MIMEMultipart()
    msg['From'] = 'reports@revenium.io'
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = f'Revenium FinOps Report - {date.today()}'

    # Attach HTML report
    with open(report_path, 'r') as f:
        html_content = f.read()

    msg.attach(MIMEText(html_content, 'html'))

    # Send
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)

# Usage
send_report_email(
    ['finance@company.com', 'cto@company.com'],
    'reports/html/customer_profitability.html'
)
```

### Workflow: Data Export

**Use Case**: Export data for external analysis

**CSV Export** (already in CSV):
```bash
# Copy to shared location
cp data/simulated_calls.csv /shared/ai_usage_$(date +%Y%m%d).csv
```

**JSON Export**:
```python
import csv
import json

def csv_to_json(csv_file, json_file):
    """Convert CSV to JSON"""
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

csv_to_json('data/simulated_calls.csv', 'export/data.json')
```

**Excel Export**:
```python
import csv

def csv_to_excel(csv_file, excel_file):
    """Convert CSV to Excel-friendly format"""
    # CSV can be opened directly in Excel
    # Or use openpyxl for advanced formatting
    pass
```

---

## Troubleshooting Workflows

### Workflow: Port 8000 Already in Use

**Problem**: `Address already in use` error

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
# Edit viewer/serve.py and change PORT = 8001
```

### Workflow: No Data Found

**Problem**: Analyzers can't find CSV file

**Solution**:
```bash
# Check if data exists
ls -lh src/data/simulated_calls.csv

# If missing, generate data
cd src
python3 simulator/core.py

# Verify data generated
wc -l data/simulated_calls.csv
```

### Workflow: Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Ensure running from correct directory
pwd  # Should be in src/ for most commands

# For simulators
cd src
python3 simulator/core.py

# For analyzers
cd src
python3 run_all_analyzers.py

# For viewer
cd viewer
python3 serve.py
```

### Workflow: Charts Not Rendering

**Problem**: HTML reports show blank charts

**Solution**:
1. Check internet connection (Chart.js loads from CDN)
2. Check browser console for errors
3. Try different browser (Chrome, Firefox)
4. Verify JavaScript is enabled

**Offline Workaround**:
Download Chart.js locally:
```bash
cd viewer
curl -o chart.js https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js

# Update html_generator.py to use local file
```

### Workflow: Memory Issues

**Problem**: Python process using too much memory

**Solution**:
```bash
# Reduce dataset size
# Edit simulator parameters:
simulator = AICallSimulator(
    num_customers=50,  # Reduce from 100
    num_days=15        # Reduce from 30
)

# Or process in chunks
def process_csv_in_chunks(csv_file, chunk_size=10000):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                process_chunk(chunk)
                chunk = []
        if chunk:
            process_chunk(chunk)
```

---

## Advanced Workflows

### Workflow: A/B Testing Scenarios

**Use Case**: Compare different simulation parameters

**Steps**:
```bash
# Scenario A: Current pricing
python3 simulator/core.py
cp data/simulated_calls.csv data/scenario_a.csv

# Scenario B: Adjusted pricing
# Edit SUBSCRIPTION_TIERS in simulator/core.py
python3 simulator/core.py
cp data/simulated_calls.csv data/scenario_b.csv

# Compare results
python3 compare_scenarios.py scenario_a.csv scenario_b.csv
```

### Workflow: Batch Processing Multiple Datasets

**Use Case**: Process historical data files

**Script**:
```bash
#!/bin/bash
# batch_process.sh

for file in data/historical/*.csv; do
    echo "Processing $file..."

    # Copy to working location
    cp "$file" data/simulated_calls.csv

    # Run analyzers
    python3 run_all_analyzers.py

    # Archive results
    basename=$(basename "$file" .csv)
    mkdir -p "archives/$basename"
    cp -r reports/html/* "archives/$basename/"

    echo "Completed $file"
done
```

### Workflow: Automated Testing

**Use Case**: CI/CD integration

**GitHub Actions**:
```yaml
name: Generate and Test Reports

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Generate data
      run: |
        cd src
        python3 simulator/core.py

    - name: Run analyzers
      run: |
        cd src
        python3 run_all_analyzers.py

    - name: Verify reports
      run: |
        test -f src/reports/html/finops_understanding.html
        test -f src/reports/html/customer_profitability.html

    - name: Archive reports
      uses: actions/upload-artifact@v2
      with:
        name: reports
        path: src/reports/html/
```

---

## Performance Optimization Workflows

### Workflow: Profile Performance

**Use Case**: Identify bottlenecks

**Steps**:
```bash
# Profile simulator
python3 -m cProfile -o sim.prof simulator/core.py

# Analyze profile
python3 -m pstats sim.prof
# In pstats shell:
# > sort cumulative
# > stats 20

# Profile analyzer
python3 -m cProfile -o analyze.prof run_all_analyzers.py
```

### Workflow: Optimize for Large Datasets

**Use Case**: Handle 1M+ calls

**Techniques**:

1. **Stream Processing**:
```python
def stream_process_csv(csv_file):
    """Process CSV without loading all into memory"""
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Process row immediately
            yield process_row(row)
```

2. **Parallel Processing**:
```python
from multiprocessing import Pool

def process_chunk(chunk):
    """Process chunk of data"""
    return analyze_chunk(chunk)

# Split data into chunks
chunks = split_data_into_chunks(data, num_chunks=8)

# Process in parallel
with Pool(8) as pool:
    results = pool.map(process_chunk, chunks)

# Combine results
final_result = combine_results(results)
```

---

## Deployment Workflows

### Workflow: Deploy to Production

**Use Case**: Production deployment

**Steps**:

1. **Containerize**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY src/ ./src/
COPY viewer/ ./viewer/
COPY showcase/ ./showcase/

EXPOSE 8000

CMD ["python3", "viewer/serve.py"]
```

2. **Build**:
```bash
docker build -t revenium-showcase .
```

3. **Run**:
```bash
docker run -p 8000:8000 revenium-showcase
```

4. **Deploy to Cloud**:
```bash
# AWS ECR
docker tag revenium-showcase:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/revenium-showcase:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/revenium-showcase:latest

# Deploy to ECS/Fargate
aws ecs update-service --cluster showcase --service revenium --force-new-deployment
```

### Workflow: Health Checks

**Use Case**: Monitoring deployment health

**Endpoint**:
```python
# Add to viewer/serve.py

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Check if data exists
            if os.path.exists('src/data/simulated_calls.csv'):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b'No data')
```

**Monitoring**:
```bash
# Check health
curl http://localhost:8000/health

# Automated monitoring
while true; do
    if ! curl -f http://localhost:8000/health; then
        echo "Health check failed!" | mail -s "Alert" admin@company.com
    fi
    sleep 60
done
```

---

## Documentation Workflows

### Workflow: Generate Documentation

**Use Case**: Update documentation

**Steps**:
```bash
# Generate API docs from docstrings
python3 -m pydoc -w simulator.core
python3 -m pydoc -w analyzers.finops.understanding

# Convert to HTML
for file in src/**/*.py; do
    python3 -m pydoc -w "$file"
done
```

### Workflow: Update Specs

**Use Case**: Keep specs in sync with code

**Process**:
1. Code changes committed
2. Update relevant spec file (this document, etc.)
3. Update main README if needed
4. Commit spec changes with code

---

## Related Specifications

- **Architecture**: See `architecture.md`
- **Data Schema**: See `data-schema.md`
- **Simulators**: See `simulators.md`
- **Analyzers**: See `analyzers.md`
- **Reports**: See `reports.md`
- **Integration**: See `integration.md`
- **Requirements**: See `requirements.md`
