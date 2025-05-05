# src/engine/systems/random_events.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import random
from enum import Enum
from ..city.city_manager import CityManager
from ..world.world_manager import WorldManager
from ..environment.weather_system_fx import WeatherSystem

class EventType(Enum):
    CITY = "city"
    WORLD = "world"
    WEATHER = "weather"
    COMBAT = "combat"

@dataclass
class EventCondition:
    type: str
    params: dict

@dataclass
class RandomEvent:
    event_id: str
    type: EventType
    name: str
    description: str
    conditions: List[EventCondition]
    effects: dict
    duration: float
    cooldown: float
    weight: float = 1.0

class RandomEventSystem:
    def __init__(self, city_manager: CityManager, 
                 world_manager: WorldManager,
                 weather_system: WeatherSystem):
        self.city_manager = city_manager
        self.world_manager = world_manager
        self.weather_system = weather_system
        
        self.events: Dict[str, RandomEvent] = {}
        self.active_events: Dict[str, float] = {}  # event_id: remaining_duration
        self.cooldowns: Dict[str, float] = {}  # event_id: remaining_cooldown
        
        self._load_events()

    def _load_events(self):
        # City events
        self.events["trade_caravan"] = RandomEvent(
            "trade_caravan",
            EventType.CITY,
            "Trade Caravan",
            "A trade caravan arrives offering special deals",
            [
                EventCondition("city_level", {"min_level": 3}),
                EventCondition("weather", {"not": "storm"})
            ],
            {
                "trade_prices": 0.8,
                "resource_variety": 1.5
            },
            300.0,  # 5 minutes
            3600.0  # 1 hour cooldown
        )
        
        # Weather events
        self.events["magical_storm"] = RandomEvent(
            "magical_storm",
            EventType.WEATHER,
            "Magical Storm",
            "A storm of magical energy affects all spells",
            [
                EventCondition("time", {"night_only": True}),
                EventCondition("world_magic", {"min_level": 2})
            ],
            {
                "magic_damage": 1.5,
                "mana_cost": 0.7
            },
            600.0,  # 10 minutes
            7200.0  # 2 hours cooldown
        )
        
        # Add more events...

    def update(self, dt: float):
        # Update active events
        finished_events = []
        for event_id, remaining_time in self.active_events.items():
            self.active_events[event_id] = remaining_time - dt
            if self.active_events[event_id] <= 0:
                finished_events.append(event_id)
                
        # Clean up finished events
        for event_id in finished_events:
            self._end_event(event_id)
            
        # Update cooldowns
        cooldown_finished = []
        for event_id, remaining_cooldown in self.cooldowns.items():
            self.cooldowns[event_id] = remaining_cooldown - dt
            if self.cooldowns[event_id] <= 0:
                cooldown_finished.append(event_id)
                
        for event_id in cooldown_finished:
            del self.cooldowns[event_id]
            
        # Try to trigger new events
        self._check_new_events()

    def _check_new_events(self):
        available_events = []
        
        for event_id, event in self.events.items():
            if (event_id not in self.active_events and 
                event_id not in self.cooldowns and 
                self._check_conditions(event)):
                available_events.append(event)
                
        if available_events:
            # Weight-based random selection
            weights = [event.weight for event in available_events]
            selected_event = random.choices(available_events, weights=weights)[0]
            self._start_event(selected_event)

    def _check_conditions(self, event: RandomEvent) -> bool:
        for condition in event.conditions:
            if not self._evaluate_condition(condition):
                return False
        return True

    def _evaluate_condition(self, condition: EventCondition) -> bool:
        if condition.type == "city_level":
            return self.city_manager.level >= condition.params["min_level"]
        elif condition.type == "weather":
            return self.weather_system.current_weather != condition.params["not"]
        elif condition.type == "time":
            return self.world_manager.is_night() if condition.params["night_only"] else True
        return True

    def _start_event(self, event: RandomEvent):
        self.active_events[event.event_id] = event.duration
        self._apply_effects(event.effects)

    def _end_event(self, event_id: str):
        if event_id not in self.events:
            return
            
        event = self.events[event_id]
        self._remove_effects(event.effects)
        del self.active_events[event_id]
        self.cooldowns[event_id] = event.cooldown

    def _apply_effects(self, effects: dict):
        for effect, value in effects.items():
            if effect.startswith("trade_"):
                self.city_manager.modify_trade_modifier(value)
            elif effect.startswith("magic_"):
                self.world_manager.modify_magic_modifier(effect, value)

    def _remove_effects(self, effects: dict):
        for effect, value in effects.items():
            if effect.startswith("trade_"):
                self.city_manager.modify_trade_modifier(1.0 / value)
            elif effect.startswith("magic_"):
                self.world_manager.modify_magic_modifier(effect, 1.0 / value)

    def save_state(self) -> dict:
        return {
            "active_events": self.active_events,
            "cooldowns": self.cooldowns
        }

    def load_state(self, data: dict):
        self.active_events = data.get("active_events", {})
        self.cooldowns = data.get("cooldowns", {})