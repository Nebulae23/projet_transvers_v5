# src/engine/gameplay/visibility_manager.py
from ..environment.weather_system_fx import WeatherState

class VisibilityManager:
    def __init__(self):
        self.base_visibility_range = 100.0
        self.current_visibility_range = self.base_visibility_range
        self.visibility_modifiers = {
            WeatherState.CLEAR: 1.0,
            WeatherState.RAIN: 0.7,
            WeatherState.STORM: 0.4
        }
        
        # Lightning flash settings
        self.lightning_flash_duration = 0.2
        self.lightning_flash_intensity = 2.0
        self.flash_timer = 0
        self.is_flashing = False
        
    def update(self, weather_state: WeatherState, intensity: float):
        # Calculate base visibility
        base_modifier = self.visibility_modifiers[weather_state]
        self.current_visibility_range = self.base_visibility_range * base_modifier * (1 - (intensity * 0.5))
        
        # Handle lightning flashes in storms
        if weather_state == WeatherState.STORM:
            self._handle_lightning_flashes()
            
    def _handle_lightning_flashes(self):
        if self.is_flashing:
            self.flash_timer -= 1/60  # Assuming 60 FPS
            if self.flash_timer <= 0:
                self.is_flashing = False
                
    def trigger_lightning_flash(self):
        """Trigger a lightning flash effect"""
        self.is_flashing = True
        self.flash_timer = self.lightning_flash_duration
        self.current_visibility_range *= self.lightning_flash_intensity
        
    def get_entity_visibility(self, entity, target) -> float:
        """Calculate visibility between two entities"""
        base_visibility = self.current_visibility_range
        
        # Apply entity-specific modifiers
        if hasattr(entity, 'weather_effects'):
            base_visibility *= entity.weather_effects.visibility_range
            
        # Calculate distance-based visibility
        distance = ((entity.x - target.x) ** 2 + (entity.y - target.y) ** 2) ** 0.5
        distance_factor = max(0, 1 - (distance / base_visibility))
        
        # Apply lightning flash boost if active
        if self.is_flashing:
            distance_factor = min(1.0, distance_factor * self.lightning_flash_intensity)
            
        return distance_factor