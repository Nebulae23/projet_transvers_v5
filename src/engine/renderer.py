# src/engine/renderer.py
# Uncomment and properly handle OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GL import shaders
    import numpy as np
    from PIL import Image
    import ctypes
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available, software rendering will be used")
import os # Pour joindre les chemins de shaders
import pygame

# Import OpenGLContext from core instead of defining it here
from .core import OpenGLContext

# TODO: Importer les futurs modules nécessaires
# from .rendering.post_process import PostProcessor
# from .rendering.shadows import ShadowManager
# from .rendering.materials import Material, PBRMaterial
# from .rendering.lights import PointLight, DirectionalLight, SpotLight
# from .rendering.gbuffer import GBuffer
# from .rendering.hdr import HDRFramebuffer

# Enhanced ShaderPipeline with proper fallback handling
class ShaderPipeline:
    def __init__(self):
        self.active_shader = None
        self.shaders = {}
        self.stages = {'geometry': None, 'lighting': None, 'post': None}
        self.using_opengl = OPENGL_AVAILABLE
        
        # Check if OpenGL shader functions are actually available
        if self.using_opengl:
            try:
                self.using_opengl = bool(glCreateShader)
                if not self.using_opengl:
                    print("Shader functions not available for ShaderPipeline")
            except (AttributeError, TypeError):
                self.using_opengl = False
                print("Shader functions not available for ShaderPipeline")
        
    def load_shader(self, name, vertex_path=None, fragment_path=None):
        """Load a shader program from vertex and fragment shader files"""
        self.shaders[name] = {"name": name}
        
        if not self.using_opengl:
            return self.shaders[name]
            
        try:
            # Read shader source code from files
            if vertex_path and fragment_path:
                with open(vertex_path, 'r') as vertex_file:
                    vertex_source = vertex_file.read()
                    
                with open(fragment_path, 'r') as fragment_file:
                    fragment_source = fragment_file.read()
                
                # Compile shaders
                vertex_shader = shaders.compileShader(vertex_source, GL_VERTEX_SHADER)
                fragment_shader = shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER)
                
                # Create program
                program = shaders.compileProgram(vertex_shader, fragment_shader)
                
                # Store in the dictionary
                self.shaders[name]["program"] = program
                self.shaders[name]["vertex"] = vertex_shader
                self.shaders[name]["fragment"] = fragment_shader
                
            self.stages[name] = self.shaders[name]
            return self.shaders[name]
            
        except Exception as e:
            print(f"Error loading shader {name}: {e}")
            return self.shaders[name]
        
    def use_shader(self, name):
        """Activate a shader program by name"""
        if not self.using_opengl:
            self.active_shader = name
            return
            
        if name in self.shaders and "program" in self.shaders[name]:
            self.active_shader = name
            glUseProgram(self.shaders[name]["program"])
        
    def use(self):
        """Use the currently active shader"""
        if not self.using_opengl:
            return
            
        if self.active_shader and self.active_shader in self.shaders and "program" in self.shaders[self.active_shader]:
            glUseProgram(self.shaders[self.active_shader]["program"])
            
    def set_uniform(self, name, value):
        """Set a uniform value in the current shader"""
        if not self.using_opengl or not self.active_shader:
            return
            
        shader = self.shaders.get(self.active_shader)
        if not shader or "program" not in shader:
            return
            
        try:
            # Get uniform location
            location = glGetUniformLocation(shader["program"], name)
            
            # Set value based on type
            if isinstance(value, (int, bool)):
                glUniform1i(location, value)
            elif isinstance(value, float):
                glUniform1f(location, value)
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                glUniform2f(location, *value)
            elif isinstance(value, (list, tuple)) and len(value) == 3:
                glUniform3f(location, *value)
            elif isinstance(value, (list, tuple)) and len(value) == 4:
                glUniform4f(location, *value)
            # Add more types as needed
            
        except Exception as e:
            print(f"Error setting uniform {name}: {e}")
        
    def get_active_shader(self):
        """Return the currently active shader"""
        return self.active_shader

# Comment out complex classes for now
# These will be implemented in future updates

# class Camera:
#     def __init__(self, width, height, position=pyrr.Vector3([0.0, 5.0, 10.0]), front=pyrr.Vector3([0.0, 0.0, -1.0]), up=pyrr.Vector3([0.0, 1.0, 0.0])):
#         # Implementation...

# class Shader:
#     def __init__(self, vertex_path, fragment_path, geometry_path=None):
#         # Implementation...

# class Renderer:
#     def __init__(self, width, height):
#         # Implementation...

# Note: Les fichiers shader référencés (ex: "shaders/g_buffer.vs") n'existent pas encore.
# Il faudra les créer dans les étapes suivantes.
# De même pour les classes importées (GBuffer, HDRFramebuffer, PostProcessor, etc.)