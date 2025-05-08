#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renderer module for Nightfall Defenders
Implements an Octopath Traveler-inspired visual style
"""

import os
from panda3d.core import (
    FrameBufferProperties, 
    WindowProperties, 
    GraphicsPipe, 
    GraphicsOutput,
    Shader, 
    Texture, 
    TextureStage,
    CardMaker, 
    NodePath, 
    Vec3, 
    Vec4
)

class Renderer:
    """
    Custom rendering pipeline with deferred shading and post-processing
    for Octopath Traveler-inspired visuals
    """
    
    def __init__(self, game):
        """Initialize the renderer"""
        self.game = game
        self.resource_manager = game.resource_manager
        
        # Setup graphics quality based on config
        self.setup_graphics_quality()
        
        # Create render targets
        self.setup_render_targets()
        
        # Create post-processing pipeline
        self.setup_post_processing()
        
        # Enable shader generator for auto-shader generation
        self.game.render.setShaderAuto()
    
    def setup_graphics_quality(self):
        """Configure rendering quality based on settings"""
        quality = "medium"
        
        # Try to get from game config if available
        if hasattr(self.game, 'game_config'):
            try:
                quality = self.game.game_config.get_graphics_quality()
            except:
                pass
        
        # Default values
        self.shadow_map_size = 1024
        self.bloom_quality = 0.5
        self.dof_quality = 0.25
        self.use_ssao = False
        
        # Configure based on quality setting
        if quality == "low":
            # Low quality settings
            self.shadow_map_size = 512
            self.bloom_quality = 0.25
            self.use_ssao = False
        elif quality == "medium":
            # Medium quality settings
            self.shadow_map_size = 1024
            self.bloom_quality = 0.5
            self.use_ssao = False
        elif quality == "high":
            # High quality settings
            self.shadow_map_size = 2048
            self.bloom_quality = 0.75
            self.dof_quality = 0.5
            self.use_ssao = True
        elif quality == "ultra":
            # Ultra quality settings
            self.shadow_map_size = 4096
            self.bloom_quality = 1.0
            self.dof_quality = 1.0
            self.use_ssao = True
    
    def setup_render_targets(self):
        """Setup the render targets for deferred rendering"""
        # Main window properties
        window_props = self.game.win.getProperties()
        win_size = (window_props.getXSize(), window_props.getYSize())
        
        # Frame buffer properties
        fb_props = FrameBufferProperties()
        fb_props.setRgbColor(True)
        fb_props.setAlphaBits(8)
        fb_props.setDepthBits(24)
        
        # Create G-Buffer (position, normal, albedo, etc.)
        self.g_buffer = self.game.win.makeTextureBuffer("G-Buffer", win_size[0], win_size[1])
        self.g_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.g_buffer_camera = self.game.makeCamera(self.g_buffer)
        self.g_buffer_camera.reparentTo(self.game.render)
        
        # Create textures for deferred rendering
        self.position_tex = Texture()
        self.normal_tex = Texture()
        self.albedo_tex = Texture()
        self.depth_tex = Texture()
        
        # Attach these textures to the G-Buffer
        self.g_buffer.addRenderTexture(self.position_tex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.g_buffer.addRenderTexture(self.normal_tex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        self.g_buffer.addRenderTexture(self.albedo_tex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)
        self.g_buffer.addRenderTexture(self.depth_tex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
        
        # Create the final render target
        self.final_buffer = self.game.win.makeTextureBuffer("Final-Buffer", win_size[0], win_size[1])
        self.final_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.final_tex = Texture()
        self.final_buffer.addRenderTexture(self.final_tex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        
        # Create a camera for the final composition
        self.final_camera = self.game.makeCamera(self.final_buffer)
        self.final_camera.reparentTo(self.game.render2d)
    
    def setup_post_processing(self):
        """Set up post-processing effects for Octopath Traveler style"""
        # Create the post-processing root node
        self.post_root = NodePath("PostProcessRoot")
        self.post_root.reparentTo(self.game.render2d)
        
        # Create a full-screen quad
        cm = CardMaker("PostProcessQuad")
        cm.setFrameFullscreenQuad()
        self.post_quad = self.post_root.attachNewNode(cm.generate())
        
        # Shader for Octopath Traveler-style rendering
        # We'll implement these shaders in separate files
        
        # 1. Create and apply diorama effect (the cardboard cutout look)
        self.create_diorama_shader()
        
        # 2. Create and apply tilt-shift effect
        self.create_tilt_shift_shader()
        
        # 3. Create and apply color grading for stylized look
        self.create_color_grading_shader()
    
    def create_diorama_shader(self):
        """Create the shader for the diorama cardboard cutout effect"""
        # Shader paths
        vertex_path = os.path.join("src", "assets", "shaders", "diorama.vert")
        fragment_path = os.path.join("src", "assets", "shaders", "diorama.frag")
        
        # Create the shader directory if it doesn't exist
        shader_dir = os.path.join("src", "assets", "shaders")
        os.makedirs(shader_dir, exist_ok=True)
        
        # Check if shader files exist
        if os.path.exists(vertex_path) and os.path.exists(fragment_path):
            try:
                self.diorama_shader = Shader.load(Shader.SL_GLSL, 
                                                vertex=vertex_path,
                                                fragment=fragment_path)
                print("Loaded diorama shader from files")
            except Exception as e:
                print(f"Failed to load diorama shader from files: {e}")
                # Fall back to inline shader as a backup
                self.create_fallback_diorama_shader()
        else:
            print("Diorama shader files not found, using fallback")
            # Create fallback shader inline
            self.create_fallback_diorama_shader()
        
        # Set up a post-process quad for the diorama effect
        cm = CardMaker("diorama_quad")
        cm.setFrameFullscreenQuad()
        self.diorama_quad = self.game.render2d.attachNewNode(cm.generate())
        
        # Apply the shader
        self.diorama_quad.setShader(self.diorama_shader)
        
        # Set initial shader inputs
        self.diorama_quad.setShaderInput("depth_offset", 0.0)
        self.diorama_quad.setShaderInput("depth_scale", 1.0)
        self.diorama_quad.setShaderInput("depth_contrast", 1.5)
        self.diorama_quad.setShaderInput("edge_strength", 0.8)
        self.diorama_quad.setShaderInput("ambient_intensity", 0.6)
        self.diorama_quad.setShaderInput("light_direction", Vec3(0.0, -0.5, -0.5))
        self.diorama_quad.setShaderInput("light_color", Vec3(1.0, 0.9, 0.8))
        
        # Set the diorama effect to render after main scene
        self.diorama_quad.setBin("fixed", 10)
        
        print("Diorama shader set up successfully")
    
    def create_fallback_diorama_shader(self):
        """Create a simple fallback diorama shader if files are not found"""
        self.diorama_shader = Shader.make(Shader.SL_GLSL, 
            """
            #version 330
            
            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord0;
            out vec2 texcoord;
            
            void main() {
                gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                texcoord = p3d_MultiTexCoord0;
            }
            """,
            """
            #version 330
            
            uniform sampler2D p3d_Texture0;
            in vec2 texcoord;
            out vec4 fragColor;
            
            void main() {
                // Simple pass-through until we implement the actual shader
                fragColor = texture(p3d_Texture0, texcoord);
            }
            """
        )
    
    def create_tilt_shift_shader(self):
        """Create the shader for the tilt-shift effect"""
        # Shader paths
        vertex_path = os.path.join("src", "assets", "shaders", "tilt_shift.vert")
        fragment_path = os.path.join("src", "assets", "shaders", "tilt_shift.frag")
        
        # Check if shader files exist
        if os.path.exists(vertex_path) and os.path.exists(fragment_path):
            try:
                self.tilt_shift_shader = Shader.load(Shader.SL_GLSL, 
                                                   vertex=vertex_path,
                                                   fragment=fragment_path)
                print("Loaded tilt-shift shader from files")
            except Exception as e:
                print(f"Failed to load tilt-shift shader from files: {e}")
                # Fall back to inline shader as a backup
                self.create_fallback_tilt_shift_shader()
        else:
            print("Tilt-shift shader files not found, using fallback")
            # Create fallback shader inline
            self.create_fallback_tilt_shift_shader()
        
        # Set up a post-process quad for the tilt-shift effect
        cm = CardMaker("tilt_shift_quad")
        cm.setFrameFullscreenQuad()
        self.tilt_shift_quad = self.game.render2d.attachNewNode(cm.generate())
        
        # Apply the shader
        self.tilt_shift_quad.setShader(self.tilt_shift_shader)
        
        # Set initial shader inputs
        self.tilt_shift_quad.setShaderInput("blur_amount", 5.0)
        self.tilt_shift_quad.setShaderInput("focus_width", 0.15)
        self.tilt_shift_quad.setShaderInput("focus_position", 0.5)
        self.tilt_shift_quad.setShaderInput("samples", 4)
        
        # Set the tilt-shift effect to render after diorama effect
        self.tilt_shift_quad.setBin("fixed", 20)
        
        print("Tilt-shift shader set up successfully")
    
    def create_fallback_tilt_shift_shader(self):
        """Create a simple fallback tilt-shift shader if files are not found"""
        self.tilt_shift_shader = Shader.make(Shader.SL_GLSL, 
            """
            #version 330
            
            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord0;
            out vec2 texcoord;
            
            void main() {
                gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                texcoord = p3d_MultiTexCoord0;
            }
            """,
            """
            #version 330
            
            uniform sampler2D p3d_Texture0;
            in vec2 texcoord;
            out vec4 fragColor;
            
            void main() {
                // Simple pass-through until we implement the actual shader
                fragColor = texture(p3d_Texture0, texcoord);
            }
            """
        )
    
    def create_color_grading_shader(self):
        """Create the shader for color grading"""
        # Shader paths
        vertex_path = os.path.join("src", "assets", "shaders", "color_grading.vert")
        fragment_path = os.path.join("src", "assets", "shaders", "color_grading.frag")
        
        # Check if shader files exist
        if os.path.exists(vertex_path) and os.path.exists(fragment_path):
            try:
                self.color_grading_shader = Shader.load(Shader.SL_GLSL, 
                                                      vertex=vertex_path,
                                                      fragment=fragment_path)
                print("Loaded color grading shader from files")
            except Exception as e:
                print(f"Failed to load color grading shader from files: {e}")
                # Fall back to inline shader as a backup
                self.create_fallback_color_grading_shader()
        else:
            print("Color grading shader files not found, using fallback")
            # Create fallback shader inline
            self.create_fallback_color_grading_shader()
        
        # Set up a post-process quad for the color grading effect
        cm = CardMaker("color_grading_quad")
        cm.setFrameFullscreenQuad()
        self.color_grading_quad = self.game.render2d.attachNewNode(cm.generate())
        
        # Apply the shader
        self.color_grading_quad.setShader(self.color_grading_shader)
        
        # Set initial shader inputs
        self.color_grading_quad.setShaderInput("color_filter", Vec3(1.0, 1.0, 1.0))
        self.color_grading_quad.setShaderInput("contrast", 1.2)
        self.color_grading_quad.setShaderInput("brightness", 1.0)
        self.color_grading_quad.setShaderInput("saturation", 1.1)
        self.color_grading_quad.setShaderInput("gamma", 1.0)
        self.color_grading_quad.setShaderInput("use_lut", False)
        self.color_grading_quad.setShaderInput("day_night_blend", 0.0)
        self.color_grading_quad.setShaderInput("day_tint", Vec3(1.0, 1.0, 1.0))
        self.color_grading_quad.setShaderInput("night_tint", Vec3(0.7, 0.8, 1.1))
        
        # Set the color grading effect to render after tilt-shift effect
        self.color_grading_quad.setBin("fixed", 30)
        
        print("Color grading shader set up successfully")
    
    def create_fallback_color_grading_shader(self):
        """Create a simple fallback color grading shader if files are not found"""
        self.color_grading_shader = Shader.make(Shader.SL_GLSL, 
            """
            #version 330
            
            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord0;
            out vec2 texcoord;
            
            void main() {
                gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                texcoord = p3d_MultiTexCoord0;
            }
            """,
            """
            #version 330
            
            uniform sampler2D p3d_Texture0;
            in vec2 texcoord;
            out vec4 fragColor;
            
            void main() {
                // Simple pass-through until we implement the actual shader
                fragColor = texture(p3d_Texture0, texcoord);
            }
            """
        )
    
    def update(self, dt):
        """Update the renderer each frame"""
        # Here we would update any time-based shader parameters
        # like day/night cycle lighting, etc.
        pass
    
    def resize(self, width, height):
        """Handle window resize events"""
        # Resize render targets
        self.g_buffer.setSize(width, height)
        self.final_buffer.setSize(width, height)
    
    def apply_octopath_style(self, node_path):
        """Apply Octopath Traveler style shaders to a specific node"""
        # Here we would apply the specific shaders for the Octopath look
        # to individual models rather than through the post-processing pipeline
        pass 