#!/usr/bin/env python3
"""
HTML Report Generator
Converts analysis results into beautiful, interactive HTML reports with Chart.js
"""

from typing import Dict, List, Any
import json
import random


class HTMLReportGenerator:
    """Generate styled HTML reports from analysis data"""
    
    @staticmethod
    def get_chart_js_cdn() -> str:
        """Return Chart.js CDN script tag"""
        return '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'
    
    @staticmethod
    def get_base_styles() -> str:
        """Return base CSS styles for reports"""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 50px;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            
            h1 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 3em;
                margin-bottom: 15px;
                font-weight: 800;
                letter-spacing: -1px;
            }
            
            h2 {
                color: #667eea;
                font-size: 2em;
                margin-top: 50px;
                margin-bottom: 25px;
                border-left: 5px solid #667eea;
                padding-left: 20px;
                font-weight: 700;
            }
            
            h3 {
                color: #333;
                font-size: 1.3em;
                margin-top: 30px;
                margin-bottom: 15px;
            }
            
            .metadata {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 30px;
                font-size: 0.9em;
                color: #666;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 35px;
                border-radius: 16px;
                margin: 25px 0;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
            }
            
            .metric-card h3 {
                color: white;
                margin-top: 0;
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .metric-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .metric-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .metric-box {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 12px;
                border-left: 5px solid #667eea;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .metric-box:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            }
            
            .metric-box h4 {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .metric-box .value {
                font-size: 1.8em;
                font-weight: bold;
                color: #1a1a1a;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85em;
                letter-spacing: 1px;
            }
            
            td {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            tr:hover {
                background: #f8f9fa;
            }
            
            .alert {
                padding: 15px 20px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid;
            }
            
            .alert-success {
                background: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            
            .alert-warning {
                background: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            
            .alert-danger {
                background: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            
            .alert-info {
                background: #d1ecf1;
                border-color: #17a2b8;
                color: #0c5460;
            }
            
            .revenium-value {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin: 30px 0;
            }
            
            .revenium-value h2 {
                color: white;
                border-left-color: white;
                margin-top: 0;
            }
            
            .revenium-value h3 {
                color: white;
            }
            
            .comparison {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }
            
            .comparison-box {
                padding: 20px;
                border-radius: 5px;
            }
            
            .without-revenium {
                background: #f8d7da;
                border: 2px solid #dc3545;
            }
            
            .with-revenium {
                background: #d4edda;
                border: 2px solid #28a745;
            }
            
            .chart-bar {
                background: #e0e0e0;
                height: 30px;
                border-radius: 3px;
                margin: 10px 0;
                position: relative;
                overflow: hidden;
            }
            
            .chart-fill {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                height: 100%;
                display: flex;
                align-items: center;
                padding: 0 10px;
                color: white;
                font-weight: bold;
                font-size: 0.9em;
            }
            
            .chart-container {
                background: white;
                padding: 30px;
                border-radius: 16px;
                margin: 30px 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                position: relative;
            }
            
            .chart-container h3 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.5em;
                font-weight: 600;
            }
            
            .chart-wrapper {
                position: relative;
                height: 400px;
                margin: 20px 0;
            }
            
            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }
            
            .footer {
                margin-top: 60px;
                padding-top: 30px;
                border-top: 2px solid #e0e0e0;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }
            
            @media print {
                body {
                    background: white;
                    padding: 0;
                }
                
                .container {
                    box-shadow: none;
                    padding: 20px;
                }
                
                .metric-card, .revenium-value {
                    break-inside: avoid;
                }
            }
        </style>
        """
    
    @staticmethod
    def generate_header(title: str, subtitle: str = "", metadata: Dict[str, str] = None) -> str:
        """Generate HTML header section"""
        html = f"<h1>{title}</h1>\n"
        
        if subtitle:
            html += f"<p style='font-size: 1.2em; color: #666; margin-bottom: 20px;'>{subtitle}</p>\n"
        
        if metadata:
            html += "<div class='metadata'>\n"
            for key, value in metadata.items():
                html += f"<strong>{key}:</strong> {value} &nbsp;&nbsp;&nbsp;\n"
            html += "</div>\n"
        
        return html
    
    @staticmethod
    def generate_metric_card(title: str, value: str, subtitle: str = "") -> str:
        """Generate a prominent metric card"""
        html = "<div class='metric-card'>\n"
        html += f"<h3>{title}</h3>\n"
        html += f"<div class='metric-value'>{value}</div>\n"
        if subtitle:
            html += f"<p style='opacity: 0.9;'>{subtitle}</p>\n"
        html += "</div>\n"
        return html
    
    @staticmethod
    def generate_metric_grid(metrics: List[Dict[str, str]]) -> str:
        """Generate a grid of metric boxes"""
        html = "<div class='metric-grid'>\n"
        for metric in metrics:
            html += "<div class='metric-box'>\n"
            html += f"<h4>{metric['label']}</h4>\n"
            html += f"<div class='value'>{metric['value']}</div>\n"
            if 'subtitle' in metric:
                html += f"<p style='color: #666; font-size: 0.9em; margin-top: 5px;'>{metric['subtitle']}</p>\n"
            html += "</div>\n"
        html += "</div>\n"
        return html
    
    @staticmethod
    def generate_table(headers: List[str], rows: List[List[str]], caption: str = "") -> str:
        """Generate an HTML table"""
        html = "<table>\n"
        if caption:
            html += f"<caption style='caption-side: top; padding: 10px; font-weight: bold; text-align: left;'>{caption}</caption>\n"
        
        html += "<thead><tr>\n"
        for header in headers:
            html += f"<th>{header}</th>\n"
        html += "</tr></thead>\n"
        
        html += "<tbody>\n"
        for row in rows:
            html += "<tr>\n"
            for cell in row:
                html += f"<td>{cell}</td>\n"
            html += "</tr>\n"
        html += "</tbody>\n"
        html += "</table>\n"
        
        return html
    
    @staticmethod
    def generate_alert(message: str, alert_type: str = "info") -> str:
        """Generate an alert box"""
        return f"<div class='alert alert-{alert_type}'>{message}</div>\n"
    
    @staticmethod
    def generate_bar_chart(items: List[Dict[str, Any]], max_value: float = None) -> str:
        """Generate a simple horizontal bar chart"""
        if not max_value:
            max_value = max(item['value'] for item in items)
        
        html = "<div style='margin: 20px 0;'>\n"
        for item in items:
            percentage = (item['value'] / max_value * 100) if max_value > 0 else 0
            html += f"<div style='margin: 15px 0;'>\n"
            html += f"<div style='margin-bottom: 5px;'><strong>{item['label']}</strong></div>\n"
            html += "<div class='chart-bar'>\n"
            html += f"<div class='chart-fill' style='width: {percentage}%;'>{item['display']}</div>\n"
            html += "</div>\n"
            html += "</div>\n"
        html += "</div>\n"
        
        return html
    
    @staticmethod
    def generate_revenium_value_section(content: str) -> str:
        """Generate Revenium value proposition section"""
        return f"<div class='revenium-value'>\n{content}\n</div>\n"
    
    @staticmethod
    def generate_comparison(without: str, with_revenium: str) -> str:
        """Generate before/after comparison"""
        html = "<div class='comparison'>\n"
        html += f"<div class='comparison-box without-revenium'>\n<h3>❌ Without Revenium</h3>\n{without}\n</div>\n"
        html += f"<div class='comparison-box with-revenium'>\n<h3>✅ With Revenium</h3>\n{with_revenium}\n</div>\n"
        html += "</div>\n"
        return html
    
    @staticmethod
    def generate_chart(chart_id: str, chart_type: str, data: Dict[str, Any], title: str = "") -> str:
        """Generate a Chart.js chart with modern styling"""
        labels = json.dumps(data.get('labels', []))
        datasets = json.dumps(data.get('datasets', []))
        
        # Generate unique colors for datasets if not provided
        for dataset in data.get('datasets', []):
            if 'backgroundColor' not in dataset:
                dataset['backgroundColor'] = HTMLReportGenerator._generate_gradient_colors(len(data.get('labels', [])))
            if 'borderColor' not in dataset:
                dataset['borderColor'] = 'rgba(102, 126, 234, 1)'
        
        datasets = json.dumps(data.get('datasets', []))
        
        options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top',
                    'labels': {
                        'font': {'size': 12, 'weight': 'bold'},
                        'padding': 15,
                        'usePointStyle': True
                    }
                },
                'tooltip': {
                    'backgroundColor': 'rgba(0, 0, 0, 0.8)',
                    'padding': 12,
                    'titleFont': {'size': 14, 'weight': 'bold'},
                    'bodyFont': {'size': 13},
                    'cornerRadius': 8
                }
            },
            'scales': {}
        }
        
        if chart_type in ['bar', 'line']:
            options['scales'] = {
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': 'rgba(0, 0, 0, 0.05)'},
                    'ticks': {'font': {'size': 11}}
                },
                'x': {
                    'grid': {'display': False},
                    'ticks': {'font': {'size': 11}}
                }
            }
        
        options_json = json.dumps(options)
        
        html = f"""
        <div class="chart-container">
            {f'<h3>{title}</h3>' if title else ''}
            <div class="chart-wrapper">
                <canvas id="{chart_id}"></canvas>
            </div>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx, {{
                    type: '{chart_type}',
                    data: {{
                        labels: {labels},
                        datasets: {datasets}
                    }},
                    options: {options_json}
                }});
            }})();
        </script>
        """
        return html
    
    @staticmethod
    def _generate_gradient_colors(count: int) -> List[str]:
        """Generate gradient colors for charts"""
        colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)',
            'rgba(165, 177, 194, 0.8)',
            'rgba(52, 172, 224, 0.8)',
            'rgba(73, 219, 199, 0.8)',
            'rgba(255, 195, 113, 0.8)',
            'rgba(255, 107, 107, 0.8)'
        ]
        return colors[:count] if count <= len(colors) else colors * (count // len(colors) + 1)
    
    @staticmethod
    def wrap_html(content: str, title: str) -> str:
        """Wrap content in complete HTML document"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {HTMLReportGenerator.get_chart_js_cdn()}
    {HTMLReportGenerator.get_base_styles()}
</head>
<body>
    <div class="container">
        {content}
        <div class="footer">
            <p><strong>Generated by Revenium FinOps Showcase</strong></p>
            <p>Powered by Revenium API Intelligence Platform</p>
        </div>
    </div>
</body>
</html>
"""
