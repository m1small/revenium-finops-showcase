"""
Revenium Chart Builder

Multi-dimensional analysis with saved chart configurations.
"""

import uuid
from typing import List, Dict, Any


class ReveniumChartBuilder:
    """Build and save multi-dimensional analysis charts."""

    def __init__(self, api_key: str, workspace: str = "default"):
        """Initialize chart builder.

        Args:
            api_key: Revenium API key
            workspace: Workspace for chart sharing
        """
        self.api_key = api_key
        self.workspace = workspace

    def build_multi_dimensional_chart(
        self,
        dimensions: List[str],
        metrics: List[str],
        filters: Dict[str, Any],
        visualization_type: str,
        name: str,
        description: str = ""
    ) -> str:
        """Create a multi-dimensional chart configuration.

        Args:
            dimensions: List of dimensions to group by (e.g., ['organization_id', 'product_id', 'model'])
            metrics: List of metrics to aggregate (e.g., ['cost_usd', 'total_tokens'])
            filters: Filter criteria (e.g., {'environment': 'production'})
            visualization_type: Chart type ('treemap', 'sunburst', 'bar', 'line')
            name: Display name for the chart
            description: Optional description

        Returns:
            Chart ID
        """
        chart_id = str(uuid.uuid4())

        chart_config = {
            'chart_id': chart_id,
            'name': name,
            'description': description,
            'workspace': self.workspace,
            'dimensions': dimensions,
            'metrics': metrics,
            'filters': filters,
            'visualization_type': visualization_type,
            'created_at': '2025-12-22T00:00:00Z'
        }

        # In production: POST to Revenium API to save chart
        print(f"[Chart Builder] Created chart: {name}")
        print(f"  Dimensions: {' → '.join(dimensions)}")
        print(f"  Metrics: {', '.join(metrics)}")
        print(f"  Type: {visualization_type}")
        print(f"  ID: {chart_id}")

        return chart_id

    def get_chart(self, chart_id: str) -> Dict[str, Any]:
        """Retrieve saved chart configuration.

        Args:
            chart_id: Chart ID

        Returns:
            Chart configuration
        """
        # In production: GET from Revenium API
        return {
            'chart_id': chart_id,
            'name': 'Saved Chart',
            'status': 'active'
        }

    def list_workspace_charts(self) -> List[Dict[str, Any]]:
        """List all charts in workspace.

        Returns:
            List of chart configurations
        """
        # In production: GET from Revenium API
        return [
            {'chart_id': '1', 'name': 'Org-Product Cost Hierarchy'},
            {'chart_id': '2', 'name': 'Model Efficiency Comparison'},
            {'chart_id': '3', 'name': 'Customer Usage Trends'}
        ]


# Example usage
if __name__ == '__main__':
    builder = ReveniumChartBuilder(api_key="your-api-key", workspace="team-finops")

    # Example 1: Org → Product → Model cost hierarchy
    chart_id_1 = builder.build_multi_dimensional_chart(
        dimensions=['organization_id', 'product_id', 'model'],
        metrics=['cost_usd', 'total_tokens'],
        filters={'environment': 'production'},
        visualization_type='treemap',
        name='Org-Product-Model Cost Hierarchy',
        description='Hierarchical view of costs across organizations, products, and models'
    )

    print()

    # Example 2: Customer profitability by feature
    chart_id_2 = builder.build_multi_dimensional_chart(
        dimensions=['customer_id', 'feature_id'],
        metrics=['cost_usd', 'call_count'],
        filters={'subscription_tier': 'pro'},
        visualization_type='sunburst',
        name='Pro Tier Customer-Feature Analysis',
        description='Analyze feature usage and costs for Pro tier customers'
    )

    print()

    # Example 3: Time-series cost by provider
    chart_id_3 = builder.build_multi_dimensional_chart(
        dimensions=['timestamp', 'provider'],
        metrics=['cost_usd'],
        filters={},
        visualization_type='line',
        name='Provider Cost Trends Over Time',
        description='Track cost evolution across AI providers'
    )

    print()
    print("Charts created and saved to workspace. Team members can now access these views.")
