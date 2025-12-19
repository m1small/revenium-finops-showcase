#!/usr/bin/env python3
"""
Steady Growth Scenario
Simulates predictable, linear growth in AI usage over time
"""

import random
from typing import Dict, Any


class SteadyGrowthScenario:
    """Applies steady growth pattern to customer usage"""
    
    def __init__(self, growth_rate: float = 0.05):
        """
        Initialize steady growth scenario
        
        Args:
            growth_rate: Daily growth rate (default 5% per week = ~0.7% per day)
        """
        self.growth_rate = growth_rate / 7  # Convert weekly to daily
    
    def apply(self, customer: Dict[str, Any], day: int) -> Dict[str, Any]:
        """
        Apply growth pattern to customer for given day
        
        Args:
            customer: Customer profile dict
            day: Day number in simulation
            
        Returns:
            Modified customer profile with adjusted calls_per_day
        """
        growth_factor = 1 + (self.growth_rate * day)
        customer['calls_per_day'] = int(customer['calls_per_day'] * growth_factor)
        return customer
    
    def description(self) -> str:
        """Return scenario description"""
        return f"Steady growth at {self.growth_rate * 7 * 100:.1f}% per week"
