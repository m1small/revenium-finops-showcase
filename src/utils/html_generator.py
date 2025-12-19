#!/usr/bin/env python3
"""
HTML Report Generator - Utility for creating styled HTML reports
"""

from datetime import datetime
from typing import List, Dict, Optional, Any


class HTMLReportGenerator:
    """Generate styled HTML reports with consistent formatting"""
    
    def __init__(self, title: str, description: str, category: str = ""):
        self.title = title
        self.description = description
        self.category = category
        self.sections = []
        self.generated_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def add_section(self, title: str, level: int = 2) -> None:
        """Add a section header"""
        self.sections.append({
            'type': 'section',
            'title': title,
            'level': level
        })
    
    def add_paragraph(self, text: str) -> None:
        """Add a paragraph of text"""
        self.sections.append({
            'type': 'paragraph',
            'text': text
        })
    
    def add_metric_cards(self, metrics: List[Dict[str, Any]]) -> None:
        """Add a grid of metric cards
        
        Args:
            metrics: List of dicts with 'label', 'value', and optional 'trend'
        """
        self.sections.append({
            'type': 'metrics',
            'data': metrics
        })
    
    def add_table(self, headers: List[str], rows: List[List[Any]], 
                  caption: Optional[str] = None) -> None:
        """Add a data table
        
        Args:
            headers: Column headers
            rows: Table data rows
            caption: Optional table caption
        """
        self.sections.append({
            'type': 'table',
            'headers': headers,
            'rows': rows,
            'caption': caption
        })
    
    def add_alert(self, message: str, alert_type: str = 'info') -> None:
        """Add an alert box
        
        Args:
            message: Alert message
            alert_type: 'info', 'warning', 'success', or 'danger'
        """
        self.sections.append({
            'type': 'alert',
            'message': message,
            'alert_type': alert_type
        })
    
    def add_list(self, items: List[str], ordered: bool = False) -> None:
        """Add a list
        
        Args:
            items: List items
            ordered: True for numbered list, False for bullets
        """
        self.sections.append({
            'type': 'list',
            'items': items,
            'ordered': ordered
        })
    
    def add_html(self, html: str) -> None:
        """Add raw HTML content"""
        self.sections.append({
            'type': 'raw_html',
            'content': html
        })
    
    def _get_css(self) -> str:
        """Return embedded CSS styles"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #ffffff;
            color: #1f2937;
            line-height: 1.6;
            padding: 2rem;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .report-header {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }
        
        h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .report-meta {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        .report-description {
            color: #4b5563;
            margin-top: 0.5rem;
        }
        
        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            color: #1f2937;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            color: #1f2937;
        }
        
        h4 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            color: #374151;
        }
        
        p {
            margin: 1rem 0;
            color: #4b5563;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .metric-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.25rem;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 1.75rem;
            font-weight: 600;
            color: #1f2937;
        }
        
        .metric-trend {
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .metric-trend.positive {
            color: #16a34a;
        }
        
        .metric-trend.negative {
            color: #dc2626;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }
        
        caption {
            caption-side: top;
            padding: 0.75rem;
            font-weight: 600;
            text-align: left;
            color: #1f2937;
        }
        
        th {
            background: #f9fafb;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            font-size: 0.875rem;
        }
        
        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e5e7eb;
            font-size: 0.875rem;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tbody tr:hover {
            background: #f9fafb;
        }
        
        .alert {
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        
        .alert-info {
            background: #eff6ff;
            border-color: #2563eb;
            color: #1e40af;
        }
        
        .alert-warning {
            background: #fff7ed;
            border-color: #ea580c;
            color: #c2410c;
        }
        
        .alert-success {
            background: #f0fdf4;
            border-color: #16a34a;
            color: #15803d;
        }
        
        .alert-danger {
            background: #fef2f2;
            border-color: #dc2626;
            color: #b91c1c;
        }
        
        ul, ol {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        li {
            margin: 0.5rem 0;
            color: #4b5563;
        }
        
        .text-right {
            text-align: right;
        }
        
        .text-center {
            text-align: center;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            
            h2 {
                font-size: 1.25rem;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.75rem;
            }
            
            th, td {
                padding: 0.5rem;
            }
        }
        
        @media print {
            body {
                padding: 0;
            }
            
            .no-print {
                display: none;
            }
            
            .report-container {
                max-width: 100%;
            }
            
            h2 {
                page-break-after: avoid;
            }
            
            table {
                page-break-inside: avoid;
            }
        }
        """
    
    def _render_section(self, section: Dict) -> str:
        """Render a single section to HTML"""
        section_type = section['type']
        
        if section_type == 'section':
            level = section['level']
            title = section['title']
            return f'<h{level}>{title}</h{level}>\n'
        
        elif section_type == 'paragraph':
            return f'<p>{section["text"]}</p>\n'
        
        elif section_type == 'metrics':
            html = '<div class="metrics-grid">\n'
            for metric in section['data']:
                html += '  <div class="metric-card">\n'
                html += f'    <div class="metric-label">{metric["label"]}</div>\n'
                html += f'    <div class="metric-value">{metric["value"]}</div>\n'
                if 'trend' in metric and metric['trend']:
                    trend_class = 'positive' if '+' in str(metric['trend']) else 'negative'
                    html += f'    <div class="metric-trend {trend_class}">{metric["trend"]}</div>\n'
                html += '  </div>\n'
            html += '</div>\n'
            return html
        
        elif section_type == 'table':
            html = '<table>\n'
            if section.get('caption'):
                html += f'  <caption>{section["caption"]}</caption>\n'
            html += '  <thead>\n    <tr>\n'
            for header in section['headers']:
                html += f'      <th>{header}</th>\n'
            html += '    </tr>\n  </thead>\n  <tbody>\n'
            for row in section['rows']:
                html += '    <tr>\n'
                for cell in row:
                    html += f'      <td>{cell}</td>\n'
                html += '    </tr>\n'
            html += '  </tbody>\n</table>\n'
            return html
        
        elif section_type == 'alert':
            alert_type = section['alert_type']
            message = section['message']
            return f'<div class="alert alert-{alert_type}">{message}</div>\n'
        
        elif section_type == 'list':
            tag = 'ol' if section['ordered'] else 'ul'
            html = f'<{tag}>\n'
            for item in section['items']:
                html += f'  <li>{item}</li>\n'
            html += f'</{tag}>\n'
            return html
        
        elif section_type == 'raw_html':
            return section['content'] + '\n'
        
        return ''
    
    def generate(self) -> str:
        """Generate complete HTML document"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} - Revenium FinOps</title>
    <style>{self._get_css()}</style>
</head>
<body>
    <div class="report-container">
        <header class="report-header">
            <h1>{self.title}</h1>
            <div class="report-meta">
                Generated: {self.generated_date}"""
        
        if self.category:
            html += f' | Category: {self.category}'
        
        html += """
            </div>"""
        
        if self.description:
            html += f"""
            <div class="report-description">{self.description}</div>"""
        
        html += """
        </header>
        
        <main>
"""
        
        # Render all sections
        for section in self.sections:
            html += self._render_section(section)
        
        html += """
        </main>
    </div>
</body>
</html>"""
        
        return html
    
    def save(self, filepath: str) -> None:
        """Save HTML report to file"""
        html = self.generate()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
