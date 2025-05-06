# src/engine/world/world_renderer.py
from typing import Dict, List, Tuple, Optional
import numpy as np
from OpenGL.GL import *
from ..rendering.shader_manager import ShaderManager
from .terrain import TerrainChunk
from .npc import NPC
from .resource_nodes import ResourceNode

class WorldRenderer:
    def __init__(self):
        self.shader_manager = ShaderManager()
        self.initialize_shaders()
        self.g_buffer = self._create_g_buffer()
        self.sprite_vao = None  # Will be initialized later
        self.quad_vao = None    # Will be initialized later
        self.resource_models = {}
        self.resource_indices_count = {}
        
    def initialize_shaders(self):
        # Set up HD-2D specific shaders
        self.terrain_shader = self.shader_manager.load_shader_program('terrain', 'terrain.vert', 'terrain.frag')
        self.npc_shader = self.shader_manager.load_shader_program('sprite', 'sprite.vert', 'sprite.frag')
        self.resource_shader = self.shader_manager.load_shader_program('geometry', 'geometry.vert', 'geometry.frag')
        self.post_shader = self.shader_manager.load_shader_program('post', 'post.vert', 'post.frag')
        
        # Configure shaders for Octopath-style rendering
        self.shader_manager.use_program('terrain')
        self.shader_manager.set_uniform('terrain', "tilt_shift_focus", 0.5)
        self.shader_manager.set_uniform('terrain', "tilt_shift_range", 0.3)
        
        self.shader_manager.use_program('sprite')
        self.shader_manager.set_uniform('sprite', "sprite_depth_scale", 0.8)
        self.shader_manager.set_uniform('sprite', "normal_strength", 0.6)
        
    def _create_g_buffer(self):
        # Create G-buffer for deferred rendering
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        # Position buffer (RGB16F)
        position_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, position_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 1920, 1080, 0, GL_RGB, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, position_buffer, 0)
        
        # Normal buffer (RGB16F)
        normal_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, normal_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 1920, 1080, 0, GL_RGB, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, normal_buffer, 0)
        
        # Albedo + Roughness buffer (RGBA8)
        albedo_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, albedo_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 1920, 1080, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, albedo_buffer, 0)
        
        # Depth buffer
        depth_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, depth_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32F, 1920, 1080, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_buffer, 0)
        
        # Tell OpenGL which color attachments we'll use
        glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return {
            'fbo': fbo,
            'position': position_buffer,
            'normal': normal_buffer,
            'albedo': albedo_buffer,
            'depth': depth_buffer
        }
        
    def render_world(self, chunks: List[TerrainChunk], npcs: List[NPC], 
                    resources: List[ResourceNode], camera_position: Tuple[float, float, float]):
        # Geometry Pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.g_buffer['fbo'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Render terrain with tilt-shift effect
        self.shader_manager.use_program('terrain')
        self._setup_camera(camera_position)
        for chunk in chunks:
            self._render_terrain_chunk(chunk)
            
        # Render NPCs with HD-2D sprite integration
        self.shader_manager.use_program('sprite')
        for npc in npcs:
            self._render_npc(npc)
            
        # Render resource nodes
        self.shader_manager.use_program('geometry')
        for resource in resources:
            self._render_resource_node(resource)
            
        # Post-processing pass for HD-2D style
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.shader_manager.use_program('post')
        self._apply_post_processing()
        
    def _setup_camera(self, camera_position: Tuple[float, float, float]):
        # Set up isometric-style camera for HD-2D look
        view_matrix = self._calculate_view_matrix(camera_position)
        projection_matrix = self._calculate_projection_matrix()
        
        self.shader_manager.set_uniform('terrain', "view", view_matrix)
        self.shader_manager.set_uniform('terrain', "projection", projection_matrix)
        self.shader_manager.set_uniform('sprite', "view", view_matrix)
        self.shader_manager.set_uniform('sprite', "projection", projection_matrix)
        self.shader_manager.set_uniform('geometry', "view", view_matrix)
        self.shader_manager.set_uniform('geometry', "projection", projection_matrix)
        
    def _calculate_view_matrix(self, camera_position: Tuple[float, float, float]) -> np.ndarray:
        # Calculate view matrix for isometric-style camera
        cam_dist = 50.0
        cam_height = 30.0
        cam_angle = np.pi / 4  # 45 degrees
        
        eye = np.array([
            camera_position[0] - cam_dist * np.cos(cam_angle),
            camera_position[1] + cam_height,
            camera_position[2] - cam_dist * np.sin(cam_angle)
        ])
        
        target = np.array(camera_position)
        up = np.array([0.0, 1.0, 0.0])
        
        forward = target - eye
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        up = np.cross(right, forward)
        
        view_matrix = np.eye(4)
        view_matrix[:3, 0] = right
        view_matrix[:3, 1] = up
        view_matrix[:3, 2] = -forward
        view_matrix[:3, 3] = -eye
        
        return view_matrix
        
    def _calculate_projection_matrix(self) -> np.ndarray:
        # Perspective projection with wide FOV for HD-2D style
        aspect = 1920 / 1080
        fov = np.pi / 3  # 60 degrees
        near = 0.1
        far = 1000.0
        
        f = 1.0 / np.tan(fov / 2)
        projection = np.zeros((4, 4))
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = (far + near) / (near - far)
        projection[2, 3] = 2 * far * near / (near - far)
        projection[3, 2] = -1
        
        return projection
        
    def _render_terrain_chunk(self, chunk: TerrainChunk):
        self.shader_manager.set_uniform('terrain', "model_matrix", self._get_chunk_transform(chunk))
        self.shader_manager.set_uniform('terrain', "heightmap_scale", 20.0)
        
        # Bind mesh data and render
        # Check if chunk.mesh has 'vao' key or use alternative
        if hasattr(chunk, 'mesh') and chunk.mesh and isinstance(chunk.mesh, dict):
            if 'vao' in chunk.mesh:
                glBindVertexArray(chunk.mesh['vao'])
                glDrawElements(GL_TRIANGLES, len(chunk.mesh['indices']), GL_UNSIGNED_INT, None)
            else:
                # Handle case where mesh structure doesn't have 'vao'
                print("Warning: Terrain chunk mesh doesn't have 'vao' attribute")
        
    def _render_npc(self, npc: NPC):
        self.shader_manager.set_uniform('sprite', "model_matrix", self._get_npc_transform(npc))
        self.shader_manager.set_uniform('sprite', "sprite_animation_frame", npc.animation_frame)
        self.shader_manager.set_uniform('sprite', "sprite_facing", npc.rotation)
        
        # Bind sprite texture and render billboard
        if self.sprite_vao:
            glBindVertexArray(self.sprite_vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        else:
            print("Warning: sprite_vao not initialized")
        
    def _render_resource_node(self, resource: ResourceNode):
        self.shader_manager.set_uniform('geometry', "model_matrix", self._get_resource_transform(resource))
        
        # Check if resource type exists in models dictionary
        if resource.resource_type in self.resource_models and resource.resource_type in self.resource_indices_count:
            # Bind resource model and render
            glBindVertexArray(self.resource_models[resource.resource_type])
            glDrawElements(GL_TRIANGLES, self.resource_indices_count[resource.resource_type], 
                        GL_UNSIGNED_INT, None)
        else:
            print(f"Warning: Resource type {resource.resource_type} not found in models")
                      
    def _apply_post_processing(self):
        # Bind G-buffer textures
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['position'])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['normal'])
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['albedo'])
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['depth'])
        
        # Set post-processing uniforms for HD-2D style
        self.shader_manager.set_uniform('post', "depth_of_field_enabled", 1)
        self.shader_manager.set_uniform('post', "bloom_threshold", 0.8)
        self.shader_manager.set_uniform('post', "vignette_strength", 0.3)
        self.shader_manager.set_uniform('post', "color_grading_strength", 0.5)
        
        # Render full-screen quad
        if self.quad_vao:
            glBindVertexArray(self.quad_vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        else:
            print("Warning: quad_vao not initialized")
        
    def _get_chunk_transform(self, chunk: TerrainChunk) -> np.ndarray:
        position = np.array([
            chunk.position[0] * chunk.size,
            0,
            chunk.position[1] * chunk.size,
            1
        ])
        return np.array([
            [chunk.size, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, chunk.size, position[2]],
            [0, 0, 0, 1]
        ])
        
    def _get_npc_transform(self, npc: NPC) -> np.ndarray:
        # Calculate billboard transform matrix
        position = np.array(npc.position)
        scale = np.array([2.0, 2.0, 1.0])  # Adjust scale for HD-2D style
        
        return np.array([
            [scale[0], 0, 0, position[0]],
            [0, scale[1], 0, position[1]],
            [0, 0, scale[2], position[2]],
            [0, 0, 0, 1]
        ])
        
    def _get_resource_transform(self, resource: ResourceNode) -> np.ndarray:
        position = np.array(resource.position)
        return np.array([
            [1, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ])