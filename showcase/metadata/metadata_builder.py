"""
Metadata Builder

Fluent API for constructing hierarchical metadata for AI calls.
"""

from typing import Dict, Any, Optional


class MetadataBuilder:
    """Fluent builder for Revenium metadata."""

    def __init__(self):
        """Initialize empty metadata."""
        self._metadata = {}

    def customer(self, customer_id: str, tier: str = 'pro') -> 'MetadataBuilder':
        """Set customer information.

        Args:
            customer_id: Unique customer identifier
            tier: Subscription tier (starter, pro, enterprise)

        Returns:
            Self for chaining
        """
        self._metadata['customer_id'] = customer_id
        self._metadata['subscription_tier'] = tier
        return self

    def organization(self, org_id: str) -> 'MetadataBuilder':
        """Set organization.

        Args:
            org_id: Organization identifier

        Returns:
            Self for chaining
        """
        self._metadata['organization_id'] = org_id
        return self

    def product(self, product_id: str) -> 'MetadataBuilder':
        """Set product.

        Args:
            product_id: Product identifier

        Returns:
            Self for chaining
        """
        self._metadata['product_id'] = product_id
        return self

    def feature(self, feature_id: str) -> 'MetadataBuilder':
        """Set feature.

        Args:
            feature_id: Feature identifier

        Returns:
            Self for chaining
        """
        self._metadata['feature_id'] = feature_id
        return self

    def environment(self, env: str = 'production') -> 'MetadataBuilder':
        """Set environment.

        Args:
            env: Environment (production, staging, development)

        Returns:
            Self for chaining
        """
        self._metadata['environment'] = env
        return self

    def region(self, region: str) -> 'MetadataBuilder':
        """Set region.

        Args:
            region: AWS region or equivalent

        Returns:
            Self for chaining
        """
        self._metadata['region'] = region
        return self

    def custom(self, key: str, value: Any) -> 'MetadataBuilder':
        """Add custom metadata field.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for chaining
        """
        self._metadata[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return metadata dictionary.

        Returns:
            Metadata dictionary
        """
        return self._metadata.copy()


# Example usage
if __name__ == '__main__':
    # Example 1: Simple metadata
    metadata = (MetadataBuilder()
                .customer('cust_0042', tier='enterprise')
                .feature('chat')
                .build())

    print("Example 1 - Simple:")
    print(metadata)
    print()

    # Example 2: Full hierarchy
    metadata = (MetadataBuilder()
                .customer('cust_0123', tier='pro')
                .organization('org_001')
                .product('product_a')
                .feature('code')
                .environment('production')
                .region('us-east-1')
                .custom('team_id', 'engineering')
                .custom('project_id', 'project_alpha')
                .build())

    print("Example 2 - Full hierarchy:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print()

    # Example 3: Use with Revenium tracker
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from instrumentation.revenium_basic import ReveniumBasicTracker

    tracker = ReveniumBasicTracker(api_key="your-api-key")

    metadata = (MetadataBuilder()
                .customer('cust_0999', tier='starter')
                .product('product_b')
                .feature('summarize')
                .environment('production')
                .build())

    call_id = tracker.track_ai_call(
        provider="anthropic",
        model="claude-sonnet-4",
        input_tokens=500,
        output_tokens=200,
        cost_usd=0.0045,
        latency_ms=2100,
        metadata=metadata
    )

    print(f"Example 3 - Tracked call: {call_id}")
