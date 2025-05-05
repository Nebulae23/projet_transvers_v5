import dataclasses
from typing import Dict

@dataclasses.dataclass
class ResourceComponent:
    """
    Component managing resources for an entity (e.g., a city or building).
    """
    # Current amount of each resource type
    current_resources: Dict[str, float] = dataclasses.field(default_factory=lambda: {"wood": 0.0, "stone": 0.0, "gold": 0.0, "food": 0.0})

    # Maximum storage capacity for each resource type
    storage_capacity: Dict[str, float] = dataclasses.field(default_factory=lambda: {"wood": 1000.0, "stone": 1000.0, "gold": 5000.0, "food": 500.0})

    # Net production rate per second (positive for production, negative for consumption)
    production_rates: Dict[str, float] = dataclasses.field(default_factory=lambda: {"wood": 0.0, "stone": 0.0, "gold": 0.0, "food": 0.0})

    # Modifiers affecting production rates (e.g., technology bonus, event malus)
    # Example: {"wood": 1.1} means 10% bonus to wood production
    production_modifiers: Dict[str, float] = dataclasses.field(default_factory=lambda: {"wood": 1.0, "stone": 1.0, "gold": 1.0, "food": 1.0})

    def get_effective_production_rate(self, resource_type: str) -> float:
        """Calculates the effective production rate including modifiers."""
        base_rate = self.production_rates.get(resource_type, 0.0)
        modifier = self.production_modifiers.get(resource_type, 1.0)
        return base_rate * modifier

    def can_afford(self, costs: Dict[str, float]) -> bool:
        """Checks if the entity has enough resources to cover the costs."""
        for resource, amount in costs.items():
            if self.current_resources.get(resource, 0.0) < amount:
                return False
        return True

    def add_resources(self, resources: Dict[str, float]):
        """Adds resources, respecting storage capacity."""
        for resource, amount in resources.items():
            if resource in self.current_resources:
                current = self.current_resources[resource]
                capacity = self.storage_capacity.get(resource, float('inf'))
                self.current_resources[resource] = min(current + amount, capacity)

    def spend_resources(self, costs: Dict[str, float]) -> bool:
        """Spends resources if affordable."""
        if self.can_afford(costs):
            for resource, amount in costs.items():
                self.current_resources[resource] -= amount
            return True
        return False