# src/engine/gameplay/entity_weather_effects.py
from dataclasses import dataclass

@dataclass
class EntityWeatherEffects:
    """Component for entities that are affected by weather"""
    affects_movement: bool = True
    affects_visibility: bool = True
    affects_combat: bool = True
    affects_detection: bool = True
    
    # Resistance values (0-1, higher means more resistant)
    rain_resistance: float = 0.0
    storm_resistance: float = 0.0
    
    # Base stats to restore after weather effects
    base_speed: float = 0.0
    base_visibility_range: float = 0.0
    base_attack_speed: float = 0.0
    base_accuracy: float = 0.0
    base_detection_range: float = 0.0
    
    def __post_init__(self):
        self.current_effects = set()
        
    def add_effect(self, effect_name: str):
        self.current_effects.add(effect_name)
        
    def remove_effect(self, effect_name: str):
        if effect_name in self.current_effects:
            self.current_effects.remove(effect_name)
            
    def has_effect(self, effect_name: str) -> bool:
        return effect_name in self.current_effects
    
    def reset_stats(self, entity):
        """Reset entity stats to base values"""
        if self.affects_movement:
            entity.speed = self.base_speed
        if self.affects_visibility:
            entity.visibility_range = self.base_visibility_range
        if self.affects_combat:
            entity.attack_speed = self.base_attack_speed
            entity.accuracy = self.base_accuracy
        if self.affects_detection:
            entity.detection_range = self.base_detection_range