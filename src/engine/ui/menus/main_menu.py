# src/engine/ui/menus/main_menu.py
import pygame
import os
import math
from typing import Dict, List, Callable

from ..ui_base import UIElement, Button, Panel, Label

# Create a simple placeholder for EffectSystem to avoid OpenGL dependency
class SimpleFxSystem:
    """Simple placeholder for EffectSystem to avoid OpenGL requirements"""
    def __init__(self):
        self.particles = []
        
    def add_particle(self, position, velocity, color, life=1.0, size=5):
        self.particles.append({
            'position': position,
            'velocity': velocity,
            'color': color,
            'life': life,
            'size': size
        })
        
    def update(self, dt):
        # Simple update for particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Update position
            particle['position'] = (
                particle['position'][0] + particle['velocity'][0] * dt,
                particle['position'][1] + particle['velocity'][1] * dt
            )
            
    def render(self, surface):
        # Draw particles as simple circles
        for particle in self.particles:
            size = int(particle['size'] * (particle['life'] / 1.0))
            alpha = int(255 * (particle['life'] / 1.0))
            color = (
                particle['color'][0],
                particle['color'][1],
                particle['color'][2],
                alpha
            )
            pos = (int(particle['position'][0]), int(particle['position'][1]))
            
            # Create a small surface for the particle
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            
            # Blit to the main surface
            surface.blit(particle_surface, (pos[0]-size, pos[1]-size))

