# src/engine/fx/particle.py
import numpy as np
from dataclasses import dataclass

@dataclass
class ParticleProperties:
    lifetime: float = 1.0
    size: float = 1.0
    color: tuple = (1.0, 1.0, 1.0, 1.0)  # RGBA
    velocity: tuple = (0.0, 0.0)
    gravity: float = 0.0
    drag: float = 0.0

class Particle:
    def __init__(self, x: float, y: float, properties: ParticleProperties):
        self.x = x
        self.y = y
        self.orig_x = x
        self.orig_y = y
        self.properties = properties
        self.time_alive = 0.0
        self.active = False
        self.velocity_x = properties.velocity[0]
        self.velocity_y = properties.velocity[1]
        self.size = properties.size
        self.color = list(properties.color)
        
    def update(self, dt: float) -> bool:
        if not self.active:
            return False
            
        self.time_alive += dt
        
        if self.time_alive >= self.properties.lifetime:
            self.active = False
            return False
            
        # Apply gravity
        self.velocity_y += self.properties.gravity * dt
        
        # Apply drag
        self.velocity_x *= (1.0 - self.properties.drag * dt)
        self.velocity_y *= (1.0 - self.properties.drag * dt)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update alpha based on lifetime
        life_ratio = self.time_alive / self.properties.lifetime
        self.color[3] = 1.0 - life_ratio
        
        return True
        
    def reset(self, x: float, y: float, properties: ParticleProperties = None):
        self.x = x
        self.y = y
        self.orig_x = x
        self.orig_y = y
        self.time_alive = 0.0
        self.active = True
        
        if properties:
            self.properties = properties
            
        self.velocity_x = self.properties.velocity[0]
        self.velocity_y = self.properties.velocity[1]
        self.size = self.properties.size
        self.color = list(self.properties.color)