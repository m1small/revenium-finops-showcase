"""
Basic Revenium Instrumentation

Simple SDK for tracking AI API calls with comprehensive metadata.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional


class ReveniumBasicTracker:
    """Basic Revenium tracking for AI API calls."""

    def __init__(self, api_key: str, endpoint: str = "https://api.revenium.io/v1/calls"):
        """Initialize the tracker.

        Args:
            api_key: Revenium API key
            endpoint: Revenium API endpoint
        """
        self.api_key = api_key
        self.endpoint = endpoint

    def track_ai_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track an AI API call.

        Args:
            provider: AI provider (e.g., 'openai', 'anthropic')
            model: Model name (e.g., 'gpt-4', 'claude-sonnet-4')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            metadata: Optional metadata dictionary

        Returns:
            Call ID
        """
        call_id = str(uuid.uuid4())

        # Prepare payload
        payload = {
            'call_id': call_id,
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost_usd': cost_usd,
            'latency_ms': latency_ms,
            'status': 'success'
        }

        # Add metadata if provided
        if metadata:
            payload.update({
                'customer_id': metadata.get('customer_id'),
                'organization_id': metadata.get('organization_id'),
                'product_id': metadata.get('product_id'),
                'feature_id': metadata.get('feature_id'),
                'subscription_tier': metadata.get('subscription_tier'),
                'environment': metadata.get('environment', 'production'),
                'region': metadata.get('region', 'us-east-1')
            })

        # In production, this would make an HTTP POST to Revenium API
        # For showcase: print call data
        print(f"[Revenium] Tracked call {call_id}: {provider}/{model} - ${cost_usd:.4f}")

        return call_id


# Example usage
if __name__ == '__main__':
    tracker = ReveniumBasicTracker(api_key="your-api-key")

    # Track OpenAI call
    call_id = tracker.track_ai_call(
        provider="openai",
        model="gpt-4",
        input_tokens=150,
        output_tokens=300,
        cost_usd=0.0135,
        latency_ms=1250,
        metadata={
            'customer_id': 'cust_0001',
            'organization_id': 'org_001',
            'product_id': 'product_a',
            'feature_id': 'chat',
            'subscription_tier': 'pro'
        }
    )

    print(f"Call tracked with ID: {call_id}")
