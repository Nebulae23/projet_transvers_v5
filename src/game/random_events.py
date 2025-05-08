#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Random Events System for Nightfall Defenders
Provides time-based and condition-based random events that affect gameplay
"""

import random
import time
from enum import Enum

class EventType(Enum):
    """Types of random events"""
    POSITIVE = "positive"  # Beneficial events
    NEGATIVE = "negative"  # Harmful events
    NEUTRAL = "neutral"    # Mixed or atmospheric events

class EventTrigger(Enum):
    """Types of event triggers"""
    TIME_BASED = "time"          # Occurs after X days
    CONDITION_BASED = "condition"  # Triggered by player actions/states
    RANDOM = "random"            # Occurs randomly with set probability

class EventDuration(Enum):
    """Duration types for events"""
    SINGLE_DAY = "single_day"    # Lasts until next dawn
    MULTI_DAY = "multi_day"      # Lasts multiple days
    PERMANENT = "permanent"      # Permanently changes game state

class RandomEvent:
    """Base class for random events"""
    
    def __init__(self, event_id, name, description, event_type, trigger_type, duration_type, icon=None):
        """
        Initialize a random event
        
        Args:
            event_id (str): Unique identifier for the event
            name (str): Display name for the event
            description (str): Description explaining the event
            event_type (EventType): Type of event (positive, negative, neutral)
            trigger_type (EventTrigger): How the event is triggered
            duration_type (EventDuration): How long the event lasts
            icon (str): Path to the event icon texture
        """
        self.event_id = event_id
        self.name = name
        self.description = description
        self.event_type = event_type
        self.trigger_type = trigger_type
        self.duration_type = duration_type
        self.icon = icon
        
        # Event state
        self.is_active = False
        self.start_time = None
        self.end_time = None
        self.duration_days = 1  # Default to 1 day
        
        # Event effects
        self.effects = {}
    
    def activate(self, game, current_day, duration_days=None):
        """
        Activate the event
        
        Args:
            game: The main game instance
            current_day (int): The current day number
            duration_days (int, optional): Override for event duration in days
        """
        self.is_active = True
        self.start_time = time.time()
        
        # Set duration
        if duration_days is not None:
            self.duration_days = duration_days
        elif self.duration_type == EventDuration.SINGLE_DAY:
            self.duration_days = 1
        elif self.duration_type == EventDuration.MULTI_DAY:
            self.duration_days = random.randint(2, 5)  # Random duration between 2-5 days
        elif self.duration_type == EventDuration.PERMANENT:
            self.duration_days = -1  # -1 indicates permanent
        
        # Calculate end day
        if self.duration_days > 0:
            self.end_day = current_day + self.duration_days
        else:
            self.end_day = -1  # No end
        
        # Apply effects
        self.apply_effects(game)
        
        # Notify player
        self._notify_activation(game)
    
    def deactivate(self, game):
        """
        Deactivate the event
        
        Args:
            game: The main game instance
        """
        self.is_active = False
        
        # Remove effects
        self.remove_effects(game)
        
        # Notify player
        self._notify_deactivation(game)
    
    def apply_effects(self, game):
        """
        Apply event effects to the game
        
        Args:
            game: The main game instance
        """
        # Override in subclasses
        pass
    
    def remove_effects(self, game):
        """
        Remove event effects from the game
        
        Args:
            game: The main game instance
        """
        # Override in subclasses
        pass
    
    def update(self, game, current_day):
        """
        Update the event state
        
        Args:
            game: The main game instance
            current_day (int): The current day number
            
        Returns:
            bool: True if the event is still active, False if it ended
        """
        if not self.is_active:
            return False
        
        # Check if event should end based on duration
        if self.duration_type != EventDuration.PERMANENT and current_day >= self.end_day:
            self.deactivate(game)
            return False
        
        # Perform any ongoing effects
        self._update_effects(game)
        
        return True
    
    def _update_effects(self, game):
        """Update any ongoing effects"""
        # Override in subclasses if needed
        pass
    
    def _notify_activation(self, game):
        """Notify the player that an event has started"""
        if hasattr(game, 'show_message'):
            game.show_message(f"Event: {self.name}", self.description, duration=5.0)
        else:
            print(f"Event Started: {self.name} - {self.description}")
    
    def _notify_deactivation(self, game):
        """Notify the player that an event has ended"""
        if hasattr(game, 'show_message'):
            game.show_message(f"Event Ended: {self.name}", "The effects have worn off.", duration=3.0)
        else:
            print(f"Event Ended: {self.name}")
    
    def get_remaining_days(self, current_day):
        """
        Get the number of days remaining for this event
        
        Args:
            current_day (int): The current day number
            
        Returns:
            int: Days remaining, or -1 if permanent
        """
        if self.duration_type == EventDuration.PERMANENT:
            return -1
        
        return max(0, self.end_day - current_day)
    
    def to_dict(self):
        """
        Convert event to dictionary for saving
        
        Returns:
            dict: Dictionary representation of the event
        """
        return {
            'event_id': self.event_id,
            'is_active': self.is_active,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_days': self.duration_days,
            'end_day': self.end_day,
            # Add any subclass-specific data here
        }
    
    @classmethod
    def from_dict(cls, data, events_catalog):
        """
        Create event from saved dictionary
        
        Args:
            data (dict): Dictionary with event data
            events_catalog (dict): Catalog of all event templates
            
        Returns:
            RandomEvent: The reconstructed event
        """
        event_id = data['event_id']
        if event_id not in events_catalog:
            return None
        
        # Create instance from template
        event = events_catalog[event_id]
        
        # Restore state
        event.is_active = data['is_active']
        event.start_time = data['start_time']
        event.end_time = data['end_time']
        event.duration_days = data['duration_days']
        event.end_day = data['end_day']
        
        # Restore subclass-specific data here
        
        return event


# Example event subclasses

class ResourceBonusEvent(RandomEvent):
    """Event that provides bonus resources"""
    
    def __init__(self, event_id, name, description, resource_type, bonus_amount):
        """
        Initialize a resource bonus event
        
        Args:
            event_id (str): Unique identifier for the event
            name (str): Display name for the event
            description (str): Description explaining the event
            resource_type (str): Type of resource to boost
            bonus_amount (int): Amount of bonus resources
        """
        super().__init__(
            event_id,
            name,
            description,
            EventType.POSITIVE,
            EventTrigger.RANDOM,
            EventDuration.SINGLE_DAY
        )
        self.resource_type = resource_type
        self.bonus_amount = bonus_amount
    
    def apply_effects(self, game):
        """Add resources to player inventory"""
        if hasattr(game, 'player') and hasattr(game.player, 'inventory'):
            if self.resource_type not in game.player.inventory:
                game.player.inventory[self.resource_type] = 0
            
            game.player.inventory[self.resource_type] += self.bonus_amount
            
            # Log the bonus
            if hasattr(game, 'debug_mode') and game.debug_mode:
                print(f"Resource bonus: Added {self.bonus_amount} {self.resource_type}")


class SicknessEvent(RandomEvent):
    """Event that reduces player max health"""
    
    def __init__(self, event_id, name, description, health_reduction_percent):
        """
        Initialize a sickness event
        
        Args:
            event_id (str): Unique identifier for the event
            name (str): Display name for the event
            description (str): Description explaining the event
            health_reduction_percent (float): Percentage to reduce max health by
        """
        super().__init__(
            event_id,
            name,
            description,
            EventType.NEGATIVE,
            EventTrigger.RANDOM,
            EventDuration.MULTI_DAY
        )
        self.health_reduction_percent = health_reduction_percent
        self.original_max_health = None
    
    def apply_effects(self, game):
        """Reduce player's max health"""
        if hasattr(game, 'player'):
            # Store original value
            self.original_max_health = game.player.max_health
            
            # Calculate and apply reduction
            reduction = int(game.player.max_health * self.health_reduction_percent)
            game.player.max_health -= reduction
            
            # Ensure current health doesn't exceed max
            game.player.health = min(game.player.health, game.player.max_health)
            
            # Log the effect
            if hasattr(game, 'debug_mode') and game.debug_mode:
                print(f"Sickness: Max health reduced by {self.health_reduction_percent*100}% ({reduction} points)")
    
    def remove_effects(self, game):
        """Restore player's max health"""
        if hasattr(game, 'player') and self.original_max_health is not None:
            game.player.max_health = self.original_max_health
            
            # Log the restoration
            if hasattr(game, 'debug_mode') and game.debug_mode:
                print(f"Sickness cured: Max health restored to {game.player.max_health}")


