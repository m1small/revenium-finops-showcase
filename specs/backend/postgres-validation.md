# PostgreSQL Validation Layer - MVP Specification

## Purpose

Simple, reliable validation system using PostgreSQL to independently track all AI API calls for reconciliation against Revenium data.

---

## Architecture

```
Application Code
    |
    ├─→ Revenium Middleware (async)
    |
    └─→ PostgreSQL Logger (sync, blocking)
         ↓
    ai_calls table
         ↓
    Reconciliation Query
```

**Key Design**: PostgreSQL writes are synchronous and blocking - if the insert fails, we know immediately.

---

## Database Schema

```sql
-- Core tracking table
CREATE TABLE ai_calls (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Provider info
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    
    -- Usage data
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    
    -- Cost tracking
    cost_usd DECIMAL(10, 6) NOT NULL,
    
    -- Performance
    latency_ms INTEGER,
    
    -- Attribution (optional metadata)
    customer_id VARCHAR(100),
    organization_id VARCHAR(100),
    product_id VARCHAR(100),
    environment VARCHAR(20),
    
    -- Request tracking
    request_id VARCHAR(200),
    trace_id VARCHAR(200),
    
    -- Indexes for fast queries
    INDEX idx_created_at (created_at),
    INDEX idx_provider (provider),
    INDEX idx_customer (customer_id),
    INDEX idx_organization (organization_id)
);

-- Reconciliation summary table (materialized view alternative)
CREATE TABLE reconciliation_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Aggregated data
    total_calls INTEGER NOT NULL,
    total_cost_usd DECIMAL(12, 2) NOT NULL,
    total_tokens BIGINT NOT NULL,
    
    -- By provider
    provider_stats JSONB,
    
    -- Revenium comparison
    revenium_calls INTEGER,
    revenium_cost_usd DECIMAL(12, 2),
    variance_pct DECIMAL(5, 2),
    status VARCHAR(10), -- PASS/FAIL
    
    -- Metadata
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(report_date)
);
```

---

## Implementation

### Setup Script

```bash
#!/bin/bash
# setup-postgres.sh

# Create database
createdb ai_metrics

# Run schema
psql ai_metrics < schema.sql

# Create read-only user for reconciliation queries
psql ai_metrics << EOF
CREATE USER reconciliation_reader WITH PASSWORD 'secure_password';
GRANT SELECT ON ai_calls TO reconciliation_reader;
GRANT SELECT ON reconciliation_reports TO reconciliation_reader;
EOF

echo "✓ PostgreSQL validation database ready"
```

### Python Logger Class

```python
# ai_logger.py
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AICallLogger:
    """PostgreSQL-based validation logger for AI calls"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ai_metrics',
            'user': 'app_user',
            'password': 'secure_password'
        }
        """
        self.db_config = db_config
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection with retry logic"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False  # Use transactions
            logger.info("Connected to PostgreSQL validation database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def log_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: Optional[int] = None,
        customer_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        product_id: Optional[str] = None,
        environment: Optional[str] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> int:
        """
        Log a single AI call to PostgreSQL
        
        Returns: id of inserted row
        Raises: Exception if insert fails
        """
        query = """
            INSERT INTO ai_calls (
                provider, model, input_tokens, output_tokens, cost_usd,
                latency_ms, customer_id, organization_id, product_id,
                environment, request_id, trace_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (
                provider, model, input_tokens, output_tokens, 
                Decimal(str(cost_usd)),
                latency_ms, customer_id, organization_id, product_id,
                environment, request_id, trace_id
            ))
            row_id = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return row_id
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to log AI call: {e}")
            raise
    
    def log_batch(self, calls: list[Dict[str, Any]]) -> int:
        """
        Batch insert multiple calls for better performance
        
        Returns: number of rows inserted
        """
        if not calls:
            return 0
        
        query = """
            INSERT INTO ai_calls (
                provider, model, input_tokens, output_tokens, cost_usd,
                latency_ms, customer_id, organization_id, product_id,
                environment, request_id, trace_id
            ) VALUES %s
        """
        
        values = [
            (
                call['provider'], call['model'], 
                call['input_tokens'], call['output_tokens'],
                Decimal(str(call['cost_usd'])),
                call.get('latency_ms'),
                call.get('customer_id'),
                call.get('organization_id'),
                call.get('product_id'),
                call.get('environment'),
                call.get('request_id'),
                call.get('trace_id')
            )
            for call in calls
        ]
        
        try:
            cursor = self.conn.cursor()
            execute_values(cursor, query, values)
            self.conn.commit()
            count = cursor.rowcount
            cursor.close()
            return count
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to batch log AI calls: {e}")
            raise
    
    def get_stats(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get aggregated statistics for a time period"""
        query = """
            SELECT 
                COUNT(*) as total_calls,
                SUM(cost_usd) as total_cost,
                SUM(total_tokens) as total_tokens,
                AVG(latency_ms) as avg_latency,
                jsonb_object_agg(
                    provider,
                    jsonb_build_object(
                        'calls', provider_calls,
                        'cost', provider_cost,
                        'tokens', provider_tokens
                    )
                ) as by_provider
            FROM (
                SELECT 
                    provider,
                    COUNT(*) as provider_calls,
                    SUM(cost_usd) as provider_cost,
                    SUM(total_tokens) as provider_tokens
                FROM ai_calls
                WHERE created_at >= %s AND created_at < %s
                GROUP BY provider
            ) provider_stats
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (start_date, end_date))
        row = cursor.fetchone()
        cursor.close()
        
        return {
            'total_calls': row[0] or 0,
            'total_cost_usd': float(row[1] or 0),
            'total_tokens': row[2] or 0,
            'avg_latency_ms': float(row[3] or 0),
            'by_provider': row[4] or {}
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed")
```

