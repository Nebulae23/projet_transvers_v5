# src/engine/fx/particle_emitter.py
import random
import numpy as np
from typing import List
from .particle import ParticleProperties

class ParticleEmitter:
    def __init__(self, 
                 x: float, 
                 y: float,
                 emit_rate: float,
                 particle_properties: ParticleProperties,
                 spread_angle: float = 360.0,
                 speed_range: tuple = (1.0, 1.0),
                 size_range: tuple = (1.0, 1.0),
                 lifetime_range: tuple = (1.0, 1.0)):
        self.x = x
        self.y = y
        self.emit_rate = emit_rate  # particles per second
        self.base_properties = particle_properties
        self.spread_angle = spread_angle
        self.speed_range = speed_range
        self.size_range = size_range
        self.lifetime_range = lifetime_range
        self.active = True
        self.emit_accumulator = 0.0
        
    def generate_particle_properties(self) -> ParticleProperties:
        """Generate randomized particle properties"""
        angle = random.uniform(0, self.spread_angle) * np.pi / 180.0
        speed = random.uniform(*self.speed_range)
        
        velocity = (
            speed * np.cos(angle),
            speed * np.sin(angle)
        )
        
        return ParticleProperties(
            lifetime=random.uniform(*self.lifetime_range),
            size=random.uniform(*self.size_range),
            color=self.base_properties.color,
            velocity=velocity,
            gravity=self.base_properties.gravity,
            drag=self.base_properties.drag
        )
        
    def emit(self, dt: float) -> List[ParticleProperties]:
        """Emit new particles based on emission rate"""
        if not self.active:
            return []
            
        self.emit_accumulator += dt
        particles_to_emit = int(self.emit_accumulator * self.emit_rate)
        self.emit_accumulator -= particles_to_emit / self.emit_rate
        
        return [self.generate_particle_properties() 
                for _ in range(particles_to_emit)]