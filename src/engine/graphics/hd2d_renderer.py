# src/engine/graphics/hd2d_renderer.py

import numpy as np
import pygame
from typing import Dict, List, Tuple, Optional
import os
import sys

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    import ctypes
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for HD2DRenderer, using fallback")

class HD2DRenderer:
    """
    Renderer for HD-2D style graphics (Octopath Traveler inspired).
    Handles rendering 3D environments with 2D sprite characters.
    """
    def __init__(self):
        """Initialize the HD-2D renderer."""
        # Check if OpenGL is available
        self.using_gl = OPENGL_AVAILABLE
        
        # Fallback surface for software rendering
        self.fallback_surface = pygame.Surface((800, 600))
        self.fallback_surface.fill((50, 80, 120))  # Blue-ish background
        
        # Initialize shader programs
        self.shader_manager = None
        self.terrain_shader = None
        self.vegetation_shader = None
        self.structure_shader = None
        
        # Terrain data
        self.terrain_mesh = None
        self.terrain_textures = {}
        
        # Vegetation data
        self.vegetation_meshes = {}
        self.vegetation_textures = {}
        
        # Structure (buildings) data
        self.structure_meshes = {}
        self.structure_textures = {}
        
        # Scene state
        self.current_camera_matrix = None
        self.light_positions = []
        self.light_colors = []
        
        # Skip OpenGL initialization if not available
        if not self.using_gl:
            print("Using fallback HD2D rendering")
            return
            
        # Initialize renderer
        self._init_renderer()
        
    def _init_renderer(self):
        """Initialize renderer resources."""
        try:
            # Try to import shader manager
            from ..rendering.shader_manager import ShaderManager
            self.shader_manager = ShaderManager()
            
            # Check if needed functions are available
            if not bool(glGenVertexArrays) or not bool(glCreateShader):
                print("Required OpenGL functions not available, using fallback rendering")
                self.using_gl = False
                return
                
            # Load shader programs
            self._load_shaders()
            
            # Load meshes and textures
            self._load_resources()
            
            print("HD-2D renderer initialized successfully")
            
        except ImportError:
            print("Warning: ShaderManager not available, HD-2D renderer will be limited")
            self.using_gl = False
        except Exception as e:
            print(f"Error initializing HD-2D renderer: {e}")
            self.using_gl = False
            
    def _load_shaders(self):
        """Load shader programs for HD-2D rendering."""
        if not self.shader_manager or not self.using_gl:
            return
            
        try:
            # Load terrain shader
            self.terrain_shader = self.shader_manager.load_shader_program(
                "terrain",
                "geometry.vert",
                "geometry.frag"
            )
            
            # Load vegetation shader
            self.vegetation_shader = self.shader_manager.load_shader_program(
                "vegetation",
                "geometry.vert",
                "geometry.frag"
            )
            
            # Load structure shader
            self.structure_shader = self.shader_manager.load_shader_program(
                "structure",
                "pbr.vert",
                "pbr.frag"
            )
            
            # Check if any shader failed to load
            if not self.terrain_shader or not self.vegetation_shader or not self.structure_shader:
                print("One or more shaders failed to load")
                
        except Exception as e:
            print(f"Error loading HD-2D shaders: {e}")
            
    def _load_resources(self):
        """Load meshes and textures for HD-2D rendering."""
        if not self.using_gl:
            return
            
        # This would load 3D models and textures in a real implementation
        # For now, we'll create placeholder meshes
        
        # Check if assets exist, otherwise generate placeholder meshes
        self._create_placeholder_terrain()
        self._create_placeholder_vegetation()
        self._create_placeholder_structures()
        
    def _create_placeholder_terrain(self):
        """Create a placeholder terrain mesh."""
        if not self.using_gl:
            return
            
        # Create a simple plane for terrain
        vertices = np.array([
            # Positions             # Normals           # Texture coords
            -50.0, -0.1, -50.0,     0.0, 1.0, 0.0,      0.0, 0.0,
             50.0, -0.1, -50.0,     0.0, 1.0, 0.0,      1.0, 0.0,
             50.0, -0.1,  50.0,     0.0, 1.0, 0.0,      1.0, 1.0,
            -50.0, -0.1,  50.0,     0.0, 1.0, 0.0,      0.0, 1.0
        ], dtype=np.float32)
        
        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)
        
        # Create OpenGL buffers
        try:
            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)
            ebo = glGenBuffers(1)
            
            glBindVertexArray(vao)
            
            # Bind vertex buffer
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            
            # Bind element buffer
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            
            # Position attribute
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, None)
            glEnableVertexAttribArray(0)
            
            # Normal attribute
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)
            
            # Texture coord attribute
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
            glEnableVertexAttribArray(2)
            
            # Unbind VAO
            glBindVertexArray(0)
            
            # Store the mesh data
            self.terrain_mesh = {
                'vao': vao,
                'vbo': vbo,
                'ebo': ebo,
                'indices_count': len(indices)
            }
            
            # Create a simple placeholder texture
            self._create_placeholder_texture('terrain_diffuse', (100, 100, 200))
            
        except Exception as e:
            print(f"Error creating placeholder terrain mesh: {e}")
            
    def get_surface(self, width=800, height=600):
        """Get the rendering surface for fallback mode."""
        # Resize if needed
        if (self.fallback_surface.get_width(), self.fallback_surface.get_height()) != (width, height):
            self.fallback_surface = pygame.Surface((width, height))
            
        # Draw a simple fallback scene with gradient sky and ground
        # Sky gradient
        for y in range(0, height//2):
            color_value = 50 + int(y * 0.5)
            sky_color = (color_value, color_value + 30, color_value + 70)
            pygame.draw.line(self.fallback_surface, sky_color, (0, y), (width, y))
        
        # Ground
        ground_rect = pygame.Rect(0, height//2, width, height//2)
        pygame.draw.rect(self.fallback_surface, (40, 80, 40), ground_rect)
        
        # Draw grid on ground
        grid_size = 40
        grid_color = (30, 60, 30)
        for x in range(0, width, grid_size):
            pygame.draw.line(self.fallback_surface, grid_color, 
                           (x, height//2), (x, height))
            
        for y in range(height//2, height, grid_size):
            pygame.draw.line(self.fallback_surface, grid_color, 
                           (0, y), (width, y))
        
        # Draw some simple vegetation
        for i in range(10):
            tree_x = (i * 100) % width
            tree_y = height//2 + 50 + (i * 30) % 100
            tree_height = 80 + (i * 10) % 40
            
            # Tree trunk
            pygame.draw.rect(self.fallback_surface, (100, 70, 40), 
                           (tree_x-5, tree_y, 10, tree_height))
            
            # Tree top
            pygame.draw.circle(self.fallback_surface, (30, 100, 30), 
                             (tree_x, tree_y-20), 30)
            
        return self.fallback_surface
            
    def begin_scene(self, camera_matrix):
        """
        Begin rendering the scene.
        
        Args:
            camera_matrix: The camera view-projection matrix.
        """
        if not self.using_gl:
            return
        
        try:
            self.current_camera_matrix = camera_matrix
            
            # Clear depth buffer
            glClear(GL_DEPTH_BUFFER_BIT)
            
            # Set up common state
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        except Exception as e:
            print(f"Error in begin_scene: {e}")
            
    def render_terrain(self):
        """Render the terrain."""
        if not self.using_gl or not self.terrain_mesh or not self.terrain_shader:
            return
            
        try:
            # Use terrain shader
            glUseProgram(self.terrain_shader)
            
            # Set uniforms
            # (In a real implementation, this would set camera matrices, lighting parameters, etc.)
            
            # Bind terrain VAO
            glBindVertexArray(self.terrain_mesh['vao'])
            
            # Draw terrain
            glDrawElements(GL_TRIANGLES, self.terrain_mesh['indices_count'], GL_UNSIGNED_INT, None)
            
            # Unbind
            glBindVertexArray(0)
            glUseProgram(0)
        except Exception as e:
            print(f"Error rendering terrain: {e}")
            
    def render_vegetation(self):
        """Render vegetation (trees, grass, etc.)."""
        if not self.using_gl or not self.vegetation_meshes or not self.vegetation_shader:
            return
            
        try:
            # Use vegetation shader
            glUseProgram(self.vegetation_shader)
            
            # Set uniforms
            # (In a real implementation, this would include matrices, wind animation parameters, etc.)
            
            # Render trees
            if 'tree' in self.vegetation_meshes:
                # Bind tree VAO
                glBindVertexArray(self.vegetation_meshes['tree']['vao'])
                
                # Draw multiple trees at different positions
                # (In a real implementation, this would use instanced rendering)
                for i in range(10):
                    # Calculate position
                    pos_x = (i * 10) - 50
                    pos_z = (i * 5) - 25
                    
                    # Set model matrix uniform
                    # (This would transform the tree to its world position)
                    
                    # Draw tree
                    glDrawElements(GL_TRIANGLES, self.vegetation_meshes['tree']['indices_count'], GL_UNSIGNED_INT, None)
                    
            # Unbind
            glBindVertexArray(0)
            glUseProgram(0)
        except Exception as e:
            print(f"Error rendering vegetation: {e}")
            
    def render_structures(self):
        """Render structures (buildings, bridges, etc.)."""
        if not self.using_gl or not self.structure_meshes or not self.structure_shader:
            return
            
        try:
            # Use structure shader
            glUseProgram(self.structure_shader)
            
            # Set uniforms
            # (In a real implementation, this would include matrices, material parameters, etc.)
            
            # Render buildings
            if 'building' in self.structure_meshes:
                # Bind building VAO
                glBindVertexArray(self.structure_meshes['building']['vao'])
                
                # Draw multiple buildings at different positions
                # (In a real implementation, this would use instanced rendering)
                for i in range(5):
                    # Calculate position
                    pos_x = (i * 20) - 40
                    pos_z = -30
                    
                    # Set model matrix uniform
                    # (This would transform the building to its world position)
                    
                    # Draw building
                    glDrawElements(GL_TRIANGLES, self.structure_meshes['building']['indices_count'], GL_UNSIGNED_INT, None)
                    
            # Unbind
            glBindVertexArray(0)
            glUseProgram(0)
        except Exception as e:
            print(f"Error rendering structures: {e}")
            
    def end_scene(self):
        """End rendering the scene."""
        if not self.using_gl:
            return
            
        try:
            # Clean up state
            glDisable(GL_CULL_FACE)
            
            # Reset active shader
            glUseProgram(0)
            
            # Clear references
            self.current_camera_matrix = None
        except Exception as e:
            print(f"Error in end_scene: {e}")
            
    def cleanup(self):
        """Clean up resources."""
        if not self.using_gl:
            return
            
        try:
            # Delete terrain resources
            if self.terrain_mesh:
                glDeleteVertexArrays(1, [self.terrain_mesh['vao']])
                glDeleteBuffers(1, [self.terrain_mesh['vbo']])
                glDeleteBuffers(1, [self.terrain_mesh['ebo']])
                
            # Delete vegetation resources
            for mesh in self.vegetation_meshes.values():
                if 'vao' in mesh:
                    glDeleteVertexArrays(1, [mesh['vao']])
                    
            # Delete structure resources
            for mesh in self.structure_meshes.values():
                if 'vao' in mesh:
                    glDeleteVertexArrays(1, [mesh['vao']])
                    
            # Delete textures
            for texture_id in self.terrain_textures.values():
                glDeleteTextures(1, [texture_id])
                
            for texture_id in self.vegetation_textures.values():
                glDeleteTextures(1, [texture_id])
                
            for texture_id in self.structure_textures.values():
                glDeleteTextures(1, [texture_id])
                
            print("HD-2D renderer cleaned up")
            
        except Exception as e:
            print(f"Error cleaning up HD-2D renderer: {e}")
            
    def _create_placeholder_texture(self, name, color):
        """
        Create a placeholder texture with a solid color.
        
        Args:
            name (str): Name to identify the texture.
            color (tuple): RGB color tuple (r, g, b).
        """
        if not self.using_gl:
            return
            
        try:
            # Create a simple 16x16 texture with the given color
            size = 16
            data = np.zeros((size, size, 3), dtype=np.uint8)
            
            # Set all pixels to the given color
            data[:,:,0] = color[0]  # R
            data[:,:,1] = color[1]  # G
            data[:,:,2] = color[2]  # B
            
            # Create OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
            
            # Unbind texture
            glBindTexture(GL_TEXTURE_2D, 0)
            
            # Store texture ID
            if 'terrain' in name:
                self.terrain_textures[name] = texture_id
            elif 'vegetation' in name or 'tree' in name:
                self.vegetation_textures[name] = texture_id
            elif 'structure' in name or 'building' in name:
                self.structure_textures[name] = texture_id
                
        except Exception as e:
            print(f"Error creating placeholder texture: {e}")
            
    def _create_placeholder_vegetation(self):
        """Create placeholder vegetation meshes."""
        if not self.using_gl:
            return
            
        try:
            # Create tree mesh
            tree_vao = glGenVertexArrays(1)
            glBindVertexArray(tree_vao)
            
            # Simple tree cube vertices
            # This is just a placeholder - a real implementation would use proper meshes
            self.vegetation_meshes['tree'] = {
                'vao': tree_vao,
                'indices_count': 36  # Cube has 36 indices (6 faces * 2 triangles * 3 vertices)
            }
            
            # Create placeholder tree texture
            self._create_placeholder_texture('tree_diffuse', (30, 100, 30))
            
        except Exception as e:
            print(f"Error creating placeholder vegetation: {e}")
            
    def _create_placeholder_structures(self):
        """Create placeholder building meshes."""
        if not self.using_gl:
            return
            
        try:
            # Building placeholder
            building_vao = glGenVertexArrays(1)
            glBindVertexArray(building_vao)
            
            # Simple building box vertices
            # This is just a placeholder - a real implementation would use proper meshes
            self.structure_meshes['building'] = {
                'vao': building_vao,
                'indices_count': 36  # Box has 36 indices
            }
            
            # Create placeholder building texture
            self._create_placeholder_texture('building_diffuse', (120, 100, 80))
            
        except Exception as e:
            print(f"Error creating placeholder structures: {e}") 