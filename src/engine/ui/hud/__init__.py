# src/engine/ui/hud/__init__.py
"""
HUD (Heads-Up Display) components for game UI.
"""

from .game_hud import GameHUD

__all__ = ['GameHUD']

# Import components
from .health_bar import HealthBar
from .resource_display import ResourceDisplay
from .ability_bar import AbilityBar
from .minimap import Minimap
from .status_effects import StatusEffectsDisplay
from .quest_tracker import QuestTracker
from .styles.layout_config import get_layout_config
from .styles.hud_theme import get_theme

# GameHUD class directly in this module to avoid circular imports
class GameHUD:
    """
    Main container for the In-Game Heads-Up Display.
    Manages all the individual HUD elements like health bar, minimap, etc.
    """
    def __init__(self, screen_width, screen_height, player_id, world):
        self.width = screen_width
        self.height = screen_height
        self.player_id = player_id
        self.world = world
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

    def draw(self, screen):
        """Draws all child HUD elements."""
        for child in self.children:
            if hasattr(child, 'draw'):
                try:
                    child.draw(screen)
                except Exception as e:
                    print(f"Error drawing HUD element: {e}")

    def handle_event(self, event):
        """Handles events for child HUD elements (if any are interactive)."""
        for child in self.children:
            if hasattr(child, 'handle_event'):
                try:
                    child.handle_event(event)
                except Exception as e:
                    print(f"Error handling event in HUD element: {e}")

    def resize(self, new_width, new_height):
        """Handles screen resizing by recalculating layout and repositioning elements."""
        self.width = new_width
        self.height = new_height
        self.layout = get_layout_config(new_width, new_height)
        # Re-create elements with new layout for simplicity
        self._setup_elements() 