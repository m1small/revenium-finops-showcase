# Report Generation Specification

## Overview

The report generation system creates beautiful, interactive HTML reports from analysis results using modern web technologies, Chart.js visualizations, and a responsive design system.

## HTML Report Generator

**File**: `src/utils/html_generator.py`

**Class**: `HTMLReportGenerator`

**Purpose**: Provide reusable components for creating styled HTML reports

## Design System

### Color Palette

**Primary Gradient**:
- Start: `#667eea` (Purple-blue)
- End: `#764ba2` (Violet)
- Usage: Headers, cards, buttons, accents

**Status Colors**:
- Success: `rgba(73, 219, 199, 0.8)` (Teal)
- Warning: `rgba(255, 195, 113, 0.8)` (Orange)
- Danger: `rgba(255, 107, 107, 0.8)` (Red)
- Info: `rgba(102, 126, 234, 0.8)` (Blue)

**Chart Colors** (Gradient Palette):
```python
[
    'rgba(102, 126, 234, 0.8)',   # Blue
    'rgba(237, 100, 166, 0.8)',   # Pink
    'rgba(255, 195, 113, 0.8)',   # Orange
    'rgba(147, 51, 234, 0.8)',    # Purple
    'rgba(34, 211, 238, 0.8)',    # Cyan
    'rgba(251, 146, 60, 0.8)',    # Deep Orange
    'rgba(168, 85, 247, 0.8)',    # Violet
    'rgba(59, 130, 246, 0.8)'     # Light Blue
]
```

### Typography

**Font Stack**:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, sans-serif;
```

**Font Sizes**:
- H1: 3em (48px) - Page title
- H2: 2em (32px) - Section headers
- H3: 1.3em (20.8px) - Subsection headers
- Body: 1em (16px)
- Small: 0.9em (14.4px)

**Font Weights**:
- Headers: 700-800 (Bold/Extra Bold)
- Body: 400 (Regular)
- Emphasis: 600 (Semi-bold)

**Line Heights**:
- Body: 1.6
- Headers: 1.2

### Spacing System

**Container**:
- Max width: 1400px
- Padding: 50px
- Border radius: 16px

**Cards**:
- Padding: 30-40px
- Border radius: 12-16px
- Margin: 20-30px

**Grids**:
- Gap: 20-30px
- Min column width: 300px

### Animation System

**Transitions**:
- Duration: 0.3-0.8s
- Easing: `cubic-bezier(0.175, 0.885, 0.32, 1.275)` (bounce)

**Keyframe Animations**:

1. **Gradient Shift** (background):
   ```css
   @keyframes gradientShift {
       0% { background-position: 0% 50%; }
       50% { background-position: 100% 50%; }
       100% { background-position: 0% 50%; }
   }
   ```

2. **Fade In Down** (headers):
   ```css
   @keyframes fadeInDown {
       from { opacity: 0; transform: translateY(-30px); }
       to { opacity: 1; transform: translateY(0); }
   }
   ```

3. **Fade In Up** (content):
   ```css
   @keyframes fadeInUp {
       from { opacity: 0; transform: translateY(30px); }
       to { opacity: 1; transform: translateY(0); }
   }
   ```

**Hover Effects**:
- Cards: `translateY(-5px)` + shadow increase
- Scale: `transform: scale(1.02)`
- Icons: Rotate 360deg

## Chart.js Integration

### CDN Import

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
```

**Version**: 4.4.1
**Source**: jsdelivr CDN
**License**: MIT

### Chart Generation Method

```python
def generate_chart(self,
                   chart_id: str,
                   chart_type: str,
                   data: Dict,
                   title: str = "") -> str:
    """
    Generate Chart.js visualization

    Args:
        chart_id: Unique ID for canvas element
        chart_type: 'bar', 'line', 'doughnut', 'pie', etc.
        data: Chart data with labels and datasets
        title: Chart title

    Returns:
        HTML string with canvas and script
    """
```

