# src/engine/fx/weather_particles.py
from .particle import ParticleProperties
from .particle_emitter import ParticleEmitter
from .particle_system import ParticleSystem

class WeatherParticles:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.particle_system = ParticleSystem(max_particles=50000)
        
    def create_rain(self, intensity: float = 1.0):
        """Create rain emitters across the top of the screen"""
        rain_props = ParticleProperties(
            lifetime=1.5,
            size=2.0,
            color=(0.7, 0.7, 1.0, 0.5),
            velocity=(0, 300),
            gravity=900,
            drag=0.1
        )
        
        # Create multiple rain emitters across the top
        num_emitters = int(10 * intensity)
        spacing = self.width / (num_emitters + 1)
        
        for i in range(num_emitters):
            emitter = ParticleEmitter(
                x=spacing * (i + 1),
                y=-10,
                emit_rate=100 * intensity,
                particle_properties=rain_props,
                spread_angle=30,
                speed_range=(200, 400),
                size_range=(1.0, 3.0),
                lifetime_range=(1.0, 2.0)
            )
            self.particle_system.add_emitter(f"rain_{i}", emitter)
            
    def create_storm(self, intensity: float = 1.0):
        """Create storm effect with rain and occasional lightning particles"""
        # Create intense rain
        self.create_rain(intensity * 2.0)
        
        # Add lightning flash particles
        lightning_props = ParticleProperties(
            lifetime=0.2,
            size=50.0,
            color=(1.0, 1.0, 0.8, 0.8),
            velocity=(0, 0),
            gravity=0,
            drag=0
        )
        
        lightning_emitter = ParticleEmitter(
            x=self.width / 2,
            y=self.height / 2,
            emit_rate=0.5 * intensity,  # Lightning strikes per second
            particle_properties=lightning_props,
            spread_angle=360,
            speed_range=(0, 0),
            size_range=(40, 60),
            lifetime_range=(0.1, 0.3)
        )
        
        self.particle_system.add_emitter("lightning", lightning_emitter)
        
    def update(self, dt: float):
        """Update all weather particles"""
        self.particle_system.update(dt)
        
    def clear(self):
        """Clear all weather effects"""
        self.particle_system.clear_all()