# src/engine/combat/dodge_system.py
import time
from typing import Dict, Tuple

class DodgeSystem:
    def __init__(self):
        self.dodge_cooldown = 1.0  # seconds
        self.iframe_duration = 0.3  # seconds
        self.dodge_distance = 5.0   # units
        self.stamina_cost = 20
        
        self._last_dodge_time = 0
        self._current_iframe = False
        self._dodge_direction = (0, 0)
        
    def start_dodge(self, entity: any, direction: Tuple[float, float]) -> bool:
        current_time = time.time()
        
        # Check cooldown and stamina
        if (current_time - self._last_dodge_time < self.dodge_cooldown or
            entity.stats.stamina < self.stamina_cost):
            return False
            
        # Normalize direction
        magnitude = (direction[0]**2 + direction[1]**2)**0.5
        if magnitude == 0:
            return False
            
        self._dodge_direction = (
            direction[0] / magnitude,
            direction[1] / magnitude
        )
        
        # Apply dodge
        entity.stats.stamina -= self.stamina_cost
        entity.position = (
            entity.position[0] + self._dodge_direction[0] * self.dodge_distance,
            entity.position[1] + self._dodge_direction[1] * self.dodge_distance
        )
        
        # Start iframe
        self._current_iframe = True
        self._last_dodge_time = current_time
        
        # Trigger dodge animation
        self._play_dodge_animation(entity)
        
        return True
        
    def update(self, delta_time: float) -> None:
        if self._current_iframe:
            current_time = time.time()
            if current_time - self._last_dodge_time >= self.iframe_duration:
                self._current_iframe = False
                
    def is_invulnerable(self) -> bool:
        return self._current_iframe
        
    def _play_dodge_animation(self, entity: any) -> None:
        if hasattr(entity, 'animator'):
            entity.animator.play_animation(
                'dodge',
                blend_time=0.1,
                speed=1.5,
                direction=self._dodge_direction
            )