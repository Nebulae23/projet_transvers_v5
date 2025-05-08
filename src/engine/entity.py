#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entity System for Nightfall Defenders
Implements a component-based entity system
"""

import uuid
from typing import Dict, List, Type, TypeVar, Generic, Optional, Any

T = TypeVar('T')


class Component:
    """Base class for all entity components"""
    
    def __init__(self, entity=None):
        """
        Initialize the component
        
        Args:
            entity: The entity this component belongs to
        """
        self.entity = entity
    
    def update(self, dt: float):
        """
        Update the component
        
        Args:
            dt (float): Delta time since last update
        """
        pass
    
    def on_attach(self, entity):
        """
        Called when the component is attached to an entity
        
        Args:
            entity: The entity being attached to
        """
        self.entity = entity
    
    def on_detach(self):
        """Called when the component is detached from an entity"""
        self.entity = None


class TransformComponent(Component):
    """Component for entity position, rotation, and scale"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, 
                 h: float = 0.0, p: float = 0.0, r: float = 0.0,
                 scale_x: float = 1.0, scale_y: float = 1.0, scale_z: float = 1.0):
        """
        Initialize the transform component
        
        Args:
            x (float): X position
            y (float): Y position
            z (float): Z position
            h (float): Heading (yaw) in degrees
            p (float): Pitch in degrees
            r (float): Roll in degrees
            scale_x (float): X scale
            scale_y (float): Y scale
            scale_z (float): Z scale
        """
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.h = h
        self.p = p
        self.r = r
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z
        
        # Panda3D node for this transform
        self.node_path = None
    
    def update(self, dt: float):
        """Update the transform"""
        # If we have a node path, update its position, rotation, and scale
        if self.node_path:
            self.node_path.setPos(self.x, self.y, self.z)
            self.node_path.setHpr(self.h, self.p, self.r)
            self.node_path.setScale(self.scale_x, self.scale_y, self.scale_z)
    
    def set_position(self, x: float, y: float, z: float = None):
        """
        Set the position of the entity
        
        Args:
            x (float): X position
            y (float): Y position
            z (float, optional): Z position (unchanged if None)
        """
        self.x = x
        self.y = y
        if z is not None:
            self.z = z
        
        if self.node_path:
            if z is not None:
                self.node_path.setPos(x, y, z)
            else:
                self.node_path.setX(x)
                self.node_path.setY(y)
    
    def set_rotation(self, h: float, p: float = None, r: float = None):
        """
        Set the rotation of the entity
        
        Args:
            h (float): Heading (yaw) in degrees
            p (float, optional): Pitch in degrees (unchanged if None)
            r (float, optional): Roll in degrees (unchanged if None)
        """
        self.h = h
        if p is not None:
            self.p = p
        if r is not None:
            self.r = r
        
        if self.node_path:
            if p is not None and r is not None:
                self.node_path.setHpr(h, p, r)
            else:
                if p is not None:
                    self.node_path.setP(p)
                if r is not None:
                    self.node_path.setR(r)
                self.node_path.setH(h)
    
    def set_scale(self, scale_x: float, scale_y: float = None, scale_z: float = None):
        """
        Set the scale of the entity
        
        Args:
            scale_x (float): X scale (if scale_y and scale_z are None, used for all axes)
            scale_y (float, optional): Y scale (unchanged if None)
            scale_z (float, optional): Z scale (unchanged if None)
        """
        self.scale_x = scale_x
        
        if scale_y is None and scale_z is None:
            # Uniform scale
            self.scale_y = scale_x
            self.scale_z = scale_x
        else:
            if scale_y is not None:
                self.scale_y = scale_y
            if scale_z is not None:
                self.scale_z = scale_z
        
        if self.node_path:
            self.node_path.setScale(self.scale_x, self.scale_y, self.scale_z)


class SpriteComponent(Component):
    """Component for rendering a sprite"""
    
    def __init__(self, texture_path: str = None, width: float = 1.0, height: float = 1.0):
        """
        Initialize the sprite component
        
        Args:
            texture_path (str): Path to the texture file
            width (float): Width of the sprite
            height (float): Height of the sprite
        """
        super().__init__()
        self.texture_path = texture_path
        self.width = width
        self.height = height
        
        # Panda3D objects
        self.card = None
        self.texture = None
    
    def on_attach(self, entity):
        """Called when the component is attached to an entity"""
        super().on_attach(entity)
        
        # Load the sprite if we have a texture path
        if self.texture_path and entity.game:
            self.load_sprite(entity.game)
    
    def load_sprite(self, game):
        """
        Load the sprite
        
        Args:
            game: The game instance
        """
        # Create a card (plane) for the sprite
        from panda3d.core import CardMaker
        cm = CardMaker(f"Sprite-{self.entity.id if self.entity else 'Unattached'}")
        cm.setFrame(-self.width/2, self.width/2, -self.height/2, self.height/2)
        
        # Get the transform component
        transform = self.entity.get_component(TransformComponent)
        if transform and transform.node_path:
            # Attach the card to the entity's node path
            self.card = transform.node_path.attachNewNode(cm.generate())
            
            # Load the texture
            if self.texture_path:
                self.texture = game.resource_manager.load_texture(self.texture_path)
                if self.texture:
                    self.card.setTexture(self.texture)
        else:
            print(f"Warning: Sprite component attached to entity without a node path")
    
    def set_texture(self, texture_path: str, game):
        """
        Set the sprite texture
        
        Args:
            texture_path (str): Path to the texture file
            game: The game instance
        """
        self.texture_path = texture_path
        
        if self.card:
            # Load and apply the new texture
            self.texture = game.resource_manager.load_texture(texture_path)
            if self.texture:
                self.card.setTexture(self.texture)
    
    def on_detach(self):
        """Called when the component is detached from an entity"""
        super().on_detach()
        
        # Clean up resources
        if self.card:
            self.card.removeNode()
            self.card = None
        self.texture = None


