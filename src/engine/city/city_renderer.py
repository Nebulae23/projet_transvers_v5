# src/engine/city/city_renderer.py
from typing import List
import numpy as np
from OpenGL.GL import *
import pygame
from ..rendering.shader_manager import ShaderManager
from ..core import OpenGLContext
from .district import District
from .building import Building
from .defense import DefenseTower

class CityRenderer:
    def __init__(self, gl_context: OpenGLContext):
        self.gl_context = gl_context
        self.shader_manager = ShaderManager()  # Use ShaderManager instead of ShaderPipeline
        self.initialize_shaders()
        
    def initialize_shaders(self):
        # Setup HD-2D specific shaders
        # Load shaders using the shader manager
        self.geometry_program = self.shader_manager.load_shader_program('geometry', 'geometry.vert', 'geometry.frag')
        self.lighting_program = self.shader_manager.load_shader_program('lighting', 'lighting.vert', 'lighting.frag')
        self.post_program = self.shader_manager.load_shader_program('post', 'post.vert', 'post.frag')
        
        # Initialize framebuffers for deferred rendering
        self.g_buffer = self._create_g_buffer()
        
    def _create_g_buffer(self):
        # Create G-buffer for deferred rendering
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        # Position buffer
        position_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, position_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 1920, 1080, 0, GL_RGB, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, position_buffer, 0)
        
        # Normal buffer
        normal_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, normal_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 1920, 1080, 0, GL_RGB, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, normal_buffer, 0)
        
        # Albedo + Roughness buffer
        albedo_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, albedo_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1920, 1080, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, albedo_buffer, 0)
        
        # Depth buffer
        depth_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, depth_buffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 1920, 1080, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_buffer, 0)
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return {
            'fbo': fbo,
            'position': position_buffer,
            'normal': normal_buffer,
            'albedo': albedo_buffer,
            'depth': depth_buffer
        }
        
    def render_city(self, districts: List[District], towers: List[DefenseTower]):
        # Geometry Pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.g_buffer['fbo'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.shader_manager.use_program('geometry')
        for district in districts:
            self._render_district(district)
            
        # Lighting Pass
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.shader_manager.use_program('lighting')
        
        # Bind G-buffer textures
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['position'])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['normal'])
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.g_buffer['albedo'])
        
        # Render lighting
        self._render_fullscreen_quad()
        
        # Post-processing
        self.shader_manager.use_program('post')
        self._apply_post_processing()
        
    def _render_district(self, district: District):
        self.shader_manager.set_uniform('geometry', "model_matrix", district._get_transform_matrix())
        self.gl_context.draw_mesh(district.mesh)
        
        for building in district.buildings:
            self._render_building(building)
            
    def _render_building(self, building: Building):
        self.shader_manager.set_uniform('geometry', "model_matrix", building._get_transform_matrix())
        self.shader_manager.set_uniform('geometry', "material.albedo_map", building.material['albedo_map'])
        self.shader_manager.set_uniform('geometry', "material.normal_map", building.material['normal_map'])
        self.shader_manager.set_uniform('geometry', "material.roughness_map", building.material['roughness_map'])
        self.gl_context.draw_mesh(building.mesh)
        
    def _render_fullscreen_quad(self):
        # Render a fullscreen quad for post-processing
        vertices = np.array([
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
            -1.0,  1.0,  0.0, 1.0
        ], dtype=np.float32)
        
        self.gl_context.draw_mesh(vertices)
        
    def _apply_post_processing(self):
        # Apply HD-2D specific post-processing effects
        self.shader_manager.set_uniform('post', "dof_enabled", 1)
        self.shader_manager.set_uniform('post', "bloom_threshold", 1.0)
        self._render_fullscreen_quad()