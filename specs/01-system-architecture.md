# System Architecture Specification

## Overview

The Revenium FinOps Showcase is a demonstration system for AI cost management and financial operations analysis. The system simulates AI API usage, analyzes costs across multiple dimensions, and generates interactive HTML reports.

## Architectural Principles

1. **Zero External Dependencies**: System uses only standard library components (except Chart.js via CDN)
2. **Separation of Concerns**: Clear boundaries between simulation, analysis, and presentation
3. **Data-Driven Design**: All analysis operates on CSV-based datasets
4. **Stateless Components**: Analyzers are independent and can run in any order
5. **Live Monitoring**: Real-time progress tracking during data generation and analysis

## Component Layers

### Layer 1: Configuration
- Centralized configuration management
- System-wide constants and thresholds
- Provider and model definitions
- Default values for all configurable parameters

### Layer 2: Data Generation
- Traffic simulation engine
- Scenario-based pattern generators
- CSV data persistence
- Batch writing optimization

### Layer 3: Data Analysis
- Common analysis utilities
- FinOps domain analyzers (5 components)
- UBR domain analyzers (3 components)
- Advanced analytics (5 components)

### Layer 4: Report Generation
- HTML template system
- Chart.js visualization integration
- Shared UI components
- Report orchestration

### Layer 5: Web Interface
- HTTP server for report delivery
- Real-time status API
- Background monitoring
- On-demand analyzer execution

## Component Interactions

```
User → CLI → Simulator → CSV File → Analyzer → Data Dict → Generator → HTML Report → Viewer → User
                                        ↑                                      ↓
                                   Common Utils                          Status API
```

### Data Flow

1. **Generation Phase**:
   - User invokes simulator with target size
   - Simulator cycles through scenarios
   - Each scenario generates batches of API calls
   - Calls appended to CSV file
   - Process continues until target size reached

2. **Analysis Phase**:
   - Analyzer loads CSV into memory
   - Applies domain-specific transformations
   - Calculates metrics and aggregations
   - Returns structured dictionary
   - Generator converts to HTML

3. **Viewing Phase**:
   - Server monitors CSV file size
   - Serves static HTML reports
   - Provides status JSON API
   - Supports on-demand analyzer execution

## Key Abstractions

### Simulator Pattern
All scenario simulators implement:
- Constructor accepting configuration parameters
- Run method generating call records
- Shared core functionality for provider/model selection
- Time-based multipliers for realistic patterns

### Analyzer Pattern
All analyzers implement:
- Constructor accepting CSV file path
- Analyze method returning structured dictionary
- Common utility functions for grouping and aggregation
- Recommendations generation

### Generator Pattern
All generators implement:
- Function accepting data dictionary and output path
- HTML template composition
- Chart.js integration where applicable
- Consistent styling via shared utilities

## Scalability Considerations

### Memory Management
- CSV files loaded entirely into memory
- Maximum practical dataset: 2GB (configurable)
- Batch writing reduces I/O overhead
- Analysis operates on in-memory data structures

### Performance Optimization
- Batch size: 5000 records per write
- Background monitoring interval: 10 seconds
- Status polling interval: 15 seconds
- No database overhead

### Extensibility
- New analyzers: Add class + generator + registry entry
- New scenarios: Subclass base simulator
- New providers: Update configuration
- New metrics: Extend analyzer classes

## Security Considerations

- Local-only HTTP server (no external access)
- No authentication required (demo system)
- No sensitive data processing
- CSV files are plain text
- No code execution from data

## Deployment Model

### File System Structure
```
/
├── data/                   # Generated CSV files
├── reports/html/           # Generated HTML reports
├── src/                    # Source code
│   ├── config.py          # Configuration
│   ├── simulator/         # Data generation
│   ├── analyzers/         # Analysis engines
│   └── generators/        # Report generation
└── viewer/                # Web server
```

### Runtime Requirements
- Python 3.7+
- File system access for data/reports directories
- Network access for Chart.js CDN (report viewing)
- Port 8000 available (configurable)

## Error Handling Strategy

### Simulation Errors
- Continue on individual call generation errors
- Stop on file system errors
- Report progress on interrupt

### Analysis Errors
- Skip failed analyzers, continue with others
- Print stack traces for debugging
- Generate partial reports on non-critical errors

### Server Errors
- Graceful handling of missing files
- 404 for non-existent reports
- JSON error responses for API endpoints
