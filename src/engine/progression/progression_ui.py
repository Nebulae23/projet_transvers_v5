# src/engine/progression/progression_ui.py
import pygame
from typing import Tuple, Optional
from ..ui.ui_base import UIElement, UIElementType, TextElement, BarElement
from ..ui.layout import Layout, LayoutType
from .experience import ExperienceSystem
from .stats import CharacterStats, StatType

class StatDisplayUI(UIElement):
    def __init__(self,
                position: Tuple[int, int],
                size: Tuple[int, int],
                stat_type: StatType,
                character_stats: CharacterStats):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.stat_type = stat_type
        self.character_stats = character_stats
        
        # Create display elements
        stat_info = character_stats.stats[stat_type]
        
        self.name_text = TextElement(
            (position[0], position[1]),
            stat_info.name,
            24
        )
        
        self.value_text = TextElement(
            (position[0] + 120, position[1]),
            str(int(character_stats.get_stat_value(stat_type))),
            24
        )
        
        self.add_button = TextElement(
            (position[0] + 180, position[1]),
            "+",
            24
        )
        self.add_button.set_click_handler(self._on_increase)
        
        # Add elements
        self.add_child(self.name_text)
        self.add_child(self.value_text)
        self.add_child(self.add_button)
        
    def _on_increase(self):
        if self.character_stats.increase_stat(self.stat_type):
            self.update_display()
            
    def update_display(self):
        self.value_text.set_text(
            str(int(self.character_stats.get_stat_value(self.stat_type)))
        )
        
class LevelUpNotification(UIElement):
    def __init__(self,
                position: Tuple[int, int],
                size: Tuple[int, int],
                level: int):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.set_background((0, 0, 0, 180))
        self.lifetime = 3.0  # Seconds to display
        
        # Create text elements
        self.level_text = TextElement(
            (position[0] + 10, position[1] + 10),
            f"Level Up! Level {level}",
            32
        )
        
        self.rewards_text = TextElement(
            (position[0] + 10, position[1] + 50),
            "Rewards:\n+1 Stat Point\n+1 Skill Point",
            24
        )
        
        self.add_child(self.level_text)
        self.add_child(self.rewards_text)
        
    def update(self, dt: float) -> bool:
        """Update notification and return True if it should be removed"""
        self.lifetime -= dt
        return self.lifetime <= 0

class ProgressionUI(UIElement):
    def __init__(self,
                position: Tuple[int, int],
                size: Tuple[int, int],
                exp_system: ExperienceSystem,
                character_stats: CharacterStats):
        super().__init__(position, size, UIElementType.CONTAINER)
        self.exp_system = exp_system
        self.character_stats = character_stats
        self.notifications: List[LevelUpNotification] = []
        
        # Create experience bar
        self.level_text = TextElement(
            (position[0], position[1]),
            f"Level {exp_system.current_level}",
            28
        )
        
        self.exp_bar = BarElement(
            (position[0], position[1] + 40),
            (300, 20),
            exp_system.get_progress_to_next_level()
        )
        
        # Create stat displays
        self.stat_displays = []
        for i, stat_type in enumerate(StatType):
            stat_display = StatDisplayUI(
                (position[0], position[1] + 100 + i * 40),
                (200, 30),
                stat_type,
                character_stats
            )
            self.stat_displays.append(stat_display)
            self.add_child(stat_display)
            
        # Add elements
        self.add_child(self.level_text)
        self.add_child(self.exp_bar)
        
        # Register callbacks
        exp_system.register_level_up_callback(self._on_level_up)
        character_stats.register_stat_changed_callback(self._on_stats_changed)
        
    def _on_level_up(self, new_level: int):
        self.level_text.set_text(f"Level {new_level}")
        
        # Create notification
        notification = LevelUpNotification(
            (self.position[0] + 400, self.position[1]),
            (300, 100),
            new_level
        )
        self.notifications.append(notification)
        self.add_child(notification)
        
    def _on_stats_changed(self):
        for stat_display in self.stat_displays:
            stat_display.update_display()
            
    def update(self, dt: float):
        # Update experience bar
        self.exp_bar.set_value(self.exp_system.get_progress_to_next_level())
        
        # Update notifications
        completed = []
        for notification in self.notifications:
            if notification.update(dt):
                completed.append(notification)
                self.remove_child(notification)
        
        for notification in completed:
            self.notifications.remove(notification)