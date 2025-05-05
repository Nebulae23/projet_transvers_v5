# src/engine/combat/ai_patterns.py
from enum import Enum
from typing import Dict, List, Tuple, Optional
import numpy as np
from .enemy import Enemy
from .boss import Boss

class AIState(Enum):
    IDLE = "idle"
    PURSUE = "pursue"
    ATTACK = "attack"
    RETREAT = "retreat"
    FLANK = "flank"
    DEFENSIVE = "defensive"

class AIPattern:
    def __init__(self):
        self.current_state = AIState.IDLE
        self.target_position = None
        self.path = []
        self.attack_cooldown = 0
        self.state_duration = 0
        
        # Animation transitions
        self.current_animation = "idle"
        self.animation_blend = 0.0
        self.transition_duration = 0.3
        
    def update(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]) -> AIState:
        self.state_duration -= dt
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        
        # Update animation blending
        if self.animation_blend < 1.0:
            self.animation_blend = min(1.0, self.animation_blend + dt / self.transition_duration)
            
        # State machine logic
        if self.state_duration <= 0:
            new_state = self._choose_next_state(enemy, player_pos)
            self._transition_to_state(new_state, enemy)
            
        return self._execute_current_state(dt, enemy, player_pos)
        
    def _choose_next_state(self, enemy: Enemy, player_pos: Tuple[float, float, float]) -> AIState:
        distance = np.linalg.norm(np.array(player_pos) - np.array(enemy.position))
        
        if enemy.health < enemy.max_health * 0.3:
            return AIState.DEFENSIVE
        elif distance < 2.0 and self.attack_cooldown <= 0:
            return AIState.ATTACK
        elif distance < 10.0:
            return AIState.PURSUE if np.random.random() < 0.7 else AIState.FLANK
        else:
            return AIState.IDLE
            
    def _transition_to_state(self, new_state: AIState, enemy: Enemy):
        self.current_state = new_state
        self.state_duration = np.random.uniform(2.0, 4.0)
        self.animation_blend = 0.0
        
        # Set up state-specific behaviors
        if new_state == AIState.PURSUE:
            self._transition_animation("run")
        elif new_state == AIState.ATTACK:
            self._transition_animation("attack")
            self.attack_cooldown = 1.0
        elif new_state == AIState.RETREAT:
            self._transition_animation("run_backward")
        elif new_state == AIState.FLANK:
            self._transition_animation("strafe")
        elif new_state == AIState.DEFENSIVE:
            self._transition_animation("defend")
        else:
            self._transition_animation("idle")
            
    def _execute_current_state(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]) -> AIState:
        if self.current_state == AIState.PURSUE:
            self._execute_pursue(dt, enemy, player_pos)
        elif self.current_state == AIState.ATTACK:
            self._execute_attack(dt, enemy, player_pos)
        elif self.current_state == AIState.RETREAT:
            self._execute_retreat(dt, enemy, player_pos)
        elif self.current_state == AIState.FLANK:
            self._execute_flank(dt, enemy, player_pos)
        elif self.current_state == AIState.DEFENSIVE:
            self._execute_defensive(dt, enemy, player_pos)
            
        return self.current_state
        
    def _transition_animation(self, new_animation: str):
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.animation_blend = 0.0
            
    def _execute_pursue(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]):
        direction = np.array(player_pos) - np.array(enemy.position)
        direction = direction / np.linalg.norm(direction)
        enemy.position += direction * dt * 5.0
        
    def _execute_attack(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]):
        if isinstance(enemy, Boss):
            available_abilities = [name for name, ability in enemy.abilities.items() 
                                if ability.current_cooldown <= 0]
            if available_abilities:
                enemy.use_ability(np.random.choice(available_abilities))
        else:
            # Regular enemy attack logic
            enemy.deal_damage(enemy.level * 10)
            
    def _execute_retreat(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]):
        direction = np.array(enemy.position) - np.array(player_pos)
        direction = direction / np.linalg.norm(direction)
        enemy.position += direction * dt * 3.0
        
    def _execute_flank(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]):
        direction = np.array(player_pos) - np.array(enemy.position)
        perpendicular = np.array([-direction[2], 0, direction[0]])
        perpendicular = perpendicular / np.linalg.norm(perpendicular)
        enemy.position += perpendicular * dt * 4.0
        
    def _execute_defensive(self, dt: float, enemy: Enemy, player_pos: Tuple[float, float, float]):
        # Increase defense and try to maintain distance
        direction = np.array(enemy.position) - np.array(player_pos)
        distance = np.linalg.norm(direction)
        if distance < 5.0:
            direction = direction / distance
            enemy.position += direction * dt * 2.0