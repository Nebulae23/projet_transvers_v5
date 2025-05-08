#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the Random Events System
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.random_events import (
    RandomEventSystem, RandomEvent, EventType, EventTrigger, EventDuration,
    ResourceBonusEvent, SicknessEvent, FamineEvent, WeatherEvent
)

class MockPlayer:
    """Mock player for testing"""
    
    def __init__(self):
        """Initialize the mock player"""
        self.max_health = 100
        self.health = 100
        self.speed = 5.0
        self.inventory = {"wood": 10, "stone": 5, "crystal": 0}
    
    def __str__(self):
        """String representation for debugging"""
        return f"Player(health={self.health}/{self.max_health}, speed={self.speed}, inventory={self.inventory})"


class MockBuilding:
    """Mock building for testing"""
    
    def __init__(self, name, production_rate):
        """Initialize the mock building"""
        self.name = name
        self.production_rate = production_rate
    
    def __str__(self):
        """String representation for debugging"""
        return f"Building({self.name}, production_rate={self.production_rate})"


class MockCityManager:
    """Mock city manager for testing"""
    
    def __init__(self):
        """Initialize the mock city manager"""
        self.buildings = [
            MockBuilding("Farm", 10),
            MockBuilding("Mine", 8),
            MockBuilding("Lumber Mill", 12)
        ]
    
    def __str__(self):
        """String representation for debugging"""
        return f"CityManager(buildings=[{', '.join(str(b) for b in self.buildings)}])"


class MockDayNightCycle:
    """Mock day night cycle for testing"""
    
    def __init__(self):
        """Initialize the mock day night cycle"""
        self.current_day = 1
        self.time_of_day = 0.5  # Midday
        self.current_weather = None
    
    def set_weather(self, weather_type):
        """Set current weather"""
        self.current_weather = weather_type
        print(f"Weather set to: {weather_type}")
    
    def reset_weather(self):
        """Reset weather to default"""
        self.current_weather = None
        print("Weather reset to default")
    
    def __str__(self):
        """String representation for debugging"""
        return f"DayNightCycle(day={self.current_day}, time={self.time_of_day}, weather={self.current_weather})"


class MockGame:
    """Mock game for testing"""
    
    def __init__(self):
        """Initialize the mock game"""
        self.player = MockPlayer()
        self.city_manager = MockCityManager()
        self.day_night_cycle = MockDayNightCycle()
        self.debug_mode = True
        self.messages = []
    
    def show_message(self, title, message, duration=3.0):
        """Show a message to the player"""
        self.messages.append({"title": title, "message": message, "duration": duration})
        print(f"Message: {title} - {message} (duration: {duration}s)")
    
    def advance_day(self):
        """Advance to the next day"""
        self.day_night_cycle.current_day += 1
        print(f"Advanced to day {self.day_night_cycle.current_day}")
    
    def get_current_day(self):
        """Get the current day number"""
        return self.day_night_cycle.current_day
    
    def __str__(self):
        """String representation for debugging"""
        return f"Game(player={self.player}, city_manager={self.city_manager}, day_night_cycle={self.day_night_cycle})"


def test_resource_bonus_event():
    """Test resource bonus event"""
    print("\n=== Testing Resource Bonus Event ===")
    
    # Create mock game
    game = MockGame()
    
    # Create resource bonus event
    event = ResourceBonusEvent(
        "test_wood_bonus",
        "Wood Bonus",
        "You found some extra wood!",
        "wood",
        15
    )
    
    # Print initial inventory
    print(f"Initial inventory: {game.player.inventory}")
    
    # Activate event
    print("Activating event...")
    event.activate(game, game.get_current_day())
    
    # Check inventory after activation
    print(f"Inventory after activation: {game.player.inventory}")
    
    # Check event state
    print(f"Event active: {event.is_active}")
    print(f"Event duration days: {event.duration_days}")
    print(f"Event end day: {event.end_day}")
    
    # Advance a day
    game.advance_day()
    
    # Update event
    print("Updating event...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active: {still_active}")
    
    print("Resource bonus event test completed.")


def test_sickness_event():
    """Test sickness event"""
    print("\n=== Testing Sickness Event ===")
    
    # Create mock game
    game = MockGame()
    
    # Create sickness event
    event = SicknessEvent(
        "test_sickness",
        "Common Cold",
        "You caught a cold!",
        0.2  # 20% health reduction
    )
    
    # Print initial health
    print(f"Initial health: {game.player.health}/{game.player.max_health}")
    
    # Activate event
    print("Activating event...")
    event.activate(game, game.get_current_day(), duration_days=2)
    
    # Check health after activation
    print(f"Health after activation: {game.player.health}/{game.player.max_health}")
    
    # Advance a day
    game.advance_day()
    
    # Update event
    print("Updating event...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active after day 1: {still_active}")
    
    # Advance another day
    game.advance_day()
    
    # Update event again
    print("Updating event again...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active after day 2: {still_active}")
    
    # Check health after event ended
    print(f"Health after event ended: {game.player.health}/{game.player.max_health}")
    
    print("Sickness event test completed.")


