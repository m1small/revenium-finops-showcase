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
    
    def print_educational_header(self):
        """Print educational context before simulation starts"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}How This Works:{Colors.END}")
        print(f"  1. {Colors.CYAN}AI API calls{Colors.END} are made to various providers")
        print(f"  2. {Colors.MAGENTA}Revenium middleware{Colors.END} tracks calls for billing")
        print(f"  3. {Colors.MAGENTA}CloudWatch{Colors.END} independently logs all calls")
        print(f"  4. {Colors.GREEN}Reconciliation{Colors.END} compares both systems weekly")
        print(f"\n{Colors.BOLD}Watch for:{Colors.END}")
        print(f"  • {Colors.GREEN}✓ Tracked{Colors.END} = Revenium successfully captured the call")
        print(f"  • {Colors.RED}✗ Missed{Colors.END} = Revenium failed (CloudWatch still has it)")
        print(f"  • Variance should stay under 2% for accurate billing\n")
        
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
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        
        self.print_educational_header()
        
        print(f"{Colors.CYAN}Configuration:{Colors.END}")
        print(f"  Duration: {duration_seconds} seconds")
        print(f"  Rate: {calls_per_second} calls/second")
        print(f"  Revenium failure rate: {self.revenium.failure_rate*100}%")
        
        if self.revenium.failure_rate > 0:
            print(f"\n{Colors.YELLOW}Note: Failure rate is set to {self.revenium.failure_rate*100}%")
            print(f"This simulates real-world scenarios where middleware might miss calls{Colors.END}")
        
        print(f"\n{Colors.YELLOW}Starting simulation...{Colors.END}\n")
        
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
    
    def print_insights(self, report: Dict):
        """Print educational insights based on simulation results"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}What This Means{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        variance = report['variance_pct']
        rev_calls = report['revenium_calls']
        cw_calls = report['cloudwatch_calls']
        
        # Variance insights
        if variance < 1.0:
            print(f"{Colors.GREEN}✓ Excellent Tracking:{Colors.END}")
            print(f"  Variance of {variance:.2f}% is well within acceptable limits.")
            print(f"  Revenium is accurately capturing nearly all AI API calls.")
        elif variance < 2.0:
            print(f"{Colors.GREEN}✓ Good Tracking:{Colors.END}")
            print(f"  Variance of {variance:.2f}% is acceptable (under 2% threshold).")
            print(f"  Minor discrepancies are normal in distributed systems.")
        else:
            print(f"{Colors.RED}⚠ High Variance:{Colors.END}")
            print(f"  Variance of {variance:.2f}% exceeds the 2% threshold.")
            print(f"  This would trigger investigation in production.")
            print(f"\n  {Colors.YELLOW}Possible causes:{Colors.END}")
            print(f"    • Middleware performance issues")
            print(f"    • Network connectivity problems")
            print(f"    • High system load")
        
        # Dual-track value
        print(f"\n{Colors.BOLD}Why Dual-Track Matters:{Colors.END}")
        missed_calls = cw_calls - rev_calls
        if missed_calls > 0:
            missed_cost = (report['cloudwatch_cost'] - report['revenium_cost'])
            print(f"  • Revenium missed {missed_calls} calls (${missed_cost:.4f})")
            print(f"  • CloudWatch caught them all - no revenue lost!")
            print(f"  • Weekly reconciliation ensures accurate billing")
        else:
            print(f"  • Perfect tracking - both systems agree")
            print(f"  • CloudWatch provides validation and backup")
            print(f"  • Confidence in billing accuracy")
        
        # Best practices
        print(f"\n{Colors.BOLD}Production Best Practices:{Colors.END}")
        print(f"  1. Monitor variance trends over time")
        print(f"  2. Set alerts for variance > 2%")
        print(f"  3. Run reconciliation weekly")
        print(f"  4. Investigate any sustained high variance")
        print(f"  5. Use CloudWatch data for billing disputes")
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    def print_best_practice_report(self, report: Dict, rev_stats: Dict):
        """Print a sample best practice report"""
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}Sample Best Practice Report{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.BOLD}Weekly Reconciliation Report{Colors.END}")
        print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Period: Week of {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}\n")
        
        # Executive Summary
        print(f"{Colors.BOLD}{Colors.MAGENTA}Executive Summary:{Colors.END}")
        status_icon = "✓" if report['status'] == 'PASS' else "✗"
        status_color = Colors.GREEN if report['status'] == 'PASS' else Colors.RED
        print(f"  Status: {status_color}{status_icon} {report['status']}{Colors.END}")
        print(f"  Variance: {report['variance_pct']:.2f}% (threshold: 2.0%)")
        print(f"  Total API Calls: {report['cloudwatch_calls']:,}")
        print(f"  Total Cost: ${report['cloudwatch_cost']:.2f}")
        
        # Tracking Accuracy
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Tracking Accuracy:{Colors.END}")
        tracking_rate = (report['revenium_calls'] / report['cloudwatch_calls'] * 100) if report['cloudwatch_calls'] > 0 else 0
        print(f"  Revenium Captured: {report['revenium_calls']:,} calls ({tracking_rate:.2f}%)")
        print(f"  CloudWatch Logged: {report['cloudwatch_calls']:,} calls (100%)")
        print(f"  Missed Calls: {report['cloudwatch_calls'] - report['revenium_calls']:,}")
        
        # Financial Impact
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Financial Impact:{Colors.END}")
        cost_diff = report['cloudwatch_cost'] - report['revenium_cost']
        print(f"  Revenium Tracked Cost: ${report['revenium_cost']:.2f}")
        print(f"  CloudWatch Total Cost: ${report['cloudwatch_cost']:.2f}")
        if cost_diff > 0:
            print(f"  {Colors.YELLOW}Potential Revenue Gap: ${cost_diff:.2f}{Colors.END}")
            print(f"  {Colors.GREEN}Protected by CloudWatch backup{Colors.END}")
        else:
            print(f"  {Colors.GREEN}No revenue gap detected{Colors.END}")
        
        # Performance Metrics
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Performance Metrics:{Colors.END}")
        avg_latency = rev_stats.get('avg_latency', 0)
        print(f"  Average Latency: {avg_latency:.2f}ms (target: <50ms)")
        latency_status = "✓ Within target" if avg_latency < 50 else "⚠ Above target"
        latency_color = Colors.GREEN if avg_latency < 50 else Colors.YELLOW
        print(f"  Latency Status: {latency_color}{latency_status}{Colors.END}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Recommendations:{Colors.END}")
        if report['variance_pct'] >= 2.0:
            print(f"  {Colors.RED}• URGENT: Investigate high variance{Colors.END}")
            print(f"    - Review Revenium middleware logs")
            print(f"    - Check system resource utilization")
            print(f"    - Verify network connectivity")
        elif report['variance_pct'] >= 1.0:
            print(f"  {Colors.YELLOW}• Monitor variance trend{Colors.END}")
            print(f"    - Track daily variance for patterns")
        else:
            print(f"  {Colors.GREEN}• Continue current monitoring{Colors.END}")
        
        if avg_latency >= 50:
            print(f"  {Colors.YELLOW}• Optimize middleware performance{Colors.END}")
            print(f"    - Review async processing efficiency")
            print(f"    - Consider scaling middleware instances")
        
        if tracking_rate < 98:
            print(f"  {Colors.YELLOW}• Improve tracking reliability{Colors.END}")
            print(f"    - Implement retry mechanisms")
            print(f"    - Add redundancy to tracking pipeline")
        
        # Action Items
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}Action Items:{Colors.END}")
        print(f"  [ ] Review this report with engineering team")
        print(f"  [ ] Update billing records with CloudWatch data")
        print(f"  [ ] Archive report for compliance")
        if report['variance_pct'] >= 2.0:
            print(f"  [ ] {Colors.RED}Create incident ticket for variance investigation{Colors.END}")
        print(f"  [ ] Schedule next reconciliation for {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
        
        # Sign-off
        print(f"\n{Colors.BOLD}Report Generated By:{Colors.END} Revenium Reconciliation System")
        print(f"{Colors.BOLD}Next Review:{Colors.END} {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
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
        
        # Add insights and best practice report
        self.print_insights(report)
        self.print_best_practice_report(report, rev_stats)

def configure_simulation():
    """Interactive configuration for learning different scenarios"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Simulation Configuration{Colors.END}\n")
    
    scenarios = {
        '1': ('Normal Operation', 30, 5, 0.0),
        '2': ('High Volume', 20, 20, 0.0),
        '3': ('With Failures (3%)', 30, 5, 0.03),
        '4': ('High Failure (10%)', 30, 5, 0.10),
        '5': ('Custom', None, None, None)
    }
    
    print("Choose a scenario to explore:")
    for key, (name, duration, rate, failure) in scenarios.items():
        if key != '5':
            print(f"  {key}. {name} - {duration}s, {rate} calls/sec, {failure*100}% failure")
        else:
            print(f"  {key}. {name} - Configure your own parameters")
    
    choice = input(f"\n{Colors.BOLD}Enter choice (1-5) [default: 1]: {Colors.END}").strip() or '1'
    
    if choice in scenarios and choice != '5':
        name, duration, rate, failure = scenarios[choice]
        print(f"\n{Colors.GREEN}✓ Selected: {name}{Colors.END}")
        return duration, rate, failure
    elif choice == '5':
        print(f"\n{Colors.CYAN}Custom Configuration:{Colors.END}")
        try:
            duration = int(input("  Duration (seconds) [default: 30]: ") or "30")
            rate = int(input("  Calls per second [default: 5]: ") or "5")
            failure = float(input("  Failure rate 0.0-1.0 [default: 0.0]: ") or "0.0")
            print(f"\n{Colors.GREEN}✓ Custom configuration set{Colors.END}")
            return duration, rate, failure
        except ValueError:
            print(f"\n{Colors.YELLOW}Invalid input, using defaults{Colors.END}")
            return 30, 5, 0.0
    else:
        print(f"\n{Colors.YELLOW}Invalid choice, using Normal Operation{Colors.END}")
        return 30, 5, 0.0

def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Revenium Local Simulator{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Learn how dual-track AI metering works{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    
    # Interactive configuration
    duration, rate, failure_rate = configure_simulation()
    
    # Create simulator
    sim = Simulator()
    sim.revenium.failure_rate = failure_rate
    
    # Run simulation
    try:
        sim.run_simulation(duration_seconds=duration, calls_per_second=rate)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")

if __name__ == "__main__":
    main()
