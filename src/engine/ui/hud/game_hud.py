# src/engine/ui/hud/game_hud.py

import pygame
import math
from typing import Dict, List, Optional, Tuple, Any

from ..ui_base import UIElement, Panel, Label, Button
from .styles import HUDStyle

class HealthBar(UIElement):
    """Health bar UI element."""
    def __init__(self, x, y, width, height, max_value, current_value):
        super().__init__(x=x, y=y, width=width, height=height)
        self.max_value = max_value
        self.current_value = current_value
        self.color = (220, 50, 50)  # Red
        self.background_color = (60, 30, 30)
        self.border_color = (100, 100, 100)
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, (pos_x, pos_y, self.width, self.height))
        
        # Draw health bar
        health_width = int(self.width * (self.current_value / self.max_value))
        pygame.draw.rect(screen, self.color, (pos_x, pos_y, health_width, self.height))
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, (pos_x, pos_y, self.width, self.height), 2)
        
        # Draw text
        font = pygame.font.SysFont(None, 20)
        text = f"{self.current_value}/{self.max_value}"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(pos_x + self.width // 2, pos_y + self.height // 2))
        screen.blit(text_surface, text_rect)


class ResourceBar(UIElement):
    """Resource bar (mana, energy, etc.) UI element."""
    def __init__(self, x, y, width, height, max_value, current_value):
        super().__init__(x=x, y=y, width=width, height=height)
        self.max_value = max_value
        self.current_value = current_value
        self.color = (50, 100, 220)  # Blue
        self.background_color = (30, 40, 60)
        self.border_color = (100, 100, 100)
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, (pos_x, pos_y, self.width, self.height))
        
        # Draw resource bar
        resource_width = int(self.width * (self.current_value / self.max_value))
        pygame.draw.rect(screen, self.color, (pos_x, pos_y, resource_width, self.height))
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, (pos_x, pos_y, self.width, self.height), 2)
        
        # Draw text
        font = pygame.font.SysFont(None, 16)
        text = f"{self.current_value}/{self.max_value}"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(pos_x + self.width // 2, pos_y + self.height // 2))
        screen.blit(text_surface, text_rect)


class Minimap(UIElement):
    """Minimap UI element."""
    def __init__(self, x, y, width, height):
        super().__init__(x=x, y=y, width=width, height=height)
        self.background_color = (30, 30, 40, 180)  # Semi-transparent dark blue
        self.border_color = (100, 100, 100)
        self.player_position = (width // 2, height // 2)  # Center of minimap
        self.map_objects = []  # List of objects to display on minimap
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Create minimap surface with transparency
        minimap_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(minimap_surface, self.background_color, (0, 0, self.width, self.height))
        
        # Draw map objects
        for obj in self.map_objects:
            color = obj.get('color', (200, 200, 200))
            pos = obj.get('position', (0, 0))
            size = obj.get('size', 3)
            pygame.draw.circle(minimap_surface, color, pos, size)
            
        # Draw player position
        pygame.draw.circle(minimap_surface, (0, 255, 0), self.player_position, 5)
        
        # Draw border
        pygame.draw.rect(minimap_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Blit minimap to screen
        screen.blit(minimap_surface, (pos_x, pos_y))


class AbilityBar(UIElement):
    """Ability bar for displaying and using abilities."""
    def __init__(self, x, y, width, height, abilities=None):
        super().__init__(x=x, y=y, width=width, height=height)
        self.abilities = abilities or []
        self.background_color = (40, 40, 50, 180)  # Semi-transparent dark
        self.border_color = (100, 100, 100)
        self.ability_size = 50  # Size of ability icons
        self.ability_spacing = 10  # Spacing between ability icons
        
    def update(self, dt):
        # Update ability cooldowns
        for ability in self.abilities:
            if 'cooldown_remaining' in ability and ability['cooldown_remaining'] > 0:
                ability['cooldown_remaining'] = max(0, ability['cooldown_remaining'] - dt)
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Create ability bar surface with transparency
        bar_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(bar_surface, self.background_color, (0, 0, self.width, self.height))
        
        # Draw ability slots
        max_abilities = min(5, len(self.abilities) if self.abilities else 5)
        total_width = max_abilities * self.ability_size + (max_abilities - 1) * self.ability_spacing
        start_x = (self.width - total_width) // 2
        
        for i in range(max_abilities):
            slot_x = start_x + i * (self.ability_size + self.ability_spacing)
            
            # Draw slot background
            pygame.draw.rect(bar_surface, (60, 60, 70), (slot_x, 5, self.ability_size, self.ability_size))
            
            # Draw ability icon if available
            if self.abilities and i < len(self.abilities):
                ability = self.abilities[i]
                
                # Draw ability icon (placeholder)
                icon_color = ability.get('color', (200, 200, 200))
                pygame.draw.rect(bar_surface, icon_color, (slot_x + 2, 7, self.ability_size - 4, self.ability_size - 4))
                
                # Draw cooldown overlay if on cooldown
                if 'cooldown_remaining' in ability and ability['cooldown_remaining'] > 0:
                    cooldown_pct = ability['cooldown_remaining'] / ability['cooldown']
                    cooldown_height = int((self.ability_size - 4) * cooldown_pct)
                    pygame.draw.rect(bar_surface, (0, 0, 0, 150), 
                                   (slot_x + 2, 7, self.ability_size - 4, cooldown_height))
                    
                # Draw key binding
                font = pygame.font.SysFont(None, 16)
                key_text = ability.get('key', str(i + 1))
                text_surface = font.render(key_text, True, (255, 255, 255))
                bar_surface.blit(text_surface, (slot_x + 3, 7))
            
            # Draw slot border
            pygame.draw.rect(bar_surface, self.border_color, (slot_x, 5, self.ability_size, self.ability_size), 2)
        
        # Draw border around the entire bar
        pygame.draw.rect(bar_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Blit ability bar to screen
        screen.blit(bar_surface, (pos_x, pos_y))
        
    def handle_event(self, event):
        """Handle ability activation events."""
        if event.type == pygame.KEYDOWN:
            # Number keys 1-5 activate abilities
            if pygame.K_1 <= event.key <= pygame.K_5:
                ability_index = event.key - pygame.K_1
                if self.abilities and ability_index < len(self.abilities):
                    self._activate_ability(ability_index)
                    return True
        return False
        
    def _activate_ability(self, index):
        """Activate an ability by index."""
        if not self.abilities or index >= len(self.abilities):
            return
            
        ability = self.abilities[index]
        
        # Check if ability is on cooldown
        if 'cooldown_remaining' in ability and ability['cooldown_remaining'] > 0:
            print(f"Ability {ability['name']} is on cooldown: {ability['cooldown_remaining']:.1f}s remaining")
            return
            
        # Activate ability
        print(f"Activated ability: {ability['name']}")
        
        # Start cooldown
        if 'cooldown' in ability:
            ability['cooldown_remaining'] = ability['cooldown']


class StatusPanel(UIElement):
    """Status panel for displaying player level and game state."""
    def __init__(self, x, y, width, height, player_level=1, time_of_day="day", weather="clear"):
        super().__init__(x=x, y=y, width=width, height=height)
        self.player_level = player_level
        self.time_of_day = time_of_day
        self.weather = weather
        self.background_color = (40, 40, 50, 180)  # Semi-transparent dark
        self.border_color = (100, 100, 100)
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Create status panel surface with transparency
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(panel_surface, self.background_color, (0, 0, self.width, self.height))
        
        # Draw border
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Draw level
        font = pygame.font.SysFont(None, 24)
        level_text = f"Level: {self.player_level}"
        level_surface = font.render(level_text, True, (255, 220, 150))
        panel_surface.blit(level_surface, (10, 10))
        
        # Draw time of day
        time_text = f"Time: {self.time_of_day.capitalize()}"
        time_color = (150, 200, 255) if self.time_of_day == "day" else (100, 120, 200)
        time_surface = font.render(time_text, True, time_color)
        panel_surface.blit(time_surface, (10, 35))
        
        # Draw weather
        weather_text = f"Weather: {self.weather.capitalize()}"
        weather_color = (200, 200, 255)  # Default color
        if self.weather == "rain":
            weather_color = (100, 150, 255)
        elif self.weather == "storm":
            weather_color = (150, 150, 255)
        elif self.weather == "snow":
            weather_color = (220, 220, 255)
        weather_surface = font.render(weather_text, True, weather_color)
        panel_surface.blit(weather_surface, (100, 10))
        
        # Blit panel to screen
        screen.blit(panel_surface, (pos_x, pos_y))


class QuestTracker(UIElement):
    """Quest tracker for displaying active quests."""
    def __init__(self, x, y, width, height, quests=None):
        super().__init__(x=x, y=y, width=width, height=height)
        self.quests = quests or []
        self.background_color = (40, 40, 50, 180)  # Semi-transparent dark
        self.border_color = (100, 100, 100)
        self.scroll_offset = 0
        self.max_visible_quests = 5
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        # Get position
        pos_x, pos_y = self.absolute_position
        
        # Create quest tracker surface with transparency
        tracker_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(tracker_surface, self.background_color, (0, 0, self.width, self.height))
        
        # Draw border
        pygame.draw.rect(tracker_surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # Draw header
        font = pygame.font.SysFont(None, 24)
        header_text = "Active Quests"
        header_surface = font.render(header_text, True, (220, 220, 150))
        tracker_surface.blit(header_surface, (10, 10))
        
        # Draw quests
        small_font = pygame.font.SysFont(None, 18)
        y_offset = 40
        
        visible_quests = self.quests[self.scroll_offset:self.scroll_offset + self.max_visible_quests]
        
        if not visible_quests:
            # No quests message
            no_quests_text = "No active quests"
            no_quests_surface = small_font.render(no_quests_text, True, (180, 180, 180))
            tracker_surface.blit(no_quests_surface, (10, y_offset))
        else:
            for quest in visible_quests:
                # Draw quest name
                quest_name = quest.get('name', 'Unknown Quest')
                quest_surface = small_font.render(quest_name, True, (255, 255, 255))
                tracker_surface.blit(quest_surface, (10, y_offset))
                y_offset += 20
                
                # Draw quest objective
                quest_objective = quest.get('objective', 'No objective')
                objective_surface = small_font.render(f"- {quest_objective}", True, (200, 200, 200))
                tracker_surface.blit(objective_surface, (20, y_offset))
                y_offset += 25
        
        # Draw scroll indicators if needed
        if len(self.quests) > self.max_visible_quests:
            if self.scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(tracker_surface, (200, 200, 200), 
                                   [(self.width - 20, 15), (self.width - 10, 25), (self.width - 30, 25)])
            
            if self.scroll_offset + self.max_visible_quests < len(self.quests):
                # Down arrow
                pygame.draw.polygon(tracker_surface, (200, 200, 200), 
                                   [(self.width - 20, self.height - 15), 
                                    (self.width - 10, self.height - 25), 
                                    (self.width - 30, self.height - 25)])
        
        # Blit tracker to screen
        screen.blit(tracker_surface, (pos_x, pos_y))
        
    def handle_event(self, event):
        """Handle quest tracker events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get position
            pos_x, pos_y = self.absolute_position
            
            # Check if mouse is over the tracker
            if (pos_x <= event.pos[0] <= pos_x + self.width and 
                pos_y <= event.pos[1] <= pos_y + self.height):
                
                # Scroll up
                if event.button == 4 and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                    return True
                
                # Scroll down
                elif event.button == 5 and self.scroll_offset + self.max_visible_quests < len(self.quests):
                    self.scroll_offset += 1
                    return True
                    
        return False

class GameHUD:
    """
    Game HUD (Heads-Up Display) for the main game scene.
    Displays player health, resources, minimap, ability bar, etc.
    """
    def __init__(self, width: int, height: int):
        """
        Initialize the game HUD.
        
        Args:
            width (int): Screen width.
            height (int): Screen height.
        """
        self.width = width
        self.height = height
        
        # UI elements
        self.health_bar = None
        self.resource_bar = None
        self.minimap = None
        self.ability_bar = None
        self.status_panel = None
        self.quest_tracker = None
        self.ui_elements = []
        
        # Fonts
        self.font = None
        self.small_font = None
        
        # Player data
        self.player_health = 100
        self.player_max_health = 100
        self.player_resource = 50
        self.player_max_resource = 100
        self.player_level = 1
        self.player_abilities = []
        
        # Game data
        self.active_quests = []
        self.current_area = ""
        self.time_of_day = "day"
        self.weather = "clear"
        
        # Debug info
        self.debug_info = {}
        self.show_debug = False
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI elements."""
        # Create fonts
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        # Create health bar (bottom left)
        self.health_bar = HealthBar(
            x=20,
            y=self.height - 80,
            width=200,
            height=25,
            max_value=self.player_max_health,
            current_value=self.player_health
        )
        
        # Create resource bar (below health bar)
        self.resource_bar = ResourceBar(
            x=20,
            y=self.height - 50,
            width=200,
            height=15,
            max_value=self.player_max_resource,
            current_value=self.player_resource
        )
        
        # Create minimap (top right)
        self.minimap = Minimap(
            x=self.width - 220,
            y=20,
            width=200,
            height=200
        )
        
        # Create ability bar (bottom center)
        self.ability_bar = AbilityBar(
            x=self.width // 2 - 150,
            y=self.height - 80,
            width=300,
            height=60,
            abilities=self.player_abilities
        )
        
        # Create status panel (top left)
        self.status_panel = StatusPanel(
            x=20,
            y=20,
            width=200,
            height=60,
            player_level=self.player_level,
            time_of_day=self.time_of_day,
            weather=self.weather
        )
        
        # Create quest tracker (right side)
        self.quest_tracker = QuestTracker(
            x=self.width - 320,
            y=240,
            width=300,
            height=200,
            quests=self.active_quests
        )
        
        # Add all UI elements to list
        self.ui_elements = [
            self.health_bar,
            self.resource_bar,
            self.minimap,
            self.ability_bar,
            self.status_panel,
            self.quest_tracker
        ]
        
    def update(self, dt, debug_info=None):
        """
        Update HUD elements.
        
        Args:
            dt (float): Time elapsed since last frame.
            debug_info (dict): Debug information to display.
        """
        # Update debug info
        if debug_info:
            self.debug_info = debug_info
            
        # Update health and resource bars
        self.health_bar.current_value = self.player_health
        self.health_bar.update(dt)
        
        self.resource_bar.current_value = self.player_resource
        self.resource_bar.update(dt)
        
        # Update status panel
        self.status_panel.player_level = self.player_level
        self.status_panel.time_of_day = self.time_of_day
        self.status_panel.weather = self.weather
        self.status_panel.update(dt)
        
        # Update ability bar
        self.ability_bar.abilities = self.player_abilities
        self.ability_bar.update(dt)
        
        # Update quest tracker
        self.quest_tracker.quests = self.active_quests
        self.quest_tracker.update(dt)
        
        # Update minimap
        self.minimap.update(dt)
        
    def draw(self, screen):
        """
        Draw the HUD.
        
        Args:
            screen: The pygame screen to draw on.
        """
        # Draw all UI elements
        for element in self.ui_elements:
            element.draw(screen)
            
        # Draw debug info if enabled
        if self.show_debug:
            self._draw_debug_info(screen)
            
    def _draw_debug_info(self, screen):
        """Draw debug information overlay."""
        # Create debug panel
        debug_panel = pygame.Surface((300, 150), pygame.SRCALPHA)
        debug_panel.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Draw debug info text
        y_offset = 10
        for key, value in self.debug_info.items():
            text = f"{key}: {value}"
            text_surface = self.small_font.render(text, True, (255, 255, 255))
            debug_panel.blit(text_surface, (10, y_offset))
            y_offset += 20
            
        # Draw debug panel
        screen.blit(debug_panel, (20, 100))
        
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            bool: True if event was handled, False otherwise.
        """
        # Toggle debug info
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.show_debug = not self.show_debug
            return True
            
        # Check if any UI element handled the event
        for element in self.ui_elements:
            try:
                if hasattr(element, 'handle_event') and element.handle_event(event):
                    return True
            except AttributeError:
                # Handle case where event is missing expected attributes
                continue
                
        return False
        
    def set_player_data(self, health, max_health, resource, max_resource, level):
        """
        Set player data for the HUD.
        
        Args:
            health (int): Current player health.
            max_health (int): Maximum player health.
            resource (int): Current player resource (mana, energy, etc.).
            max_resource (int): Maximum player resource.
            level (int): Player level.
        """
        self.player_health = health
        self.player_max_health = max_health
        self.player_resource = resource
        self.player_max_resource = max_resource
        self.player_level = level
        
        # Update UI elements
        self.health_bar.max_value = max_health
        self.resource_bar.max_value = max_resource
        
    def set_abilities(self, abilities):
        """
        Set player abilities for the ability bar.
        
        Args:
            abilities (list): List of player abilities.
        """
        self.player_abilities = abilities
        
    def set_quests(self, quests):
        """
        Set active quests for the quest tracker.
        
        Args:
            quests (list): List of active quests.
        """
        self.active_quests = quests
        
    def set_game_state(self, area, time_of_day, weather):
        """
        Set game state information.
        
        Args:
            area (str): Current area name.
            time_of_day (str): Current time of day.
            weather (str): Current weather condition.
        """
        self.current_area = area
        self.time_of_day = time_of_day
        self.weather = weather 