### Supported Chart Types

1. **Bar Chart**:
   - Vertical bars
   - Multiple datasets supported
   - Best for: Comparisons, distributions

2. **Line Chart**:
   - Connected points with lines
   - Time series support
   - Best for: Trends, forecasts

3. **Doughnut Chart**:
   - Ring chart with hollow center
   - Percentage display
   - Best for: Composition, proportions

4. **Pie Chart**:
   - Traditional pie slices
   - Simple proportions
   - Best for: Simple distributions

5. **Radar Chart**:
   - Multi-axis spider chart
   - Best for: Multi-dimensional comparisons

6. **Polar Area Chart**:
   - Circular sectors
   - Best for: Comparative magnitudes

### Chart Configuration

**Default Options**:
```javascript
{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
            labels: {
                font: { size: 12, weight: 'bold' },
                padding: 15
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            cornerRadius: 8,
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 13 }
        }
    },
    scales: {  // For bar/line charts
        y: {
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
        },
        x: {
            grid: { display: false }
        }
    }
}
```

**Chart Dimensions**:
- Height: 400px (fixed)
- Width: 100% (responsive)
- Aspect ratio: Disabled (maintains height)

### Chart Data Format

```python
# Bar chart example
data = {
    'labels': ['OpenAI', 'Anthropic', 'Bedrock'],
    'datasets': [{
        'label': 'Total Cost',
        'data': [1234.56, 2345.67, 567.89],
        'backgroundColor': 'rgba(102, 126, 234, 0.8)',
        'borderColor': 'rgba(102, 126, 234, 1)',
        'borderWidth': 2
    }]
}

# Multi-dataset example
data = {
    'labels': ['Starter', 'Pro', 'Enterprise'],
    'datasets': [
        {
            'label': 'Revenue',
            'data': [5800, 9900, 5980],
            'backgroundColor': 'rgba(102, 126, 234, 0.8)'
        },
        {
            'label': 'Cost',
            'data': [3200, 4500, 2100],
            'backgroundColor': 'rgba(237, 100, 166, 0.8)'
        }
    ]
}
```

## Report Components

### 1. Metric Cards

**Purpose**: Display key KPIs prominently

**Usage**:
```python
html = generate_metric_card(
    title="Total AI Cost",
    value="$22,345.67",
    subtitle="30-day period",
    trend="+12.5%"
)
```

**Styling**:
- Gradient background (purple to violet)
- Large value text (2-3em)
- White text on colored background
- Hover lift effect
- Shadow elevation

**Layout**:
```
┌─────────────────────────────┐
│  Total AI Cost              │
│  $22,345.67                 │
│  30-day period  |  +12.5%   │
└─────────────────────────────┘
```

### 2. Data Tables

**Purpose**: Display detailed tabular data

**Features**:
- Alternating row colors (zebra striping)
- Hover highlighting
- Sortable headers (future)
- Responsive scrolling

**Styling**:
```python
html = generate_table(
    headers=['Customer', 'Tier', 'Cost', 'Margin'],
    rows=[
        ['cust_0001', 'Enterprise', '$450.23', '33.5%'],
        ['cust_0002', 'Pro', '$123.45', '52.1%'],
        ...
    ],
    highlight_negative=True  # Red text for negative values
)
```

**Features**:
- Right-align numeric columns
- Currency formatting
- Percentage formatting
- Conditional formatting

### 3. Charts

**Purpose**: Visualize data trends and comparisons

**Container**:
```html
<div class="chart-container">
    <h3>Chart Title</h3>
    <div class="chart-wrapper">
        <canvas id="chartId"></canvas>
    </div>
</div>
```

**Styling**:
- White background
- Box shadow for elevation
- Padding: 30px
- Border radius: 12px
- Height: 400px (fixed)

**Grid Layouts**:
```python
# Side-by-side charts
<div class="charts-grid">
    <div class="chart-container">...</div>
    <div class="chart-container">...</div>
</div>
```

