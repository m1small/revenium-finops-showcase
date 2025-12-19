#!/usr/bin/env python3
"""
FinOps Domain: Understanding Usage & Cost
Analyzes cost allocation, spend breakdowns, and forecasting
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class UnderstandingUsageAnalyzer:
    """Analyzes usage patterns and cost allocation"""
    
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
                calls.append(row)
        return calls
    
    def total_spend_by_provider(self) -> Dict[str, float]:
        """Calculate total spend by provider"""
        spend = defaultdict(float)
        for call in self.calls:
            spend[call['provider']] += call['cost_usd']
        return dict(spend)
    
    def total_spend_by_model(self) -> Dict[str, float]:
        """Calculate total spend by model"""
        spend = defaultdict(float)
        for call in self.calls:
            spend[call['model']] += call['cost_usd']
        return dict(spend)
    
    def total_spend_by_customer(self) -> Dict[str, float]:
        """Calculate total spend by customer"""
        spend = defaultdict(float)
        for call in self.calls:
            spend[call['customer_id']] += call['cost_usd']
        return dict(spend)
    
    def cost_allocation_hierarchy(self) -> Dict:
        """Break down costs by org → product → customer"""
        hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        for call in self.calls:
            org = call['organization_id']
            product = call['product_id']
            customer = call['customer_id']
            cost = call['cost_usd']
            
            hierarchy[org][product][customer] += cost
        
        return dict(hierarchy)
    
    def token_efficiency_metrics(self) -> Dict:
        """Calculate token usage efficiency"""
        total_input = sum(call['input_tokens'] for call in self.calls)
        total_output = sum(call['output_tokens'] for call in self.calls)
        total_cost = sum(call['cost_usd'] for call in self.calls)
        
        return {
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'avg_cost_per_1k_tokens': (total_cost / ((total_input + total_output) / 1000)),
            'input_output_ratio': total_input / total_output if total_output > 0 else 0
        }
    
    def forecast_30_day_cost(self) -> Dict:
        """Forecast next 30 days based on current trends"""
        # Calculate daily average
        dates = set(call['timestamp'][:10] for call in self.calls)
        num_days = len(dates)
        total_cost = sum(call['cost_usd'] for call in self.calls)
        daily_avg = total_cost / num_days if num_days > 0 else 0
        
        # Simple linear forecast
        forecast_30_day = daily_avg * 30
        
        # Calculate trend (compare first half vs second half)
        sorted_calls = sorted(self.calls, key=lambda x: x['timestamp'])
        midpoint = len(sorted_calls) // 2
        first_half_cost = sum(call['cost_usd'] for call in sorted_calls[:midpoint])
        second_half_cost = sum(call['cost_usd'] for call in sorted_calls[midpoint:])
        
        growth_rate = (second_half_cost - first_half_cost) / first_half_cost if first_half_cost > 0 else 0
        
        return {
            'current_daily_avg': daily_avg,
            'forecast_30_day': forecast_30_day,
            'growth_rate': growth_rate,
            'forecast_with_growth': forecast_30_day * (1 + growth_rate)
        }
    
    def generate_report(self, output_file: str = 'reports/finops_understanding.md'):
        """Generate markdown report"""
        
        # Calculate metrics
        provider_spend = self.total_spend_by_provider()
        model_spend = self.total_spend_by_model()
        customer_spend = self.total_spend_by_customer()
        hierarchy = self.cost_allocation_hierarchy()
        efficiency = self.token_efficiency_metrics()
        forecast = self.forecast_30_day_cost()
        
        total_spend = sum(call['cost_usd'] for call in self.calls)
        total_calls = len(self.calls)
        
        # Generate report
        report = f"""# FinOps Domain: Understanding Usage & Cost

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total AI Spend**: ${total_spend:,.2f} (30 days)
- **Total API Calls**: {total_calls:,}
- **Average Cost per Call**: ${total_spend/total_calls:.4f}
- **30-Day Forecast**: ${forecast['forecast_30_day']:,.2f}
- **Forecast with Growth**: ${forecast['forecast_with_growth']:,.2f}

---

## Spend by Provider

