# src/engine/rendering/world_renderer.py
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import os
import pygame
import math

# Try to import HD2DRenderer
try:
    from ..graphics.hd2d_renderer import HD2DRenderer
    HD2D_AVAILABLE = True
except ImportError:
    HD2D_AVAILABLE = False
    print("HD2DRenderer not available, using fallback rendering")

# Try to import OpenGL
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False

# Try to import subsystems with fallback dummies
try:
    from .water_system import WaterSystem
    WATER_SYSTEM_AVAILABLE = True
except ImportError:
    WATER_SYSTEM_AVAILABLE = False
    # Dummy WaterSystem class
    class WaterSystem:
        def __init__(self, resolution):
            self.width, self.height = resolution
        def update(self, delta_time):
            pass
        def render(self, camera_matrix):
            pass
        def cleanup(self):
            pass
    print("WaterSystem not available, using dummy implementation")

try:
    from .sky_system import SkySystem
    SKY_SYSTEM_AVAILABLE = True
except ImportError:
    SKY_SYSTEM_AVAILABLE = False
    # Dummy SkySystem class
    class SkySystem:
        def __init__(self):
            pass
        def update(self, delta_time):
            pass
        def render(self, camera_matrix):
            pass
        def cleanup(self):
            pass
    print("SkySystem not available, using dummy implementation")

try:
    from .effect_system import EffectSystem
    EFFECT_SYSTEM_AVAILABLE = True
except ImportError:
    EFFECT_SYSTEM_AVAILABLE = False
    # Dummy EffectSystem class
    class EffectSystem:
        def __init__(self):
            pass
        def update(self, delta_time):
            pass
        def render(self, camera_matrix):
            pass
        def cleanup(self):
            pass
    print("EffectSystem not available, using dummy implementation")