def test_famine_event():
    """Test famine event"""
    print("\n=== Testing Famine Event ===")
    
    # Create mock game
    game = MockGame()
    
    # Create famine event
    event = FamineEvent(
        "test_famine",
        "Food Shortage",
        "A food shortage has reduced city production.",
        0.5  # 50% production reduction
    )
    
    # Print initial production rates
    print("Initial production rates:")
    for building in game.city_manager.buildings:
        print(f"  {building.name}: {building.production_rate}")
    
    # Activate event
    print("Activating event...")
    event.activate(game, game.get_current_day(), duration_days=2)
    
    # Check production rates after activation
    print("Production rates after activation:")
    for building in game.city_manager.buildings:
        print(f"  {building.name}: {building.production_rate}")
    
    # Advance a day
    game.advance_day()
    
    # Update event
    print("Updating event...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active after day 1: {still_active}")
    
    # Advance another day
    game.advance_day()
    
    # Update event again
    print("Updating event again...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active after day 2: {still_active}")
    
    # Check production rates after event ended
    print("Production rates after event ended:")
    for building in game.city_manager.buildings:
        print(f"  {building.name}: {building.production_rate}")
    
    print("Famine event test completed.")


def test_weather_event():
    """Test weather event"""
    print("\n=== Testing Weather Event ===")
    
    # Create mock game
    game = MockGame()
    
    # Create weather event
    event = WeatherEvent(
        "test_weather",
        "Heavy Rain",
        "Heavy rain is falling.",
        "heavy_rain",
        -0.15  # 15% movement speed reduction
    )
    
    # Print initial state
    print(f"Initial weather: {game.day_night_cycle.current_weather}")
    print(f"Initial movement speed: {game.player.speed}")
    
    # Activate event
    print("Activating event...")
    event.activate(game, game.get_current_day())
    
    # Check state after activation
    print(f"Weather after activation: {game.day_night_cycle.current_weather}")
    print(f"Movement speed after activation: {game.player.speed}")
    
    # Advance a day
    game.advance_day()
    
    # Update event
    print("Updating event...")
    still_active = event.update(game, game.get_current_day())
    
    # Check if event still active
    print(f"Event still active: {still_active}")
    
    # Check state after event ended
    print(f"Weather after event ended: {game.day_night_cycle.current_weather}")
    print(f"Movement speed after event ended: {game.player.speed}")
    
    print("Weather event test completed.")


def test_random_event_system():
    """Test the random event system"""
    print("\n=== Testing Random Event System ===")
    
    # Create mock game
    game = MockGame()
    
    # Create random event system
    event_system = RandomEventSystem(game)
    
    # Enable debug mode
    event_system.enable_debug_mode(True)
    
    # Set high event chance for testing
    event_system.daily_event_chance = 1.0  # 100% chance
    
    # Print initial state
    print(f"Initial day: {game.get_current_day()}")
    print(f"Active events: {len(event_system.active_events)}")
    
    # Update system (should trigger an event)
    print("Updating event system...")
    event_system.update(game.get_current_day())
    
    # Print state after update
    print(f"Active events after update: {len(event_system.active_events)}")
    for i, event in enumerate(event_system.active_events):
        print(f"  Event {i+1}: {event.name} ({event.event_type.value})")
    
    # Advance a day
    game.advance_day()
    
    # Update system again
    print("Updating event system again...")
    event_system.update(game.get_current_day())
    
    # Print state after second update
    print(f"Active events after second update: {len(event_system.active_events)}")
    for i, event in enumerate(event_system.active_events):
        print(f"  Event {i+1}: {event.name} ({event.event_type.value})")
    
    # Test triggering a specific event
    print("\nTesting specific event trigger:")
    success = event_system.trigger_specific_event("common_cold", game.get_current_day())
    print(f"Trigger success: {success}")
    
    # Print player health after sickness
    print(f"Player health after sickness: {game.player.health}/{game.player.max_health}")
    
    # Test clearing all events
    print("\nTesting clear all events:")
    event_system.clear_all_events()
    print(f"Active events after clear: {len(event_system.active_events)}")
    
    # Print player health after clearing events
    print(f"Player health after clearing events: {game.player.health}/{game.player.max_health}")
    
    # Test save/load state
    print("\nTesting save/load state:")
    
    # Trigger an event
    event_system.trigger_specific_event("light_rain", game.get_current_day())
    
    # Save state
    state = event_system.save_state()
    print(f"Saved state with {len(event_system.active_events)} active events")
    
    # Clear events
    event_system.clear_all_events()
    print(f"Cleared events, now have {len(event_system.active_events)} active events")
    
    # Load state
    event_system.load_state(state)
    print(f"Loaded state, now have {len(event_system.active_events)} active events")
    
    print("Random event system test completed.")


def main():
    """Main test function"""
    print("=== NIGHTFALL DEFENDERS RANDOM EVENTS SYSTEM TEST ===\n")
    
    try:
        # Run tests
        test_resource_bonus_event()
        test_sickness_event()
        test_famine_event() 
        test_weather_event()
        test_random_event_system()
        
        print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")
        return 0
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 