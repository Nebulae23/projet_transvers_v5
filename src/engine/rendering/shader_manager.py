# src/engine/rendering/shader_manager.py

import os
from typing import Dict, List, Optional, Tuple, Any
import sys

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for shader manager, using fallback")

import numpy as np

class ShaderManager:
    """
    Shader management system for loading, compiling and using GLSL shaders.
    """
    def __init__(self, shader_base_path="src/engine/shaders"):
        """
        Initialize the shader manager.
        
        Args:
            shader_base_path (str): Base directory for shader files.
        """
        self.shader_base_path = shader_base_path
        self.shader_programs: Dict[str, int] = {}
        self.shaders: Dict[str, int] = {}
        self.active_program: Optional[int] = None
        
        # Keep track of uniform locations for each program
        self.uniform_locations: Dict[int, Dict[str, int]] = {}
        
        # Check if OpenGL is available and properly initialized
        self.gl_initialized = OPENGL_AVAILABLE
        
        if self.gl_initialized:
            # Check if key shader functions are available
            try:
                if not bool(glCreateShader):
                    print("Error: glCreateShader function not available")
                    self.gl_initialized = False
            except Exception as e:
                print(f"Error checking shader functions: {e}")
                self.gl_initialized = False
        
        print(f"Shader Manager initialized with base path: {shader_base_path}")
        
    def load_shader_program(self, name: str, vertex_path: str, fragment_path: str, geometry_path: Optional[str] = None) -> int:
        """
        Load and compile a shader program with vertex and fragment shaders.
        
        Args:
            name (str): Name to identify the shader program.
            vertex_path (str): Path to the vertex shader file, relative to shader_base_path.
            fragment_path (str): Path to the fragment shader file, relative to shader_base_path.
            geometry_path (Optional[str]): Path to the geometry shader file, if used.
            
        Returns:
            int: OpenGL shader program ID.
        """
        # Check if OpenGL is properly initialized
        if not self.gl_initialized:
            print(f"Error loading shader program '{name}': OpenGL not properly initialized")
            return 0
            
        try:
            # Load shader sources
            vertex_source = self._load_shader_source(vertex_path)
            fragment_source = self._load_shader_source(fragment_path)
            geometry_source = self._load_shader_source(geometry_path) if geometry_path else None
            
            # Compile individual shaders
            vertex_shader = self._compile_shader(vertex_source, GL_VERTEX_SHADER)
            if vertex_shader == 0:
                return 0
                
            fragment_shader = self._compile_shader(fragment_source, GL_FRAGMENT_SHADER)
            if fragment_shader == 0:
                return 0
                
            geometry_shader = None
            if geometry_source:
                geometry_shader = self._compile_shader(geometry_source, GL_GEOMETRY_SHADER)
                if geometry_shader == 0:
                    return 0
            
            # Store individual shaders for potential reuse
            shader_key = f"vertex:{vertex_path}"
            self.shaders[shader_key] = vertex_shader
            
            shader_key = f"fragment:{fragment_path}"
            self.shaders[shader_key] = fragment_shader
            
            if geometry_shader:
                shader_key = f"geometry:{geometry_path}"
                self.shaders[shader_key] = geometry_shader
            
            # Create shader program
            program = glCreateProgram()
            glAttachShader(program, vertex_shader)
            glAttachShader(program, fragment_shader)
            if geometry_shader:
                glAttachShader(program, geometry_shader)
                
            # Link program
            glLinkProgram(program)
            
            # Check for linking errors
            if not glGetProgramiv(program, GL_LINK_STATUS):
                info_log = glGetProgramInfoLog(program)
                raise RuntimeError(f"Shader program linking failed: {info_log}")
                
            # Clean up individual shaders after linking
            glDetachShader(program, vertex_shader)
            glDetachShader(program, fragment_shader)
            if geometry_shader:
                glDetachShader(program, geometry_shader)
                
            # Store program
            self.shader_programs[name] = program
            
            # Initialize uniform location cache for this program
            self.uniform_locations[program] = {}
            
            print(f"Successfully loaded shader program '{name}'")
            return program
            
        except Exception as e:
            print(f"Error loading shader program '{name}': {e}")
            return 0
            
    def _load_shader_source(self, relative_path: str) -> str:
        """
        Load shader source code from file.
        
        Args:
            relative_path (str): Path to shader file, relative to shader_base_path.
            
        Returns:
            str: Shader source code.
        """
        if not relative_path:
            return None
            
        full_path = os.path.join(self.shader_base_path, relative_path)
        try:
            with open(full_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading shader source from {full_path}: {e}")
            return None
            
    def _compile_shader(self, source: str, shader_type: int) -> int:
        """
        Compile a shader from source.
        
        Args:
            source (str): Shader source code.
            shader_type (int): Type of shader (GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER).
            
        Returns:
            int: OpenGL shader ID.
        """
        if not source:
            return 0
            
        try:
            # Create shader
            shader = glCreateShader(shader_type)
            glShaderSource(shader, source)
            
            # Compile shader
            glCompileShader(shader)
            
            # Check for compilation errors
            if not glGetShaderiv(shader, GL_COMPILE_STATUS):
                info_log = glGetShaderInfoLog(shader)
                shader_type_str = {
                    GL_VERTEX_SHADER: "vertex",
                    GL_FRAGMENT_SHADER: "fragment",
                    GL_GEOMETRY_SHADER: "geometry"
                }.get(shader_type, "unknown")
                
                print(f"{shader_type_str} shader compilation failed: {info_log}")
                return 0
                
            return shader
        except Exception as e:
            print(f"Error compiling shader: {e}")
            return 0
        
    def use_program(self, name: str) -> bool:
        """
        Activate a shader program for rendering.
        
        Args:
            name (str): Name of the shader program to use.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if name not in self.shader_programs:
            print(f"Shader program '{name}' not found")
            return False
            
        program = self.shader_programs[name]
        glUseProgram(program)
        self.active_program = program
        return True
        
    def get_program(self, name: str) -> int:
        """
        Get the OpenGL ID for a shader program.
        
        Args:
            name (str): Name of the shader program.
            
        Returns:
            int: OpenGL shader program ID.
        """
        return self.shader_programs.get(name, 0)
        
    def set_uniform(self, name: str, value: Any) -> bool:
        """
        Set a uniform value in the currently active shader program.
        
        Args:
            name (str): Name of the uniform variable.
            value (Any): Value to set. Type determines the uniform function to call.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.active_program:
            print("No active shader program")
            return False
            
        # Get uniform location (using cache if available)
        if name in self.uniform_locations[self.active_program]:
            location = self.uniform_locations[self.active_program][name]
        else:
            location = glGetUniformLocation(self.active_program, name)
            self.uniform_locations[self.active_program][name] = location
            
        if location == -1:
            # Uniform not found or not active
            return False
            
        # Set uniform based on value type
        try:
            if isinstance(value, int):
                glUniform1i(location, value)
            elif isinstance(value, float):
                glUniform1f(location, value)
            elif isinstance(value, bool):
                glUniform1i(location, int(value))
            elif isinstance(value, (list, tuple)):
                if len(value) == 2:
                    glUniform2f(location, *value)
                elif len(value) == 3:
                    glUniform3f(location, *value)
                elif len(value) == 4:
                    glUniform4f(location, *value)
                else:
                    print(f"Unsupported uniform vector size: {len(value)}")
                    return False
            elif isinstance(value, np.ndarray):
                # Handle matrices
                if value.shape == (2, 2):
                    glUniformMatrix2fv(location, 1, GL_FALSE, value)
                elif value.shape == (3, 3):
                    glUniformMatrix3fv(location, 1, GL_FALSE, value)
                elif value.shape == (4, 4):
                    glUniformMatrix4fv(location, 1, GL_FALSE, value)
                # Handle vectors
                elif value.shape == (2,):
                    glUniform2fv(location, 1, value)
                elif value.shape == (3,):
                    glUniform3fv(location, 1, value)
                elif value.shape == (4,):
                    glUniform4fv(location, 1, value)
                else:
                    print(f"Unsupported numpy array shape: {value.shape}")
                    return False
            else:
                print(f"Unsupported uniform type: {type(value)}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error setting uniform '{name}': {e}")
            return False
            
    def set_uniform_matrix(self, name: str, matrix, transpose: bool = False) -> bool:
        """
        Set a matrix uniform in the currently active shader program.
        
        Args:
            name (str): Name of the uniform variable.
            matrix: Matrix to set (compatible with glm matrices).
            transpose (bool): Whether to transpose the matrix.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.active_program:
            print("No active shader program")
            return False
            
        # Get uniform location (using cache if available)
        if name in self.uniform_locations[self.active_program]:
            location = self.uniform_locations[self.active_program][name]
        else:
            location = glGetUniformLocation(self.active_program, name)
            self.uniform_locations[self.active_program][name] = location
            
        if location == -1:
            # Uniform not found or not active
            return False
            
        try:
            # Handle glm matrices
            import glm
            if isinstance(matrix, glm.mat2):
                glUniformMatrix2fv(location, 1, transpose, glm.value_ptr(matrix))
            elif isinstance(matrix, glm.mat3):
                glUniformMatrix3fv(location, 1, transpose, glm.value_ptr(matrix))
            elif isinstance(matrix, glm.mat4):
                glUniformMatrix4fv(location, 1, transpose, glm.value_ptr(matrix))
            # Handle numpy arrays
            elif isinstance(matrix, np.ndarray):
                if matrix.shape == (2, 2):
                    glUniformMatrix2fv(location, 1, transpose, matrix)
                elif matrix.shape == (3, 3):
                    glUniformMatrix3fv(location, 1, transpose, matrix)
                elif matrix.shape == (4, 4):
                    glUniformMatrix4fv(location, 1, transpose, matrix)
                else:
                    print(f"Unsupported matrix shape: {matrix.shape}")
                    return False
            else:
                print(f"Unsupported matrix type: {type(matrix)}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error setting matrix uniform '{name}': {e}")
            return False
            
    def cleanup(self):
        """Clean up shader resources."""
        for program in self.shader_programs.values():
            glDeleteProgram(program)
            
        for shader in self.shaders.values():
            glDeleteShader(shader)
            
        self.shader_programs.clear()
        self.shaders.clear()
        self.uniform_locations.clear()
        self.active_program = None 