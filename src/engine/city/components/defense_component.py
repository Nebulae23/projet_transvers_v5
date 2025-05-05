import dataclasses
from typing import Dict, List

@dataclasses.dataclass
class DefenseComponent:
    """
    Component managing defensive capabilities for buildings or units.
    """
    defense_points: float = 100.0  # Current structural integrity or shield points
    max_defense_points: float = 100.0 # Maximum defense points
    resistance: Dict[str, float] = dataclasses.field(default_factory=dict) # Resistance percentages (0.0 to 1.0), e.g., {"physical": 0.1, "fire": 0.5}

    # Offensive capabilities (if the structure can attack)
    can_attack: bool = False
    attack_range: float = 0.0  # Range in grid units or world units
    base_damage: float = 10.0 # Base damage per attack
    attack_speed: float = 1.0 # Attacks per second
    damage_types: List[str] = dataclasses.field(default_factory=list) # e.g., ["physical", "piercing"]
    ammunition: int = -1  # Current ammunition count (-1 for infinite)
    max_ammunition: int = -1 # Maximum ammunition capacity (-1 for infinite)
    priority_targets: List[str] = dataclasses.field(default_factory=list) # List of entity type IDs to prioritize targeting

    def take_damage(self, amount: float, damage_type: str = "physical"):
        """Applies damage, considering resistance."""
        resistance_multiplier = 1.0 - self.resistance.get(damage_type, 0.0)
        actual_damage = amount * resistance_multiplier
        self.defense_points = max(0.0, self.defense_points - actual_damage)

    def repair(self, amount: float):
        """Repairs the defense points."""
        self.defense_points = min(self.max_defense_points, self.defense_points + amount)

    def can_fire(self) -> bool:
        """Checks if the entity can fire (has ammo or infinite ammo)."""
        return self.can_attack and (self.ammunition > 0 or self.ammunition == -1)

    def consume_ammo(self):
        """Consumes one unit of ammo if not infinite."""
        if self.can_attack and self.ammunition > 0:
            self.ammunition -= 1