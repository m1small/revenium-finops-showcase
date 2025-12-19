#!/usr/bin/env python3
"""
Usage-Based Revenue: Customer Profitability Analysis
Analyzes cost to serve, margins, and customer lifetime value
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class CustomerProfitabilityAnalyzer:
    """Analyzes customer profitability and margins"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
        # Subscription tier pricing
        self.tier_pricing = {
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
    
    def calculate_cost_to_serve(self) -> Dict:
        """Calculate cost to serve each customer"""
        customer_costs = defaultdict(lambda: {
            'ai_cost': 0,
            'calls': 0,
            'tier': None,
            'revenue': 0
        })
        
        for call in self.calls:
            customer_id = call['customer_id']
            customer_costs[customer_id]['ai_cost'] += call['cost_usd']
            customer_costs[customer_id]['calls'] += 1
            customer_costs[customer_id]['tier'] = call['subscription_tier']
        
        # Add revenue
        for customer_id, data in customer_costs.items():
            tier = data['tier']
            data['revenue'] = self.tier_pricing.get(tier, 0)
            data['margin'] = data['revenue'] - data['ai_cost']
            data['margin_pct'] = (data['margin'] / data['revenue'] * 100) if data['revenue'] > 0 else -100
            data['cost_to_revenue_ratio'] = (data['ai_cost'] / data['revenue']) if data['revenue'] > 0 else float('inf')
        
        return dict(customer_costs)
    
    def margin_analysis(self) -> Dict:
        """Analyze margins across customer base"""
        customer_costs = self.calculate_cost_to_serve()
        
        margins = [data['margin'] for data in customer_costs.values()]
        margin_pcts = [data['margin_pct'] for data in customer_costs.values()]
        
        # Categorize customers
        profitable = [cid for cid, data in customer_costs.items() if data['margin'] > 0]
        break_even = [cid for cid, data in customer_costs.items() if -5 <= data['margin'] <= 0]
        unprofitable = [cid for cid, data in customer_costs.items() if data['margin'] < -5]
        
        total_revenue = sum(data['revenue'] for data in customer_costs.values())
        total_cost = sum(data['ai_cost'] for data in customer_costs.values())
        total_margin = total_revenue - total_cost
        
        return {
            'total_customers': len(customer_costs),
            'profitable_count': len(profitable),
            'break_even_count': len(break_even),
            'unprofitable_count': len(unprofitable),
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_margin': total_margin,
            'avg_margin': sum(margins) / len(margins) if margins else 0,
            'avg_margin_pct': sum(margin_pcts) / len(margin_pcts) if margin_pcts else 0,
            'profitable_customers': profitable,
            'unprofitable_customers': unprofitable
        }
    
    def identify_unprofitable_customers(self) -> List[Dict]:
        """Identify and rank unprofitable customers"""
        customer_costs = self.calculate_cost_to_serve()
        
        unprofitable = []
        for customer_id, data in customer_costs.items():
            if data['margin'] < 0:
                unprofitable.append({
                    'customer_id': customer_id,
                    'tier': data['tier'],
                    'revenue': data['revenue'],
                    'ai_cost': data['ai_cost'],
                    'margin': data['margin'],
                    'margin_pct': data['margin_pct'],
                    'calls': data['calls'],
                    'cost_per_call': data['ai_cost'] / data['calls']
                })
        
        return sorted(unprofitable, key=lambda x: x['margin'])
    
    def customer_lifetime_value_projection(self) -> Dict:
        """Project customer lifetime value"""
        customer_costs = self.calculate_cost_to_serve()
        
        # Assumptions
        avg_customer_lifetime_months = 24
        monthly_churn_rate = 0.05
        
        ltv_projections = []
        
        for customer_id, data in customer_costs.items():
            monthly_revenue = data['revenue']
            monthly_cost = data['ai_cost']
            monthly_margin = data['margin']
            
            # Simple LTV calculation
            retention_rate = 1 - monthly_churn_rate
            ltv = monthly_margin * avg_customer_lifetime_months * retention_rate
            
            # Customer acquisition cost (assumed)
            cac = 150  # Assumed $150 CAC
            
            ltv_projections.append({
                'customer_id': customer_id,
                'tier': data['tier'],
                'monthly_margin': monthly_margin,
                'ltv': ltv,
                'cac': cac,
                'ltv_to_cac_ratio': ltv / cac if cac > 0 else 0,
                'payback_months': cac / monthly_margin if monthly_margin > 0 else float('inf')
            })
        
        # Calculate aggregates
        avg_ltv = sum(p['ltv'] for p in ltv_projections) / len(ltv_projections) if ltv_projections else 0
        avg_ltv_to_cac = sum(p['ltv_to_cac_ratio'] for p in ltv_projections) / len(ltv_projections) if ltv_projections else 0
        
        return {
            'projections': sorted(ltv_projections, key=lambda x: x['ltv'], reverse=True),
            'avg_ltv': avg_ltv,
            'avg_ltv_to_cac_ratio': avg_ltv_to_cac,
            'assumptions': {
                'avg_lifetime_months': avg_customer_lifetime_months,
                'monthly_churn_rate': monthly_churn_rate,
                'assumed_cac': 150
            }
        }
    
    def margin_distribution(self) -> Dict:
        """Calculate margin distribution histogram"""
        customer_costs = self.calculate_cost_to_serve()
        
        # Define margin buckets
        buckets = {
            'highly_profitable': 0,    # >80% margin
            'profitable': 0,            # 50-80% margin
            'moderate': 0,              # 20-50% margin
            'low': 0,                   # 0-20% margin
            'break_even': 0,            # -10 to 0% margin
            'unprofitable': 0           # <-10% margin
        }
        
        for data in customer_costs.values():
            margin_pct = data['margin_pct']
            if margin_pct > 80:
                buckets['highly_profitable'] += 1
            elif margin_pct > 50:
                buckets['profitable'] += 1
            elif margin_pct > 20:
                buckets['moderate'] += 1
            elif margin_pct > 0:
                buckets['low'] += 1
            elif margin_pct > -10:
                buckets['break_even'] += 1
            else:
                buckets['unprofitable'] += 1
        
        return buckets
    
    def generate_report(self, output_file: str = 'reports/customer_profitability.md'):
        """Generate markdown report"""
        
        cost_to_serve = self.calculate_cost_to_serve()
        margin_analysis = self.margin_analysis()
        unprofitable = self.identify_unprofitable_customers()
        ltv = self.customer_lifetime_value_projection()
        distribution = self.margin_distribution()
        
        report = f"""# Usage-Based Revenue: Customer Profitability Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Total Customers**: {margin_analysis['total_customers']}  
**Total Revenue**: ${margin_analysis['total_revenue']:,.2f}/month  
**Total AI Cost**: ${margin_analysis['total_cost']:,.2f}/month  
**Total Margin**: ${margin_analysis['total_margin']:,.2f}/month ({margin_analysis['avg_margin_pct']:.1f}% avg)

**Customer Breakdown**:
- 🟢 Profitable: {margin_analysis['profitable_count']} ({margin_analysis['profitable_count']/margin_analysis['total_customers']*100:.1f}%)
- 🟡 Break-even: {margin_analysis['break_even_count']} ({margin_analysis['break_even_count']/margin_analysis['total_customers']*100:.1f}%)
- 🔴 Unprofitable: {margin_analysis['unprofitable_count']} ({margin_analysis['unprofitable_count']/margin_analysis['total_customers']*100:.1f}%)

---

## Cost to Serve Analysis

### Top 10 Most Profitable Customers

| Customer | Tier | Revenue | AI Cost | Margin | Margin % | Calls |
|----------|------|---------|---------|--------|----------|-------|
"""
        
        sorted_customers = sorted(cost_to_serve.items(), key=lambda x: x[1]['margin'], reverse=True)
        for customer_id, data in sorted_customers[:10]:
            report += f"| {customer_id} | {data['tier']} | ${data['revenue']:.2f} | "
            report += f"${data['ai_cost']:.2f} | ${data['margin']:.2f} | "
            report += f"{data['margin_pct']:.1f}% | {data['calls']:,} |\n"
        
        report += "\n### Top 10 Least Profitable Customers\n\n"
        report += "| Customer | Tier | Revenue | AI Cost | Margin | Margin % | Calls |\n"
        report += "|----------|------|---------|---------|--------|----------|-------|\n"
        
        for customer_id, data in sorted_customers[-10:]:
            report += f"| {customer_id} | {data['tier']} | ${data['revenue']:.2f} | "
            report += f"${data['ai_cost']:.2f} | ${data['margin']:.2f} | "
            report += f"{data['margin_pct']:.1f}% | {data['calls']:,} |\n"
        
        report += "\n---\n\n## Unprofitable Customers Detail\n\n"
        
        if unprofitable:
            total_unprofitable_loss = sum(c['margin'] for c in unprofitable)
            report += f"**Total Monthly Loss**: ${abs(total_unprofitable_loss):,.2f}\n\n"
            report += "| Customer | Tier | Revenue | AI Cost | Loss | Calls | Cost/Call |\n"
            report += "|----------|------|---------|---------|------|-------|----------|\n"
            
            for customer in unprofitable[:20]:
                report += f"| {customer['customer_id']} | {customer['tier']} | "
                report += f"${customer['revenue']:.2f} | ${customer['ai_cost']:.2f} | "
                report += f"${abs(customer['margin']):.2f} | {customer['calls']:,} | "
                report += f"${customer['cost_per_call']:.4f} |\n"
        else:
            report += "*No unprofitable customers identified.*\n"
        
        report += "\n---\n\n## Margin Distribution\n\n"
        report += "| Category | Count | Percentage |\n"
        report += "|----------|-------|------------|\n"
        
        total = margin_analysis['total_customers']
        for category, count in distribution.items():
            pct = (count / total * 100) if total > 0 else 0
            report += f"| {category.replace('_', ' ').title()} | {count} | {pct:.1f}% |\n"
        
        # Text-based histogram
        report += "\n### Visual Distribution\n\n```\n"
        max_count = max(distribution.values()) if distribution.values() else 1
        for category, count in distribution.items():
            bar_length = int((count / max_count) * 40) if max_count > 0 else 0
            bar = '█' * bar_length
            report += f"{category:20s} | {bar} {count}\n"
        report += "```\n"
        
        report += "\n---\n\n## Customer Lifetime Value Projections\n\n"
        report += f"**Average LTV**: ${ltv['avg_ltv']:,.2f}  \n"
        report += f"**Average LTV:CAC Ratio**: {ltv['avg_ltv_to_cac_ratio']:.2f}x\n\n"
        
        report += "**Assumptions**:\n"
        report += f"- Average customer lifetime: {ltv['assumptions']['avg_lifetime_months']} months\n"
        report += f"- Monthly churn rate: {ltv['assumptions']['monthly_churn_rate']*100:.1f}%\n"
        report += f"- Customer acquisition cost: ${ltv['assumptions']['assumed_cac']}\n\n"
        
        report += "### Top 10 Customers by LTV\n\n"
        report += "| Customer | Tier | Monthly Margin | LTV | LTV:CAC | Payback (months) |\n"
        report += "|----------|------|----------------|-----|---------|------------------|\n"
        
        for proj in ltv['projections'][:10]:
            payback = f"{proj['payback_months']:.1f}" if proj['payback_months'] != float('inf') else "N/A"
            report += f"| {proj['customer_id']} | {proj['tier']} | "
            report += f"${proj['monthly_margin']:.2f} | ${proj['ltv']:,.2f} | "
            report += f"{proj['ltv_to_cac_ratio']:.2f}x | {payback} |\n"
        
        report += "\n---\n\n## Key Insights\n\n"
        
        # Insight 1: Unprofitable customer impact
        if unprofitable:
            total_loss = abs(sum(c['margin'] for c in unprofitable))
            report += f"1. **Revenue at Risk**: ${total_loss:,.2f}/month from {len(unprofitable)} unprofitable customers\n"
        
        # Insight 2: Tier profitability
        tier_margins = defaultdict(list)
        for data in cost_to_serve.values():
            tier_margins[data['tier']].append(data['margin_pct'])
        
        for tier in ['starter', 'pro', 'enterprise']:
            if tier in tier_margins:
                avg_margin = sum(tier_margins[tier]) / len(tier_margins[tier])
                report += f"2. **{tier.capitalize()} Tier**: Average margin {avg_margin:.1f}%\n"
        
        # Insight 3: LTV health
        healthy_ltv = sum(1 for p in ltv['projections'] if p['ltv_to_cac_ratio'] > 3)
        report += f"3. **LTV Health**: {healthy_ltv}/{len(ltv['projections'])} customers have LTV:CAC >3x (healthy threshold)\n"
        
        report += "\n---\n\n## Recommendations\n\n"
        report += "### Immediate Actions\n\n"
        
        if unprofitable:
            report += f"1. **Address Unprofitable Customers**: Contact {len(unprofitable)} customers losing money\n"
            report += "   - Option A: Upgrade to higher tier\n"
            report += "   - Option B: Implement usage caps\n"
            report += "   - Option C: Add overage charges\n\n"
        
        report += "2. **Tier Optimization**: Review pricing for customers near break-even\n"
        report += "3. **Usage Monitoring**: Set up alerts for customers approaching unprofitability\n"
        
        report += "\n### Pricing Strategy\n\n"
        
        # Calculate optimal pricing
        avg_cost_by_tier = {}
        for tier in ['starter', 'pro', 'enterprise']:
            tier_costs = [data['ai_cost'] for data in cost_to_serve.values() if data['tier'] == tier]
            if tier_costs:
                avg_cost_by_tier[tier] = sum(tier_costs) / len(tier_costs)
        
        report += "**Recommended Minimum Pricing** (for 50% margin):\n\n"
        for tier, avg_cost in sorted(avg_cost_by_tier.items()):
            recommended_price = avg_cost * 2  # 50% margin
            current_price = self.tier_pricing[tier]
            if recommended_price > current_price:
                report += f"- **{tier.capitalize()}**: ${recommended_price:.2f}/month "
                report += f"(current: ${current_price:.2f}) ⚠️ UNDERPRICED\n"
            else:
                report += f"- **{tier.capitalize()}**: ${current_price:.2f}/month ✅ ADEQUATE\n"
        
        report += "\n### Long-term Strategy\n\n"
        report += "1. **Usage-Based Pricing**: Consider hybrid model with base fee + usage charges\n"
        report += "2. **Customer Segmentation**: Create specialized tiers for high-usage customers\n"
        report += "3. **Value-Based Pricing**: Price based on customer value, not just cost\n"
        report += "4. **Retention Focus**: Improve LTV by reducing churn for profitable customers\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Customer Profitability report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = CustomerProfitabilityAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
