#!/usr/bin/env python3
"""
FinOps Domain: Real-Time Decision Making
Detects anomalies, threshold violations, and provides immediate optimization alerts
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class RealTimeDecisionAnalyzer:
    """Analyzes real-time patterns and generates alerts"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
    def _load_data(self) -> List[Dict]:
        """Load AI call data from CSV"""
        calls = []
        with open(self.data_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['cost_usd'] = float(row['cost_usd'])
                row['input_tokens'] = int(row['input_tokens'])
                row['output_tokens'] = int(row['output_tokens'])
                row['latency_ms'] = int(row['latency_ms'])
                row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                calls.append(row)
        return sorted(calls, key=lambda x: x['timestamp'])
    
    def detect_cost_anomalies(self, threshold_multiplier: float = 2.0) -> List[Dict]:
        """Detect unusual cost spikes"""
        # Calculate daily costs
        daily_costs = defaultdict(float)
        for call in self.calls:
            day = call['timestamp'].date()
            daily_costs[day] += call['cost_usd']
        
        # Calculate baseline (average)
        avg_daily_cost = sum(daily_costs.values()) / len(daily_costs)
        std_dev = (sum((cost - avg_daily_cost) ** 2 for cost in daily_costs.values()) / len(daily_costs)) ** 0.5
        
        # Detect anomalies
        anomalies = []
        for day, cost in daily_costs.items():
            if cost > avg_daily_cost + (threshold_multiplier * std_dev):
                anomalies.append({
                    'date': day,
                    'cost': cost,
                    'baseline': avg_daily_cost,
                    'deviation': ((cost - avg_daily_cost) / avg_daily_cost) * 100,
                    'severity': 'HIGH' if cost > avg_daily_cost * 2.5 else 'MEDIUM'
                })
        
        return sorted(anomalies, key=lambda x: x['cost'], reverse=True)
    
    def identify_threshold_violations(self) -> Dict:
        """Identify customers exceeding cost thresholds"""
        # Define thresholds by subscription tier
        thresholds = {
            'starter': 50,    # $50/month
            'pro': 150,       # $150/month
            'enterprise': 500 # $500/month
        }
        
        # Calculate customer costs
        customer_costs = defaultdict(lambda: {'cost': 0, 'tier': None, 'calls': 0})
        for call in self.calls:
            customer_id = call['customer_id']
            customer_costs[customer_id]['cost'] += call['cost_usd']
            customer_costs[customer_id]['tier'] = call['subscription_tier']
            customer_costs[customer_id]['calls'] += 1
        
        # Find violations
        violations = []
        for customer_id, data in customer_costs.items():
            tier = data['tier']
            cost = data['cost']
            threshold = thresholds.get(tier, 100)
            
            if cost > threshold:
                violations.append({
                    'customer_id': customer_id,
                    'tier': tier,
                    'cost': cost,
                    'threshold': threshold,
                    'overage': cost - threshold,
                    'overage_pct': ((cost - threshold) / threshold) * 100,
                    'calls': data['calls']
                })
        
        return {
            'violations': sorted(violations, key=lambda x: x['overage'], reverse=True),
            'total_overage': sum(v['overage'] for v in violations),
            'affected_customers': len(violations)
        }
    
    def detect_inefficient_usage(self) -> List[Dict]:
        """Detect inefficient model usage patterns"""
        # Calculate model efficiency baseline
        model_efficiency = defaultdict(lambda: {'costs': [], 'tokens': []})
        
        for call in self.calls:
            model = call['model']
            total_tokens = call['input_tokens'] + call['output_tokens']
            model_efficiency[model]['costs'].append(call['cost_usd'])
            model_efficiency[model]['tokens'].append(total_tokens)
        
        # Calculate average cost per 1K tokens for each model
        model_baselines = {}
        for model, data in model_efficiency.items():
            total_cost = sum(data['costs'])
            total_tokens = sum(data['tokens'])
            model_baselines[model] = total_cost / (total_tokens / 1000) if total_tokens > 0 else 0
        
        # Find expensive models being used for simple tasks
        inefficiencies = []
        expensive_models = sorted(model_baselines.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for model, baseline_cost in expensive_models:
            model_calls = [c for c in self.calls if c['model'] == model]
            
            # Check if used for simple tasks (low token count)
            simple_task_calls = [c for c in model_calls 
                                if (c['input_tokens'] + c['output_tokens']) < 500]
            
            if len(simple_task_calls) > len(model_calls) * 0.3:  # >30% simple tasks
                total_waste = sum(c['cost_usd'] for c in simple_task_calls)
                
                # Estimate savings with cheaper model
                cheapest_model = min(model_baselines.items(), key=lambda x: x[1])
                potential_savings = total_waste * (1 - (cheapest_model[1] / baseline_cost))
                
                inefficiencies.append({
                    'model': model,
                    'simple_task_calls': len(simple_task_calls),
                    'total_calls': len(model_calls),
                    'waste_pct': (len(simple_task_calls) / len(model_calls)) * 100,
                    'current_cost': total_waste,
                    'potential_savings': potential_savings,
                    'recommendation': f"Switch to {cheapest_model[0]} for simple tasks"
                })
        
        return sorted(inefficiencies, key=lambda x: x['potential_savings'], reverse=True)
    
    def suggest_immediate_optimizations(self) -> List[Dict]:
        """Generate actionable optimization suggestions"""
        optimizations = []
        
        # 1. High-cost customer optimization
        customer_costs = defaultdict(float)
        for call in self.calls:
            customer_costs[call['customer_id']] += call['cost_usd']
        
        top_customers = sorted(customer_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        total_top_cost = sum(cost for _, cost in top_customers)
        
        optimizations.append({
            'priority': 'HIGH',
            'category': 'Customer Management',
            'issue': f'Top 5 customers account for ${total_top_cost:,.2f}',
            'action': 'Review pricing tiers and implement usage caps',
            'estimated_impact': f'${total_top_cost * 0.2:,.2f}/month revenue protection',
            'effort': 'Medium'
        })
        
        # 2. Model consolidation
        model_usage = defaultdict(int)
        for call in self.calls:
            model_usage[call['model']] += 1
        
        if len(model_usage) > 4:
            optimizations.append({
                'priority': 'MEDIUM',
                'category': 'Model Optimization',
                'issue': f'Using {len(model_usage)} different models',
                'action': 'Consolidate to 2-3 primary models',
                'estimated_impact': '$500-1000/month in reduced complexity costs',
                'effort': 'High'
            })
        
        # 3. Off-peak usage incentives
        hourly_costs = defaultdict(float)
        for call in self.calls:
            hour = call['timestamp'].hour
            hourly_costs[hour] += call['cost_usd']
        
        peak_hours = sorted(hourly_costs.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_cost = sum(cost for _, cost in peak_hours)
        
        optimizations.append({
            'priority': 'LOW',
            'category': 'Usage Patterns',
            'issue': f'${peak_cost:,.2f} spent during peak hours',
            'action': 'Implement off-peak pricing incentives',
            'estimated_impact': f'${peak_cost * 0.15:,.2f}/month cost reduction',
            'effort': 'Low'
        })
        
        # 4. Token optimization
        high_token_calls = [c for c in self.calls if (c['input_tokens'] + c['output_tokens']) > 3000]
        if len(high_token_calls) > len(self.calls) * 0.1:
            high_token_cost = sum(c['cost_usd'] for c in high_token_calls)
            
            optimizations.append({
                'priority': 'MEDIUM',
                'category': 'Token Efficiency',
                'issue': f'{len(high_token_calls)} calls with >3K tokens (${high_token_cost:,.2f})',
                'action': 'Implement prompt optimization and context pruning',
                'estimated_impact': f'${high_token_cost * 0.25:,.2f}/month savings',
                'effort': 'Medium'
            })
        
        return optimizations
    
    def generate_report(self, output_file: str = 'reports/finops_realtime.md'):
        """Generate markdown report"""
        
        anomalies = self.detect_cost_anomalies()
        violations = self.identify_threshold_violations()
        inefficiencies = self.detect_inefficient_usage()
        optimizations = self.suggest_immediate_optimizations()
        
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        report = f"""# FinOps Domain: Real-Time Decision Making

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Real-time monitoring has identified cost anomalies, threshold violations, and immediate optimization opportunities.

**Key Alerts**:
- 🔴 {len(anomalies)} cost anomaly days detected
- ⚠️ {violations['affected_customers']} customers exceeding thresholds
- 💡 {len(inefficiencies)} inefficient usage patterns found
- 💰 ${violations['total_overage']:,.2f} in total overages

---

## Cost Anomaly Detection

"""
        
        if anomalies:
            report += "| Date | Cost | Baseline | Deviation | Severity |\n"
            report += "|------|------|----------|-----------|----------|\n"
            
            for anomaly in anomalies[:10]:
                report += f"| {anomaly['date']} | ${anomaly['cost']:,.2f} | "
                report += f"${anomaly['baseline']:,.2f} | "
                report += f"+{anomaly['deviation']:.1f}% | {anomaly['severity']} |\n"
        else:
            report += "*No significant cost anomalies detected.*\n"
        
        report += "\n---\n\n## Customer Threshold Violations\n\n"
        
        if violations['violations']:
            report += f"**{violations['affected_customers']} customers** have exceeded their tier thresholds.\n\n"
            report += "| Customer | Tier | Cost | Threshold | Overage | % Over |\n"
            report += "|----------|------|------|-----------|---------|--------|\n"
            
            for v in violations['violations'][:15]:
                report += f"| {v['customer_id']} | {v['tier']} | "
                report += f"${v['cost']:,.2f} | ${v['threshold']:,.2f} | "
                report += f"${v['overage']:,.2f} | +{v['overage_pct']:.0f}% |\n"
            
            report += f"\n**Total Overage**: ${violations['total_overage']:,.2f}\n"
            report += f"\n⚠️ **Action Required**: Review pricing for {violations['affected_customers']} customers\n"
        else:
            report += "*All customers within their tier thresholds.*\n"
        
        report += "\n---\n\n## Inefficient Usage Patterns\n\n"
        
        if inefficiencies:
            for ineff in inefficiencies:
                report += f"### {ineff['model']}\n\n"
                report += f"- **Issue**: {ineff['simple_task_calls']:,} simple tasks "
                report += f"({ineff['waste_pct']:.1f}% of calls) using expensive model\n"
                report += f"- **Current Cost**: ${ineff['current_cost']:,.2f}\n"
                report += f"- **Potential Savings**: ${ineff['potential_savings']:,.2f}/month\n"
                report += f"- **Recommendation**: {ineff['recommendation']}\n\n"
        else:
            report += "*No major inefficiencies detected.*\n"
        
        report += "\n---\n\n## Immediate Optimization Opportunities\n\n"
        
        for opt in sorted(optimizations, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[x['priority']]):
            priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}[opt['priority']]
            report += f"### {priority_emoji} {opt['priority']} Priority: {opt['category']}\n\n"
            report += f"**Issue**: {opt['issue']}\n\n"
            report += f"**Action**: {opt['action']}\n\n"
            report += f"**Estimated Impact**: {opt['estimated_impact']}\n\n"
            report += f"**Effort**: {opt['effort']}\n\n"
        
        report += "---\n\n## Real-Time Alerts Configuration\n\n"
        report += "### Recommended Alert Thresholds\n\n"
        
        avg_daily = total_cost / 30
        report += f"1. **Daily Spend Alert**: ${avg_daily * 1.5:,.2f} (150% of average)\n"
        report += f"2. **Customer Overage**: Tier threshold + 20%\n"
        report += f"3. **Hourly Spike**: ${avg_daily / 24 * 3:,.2f} (3x hourly average)\n"
        report += f"4. **Model Cost Alert**: ${total_cost / len(self.calls) * 100:,.2f} per 100 calls\n"
        
        report += "\n### Alert Channels\n\n"
        report += "- **Critical (HIGH)**: Immediate Slack/email notification\n"
        report += "- **Warning (MEDIUM)**: Daily digest email\n"
        report += "- **Info (LOW)**: Weekly summary report\n"
        
        report += "\n---\n\n## Key Insights\n\n"
        
        if anomalies:
            worst_day = max(anomalies, key=lambda x: x['cost'])
            report += f"1. **Highest Anomaly**: {worst_day['date']} with ${worst_day['cost']:,.2f} "
            report += f"({worst_day['deviation']:.0f}% above baseline)\n"
        
        if violations['violations']:
            worst_violator = max(violations['violations'], key=lambda x: x['overage'])
            report += f"2. **Largest Overage**: {worst_violator['customer_id']} "
            report += f"(${worst_violator['overage']:,.2f} over threshold)\n"
        
        report += f"3. **Total Optimization Potential**: ${sum(i['potential_savings'] for i in inefficiencies):,.2f}/month\n"
        
        report += "\n---\n\n## Recommended Actions (Next 24 Hours)\n\n"
        report += "1. ✅ Contact customers exceeding thresholds\n"
        report += "2. ✅ Implement model routing for simple tasks\n"
        report += "3. ✅ Set up automated alerts for anomalies\n"
        report += "4. ✅ Review and adjust tier pricing\n"
        report += "5. ✅ Schedule weekly optimization review\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Real-Time Decision report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = RealTimeDecisionAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
