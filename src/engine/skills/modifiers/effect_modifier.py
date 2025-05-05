# src/engine/skills/modifiers/effect_modifier.py
from typing import Dict, List, Any
from .base_modifier import BaseModifier

class EffectModifier(BaseModifier):
    def __init__(self, name: str, effect_type: str, power: float):
        super().__init__(name, power)
        self.effect_type = effect_type
        self.particles = []
        self.visual_effects = []
        
    def apply(self, target: Any) -> None:
        if hasattr(target, 'effects'):
            effect = {
                'type': self.effect_type,
                'power': self.power,
                'duration': self.duration
            }
            target.effects.append(effect)
            self._apply_visual_effects(target)
            
    def remove(self, target: Any) -> None:
        if hasattr(target, 'effects'):
            target.effects = [effect for effect in target.effects 
                            if effect['type'] != self.effect_type]
            self._remove_visual_effects()
            
    def _apply_visual_effects(self, target: Any) -> None:
        if self.effect_type == 'burn':
            self.particles = self._create_fire_particles()
        elif self.effect_type == 'freeze':
            self.particles = self._create_ice_particles()
            
    def _remove_visual_effects(self) -> None:
        for particle in self.particles:
            particle.fade_out()
        self.particles.clear()
            
    def _create_fire_particles(self) -> List:
        return [
            {
                'type': 'fire',
                'color': (255, 100, 0),
                'size': 2.0,
                'lifetime': 1.0,
                'emission_rate': 20
            }
        ]
        
    def _create_ice_particles(self) -> List:
        return [
            {
                'type': 'ice',
                'color': (200, 220, 255),
                'size': 1.5,
                'lifetime': 0.8,
                'emission_rate': 15
            }
        ]