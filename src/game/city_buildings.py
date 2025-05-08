#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
City Building Types for Nightfall Defenders
Contains specific building implementations for the city automation system
"""

from game.city_automation import Building, BuildingType, ResourceType, BuildingState

class House(Building):
    """Housing for population"""
    
    def __init__(self, building_id, position):
        """Initialize a house"""
        super().__init__(
            building_id, 
            "House", 
            BuildingType.HOUSE,
            position,
            size=(1, 1)
        )
        
        # Population capacity
        self.worker_capacity = 5
        self.max_health = 100
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.POPULATION: 0.1  # Slow population growth
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.FOOD: 0.2
        }

class Farm(Building):
    """Food production building"""
    
    def __init__(self, building_id, position):
        """Initialize a farm"""
        super().__init__(
            building_id, 
            "Farm", 
            BuildingType.FARM,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 10
        self.max_health = 150
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.FOOD: 1.0
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.WATER: 0.5
        }

class Mine(Building):
    """Resource extraction building"""
    
    def __init__(self, building_id, position):
        """Initialize a mine"""
        super().__init__(
            building_id, 
            "Mine", 
            BuildingType.MINE,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 15
        self.max_health = 200
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.STONE: 0.8,
            ResourceType.IRON: 0.5
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.ENERGY: 1.0
        }

class Barracks(Building):
    """Military training building"""
    
    def __init__(self, building_id, position):
        """Initialize barracks"""
        super().__init__(
            building_id, 
            "Barracks", 
            BuildingType.BARRACKS,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 20
        self.max_health = 300
        self.health = self.max_health
        
        # Defense boost for city
        self.defense_boost = 1.2
        
        # Resource consumption
        self.consumption = {
            ResourceType.FOOD: 1.0,
            ResourceType.GOLD: 0.5
        }

class Tower(Building):
    """Defensive tower"""
    
    def __init__(self, building_id, position):
        """Initialize a tower"""
        super().__init__(
            building_id, 
            "Tower", 
            BuildingType.TOWER,
            position,
            size=(1, 1)
        )
        
        # Worker capacity
        self.worker_capacity = 3
        self.max_health = 250
        self.health = self.max_health
        
        # Defense capabilities
        self.defense_range = 30.0
        self.defense_damage = 15.0
        self.defense_cooldown = 2.0
        
        # Resource consumption
        self.consumption = {
            ResourceType.ENERGY: 0.5
        }

class Workshop(Building):
    """Production building for advanced resources"""
    
    def __init__(self, building_id, position):
        """Initialize a workshop"""
        super().__init__(
            building_id, 
            "Workshop", 
            BuildingType.WORKSHOP,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 10
        self.max_health = 200
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.ENERGY: 1.0,
            ResourceType.GOLD: 0.5
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.WOOD: 0.8,
            ResourceType.IRON: 0.5
        }

class Market(Building):
    """Trading building for resources"""
    
    def __init__(self, building_id, position):
        """Initialize a market"""
        super().__init__(
            building_id, 
            "Market", 
            BuildingType.MARKET,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 8
        self.max_health = 150
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.GOLD: 1.0
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.FOOD: 0.3,
            ResourceType.WOOD: 0.3
        }
        
        # Trade efficiency - affects resource exchange rates
        self.trade_efficiency = 1.0

class Storage(Building):
    """Storage building for increased resource capacity"""
    
    def __init__(self, building_id, position):
        """Initialize a storage building"""
        super().__init__(
            building_id, 
            "Storage", 
            BuildingType.STORAGE,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 5
        self.max_health = 200
        self.health = self.max_health
        
        # Storage bonuses
        self.storage = {
            ResourceType.FOOD: 200,
            ResourceType.WOOD: 200,
            ResourceType.STONE: 200,
            ResourceType.IRON: 100,
            ResourceType.GOLD: 100
        }

class Wall(Building):
    """Defensive wall segment"""
    
    def __init__(self, building_id, position):
        """Initialize a wall segment"""
        super().__init__(
            building_id, 
            "Wall", 
            BuildingType.WALL,
            position,
            size=(1, 1)
        )
        
        # Wall properties
        self.worker_capacity = 0  # No workers needed
        self.max_health = 500
        self.health = self.max_health
        
        # Wall provides passive defense
        self.defense_boost = 1.1  # Small boost per segment

class Gate(Building):
    """City gate with defensive properties"""
    
    def __init__(self, building_id, position):
        """Initialize a city gate"""
        super().__init__(
            building_id, 
            "Gate", 
            BuildingType.GATE,
            position,
            size=(2, 1)
        )
        
        # Gate properties
        self.worker_capacity = 5
        self.max_health = 400
        self.health = self.max_health
        
        # Defense capabilities
        self.defense_range = 20.0
        self.defense_damage = 10.0
        self.defense_cooldown = 3.0
        
        # Gate can be opened/closed
        self.is_open = True
        
    def toggle_gate(self):
        """Toggle gate between open and closed"""
        self.is_open = not self.is_open
        return self.is_open

class Laboratory(Building):
    """Research building for tech upgrades"""
    
    def __init__(self, building_id, position):
        """Initialize a laboratory"""
        super().__init__(
            building_id, 
            "Laboratory", 
            BuildingType.LABORATORY,
            position,
            size=(2, 2)
        )
        
        # Worker capacity
        self.worker_capacity = 10
        self.max_health = 150
        self.health = self.max_health
        
        # Resource production
        self.production = {
            ResourceType.KNOWLEDGE: 1.0
        }
        
        # Resource consumption
        self.consumption = {
            ResourceType.ENERGY: 1.0,
            ResourceType.GOLD: 0.5
        }
        
        # Research properties
        self.research_bonus = 1.0
        self.active_research = None
        self.research_progress = 0.0

# Factory function to create buildings
def create_building(building_type, building_id, position):
    """
    Create a building of the specified type
    
    Args:
        building_type (BuildingType): Type of building to create
        building_id (str): Building ID
        position (tuple): Grid position (x, y)
        
    Returns:
        Building: The created building
    """
    if building_type == BuildingType.HOUSE:
        return House(building_id, position)
    elif building_type == BuildingType.FARM:
        return Farm(building_id, position)
    elif building_type == BuildingType.MINE:
        return Mine(building_id, position)
    elif building_type == BuildingType.BARRACKS:
        return Barracks(building_id, position)
    elif building_type == BuildingType.TOWER:
        return Tower(building_id, position)
    elif building_type == BuildingType.WORKSHOP:
        return Workshop(building_id, position)
    elif building_type == BuildingType.MARKET:
        return Market(building_id, position)
    elif building_type == BuildingType.TEMPLE:
        return Building(building_id, "Temple", building_type, position, (2, 2))
    elif building_type == BuildingType.WALL:
        return Wall(building_id, position)
    elif building_type == BuildingType.GATE:
        return Gate(building_id, position)
    elif building_type == BuildingType.STORAGE:
        return Storage(building_id, position)
    elif building_type == BuildingType.LABORATORY:
        return Laboratory(building_id, position)
    else:
        # Generic building as fallback
        return Building(building_id, f"Unknown Building", building_type, position, (1, 1)) 