### 4. Alert Boxes

**Purpose**: Highlight important recommendations

**Types**:
- Info (blue)
- Success (green/teal)
- Warning (orange)
- Danger (red)

**Usage**:
```python
html = generate_alert(
    message="15 customers are unprofitable - implement usage caps",
    type="warning",
    title="Action Required"
)
```

**Styling**:
- Colored left border (5px)
- Light background tint
- Bold title
- Icon (optional)

### 5. Comparison Sections

**Purpose**: Show before/after or with/without Revenium

**Layout**:
```
┌─────────────────┬─────────────────┐
│  Without        │  With           │
│  Revenium       │  Revenium       │
│                 │                 │
│  ❌ Manual      │  ✅ Automatic   │
│  ❌ Delayed     │  ✅ Real-time   │
└─────────────────┴─────────────────┘
```

**Styling**:
- Two-column grid
- Icons (✅ ❌)
- Color coding (red vs green)
- Centered alignment

### 6. Recommendation Lists

**Purpose**: Provide actionable next steps

**Format**:
```python
recommendations = [
    "🚨 High priority: Contact cust_0042 about usage spike",
    "💰 Potential saving: Switch to claude-sonnet-4 for simple tasks",
    "📊 Opportunity: Implement reserved capacity for 30% savings"
]
```

**Styling**:
- Numbered or bulleted list
- Emoji icons for categories
- Bold key phrases
- Padding between items

## Report Structure

### Standard Report Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Title</title>
    <style>
        /* Embedded CSS */
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- Report metadata -->
        <div class="metadata">
            Generated: 2025-12-19 10:30:00
            Data period: 30 days
            Total records: 142,126
        </div>

        <!-- Executive Summary -->
        <h1>Report Title</h1>

        <!-- Key Metrics -->
        <div class="metric-card">...</div>

        <!-- Sections -->
        <h2>Section 1</h2>
        <div class="chart-container">...</div>

        <h2>Section 2</h2>
        <table>...</table>

        <!-- Recommendations -->
        <h2>Recommendations</h2>
        <div class="alert">...</div>

        <!-- Revenium Value Prop -->
        <h2>With vs Without Revenium</h2>
        <div class="comparison">...</div>
    </div>

    <script>
        /* Chart initialization */
    </script>
