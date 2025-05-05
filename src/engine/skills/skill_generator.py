# src/engine/skills/skill_generator.py
import random
import numpy as np
from typing import Dict, List, Optional

class SkillGenerator:
    def __init__(self):
        self.base_templates = {
            'offensive': {
                'damage_range': (100, 500),
                'cost_range': (20, 100),
                'cooldown_range': (5, 30)
            },
            'defensive': {
                'shield_range': (50, 300),
                'cost_range': (15, 80),
                'cooldown_range': (8, 25)
            },
            'utility': {
                'duration_range': (10, 60),
                'cost_range': (10, 50),
                'cooldown_range': (15, 45)
            }
        }
        
    def generate_skill(self, player_level: int, skill_type: str) -> Dict:
        template = self.base_templates[skill_type]
        power_scaling = 1 + (player_level - 50) * 0.1
        
        skill = {
            'id': f"{skill_type}_{random.randint(1000, 9999)}",
            'type': skill_type,
            'level_requirement': player_level,
            'evolution_paths': self._generate_evolution_paths(),
        }
        
        if skill_type == 'offensive':
            skill.update({
                'damage': random.randint(
                    int(template['damage_range'][0] * power_scaling),
                    int(template['damage_range'][1] * power_scaling)
                ),
                'cost': random.randint(*template['cost_range']),
                'cooldown': random.randint(*template['cooldown_range'])
            })
        elif skill_type == 'defensive':
            skill.update({
                'shield_value': random.randint(
                    int(template['shield_range'][0] * power_scaling),
                    int(template['shield_range'][1] * power_scaling)
                ),
                'cost': random.randint(*template['cost_range']),
                'cooldown': random.randint(*template['cooldown_range'])
            })
        else:  # utility
            skill.update({
                'duration': random.randint(*template['duration_range']),
                'cost': random.randint(*template['cost_range']),
                'cooldown': random.randint(*template['cooldown_range'])
            })
            
        return skill
    
    def _generate_evolution_paths(self) -> List[Dict]:
        paths = []
        num_paths = random.randint(2, 3)
        
        for _ in range(num_paths):
            paths.append({
                'name': f"Evolution Path {_+1}",
                'requirements': {
                    'player_level': random.randint(55, 70),
                    'skill_uses': random.randint(100, 500)
                },
                'modifiers': {
                    'damage_mult': 1 + random.random() * 0.5,
                    'cooldown_reduction': random.randint(5, 20) / 100,
                    'cost_reduction': random.randint(5, 15) / 100
                }
            })
        
        return paths

    def combine_skills(self, skill1: Dict, skill2: Dict) -> Optional[Dict]:
        if skill1['type'] != skill2['type']:
            return None
            
        new_skill = {
            'id': f"combined_{random.randint(1000, 9999)}",
            'type': skill1['type'],
            'level_requirement': max(skill1['level_requirement'], skill2['level_requirement']),
            'evolution_paths': self._generate_evolution_paths()
        }
        
        # Combine relevant stats based on skill type
        if skill1['type'] == 'offensive':
            new_skill['damage'] = int((skill1['damage'] + skill2['damage']) * 1.2)
            new_skill['cost'] = int((skill1['cost'] + skill2['cost']) * 0.8)
            new_skill['cooldown'] = min(skill1['cooldown'], skill2['cooldown'])
        
        return new_skill