# src/engine/progression/stats.py
from typing import Dict, List, Callable
from dataclasses import dataclass
from enum import Enum

class StatType(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    VITALITY = "vitality"
    INTELLIGENCE = "intelligence"

@dataclass
class StatInfo:
    name: str
    description: str
    base_value: float
    value_per_point: float
    effects: Dict[str, float]  # Effect type -> multiplier

class CharacterStats:
    def __init__(self):
        self.stats: Dict[StatType, StatInfo] = {}
        self.stat_points = 0
        self.stat_values: Dict[StatType, int] = {stat: 0 for stat in StatType}
        self.on_stat_changed: List[Callable[[], None]] = []
        self._initialize_stats()
        
    def _initialize_stats(self):
        self.stats[StatType.STRENGTH] = StatInfo(
            "Strength",
            "Increases physical damage and carrying capacity",
            10.0,
            2.0,
            {"attack_damage": 0.1, "carry_weight": 5.0}
        )
        
        self.stats[StatType.DEXTERITY] = StatInfo(
            "Dexterity",
            "Improves attack speed and dodge chance",
            10.0,
            1.5,
            {"attack_speed": 0.05, "dodge_chance": 0.01}
        )
        
        self.stats[StatType.VITALITY] = StatInfo(
            "Vitality",
            "Increases health and health regeneration",
            10.0,
            3.0,
            {"max_health": 10.0, "health_regen": 0.1}
        )
        
        self.stats[StatType.INTELLIGENCE] = StatInfo(
            "Intelligence",
            "Improves skill effectiveness and mana",
            10.0,
            1.5,
            {"skill_power": 0.05, "max_mana": 5.0}
        )
        
    def add_stat_points(self, amount: int):
        self.stat_points += amount
        
    def can_increase_stat(self, stat_type: StatType) -> bool:
        return self.stat_points > 0
        
    def increase_stat(self, stat_type: StatType) -> bool:
        if not self.can_increase_stat(stat_type):
            return False
            
        self.stat_points -= 1
        self.stat_values[stat_type] += 1
        
        # Notify listeners
        for callback in self.on_stat_changed:
            callback()
            
        return True
        
    def get_stat_value(self, stat_type: StatType) -> float:
        """Get total value for a stat including base value"""
        if stat_type not in self.stats:
            return 0.0
            
        stat_info = self.stats[stat_type]
        return stat_info.base_value + (stat_info.value_per_point * self.stat_values[stat_type])
        
    def get_stat_effects(self) -> Dict[str, float]:
        """Get combined effects of all stats"""
        effects = {}
        for stat_type, stat_info in self.stats.items():
            stat_value = self.stat_values[stat_type]
            for effect, multiplier in stat_info.effects.items():
                effects[effect] = effects.get(effect, 0) + (stat_value * multiplier)
        return effects
        
    def register_stat_changed_callback(self, callback: Callable[[], None]):
        self.on_stat_changed.append(callback)