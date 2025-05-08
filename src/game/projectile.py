#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Projectile system for Nightfall Defenders
Implements different trajectory types for abilities
"""

import math
from panda3d.core import Vec3, Point3, LineSegs, NodePath

class Projectile:
    """Class for ability projectiles with different trajectory types"""
    
    def __init__(self, game, position, direction, speed, damage, range, owner=None, ability=None,
                 arc_height=0.0, gravity=0.0, homing=False, turn_rate=0.0, pierce=0, chain=0, 
                 chain_range=5.0, chain_targets=None, aoe_radius=0.0):
        """
        Initialize a projectile
        
        Args:
            game: Game instance
            position: Starting position (Vec3)
            direction: Direction vector (normalized Vec3)
            speed: Movement speed
            damage: Base damage
            range: Maximum travel distance
            owner: Entity that created this projectile
            ability: Ability that created this projectile
            arc_height: Height of arc for arcing trajectories
            gravity: Gravity strength for arcing trajectories
            homing: Whether this projectile homes in on targets
            turn_rate: Turn rate for homing projectiles
            pierce: Number of targets to pierce
            chain: Number of times to chain to new targets
            chain_range: Range to look for chain targets
            chain_targets: List of entities already hit (for chaining)
            aoe_radius: Explosion radius on impact
        """
        self.game = game
        self.position = Vec3(position)
        self.direction = Vec3(direction)
        self.initial_position = Vec3(position)
        self.speed = speed
        self.damage = damage
        self.range = range
        self.owner = owner
        self.ability = ability
        
        # Specialized trajectory parameters
        self.trajectory_type = "straight"  # Default
        self.arc_height = arc_height
        self.gravity = gravity
        self.homing = homing
        self.turn_rate = turn_rate
        self.pierce = pierce
        self.chain = chain
        self.chain_range = chain_range
        self.chain_targets = chain_targets or []
        self.aoe_radius = aoe_radius
        
        # Used for some trajectories
        self.target = None
        self.target_position = None
        self.time_alive = 0.0
        self.distance_traveled = 0.0
        self.hit_entities = []
        
        # Visual representation
        self.visual_node = None
        self.trail_effect = None
        self.create_visual_representation()
    
    def update(self, dt):
        """
        Update projectile position and effects
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            bool: True if the projectile should continue to exist
        """
        # Update time alive
        self.time_alive += dt
        
        # Store previous position for distance calculation
        prev_position = Vec3(self.position)
        
        # Update position based on trajectory type
        if self.trajectory_type == "straight":
            self._update_straight(dt)
        elif self.trajectory_type == "arcing":
            self._update_arcing(dt)
        elif self.trajectory_type == "homing":
            self._update_homing(dt)
        elif self.trajectory_type == "spiral":
            self._update_spiral(dt)
        elif self.trajectory_type == "wave":
            self._update_wave(dt)
        elif self.trajectory_type == "zigzag":
            self._update_zigzag(dt)
        else:
            # Default to straight
            self._update_straight(dt)
        
        # Update visual representation
        self._update_visual()
        
        # Update distance traveled
        self.distance_traveled += (self.position - prev_position).length()
        
        # Check for collisions
        self._check_collisions()
        
        # Check for max range
        if self.distance_traveled >= self.range:
            self._on_max_range()
            return False
        
        return True
    
    def _update_straight(self, dt):
        """Update for straight trajectory"""
        self.position += self.direction * self.speed * dt
    
    def _update_arcing(self, dt):
        """Update for arcing trajectory"""
        # Calculate horizontal position based on initial direction and speed
        self.position += self.direction * self.speed * dt
        
        # Calculate vertical position based on parabolic arc
        # For a simple arc, we can use a parabola: h(t) = h_max * (1 - (2t-1)^2)
        # where t is normalized time from 0 to 1 over the arc
        
        # First, estimate time to target based on distance and speed
        total_distance = self.range
        total_time = total_distance / self.speed
        
        # Normalized time (0 to 1)
        normalized_time = min(1.0, self.time_alive / total_time)
        
        # Calculate height using parabolic formula
        height_factor = 1.0 - (2.0 * normalized_time - 1.0) ** 2
        arc_height = self.arc_height * height_factor
        
        # Apply gravity if specified
        if self.gravity > 0:
            arc_height -= 0.5 * self.gravity * self.time_alive ** 2
        
        # Set z position (height)
        self.position.z = self.initial_position.z + arc_height
    
    def _update_homing(self, dt):
        """Update for homing trajectory"""
        if self.target is None or not hasattr(self.target, 'position'):
            # If no target, move straight
            self._update_straight(dt)
            return
        
        # Calculate direction to target
        to_target = self.target.position - self.position
        distance = to_target.length()
        
        if distance < 0.1:
            # We've reached the target
            self._update_straight(dt)
            return
        
        # Normalize direction to target
        to_target.normalize()
        
        # Interpolate between current direction and direction to target
        # based on turn rate
        turn_amount = min(1.0, self.turn_rate * dt)
        new_direction = self.direction * (1.0 - turn_amount) + to_target * turn_amount
        new_direction.normalize()
        
        # Update direction
        self.direction = new_direction
        
        # Move in the new direction
        self._update_straight(dt)
    
    def _update_spiral(self, dt):
        """Update for spiral trajectory"""
        # Spiral around the original direction
        spiral_radius = 0.5
        spiral_frequency = 5.0
        
        # Calculate spiral offsets
        spiral_angle = self.time_alive * spiral_frequency
        
        # We need two perpendicular vectors to the direction vector
        # to define the spiral plane
        up_vector = Vec3(0, 0, 1)
        right_vector = self.direction.cross(up_vector)
        right_vector.normalize()
        up_vector = right_vector.cross(self.direction)
        up_vector.normalize()
        
        # Calculate spiral offset
        x_offset = math.cos(spiral_angle) * spiral_radius
        y_offset = math.sin(spiral_angle) * spiral_radius
        
        # Apply spiral offset
        offset = right_vector * x_offset + up_vector * y_offset
        
        # Move forward along the main direction, plus the spiral offset
        self.position += self.direction * self.speed * dt + offset * dt
    
    def _update_wave(self, dt):
        """Update for wave trajectory"""
        wave_amplitude = 0.5
        wave_frequency = 10.0
        
        # Calculate wave offset
        distance_traveled = self.speed * self.time_alive
        wave_offset = math.sin(distance_traveled * wave_frequency) * wave_amplitude
        
        # We need a perpendicular vector to the direction for the wave
        up_vector = Vec3(0, 0, 1)
        right_vector = self.direction.cross(up_vector)
        right_vector.normalize()
        
        # Move forward along the main direction, plus the wave offset
        self.position += self.direction * self.speed * dt + right_vector * wave_offset * dt
    
    def _update_zigzag(self, dt):
        """Update for zigzag trajectory"""
        zigzag_width = 1.0
        zigzag_frequency = 2.0
        
        # Calculate zigzag offset
        zigzag_period = 1.0 / zigzag_frequency
        zigzag_phase = (self.time_alive % zigzag_period) / zigzag_period
        
        # Determine the zigzag direction (+1 or -1)
        zigzag_dir = 1 if zigzag_phase < 0.5 else -1
        
        # We need a perpendicular vector to the direction for the zigzag
        up_vector = Vec3(0, 0, 1)
        right_vector = self.direction.cross(up_vector)
        right_vector.normalize()
        
        # Move forward along the main direction, plus zigzag offset
        forward_distance = self.speed * dt
        self.position += self.direction * forward_distance + right_vector * zigzag_dir * zigzag_width * dt
    
    def _check_collisions(self):
        """Check for collisions with entities"""
        # This would be called by the physics system in a real implementation
        # Here we'll just simulate it for testing
        
        # Get nearby entities
        entities = self._get_nearby_entities()
        
        for entity in entities:
            # Skip owner
            if entity == self.owner:
                continue
                
            # Skip already hit entities if not piercing
            if entity in self.hit_entities and self.pierce <= 0:
                continue
                
            # Check distance
            distance = (entity.position - self.position).length()
            collision_radius = getattr(entity, 'collision_radius', 0.5)
            
            if distance <= collision_radius:
                # Collision detected
                self._on_hit_entity(entity)
                
                # Count hit
                self.hit_entities.append(entity)
                
                # Check pierce
                if self.pierce > 0:
                    self.pierce -= 1
                else:
                    # If chaining, create a new projectile targeting a nearby entity
                    if self.chain > 0:
                        self._chain_to_new_target(entity)
                    
                    # Destroy projectile if not piercing
                    if not self.chain:
                        return False
    
    def _on_hit_entity(self, entity):
        """Handle collision with an entity"""
        # Apply damage
        if hasattr(entity, 'take_damage'):
            entity.take_damage(self.damage, source=self.owner)
        
        # Apply ability effects
        if self.ability:
            for effect in getattr(self.ability, 'effects', []):
                self._apply_effect(entity, effect)
        
        # Explosion if AoE
        if self.aoe_radius > 0:
            self._create_explosion()
    
    def _on_max_range(self):
        """Handle reaching maximum range"""
        # Explosion if AoE
        if self.aoe_radius > 0:
            self._create_explosion()
    
    def _create_explosion(self):
        """Create an explosion effect"""
        # Get nearby entities within explosion radius
        nearby_entities = self._get_nearby_entities(self.aoe_radius)
        
        for entity in nearby_entities:
            # Skip owner
            if entity == self.owner:
                continue
                
            # Calculate damage based on distance
            distance = (entity.position - self.position).length()
            if distance <= self.aoe_radius:
                # Apply falloff based on distance
                falloff = 1.0 - (distance / self.aoe_radius)
                damage = int(self.damage * falloff)
                
                # Apply damage
                if hasattr(entity, 'take_damage'):
                    entity.take_damage(damage, source=self.owner)
    
    def _chain_to_new_target(self, hit_entity):
        """Chain to a new target after hitting an entity"""
        # Find a new target
        new_target = self._find_chain_target(hit_entity)
        
        if new_target:
            # Create a new projectile
            chain_projectile = Projectile(
                game=self.game,
                position=self.position,
                direction=(new_target.position - self.position).normalized(),
                speed=self.speed,
                damage=self.damage * 0.8,  # Reduced damage for chain targets
                range=self.chain_range,
                owner=self.owner,
                ability=self.ability,
                homing=True,  # Chain projectiles always home in
                turn_rate=0.5,
                chain=self.chain - 1,
                chain_targets=self.hit_entities + [hit_entity],
                aoe_radius=self.aoe_radius
            )
            
            chain_projectile.target = new_target
            chain_projectile.trajectory_type = "homing"
            
            # Add to game
            self.game.entity_manager.add_entity(chain_projectile)
    
    def _find_chain_target(self, hit_entity):
        """Find a suitable chain target"""
        # Get nearby entities
        nearby_entities = self._get_nearby_entities(self.chain_range)
        
        # Filter out invalid targets
        valid_targets = []
        for entity in nearby_entities:
            # Skip owner, hit entity, and already hit entities
            if (entity == self.owner or 
                entity == hit_entity or 
                entity in self.hit_entities or 
                entity in self.chain_targets):
                continue
            
            valid_targets.append(entity)
        
        # Return closest valid target
        if valid_targets:
            return min(valid_targets, key=lambda e: (e.position - self.position).length())
        
        return None
    
    def _get_nearby_entities(self, radius=None):
        """Get entities near the projectile"""
        if radius is None:
            radius = 1.0  # Default collision radius
        
        # In a real implementation, this would use a spatial query
        # For testing, we'll just return all entities
        entities = []
        
        if hasattr(self.game, 'entity_manager') and hasattr(self.game.entity_manager, 'get_entities'):
            entities = self.game.entity_manager.get_entities()
        
        # Filter by distance
        nearby = []
        for entity in entities:
            distance = (entity.position - self.position).length()
            if distance <= radius:
                nearby.append(entity)
        
        return nearby
    
    def _apply_effect(self, entity, effect):
        """Apply a status effect to an entity"""
        if hasattr(entity, 'add_effect'):
            entity.add_effect(effect)
    
    def create_visual_representation(self):
        """Create visual representation of the projectile"""
        if not hasattr(self.game, 'render'):
            return
            
        # Create a visual node
        from panda3d.core import NodePath, PandaNode
        self.visual_node = NodePath(PandaNode("projectile"))
        self.visual_node.reparentTo(self.game.render)
        
        # Create a basic shape
        ls = LineSegs()
        ls.setColor(1, 0.5, 0, 1)  # Orange color
        ls.moveTo(0, 0, 0)
        ls.drawTo(0, 0.5, 0)
        
        projectile_shape = ls.create()
        shape_node = NodePath(projectile_shape)
        shape_node.reparentTo(self.visual_node)
        
        # Create a trail effect for some trajectories
        if self.trajectory_type in ["arcing", "spiral", "wave", "zigzag"]:
            self.trail_effect = LineSegs()
            self.trail_effect.setColor(1, 0.5, 0, 0.5)  # Transparent orange
            self.trail_effect.setThickness(2)
            
            # Initial point
            self.trail_effect.moveTo(self.position)
            
            # Create the trail node
            trail_node = self.trail_effect.create()
            self.trail_node_path = NodePath(trail_node)
            self.trail_node_path.reparentTo(self.game.render)
    
    def _update_visual(self):
        """Update the visual representation"""
        if self.visual_node:
            self.visual_node.setPos(self.position)
            self.visual_node.lookAt(self.position + self.direction)
        
        # Update trail
        if hasattr(self, 'trail_effect') and self.trail_effect:
            self.trail_effect.drawTo(self.position)
            
            # Update the trail node
            if hasattr(self, 'trail_node_path'):
                self.trail_node_path.removeNode()
                
            trail_node = self.trail_effect.create()
            self.trail_node_path = NodePath(trail_node)
            self.trail_node_path.reparentTo(self.game.render)
    
    def destroy(self):
        """Clean up projectile"""
        if self.visual_node:
            self.visual_node.removeNode()
        
        if hasattr(self, 'trail_node_path'):
            self.trail_node_path.removeNode()

class StraightProjectile(Projectile):
    """A projectile that travels in a straight line"""
    
    def __init__(self, game, position, direction, owner=None, damage=10, speed=20.0, range=50.0):
        """
        Initialize a straight projectile
        
        Args:
            game: Game instance
            position: Starting position (Vec3)
            direction: Direction vector (normalized Vec3)
            owner: Entity that created this projectile
            damage: Base damage
            speed: Movement speed
            range: Maximum travel distance
        """
        super().__init__(game, position, direction, speed, damage, range, owner)
        self.trajectory_type = "straight"
        
        # Override visual representation for straight projectiles
        self.create_visual_representation()


class ArcingProjectile(Projectile):
    """A projectile that follows an arc trajectory"""
    
    def __init__(self, game, position, direction, owner=None, damage=15, speed=15.0, range=40.0, 
                 arc_height=3.0, gravity=9.8):
        """
        Initialize an arcing projectile
        
        Args:
            game: Game instance
            position: Starting position (Vec3)
            direction: Direction vector (normalized Vec3)
            owner: Entity that created this projectile
            damage: Base damage
            speed: Movement speed
            range: Maximum travel distance
            arc_height: Maximum height of the arc
            gravity: Gravitational force to apply
        """
        super().__init__(game, position, direction, speed, damage, range, owner, 
                         arc_height=arc_height, gravity=gravity)
        self.trajectory_type = "arcing"
        
        # Override visual representation for arcing projectiles
        self.create_visual_representation()


class HomingProjectile(Projectile):
    """A projectile that homes in on a target"""
    
    def __init__(self, game, position, direction, owner=None, target=None, damage=12, 
                 speed=12.0, range=60.0, turn_rate=2.0):
        """
        Initialize a homing projectile
        
        Args:
            game: Game instance
            position: Starting position (Vec3)
            direction: Direction vector (normalized Vec3)
            owner: Entity that created this projectile
            target: Target entity to home in on
            damage: Base damage
            speed: Movement speed
            range: Maximum travel distance
            turn_rate: How quickly the projectile can change direction
        """
        super().__init__(game, position, direction, speed, damage, range, owner, 
                         homing=True, turn_rate=turn_rate)
        self.trajectory_type = "homing"
        self.target = target
        
        # Override visual representation for homing projectiles
        self.create_visual_representation()
        
    def create_visual_representation(self):
        """Create visual representation for homing projectile"""
        super().create_visual_representation()
        # Add a subtle glow/trail effect for homing projectiles
        if self.visual_node:
            # Add a custom visual effect here
            pass


class SpiralProjectile(Projectile):
    """A projectile that follows a spiral trajectory"""
    
    def __init__(self, game, position, direction, owner=None, damage=8, speed=15.0, 
                 range=35.0, spiral_radius=0.5, spiral_frequency=5.0):
        """
        Initialize a spiral projectile
        
        Args:
            game: Game instance
            position: Starting position (Vec3)
            direction: Direction vector (normalized Vec3)
            owner: Entity that created this projectile
            damage: Base damage
            speed: Movement speed
            range: Maximum travel distance
            spiral_radius: Radius of the spiral
            spiral_frequency: How quickly the projectile spirals
        """
        super().__init__(game, position, direction, speed, damage, range, owner)
        self.trajectory_type = "spiral"
        self.spiral_radius = spiral_radius
        self.spiral_frequency = spiral_frequency
        
        # Override visual representation for spiral projectiles
        self.create_visual_representation()
    
    def create_visual_representation(self):
        """Create visual representation for spiral projectile"""
        super().create_visual_representation()
        # Add a custom spiral trail
        if self.visual_node:
            # Add a custom visual effect here
            pass
