#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Input Manager for Nightfall Defenders
Handles keyboard, mouse, and controller input
"""

from direct.showbase.DirectObject import DirectObject
from panda3d.core import MouseButton, KeyboardButton, ModifierButtons

class InputManager(DirectObject):
    """
    Manages input from keyboard, mouse, and controllers
    Also handles input mapping and configuration
    """
    
    def __init__(self, game):
        """Initialize the input manager"""
        DirectObject.__init__(self)
        
        self.game = game
        
        # Track pressed keys and buttons
        self.keys_pressed = set()
        self.mouse_buttons_pressed = set()
        
        # Track mouse position
        self.mouse_position = (0, 0)
        self.mouse_delta = (0, 0)
        self.last_mouse_position = (0, 0)
        
        # Input mapping
        self.key_map = {
            # Movement
            "move_up": ["w", "arrow_up"],
            "move_down": ["s", "arrow_down"],
            "move_left": ["a", "arrow_left"],
            "move_right": ["d", "arrow_right"],
            
            # Actions
            "interact": ["e"],
            "attack": ["mouse1"],
            "secondary_ability": ["mouse3"],
            "dodge": ["space"],
            "use_item": ["q"],
            
            # UI
            "inventory": ["i"],
            "character": ["c"],
            "map": ["m"],
            "pause": ["escape"],
            
            # Debug
            "debug_toggle": ["f12"]
        }
        
        # Action state tracking for direct state setting
        self.action_states = {}
        
        # Set up input handlers
        self.setup_input_handlers()
    
    def setup_input_handlers(self):
        """Set up event handlers for input"""
        # Keyboard events
        self.accept("wheel_up", self.on_mouse_wheel, [1])
        self.accept("wheel_down", self.on_mouse_wheel, [-1])
        
        # Accept all keys for tracking pressed state
        for key in ["w", "a", "s", "d", 
                   "arrow_up", "arrow_down", "arrow_left", "arrow_right",
                   "e", "q", "i", "c", "m", "escape", "space", "f12"]:
            self.accept(key, self.on_key_pressed, [key])
            self.accept(key + "-up", self.on_key_released, [key])
        
        # Mouse buttons
        self.accept("mouse1", self.on_mouse_pressed, [MouseButton.one()])
        self.accept("mouse1-up", self.on_mouse_released, [MouseButton.one()])
        self.accept("mouse2", self.on_mouse_pressed, [MouseButton.two()])
        self.accept("mouse2-up", self.on_mouse_released, [MouseButton.two()])
        self.accept("mouse3", self.on_mouse_pressed, [MouseButton.three()])
        self.accept("mouse3-up", self.on_mouse_released, [MouseButton.three()])
    
    def on_key_pressed(self, key):
        """Handle key press events"""
        self.keys_pressed.add(key)
    
    def on_key_released(self, key):
        """Handle key release events"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def on_mouse_pressed(self, button):
        """Handle mouse button press events"""
        self.mouse_buttons_pressed.add(button)
    
    def on_mouse_released(self, button):
        """Handle mouse button release events"""
        if button in self.mouse_buttons_pressed:
            self.mouse_buttons_pressed.remove(button)
    
    def on_mouse_wheel(self, direction):
        """Handle mouse wheel events"""
        # Could be used for weapon switching, zooming, etc.
        pass
    
    def set_pressed(self, action, pressed):
        """
        Directly set the state of an action
        
        Args:
            action (str): The action name to set
            pressed (bool): Whether the action is pressed/active
        """
        self.action_states[action] = pressed
    
    def update(self, dt):
        """Update input state"""
        # Update mouse position and delta
        if self.game.mouseWatcherNode.hasMouse():
            x = self.game.mouseWatcherNode.getMouseX()
            y = self.game.mouseWatcherNode.getMouseY()
            
            self.mouse_position = (x, y)
            self.mouse_delta = (
                x - self.last_mouse_position[0],
                y - self.last_mouse_position[1]
            )
            self.last_mouse_position = self.mouse_position
    
    def is_pressed(self, action):
        """
        Check if an action's key or button is currently pressed
        
        Args:
            action (str): The action to check
            
        Returns:
            bool: True if the action's key is pressed, False otherwise
        """
        # First check if we have a direct state set
        if action in self.action_states:
            return self.action_states[action]
        
        # Then check key map
        if action in self.key_map:
            keys = self.key_map[action]
            for key in keys:
                if key in self.keys_pressed:
                    return True
                
                # Check for mouse buttons
                if key == "mouse1" and MouseButton.one() in self.mouse_buttons_pressed:
                    return True
                if key == "mouse2" and MouseButton.two() in self.mouse_buttons_pressed:
                    return True
                if key == "mouse3" and MouseButton.three() in self.mouse_buttons_pressed:
                    return True
        
        return False
    
    def get_movement_vector(self):
        """
        Get the movement direction based on pressed keys
        
        Returns:
            tuple: (x, y) movement vector, where each component is -1, 0, or 1
        """
        x = 0
        y = 0
        
        if self.is_pressed("move_up"):
            y += 1
        if self.is_pressed("move_down"):
            y -= 1
        if self.is_pressed("move_left"):
            x -= 1
        if self.is_pressed("move_right"):
            x += 1
            
        return (x, y)
    
    def get_mouse_position(self):
        """
        Get the current mouse position
        
        Returns:
            tuple: (x, y) coordinates in screen space (-1 to 1)
        """
        return self.mouse_position
    
    def get_mouse_delta(self):
        """
        Get the mouse movement since the last update
        
        Returns:
            tuple: (dx, dy) change in mouse position
        """
        return self.mouse_delta 