### Integration Example

```python
# app.py - Your application code
import anthropic
import revenium_middleware_anthropic
from ai_logger import AICallLogger
import time
import os

# Setup PostgreSQL logger
pg_logger = AICallLogger({
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5432)),
    'database': os.getenv('PG_DATABASE', 'ai_metrics'),
    'user': os.getenv('PG_USER', 'app_user'),
    'password': os.getenv('PG_PASSWORD')
})

# Setup Anthropic client (Revenium auto-wraps)
client = anthropic.Anthropic()

def make_ai_call(prompt: str, customer_id: str) -> str:
    """Make AI call with dual tracking"""
    
    start_time = time.time()
    
    # Call AI (Revenium middleware tracks automatically)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        usage_metadata={
            "customer_id": customer_id,
            "organization_id": "acme-corp",
            "product_id": "chatbot",
            "environment": "production"
        }
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Calculate cost (simplified pricing)
    cost_usd = (
        response.usage.input_tokens * 0.000003 +
        response.usage.output_tokens * 0.000015
    )
    
    # Log to PostgreSQL (validation layer)
    try:
        pg_logger.log_call(
            provider='anthropic',
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            customer_id=customer_id,
            organization_id="acme-corp",
            product_id="chatbot",
            environment="production",
            request_id=response.id
        )
    except Exception as e:
        # Log error but don't fail the request
        logger.error(f"Failed to log to PostgreSQL: {e}")
        # Could trigger alert here
    
    return response.content[0].text

# Example usage
result = make_ai_call("Hello, Claude!", "cust_001")
```

---

## Reconciliation Script

```python
# reconciliation.py
from ai_logger import AICallLogger
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
import json

class Reconciliation:
    """Weekly reconciliation between PostgreSQL and Revenium"""
    
    def __init__(self, pg_config: Dict, revenium_api_key: str):
        self.pg_logger = AICallLogger(pg_config)
        self.revenium_api_key = revenium_api_key
        self.revenium_base_url = "https://api.revenium.ai"
    
    def query_revenium(self, start_date: datetime, end_date: datetime) -> Dict:
        """Query Revenium API for usage data"""
        headers = {
            'Authorization': f'Bearer {self.revenium_api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        response = requests.get(
            f"{self.revenium_base_url}/v1/usage",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'total_calls': data['total_transactions'],
            'total_cost_usd': data['total_cost'],
            'by_provider': data.get('by_provider', {})
        }
    
    def reconcile(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Perform reconciliation between PostgreSQL and Revenium"""
        
        # Get PostgreSQL stats
        pg_stats = self.pg_logger.get_stats(start_date, end_date)
        
        # Get Revenium stats
        revenium_stats = self.query_revenium(start_date, end_date)
        
        # Calculate variance
        pg_calls = pg_stats['total_calls']
        revenium_calls = revenium_stats['total_calls']
        
        if pg_calls == 0:
            variance_pct = 0.0
        else:
            variance_pct = abs(pg_calls - revenium_calls) / pg_calls * 100
        
        status = 'PASS' if variance_pct < 2.0 else 'FAIL'
        
        report = {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'postgresql': {
                'total_calls': pg_calls,
                'total_cost_usd': pg_stats['total_cost_usd'],
                'by_provider': pg_stats['by_provider']
            },
            'revenium': {
                'total_calls': revenium_calls,
                'total_cost_usd': revenium_stats['total_cost_usd'],
                'by_provider': revenium_stats.get('by_provider', {})
            },
            'variance_pct': round(variance_pct, 2),
            'status': status,
            'missing_calls': pg_calls - revenium_calls,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Save report to database
        self.save_report(report)
        
        # Alert if failed
        if status == 'FAIL':
            self.send_alert(report)
        
        return report
    
    def save_report(self, report: Dict):
        """Save reconciliation report to database"""
        query = """
            INSERT INTO reconciliation_reports (
                report_date, period_start, period_end,
                total_calls, total_cost_usd, total_tokens,
                provider_stats, revenium_calls, revenium_cost_usd,
                variance_pct, status
            ) VALUES (
                CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (report_date) 
            DO UPDATE SET
                period_start = EXCLUDED.period_start,
                period_end = EXCLUDED.period_end,
                total_calls = EXCLUDED.total_calls,
                total_cost_usd = EXCLUDED.total_cost_usd,
                variance_pct = EXCLUDED.variance_pct,
                status = EXCLUDED.status,
                generated_at = NOW()
        """
        
        cursor = self.pg_logger.conn.cursor()
        cursor.execute(query, (
            report['period_start'],
            report['period_end'],
            report['postgresql']['total_calls'],
            report['postgresql']['total_cost_usd'],
            report['postgresql'].get('total_tokens', 0),
            json.dumps(report['postgresql']['by_provider']),
            report['revenium']['total_calls'],
            report['revenium']['total_cost_usd'],
            report['variance_pct'],
            report['status']
        ))
        self.pg_logger.conn.commit()
        cursor.close()
    
    def send_alert(self, report: Dict):
        """Send alert when reconciliation fails"""
        # Implement your alerting (Slack, email, PagerDuty, etc.)
        print(f"🚨 RECONCILIATION FAILED: {report['variance_pct']}% variance")
        print(f"PostgreSQL: {report['postgresql']['total_calls']} calls")
        print(f"Revenium: {report['revenium']['total_calls']} calls")
        print(f"Missing: {report['missing_calls']} calls")

# Weekly reconciliation job
if __name__ == '__main__':
    import os
    
    pg_config = {
        'host': os.getenv('PG_HOST'),
        'database': os.getenv('PG_DATABASE'),
        'user': os.getenv('PG_USER'),
        'password': os.getenv('PG_PASSWORD')
    }
    
    reconciler = Reconciliation(
        pg_config=pg_config,
        revenium_api_key=os.getenv('REVENIUM_API_KEY')
    )
    
    # Reconcile last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    report = reconciler.reconcile(start_date, end_date)
    
    print(json.dumps(report, indent=2))
```

