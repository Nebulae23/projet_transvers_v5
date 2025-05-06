import traceback
import pygame
import numpy as np
from typing import Tuple, Dict, Any, Optional, List

# Import OpenGL with error handling
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for UI rendering, falling back to software rendering")

class OpenGLUIRenderer:
    """
    Renderer for UI elements using OpenGL.
    Handles rendering rectangles, text, and images for the UI system.
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.text_cache = {}  # Cache for text textures
        self.image_cache = {}  # Cache for image textures
        self.shader_program = None
        self.using_opengl = OPENGL_AVAILABLE
        self.debug = False  # Set to False to disable debug messages
        
        # Initialize OpenGL resources if available
        if self.using_opengl:
            self._initialize_gl()
    
    def _initialize_gl(self):
        """Initialize OpenGL resources"""
        if not self.using_opengl:
            print("OpenGL not available, UI renderer initialized for fallback mode")
            return
            
        try:
            # Create shader program
            self._create_ui_shader()
            
            # Create and bind VAO and VBO
            self.vao = glGenVertexArrays(1)
            self.vbo = glGenBuffers(1)
            
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            
            # Create rectangle vertices (position and texture coordinates)
            self.rect_vertices = np.array([
                # Position (x, y)  # TexCoords (s, t)
                0.0, 0.0,          0.0, 0.0,  # bottom-left
                1.0, 0.0,          1.0, 0.0,  # bottom-right
                1.0, 1.0,          1.0, 1.0,  # top-right
                0.0, 1.0,          0.0, 1.0   # top-left
            ], dtype=np.float32)
            
            # Set vertex buffer data
            glBufferData(GL_ARRAY_BUFFER, self.rect_vertices.nbytes, self.rect_vertices, GL_STATIC_DRAW)
            
            # Position attribute
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            
            # Texture coordinate attribute
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), ctypes.c_void_p(2 * sizeof(GLfloat)))
            glEnableVertexAttribArray(1)
            
            # Create elements/indices for drawing quads
            self.indices = np.array([
                0, 1, 2,  # First triangle
                2, 3, 0   # Second triangle
            ], dtype=np.uint32)
            
            # Create and bind EBO
            self.ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
            
            # Unbind VAO
            glBindVertexArray(0)
            
            # Setup orthographic projection matrix
            self.projection = glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1.0, 1.0)
            
            # Enable blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            if self.debug:
                print("OpenGL UI renderer initialized successfully")
                print(f"Screen dimensions: {self.width}x{self.height}")
                print(f"Shader program: {self.shader_program}")
                print(f"VAO: {self.vao}, VBO: {self.vbo}, EBO: {self.ebo}")
                
        except Exception as e:
            print(f"Error initializing OpenGL UI renderer: {e}")
            traceback.print_exc()
            self.using_opengl = False
    
    def _create_ui_shader(self):
        """Create basic shader for UI rendering"""
        if not self.using_opengl:
            return
            
        # Vertex shader
        vertex_shader = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;
        
        out vec2 TexCoord;
        
        uniform mat4 model;
        uniform mat4 projection;
        
        void main()
        {
            gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
        }
        """
        
        # Fragment shader
        fragment_shader = """
        #version 330 core
        in vec2 TexCoord;
        
        out vec4 FragColor;
        
        uniform sampler2D textureSampler;
        uniform vec4 color;
        uniform bool useTexture;
        
        void main()
        {
            if (useTexture)
            {
                vec4 texColor = texture(textureSampler, TexCoord);
                FragColor = texColor * color;
            }
            else
            {
                FragColor = color;
            }
        }
        """
        
        try:
            # Compile vertex shader
            vertex = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex, vertex_shader)
            glCompileShader(vertex)
            
            # Check for shader compile errors
            success = glGetShaderiv(vertex, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(vertex)
                print(f"ERROR::SHADER::VERTEX::COMPILATION_FAILED\n{info_log}")
                return
            
            # Compile fragment shader
            fragment = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment, fragment_shader)
            glCompileShader(fragment)
            
            # Check for shader compile errors
            success = glGetShaderiv(fragment, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(fragment)
                print(f"ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n{info_log}")
                return
            
            # Link shaders
            self.shader_program = glCreateProgram()
            glAttachShader(self.shader_program, vertex)
            glAttachShader(self.shader_program, fragment)
            glLinkProgram(self.shader_program)
            
            # Check for linking errors
            success = glGetProgramiv(self.shader_program, GL_LINK_STATUS)
            if not success:
                info_log = glGetProgramInfoLog(self.shader_program)
                print(f"ERROR::SHADER::PROGRAM::LINKING_FAILED\n{info_log}")
                return
            
            # Delete the shaders as they're linked into our program now and no longer necessary
            glDeleteShader(vertex)
            glDeleteShader(fragment)
            
            if self.debug:
                print(f"UI shader program created successfully: {self.shader_program}")
        
        except Exception as e:
            print(f"Error creating UI shader: {e}")
            traceback.print_exc()
            self.shader_program = None
    
    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int, int]):
        """Draw a rectangle with OpenGL"""
        if not self.using_opengl or not self.shader_program:
            return
        
        try:
            if self.debug:
                print(f"OpenGL UI: Drawing rectangle at ({x}, {y}) size: {width}x{height} color: {color}")
            
            # Save GL state
            previous_blend_state = glIsEnabled(GL_BLEND)
            previous_depth_test_state = glIsEnabled(GL_DEPTH_TEST)
            
            # Setup GL state for UI drawing
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_DEPTH_TEST)
            
            # Use shader program
            glUseProgram(self.shader_program)
            
            # Create model matrix
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(x, y, 0.0))
            model = glm.scale(model, glm.vec3(width, height, 1.0))
            
            # Set projection and model matrices
            projection_loc = glGetUniformLocation(self.shader_program, "projection")
            model_loc = glGetUniformLocation(self.shader_program, "model")
            glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(self.projection))
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
            
            # Set texture flag (0 = no texture, using color)
            texture_flag_loc = glGetUniformLocation(self.shader_program, "useTexture")
            glUniform1i(texture_flag_loc, 0)
            
            # Set color with alpha handling
            color_loc = glGetUniformLocation(self.shader_program, "color")
            r = color[0] / 255.0
            g = color[1] / 255.0
            b = color[2] / 255.0
            a = color[3] / 255.0 if len(color) > 3 else 1.0
            glUniform4f(color_loc, r, g, b, a)
            
            # Bind VAO and draw
            glBindVertexArray(self.vao)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            
            # Restore previous GL state
            if not previous_blend_state:
                glDisable(GL_BLEND)
            if previous_depth_test_state:
                glEnable(GL_DEPTH_TEST)
                
        except Exception as e:
            print(f"Error drawing rectangle: {e}")
            traceback.print_exc()
    
    def _ensure_consistent_orientation(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Ensure that the texture will be displayed in the correct orientation.
        This method is used to fix any orientation issues before creating textures.
        """
        if self.debug:
            print(f"Ensuring consistent orientation for surface: {surface.get_size()}")
            
        # Ensure the surface has the right format with alpha channel
        if surface.get_bitsize() != 32:
            surface = surface.convert_alpha()
        
        # Return the prepared surface
        return surface
        
    def create_texture_from_surface(self, surface: pygame.Surface) -> int:
        """Convert a pygame surface to an OpenGL texture"""
        if not self.using_opengl:
            return 0
            
        try:
            # Get the size of the surface
            width, height = surface.get_size()
            
            if width <= 0 or height <= 0:
                if self.debug:
                    print(f"Warning: Invalid surface size ({width}x{height})")
                return 0
                
            # Create texture
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Get pixel data from pygame surface
            # Convert to RGBA if needed
            if surface.get_bitsize() != 32:
                surface = surface.convert_alpha()
                
            # Use flipped=0 to prevent vertical flipping when converting to OpenGL texture
            data = pygame.image.tostring(surface, "RGBA", 0)  # Changed from 1 to 0
            
            # Upload data to texture
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            
            if self.debug:
                print(f"Created texture ID: {texture} with size: {width}x{height}")
                
            return texture
            
        except Exception as e:
            print(f"Error creating texture: {e}")
            return 0
    
    def draw_texture(self, texture_id: int, x: int, y: int, width: int, height: int, color: Tuple[int, int, int, int]=(255, 255, 255, 255)):
        """Draw a texture with OpenGL"""
        if not self.using_opengl or not self.shader_program or texture_id == 0:
            return
            
        try:
            if self.debug:
                print(f"OpenGL UI: Drawing texture {texture_id} at ({x}, {y}) size: {width}x{height}")
            
            # Save GL state
            previous_blend_state = glIsEnabled(GL_BLEND)
            previous_depth_test_state = glIsEnabled(GL_DEPTH_TEST)
            
            # Setup GL state for UI drawing
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_DEPTH_TEST)
            
            # Use shader program
            glUseProgram(self.shader_program)
            
            # Create model matrix
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(x, y, 0.0))
            model = glm.scale(model, glm.vec3(width, height, 1.0))
            
            # Set projection and model matrices
            projection_loc = glGetUniformLocation(self.shader_program, "projection")
            model_loc = glGetUniformLocation(self.shader_program, "model")
            glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(self.projection))
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
            
            # Set texture flag (1 = use texture)
            texture_flag_loc = glGetUniformLocation(self.shader_program, "useTexture")
            glUniform1i(texture_flag_loc, 1)
            
            # Set color (for tinting) with alpha handling
            color_loc = glGetUniformLocation(self.shader_program, "color")
            r = color[0] / 255.0
            g = color[1] / 255.0
            b = color[2] / 255.0
            a = color[3] / 255.0 if len(color) > 3 else 1.0
            glUniform4f(color_loc, r, g, b, a)
            
            # Bind texture
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Set texture uniform
            texture_loc = glGetUniformLocation(self.shader_program, "textureSampler")
            glUniform1i(texture_loc, 0)
            
            # Bind VAO and draw
            glBindVertexArray(self.vao)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            
            # Unbind texture
            glBindTexture(GL_TEXTURE_2D, 0)
            
            # Restore previous GL state
            if not previous_blend_state:
                glDisable(GL_BLEND)
            if previous_depth_test_state:
                glEnable(GL_DEPTH_TEST)
                
        except Exception as e:
            print(f"Error drawing texture: {e}")
            traceback.print_exc()
    
    def draw_texture_debug(self, texture_id: int, x: int, y: int, width: int, height: int):
        """
        Draw a texture with visual debug aids to help identify orientation issues.
        This draws a colored border around the texture with different colors for each corner.
        """
        if not self.using_opengl or not self.shader_program or texture_id == 0 or not self.debug:
            return
            
        # First draw the texture normally
        self.draw_texture(texture_id, x, y, width, height)
        
        # Draw colored borders to indicate orientation
        border_width = max(2, min(width, height) // 20)  # Scale border with texture size
        
        # Top border (red)
        self.draw_rectangle(x, y, width, border_width, (255, 0, 0, 200))
        
        # Right border (green)
        self.draw_rectangle(x + width - border_width, y, border_width, height, (0, 255, 0, 200))
        
        # Bottom border (blue)
        self.draw_rectangle(x, y + height - border_width, width, border_width, (0, 0, 255, 200))
        
        # Left border (yellow)
        self.draw_rectangle(x, y, border_width, height, (255, 255, 0, 200))
        
        # Draw corner markers
        corner_size = border_width * 2
        
        # Top-left (cyan)
        self.draw_rectangle(x, y, corner_size, corner_size, (0, 255, 255, 200))
        
        # Top-right (magenta)
        self.draw_rectangle(x + width - corner_size, y, corner_size, corner_size, (255, 0, 255, 200))
        
        # Bottom-right (white)
        self.draw_rectangle(x + width - corner_size, y + height - corner_size, corner_size, corner_size, (255, 255, 255, 200))
        
        # Bottom-left (gray)
        self.draw_rectangle(x, y + height - corner_size, corner_size, corner_size, (128, 128, 128, 200))
    
    def render_text(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int, int], x: int, y: int):
        """Render text using OpenGL"""
        if not self.using_opengl:
            return
            
        if self.debug:
            print(f"OpenGL UI: Rendering text '{text}' at ({x}, {y}) with color {color}")
            
        # Create or retrieve cached texture for the text
        cache_key = (text, font, color)
        if cache_key in self.text_cache:
            texture_id, text_width, text_height = self.text_cache[cache_key]
            if self.debug:
                print(f"Using cached text texture: {texture_id} ({text_width}x{text_height})")
        else:
            # Create pygame surface for the text
            text_surface = font.render(text, True, color)
            text_width, text_height = text_surface.get_size()
            
            # Create texture from surface
            texture_id = self.create_texture_from_surface(text_surface)
            
            if texture_id:
                # Cache the texture
                self.text_cache[cache_key] = (texture_id, text_width, text_height)
            else:
                print(f"Failed to create texture for text: {text}")
                return
                
        # Draw the text texture
        self.draw_texture(texture_id, x, y, text_width, text_height)
    
    def load_image(self, path: str) -> Tuple[int, int, int]:
        """Load an image and create an OpenGL texture from it"""
        if not self.using_opengl:
            return 0, 0, 0
            
        # Check if already cached
        if path in self.image_cache:
            return self.image_cache[path]
            
        try:
            # Load image using pygame
            image = pygame.image.load(path)
            width, height = image.get_size()
            
            # Create OpenGL texture
            texture_id = self.create_texture_from_surface(image)
            
            # Cache the texture
            if texture_id != 0:
                self.image_cache[path] = (texture_id, width, height)
                return texture_id, width, height
            
        except Exception as e:
            print(f"Error loading image {path}: {e}")
        
        return 0, 0, 0
    
    def cleanup(self):
        """Clean up OpenGL resources"""
        if not self.using_opengl:
            return
            
        try:
            # Delete all textures
            for texture_id, _, _ in self.text_cache.values():
                glDeleteTextures(1, [texture_id])
            
            for texture_id, _, _ in self.image_cache.values():
                glDeleteTextures(1, [texture_id])
            
            # Delete VAO and VBO
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])
            glDeleteBuffers(1, [self.ebo])
            
            # Delete shader program
            if self.shader_program:
                glDeleteProgram(self.shader_program)
                
            print("OpenGL UI renderer resources cleaned up")
            
        except Exception as e:
            print(f"Error cleaning up OpenGL UI renderer: {e}")
    
    def resize(self, width: int, height: int):
        """Update renderer size and viewport"""
        if self.width == width and self.height == height:
            return
            
        self.width = width
        self.height = height
        
        if self.debug:
            print(f"OpenGL UI renderer resized to {width}x{height}")
            
        # We don't actually change the viewport here, as that's handled
        # by the core engine. We just update our internal dimensions for
        # the projection matrix calculations. 