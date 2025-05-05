# src/engine/rendering/water_system.py
from typing import Optional
import numpy as np
import pygame
import sys

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available in WaterSystem, using fallback")

class WaterSystem:
    def __init__(self, window_size: tuple[int, int]):
        self.window_size = window_size
        
        # Fallback surface for software rendering
        self.fallback_surface = pygame.Surface(window_size)
        self.fallback_surface.fill((0, 100, 200))  # Blue for water
        
        # Skip OpenGL initialization if not available
        if not OPENGL_AVAILABLE:
            print("Using fallback water rendering")
            self.reflection_fbo = None
            self.refraction_fbo = None
            self.water_shader = None
            self.using_gl = False
            return
            
        try:
            # Create reflection and refraction textures
            self.reflection_fbo = self._create_reflection_fbo()
            self.refraction_fbo = self._create_refraction_fbo()
            
            # Load shaders
            self.water_shader = self._create_water_shader()
            
            self.using_gl = True
        except Exception as e:
            print(f"Error initializing WaterSystem with OpenGL: {e}")
            self.reflection_fbo = None
            self.refraction_fbo = None
            self.water_shader = None
            self.using_gl = False
        
        # Water surface parameters
        self.wave_speed = 0.03
        self.wave_strength = 0.04
        self.reflection_distortion = 0.02
        self.water_color = (0.0, 0.3, 0.5) if OPENGL_AVAILABLE else (0, 76, 127)
        self.fresnel_strength = 0.5
        
        # Time-based animation
        self.time = 0.0
        
    def update_reflections(self, camera_matrix: np.ndarray) -> None:
        if not self.using_gl:
            return  # Skip if not using OpenGL
            
        try:
            # Calculate reflection camera
            reflection_matrix = self._calculate_reflection_matrix()
            reflection_camera = reflection_matrix @ camera_matrix
            
            # Render to reflection texture
            glBindFramebuffer(GL_FRAMEBUFFER, self.reflection_fbo)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Enable clip plane for water surface
            glEnable(GL_CLIP_PLANE0)
            self._set_clip_plane(glm.vec4(0, 1, 0, 0))
            
            # Render reflection scene from reflection camera
            self._render_reflection_scene(reflection_camera)
            
            glDisable(GL_CLIP_PLANE0)
        except Exception as e:
            print(f"Error updating reflections: {e}")
        
    def update(self, delta_time: float) -> None:
        self.time += delta_time
        
        # Update fallback surface animation if not using OpenGL
        if not self.using_gl:
            # Simple wave animation by shifting shades of blue
            wave_pos = int((self.time * 5) % self.window_size[1])
            for y in range(0, self.window_size[1], 20):
                pos = (wave_pos + y) % self.window_size[1]
                color = (0, 100 + int(20 * abs(wave_pos / self.window_size[1])), 200)
                pygame.draw.line(self.fallback_surface, color, (0, pos), (self.window_size[0], pos), 2)
        
    def render(self, camera_matrix: np.ndarray = None) -> None:
        if not self.using_gl:
            return  # Render is handled by getting the fallback surface
        
        try:
            glUseProgram(self.water_shader)
            
            # Bind textures
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.reflection_fbo)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.refraction_fbo)
            
            # Update uniforms
            self._update_water_uniforms(camera_matrix)
            
            # Render water surface
            self._render_water_mesh()
        except Exception as e:
            print(f"Error rendering water: {e}")
        
    def get_surface(self):
        """Get the water rendering surface for fallback mode."""
        return self.fallback_surface
        
    def _create_reflection_fbo(self) -> int:
        if not OPENGL_AVAILABLE:
            return None
            
        try:
            fbo = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, fbo)
            
            # Color attachment
            color_tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, color_tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, 
                        self.window_size[0], self.window_size[1],
                        0, GL_RGBA, GL_FLOAT, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                                GL_TEXTURE_2D, color_tex, 0)
            
            # Depth attachment
            depth_tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, depth_tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24,
                        self.window_size[0], self.window_size[1],
                        0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                GL_TEXTURE_2D, depth_tex, 0)
            
            return fbo
        except Exception as e:
            print(f"Error creating reflection FBO: {e}")
            return None
        
    def _create_refraction_fbo(self) -> int:
        # Similar to reflection FBO but with different parameters
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        color_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, color_tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F,
                    self.window_size[0], self.window_size[1],
                    0, GL_RGBA, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                              GL_TEXTURE_2D, color_tex, 0)
        
        return fbo
        
    def _create_water_shader(self) -> int:
        # Create and compile water surface shader
        vertex_shader = """
        #version 430
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec2 texcoord;
        
        uniform mat4 modelViewProj;
        uniform float time;
        uniform float waveStrength;
        
        out vec2 v_texcoord;
        out vec3 v_position;
        
        void main() {
            vec3 pos = position;
            pos.y += sin(pos.x * 2.0 + time) * waveStrength;
            pos.y += cos(pos.z * 2.0 + time * 0.7) * waveStrength;
            
            gl_Position = modelViewProj * vec4(pos, 1.0);
            v_texcoord = texcoord;
            v_position = pos;
        }
        """
        
        fragment_shader = """
        #version 430
        in vec2 v_texcoord;
        in vec3 v_position;
        
        uniform sampler2D reflectionTexture;
        uniform sampler2D refractionTexture;
        uniform vec3 waterColor;
        uniform float fresnelStrength;
        uniform float reflectionDistortion;
        
        out vec4 fragColor;
        
        void main() {
            vec2 reflectionCoord = v_texcoord + vec2(
                sin(v_position.x * 4.0 + time * 2.0) * reflectionDistortion,
                cos(v_position.z * 4.0 + time * 1.4) * reflectionDistortion
            );
            
            vec3 reflection = texture(reflectionTexture, reflectionCoord).rgb;
            vec3 refraction = texture(refractionTexture, v_texcoord).rgb;
            
            float fresnel = pow(1.0 - max(0.0, dot(normalize(v_position), vec3(0,1,0))), fresnelStrength);
            
            vec3 finalColor = mix(refraction, reflection, fresnel) + waterColor;
            
            fragColor = vec4(finalColor, 1.0);
        }
        """
        
        # Compile and link shaders
        return self._compile_shader_program(vertex_shader, fragment_shader)
        
    def _compile_shader_program(self, vertex_src: str, fragment_src: str) -> int:
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        
        glShaderSource(vertex_shader, vertex_src)
        glShaderSource(fragment_shader, fragment_src)
        
        glCompileShader(vertex_shader)
        glCompileShader(fragment_shader)
        
        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)
        
        return program

    def _set_clip_plane(self, plane):
        if not self.using_gl:
            return
        pass  # Implementation depends on OpenGL version
        
    def _render_reflection_scene(self, camera):
        if not self.using_gl:
            return
        pass  # Would depend on the rendering system
        
    def _update_water_uniforms(self, camera):
        if not self.using_gl:
            return
        pass  # Implementation depends on shader structure
        
    def _render_water_mesh(self):
        if not self.using_gl:
            return
        pass  # Implementation depends on mesh structure
        
    def _calculate_reflection_matrix(self):
        if not self.using_gl:
            return np.identity(4)
        # Placeholder implementation
        return np.identity(4)