</body>
</html>
```

### Report Sections (Typical)

1. **Metadata** - Generation timestamp, data period, record count
2. **Executive Summary** - Key findings in 2-3 sentences
3. **Key Metrics** - Top 3-5 KPIs in metric cards
4. **Detailed Analysis** - Charts, tables, breakdowns
5. **Recommendations** - Actionable next steps
6. **Revenium Value** - With/without comparison

## Responsive Design

### Breakpoints

```css
/* Desktop (default) */
@media (min-width: 1024px) {
    .charts-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Tablet */
@media (max-width: 1023px) {
    .container { padding: 30px; }
    h1 { font-size: 2.5em; }
    .charts-grid { grid-template-columns: 1fr; }
}

/* Mobile */
@media (max-width: 768px) {
    .container { padding: 20px; }
    h1 { font-size: 2em; }
    h2 { font-size: 1.5em; }
    table { font-size: 0.85em; }
}
```

### Mobile Optimizations

- Stacked charts (single column)
- Reduced padding/margins
- Smaller font sizes
- Horizontal table scrolling
- Touch-friendly tap targets (min 44px)

## Print Styles

```css
@media print {
    body {
        background: white;
        color: black;
    }

    .container {
        box-shadow: none;
        padding: 20px;
    }

    .metric-card {
        background: white;
        border: 2px solid #333;
        color: black;
    }

    /* Page breaks */
    h2 { page-break-before: always; }
    .chart-container { page-break-inside: avoid; }
}
```

## Accessibility

### WCAG Compliance

**Color Contrast**:
- Text on background: Minimum 4.5:1 (WCAG AA)
- Large text (18pt+): Minimum 3:1
- Charts: Distinct colors, patterns for colorblind

**Keyboard Navigation**:
- All interactive elements focusable
- Visible focus indicators
- Logical tab order

**Screen Readers**:
- Semantic HTML (`<header>`, `<main>`, `<section>`)
- Alt text for charts (in `<canvas>` fallback)
- ARIA labels where needed
- Table headers properly marked

**Example**:
```html
<table role="table">
    <thead>
        <tr>
            <th scope="col">Customer</th>
            <th scope="col">Cost</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>cust_0001</td>
            <td>$450.23</td>
        </tr>
    </tbody>
</table>
```

## Performance Optimization

### File Size

**Techniques**:
- Embedded CSS (no external requests)
- Embedded JS (except Chart.js CDN)
- Minified where possible
- No images (pure CSS gradients)

**Typical Sizes**:
- HTML: 10-20 KB
- CSS (embedded): 5-8 KB
- Chart.js (CDN): ~200 KB (cached)
- Total: 15-30 KB per report

### Load Time

**Optimization**:
- Single HTML file (1 HTTP request + Chart.js CDN)
- Chart.js loaded from fast CDN (jsdelivr)
- No render-blocking resources
- Charts render after page load

**Typical Load**:
- First load: <500ms (with CDN)
- Cached: <100ms

### Chart Rendering

**Lazy Loading**:
```javascript
// Charts only initialize after DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});
```

**Animation**:
- Smooth animations (400ms default)
- Hardware-accelerated where possible
- Disable animations in print mode

## Browser Compatibility

### Supported Browsers

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

### Required Features

- ES6 JavaScript
- CSS Grid
- CSS Flexbox
- CSS Animations
- Canvas API (for Chart.js)
- Local Storage (for viewer preferences)

### Polyfills

Not required for target browsers (all modern)

## Examples

### Customer Profitability Report

**Charts Included**:
1. Revenue vs Cost by Tier (Bar chart)
2. Profit Margin % by Tier (Bar chart)
3. Customer Distribution by Margin (Doughnut chart)
4. Average Margin by Category (Bar chart)

**Tables**:
- Top 10 unprofitable customers
- Tier analysis summary

**Recommendations**:
- Usage cap implementations
- Tier upgrade suggestions
- Customer interventions

### Feature Economics Report

**Charts Included**:
1. Total Cost by Feature (Bar chart)
2. Customer Adoption by Feature (Bar chart)

**Tables**:
- Feature cost breakdown
- Adoption rates
- Investment matrix

**Recommendations**:
- Invest/maintain/optimize/sunset decisions
- Bundle opportunities

## Testing

### Visual Regression Testing

```python
# Generate report
analyzer.generate_html_report('test_report.html')

# Open in browser
import webbrowser
webbrowser.open('test_report.html')

# Manual verification:
# - Layout correct
# - Charts render
# - Colors match design
# - Responsive works
# - Print preview looks good
```

### Cross-Browser Testing

- Chrome (primary target)
- Firefox
- Safari (macOS/iOS)
- Edge

### Accessibility Testing

- Screen reader (NVDA, JAWS)
- Keyboard navigation
- Color contrast checker
- WAVE accessibility tool

## Future Enhancements

### Planned Features

1. **Dark Mode**:
   - Toggle switch in viewer
   - Inverted color scheme
   - Reduced eye strain

2. **Chart Exports**:
   - Download as PNG
   - Download as PDF
   - Copy to clipboard

3. **Interactive Filtering**:
   - Date range selector
   - Provider filter
   - Customer filter
   - Real-time chart updates

4. **Real-Time Updates**:
   - WebSocket connection
   - Live data streaming
   - Auto-refresh charts

5. **Custom Themes**:
   - Color palette selector
   - Font options
   - Layout preferences

## Related Specifications

- **Architecture**: See `architecture.md`
- **Analyzers**: See `analyzers.md` (consumers of report generator)
- **Workflows**: See `workflows.md` (how reports are generated and viewed)
