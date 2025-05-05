# src/engine/combat/enemy.py
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
from .combat_fx import CombatEffects

class PsychologicalState(Enum):
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"
    FEARFUL = "fearful"
    CONFUSED = "confused"
    ENRAGED = "enraged"

@dataclass
class StateEffect:
    damage_multiplier: float
    defense_multiplier: float
    speed_multiplier: float
    visual_effect: str
    particle_color: tuple
    
class Enemy:
    STATE_EFFECTS = {
        PsychologicalState.NORMAL: StateEffect(1.0, 1.0, 1.0, "none", (1.0, 1.0, 1.0)),
        PsychologicalState.AGGRESSIVE: StateEffect(1.5, 0.8, 1.2, "red_aura", (1.0, 0.2, 0.2)),
        PsychologicalState.FEARFUL: StateEffect(0.7, 0.7, 1.5, "blue_mist", (0.2, 0.2, 1.0)),
        PsychologicalState.CONFUSED: StateEffect(0.8, 0.8, 0.8, "swirl", (0.8, 0.2, 0.8)),
        PsychologicalState.ENRAGED: StateEffect(2.0, 0.5, 1.3, "flame", (1.0, 0.4, 0.0))
    }
    
    def __init__(self, enemy_type: str, level: int):
        self.type = enemy_type
        self.level = level
        self.health = 100 * level
        self.max_health = self.health
        self.state = PsychologicalState.NORMAL
        self.state_duration = 0
        self.fx_system = CombatEffects()
        
        # HD-2D specific properties
        self.state_indicator_mesh = None
        self.current_visual_effect = None
        self.particle_emitter = None
        self.animation_state = "idle"
        self.animation_frame = 0
        
    def update(self, dt: float):
        # Update psychological state
        if self.state_duration > 0:
            self.state_duration -= dt
            if self.state_duration <= 0:
                self.change_state(PsychologicalState.NORMAL)
                
        # Update visual effects
        if self.current_visual_effect:
            self.fx_system.update_effect(self.current_visual_effect, dt)
            
        # Update particle effects
        if self.particle_emitter:
            self.particle_emitter.update(dt)
            
        # Update animation
        self.animation_frame = (self.animation_frame + dt * 10) % 8
        
    def change_state(self, new_state: PsychologicalState, duration: float = 5.0):
        self.state = new_state
        self.state_duration = duration
        
        # Update visual effects
        effect = self.STATE_EFFECTS[new_state]
        if effect.visual_effect != "none":
            self.current_visual_effect = self.fx_system.create_effect(
                effect.visual_effect,
                effect.particle_color
            )
            
    def take_damage(self, amount: float) -> float:
        # Apply state modifiers
        effect = self.STATE_EFFECTS[self.state]
        modified_damage = amount / effect.defense_multiplier
        
        self.health = max(0, self.health - modified_damage)
        if self.health < self.max_health * 0.3 and self.state != PsychologicalState.ENRAGED:
            self.change_state(PsychologicalState.ENRAGED)
            
        return modified_damage
        
    def deal_damage(self, base_damage: float) -> float:
        effect = self.STATE_EFFECTS[self.state]
        return base_damage * effect.damage_multiplier