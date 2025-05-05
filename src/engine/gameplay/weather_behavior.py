# src/engine/gameplay/weather_behavior.py
from enum import Enum
from ..environment.weather_system_fx import WeatherState

class BehaviorModification(Enum):
    NORMAL = "normal"
    CAUTIOUS = "cautious"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"

class WeatherBehaviorModifier:
    def __init__(self):
        self.current_modification = BehaviorModification.NORMAL
        
        # Behavior patterns for different weather states
        self.behavior_patterns = {
            WeatherState.CLEAR: {
                "patrol_radius": 1.0,
                "attack_threshold": 0.7,
                "retreat_threshold": 0.3,
                "group_cohesion": 0.5
            },
            WeatherState.RAIN: {
                "patrol_radius": 0.7,
                "attack_threshold": 0.8,
                "retreat_threshold": 0.4,
                "group_cohesion": 0.7
            },
            WeatherState.STORM: {
                "patrol_radius": 0.4,
                "attack_threshold": 0.9,
                "retreat_threshold": 0.6,
                "group_cohesion": 0.9
            }
        }
        
    def update(self, weather_state: WeatherState, intensity: float):
        self._determine_behavior_modification(weather_state, intensity)
        
    def _determine_behavior_modification(self, weather_state: WeatherState, intensity: float):
        if weather_state == WeatherState.CLEAR:
            self.current_modification = BehaviorModification.NORMAL
        elif weather_state == WeatherState.RAIN:
            if intensity > 0.7:
                self.current_modification = BehaviorModification.CAUTIOUS
            else:
                self.current_modification = BehaviorModification.DEFENSIVE
        else:  # STORM
            if intensity > 0.8:
                self.current_modification = BehaviorModification.DEFENSIVE
            else:
                self.current_modification = BehaviorModification.AGGRESSIVE
                
    def get_behavior_parameters(self, weather_state: WeatherState) -> dict:
        return self.behavior_patterns[weather_state]
    
    def modify_ai_behavior(self, ai_entity, weather_state: WeatherState, intensity: float):
        """Modify AI entity behavior based on weather conditions"""
        params = self.get_behavior_parameters(weather_state)
        
        # Apply behavior modifications
        ai_entity.patrol_radius *= params["patrol_radius"]
        ai_entity.attack_threshold = params["attack_threshold"]
        ai_entity.retreat_threshold = params["retreat_threshold"]
        ai_entity.group_cohesion = params["group_cohesion"]
        
        # Apply intensity-based modifications
        if self.current_modification == BehaviorModification.DEFENSIVE:
            ai_entity.prefer_ranged_attacks = True
            ai_entity.keep_distance = True
        elif self.current_modification == BehaviorModification.AGGRESSIVE:
            ai_entity.prefer_ranged_attacks = False
            ai_entity.keep_distance = False