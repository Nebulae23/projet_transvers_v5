import numpy as np
from typing import List, Tuple

class WeatheringEffect:
    def __init__(self):
        self.intensity = 0.0
        self.mask = None  # Texture mask for the effect
        self.blend_mode = 'multiply'
    
    def apply(self, material_params: dict) -> dict:
        """Apply weathering effect to material parameters"""
        return material_params

class RustEffect(WeatheringEffect):
    def __init__(self):
        super().__init__()
        self.rust_color = np.array([0.65, 0.32, 0.17], dtype=np.float32)
    
    def apply(self, material_params: dict) -> dict:
        """Apply rust weathering effect"""
        # Modify albedo, roughness, and metallic parameters
        material_params['albedo'] = self._blend_colors(
            material_params['albedo'],
            self.rust_color,
            self.intensity
        )
        material_params['roughness'] = min(1.0, material_params['roughness'] + self.intensity * 0.5)
        material_params['metallic'] *= (1.0 - self.intensity)
        return material_params
    
    def _blend_colors(self, base: np.ndarray, rust: np.ndarray, t: float) -> np.ndarray:
        return base * (1 - t) + rust * t

class WeatheringSystem:
    def __init__(self):
        self.effects: List[Tuple[WeatheringEffect, float]] = []  # (effect, age)
        self.update_interval = 1.0  # seconds
        self.time_accumulator = 0.0
    
    def add_effect(self, effect: WeatheringEffect):
        """Add a new weathering effect"""
        self.effects.append((effect, 0.0))
    
    def update(self, dt: float, material_params: dict) -> dict:
        """Update weathering effects over time"""
        self.time_accumulator += dt
        
        if self.time_accumulator >= self.update_interval:
            self.time_accumulator = 0.0
            
            # Update each effect
            for i, (effect, age) in enumerate(self.effects):
                self.effects[i] = (effect, age + self.update_interval)
                # Apply aging logic
                effect.intensity = min(1.0, age / 100.0)  # Example aging rate
                material_params = effect.apply(material_params)
        
        return material_params
    
    def reset(self):
        """Reset all weathering effects"""
        self.effects.clear()
        self.time_accumulator = 0.0