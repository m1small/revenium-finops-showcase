# System Architecture

## Overview

The Revenium FinOps Showcase is a Python-based demonstration system that simulates AI API usage and generates comprehensive business intelligence reports. The system follows a layered architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Web Viewer (viewer/index.html)                        │ │
│  │  - Modern animated UI with gradient backgrounds        │ │
│  │  - Report navigation and category browsing             │ │
│  │  - Responsive design (desktop/tablet/mobile)           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP (port 8000)
                            │
┌─────────────────────────────────────────────────────────────┐
│                   WEB SERVER LAYER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Auto-Processing Server (viewer/serve.py)              │ │
│  │  - Serves HTML reports                                 │ │
│  │  - Detects data changes                                │ │
│  │  - Auto-runs analyzers when needed                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Reads reports
                            │
┌─────────────────────────────────────────────────────────────┐
│                  REPORT GENERATION LAYER                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  HTML Report Generator (utils/html_generator.py)       │ │
│  │  - Chart.js 4.4.1 integration                          │ │
│  │  - Modern gradient design system                       │ │
│  │  - Responsive components (cards, tables, charts)       │ │
│  │  - Embedded CSS/JS (no external dependencies)          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Generates HTML
                            │
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE LAYER                    │
│  ┌───────────────────────┐  ┌───────────────────────────┐  │
│  │  FinOps Analyzers     │  │  UBR Analyzers            │  │
│  │  ──────────────────   │  │  ────────────────         │  │
│  │  1. Understanding     │  │  1. Profitability         │  │
│  │  2. Performance       │  │  2. Pricing Strategy      │  │
│  │  3. Real-time         │  │  3. Feature Economics     │  │
│  │  4. Optimization      │  │                           │  │
│  │  5. Alignment         │  │                           │  │
│  └───────────────────────┘  └───────────────────────────┘  │
│                                                             │
│  Common Pattern:                                            │
│  - load_data() -> analyze() -> generate_html_report()      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Reads CSV
                            │
┌─────────────────────────────────────────────────────────────┐
│                      DATA STORAGE LAYER                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  CSV Data Store (data/simulated_calls.csv)             │ │
│  │  - 19-field metadata schema                            │ │
│  │  - Git-friendly text format                            │ │
│  │  - Portable and human-readable                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Writes CSV
                            │
┌─────────────────────────────────────────────────────────────┐
│                  DATA SIMULATION LAYER                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Core Simulator (simulator/core.py)                    │ │
│  │  - Base traffic patterns                               │ │
│  │  - Customer archetypes (light/power/heavy)             │ │
│  │  - Realistic usage patterns                            │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Scenario Simulators (simulator/scenarios/)            │ │
│  │  - Seasonal patterns                                   │ │
│  │  - Burst traffic                                       │ │
│  │  - Gradual decline (churn)                             │ │
│  │  - Steady growth (legacy)                              │ │
│  │  - Viral spike (legacy)                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Simulation Layer
**Location**: `src/simulator/`

**Purpose**: Generate realistic AI API usage data with rich Revenium metadata

**Components**:
- **AICallSimulator** (`core.py`): Base simulator with realistic patterns
- **Scenario Simulators** (`scenarios/`): Specialized traffic patterns
- **Master Runner** (`run_all_simulators.py`): Orchestrates all simulators

**Output**: CSV file with 19-field metadata schema

**Key Features**:
- Multi-provider support (OpenAI, Anthropic, Bedrock)
- Customer archetypes (light, power, heavy users)
- Realistic patterns (business hours, weekend effects)
- Deterministic with optional seed

### 2. Data Storage Layer
**Location**: `src/data/`

**Purpose**: Store simulated AI call data in portable, Git-friendly format

**Format**: CSV (Comma-Separated Values)

**Advantages**:
- Human-readable and editable
- No database required
- Git-friendly (text-based diffs)
- Import into Excel/Google Sheets
- Portable across platforms

**Schema**: See `data-schema.md` for complete field definitions

### 3. Analysis Engine Layer
**Location**: `src/analyzers/`

**Purpose**: Transform raw CSV data into actionable business insights

**Architecture Pattern**:
```python
class Analyzer:
    def __init__(self, csv_file: str)
    def load_data(self) -> None
    def analyze(self) -> Dict
    def generate_html_report(self, output_file: str) -> str
```

