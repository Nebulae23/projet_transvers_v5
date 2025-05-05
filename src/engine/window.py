# src/engine/window.py
import pygame

class Window:
    def __init__(self, width=1280, height=720, title="Game Window", fullscreen=False):
        """
        Initialize pygame window
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        
        # Set up the display
        flags = 0
        if fullscreen:
            flags = pygame.FULLSCREEN
        
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)
        
        # Set up clock for timing
        self.clock = pygame.time.Clock()
        
        print(f"Window created ({width}x{height}, {'fullscreen' if fullscreen else 'windowed'})")
    
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
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        print(f"Toggled to {'fullscreen' if self.fullscreen else 'windowed'} mode")
        
    def clear(self, color=(0, 0, 0)):
        """
        Clear the screen with the given color
        """
        self.screen.fill(color)
        
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