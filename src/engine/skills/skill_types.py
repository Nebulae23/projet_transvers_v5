# src/engine/skills/skill_types.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from copy import deepcopy

class SkillType(Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    UTILITY = "utility"
    MOVEMENT = "movement"
    BUFF = "buff"
    DEBUFF = "debuff"

class EffectType(Enum):
    DAMAGE = "damage"
    HEAL = "heal"
    SHIELD = "shield"
    STUN = "stun"
    SLOW = "slow"
    BOOST = "boost"
    DOT = "dot"  # Damage over time
    HOT = "hot"  # Heal over time

@dataclass
class ResourceCost:
    type: str  # mana, energy, rage, etc.
    amount: float
    
    def copy(self):
        return deepcopy(self)

@dataclass
class Effect:
    type: EffectType
    power: float
    duration: float = 0
    area: float = 0
    can_chain: bool = False
    
    def copy(self):
        return deepcopy(self)

@dataclass
class Skill:
    id: str
    name: str
    skill_type: SkillType
    effects: List[Effect]
    resource_cost: ResourceCost
    description: str
    visual_effects: Dict[str, dict]
    chain_count: int = 1
    
    def copy(self):
        return deepcopy(self)