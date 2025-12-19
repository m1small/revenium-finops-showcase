#!/usr/bin/env python3
"""
Usage-Based Revenue: Feature Economics Analysis
Analyzes cost per feature, profitability, and investment recommendations
"""

import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


class FeatureEconomicsAnalyzer:
    """Analyzes feature-level economics and ROI"""
    
    def __init__(self, data_file: str = 'data/simulated_calls.csv'):
        self.data_file = data_file
        self.calls = self._load_data()
        
        # Simulated feature pricing (if features were sold separately)
        self.feature_pricing = {
            'feature-chat': 15,
            'feature-summarize': 20,
            'feature-code': 30,
            'feature-translate': 10,
            'feature-analyze': 25
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
    
    def cost_per_feature(self) -> Dict:
        """Calculate cost metrics per feature"""
        feature_stats = defaultdict(lambda: {
            'total_cost': 0,
            'calls': 0,
            'customers': set(),
            'products': set(),
            'total_tokens': 0
        })
        
        for call in self.calls:
            feature = call['feature_id']
            stats = feature_stats[feature]
            stats['total_cost'] += call['cost_usd']
            stats['calls'] += 1
            stats['customers'].add(call['customer_id'])
            stats['products'].add(call['product_id'])
            stats['total_tokens'] += call['input_tokens'] + call['output_tokens']
        
        results = {}
        for feature, stats in feature_stats.items():
            results[feature] = {
                'total_cost': stats['total_cost'],
                'calls': stats['calls'],
                'customer_count': len(stats['customers']),
                'product_count': len(stats['products']),
                'avg_cost_per_call': stats['total_cost'] / stats['calls'],
                'avg_cost_per_customer': stats['total_cost'] / len(stats['customers']),
                'total_tokens': stats['total_tokens']
            }
        
        return results
    
    def feature_profitability(self) -> Dict:
        """Analyze profitability if features were priced separately"""
        feature_costs = self.cost_per_feature()
        
        profitability = {}
        
        for feature, costs in feature_costs.items():
            # Assume each customer using the feature pays the feature price
            potential_revenue = self.feature_pricing.get(feature, 0) * costs['customer_count']
            actual_cost = costs['total_cost']
            margin = potential_revenue - actual_cost
            margin_pct = (margin / potential_revenue * 100) if potential_revenue > 0 else -100
            
            profitability[feature] = {
                'potential_revenue': potential_revenue,
                'actual_cost': actual_cost,
                'margin': margin,
                'margin_pct': margin_pct,
                'customers': costs['customer_count'],
                'calls': costs['calls'],
                'price_point': self.feature_pricing.get(feature, 0),
                'status': 'PROFITABLE' if margin > 0 else 'UNPROFITABLE'
            }
        
        return profitability
    
    def feature_usage_distribution(self) -> Dict:
        """Analyze feature usage patterns"""
        # Usage by customer
        customer_features = defaultdict(set)
        feature_calls_by_customer = defaultdict(lambda: defaultdict(int))
        
        for call in self.calls:
            customer_id = call['customer_id']
            feature = call['feature_id']
            customer_features[customer_id].add(feature)
            feature_calls_by_customer[customer_id][feature] += 1
        
        # Calculate adoption rates
        total_customers = len(customer_features)
        feature_adoption = defaultdict(int)
        
        for customer_id, features in customer_features.items():
            for feature in features:
                feature_adoption[feature] += 1
        
        # Calculate usage intensity
        feature_intensity = {}
        for feature in feature_adoption.keys():
            users = [cid for cid, features in customer_features.items() if feature in features]
            total_calls = sum(feature_calls_by_customer[cid][feature] for cid in users)
            avg_calls_per_user = total_calls / len(users) if users else 0
            
            feature_intensity[feature] = {
                'adoption_count': feature_adoption[feature],
                'adoption_rate': (feature_adoption[feature] / total_customers * 100),
                'avg_calls_per_user': avg_calls_per_user,
                'total_calls': total_calls
            }
        
        return feature_intensity
    
    def feature_investment_recommendations(self) -> List[Dict]:
        """Generate invest/maintain/sunset recommendations"""
        profitability = self.feature_profitability()
        usage = self.feature_usage_distribution()
        
        recommendations = []
        
        for feature in profitability.keys():
            prof = profitability[feature]
            use = usage[feature]
            
            # Scoring criteria
            margin_score = 1 if prof['margin_pct'] > 50 else 0.5 if prof['margin_pct'] > 0 else 0
            adoption_score = 1 if use['adoption_rate'] > 60 else 0.5 if use['adoption_rate'] > 30 else 0
            intensity_score = 1 if use['avg_calls_per_user'] > 100 else 0.5 if use['avg_calls_per_user'] > 30 else 0
            
            total_score = (margin_score + adoption_score + intensity_score) / 3
            
            # Determine recommendation
            if total_score > 0.7:
                recommendation = 'INVEST'
                action = 'Increase investment, expand capabilities'
            elif total_score > 0.4:
                recommendation = 'MAINTAIN'
                action = 'Keep current investment level'
            else:
                recommendation = 'SUNSET'
                action = 'Consider deprecation or major overhaul'
            
            recommendations.append({
                'feature': feature,
                'recommendation': recommendation,
                'action': action,
                'score': total_score,
                'margin_pct': prof['margin_pct'],
                'adoption_rate': use['adoption_rate'],
                'avg_calls_per_user': use['avg_calls_per_user'],
                'monthly_cost': prof['actual_cost'],
                'monthly_revenue_potential': prof['potential_revenue']
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def feature_bundle_analysis(self) -> Dict:
        """Analyze which features are commonly used together"""
        customer_features = defaultdict(set)
        
        for call in self.calls:
            customer_id = call['customer_id']
            feature = call['feature_id']
            customer_features[customer_id].add(feature)
        
        # Find common combinations
        feature_pairs = defaultdict(int)
        
        for customer_id, features in customer_features.items():
            features_list = sorted(list(features))
            for i, f1 in enumerate(features_list):
                for f2 in features_list[i+1:]:
                    pair = f"{f1}+{f2}"
                    feature_pairs[pair] += 1
        
        # Calculate bundle opportunities
        total_customers = len(customer_features)
        bundles = []
        
        for pair, count in sorted(feature_pairs.items(), key=lambda x: x[1], reverse=True):
            features = pair.split('+')
            adoption_rate = (count / total_customers) * 100
            
            if adoption_rate > 20:  # Only significant bundles
                bundles.append({
                    'features': features,
                    'customer_count': count,
                    'adoption_rate': adoption_rate,
                    'bundle_name': f"{features[0].split('-')[1].title()} + {features[1].split('-')[1].title()}"
                })
        
        return {
            'bundles': bundles[:10],  # Top 10 bundles
            'avg_features_per_customer': sum(len(f) for f in customer_features.values()) / len(customer_features)
        }
    
    def generate_report(self, output_file: str = 'reports/feature_economics.md'):
        """Generate markdown report"""
        
        costs = self.cost_per_feature()
        profitability = self.feature_profitability()
        usage = self.feature_usage_distribution()
        recommendations = self.feature_investment_recommendations()
        bundles = self.feature_bundle_analysis()
        
        total_cost = sum(c['total_cost'] for c in costs.values())
        total_calls = sum(c['calls'] for c in costs.values())
        
        report = f"""# Usage-Based Revenue: Feature Economics Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Analysis of feature-level costs, profitability, and strategic investment recommendations.

**Total Feature Cost**: ${total_cost:,.2f}/month  
**Total Calls**: {total_calls:,}  
**Average Features per Customer**: {bundles['avg_features_per_customer']:.1f}

---

## Cost per Feature

| Feature | Total Cost | Calls | Customers | Avg Cost/Call | Avg Cost/Customer |
|---------|------------|-------|-----------|---------------|-------------------|
"""
        
        for feature, data in sorted(costs.items(), key=lambda x: x[1]['total_cost'], reverse=True):
            feature_name = feature.split('-')[1].title()
            report += f"| {feature_name} | ${data['total_cost']:,.2f} | {data['calls']:,} | "
            report += f"{data['customer_count']} | ${data['avg_cost_per_call']:.4f} | "
            report += f"${data['avg_cost_per_customer']:.2f} |\n"
        
        report += "\n---\n\n## Feature Profitability Analysis\n\n"
        report += "*Analysis assumes features priced separately at market rates*\n\n"
        report += "| Feature | Price Point | Revenue Potential | Actual Cost | Margin | Margin % | Status |\n"
        report += "|---------|-------------|-------------------|-------------|--------|----------|--------|\n"
        
        for feature, data in sorted(profitability.items(), key=lambda x: x[1]['margin'], reverse=True):
            feature_name = feature.split('-')[1].title()
            status_icon = '🟢' if data['status'] == 'PROFITABLE' else '🔴'
            report += f"| {feature_name} | ${data['price_point']} | "
            report += f"${data['potential_revenue']:,.2f} | ${data['actual_cost']:,.2f} | "
            report += f"${data['margin']:,.2f} | {data['margin_pct']:.1f}% | "
            report += f"{status_icon} {data['status']} |\n"
        
        report += "\n---\n\n## Feature Usage Distribution\n\n"
        report += "| Feature | Adoption Rate | Users | Avg Calls/User | Total Calls |\n"
        report += "|---------|---------------|-------|----------------|-------------|\n"
        
        for feature, data in sorted(usage.items(), key=lambda x: x[1]['adoption_rate'], reverse=True):
            feature_name = feature.split('-')[1].title()
            report += f"| {feature_name} | {data['adoption_rate']:.1f}% | "
            report += f"{data['adoption_count']} | {data['avg_calls_per_user']:.0f} | "
            report += f"{data['total_calls']:,} |\n"
        
        # Visual adoption chart
        report += "\n### Adoption Rate Visualization\n\n```\n"
        max_adoption = max(u['adoption_rate'] for u in usage.values())
        for feature, data in sorted(usage.items(), key=lambda x: x[1]['adoption_rate'], reverse=True):
            feature_name = feature.split('-')[1].title()
            bar_length = int((data['adoption_rate'] / max_adoption) * 40) if max_adoption > 0 else 0
            bar = '█' * bar_length
            report += f"{feature_name:15s} | {bar} {data['adoption_rate']:.1f}%\n"
        report += "```\n"
        
        report += "\n---\n\n## Investment Recommendations\n\n"
        
        for rec in recommendations:
            feature_name = rec['feature'].split('-')[1].title()
            
            if rec['recommendation'] == 'INVEST':
                icon = '🚀'
                color = '🟢'
            elif rec['recommendation'] == 'MAINTAIN':
                icon = '⚖️'
                color = '🟡'
            else:
                icon = '⚠️'
                color = '🔴'
            
            report += f"### {icon} {feature_name} - {color} {rec['recommendation']}\n\n"
            report += f"**Action**: {rec['action']}\n\n"
            report += f"**Metrics**:\n"
            report += f"- Overall Score: {rec['score']:.2f}/1.0\n"
            report += f"- Margin: {rec['margin_pct']:.1f}%\n"
            report += f"- Adoption Rate: {rec['adoption_rate']:.1f}%\n"
            report += f"- Avg Calls per User: {rec['avg_calls_per_user']:.0f}\n"
            report += f"- Monthly Cost: ${rec['monthly_cost']:,.2f}\n"
            report += f"- Revenue Potential: ${rec['monthly_revenue_potential']:,.2f}\n\n"
        
        report += "---\n\n## Feature Bundle Opportunities\n\n"
        
        if bundles['bundles']:
            report += "Features commonly used together (potential bundle offerings):\n\n"
            report += "| Bundle | Customers | Adoption Rate | Recommendation |\n"
            report += "|--------|-----------|---------------|----------------|\n"
            
            for bundle in bundles['bundles']:
                report += f"| {bundle['bundle_name']} | {bundle['customer_count']} | "
                report += f"{bundle['adoption_rate']:.1f}% | "
                
                if bundle['adoption_rate'] > 40:
                    report += "Strong bundle candidate |\n"
                else:
                    report += "Consider bundle |\n"
        else:
            report += "*No significant bundle patterns detected.*\n"
        
        report += "\n---\n\n## Key Insights\n\n"
        
        # Most expensive feature
        most_expensive = max(costs.items(), key=lambda x: x[1]['total_cost'])
        report += f"1. **Highest Cost Feature**: {most_expensive[0].split('-')[1].title()} "
        report += f"(${most_expensive[1]['total_cost']:,.2f}/month, "
        report += f"{most_expensive[1]['total_cost']/total_cost*100:.1f}% of total)\n"
        
        # Most adopted feature
        most_adopted = max(usage.items(), key=lambda x: x[1]['adoption_rate'])
        report += f"2. **Most Popular Feature**: {most_adopted[0].split('-')[1].title()} "
        report += f"({most_adopted[1]['adoption_rate']:.1f}% adoption rate)\n"
        
        # Most profitable
        most_profitable = max(profitability.items(), key=lambda x: x[1]['margin'])
        report += f"3. **Most Profitable Feature**: {most_profitable[0].split('-')[1].title()} "
        report += f"(${most_profitable[1]['margin']:,.2f} margin, {most_profitable[1]['margin_pct']:.1f}%)\n"
        
        # Investment priorities
        invest_features = [r for r in recommendations if r['recommendation'] == 'INVEST']
        sunset_features = [r for r in recommendations if r['recommendation'] == 'SUNSET']
        
        if invest_features:
            report += f"4. **Investment Priorities**: {len(invest_features)} features recommended for increased investment\n"
        
        if sunset_features:
            report += f"5. **Sunset Candidates**: {len(sunset_features)} features underperforming on multiple metrics\n"
        
        report += "\n---\n\n## Strategic Recommendations\n\n"
        report += "### Immediate Actions (0-30 days)\n\n"
        
        if invest_features:
            top_invest = invest_features[0]
            feature_name = top_invest['feature'].split('-')[1].title()
            report += f"1. **Expand {feature_name}**: Highest-scoring feature - allocate additional development resources\n"
        
        if sunset_features:
            top_sunset = sunset_features[0]
            feature_name = top_sunset['feature'].split('-')[1].title()
            report += f"2. **Review {feature_name}**: Low performance - conduct user research or consider deprecation\n"
        
        if bundles['bundles']:
            top_bundle = bundles['bundles'][0]
            report += f"3. **Create Bundle**: Launch '{top_bundle['bundle_name']}' bundle ({top_bundle['adoption_rate']:.0f}% natural adoption)\n"
        
        report += "\n### Short-term Strategy (1-3 months)\n\n"
        report += "1. **Feature Pricing**: Consider à la carte pricing for high-value features\n"
        report += "2. **Usage Analytics**: Implement feature-level usage tracking and alerts\n"
        report += "3. **Customer Segmentation**: Identify power users of each feature for upsell\n"
        report += "4. **Cost Optimization**: Optimize infrastructure for high-cost features\n"
        
        report += "\n### Long-term Strategy (3-12 months)\n\n"
        report += "1. **Feature Roadmap**: Prioritize development based on profitability and adoption\n"
        report += "2. **Tiered Features**: Create feature-based tiers (Basic, Pro, Enterprise)\n"
        report += "3. **API Monetization**: Offer feature APIs for enterprise customers\n"
        report += "4. **Sunset Plan**: Gracefully deprecate underperforming features\n"
        
        report += "\n### Financial Impact\n\n"
        
        # Calculate potential revenue from feature-based pricing
        total_potential = sum(p['potential_revenue'] for p in profitability.values())
        current_revenue = 100 * 29 + 0 * 99 + 0 * 299  # Simplified assumption
        
        report += f"**Feature-Based Pricing Potential**:\n"
        report += f"- Current bundled revenue (estimated): ${current_revenue:,.2f}/month\n"
        report += f"- À la carte revenue potential: ${total_potential:,.2f}/month\n"
        report += f"- Potential uplift: ${total_potential - current_revenue:,.2f}/month\n\n"
        
        report += "*Note: Actual revenue will depend on pricing strategy and customer adoption*\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Feature Economics report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    
    analyzer = FeatureEconomicsAnalyzer()
    analyzer.generate_report()


if __name__ == '__main__':
    main()
