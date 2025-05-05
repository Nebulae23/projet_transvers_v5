# src/engine/combat/ability_system.py
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from .combat_fx import CombatEffects, ParticleEmitter

class AbilityType(Enum):
    PHYSICAL = "physical"
    MAGICAL = "magical"
    HYBRID = "hybrid"
    BUFF = "buff"
    DEBUFF = "debuff"
    SUMMON = "summon"

@dataclass
class AbilityEffect:
    damage: float
    duration: float
    particle_color: tuple
    visual_effect: str

class Ability:
    def __init__(self, name: str, base_power: float, cooldown: float, 
                ability_type: AbilityType, fx_type: str):
        self.name = name
        self.base_power = base_power
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.type = ability_type
        self.fx_type = fx_type
        self.level = 1
        self.fx_system = CombatEffects()
        
class AbilityFusion:
    def __init__(self):
        self.fx_system = CombatEffects()
        self.active_fusions: Dict[str, Tuple[Ability, Ability, AbilityEffect]] = {}
        self.available_patterns = {
            (AbilityType.PHYSICAL, AbilityType.MAGICAL): self._create_spellstrike_fusion,
            (AbilityType.MAGICAL, AbilityType.MAGICAL): self._create_spell_fusion,
            (AbilityType.PHYSICAL, AbilityType.PHYSICAL): self._create_combat_fusion,
            (AbilityType.MAGICAL, AbilityType.BUFF): self._create_enchanted_fusion,
        }
        
    def create_fusion(self, ability1: Ability, ability2: Ability) -> Optional[AbilityEffect]:
        key = (ability1.type, ability2.type)
        if key in self.available_patterns:
            fusion = self.available_patterns[key](ability1, ability2)
            fusion_id = f"fusion_{ability1.name}_{ability2.name}"
            self.active_fusions[fusion_id] = (ability1, ability2, fusion)
            return fusion
        return None
        
    def _create_spellstrike_fusion(self, physical: Ability, magical: Ability) -> AbilityEffect:
        damage = (physical.base_power + magical.base_power) * 1.5
        duration = max(physical.cooldown, magical.cooldown) * 0.7
        
        # Create unique particle color blend
        color1 = np.array(self.fx_system.get_ability_color(physical.fx_type))
        color2 = np.array(self.fx_system.get_ability_color(magical.fx_type))
        blend_color = tuple(np.sqrt((color1**2 + color2**2) / 2))
        
        return AbilityEffect(
            damage=damage,
            duration=duration,
            particle_color=blend_color,
            visual_effect="spellstrike_fusion"
        )
        
    def _create_spell_fusion(self, spell1: Ability, spell2: Ability) -> AbilityEffect:
        damage = (spell1.base_power + spell2.base_power) * 1.3
        duration = (spell1.cooldown + spell2.cooldown) * 0.6
        
        color1 = np.array(self.fx_system.get_ability_color(spell1.fx_type))
        color2 = np.array(self.fx_system.get_ability_color(spell2.fx_type))
        blend_color = tuple((color1 + color2) / 2)
        
        return AbilityEffect(
            damage=damage,
            duration=duration,
            particle_color=blend_color,
            visual_effect="spell_fusion"
        )
        
    def _create_combat_fusion(self, combat1: Ability, combat2: Ability) -> AbilityEffect:
        damage = (combat1.base_power + combat2.base_power) * 1.4
        duration = min(combat1.cooldown, combat2.cooldown) * 0.8
        
        color1 = np.array(self.fx_system.get_ability_color(combat1.fx_type))
        color2 = np.array(self.fx_system.get_ability_color(combat2.fx_type))
        blend_color = tuple(np.maximum(color1, color2))
        
        return AbilityEffect(
            damage=damage,
            duration=duration,
            particle_color=blend_color,
            visual_effect="combat_fusion"
        )
        
    def _create_enchanted_fusion(self, spell: Ability, buff: Ability) -> AbilityEffect:
        damage = spell.base_power * 1.8
        duration = (spell.cooldown + buff.cooldown) * 0.5
        
        color1 = np.array(self.fx_system.get_ability_color(spell.fx_type))
        color2 = np.array(self.fx_system.get_ability_color(buff.fx_type))
        blend_color = tuple(np.clip(color1 + color2 * 0.5, 0, 1))
        
        return AbilityEffect(
            damage=damage,
            duration=duration,
            particle_color=blend_color,
            visual_effect="enchanted_fusion"
        )
        
    def update_fusions(self, dt: float):
        completed_fusions = []
        for fusion_id, (ability1, ability2, effect) in self.active_fusions.items():
            effect.duration -= dt
            if effect.duration <= 0:
                completed_fusions.append(fusion_id)
                
        for fusion_id in completed_fusions:
            del self.active_fusions[fusion_id]