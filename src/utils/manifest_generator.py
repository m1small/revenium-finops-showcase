#!/usr/bin/env python3
"""
Manifest Generator - Creates manifest.json for report viewer
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any


class ManifestGenerator:
    """Generate manifest file for HTML reports"""
    
    def __init__(self):
        self.reports = []
        self.generated = datetime.now().isoformat()
    
    def add_report(self, 
                   report_id: str,
                   category: str,
                   title: str,
                   description: str,
                   filename: str,
                   metrics: Dict[str, Any] = None) -> None:
        """Add a report to the manifest
        
        Args:
            report_id: Unique identifier (e.g., 'finops-understanding')
            category: 'finops' or 'ubr'
            title: Display title
            description: Short description
            filename: HTML filename
            metrics: Optional dict of key metrics
        """
        report = {
            'id': report_id,
            'category': category,
            'title': title,
            'description': description,
            'file': filename,
            'generated': datetime.now().isoformat()
        }
        
        if metrics:
            report['metrics'] = metrics
        
        self.reports.append(report)
    
    def generate(self) -> Dict:
        """Generate manifest dictionary"""
        return {
            'generated': self.generated,
            'reports': self.reports
        }
    
    def save(self, filepath: str = 'reports/html/manifest.json') -> None:
        """Save manifest to JSON file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        manifest = self.generate()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Manifest generated: {filepath}")


def create_default_manifest():
    """Create a default manifest with all expected reports"""
    manifest = ManifestGenerator()
    
    # FinOps Domain Reports
    manifest.add_report(
        report_id='finops-understanding',
        category='finops',
        title='Understanding Usage & Cost',
        description='Cost allocation, spend breakdowns, and forecasting',
        filename='finops_understanding.html'
    )
    
    manifest.add_report(
        report_id='finops-performance',
        category='finops',
        title='Performance Tracking',
        description='Model efficiency and latency analysis',
        filename='finops_performance.html'
    )
    
    manifest.add_report(
        report_id='finops-realtime',
        category='finops',
        title='Real-Time Decision Making',
        description='Anomaly detection and immediate optimizations',
        filename='finops_realtime.html'
    )
    
    manifest.add_report(
        report_id='finops-optimization',
        category='finops',
        title='Rate Optimization',
        description='Reserved capacity and model switching opportunities',
        filename='finops_optimization.html'
    )
    
    manifest.add_report(
        report_id='finops-alignment',
        category='finops',
        title='Organizational Alignment',
        description='Cost tracking and chargeback reports',
        filename='finops_alignment.html'
    )
    
    # Usage-Based Revenue Reports
    manifest.add_report(
        report_id='ubr-profitability',
        category='ubr',
        title='Customer Profitability',
        description='Margin analysis and customer lifetime value',
        filename='customer_profitability.html'
    )
    
    manifest.add_report(
        report_id='ubr-pricing',
        category='ubr',
        title='Pricing Strategy',
        description='Pricing model comparison and recommendations',
        filename='pricing_strategy.html'
    )
    
    manifest.add_report(
        report_id='ubr-features',
        category='ubr',
        title='Feature Economics',
        description='Feature profitability and investment recommendations',
        filename='feature_economics.html'
    )
    
    return manifest


if __name__ == '__main__':
    manifest = create_default_manifest()
    manifest.save()