class FamineEvent(RandomEvent):
    """Event that reduces city resource production"""
    
    def __init__(self, event_id, name, description, production_reduction_percent):
        """
        Initialize a famine event
        
        Args:
            event_id (str): Unique identifier for the event
            name (str): Display name for the event
            description (str): Description explaining the event
            production_reduction_percent (float): Percentage to reduce production by
        """
        super().__init__(
            event_id,
            name,
            description,
            EventType.NEGATIVE,
            EventTrigger.RANDOM,
            EventDuration.MULTI_DAY
        )
        self.production_reduction_percent = production_reduction_percent
        self.city_buildings_affected = []
    
    def apply_effects(self, game):
        """Reduce city building production"""
        if hasattr(game, 'city_manager') and hasattr(game.city_manager, 'buildings'):
            for building in game.city_manager.buildings:
                if hasattr(building, 'production_rate'):
                    # Store original value
                    self.city_buildings_affected.append({
                        'building': building,
                        'original_rate': building.production_rate
                    })
                    
                    # Apply reduction
                    building.production_rate *= (1 - self.production_reduction_percent)
            
            # Log the effect
            if hasattr(game, 'debug_mode') and game.debug_mode:
                print(f"Famine: City production reduced by {self.production_reduction_percent*100}%")
    
    def remove_effects(self, game):
        """Restore city building production"""
        for affected in self.city_buildings_affected:
            if hasattr(affected['building'], 'production_rate'):
                affected['building'].production_rate = affected['original_rate']
        
        # Clear the list
        self.city_buildings_affected = []
        
        # Log the restoration
        if hasattr(game, 'debug_mode') and game.debug_mode:
            print("Famine ended: City production restored")


