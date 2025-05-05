# src/engine/events/event_generator.py
from typing import List, Dict
import random
from .weather_event import WeatherEvent, EventTriggerType
from ..environment.weather_system_fx import WeatherState

class EventGenerator:
    def __init__(self):
        self.active_events: List[WeatherEvent] = []
        self.available_events: Dict[str, WeatherEvent] = {}
        self.event_cooldowns: Dict[str, float] = {}
        
        # Minimum time between events of the same type (in seconds)
        self.min_event_spacing = 120.0
        
        # Initialize event pool
        self._initialize_event_pool()

    def _initialize_event_pool(self):
        """Initialize the pool of available weather events"""
        from .special_encounters import create_special_encounters
        
        # Get special encounters
        special_encounters = create_special_encounters()
        
        # Add to available events
        for event in special_encounters:
            self.available_events[event.event_id] = event
            self.event_cooldowns[event.event_id] = 0.0

    def update(self, dt: float, weather_state: WeatherState, intensity: float):
        """Update event system state"""
        # Update cooldowns
        for event_id in self.event_cooldowns:
            self.event_cooldowns[event_id] = max(0.0, self.event_cooldowns[event_id] - dt)
            
        # Update active events
        completed_events = []
        for event in self.active_events:
            if event.update(dt):
                completed_events.append(event)
                
        # Remove completed events
        for event in completed_events:
            self.active_events.remove(event)
            self.event_cooldowns[event.event_id] = self.min_event_spacing
            
        # Try to trigger new events
        self._try_trigger_events(weather_state, intensity)

    def _try_trigger_events(self, weather_state: WeatherState, intensity: float):
        """Attempt to trigger new events based on current conditions"""
        if len(self.active_events) >= 2:  # Max concurrent events
            return
            
        eligible_events = [
            event for event_id, event in self.available_events.items()
            if (event.can_trigger(weather_state, intensity) and 
                self.event_cooldowns[event_id] <= 0.0)
        ]
        
        if eligible_events:
            # Randomly select an event with weight based on intensity
            weights = [intensity ** 2 for _ in eligible_events]  # Higher intensity = higher chance
            selected_event = random.choices(eligible_events, weights=weights, k=1)[0]
            
            # Start the event
            selected_event.start()
            self.active_events.append(selected_event)

    def get_active_events(self) -> List[WeatherEvent]:
        return self.active_events.copy()