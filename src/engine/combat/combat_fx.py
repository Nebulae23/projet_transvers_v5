# src/engine/combat/combat_fx.py
from typing import Dict, List, Tuple, Optional
import numpy as np
import pygame  # Use pygame instead of OpenGL for now

# Simplified version that doesn't rely on ShaderPipeline
class ParticleEmitter:
    def __init__(self, position: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        self.position = list(position)
        self.particles = []
        self.max_particles = 1000
        self.spawn_rate = 50  # particles per second
        self.spawn_timer = 0.0
        self.particle_life = 2.0
        self.particle_size = 0.1
        self.velocity_range = (-1.0, 1.0)
        self.color = (1.0, 1.0, 1.0, 1.0)
        
    def update(self, dt: float):
        # Update existing particles
        alive_particles = []
        for particle in self.particles:
            particle['life'] -= dt
            if particle['life'] > 0:
                # Update position
                particle['position'][0] += particle['velocity'][0] * dt
                particle['position'][1] += particle['velocity'][1] * dt
                particle['position'][2] += particle['velocity'][2] * dt
                
                # Apply gravity
                particle['velocity'][1] -= 9.8 * dt
                
                # Update alpha based on life
                particle['color'][3] = particle['life'] / self.particle_life
                
                alive_particles.append(particle)
                
        self.particles = alive_particles
        
        # Spawn new particles
        self.spawn_timer += dt
        to_spawn = int(self.spawn_rate * self.spawn_timer)
        if to_spawn > 0 and len(self.particles) < self.max_particles:
            self.spawn_timer -= to_spawn / self.spawn_rate
            for _ in range(min(to_spawn, self.max_particles - len(self.particles))):
                self.particles.append({
                    'position': list(self.position),
                    'velocity': [
                        np.random.uniform(*self.velocity_range),
                        np.random.uniform(*self.velocity_range),
                        np.random.uniform(*self.velocity_range)
                    ],
                    'life': self.particle_life,
                    'color': list(self.color),
                    'size': self.particle_size
                })

class CombatEffects:
    def __init__(self):
        # Removed shader pipeline dependency
        self.effects: Dict[str, dict] = {}
        self.particle_systems: Dict[str, ParticleEmitter] = {}
        self._initialize_effects()
        
    def _initialize_effects(self):
        # Initialize predefined effects
        self.effects = {
            "blade_energy": {
                "color": (0.2, 0.6, 1.0, 1.0),
                "particle_count": 200,
                "life": 1.0,
                "size": 0.05,
                "velocity": (-2.0, 2.0)
            },
            "shadow_tendrils": {
                "color": (0.3, 0.0, 0.4, 1.0),
                "particle_count": 300,
                "life": 1.5,
                "size": 0.08,
                "velocity": (-1.0, 1.0)
            },
            "time_ripple": {
                "color": (0.8, 0.8, 1.0, 0.8),
                "particle_count": 400,
                "life": 2.0,
                "size": 0.1,
                "velocity": (-0.5, 0.5)
            },
            "spell_fusion": {
                "color": (1.0, 0.5, 0.8, 1.0),
                "particle_count": 500,
                "life": 2.5,
                "size": 0.12,
                "velocity": (-3.0, 3.0)
            }
        }
        
    def create_effect(self, effect_type: str, color: tuple, intensity: float = 1.0) -> Optional[ParticleEmitter]:
        if effect_type not in self.effects:
            return None
            
        base_effect = self.effects[effect_type]
        emitter = ParticleEmitter()
        
        # Apply effect parameters with intensity modifier
        emitter.max_particles = int(base_effect["particle_count"] * intensity)
        emitter.spawn_rate = emitter.max_particles / base_effect["life"]
        emitter.particle_life = base_effect["life"]
        emitter.particle_size = base_effect["size"]
        emitter.velocity_range = tuple(v * intensity for v in base_effect["velocity"])
        
        # Blend base effect color with provided color
        base_color = np.array(base_effect["color"])
        custom_color = np.array(color + (1.0,) if len(color) == 3 else color)
        emitter.color = tuple(np.sqrt(base_color * custom_color))
        
        effect_id = f"{effect_type}_{len(self.particle_systems)}"
        self.particle_systems[effect_id] = emitter
        return emitter
        
    def create_phase_transition(self, effect_type: str) -> ParticleEmitter:
        # Create more dramatic effects for boss phase transitions
        emitter = self.create_effect(effect_type, (1.0, 1.0, 1.0), 2.0)
        if emitter:
            emitter.max_particles *= 2
            emitter.particle_life *= 1.5
            emitter.particle_size *= 1.5
        return emitter
        
    def update_effect(self, effect: ParticleEmitter, dt: float):
        effect.update(dt)
        
    def get_ability_color(self, fx_type: str) -> tuple:
        if fx_type in self.effects:
            return self.effects[fx_type]["color"][:3]
        return (1.0, 1.0, 1.0)