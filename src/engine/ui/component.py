#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI Component Base Class for Nightfall Defenders
Provides foundation for UI elements with mouse interaction
"""

from typing import Callable, Dict, List, Any, Optional, Tuple
from panda3d.core import NodePath, Vec3, MouseWatcher, MouseButton, Point2
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

class UIComponent:
    """Base class for all UI components with mouse interaction"""
    
    # Static counter for generating unique IDs
    _next_id = 0
    
    @classmethod
    def _generate_id(cls) -> int:
        """Generate a unique ID for this component"""
        id_value = cls._next_id
        cls._next_id += 1
        return id_value
    
    def __init__(self, game, parent=None, position=(0, 0, 0), size=(1, 1), z_index=0, visible=True):
        """
        Initialize the UI component
        
        Args:
            game: Main game instance
            parent: Parent node to attach to (if None, uses aspect2d)
            position: Position (x, y, z) relative to parent
            size: Size (width, height) of the component
            z_index: Z-index for stacking order
            visible: Whether the component is initially visible
        """
        self.game = game
        self.id = self._generate_id()
        self.parent = parent if parent else game.aspect2d
        self.position = Vec3(*position)
        self.size = size
        self.z_index = z_index
        self._visible = visible
        
        # Create the root frame for this component
        self.frame = DirectFrame(
            parent=self.parent,
            pos=(position[0], 0, position[1]),  # Panda3D uses (x, z, y) for 2D positions
            frameSize=(-size[0]/2, size[0]/2, -size[1]/2, size[1]/2),
            frameColor=(0, 0, 0, 0),  # Transparent by default
            sortOrder=z_index
        )
        
        # Mouse interaction state
        self.mouse_over = False
        self.mouse_down = False
        self.mouse_disabled = False
        
        # Event callbacks
        self.callbacks = {
            "click": [],
            "mouse_over": [],
            "mouse_out": [],
            "mouse_down": [],
            "mouse_up": []
        }
        
        # Set initial visibility
        if not visible:
            self.hide()
        
        # Setup mouse watching
        self.setup_mouse_watching()
    
    def setup_mouse_watching(self):
        """Set up mouse event detection for this component"""
        # Register this component with the game's UI manager if available
        if hasattr(self.game, 'ui_manager'):
            self.game.ui_manager.register_component(self)
    
    def get_frame_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the bounds of this component in render2d space
        
        Returns:
            Tuple of (min_x, max_x, min_y, max_y)
        """
        # Convert from Panda3D's coordinate system
        x, _, y = self.frame.getPos()
        width, height = self.size
        
        return (
            x - width/2,  # min_x
            x + width/2,  # max_x
            y - height/2, # min_y
            y + height/2  # max_y
        )
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if the given point is within this component's bounds
        
        Args:
            x: X coordinate in render2d space
            y: Y coordinate in render2d space
            
        Returns:
            True if the point is within bounds, False otherwise
        """
        if not self._visible or self.mouse_disabled:
            return False
            
        # Get bounds
        min_x, max_x, min_y, max_y = self.get_frame_bounds()
        
        # Check if point is within bounds
        return (min_x <= x <= max_x) and (min_y <= y <= max_y)
    
    def on_mouse_move(self, x: float, y: float) -> bool:
        """
        Handle mouse movement events
        
        Args:
            x: X coordinate in render2d space
            y: Y coordinate in render2d space
            
        Returns:
            True if the mouse is over this component, False otherwise
        """
        if not self._visible or self.mouse_disabled:
            if self.mouse_over:
                self.mouse_over = False
                self._trigger_callbacks("mouse_out")
            return False
            
        # Check if mouse is over this component
        is_over = self.contains_point(x, y)
        
        # Handle mouse over/out events
        if is_over and not self.mouse_over:
            self.mouse_over = True
            self._trigger_callbacks("mouse_over")
        elif not is_over and self.mouse_over:
            self.mouse_over = False
            self._trigger_callbacks("mouse_out")
        
        return is_over
    
    def on_mouse_button(self, button: str, pressed: bool, x: float, y: float) -> bool:
        """
        Handle mouse button events
        
        Args:
            button: Button that was pressed/released (e.g., "mouse1")
            pressed: True if button was pressed, False if released
            x: X coordinate in render2d space
            y: Y coordinate in render2d space
            
        Returns:
            True if the event was handled, False otherwise
        """
        if not self._visible or self.mouse_disabled:
            return False
            
        # Check if the mouse is over this component
        is_over = self.contains_point(x, y)
        
        if is_over:
            if button == "mouse1":
                if pressed:
                    # Mouse down
                    self.mouse_down = True
                    self._trigger_callbacks("mouse_down")
                else:
                    # Mouse up
                    if self.mouse_down:
                        # This is a click (pressed and released over the same component)
                        self._trigger_callbacks("click")
                    
                    self.mouse_down = False
                    self._trigger_callbacks("mouse_up")
                
                return True
        elif not pressed and self.mouse_down:
            # Mouse was released outside the component
            self.mouse_down = False
            self._trigger_callbacks("mouse_up")
        
        return False
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """
        Add a callback function for an event
        
        Args:
            event_type: Type of event ("click", "mouse_over", "mouse_out", "mouse_down", "mouse_up")
            callback: Function to call when event occurs
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Remove a callback function for an event
        
        Args:
            event_type: Type of event
            callback: Function to remove
            
        Returns:
            True if callback was removed, False if not found
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        return False
    
    def _trigger_callbacks(self, event_type: str) -> None:
        """
        Trigger all callbacks for an event
        
        Args:
            event_type: Type of event
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                callback(self)
    
    def show(self) -> None:
        """Make the component visible"""
        self._visible = True
        self.frame.show()
    
    def hide(self) -> None:
        """Hide the component"""
        self._visible = False
        self.frame.hide()
    
    def is_visible(self) -> bool:
        """
        Check if the component is visible
        
        Returns:
            True if visible, False otherwise
        """
        return self._visible
    
    def set_position(self, x: float, y: float, z: float = 0) -> None:
        """
        Set the position of the component
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (usually 0 for 2D UI)
        """
        self.position = Vec3(x, z, y)  # Panda3D uses (x, z, y)
        self.frame.setPos(x, z, y)
    
    def set_size(self, width: float, height: float) -> None:
        """
        Set the size of the component
        
        Args:
            width: Width of the component
            height: Height of the component
        """
        self.size = (width, height)
        self.frame.setFrameSize(-width/2, width/2, -height/2, height/2)
    
    def enable_mouse(self) -> None:
        """Enable mouse interaction for this component"""
        self.mouse_disabled = False
    
    def disable_mouse(self) -> None:
        """Disable mouse interaction for this component"""
        self.mouse_disabled = True
        if self.mouse_over:
            self.mouse_over = False
            self._trigger_callbacks("mouse_out")
        if self.mouse_down:
            self.mouse_down = False
            self._trigger_callbacks("mouse_up")
    
    def cleanup(self) -> None:
        """Clean up resources for this component"""
        # Unregister from UI manager if available
        if hasattr(self.game, 'ui_manager'):
            self.game.ui_manager.unregister_component(self)
        
        # Clear callbacks
        for event_type in self.callbacks:
            self.callbacks[event_type] = []
        
        # Remove frame
        self.frame.destroy() 