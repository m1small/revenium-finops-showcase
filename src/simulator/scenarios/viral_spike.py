#!/usr/bin/env python3
"""
Viral Spike Scenario
Simulates sudden explosive growth in usage (e.g., viral feature, press coverage)
"""

import random
from typing import Dict, Any


class ViralSpikeScenario:
    """Applies viral spike pattern to customer usage"""
    
    def __init__(self, spike_day: int = 15, spike_multiplier: float = 10.0):
        """
        Initialize viral spike scenario
        
        Args:
            spike_day: Day when spike occurs
            spike_multiplier: Usage multiplier at peak (default 10x)
        """
        self.spike_day = spike_day
        self.spike_multiplier = spike_multiplier
    
    def apply(self, customer: Dict[str, Any], day: int) -> Dict[str, Any]:
        """
        Apply viral spike pattern to customer for given day
        
        Args:
            customer: Customer profile dict
            day: Day number in simulation
            
        Returns:
            Modified customer profile with adjusted calls_per_day
        """
        if day < self.spike_day:
            # Normal usage before spike
            return customer
        elif day == self.spike_day:
            # Spike day - 10x usage
            customer['calls_per_day'] = int(customer['calls_per_day'] * self.spike_multiplier)
        elif day < self.spike_day + 3:
            # Immediate aftermath - still elevated (5x)
            customer['calls_per_day'] = int(customer['calls_per_day'] * (self.spike_multiplier / 2))
        else:
            # Gradual decline to new normal (2x baseline)
            days_since_spike = day - self.spike_day
            decay_factor = max(2.0, self.spike_multiplier * (0.8 ** (days_since_spike - 3)))
            customer['calls_per_day'] = int(customer['calls_per_day'] * decay_factor)
        
        return customer
    
    def description(self) -> str:
        """Return scenario description"""
        return f"Viral spike on day {self.spike_day} with {self.spike_multiplier}x multiplier"
