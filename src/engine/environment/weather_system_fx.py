# src/engine/environment/weather_system_fx.py
from typing import Optional
from enum import Enum
import random
import math
from ..fx.weather_particles import WeatherParticles
from ..fx.particle import ParticleProperties

class WeatherState(Enum):
    CLEAR = "clear"
    RAIN = "rain" 
    STORM = "storm"

class WeatherSystemFX:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.weather_particles = WeatherParticles(width, height)
        self.current_state = WeatherState.CLEAR
        self.target_state = WeatherState.CLEAR
        self.transition_time = 0.0
        self.transition_duration = 2.0  # Time to transition between states
        self.state_duration = 0.0       # How long current state has lasted
        self.min_state_duration = 30.0  # Minimum time before state can change
        self.intensity = 0.0            # Current weather intensity (0-1)
        self.target_intensity = 0.0
        
        # Weather state configuration
        self.state_config = {
            WeatherState.CLEAR: {
                "min_duration": 30.0,
                "max_duration": 180.0,
                "transition_weights": {
                    WeatherState.RAIN: 0.7,
                    WeatherState.STORM: 0.3
                }
            },
            WeatherState.RAIN: {
                "min_duration": 20.0,
                "max_duration": 120.0,
                "transition_weights": {
                    WeatherState.CLEAR: 0.6,
                    WeatherState.STORM: 0.4
                }
            },
            WeatherState.STORM: {
                "min_duration": 15.0,
                "max_duration": 60.0,
                "transition_weights": {
                    WeatherState.RAIN: 0.8,
                    WeatherState.CLEAR: 0.2
                }
            }
        }

    def update(self, dt: float):
        # Update state duration
        self.state_duration += dt

        # Check for state transition
        if self.state_duration >= self.min_state_duration:
            if random.random() < 0.1 * dt:  # 10% chance per second to consider transition
                self._consider_state_transition()

        # Handle transition
        if self.current_state != self.target_state:
            self.transition_time += dt
            progress = min(1.0, self.transition_time / self.transition_duration)
            
            # Smoothly interpolate intensity
            self.intensity = self._lerp(
                self.intensity, 
                self.target_intensity, 
                progress
            )

            # Complete transition
            if progress >= 1.0:
                self.current_state = self.target_state
                self._apply_weather_state()
        
        # Update particle effects
        self.weather_particles.update(dt)

    def _lerp(self, start: float, end: float, alpha: float) -> float:
        """Linear interpolation between start and end values"""
        return start + (end - start) * alpha

    def _consider_state_transition(self):
        """Consider transitioning to a new weather state"""
        config = self.state_config[self.current_state]
        
        # Only transition if we've been in current state long enough
        if self.state_duration < config["min_duration"]:
            return

        # Get possible transitions and their weights
        transitions = config["transition_weights"]
        states = list(transitions.keys())
        weights = list(transitions.values())

        # Choose new state
        new_state = random.choices(states, weights=weights)[1]
        
        if new_state != self.current_state:
            self._transition_to(new_state)

    def _transition_to(self, new_state: WeatherState):
        """Begin transition to a new weather state"""
        self.target_state = new_state
        self.transition_time = 0.0
        
        # Set target intensity based on new state
        if new_state == WeatherState.CLEAR:
            self.target_intensity = 0.0
        elif new_state == WeatherState.RAIN:
            self.target_intensity = random.uniform(0.5, 0.8)
        else:  # STORM
            self.target_intensity = random.uniform(0.8, 1.0)

    def _apply_weather_state(self):
        """Apply the current weather state's effects"""
        self.weather_particles.clear()
        
        if self.current_state == WeatherState.RAIN:
            self.weather_particles.create_rain(self.intensity)
        elif self.current_state == WeatherState.STORM:
            self.weather_particles.create_storm(self.intensity)

    def force_weather(self, state: WeatherState, intensity: Optional[float] = None):
        """Force a specific weather state (useful for debugging or scripted events)"""
        self.current_state = state
        self.target_state = state
        self.transition_time = 0.0
        
        if intensity is not None:
            self.intensity = intensity
            self.target_intensity = intensity
            
        self._apply_weather_state()

    def cleanup(self):
        """Clean up weather effects"""
        self.weather_particles.clear()