# src/engine/ui/menus/options_menu.py
import pygame
import math
import os
from typing import Callable, Dict, Any
from ..ui_base import Panel, Button, Slider, Label

class OptionsMenu:
    """
    Options menu with configurable game settings.
    """
    def __init__(self, width: int, height: int, on_save: Callable = None, on_cancel: Callable = None):
        self.width = width
        self.height = height
        self.on_save = on_save
        self.on_cancel = on_cancel
        
        # UI elements
        self.ui_elements = []
        self.buttons = []
        self.sliders = []
        self.labels = []
        
        # Settings
        self.settings = {
            'music_volume': 0.7,
            'sfx_volume': 0.8,
            'fullscreen': False,
            'vsync': True,
            'resolution_index': 1  # Default to 1280x720
        }
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Main panel
        panel_width = min(500, self.width - 40)
        panel_height = min(500, self.height - 40)
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        self.main_panel = Panel(
            x=panel_x,
            y=panel_y,
            width=panel_width,
            height=panel_height,
            color=(40, 40, 60, 200)
        )
        self.ui_elements.append(self.main_panel)
        
        # Title
        self.title_label = Label(
            x=panel_x + panel_width // 2,
            y=panel_y + 30,
            text="OPTIONS",
            font_size=36,
            color=(255, 255, 255),
            centered=True,
            width=150,  # Providing explicit width
            height=40   # Providing explicit height
        )
        self.labels.append(self.title_label)
        self.ui_elements.append(self.title_label)
        
        # Options content
        content_x = panel_x + 50
        content_y = panel_y + 80
        content_width = panel_width - 100
        content_height = 30
        content_spacing = 50
        
        # Music volume
        self.music_label = Label(
            x=content_x,
            y=content_y,
            text="Music Volume",
            font_size=24,
            color=(220, 220, 220),
            width=200,  # Add explicit width
            height=30   # Add explicit height
        )
        self.labels.append(self.music_label)
        self.ui_elements.append(self.music_label)
        
        self.music_slider = Slider(
            x=content_x,
            y=content_y + 30,
            width=content_width,
            height=20,
            value=self.settings['music_volume'],
            color=(60, 60, 100),
            handle_color=(180, 180, 220)
        )
        self.sliders.append(self.music_slider)
        self.ui_elements.append(self.music_slider)
        
        # SFX volume
        self.sfx_label = Label(
            x=content_x,
            y=content_y + content_spacing,
            text="SFX Volume",
            font_size=24,
            color=(220, 220, 220),
            width=200,  # Add explicit width
            height=30   # Add explicit height
        )
        self.labels.append(self.sfx_label)
        self.ui_elements.append(self.sfx_label)
        
        self.sfx_slider = Slider(
            x=content_x,
            y=content_y + content_spacing + 30,
            width=content_width,
            height=20,
            value=self.settings['sfx_volume'],
            color=(60, 60, 100),
            handle_color=(180, 180, 220)
        )
        self.sliders.append(self.sfx_slider)
        self.ui_elements.append(self.sfx_slider)
        
        # Fullscreen toggle
        self.fullscreen_btn = Button(
            x=content_x,
            y=content_y + content_spacing * 2,
            width=content_width,
            height=40,
            text=f"Fullscreen: {'On' if self.settings['fullscreen'] else 'Off'}",
            on_click=self._toggle_fullscreen
        )
        self.buttons.append(self.fullscreen_btn)
        self.ui_elements.append(self.fullscreen_btn)
        
        # V-Sync toggle
        self.vsync_btn = Button(
            x=content_x,
            y=content_y + content_spacing * 3,
            width=content_width,
            height=40,
            text=f"V-Sync: {'On' if self.settings['vsync'] else 'Off'}",
            on_click=self._toggle_vsync
        )
        self.buttons.append(self.vsync_btn)
        self.ui_elements.append(self.vsync_btn)
        
        # Save button
        button_width = 120
        button_height = 40
        button_y = panel_y + panel_height - 60
        
        self.save_btn = Button(
            x=panel_x + panel_width // 3 - button_width // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="Save",
            on_click=self._on_save_click
        )
        self.buttons.append(self.save_btn)
        self.ui_elements.append(self.save_btn)
        
        # Cancel button
        self.cancel_btn = Button(
            x=panel_x + panel_width * 2 // 3 - button_width // 2,
            y=button_y,
            width=button_width,
            height=button_height,
            text="Cancel",
            on_click=self._on_cancel_click
        )
        self.buttons.append(self.cancel_btn)
        self.ui_elements.append(self.cancel_btn)
        
    def update(self, dt):
        """Update menu logic."""
        # Update UI elements
        for ui_element in self.ui_elements:
            if hasattr(ui_element, 'update'):
                ui_element.update(dt)
                
        # Update settings from UI
        self.settings['music_volume'] = self.music_slider.value
        self.settings['sfx_volume'] = self.sfx_slider.value
        
    def draw(self, screen):
        """Draw the menu."""
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw UI elements
        for ui_element in self.ui_elements:
            ui_element.draw(screen)
            
    def handle_event(self, event):
        """Handle input events."""
        # Pass event to UI elements
        for ui_element in self.ui_elements:
            if hasattr(ui_element, 'handle_event') and ui_element.handle_event(event):
                return True
                
        return False
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen setting."""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.fullscreen_btn.text = f"Fullscreen: {'On' if self.settings['fullscreen'] else 'Off'}"
        
    def _toggle_vsync(self):
        """Toggle V-Sync setting."""
        self.settings['vsync'] = not self.settings['vsync']
        self.vsync_btn.text = f"V-Sync: {'On' if self.settings['vsync'] else 'Off'}"
        
    def _on_save_click(self):
        """Save settings and close menu."""
        print("Saving options:", self.settings)
        if self.on_save:
            self.on_save(self.settings)
            
    def _on_cancel_click(self):
        """Cancel without saving and close menu."""
        print("Cancelling options")
        if self.on_cancel:
            self.on_cancel() 