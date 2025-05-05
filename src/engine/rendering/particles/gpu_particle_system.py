import numpy as np
from OpenGL.GL import *
from typing import List

class ParticleEmitter:
    def __init__(self, max_particles: int):
        self.max_particles = max_particles
        self.position = np.zeros(3, dtype=np.float32)
        self.spawn_rate = 100  # particles per second
        self.particle_life = 5.0  # seconds
        self.velocity_range = (-1.0, 1.0)
        self.size_range = (0.1, 0.5)
        self.color_start = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.color_end = np.array([1.0, 1.0, 1.0, 0.0], dtype=np.float32)

class GPUParticleSystem:
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
        self._setup_buffers()
        self._setup_shaders()
        self._setup_compute_shader()
    
    def _setup_buffers(self):
        """Initialize particle buffers on GPU"""
        self.particle_buffer = glGenBuffers(1)
        self.transform_feedback = glGenTransformFeedbacks(1)
        
        # Particle data structure:
        # position(vec3), velocity(vec3), life(float), size(float), color(vec4)
        self.stride = (3 + 3 + 1 + 1 + 4) * 4  # bytes
    
    def _setup_shaders(self):
        """Initialize particle rendering shaders"""
        # Shader implementation would go here
        self.render_shader = None
        self.update_shader = None
    
    def _setup_compute_shader(self):
        """Initialize compute shader for particle simulation"""
        # Compute shader implementation would go here
        self.compute_shader = None
    
    def add_emitter(self, emitter: ParticleEmitter):
        """Add a new particle emitter"""
        self.emitters.append(emitter)
        self._allocate_particles(emitter)
    
    def _allocate_particles(self, emitter: ParticleEmitter):
        """Allocate GPU memory for particles"""
        data = np.zeros(emitter.max_particles * self.stride, dtype=np.float32)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_buffer)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
    
    def update(self, dt: float):
        """Update particle simulation"""
        if not self.compute_shader:
            return
            
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.particle_buffer)
        
        # Dispatch compute shader
        glUseProgram(self.compute_shader)
        glUniform1f(glGetUniformLocation(self.compute_shader, 'deltaTime'), dt)
        
        for emitter in self.emitters:
            glUniform3fv(glGetUniformLocation(self.compute_shader, 'emitterPos'), 1, emitter.position)
            glUniform1f(glGetUniformLocation(self.compute_shader, 'spawnRate'), emitter.spawn_rate)
            
            work_groups = (emitter.max_particles + 255) // 256
            glDispatchCompute(work_groups, 1, 1)
        
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
    
    def render(self, view_matrix: np.ndarray, proj_matrix: np.ndarray):
        """Render particles"""
        if not self.render_shader:
            return
            
        glUseProgram(self.render_shader)
        glUniformMatrix4fv(glGetUniformLocation(self.render_shader, 'viewMatrix'), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.render_shader, 'projMatrix'), 1, GL_FALSE, proj_matrix)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_buffer)
        # Set up vertex attributes and render particles
        # Implementation would go here
    
    def cleanup(self):
        """Clean up OpenGL resources"""
        glDeleteBuffers(1, [self.particle_buffer])
        glDeleteTransformFeedbacks(1, [self.transform_feedback])