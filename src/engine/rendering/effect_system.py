# src/engine/rendering/effect_system.py
from typing import List, Dict, Optional
import numpy as np
import pygame
import random
import sys

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for EffectSystem, using fallback")
    
from dataclasses import dataclass
from enum import Enum

class EffectType(Enum):
    AURORA = "aurora"
    LIGHTNING = "lightning"
    RAIN = "rain"
    SNOW = "snow"

@dataclass
class Particle:
    position: np.ndarray
    velocity: np.ndarray
    color: np.ndarray
    size: float
    life: float
    max_life: float

class ParticleEmitter:
    def __init__(self, effect_type: EffectType):
        self.effect_type = effect_type
        self.particles: List[Particle] = []
        self.active = True
        self.position = np.zeros(3)
        
        # Emitter parameters based on effect type
        self.emit_rate = self._get_emit_rate()
        self.particle_life = self._get_particle_life()
        self.emit_timer = 0.0
        
    def update(self, delta_time: float) -> None:
        # Update existing particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.position += particle.velocity * delta_time
            particle.life -= delta_time
            
            # Effect-specific updates
            if self.effect_type == EffectType.AURORA:
                self._update_aurora_particle(particle, delta_time)
            elif self.effect_type == EffectType.LIGHTNING:
                self._update_lightning_particle(particle, delta_time)
                
        # Emit new particles
        if self.active:
            self.emit_timer += delta_time
            while self.emit_timer >= 1.0 / self.emit_rate:
                self.emit_particle()
                self.emit_timer -= 1.0 / self.emit_rate
                
    def emit_particle(self) -> None:
        if self.effect_type == EffectType.AURORA:
            self._emit_aurora_particle()
        elif self.effect_type == EffectType.LIGHTNING:
            self._emit_lightning_particle()
        elif self.effect_type == EffectType.RAIN:
            self._emit_rain_particle()
        elif self.effect_type == EffectType.SNOW:
            self._emit_snow_particle()
            
    def _get_emit_rate(self) -> float:
        rates = {
            EffectType.AURORA: 100,
            EffectType.LIGHTNING: 500,
            EffectType.RAIN: 1000,
            EffectType.SNOW: 300
        }
        return rates[self.effect_type]
        
    def _get_particle_life(self) -> float:
        lives = {
            EffectType.AURORA: 5.0,
            EffectType.LIGHTNING: 0.1,
            EffectType.RAIN: 2.0,
            EffectType.SNOW: 8.0
        }
        return lives[self.effect_type]
        
    # Placeholder methods for emitter-specific particle updates
    def _update_aurora_particle(self, particle, delta_time):
        pass
        
    def _update_lightning_particle(self, particle, delta_time):
        pass
        
    def _emit_aurora_particle(self):
        pass
        
    def _emit_lightning_particle(self):
        pass
        
    def _emit_rain_particle(self):
        pass
        
    def _emit_snow_particle(self):
        pass

