# src/engine/gameplay/weather_impact.py
from enum import Enum
from ..environment.weather_system_fx import WeatherState
from .entity_weather_effects import EntityWeatherEffects
from .weather_behavior import WeatherBehaviorModifier
from .visibility_manager import VisibilityManager

class WeatherImpactType(Enum):
    MOVEMENT = "movement"
    VISIBILITY = "visibility"
    COMBAT = "combat"
    DETECTION = "detection"

class WeatherImpactSystem:
    def __init__(self, world):
        self.world = world
        self.visibility_manager = VisibilityManager()
        self.behavior_modifier = WeatherBehaviorModifier()
        
        # Impact multipliers for different weather states
        self.impact_multipliers = {
            WeatherState.CLEAR: {
                WeatherImpactType.MOVEMENT: 1.0,
                WeatherImpactType.VISIBILITY: 1.0,
                WeatherImpactType.COMBAT: 1.0,
                WeatherImpactType.DETECTION: 1.0
            },
            WeatherState.RAIN: {
                WeatherImpactType.MOVEMENT: 0.8,
                WeatherImpactType.VISIBILITY: 0.7,
                WeatherImpactType.COMBAT: 0.9,
                WeatherImpactType.DETECTION: 0.6
            },
            WeatherState.STORM: {
                WeatherImpactType.MOVEMENT: 0.6,
                WeatherImpactType.VISIBILITY: 0.4,
                WeatherImpactType.COMBAT: 0.7,
                WeatherImpactType.DETECTION: 0.3
            }
        }

    def update(self, dt):
        weather_state = self.world.weather_system.current_state
        weather_intensity = self.world.weather_system.intensity
        
        # Get affected entities
        entities = [e for e in self.world.entities if hasattr(e, 'weather_effects')]
        
        for entity in entities:
            self._apply_weather_effects(entity, weather_state, weather_intensity, dt)
            
        # Update subsystems
        self.visibility_manager.update(weather_state, weather_intensity)
        self.behavior_modifier.update(weather_state, weather_intensity)

    def _apply_weather_effects(self, entity, weather_state, intensity, dt):
        effects = entity.weather_effects
        multipliers = self.impact_multipliers[weather_state]
        
        # Apply movement effects
        if effects.affects_movement:
            entity.speed *= multipliers[WeatherImpactType.MOVEMENT]
            
        # Apply visibility effects
        if effects.affects_visibility:
            entity.visibility_range *= multipliers[WeatherImpactType.VISIBILITY]
            
        # Apply combat effects
        if effects.affects_combat:
            entity.attack_speed *= multipliers[WeatherImpactType.COMBAT]
            entity.accuracy *= multipliers[WeatherImpactType.COMBAT]
            
        # Apply detection effects
        if effects.affects_detection:
            entity.detection_range *= multipliers[WeatherImpactType.DETECTION]