#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enemy Healthbar for Nightfall Defenders
Displays a health bar above enemies
"""

from panda3d.core import NodePath, TextNode, Vec4
from direct.gui.DirectGui import DirectWaitBar

class EnemyHealthBar:
    """
    Displays a health bar above an enemy that follows its position in the world
    """
    
    def __init__(self, game, enemy, y_offset=1.5, width=1.0):
        """
        Initialize a health bar for an enemy
        
        Args:
            game: The main game instance
            enemy: The enemy to track
            y_offset (float): Height above the enemy
            width (float): Width of the health bar
        """
        self.game = game
        self.enemy = enemy
        self.y_offset = y_offset
        self.width = width
        
        # Create a node that will be positioned above the enemy
        self.root = NodePath("HealthBarRoot")
        self.root.setBillboardPointEye()  # Always face camera
        self.root.reparentTo(self.enemy.root)
        self.root.setPos(0, 0, self.y_offset)
        self.root.setScale(0.5)  # Scale down for reasonable size
        
        # Create the health bar
        self.health_bar = DirectWaitBar(
            scale=(self.width, 1, 0.1),
            value=100,
            barColor=(0.2, 0.8, 0.2, 1),  # Green
            frameColor=(0.2, 0.2, 0.2, 0.8),  # Dark gray frame
            frameSize=(-0.5, 0.5, -0.08, 0.08),
            pos=(0, 0, 0),
            parent=self.root
        )
        
        # Initially hide the health bar until the enemy takes damage
        self.health_bar.hide()
        self.visible = False
        self.visibility_time = 0
        self.visibility_duration = 3.0  # Show for 3 seconds after taking damage
    
    def update(self, dt):
        """
        Update the health bar
        
        Args:
            dt (float): Delta time since the last update
        """
        # Don't update if the enemy is gone
        if not self.enemy or not hasattr(self.enemy, 'health'):
            return
        
        # Update health percentage
        health_percent = (self.enemy.health / self.enemy.max_health) * 100
        self.health_bar["value"] = health_percent
        
        # Update bar color based on health percentage
        if health_percent > 60:
            self.health_bar["barColor"] = (0.2, 0.8, 0.2, 1)  # Green
        elif health_percent > 30:
            self.health_bar["barColor"] = (0.8, 0.8, 0.2, 1)  # Yellow
        else:
            self.health_bar["barColor"] = (0.8, 0.2, 0.2, 1)  # Red
        
        # Update visibility
        if self.visible:
            self.visibility_time -= dt
            if self.visibility_time <= 0:
                self.hide()
    
    def show(self):
        """Show the health bar"""
        if not self.visible:
            self.health_bar.show()
            self.visible = True
        
        # Reset visibility timer
        self.visibility_time = self.visibility_duration
    
    def hide(self):
        """Hide the health bar"""
        if self.visible:
            self.health_bar.hide()
            self.visible = False
    
    def destroy(self):
        """Clean up the health bar"""
        self.health_bar.destroy()
        self.root.removeNode() 