#!/usr/bin/env python3
"""
FinOps Domain: Rate Optimization
Analyzes pricing opportunities, reserved capacity, and commitment recommendations
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class RateOptimizationAnalyzer:
    """Analyzes rate optimization and commitment opportunities"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
        # Simulated reserved pricing (30% discount for commitment)
        self.reserved_discount = 0.30
        
    def _load_data(self) -> List[Dict]:
        """Load AI call data from CSV"""
        calls = []
        with open(self.data_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['cost_usd'] = float(row['cost_usd'])
                row['input_tokens'] = int(row['input_tokens'])
                row['output_tokens'] = int(row['output_tokens'])
                calls.append(row)
        return calls
    
    def analyze_reserved_capacity_opportunity(self) -> Dict:
        """Compare actual costs vs reserved capacity pricing"""
        # Calculate usage by provider and model
        usage_stats = defaultdict(lambda: {
            'calls': 0,
            'cost': 0,
            'tokens': 0
        })
        
        for call in self.calls:
            key = f"{call['provider']}:{call['model']}"
            usage_stats[key]['calls'] += 1
            usage_stats[key]['cost'] += call['cost_usd']
            usage_stats[key]['tokens'] += call['input_tokens'] + call['output_tokens']
        
        # Calculate potential savings with reserved pricing
        opportunities = []
        total_current_cost = 0
        total_reserved_cost = 0
        
        for key, stats in usage_stats.items():
            provider, model = key.split(':')
            current_cost = stats['cost']
            reserved_cost = current_cost * (1 - self.reserved_discount)
            savings = current_cost - reserved_cost
            
            # Only recommend if significant usage (>$100/month)
            if current_cost > 100:
                opportunities.append({
                    'provider': provider,
                    'model': model,
                    'current_cost': current_cost,
                    'reserved_cost': reserved_cost,
                    'monthly_savings': savings,
                    'annual_savings': savings * 12,
                    'calls': stats['calls'],
                    'recommendation': 'STRONG' if current_cost > 500 else 'CONSIDER'
                })
            
            total_current_cost += current_cost
            total_reserved_cost += reserved_cost
        
        return {
            'opportunities': sorted(opportunities, key=lambda x: x['monthly_savings'], reverse=True),
            'total_current_cost': total_current_cost,
            'total_reserved_cost': total_reserved_cost,
            'total_monthly_savings': total_current_cost - total_reserved_cost,
            'total_annual_savings': (total_current_cost - total_reserved_cost) * 12
        }
    
    def identify_model_switching_opportunities(self) -> List[Dict]:
        """Identify opportunities to switch to cheaper models"""
        # Group by task type and analyze model costs
        task_model_costs = defaultdict(lambda: defaultdict(lambda: {
            'total_cost': 0,
            'calls': 0,
            'avg_tokens': 0
        }))
        
        for call in self.calls:
            task = call['task_type']
            model = call['model']
            stats = task_model_costs[task][model]
            stats['total_cost'] += call['cost_usd']
            stats['calls'] += 1
            stats['avg_tokens'] += (call['input_tokens'] + call['output_tokens'])
        
        # Calculate averages and find switching opportunities
        opportunities = []
        
        for task, models in task_model_costs.items():
            if len(models) < 2:
                continue
            
            # Calculate average cost per call for each model
            model_avg_costs = {}
            for model, stats in models.items():
                avg_cost = stats['total_cost'] / stats['calls']
                model_avg_costs[model] = {
                    'avg_cost': avg_cost,
                    'total_cost': stats['total_cost'],
                    'calls': stats['calls']
                }
            
            # Find most and least expensive
            most_expensive = max(model_avg_costs.items(), key=lambda x: x[1]['avg_cost'])
            least_expensive = min(model_avg_costs.items(), key=lambda x: x[1]['avg_cost'])
            
            # Calculate potential savings
            if most_expensive[1]['avg_cost'] > least_expensive[1]['avg_cost'] * 1.5:
                potential_savings = (most_expensive[1]['avg_cost'] - least_expensive[1]['avg_cost']) * most_expensive[1]['calls']
                
                opportunities.append({
                    'task_type': task,
                    'current_model': most_expensive[0],
                    'current_cost': most_expensive[1]['total_cost'],
                    'recommended_model': least_expensive[0],
                    'recommended_cost': least_expensive[1]['avg_cost'] * most_expensive[1]['calls'],
                    'monthly_savings': potential_savings,
                    'calls_affected': most_expensive[1]['calls'],
                    'cost_reduction_pct': ((most_expensive[1]['avg_cost'] - least_expensive[1]['avg_cost']) / most_expensive[1]['avg_cost']) * 100
                })
        
        return sorted(opportunities, key=lambda x: x['monthly_savings'], reverse=True)
    
    def calculate_commitment_recommendations(self) -> Dict:
        """Recommend commitment levels based on usage patterns"""
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        # Analyze usage stability (coefficient of variation)
        daily_costs = defaultdict(float)
        for call in self.calls:
            day = call['timestamp'][:10]
            daily_costs[day] += call['cost_usd']
        
        costs = list(daily_costs.values())
        avg_daily = sum(costs) / len(costs)
        variance = sum((c - avg_daily) ** 2 for c in costs) / len(costs)
        std_dev = variance ** 0.5
        cv = std_dev / avg_daily if avg_daily > 0 else 0
        
        # Determine commitment level based on stability
        if cv < 0.2:  # Very stable
            commitment_level = 0.8
            confidence = 'HIGH'
        elif cv < 0.4:  # Moderately stable
            commitment_level = 0.6
            confidence = 'MEDIUM'
        else:  # Variable
            commitment_level = 0.4
            confidence = 'LOW'
        
        committed_amount = total_cost * commitment_level
        committed_savings = committed_amount * self.reserved_discount
        
        return {
            'total_monthly_cost': total_cost,
            'usage_stability': 'STABLE' if cv < 0.3 else 'VARIABLE',
            'coefficient_variation': cv,
            'recommended_commitment_pct': commitment_level * 100,
            'recommended_commitment_amount': committed_amount,
            'expected_monthly_savings': committed_savings,
            'expected_annual_savings': committed_savings * 12,
            'confidence': confidence,
            'risk_level': 'LOW' if cv < 0.3 else 'MEDIUM' if cv < 0.5 else 'HIGH'
        }
    
    def analyze_volume_discounts(self) -> Dict:
        """Analyze potential volume discount opportunities"""
        # Calculate usage by provider
        provider_usage = defaultdict(lambda: {
            'cost': 0,
            'calls': 0,
            'tokens': 0
        })
        
        for call in self.calls:
            provider = call['provider']
            provider_usage[provider]['cost'] += call['cost_usd']
            provider_usage[provider]['calls'] += 1
            provider_usage[provider]['tokens'] += call['input_tokens'] + call['output_tokens']
        
        # Simulated volume discount tiers
        discount_tiers = [
            {'threshold': 10000, 'discount': 0.05, 'name': 'Bronze'},
            {'threshold': 25000, 'discount': 0.10, 'name': 'Silver'},
            {'threshold': 50000, 'discount': 0.15, 'name': 'Gold'},
            {'threshold': 100000, 'discount': 0.20, 'name': 'Platinum'}
        ]
        
        opportunities = []
        for provider, usage in provider_usage.items():
            monthly_cost = usage['cost']
            annual_cost = monthly_cost * 12
            
            # Find applicable tier
            applicable_tier = None
            for tier in reversed(discount_tiers):
                if annual_cost >= tier['threshold']:
                    applicable_tier = tier
                    break
            
            # Find next tier
            next_tier = None
            for tier in discount_tiers:
                if annual_cost < tier['threshold']:
                    next_tier = tier
                    break
            
            current_discount = applicable_tier['discount'] if applicable_tier else 0
            current_savings = monthly_cost * current_discount
            
            opportunities.append({
                'provider': provider,
                'monthly_cost': monthly_cost,
                'annual_cost': annual_cost,
                'current_tier': applicable_tier['name'] if applicable_tier else 'None',
                'current_discount': current_discount * 100,
                'current_monthly_savings': current_savings,
                'next_tier': next_tier['name'] if next_tier else 'Maximum',
                'next_tier_threshold': next_tier['threshold'] if next_tier else annual_cost,
                'gap_to_next_tier': (next_tier['threshold'] - annual_cost) if next_tier else 0,
                'next_tier_discount': next_tier['discount'] * 100 if next_tier else current_discount * 100
            })
        
        return sorted(opportunities, key=lambda x: x['monthly_cost'], reverse=True)
    
    def generate_report(self, output_file: str = 'reports/finops_optimization.md'):
        """Generate markdown report"""
        
        reserved = self.analyze_reserved_capacity_opportunity()
        switching = self.identify_model_switching_opportunities()
        commitment = self.calculate_commitment_recommendations()
        volume = self.analyze_volume_discounts()
        
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        report = f"""# FinOps Domain: Rate Optimization

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Analysis of rate optimization opportunities including reserved capacity, model switching, and volume discounts.

**Total Optimization Potential**: ${reserved['total_monthly_savings'] + sum(s['monthly_savings'] for s in switching):,.2f}/month

---

## Reserved Capacity Analysis

**Current Spend**: ${reserved['total_current_cost']:,.2f}/month  
**With Reserved Pricing**: ${reserved['total_reserved_cost']:,.2f}/month  
**Monthly Savings**: ${reserved['total_monthly_savings']:,.2f}  
**Annual Savings**: ${reserved['total_annual_savings']:,.2f}

### Recommended Reserved Capacity Commitments

| Provider | Model | Current Cost | Reserved Cost | Monthly Savings | Annual Savings | Recommendation |
|----------|-------|--------------|---------------|-----------------|----------------|----------------|
"""
        
        for opp in reserved['opportunities']:
            report += f"| {opp['provider']} | {opp['model']} | "
            report += f"${opp['current_cost']:,.2f} | ${opp['reserved_cost']:,.2f} | "
            report += f"${opp['monthly_savings']:,.2f} | ${opp['annual_savings']:,.2f} | "
            report += f"{opp['recommendation']} |\n"
        
        report += f"\n*Assumes {self.reserved_discount*100:.0f}% discount for 1-year commitment*\n"
        
        report += "\n---\n\n## Model Switching Opportunities\n\n"
        
        if switching:
            total_switching_savings = sum(s['monthly_savings'] for s in switching)
            report += f"**Total Potential Savings**: ${total_switching_savings:,.2f}/month\n\n"
            
            for opp in switching:
                report += f"### {opp['task_type'].replace('_', ' ').title()}\n\n"
                report += f"- **Current Model**: `{opp['current_model']}` (${opp['current_cost']:,.2f}/month)\n"
                report += f"- **Recommended Model**: `{opp['recommended_model']}` (${opp['recommended_cost']:,.2f}/month)\n"
                report += f"- **Monthly Savings**: ${opp['monthly_savings']:,.2f}\n"
                report += f"- **Cost Reduction**: {opp['cost_reduction_pct']:.1f}%\n"
                report += f"- **Calls Affected**: {opp['calls_affected']:,}\n\n"
        else:
            report += "*No significant model switching opportunities identified.*\n"
        
        report += "\n---\n\n## Commitment Recommendations\n\n"
        report += f"**Usage Stability**: {commitment['usage_stability']} "
        report += f"(CV: {commitment['coefficient_variation']:.2f})\n\n"
        report += f"**Recommended Commitment**: {commitment['recommended_commitment_pct']:.0f}% "
        report += f"(${commitment['recommended_commitment_amount']:,.2f}/month)\n\n"
        report += f"**Expected Savings**:\n"
        report += f"- Monthly: ${commitment['expected_monthly_savings']:,.2f}\n"
        report += f"- Annual: ${commitment['expected_annual_savings']:,.2f}\n\n"
        report += f"**Confidence Level**: {commitment['confidence']}  \n"
        report += f"**Risk Level**: {commitment['risk_level']}\n"
        
        if commitment['confidence'] == 'HIGH':
            report += f"\n✅ **Strong recommendation** for commitment due to stable usage patterns.\n"
        elif commitment['confidence'] == 'MEDIUM':
            report += f"\n⚠️ **Moderate recommendation** - consider shorter commitment period.\n"
        else:
            report += f"\n❌ **Caution** - usage too variable for large commitment.\n"
        
        report += "\n---\n\n## Volume Discount Analysis\n\n"
        
        for opp in volume:
            report += f"### {opp['provider'].capitalize()}\n\n"
            report += f"- **Monthly Cost**: ${opp['monthly_cost']:,.2f}\n"
            report += f"- **Annual Cost**: ${opp['annual_cost']:,.2f}\n"
            report += f"- **Current Tier**: {opp['current_tier']} ({opp['current_discount']:.0f}% discount)\n"
            report += f"- **Current Savings**: ${opp['current_monthly_savings']:,.2f}/month\n"
            
            if opp['next_tier'] != 'Maximum':
                report += f"- **Next Tier**: {opp['next_tier']} ({opp['next_tier_discount']:.0f}% discount)\n"
                report += f"- **Gap to Next Tier**: ${opp['gap_to_next_tier']:,.2f} annual spend\n"
                
                if opp['gap_to_next_tier'] < opp['annual_cost'] * 0.2:
                    report += f"  - 💡 *Within reach - consider consolidating usage*\n"
            else:
                report += f"- **Status**: Maximum tier achieved ✅\n"
            
            report += "\n"
        
        report += "---\n\n## Optimization Roadmap\n\n"
        report += "### Immediate (0-30 days)\n\n"
        
        if reserved['opportunities']:
            top_reserved = reserved['opportunities'][0]
            report += f"1. **Reserve Capacity**: Commit to `{top_reserved['model']}` "
            report += f"(save ${top_reserved['monthly_savings']:,.2f}/month)\n"
        
        if switching:
            top_switch = switching[0]
            report += f"2. **Switch Models**: Migrate {top_switch['task_type']} to `{top_switch['recommended_model']}` "
            report += f"(save ${top_switch['monthly_savings']:,.2f}/month)\n"
        
        report += "\n### Short-term (1-3 months)\n\n"
        report += f"3. **Commitment Plan**: Implement {commitment['recommended_commitment_pct']:.0f}% commitment "
        report += f"(save ${commitment['expected_monthly_savings']:,.2f}/month)\n"
        report += "4. **Usage Consolidation**: Consolidate to fewer models for volume discounts\n"
        
        report += "\n### Long-term (3-12 months)\n\n"
        report += "5. **Annual Commitment**: Negotiate annual contracts with volume discounts\n"
        report += "6. **Multi-provider Strategy**: Balance usage across providers for optimal rates\n"
        report += "7. **Continuous Optimization**: Monthly review of rate opportunities\n"
        
        report += "\n---\n\n## Financial Impact Summary\n\n"
        
        total_monthly_savings = (
            reserved['total_monthly_savings'] +
            sum(s['monthly_savings'] for s in switching) +
            commitment['expected_monthly_savings']
        )
        
        report += f"| Optimization Type | Monthly Savings | Annual Savings | Implementation Effort |\n"
        report += f"|-------------------|-----------------|----------------|----------------------|\n"
        report += f"| Reserved Capacity | ${reserved['total_monthly_savings']:,.2f} | "
        report += f"${reserved['total_annual_savings']:,.2f} | Low |\n"
        
        if switching:
            switching_monthly = sum(s['monthly_savings'] for s in switching)
            report += f"| Model Switching | ${switching_monthly:,.2f} | "
            report += f"${switching_monthly * 12:,.2f} | Medium |\n"
        
        report += f"| Commitment Discount | ${commitment['expected_monthly_savings']:,.2f} | "
        report += f"${commitment['expected_annual_savings']:,.2f} | Low |\n"
        report += f"| **TOTAL** | **${total_monthly_savings:,.2f}** | "
        report += f"**${total_monthly_savings * 12:,.2f}** | - |\n"
        
        savings_pct = (total_monthly_savings / total_cost) * 100
        report += f"\n**Total Cost Reduction**: {savings_pct:.1f}%\n"
        
        report += "\n---\n\n## Key Recommendations\n\n"
        report += f"1. ✅ **Immediate Action**: Reserve capacity for top 3 models (${reserved['opportunities'][0]['monthly_savings'] if reserved['opportunities'] else 0:,.2f}/month savings)\n"
        report += f"2. 📊 **Analysis Required**: A/B test model switches before full migration\n"
        report += f"3. 💼 **Negotiation**: Leverage ${total_cost * 12:,.2f} annual spend for better rates\n"
        report += f"4. 📈 **Monitoring**: Track usage stability monthly to adjust commitments\n"
        report += f"5. 🎯 **Target**: Achieve {savings_pct:.0f}% cost reduction within 90 days\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Rate Optimization report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = RateOptimizationAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
