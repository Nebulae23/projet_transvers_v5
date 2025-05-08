#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
City Automation System for Nightfall Defenders
Manages city buildings, resources, and defense automation
"""

from enum import Enum
import random
import math
from panda3d.core import Vec3, NodePath

class BuildingType(Enum):
    """Enumeration of different building types"""
    HOUSE = "house"
    FARM = "farm"
    MINE = "mine"
    BARRACKS = "barracks"
    TOWER = "tower"
    WORKSHOP = "workshop"
    MARKET = "market"
    TEMPLE = "temple"
    WALL = "wall"
    GATE = "gate"
    STORAGE = "storage"
    LABORATORY = "laboratory"

class BuildingState(Enum):
    """Enumeration of building states"""
    UNDER_CONSTRUCTION = "under_construction"
    OPERATIONAL = "operational"
    DAMAGED = "damaged"
    UPGRADING = "upgrading"
    DESTROYED = "destroyed"

class ResourceType(Enum):
    """Enumeration of city resource types"""
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    GOLD = "gold"
    IRON = "iron"
    POPULATION = "population"
    ENERGY = "energy"
    KNOWLEDGE = "knowledge"
    WATER = "water"

class Building:
    """Base class for all city buildings"""
    
    def __init__(self, building_id, name, building_type, position, size=(1, 1)):
        """
        Initialize a building
        
        Args:
            building_id (str): Unique identifier
            name (str): Display name
            building_type (BuildingType): Type of building
            position (tuple): Grid position (x, y)
            size (tuple): Size in grid cells (width, height)
        """
        self.building_id = building_id
        self.name = name
        self.building_type = building_type
        self.position = position
        self.size = size
        
        # State information
        self.state = BuildingState.UNDER_CONSTRUCTION
        self.construction_progress = 0.0
        self.health = 100.0
        self.max_health = 100.0
        self.level = 1
        self.upgrade_progress = 0.0
        
        # Production and consumption
        self.production = {}  # ResourceType -> amount per cycle
        self.consumption = {}  # ResourceType -> amount per cycle
        self.storage = {}  # ResourceType -> storage capacity
        
        # Visual representation
        self.node_path = None
        self.construction_effect = None
        self.operational_effect = None
        self.damage_effect = None
        
        # Workers
        self.worker_capacity = 0
        self.assigned_workers = 0
        
        # Defense capabilities (for defensive buildings)
        self.defense_range = 0.0
        self.defense_damage = 0.0
        self.defense_cooldown = 0.0
        self.defense_current_cooldown = 0.0
        
    def update(self, dt, city_manager):
        """
        Update building state
        
        Args:
            dt: Time delta
            city_manager: The city manager instance
        """
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._update_construction(dt, city_manager)
        elif self.state == BuildingState.OPERATIONAL:
            self._update_operational(dt, city_manager)
        elif self.state == BuildingState.DAMAGED:
            self._update_damaged(dt, city_manager)
        elif self.state == BuildingState.UPGRADING:
            self._update_upgrading(dt, city_manager)
            
    def _update_construction(self, dt, city_manager):
        """Update during construction phase"""
        # Progress construction based on available workers
        construction_speed = 0.1 * self.assigned_workers * dt
        self.construction_progress += construction_speed
        
        # Update health proportional to construction progress
        if self.state == BuildingState.UNDER_CONSTRUCTION and self.health < self.max_health:
            # Calculate max health at current construction progress
            max_health_at_progress = self.max_health * (self.construction_progress / 100.0)
            
            # Only increase health (don't decrease if we assign fewer workers)
            if max_health_at_progress > self.health:
                self.health = max_health_at_progress
        
        # Check if construction is complete
        if self.construction_progress >= 100.0:
            self.construction_progress = 100.0
            self.state = BuildingState.OPERATIONAL
            self.health = self.max_health  # Fully restore health
            self._on_construction_complete(city_manager)
    
    def _update_operational(self, dt, city_manager):
        """Update during operational phase"""
        # Handle resource production and consumption
        self._process_resources(dt, city_manager)
        
        # Handle defense actions for defensive buildings
        self._handle_defense(dt, city_manager)
    
    def _update_damaged(self, dt, city_manager):
        """Update during damaged phase"""
        # Slowly repair if workers are assigned
        repair_speed = 0.05 * self.assigned_workers * dt
        self.health += repair_speed
        
        # Check if repairs are complete
        if self.health >= self.max_health:
            self.health = self.max_health
            self.state = BuildingState.OPERATIONAL
            
            # Remove damage effects
            if self.damage_effect:
                self.damage_effect.removeNode()
                self.damage_effect = None
    
    def _update_upgrading(self, dt, city_manager):
        """Update during upgrading phase"""
        # Progress upgrade based on available workers
        upgrade_speed = 0.05 * self.assigned_workers * dt
        self.upgrade_progress += upgrade_speed
        
        # Check if upgrade is complete
        if self.upgrade_progress >= 100.0:
            self.upgrade_progress = 100.0
            self.level += 1
            self.state = BuildingState.OPERATIONAL
            self._on_upgrade_complete(city_manager)
    
    def _process_resources(self, dt, city_manager):
        """Process resource production and consumption"""
        # Only process resources if operational and has workers
        if self.state != BuildingState.OPERATIONAL or self.assigned_workers <= 0:
            return
            
        worker_efficiency = min(1.0, self.assigned_workers / self.worker_capacity)
        
        # Consume resources
        all_resources_available = True
        for resource_type, amount in self.consumption.items():
            required_amount = amount * dt * worker_efficiency
            if not city_manager.resource_manager.consume_resource(resource_type, required_amount):
                all_resources_available = False
                break
        
        # Produce resources only if all required resources were consumed
        if all_resources_available:
            for resource_type, amount in self.production.items():
                produced_amount = amount * dt * worker_efficiency
                city_manager.resource_manager.add_resource(resource_type, produced_amount)
    
    def _handle_defense(self, dt, city_manager):
        """Handle defense actions for defensive buildings"""
        # Only defensive buildings with defense_range > 0 can defend
        if self.defense_range <= 0 or self.state != BuildingState.OPERATIONAL:
            return
            
        # Update cooldown
        if self.defense_current_cooldown > 0:
            self.defense_current_cooldown -= dt
            return
            
        # Find enemies in range
        if hasattr(city_manager.game, 'entity_manager'):
            enemies_in_range = self._get_enemies_in_range(city_manager)
            
            if enemies_in_range:
                # Attack the closest enemy
                self._attack_enemy(enemies_in_range[0], city_manager)
                self.defense_current_cooldown = self.defense_cooldown
    
    def _get_enemies_in_range(self, city_manager):
        """Get enemies in defense range"""
        enemies_in_range = []
        
        # Convert grid position to world position
        world_pos = city_manager.grid_to_world(self.position)
        
        # Check all enemies
        for enemy in city_manager.game.entity_manager.enemies.values():
            distance = (enemy.position - Vec3(world_pos[0], world_pos[1], 0)).length()
            if distance <= self.defense_range:
                enemies_in_range.append((enemy, distance))
                
        # Sort by distance
        enemies_in_range.sort(key=lambda x: x[1])
        
        # Return just the enemy objects
        return [enemy for enemy, _ in enemies_in_range]
    
    def _attack_enemy(self, enemy, city_manager):
        """Attack an enemy"""
        # Apply damage
        if hasattr(enemy, 'take_damage'):
            enemy.take_damage(self.defense_damage, None)
            
        # Create attack effect
        if hasattr(city_manager.game, 'effect_manager'):
            city_manager.game.effect_manager.create_projectile_effect(
                city_manager.grid_to_world(self.position),
                enemy.position,
                "defense_projectile"
            )
    
    def _on_construction_complete(self, city_manager):
        """Handle construction completion"""
        print(f"Building {self.name} construction completed!")
        
        # Update visuals
        if self.node_path:
            # Remove construction effect
            if self.construction_effect:
                self.construction_effect.removeNode()
                self.construction_effect = None
                
            # Add operational effect
            if hasattr(city_manager.game, 'effect_manager'):
                self.operational_effect = city_manager.game.effect_manager.create_building_effect(
                    self.building_type,
                    city_manager.grid_to_world(self.position)
                )
                
        # Update city stats
        city_manager.on_building_completed(self)
    
    def _on_upgrade_complete(self, city_manager):
        """Handle upgrade completion"""
        print(f"Building {self.name} upgraded to level {self.level}!")
        
        # Scale stats based on new level
        self.max_health = self.max_health * 1.2
        self.health = self.max_health
        
        # Scale production and consumption
        for resource_type in self.production:
            self.production[resource_type] *= 1.3
            
        for resource_type in self.consumption:
            self.consumption[resource_type] *= 1.2
            
        # Scale defense stats
        self.defense_damage *= 1.3
        self.defense_range *= 1.1
        
        # Update building appearance
        if self.node_path and hasattr(city_manager.game, 'model_manager'):
            # Update model to show upgraded version
            city_manager.game.model_manager.update_building_model(self)
            
        # Update city stats
        city_manager.on_building_upgraded(self)
    
    def take_damage(self, amount, source=None):
        """
        Deal damage to the building
        
        Args:
            amount: Amount of damage
            source: Entity that caused the damage (optional)
            
        Returns:
            bool: True if building was destroyed
        """
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            # Buildings under construction take double damage
            amount *= 2
            
        self.health -= amount
        
        # Check if building is destroyed
        if self.health <= 0:
            self.health = 0
            self.state = BuildingState.DESTROYED
            
            # We defer the on_destroyed call since it needs city_manager
            # The caller should call on_destroyed if this returns True
            return True
            
        # Check if building becomes damaged
        if self.health < self.max_health * 0.5 and self.state == BuildingState.OPERATIONAL:
            self.state = BuildingState.DAMAGED
            
        return False
    
    def repair(self, city_manager=None):
        """
        Start repairing a damaged building
        
        Args:
            city_manager: The city manager instance
        """
        if self.state == BuildingState.DAMAGED:
            # Reset construction effect for repairs
            if self.node_path and city_manager and hasattr(city_manager.game, 'effect_manager'):
                self.construction_effect = city_manager.game.effect_manager.create_repair_effect(
                    city_manager.grid_to_world(self.position)
                )
    
    def start_repair(self, city_manager):
        """
        Start the repair process for a damaged building
        
        Args:
            city_manager: The city manager instance
            
        Returns:
            bool: True if repair started successfully
        """
        # Only damaged buildings can be repaired
        if self.state != BuildingState.DAMAGED and self.state != BuildingState.DESTROYED:
            return False
            
        # Calculate repair costs
        repair_costs = self.calculate_repair_costs()
        
        # Check if we have enough resources
        if not city_manager.resource_manager.can_afford(repair_costs):
            print(f"Not enough resources to repair {self.name}")
            return False
            
        # Pay the costs
        city_manager.resource_manager.pay_cost(repair_costs)
        
        # Set state to under repair (treat like under construction)
        self.state = BuildingState.UNDER_CONSTRUCTION
        
        # Calculate repair progress - start at 50% for damaged buildings
        if self.health > 0:
            # For damaged buildings, repair progress starts proportional to health
            self.construction_progress = 50.0 * (self.health / self.max_health)
        else:
            # For destroyed buildings, start from scratch
            self.construction_progress = 0.0
            self.health = 1  # Set minimal health to avoid division by zero
        
        # Create repair effect
        if self.node_path and hasattr(city_manager.game, 'effect_manager'):
            self.construction_effect = city_manager.game.effect_manager.create_repair_effect(
                city_manager.grid_to_world(self.position)
            )
        # Or update visual effects with fallback
        elif self.node_path:
            self._update_visual_effects(city_manager)
            
        print(f"Started repairing {self.name}")
        return True
    
    def rebuild(self, city_manager):
        """
        Rebuild a destroyed building
        
        Args:
            city_manager: The city manager instance
            
        Returns:
            bool: True if rebuild started successfully
        """
        # Only destroyed buildings can be rebuilt
        if self.state != BuildingState.DESTROYED:
            return False
            
        # Rebuilding is effectively the same as repairing a completely destroyed building
        return self.start_repair(city_manager)
    
    def calculate_repair_costs(self):
        """
        Calculate the resource costs for repairing this building
        
        Returns:
            dict: ResourceType -> amount mapping of costs
        """
        costs = {}
        
        # Base repair costs vary by building type
        if self.building_type == BuildingType.HOUSE:
            costs[ResourceType.WOOD] = 10
            costs[ResourceType.STONE] = 5
        elif self.building_type == BuildingType.FARM:
            costs[ResourceType.WOOD] = 8
            costs[ResourceType.STONE] = 3
        elif self.building_type == BuildingType.TOWER:
            costs[ResourceType.WOOD] = 5
            costs[ResourceType.STONE] = 15
        elif self.building_type == BuildingType.BARRACKS:
            costs[ResourceType.WOOD] = 15
            costs[ResourceType.STONE] = 10
            costs[ResourceType.IRON] = 5
        elif self.building_type == BuildingType.WORKSHOP:
            costs[ResourceType.WOOD] = 12
            costs[ResourceType.STONE] = 8
            costs[ResourceType.IRON] = 3
        elif self.building_type == BuildingType.STORAGE:
            costs[ResourceType.WOOD] = 20
            costs[ResourceType.STONE] = 10
        elif self.building_type == BuildingType.WALL:
            costs[ResourceType.STONE] = 15
            costs[ResourceType.IRON] = 2
        elif self.building_type == BuildingType.GATE:
            costs[ResourceType.WOOD] = 10
            costs[ResourceType.STONE] = 15
            costs[ResourceType.IRON] = 5
        else:
            # Default costs
            costs[ResourceType.WOOD] = 10
            costs[ResourceType.STONE] = 10
            
        # Adjust costs based on building size
        width, height = self.size
        size_factor = width * height / 2  # A 2x2 building would have factor 2
        
        # Scale costs by size
        for resource in costs:
            costs[resource] = int(costs[resource] * size_factor)
        
        # If completely destroyed, full cost; otherwise proportional to damage
        if self.state == BuildingState.DESTROYED:
            damage_factor = 1.0
        else:
            # Calculate what percentage of health is missing
            damage_factor = 1.0 - (self.health / self.max_health)
            
        # Scale costs by damage factor (minimum 10% of full cost)
        for resource in costs:
            costs[resource] = max(1, int(costs[resource] * max(0.1, damage_factor)))
            
        return costs
    
    def start_upgrade(self, city_manager=None):
        """
        Start upgrading the building
        
        Args:
            city_manager: The city manager instance
        """
        if self.state == BuildingState.OPERATIONAL:
            self.state = BuildingState.UPGRADING
            self.upgrade_progress = 0.0
            
            # Create upgrade effect
            if self.node_path and city_manager and hasattr(city_manager.game, 'effect_manager'):
                self.construction_effect = city_manager.game.effect_manager.create_upgrade_effect(
                    city_manager.grid_to_world(self.position)
                )
    
    def assign_workers(self, count):
        """
        Assign workers to this building
        
        Args:
            count: Number of workers to assign
            
        Returns:
            int: Actual number of workers assigned
        """
        # Ensure we don't exceed capacity
        available_capacity = self.worker_capacity - self.assigned_workers
        assigned = min(count, available_capacity)
        
        self.assigned_workers += assigned
        return assigned
    
    def unassign_workers(self, count):
        """
        Unassign workers from this building
        
        Args:
            count: Number of workers to unassign
            
        Returns:
            int: Actual number of workers unassigned
        """
        # Ensure we don't go below zero
        removed = min(count, self.assigned_workers)
        
        self.assigned_workers -= removed
        return removed
    
    def can_be_placed(self, city_grid):
        """
        Check if this building can be placed at its position
        
        Args:
            city_grid: The city grid
            
        Returns:
            bool: True if placement is valid
        """
        # Check if position is within grid bounds
        x, y = self.position
        width, height = self.size
        
        if (x < 0 or y < 0 or 
            x + width > city_grid.width or 
            y + height > city_grid.height):
            return False
            
        # Check if all cells are empty
        for dx in range(width):
            for dy in range(height):
                if city_grid.grid[x + dx][y + dy] is not None:
                    return False
                    
        return True
        
    def create_visual_representation(self, render, city_manager):
        """
        Create a visual representation of the building
        
        Args:
            render: The render node to attach to
            city_manager: The city manager instance
        """
        # Remove existing representation if any
        if self.node_path:
            self.node_path.removeNode()
            
        # Create a node for the building
        self.node_path = NodePath(f"building_{self.building_id}")
        
        # Get world position from grid position
        world_pos = city_manager.grid_to_world(self.position)
        
        # Try to load the appropriate model
        model_path = f"models/building_{self.building_type.value.lower()}"
        try:
            model = render.getParent().loader.loadModel(model_path)
            model.reparentTo(self.node_path)
        except:
            print(f"Error loading building model for {self.building_type.value}")
            
            # Use a fallback colored box
            from panda3d.core import CardMaker
            cm = CardMaker(f"building_{self.building_id}")
            
            # Size based on building dimensions
            width, height = self.size
            cm.setFrame(0, width, 0, height)
            
            card = self.node_path.attachNewNode(cm.generate())
            
            # Color based on building type
            if self.building_type == BuildingType.HOUSE:
                card.setColor(0.8, 0.6, 0.4, 1)  # Brown
            elif self.building_type == BuildingType.FARM:
                card.setColor(0.7, 0.9, 0.3, 1)  # Green-yellow
            elif self.building_type == BuildingType.MINE:
                card.setColor(0.6, 0.6, 0.6, 1)  # Gray
            elif self.building_type == BuildingType.BARRACKS:
                card.setColor(0.5, 0.5, 0.8, 1)  # Blue-gray
            elif self.building_type == BuildingType.TOWER:
                card.setColor(0.7, 0.3, 0.3, 1)  # Red-brown
            elif self.building_type == BuildingType.WORKSHOP:
                card.setColor(0.8, 0.6, 0.3, 1)  # Orange-brown
            elif self.building_type == BuildingType.MARKET:
                card.setColor(0.9, 0.8, 0.3, 1)  # Gold
            elif self.building_type == BuildingType.STORAGE:
                card.setColor(0.5, 0.7, 0.9, 1)  # Light blue
            else:
                card.setColor(0.7, 0.7, 0.7, 1)  # Default gray
        
        # Position the building
        self.node_path.setPos(world_pos[0], world_pos[1], 0.1)  # Slightly above ground
        
        # Parent to render
        self.node_path.reparentTo(render)
        
        # Add visual effects based on state
        self._update_visual_effects(city_manager)
    
    def _update_visual_effects(self, city_manager):
        """
        Update visual effects based on building state
        
        Args:
            city_manager: The city manager instance
        """
        # Clear existing effects
        if self.construction_effect:
            self.construction_effect.removeNode()
            self.construction_effect = None
            
        if self.operational_effect:
            self.operational_effect.removeNode()
            self.operational_effect = None
            
        if self.damage_effect:
            self.damage_effect.removeNode()
            self.damage_effect = None
            
        # Add effects based on state
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            # Show construction scaffolding or effect
            from panda3d.core import CardMaker
            cm = CardMaker("construction_effect")
            cm.setFrame(-0.2, self.size[0] + 0.2, -0.2, self.size[1] + 0.2)
            
            self.construction_effect = self.node_path.attachNewNode(cm.generate())
            self.construction_effect.setColor(0.8, 0.8, 0.2, 0.5)  # Yellow transparent
            self.construction_effect.setPos(0, 0, 0.2)  # Above building
            
        elif self.state == BuildingState.DAMAGED:
            # Show damage effect
            from panda3d.core import CardMaker
            cm = CardMaker("damage_effect")
            cm.setFrame(-0.1, self.size[0] + 0.1, -0.1, self.size[1] + 0.1)
            
            self.damage_effect = self.node_path.attachNewNode(cm.generate())
            self.damage_effect.setColor(0.9, 0.2, 0.2, 0.5)  # Red transparent
            self.damage_effect.setPos(0, 0, 0.2)  # Above building
            
        elif self.state == BuildingState.UPGRADING:
            # Show upgrade effect
            from panda3d.core import CardMaker
            cm = CardMaker("upgrade_effect")
            cm.setFrame(-0.2, self.size[0] + 0.2, -0.2, self.size[1] + 0.2)
            
            self.construction_effect = self.node_path.attachNewNode(cm.generate())
            self.construction_effect.setColor(0.2, 0.8, 0.9, 0.5)  # Blue transparent
            self.construction_effect.setPos(0, 0, 0.2)  # Above building
            
        elif self.state == BuildingState.OPERATIONAL:
            # Show operational effect if needed
            if self.building_type in [BuildingType.FARM, BuildingType.MINE, BuildingType.WORKSHOP]:
                from panda3d.core import CardMaker
                cm = CardMaker("operational_effect")
                cm.setFrame(-0.1, self.size[0] + 0.1, -0.1, self.size[1] + 0.1)
                
                self.operational_effect = self.node_path.attachNewNode(cm.generate())
                
                # Different colors for different building types
                if self.building_type == BuildingType.FARM:
                    self.operational_effect.setColor(0.3, 0.9, 0.3, 0.3)  # Green transparent
                elif self.building_type == BuildingType.MINE:
                    self.operational_effect.setColor(0.7, 0.7, 0.7, 0.3)  # Gray transparent
                elif self.building_type == BuildingType.WORKSHOP:
                    self.operational_effect.setColor(0.9, 0.6, 0.2, 0.3)  # Orange transparent
                
                self.operational_effect.setPos(0, 0, 0.2)  # Above building
        
        elif self.state == BuildingState.DESTROYED:
            # Show destruction effect
            from panda3d.core import CardMaker
            cm = CardMaker("destruction_effect")
            cm.setFrame(-0.1, self.size[0] + 0.1, -0.1, self.size[1] + 0.1)
            
            self.damage_effect = self.node_path.attachNewNode(cm.generate())
            self.damage_effect.setColor(0.1, 0.1, 0.1, 0.8)  # Dark transparent
            self.damage_effect.setPos(0, 0, 0.1)  # Above ground
            
            # Add rubble/smoke effect
            from panda3d.core import CardMaker
            cm = CardMaker("rubble_effect")
            cm.setFrame(-0.05, self.size[0] + 0.05, -0.05, self.size[1] + 0.05)
            
            rubble_effect = self.node_path.attachNewNode(cm.generate())
            rubble_effect.setColor(0.4, 0.4, 0.4, 1.0)  # Gray
            rubble_effect.setPos(0.1, 0.1, 0.05)  # Offset slightly for rubble pile effect
            
            # Change the building model appearance to show destruction
            for child in self.node_path.getChildren():
                if child != self.damage_effect and child != rubble_effect:
                    # Make building partially transparent and darker
                    child.setColorScale(0.3, 0.3, 0.3, 0.7)
                    # Tilt the building slightly to show it's destroyed
                    child.setR(15)  # Rotate around X axis
                    child.setP(-5)  # Rotate around Y axis
    
    def on_destroyed(self, city_manager):
        """
        Handle building destruction
        
        Args:
            city_manager: The city manager instance
        """
        print(f"Building {self.name} was destroyed!")
        
        # Update resource rates (reverse production and consumption)
        for resource_type, amount in self.production.items():
            city_manager.resource_manager.update_rate(resource_type, -amount)
            
        for resource_type, amount in self.consumption.items():
            city_manager.resource_manager.update_rate(resource_type, amount)
            
        # Update storage capacity
        for resource_type, amount in self.storage.items():
            city_manager.resource_manager.increase_capacity(resource_type, -amount)
        
        # Reset assigned workers (they're not working in a destroyed building)
        self.assigned_workers = 0
        
        # Update visual appearance
        if self.node_path:
            self._update_visual_effects(city_manager)
            
        # Create destruction effect if game has effect manager
        if hasattr(city_manager.game, 'effect_manager'):
            city_manager.game.effect_manager.create_destruction_effect(
                city_manager.grid_to_world(self.position)
            )
            
        # Notify the city manager that a building was destroyed
        city_manager.on_building_destroyed(self)

class CityGrid:
    """Manages the spatial layout of city buildings"""
    
    def __init__(self, width, height):
        """
        Initialize the city grid
        
        Args:
            width (int): Grid width
            height (int): Grid height
        """
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(height)] for _ in range(width)]
        self.terrain_types = [['grass' for _ in range(height)] for _ in range(width)]
        self.terrain_costs = {
            'grass': 1.0,
            'forest': 1.5,
            'rock': 2.0,
            'water': 5.0,
            'road': 0.5,
        }
        
        # Visual representation
        self.node_path = None
        self.tile_nodes = [[None for _ in range(height)] for _ in range(width)]
        
    def initialize_terrain(self, generator=None):
        """
        Initialize terrain with optional generator
        
        Args:
            generator: Terrain generator function
        """
        if generator:
            # Use custom generator
            self.terrain_types = generator(self.width, self.height)
        else:
            # Use simple random terrain
            for x in range(self.width):
                for y in range(self.height):
                    if random.random() < 0.7:
                        self.terrain_types[x][y] = 'grass'
                    elif random.random() < 0.5:
                        self.terrain_types[x][y] = 'forest'
                    elif random.random() < 0.5:
                        self.terrain_types[x][y] = 'rock'
                    else:
                        self.terrain_types[x][y] = 'water'
    
    def place_building(self, building):
        """
        Place a building on the grid
        
        Args:
            building: The building to place
            
        Returns:
            bool: True if placement was successful
        """
        if not building.can_be_placed(self):
            return False
            
        # Place the building
        x, y = building.position
        width, height = building.size
        
        for dx in range(width):
            for dy in range(height):
                self.grid[x + dx][y + dy] = building
                
        return True
    
    def remove_building(self, building):
        """
        Remove a building from the grid
        
        Args:
            building: The building to remove
        """
        x, y = building.position
        width, height = building.size
        
        for dx in range(width):
            for dy in range(height):
                if self.grid[x + dx][y + dy] == building:
                    self.grid[x + dx][y + dy] = None
    
    def get_building_at(self, position):
        """
        Get the building at a position
        
        Args:
            position (tuple): Grid position (x, y)
            
        Returns:
            Building or None: The building at the position
        """
        x, y = position
        
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
            
        return self.grid[x][y]
    
    def get_terrain_at(self, position):
        """
        Get the terrain type at a position
        
        Args:
            position (tuple): Grid position (x, y)
            
        Returns:
            str: Terrain type
        """
        x, y = position
        
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return 'grass'  # Default
            
        return self.terrain_types[x][y]
    
    def set_terrain_at(self, position, terrain_type):
        """
        Set the terrain type at a position
        
        Args:
            position (tuple): Grid position (x, y)
            terrain_type (str): Terrain type
        """
        x, y = position
        
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
            
        self.terrain_types[x][y] = terrain_type
        
        # Update visual representation
        if self.tile_nodes[x][y]:
            # Update tile appearance
            pass
    
    def get_construction_cost(self, position, size):
        """
        Calculate the construction cost for a position
        
        Args:
            position (tuple): Grid position (x, y)
            size (tuple): Size in grid cells (width, height)
            
        Returns:
            float: Construction cost multiplier
        """
        x, y = position
        width, height = size
        
        # Default cost
        total_cost = 0
        
        for dx in range(width):
            for dy in range(height):
                px, py = x + dx, y + dy
                
                if px < 0 or py < 0 or px >= self.width or py >= self.height:
                    continue
                    
                terrain = self.terrain_types[px][py]
                total_cost += self.terrain_costs.get(terrain, 1.0)
                
        return total_cost
    
    def find_path(self, start, end):
        """
        Find a path between two points on the grid
        
        Args:
            start (tuple): Start position (x, y)
            end (tuple): End position (x, y)
            
        Returns:
            list: List of positions forming a path
        """
        # Simple A* pathfinding
        # This is a simplified version - a real implementation would be more complex
        
        # Create open and closed sets
        open_set = [start]
        closed_set = set()
        
        # Track path and costs
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda p: f_score.get(p, float('inf')))
            
            if current == end:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score
                tentative_g = g_score.get(current, float('inf')) + self._movement_cost(current, neighbor)
                
                if neighbor not in open_set:
                    open_set.append(neighbor)
                elif tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                
                # This path is better, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
        
        # No path found
        return []
    
    def _heuristic(self, a, b):
        """Calculate heuristic distance between points"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _movement_cost(self, a, b):
        """Calculate movement cost between adjacent points"""
        terrain = self.terrain_types[b[0]][b[1]]
        return self.terrain_costs.get(terrain, 1.0)
    
    def _get_neighbors(self, position):
        """Get valid neighboring positions"""
        x, y = position
        neighbors = []
        
        # Check four adjacent cells
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            if (nx < 0 or ny < 0 or 
                nx >= self.width or ny >= self.height):
                continue
                
            # Skip if there's a building
            if self.grid[nx][ny] is not None:
                continue
                
            neighbors.append((nx, ny))
            
        return neighbors
    
    def create_visual_representation(self, render):
        """
        Create a visual representation of the grid
        
        Args:
            render: The render node to attach to
        """
        # Create a node for the grid
        self.node_path = NodePath("city_grid")
        self.node_path.reparentTo(render)
        
        # Create tiles
        for x in range(self.width):
            for y in range(self.height):
                terrain = self.terrain_types[x][y]
                
                try:
                    model = render.getParent().loader.loadModel(f"models/terrain_{terrain}")
                    model.setPos(x, y, 0)
                    model.reparentTo(self.node_path)
                    self.tile_nodes[x][y] = model
                except:
                    print(f"Error loading terrain model for {terrain}")
                    
                    # Use a simple card as fallback
                    from panda3d.core import CardMaker
                    cm = CardMaker(f"terrain_{x}_{y}")
                    cm.setFrame(0, 1, 0, 1)
                    
                    card = self.node_path.attachNewNode(cm.generate())
                    card.setPos(x, y, 0)
                    
                    # Color based on terrain
                    if terrain == 'grass':
                        card.setColor(0.3, 0.8, 0.3, 1)
                    elif terrain == 'forest':
                        card.setColor(0.1, 0.5, 0.1, 1)
                    elif terrain == 'rock':
                        card.setColor(0.5, 0.5, 0.5, 1)
                    elif terrain == 'water':
                        card.setColor(0.1, 0.3, 0.8, 1)
                    elif terrain == 'road':
                        card.setColor(0.8, 0.7, 0.5, 1)
                    
                    self.tile_nodes[x][y] = card

