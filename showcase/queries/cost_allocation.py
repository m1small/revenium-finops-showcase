#!/usr/bin/env python3
"""
Revenium Query Pattern: Cost Allocation
Demonstrates how to query Revenium data by metadata dimensions
"""

import csv
from collections import defaultdict
from typing import Dict, List, Any


class ReveniumCostAllocationQuery:
    """
    Query patterns for cost allocation using Revenium metadata
    
    This demonstrates how to leverage Revenium's metadata-driven
    architecture to slice and dice AI costs across any dimension.
    """
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        """Initialize with data source"""
        self.data_file = data_file
        self.calls = self._load_data()
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load call data from CSV"""
        with open(self.data_file, 'r') as f:
            reader = csv.DictReader(f)
            calls = list(reader)
        
        # Convert numeric fields
        for call in calls:
            call['cost_usd'] = float(call['cost_usd'])
            call['input_tokens'] = int(call['input_tokens'])
            call['output_tokens'] = int(call['output_tokens'])
        
        return calls
    
    def query_by_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Query all costs for a specific customer
        
        Example Revenium API call:
            GET /api/v1/costs?customer_id=cust_0001
        """
        customer_calls = [c for c in self.calls if c['customer_id'] == customer_id]
        
        return {
            'customer_id': customer_id,
            'total_cost': sum(c['cost_usd'] for c in customer_calls),
            'total_calls': len(customer_calls),
            'total_tokens': sum(c['input_tokens'] + c['output_tokens'] for c in customer_calls),
            'calls': customer_calls
        }
    
    def query_by_organization(self, organization_id: str) -> Dict[str, Any]:
        """
        Query all costs for an organization
        
        Example Revenium API call:
            GET /api/v1/costs?organization_id=org_001
        """
        org_calls = [c for c in self.calls if c['organization_id'] == organization_id]
        
        # Break down by customer
        by_customer = defaultdict(lambda: {'cost': 0, 'calls': 0})
        for call in org_calls:
            by_customer[call['customer_id']]['cost'] += call['cost_usd']
            by_customer[call['customer_id']]['calls'] += 1
        
        return {
            'organization_id': organization_id,
            'total_cost': sum(c['cost_usd'] for c in org_calls),
            'total_calls': len(org_calls),
            'customers': dict(by_customer)
        }
    
    def query_by_product(self, product_id: str) -> Dict[str, Any]:
        """
        Query all costs for a product
        
        Example Revenium API call:
            GET /api/v1/costs?product_id=product_a
        """
        product_calls = [c for c in self.calls if c['product_id'] == product_id]
        
        # Break down by feature
        by_feature = defaultdict(lambda: {'cost': 0, 'calls': 0})
        for call in product_calls:
            by_feature[call['feature_id']]['cost'] += call['cost_usd']
            by_feature[call['feature_id']]['calls'] += 1
        
        return {
            'product_id': product_id,
            'total_cost': sum(c['cost_usd'] for c in product_calls),
            'total_calls': len(product_calls),
            'features': dict(by_feature)
        }
    
    def query_by_feature(self, feature_id: str) -> Dict[str, Any]:
        """
        Query all costs for a feature
        
        Example Revenium API call:
            GET /api/v1/costs?feature_id=chat
        """
        feature_calls = [c for c in self.calls if c['feature_id'] == feature_id]
        
        # Break down by model
        by_model = defaultdict(lambda: {'cost': 0, 'calls': 0})
        for call in feature_calls:
            by_model[call['model']]['cost'] += call['cost_usd']
            by_model[call['model']]['calls'] += 1
        
        return {
            'feature_id': feature_id,
            'total_cost': sum(c['cost_usd'] for c in feature_calls),
            'total_calls': len(feature_calls),
            'models': dict(by_model)
        }
    
    def query_multi_dimensional(
        self,
        organization_id: str = None,
        product_id: str = None,
        customer_id: str = None,
        feature_id: str = None,
        subscription_tier: str = None
    ) -> Dict[str, Any]:
        """
        Multi-dimensional query across any combination of metadata
        
        Example Revenium API call:
            GET /api/v1/costs?organization_id=org_001&product_id=product_a&tier=pro
        """
        filtered_calls = self.calls
        
        if organization_id:
            filtered_calls = [c for c in filtered_calls if c['organization_id'] == organization_id]
        if product_id:
            filtered_calls = [c for c in filtered_calls if c['product_id'] == product_id]
        if customer_id:
            filtered_calls = [c for c in filtered_calls if c['customer_id'] == customer_id]
        if feature_id:
            filtered_calls = [c for c in filtered_calls if c['feature_id'] == feature_id]
        if subscription_tier:
            filtered_calls = [c for c in filtered_calls if c['subscription_tier'] == subscription_tier]
        
        return {
            'filters': {
                'organization_id': organization_id,
                'product_id': product_id,
                'customer_id': customer_id,
                'feature_id': feature_id,
                'subscription_tier': subscription_tier
            },
            'total_cost': sum(c['cost_usd'] for c in filtered_calls),
            'total_calls': len(filtered_calls),
            'avg_cost_per_call': sum(c['cost_usd'] for c in filtered_calls) / len(filtered_calls) if filtered_calls else 0
        }


