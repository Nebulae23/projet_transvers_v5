# src/engine/scenes/game/game_scene.py

import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

from ...ecs.world import World
from ...ecs.components import Transform, Sprite, Animation, PhysicsBody
from ..scene import Scene
from ...ui.hud.game_hud import GameHUD

# Import rendering systems
from ...rendering.billboard_system import BillboardSystem
from ...rendering.world_renderer import WorldRenderer
from ...rendering.effect_system import EffectSystem

# Import 3D libraries (wrapped in try/except for fallback support)
try:
    from OpenGL.GL import *
    import glm
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("Warning: OpenGL and glm libraries not available, using fallback rendering")

# Lazy imports to avoid circular dependencies
# from ...city.city_manager import CityManager
# from ...combat.combat_system import CombatSystem
# from ...weather.weather_system import WeatherSystem
# from ...time.day_night_cycle import DayNightCycle
# from ...time.time_manager import TimeManager
# from ...inventory.inventory import InventorySystem

class GameScene(Scene):
    """
    Main game scene implementation with Octopath-inspired style (3D world, 2D entities).
    Integrates all major game systems: city, combat, weather, day/night cycle, etc.
    """
    def __init__(self, world: World, renderer, ui_manager):
        """
        Initialize the game scene.
        
        Args:
            world (World): The ECS world instance.
            renderer (Renderer): The renderer instance.
            ui_manager (UIManager): The UI manager instance.
        """
        super().__init__(world, renderer, ui_manager)
        
        # Game systems
        self.city_manager = None
        self.combat_system = None
        self.weather_system = None
        self.day_night_cycle = None
        self.time_manager = None
        self.inventory_system = None
        
        # Player entity
        self.player_entity_id = None
        self.player_position = np.zeros(2, dtype=float)
        
        # Camera
        self.camera_position = np.zeros(3, dtype=float)
        self.camera_target = np.zeros(3, dtype=float)
        self.camera_zoom = 1.0
        self.camera_rotation = 0.0
        
        # Game state
        self.is_paused = False
        self.current_area = "city_center"  # Default starting area
        
        # Debug info
        self.debug_info = {
            "fps": 0,
            "entity_count": 0,
            "player_pos": (0, 0),
            "current_area": self.current_area,
            "time_of_day": "day",
            "weather": "clear"
        }
        
        # Rendering systems
        self.billboard_system = None
        self.world_renderer = None
        self.effect_system = None

    def initialize(self):
        """
        Initialize the game scene components.
        Called once when the scene is first loaded.
        """
        print("Initializing Game Scene")
        
        # Initialize rendering systems
        self._init_rendering_systems()
        
        # Initialize game systems
        self._init_city_system()
        self._init_combat_system()
        self._init_time_system()
        self._init_weather_system()
        self._init_inventory_system()
        
        # Initialize player entity
        self._init_player()
        
        # Initialize UI elements
        self._init_ui()
        
        # Set up initial camera position
        self._init_camera()
        
        print("Game Scene initialization complete")

    def _init_rendering_systems(self):
        """Initialize rendering systems for the game scene."""
        print("Initializing rendering systems")
        
        # Initialize billboard system for 2D entities in 3D world
        self.billboard_system = BillboardSystem(self.renderer)
        
        # Initialize world renderer for 3D terrain and structures
        self.world_renderer = WorldRenderer((self.renderer.width, self.renderer.height))
        
        # Initialize effect system for particles and visual effects
        self.effect_system = EffectSystem()
        
    def _init_city_system(self):
        """Initialize the city management system."""
        # Lazy import to avoid circular dependencies
        from ...city.city_manager import CityManager
        self.city_manager = CityManager()
        # Configure city layout, buildings, and resources
        self.city_manager.initialize()
        
    def _init_combat_system(self):
        """Initialize the combat system."""
        # Lazy import to avoid circular dependencies
        from ...combat.combat_system import CombatSystem
        self.combat_system = CombatSystem(self.world)
        # Configure abilities, enemy spawning, etc.
        
    def _init_time_system(self):
        """Initialize time management and day/night cycle."""
        # Lazy import to avoid circular dependencies
        from ...time.time_manager import TimeManager
        from ...time.day_night_cycle import DayNightCycle
        
        self.time_manager = TimeManager()
        self.day_night_cycle = DayNightCycle(cycle_duration_seconds=1200)  # 20 minutes default cycle
        # Configure day/night transitions and effects
        
    def _init_weather_system(self):
        """Initialize weather system."""
        # Lazy import to avoid circular dependencies
        from ...weather.weather_system import WeatherSystem
        self.weather_system = WeatherSystem()
        # Configure weather patterns and effects
        
    def _init_inventory_system(self):
        """Initialize inventory system."""
        # Lazy import to avoid circular dependencies
        from ...inventory.inventory import Inventory
        self.inventory_system = Inventory()
        # Configure inventory slots, starting items, etc.
        
    def _init_player(self):
        """Initialize player entity in the world."""
        # Create player entity
        player_entity = self.world.create_entity()
        self.player_entity_id = player_entity.id
        
        # Set initial position
        self.player_position = np.array([0, 0], dtype=float)
        
        # Add components
        player_entity.add_component(Transform(position=self.player_position.copy()))
        player_entity.add_component(Sprite(texture_path="assets/sprites/player.png"))
        player_entity.add_component(Animation(frames=[], frame_duration=0.1))
        player_entity.add_component(PhysicsBody(mass=70.0))
        
        # Add player entity to scene's managed entities
        self.add_entity(self.player_entity_id)
        
        print(f"Created player entity with ID: {self.player_entity_id}")
        
    def _init_ui(self):
        """Initialize UI elements for the game scene."""
        # Create HUD
        self.hud = GameHUD(self.renderer.width, self.renderer.height)
        
        # Configure UI elements specific to game scene
        
    def _init_camera(self):
        """Initialize camera position and parameters."""
        # Set camera position above and behind player
        self.camera_position = np.array([0, -10, 5], dtype=float)
        # Target player position
        self.camera_target = np.array([0, 0, 0], dtype=float)
        # Set zoom and rotation
        self.camera_zoom = 1.0
        self.camera_rotation = 0.0
        
    def update(self, dt):
        """
        Update scene logic for the current frame.
        
        Args:
            dt (float): Time elapsed since last frame.
        """
        if self.is_paused:
            return
            
        # Update player
        self._update_player(dt)
        
        # Update camera
        self._update_camera(dt)
        
        # Update game systems
        self._update_city(dt)
        self._update_combat(dt)
        self._update_time(dt)
        self._update_weather(dt)
        
        # Update UI
        if self.hud:
            self.hud.update(dt, self.debug_info)
            
        # Update debug info
        self._update_debug_info()
        
    def _update_player(self, dt):
        """Update player entity."""
        # Get player entity
        player_entity = self.world.get_entity(self.player_entity_id)
        if not player_entity:
            return
            
        # Update player logic
        # Movement, abilities, etc.
        
        # Update player position
        transform = player_entity.get_component(Transform)
        if transform:
            self.player_position = transform.position.copy()
        
    def _update_camera(self, dt):
        """Update camera position and parameters."""
        # Follow player with camera
        self.camera_target[0] = self.player_position[0]
        self.camera_target[1] = self.player_position[1]
        
        # Smoothly move camera position
        target_camera_x = self.player_position[0]
        target_camera_y = self.player_position[1] - 10  # Position camera behind player
        
        # Apply smooth camera movement
        camera_speed = 5.0 * dt
        self.camera_position[0] += (target_camera_x - self.camera_position[0]) * camera_speed
        self.camera_position[1] += (target_camera_y - self.camera_position[1]) * camera_speed
        
    def _update_city(self, dt):
        """Update city system."""
        if self.city_manager:
            self.city_manager.update(dt)
            
    def _update_combat(self, dt):
        """Update combat system."""
        if self.combat_system:
            self.combat_system.update(dt)
            
    def _update_time(self, dt):
        """Update time and day/night cycle."""
        if self.time_manager:
            self.time_manager.update()
        
        if self.day_night_cycle:
            self.day_night_cycle.update(dt)
            
    def _update_weather(self, dt):
        """Update weather system."""
        if self.weather_system:
            self.weather_system.update(dt)
            
    def _update_debug_info(self):
        """Update debug information."""
        self.debug_info["player_pos"] = tuple(self.player_position)
        self.debug_info["entity_count"] = len(self.world.entities)
        
        # Update time and weather info
        if self.day_night_cycle:
            self.debug_info["time_of_day"] = self.day_night_cycle.get_current_period()
            
        if self.weather_system:
            weather_condition = self.weather_system.get_current_condition()
            self.debug_info["weather"] = weather_condition.name if weather_condition else "Unknown"
            
    def render(self, screen=None):
        """
        Render the game scene.
        
        Args:
            screen: The pygame screen to render on. If None, use renderer.screen.
        """
        # Use the renderer's screen if screen is not provided
        if screen is None:
            screen = self.renderer.screen
        
        # Clear screen with a dark background (in a real implementation, this would be handled by the renderer)
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Create camera matrix for 3D rendering
        camera_matrix = self._create_camera_matrix()
        
        # Render 3D world
        self._render_world(screen, camera_matrix)
        
        # Render 2D entities
        self._render_entities(screen, camera_matrix)
        
        # Render UI
        self._render_ui(screen)
        
        # Render debug info if enabled
        self._render_debug(screen)
        
    def _create_camera_matrix(self):
        """Create the camera view-projection matrix for 3D rendering."""
        if not OPENGL_AVAILABLE:
            # If OpenGL and glm are not available, return identity matrix
            print("Warning: OpenGL and glm not available for camera matrix calculation")
            return np.identity(4)
            
        try:
            # Calculate view matrix (lookAt)
            view_matrix = glm.lookAt(
                glm.vec3(self.camera_position[0], self.camera_position[2], self.camera_position[1]),  # Position
                glm.vec3(self.camera_target[0], self.camera_target[2], self.camera_target[1]),      # Target
                glm.vec3(0.0, 1.0, 0.0)                                                            # Up vector
            )
            
            # Calculate projection matrix (perspective)
            projection_matrix = glm.perspective(
                glm.radians(45.0 * self.camera_zoom),                      # FOV
                self.renderer.width / self.renderer.height,                # Aspect ratio
                0.1,                                                       # Near plane
                1000.0                                                     # Far plane
            )
            
            # Combine into view-projection matrix
            return projection_matrix * view_matrix
            
        except Exception as e:
            print(f"Error creating camera matrix: {e}")
            return np.identity(4)
        
    def _render_world(self, screen, camera_matrix):
        """
        Render the 3D world environment using WorldRenderer.
        
        Args:
            screen: The pygame screen to render on.
            camera_matrix: The camera view-projection matrix.
        """
        try:
            # Use WorldRenderer to render the 3D world
            self.world_renderer.render(camera_matrix)
            
            # Render city buildings if city manager is available
            if self.city_manager:
                self.city_manager.render(self.renderer)
                
        except Exception as e:
            # Fallback rendering if WorldRenderer fails
            print(f"Error in world rendering: {e}")
            
            # Draw a simple grid as fallback
            self._render_fallback_world(screen)
            
    def _render_fallback_world(self, screen):
        """
        Render a simple fallback world when 3D rendering is not available.
        
        Args:
            screen: The pygame screen to render on.
        """
        # Draw a simple grid
        grid_size = 50
        grid_color = (50, 50, 70)
        
        # Draw horizontal grid lines
        for y in range(0, self.renderer.height, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (self.renderer.width, y))
            
        # Draw vertical grid lines
        for x in range(0, self.renderer.width, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, self.renderer.height))
            
    def _render_entities(self, screen, camera_matrix):
        """
        Render 2D entities with billboarding in 3D space using BillboardSystem.
        
        Args:
            screen: The pygame screen to render on.
            camera_matrix: The camera view-projection matrix.
        """
        try:
            # First, try to get renderable entities
            try:
                # Get all entities with Transform and Sprite components
                renderable_entities = self.world.get_renderable_entities()
            except Exception as e:
                print(f"Error getting renderable entities: {e}")
                renderable_entities = []
            
            # Use BillboardSystem to render entities if available
            if self.billboard_system:
                try:
                    # Convert camera_position to tuple for the billboard system
                    camera_pos = (self.camera_position[0], self.camera_position[1], self.camera_position[2])
                    
                    # Render entities using billboard system
                    self.billboard_system.render_entities(renderable_entities, camera_pos)
                except Exception as e:
                    print(f"Error using billboard system: {e}")
                    # Fall back to simple rendering if billboard fails
                    self._render_fallback_entities(screen, renderable_entities)
            else:
                # Fallback to simple 2D rendering if billboard system not available
                self._render_fallback_entities(screen, renderable_entities)
                
        except Exception as e:
            print(f"Error in entity rendering: {e}")
            # Just proceed without rendering entities in case of total failure
            pass
            
    def _render_fallback_entities(self, screen, entities):
        """
        Render entities using simple 2D sprites when billboard system is not available.
        
        Args:
            screen: The pygame screen to render on.
            entities: List of entities to render.
        """
        if not entities:
            return
            
        try:
            # Make sure all needed components are present
            valid_entities = []
            for entity in entities:
                if entity and hasattr(entity, 'get_component'):
                    transform = entity.get_component('Transform') if callable(getattr(entity, 'get_component', None)) else None
                    sprite = entity.get_component('Sprite') if callable(getattr(entity, 'get_component', None)) else None
                    
                    if transform and sprite and hasattr(transform, 'position'):
                        valid_entities.append((entity, transform, sprite))
            
            # Sort entities by position for basic depth sorting
            sorted_entities = sorted(
                valid_entities,
                key=lambda e: e[1].position[1] if hasattr(e[1], 'position') and e[1].position is not None else 0
            )
            
            # Draw each entity as a simple rectangle
            for entity, transform, sprite in sorted_entities:
                # Calculate screen position from world position
                screen_x = int(transform.position[0] + self.renderer.width / 2 - self.camera_position[0])
                screen_y = int(transform.position[1] + self.renderer.height / 2 - self.camera_position[1])
                
                # Draw a colored rectangle for the entity
                color = sprite.color[:3] if hasattr(sprite, 'color') and len(sprite.color) >= 3 else (255, 0, 0)
                size = 32  # Default size
                
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x - size//2, screen_y - size//2, size, size)
                )
        except Exception as e:
            print(f"Error in fallback entity rendering: {e}")
            
    def _render_ui(self, screen):
        """Render UI elements."""
        if self.hud:
            self.hud.draw(screen)
            
    def _render_debug(self, screen):
        """Render debug information if enabled."""
        # Check if debug rendering is enabled
        if not hasattr(self.renderer, 'enable_debug_rendering') or not self.renderer.enable_debug_rendering:
            return
        
        # Render debug info
        font = pygame.font.SysFont(None, 24)
        y = 10
        for key, value in self.debug_info.items():
            text = f"{key}: {value}"
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, y))
            y += 25
        
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle.
        """
        # Handle UI input first
        if self.hud and self.hud.handle_event(event):
            return True
            
        # Handle player input
        if self._handle_player_input(event):
            return True
            
        # Handle camera controls
        if self._handle_camera_input(event):
            return True
            
        # Handle system-specific input
        
        # Default event handling
        return False
        
    def _handle_player_input(self, event):
        """Handle player input events."""
        if event.type == pygame.KEYDOWN:
            # Movement keys
            if event.key == pygame.K_w:
                # Move up
                return True
            elif event.key == pygame.K_s:
                # Move down
                return True
            elif event.key == pygame.K_a:
                # Move left
                return True
            elif event.key == pygame.K_d:
                # Move right
                return True
                
            # Action keys
            elif event.key == pygame.K_SPACE:
                # Interact
                return True
            elif event.key == pygame.K_e:
                # Use ability / interact
                return True
                
        return False
        
    def _handle_camera_input(self, event):
        """Handle camera control input."""
        if event.type == pygame.KEYDOWN:
            # Camera zoom
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.camera_zoom = min(2.0, self.camera_zoom + 0.1)
                return True
            elif event.key == pygame.K_MINUS:
                self.camera_zoom = max(0.5, self.camera_zoom - 0.1)
                return True
                
            # Camera rotation
            elif event.key == pygame.K_q:
                self.camera_rotation -= 15.0  # Rotate left by 15 degrees
                return True
            elif event.key == pygame.K_e:
                self.camera_rotation += 15.0  # Rotate right by 15 degrees
                return True
                
        return False
        
    def load(self):
        """
        Called when the scene becomes active.
        """
        super().load()
        print("Loading Game Scene")
        
    def unload(self):
        """
        Called when the scene is deactivated.
        Cleans up resources.
        """
        print("Unloading Game Scene")
        
        # Clean up systems
        if self.city_manager:
            self.city_manager.cleanup()
            
        if self.combat_system:
            self.combat_system.cleanup()
            
        if self.weather_system:
            self.weather_system.cleanup()
            
        # Call parent unload to clean up entities
        super().unload()
        
    def transition_to_area(self, area_name):
        """
        Transition player to a new area.
        
        Args:
            area_name (str): The name of the area to transition to.
        """
        print(f"Transitioning to area: {area_name}")
        self.current_area = area_name
        
        # Update player position based on area entry point
        
        # Load area-specific resources
        
        # Update game systems for new area 