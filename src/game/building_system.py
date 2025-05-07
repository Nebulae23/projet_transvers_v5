#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Building System for Nightfall Defenders
Defines building types, costs, and benefits for city management
"""

class BuildingSystem:
    """Manages building types, costs, and benefits"""
    
    def __init__(self, game):
        """
        Initialize the building system
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Available building types
        self.building_types = self._create_building_types()
        
        # Player's constructed buildings
        self.constructed_buildings = []
        
        # Maximum number of each building type
        self.max_buildings_per_type = 5
    
    def _create_building_types(self):
        """Define all available building types"""
        return {
            "watchtower": {
                "name": "Watchtower",
                "description": "Provides early warning of enemy attacks",
                "costs": {"wood": 50, "stone": 30},
                "benefits": {"defense": 10, "detection_range": 15},
                "model": "buildings/watchtower.glb",
                "build_time": 30,  # seconds
                "category": "defense",
            },
            "barracks": {
                "name": "Barracks",
                "description": "Trains defenders to help fight enemies",
                "costs": {"wood": 80, "stone": 40},
                "benefits": {"max_defenders": 3, "defense": 15},
                "model": "buildings/barracks.glb",
                "build_time": 45,
                "category": "defense",
            },
            "farm": {
                "name": "Farm",
                "description": "Produces food to sustain your population",
                "costs": {"wood": 30, "stone": 10},
                "benefits": {"food_production": 5},
                "model": "buildings/farm.glb",
                "build_time": 20,
                "category": "resource",
            },
            "workshop": {
                "name": "Workshop",
                "description": "Improves crafting efficiency",
                "costs": {"wood": 40, "stone": 20, "crystal": 5},
                "benefits": {"crafting_speed": 15, "resource_efficiency": 10},
                "model": "buildings/workshop.glb",
                "build_time": 40,
                "category": "production",
            },
            "wall": {
                "name": "Wall",
                "description": "Defensive barrier against enemies",
                "costs": {"stone": 60},
                "benefits": {"defense": 20},
                "model": "buildings/wall.glb",
                "build_time": 25,
                "category": "defense",
            },
            "infirmary": {
                "name": "Infirmary",
                "description": "Heals wounded defenders and the player",
                "costs": {"wood": 45, "stone": 15, "herb": 10},
                "benefits": {"healing_rate": 5},
                "model": "buildings/infirmary.glb",
                "build_time": 35,
                "category": "support",
            }
        }
    
    def can_build(self, building_type):
        """
        Check if player has resources to build a specific building
        
        Args:
            building_type: The type of building to check
            
        Returns:
            bool: True if player has enough resources, False otherwise
        """
        if building_type not in self.building_types:
            return False
            
        building_data = self.building_types[building_type]
        
        # Check if player has enough resources
        for resource, amount in building_data["costs"].items():
            if self.game.player.resources.get(resource, 0) < amount:
                return False
                
        # Check if player has reached maximum building count for this type
        building_count = sum(1 for b in self.constructed_buildings if b["type"] == building_type)
        if building_count >= self.max_buildings_per_type:
            return False
            
        return True
        
    def start_construction(self, building_type, position):
        """
        Start constructing a building
        
        Args:
            building_type: The type of building to construct
            position: The position (Vec3) to place the building
            
        Returns:
            bool: True if construction started successfully, False otherwise
        """
        if not self.can_build(building_type):
            return False
            
        building_data = self.building_types[building_type]
        
        # Deduct resources
        for resource, amount in building_data["costs"].items():
            self.game.player.resources[resource] -= amount
            
        # Create building entity
        building = {
            "type": building_type,
            "position": position,
            "construction_progress": 0,  # 0 to 100
            "build_time": building_data["build_time"],
            "health": 100,
            "entity": None  # Will be set by entity manager
        }
        
        self.constructed_buildings.append(building)
        
        # Add to entity manager
        self.game.entity_manager.create_building(building_type, position, building)
        
        return True
        
    def update(self, dt):
        """
        Update building construction progress
        
        Args:
            dt: Delta time in seconds
        """
        for building in self.constructed_buildings:
            if building["construction_progress"] < 100:
                # Progress construction based on time
                progress_increment = (dt / building["build_time"]) * 100
                building["construction_progress"] += progress_increment
                
                # Cap progress at 100%
                if building["construction_progress"] > 100:
                    building["construction_progress"] = 100
                    # Building is complete - apply benefits
                    self._apply_building_benefits(building)
                    
                # Update visual representation based on progress
                if building["entity"]:
                    self.game.entity_manager.update_building_construction(building["entity"], building["construction_progress"])
    
    def _apply_building_benefits(self, building):
        """
        Apply benefits of a completed building
        
        Args:
            building: The building data
        """
        building_type = building["type"]
        if building_type not in self.building_types:
            return
            
        building_data = self.building_types[building_type]
        
        # Apply benefits based on building type
        for benefit_type, value in building_data["benefits"].items():
            if benefit_type == "defense":
                self.game.city_manager.defense += value
            elif benefit_type == "detection_range":
                self.game.city_manager.detection_range += value
            elif benefit_type == "max_defenders":
                self.game.city_manager.max_defenders += value
            elif benefit_type == "food_production":
                self.game.city_manager.food_production += value
            elif benefit_type == "crafting_speed":
                # Adjust crafting speed in crafting system
                self.game.crafting_system.crafting_speed_multiplier += value / 100.0
            elif benefit_type == "resource_efficiency":
                # Adjust resource efficiency in crafting system
                self.game.crafting_system.resource_efficiency += value / 100.0
            elif benefit_type == "healing_rate":
                self.game.city_manager.healing_rate += value
                
    def demolish_building(self, building_idx):
        """
        Demolish a building and recover partial resources
        
        Args:
            building_idx: Index of the building in constructed_buildings list
            
        Returns:
            bool: True if demolished successfully, False otherwise
        """
        if building_idx < 0 or building_idx >= len(self.constructed_buildings):
            return False
            
        building = self.constructed_buildings[building_idx]
        building_type = building["type"]
        
        if building_type not in self.building_types:
            return False
            
        # Remove benefits if building was completed
        if building["construction_progress"] >= 100:
            self._remove_building_benefits(building)
            
        # Recover partial resources (50%)
        building_data = self.building_types[building_type]
        for resource, amount in building_data["costs"].items():
            recovery_amount = amount // 2
            self.game.player.resources[resource] = self.game.player.resources.get(resource, 0) + recovery_amount
            
        # Remove from entity manager
        if building["entity"]:
            self.game.entity_manager.remove_entity(building["entity"])
            
        # Remove from list
        self.constructed_buildings.pop(building_idx)
        
        return True
        
    def _remove_building_benefits(self, building):
        """
        Remove benefits of a building when demolished
        
        Args:
            building: The building data
        """
        building_type = building["type"]
        if building_type not in self.building_types:
            return
            
        building_data = self.building_types[building_type]
        
        # Remove benefits based on building type
        for benefit_type, value in building_data["benefits"].items():
            if benefit_type == "defense":
                self.game.city_manager.defense -= value
            elif benefit_type == "detection_range":
                self.game.city_manager.detection_range -= value
            elif benefit_type == "max_defenders":
                self.game.city_manager.max_defenders -= value
            elif benefit_type == "food_production":
                self.game.city_manager.food_production -= value
            elif benefit_type == "crafting_speed":
                # Adjust crafting speed in crafting system
                self.game.crafting_system.crafting_speed_multiplier -= value / 100.0
            elif benefit_type == "resource_efficiency":
                # Adjust resource efficiency in crafting system
                self.game.crafting_system.resource_efficiency -= value / 100.0
            elif benefit_type == "healing_rate":
                self.game.city_manager.healing_rate -= value
                
    def get_building_info(self, building_type):
        """
        Get information about a building type
        
        Args:
            building_type: The type of building
            
        Returns:
            dict: Building information or None if not found
        """
        return self.building_types.get(building_type) 