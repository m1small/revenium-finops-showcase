"""Shared utilities and templates for HTML report generation."""

from datetime import datetime


def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency with configurable decimal places."""
    if decimals == 3:
        return f"${value:,.3f}"
    return f"${value:,.2f}"


def format_number(value: int) -> str:
    """Format integer with thousand separators."""
    return f"{value:,}"


def get_base_styles() -> str:
    """Return common CSS styles used across all reports."""
    return """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white;
                      padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #1a1a1a; margin-top: 0; font-size: 32px; }
        h2 { color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 40px; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px; margin: 30px 0; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .metric-label { font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 32px; font-weight: bold; margin-top: 8px; }
        .metric-card:nth-child(2) { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .metric-card:nth-child(3) { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .metric-card:nth-child(4) { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }
        th { background: #f8f9fa; padding: 14px; text-align: left; font-weight: 600;
              border-bottom: 2px solid #e0e0e0; font-size: 13px; text-transform: uppercase;
              color: #666; letter-spacing: 0.5px; }
        td { padding: 14px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f8f9fa; }
        .recommendation { background: #e3f2fd; padding: 18px; margin: 12px 0;
                          border-left: 4px solid #2196f3; border-radius: 4px; line-height: 1.6; }
        .timestamp { color: #999; font-size: 14px; margin-top: 40px; text-align: center;
                      padding-top: 20px; border-top: 1px solid #e0e0e0; }
        .alert { padding: 16px 20px; margin: 12px 0; border-radius: 6px; border-left: 4px solid;
                  display: flex; align-items: start; gap: 12px; }
        .alert-critical { background: #fef1f1; border-color: #d32f2f; }
        .alert-warning { background: #fff8e1; border-color: #f57c00; }
        .alert-info { background: #e3f2fd; border-color: #1976d2; }
        .alert-success { background: #f1f8f4; border-color: #388e3c; }
        .alert-icon { font-size: 24px; line-height: 1; }
        .alert-content { flex: 1; }
        .alert-title { font-weight: 600; margin-bottom: 6px; font-size: 15px; }
        .alert-description { opacity: 0.9; line-height: 1.5; }
        .chart-container { position: relative; height: 350px; margin: 30px 0; }
    """


def build_html_template(title: str, content: str, scripts: str = "") -> str:
    """Build complete HTML document with common structure."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        {get_base_styles()}
    </style>
</head>
<body>
    <div class="container">
        {content}

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            <a href="index.html" style="color: #2196f3; text-decoration: none;">View All Reports</a>
        </div>
    </div>

    {scripts}
</body>
</html>"""


def build_recommendations_html(recommendations: list) -> str:
    """Build recommendations section HTML."""
    if not recommendations:
        return '<p style="color: #666;">No recommendations at this time.</p>'

    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f'<div class="recommendation">{i}. {rec}</div>\n'
    return rec_html
