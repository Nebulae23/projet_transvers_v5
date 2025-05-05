import pygame
from .ui_base import UIElement
from .hud.health_bar import HealthBar
from .hud.resource_display import ResourceDisplay
from .hud.ability_bar import AbilityBar
from .hud.minimap import Minimap
from .hud.status_effects import StatusEffectsDisplay
from .hud.quest_tracker import QuestTracker
from .hud.styles.layout_config import get_layout_config
from .hud.styles.hud_theme import get_theme

class GameHUD:
    """
    Game Heads-Up Display
    Manages all the individual HUD elements like health bar, minimap, etc.
    """
    def __init__(self, screen_width=1280, screen_height=720, player_id=None, world=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_id = player_id
        self.world = world
        self.font = pygame.font.SysFont(None, 24)
        self.debug_mode = False
        self.layout = get_layout_config(screen_width, screen_height)
        self.theme = get_theme() # TODO: Pass theme to elements

        self.children = []
        self._setup_elements()

    def _setup_elements(self):
        """Creates and positions all HUD elements based on layout."""
        print("Setting up HUD elements...")
        
        try:
            self.health_bar = HealthBar(
                *self.layout['health_bar_pos'], *self.layout['health_bar_size'],
                self.player_id, self.world
            )
            print("Health bar created")
        except Exception as e:
            print(f"Error creating health bar: {e}")
            self.health_bar = None

        try:
            # Example Resource Bars (assuming Mana and Stamina components exist)
        # Example Resource Bars (assuming Mana and Stamina components exist)
        self.mana_bar = ResourceDisplay(
                *self.layout['mana_bar_pos'], *self.layout['resource_bar_size'],
                self.player_id, self.world, resource_type='Mana'
        )
            print("Mana bar created")
        except Exception as e:
            print(f"Error creating mana bar: {e}")
            self.mana_bar = None

        try:
        self.stamina_bar = ResourceDisplay(
                *self.layout['stamina_bar_pos'], *self.layout['resource_bar_size'],
                self.player_id, self.world, resource_type='Stamina'
        )
            print("Stamina bar created")
        except Exception as e:
            print(f"Error creating stamina bar: {e}")
            self.stamina_bar = None

        try:
        self.ability_bar = AbilityBar(
                *self.layout['ability_bar_pos'], *self.layout['ability_bar_size'],
                self.player_id, self.world
        )
            print("Ability bar created")
        except Exception as e:
            print(f"Error creating ability bar: {e}")
            self.ability_bar = None

        try:
        self.minimap = Minimap(
                *self.layout['minimap_pos'], *self.layout['minimap_size'],
                self.world, self.player_id
        )
            print("Minimap created")
        except Exception as e:
            print(f"Error creating minimap: {e}")
            self.minimap = None

        try:
        self.status_effects = StatusEffectsDisplay(
                *self.layout['status_effects_pos'], *self.layout['status_effects_size'],
                self.player_id, self.world
        )
            print("Status effects display created")
        except Exception as e:
            print(f"Error creating status effects display: {e}")
            self.status_effects = None

        try:
        self.quest_tracker = QuestTracker(
                *self.layout['quest_tracker_pos'], *self.layout['quest_tracker_size'],
                self.player_id, self.world
        )
            print("Quest tracker created")
        except Exception as e:
            print(f"Error creating quest tracker: {e}")
            self.quest_tracker = None

        # Add all elements as children for drawing and updates
        self.children = [
            self.health_bar,
            self.mana_bar,
            self.stamina_bar,
            self.ability_bar,
            self.minimap,
            self.status_effects,
            self.quest_tracker,
        ]
        # Filter out None values (failed creations)
        self.children = [child for child in self.children if child is not None]

    def update(self, dt):
        """Updates all child HUD elements."""
        for child in self.children:
            if hasattr(child, 'update'):
                try:
                    child.update(dt)
                except Exception as e:
                    print(f"Error updating HUD element: {e}")

    def draw(self, surface):
        """Draws all child HUD elements."""
        for child in self.children:
            if hasattr(child, 'draw'):
                try:
                    child.draw(surface)
                except Exception as e:
                    print(f"Error drawing HUD element: {e}")

        if self.debug_mode:
            self._draw_debug_info(surface)

    def _draw_debug_info(self, surface):
        """Draw debug information"""
        fps_text = self.font.render(f"FPS: {int(pygame.time.Clock().get_fps())}", True, (255, 255, 255))
        surface.blit(fps_text, (10, 10))

    def handle_event(self, event):
        """Handles events for child HUD elements (if any are interactive)."""
        for child in self.children:
            if hasattr(child, 'handle_event'):
                if child.handle_event(event):
                    return True
        return False

    def resize(self, new_width, new_height):
        """Handles screen resizing by recalculating layout and repositioning elements."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.layout = get_layout_config(new_width, new_height)
        # Re-create elements with new layout for simplicity
        self._setup_elements()

    def set_debug_mode(self, enabled):
        """Enable or disable debug information"""
        self.debug_mode = enabled