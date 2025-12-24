# HTML Report Generators

This directory contains modular HTML report generators for the Revenium FinOps dashboard.

## Structure

Previously, all 8 report generators were in a single monolithic `html_generator.py` file (2300+ lines).
They have been refactored into individual, focused modules:

```
generators/
├── __init__.py                  # Exports all generators
├── shared.py                    # Common utilities and templates
├── usage_cost_generator.py      # Understanding Usage & Cost report
├── performance_generator.py     # Performance Analysis report
├── realtime_generator.py        # Real-Time Monitoring & Alerts report
├── optimization_generator.py    # Rate Optimization & Cost Savings report
├── alignment_generator.py       # Organizational Cost Alignment report
├── profitability_generator.py   # Customer Profitability Analysis report
├── pricing_generator.py         # Pricing Strategy Analysis report
└── features_generator.py        # Feature Economics & ROI report
```

## Shared Utilities (`shared.py`)

Common functionality extracted to avoid duplication:

- **`format_currency(value, decimals=2)`** - Format currency values (supports 3 decimals for model costs)
- **`format_number(value)`** - Format integers with thousand separators
- **`get_base_styles()`** - Returns common CSS used across all reports
- **`build_html_template(title, content, scripts)`** - Builds complete HTML document structure
- **`build_recommendations_html(recommendations)`** - Generates recommendations section

## Usage

Import generators from the `generators` package:

```python
from generators import (
    generate_understanding_report,
    generate_performance_report,
    generate_realtime_report,
    generate_optimization_report,
    generate_alignment_report,
    generate_profitability_report,
    generate_pricing_report,
    generate_features_report
)

# Use any generator
data = analyzer.analyze()
generate_understanding_report(data, 'reports/html/understanding.html')
```

## Report Features

All reports include:
- **Professional FinOps Dashboard** design (not advertisement-style)
- **Chart.js visualizations** (2 per report)
- **Alert system** with severity levels (critical, warning, info, success)
- **Actionable recommendations** based on data analysis
- **Case study insights** incorporated as dashboard alerts

## Benefits of Refactoring

1. **Maintainability** - Each report is self-contained and easier to modify
2. **Clarity** - ~300 lines per file vs 2300+ lines monolith
3. **Reusability** - Shared utilities prevent code duplication
4. **Testing** - Individual generators can be tested in isolation
5. **Collaboration** - Multiple developers can work on different reports simultaneously

## Migration Notes

The old `utils/html_generator.py` file remains for backward compatibility but should be considered deprecated.
All new code should import from the `generators` package instead:

```python
# Old (deprecated)
from utils.html_generator import generate_understanding_report

# New (recommended)
from generators import generate_understanding_report
```
