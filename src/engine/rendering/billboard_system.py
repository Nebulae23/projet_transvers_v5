# src/engine/rendering/billboard_system.py

import pygame
import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Any
from OpenGL.GL import *
from OpenGL.GLU import *

# Try to import OpenGL
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for billboard system, using fallback rendering")

class BillboardSystem:
    """
    System for rendering 2D sprites as billboards in 3D space.
    Creates an Octopath Traveler-style effect of 2D characters in a 3D world.
    """
    def __init__(self, renderer):
        """
        Initialize the billboard system.
        
        Args:
            renderer: The renderer instance.
        """
        self.renderer = renderer
        self.shader_program = 0
        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        
        # Sprite data
        self.sprite_textures = {}
        self.sprite_animations = {}
        
        # Billboard settings
        self.always_face_camera = True
        self.vertical_billboards = True  # Rotate only around Y axis (Octopath style)
        
        # Initialize OpenGL resources if available
        if OPENGL_AVAILABLE:
            self._init_gl_resources()
            
    def _init_gl_resources(self):
        """Initialize OpenGL resources for billboard rendering."""
        try:
            # Import shader manager if available
            try:
                from ..rendering.shader_manager import ShaderManager
                shader_manager = ShaderManager()
                
                # Load billboard shader
                self.shader_program = shader_manager.load_shader_program(
                    "billboard",
                    "billboard.vert",
                    "billboard.frag"
                )
            except ImportError:
                print("ShaderManager not available, using fallback rendering")
                
            # Create billboard quad geometry
            self._create_billboard_quad()
            
            print("Billboard system GL resources initialized")
            
        except Exception as e:
            print(f"Error initializing billboard GL resources: {e}")
            
    def _create_billboard_quad(self):
        """Create a quad for billboard rendering."""
        if not OPENGL_AVAILABLE:
            return
            
        try:
            # Check if we can create vertex arrays (function should exist AND be callable)
            if not bool(glGenVertexArrays):
                print("Vertex arrays not supported, disabling billboard system")
                return
                
            # Vertex data for a centered quad
            vertices = np.array([
                # Positions          # Texture coords
                -0.5, -0.5, 0.0,     0.0, 1.0,
                 0.5, -0.5, 0.0,     1.0, 1.0,
                 0.5,  0.5, 0.0,     1.0, 0.0,
                -0.5,  0.5, 0.0,     0.0, 0.0
            ], dtype=np.float32)
            
            indices = np.array([
                0, 1, 2,
                2, 3, 0
            ], dtype=np.uint32)
            
            # Create buffers
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            self.ebo = glGenBuffers(1)
            
            # Bind vertex array
            glBindVertexArray(self.vao)
            
            # Bind vertex buffer
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            
            # Bind element buffer
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            
            # Position attribute
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, None)
            glEnableVertexAttribArray(0)
            
            # Texture coord attribute
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)
            
            # Unbind VAO
            glBindVertexArray(0)
            
            print("Billboard quad created successfully")
            
        except Exception as e:
            print(f"Error creating billboard quad: {e}")
            self.vao = 0
            self.vbo = 0
            self.ebo = 0
            
    def render_entities(self, entities, camera_pos):
        """
        Render entities as billboards.
        
        Args:
            entities: List of entities to render.
            camera_pos: The camera position (x, y, z).
        """
        if not entities:
            return
            
        if OPENGL_AVAILABLE and self.shader_program and self.vao:
            self._render_entities_gl(entities, camera_pos)
        else:
            self._render_entities_pygame(entities, camera_pos)
            
    def _render_entities_gl(self, entities, camera_pos):
        """
        Render entities using OpenGL billboarding.
        
        Args:
            entities: List of entities to render.
            camera_pos: The camera position (x, y, z).
        """
        try:
            # Use billboard shader
            glUseProgram(self.shader_program)
            
            # Set camera position uniform
            camera_pos_loc = glGetUniformLocation(self.shader_program, "cameraPosition")
            if camera_pos_loc != -1:
                glUniform3f(camera_pos_loc, camera_pos[0], camera_pos[1], camera_pos[2])
                
            # Set vertical billboarding flag
            vertical_loc = glGetUniformLocation(self.shader_program, "verticalBillboard")
            if vertical_loc != -1:
                glUniform1i(vertical_loc, int(self.vertical_billboards))
                
            # Get view-projection matrix from renderer
            if hasattr(self.renderer, "gl_context") and self.renderer.gl_context:
                view_proj_loc = glGetUniformLocation(self.shader_program, "viewProj")
                # This would need to be implemented to get the actual matrix
                # glUniformMatrix4fv(view_proj_loc, 1, GL_FALSE, view_proj_matrix)
                
            # Bind the quad VAO
            glBindVertexArray(self.vao)
            
            # Enable alpha blending
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Sort entities by distance to camera (back to front)
            sorted_entities = sorted(
                entities,
                key=lambda e: -self._calculate_distance_to_camera(e, camera_pos)
            )
            
            # Render each entity
            for entity in sorted_entities:
                transform = entity.get_component("Transform")
                sprite = entity.get_component("Sprite")
                
                if not transform or not sprite:
                    continue
                    
                # Get sprite texture
                texture_id = self._get_sprite_texture(sprite)
                
                if texture_id == 0:
                    continue
                    
                # Bind texture
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glUniform1i(glGetUniformLocation(self.shader_program, "spriteTexture"), 0)
                
                # Create model matrix
                model_matrix = glm.mat4(1.0)
                model_matrix = glm.translate(model_matrix, glm.vec3(
                    transform.position[0],
                    transform.position[1],
                    transform.position[2] if len(transform.position) > 2 else 0.0
                ))
                
                # Scale the billboard
                sprite_scale = sprite.scale if hasattr(sprite, "scale") else (1.0, 1.0)
                model_matrix = glm.scale(model_matrix, glm.vec3(
                    sprite_scale[0],
                    sprite_scale[1],
                    1.0
                ))
                
                # Set model matrix uniform
                model_loc = glGetUniformLocation(self.shader_program, "model")
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_matrix))
                
                # Draw the billboard
                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
                
            # Cleanup
            glBindVertexArray(0)
            glBindTexture(GL_TEXTURE_2D, 0)
            glUseProgram(0)
            glDisable(GL_BLEND)
            
        except Exception as e:
            print(f"Error rendering entities with GL: {e}")
            self._render_entities_pygame(entities, camera_pos)
            
    def _render_entities_pygame(self, entities, camera_pos):
        """
        Render entities using Pygame (fallback method).
        
        Args:
            entities: List of entities to render.
            camera_pos: The camera position (x, y, z).
        """
        # Skip if no screen available
        if not hasattr(self.renderer, "screen") or not self.renderer.screen:
            return
            
        screen = self.renderer.screen
        screen_center = (screen.get_width() // 2, screen.get_height() // 2)
        
        # Get camera view direction (for simple pseudo-3D positioning)
        camera_view_dir = np.array([0, 0, 1], dtype=float)  # Default: looking forward
        
        # Sort entities by y position (simple depth sorting)
        sorted_entities = sorted(
            entities,
            key=lambda e: e.get_component("Transform").position[1]
        )
        
        # Render each entity
        for entity in sorted_entities:
            transform = entity.get_component("Transform")
            sprite = entity.get_component("Sprite")
            
            if not transform or not sprite:
                continue
                
            # Calculate screen position
            entity_pos = np.array([
                transform.position[0],
                transform.position[1],
                transform.position[2] if len(transform.position) > 2 else 0.0
            ], dtype=float)
            
            # Simple projection to screen space
            # This is a very basic approximation for a 2.5D effect
            rel_pos = entity_pos - np.array(camera_pos, dtype=float)
            
            # Simple scale based on distance
            distance = np.linalg.norm(rel_pos)
            scale_factor = 1.0
            if distance > 0:
                scale_factor = 100.0 / (distance + 10.0)  # Arbitrary scaling
                
            # Apply maximum scale limit
            scale_factor = min(1.5, scale_factor)
            
            # Calculate screen coordinates
            screen_x = int(screen_center[0] + rel_pos[0] * 20)
            screen_y = int(screen_center[1] + rel_pos[1] * 20)
            
            # Get sprite image or draw a placeholder
            sprite_surface = None
            
            if hasattr(sprite, "surface") and sprite.surface:
                sprite_surface = sprite.surface
            elif hasattr(sprite, "image_path") and sprite.image_path:
                try:
                    sprite_surface = pygame.image.load(sprite.image_path)
                except:
                    pass
                    
            if sprite_surface:
                # Scale the sprite
                base_width, base_height = sprite_surface.get_size()
                
                # Apply entity-specific scaling
                entity_scale = sprite.scale if hasattr(sprite, "scale") else (1.0, 1.0)
                width = int(base_width * scale_factor * entity_scale[0])
                height = int(base_height * scale_factor * entity_scale[1])
                
                # Ensure minimum size
                width = max(4, width)
                height = max(4, height)
                
                # Scale the sprite
                scaled_sprite = pygame.transform.scale(sprite_surface, (width, height))
                
                # Calculate centered position
                sprite_x = screen_x - width // 2
                sprite_y = screen_y - height // 2
                
                # Draw the sprite
                screen.blit(scaled_sprite, (sprite_x, sprite_y))
            else:
                # Draw a placeholder rectangle with the entity's color
                color = sprite.color if hasattr(sprite, "color") else (255, 0, 0)
                size = max(4, int(32 * scale_factor))
                
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x - size // 2, screen_y - size // 2, size, size)
                )
                
    def _get_sprite_texture(self, sprite):
        """
        Get or create an OpenGL texture for the sprite.
        
        Args:
            sprite: The sprite component.
            
        Returns:
            int: OpenGL texture ID or 0 if not available.
        """
        if not OPENGL_AVAILABLE:
            return 0
            
        # Try to get existing texture
        entity_id = getattr(sprite, "entity_id", id(sprite))
        if entity_id in self.sprite_textures:
            return self.sprite_textures[entity_id]
            
        # Load texture from surface or image path
        texture_id = 0
        
        try:
            surface = None
            
            if hasattr(sprite, "surface") and sprite.surface:
                surface = sprite.surface
            elif hasattr(sprite, "image_path") and sprite.image_path:
                try:
                    surface = pygame.image.load(sprite.image_path)
                except Exception as e:
                    print(f"Error loading sprite image: {e}")
                    return 0
                    
            if surface:
                texture_id = self._create_texture_from_surface(surface)
                
            # Store the texture ID
            if texture_id:
                self.sprite_textures[entity_id] = texture_id
                
            return texture_id
            
        except Exception as e:
            print(f"Error getting sprite texture: {e}")
            return 0
            
    def _create_texture_from_surface(self, surface):
        """
        Create an OpenGL texture from a pygame surface.
        
        Args:
            surface: The pygame surface.
            
        Returns:
            int: OpenGL texture ID or 0 if failed.
        """
        if not OPENGL_AVAILABLE:
            return 0
            
        try:
            # Create a new OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Get surface data
            width, height = surface.get_size()
            data = pygame.image.tostring(surface, "RGBA", True)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Unbind texture
            glBindTexture(GL_TEXTURE_2D, 0)
            
            return texture_id
            
        except Exception as e:
            print(f"Error creating texture: {e}")
            return 0
            
    def _calculate_distance_to_camera(self, entity, camera_pos):
        """
        Calculate the distance from an entity to the camera.
        
        Args:
            entity: The entity.
            camera_pos: The camera position (x, y, z).
            
        Returns:
            float: Distance to camera.
        """
        transform = entity.get_component("Transform")
        if not transform:
            return 0.0
            
        entity_pos = np.array([
            transform.position[0],
            transform.position[1],
            transform.position[2] if len(transform.position) > 2 else 0.0
        ], dtype=float)
        
        camera_pos_array = np.array(camera_pos, dtype=float)
        return np.linalg.norm(entity_pos - camera_pos_array)
        
    def cleanup(self):
        """Clean up billboard system resources."""
        if not OPENGL_AVAILABLE:
            return
            
        try:
            # Delete buffers
            if self.vbo:
                glDeleteBuffers(1, [self.vbo])
                self.vbo = 0
                
            if self.ebo:
                glDeleteBuffers(1, [self.ebo])
                self.ebo = 0
                
            if self.vao:
                glDeleteVertexArrays(1, [self.vao])
                self.vao = 0
                
            # Delete textures
            for texture_id in self.sprite_textures.values():
                glDeleteTextures(1, [texture_id])
                
            self.sprite_textures.clear()
            
        except Exception as e:
            print(f"Error cleaning up billboard system: {e}") 