# src/engine/menu/menu_system.py
from typing import Optional, List, Dict
import pygame
import numpy as np
from enum import Enum
from dataclasses import dataclass
from ..rendering.menu_camera import MenuCamera, POIPoint
from ..rendering.world_renderer import WorldRenderer
from ..world.terrain_generator import TerrainGenerator

class MenuState(Enum):
    MAIN = "main"
    OPTIONS = "options"
    LOAD_GAME = "load_game"
    NEW_GAME = "new_game"
    CREDITS = "credits"

@dataclass
class MenuItem:
    text: str
    position: tuple[float, float]
    size: tuple[float, float]
    action: callable
    hover: bool = False

class MenuSystem:
    def __init__(self, window_size: tuple[int, int], renderer=None):
        self.window_size = window_size
        self.current_state = MenuState.MAIN
        self.transition_alpha = 0.0
        self.renderer = renderer  # Store reference to main renderer
        
        # Initialize rendering systems
        self.camera = MenuCamera()
        self.world_renderer = WorldRenderer(window_size, self.renderer)
        self.terrain_gen = TerrainGenerator()
        
        # Generate showcase world
        self._generate_showcase_world()
        
        # Initialize UI elements
        self.font = pygame.freetype.Font("assets/fonts/main.ttf", 32)
        self.menu_items: Dict[MenuState, List[MenuItem]] = {}
        self._setup_menu_items()
        
        # Background effects
        self.last_special_event = 0.0
        self.special_event_interval = 30.0  # seconds
        
    def update(self, delta_time: float) -> None:
        # Update camera and world effects
        self.camera.update(delta_time)
        self.world_renderer.update_effects(delta_time)
        
        # Check for special events
        self.last_special_event += delta_time
        if self.last_special_event >= self.special_event_interval:
            self._trigger_special_event()
            self.last_special_event = 0.0
            
        # Update menu transitions
        if self.transition_alpha > 0:
            self.transition_alpha = max(0, self.transition_alpha - delta_time)
            
    def render(self, surface: pygame.Surface) -> None:
        # Render world showcase
        self.world_renderer.render(self.camera.get_view_matrix())
        
        # Render menu items
        if self.current_state in self.menu_items:
            for item in self.menu_items[self.current_state]:
                self._render_menu_item(surface, item)
                
        # Render transitions
        if self.transition_alpha > 0:
            overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(255 * self.transition_alpha)))
            surface.blit(overlay, (0, 0))
            
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
            
    def transition_to(self, new_state: MenuState) -> None:
        self.current_state = new_state
        self.transition_alpha = 1.0
        
    def _generate_showcase_world(self) -> None:
        # Generate a visually interesting world for the menu background
        seed = np.random.randint(1000000)
        self.terrain_gen.generate(seed)
        
        # Set up camera points of interest
        scenic_points = self._find_scenic_points()
        for point in scenic_points:
            self.camera.add_poi(point)
            
    def _find_scenic_points(self) -> List[POIPoint]:
        points = []
        height_map = self.terrain_gen.height_map
        
        # Find interesting terrain features
        for y in range(1, height_map.shape[0]-1, 50):
            for x in range(1, height_map.shape[1]-1, 50):
                height = height_map[y, x]
                
                # Mountains
                if height > 0.7:
                    points.append(POIPoint(
                        position=np.array([x, height * 20 + 10, y]),
                        target=np.array([x, height * 20, y]),
                        transition_time=3.0,
                        hold_time=8.0
                    ))
                    
                # Coastlines
                elif 0.3 < height < 0.35:
                    points.append(POIPoint(
                        position=np.array([x, 10, y]),
                        target=np.array([x, 0, y]),
                        transition_time=2.0,
                        hold_time=6.0
                    ))
                    
        return points[:10]  # Limit to 10 most interesting points
        
    def _setup_menu_items(self) -> None:
        # Main menu items
        self.menu_items[MenuState.MAIN] = [
            MenuItem(
                text="New Game",
                position=(self.window_size[0]*0.5, self.window_size[1]*0.4),
                size=(200, 50),
                action=lambda: self.transition_to(MenuState.NEW_GAME)
            ),
            MenuItem(
                text="Load Game",
                position=(self.window_size[0]*0.5, self.window_size[1]*0.5),
                size=(200, 50),
                action=lambda: self.transition_to(MenuState.LOAD_GAME)
            ),
            MenuItem(
                text="Options",
                position=(self.window_size[0]*0.5, self.window_size[1]*0.6),
                size=(200, 50),
                action=lambda: self.transition_to(MenuState.OPTIONS)
            ),
            MenuItem(
                text="Credits",
                position=(self.window_size[0]*0.5, self.window_size[1]*0.7),
                size=(200, 50),
                action=lambda: self.transition_to(MenuState.CREDITS)
            )
        ]
        
    def _render_menu_item(self, surface: pygame.Surface, item: MenuItem) -> None:
        color = (255, 255, 255) if not item.hover else (200, 200, 100)
        text_surface, rect = self.font.render(item.text, color)
        
        # Center text at item position
        pos = (item.position[0] - rect.width/2,
               item.position[1] - rect.height/2)
        
        # Draw text with HD-2D style
        if item.hover:
            # Draw glow effect
            glow_surface = pygame.Surface((rect.width + 20, rect.height + 20),
                                       pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, 50),
                           (0, 0, rect.width + 20, rect.height + 20))
            surface.blit(glow_surface,
                        (pos[0] - 10, pos[1] - 10))
            
        surface.blit(text_surface, pos)
        
    def _handle_mouse_hover(self, pos: tuple[float, float]) -> None:
        if self.current_state not in self.menu_items:
            return
            
        for item in self.menu_items[self.current_state]:
            item.hover = self._is_point_in_item(pos, item)
            
    def _handle_mouse_click(self, pos: tuple[float, float]) -> None:
        if self.current_state not in self.menu_items:
            return
            
        for item in self.menu_items[self.current_state]:
            if self._is_point_in_item(pos, item):
                item.action()
                break
                
    def _is_point_in_item(self, pos: tuple[float, float],
                         item: MenuItem) -> bool:
        return (abs(pos[0] - item.position[0]) < item.size[0]/2 and
                abs(pos[1] - item.position[1]) < item.size[1]/2)
                
    def _trigger_special_event(self) -> None:
        # Randomly trigger special visual effects
        events = ["aurora", "thunderstorm"]
        event = np.random.choice(events)
        
        camera_pos = self.camera.position
        self.world_renderer.trigger_special_event(event, camera_pos)