**Components**:
- **FinOps Analyzers** (`finops/`): 5 domain-specific analyzers
- **UBR Analyzers** (`ubr/`): 3 revenue-focused analyzers
- **Master Runner** (`run_all_analyzers.py`): Executes all analyzers

**Design Principles**:
- Self-contained (each <400 lines)
- Independent execution
- Consistent interface
- Comprehensive error handling

### 4. Report Generation Layer
**Location**: `src/utils/html_generator.py`

**Purpose**: Create beautiful, interactive HTML reports from analysis results

**Features**:
- Chart.js 4.4.1 integration (CDN)
- Modern gradient design system
- Responsive components
- Print-friendly layouts
- Zero external file dependencies (embedded CSS/JS)

**Components**:
- Metric cards with gradients
- Data tables with formatting
- Interactive charts (bar, line, doughnut, pie)
- Alert boxes for recommendations
- Comparison sections

### 5. Web Server Layer
**Location**: `viewer/serve.py`

**Purpose**: Serve HTML reports with auto-processing capabilities

**Features**:
- Simple Python HTTP server (port 8000)
- Data freshness detection
- Auto-runs analyzers when data changes
- Static file serving
- No configuration required

**Workflow**:
1. Check if `data/simulated_calls.csv` exists
2. Compare timestamps with existing reports
3. Run analyzers if data is newer
4. Serve reports via HTTP

### 6. User Interface Layer
**Location**: `viewer/index.html`

**Purpose**: Interactive web-based report viewer

**Features**:
- Modern animated gradient background
- Category-based navigation (FinOps vs UBR)
- Responsive card-based layout
- Hover effects and transitions
- Mobile-optimized

**Design Elements**:
- Animated gradients with keyframes
- Fade-in/slide-up entrance animations
- Card hover transformations
- Badge system for highlights
- Gradient text effects

## Data Flow

### Simulation Flow
```
1. User runs simulator
   ↓
2. AICallSimulator generates realistic calls
   ↓
3. Calls enriched with Revenium metadata
   ↓
4. Data written to CSV (append or overwrite)
   ↓
5. CSV file ready for analysis
```

### Analysis Flow
```
1. User runs analyzer(s)
   ↓
2. Analyzer loads CSV data
   ↓
3. Data parsed and validated
   ↓
4. Analysis logic executes
   ↓
5. Results formatted
   ↓
6. HTML report generated
   ↓
7. Report saved to reports/html/
   ↓
8. Manifest updated
```

### Viewing Flow
```
1. User starts web server
   ↓
2. Server checks data freshness
   ↓
3. Auto-runs analyzers if needed
   ↓
4. Server starts on port 8000
   ↓
5. User opens browser to localhost:8000
   ↓
6. Viewer loads manifest.json
   ↓
7. Reports displayed with navigation
   ↓
8. User browses interactive reports
```

## Integration Points

### Showcase Layer
**Location**: `showcase/`

**Purpose**: Demonstrate real-world Revenium SDK integration patterns

**Components**:
- **Instrumentation** (`instrumentation/`): Basic tracking examples
- **Metadata Builders** (`metadata/`): Fluent API for metadata
- **Query Patterns** (`queries/`): Common aggregation queries
- **Scenarios** (`scenarios/`): Business use case demonstrations

**Integration with Core**:
- Independent of simulation layer
- Shows how real apps would integrate
- Uses same metadata schema
- Demonstrates best practices

## Technology Stack

### Core Technologies
- **Python**: 3.7+ (standard library only)
- **Chart.js**: 4.4.1 (CDN, for visualizations)
- **HTTP Server**: Python `http.server` module
- **Data Format**: CSV (text-based)

### Design Technologies
- **CSS**: Modern features (Grid, Flexbox, Animations)
- **JavaScript**: ES6+ for Chart.js integration
- **HTML5**: Semantic markup

### No External Dependencies
- Zero pip packages required
- Chart.js loaded via CDN (not bundled)
- All utilities in standard library
- Self-contained deployment

## Scalability Considerations

### Current Design
- Optimized for demo/showcase scenarios
- Handles 100K+ calls efficiently
- In-memory CSV processing
- Linear complexity for most operations

