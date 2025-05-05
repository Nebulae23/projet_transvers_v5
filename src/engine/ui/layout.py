# src/engine/ui/layout.py
from typing import Tuple, List, Optional
from enum import Enum
from .ui_base import UIElement

class LayoutType(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"

class Layout:
    def __init__(self, 
                 container: UIElement,
                 layout_type: LayoutType,
                 padding: int = 10,
                 spacing: int = 5):
        self.container = container
        self.layout_type = layout_type
        self.padding = padding
        self.spacing = spacing
        
    def arrange(self):
        if self.layout_type == LayoutType.VERTICAL:
            self._arrange_vertical()
        elif self.layout_type == LayoutType.HORIZONTAL:
            self._arrange_horizontal()
        elif self.layout_type == LayoutType.GRID:
            self._arrange_grid()
            
    def _arrange_vertical(self):
        current_y = self.container.position[1] + self.padding
        for child in self.container.children:
            child.set_position((
                self.container.position[0] + self.padding,
                current_y
            ))
            current_y += child.size[1] + self.spacing
            
    def _arrange_horizontal(self):
        current_x = self.container.position[0] + self.padding
        for child in self.container.children:
            child.set_position((
                current_x,
                self.container.position[1] + self.padding
            ))
            current_x += child.size[0] + self.spacing
            
    def _arrange_grid(self, columns: int = 4):
        current_x = self.container.position[0] + self.padding
        current_y = self.container.position[1] + self.padding
        col_count = 0
        
        max_width = (self.container.size[0] - 2 * self.padding -
                    (columns - 1) * self.spacing) // columns
                    
        for child in self.container.children:
            child.set_position((current_x, current_y))
            
            col_count += 1
            if col_count >= columns:
                col_count = 0
                current_x = self.container.position[0] + self.padding
                current_y += max_width + self.spacing
            else:
                current_x += max_width + self.spacing

class DockLayout:
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        
    def dock(self, element: UIElement, position: str):
        if position == "top":
            element.set_position((0, 0))
        elif position == "bottom":
            element.set_position((0, self.screen_size[1] - element.size[1]))
        elif position == "left":
            element.set_position((0, 0))
        elif position == "right":
            element.set_position((self.screen_size[0] - element.size[0], 0))
        elif position == "center":
            element.set_position((
                self.screen_size[0]//2 - element.size[0]//2,
                self.screen_size[1]//2 - element.size[1]//2
            ))