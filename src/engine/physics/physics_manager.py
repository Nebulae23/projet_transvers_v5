#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Physics Manager for Nightfall Defenders
Integrates all physics systems with spatial partitioning for optimization
"""

import math
from typing import List, Dict, Tuple, Set, Optional
from panda3d.core import Vec3, Point3, NodePath, CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay, CollisionSphere

from src.engine.physics.verlet import VerletSystem, VerletPoint
from src.engine.physics.cloth_system import ClothSystem

# Size of spatial grid cells for partitioning
GRID_CELL_SIZE = 10.0

class SpatialCell:
    """A cell in the spatial partitioning grid"""
    
    def __init__(self, x: int, y: int, z: int):
        """
        Initialize a spatial cell
        
        Args:
            x: X grid position
            y: Y grid position
            z: Z grid position
        """
        self.x = x
        self.y = y
        self.z = z
        self.entities = set()  # Entities in this cell
    
    def get_key(self) -> Tuple[int, int, int]:
        """
        Get a unique key for this cell
        
        Returns:
            Tuple of (x, y, z) coordinates
        """
        return (self.x, self.y, self.z)


class SpatialGrid:
    """Spatial partitioning grid for physics optimization"""
    
    def __init__(self, cell_size: float = GRID_CELL_SIZE):
        """
        Initialize the spatial grid
        
        Args:
            cell_size: Size of each cell in world units
        """
        self.cell_size = cell_size
        self.cells = {}  # Map from (x,y,z) tuple to SpatialCell
        self.entity_cells = {}  # Map from entity ID to list of cells it occupies
    
    def position_to_cell_coords(self, position: Vec3) -> Tuple[int, int, int]:
        """
        Convert a world position to cell coordinates
        
        Args:
            position: World position
            
        Returns:
            Tuple of (x, y, z) cell coordinates
        """
        x = int(math.floor(position.x / self.cell_size))
        y = int(math.floor(position.y / self.cell_size))
        z = int(math.floor(position.z / self.cell_size))
        return (x, y, z)
    
    def get_or_create_cell(self, x: int, y: int, z: int) -> SpatialCell:
        """
        Get a cell, creating it if it doesn't exist
        
        Args:
            x: X cell coordinate
            y: Y cell coordinate
            z: Z cell coordinate
            
        Returns:
            SpatialCell at the specified coordinates
        """
        key = (x, y, z)
        if key not in self.cells:
            self.cells[key] = SpatialCell(x, y, z)
        return self.cells[key]
    
    def add_entity(self, entity_id: str, position: Vec3, radius: float = 1.0):
        """
        Add an entity to the spatial grid
        
        Args:
            entity_id: Unique entity ID
            position: Entity position
            radius: Entity radius for determining cell occupancy
        """
        # Calculate which cells this entity occupies
        min_cell = self.position_to_cell_coords(position - Vec3(radius, radius, radius))
        max_cell = self.position_to_cell_coords(position + Vec3(radius, radius, radius))
        
        # Add entity to all overlapping cells
        occupied_cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    cell = self.get_or_create_cell(x, y, z)
                    cell.entities.add(entity_id)
                    occupied_cells.append(cell.get_key())
        
        # Store which cells this entity occupies
        self.entity_cells[entity_id] = occupied_cells
    
    def update_entity(self, entity_id: str, position: Vec3, radius: float = 1.0):
        """
        Update an entity's position in the grid
        
        Args:
            entity_id: Unique entity ID
            position: New entity position
            radius: Entity radius for determining cell occupancy
        """
        # Remove from old cells first
        self.remove_entity(entity_id)
        
        # Add to new cells
        self.add_entity(entity_id, position, radius)
    
    def remove_entity(self, entity_id: str):
        """
        Remove an entity from the grid
        
        Args:
            entity_id: Unique entity ID
        """
        if entity_id in self.entity_cells:
            # Remove from all occupied cells
            for cell_key in self.entity_cells[entity_id]:
                if cell_key in self.cells:
                    self.cells[cell_key].entities.discard(entity_id)
                    
                    # Clean up empty cells
                    if not self.cells[cell_key].entities:
                        del self.cells[cell_key]
            
            # Remove entity from tracking
            del self.entity_cells[entity_id]
    
    def get_nearby_entities(self, position: Vec3, radius: float = GRID_CELL_SIZE) -> Set[str]:
        """
        Get entities near a position
        
        Args:
            position: Center position
            radius: Search radius
            
        Returns:
            Set of entity IDs near the position
        """
        min_cell = self.position_to_cell_coords(position - Vec3(radius, radius, radius))
        max_cell = self.position_to_cell_coords(position + Vec3(radius, radius, radius))
        
        nearby_entities = set()
        
        # Check all cells in the range
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    key = (x, y, z)
                    if key in self.cells:
                        nearby_entities.update(self.cells[key].entities)
        
        return nearby_entities
    
    def get_potential_collisions(self, entity_id: str) -> Set[str]:
        """
        Get potential collision entities for an entity
        
        Args:
            entity_id: Entity ID to check
            
        Returns:
            Set of entity IDs that might collide with this entity
        """
        potential_collisions = set()
        
        # Check all cells this entity occupies
        if entity_id in self.entity_cells:
            for cell_key in self.entity_cells[entity_id]:
                if cell_key in self.cells:
                    # Add all entities in this cell except self
                    for other_id in self.cells[cell_key].entities:
                        if other_id != entity_id:
                            potential_collisions.add(other_id)
        
        return potential_collisions
    
    def clear(self):
        """Clear all entities from the grid"""
        self.cells.clear()
        self.entity_cells.clear()


class PhysicsManager:
    """Manages all physics systems in the game"""
    
    def __init__(self, game):
        """
        Initialize the physics manager
        
        Args:
            game: Main game instance
        """
        self.game = game
        
        # Verlet physics system for character animation
        self.verlet_system = VerletSystem()
        
        # Cloth system for fabric physics
        self.cloth_system = ClothSystem(self.verlet_system)
        
        # Spatial partitioning
        self.spatial_grid = SpatialGrid()
        
        # Collision system
        self.setup_collision_system()
        
        # Physics entities (dynamic objects with physics)
        self.physics_entities = {}
        
        # Static collision objects (terrain, buildings)
        self.static_collision_objects = {}
        
        # Physics configuration
        self.gravity = Vec3(0, 0, -9.8)  # Default gravity
        self.verlet_system.set_gravity(self.gravity)
        
        # Timestep configuration for stable physics
        self.fixed_timestep = 1.0 / 60.0  # Physics runs at 60 Hz
        self.time_accumulator = 0.0
        self.max_steps_per_frame = 3  # Limit physics steps per frame
        
        # Debug visualization
        self.debug_node = None
        self.show_debug = False
    
    def setup_collision_system(self):
        """Set up the collision detection system"""
        # Create collision traverser
        self.collision_traverser = CollisionTraverser("physics_traverser")
        
        # Collision handler for physics queries
        self.collision_handler = CollisionHandlerQueue()
    
    def register_physics_entity(self, entity_id: str, position: Vec3, radius: float, mass: float = 1.0):
        """
        Register an entity with the physics system
        
        Args:
            entity_id: Unique entity ID
            position: Initial position
            radius: Collision radius
            mass: Entity mass
        """
        self.physics_entities[entity_id] = {
            "position": Vec3(position),
            "velocity": Vec3(0, 0, 0),
            "acceleration": Vec3(0, 0, 0),
            "radius": radius,
            "mass": mass,
            "forces": [],  # List of forces acting on this entity
            "verlet_rig": None  # Optional Verlet rig for animation
        }
        
        # Add to spatial grid
        self.spatial_grid.add_entity(entity_id, position, radius)
    
    def register_static_object(self, object_id: str, position: Vec3, size: Vec3):
        """
        Register a static collision object
        
        Args:
            object_id: Unique object ID
            position: Object position
            size: Object size (x, y, z dimensions)
        """
        self.static_collision_objects[object_id] = {
            "position": Vec3(position),
            "size": Vec3(size),
            "collision_node": None  # Will be created as needed
        }
    
    def create_character_rig(self, entity_id: str, height: float = 2.0) -> Dict[str, VerletPoint]:
        """
        Create a Verlet character rig for an entity
        
        Args:
            entity_id: Entity ID to create rig for
            height: Character height
            
        Returns:
            Dictionary mapping joint names to VerletPoints
        """
        if entity_id not in self.physics_entities:
            print(f"Warning: Cannot create rig for unknown entity {entity_id}")
            return None
            
        entity = self.physics_entities[entity_id]
        position = entity["position"]
        
        # Create the rig
        joints = self.verlet_system.create_character_rig(position, height)
        
        # Store rig with entity
        entity["verlet_rig"] = joints
        
        return joints
    
    def create_cloth(self, position: Vec3, width: float, height: float, render_node: NodePath = None,
                    texture_path: str = None, cloth_type: str = "flag") -> Dict:
        """
        Create a cloth object
        
        Args:
            position: Cloth position
            width: Cloth width
            height: Cloth height
            render_node: Node to attach visuals to
            texture_path: Optional texture path
            cloth_type: Type of cloth ("flag", "cape", "banner")
            
        Returns:
            Cloth data dictionary
        """
        if cloth_type == "flag":
            return self.cloth_system.create_flag(position, width, height, 0.1, render_node, texture_path)
        elif cloth_type == "cape":
            return self.cloth_system.create_cape(position, width, height, 0.3, render_node, texture_path)
        else:
            # Default grid cloth
            return self.cloth_system.create_cloth_grid(position, width, height, 10, 10, True, 0.8, 1.0)
    
    def apply_force(self, entity_id: str, force: Vec3, duration: float = 0.0):
        """
        Apply a force to an entity
        
        Args:
            entity_id: Entity ID
            force: Force vector
            duration: Force duration in seconds (0 = instant impulse)
        """
        if entity_id not in self.physics_entities:
            return
            
        entity = self.physics_entities[entity_id]
        
        if duration <= 0:
            # Instant impulse (changes velocity directly)
            impulse = force / entity["mass"]
            entity["velocity"] += impulse
        else:
            # Sustained force
            entity["forces"].append({
                "force": Vec3(force),
                "duration": duration,
                "remaining": duration
            })
            
        # If entity has a Verlet rig, apply force to its root
        if entity["verlet_rig"] and "root" in entity["verlet_rig"]:
            root_point = entity["verlet_rig"]["root"]
            root_point.apply_force(force)
    
    def set_wind(self, direction: Vec3, strength: float, turbulence: float = 0.3):
        """
        Set wind parameters for cloth simulation
        
        Args:
            direction: Wind direction
            strength: Wind strength
            turbulence: Wind turbulence factor
        """
        self.cloth_system.set_wind(direction, strength, turbulence)
    
    def update(self, dt: float):
        """
        Update all physics systems
        
        Args:
            dt: Delta time in seconds
        """
        # Accumulate time for fixed timestep physics
        self.time_accumulator += dt
        
        # Limit number of physics steps per frame
        steps = 0
        
        # Run physics with fixed timestep for stability
        while self.time_accumulator >= self.fixed_timestep and steps < self.max_steps_per_frame:
            self._fixed_update(self.fixed_timestep)
            self.time_accumulator -= self.fixed_timestep
            steps += 1
        
        # If we hit the step limit, consume the remaining time
        if self.time_accumulator > self.fixed_timestep and steps >= self.max_steps_per_frame:
            self._fixed_update(self.time_accumulator)
            self.time_accumulator = 0
        
        # Update debug visualization if enabled
        if self.show_debug:
            self.update_debug_visualization()
    
    def _fixed_update(self, dt: float):
        """
        Fixed timestep physics update
        
        Args:
            dt: Fixed delta time
        """
        # Update all physics entities
        self._update_entities(dt)
        
        # Update Verlet physics (character animation and cloth)
        self.verlet_system.update(dt)
        
        # Update cloth physics
        self.cloth_system.update(dt)
        
        # Handle collisions between entities
        self._handle_entity_collisions()
        
        # Handle collisions with static objects
        self._handle_static_collisions()
    
    def _update_entities(self, dt: float):
        """
        Update all physics entities
        
        Args:
            dt: Delta time
        """
        for entity_id, entity in self.physics_entities.items():
            # Reset acceleration
            entity["acceleration"] = Vec3(0, 0, 0)
            
            # Apply gravity
            entity["acceleration"] += self.gravity
            
            # Process sustained forces
            remaining_forces = []
            for force_data in entity["forces"]:
                # Apply force
                entity["acceleration"] += force_data["force"] / entity["mass"]
                
                # Update remaining time
                force_data["remaining"] -= dt
                
                # Keep if still active
                if force_data["remaining"] > 0:
                    remaining_forces.append(force_data)
            
            # Replace forces list with remaining forces
            entity["forces"] = remaining_forces
            
            # Update velocity
            entity["velocity"] += entity["acceleration"] * dt
            
            # Apply damping to prevent excessive velocities
            damping = 0.99
            entity["velocity"] *= damping
            
            # Update position
            new_position = entity["position"] + entity["velocity"] * dt
            entity["position"] = new_position
            
            # Update spatial grid position
            self.spatial_grid.update_entity(entity_id, new_position, entity["radius"])
            
            # If entity has a Verlet rig, update the root position
            if entity["verlet_rig"] and "root" in entity["verlet_rig"]:
                root = entity["verlet_rig"]["root"]
                root.set_position(new_position)
    
    def _handle_entity_collisions(self):
        """Handle collisions between dynamic entities"""
        # Use spatial grid to find potential collisions
        checked_pairs = set()
        
        for entity_id, entity in self.physics_entities.items():
            # Get potential collision entities
            potential_collisions = self.spatial_grid.get_potential_collisions(entity_id)
            
            for other_id in potential_collisions:
                # Form a unique pair ID (using min/max ensures we check each pair only once)
                pair_id = (min(entity_id, other_id), max(entity_id, other_id))
                
                # Skip if this pair has already been checked
                if pair_id in checked_pairs:
                    continue
                    
                checked_pairs.add(pair_id)
                
                # Get the other entity
                if other_id not in self.physics_entities:
                    continue
                    
                other = self.physics_entities[other_id]
                
                # Check collision
                delta = entity["position"] - other["position"]
                distance = delta.length()
                min_distance = entity["radius"] + other["radius"]
                
                if distance < min_distance:
                    # Collision detected - calculate resolution
                    overlap = min_distance - distance
                    
                    # Direction to push entities apart
                    direction = delta.normalized() if distance > 0.001 else Vec3(1, 0, 0)
                    
                    # Calculate masses for response
                    total_mass = entity["mass"] + other["mass"]
                    entity_ratio = other["mass"] / total_mass
                    other_ratio = entity["mass"] / total_mass
                    
                    # Move entities apart based on mass ratio
                    entity["position"] += direction * overlap * entity_ratio
                    other["position"] -= direction * overlap * other_ratio
                    
                    # Calculate impulse for bounce
                    relative_velocity = entity["velocity"] - other["velocity"]
                    velocity_along_normal = relative_velocity.dot(direction)
                    
                    # Only apply impulse if objects are moving toward each other
                    if velocity_along_normal < 0:
                        # Coefficient of restitution (bounciness)
                        restitution = 0.3
                        
                        # Calculate impulse scalar
                        impulse_scalar = -(1 + restitution) * velocity_along_normal
                        impulse_scalar /= total_mass
                        
                        # Apply impulse
                        impulse = direction * impulse_scalar
                        entity["velocity"] += impulse * other["mass"]
                        other["velocity"] -= impulse * entity["mass"]
    
    def _handle_static_collisions(self):
        """Handle collisions with static objects"""
        for entity_id, entity in self.physics_entities.items():
            for object_id, static_obj in self.static_collision_objects.items():
                # Simple box collision check
                min_pos = static_obj["position"] - static_obj["size"] * 0.5
                max_pos = static_obj["position"] + static_obj["size"] * 0.5
                
                # Find closest point on box to entity
                closest_x = max(min_pos.x, min(entity["position"].x, max_pos.x))
                closest_y = max(min_pos.y, min(entity["position"].y, max_pos.y))
                closest_z = max(min_pos.z, min(entity["position"].z, max_pos.z))
                
                closest_point = Vec3(closest_x, closest_y, closest_z)
                
                # Check if entity collides with this point
                delta = entity["position"] - closest_point
                distance = delta.length()
                
                if distance < entity["radius"]:
                    # Collision detected
                    overlap = entity["radius"] - distance
                    
                    # Direction to push entity
                    if distance > 0.001:
                        direction = delta / distance
                    else:
                        # If entity is exactly at closest point, use a default direction
                        direction = Vec3(0, 0, 1)
                    
                    # Move entity out of collision
                    entity["position"] += direction * overlap
                    
                    # Reflect velocity for bounce
                    dot_product = entity["velocity"].dot(direction)
                    if dot_product < 0:
                        # Entity is moving toward the surface
                        reflection = entity["velocity"] - direction * (2 * dot_product)
                        
                        # Apply friction
                        friction = 0.8
                        entity["velocity"] = reflection * friction
    
    def ray_cast(self, start: Vec3, direction: Vec3, max_distance: float = 100.0) -> Dict:
        """
        Cast a ray and return the first hit
        
        Args:
            start: Ray start position
            direction: Ray direction (will be normalized)
            max_distance: Maximum ray distance
            
        Returns:
            Dictionary with hit information or None if no hit
        """
        # Normalize direction
        if direction.length_squared() < 0.0001:
            return None
            
        direction.normalize()
        
        # Create a collision ray
        ray = CollisionRay(start, direction)
        ray_node = CollisionNode("physics_ray")
        ray_node.addSolid(ray)
        
        ray_np = self.game.render.attachNewNode(ray_node)
        self.collision_traverser.addCollider(ray_np, self.collision_handler)
        
        # Traverse the scene
        self.collision_traverser.traverse(self.game.render)
        
        # Check for hits
        num_entries = self.collision_handler.getNumEntries()
        if num_entries > 0:
            # Sort entries by distance
            self.collision_handler.sortEntries()
            
            # Get the closest hit
            entry = self.collision_handler.getEntry(0)
            hit_pos = entry.getSurfacePoint(self.game.render)
            hit_normal = entry.getSurfaceNormal(self.game.render)
            hit_distance = (hit_pos - start).length()
            
            # Clean up
            self.collision_traverser.removeCollider(ray_np)
            ray_np.removeNode()
            
            # Check if hit is within max distance
            if hit_distance <= max_distance:
                return {
                    "position": hit_pos,
                    "normal": hit_normal,
                    "distance": hit_distance,
                    "node": entry.getIntoNodePath()
                }
        
        # Clean up
        self.collision_traverser.removeCollider(ray_np)
        ray_np.removeNode()
        
        return None
    
    def enable_debug_visualization(self, render_node: NodePath):
        """
        Enable debug visualization
        
        Args:
            render_node: Node to attach visualization to
        """
        self.show_debug = True
        
        if self.debug_node is None:
            self.debug_node = render_node.attachNewNode("physics_debug")
            
        # Enable Verlet system debug visualization
        self.verlet_system.enable_debug_visualization(self.debug_node)
    
    def update_debug_visualization(self):
        """Update debug visualization"""
        if not self.debug_node:
            return
            
        # Clear previous visualization
        self.debug_node.removeNode()
        self.debug_node = self.game.render.attachNewNode("physics_debug")
        
        # Visualize physics entities
        from panda3d.core import LineSegs
        
        # Draw entity colliders
        lines = LineSegs()
        lines.setThickness(1.0)
        lines.setColor(0, 1, 0, 1)  # Green
        
        for entity_id, entity in self.physics_entities.items():
            # Draw a circle for each entity
            self._draw_sphere_wireframe(lines, entity["position"], entity["radius"], 8)
            
            # Draw velocity vector
            if entity["velocity"].length_squared() > 0.0001:
                lines.setColor(1, 1, 0, 1)  # Yellow for velocity
                lines.moveTo(entity["position"])
                lines.drawTo(entity["position"] + entity["velocity"])
                lines.setColor(0, 1, 0, 1)  # Back to green
        
        # Draw static objects
        lines.setColor(0, 0, 1, 1)  # Blue for static objects
        
        for object_id, static_obj in self.static_collision_objects.items():
            half_size = static_obj["size"] * 0.5
            pos = static_obj["position"]
            
            # Draw wireframe box
            self._draw_box_wireframe(lines, pos, half_size)
        
        # Create the lines node
        lines_node = lines.create()
        self.debug_node.attachNewNode(lines_node)
    
    def _draw_sphere_wireframe(self, lines: 'LineSegs', center: Vec3, radius: float, segments: int = 8):
        """
        Draw a wireframe sphere
        
        Args:
            lines: LineSegs to draw with
            center: Center position
            radius: Sphere radius
            segments: Number of segments per circle
        """
        # Draw three circles representing the sphere
        for axis in range(3):
            prev_point = None
            
            for i in range(segments + 1):
                angle = i * 2 * math.pi / segments
                
                if axis == 0:  # YZ plane
                    point = center + Vec3(0, 
                                         radius * math.cos(angle), 
                                         radius * math.sin(angle))
                elif axis == 1:  # XZ plane
                    point = center + Vec3(radius * math.cos(angle),
                                         0,
                                         radius * math.sin(angle))
                else:  # XY plane
                    point = center + Vec3(radius * math.cos(angle),
                                         radius * math.sin(angle),
                                         0)
                
                if prev_point:
                    lines.moveTo(prev_point)
                    lines.drawTo(point)
                
                prev_point = point
    
    def _draw_box_wireframe(self, lines: 'LineSegs', center: Vec3, half_size: Vec3):
        """
        Draw a wireframe box
        
        Args:
            lines: LineSegs to draw with
            center: Center position
            half_size: Half size in each dimension
        """
        # Define the 8 corners of the box
        corners = [
            center + Vec3(-half_size.x, -half_size.y, -half_size.z),
            center + Vec3(half_size.x, -half_size.y, -half_size.z),
            center + Vec3(half_size.x, half_size.y, -half_size.z),
            center + Vec3(-half_size.x, half_size.y, -half_size.z),
            center + Vec3(-half_size.x, -half_size.y, half_size.z),
            center + Vec3(half_size.x, -half_size.y, half_size.z),
            center + Vec3(half_size.x, half_size.y, half_size.z),
            center + Vec3(-half_size.x, half_size.y, half_size.z)
        ]
        
        # Bottom face
        lines.moveTo(corners[0])
        lines.drawTo(corners[1])
        lines.drawTo(corners[2])
        lines.drawTo(corners[3])
        lines.drawTo(corners[0])
        
        # Top face
        lines.moveTo(corners[4])
        lines.drawTo(corners[5])
        lines.drawTo(corners[6])
        lines.drawTo(corners[7])
        lines.drawTo(corners[4])
        
        # Connect bottom to top
        lines.moveTo(corners[0])
        lines.drawTo(corners[4])
        
        lines.moveTo(corners[1])
        lines.drawTo(corners[5])
        
        lines.moveTo(corners[2])
        lines.drawTo(corners[6])
        
        lines.moveTo(corners[3])
        lines.drawTo(corners[7])
    
    def clear(self):
        """Clear all physics objects"""
        self.physics_entities.clear()
        self.static_collision_objects.clear()
        self.spatial_grid.clear()
        
        # Reset Verlet system
        self.verlet_system = VerletSystem()
        self.verlet_system.set_gravity(self.gravity)
        
        # Reset cloth system
        self.cloth_system = ClothSystem(self.verlet_system) 