#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crafting Bench for Nightfall Defenders
An interactive object that the player can use to access crafting
"""

from panda3d.core import NodePath, Vec3, Point3, BitMask32
import math

class CraftingBench:
    """Interactive crafting bench object"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """
        Initialize a crafting bench
        
        Args:
            game: The main game instance
            position (Vec3): Position of the crafting bench
        """
        self.game = game
        
        # Create the crafting bench node
        self.root = NodePath("CraftingBench")
        self.root.reparentTo(game.render)
        
        # Set properties
        self.position = Vec3(position)
        self.collision_radius = 1.2  # Larger interaction radius
        
        # Set initial position
        self.root.setPos(self.position)
        
        # Set up the model
        self.setup_model()
        
        # Debug visualization
        self.debug_node = self.root.attachNewNode("BenchDebug")
        self.draw_debug_visualization()
        
        # Set as interactable
        self.is_interactable = True
    
    def setup_model(self):
        """Set up the crafting bench model"""
        try:
            # For now, just use a box as placeholder
            self.model = self.game.loader.loadModel("models/box")
            self.model.setScale(1.0, 1.0, 0.5)  # Size of bench
            self.model.reparentTo(self.root)
            
            # Set color
            self.model.setColor(0.6, 0.4, 0.2, 1)  # Brown wooden color
            
            # Add a second box for the table top
            self.top = self.game.loader.loadModel("models/box")
            self.top.setScale(1.2, 0.8, 0.1)  # Table top
            self.top.setPos(0, 0, 0.3)  # Position on top of the bench
            self.top.setColor(0.7, 0.5, 0.3, 1)  # Lighter brown
            self.top.reparentTo(self.root)
            
            # Add a prompt text
            from direct.gui.OnscreenText import OnscreenText
            from panda3d.core import TextNode
            
            text = TextNode('craftingBenchPrompt')
            text.setText("Press E to Craft")
            text.setAlign(TextNode.ACenter)
            text.setTextColor(1, 1, 1, 1)
            
            self.prompt = self.root.attachNewNode(text)
            self.prompt.setScale(0.5)
            self.prompt.setPos(0, 0, 1.2)  # Position above the bench
            self.prompt.setBillboardPointEye()  # Always face camera
            self.prompt.hide()  # Hide initially
            
        except Exception as e:
            print(f"Error loading crafting bench model: {e}")
            # Fallback to a simple marker
            from panda3d.core import PointLight
            plight = PointLight("BenchMarker")
            plight.setColor((0.8, 0.6, 0.3, 1))
            plnp = self.root.attachNewNode(plight)
            plnp.setPos(0, 0, 0.5)
    
    def draw_debug_visualization(self):
        """Draw debug visualization for the crafting bench"""
        # Clear any existing debug visualization
        self.debug_node.removeNode()
        self.debug_node = self.root.attachNewNode("BenchDebug")
        
        # Only draw debug visuals if debug mode is enabled
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            from panda3d.core import LineSegs
            
            # Draw interaction radius
            segs = LineSegs()
            segs.setColor(0.2, 0.8, 0.2, 1)  # Green
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
        Update the crafting bench state
        
        Args:
            dt (float): Delta time since last update
        
        Returns:
            bool: Always True as crafting benches persist
        """
        # Check if player is nearby
        show_prompt = False
        if hasattr(self.game, 'player') and self.game.player:
            distance = (self.game.player.position - self.position).length()
            show_prompt = distance < self.collision_radius
        
        # Show/hide the prompt based on distance
        if hasattr(self, 'prompt'):
            if show_prompt and not self.prompt.isHidden():
                self.prompt.show()
            elif not show_prompt and self.prompt.isHidden():
                self.prompt.hide()
        
        # Update debug visualization if needed
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            self.draw_debug_visualization()
        
        return True
    
    def interact(self, player):
        """
        Handle interaction with the crafting bench
        
        Args:
            player: The player entity interacting with the bench
        
        Returns:
            bool: True if interaction was handled
        """
        # Open the crafting UI
        if hasattr(self.game, 'crafting_ui'):
            self.game.crafting_ui.show()
        else:
            print("Crafting UI not available")
        
        return True 