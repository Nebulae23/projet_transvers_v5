# src/engine/skills/skill_template.py
from typing import List, Dict
from dataclasses import dataclass
from .skill_types import Skill, SkillType, Effect, ResourceCost

@dataclass
class SkillTemplate:
    id: str
    name: str
    skill_type: SkillType
    base_effects: List[Effect]
    class_restrictions: List[str]
    resource_cost: ResourceCost
    description_template: str
    visual_effects: Dict[str, dict]
    
    def create_skill(self) -> Skill:
        return Skill(
            id=f"{self.id}_{hash(self)}",
            name=self.name,
            skill_type=self.skill_type,
            effects=[effect.copy() for effect in self.base_effects],
            resource_cost=self.resource_cost.copy(),
            description=self.description_template,
            visual_effects=dict(self.visual_effects)
        )
        
    def validate_for_class(self, class_type: str) -> bool:
        return class_type in self.class_restrictions
        
    def estimate_power_level(self) -> float:
        total_power = sum(effect.power for effect in self.base_effects)
        return total_power / self.resource_cost.amount