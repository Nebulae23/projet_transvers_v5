# src/engine/combat/boss.py
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
from .enemy import Enemy, PsychologicalState
from .combat_fx import CombatEffects, ParticleEmitter

class BossPhase(Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    FINAL = "final"

class BossAbility:
    def __init__(self, name: str, damage: float, cooldown: float, fx_type: str):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.fx_type = fx_type
        
class Boss(Enemy):
    def __init__(self, boss_type: str, level: int):
        super().__init__(boss_type, level)
        self.phase = BossPhase.PHASE_1
        self.phase_health_thresholds = {
            BossPhase.PHASE_2: 0.7,
            BossPhase.PHASE_3: 0.4,
            BossPhase.FINAL: 0.2
        }
        
        # Initialize epic visual effects
        self.fx_system = CombatEffects()
        self.phase_transitions = {
            BossPhase.PHASE_2: self.fx_system.create_phase_transition("power_surge"),
            BossPhase.PHASE_3: self.fx_system.create_phase_transition("dark_energy"),
            BossPhase.FINAL: self.fx_system.create_phase_transition("ultimate_power")
        }
        
        # Boss-specific abilities
        self.abilities = self._initialize_abilities()
        
        # HD-2D visual elements
        self.aura_emitter = ParticleEmitter()
        self.weapon_trail = None
        self.phase_indicators = {}
        self.current_phase_fx = None
        
    def _initialize_abilities(self) -> Dict[str, BossAbility]:
        return {
            "ultimate_strike": BossAbility("Ultimate Strike", 150, 15.0, "thunder_strike"),
            "dark_nova": BossAbility("Dark Nova", 100, 10.0, "dark_explosion"),
            "spirit_crush": BossAbility("Spirit Crush", 80, 8.0, "spirit_waves"),
            "final_judgment": BossAbility("Final Judgment", 200, 20.0, "judgment_rays")
        }
        
    def update(self, dt: float):
        super().update(dt)
        
        # Update ability cooldowns
        for ability in self.abilities.values():
            if ability.current_cooldown > 0:
                ability.current_cooldown = max(0, ability.current_cooldown - dt)
                
        # Update phase-specific effects
        if self.current_phase_fx:
            self.current_phase_fx.update(dt)
            
        # Check for phase transitions
        health_ratio = self.health / self.max_health
        for phase, threshold in self.phase_health_thresholds.items():
            if health_ratio <= threshold and self.phase.value < phase.value:
                self._transition_to_phase(phase)
                
    def _transition_to_phase(self, new_phase: BossPhase):
        self.phase = new_phase
        
        # Trigger epic phase transition effects
        if new_phase in self.phase_transitions:
            transition_fx = self.phase_transitions[new_phase]
            transition_fx.play()
            
        # Update visual elements
        self._update_phase_visuals(new_phase)
        
        # Grant phase-specific buffs
        if new_phase == BossPhase.PHASE_2:
            self.change_state(PsychologicalState.AGGRESSIVE, duration=float('inf'))
        elif new_phase == BossPhase.PHASE_3:
            self.change_state(PsychologicalState.ENRAGED, duration=float('inf'))
            
    def _update_phase_visuals(self, phase: BossPhase):
        # Update HD-2D visual effects for the new phase
        if phase == BossPhase.PHASE_2:
            self.current_phase_fx = self.fx_system.create_effect("power_aura", (1.0, 0.7, 0.2))
        elif phase == BossPhase.PHASE_3:
            self.current_phase_fx = self.fx_system.create_effect("dark_aura", (0.3, 0.0, 0.5))
        elif phase == BossPhase.FINAL:
            self.current_phase_fx = self.fx_system.create_effect("ultimate_aura", (1.0, 0.0, 0.0))
            
    def use_ability(self, ability_name: str) -> Optional[float]:
        if ability_name not in self.abilities:
            return None
            
        ability = self.abilities[ability_name]
        if ability.current_cooldown > 0:
            return None
            
        # Trigger ability visual effects
        self.fx_system.create_effect(ability.fx_type, self.STATE_EFFECTS[self.state].particle_color)
        
        # Apply ability
        ability.current_cooldown = ability.cooldown
        return self.deal_damage(ability.damage)