class WeatherEvent(RandomEvent):
    """Event that changes weather conditions"""
    
    def __init__(self, event_id, name, description, weather_type, movement_effect=0):
        """
        Initialize a weather event
        
        Args:
            event_id (str): Unique identifier for the event
            name (str): Display name for the event
            description (str): Description explaining the event
            weather_type (str): Type of weather (rain, snow, storm, etc.)
            movement_effect (float): Movement speed multiplier effect
        """
        super().__init__(
            event_id,
            name,
            description,
            EventType.NEUTRAL,
            EventTrigger.RANDOM,
            EventDuration.SINGLE_DAY
        )
        self.weather_type = weather_type
        self.movement_effect = movement_effect
        self.original_speed = None
    
    def apply_effects(self, game):
        """Apply weather effects to the game"""
        # Apply visual effects if available
        if hasattr(game, 'day_night_cycle'):
            game.day_night_cycle.set_weather(self.weather_type)
        
        # Apply movement effects if any
        if self.movement_effect != 0 and hasattr(game, 'player'):
            self.original_speed = game.player.speed
            game.player.speed *= (1 + self.movement_effect)
            
            # Log the effect
            if hasattr(game, 'debug_mode') and game.debug_mode:
                if self.movement_effect < 0:
                    print(f"Weather ({self.weather_type}): Movement speed reduced by {-self.movement_effect*100}%")
                else:
                    print(f"Weather ({self.weather_type}): Movement speed increased by {self.movement_effect*100}%")
    
    def remove_effects(self, game):
        """Remove weather effects"""
        # Reset weather if available
        if hasattr(game, 'day_night_cycle'):
            game.day_night_cycle.reset_weather()
        
        # Reset movement speed if modified
        if self.movement_effect != 0 and hasattr(game, 'player') and self.original_speed is not None:
            game.player.speed = self.original_speed
            
            # Log the restoration
            if hasattr(game, 'debug_mode') and game.debug_mode:
                print(f"Weather ({self.weather_type}) ended: Movement speed restored")


