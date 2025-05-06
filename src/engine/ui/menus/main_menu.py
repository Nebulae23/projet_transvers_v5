# src/engine/ui/menus/main_menu.py
import pygame
import os
import math
import random
from typing import Dict, List, Callable

from ..ui_base import UIElement, Button, Panel, Label, get_ui_renderer, UIEvent, UIEventType

# Try to import OpenGL
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for MainMenu, using fallback rendering")

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
        # Debug flag - set to True to see UI rendering debug info
        self.debug = False
        
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
        self.background_texture = 0  # OpenGL texture ID
        
        # Title
        self.title_font = None
        self.subtitle_font = None
        self.title_texture = 0  # OpenGL texture ID
        self.subtitle_texture = 0  # OpenGL texture ID
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
            color=(60, 60, 100, 220),  # Semi-transparent dark blue
            hover_color=(80, 80, 140, 240),  # Semi-transparent brighter blue when hovered
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
            color=(60, 60, 100, 220),
            hover_color=(80, 80, 140, 240),
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
            color=(60, 60, 100, 220),
            hover_color=(80, 80, 140, 240),
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
            color=(60, 60, 100, 220),
            hover_color=(80, 80, 140, 240),
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
            color=(60, 60, 100, 220),
            hover_color=(80, 80, 140, 240),
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
            # Get UI renderer
            renderer = get_ui_renderer(self.width, self.height)
            
            # Load background image
            bg_path = "assets/ui/main_menu_bg.png"
            if os.path.exists(bg_path):
                # For PyGame fallback
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.width, self.height))
                
                # For OpenGL
                if OPENGL_AVAILABLE and renderer is not None:
                    self.background_texture, _, _ = renderer.load_image(bg_path)
                    if self.debug:
                        print(f"Loaded background texture: {self.background_texture}")
            else:
                # Create a fallback background
                self.background = pygame.Surface((self.width, self.height))
                # Create a gradient background
                for y in range(self.height):
                    color_val = max(0, min(255, int(20 + (y / self.height) * 80)))
                    color = (color_val // 4, color_val // 3, color_val)
                    pygame.draw.line(self.background, color, (0, y), (self.width, y))
                
                # For OpenGL, create a texture from this surface
                if OPENGL_AVAILABLE and renderer is not None:
                    self.background_texture = renderer.create_texture_from_surface(self.background)
                    
            # Create background overlay for particles
            self.background_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create title and subtitle textures for OpenGL
            if OPENGL_AVAILABLE and renderer is not None:
                # Title
                title_surface = self.title_font.render(self.game_title, True, (255, 215, 0))  # Gold color
                self.title_texture = renderer.create_texture_from_surface(title_surface)
                self.title_width, self.title_height = title_surface.get_size()
                
                # Subtitle
                subtitle_surface = self.subtitle_font.render(self.game_subtitle, True, (230, 230, 230))
                self.subtitle_texture = renderer.create_texture_from_surface(subtitle_surface)
                self.subtitle_width, self.subtitle_height = subtitle_surface.get_size()
                
            if self.debug:
                print(f"Assets loaded. Background texture: {self.background_texture}, Title: {self.title_texture}")
                
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
            
        # Add particles or other effects
        self._update_background_effects(dt)
        
        # Update effects system
        if self.effect_system:
            self.effect_system.update(dt)
        
    def _update_background_effects(self, dt):
        """Add and update particle effects on the background."""
        if self.effect_system and hasattr(self.effect_system, 'add_particle'):
            # Add particles occasionally
            if random.random() < 0.05:
                # Create a particle at a random position
                pos_x = random.randint(0, self.width)
                pos_y = random.randint(0, self.height)
                
                # Create a random velocity
                vel_x = random.uniform(-10, 10)
                vel_y = random.uniform(-10, 10)
                
                # Create a random color
                color = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(200, 255),
                    random.randint(50, 150)
                )
                
                # Add the particle
                self.effect_system.add_particle(
                    position=(pos_x, pos_y),
                    velocity=(vel_x, vel_y),
                    color=color,
                    life=random.uniform(0.5, 2.0),
                    size=random.randint(2, 8)
                )

    def draw(self, screen):
        """
        Draw the menu.
        
        Args:
            screen: The pygame surface to draw on, or the screen for OpenGL context.
        """
        if self.debug:
            print("Drawing main menu")
            
        # Get UI renderer
        renderer = get_ui_renderer(self.width, self.height)
        using_opengl = OPENGL_AVAILABLE and renderer is not None
        
        if self.debug:
            print(f"Main menu rendering - Using OpenGL: {using_opengl}, Screen size: {self.width}x{self.height}")
            if using_opengl:
                print(f"Background texture: {self.background_texture}, Title texture: {self.title_texture}")
            
        # Draw background
        if using_opengl:
            if self.background_texture:
                renderer.draw_texture(
                    self.background_texture, 
                    0, 0, 
                    self.width, self.height
                )
                if self.debug:
                    print(f"Drew background with OpenGL, texture: {self.background_texture}")
            else:
                # Draw a solid color rectangle as background if texture not available
                renderer.draw_rectangle(
                    0, 0, 
                    self.width, self.height,
                    (20, 20, 40, 255)  # Dark blue background
                )
                if self.debug:
                    print("Drew solid color background with OpenGL (no texture)")
        else:
            # PyGame fallback
            if self.background:
                screen.blit(self.background, (0, 0))
            if self.debug:
                print("Drew background with PyGame")
            else:
                screen.fill((20, 20, 40))
                if self.debug:
                    print("Drew solid color background with PyGame")
            
        # Draw title panel
        self.title_panel.draw(screen)
        
        # Draw menu panel
        self.menu_panel.draw(screen)
        
        # Draw title and subtitle
        if using_opengl:
            # Draw with OpenGL
            if self.title_texture:
                title_x = self.width // 2 - self.title_width // 2
                title_y = self.height // 4 - self.title_height // 2 - 30
                renderer.draw_texture(
                    self.title_texture,
                    title_x, title_y,
                    self.title_width, self.title_height
                )
                
            if self.subtitle_texture:
                subtitle_x = self.width // 2 - self.subtitle_width // 2
                subtitle_y = self.height // 4 + self.title_height // 2
                renderer.draw_texture(
                    self.subtitle_texture,
                    subtitle_x, subtitle_y,
                    self.subtitle_width, self.subtitle_height
                )
        else:
            # PyGame fallback
            title_surface = self.title_font.render(self.game_title, True, (255, 215, 0))
            subtitle_surface = self.subtitle_font.render(self.game_subtitle, True, (230, 230, 230))
            
            title_x = self.width // 2 - title_surface.get_width() // 2
            title_y = self.height // 4 - title_surface.get_height() // 2 - 30
            
            subtitle_x = self.width // 2 - subtitle_surface.get_width() // 2
            subtitle_y = self.height // 4 + title_surface.get_height() // 2
            
            screen.blit(title_surface, (title_x, title_y))
            screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
        # Draw particle effects
        if hasattr(self.effect_system, 'render'):
            if using_opengl:
                # OpenGL rendering for particles would go here
                # This would require extending the effect system for OpenGL
                pass
            else:
                # PyGame fallback for particles
                self.background_overlay.fill((0, 0, 0, 0))  # Clear overlay
                self.effect_system.render(self.background_overlay)
                screen.blit(self.background_overlay, (0, 0))
            
    def handle_event(self, event):
        """
        Handle menu events.
        
        Args:
            event: The pygame event to handle.
        """
        # Convert pygame event to UI event
        if event.type == pygame.MOUSEMOTION:
            ui_event_data = {
                "x": event.pos[0],
                "y": event.pos[1]
            }
            ui_event = UIEvent(UIEventType.MOUSE_MOTION, ui_event_data)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            ui_event_data = {
                "x": event.pos[0],
                "y": event.pos[1],
                "button": event.button
            }
            ui_event = UIEvent(UIEventType.MOUSE_BUTTON_DOWN, ui_event_data)
            
        elif event.type == pygame.MOUSEBUTTONUP:
            ui_event_data = {
                "x": event.pos[0],
                "y": event.pos[1],
                "button": event.button
            }
            ui_event = UIEvent(UIEventType.MOUSE_BUTTON_UP, ui_event_data)
            
        else:
            # Ignore other event types
            return False
        
        # Dispatch event to buttons
        for button in self.buttons:
            if button.handle_event(ui_event):
                return True
                
        return False
        
    def _on_new_game_click(self):
        """Handle New Game button click."""
        if self.debug:
            print("New Game clicked")
        if self.on_start_game:
            self.on_start_game()
            
    def _on_load_game_click(self):
        """Handle Load Game button click."""
        if self.debug:
            print("Load Game clicked")
        if self.on_load_game:
            self.on_load_game()
            
    def _on_options_click(self):
        """Handle Options button click."""
        if self.debug:
            print("Options clicked")
        if self.on_options:
            self.on_options()
            
    def _on_credits_click(self):
        """Handle Credits button click."""
        if self.debug:
            print("Credits clicked")
        if self.on_credits:
            self.on_credits()
            
    def _on_quit_click(self):
        """Handle Quit button click."""
        if self.debug:
            print("Quit clicked")
        if self.on_quit:
            self.on_quit()