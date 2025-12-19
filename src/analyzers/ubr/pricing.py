#!/usr/bin/env python3
"""
Usage-Based Revenue: Pricing Strategy Simulator
Tests different pricing models and recommends optimal structure
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class PricingStrategySimulator:
    """Simulates and compares different pricing models"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
        # Current flat pricing
        self.current_pricing = {
            'starter': 29,
            'pro': 99,
            'enterprise': 299
        }
        
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
    
    def calculate_current_model(self) -> Dict:
        """Calculate revenue and margins under current flat pricing"""
        customer_data = defaultdict(lambda: {
            'tier': None,
            'calls': 0,
            'cost': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_data[customer_id]['tier'] = call['subscription_tier']
            customer_data[customer_id]['calls'] += 1
            customer_data[customer_id]['cost'] += call['cost_usd']
        
        total_revenue = 0
        total_cost = 0
        customer_margins = []
        
        for customer_id, data in customer_data.items():
            revenue = self.current_pricing[data['tier']]
            cost = data['cost']
            margin = revenue - cost
            
            total_revenue += revenue
            total_cost += cost
            customer_margins.append(margin)
        
        return {
            'model': 'Flat Pricing',
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_margin': total_revenue - total_cost,
            'margin_pct': ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0,
            'customers': len(customer_data),
            'avg_revenue_per_customer': total_revenue / len(customer_data),
            'negative_margin_customers': sum(1 for m in customer_margins if m < 0)
        }
    
    def simulate_tiered_pricing(self) -> Dict:
        """Simulate tiered pricing with included calls and overage"""
        # Tiered model: base fee + included calls + overage
        tiers = {
            'starter': {
                'base_fee': 29,
                'included_calls': 100,
                'overage_per_call': 0.15
            },
            'pro': {
                'base_fee': 99,
                'included_calls': 500,
                'overage_per_call': 0.12
            },
            'enterprise': {
                'base_fee': 299,
                'included_calls': 2000,
                'overage_per_call': 0.10
            }
        }
        
        customer_data = defaultdict(lambda: {
            'tier': None,
            'calls': 0,
            'cost': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_data[customer_id]['tier'] = call['subscription_tier']
            customer_data[customer_id]['calls'] += 1
            customer_data[customer_id]['cost'] += call['cost_usd']
        
        total_revenue = 0
        total_cost = 0
        customer_margins = []
        
        for customer_id, data in customer_data.items():
            tier_config = tiers[data['tier']]
            base_fee = tier_config['base_fee']
            included = tier_config['included_calls']
            overage_rate = tier_config['overage_per_call']
            
            # Calculate revenue
            if data['calls'] <= included:
                revenue = base_fee
            else:
                overage_calls = data['calls'] - included
                revenue = base_fee + (overage_calls * overage_rate)
            
            cost = data['cost']
            margin = revenue - cost
            
            total_revenue += revenue
            total_cost += cost
            customer_margins.append(margin)
        
        return {
            'model': 'Tiered Pricing',
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_margin': total_revenue - total_cost,
            'margin_pct': ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0,
            'customers': len(customer_data),
            'avg_revenue_per_customer': total_revenue / len(customer_data),
            'negative_margin_customers': sum(1 for m in customer_margins if m < 0),
            'config': tiers
        }
    
    def simulate_pure_usage(self) -> Dict:
        """Simulate pure usage-based pricing (no base fee)"""
        # Price per call based on cost + markup
        markup_multiplier = 2.5  # 150% markup (60% margin)
        
        customer_data = defaultdict(lambda: {
            'calls': 0,
            'cost': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_data[customer_id]['calls'] += 1
            customer_data[customer_id]['cost'] += call['cost_usd']
        
        total_revenue = 0
        total_cost = 0
        customer_margins = []
        
        for customer_id, data in customer_data.items():
            cost = data['cost']
            revenue = cost * markup_multiplier
            margin = revenue - cost
            
            total_revenue += revenue
            total_cost += cost
            customer_margins.append(margin)
        
        return {
            'model': 'Pure Usage-Based',
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_margin': total_revenue - total_cost,
            'margin_pct': ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0,
            'customers': len(customer_data),
            'avg_revenue_per_customer': total_revenue / len(customer_data),
            'negative_margin_customers': sum(1 for m in customer_margins if m < 0),
            'markup_multiplier': markup_multiplier
        }
    
    def simulate_hybrid_pricing(self) -> Dict:
        """Simulate hybrid pricing (base fee + usage component)"""
        # Hybrid model: lower base fee + cost-plus pricing
        tiers = {
            'starter': {
                'base_fee': 19,
                'cost_multiplier': 2.0  # 100% markup
            },
            'pro': {
                'base_fee': 49,
                'cost_multiplier': 1.8  # 80% markup
            },
            'enterprise': {
                'base_fee': 149,
                'cost_multiplier': 1.5  # 50% markup
            }
        }
        
        customer_data = defaultdict(lambda: {
            'tier': None,
            'calls': 0,
            'cost': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_data[customer_id]['tier'] = call['subscription_tier']
            customer_data[customer_id]['calls'] += 1
            customer_data[customer_id]['cost'] += call['cost_usd']
        
        total_revenue = 0
        total_cost = 0
        customer_margins = []
        
        for customer_id, data in customer_data.items():
            tier_config = tiers[data['tier']]
            base_fee = tier_config['base_fee']
            multiplier = tier_config['cost_multiplier']
            
            # Revenue = base fee + (cost * multiplier)
            revenue = base_fee + (data['cost'] * multiplier)
            cost = data['cost']
            margin = revenue - cost
            
            total_revenue += revenue
            total_cost += cost
            customer_margins.append(margin)
        
        return {
            'model': 'Hybrid Pricing',
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_margin': total_revenue - total_cost,
            'margin_pct': ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0,
            'customers': len(customer_data),
            'avg_revenue_per_customer': total_revenue / len(customer_data),
            'negative_margin_customers': sum(1 for m in customer_margins if m < 0),
            'config': tiers
        }
    
    def compare_models(self) -> List[Dict]:
        """Compare all pricing models"""
        current = self.calculate_current_model()
        tiered = self.simulate_tiered_pricing()
        pure_usage = self.simulate_pure_usage()
        hybrid = self.simulate_hybrid_pricing()
        
        return [current, tiered, pure_usage, hybrid]
    
    def customer_segment_impact(self) -> Dict:
        """Analyze impact on different customer segments"""
        customer_data = defaultdict(lambda: {
            'tier': None,
            'calls': 0,
            'cost': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_data[customer_id]['tier'] = call['subscription_tier']
            customer_data[customer_id]['calls'] += 1
            customer_data[customer_id]['cost'] += call['cost_usd']
        
        # Categorize by usage
        segments = {
            'light': [],    # <200 calls
            'medium': [],   # 200-1000 calls
            'heavy': []     # >1000 calls
        }
        
        for customer_id, data in customer_data.items():
            if data['calls'] < 200:
                segment = 'light'
            elif data['calls'] < 1000:
                segment = 'medium'
            else:
                segment = 'heavy'
            
            segments[segment].append({
                'customer_id': customer_id,
                'tier': data['tier'],
                'calls': data['calls'],
                'cost': data['cost']
            })
        
        # Calculate impact for each segment under different models
        impact = {}
        
        for segment_name, customers in segments.items():
            if not customers:
                continue
                
            segment_impact = {
                'customer_count': len(customers),
                'avg_calls': sum(c['calls'] for c in customers) / len(customers),
                'avg_cost': sum(c['cost'] for c in customers) / len(customers),
                'models': {}
            }
            
            # Current model
            current_revenue = sum(self.current_pricing[c['tier']] for c in customers)
            segment_impact['models']['current'] = current_revenue / len(customers)
            
            # Tiered model (simplified)
            tiered_revenue = 0
            for c in customers:
                base = {'starter': 29, 'pro': 99, 'enterprise': 299}[c['tier']]
                included = {'starter': 100, 'pro': 500, 'enterprise': 2000}[c['tier']]
                overage_rate = {'starter': 0.15, 'pro': 0.12, 'enterprise': 0.10}[c['tier']]
                
                if c['calls'] > included:
                    tiered_revenue += base + ((c['calls'] - included) * overage_rate)
                else:
                    tiered_revenue += base
            
            segment_impact['models']['tiered'] = tiered_revenue / len(customers)
            
            # Pure usage
            pure_usage_revenue = sum(c['cost'] * 2.5 for c in customers)
            segment_impact['models']['pure_usage'] = pure_usage_revenue / len(customers)
            
            # Hybrid
            hybrid_revenue = 0
            for c in customers:
                base = {'starter': 19, 'pro': 49, 'enterprise': 149}[c['tier']]
                multiplier = {'starter': 2.0, 'pro': 1.8, 'enterprise': 1.5}[c['tier']]
                hybrid_revenue += base + (c['cost'] * multiplier)
            
            segment_impact['models']['hybrid'] = hybrid_revenue / len(customers)
            
            impact[segment_name] = segment_impact
        
        return impact
    
    def generate_report(self, output_file: str = 'reports/pricing_strategy.md'):
        """Generate markdown report"""
        
        models = self.compare_models()
        segment_impact = self.customer_segment_impact()
        
        report = f"""# Usage-Based Revenue: Pricing Strategy Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Comparison of four pricing models to optimize revenue and margins while maintaining customer satisfaction.

---

## Pricing Model Comparison

| Model | Total Revenue | Total Cost | Margin | Margin % | Avg Rev/Customer | Unprofitable Customers |
|-------|---------------|------------|--------|----------|------------------|------------------------|
"""
        
        for model in models:
            report += f"| {model['model']} | ${model['total_revenue']:,.2f} | "
            report += f"${model['total_cost']:,.2f} | ${model['total_margin']:,.2f} | "
            report += f"{model['margin_pct']:.1f}% | ${model['avg_revenue_per_customer']:.2f} | "
            report += f"{model['negative_margin_customers']} |\n"
        
        # Find best model
        best_margin = max(models, key=lambda x: x['total_margin'])
        best_margin_pct = max(models, key=lambda x: x['margin_pct'])
        
        report += f"\n**Highest Total Margin**: {best_margin['model']} (${best_margin['total_margin']:,.2f})  \n"
        report += f"**Highest Margin %**: {best_margin_pct['model']} ({best_margin_pct['margin_pct']:.1f}%)\n"
        
        report += "\n---\n\n## Model Details\n\n"
        
        # Current Model
        current = models[0]
        report += f"### 1. {current['model']}\n\n"
        report += "**Structure**: Fixed monthly fee per tier\n\n"
        report += "| Tier | Monthly Fee |\n"
        report += "|------|-------------|\n"
        for tier, price in self.current_pricing.items():
            report += f"| {tier.capitalize()} | ${price} |\n"
        report += f"\n**Pros**: Simple, predictable revenue  \n"
        report += f"**Cons**: {current['negative_margin_customers']} unprofitable customers, no usage alignment\n"
        
        # Tiered Model
        tiered = models[1]
        report += f"\n### 2. {tiered['model']}\n\n"
        report += "**Structure**: Base fee + included calls + overage charges\n\n"
        report += "| Tier | Base Fee | Included Calls | Overage Rate |\n"
        report += "|------|----------|----------------|-------------|\n"
        for tier, config in tiered['config'].items():
            report += f"| {tier.capitalize()} | ${config['base_fee']} | "
            report += f"{config['included_calls']:,} | ${config['overage_per_call']:.2f}/call |\n"
        report += f"\n**Pros**: Fair usage-based component, protects against heavy users  \n"
        report += f"**Cons**: More complex billing, potential customer friction on overages\n"
        
        # Pure Usage
        pure = models[2]
        report += f"\n### 3. {pure['model']}\n\n"
        report += f"**Structure**: Pay per use only ({pure['markup_multiplier']}x cost markup)\n\n"
        report += f"**Pros**: Perfect cost alignment, no unprofitable customers  \n"
        report += f"**Cons**: Unpredictable revenue, may deter light users, highest total cost to customers\n"
        
        # Hybrid Model
        hybrid = models[3]
        report += f"\n### 4. {hybrid['model']}\n\n"
        report += "**Structure**: Reduced base fee + cost-plus pricing\n\n"
        report += "| Tier | Base Fee | Cost Multiplier |\n"
        report += "|------|----------|----------------|\n"
        for tier, config in hybrid['config'].items():
            markup_pct = (config['cost_multiplier'] - 1) * 100
            report += f"| {tier.capitalize()} | ${config['base_fee']} | "
            report += f"{config['cost_multiplier']}x ({markup_pct:.0f}% markup) |\n"
        report += f"\n**Pros**: Balanced approach, predictable base + fair usage component  \n"
        report += f"**Cons**: Requires cost transparency, moderate complexity\n"
        
        report += "\n---\n\n## Customer Segment Impact Analysis\n\n"
        
        for segment, data in sorted(segment_impact.items()):
            report += f"### {segment.capitalize()} Usage Customers\n\n"
            report += f"- **Count**: {data['customer_count']} customers\n"
            report += f"- **Avg Calls**: {data['avg_calls']:.0f} calls/month\n"
            report += f"- **Avg Cost to Serve**: ${data['avg_cost']:.2f}/month\n\n"
            report += "**Average Revenue per Customer by Model**:\n\n"
            
            for model_name, avg_revenue in data['models'].items():
                change = ''
                if model_name != 'current':
                    current_rev = data['models']['current']
                    diff = avg_revenue - current_rev
                    diff_pct = (diff / current_rev * 100) if current_rev > 0 else 0
                    change = f" ({diff_pct:+.1f}%)"
                
                report += f"- **{model_name.replace('_', ' ').title()}**: ${avg_revenue:.2f}{change}\n"
            
            report += "\n"
        
        report += "---\n\n## Revenue Impact Projection\n\n"
        
        current_model = models[0]
        
        report += "| Metric | Current | Tiered | Pure Usage | Hybrid |\n"
        report += "|--------|---------|--------|------------|--------|\n"
        
        report += f"| Monthly Revenue | ${current_model['total_revenue']:,.2f} | "
        for model in models[1:]:
            diff = model['total_revenue'] - current_model['total_revenue']
            report += f"${model['total_revenue']:,.2f} ({diff:+,.0f}) | "
        report += "\n"
        
        report += f"| Monthly Margin | ${current_model['total_margin']:,.2f} | "
        for model in models[1:]:
            diff = model['total_margin'] - current_model['total_margin']
            report += f"${model['total_margin']:,.2f} ({diff:+,.0f}) | "
        report += "\n"
        
        report += f"| Margin % | {current_model['margin_pct']:.1f}% | "
        for model in models[1:]:
            report += f"{model['margin_pct']:.1f}% | "
        report += "\n"
        
        report += f"| Unprofitable Customers | {current_model['negative_margin_customers']} | "
        for model in models[1:]:
            report += f"{model['negative_margin_customers']} | "
        report += "\n"
        
        report += "\n### Annual Impact\n\n"
        
        for model in models[1:]:
            annual_diff = (model['total_margin'] - current_model['total_margin']) * 12
            report += f"- **{model['model']}**: ${annual_diff:+,.2f} annual margin change\n"
        
        report += "\n---\n\n## Recommendation\n\n"
        
        # Determine best recommendation
        recommended = max(models, key=lambda x: (x['margin_pct'], -x['negative_margin_customers']))
        
        report += f"### Recommended Model: **{recommended['model']}**\n\n"
        report += "**Rationale**:\n\n"
        report += f"1. **Margin Optimization**: {recommended['margin_pct']:.1f}% margin "
        report += f"(vs {current_model['margin_pct']:.1f}% current)\n"
        report += f"2. **Revenue Growth**: ${recommended['total_revenue'] - current_model['total_revenue']:+,.2f}/month\n"
        report += f"3. **Risk Reduction**: {recommended['negative_margin_customers']} unprofitable customers "
        report += f"(vs {current_model['negative_margin_customers']} current)\n"
        report += f"4. **Customer Fairness**: Usage-aligned pricing reduces subsidization\n"
        
        report += "\n### Implementation Roadmap\n\n"
        report += "**Phase 1 (Month 1-2): Preparation**\n"
        report += "- Communicate pricing changes to customers (60-day notice)\n"
        report += "- Update billing systems and infrastructure\n"
        report += "- Create customer migration guides\n"
        report += "- Set up usage tracking and alerts\n\n"
        
        report += "**Phase 2 (Month 3): Soft Launch**\n"
        report += "- Offer new pricing to new customers only\n"
        report += "- Grandfather existing customers with opt-in option\n"
        report += "- Monitor adoption and feedback\n"
        report += "- Adjust pricing parameters if needed\n\n"
        
        report += "**Phase 3 (Month 4-6): Full Migration**\n"
        report += "- Migrate existing customers in waves\n"
        report += "- Provide migration incentives (e.g., first month discount)\n"
        report += "- Monitor churn and customer satisfaction\n"
        report += "- Optimize based on real-world data\n\n"
        
        report += "### Success Metrics\n\n"
        report += f"- **Target Margin**: >{recommended['margin_pct']:.0f}%\n"
        report += f"- **Target Revenue**: ${recommended['total_revenue']:,.2f}/month\n"
        report += "- **Churn Rate**: <5% during migration\n"
        report += "- **Customer Satisfaction**: >80% approval\n"
        report += "- **Unprofitable Customers**: <5%\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Pricing Strategy report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = PricingStrategySimulator()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
