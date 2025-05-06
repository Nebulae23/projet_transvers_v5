# src/engine/rendering/sky_system.py
from typing import Optional, Dict
import numpy as np
import pygame
import sys

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    import glm
    import noise
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for SkySystem, using fallback")

class SkySystem:
    def __init__(self, renderer=None):
        # Fallback surface for software rendering
        self.fallback_surface = pygame.Surface((800, 600))  # Default size
        self.fallback_surface.fill((135, 206, 235))  # Sky blue
        
        # Check if OpenGL and shaders are available
        self.using_gl = False
        self.shaders_available = False
        
        if renderer and hasattr(renderer, 'has_feature'):
            self.shaders_available = renderer.has_feature('shaders')
            self.using_gl = renderer.gl_context and renderer.gl_context.active
        else:
            # Legacy check for OpenGL and shader availability
            self.using_gl = OPENGL_AVAILABLE
            self.shaders_available = self._check_shader_support()
        
        # Cloud parameters
        self.cloud_coverage = 0.5
        self.cloud_density = 0.6
        self.cloud_speed = 0.02
        
        # Atmosphere parameters
        self.rayleigh_scattering = 0.0025
        self.mie_scattering = 0.0010
        self.atmosphere_height = 8000.0
        
        # Time of day
        self.time_of_day = 0.0  # 0-1 range
        self.sun_position = (0, 1, 0) if not OPENGL_AVAILABLE else glm.vec3(0, 1, 0)
        
        # Weather state
        self.weather_state = "clear"
        self.weather_transition = 0.0
        
        # Aurora parameters
        self.aurora_active = False
        self.aurora_intensity = 0.0
        self.aurora_color = (0.1, 0.8, 0.3) if not OPENGL_AVAILABLE else glm.vec3(0.1, 0.8, 0.3)
        
        # Skip OpenGL initialization if not available or shaders not supported
        if not self.using_gl or not self.shaders_available:
            print(f"Using fallback sky rendering: " + 
                 ("OpenGL not available" if not self.using_gl else "Shaders not supported"))
            self.sky_shader = 0
            self.cloud_shader = 0
            self.aurora_shader = 0
            self.cloud_texture = 0
            return
            
        try:
            # Initialize shaders
            self.sky_shader = self._create_sky_shader()
            if not self.sky_shader:
                raise Exception("Failed to create sky shader")
                
            self.cloud_shader = self._create_cloud_shader()
            if not self.cloud_shader:
                raise Exception("Failed to create cloud shader")
                
            self.aurora_shader = self._create_aurora_shader()
            if not self.aurora_shader:
                raise Exception("Failed to create aurora shader")
            
            # Create volumetric texture for clouds
            self.cloud_texture = self._create_cloud_texture()
            if not self.cloud_texture:
                raise Exception("Failed to create cloud texture")
                
            print("Sky system initialized with OpenGL rendering")
        except Exception as e:
            print(f"Error initializing SkySystem with OpenGL: {e}")
            self.using_gl = False
            self.sky_shader = 0
            self.cloud_shader = 0
            self.aurora_shader = 0
            self.cloud_texture = 0
    
    def _check_shader_support(self):
        """Check if shader support is available using direct function checks"""
        if not OPENGL_AVAILABLE:
            return False
            
        try:
            return bool(glCreateShader) and bool(glShaderSource) and bool(glCompileShader)
        except (AttributeError, TypeError):
            return False
        
    def update(self, delta_time: float) -> None:
        # Update time of day
        self.time_of_day += delta_time * 0.001
        if self.time_of_day >= 1.0:
            self.time_of_day = 0.0
            
        # Update sun position
        self._update_sun_position()
        
        # Update fallback if not using OpenGL
        if not self.using_gl or not self.shaders_available:
            self._update_fallback(delta_time)
            return
            
        try:
            # Update clouds
            self._update_clouds(delta_time)
            
            # Update aurora if active
            if self.aurora_active:
                self._update_aurora(delta_time)
                
            # Update weather transitions
            self._update_weather(delta_time)
        except Exception as e:
            print(f"Error updating SkySystem: {e}")
            
    def render(self, camera_matrix: np.ndarray = None) -> None:
        if not self.using_gl or not self.shaders_available:
            return  # Render is handled by getting the fallback surface
            
        try:
            # 1. Render sky dome
            glUseProgram(self.sky_shader)
            self._update_sky_uniforms(camera_matrix)
            self._render_sky_dome()
            
            # 2. Render volumetric clouds
            glUseProgram(self.cloud_shader)
            self._update_cloud_uniforms(camera_matrix)
            self._render_clouds()
            
            # 3. Render aurora if active
            if self.aurora_active:
                glUseProgram(self.aurora_shader)
                self._update_aurora_uniforms(camera_matrix)
                self._render_aurora()
        except Exception as e:
            print(f"Error rendering SkySystem: {e}")
            
    def get_surface(self):
        """Get the sky rendering surface for fallback mode."""
        return self.fallback_surface
        
    def start_aurora(self) -> None:
        self.aurora_active = True
        self.aurora_intensity = 0.0
        
    def set_weather(self, weather: str) -> None:
        if weather in ["clear", "cloudy", "storm"]:
            self.weather_state = weather
            self.weather_transition = 0.0
    
    def _update_fallback(self, delta_time: float) -> None:
        """Update the fallback rendering surface based on time of day."""
        # Set sky color based on time of day
        if self.time_of_day < 0.25:  # Night
            sky_color = (20, 20, 50)
        elif self.time_of_day < 0.3:  # Dawn
            t = (self.time_of_day - 0.25) / 0.05
            sky_color = (
                int(20 + t * (135 - 20)),
                int(20 + t * (206 - 20)),
                int(50 + t * (235 - 50))
            )
        elif self.time_of_day < 0.7:  # Day
            sky_color = (135, 206, 235)
        elif self.time_of_day < 0.75:  # Dusk
            t = (self.time_of_day - 0.7) / 0.05
            sky_color = (
                int(135 + t * (255 - 135)),
                int(206 + t * (100 - 206)),
                int(235 + t * (50 - 235))
            )
        elif self.time_of_day < 0.8:  # Sunset
            t = (self.time_of_day - 0.75) / 0.05
            sky_color = (
                int(255 - t * (255 - 20)),
                int(100 - t * (100 - 20)),
                int(50 - t * (50 - 20))
            )
        else:  # Night
            sky_color = (20, 20, 50)
            
        # Fill the surface with the base sky color
        self.fallback_surface.fill(sky_color)
        
        # Add sun/moon
        sun_x = int(self.fallback_surface.get_width() * self.time_of_day)
        sun_y = int(self.fallback_surface.get_height() * 0.5 * (1 - abs(2 * self.time_of_day - 1)))
        
        if self.time_of_day > 0.25 and self.time_of_day < 0.75:
            # Sun
            pygame.draw.circle(self.fallback_surface, (255, 255, 200), (sun_x, sun_y), 30)
        else:
            # Moon
            pygame.draw.circle(self.fallback_surface, (240, 240, 240), (sun_x, sun_y), 20)
            
        # Add clouds based on weather state
        if self.weather_state in ["cloudy", "storm"]:
            cloud_count = 10 if self.weather_state == "cloudy" else 20
            for i in range(cloud_count):
                cloud_x = (i * 100 + int(self.time_of_day * 100)) % self.fallback_surface.get_width()
                cloud_y = 100 + (i * 20) % 100
                cloud_width = 100 + (i * 30) % 100
                cloud_height = 30 + (i * 10) % 20
                
                if self.weather_state == "cloudy":
                    cloud_color = (200, 200, 200)
                else:
                    cloud_color = (80, 80, 80)
                    
                pygame.draw.ellipse(self.fallback_surface, cloud_color, 
                                  (cloud_x, cloud_y, cloud_width, cloud_height))
                
    def _create_cloud_texture(self) -> int:
        if not self.using_gl:
            return 0
            
        try:
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_3D, texture)
            
            # Generate 3D Perlin noise for base cloud shape
            size = 128
            data = np.zeros((size, size, size), dtype=np.float32)
            
            for x in range(size):
                for y in range(size):
                    for z in range(size):
                        # Multiple octaves of noise
                        value = noise.pnoise3(x/50, y/50, z/50, octaves=4)
                        value += noise.pnoise3(x/25, y/25, z/25, octaves=2) * 0.5
                        data[x,y,z] = (value + 1) * 0.5
                        
            glTexImage3D(GL_TEXTURE_3D, 0, GL_R32F, size, size, size, 0,
                        GL_RED, GL_FLOAT, data)
            
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            return texture
        except Exception as e:
            print(f"Error creating cloud texture: {e}")
            return 0
        
    def _update_sun_position(self) -> None:
        # Calculate sun position based on time of day
        angle = self.time_of_day * 2 * np.pi
        if self.using_gl:
            self.sun_position = glm.vec3(
                np.cos(angle),
                np.sin(angle),
                0.0
            )
        else:
            self.sun_position = (
                np.cos(angle),
                np.sin(angle),
                0.0
            )
            
    def _create_sky_shader(self) -> int:
        # This would be implemented to create a sky shader
        if not self.using_gl:
            return 0
            
        try:
            # Placeholder - would need actual shader creation code
            return 1
        except Exception as e:
            print(f"Error creating sky shader: {e}")
            return 0
            
    def _create_cloud_shader(self) -> int:
        # This would be implemented to create a cloud shader
        if not self.using_gl:
            return 0
            
        try:
            # Placeholder - would need actual shader creation code
            return 1
        except Exception as e:
            print(f"Error creating cloud shader: {e}")
            return 0
            
    def _create_aurora_shader(self) -> int:
        # This would be implemented to create an aurora shader
        if not self.using_gl:
            return 0
            
        try:
            # Placeholder - would need actual shader creation code
            return 1
        except Exception as e:
            print(f"Error creating aurora shader: {e}")
            return 0
            
    def _update_clouds(self, delta_time: float) -> None:
        # This would be implemented to update cloud positions
        pass
        
    def _update_weather(self, delta_time: float) -> None:
        # This would be implemented to handle weather transitions
        pass
        
    def _update_aurora(self, delta_time: float) -> None:
        if self.aurora_active:
            self.aurora_intensity = min(1.0, self.aurora_intensity + delta_time)
            
            # Update aurora color
            t = self.time_of_day * 10
            if self.using_gl:
                self.aurora_color = glm.vec3(
                    0.1 + 0.1 * np.sin(t),
                    0.6 + 0.2 * np.sin(t * 0.7),
                    0.2 + 0.1 * np.sin(t * 1.3)
                )
            else:
                self.aurora_color = (
                    0.1 + 0.1 * np.sin(t),
                    0.6 + 0.2 * np.sin(t * 0.7),
                    0.2 + 0.1 * np.sin(t * 1.3)
                )
    
    def _update_sky_uniforms(self, camera_matrix):
        # This would update shader uniforms for the sky dome
        pass
        
    def _render_sky_dome(self):
        # This would render the sky dome
        pass
        
    def _update_cloud_uniforms(self, camera_matrix):
        # This would update shader uniforms for clouds
        pass
        
    def _render_clouds(self):
        # This would render volumetric clouds
        pass
        
    def _update_aurora_uniforms(self, camera_matrix):
        # This would update shader uniforms for the aurora
        pass
        
    def _render_aurora(self):
        # This would render the aurora effect
        pass
        
    def cleanup(self):
        """Clean up OpenGL resources."""
        if not self.using_gl:
            return
            
        try:
            # Delete textures and shaders
            if self.cloud_texture:
                glDeleteTextures(1, [self.cloud_texture])
                
            # Delete shaders
            if self.sky_shader:
                glDeleteProgram(self.sky_shader)
                
            if self.cloud_shader:
                glDeleteProgram(self.cloud_shader)
                
            if self.aurora_shader:
                glDeleteProgram(self.aurora_shader)
        except Exception as e:
            print(f"Error cleaning up SkySystem: {e}")