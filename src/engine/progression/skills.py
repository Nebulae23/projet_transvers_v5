# src/engine/progression/skills.py
from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

class SkillType(Enum):
    COMBAT = "combat"
    DEFENSE = "defense"
    UTILITY = "utility"
    PASSIVE = "passive"

@dataclass
class SkillNode:
    id: str
    name: str
    description: str
    skill_type: SkillType
    cost: int  # Skill points required
    prerequisites: List[str]  # List of required skill IDs
    effects: Dict[str, float]  # Effect type -> value mapping
    icon_path: str
    position: tuple  # (x, y) position in skill tree UI

class SkillTree:
    def __init__(self):
        self.nodes: Dict[str, SkillNode] = {}
        self.unlocked_skills: Set[str] = set()
        self.available_points = 0
        self._initialize_skills()
        
    def _initialize_skills(self):
        # Combat skills
        self.nodes["basic_strike"] = SkillNode(
            "basic_strike",
            "Basic Strike",
            "Improve basic attack damage",
            SkillType.COMBAT,
            1,
            [],
            {"attack_damage": 10},
            "assets/skills/basic_strike.png",
            (0, 0)
        )
        
        self.nodes["power_strike"] = SkillNode(
            "power_strike",
            "Power Strike",
            "Powerful attack with bonus damage",
            SkillType.COMBAT,
            2,
            ["basic_strike"],
            {"special_damage": 25},
            "assets/skills/power_strike.png",
            (1, 0)
        )
        
        # Defense skills
        self.nodes["toughness"] = SkillNode(
            "toughness",
            "Toughness",
            "Increase maximum health",
            SkillType.DEFENSE,
            1,
            [],
            {"max_health": 50},
            "assets/skills/toughness.png",
            (0, 1)
        )
        
        # Add more skills as needed...
        
    def add_skill_points(self, amount: int):
        self.available_points += amount
        
    def can_unlock(self, skill_id: str) -> bool:
        if skill_id not in self.nodes:
            return False
            
        skill = self.nodes[skill_id]
        
        # Check if already unlocked
        if skill_id in self.unlocked_skills:
            return False
            
        # Check prerequisites
        for prereq in skill.prerequisites:
            if prereq not in self.unlocked_skills:
                return False
                
        # Check points
        return self.available_points >= skill.cost
        
    def unlock_skill(self, skill_id: str) -> bool:
        if not self.can_unlock(skill_id):
            return False
            
        skill = self.nodes[skill_id]
        self.available_points -= skill.cost
        self.unlocked_skills.add(skill_id)
        return True
        
    def get_skill_effects(self) -> Dict[str, float]:
        """Get combined effects of all unlocked skills"""
        effects = {}
        for skill_id in self.unlocked_skills:
            skill = self.nodes[skill_id]
            for effect, value in skill.effects.items():
                effects[effect] = effects.get(effect, 0) + value
        return effects