import numpy as np
from ..gpu_particle_system import ParticleEmitter

class FireEffect(ParticleEmitter):
    def __init__(self, max_particles: int = 1000):
        super().__init__(max_particles)
        self.spawn_rate = 200
        self.particle_life = 2.0
        self.velocity_range = (-0.5, 2.0)
        self.size_range = (0.1, 0.3)
        self.color_start = np.array([1.0, 0.7, 0.0, 1.0], dtype=np.float32)
        self.color_end = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

class SmokeEffect(ParticleEmitter):
    def __init__(self, max_particles: int = 500):
        super().__init__(max_particles)
        self.spawn_rate = 50
        self.particle_life = 4.0
        self.velocity_range = (-0.2, 1.0)
        self.size_range = (0.3, 0.8)
        self.color_start = np.array([0.7, 0.7, 0.7, 0.3], dtype=np.float32)
        self.color_end = np.array([0.3, 0.3, 0.3, 0.0], dtype=np.float32)

class WaterEffect(ParticleEmitter):
    def __init__(self, max_particles: int = 2000):
        super().__init__(max_particles)
        self.spawn_rate = 500
        self.particle_life = 1.5
        self.velocity_range = (-1.0, 1.0)
        self.size_range = (0.05, 0.15)
        self.color_start = np.array([0.2, 0.5, 1.0, 0.8], dtype=np.float32)
        self.color_end = np.array([0.2, 0.5, 1.0, 0.0], dtype=np.float32)

class SparkEffect(ParticleEmitter):
    def __init__(self, max_particles: int = 200):
        super().__init__(max_particles)
        self.spawn_rate = 100
        self.particle_life = 0.5
        self.velocity_range = (-3.0, 3.0)
        self.size_range = (0.02, 0.08)
        self.color_start = np.array([1.0, 0.9, 0.3, 1.0], dtype=np.float32)
        self.color_end = np.array([1.0, 0.6, 0.0, 0.0], dtype=np.float32)

class WeatherEffect(ParticleEmitter):
    def __init__(self, max_particles: int = 5000):
        super().__init__(max_particles)
        self.area_size = np.array([100.0, 50.0, 100.0], dtype=np.float32)  # Width, Height, Depth
    
    def update_spawn_position(self):
        """Randomly distribute particles across the area"""
        self.position = np.random.uniform(
            -self.area_size / 2,
            self.area_size / 2
        )

class RainEffect(WeatherEffect):
    def __init__(self, max_particles: int = 5000):
        super().__init__(max_particles)
        self.spawn_rate = 2000
        self.particle_life = 2.0
        self.velocity_range = (-0.1, -10.0)
        self.size_range = (0.02, 0.05)
        self.color_start = np.array([0.7, 0.7, 0.8, 0.5], dtype=np.float32)
        self.color_end = np.array([0.7, 0.7, 0.8, 0.0], dtype=np.float32)

class SnowEffect(WeatherEffect):
    def __init__(self, max_particles: int = 3000):
        super().__init__(max_particles)
        self.spawn_rate = 1000
        self.particle_life = 5.0
        self.velocity_range = (-0.5, -2.0)
        self.size_range = (0.05, 0.1)
        self.color_start = np.array([1.0, 1.0, 1.0, 0.8], dtype=np.float32)
        self.color_end = np.array([1.0, 1.0, 1.0, 0.0], dtype=np.float32)