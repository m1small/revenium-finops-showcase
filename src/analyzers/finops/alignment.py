#!/usr/bin/env python3
"""
FinOps Domain: Organizational Alignment
Analyzes cost allocation by team/product/feature and generates chargeback reports
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class OrganizationalAlignmentAnalyzer:
    """Analyzes organizational cost allocation and alignment"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
        # Simulated budgets by organization
        self.org_budgets = {
            'org-alpha': 5000,
            'org-beta': 3000,
            'org-gamma': 2000
        }
        
        # Simulated budgets by product
        self.product_budgets = {
            'product-ai-chat': 4000,
            'product-doc-analyzer': 3000,
            'product-code-assistant': 3000
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
    
    def cost_by_organization(self) -> Dict:
        """Calculate costs by organization"""
        org_costs = defaultdict(lambda: {
            'total_cost': 0,
            'calls': 0,
            'customers': set(),
            'products': defaultdict(float)
        })
        
        for call in self.calls:
            org = call['organization_id']
            org_costs[org]['total_cost'] += call['cost_usd']
            org_costs[org]['calls'] += 1
            org_costs[org]['customers'].add(call['customer_id'])
            org_costs[org]['products'][call['product_id']] += call['cost_usd']
        
        # Convert sets to counts
        results = {}
        for org, data in org_costs.items():
            results[org] = {
                'total_cost': data['total_cost'],
                'calls': data['calls'],
                'customer_count': len(data['customers']),
                'products': dict(data['products']),
                'budget': self.org_budgets.get(org, 0),
                'budget_used_pct': (data['total_cost'] / self.org_budgets.get(org, 1)) * 100
            }
        
        return results
    
    def cost_by_product(self) -> Dict:
        """Calculate costs by product"""
        product_costs = defaultdict(lambda: {
            'total_cost': 0,
            'calls': 0,
            'customers': set(),
            'features': defaultdict(float),
            'organizations': defaultdict(float)
        })
        
        for call in self.calls:
            product = call['product_id']
            product_costs[product]['total_cost'] += call['cost_usd']
            product_costs[product]['calls'] += 1
            product_costs[product]['customers'].add(call['customer_id'])
            product_costs[product]['features'][call['feature_id']] += call['cost_usd']
            product_costs[product]['organizations'][call['organization_id']] += call['cost_usd']
        
        results = {}
        for product, data in product_costs.items():
            results[product] = {
                'total_cost': data['total_cost'],
                'calls': data['calls'],
                'customer_count': len(data['customers']),
                'features': dict(data['features']),
                'organizations': dict(data['organizations']),
                'budget': self.product_budgets.get(product, 0),
                'budget_used_pct': (data['total_cost'] / self.product_budgets.get(product, 1)) * 100
            }
        
        return results
    
    def cost_by_feature(self) -> Dict:
        """Calculate costs by feature"""
        feature_costs = defaultdict(lambda: {
            'total_cost': 0,
            'calls': 0,
            'customers': set(),
            'products': set()
        })
        
        for call in self.calls:
            feature = call['feature_id']
            feature_costs[feature]['total_cost'] += call['cost_usd']
            feature_costs[feature]['calls'] += 1
            feature_costs[feature]['customers'].add(call['customer_id'])
            feature_costs[feature]['products'].add(call['product_id'])
        
        results = {}
        for feature, data in feature_costs.items():
            results[feature] = {
                'total_cost': data['total_cost'],
                'calls': data['calls'],
                'customer_count': len(data['customers']),
                'product_count': len(data['products']),
                'avg_cost_per_call': data['total_cost'] / data['calls']
            }
        
        return results
    
    def generate_chargeback_report(self) -> Dict:
        """Generate chargeback/showback data"""
        org_costs = self.cost_by_organization()
        product_costs = self.cost_by_product()
        
        chargeback = {
            'by_organization': {},
            'by_product': {},
            'cross_charges': defaultdict(lambda: defaultdict(float))
        }
        
        # Organization chargeback
        for org, data in org_costs.items():
            chargeback['by_organization'][org] = {
                'total_charge': data['total_cost'],
                'budget': data['budget'],
                'variance': data['total_cost'] - data['budget'],
                'variance_pct': ((data['total_cost'] - data['budget']) / data['budget'] * 100) if data['budget'] > 0 else 0,
                'status': 'OVER' if data['total_cost'] > data['budget'] else 'UNDER'
            }
        
        # Product chargeback
        for product, data in product_costs.items():
            chargeback['by_product'][product] = {
                'total_charge': data['total_cost'],
                'budget': data['budget'],
                'variance': data['total_cost'] - data['budget'],
                'variance_pct': ((data['total_cost'] - data['budget']) / data['budget'] * 100) if data['budget'] > 0 else 0,
                'status': 'OVER' if data['total_cost'] > data['budget'] else 'UNDER'
            }
        
        # Cross-organization charges (products used by multiple orgs)
        for call in self.calls:
            org = call['organization_id']
            product = call['product_id']
            chargeback['cross_charges'][org][product] += call['cost_usd']
        
        return chargeback
    
    def budget_tracking(self) -> Dict:
        """Track budget vs actual spending"""
        org_costs = self.cost_by_organization()
        product_costs = self.cost_by_product()
        
        total_org_budget = sum(self.org_budgets.values())
        total_org_actual = sum(data['total_cost'] for data in org_costs.values())
        
        total_product_budget = sum(self.product_budgets.values())
        total_product_actual = sum(data['total_cost'] for data in product_costs.values())
        
        return {
            'organization_level': {
                'total_budget': total_org_budget,
                'total_actual': total_org_actual,
                'variance': total_org_actual - total_org_budget,
                'variance_pct': ((total_org_actual - total_org_budget) / total_org_budget * 100) if total_org_budget > 0 else 0,
                'by_org': org_costs
            },
            'product_level': {
                'total_budget': total_product_budget,
                'total_actual': total_product_actual,
                'variance': total_product_actual - total_product_budget,
                'variance_pct': ((total_product_actual - total_product_budget) / total_product_budget * 100) if total_product_budget > 0 else 0,
                'by_product': product_costs
            }
        }
    
    def cross_team_comparison(self) -> Dict:
        """Compare costs across teams/organizations"""
        org_costs = self.cost_by_organization()
        
        # Calculate efficiency metrics
        comparisons = []
        for org, data in org_costs.items():
            comparisons.append({
                'organization': org,
                'total_cost': data['total_cost'],
                'cost_per_call': data['total_cost'] / data['calls'],
                'cost_per_customer': data['total_cost'] / data['customer_count'],
                'calls': data['calls'],
                'customers': data['customer_count'],
                'efficiency_score': data['calls'] / data['total_cost']  # calls per dollar
            })
        
        # Rank by efficiency
        comparisons.sort(key=lambda x: x['efficiency_score'], reverse=True)
        
        return {
            'comparisons': comparisons,
            'most_efficient': comparisons[0]['organization'] if comparisons else None,
            'least_efficient': comparisons[-1]['organization'] if comparisons else None
        }
    
    def generate_report(self, output_file: str = 'reports/finops_alignment.md'):
        """Generate markdown report"""
        
        org_costs = self.cost_by_organization()
        product_costs = self.cost_by_product()
        feature_costs = self.cost_by_feature()
        chargeback = self.generate_chargeback_report()
        budget = self.budget_tracking()
        comparison = self.cross_team_comparison()
        
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        report = f"""# FinOps Domain: Organizational Alignment

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Analysis of cost allocation across organizations, products, and features with budget tracking and chargeback recommendations.

**Total Spend**: ${total_cost:,.2f}  
**Budget Variance**: ${budget['organization_level']['variance']:,.2f} ({budget['organization_level']['variance_pct']:+.1f}%)

---

## Cost by Organization

| Organization | Total Cost | Budget | Variance | % Used | Calls | Customers |
|--------------|------------|--------|----------|--------|-------|-----------|
"""
        
        for org, data in sorted(org_costs.items(), key=lambda x: x[1]['total_cost'], reverse=True):
            variance = data['total_cost'] - data['budget']
            status = '🔴' if variance > 0 else '🟢'
            report += f"| {org} | ${data['total_cost']:,.2f} | ${data['budget']:,.2f} | "
            report += f"{status} ${variance:,.2f} | {data['budget_used_pct']:.1f}% | "
            report += f"{data['calls']:,} | {data['customer_count']} |\n"
        
        report += "\n### Organization Product Breakdown\n\n"
        
        for org, data in sorted(org_costs.items()):
            report += f"#### {org}\n\n"
            for product, cost in sorted(data['products'].items(), key=lambda x: x[1], reverse=True):
                pct = (cost / data['total_cost']) * 100
                report += f"- **{product}**: ${cost:,.2f} ({pct:.1f}%)\n"
            report += "\n"
        
        report += "---\n\n## Cost by Product\n\n"
        report += "| Product | Total Cost | Budget | Variance | % Used | Calls | Customers |\n"
        report += "|---------|------------|--------|----------|--------|-------|----------|\n"
        
        for product, data in sorted(product_costs.items(), key=lambda x: x[1]['total_cost'], reverse=True):
            variance = data['total_cost'] - data['budget']
            status = '🔴' if variance > 0 else '🟢'
            report += f"| {product} | ${data['total_cost']:,.2f} | ${data['budget']:,.2f} | "
            report += f"{status} ${variance:,.2f} | {data['budget_used_pct']:.1f}% | "
            report += f"{data['calls']:,} | {data['customer_count']} |\n"
        
        report += "\n---\n\n## Cost by Feature\n\n"
        report += "| Feature | Total Cost | Calls | Customers | Avg Cost/Call |\n"
        report += "|---------|------------|-------|-----------|---------------|\n"
        
        for feature, data in sorted(feature_costs.items(), key=lambda x: x[1]['total_cost'], reverse=True):
            report += f"| {feature} | ${data['total_cost']:,.2f} | {data['calls']:,} | "
            report += f"{data['customer_count']} | ${data['avg_cost_per_call']:.4f} |\n"
        
        report += "\n---\n\n## Chargeback Report\n\n"
        report += "### Organization Chargeback Summary\n\n"
        report += "| Organization | Charge | Budget | Variance | Status |\n"
        report += "|--------------|--------|--------|----------|--------|\n"
        
        for org, data in sorted(chargeback['by_organization'].items()):
            status_icon = '🔴 OVER' if data['status'] == 'OVER' else '🟢 UNDER'
            report += f"| {org} | ${data['total_charge']:,.2f} | ${data['budget']:,.2f} | "
            report += f"${data['variance']:,.2f} ({data['variance_pct']:+.1f}%) | {status_icon} |\n"
        
        report += "\n### Product Chargeback Summary\n\n"
        report += "| Product | Charge | Budget | Variance | Status |\n"
        report += "|---------|--------|--------|----------|--------|\n"
        
        for product, data in sorted(chargeback['by_product'].items()):
            status_icon = '🔴 OVER' if data['status'] == 'OVER' else '🟢 UNDER'
            report += f"| {product} | ${data['total_charge']:,.2f} | ${data['budget']:,.2f} | "
            report += f"${data['variance']:,.2f} ({data['variance_pct']:+.1f}%) | {status_icon} |\n"
        
        report += "\n### Cross-Organization Product Usage\n\n"
        
        for org, products in sorted(chargeback['cross_charges'].items()):
            report += f"#### {org}\n\n"
            for product, cost in sorted(products.items(), key=lambda x: x[1], reverse=True):
                report += f"- {product}: ${cost:,.2f}\n"
            report += "\n"
        
        report += "---\n\n## Budget Tracking\n\n"
        report += "### Organization Level\n\n"
        report += f"- **Total Budget**: ${budget['organization_level']['total_budget']:,.2f}\n"
        report += f"- **Total Actual**: ${budget['organization_level']['total_actual']:,.2f}\n"
        report += f"- **Variance**: ${budget['organization_level']['variance']:,.2f} "
        report += f"({budget['organization_level']['variance_pct']:+.1f}%)\n"
        
        if budget['organization_level']['variance'] > 0:
            report += f"\n⚠️ **Alert**: Organizations are ${budget['organization_level']['variance']:,.2f} over budget\n"
        
        report += "\n### Product Level\n\n"
        report += f"- **Total Budget**: ${budget['product_level']['total_budget']:,.2f}\n"
        report += f"- **Total Actual**: ${budget['product_level']['total_actual']:,.2f}\n"
        report += f"- **Variance**: ${budget['product_level']['variance']:,.2f} "
        report += f"({budget['product_level']['variance_pct']:+.1f}%)\n"
        
        if budget['product_level']['variance'] > 0:
            report += f"\n⚠️ **Alert**: Products are ${budget['product_level']['variance']:,.2f} over budget\n"
        
        report += "\n---\n\n## Cross-Team Comparison\n\n"
        report += "| Rank | Organization | Total Cost | Cost/Call | Cost/Customer | Efficiency Score |\n"
        report += "|------|--------------|------------|-----------|---------------|------------------|\n"
        
        for i, comp in enumerate(comparison['comparisons'], 1):
            report += f"| {i} | {comp['organization']} | ${comp['total_cost']:,.2f} | "
            report += f"${comp['cost_per_call']:.4f} | ${comp['cost_per_customer']:,.2f} | "
            report += f"{comp['efficiency_score']:.2f} |\n"
        
        report += f"\n**Most Efficient**: {comparison['most_efficient']} "
        report += f"(highest calls per dollar)\n"
        report += f"**Least Efficient**: {comparison['least_efficient']}\n"
        
        report += "\n---\n\n## Key Insights\n\n"
        
        # Budget overruns
        over_budget_orgs = [org for org, data in chargeback['by_organization'].items() 
                           if data['status'] == 'OVER']
        if over_budget_orgs:
            report += f"1. **Budget Overruns**: {len(over_budget_orgs)} organizations over budget "
            report += f"({', '.join(over_budget_orgs)})\n"
        
        # Most expensive product
        most_expensive_product = max(product_costs.items(), key=lambda x: x[1]['total_cost'])
        report += f"2. **Highest Cost Product**: {most_expensive_product[0]} "
        report += f"(${most_expensive_product[1]['total_cost']:,.2f}, "
        report += f"{most_expensive_product[1]['total_cost']/total_cost*100:.1f}% of total)\n"
        
        # Efficiency gap
        if len(comparison['comparisons']) > 1:
            efficiency_gap = (comparison['comparisons'][0]['efficiency_score'] - 
                            comparison['comparisons'][-1]['efficiency_score'])
            report += f"3. **Efficiency Gap**: {efficiency_gap:.2f} calls/$ between most and least efficient orgs\n"
        
        report += "\n---\n\n## Recommendations\n\n"
        report += "### Immediate Actions\n\n"
        
        if over_budget_orgs:
            report += f"1. **Budget Review**: Meet with {', '.join(over_budget_orgs)} to review spending\n"
        
        report += "2. **Chargeback Implementation**: Implement monthly chargeback process\n"
        report += "3. **Budget Alerts**: Set up 80% and 100% budget threshold alerts\n"
        
        report += "\n### Process Improvements\n\n"
        report += "1. **Cost Allocation**: Implement automated cost allocation tagging\n"
        report += "2. **Showback Reports**: Distribute monthly showback reports to all teams\n"
        report += "3. **Budget Planning**: Conduct quarterly budget review and adjustment\n"
        report += "4. **Efficiency Sharing**: Share best practices from most efficient teams\n"
        
        report += "\n### Governance\n\n"
        report += "1. **Approval Process**: Require approval for spend >$1000/month per product\n"
        report += "2. **Cost Centers**: Define clear cost center ownership\n"
        report += "3. **KPIs**: Track cost per customer and cost per call as key metrics\n"
        report += "4. **Review Cadence**: Monthly FinOps review with all stakeholders\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Organizational Alignment report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = OrganizationalAlignmentAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
