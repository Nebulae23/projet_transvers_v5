# src/engine/systems/tutorial_ui.py
from typing import Optional
import pygame
import pygame.freetype
from dataclasses import dataclass
from ..ui.ui_base import UIElement, UIManager
from ..graphics.hd2d_renderer import HD2DRenderer

@dataclass
class TutorialPopup:
    title: str
    description: str
    target_element: str
    position: tuple[float, float]
    size: tuple[float, float]
    alpha: float = 1.0
    
class TutorialUI:
    def __init__(self, ui_manager: UIManager, hd2d_renderer: HD2DRenderer):
        self.ui_manager = ui_manager
        self.renderer = hd2d_renderer
        self.current_popup: Optional[TutorialPopup] = None
        self.font = pygame.freetype.Font("assets/fonts/main.ttf", 16)
        
        # HD-2D style settings
        self.popup_style = {
            "background_color": (20, 20, 30, 200),
            "border_color": (255, 215, 0, 255),
            "text_color": (255, 255, 255, 255),
            "highlight_color": (100, 149, 237, 255)
        }
        
        # Animation parameters
        self.animation_duration = 0.5
        self.animation_timer = 0.0
        self.target_alpha = 1.0
        
    def show_tutorial_popup(self, title: str, description: str, target_element: str):
        # Calculate optimal position based on target element
        target_pos = self.ui_manager.get_element_position(target_element)
        screen_size = self.ui_manager.get_screen_size()
        
        popup_size = (300, 200)
        popup_pos = self._calculate_popup_position(target_pos, popup_size, screen_size)
        
        self.current_popup = TutorialPopup(
            title=title,
            description=description,
            target_element=target_element,
            position=popup_pos,
            size=popup_size,
            alpha=0.0
        )
        
        self.animation_timer = 0.0
        self.target_alpha = 1.0
        
    def hide_tutorial_popup(self):
        if self.current_popup:
            self.target_alpha = 0.0
            self.animation_timer = 0.0
            
    def update(self, dt: float):
        if not self.current_popup:
            return
            
        # Update animation
        if self.animation_timer < self.animation_duration:
            self.animation_timer += dt
            progress = min(1.0, self.animation_timer / self.animation_duration)
            
            current_alpha = self.current_popup.alpha
            target_alpha = self.target_alpha
            self.current_popup.alpha = current_alpha + (target_alpha - current_alpha) * progress
            
            if progress >= 1.0 and self.target_alpha == 0.0:
                self.current_popup = None
                
    def render(self, surface: pygame.Surface):
        if not self.current_popup:
            return
            
        # Create popup surface with HD-2D effects
        popup_surface = pygame.Surface(self.current_popup.size, pygame.SRCALPHA)
        
        # Draw background with HD-2D style
        self.renderer.draw_panel_2d(
            popup_surface,
            (0, 0),
            self.current_popup.size,
            self.popup_style["background_color"],
            self.popup_style["border_color"],
            self.current_popup.alpha
        )
        
        # Draw title
        title_surface, _ = self.font.render(
            self.current_popup.title,
            self.popup_style["text_color"]
        )
        popup_surface.blit(title_surface, (10, 10))
        
        # Draw description with word wrap
        desc_lines = self._wrap_text(
            self.current_popup.description,
            self.current_popup.size[0] - 20
        )
        
        for i, line in enumerate(desc_lines):
            line_surface, _ = self.font.render(
                line,
                self.popup_style["text_color"]
            )
            popup_surface.blit(line_surface, (10, 40 + i * 20))
            
        # Draw highlight arrow pointing to target element
        self._draw_target_arrow(popup_surface)
        
        # Apply HD-2D post-processing effects
        self.renderer.apply_hd2d_effects(popup_surface)
        
        # Draw to main surface
        surface.blit(
            popup_surface,
            self.current_popup.position,
            special_flags=pygame.BLEND_ALPHA_SDL2
        )
        
    def _calculate_popup_position(self, target_pos: tuple[float, float],
                                popup_size: tuple[float, float],
                                screen_size: tuple[float, float]) -> tuple[float, float]:
        x, y = target_pos
        w, h = popup_size
        screen_w, screen_h = screen_size
        
        # Try to position popup to the right of target
        if x + w + 20 < screen_w:
            popup_x = x + 20
        # Otherwise, try left side
        else:
            popup_x = x - w - 20
            
        # Try to center vertically with target
        popup_y = y - h/2
        # Clamp to screen bounds
        popup_y = max(10, min(screen_h - h - 10, popup_y))
        
        return (popup_x, popup_y)
        
    def _wrap_text(self, text: str, max_width: float) -> list[str]:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface, _ = self.font.render(test_line, (0, 0, 0))
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def _draw_target_arrow(self, surface: pygame.Surface):
        if not self.current_popup:
            return
            
        target_pos = self.ui_manager.get_element_position(self.current_popup.target_element)
        popup_center = (
            self.current_popup.position[0] + self.current_popup.size[0]/2,
            self.current_popup.position[1] + self.current_popup.size[1]/2
        )
        
        # Calculate arrow direction
        dx = target_pos[0] - popup_center[0]
        dy = target_pos[1] - popup_center[1]
        
        # Draw arrow with HD-2D glow effect
        self.renderer.draw_arrow_2d(
            surface,
            popup_center,
            (dx, dy),
            self.popup_style["highlight_color"],
            self.current_popup.alpha
        )