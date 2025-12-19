#!/usr/bin/env python3
"""
Revenium Implementation Simulator
Simulates the dual-track architecture locally without external dependencies
"""

import time
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict
import threading
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

class AICall:
    """Simulates an AI API call"""
    def __init__(self, provider: str, model: str, customer_id: str):
        self.timestamp = datetime.now()
        self.provider = provider
        self.model = model
        self.customer_id = customer_id
        self.input_tokens = random.randint(50, 500)
        self.output_tokens = random.randint(100, 1000)
        self.latency_ms = random.uniform(200, 800)
        self.cost_usd = self.calculate_cost()
        
    def calculate_cost(self) -> float:
        """Calculate cost based on tokens"""
        # Simplified pricing
        input_cost = self.input_tokens * 0.000003
        output_cost = self.output_tokens * 0.000015
        return round(input_cost + output_cost, 6)

class ReveniumMiddleware:
    """Simulates Revenium middleware tracking"""
    def __init__(self):
        self.calls: List[AICall] = []
        self.uptime = 100.0
        self.failure_rate = 0.0  # Can be adjusted to simulate failures
        
    def track(self, call: AICall) -> bool:
        """Track an AI call (async simulation)"""
        # Simulate occasional tracking failures
        if random.random() < self.failure_rate:
            return False
        
        # Add artificial delay to simulate async processing
        time.sleep(0.001)
        
        # Simulate middleware adding latency
        call.latency_ms += random.uniform(5, 30)
        
        self.calls.append(call)
        return True
    
    def get_stats(self) -> Dict:
        """Get Revenium statistics"""
        if not self.calls:
            return {"total_calls": 0, "total_cost": 0, "avg_latency": 0}
        
        return {
            "total_calls": len(self.calls),
            "total_cost": sum(c.cost_usd for c in self.calls),
            "avg_latency": sum(c.latency_ms for c in self.calls) / len(self.calls),
            "by_customer": self._group_by_customer()
        }
    
    def _group_by_customer(self) -> Dict:
        """Group costs by customer"""
        customer_data = defaultdict(lambda: {"calls": 0, "cost": 0.0})
        for call in self.calls:
            customer_data[call.customer_id]["calls"] += 1
            customer_data[call.customer_id]["cost"] += call.cost_usd
        return dict(customer_data)

class CloudWatchMetrics:
    """Simulates CloudWatch metrics collection"""
    def __init__(self):
        self.calls: List[AICall] = []
        
    def log(self, call: AICall):
        """Log AI call to CloudWatch"""
        # Simulate CloudWatch always capturing calls
        self.calls.append(call)
    
    def get_stats(self) -> Dict:
        """Get CloudWatch statistics"""
        if not self.calls:
            return {"total_calls": 0, "total_cost": 0}
        
        return {
            "total_calls": len(self.calls),
            "total_cost": sum(c.cost_usd for c in self.calls),
            "by_provider": self._group_by_provider()
        }
    
    def _group_by_provider(self) -> Dict:
        """Group by provider"""
        provider_data = defaultdict(lambda: {"calls": 0, "cost": 0.0})
        for call in self.calls:
            provider_data[call.provider]["calls"] += 1
            provider_data[call.provider]["cost"] += call.cost_usd
        return dict(provider_data)

class Reconciliation:
    """Simulates weekly reconciliation between Revenium and CloudWatch"""
    @staticmethod
    def reconcile(revenium: ReveniumMiddleware, cloudwatch: CloudWatchMetrics) -> Dict:
        """Perform reconciliation"""
        rev_stats = revenium.get_stats()
        cw_stats = cloudwatch.get_stats()
        
        rev_calls = rev_stats.get("total_calls", 0)
        cw_calls = cw_stats.get("total_calls", 0)
        
        if cw_calls == 0:
            variance = 0.0
        else:
            variance = abs(rev_calls - cw_calls) / cw_calls * 100
        
        status = "PASS" if variance < 2.0 else "FAIL"
        
        return {
            "revenium_calls": rev_calls,
            "cloudwatch_calls": cw_calls,
            "variance_pct": round(variance, 2),
            "status": status,
            "revenium_cost": rev_stats.get("total_cost", 0),
            "cloudwatch_cost": cw_stats.get("total_cost", 0)
        }