class PhysicsComponent(Component):
    """Component for physics properties and movement"""
    
    def __init__(self, mass: float = 1.0, velocity_x: float = 0.0, velocity_y: float = 0.0,
                 acceleration_x: float = 0.0, acceleration_y: float = 0.0,
                 max_velocity: float = 10.0, friction: float = 0.1):
        """
        Initialize the physics component
        
        Args:
            mass (float): Mass of the entity
            velocity_x (float): Initial X velocity
            velocity_y (float): Initial Y velocity
            acceleration_x (float): Initial X acceleration
            acceleration_y (float): Initial Y acceleration
            max_velocity (float): Maximum velocity
            friction (float): Friction coefficient (0-1)
        """
        super().__init__()
        self.mass = mass
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.max_velocity = max_velocity
        self.friction = friction
    
    def update(self, dt: float):
        """Update the physics"""
        # Update velocity based on acceleration
        self.velocity_x += self.acceleration_x * dt
        self.velocity_y += self.acceleration_y * dt
        
        # Apply friction
        self.velocity_x *= (1.0 - self.friction * dt)
        self.velocity_y *= (1.0 - self.friction * dt)
        
        # Clamp to max velocity
        speed = (self.velocity_x ** 2 + self.velocity_y ** 2) ** 0.5
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            self.velocity_x *= scale
            self.velocity_y *= scale
        
        # Update position based on velocity
        transform = self.entity.get_component(TransformComponent)
        if transform:
            transform.x += self.velocity_x * dt
            transform.y += self.velocity_y * dt
    
    def apply_force(self, force_x: float, force_y: float):
        """
        Apply a force to the entity
        
        Args:
            force_x (float): X force
            force_y (float): Y force
        """
        # Force = mass * acceleration (F = ma), so a = F/m
        self.acceleration_x += force_x / self.mass
        self.acceleration_y += force_y / self.mass
    
    def set_velocity(self, velocity_x: float, velocity_y: float):
        """
        Set the velocity directly
        
        Args:
            velocity_x (float): X velocity
            velocity_y (float): Y velocity
        """
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y


class CollisionComponent(Component):
    """Component for collision detection"""
    
    def __init__(self, radius: float = 0.5, collision_mask: int = 1):
        """
        Initialize the collision component
        
        Args:
            radius (float): Collision radius
            collision_mask (int): Collision mask for filtering collisions
        """
        super().__init__()
        self.radius = radius
        self.collision_mask = collision_mask
        
        # Collision state
        self.is_colliding = False
        self.colliding_with = []
    
    def update(self, dt: float):
        """Update the collision state"""
        # This would normally check for collisions with other entities
        # For now, just reset collision state
        self.is_colliding = False
        self.colliding_with = []
    
    def check_collision(self, other):
        """
        Check if this entity is colliding with another entity
        
        Args:
            other: The other entity to check collision with
            
        Returns:
            bool: True if colliding, False otherwise
        """
        # Get both transform components
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.get_component(TransformComponent)
        other_collision = other.get_component(CollisionComponent)
        
        if not transform or not other_transform or not other_collision:
            return False
        
        # Simple distance-based collision check
        dx = transform.x - other_transform.x
        dy = transform.y - other_transform.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Check if the distance is less than the sum of radii
        is_colliding = distance < (self.radius + other_collision.radius)
        
        if is_colliding:
            self.is_colliding = True
            self.colliding_with.append(other)
        
        return is_colliding


