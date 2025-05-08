#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
InfoBoxUI Component for Nightfall Defenders
Provides collapsible information boxes for the UI
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from panda3d.core import TextNode, TransparencyAttrib, Vec4

class InfoBoxUI:
    """Collapsible information box for UI display"""
    
    def __init__(self, game, title, position, size=(0.4, 0.3), parent=None, expanded=True):
        """
        Initialize the info box
        
        Args:
            game: The game instance
            title: Title of the info box
            position: Position tuple (x, y) on screen
            size: Size tuple (width, height) of expanded box
            parent: Parent node (defaults to aspect2d)
            expanded: Whether box starts expanded or collapsed
        """
        self.game = game
        self.title = title
        self.position = position
        self.size = size
        self.expanded = expanded
        
        # Content items (labels, values, etc.)
        self.content_items = []
        
        # Create the parent node if none provided
        if parent is None:
            parent = game.aspect2d
        
        # Create the main frame
        self.frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.3, 0.8),
            frameSize=(-size[0]/2, size[0]/2, -size[1]/2, size[1]/2),
            pos=(position[0], 0, position[1]),
            parent=parent
        )
        
        # Title bar background
        title_height = 0.06
        self.title_bar = DirectFrame(
            frameColor=(0.3, 0.3, 0.4, 0.9),
            frameSize=(-size[0]/2, size[0]/2, -title_height/2, title_height/2),
            pos=(0, 0, size[1]/2 - title_height/2),
            parent=self.frame
        )
        
        # Title text
        self.title_label = DirectLabel(
            text=title,
            text_scale=0.04,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_pos=(-size[0]/2 + 0.05, -0.01),
            frameColor=(0, 0, 0, 0),
            parent=self.title_bar
        )
        
        # Collapse/expand button
        button_size = 0.03
        self.toggle_button = DirectButton(
            text="-" if expanded else "+",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.4, 0.4, 0.5, 0.9),
            frameSize=(-button_size, button_size, -button_size, button_size),
            relief=DGG.FLAT,
            pos=(size[0]/2 - 0.05, 0, 0),
            command=self.toggle_expanded,
            parent=self.title_bar
        )
        
        # Content area
        self.content_frame = DirectFrame(
            frameColor=(0, 0, 0, 0),  # Transparent
            frameSize=(-size[0]/2, size[0]/2, -size[1]/2 + title_height, 0),
            pos=(0, 0, size[1]/2 - title_height),
            parent=self.frame
        )
        
        # Update initial state
        if not expanded:
            self.collapse()
    
    def toggle_expanded(self):
        """Toggle between expanded and collapsed states"""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self):
        """Expand the info box"""
        self.expanded = True
        self.toggle_button["text"] = "-"
        
        # Restore full size
        self.frame["frameSize"] = (-self.size[0]/2, self.size[0]/2, 
                                   -self.size[1]/2, self.size[1]/2)
        
        # Show content
        self.content_frame.show()
    
    def collapse(self):
        """Collapse the info box to just the title bar"""
        self.expanded = False
        self.toggle_button["text"] = "+"
        
        # Adjust frame size to just title bar
        title_height = 0.06
        self.frame["frameSize"] = (-self.size[0]/2, self.size[0]/2, 
                                    self.size[1]/2 - title_height, self.size[1]/2)
        
        # Hide content
        self.content_frame.hide()
    
    def add_text_row(self, label_text, value_text="", row_index=None):
        """
        Add a row with label and value text
        
        Args:
            label_text: Label text
            value_text: Value text (can be empty)
            row_index: Row index (auto if None)
            
        Returns:
            tuple: (label, value) DirectLabel objects
        """
        # Calculate row index if not provided
        if row_index is None:
            row_index = len(self.content_items)
        
        # Calculate position
        row_height = 0.05
        y_pos = -row_index * row_height - 0.03
        
        # Create label
        label = DirectLabel(
            text=label_text,
            text_scale=0.035,
            text_align=TextNode.ALeft,
            text_fg=(0.9, 0.9, 0.9, 1),
            frameColor=(0, 0, 0, 0),
            pos=(-self.size[0]/2 + 0.05, 0, y_pos),
            parent=self.content_frame
        )
        
        # Create value
        value = DirectLabel(
            text=value_text,
            text_scale=0.035,
            text_align=TextNode.ARight,
            text_fg=(1, 1, 0.8, 1),
            frameColor=(0, 0, 0, 0),
            pos=(self.size[0]/2 - 0.05, 0, y_pos),
            parent=self.content_frame
        )
        
        # Add to content items
        item = (label, value)
        
        if row_index >= len(self.content_items):
            self.content_items.append(item)
        else:
            # Remove old items at this position
            old_items = self.content_items[row_index]
            for old_item in old_items:
                old_item.destroy()
            
            # Add new items
            self.content_items[row_index] = item
        
        return item
    
    def update_value(self, row_index, new_value):
        """
        Update the value text for a specific row
        
        Args:
            row_index: Row index to update
            new_value: New value text
        """
        if 0 <= row_index < len(self.content_items):
            _, value_label = self.content_items[row_index]
            value_label["text"] = str(new_value)
    
    def clear(self):
        """Clear all content items"""
        for label, value in self.content_items:
            label.destroy()
            value.destroy()
        
        self.content_items = []
    
    def show(self):
        """Show the info box"""
        self.frame.show()
    
    def hide(self):
        """Hide the info box"""
        self.frame.hide()
    
    def destroy(self):
        """Clean up resources"""
        self.clear()
        self.frame.destroy() 