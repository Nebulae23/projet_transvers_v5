# src/engine/environment/components.py
from engine.ecs.component import Component

class TimeAwareComponent(Component):
    def __init__(self):
        self.current_phase = None
        self.is_active = True
        
class LightSensitiveComponent(Component):
    def __init__(self, min_visibility=0.0, max_visibility=1.0):
        self.min_visibility = min_visibility
        self.max_visibility = max_visibility
        self.current_visibility = max_visibility
        
class SpawnPointComponent(Component):
    def __init__(self, x, y, radius=100.0, enemy_types=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.enemy_types = enemy_types or ["basic"]  # Default enemy type
        self.active = True
        self.cooldown = 0
        
class EnvironmentalEffectComponent(Component):
    def __init__(self):
        self.current_effects = set()  # Set of active environmental effects
        self.resistance = {
            "cold": 0,
            "heat": 0,
            "rain": 0,
            "darkness": 0
        }