class WorldRenderer:
    """
    Renderer for the 3D world environment with HD-2D style graphics.
    """
    def __init__(self, resolution: Tuple[int, int], renderer=None):
        """
        Initialize the world renderer.
        
        Args:
            resolution (Tuple[int, int]): The rendering resolution (width, height).
            renderer: The main renderer object with OpenGL context info
        """
        self.width, self.height = resolution
        self.hd2d_renderer = None
        self.renderer = renderer  # Store reference to main renderer
        
        # Camera settings
        self.camera_position = np.array([0.0, 10.0, 10.0], dtype=float)  # Position behind and above player
        self.camera_target = np.array([0.0, 0.0, 0.0], dtype=float)      # Look at the center
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=float)          # Y is up
        
        # Environment settings
        self.terrain_scale = 1.0
        self.terrain_height_scale = 0.5
        
        # Lighting settings
        self.global_light_direction = np.array([0.5, -0.7, 0.5], dtype=float)
        self.global_light_color = np.array([1.0, 0.95, 0.8], dtype=float)
        self.ambient_light_color = np.array([0.3, 0.35, 0.4], dtype=float)
        
        # Time of day 
        self.time_of_day = 0.5  # 0.0-1.0 (0.0 = midnight, 0.5 = noon, 1.0 = midnight)
        
        # Weather effects
        self.weather_type = "clear"  # clear, rain, snow, fog
        self.weather_intensity = 0.0  # 0.0-1.0
        
        # Initialize the HD-2D renderer if available
        self._init_hd2d_renderer()
        
        # Create a fallback surface for software rendering
        self.fallback_surface = pygame.Surface(resolution)
        
        # Render targets and post-processing
        self.using_framebuffers = False
        self.main_fbo = 0
        self.temp_fbo = 0
        
        # Try to initialize framebuffers if OpenGL is available
        self._init_framebuffers(resolution)
        
        # Initialize subsystems
        # Pass renderer to subsystems for feature detection
        self.water_system = WaterSystem(resolution, self.renderer)
        self.sky_system = SkySystem(self.renderer)
        self.effect_system = EffectSystem()
        
        # Post-processing parameters
        self.bloom_intensity = 0.3
        self.dof_enabled = False
        self.dof_focus_distance = 10.0
        
    def _init_hd2d_renderer(self):
        """Initialize the HD-2D renderer."""
        if HD2D_AVAILABLE and OPENGL_AVAILABLE:
            try:
                self.hd2d_renderer = HD2DRenderer()
                print("HD-2D renderer initialized successfully")
            except Exception as e:
                print(f"Error initializing HD-2D renderer: {e}")
                self.hd2d_renderer = None
                
    def _init_framebuffers(self, resolution):
        """
        Initialize framebuffers for post-processing effects.
        
        Args:
            resolution (Tuple[int, int]): The framebuffer resolution.
        """
        if not OPENGL_AVAILABLE:
            print("OpenGL not available, disabling framebuffers")
            self.using_framebuffers = False
            return
            
        try:
            # Check if we can create framebuffers (function should exist AND be callable)
            if not bool(glGenFramebuffers):
                print("Framebuffers not supported, disabling post-processing")
                self.using_framebuffers = False
                return
                
            # Create main framebuffer
            self.main_fbo = glGenFramebuffers(1)
            
            # Create temp framebuffer for post-processing
            self.temp_fbo = glGenFramebuffers(1)
            
            # Set framebuffer flag
            self.using_framebuffers = True
            
            print("Framebuffers initialized successfully")
            
        except Exception as e:
            print(f"Error initializing framebuffers: {e}")
            self.using_framebuffers = False
                
    def render(self, camera_matrix=None):
        """
        Render the 3D world with HD-2D style graphics.
        
        Args:
            camera_matrix: The camera view-projection matrix.
        """
        if self.hd2d_renderer is None:
            # Use fallback rendering
            self._render_fallback()
            return
            
        try:
            # Begin scene rendering with framebuffers if available
            if self.using_framebuffers:
                glBindFramebuffer(GL_FRAMEBUFFER, self.main_fbo)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
            # Begin scene rendering
            self.hd2d_renderer.begin_scene(camera_matrix)
            
            # Render sky if available
            if hasattr(self.sky_system, 'render'):
                try:
                    self.sky_system.render(camera_matrix)
                except Exception as e:
                    print(f"Error rendering sky: {e}")
                
            # Render terrain
            self.hd2d_renderer.render_terrain()
            
            # Render structures (buildings, bridges, etc.)
            self.hd2d_renderer.render_structures()
            
            # Render vegetation (trees, bushes, grass)
            self.hd2d_renderer.render_vegetation()
            
            # Render water if available
            if hasattr(self.water_system, 'render'):
                try:
                    self.water_system.render(camera_matrix)
                except Exception as e:
                    print(f"Error rendering water: {e}")
                
            # Render particle effects if available
            if hasattr(self.effect_system, 'render'):
                try:
                    self.effect_system.render(camera_matrix)
                except Exception as e:
                    print(f"Error rendering effects: {e}")
                
            # End scene rendering
            self.hd2d_renderer.end_scene()
            
            # Apply post-processing if framebuffers are available
            if self.using_framebuffers:
                self._apply_post_processing()
                
                # Render to screen
                glBindFramebuffer(GL_FRAMEBUFFER, 0)
                self._blit_to_screen()
                
        except Exception as e:
            print(f"Error rendering world: {e}")
            self._render_fallback()
            
    def _render_fallback(self):
        """
        Render a simplified fallback world when HD-2D rendering is not available.
        """
        # Check if we can use the hd2d_renderer's fallback
        if self.hd2d_renderer and hasattr(self.hd2d_renderer, 'get_surface'):
            try:
                hd2d_surface = self.hd2d_renderer.get_surface(self.width, self.height)
                self.fallback_surface.blit(hd2d_surface, (0, 0))
                return
            except Exception as e:
                print(f"Error using HD2D fallback surface: {e}")
        
        # If HD2D fallback is not available, render our own
        # Clear the fallback surface
        self.fallback_surface.fill((50, 50, 80))
        
        # Render sky if available
        if hasattr(self.sky_system, 'get_surface') and callable(self.sky_system.get_surface):
            try:
                sky_surface = self.sky_system.get_surface()
                if sky_surface:
                    # Scale sky to match our surface size
                    sky_surface = pygame.transform.scale(sky_surface, 
                                                      (self.fallback_surface.get_width(),
                                                       self.fallback_surface.get_height()))
                    self.fallback_surface.blit(sky_surface, (0, 0))
            except Exception as e:
                print(f"Error rendering fallback sky: {e}")
        
        # Draw a grid to represent the ground
        grid_color = (70, 70, 100)
        grid_size = 50
        
        # Draw horizontal grid lines
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.fallback_surface, grid_color, (0, y), (self.width, y))
            
        # Draw vertical grid lines
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.fallback_surface, grid_color, (x, 0), (x, self.height))
            
        # Draw some placeholder terrain features
        # Hills
        pygame.draw.ellipse(
            self.fallback_surface,
            (60, 100, 60),
            (self.width // 4, self.height // 2, self.width // 2, self.height // 4)
        )
        
        # Water - render fallback water if available
        water_height = self.height // 4
        water_y = self.height - water_height
        
        if hasattr(self.water_system, 'get_surface') and callable(self.water_system.get_surface):
            try:
                water_surface = self.water_system.get_surface()
                if water_surface:
                    # Scale water to match the width and desired height
                    water_surface = pygame.transform.scale(water_surface, 
                                                        (self.width, water_height))
                    # Apply transparency
                    water_surface.set_alpha(180)
                    self.fallback_surface.blit(water_surface, (0, water_y))
                else:
                    # Fallback water rendering
                    pygame.draw.rect(
                        self.fallback_surface,
                        (40, 60, 150),
                        (0, water_y, self.width, water_height)
                    )
            except Exception as e:
                print(f"Error rendering fallback water: {e}")
        else:
            # Fallback water rendering
            pygame.draw.rect(
                self.fallback_surface,
                (40, 60, 150),
                (0, water_y, self.width, water_height)
            )
        
    def _apply_post_processing(self):
        """Apply post-processing effects to the rendered scene."""
        # This is a placeholder for actual post-processing implementation
        # In a real implementation, this would apply bloom, depth of field, etc.
        if not self.using_framebuffers:
            return
            
        try:
            # Ping-pong between framebuffers for multi-pass effects
            # Currently just a placeholder
            pass
        except Exception as e:
            print(f"Error applying post-processing: {e}")
            
    def _blit_to_screen(self):
        """Blit the final post-processed image to the screen."""
        if not self.using_framebuffers:
            return
            
        try:
            # In a real implementation, this would copy the framebuffer to the screen
            # with a full-screen quad and a simple shader
            pass
        except Exception as e:
            print(f"Error blitting to screen: {e}")
            
    def update(self, delta_time):
        """
        Update animations and effects.
        
        Args:
            delta_time (float): Time elapsed since last update.
        """
        # Update subsystems
        self.water_system.update(delta_time)
        self.sky_system.update(delta_time)
        self.effect_system.update(delta_time)
            
    def set_camera(self, position, target, up=None):
        """
        Set the camera position and orientation.
        
        Args:
            position: The camera position (x, y, z).
            target: The camera target point (x, y, z).
            up: The camera up vector (x, y, z). Defaults to (0, 1, 0).
        """
        self.camera_position = np.array(position, dtype=float)
        self.camera_target = np.array(target, dtype=float)
        
        if up is not None:
            self.camera_up = np.array(up, dtype=float)
            
    def set_time_of_day(self, time_value):
        """
        Set the time of day for lighting.
        
        Args:
            time_value (float): Value between 0.0 (midnight) and 1.0 (next midnight).
        """
        self.time_of_day = max(0.0, min(1.0, time_value))
        
        # Update lighting based on time of day
        self._update_lighting()
        
    def set_weather(self, weather_type, intensity=0.5):
        """
        Set the weather conditions.
        
        Args:
            weather_type (str): Weather type ("clear", "rain", "snow", "fog").
            intensity (float): Weather intensity from 0.0 to 1.0.
        """
        valid_types = ["clear", "rain", "snow", "fog"]
        if weather_type not in valid_types:
            print(f"Invalid weather type: {weather_type}. Using 'clear' instead.")
            weather_type = "clear"
            
        self.weather_type = weather_type
        self.weather_intensity = max(0.0, min(1.0, intensity))
        
    def _update_lighting(self):
        """Update lighting based on time of day and weather."""
        # Calculate sun position based on time of day
        # 0.25 = sunrise, 0.5 = noon, 0.75 = sunset
        angle = (self.time_of_day - 0.5) * math.pi * 2
        
        # Day/night cycle affects light direction and color
        if 0.25 <= self.time_of_day <= 0.75:  # Day time
            # Sun position moves across the sky
            self.global_light_direction = np.array([
                math.sin(angle),
                -math.cos(angle),
                0.5
            ], dtype=float)
            
            # Normalize the direction vector
            norm = np.linalg.norm(self.global_light_direction)
            if norm > 0:
                self.global_light_direction /= norm
                
            # Light color changes from orange at sunrise to white at noon to orange at sunset
            noon_factor = 1.0 - 2.0 * abs(self.time_of_day - 0.5)  # 0 at noon, 1 at sunrise/sunset
            
            # Interpolate between warm and neutral light
            self.global_light_color = np.array([
                1.0,  # Red stays constant
                0.8 + 0.15 * (1.0 - noon_factor),  # Green increases toward noon
                0.7 + 0.3 * (1.0 - noon_factor)    # Blue increases toward noon
            ], dtype=float)
            
            # Ambient light is brighter during the day
            self.ambient_light_color = np.array([
                0.2 + 0.1 * (1.0 - noon_factor),
                0.25 + 0.1 * (1.0 - noon_factor),
                0.3 + 0.1 * (1.0 - noon_factor)
            ], dtype=float)
            
        else:  # Night time
            # Moon light is from above
            self.global_light_direction = np.array([0.2, -0.9, 0.3], dtype=float)
            
            # Moonlight is dim and blue-ish
            self.global_light_color = np.array([0.6, 0.6, 0.8], dtype=float)
            
            # Ambient light is dark at night
            self.ambient_light_color = np.array([0.05, 0.05, 0.1], dtype=float)
            
        # Apply weather effects to lighting
        if self.weather_type != "clear":
            # Reduce light intensity based on weather
            reduction_factor = 1.0 - (0.3 * self.weather_intensity)
            self.global_light_color *= reduction_factor
            
            # Add fog for certain weather types
            if self.weather_type in ["rain", "fog"]:
                # Increase ambient light slightly to simulate diffusion
                ambient_increase = 0.05 * self.weather_intensity
                self.ambient_light_color += ambient_increase
                
                # For fog, reduce light further and add blue tint
                if self.weather_type == "fog":
                    self.global_light_color *= 0.8
                    # Add bluish tint to ambient light
                    self.ambient_light_color[2] += 0.1 * self.weather_intensity
                    
    def resize(self, width, height):
        """
        Handle resize events.
        
        Args:
            width (int): New viewport width.
            height (int): New viewport height.
        """
        self.width = width
        self.height = height
        
        # Update fallback surface
        self.fallback_surface = pygame.Surface((width, height))
        
        # Re-initialize framebuffers if needed
        if self.using_framebuffers:
            # Delete old framebuffers
            if self.main_fbo:
                glDeleteFramebuffers(1, [self.main_fbo])
            if self.temp_fbo:
                glDeleteFramebuffers(1, [self.temp_fbo])
                
            # Create new framebuffers
            self._init_framebuffers((width, height))
            
    def cleanup(self):
        """Clean up renderer resources."""
        if self.hd2d_renderer:
            self.hd2d_renderer.cleanup()
            
        # Clean up framebuffers
        if self.using_framebuffers:
            if self.main_fbo:
                glDeleteFramebuffers(1, [self.main_fbo])
            if self.temp_fbo:
                glDeleteFramebuffers(1, [self.temp_fbo])
        
        # Clean up subsystems
        self.water_system.cleanup()
        self.sky_system.cleanup()
        self.effect_system.cleanup()