### Performance Characteristics
- **CSV Loading**: O(n) streaming
- **Analysis**: O(n) single-pass where possible
- **Report Generation**: O(1) template-based
- **Memory**: Proportional to dataset size

### Scaling Strategies (Future)
- Stream processing for large datasets
- Chunked CSV reading
- Parallel analyzer execution
- Database backend option
- Incremental updates

## Security Considerations

### Current Security Posture
- Read-only data access for analyzers
- No user authentication (demo system)
- Local-only web server (localhost:8000)
- No sensitive data handling
- Simulated data only

### Production Considerations (Future)
- Add authentication/authorization
- HTTPS/TLS support
- Input validation and sanitization
- Rate limiting
- CORS configuration
- Environment-based secrets

## Extensibility

### Adding New Analyzers
1. Create analyzer in `src/analyzers/finops/` or `src/analyzers/ubr/`
2. Implement standard interface (load_data, analyze, generate_html_report)
3. Add to `run_all_analyzers.py`
4. Add to manifest categories

### Adding New Traffic Patterns
1. Create scenario in `src/simulator/scenarios/`
2. Inherit from `AICallSimulator` or create custom
3. Add to `run_all_simulators.py`
4. Document in scenarios README

### Adding New Chart Types
1. Add chart generation method to `HTMLReportGenerator`
2. Use Chart.js configuration
3. Add CSS styling if needed
4. Update analyzer to use new chart

### Adding New Metadata Fields
1. Update `AICall` dataclass in `simulator/core.py`
2. Update CSV schema
3. Update analyzers that use new fields
4. Document in `data-schema.md`

## Deployment Architecture

### Current Deployment
- Local development environment
- Manual execution of scripts
- Port 8000 for web viewer
- File-based storage

### Recommended Production Deployment
```
┌─────────────────────────────────────────┐
│         Load Balancer (HTTPS)           │
└─────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼────────┐ ┌────────▼────────┐
│  Web Server 1   │ │  Web Server 2   │
│  (Docker)       │ │  (Docker)       │
└────────┬────────┘ └────────┬────────┘
         │                   │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │  Shared Storage   │
         │  (S3, NFS, etc.)  │
         └───────────────────┘
```

### Container Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY src/ ./src/
COPY viewer/ ./viewer/
COPY showcase/ ./showcase/
EXPOSE 8000
CMD ["python3", "viewer/serve.py"]
```

## Monitoring & Observability

### Current Capabilities
- Console output for progress
- Success/failure reporting
- Timing information
- CSV row counts

### Future Enhancements
- Structured logging (JSON)
- Metrics collection (Prometheus)
- Health check endpoints
- Error tracking (Sentry)
- Performance monitoring

## Design Principles

1. **Simplicity**: Minimal dependencies, straightforward architecture
2. **Modularity**: Independent components with clear interfaces
3. **Extensibility**: Easy to add new analyzers, patterns, charts
4. **Performance**: Fast execution, efficient processing
5. **Portability**: Works on any platform with Python 3.7+
6. **Maintainability**: Consistent patterns, comprehensive docs
7. **Demonstrability**: Self-contained, quick to run, impressive results

## Architecture Trade-offs

### Chosen: CSV Storage
**Pros**: Simple, portable, Git-friendly, human-readable
**Cons**: Not ideal for very large datasets (>1M rows)
**Alternative**: PostgreSQL, SQLite, Parquet

### Chosen: In-Memory Processing
**Pros**: Fast, simple, no external dependencies
**Cons**: Memory usage scales with dataset
**Alternative**: Stream processing, chunked reads

### Chosen: CDN for Chart.js
**Pros**: No bundling, always latest version, fast CDN
**Cons**: Requires internet for initial load
**Alternative**: Bundle Chart.js locally

### Chosen: Python HTTP Server
**Pros**: Built-in, zero config, perfect for demos
**Cons**: Not production-grade, no HTTPS
**Alternative**: nginx, Apache, Caddy

## Related Specifications

- **Data Schema**: See `data-schema.md`
- **Simulators**: See `simulators.md`
- **Analyzers**: See `analyzers.md`
- **Reports**: See `reports.md`
- **Integration**: See `integration.md`
- **Workflows**: See `workflows.md`
