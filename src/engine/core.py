# src/engine/core.py
import pygame
from pygame.locals import *
import sys
import time
import numpy as np
import os

# Import OpenGL with error handling
try:
    from OpenGL.GL import GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, \
                         GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_CONTEXT_PROFILE_CORE, \
                         GL_TEXTURE_2D, GL_UNSIGNED_BYTE, GL_RGB, GL_RGBA, \
                         glEnable, glDisable, glClearColor, glClear, glViewport, \
                         glBlendFunc, glBindTexture, glActiveTexture
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL not available, software rendering will be used")

# from .renderer import Renderer  # Commented out original import
from .window import Window
from .physics.verlet_system import PhysicsSystem
from .ui.hud import GameHUD
from .ui.menu import MenuManager  # Import just MenuManager from menu.py
from .ui.menus.main_menu import MainMenu  # Import MainMenu from menus/main_menu.py
# Remove direct imports that can cause circular dependencies
from .scenes.demo_scene import DemoScene # Original import
from .scenes.game.game_scene import GameScene  # Import GameScene
from .scenes.game.character_creation_scene import CharacterCreationScene  # Import CharacterCreationScene

# Create OpenGLContext for 3D rendering
class OpenGLContext:
    def __init__(self):
        self.active = False
        self.width = 0
        self.height = 0
        self.shader_manager = None
        self.texture_manager = None
        
    def initialize(self, width, height):
        """
        Initialize the OpenGL context with the given dimensions.
        
        Args:
            width (int): Viewport width.
            height (int): Viewport height.
        """
        print("Initializing OpenGL context")
        
        self.width = width
        self.height = height
        
        if not OPENGL_AVAILABLE:
            print("OpenGL libraries not available, falling back to software rendering")
            return False
        
        try:
            # Set up OpenGL context
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
            
            # Create OpenGL surface
            pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
            
            # Initialize OpenGL state
            glViewport(0, 0, width, height)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Initialize shader manager
            from .rendering.shader_manager import ShaderManager
            self.shader_manager = ShaderManager()
            
            # Initialize texture manager (would be implemented in texture_manager.py)
            # self.texture_manager = TextureManager()
            
            # Set active flag
            self.active = True
            
            print("OpenGL initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing OpenGL: {e}")
            self.active = False
            return False
            
    def resize(self, width, height):
        """
        Resize the OpenGL viewport.
        
        Args:
            width (int): New viewport width.
            height (int): New viewport height.
        """
        if not self.active or not OPENGL_AVAILABLE:
            return
            
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
            
    def draw_mesh(self, mesh, shader_program, textures=None, model_matrix=None):
        """
        Draw a mesh with the given shader program and textures.
        
        Args:
            mesh: The mesh to draw.
            shader_program: The shader program to use.
            textures: Optional textures to bind.
            model_matrix: Optional model transformation matrix.
        """
        if not self.active or not OPENGL_AVAILABLE:
            return
            
        # This would be implemented for 3D rendering
        pass
        
    def clear(self, color=(0.1, 0.1, 0.2, 1.0)):
        """
        Clear the OpenGL framebuffer.
        
        Args:
            color: Clear color (r, g, b, a) in [0, 1] range.
        """
        if not self.active or not OPENGL_AVAILABLE:
            return
            
        glClearColor(*color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
    def cleanup(self):
        """Clean up OpenGL resources."""
        if not self.active or not OPENGL_AVAILABLE:
            return
            
        # Clean up shader manager
        if self.shader_manager:
            self.shader_manager.cleanup()
            
        # Clean up texture manager
        if self.texture_manager:
            self.texture_manager.cleanup()
            
        self.active = False
        print("OpenGL context cleaned up")

# Placeholder Renderer class until proper implementation
class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = None
        self.gl_context = None
        self.enable_debug_rendering = True
        
    def initialize_gl(self, width, height):
        """Initialize OpenGL context if possible."""
        self.gl_context = OpenGLContext()
        success = self.gl_context.initialize(width, height)
        
        if not success:
            print("Using software rendering instead")
            
        return success
        
    def set_screen(self, screen):
        self.screen = screen
        
    def clear(self):
        # Try to use OpenGL clearing if available
        if self.gl_context and self.gl_context.active:
            self.gl_context.clear()
        elif self.screen:
            # Fall back to pygame clearing
            self.screen.fill((0, 0, 0))
            
    def render_scene(self, scene):
        # Simple placeholder for rendering
        if not scene or not self.screen:
            return
            
        # In a real implementation, this would use OpenGL for 3D and pygame for 2D

class Engine:
    def __init__(self, window=None, window_width=1280, window_height=720, title="Nightfall Defenders"):
        # Pygame initialization
        pygame.init()
        self.clock = pygame.time.Clock()
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Create or use provided window
        if window is None:
            self.window = Window(window_width, window_height, title)
        else:
            self.window = window
            window_width = window.width
            window_height = window.height
            
        self.screen = self.window.get_screen()
        
        # Create renderer
        self.renderer = Renderer(window_width, window_height)
        self.renderer.set_screen(self.screen)
        
        # Try to initialize OpenGL
        self.using_opengl = self.renderer.initialize_gl(window_width, window_height)
        
        # ECS World
        from .ecs.world import World
        self.world = World()

        # Physics system
        self.physics_system = PhysicsSystem()
        
        # UI and Menu system
        self.menu_manager = MenuManager(self)
        
        # Create the main menu with delayed imports to avoid circular dependencies
        self._create_main_menu()
        
        # Game state
        self.is_running = False
        self.is_paused = False
        self.active_scene = None
        self.dt = 0  # Delta time
        
        # DEBUG
        self.enable_debug_rendering = True
        
        # Default frame rate limit
        self.frame_rate = 60
        self.fixed_time_step = 1.0 / self.frame_rate
        
        # Register system update handlers
        self.system_update_handlers = []
    
    def _ensure_directories(self):
        """Ensure required directories exist for the engine."""
        # Create graphics directory for HD2D rendering
        graphics_dir = os.path.join("src", "engine", "graphics")
        if not os.path.exists(graphics_dir):
            os.makedirs(graphics_dir)
            print(f"Created directory: {graphics_dir}")
            
            # Create a placeholder __init__.py file
            init_file = os.path.join(graphics_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write("# Graphics module for HD-2D rendering\n")
                
        # Create shader directory if it doesn't exist
        shader_dir = os.path.join("src", "engine", "shaders")
        if not os.path.exists(shader_dir):
            os.makedirs(shader_dir)
            print(f"Created directory: {shader_dir}")
            
        # Create assets directories
        asset_dirs = [
            os.path.join("assets", "sprites", "player", "male"),
            os.path.join("assets", "sprites", "player", "female"),
            os.path.join("assets", "sprites", "enemies"),
            os.path.join("assets", "sprites", "npc"),
            os.path.join("assets", "backgrounds"),
            os.path.join("assets", "ui")
        ]
        
        for directory in asset_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
                
        # Initialize procedural generator to create assets on first run
        try:
            from .rendering.procedural_generator import ProceduralGenerator
            
            # Check if we need to generate assets
            male_sprite_path = os.path.join("assets", "sprites", "player", "male", "default_idle.png")
            female_sprite_path = os.path.join("assets", "sprites", "player", "female", "default_idle.png")
            
            if not os.path.exists(male_sprite_path) or not os.path.exists(female_sprite_path):
                print("First run detected. Generating game assets...")
                generator = ProceduralGenerator()
                generator.initialize_all_assets()
                print("Asset generation complete.")
            else:
                print("Using existing game assets.")
                
        except ImportError:
            print("ProceduralGenerator not available, skipping asset generation.")
        except Exception as e:
            print(f"Error initializing procedural generator: {e}")
            print("Using default assets instead.")
    
    def _create_main_menu(self):
        # Initialize the main menu
        main_menu = MainMenu(
            width=self.window.width, 
            height=self.window.height,
            on_start_game=self.start_new_game,
            on_load_game=self.load_game,
            on_options=self.show_options,
            on_credits=self.show_credits,
            on_quit=self.quit
        )
        self.menu_manager.push_menu(main_menu)
        
    def run(self):
        """Main game loop"""
        self.is_running = True
        
        # Initialize main menu instead of directly loading a demo scene
        # We'll transition to the game scene when the player starts a new game
        
        last_time = time.time()
        accumulated_time = 0
        
        # Main game loop
        while self.is_running:
            # Calculate delta time
            current_time = time.time()
            frame_time = current_time - last_time
            last_time = current_time
            
            # Cap frame time to prevent spiral of death
            if frame_time > 0.25:
                frame_time = 0.25
                
            accumulated_time += frame_time
            
            # Process input events
            self.process_events()
            
            # Fixed update step
            while accumulated_time >= self.fixed_time_step:
                # Skip updates if paused or in menu
                if not (self.is_paused or self.menu_manager.is_menu_active):
                    self.fixed_update(self.fixed_time_step)
                accumulated_time -= self.fixed_time_step
            
            # Update menus always
            if self.menu_manager.is_menu_active:
                self.menu_manager.update(frame_time)
            
            # Variable update
            if not (self.is_paused or self.menu_manager.is_menu_active):
                self.update(frame_time)
            
            # Render
            self.render()
            
            # Cap frame rate
            self.clock.tick(self.frame_rate)
            self.dt = frame_time
        
        # Clean up
        self.shutdown()
    
    def fixed_update(self, dt):
        """Fixed timestep updates (physics, AI, etc.)"""
        # Update physics
        self.physics_system.update(dt)
        
        # Update active scene (fixed step)
        if self.active_scene:
            self.active_scene.fixed_update(dt)
            
        # Update systems
        for system in self.system_update_handlers:
            if hasattr(system, 'fixed_update'):
                system.fixed_update(dt)
    
    def update(self, dt):
        """Variable timestep updates (rendering, UI, etc.)"""
        # Update active scene
        if self.active_scene:
            self.active_scene.update(dt)
            
        # Update systems
        for system in self.system_update_handlers:
            if hasattr(system, 'update'):
                system.update(dt)

    def render(self):
        """Render the game"""
        # Clear screen
        self.renderer.clear()
        
        # Render game world
        if self.active_scene and not self.menu_manager.is_menu_active:
            self.active_scene.render(self.screen)
            
            # Render HUD if in gameplay and HUD exists
            if hasattr(self.active_scene, 'hud') and self.active_scene.hud is not None:
                self.active_scene.hud.draw(self.screen)
        
        # Render menus on top
        if self.menu_manager.is_menu_active:
            self.menu_manager.draw(self.screen)
        
        # Flip display buffer
        pygame.display.flip()
    
    def process_events(self):
        """Process input events"""
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                self.is_running = False
                return
            
            # Menu gets first priority on events
            if self.menu_manager.is_menu_active:
                if self.menu_manager.handle_event(event):
                    continue # Menu handled event, skip further processing
            
            # If not in menu, let active scene handle events
            elif self.active_scene:
                self.active_scene.handle_event(event)
            
            # Global keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                # ESC for pause menu (when in game)
                if event.key == pygame.K_ESCAPE and not self.menu_manager.is_menu_active:
                    # Create pause menu
                    print("Toggling pause")
                    self.is_paused = not self.is_paused
                    
                    # If pausing, show pause menu
                    if self.is_paused:
                        self.show_pause_menu()
                
                # DEBUG: F1 to toggle debug rendering
                elif event.key == pygame.K_F1:
                    self.enable_debug_rendering = not self.enable_debug_rendering
                    print(f"Debug rendering: {self.enable_debug_rendering}")
    
    def set_active_scene(self, scene):
        """Set the active game scene"""
        if self.active_scene:
            self.active_scene.exit()
        
        self.active_scene = scene
        
        if scene:
            scene.enter()
    
    def register_system(self, system):
        """Register a system to receive update calls"""
        self.system_update_handlers.append(system)
    
    def start_new_game(self):
        """Start a new game from the main menu"""
        print("Starting new game")
        
        # Close all menus
        self.menu_manager.clear_stack()
        
        # Import character creation scene lazily to avoid circular imports
        from .scenes.game.character_creation_scene import CharacterCreationScene
        
        # Create and show character creation scene
        character_creation = CharacterCreationScene(self.world, self.renderer, self.menu_manager, 
                                                   on_character_created=self.on_character_created)
        self.set_active_scene(character_creation)
        
    def on_character_created(self, character_data):
        """
        Called when character creation is complete.
        Transitions to the main game scene.
        
        Args:
            character_data (dict): The created character data.
        """
        print(f"Character creation complete: {character_data['name']}")
        
        # Import GameScene lazily to avoid circular imports
        from .scenes.game.game_scene import GameScene
        
        # Create main game scene
        game_scene = GameScene(self.world, self.renderer, self.menu_manager)
        
        # Set as active scene
        self.set_active_scene(game_scene)
    
    def load_game(self):
        """Load a saved game"""
        print("Loading saved game")
        # In a real implementation, this would show a save selection screen
        # For now, we'll just create a new game scene
        
        # Close all menus
        self.menu_manager.clear_stack()
        
        # Import GameScene lazily to avoid circular imports
        from .scenes.game.game_scene import GameScene
        
        # Create game scene
        game_scene = GameScene(self.world, self.renderer, self.menu_manager)
        
        # Set as active scene
        self.set_active_scene(game_scene)
    
    def show_pause_menu(self):
        """Show the pause menu"""
        from .ui.menus.pause_menu import PauseMenu
        
        pause_menu = PauseMenu(
            width=self.window.width, 
            height=self.window.height,
            on_resume=self.resume_game,
            on_save_game=self.save_game,
            on_load_game=self.load_game,
            on_options=self.show_options,
            on_quit=self.quit_to_main_menu
        )
        
        self.menu_manager.push_menu(pause_menu)
    
    def resume_game(self):
        """Resume the game from pause"""
        print("Resuming game")
        self.is_paused = False
        self.menu_manager.pop_menu()  # Remove pause menu
    
    def save_game(self):
        """Save the current game"""
        print("Saving game")
        # In a real implementation, this would save the game state
        # For now, just print a message
        
    def show_options(self):
        """Show the options menu"""
        print("Showing options menu")
        
        # Import options menu lazily to avoid circular imports
        try:
            from .ui.menus.options_menu import OptionsMenu
            
            # Create and show options menu
            options_menu = OptionsMenu(
                width=self.window.width, 
                height=self.window.height,
                on_save=self._on_save_options,
                on_cancel=self._on_cancel_options
            )
            
            self.menu_manager.push_menu(options_menu)
        except ImportError as e:
            print(f"Error loading options menu: {e}")

    def _on_save_options(self, settings):
        """Handle saving options from the options menu"""
        print(f"Saving settings: {settings}")
        # Apply settings here
        
        # Remove options menu
        self.menu_manager.pop_menu()
        
    def _on_cancel_options(self):
        """Handle cancelling options menu"""
        print("Cancelled options")
        self.menu_manager.pop_menu()
    
    def show_credits(self):
        """Show the credits screen"""
        print("Showing credits")
        # In a real implementation, this would show a credits screen
        
    def quit_to_main_menu(self):
        """Quit the current game and return to the main menu"""
        print("Quitting to main menu")
        
        # Unpause the game
        self.is_paused = False
        
        # Clear menu stack
        self.menu_manager.clear_stack()
        
        # Unload current scene
        if self.active_scene:
            self.active_scene.unload()
            self.active_scene = None
        
        # Create main menu
        self._create_main_menu()
    
    def quit(self):
        """Quit the game"""
        self.is_running = False
    
    def is_in_gameplay(self):
        """Return True if the game is in active gameplay state"""
        return (not self.menu_manager.is_menu_active and 
                self.active_scene is not None and 
                not self.is_paused)
    
    def on_pause_state_change(self, is_paused):
        """Called when pause state changes (e.g., from menu manager)"""
        self.is_paused = is_paused
    
    def shutdown(self):
        """Clean up resources before exit"""
        # Clean up active scene
        if self.active_scene:
            self.active_scene.unload()
            
        # Close window
        self.window.close()
        
        # Quit pygame
        pygame.quit()