class ResourceManager:
    """Manages city resources and storage"""
    
    def __init__(self):
        """Initialize the resource manager"""
        self.resources = {}
        self.storage_capacity = {}
        self.resource_rates = {}  # Net production/consumption rates
        
        # Initialize base resources
        for resource_type in ResourceType:
            self.resources[resource_type] = 0
            self.storage_capacity[resource_type] = 100  # Default capacity
            self.resource_rates[resource_type] = 0
    
    def add_resource(self, resource_type, amount):
        """
        Add resources
        
        Args:
            resource_type (ResourceType): Type of resource
            amount (float): Amount to add
            
        Returns:
            float: Actual amount added (limited by storage)
        """
        if amount <= 0:
            return 0
            
        # Get current level and capacity
        current = self.resources.get(resource_type, 0)
        capacity = self.storage_capacity.get(resource_type, float('inf'))
        
        # Calculate how much can be added
        can_add = min(amount, capacity - current)
        
        if can_add <= 0:
            return 0
            
        # Add resources
        self.resources[resource_type] = current + can_add
        
        return can_add
    
    def consume_resource(self, resource_type, amount):
        """
        Consume resources
        
        Args:
            resource_type (ResourceType): Type of resource
            amount (float): Amount to consume
            
        Returns:
            bool: True if the resources were available and consumed
        """
        if amount <= 0:
            return True
            
        # Check if enough resources are available
        current = self.resources.get(resource_type, 0)
        
        if current < amount:
            return False
            
        # Consume resources
        self.resources[resource_type] = current - amount
        
        return True
    
    def get_resource(self, resource_type):
        """
        Get the current amount of a resource
        
        Args:
            resource_type (ResourceType): Type of resource
            
        Returns:
            float: Current amount
        """
        return self.resources.get(resource_type, 0)
    
    def get_capacity(self, resource_type):
        """
        Get the storage capacity for a resource
        
        Args:
            resource_type (ResourceType): Type of resource
            
        Returns:
            float: Storage capacity
        """
        return self.storage_capacity.get(resource_type, 0)
    
    def increase_capacity(self, resource_type, amount):
        """
        Increase storage capacity
        
        Args:
            resource_type (ResourceType): Type of resource
            amount (float): Amount to increase by
        """
        current = self.storage_capacity.get(resource_type, 0)
        self.storage_capacity[resource_type] = current + amount
    
    def update_rate(self, resource_type, delta):
        """
        Update the production/consumption rate
        
        Args:
            resource_type (ResourceType): Type of resource
            delta (float): Change in rate (positive for production, negative for consumption)
        """
        current = self.resource_rates.get(resource_type, 0)
        self.resource_rates[resource_type] = current + delta
    
    def get_rate(self, resource_type):
        """
        Get the net production/consumption rate
        
        Args:
            resource_type (ResourceType): Type of resource
            
        Returns:
            float: Net rate (positive for production, negative for consumption)
        """
        return self.resource_rates.get(resource_type, 0)
    
    def update(self, dt):
        """
        Update resources based on rates
        
        Args:
            dt: Time delta
        """
        # Apply resource rates
        for resource_type, rate in self.resource_rates.items():
            if rate > 0:
                # Production
                self.add_resource(resource_type, rate * dt)
            elif rate < 0:
                # Consumption
                self.consume_resource(resource_type, -rate * dt)
    
    def can_afford(self, costs):
        """
        Check if resources are available for a cost
        
        Args:
            costs (dict): ResourceType -> amount mapping
            
        Returns:
            bool: True if all resources are available
        """
        for resource_type, amount in costs.items():
            if self.resources.get(resource_type, 0) < amount:
                return False
                
        return True
    
    def pay_cost(self, costs):
        """
        Pay a resource cost
        
        Args:
            costs (dict): ResourceType -> amount mapping
            
        Returns:
            bool: True if payment was successful
        """
        # First check if we can afford it
        if not self.can_afford(costs):
            return False
            
        # Pay the costs
        for resource_type, amount in costs.items():
            self.resources[resource_type] -= amount
            
        return True 