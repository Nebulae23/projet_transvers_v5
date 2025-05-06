# src/engine/window.py
import pygame

# Try to import OpenGL
try:
    from OpenGL.GL import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available for Window class")

class Window:
    def __init__(self, width=1280, height=720, title="Game Window", fullscreen=False, use_opengl=True):
        """
        Initialize pygame window
        
        Args:
            width (int): Window width
            height (int): Window height
            title (str): Window title
            fullscreen (bool): Whether to start in fullscreen mode
            use_opengl (bool): Whether to initialize with OpenGL support
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        
        # Set OpenGL attributes if requested and available
        self.using_opengl = use_opengl and OPENGL_AVAILABLE
        
        if self.using_opengl:
            print("Setting up OpenGL window...")
            # Set up OpenGL context attributes
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
        
        # Set up the display with appropriate flags
        flags = 0
        if fullscreen:
            flags |= pygame.FULLSCREEN
        if self.using_opengl:
            flags |= pygame.OPENGL | pygame.DOUBLEBUF
        
        try:
            self.screen = pygame.display.set_mode((width, height), flags)
            mode_str = 'OpenGL' if self.using_opengl else 'software rendering'
            print(f"Window created ({width}x{height}, {'fullscreen' if fullscreen else 'windowed'}, {mode_str})")
        except pygame.error as e:
            print(f"Error creating window: {e}")
            # Fallback to software rendering if OpenGL fails
            if self.using_opengl:
                print("Falling back to software rendering")
                self.using_opengl = False
                flags &= ~(pygame.OPENGL | pygame.DOUBLEBUF)
                self.screen = pygame.display.set_mode((width, height), flags)
        
        # Set up clock for timing
        self.clock = pygame.time.Clock()
    
    def is_using_opengl(self):
        """
        Check if window is using OpenGL
        
        Returns:
            bool: True if using OpenGL, False otherwise
        """
        return self.using_opengl
    
    def get_screen(self):
        """
        Get the pygame screen surface
        """
        return self.screen
    
    def get_size(self):
        """
        Get window dimensions
        """
        return (self.width, self.height)
    
    def set_title(self, title):
        """
        Set window title
        """
        self.title = title
        pygame.display.set_caption(title)
        
    def toggle_fullscreen(self):
        """
        Toggle between fullscreen and windowed mode
        """
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        if self.using_opengl:
            flags |= pygame.OPENGL | pygame.DOUBLEBUF
        
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        print(f"Toggled to {'fullscreen' if self.fullscreen else 'windowed'} mode")
        
    def clear(self, color=(0, 0, 0)):
        """
        Clear the screen with the given color
        """
        if not self.using_opengl:
            self.screen.fill(color)
        # Note: OpenGL clearing is handled by the renderer/OpenGLContext
        
    def swap_buffers(self):
        """
        Update the display (swap buffers)
        """
        pygame.display.flip()
        
    def should_close(self):
        """
        Check if window should close (e.g., user clicked X)
        """
        for event in pygame.event.get(pygame.QUIT):
            if event.type == pygame.QUIT:
                return True
        return False
        
    def close(self):
        """
        Close the window
        """
        pygame.quit()
        print("Window closed")