class AnimationComponent(Component):
    """Component for sprite animations"""
    
    def __init__(self, animations: Dict[str, List[str]] = None, frame_duration: float = 0.1):
        """
        Initialize the animation component
        
        Args:
            animations (Dict[str, List[str]]): Dictionary of animation name -> list of texture paths
            frame_duration (float): Duration of each frame in seconds
        """
        super().__init__()
        self.animations = animations or {}
        self.frame_duration = frame_duration
        
        # Animation state
        self.current_animation = None
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.is_playing = False
        self.loop = True
    
    def update(self, dt: float):
        """Update the animation"""
        if not self.is_playing or not self.current_animation:
            return
        
        # Update time accumulator
        self.time_accumulator += dt
        
        # Check if it's time to advance to the next frame
        if self.time_accumulator >= self.frame_duration:
            self.time_accumulator -= self.frame_duration
            
            # Advance frame
            self.current_frame += 1
            
            # Check for animation end
            frames = self.animations.get(self.current_animation, [])
            if self.current_frame >= len(frames):
                if self.loop:
                    # Loop back to start
                    self.current_frame = 0
                else:
                    # Stop at last frame
                    self.current_frame = len(frames) - 1
                    self.is_playing = False
            
            # Update sprite texture
            if 0 <= self.current_frame < len(frames):
                sprite = self.entity.get_component(SpriteComponent)
                if sprite and self.entity.game:
                    sprite.set_texture(frames[self.current_frame], self.entity.game)
    
    def play(self, animation_name: str, loop: bool = True):
        """
        Play an animation
        
        Args:
            animation_name (str): Name of the animation to play
            loop (bool): Whether to loop the animation
        """
        if animation_name not in self.animations:
            print(f"Warning: Animation '{animation_name}' not found")
            return
        
        # If already playing this animation, do nothing
        if self.current_animation == animation_name and self.is_playing:
            return
        
        self.current_animation = animation_name
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.is_playing = True
        self.loop = loop
        
        # Update sprite texture immediately
        frames = self.animations.get(animation_name, [])
        if frames and self.entity and self.entity.game:
            sprite = self.entity.get_component(SpriteComponent)
            if sprite:
                sprite.set_texture(frames[0], self.entity.game)
    
    def stop(self):
        """Stop the current animation"""
        self.is_playing = False
    
    def add_animation(self, name: str, texture_paths: List[str]):
        """
        Add a new animation
        
        Args:
            name (str): Name of the animation
            texture_paths (List[str]): List of texture paths for the animation frames
        """
        self.animations[name] = texture_paths


class Entity:
    """Base class for all game entities"""
    
    def __init__(self, game=None, name: str = "Entity"):
        """
        Initialize the entity
        
        Args:
            game: The game instance
            name (str): Name of the entity
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.game = game
        self.components: Dict[Type[Component], Component] = {}
        self.active = True
        
        # Create a node path for this entity if game is provided
        self.node_path = None
        if game:
            self.node_path = game.render.attachNewNode(f"Entity-{self.id}")
    
    def add_component(self, component: Component) -> Component:
        """
        Add a component to the entity
        
        Args:
            component (Component): The component to add
            
        Returns:
            Component: The added component
        """
        component_type = type(component)
        self.components[component_type] = component
        component.on_attach(self)
        
        # Special handling for TransformComponent
        if isinstance(component, TransformComponent) and self.node_path:
            component.node_path = self.node_path
        
        return component
    
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Get a component by type
        
        Args:
            component_type (Type[T]): The type of component to get
            
        Returns:
            Optional[T]: The component, or None if not found
        """
        return self.components.get(component_type)
    
    def remove_component(self, component_type: Type[Component]) -> bool:
        """
        Remove a component by type
        
        Args:
            component_type (Type[Component]): The type of component to remove
            
        Returns:
            bool: True if the component was removed, False if not found
        """
        if component_type in self.components:
            component = self.components[component_type]
            component.on_detach()
            del self.components[component_type]
            return True
        return False
    
    def update(self, dt: float):
        """
        Update the entity
        
        Args:
            dt (float): Delta time since last update
        """
        if not self.active:
            return
        
        # Update all components
        for component in self.components.values():
            component.update(dt)
    
    def destroy(self):
        """Destroy the entity and all its components"""
        # Detach all components
        for component in list(self.components.values()):
            component.on_detach()
        
        self.components.clear()
        
        # Remove from scene graph
        if self.node_path:
            self.node_path.removeNode()
            self.node_path = None
        
        self.active = False


class EntityManager:
    """Manages all game entities"""
    
    def __init__(self, game):
        """
        Initialize the entity manager
        
        Args:
            game: The game instance
        """
        self.game = game
        self.entities: Dict[str, Entity] = {}
    
    def create_entity(self, name: str = "Entity") -> Entity:
        """
        Create a new entity
        
        Args:
            name (str): Name of the entity
            
        Returns:
            Entity: The created entity
        """
        entity = Entity(self.game, name)
        self.entities[entity.id] = entity
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID
        
        Args:
            entity_id (str): ID of the entity
            
        Returns:
            Optional[Entity]: The entity, or None if not found
        """
        return self.entities.get(entity_id)
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity by ID
        
        Args:
            entity_id (str): ID of the entity
            
        Returns:
            bool: True if the entity was removed, False if not found
        """
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.destroy()
            del self.entities[entity_id]
            return True
        return False
    
    def update(self, dt: float):
        """
        Update all entities
        
        Args:
            dt (float): Delta time since last update
        """
        for entity in list(self.entities.values()):
            entity.update(dt)
    
    def clear(self):
        """Remove all entities"""
        for entity in list(self.entities.values()):
            entity.destroy()
        
        self.entities.clear()
    
    def get_entities_by_name(self, name: str) -> List[Entity]:
        """
        Get all entities with a specific name
        
        Args:
            name (str): Name to search for
            
        Returns:
            List[Entity]: List of matching entities
        """
        return [entity for entity in self.entities.values() if entity.name == name] 