#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI Manager for Nightfall Defenders
Manages UI components and handles mouse interaction
"""

from typing import Dict, List, Any, Optional, Set
from panda3d.core import MouseWatcher, MouseButton, Point2

class UIManager:
    """Manages UI components and mouse interaction"""
    
    def __init__(self, game):
        """
        Initialize the UI manager
        
        Args:
            game: Main game instance
        """
        self.game = game
        
        # Registered UI components
        self.components = set()
        
        # Track mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_buttons = {"mouse1": False, "mouse3": False}
        
        # Custom cursor
        self.custom_cursor_enabled = False
        self.cursor_image = None
        
        # Add update task to game task manager
        self.game.task_mgr.add(self.update, "ui_manager_update")
        
        # Set up mouse event handlers
        self._setup_mouse_events()
    
    def _setup_mouse_events(self):
        """Set up handlers for mouse events"""
        # Mouse button events
        self.game.accept("mouse1", self._on_mouse_button, ["mouse1", True])
        self.game.accept("mouse1-up", self._on_mouse_button, ["mouse1", False])
        self.game.accept("mouse3", self._on_mouse_button, ["mouse3", True])
        self.game.accept("mouse3-up", self._on_mouse_button, ["mouse3", False])
    
    def update(self, task):
        """
        Update UI components and handle mouse movement
        
        Args:
            task: Task object from Panda3D
            
        Returns:
            Task continuation value
        """
        # Get mouse position
        mouse_watcher = self.game.mouseWatcherNode
        if mouse_watcher.hasMouse():
            # Get mouse position in render2d coordinates (-1 to 1)
            mouse_pos = Point2(mouse_watcher.getMouse())
            
            # Convert to aspect2d coordinates
            self.mouse_x = mouse_pos.getX()
            self.mouse_y = mouse_pos.getY()
            
            # Update custom cursor position if enabled
            if self.custom_cursor_enabled and self.cursor_image:
                self.cursor_image.setPos(self.mouse_x, 0, self.mouse_y)
                
            # Notify components of mouse movement
            self._handle_mouse_move(self.mouse_x, self.mouse_y)
        
        return task.cont
    
    def _handle_mouse_move(self, x, y):
        """
        Handle mouse movement and notify components
        
        Args:
            x: X coordinate in render2d space
            y: Y coordinate in render2d space
        """
        # Notify components of mouse movement in reverse order (top to bottom)
        # This ensures that top components get mouse events first
        for component in sorted(self.components, key=lambda c: -c.z_index):
            component.on_mouse_move(x, y)
    
    def _on_mouse_button(self, button, pressed):
        """
        Handle mouse button events
        
        Args:
            button: Button that was pressed/released (e.g., "mouse1")
            pressed: True if button was pressed, False if released
        """
        # Update button state
        self.mouse_buttons[button] = pressed
        
        # Notify components of button event in reverse order (top to bottom)
        for component in sorted(self.components, key=lambda c: -c.z_index):
            # If a component handles the event, don't pass it to others below it
            if component.on_mouse_button(button, pressed, self.mouse_x, self.mouse_y):
                break
    
    def register_component(self, component):
        """
        Register a UI component with the manager
        
        Args:
            component: Component to register
        """
        self.components.add(component)
    
    def unregister_component(self, component):
        """
        Unregister a UI component from the manager
        
        Args:
            component: Component to unregister
        """
        if component in self.components:
            self.components.remove(component)
    
    def enable_custom_cursor(self, image_path=None):
        """
        Enable a custom mouse cursor
        
        Args:
            image_path: Path to cursor image (if None, uses a default cursor)
        """
        from direct.gui.OnscreenImage import OnscreenImage
        from panda3d.core import TransparencyAttrib
        
        # Hide the system cursor
        props = self.game.win.getProperties()
        props.setCursorHidden(True)
        self.game.win.requestProperties(props)
        
        # Create cursor image
        if image_path:
            self.cursor_image = OnscreenImage(
                image=image_path,
                pos=(0, 0, 0),
                scale=0.03
            )
        else:
            # Use a default cursor if no image is provided
            self.cursor_image = OnscreenImage(
                image="assets/generated/ui/cursor.png",
                pos=(0, 0, 0),
                scale=0.03
            )
        
        # Make the cursor image transparent
        self.cursor_image.setTransparency(TransparencyAttrib.MAlpha)
        
        # Move the cursor to the top layer
        self.cursor_image.setZ(100)
        
        # Set cursor position
        self.cursor_image.setPos(self.mouse_x, 0, self.mouse_y)
        
        self.custom_cursor_enabled = True
    
    def disable_custom_cursor(self):
        """Disable the custom cursor and restore the system cursor"""
        # Show the system cursor
        props = self.game.win.getProperties()
        props.setCursorHidden(False)
        self.game.win.requestProperties(props)
        
        # Remove the cursor image
        if self.cursor_image:
            self.cursor_image.destroy()
            self.cursor_image = None
        
        self.custom_cursor_enabled = False
    
    def cleanup(self):
        """Clean up resources and remove tasks"""
        # Remove task
        self.game.task_mgr.remove("ui_manager_update")
        
        # Remove mouse event handlers
        self.game.ignore("mouse1")
        self.game.ignore("mouse1-up")
        self.game.ignore("mouse3")
        self.game.ignore("mouse3-up")
        
        # Disable custom cursor
        self.disable_custom_cursor()
        
        # Clear components
        self.components.clear() 