class MainMenu:
    """
    Main menu for the game with Octopath-inspired styling.
    Provides options for New Game, Load Game, Options, Credits, and Quit.
    """
    def __init__(self, width: int, height: int, on_start_game: Callable = None, on_load_game: Callable = None, 
                 on_options: Callable = None, on_credits: Callable = None, on_quit: Callable = None):
        """
        Initialize the main menu.
        
        Args:
            width (int): Screen width.
            height (int): Screen height.
            on_start_game (callable): Callback when 'New Game' is selected.
            on_load_game (callable): Callback when 'Load Game' is selected.
            on_options (callable): Callback when 'Options' is selected.
            on_credits (callable): Callback when 'Credits' is selected.
            on_quit (callable): Callback when 'Quit' is selected.
        """
        self.width = width
        self.height = height
        
        # Callbacks
        self.on_start_game = on_start_game
        self.on_load_game = on_load_game
        self.on_options = on_options
        self.on_credits = on_credits
        self.on_quit = on_quit
        
        # UI elements
        self.title_panel = None
        self.menu_panel = None
        self.buttons = []
        self.ui_elements = []
        
        # Background
        self.background = None
        self.background_overlay = None
        
        # Title
        self.title_font = None
        self.subtitle_font = None
        self.game_title = "Nightfall Defenders"
        self.game_subtitle = "An Octopath-Inspired Adventure"
        
        # Animation
        self.time = 0
        self.effect_system = None
        
        # Initialize UI
        self._init_ui()
        self._load_assets()
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Create fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.subtitle_font = pygame.font.SysFont(None, 36)
        
        # Create title panel
        self.title_panel = Panel(
            x=self.width // 2 - 300,
            y=self.height // 4 - 100,
            width=600,
            height=200,
            color=(0, 0, 0, 180)  # Semi-transparent black
        )
        
        # Create menu panel
        self.menu_panel = Panel(
            x=self.width // 2 - 150,
            y=self.height // 2,
            width=300,
            height=300,
            color=(0, 0, 0, 180)  # Semi-transparent black
        )
        
        # Create buttons
        button_width = 250
        button_height = 40
        button_x = self.width // 2 - button_width // 2
        button_y = self.height // 2 + 30
        button_spacing = 50
        
        # New Game button
        new_game_btn = Button(
            x=button_x,
            y=button_y,
            width=button_width,
            height=button_height,
            text="New Game",
            on_click=self._on_new_game_click
        )
        self.buttons.append(new_game_btn)
        
        # Load Game button
        load_game_btn = Button(
            x=button_x,
            y=button_y + button_spacing,
            width=button_width,
            height=button_height,
            text="Load Game",
            on_click=self._on_load_game_click
        )
        self.buttons.append(load_game_btn)
        
        # Options button
        options_btn = Button(
            x=button_x,
            y=button_y + 2 * button_spacing,
            width=button_width,
            height=button_height,
            text="Options",
            on_click=self._on_options_click
        )
        self.buttons.append(options_btn)
        
        # Credits button
        credits_btn = Button(
            x=button_x,
            y=button_y + 3 * button_spacing,
            width=button_width,
            height=button_height,
            text="Credits",
            on_click=self._on_credits_click
        )
        self.buttons.append(credits_btn)
        
        # Quit button
        quit_btn = Button(
            x=button_x,
            y=button_y + 4 * button_spacing,
            width=button_width,
            height=button_height,
            text="Quit",
            on_click=self._on_quit_click
        )
        self.buttons.append(quit_btn)
        
        # Add buttons to UI elements
        self.ui_elements = [self.title_panel, self.menu_panel] + self.buttons
        
        # Create the effects system
        try:
            # Try to import the real effect system
            from ...rendering.effect_system import EffectSystem
            self.effect_system = EffectSystem()
        except (ImportError, AttributeError, ModuleNotFoundError) as e:
            # If it fails, use our simple implementation
            print(f"Using simple effect system due to: {e}")
            self.effect_system = SimpleFxSystem()
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Error initializing effect system: {e}")
            self.effect_system = SimpleFxSystem()
        
    def _load_assets(self):
        """Load menu assets."""
        try:
            # Load background image
            bg_path = "assets/ui/main_menu_bg.png"
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.width, self.height))
            else:
                # Create a fallback background
                self.background = pygame.Surface((self.width, self.height))
                # Create a gradient background
                for y in range(self.height):
                    color_val = max(0, min(255, int(20 + (y / self.height) * 80)))
                    color = (color_val // 4, color_val // 3, color_val)
                    pygame.draw.line(self.background, color, (0, y), (self.width, y))
                    
            # Create background overlay for particles
            self.background_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        except Exception as e:
            print(f"Error loading menu assets: {e}")
            # Create fallback assets
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((20, 20, 40))
            self.background_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def update(self, dt):
        """
        Update menu logic.
        
        Args:
            dt (float): Time elapsed since last frame.
        """
        # Update time
        self.time += dt
        
        # Update button animations
        for button in self.buttons:
            button.update(dt)
            
        # Update background effects
        self._update_background_effects(dt)
        
    def _update_background_effects(self, dt):
        """Update background visual effects."""
        # Clear overlay
        self.background_overlay.fill((0, 0, 0, 0))
        
        # Add animated particles or effects
        for i in range(20):
            x = (self.width // 2) + math.sin(self.time + i * 0.5) * (self.width // 3)
            y = (self.height // 2) + math.cos(self.time + i * 0.5) * (self.height // 3)
            size = 2 + math.sin(self.time * 2 + i) * 2
            alpha = int(128 + 127 * math.sin(self.time + i * 0.2))
            pygame.draw.circle(self.background_overlay, (255, 255, 255, alpha), (int(x), int(y)), int(size))

    def draw(self, screen):
        """
        Draw the menu.
        
        Args:
            screen: The pygame screen to draw on.
        """
        # Draw background
        if self.background:
            screen.blit(self.background, (0, 0))
            
        # Draw background effects
        if self.background_overlay:
            screen.blit(self.background_overlay, (0, 0))
            
        # Draw UI panels
        self.title_panel.draw(screen)
        self.menu_panel.draw(screen)
        
        # Draw title
        title_surface = self.title_font.render(self.game_title, True, (255, 220, 180))
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4 - 50))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_surface = self.subtitle_font.render(self.game_subtitle, True, (220, 220, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, self.height // 4 + 10))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            bool: True if event was handled, False otherwise.
        """
        # Check if any button handled the event
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        return False
        
    def _on_new_game_click(self):
        """Handle New Game button click."""
        print("New Game clicked")
        if self.on_start_game:
            self.on_start_game()
            
    def _on_load_game_click(self):
        """Handle Load Game button click."""
        print("Load Game clicked")
        if self.on_load_game:
            self.on_load_game()
            
    def _on_options_click(self):
        """Handle Options button click."""
        print("Options clicked")
        if self.on_options:
            self.on_options()
            
    def _on_credits_click(self):
        """Handle Credits button click."""
        print("Credits clicked")
        if self.on_credits:
            self.on_credits()
            
    def _on_quit_click(self):
        """Handle Quit button click."""
        print("Quit clicked")
        if self.on_quit:
            self.on_quit()