| Provider | Total Spend | % of Total | Avg per Call |
|----------|-------------|------------|--------------|
"""
        
        for provider, spend in sorted(provider_spend.items(), key=lambda x: x[1], reverse=True):
            pct = (spend / total_spend * 100)
            calls_count = sum(1 for c in self.calls if c['provider'] == provider)
            avg_per_call = spend / calls_count if calls_count > 0 else 0
            report += f"| {provider} | ${spend:,.2f} | {pct:.1f}% | ${avg_per_call:.4f} |\n"
        
        report += f"\n---\n\n## Spend by Model\n\n"
        report += "| Model | Total Spend | % of Total | Calls |\n"
        report += "|-------|-------------|------------|-------|\n"
        
        for model, spend in sorted(model_spend.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = (spend / total_spend * 100)
            calls_count = sum(1 for c in self.calls if c['model'] == model)
            report += f"| {model} | ${spend:,.2f} | {pct:.1f}% | {calls_count:,} |\n"
        
        report += f"\n---\n\n## Top 10 Customers by Spend\n\n"
        report += "| Customer ID | Total Spend | Calls | Avg per Call |\n"
        report += "|-------------|-------------|-------|-------------|\n"
        
        for customer, spend in sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:10]:
            calls_count = sum(1 for c in self.calls if c['customer_id'] == customer)
            avg_per_call = spend / calls_count if calls_count > 0 else 0
            report += f"| {customer} | ${spend:,.2f} | {calls_count:,} | ${avg_per_call:.4f} |\n"
        
        report += f"\n---\n\n## Cost Allocation Hierarchy\n\n"
        
        for org, products in sorted(hierarchy.items()):
            org_total = sum(sum(customers.values()) for customers in products.values())
            report += f"### {org} (${org_total:,.2f})\n\n"
            
            for product, customers in sorted(products.items(), key=lambda x: sum(x[1].values()), reverse=True):
                product_total = sum(customers.values())
                report += f"- **{product}**: ${product_total:,.2f} ({len(customers)} customers)\n"
        
        report += f"\n---\n\n## Token Efficiency Metrics\n\n"
        report += f"- **Total Input Tokens**: {efficiency['total_input_tokens']:,}\n"
        report += f"- **Total Output Tokens**: {efficiency['total_output_tokens']:,}\n"
        report += f"- **Total Tokens**: {efficiency['total_tokens']:,}\n"
        report += f"- **Average Cost per 1K Tokens**: ${efficiency['avg_cost_per_1k_tokens']:.4f}\n"
        report += f"- **Input/Output Ratio**: {efficiency['input_output_ratio']:.2f}\n"
        
        report += f"\n---\n\n## 30-Day Cost Forecast\n\n"
        report += f"- **Current Daily Average**: ${forecast['current_daily_avg']:,.2f}\n"
        report += f"- **Linear Forecast (30 days)**: ${forecast['forecast_30_day']:,.2f}\n"
        report += f"- **Growth Rate**: {forecast['growth_rate']*100:+.1f}%\n"
        report += f"- **Forecast with Growth**: ${forecast['forecast_with_growth']:,.2f}\n"
        
        if forecast['growth_rate'] > 0.1:
            report += f"\n⚠️ **Alert**: Cost growth rate is {forecast['growth_rate']*100:.1f}%. "
            report += f"Expected increase of ${forecast['forecast_with_growth'] - forecast['forecast_30_day']:,.2f} over baseline.\n"
        
        report += f"\n---\n\n## Key Insights\n\n"
        
        # Top provider
        top_provider = max(provider_spend.items(), key=lambda x: x[1])
        report += f"1. **{top_provider[0].capitalize()}** accounts for {top_provider[1]/total_spend*100:.1f}% of total spend (${top_provider[1]:,.2f})\n"
        
        # Top customer concentration
        top_10_spend = sum(spend for _, spend in sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:10])
        report += f"2. Top 10 customers represent {top_10_spend/total_spend*100:.1f}% of total spend (${top_10_spend:,.2f})\n"
        
        # Cost per call variance
        costs = [call['cost_usd'] for call in self.calls]
        max_cost = max(costs)
        min_cost = min(costs)
        report += f"3. Cost per call ranges from ${min_cost:.4f} to ${max_cost:.4f} (variance indicates optimization opportunities)\n"
        
        report += f"\n---\n\n## Recommendations\n\n"
        report += "1. **Cost Allocation**: Implement chargeback model based on organization/product hierarchy\n"
        report += "2. **Customer Monitoring**: Set up alerts for top 10 customers (70% of spend)\n"
        report += "3. **Forecasting**: Review monthly to adjust capacity planning\n"
        report += f"4. **Budget Planning**: Allocate ${forecast['forecast_with_growth']*1.1:,.2f}/month (10% buffer)\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Understanding Usage report generated: {output_file}")
    
    def generate_html_report(self, output_file: str = 'reports/html/finops_understanding.html'):
        """Generate HTML report"""
        from utils.html_generator import HTMLReportGenerator
        
        # Calculate metrics
        provider_spend = self.total_spend_by_provider()
        model_spend = self.total_spend_by_model()
        customer_spend = self.total_spend_by_customer()
        hierarchy = self.cost_allocation_hierarchy()
        efficiency = self.token_efficiency_metrics()
        forecast = self.forecast_30_day_cost()
        
        total_spend = sum(call['cost_usd'] for call in self.calls)
        total_calls = len(self.calls)
        
        # Create HTML generator
        generator = HTMLReportGenerator(
            title="FinOps: Understanding Usage & Cost",
            description="Cost allocation, spend breakdowns, and forecasting analysis",
            category="FinOps Domain"
        )
        
        # Executive Summary
        generator.add_section("Executive Summary", level=2)
        generator.add_metric_cards([
            {"label": "Total AI Spend (30 days)", "value": f"${total_spend:,.2f}"},
            {"label": "Total API Calls", "value": f"{total_calls:,}"},
            {"label": "Average Cost per Call", "value": f"${total_spend/total_calls:.4f}"},
            {"label": "30-Day Forecast", "value": f"${forecast['forecast_30_day']:,.2f}"},
            {"label": "Forecast with Growth", "value": f"${forecast['forecast_with_growth']:,.2f}",
             "trend": f"{forecast['growth_rate']*100:+.1f}%"}
        ])
        
        # Spend by Provider
        generator.add_section("Spend by Provider", level=2)
        provider_rows = []
        for provider, spend in sorted(provider_spend.items(), key=lambda x: x[1], reverse=True):
            pct = (spend / total_spend * 100)
            calls_count = sum(1 for c in self.calls if c['provider'] == provider)
            avg_per_call = spend / calls_count if calls_count > 0 else 0
            provider_rows.append([
                provider.capitalize(),
                f"${spend:,.2f}",
                f"{pct:.1f}%",
                f"${avg_per_call:.4f}"
            ])
        generator.add_table(
            headers=["Provider", "Total Spend", "% of Total", "Avg per Call"],
            rows=provider_rows
        )
        
        # Spend by Model
        generator.add_section("Spend by Model", level=2)
        model_rows = []
        for model, spend in sorted(model_spend.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = (spend / total_spend * 100)
            calls_count = sum(1 for c in self.calls if c['model'] == model)
            model_rows.append([
                model,
                f"${spend:,.2f}",
                f"{pct:.1f}%",
                f"{calls_count:,}"
            ])
        generator.add_table(
            headers=["Model", "Total Spend", "% of Total", "Calls"],
            rows=model_rows
        )
        
        # Top 10 Customers
        generator.add_section("Top 10 Customers by Spend", level=2)
        customer_rows = []
        for customer, spend in sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:10]:
            calls_count = sum(1 for c in self.calls if c['customer_id'] == customer)
            avg_per_call = spend / calls_count if calls_count > 0 else 0
            customer_rows.append([
                customer,
                f"${spend:,.2f}",
                f"{calls_count:,}",
                f"${avg_per_call:.4f}"
            ])
        generator.add_table(
            headers=["Customer ID", "Total Spend", "Calls", "Avg per Call"],
            rows=customer_rows
        )
        
        # Cost Allocation Hierarchy
        generator.add_section("Cost Allocation Hierarchy", level=2)
        for org, products in sorted(hierarchy.items()):
            org_total = sum(sum(customers.values()) for customers in products.values())
            generator.add_section(f"{org} (${org_total:,.2f})", level=3)
            
            items = []
            for product, customers in sorted(products.items(), key=lambda x: sum(x[1].values()), reverse=True):
                product_total = sum(customers.values())
                items.append(f"<strong>{product}</strong>: ${product_total:,.2f} ({len(customers)} customers)")
            generator.add_list(items, ordered=False)
        
        # Token Efficiency Metrics
        generator.add_section("Token Efficiency Metrics", level=2)
        generator.add_metric_cards([
            {"label": "Total Input Tokens", "value": f"{efficiency['total_input_tokens']:,}"},
            {"label": "Total Output Tokens", "value": f"{efficiency['total_output_tokens']:,}"},
            {"label": "Total Tokens", "value": f"{efficiency['total_tokens']:,}"},
            {"label": "Avg Cost per 1K Tokens", "value": f"${efficiency['avg_cost_per_1k_tokens']:.4f}"},
            {"label": "Input/Output Ratio", "value": f"{efficiency['input_output_ratio']:.2f}"}
        ])
        
        # 30-Day Cost Forecast
        generator.add_section("30-Day Cost Forecast", level=2)
        generator.add_metric_cards([
            {"label": "Current Daily Average", "value": f"${forecast['current_daily_avg']:,.2f}"},
            {"label": "Linear Forecast (30 days)", "value": f"${forecast['forecast_30_day']:,.2f}"},
            {"label": "Growth Rate", "value": f"{forecast['growth_rate']*100:+.1f}%"},
            {"label": "Forecast with Growth", "value": f"${forecast['forecast_with_growth']:,.2f}"}
        ])
        
        if forecast['growth_rate'] > 0.1:
            generator.add_alert(
                f"⚠️ Cost growth rate is {forecast['growth_rate']*100:.1f}%. Expected increase of ${forecast['forecast_with_growth'] - forecast['forecast_30_day']:,.2f} over baseline.",
                alert_type='warning'
            )
        
        # Key Insights
        generator.add_section("Key Insights", level=2)
        top_provider = max(provider_spend.items(), key=lambda x: x[1])
        top_10_spend = sum(spend for _, spend in sorted(customer_spend.items(), key=lambda x: x[1], reverse=True)[:10])
        costs = [call['cost_usd'] for call in self.calls]
        max_cost = max(costs)
        min_cost = min(costs)
        
        insights = [
            f"<strong>{top_provider[0].capitalize()}</strong> accounts for {top_provider[1]/total_spend*100:.1f}% of total spend (${top_provider[1]:,.2f})",
            f"Top 10 customers represent {top_10_spend/total_spend*100:.1f}% of total spend (${top_10_spend:,.2f})",
            f"Cost per call ranges from ${min_cost:.4f} to ${max_cost:.4f} (variance indicates optimization opportunities)"
        ]
        generator.add_list(insights, ordered=True)
        
        # Recommendations
        generator.add_section("Recommendations", level=2)
        recommendations = [
            "<strong>Cost Allocation</strong>: Implement chargeback model based on organization/product hierarchy",
            "<strong>Customer Monitoring</strong>: Set up alerts for top 10 customers (70% of spend)",
            "<strong>Forecasting</strong>: Review monthly to adjust capacity planning",
            f"<strong>Budget Planning</strong>: Allocate ${forecast['forecast_with_growth']*1.1:,.2f}/month (10% buffer)"
        ]
        generator.add_list(recommendations, ordered=True)
        
        # Save HTML report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        generator.save(output_file)
        print(f"✓ Understanding Usage HTML report generated: {output_file}")


def main():
    """Main execution"""
    import os
    os.makedirs('reports', exist_ok=True)
    os.makedirs('reports/html', exist_ok=True)
    
    analyzer = UnderstandingUsageAnalyzer()
    
    # Generate markdown report
    analyzer.generate_report()
    
    # Generate HTML report if requested
    if os.environ.get('GENERATE_HTML'):
        analyzer.generate_html_report()


if __name__ == '__main__':
    main()
