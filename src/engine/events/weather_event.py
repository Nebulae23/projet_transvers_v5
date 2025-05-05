# src/engine/events/weather_event.py
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from ..environment.weather_system_fx import WeatherState

class EventTriggerType(Enum):
    WEATHER_CHANGE = "weather_change"
    TIME_BASED = "time_based"
    INTENSITY_THRESHOLD = "intensity_threshold"
    PLAYER_PROXIMITY = "player_proximity"

class EventRewardType(Enum):
    ITEM = "item"
    RESOURCE = "resource" 
    ABILITY = "ability"
    STAT_BOOST = "stat_boost"

@dataclass
class EventReward:
    type: EventRewardType
    value: str
    quantity: int = 1
    duration: Optional[float] = None  # For temporary rewards like stat boosts

class WeatherEvent:
    def __init__(self, 
                 event_id: str,
                 name: str,
                 required_weather: WeatherState,
                 min_intensity: float = 0.0,
                 trigger_type: EventTriggerType = EventTriggerType.WEATHER_CHANGE,
                 duration: float = 60.0,  # Duration in seconds
                 rewards: List[EventReward] = None):
        self.event_id = event_id
        self.name = name
        self.required_weather = required_weather
        self.min_intensity = min_intensity
        self.trigger_type = trigger_type
        self.duration = duration
        self.rewards = rewards or []
        
        self.is_active = False
        self.start_time = None
        self.completion_progress = 0.0

    def can_trigger(self, weather_state: WeatherState, intensity: float) -> bool:
        return (weather_state == self.required_weather and 
                intensity >= self.min_intensity and 
                not self.is_active)

    def start(self):
        self.is_active = True
        self.start_time = datetime.now()
        self.completion_progress = 0.0

    def update(self, dt: float) -> bool:
        """Update event progress. Returns True if event is completed."""
        if not self.is_active:
            return False

        time_elapsed = (datetime.now() - self.start_time).total_seconds()
        self.completion_progress = min(1.0, time_elapsed / self.duration)
        
        if self.completion_progress >= 1.0:
            self.complete()
            return True
        return False

    def complete(self):
        self.is_active = False
        self.start_time = None
        
    def reset(self):
        self.is_active = False
        self.start_time = None
        self.completion_progress = 0.0