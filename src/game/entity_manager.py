#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entity Manager for Nightfall Defenders
Manages all game entities, including the player, enemies, projectiles, etc.
"""

from panda3d.core import Vec3
import random
import math

# Import entity types
from game.player import Player
from game.enemy import BasicEnemy, RangedEnemy
from game.projectile import Projectile, StraightProjectile, ArcingProjectile, HomingProjectile, SpiralProjectile
from game.resource_node import ResourceNode
from game.resource_drop import ResourceDrop
from game.crafting_bench import CraftingBench

class EntityManager:
    """Manages all game entities and their interactions"""
    
    def __init__(self, game):
        """Initialize the entity manager"""
        self.game = game
        
        # Lists of entities by type
        self.entities = {}  # All entities by ID
        self.players = []  # Player entities
        self.enemies = []  # Enemy entities
        self.projectiles = []  # Projectile entities
        self.resources = []  # Resource entities
        self.resource_nodes = []  # Resource node entities
        self.resource_drops = []  # Resource drop entities
        self.interactables = []  # Interactable objects
        self.buildings = []  # Building entities
        
        # Entity ID counter
        self.next_entity_id = 1
        
        # Spatial partitioning for performance
        self.cell_size = 20.0  # Size of each spatial cell
        self.spatial_grid = {}  # Grid cells for spatial partitioning
        
        # Entity creation settings
        self.max_enemies = 50  # Maximum number of enemies in the world
        self.max_projectiles = 100  # Maximum number of projectiles
        self.max_resource_nodes = 100  # Maximum number of resource nodes
        self.max_resource_drops = 100  # Maximum number of resource drops
        
        # Track total enemies killed
        self.enemies_killed = 0
        self.resources_collected = {
            "wood": 0,
            "stone": 0,
            "crystal": 0,
            "herb": 0,
            "experience": 0
        }
        
        # Track subservient enemies
        self.subservient_enemies = []
        
        # Debug information
        self.debug_info = {
            "enemy_count": 0,
            "projectile_count": 0,
            "update_time": 0.0,
            "subservient_count": 0
        }
    
    def create_player(self, position=Vec3(0, 0, 0)):
        """Create the player entity"""
        player = Player(self.game)
        player.position = Vec3(position)
        player.is_player = True
        
        # Add to entity lists
        self.entities[self.next_entity_id] = player
        self.players.append(player)
        
        # Make accessible directly from game
        self.game.player = player
        
        # Add to spatial partitioning
        self.add_to_spatial_grid(player)
        
        return self.next_entity_id
    
    def create_enemy(self, enemy_type, position):
        """
        Create an enemy entity
        
        Args:
            enemy_type (str): Type of enemy to create ("basic" or "ranged")
            position (Vec3): Position to spawn the enemy
        
        Returns:
            Enemy: The created enemy object
        """
        # Check if we've reached the enemy limit
        if len(self.enemies) >= self.max_enemies:
            return None
        
        enemy = None
        if enemy_type == "basic":
            enemy = BasicEnemy(self.game, position)
        elif enemy_type == "ranged":
            enemy = RangedEnemy(self.game, position)
        else:
            print(f"Unknown enemy type: {enemy_type}")
            return None
        
        # Add to entity lists
        self.entities[self.next_entity_id] = enemy
        self.enemies.append(enemy)
        
        # Add to spatial partitioning
        self.add_to_spatial_grid(enemy)
        
        # Increment the entity ID
        self.next_entity_id += 1
        
        # Return the enemy object
        return enemy
    
    def create_projectile(self, projectile_type, origin, direction, owner=None, target=None, damage=10):
        """
        Create a projectile entity
        
        Args:
            projectile_type (str): Type of projectile to create
            origin (Vec3): Starting position
            direction (Vec3): Direction vector
            owner: Entity that created the projectile
            target: Optional target entity for homing projectiles
            damage (int): Amount of damage the projectile deals
        
        Returns:
            entity_id: ID of the created projectile entity
        """
        # Check if we've reached the projectile limit
        if len(self.projectiles) >= self.max_projectiles:
            # Remove oldest projectile to make room
            oldest_projectile = self.projectiles[0]
            self.remove_entity(oldest_projectile)
        
        # Create projectile based on type
        projectile = None
        
        if projectile_type == "straight":
            projectile = StraightProjectile(self.game, origin, direction, owner, damage=damage)
        elif projectile_type == "arcing":
            projectile = ArcingProjectile(self.game, origin, direction, owner, damage=damage)
        elif projectile_type == "spiral":
            projectile = SpiralProjectile(self.game, origin, direction, owner, damage=damage)
        elif projectile_type == "homing" and target:
            projectile = HomingProjectile(self.game, origin, direction, owner, target, damage=damage)
        else:
            # Default to straight projectile
            projectile = StraightProjectile(self.game, origin, direction, owner, damage=damage)
        
        # Add to entity lists
        self.entities[self.next_entity_id] = projectile
        self.projectiles.append(projectile)
        
        print(f"Created {projectile_type} projectile at {origin}")
        
        return self.next_entity_id
    
    def create_resource_node(self, position, resource_type="wood"):
        """
        Create a resource node at the specified position
        
        Args:
            position (Vec3): Position to create the resource node
            resource_type (str): Type of resource this node will provide
        
        Returns:
            entity_id: ID of the created resource node
        """
        # Create the resource node
        node = ResourceNode(self.game, position, resource_type)
        
        # Add to entity lists
        self.entities[self.next_entity_id] = node
        self.resource_nodes.append(node)
        
        # Add to spatial partitioning
        self.add_to_spatial_grid(node)
        
        return self.next_entity_id
    
    def populate_resource_nodes(self, count=20, area_size=30):
        """
        Populate the world with random resource nodes
        
        Args:
            count (int): Number of resource nodes to create
            area_size (float): Size of the area to populate
        """
        resource_types = ["wood", "stone", "crystal", "herb"]
        weights = [0.5, 0.3, 0.1, 0.1]  # Probability weights for each type
        
        # Create specified number of resource nodes
        for _ in range(count):
            # Random position within the area
            x = random.uniform(-area_size, area_size)
            y = random.uniform(-area_size, area_size)
            
            # Keep resources away from the center (player spawn)
            distance_from_center = math.sqrt(x*x + y*y)
            if distance_from_center < 10:  # Minimum distance from center
                continue
            
            # Select resource type based on weights
            resource_type = random.choices(resource_types, weights=weights)[0]
            
            # Create the resource node
            self.create_resource_node(Vec3(x, y, 0), resource_type)
    
    def create_resource_drop(self, position, resource_type, amount=1):
        """
        Create a resource drop entity at the specified position
        
        Args:
            position (Vec3): Position to create the drop
            resource_type (str): Type of resource
            amount (int): Amount of the resource
        
        Returns:
            entity_id: ID of the created resource drop
        """
        # Check if we've reached the drop limit
        if len(self.resource_drops) >= self.max_resource_drops:
            # Remove oldest drop
            oldest_drop = self.resource_drops[0]
            self.resource_drops.remove(oldest_drop)
            if oldest_drop in self.entities:
                del self.entities[oldest_drop]
        
        # Create the resource drop
        drop = ResourceDrop(self.game, position, resource_type, amount)
        
        # Add to lists
        self.entities[self.next_entity_id] = drop
        self.resource_drops.append(drop)
        
        return self.next_entity_id
    
    def create_crafting_bench(self, position):
        """
        Create a crafting bench at the specified position
        
        Args:
            position (Vec3): Position to create the crafting bench
        
        Returns:
            entity_id: ID of the created crafting bench
        """
        # Create the crafting bench
        bench = CraftingBench(self.game, position)
        
        # Add to entity lists
        self.entities[self.next_entity_id] = bench
        self.interactables.append(bench)
        
        # Add to spatial partitioning
        self.add_to_spatial_grid(bench)
        
        return self.next_entity_id
    
    def create_building(self, building_type, position, building_data):
        """
        Create a building entity
        
        Args:
            building_type (str): Type of building
            position (Vec3): Position to place the building
            building_data (dict): Building data
            
        Returns:
            entity_id: ID of the created building entity
        """
        # Load building model based on type
        building_info = self.game.building_system.building_types.get(building_type)
        if not building_info:
            print(f"Unknown building type: {building_type}")
            return None
            
        model_path = building_info.get("model", "models/box")  # Fallback to a box if model not found
        
        try:
            # Create entity
            entity = NodePath(f"building_{building_type}")
            entity.reparentTo(self.game.render)
            entity.setPos(position)
            
            # Try to load model
            try:
                model = self.game.loader.loadModel(model_path)
                model.reparentTo(entity)
            except Exception as e:
                print(f"Failed to load building model {model_path}: {e}")
                # Create a placeholder model
                from panda3d.core import CardMaker
                cm = CardMaker("building_placeholder")
                cm.setFrame(-2, 2, -2, 2)
                model = entity.attachNewNode(cm.generate())
                model.setP(-90)  # Make it flat on the ground
                model.setZ(0.1)  # Slightly above ground
            
            # Set scale based on building type
            if building_type == "watchtower":
                entity.setScale(1.0, 1.0, 2.0)
            elif building_type == "wall":
                entity.setScale(2.0, 0.5, 1.0)
            else:
                entity.setScale(1.5, 1.5, 1.0)
                
            # Add construction scaffolding for buildings in progress
            self.update_building_construction(entity, 0)  # Start at 0% progress
            
            # Add entity properties
            entity_id = self.next_entity_id
            self.next_entity_id += 1
            
            entity.setPythonTag("entity_id", entity_id)
            entity.setPythonTag("entity_type", "building")
            entity.setPythonTag("building_type", building_type)
            entity.setPythonTag("position", position)
            entity.setPythonTag("building_data", building_data)
            entity.setPythonTag("interactable", False)  # Buildings are not interactable by default
            
            # Store entity
            self.entities[entity_id] = entity
            self.buildings.append(entity)
            
            # Update building data with entity reference
            building_data["entity"] = entity
            
            return entity_id
            
        except Exception as e:
            print(f"Error creating building: {e}")
            return None
            
    def update_building_construction(self, entity, progress):
        """
        Update building visual based on construction progress
        
        Args:
            entity: Building entity
            progress (float): Construction progress (0-100)
        """
        if not entity:
            return
            
        # For now, we'll just adjust opacity based on construction progress
        # In a more complete implementation, this would show different construction stages
        if progress < 100:
            # Show scaffolding around building
            if not entity.find("scaffolding"):
                from panda3d.core import CardMaker
                cm = CardMaker("scaffolding")
                cm.setFrame(-2.2, 2.2, 0, 2.2)
                
                # Create scaffolding on each side
                for angle in [0, 90, 180, 270]:
                    scaffold = entity.attachNewNode(cm.generate())
                    scaffold.setH(angle)
                    scaffold.setPos(0, 0, 0)
                    scaffold.setColorScale(0.7, 0.7, 0.5, 0.8)
                    scaffold.setName("scaffolding")
                
            # Make building partially transparent based on progress
            alpha = 0.2 + (progress / 100.0) * 0.8
            for child in entity.getChildren():
                if child.getName() != "scaffolding":
                    child.setAlphaScale(alpha)
        else:
            # Remove scaffolding once construction is complete
            for scaffold in entity.findAllMatches("**/scaffolding"):
                scaffold.removeNode()
                
            # Make building fully opaque
            for child in entity.getChildren():
                child.setAlphaScale(1.0)
                
    def update(self, dt):
        """
        Update all entities
        
        Args:
            dt (float): Delta time since last update
        """
        # Update all entities
        entities_to_remove = []
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            active = projectile.update(dt)
            if not active:
                entities_to_remove.append(projectile)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            # Track enemies that have become subservient
            if hasattr(enemy, 'psychology') and hasattr(enemy.psychology, 'state'):
                from game.enemy_psychology import PsychologicalState
                
                # Add newly subservient enemies to the list
                if enemy.psychology.state == PsychologicalState.SUBSERVIENT and enemy not in self.subservient_enemies:
                    self.subservient_enemies.append(enemy)
                # Remove enemies that are no longer subservient
                elif enemy.psychology.state != PsychologicalState.SUBSERVIENT and enemy in self.subservient_enemies:
                    self.subservient_enemies.remove(enemy)
        
        # Update player(s)
        for player in self.players:
            player.update(dt)
        
        # Update resource nodes
        for node in list(self.resource_nodes):
            if node.update(dt) == False:
                self.resource_nodes.remove(node)
                if node in self.entities:
                    del self.entities[node]
        
        # Update resource drops
        for drop in list(self.resource_drops):
            if drop.update(dt) == False:
                self.resource_drops.remove(drop)
                if drop in self.entities:
                    del self.entities[drop]
        
        # Update interactables
        for interactable in list(self.interactables):
            if hasattr(interactable, 'update'):
                if interactable.update(dt) == False:
                    self.interactables.remove(interactable)
                    if interactable in self.entities:
                        del self.entities[interactable]
        
        # Remove any inactive entities
        for entity in entities_to_remove:
            self.remove_entity(entity)
        
        # Update debug information
        self.debug_info["enemy_count"] = len(self.enemies)
        self.debug_info["projectile_count"] = len(self.projectiles)
        self.debug_info["resource_node_count"] = len(self.resource_nodes)
        self.debug_info["resource_drop_count"] = len(self.resource_drops)
        self.debug_info["subservient_count"] = len(self.subservient_enemies)
    
    def spawn_random_enemies(self, count, min_distance=15.0, max_distance=30.0):
        """
        Spawn a number of random enemies around the player
        
        Args:
            count (int): Number of enemies to spawn
            min_distance (float): Minimum distance from player
            max_distance (float): Maximum distance from player
        
        Returns:
            int: Number of enemies successfully spawned
        """
        if not self.game.player:
            return 0
            
        player_pos = self.game.player.position
        spawned = 0
        
        # Get spawn multiplier from day/night cycle if available
        spawn_multiplier = 1.0
        if hasattr(self.game, 'day_night_cycle'):
            spawn_multiplier = self.game.day_night_cycle.get_enemy_spawn_multiplier()
        
        # Apply adaptive difficulty spawn rate multiplier if available
        if hasattr(self.game, 'adaptive_difficulty_system'):
            # Get current difficulty factors
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            spawn_multiplier *= factors['enemy_spawn_rate']
            
            # Debug info
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                print(f"Applying adaptive difficulty to spawn rate: x{factors['enemy_spawn_rate']:.2f}")
                print(f"Combined spawn multiplier: x{spawn_multiplier:.2f}")
        
        # Adjust count based on spawn multiplier
        adjusted_count = int(count * spawn_multiplier)
        
        # Ensure at least one enemy spawns if count > 0, even with low multipliers
        if count > 0 and adjusted_count == 0:
            adjusted_count = 1
            
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            print(f"Spawning {adjusted_count} enemies (original count: {count})")
        
        for _ in range(adjusted_count):
            # Skip if we've reached the enemy limit
            if len(self.enemies) >= self.max_enemies:
                break
                
            # Generate random angle and distance
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(min_distance, max_distance)
            
            # Calculate spawn position
            spawn_x = player_pos.x + math.cos(angle) * distance
            spawn_y = player_pos.y + math.sin(angle) * distance
            spawn_pos = Vec3(spawn_x, spawn_y, 0)
            
            # Check if this position is valid
            if not self._is_valid_spawn_position(spawn_pos):
                continue
            
            # Determine enemy type - apply difficulty-based probabilities
            enemy_type_probs = {
                "basic": 0.6,   # Default 60% chance for basic enemy
                "ranged": 0.2,  # Default 20% chance for ranged enemy
                "nimble": 0.1,  # Default 10% chance for nimble enemy
                "brute": 0.05,  # Default 5% chance for brute enemy
                "alpha": 0.05   # Default 5% chance for alpha enemy
            }
            
            # Modify probabilities based on difficulty if available
            if hasattr(self.game, 'adaptive_difficulty_system'):
                factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
                # Higher difficulty means more special enemy types
                if factors['enemy_spawn_rate'] > 1.0:
                    # Reduce basic enemies, increase special types
                    modifier = (factors['enemy_spawn_rate'] - 1.0) * 0.5
                    enemy_type_probs["basic"] = max(0.3, 0.6 - modifier)
                    enemy_type_probs["ranged"] = min(0.4, 0.2 + modifier * 0.3)
                    enemy_type_probs["nimble"] = min(0.2, 0.1 + modifier * 0.2)
                    enemy_type_probs["brute"] = min(0.15, 0.05 + modifier * 0.25)
                    enemy_type_probs["alpha"] = min(0.15, 0.05 + modifier * 0.25)
            
            # Select enemy type based on probabilities
            enemy_types = list(enemy_type_probs.keys())
            enemy_weights = [enemy_type_probs[t] for t in enemy_types]
            enemy_type = random.choices(enemy_types, weights=enemy_weights, k=1)[0]
            
            # Create the enemy
            if self.create_enemy(enemy_type, spawn_pos):
                spawned += 1
                
        return spawned
        
    def spawn_enemy_at_position(self, position, force_spawn=False):
        """
        Spawn an enemy at a specific position (used for fog-based spawning)
        
        Args:
            position (Vec3): Position to spawn the enemy
            force_spawn (bool): Whether to force spawn even if at max enemies
            
        Returns:
            Enemy: The spawned enemy or None if unsuccessful
        """
        # Skip if we've reached the enemy limit and not forcing
        if len(self.enemies) >= self.max_enemies and not force_spawn:
            return None
            
        # Check if this position is valid
        if not self._is_valid_spawn_position(position):
            return None
            
        # Get spawn multiplier and strength multiplier from day/night cycle if available
        spawn_multiplier = 1.0
        strength_multiplier = 1.0
        if hasattr(self.game, 'day_night_cycle'):
            spawn_multiplier = self.game.day_night_cycle.get_enemy_spawn_multiplier()
            strength_multiplier = self.game.day_night_cycle.get_enemy_strength_multiplier()
        
        # Apply adaptive difficulty if available
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            spawn_multiplier *= factors['enemy_spawn_rate']
            
            # Debug info
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                print(f"Fog spawn using adaptive difficulty: x{factors['enemy_spawn_rate']:.2f}")
                print(f"Combined spawn chance: x{spawn_multiplier:.2f}")
        
        # Skip spawn chance based on spawn multiplier
        # Higher spawn_multiplier means greater chance of spawning
        if random.random() > spawn_multiplier * 0.5:
            return None
        
        # Determine enemy type based on difficulty
        enemy_type_probs = {
            "basic": 0.5,   # Default 50% chance for basic enemy
            "ranged": 0.3,  # Default 30% chance for ranged enemy (higher for fog)
            "nimble": 0.1,  # Default 10% chance for nimble enemy
            "brute": 0.05,  # Default 5% chance for brute enemy
            "alpha": 0.05   # Default 5% chance for alpha enemy
        }
        
        # Modify probabilities based on difficulty if available
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            # Higher difficulty means more special enemy types
            if factors['enemy_spawn_rate'] > 1.0:
                # Reduce basic enemies, increase special types
                modifier = (factors['enemy_spawn_rate'] - 1.0) * 0.5
                enemy_type_probs["basic"] = max(0.3, 0.5 - modifier)
                enemy_type_probs["ranged"] = min(0.4, 0.3 + modifier * 0.2)
                enemy_type_probs["nimble"] = min(0.2, 0.1 + modifier * 0.2)
                enemy_type_probs["brute"] = min(0.15, 0.05 + modifier * 0.3)
                enemy_type_probs["alpha"] = min(0.15, 0.05 + modifier * 0.3)
        
        # Select enemy type based on probabilities
        enemy_types = list(enemy_type_probs.keys())
        enemy_weights = [enemy_type_probs[t] for t in enemy_types]
        enemy_type = random.choices(enemy_types, weights=enemy_weights, k=1)[0]
        
        # Create the enemy
        enemy = self.create_enemy(enemy_type, position)
        
        # Apply night spawn buffs if spawned from fog
        if enemy and strength_multiplier > 1.0:
            # Buff enemy based on night strength multiplier
            enemy.max_health *= strength_multiplier
            enemy.health = enemy.max_health
            enemy.damage *= strength_multiplier
            
            # Apply visual effect to indicate night-buffed enemy
            if hasattr(enemy, 'model'):
                # Add a glow effect or color tint to indicate buffed status
                try:
                    enemy.model.setColorScale(0.7, 0.7, 1.2, 1.0)  # Slight blue tint
                except:
                    pass
        
        # Record spawn in performance tracker if available
        if enemy and hasattr(self.game, 'performance_tracker'):
            self.game.performance_tracker.record_combat_event('enemy_spawned', source=enemy_type)
        
        return enemy
    
    def _is_valid_spawn_position(self, position):
        """
        Check if a position is valid for enemy spawning
        
        Args:
            position (Vec3): Position to check
            
        Returns:
            bool: True if position is valid for spawning
        """
        # Check if too close to player
        if self.game.player:
            distance_to_player = (position - self.game.player.position).length()
            if distance_to_player < 10.0:  # Minimum safe distance from player
                return False
        
        # Check if inside city boundaries
        if hasattr(self.game, 'city_manager') and hasattr(self.game.city_manager, 'is_inside_city'):
            if self.game.city_manager.is_inside_city(position):
                return False
                
        # Check if collision with buildings or other obstacles
        # This would need proper collision detection based on your implementation
        
        return True
    
    def find_enemy_targets_for_subservient(self, subservient_enemy, max_targets=3):
        """
        Find potential enemy targets for a subservient enemy to attack
        
        Args:
            subservient_enemy: The subservient enemy looking for targets
            max_targets (int): Maximum number of targets to return
            
        Returns:
            list: Potential enemy targets (non-subservient enemies)
        """
        if not subservient_enemy or not hasattr(subservient_enemy, 'position'):
            return []
            
        # Get subservient enemy position
        pos = subservient_enemy.position
        
        # Get detection range (or use default)
        detection_range = getattr(subservient_enemy, 'detection_range', 10.0)
        
        # Find nearby enemies that are not subservient themselves
        targets = []
        for enemy in self.enemies:
            # Skip the subservient enemy itself
            if enemy == subservient_enemy:
                continue
                
            # Skip other subservient enemies
            if enemy in self.subservient_enemies:
                continue
                
            # Check distance
            if hasattr(enemy, 'position'):
                distance = (enemy.position - pos).length()
                if distance <= detection_range:
                    targets.append(enemy)
        
        # Sort by distance and limit to max_targets
        targets.sort(key=lambda e: (e.position - pos).length())
        return targets[:max_targets]
    
    def get_nearby_entities(self, position, radius, entity_type=None):
        """
        Get entities near a position using spatial partitioning
        
        Args:
            position (Vec3): Center position
            radius (float): Search radius
            entity_type (str, optional): Type of entity to filter for
        
        Returns:
            list: Entities within the specified radius
        """
        nearby = []
        
        # Simple approach without spatial partitioning
        for entity in self.entities.values():
            # Skip if not the requested type
            if entity_type:
                if entity_type == "enemy" and entity not in self.enemies:
                    continue
                if entity_type == "player" and entity not in self.players:
                    continue
                if entity_type == "projectile" and entity not in self.projectiles:
                    continue
                if entity_type == "subservient" and entity not in self.subservient_enemies:
                    continue
            
            # Check distance
            if hasattr(entity, 'position'):
                distance = (entity.position - position).length()
                if distance <= radius:
                    nearby.append(entity)
        
        return nearby
    
    def get_nearby_interactables(self, position, radius):
        """
        Get interactable entities near a position
        
        Args:
            position (Vec3): Center position
            radius (float): Search radius
        
        Returns:
            list: Interactable entities within the specified radius
        """
        nearby = []
        
        for entity in self.interactables:
            if hasattr(entity, 'position'):
                distance = (entity.position - position).length()
                if distance <= radius:
                    nearby.append(entity)
        
        return nearby
    
    def add_to_spatial_grid(self, entity):
        """
        Add an entity to the spatial partitioning grid
        
        Args:
            entity: The entity to add
        """
        if hasattr(entity, 'position'):
            cell_x = int(entity.position.x / self.cell_size)
            cell_y = int(entity.position.y / self.cell_size)
            cell_key = (cell_x, cell_y)
            
            if cell_key not in self.spatial_grid:
                self.spatial_grid[cell_key] = []
                
            self.spatial_grid[cell_key].append(entity)
            
            # Store the cell with the entity for quick removal
            if hasattr(entity, 'setPythonTag'):
                entity.setPythonTag("spatial_cell", cell_key)
            else:
                entity.spatial_cell = cell_key
    
    def remove_from_spatial_grid(self, entity):
        """
        Remove an entity from the spatial partitioning grid
        
        Args:
            entity: The entity to remove
        """
        # Get the cell key from the entity if it has one
        cell_key = None
        if hasattr(entity, 'getPythonTag') and entity.getPythonTag("spatial_cell"):
            cell_key = entity.getPythonTag("spatial_cell")
        elif hasattr(entity, 'spatial_cell'):
            cell_key = entity.spatial_cell
            
        # Remove from the grid if the cell exists
        if cell_key and cell_key in self.spatial_grid:
            if entity in self.spatial_grid[cell_key]:
                self.spatial_grid[cell_key].remove(entity)
    
    def update_spatial_grid_position(self, entity):
        """
        Update an entity's position in the spatial grid if it has moved
        
        Args:
            entity: The entity to update
        """
        if not hasattr(entity, 'position') or not hasattr(entity, 'spatial_cell'):
            return
        
        # Calculate new cell
        cell_x = int(entity.position.x / self.cell_size)
        cell_y = int(entity.position.y / self.cell_size)
        new_cell_key = (cell_x, cell_y)
        
        # If cell changed, update
        if new_cell_key != entity.spatial_cell:
            # Remove from old cell
            old_cell_key = entity.spatial_cell
            if old_cell_key in self.spatial_grid and entity in self.spatial_grid[old_cell_key]:
                self.spatial_grid[old_cell_key].remove(entity)
            
            # Add to new cell
            if new_cell_key not in self.spatial_grid:
                self.spatial_grid[new_cell_key] = []
            
            self.spatial_grid[new_cell_key].append(entity)
            entity.spatial_cell = new_cell_key
    
    def remove_entity(self, entity):
        """
        Remove an entity from the world
        
        Args:
            entity: The entity to remove
        """
        # Get entity ID if it's a NodePath
        entity_id = None
        if hasattr(entity, 'getPythonTag') and entity.getPythonTag("entity_id"):
            entity_id = entity.getPythonTag("entity_id")
            
        # Remove from entity lists
        if entity in self.players:
            self.players.remove(entity)
        if entity in self.enemies:
            self.enemies.remove(entity)
            # Also remove from subservient list if present
            if entity in self.subservient_enemies:
                self.subservient_enemies.remove(entity)
        if entity in self.projectiles:
            self.projectiles.remove(entity)
        if entity in self.resource_nodes:
            self.resource_nodes.remove(entity)
        if entity in self.resource_drops:
            self.resource_drops.remove(entity)
        if entity in self.interactables:
            self.interactables.remove(entity)
        if entity in self.buildings:
            self.buildings.remove(entity)
            
        # Remove from entities dictionary if we have the ID
        if entity_id and entity_id in self.entities:
            del self.entities[entity_id]
        
        # Remove from spatial grid
        self.remove_from_spatial_grid(entity)
        
        # If entity is a NodePath, remove it from the scene graph
        if hasattr(entity, 'removeNode'):
            entity.removeNode()
    
    def clear_all_entities(self):
        """Remove all entities except the player"""
        # Save player entities
        players = list(self.players)
        
        # Clear all entity lists
        for entity in self.entities.values():
            if entity not in players:
                # Clean up the entity
                if hasattr(entity, 'root') and entity.root:
                    entity.root.removeNode()
        
        # Reset lists
        self.entities = {}
        self.enemies = []
        self.projectiles = []
        self.resources = []
        self.resource_nodes = []
        self.resource_drops = []
        self.interactables = []
        self.buildings = []
        self.subservient_enemies = []
        
        # Reset spatial grid
        self.spatial_grid = {}
        
        # Re-add players to spatial grid
        for player in players:
            self.add_to_spatial_grid(player)
    
    def remove_enemy(self, enemy):
        """
        Remove an enemy from all entity lists
        
        Args:
            enemy: The enemy to remove
        """
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        
        if enemy in self.entities:
            del self.entities[enemy]
        
        # Increment kill counter
        self.enemies_killed += 1
    
    def add_resource_collection(self, resource_type, amount):
        """
        Track resource collection
        
        Args:
            resource_type (str): Type of resource collected
            amount (int): Amount collected
        """
        if resource_type in self.resources_collected:
            self.resources_collected[resource_type] += amount
    
    def get_debug_info(self):
        """Get debug information about entity counts"""
        return {
            "enemy_count": len(self.enemies),
            "projectile_count": len(self.projectiles),
            "resource_node_count": len(self.resource_nodes),
            "resource_drop_count": len(self.resource_drops),
            "enemies_killed": self.enemies_killed,
            "resources_collected": self.resources_collected,
            "subservient_count": len(self.subservient_enemies)
        } 