def example_usage():
    """Demonstrate query patterns"""
    
    print("=" * 70)
    print("🔍 REVENIUM QUERY PATTERNS: COST ALLOCATION")
    print("=" * 70)
    print()
    
    # Initialize query engine
    query = ReveniumCostAllocationQuery('data/simulated_calls.csv')
    
    print("📊 EXAMPLE 1: Query by Customer")
    print("-" * 70)
    result = query.query_by_customer('cust_0001')
    print(f"Customer: {result['customer_id']}")
    print(f"Total Cost: ${result['total_cost']:.2f}")
    print(f"Total Calls: {result['total_calls']:,}")
    print(f"Total Tokens: {result['total_tokens']:,}")
    print()
    
    print("📊 EXAMPLE 2: Query by Organization")
    print("-" * 70)
    result = query.query_by_organization('org_001')
    print(f"Organization: {result['organization_id']}")
    print(f"Total Cost: ${result['total_cost']:.2f}")
    print(f"Total Calls: {result['total_calls']:,}")
    print(f"Customers: {len(result['customers'])}")
    print()
    
    print("📊 EXAMPLE 3: Query by Product")
    print("-" * 70)
    result = query.query_by_product('product_a')
    print(f"Product: {result['product_id']}")
    print(f"Total Cost: ${result['total_cost']:.2f}")
    print(f"Total Calls: {result['total_calls']:,}")
    print(f"Features: {len(result['features'])}")
    for feature, data in list(result['features'].items())[:3]:
        print(f"  - {feature}: ${data['cost']:.2f} ({data['calls']:,} calls)")
    print()
    
    print("📊 EXAMPLE 4: Multi-Dimensional Query")
    print("-" * 70)
    result = query.query_multi_dimensional(
        organization_id='org_001',
        product_id='product_a',
        subscription_tier='pro'
    )
    print(f"Filters: {result['filters']}")
    print(f"Total Cost: ${result['total_cost']:.2f}")
    print(f"Total Calls: {result['total_calls']:,}")
    print(f"Avg Cost/Call: ${result['avg_cost_per_call']:.4f}")
    print()
    
    print("=" * 70)
    print("💡 KEY BENEFITS OF REVENIUM METADATA")
    print("=" * 70)
    print()
    print("✅ Query by ANY metadata dimension")
    print("✅ Combine multiple filters for precise analysis")
    print("✅ Real-time cost visibility")
    print("✅ No complex ETL or data warehousing")
    print("✅ Consistent schema across all AI providers")
    print()
    print("=" * 70)


if __name__ == '__main__':
    example_usage()