class RandomEventSystem:
    """
    System for managing random events in the game
    """
    
    def __init__(self, game):
        """
        Initialize the random event system
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.active_events = []
        self.event_history = []
        self.events_catalog = {}
        
        # Event chance settings
        self.daily_event_chance = 0.3  # 30% chance per day
        self.max_simultaneous_events = 3
        
        # Timing
        self.last_check_day = 0
        
        # Register standard events
        self._register_standard_events()
        
        # Debug mode
        self.debug_mode = False
    
    def _register_standard_events(self):
        """Register standard event types"""
        # Resource bonus events
        self.register_event(ResourceBonusEvent("resource_wood_bonus", "Lumber Windfall", 
            "A fallen tree provides extra wood.", "wood", 20))
        
        self.register_event(ResourceBonusEvent("resource_stone_bonus", "Stone Deposit", 
            "You discovered a rich stone deposit.", "stone", 15))
        
        self.register_event(ResourceBonusEvent("resource_crystal_bonus", "Crystal Formation", 
            "A rare crystal formation has been discovered.", "crystal", 10))
        
        # Negative events
        self.register_event(SicknessEvent("common_cold", "Common Cold", 
            "Your character has caught a cold, reducing maximum health.", 0.15))
        
        self.register_event(SicknessEvent("severe_illness", "Severe Illness", 
            "A severe illness affects your character, significantly reducing maximum health.", 0.25))
        
        self.register_event(FamineEvent("minor_famine", "Food Shortage", 
            "A food shortage has reduced city production.", 0.25))
        
        self.register_event(FamineEvent("major_famine", "Major Famine", 
            "A major famine has severely impacted city production.", 0.75))
        
        # Weather events
        self.register_event(WeatherEvent("light_rain", "Light Rain", 
            "A gentle rain is falling.", "rain", -0.05))
        
        self.register_event(WeatherEvent("heavy_rain", "Heavy Rain", 
            "Heavy rain makes movement more difficult.", "heavy_rain", -0.15))
        
        self.register_event(WeatherEvent("snow", "Snowfall", 
            "Snow covers the landscape, making movement more difficult.", "snow", -0.1))
        
        self.register_event(WeatherEvent("strong_winds", "Strong Winds", 
            "Strong winds push you forward.", "wind", 0.1))
    
    def register_event(self, event):
        """
        Register an event in the catalog
        
        Args:
            event (RandomEvent): Event to register
        """
        self.events_catalog[event.event_id] = event
    
    def update(self, current_day):
        """
        Update the random event system
        
        Args:
            current_day (int): The current day number
        """
        # Update active events
        self._update_active_events(current_day)
        
        # Check for new events once per day
        if current_day > self.last_check_day:
            self._check_for_new_events(current_day)
            self.last_check_day = current_day
    
    def _update_active_events(self, current_day):
        """
        Update all active events
        
        Args:
            current_day (int): The current day number
        """
        # Use a copy to allow removal during iteration
        for event in list(self.active_events):
            still_active = event.update(self.game, current_day)
            if not still_active:
                self.active_events.remove(event)
                self.event_history.append(event)
    
    def _check_for_new_events(self, current_day):
        """
        Check for and potentially trigger new events
        
        Args:
            current_day (int): The current day number
        """
        # Don't exceed max simultaneous events
        if len(self.active_events) >= self.max_simultaneous_events:
            return
        
        # Check for random event trigger
        if random.random() < self.daily_event_chance:
            self._trigger_random_event(current_day)
            
            # Log the event check
            if self.debug_mode or (hasattr(self.game, 'debug_mode') and self.game.debug_mode):
                print(f"Day {current_day}: Random event triggered")
    
    def _trigger_random_event(self, current_day):
        """
        Trigger a random event from the catalog
        
        Args:
            current_day (int): The current day number
        """
        # Filter out events that we already have active
        available_events = [e for e in self.events_catalog.values() 
                           if not any(a.event_id == e.event_id for a in self.active_events)]
        
        if not available_events:
            return
        
        # Pick a random event
        event = random.choice(available_events)
        
        # Create a new instance (to avoid modifying the template)
        event_instance = type(event)(
            event.event_id, 
            event.name, 
            event.description,
            *self._get_event_specific_args(event)
        )
        
        # Activate the event
        event_instance.activate(self.game, current_day)
        
        # Add to active events
        self.active_events.append(event_instance)
    
    def _get_event_specific_args(self, event):
        """Get the event-specific constructor arguments based on event type"""
        if isinstance(event, ResourceBonusEvent):
            return [event.resource_type, event.bonus_amount]
        elif isinstance(event, SicknessEvent):
            return [event.health_reduction_percent]
        elif isinstance(event, FamineEvent):
            return [event.production_reduction_percent]
        elif isinstance(event, WeatherEvent):
            return [event.weather_type, event.movement_effect]
        return []
    
    def get_active_events(self):
        """
        Get all currently active events
        
        Returns:
            list: List of active RandomEvent objects
        """
        return self.active_events
    
    def get_event_history(self):
        """
        Get event history
        
        Returns:
            list: List of past RandomEvent objects
        """
        return self.event_history
    
    def clear_all_events(self):
        """Clear all active events"""
        for event in list(self.active_events):
            event.deactivate(self.game)
            self.active_events.remove(event)
    
    def trigger_specific_event(self, event_id, current_day, duration_days=None):
        """
        Trigger a specific event by ID
        
        Args:
            event_id (str): ID of the event to trigger
            current_day (int): Current day number
            duration_days (int, optional): Override default duration
            
        Returns:
            bool: True if event was triggered, False otherwise
        """
        if event_id not in self.events_catalog:
            return False
        
        # Get event template
        event = self.events_catalog[event_id]
        
        # Create a new instance
        event_instance = type(event)(
            event.event_id, 
            event.name, 
            event.description,
            *self._get_event_specific_args(event)
        )
        
        # Activate the event
        event_instance.activate(self.game, current_day, duration_days)
        
        # Add to active events
        self.active_events.append(event_instance)
        
        return True
    
    def save_state(self):
        """
        Save the current state of events
        
        Returns:
            dict: Serializable state of the event system
        """
        return {
            'active_events': [event.to_dict() for event in self.active_events],
            'event_history': [event.to_dict() for event in self.event_history],
            'last_check_day': self.last_check_day
        }
    
    def load_state(self, state):
        """
        Load a saved state
        
        Args:
            state (dict): Saved state dictionary
        """
        # Clear current events
        self.clear_all_events()
        self.active_events = []
        self.event_history = []
        
        # Restore timing info
        self.last_check_day = state.get('last_check_day', 0)
        
        # Restore active events
        for event_data in state.get('active_events', []):
            event = RandomEvent.from_dict(event_data, self.events_catalog)
            if event:
                self.active_events.append(event)
        
        # Restore event history
        for event_data in state.get('event_history', []):
            event = RandomEvent.from_dict(event_data, self.events_catalog)
            if event:
                self.event_history.append(event)
    
    def enable_debug_mode(self, enabled=True):
        """
        Enable or disable debug mode
        
        Args:
            enabled (bool): Whether debug mode should be enabled
        """
        self.debug_mode = enabled 