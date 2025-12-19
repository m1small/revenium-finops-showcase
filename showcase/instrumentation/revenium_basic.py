#!/usr/bin/env python3
"""
Revenium Basic Instrumentation Example
Demonstrates the simplest way to integrate Revenium tracking
"""

from typing import Dict, Any
import time
import uuid


class ReveniumBasicTracker:
    """
    Basic Revenium integration pattern
    
    This example shows the minimal code needed to track AI API calls
    with Revenium metadata for cost allocation and analysis.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Revenium tracker
        
        Args:
            api_key: Your Revenium API key
        """
        self.api_key = api_key
        self.endpoint = "https://api.revenium.io/v1/track"
    
    def track_ai_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Track an AI API call with Revenium
        
        Args:
            provider: AI provider (openai, anthropic, bedrock)
            model: Model name (gpt-4, claude-sonnet-4, etc)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            metadata: Additional metadata for cost allocation
            
        Returns:
            call_id: Unique identifier for this call
        """
        call_id = str(uuid.uuid4())
        
        # Build tracking payload
        payload = {
            'call_id': call_id,
            'timestamp': time.time(),
            'provider': provider,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost_usd,
            'latency_ms': latency_ms,
            'metadata': metadata
        }
        
        # In production, this would send to Revenium API
        # For demo purposes, we'll just print
        print(f"✅ Tracked AI call: {call_id}")
        print(f"   Provider: {provider}, Model: {model}")
        print(f"   Cost: ${cost_usd:.4f}, Tokens: {input_tokens + output_tokens}")
        print(f"   Metadata: {metadata}")
        
        return call_id


def example_usage():
    """Example: Track a simple AI call"""
    
    # Initialize tracker
    tracker = ReveniumBasicTracker(api_key="your-api-key-here")
    
    # Track an AI call with metadata
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
            'subscription_tier': 'pro',
            'environment': 'production'
        }
    )
    
    print(f"\n📊 Call tracked with ID: {call_id}")
    print("\n💡 Key Benefits:")
    print("   ✅ Automatic cost tracking across all AI providers")
    print("   ✅ Real-time visibility into AI spending")
    print("   ✅ Multi-dimensional cost allocation")
    print("   ✅ Customer profitability analysis")


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 REVENIUM BASIC INSTRUMENTATION EXAMPLE")
    print("=" * 70)
    print()
    
    example_usage()
    
    print()
    print("=" * 70)
    print("📚 Next Steps:")
    print("   1. See revenium_async.py for fire-and-forget pattern")
    print("   2. See revenium_metadata.py for advanced metadata strategies")
    print("   3. See revenium_error_handling.py for production error handling")
    print("=" * 70)
