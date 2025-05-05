# src/engine/combat/parry_system.py
import time
from typing import Dict, Optional

class ParrySystem:
    def __init__(self):
        self.parry_window = 0.15  # seconds
        self.parry_cooldown = 0.5  # seconds
        self.stamina_cost = 15
        self.perfect_parry_window = 0.05  # seconds
        
        self._parry_active = False
        self._last_parry_time = 0
        self._parry_start_time = 0
        
    def start_parry(self, entity: any) -> bool:
        current_time = time.time()
        
        # Check cooldown and stamina
        if (current_time - self._last_parry_time < self.parry_cooldown or
            entity.stats.stamina < self.stamina_cost):
            return False
            
        entity.stats.stamina -= self.stamina_cost
        self._parry_active = True
        self._parry_start_time = current_time
        self._last_parry_time = current_time
        
        # Trigger parry animation
        self._play_parry_animation(entity)
        
        return True
        
    def check_parry(self, attack_time: float) -> Dict[str, bool]:
        if not self._parry_active:
            return {'success': False, 'perfect': False}
            
        time_diff = abs(attack_time - self._parry_start_time)
        
        if time_diff <= self.perfect_parry_window:
            return {'success': True, 'perfect': True}
        elif time_diff <= self.parry_window:
            return {'success': True, 'perfect': False}
            
        return {'success': False, 'perfect': False}
        
    def update(self, delta_time: float) -> None:
        if self._parry_active:
            current_time = time.time()
            if current_time - self._parry_start_time >= self.parry_window:
                self._parry_active = False
                
    def _play_parry_animation(self, entity: any) -> None:
        if hasattr(entity, 'animator'):
            entity.animator.play_animation(
                'parry',
                blend_time=0.05,
                speed=1.2
            )
            
    def handle_successful_parry(self, entity: any, attacker: any, perfect: bool) -> None:
        # Stagger attacker
        if hasattr(attacker, 'stagger'):
            stagger_duration = 1.0 if perfect else 0.5
            attacker.stagger(stagger_duration)
            
        # Apply visual effects
        self._spawn_parry_effects(entity, perfect)
        
        # Perfect parry bonus
        if perfect:
            entity.stats.stamina += self.stamina_cost  # Refund stamina
            self._last_parry_time = 0  # Reset cooldown
            
    def _spawn_parry_effects(self, entity: any, perfect: bool) -> None:
        if hasattr(entity, 'fx_system'):
            effect = 'perfect_parry' if perfect else 'parry'
            entity.fx_system.spawn_effect(
                effect_type=effect,
                position=entity.position,
                scale=1.5 if perfect else 1.0,
                duration=0.5
            )