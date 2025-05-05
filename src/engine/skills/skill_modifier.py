# src/engine/skills/skill_modifier.py
from enum import Enum
from dataclasses import dataclass
from typing import Callable, List
from .skill_types import Skill, Effect

class ModifierType(Enum):
    DAMAGE_BOOST = "damage_boost"
    AREA_INCREASE = "area_increase"
    DURATION_EXTEND = "duration_extend"
    COST_REDUCTION = "cost_reduction"
    EFFECT_ADD = "effect_add"
    CHAIN_EFFECT = "chain_effect"

@dataclass
class ScalingFunction:
    base_value: float
    scaling_factor: float
    max_value: float
    
    def calculate(self, paragon_level: int) -> float:
        scaled = self.base_value + (paragon_level * self.scaling_factor)
        return min(scaled, self.max_value)

class SkillModifier:
    def __init__(self, 
                 modifier_type: ModifierType,
                 scaling: ScalingFunction,
                 effects: List[Effect],
                 weight_function: Callable[[int], float]):
        self.type = modifier_type
        self.scaling = scaling
        self.effects = effects
        self.weight_function = weight_function
        
    def apply(self, skill: Skill, paragon_level: int) -> None:
        modifier_value = self.scaling.calculate(paragon_level)
        
        if self.type == ModifierType.DAMAGE_BOOST:
            self._apply_damage_boost(skill, modifier_value)
        elif self.type == ModifierType.AREA_INCREASE:
            self._apply_area_increase(skill, modifier_value)
        elif self.type == ModifierType.DURATION_EXTEND:
            self._apply_duration_extend(skill, modifier_value)
        elif self.type == ModifierType.COST_REDUCTION:
            self._apply_cost_reduction(skill, modifier_value)
        elif self.type == ModifierType.EFFECT_ADD:
            self._apply_effect_add(skill, modifier_value)
        elif self.type == ModifierType.CHAIN_EFFECT:
            self._apply_chain_effect(skill, modifier_value)
            
    def get_weight(self, paragon_level: int) -> float:
        return self.weight_function(paragon_level)
        
    def _apply_damage_boost(self, skill: Skill, value: float) -> None:
        for effect in skill.effects:
            effect.power *= (1 + value)
            
    def _apply_area_increase(self, skill: Skill, value: float) -> None:
        for effect in skill.effects:
            if hasattr(effect, 'area'):
                effect.area *= (1 + value)
                
    def _apply_duration_extend(self, skill: Skill, value: float) -> None:
        for effect in skill.effects:
            if hasattr(effect, 'duration'):
                effect.duration *= (1 + value)
                
    def _apply_cost_reduction(self, skill: Skill, value: float) -> None:
        skill.resource_cost.amount *= (1 - min(value, 0.75))
        
    def _apply_effect_add(self, skill: Skill, value: float) -> None:
        for effect in self.effects:
            new_effect = effect.copy()
            new_effect.power *= value
            skill.effects.append(new_effect)
            
    def _apply_chain_effect(self, skill: Skill, value: float) -> None:
        skill.chain_count = max(1, int(value))
        for effect in skill.effects:
            effect.can_chain = True