class EffectSystem:
    def __init__(self):
        # Fallback surface for software rendering
        self.fallback_surface = pygame.Surface((800, 600), pygame.SRCALPHA)  # Default size
        self.fallback_surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Fallback particle storage
        self.fallback_particles = []
        
        # OpenGL state
        self.using_gl = OPENGL_AVAILABLE
        
        self.emitters: List[ParticleEmitter] = []
        
        # Skip OpenGL initialization if not available
        if not self.using_gl:
            print("Using fallback effect rendering")
            self.particle_shader = 0
            self.particle_vao = 0
            return
            
        try:
            # Check if shader functions are available
            if not bool(glCreateShader):
                print("Shader functions not available for EffectSystem")
                self.using_gl = False
                self.particle_shader = 0
                self.particle_vao = 0
                return
                
            # Initialize shaders and buffers
            self.particle_shader = self._create_particle_shader()
            self.particle_vao = self._create_particle_vao()
        except Exception as e:
            print(f"Error initializing EffectSystem with OpenGL: {e}")
            self.using_gl = False
            self.particle_shader = 0
            self.particle_vao = 0
        
    def update(self, delta_time: float) -> None:
        # Update fallback particles if not using OpenGL
        if not self.using_gl:
            self._update_fallback_particles(delta_time)
            return
            
        try:
            # Update all emitters
            self.emitters = [e for e in self.emitters if e.active]
            for emitter in self.emitters:
                emitter.update(delta_time)
        except Exception as e:
            print(f"Error updating effects: {e}")
            
    def render(self, camera_matrix=None) -> None:
        if not self.using_gl:
            # Software rendering is handled by getting the fallback surface
            return
            
        try:
            glUseProgram(self.particle_shader)
            glBindVertexArray(self.particle_vao)
            
            # Update shader uniforms
            self._update_shader_uniforms(camera_matrix)
            
            # Render particles for each emitter
            for emitter in self.emitters:
                self._render_emitter_particles(emitter)
        except Exception as e:
            print(f"Error rendering effects: {e}")
            
    def get_surface(self, width=800, height=600):
        """Get the effect rendering surface for fallback mode."""
        # Resize if needed
        if (self.fallback_surface.get_width(), self.fallback_surface.get_height()) != (width, height):
            self.fallback_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
        # Clear the surface
        self.fallback_surface.fill((0, 0, 0, 0))
        
        # Draw particles
        for particle in self.fallback_particles:
            # Scale position from world space to screen space
            x = int(particle["position"][0]) + width // 2
            y = int(particle["position"][1]) + height // 2
            
            # Make sure particle is on screen
            if 0 <= x < width and 0 <= y < height:
                # Draw the particle
                if particle["type"] == "rain":
                    pygame.draw.line(
                        self.fallback_surface, 
                        particle["color"],
                        (x, y), 
                        (x + particle["velocity"][0], y + particle["velocity"][1]),
                        1
                    )
                elif particle["type"] == "snow":
                    pygame.draw.circle(
                        self.fallback_surface,
                        particle["color"],
                        (x, y),
                        particle["size"]
                    )
                elif particle["type"] == "lightning":
                    # Draw lightning as a series of connected line segments
                    # This is just a simple approximation
                    pygame.draw.circle(
                        self.fallback_surface,
                        particle["color"],
                        (x, y),
                        particle["size"] * 2,  # Bigger for visibility
                        0  # Filled
                    )
                else:  # Default particle rendering
                    pygame.draw.circle(
                        self.fallback_surface,
                        particle["color"],
                        (x, y),
                        particle["size"]
                    )
                    
        return self.fallback_surface
        
    def _update_fallback_particles(self, delta_time):
        """Update fallback particle simulation."""
        # Update existing particles
        new_particles = []
        for particle in self.fallback_particles:
            # Update position
            particle["position"][0] += particle["velocity"][0] * delta_time
            particle["position"][1] += particle["velocity"][1] * delta_time
            
            # Update life
            particle["life"] -= delta_time
            
            # Keep if still alive
            if particle["life"] > 0:
                new_particles.append(particle)
                
        self.fallback_particles = new_particles
        
        # Add new particles based on active weather or effects
        # In a real implementation, this would check scene state
        if len(self.fallback_particles) < 100 and random.random() < 0.1:
            self._add_fallback_particle()
            
    def _add_fallback_particle(self):
        """Add a new particle to the fallback system."""
        # Randomly choose particle type
        particle_type = random.choice(["rain", "snow"])
        
        if particle_type == "rain":
            self.fallback_particles.append({
                "type": "rain",
                "position": [random.uniform(-400, 400), -300],
                "velocity": [random.uniform(-20, -5), random.uniform(200, 300)],
                "color": (100, 150, 255, 150),
                "size": 1,
                "life": random.uniform(1.0, 2.0)
            })
        elif particle_type == "snow":
            self.fallback_particles.append({
                "type": "snow",
                "position": [random.uniform(-400, 400), -300],
                "velocity": [random.uniform(-10, 10), random.uniform(30, 60)],
                "color": (255, 255, 255, 200),
                "size": random.uniform(1, 3),
                "life": random.uniform(4.0, 8.0)
            })
        
    def spawn_aurora_particles(self, position: np.ndarray) -> None:
        emitter = ParticleEmitter(EffectType.AURORA)
        emitter.position = position
        self.emitters.append(emitter)
        
    def spawn_lightning(self, position: np.ndarray) -> None:
        emitter = ParticleEmitter(EffectType.LIGHTNING)
        emitter.position = position
        self.emitters.append(emitter)
        
    def spawn_rain(self, intensity=0.5):
        """Spawn rain effect (works in both GL and fallback modes)."""
        if self.using_gl:
            # Create Rain emitter
            emitter = ParticleEmitter(EffectType.RAIN)
            emitter.position = np.zeros(3)  # Rain comes from above
            self.emitters.append(emitter)
        else:
            # Add more fallback particles
            for _ in range(int(intensity * 100)):
                self.fallback_particles.append({
                    "type": "rain",
                    "position": [random.uniform(-400, 400), -300],
                    "velocity": [random.uniform(-20, -5), random.uniform(200, 300)],
                    "color": (100, 150, 255, 150),
                    "size": 1,
                    "life": random.uniform(1.0, 2.0)
                })
                
    def spawn_snow(self, intensity=0.5):
        """Spawn snow effect (works in both GL and fallback modes)."""
        if self.using_gl:
            # Create Snow emitter
            emitter = ParticleEmitter(EffectType.SNOW)
            emitter.position = np.zeros(3)  # Snow comes from above
            self.emitters.append(emitter)
        else:
            # Add more fallback particles
            for _ in range(int(intensity * 50)):
                self.fallback_particles.append({
                    "type": "snow",
                    "position": [random.uniform(-400, 400), -300],
                    "velocity": [random.uniform(-10, 10), random.uniform(30, 60)],
                    "color": (255, 255, 255, 200),
                    "size": random.uniform(1, 3),
                    "life": random.uniform(4.0, 8.0)
                })
        
    def _create_particle_shader(self) -> int:
        if not self.using_gl:
            return 0
            
        try:
            vertex_shader = """
            #version 430
            layout(location = 0) in vec3 position;
            layout(location = 1) in vec3 velocity;
            layout(location = 2) in vec4 color;
            layout(location = 3) in float size;
            
            uniform mat4 viewProj;
            
            out vec4 v_color;
            
            void main() {
                gl_Position = viewProj * vec4(position, 1.0);
                gl_PointSize = size;
                v_color = color;
            }
            """
            
            fragment_shader = """
            #version 430
            in vec4 v_color;
            
            out vec4 fragColor;
            
            void main() {
                vec2 coord = gl_PointCoord * 2.0 - 1.0;
                float r = dot(coord, coord);
                if (r > 1.0) discard;
                
                float alpha = smoothstep(1.0, 0.0, r);
                fragColor = v_color * alpha;
            }
            """
            
            return self._compile_shader_program(vertex_shader, fragment_shader)
        except Exception as e:
            print(f"Error creating particle shader: {e}")
            return 0
        
    def _create_particle_vao(self) -> int:
        if not self.using_gl:
            return 0
            
        try:
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            
            # Create buffers for particle attributes
            position_buffer = glGenBuffers(1)
            velocity_buffer = glGenBuffers(1)
            color_buffer = glGenBuffers(1)
            size_buffer = glGenBuffers(1)
            
            glBindBuffer(GL_ARRAY_BUFFER, position_buffer)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(0)
            
            glBindBuffer(GL_ARRAY_BUFFER, velocity_buffer)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(1)
            
            glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
            glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(2)
            
            glBindBuffer(GL_ARRAY_BUFFER, size_buffer)
            glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(3)
            
            return vao
        except Exception as e:
            print(f"Error creating particle VAO: {e}")
            return 0
        
    def _compile_shader_program(self, vertex_src: str, fragment_src: str) -> int:
        if not self.using_gl:
            return 0
            
        try:
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
        except Exception as e:
            print(f"Error compiling shader program: {e}")
            return 0
            
    def _update_shader_uniforms(self, camera_matrix):
        """Update shader uniforms with camera data."""
        if not self.using_gl or not self.particle_shader:
            return
            
        try:
            if camera_matrix is not None:
                view_proj_loc = glGetUniformLocation(self.particle_shader, "viewProj")
                if view_proj_loc != -1:
                    glUniformMatrix4fv(view_proj_loc, 1, GL_FALSE, camera_matrix)
        except Exception as e:
            print(f"Error updating shader uniforms: {e}")
            
    def _render_emitter_particles(self, emitter):
        """Render particles for a specific emitter."""
        if not self.using_gl or not self.particle_shader or not self.particle_vao:
            return
            
        try:
            if not emitter.particles:
                return
                
            # Prepare particle data for rendering
            positions = np.array([p.position for p in emitter.particles], dtype=np.float32)
            velocities = np.array([p.velocity for p in emitter.particles], dtype=np.float32)
            colors = np.array([p.color for p in emitter.particles], dtype=np.float32)
            sizes = np.array([p.size for p in emitter.particles], dtype=np.float32)
            
            # Update buffers
            glBindVertexArray(self.particle_vao)
            
            # Position buffer
            position_buffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, position_buffer)
            glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STREAM_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            
            # Velocity buffer
            velocity_buffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, velocity_buffer)
            glBufferData(GL_ARRAY_BUFFER, velocities.nbytes, velocities, GL_STREAM_DRAW)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
            
            # Color buffer
            color_buffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
            glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STREAM_DRAW)
            glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 0, None)
            
            # Size buffer
            size_buffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, size_buffer)
            glBufferData(GL_ARRAY_BUFFER, sizes.nbytes, sizes, GL_STREAM_DRAW)
            glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 0, None)
            
            # Draw particles
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDrawArrays(GL_POINTS, 0, len(emitter.particles))
            
            # Clean up
            glDeleteBuffers(4, [position_buffer, velocity_buffer, color_buffer, size_buffer])
            
        except Exception as e:
            print(f"Error rendering particles: {e}")
            
    def cleanup(self):
        """Clean up OpenGL resources."""
        if not self.using_gl:
            return
            
        try:
            if self.particle_shader:
                glDeleteProgram(self.particle_shader)
                
            if self.particle_vao:
                glDeleteVertexArrays(1, [self.particle_vao])
        except Exception as e:
            print(f"Error cleaning up EffectSystem: {e}")