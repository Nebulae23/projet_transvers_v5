#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Button UI Component for Nightfall Defenders
Implements an interactive button with mouse hover and click effects
"""

from typing import Callable, Dict, List, Any, Optional, Tuple
from panda3d.core import Vec4, TextNode
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

from engine.ui.component import UIComponent

class Button(UIComponent):
    """Interactive button with text label and hover/click effects"""
    
    def __init__(self, game, text="Button", 
                 position=(0, 0, 0), 
                 size=(0.3, 0.1), 
                 parent=None,
                 command=None,
                 text_color=(1, 1, 1, 1),
                 normal_color=(0.25, 0.25, 0.25, 0.8),
                 hover_color=(0.35, 0.35, 0.35, 0.9),
                 click_color=(0.2, 0.2, 0.2, 1.0),
                 disabled_color=(0.15, 0.15, 0.15, 0.5),
                 text_scale=0.04,
                 rounded=True,
                 disabled=False,
                 z_index=0):
        """
        Initialize the button
        
        Args:
            game: Main game instance
            text: Text to display on the button
            position: Position (x, y, z) relative to parent
            size: Size (width, height) of the button
            parent: Parent node to attach to (if None, uses aspect2d)
            command: Function to call when button is clicked
            text_color: Color of the button text (r, g, b, a)
            normal_color: Button color in normal state (r, g, b, a)
            hover_color: Button color when hovered (r, g, b, a)
            click_color: Button color when clicked (r, g, b, a)
            disabled_color: Button color when disabled (r, g, b, a)
            text_scale: Scale of the button text
            rounded: Whether to use rounded corners
            disabled: Whether the button is initially disabled
            z_index: Z-index for stacking order
        """
        # Initialize base class
        super().__init__(game, parent, position, size, z_index)
        
        # Button properties
        self.text = text
        self.normal_color = Vec4(*normal_color)
        self.hover_color = Vec4(*hover_color)
        self.click_color = Vec4(*click_color)
        self.disabled_color = Vec4(*disabled_color)
        self.text_color = Vec4(*text_color)
        self.rounded = rounded
        self.disabled = disabled
        
        # Create the button background
        self.background = DirectFrame(
            parent=self.frame,
            pos=(0, 0, 0),  # Center in the frame
            frameSize=(-size[0]/2, size[0]/2, -size[1]/2, size[1]/2),
            frameColor=disabled_color if disabled else normal_color,
            relief="raised" if not rounded else "sunken",  # Use sunken for rounded effect
            borderWidth=(0.003, 0.003)
        )
        
        # Create the button text
        self.text_node = OnscreenText(
            text=text,
            parent=self.frame,
            pos=(0, 0),  # Center in the frame
            scale=text_scale,
            fg=text_color,
            shadow=(0, 0, 0, 0.5),
            shadowOffset=(0.002, 0.002),
            align=TextNode.ACenter
        )
        
        # Set up callbacks
        if command:
            self.add_callback("click", lambda btn: command())
        
        # Set up mouse event handlers
        self.add_callback("mouse_over", self._on_mouse_over)
        self.add_callback("mouse_out", self._on_mouse_out)
        self.add_callback("mouse_down", self._on_mouse_down)
        self.add_callback("mouse_up", self._on_mouse_up)
        
        # Set initial state
        if disabled:
            self.disable()
    
    def _on_mouse_over(self, button):
        """Handle mouse over event"""
        if not self.disabled:
            self.background["frameColor"] = self.hover_color
    
    def _on_mouse_out(self, button):
        """Handle mouse out event"""
        if not self.disabled:
            self.background["frameColor"] = self.normal_color
    
    def _on_mouse_down(self, button):
        """Handle mouse down event"""
        if not self.disabled:
            self.background["frameColor"] = self.click_color
    
    def _on_mouse_up(self, button):
        """Handle mouse up event"""
        if not self.disabled:
            if self.mouse_over:
                self.background["frameColor"] = self.hover_color
            else:
                self.background["frameColor"] = self.normal_color
    
    def set_text(self, text):
        """
        Set the button text
        
        Args:
            text: New text for the button
        """
        self.text = text
        self.text_node.setText(text)
    
    def get_text(self):
        """
        Get the button text
        
        Returns:
            Current button text
        """
        return self.text
    
    def set_text_color(self, color):
        """
        Set the text color
        
        Args:
            color: New text color (r, g, b, a)
        """
        self.text_color = Vec4(*color)
        self.text_node.setFg(self.text_color)
    
    def enable(self):
        """Enable the button"""
        self.disabled = False
        self.enable_mouse()
        self.background["frameColor"] = self.normal_color
    
    def disable(self):
        """Disable the button"""
        self.disabled = True
        self.disable_mouse()
        self.background["frameColor"] = self.disabled_color
    
    def is_disabled(self):
        """
        Check if the button is disabled
        
        Returns:
            True if disabled, False otherwise
        """
        return self.disabled
    
    def set_command(self, command):
        """
        Set the function to call when the button is clicked
        
        Args:
            command: Function to call
        """
        # Remove existing click callbacks
        self.callbacks["click"] = []
        
        # Add new command
        if command:
            self.add_callback("click", lambda btn: command())
    
    def cleanup(self):
        """Clean up resources"""
        # Base class cleanup
        super().cleanup() 