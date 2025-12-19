#!/usr/bin/env python3
"""
HTML Report Generator
Converts analysis results into beautiful, interactive HTML reports
"""

from typing import Dict, List, Any
import json


class HTMLReportGenerator:
    """Generate styled HTML reports from analysis data"""
    
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
                background: #f5f5f5;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            h1 {
                color: #1a1a1a;
                font-size: 2.5em;
                margin-bottom: 10px;
                border-bottom: 3px solid #0066cc;
                padding-bottom: 10px;
            }
            
            h2 {
                color: #0066cc;
                font-size: 1.8em;
                margin-top: 40px;
                margin-bottom: 20px;
                border-left: 4px solid #0066cc;
                padding-left: 15px;
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
                padding: 25px;
                border-radius: 8px;
                margin: 20px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                border-left: 4px solid #0066cc;
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
                background: #0066cc;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85em;
                letter-spacing: 0.5px;
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
            
            .footer {
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
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
    def wrap_html(content: str, title: str) -> str:
        """Wrap content in complete HTML document"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {HTMLReportGenerator.get_base_styles()}
</head>
<body>
    <div class="container">
        {content}
        <div class="footer">
            <p>Generated by Revenium FinOps Showcase</p>
            <p>Powered by Revenium API Intelligence Platform</p>
        </div>
    </div>
</body>
</html>
"""
