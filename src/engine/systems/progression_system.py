# src/engine/systems/progression_system.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import math
from enum import Enum

class ParagonStat(Enum):
    STRENGTH = "strength"
    VITALITY = "vitality"
    INTELLIGENCE = "intelligence"
    DEXTERITY = "dexterity"
    LUCK = "luck"

@dataclass
class ParagonBonus:
    stat: ParagonStat
    value: float
    cost: int

class ProgressionSystem:
    def __init__(self):
        self.max_level = 50
        self.paragon_level = 0
        self.paragon_points = 0
        self.paragon_points_spent: Dict[ParagonStat, int] = {
            stat: 0 for stat in ParagonStat
        }
        self.stat_bonuses: Dict[ParagonStat, float] = {
            stat: 0.0 for stat in ParagonStat
        }

    def gain_experience(self, exp: int) -> bool:
        if self.paragon_level >= 1000:  # Maximum paragon level
            return False

        required_exp = self._calculate_paragon_exp_required()
        if exp >= required_exp:
            self.paragon_level += 1
            self.paragon_points += 1
            return True
        return False

    def _calculate_paragon_exp_required(self) -> int:
        # Experience curve for paragon levels
        base_exp = 100000  # Base exp for first paragon level
        return int(base_exp * math.pow(1.1, self.paragon_level))

    def get_available_bonuses(self) -> List[ParagonBonus]:
        bonuses = []
        for stat in ParagonStat:
            points_invested = self.paragon_points_spent[stat]
            next_bonus = self._calculate_next_bonus(stat, points_invested)
            cost = self._calculate_bonus_cost(points_invested)
            bonuses.append(ParagonBonus(stat, next_bonus, cost))
        return bonuses

    def _calculate_next_bonus(self, stat: ParagonStat, points: int) -> float:
        # Different stats have different scaling
        base_value = {
            ParagonStat.STRENGTH: 0.01,      # 1% per point
            ParagonStat.VITALITY: 0.01,      # 1% per point
            ParagonStat.INTELLIGENCE: 0.01,  # 1% per point
            ParagonStat.DEXTERITY: 0.005,    # 0.5% per point
            ParagonStat.LUCK: 0.002,         # 0.2% per point
        }[stat]
        
        # Diminishing returns after certain thresholds
        if points < 10:
            return base_value
        elif points < 20:
            return base_value * 0.8
        else:
            return base_value * 0.5

    def _calculate_bonus_cost(self, points: int) -> int:
        # Increasing cost for each point invested
        return 1 + points // 5

    def purchase_bonus(self, stat: ParagonStat) -> bool:
        if stat not in self.paragon_points_spent:
            return False

        points_invested = self.paragon_points_spent[stat]
        cost = self._calculate_bonus_cost(points_invested)
        
        if self.paragon_points >= cost:
            self.paragon_points -= cost
            self.paragon_points_spent[stat] += 1
            bonus = self._calculate_next_bonus(stat, points_invested)
            self.stat_bonuses[stat] += bonus
            return True
        return False

    def get_total_bonus(self, stat: ParagonStat) -> float:
        return self.stat_bonuses.get(stat, 0.0)

    def reset_paragon_points(self):
        refund = sum(self.paragon_points_spent.values())
        self.paragon_points += refund
        self.paragon_points_spent = {stat: 0 for stat in ParagonStat}
        self.stat_bonuses = {stat: 0.0 for stat in ParagonStat}

    def save_state(self) -> dict:
        return {
            "paragon_level": self.paragon_level,
            "paragon_points": self.paragon_points,
            "points_spent": {stat.value: points for stat, points in self.paragon_points_spent.items()},
            "bonuses": {stat.value: bonus for stat, bonus in self.stat_bonuses.items()}
        }

    def load_state(self, data: dict):
        self.paragon_level = data.get("paragon_level", 0)
        self.paragon_points = data.get("paragon_points", 0)
        self.paragon_points_spent = {
            ParagonStat(stat): points 
            for stat, points in data.get("points_spent", {}).items()
        }
        self.stat_bonuses = {
            ParagonStat(stat): bonus 
            for stat, bonus in data.get("bonuses", {}).items()
        }