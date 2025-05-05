# src/engine/skills/class_skill_manager.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from .skill_types import Skill
from .skill_generator import SkillGenerator

@dataclass
class SkillBranch:
    id: str
    level: int
    skills: List[Skill]
    unlocked: bool = False

class ClassSkillManager:
    def __init__(self, skill_generator: SkillGenerator):
        self.skill_generator = skill_generator
        self.principal_skills: Dict[str, Dict[str, SkillBranch]] = {}
        self.procedural_skills: List[Skill] = []
        self.max_procedural_skills = 10
        
    def initialize_class(self, class_type: str) -> None:
        self.principal_skills[class_type] = {}
        
    def add_principal_skill(self, class_type: str, skill_id: str, 
                          branches: List[SkillBranch]) -> None:
        if class_type not in self.principal_skills:
            self.initialize_class(class_type)
            
        self.principal_skills[class_type][skill_id] = {
            branch.id: branch for branch in branches
        }
        
    def unlock_branch(self, class_type: str, skill_id: str, 
                     branch_id: str) -> bool:
        if (class_type not in self.principal_skills or 
            skill_id not in self.principal_skills[class_type] or
            branch_id not in self.principal_skills[class_type][skill_id]):
            return False
            
        branch = self.principal_skills[class_type][skill_id][branch_id]
        if branch.unlocked:
            return False
            
        branch.unlocked = True
        return True
        
    def get_available_skills(self, class_type: str, level: int) -> List[Skill]:
        available = []
        
        # Add principal skills
        if class_type in self.principal_skills:
            for skill_branches in self.principal_skills[class_type].values():
                for branch in skill_branches.values():
                    if branch.unlocked and branch.level <= level:
                        available.extend(branch.skills)
                        
        # Add procedural skills if level > 50
        if level > 50:
            available.extend(self.procedural_skills)
            
        return available
        
    def try_generate_procedural_skill(self, class_type: str, 
                                    paragon_level: int) -> Optional[Skill]:
        if len(self.procedural_skills) >= self.max_procedural_skills:
            return None
            
        new_skill = self.skill_generator.generate_skill(class_type, paragon_level)
        if new_skill:
            self.procedural_skills.append(new_skill)
            
        return new_skill
        
    def remove_procedural_skill(self, skill_id: str) -> bool:
        for i, skill in enumerate(self.procedural_skills):
            if skill.id == skill_id:
                self.procedural_skills.pop(i)
                return True
        return False