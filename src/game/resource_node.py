#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resource Node module for Nightfall Defenders
Implements gatherable resources in the world
"""

from panda3d.core import NodePath, Vec3, Point3
import random
import math

class ResourceNode:
    """Resource node that can be harvested for materials"""
    
    def __init__(self, game, position, resource_type="wood"):
        """
        Initialize resource node
        
        Args:
            game: Game instance
            position: Position in the world
            resource_type: Type of resource node
        """
        self.game = game
        self.position = Vec3(position)
        self.resource_type = resource_type
        self.active = True
        
        # Resource node properties
        self.initial_resources = self._get_initial_resources()
        self.resources = self.initial_resources
        self.resources_per_harvest = 1
        self.max_harvests = self.initial_resources // self.resources_per_harvest
        self.harvest_cooldown = 0.5  # Seconds between harvests
        self.regeneration_time = self._get_regeneration_time()
        self.regeneration_timer = 0
        self.is_depleted = False
        
        # Base values for difficulty adjustment
        self.base_regeneration_time = self.regeneration_time
        self.base_resources_per_harvest = self.resources_per_harvest
        
        # Create a visual representation
        self.root = NodePath("ResourceNode")
        self.root.reparentTo(game.render)
        self.root.setPos(position)
        self.setup_model()
        
        # Track interaction state
        self.can_interact = True
        self.interaction_cooldown = 0
    
    def _get_initial_resources(self):
        """Get initial resources based on type"""
        initial_resources = {
            "wood": 5,
            "stone": 4,
            "herb": 3,
            "crystal": 2,
            "metal": 4
        }
        return initial_resources.get(self.resource_type, 3)
    
    def _get_regeneration_time(self):
        """Get regeneration time based on resource type"""
        # Regeneration time in seconds
        regeneration_times = {
            "wood": 60,      # 1 minute
            "stone": 120,    # 2 minutes
            "herb": 90,      # 1.5 minutes
            "crystal": 180,  # 3 minutes
            "metal": 150     # 2.5 minutes
        }
        return regeneration_times.get(self.resource_type, 120)
    
    def setup_model(self):
        """Set up the visual model"""
        # Load different models based on resource type
        model_paths = {
            "wood": "models/box",
            "stone": "models/box",
            "herb": "models/box",
            "crystal": "models/box",
            "metal": "models/box"
        }
        
        color_maps = {
            "wood": (0.6, 0.4, 0.2, 1),     # Brown
            "stone": (0.7, 0.7, 0.7, 1),    # Gray
            "herb": (0.2, 0.7, 0.3, 1),     # Green
            "crystal": (0.5, 0.5, 1.0, 1),  # Blue
            "metal": (0.7, 0.7, 0.8, 1)     # Silver
        }
        
        # Choose model and color based on resource type
        model_path = model_paths.get(self.resource_type, "models/box")
        color = color_maps.get(self.resource_type, (0.5, 0.5, 0.5, 1))
        
        try:
            self.model = self.game.loader.loadModel(model_path)
            scale = 0.5
            if self.resource_type == "wood":
                scale = 0.7
            elif self.resource_type == "crystal":
                scale = 0.4
            self.model.setScale(scale, scale, scale)
            self.model.setColor(*color)
            self.model.reparentTo(self.root)
        except Exception as e:
            print(f"Error loading resource node model: {e}")
    
    def update(self, dt):
        """
        Update resource node state
        
        Args:
            dt: Delta time in seconds
        """
        # Update interaction cooldown
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt
            if self.interaction_cooldown <= 0:
                self.can_interact = True
        
        # If depleted, handle regeneration
        if self.is_depleted:
            self.regeneration_timer += dt
            
            # Apply difficulty adjustment to regeneration time if available
            regeneration_time = self.regeneration_time
            if hasattr(self.game, 'adaptive_difficulty_system'):
                factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
                # For resources, higher resource_drop = faster regeneration
                regeneration_time = self.base_regeneration_time / factors['resource_drop']
            
            if self.regeneration_timer >= regeneration_time:
                self.regenerate()
    
    def harvest(self):
        """
        Harvest resources from the node
        
        Returns:
            tuple: (resource_type, amount) or None if can't harvest
        """
        if not self.can_interact or self.is_depleted:
            return None
        
        # Apply interaction cooldown
        self.can_interact = False
        self.interaction_cooldown = self.harvest_cooldown
        
        # Determine amount to harvest, with difficulty adjustment
        amount = self.resources_per_harvest
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            # Apply resource_drop multiplier to harvest amount
            base_amount = self.base_resources_per_harvest
            amount = max(1, int(base_amount * factors['resource_drop']))
            
            # Debug output if in debug mode
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                print(f"Resource harvest with difficulty factor: x{factors['resource_drop']:.2f}")
                print(f"Base amount: {base_amount}, Adjusted: {amount}")
        
        # Ensure we don't give more than available
        amount = min(amount, self.resources)
        
        # Reduce resources
        self.resources -= amount
        
        # Check if depleted
        if self.resources <= 0:
            self.deplete()
        
        # Handle model scaling based on remaining resources
        self._update_model_scale()
        
        # Record resource collection in performance tracker if available
        if hasattr(self.game, 'performance_tracker'):
            self.game.performance_tracker.record_resource_event(
                self.resource_type, amount, source="node")
            
        # Record in adaptive difficulty system if available
        if hasattr(self.game, 'adaptive_difficulty_system'):
            self.game.adaptive_difficulty_system.record_resource_event(
                'collected', self.resource_type, amount)
        
        return (self.resource_type, amount)
    
    def _update_model_scale(self):
        """Update model scale based on remaining resources"""
        if hasattr(self, 'model'):
            # Scale model based on remaining resources
            scale_factor = 0.3 + (0.7 * (self.resources / self.initial_resources))
            self.model.setScale(scale_factor, scale_factor, scale_factor)
    
    def deplete(self):
        """Deplete the resource node"""
        self.is_depleted = True
        self.resources = 0
        self.regeneration_timer = 0
        
        # Make node visually depleted
        if hasattr(self, 'model'):
            self.model.setColor(0.3, 0.3, 0.3, 0.5)  # Grayed out
            self.model.setScale(0.3, 0.3, 0.3)  # Smaller
    
    def regenerate(self):
        """Regenerate the resource node"""
        self.is_depleted = False
        self.resources = self.initial_resources
        self.regeneration_timer = 0
        
        # Restore visual appearance
        if hasattr(self, 'model'):
            color_maps = {
                "wood": (0.6, 0.4, 0.2, 1),
                "stone": (0.7, 0.7, 0.7, 1),
                "herb": (0.2, 0.7, 0.3, 1),
                "crystal": (0.5, 0.5, 1.0, 1),
                "metal": (0.7, 0.7, 0.8, 1)
            }
            color = color_maps.get(self.resource_type, (0.5, 0.5, 0.5, 1))
            self.model.setColor(*color)
            self.model.setScale(1.0, 1.0, 1.0)
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'root'):
            self.root.removeNode()
    
    def get_interaction_text(self):
        """Get text for interaction prompt"""
        if self.is_depleted:
            return f"Depleted {self.resource_type.capitalize()} (Regenerating)"
        else:
            return f"Harvest {self.resource_type.capitalize()} ({self.resources})" 