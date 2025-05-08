#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resource Drop module for Nightfall Defenders
Implements items dropped by enemies when defeated
"""

from panda3d.core import NodePath, Vec3, Point3
import random
import math

class ResourceDrop:
    """Resource item dropped by enemies or found in the world"""
    
    def __init__(self, game, position, resource_type, amount=1, lifetime=30.0):
        """
        Initialize a resource drop
        
        Args:
            game: The main game instance
            position (Vec3): Position to spawn the drop
            resource_type (str): Type of resource (wood, stone, crystal, herb, experience)
            amount (int): Amount of the resource
            lifetime (float): How long the drop remains in the world (seconds)
        """
        self.game = game
        
        # Create the resource node
        self.root = NodePath("ResourceDrop")
        self.root.reparentTo(game.render)
        
        # Drop properties
        self.position = Vec3(position)
        self.collision_radius = 0.7
        self.resource_type = resource_type
        self.amount = amount
        self.lifetime = lifetime
        self.time_alive = 0.0
        self.is_active = True
        
        # Add a bobbing animation effect
        self.bob_height = 0.2
        self.bob_speed = 2.0
        self.initial_height = position.z
        
        # Setup visuals based on resource type
        self.setup_model()
        
        # Set initial position
        self.root.setPos(self.position)
        
        # Add a slight randomization to position
        random_offset = Vec3(
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            0
        )
        self.position += random_offset
        self.root.setPos(self.position)
        
        # Debug visualization
        self.debug_node = self.root.attachNewNode("DropDebug")
        self.draw_debug_visualization()
    
    def setup_model(self):
        """Set up the resource drop model based on type"""
        try:
            self.model = self.game.loader.loadModel("models/box")
            
            # Scale and color based on resource type
            if self.resource_type == "wood":
                self.model.setScale(0.3, 0.3, 0.3)
                self.model.setColor(0.6, 0.4, 0.2, 1)  # Brown
            elif self.resource_type == "stone":
                self.model.setScale(0.3, 0.3, 0.2)
                self.model.setColor(0.5, 0.5, 0.5, 1)  # Gray
            elif self.resource_type == "crystal":
                self.model.setScale(0.2, 0.2, 0.4)
                self.model.setColor(0.4, 0.8, 0.8, 1)  # Blue-ish
            elif self.resource_type == "herb":
                self.model.setScale(0.2, 0.2, 0.1)
                self.model.setColor(0.2, 0.8, 0.2, 1)  # Green
            elif self.resource_type == "experience":
                self.model.setScale(0.3, 0.3, 0.3)
                self.model.setColor(0.8, 0.3, 0.8, 1)  # Purple
            else:
                # Default
                self.model.setScale(0.3, 0.3, 0.3)
                self.model.setColor(1.0, 1.0, 1.0, 1)
            
            self.model.reparentTo(self.root)
            
            # Make the drop rotate slowly
            self.model.hprInterval(4, (360, 360, 0)).loop()
            
        except Exception as e:
            print(f"Error loading resource drop model: {e}")
            # Fallback to a simple marker
            from panda3d.core import PointLight
            plight = PointLight("DropMarker")
            plight.setColor((1, 1, 0, 1))
            plnp = self.root.attachNewNode(plight)
            plnp.setPos(0, 0, 0.3)
    
    def draw_debug_visualization(self):
        """Draw debug visualization for the resource drop"""
        # Clear any existing debug visualization
        self.debug_node.removeNode()
        self.debug_node = self.root.attachNewNode("DropDebug")
        
        # Only draw debug visuals if debug mode is enabled
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            from panda3d.core import LineSegs
            
            # Draw pickup radius
            segs = LineSegs()
            segs.setColor(1, 1, 0, 1)  # Yellow
            segments = 16
            for i in range(segments + 1):
                angle = i * 360 / segments
                x = self.collision_radius * math.sin(math.radians(angle))
                y = self.collision_radius * math.cos(math.radians(angle))
                if i == 0:
                    segs.moveTo(x, y, 0.05)  # Slightly above ground
                else:
                    segs.drawTo(x, y, 0.05)
            self.debug_node.attachNewNode(segs.create())
    
    def update(self, dt):
        """
        Update the resource drop
        
        Args:
            dt (float): Delta time since last update
        
        Returns:
            bool: True if the drop is still active, False if it should be removed
        """
        if not self.is_active:
            return False
        
        # Update lifetime
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.destroy()
            return False
        
        # Apply bobbing animation
        bob_offset = math.sin(self.time_alive * self.bob_speed) * self.bob_height
        self.root.setZ(self.position.z + bob_offset)
        
        # Check if player is nearby to pick up
        if hasattr(self.game, 'player') and self.game.player:
            player_pos = self.game.player.position
            distance = (player_pos - self.position).length()
            
            if distance < self.collision_radius + self.game.player.collision_radius:
                self.pickup(self.game.player)
                return False
        
        # Update debug visualization if needed
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            self.draw_debug_visualization()
        
        return True
    
    def pickup(self, entity):
        """
        Pick up the resource
        
        Args:
            entity: The entity that is picking up the resource
        
        Returns:
            dict: Resource type and amount that was picked up
        """
        if not self.is_active:
            return None
        
        # If it's a player, add to their inventory
        if hasattr(entity, 'inventory') and self.resource_type != "experience":
            entity.inventory[self.resource_type] = entity.inventory.get(self.resource_type, 0) + self.amount
            print(f"Picked up {self.amount} {self.resource_type}! Inventory: {entity.get_inventory_string()}")
        
        # If it's experience, add to player's experience
        if self.resource_type == "experience" and hasattr(entity, 'add_experience'):
            entity.add_experience(self.amount)
            print(f"Gained {self.amount} experience!")
        
        # Play pickup sound if available
        if hasattr(self.game, 'resource_manager') and hasattr(self.game.resource_manager, 'load_sound'):
            try:
                sound = self.game.resource_manager.load_sound("pickup.wav", volume=0.5)
                if sound:
                    sound.play()
            except:
                pass
        
        # Destroy this resource drop
        self.destroy()
        
        return {
            "type": self.resource_type,
            "amount": self.amount
        }
    
    def destroy(self):
        """Destroy the resource drop"""
        self.is_active = False
        self.root.removeNode() 