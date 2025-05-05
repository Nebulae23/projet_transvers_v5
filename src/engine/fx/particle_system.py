# src/engine/fx/particle_system.py
from typing import List, Dict
from .particle import Particle, ParticleProperties
from .particle_emitter import ParticleEmitter

class ParticleSystem:
    def __init__(self, max_particles: int = 10000):
        self.max_particles = max_particles
        self.particle_pool: List[Particle] = []
        self.emitters: Dict[str, ParticleEmitter] = {}
        self.initialize_pool()
        
    def initialize_pool(self):
        """Initialize particle pool with inactive particles"""
        default_props = ParticleProperties()
        for _ in range(self.max_particles):
            self.particle_pool.append(Particle(0, 0, default_props))
            
    def get_inactive_particle(self) -> Particle:
        """Get first inactive particle from pool"""
        for particle in self.particle_pool:
            if not particle.active:
                return particle
        return None
        
    def add_emitter(self, name: str, emitter: ParticleEmitter):
        """Add a new particle emitter"""
        self.emitters[name] = emitter
        
    def remove_emitter(self, name: str):
        """Remove particle emitter"""
        if name in self.emitters:
            del self.emitters[name]
            
    def update(self, dt: float):
        """Update all active particles and emitters"""
        # Update emitters
        for emitter in self.emitters.values():
            if emitter.active:
                new_particles = emitter.emit(dt)
                for particle_props in new_particles:
                    particle = self.get_inactive_particle()
                    if particle:
                        particle.reset(emitter.x, emitter.y, particle_props)
                        
        # Update particles
        for particle in self.particle_pool:
            if particle.active:
                particle.update(dt)
                
    def clear_all(self):
        """Deactivate all particles"""
        for particle in self.particle_pool:
            particle.active = False