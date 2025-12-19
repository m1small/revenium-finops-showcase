#!/usr/bin/env python3
"""
Revenium Metadata Builder Library
Provides fluent API for building consistent metadata across your application
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ReveniumMetadata:
    """Structured metadata for Revenium tracking"""
    
    # Core identifiers
    customer_id: str
    organization_id: str
    
    # Product context
    product_id: Optional[str] = None
    feature_id: Optional[str] = None
    
    # Business context
    subscription_tier: Optional[str] = None
    task_type: Optional[str] = None
    
    # Technical context
    environment: str = 'production'
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Custom fields
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API submission"""
        data = asdict(self)
        # Merge custom fields into top level
        custom = data.pop('custom', {})
        data.update(custom)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


class ReveniumMetadataBuilder:
    """
    Fluent API for building Revenium metadata
    
    Example:
        metadata = (ReveniumMetadataBuilder()
            .customer('cust_0001')
            .organization('org_001')
            .product('product_a')
            .feature('chat')
            .tier('pro')
            .environment('production')
            .build())
    """
    
    def __init__(self):
        self._customer_id: Optional[str] = None
        self._organization_id: Optional[str] = None
        self._product_id: Optional[str] = None
        self._feature_id: Optional[str] = None
        self._subscription_tier: Optional[str] = None
        self._task_type: Optional[str] = None
        self._environment: str = 'production'
        self._request_id: Optional[str] = None
        self._trace_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._user_agent: Optional[str] = None
        self._custom: Dict[str, Any] = {}
    
    def customer(self, customer_id: str) -> 'ReveniumMetadataBuilder':
        """Set customer ID"""
        self._customer_id = customer_id
        return self
    
    def organization(self, organization_id: str) -> 'ReveniumMetadataBuilder':
        """Set organization ID"""
        self._organization_id = organization_id
        return self
    
    def product(self, product_id: str) -> 'ReveniumMetadataBuilder':
        """Set product ID"""
        self._product_id = product_id
        return self
    
    def feature(self, feature_id: str) -> 'ReveniumMetadataBuilder':
        """Set feature ID"""
        self._feature_id = feature_id
        return self
    
    def tier(self, subscription_tier: str) -> 'ReveniumMetadataBuilder':
        """Set subscription tier"""
        self._subscription_tier = subscription_tier
        return self
    
    def task(self, task_type: str) -> 'ReveniumMetadataBuilder':
        """Set task type"""
        self._task_type = task_type
        return self
    
    def environment(self, environment: str) -> 'ReveniumMetadataBuilder':
        """Set environment (production, staging, development)"""
        self._environment = environment
        return self
    
    def request(self, request_id: str) -> 'ReveniumMetadataBuilder':
        """Set request ID"""
        self._request_id = request_id
        return self
    
    def trace(self, trace_id: str) -> 'ReveniumMetadataBuilder':
        """Set trace ID for distributed tracing"""
        self._trace_id = trace_id
        return self
    
    def session(self, session_id: str) -> 'ReveniumMetadataBuilder':
        """Set session ID"""
        self._session_id = session_id
        return self
    
    def user_agent(self, user_agent: str) -> 'ReveniumMetadataBuilder':
        """Set user agent"""
        self._user_agent = user_agent
        return self
    
    def custom_field(self, key: str, value: Any) -> 'ReveniumMetadataBuilder':
        """Add custom metadata field"""
        self._custom[key] = value
        return self
    
    def build(self) -> ReveniumMetadata:
        """Build the metadata object"""
        if not self._customer_id:
            raise ValueError("customer_id is required")
        if not self._organization_id:
            raise ValueError("organization_id is required")
        
        return ReveniumMetadata(
            customer_id=self._customer_id,
            organization_id=self._organization_id,
            product_id=self._product_id,
            feature_id=self._feature_id,
            subscription_tier=self._subscription_tier,
            task_type=self._task_type,
            environment=self._environment,
            request_id=self._request_id,
            trace_id=self._trace_id,
            session_id=self._session_id,
            user_agent=self._user_agent,
            custom=self._custom
        )


class HierarchicalTagger:
    """
    Hierarchical metadata tagger for consistent org → product → customer → feature tagging
    
    Example:
        tagger = HierarchicalTagger(
            organization_id='org_001',
            product_id='product_a'
        )
        
        metadata = tagger.tag_for_customer(
            customer_id='cust_0001',
            feature_id='chat',
            tier='pro'
        )
    """
    
    def __init__(self, organization_id: str, product_id: str):
        self.organization_id = organization_id
        self.product_id = product_id
    
    def tag_for_customer(
        self,
        customer_id: str,
        feature_id: str,
        tier: str,
        **kwargs
    ) -> ReveniumMetadata:
        """
        Create metadata for a customer interaction
        
        Args:
            customer_id: Customer identifier
            feature_id: Feature being used
            tier: Subscription tier
            **kwargs: Additional metadata fields
        """
        builder = (ReveniumMetadataBuilder()
            .organization(self.organization_id)
            .product(self.product_id)
            .customer(customer_id)
            .feature(feature_id)
            .tier(tier))
        
        # Add any additional fields
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
            else:
                builder.custom_field(key, value)
        
        return builder.build()


def example_usage():
    """Demonstrate metadata builder usage"""
    
    print("=" * 70)
    print("📋 EXAMPLE 1: Basic Metadata Builder")
    print("=" * 70)
    
    # Build metadata using fluent API
    metadata = (ReveniumMetadataBuilder()
        .customer('cust_0001')
        .organization('org_001')
        .product('product_a')
        .feature('chat')
        .tier('pro')
        .task('chat')
        .environment('production')
        .build())
    
    print("\nBuilt metadata:")
    for key, value in metadata.to_dict().items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 2: Hierarchical Tagger")
    print("=" * 70)
    
    # Use hierarchical tagger for consistent tagging
    tagger = HierarchicalTagger(
        organization_id='org_001',
        product_id='product_a'
    )
    
    metadata = tagger.tag_for_customer(
        customer_id='cust_0001',
        feature_id='chat',
        tier='pro',
        task_type='chat',
        session_id='sess_12345'
    )
    
    print("\nTagged metadata:")
    for key, value in metadata.to_dict().items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 3: Custom Fields")
    print("=" * 70)
    
    # Add custom fields for specific use cases
    metadata = (ReveniumMetadataBuilder()
        .customer('cust_0001')
        .organization('org_001')
        .custom_field('campaign_id', 'summer_2024')
        .custom_field('ab_test_variant', 'variant_b')
        .custom_field('user_segment', 'power_user')
        .build())
    
    print("\nMetadata with custom fields:")
    for key, value in metadata.to_dict().items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("💡 Key Benefits:")
    print("   ✅ Type-safe metadata construction")
    print("   ✅ Consistent tagging across application")
    print("   ✅ Hierarchical organization structure")
    print("   ✅ Flexible custom fields")
    print("   ✅ Validation at build time")
    print("=" * 70)


if __name__ == '__main__':
    example_usage()