class Simulator:
    """Main simulator orchestrating all components"""
    def __init__(self):
        self.revenium = ReveniumMiddleware()
        self.cloudwatch = CloudWatchMetrics()
        self.reconciliation = Reconciliation()
        self.running = False
        self.call_count = 0
        
    def simulate_ai_call(self):
        """Simulate a single AI API call"""
        providers = ["openai", "anthropic", "bedrock"]
        models = {
            "openai": ["gpt-4", "gpt-4-turbo"],
            "anthropic": ["claude-sonnet-4", "claude-opus-4"],
            "bedrock": ["claude-instant", "claude-v2"]
        }
        customers = ["cust_001", "cust_002", "cust_003", "cust_004", "cust_005"]
        
        provider = random.choice(providers)
        model = random.choice(models[provider])
        customer = random.choice(customers)
        
        call = AICall(provider, model, customer)
        
        # Always log to CloudWatch (100% coverage)
        self.cloudwatch.log(call)
        
        # Revenium may miss some calls
        revenium_tracked = self.revenium.track(call)
        
        self.call_count += 1
        
        return call, revenium_tracked
    
    def run_simulation(self, duration_seconds: int = 30, calls_per_second: int = 5):
        """Run simulation for specified duration"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}Revenium Implementation Simulator{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Configuration:{Colors.END}")
        print(f"  Duration: {duration_seconds} seconds")
        print(f"  Rate: {calls_per_second} calls/second")
        print(f"  Revenium failure rate: {self.revenium.failure_rate*100}%\n")
        
        print(f"{Colors.YELLOW}Starting simulation...{Colors.END}\n")
        
        self.running = True
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_seconds:
                for _ in range(calls_per_second):
                    call, tracked = self.simulate_ai_call()
                    
                    # Print every 10th call
                    if self.call_count % 10 == 0:
                        status = f"{Colors.GREEN}✓ Tracked{Colors.END}" if tracked else f"{Colors.RED}✗ Missed{Colors.END}"
                        print(f"Call #{self.call_count}: {call.provider}/{call.model} "
                              f"→ ${call.cost_usd:.6f} ({call.input_tokens}→{call.output_tokens} tokens) "
                              f"[{status}]")
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Simulation interrupted by user{Colors.END}\n")
        
        self.running = False
        self.print_results()
    
    def print_results(self):
        """Print simulation results"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}Simulation Results{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        # Revenium stats
        rev_stats = self.revenium.get_stats()
        print(f"{Colors.BOLD}{Colors.MAGENTA}Revenium Middleware:{Colors.END}")
        print(f"  Total Calls Tracked: {rev_stats['total_calls']}")
        print(f"  Total Cost: ${rev_stats['total_cost']:.4f}")
        print(f"  Average Latency: {rev_stats.get('avg_latency', 0):.2f}ms")
        
        if rev_stats['total_calls'] > 0:
            print(f"\n  {Colors.CYAN}Cost by Customer:{Colors.END}")
            for customer, data in rev_stats.get('by_customer', {}).items():
                print(f"    {customer}: {data['calls']} calls, ${data['cost']:.4f}")
        
        # CloudWatch stats
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}CloudWatch Metrics:{Colors.END}")
        cw_stats = self.cloudwatch.get_stats()
        print(f"  Total Calls Logged: {cw_stats['total_calls']}")
        print(f"  Total Cost: ${cw_stats['total_cost']:.4f}")
        
        if cw_stats['total_calls'] > 0:
            print(f"\n  {Colors.CYAN}Cost by Provider:{Colors.END}")
            for provider, data in cw_stats.get('by_provider', {}).items():
                print(f"    {provider}: {data['calls']} calls, ${data['cost']:.4f}")
        
        # Reconciliation
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Reconciliation Report:{Colors.END}")
        report = self.reconciliation.reconcile(self.revenium, self.cloudwatch)
        
        variance_color = Colors.GREEN if report['status'] == 'PASS' else Colors.RED
        print(f"  Revenium Calls: {report['revenium_calls']}")
        print(f"  CloudWatch Calls: {report['cloudwatch_calls']}")
        print(f"  Variance: {variance_color}{report['variance_pct']:.2f}%{Colors.END}")
        print(f"  Status: {variance_color}{report['status']}{Colors.END}")
        
        # Performance metrics
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Performance Metrics:{Colors.END}")
        avg_latency = rev_stats.get('avg_latency', 0)
        latency_status = Colors.GREEN if avg_latency < 50 else Colors.YELLOW if avg_latency < 100 else Colors.RED
        print(f"  Average Latency: {latency_status}{avg_latency:.2f}ms{Colors.END} (target: <50ms)")
        
        tracking_rate = (report['revenium_calls'] / report['cloudwatch_calls'] * 100) if report['cloudwatch_calls'] > 0 else 0
        tracking_color = Colors.GREEN if tracking_rate > 98 else Colors.YELLOW if tracking_rate > 95 else Colors.RED
        print(f"  Tracking Rate: {tracking_color}{tracking_rate:.2f}%{Colors.END} (target: >98%)")
        
        # Overall assessment
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Overall Assessment:{Colors.END}")
        
        issues = []
        if report['variance_pct'] >= 2.0:
            issues.append(f"{Colors.RED}✗ Data variance exceeds 2% threshold{Colors.END}")
        if avg_latency >= 50:
            issues.append(f"{Colors.YELLOW}⚠ Latency approaching/exceeding 50ms target{Colors.END}")
        if tracking_rate < 98:
            issues.append(f"{Colors.YELLOW}⚠ Tracking rate below 98% target{Colors.END}")
        
        if issues:
            print(f"\n{Colors.YELLOW}Issues Detected:{Colors.END}")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n{Colors.GREEN}✓ All metrics within acceptable ranges{Colors.END}")
        
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def main():
    """Main entry point"""
    print(f"\n{Colors.CYAN}Revenium Local Simulator{Colors.END}")
    print(f"{Colors.CYAN}This simulates the dual-track architecture locally{Colors.END}\n")
    
    # Create simulator
    sim = Simulator()
    
    # Optionally add some failure rate to demonstrate variance
    # sim.revenium.failure_rate = 0.03  # 3% failure rate
    
    # Run simulation
    try:
        sim.run_simulation(duration_seconds=30, calls_per_second=5)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")

if __name__ == "__main__":
    main()
