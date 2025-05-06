# src/engine/rendering/shader_manager.py

import os
import pygame
import logging
from typing import Dict, List, Optional, Tuple, Any
import sys

# Conditionally import OpenGL
try:
    from OpenGL.GL import *
    from OpenGL.GL import shaders
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available in ShaderManager")

import numpy as np

class ShaderManager:
    """
    Manages shader programs, including loading, compilation, and caching.
    Also handles fallbacks when OpenGL is not available.
    """
    def __init__(self, base_path=None):
        """
        Initialize the shader manager
        
        Args:
            base_path (str): Base directory for shader files
        """
        # Set base path for shader files
        if base_path is None:
            self.base_path = os.path.join("src", "engine", "shaders")
        else:
            self.base_path = base_path
            
        print(f"Shader Manager initialized with base path: {self.base_path}")
            
        # Shader cache
        self.programs = {}
        self.using_opengl = OPENGL_AVAILABLE
        
        # Check if shader functions are actually available
        if self.using_opengl:
            try:
                self.using_opengl = bool(glCreateShader)
                if not self.using_opengl:
                    print("Error: glCreateShader function not available")
            except (AttributeError, TypeError) as e:
                self.using_opengl = False
                print(f"Error: Shader functions not available: {e}")
        
    def load_shader_program(self, name, vertex_filename, fragment_filename):
        """
        Load and compile a shader program from vertex and fragment shader files
        
        Args:
            name (str): Name to reference the shader program
            vertex_filename (str): Filename of vertex shader
            fragment_filename (str): Filename of fragment shader
            
        Returns:
            int: OpenGL program ID or None if failed
        """
        # Check if already loaded
        if name in self.programs:
            return self.programs[name].get("program")
            
        # Check OpenGL availability
        if not self.using_opengl:
            print(f"Error loading shader program '{name}': OpenGL not properly initialized")
            self.programs[name] = {"status": "error", "message": "OpenGL not available"}
            return None
            
        # Try to load and compile shaders
        try:
            # Build file paths
            vertex_path = os.path.join(self.base_path, vertex_filename)
            fragment_path = os.path.join(self.base_path, fragment_filename)
            
            # Ensure shader files exist
            if not os.path.exists(vertex_path):
                raise FileNotFoundError(f"Vertex shader file not found: {vertex_path}")
                
            if not os.path.exists(fragment_path):
                raise FileNotFoundError(f"Fragment shader file not found: {fragment_path}")
                
            # Read shader source files
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
                
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
                
            # Compile shaders
            vertex_shader = shaders.compileShader(vertex_source, GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER)
                
            # Link program
            program = shaders.compileProgram(vertex_shader, fragment_shader)
            
            # Cache and return
            self.programs[name] = {
                "program": program,
                "vertex": vertex_shader,
                "fragment": fragment_shader,
                "status": "loaded"
            }
            
            return program
            
        except Exception as e:
            print(f"Error loading shader program '{name}': {e}")
            self.programs[name] = {"status": "error", "message": str(e)}
            return None
            
    def use_program(self, name):
        """
        Use a shader program by name
        
        Args:
            name (str): Name of the shader program to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.using_opengl:
            return False
            
        program_info = self.programs.get(name)
        if not program_info or "program" not in program_info:
            return False
            
        try:
            glUseProgram(program_info["program"])
            return True
        except Exception as e:
            print(f"Error using shader program '{name}': {e}")
            return False
            
    def set_uniform(self, program_name, uniform_name, value):
        """
        Set a uniform value for a shader program
        
        Args:
            program_name (str): Name of the shader program
            uniform_name (str): Name of the uniform variable
            value: Value to set (type depends on uniform)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.using_opengl:
            return False
            
        program_info = self.programs.get(program_name)
        if not program_info or "program" not in program_info:
            return False
            
        program = program_info["program"]
        
        try:
            # Get uniform location
            location = glGetUniformLocation(program, uniform_name)
            if location == -1:
                return False  # Uniform not found or not active
                
            # Set uniform based on type
            if isinstance(value, bool):
                glUniform1i(location, int(value))
            elif isinstance(value, int):
                glUniform1i(location, value)
            elif isinstance(value, float):
                glUniform1f(location, value)
            elif isinstance(value, (list, tuple)):
                if len(value) == 2:
                    glUniform2f(location, *value)
                elif len(value) == 3:
                    glUniform3f(location, *value)
                elif len(value) == 4:
                    glUniform4f(location, *value)
                else:
                    return False  # Unsupported vector size
            else:
                return False  # Unsupported type
                
            return True
            
        except Exception as e:
            print(f"Error setting uniform '{uniform_name}' for shader '{program_name}': {e}")
            return False
            
    def cleanup(self):
        """
        Clean up shader resources (to be called on shutdown)
        """
        if not self.using_opengl:
            return
            
        for name, program_info in self.programs.items():
            if "program" in program_info:
                try:
                    glDeleteProgram(program_info["program"])
                except Exception as e:
                    print(f"Error deleting shader program '{name}': {e}")
            
        self.programs.clear() 