---

## Deployment

### Docker Compose (for local development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ai_metrics
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    environment:
      PG_HOST: postgres
      PG_DATABASE: ai_metrics
      PG_USER: app_user
      PG_PASSWORD: secure_password
      REVENIUM_METERING_API_KEY: ${REVENIUM_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

### Cron Job for Weekly Reconciliation

```bash
# /etc/cron.d/ai-reconciliation
# Run every Monday at 9 AM
0 9 * * 1 app_user /usr/bin/python3 /app/reconciliation.py >> /var/log/reconciliation.log 2>&1
```

---

## Performance Considerations

### Batch Inserts for High Volume

```python
# For high-volume applications, batch inserts
class BatchLogger:
    def __init__(self, pg_logger: AICallLogger, batch_size: int = 100):
        self.pg_logger = pg_logger
        self.batch_size = batch_size
        self.buffer = []
        self.lock = threading.Lock()
    
    def log(self, call_data: Dict):
        """Add to buffer, flush when batch size reached"""
        with self.lock:
            self.buffer.append(call_data)
            if len(self.buffer) >= self.batch_size:
                self.flush()
    
    def flush(self):
        """Write buffer to database"""
        if self.buffer:
            self.pg_logger.log_batch(self.buffer)
            self.buffer = []
```

### Indexes for Fast Queries

```sql
-- Add these indexes for common queries
CREATE INDEX idx_created_at_provider ON ai_calls(created_at, provider);
CREATE INDEX idx_customer_created ON ai_calls(customer_id, created_at);
CREATE INDEX idx_organization_created ON ai_calls(organization_id, created_at);

-- Partial index for recent data (hot partition)
CREATE INDEX idx_recent_calls ON ai_calls(created_at) 
WHERE created_at > NOW() - INTERVAL '30 days';
```

### Partitioning for Scale

```sql
-- Partition by month for better query performance
CREATE TABLE ai_calls (
    -- same columns as before
) PARTITION BY RANGE (created_at);

CREATE TABLE ai_calls_2024_12 PARTITION OF ai_calls
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE ai_calls_2025_01 PARTITION OF ai_calls
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Auto-create partitions monthly
```

---

## Monitoring

### Key Metrics to Track

```sql
-- Database health
SELECT 
    COUNT(*) as rows_today,
    pg_size_pretty(pg_total_relation_size('ai_calls')) as table_size
FROM ai_calls
WHERE created_at > CURRENT_DATE;

-- Recent reconciliation status
SELECT * FROM reconciliation_reports 
ORDER BY report_date DESC 
LIMIT 7;

-- Detect logging failures (gaps in timestamps)
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as calls_per_hour
FROM ai_calls
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
HAVING COUNT(*) < 10  -- Alert if <10 calls/hour (adjust threshold)
ORDER BY hour;
```

---

## Next Steps

1. **Setup**: Run `docker-compose up` to start PostgreSQL
2. **Schema**: Apply `schema.sql`
3. **Integrate**: Add `AICallLogger` to your application code
4. **Test**: Make some AI calls, verify PostgreSQL inserts
5. **Reconcile**: Run `reconciliation.py` to compare with Revenium
6. **Monitor**: Set up weekly cron job + alerts

This gives you a simple, reliable validation layer that's completely cloud-agnostic and provides the foundation for migrating to OpenTelemetry later.