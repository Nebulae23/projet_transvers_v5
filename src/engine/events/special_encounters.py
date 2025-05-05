# src/engine/events/special_encounters.py
from typing import List
from .weather_event import WeatherEvent, EventTriggerType, EventReward, EventRewardType
from ..environment.weather_system_fx import WeatherState

def create_special_encounters() -> List[WeatherEvent]:
    """Create pool of special weather-based encounters"""
    encounters = []
    
    # Rain Events
    encounters.extend([
        WeatherEvent(
            event_id="rain_merchant",
            name="Wandering Merchant",
            required_weather=WeatherState.RAIN,
            min_intensity=0.3,
            trigger_type=EventTriggerType.WEATHER_CHANGE,
            duration=120.0,
            rewards=[
                EventReward(EventRewardType.ITEM, "rain_coat", 1),
                EventReward(EventRewardType.RESOURCE, "gold", 100)
            ]
        ),
        WeatherEvent(
            event_id="rain_garden",
            name="Mystical Garden",
            required_weather=WeatherState.RAIN,
            min_intensity=0.6,
            trigger_type=EventTriggerType.INTENSITY_THRESHOLD,
            duration=180.0,
            rewards=[
                EventReward(EventRewardType.ABILITY, "nature_blessing", 1),
                EventReward(EventRewardType.STAT_BOOST, "healing_rate", 1, 300.0)
            ]
        )
    ])
    
    # Storm Events
    encounters.extend([
        WeatherEvent(
            event_id="lightning_forge",
            name="Thunder Forge",
            required_weather=WeatherState.STORM,
            min_intensity=0.7,
            trigger_type=EventTriggerType.WEATHER_CHANGE,
            duration=240.0,
            rewards=[
                EventReward(EventRewardType.ITEM, "lightning_blade", 1),
                EventReward(EventRewardType.ABILITY, "thunder_strike", 1)
            ]
        ),
        WeatherEvent(
            event_id="storm_ritual",
            name="Storm Caller's Ritual",
            required_weather=WeatherState.STORM,
            min_intensity=0.9,
            trigger_type=EventTriggerType.INTENSITY_THRESHOLD,
            duration=300.0,
            rewards=[
                EventReward(EventRewardType.STAT_BOOST, "lightning_resistance", 1, 600.0),
                EventReward(EventRewardType.ABILITY, "chain_lightning", 1)
            ]
        )
    ])
    
    return encounters

def get_location_based_encounters(player_position) -> List[WeatherEvent]:
    """Get additional encounters based on player location"""
    location_encounters = []
    
    # Example location-based weather event
    if player_position.is_in_mountains():
        location_encounters.append(
            WeatherEvent(
                event_id="mountain_storm",
                name="Mountain Peak Storm",
                required_weather=WeatherState.STORM,
                min_intensity=0.8,
                trigger_type=EventTriggerType.PLAYER_PROXIMITY,
                duration=180.0,
                rewards=[
                    EventReward(EventRewardType.ITEM, "storm_crystal", 1),
                    EventReward(EventRewardType.ABILITY, "wind_dash", 1)
                ]
            )
        )
    
    return location_encounters