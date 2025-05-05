# src/engine/systems/achievement_ui.py
from typing import List, Optional, Dict
import pygame
import pygame.freetype
from dataclasses import dataclass
from ..ui.ui_base import UIElement, UIManager
from ..graphics.hd2d_renderer import HD2DRenderer
from .achievement_system import Achievement, AchievementCategory

@dataclass
class AchievementNotification:
    achievement: Achievement
    duration: float
    alpha: float = 0.0
    position: tuple[float, float] = (0, 0)
    
class AchievementUI:
    def __init__(self, ui_manager: UIManager, hd2d_renderer: HD2DRenderer):
        self.ui_manager = ui_manager
        self.renderer = hd2d_renderer
        self.font = pygame.freetype.Font("assets/fonts/main.ttf", 16)
        self.title_font = pygame.freetype.Font("assets/fonts/title.ttf", 24)
        
        # HD-2D style configuration
        self.notification_style = {
            "background": (20, 20, 30, 200),
            "border": (255, 215, 0, 255),
            "text": (255, 255, 255, 255),
            "highlight": (100, 149, 237, 255)
        }
        
        self.active_notifications: List[AchievementNotification] = []
        self.notification_duration = 3.0
        self.max_notifications = 3
        
        # Achievement panel state
        self.panel_visible = False
        self.selected_category = AchievementCategory.COMBAT
        self.scroll_offset = 0
        self.achievements_per_page = 8
        
    def show_achievement_notification(self, achievement: Achievement):
        # Remove oldest notification if at max
        if len(self.active_notifications) >= self.max_notifications:
            self.active_notifications.pop(0)
            
        # Calculate notification position
        screen_size = self.ui_manager.get_screen_size()
        base_y = 50
        offset_y = len(self.active_notifications) * 70
        
        notification = AchievementNotification(
            achievement=achievement,
            duration=self.notification_duration,
            position=(screen_size[0] - 320, base_y + offset_y)
        )
        
        self.active_notifications.append(notification)
        
    def toggle_achievement_panel(self):
        self.panel_visible = not self.panel_visible
        if self.panel_visible:
            self.scroll_offset = 0
            
    def update(self, dt: float):
        # Update notifications
        completed_notifications = []
        for notification in self.active_notifications:
            notification.duration -= dt
            
            # Fade in
            if notification.duration > self.notification_duration - 0.5:
                progress = (self.notification_duration - notification.duration) * 2
                notification.alpha = min(1.0, progress)
            # Fade out
            elif notification.duration < 0.5:
                notification.alpha = max(0.0, notification.duration * 2)
            
            if notification.duration <= 0:
                completed_notifications.append(notification)
                
        # Remove completed notifications
        for notification in completed_notifications:
            self.active_notifications.remove(notification)
            
    def render(self, surface: pygame.Surface):
        # Render active notifications
        self._render_notifications(surface)
        
        # Render achievement panel if visible
        if self.panel_visible:
            self._render_achievement_panel(surface)
            
    def _render_notifications(self, surface: pygame.Surface):
        for notification in self.active_notifications:
            notif_surface = pygame.Surface((300, 60), pygame.SRCALPHA)
            
            # Draw HD-2D style background
            self.renderer.draw_panel_2d(
                notif_surface,
                (0, 0),
                (300, 60),
                self.notification_style["background"],
                self.notification_style["border"],
                notification.alpha
            )
            
            # Draw achievement icon with HD-2D effects
            icon = pygame.image.load(notification.achievement.icon_path)
            icon = pygame.transform.scale(icon, (40, 40))
            self.renderer.apply_hd2d_effects(icon)
            notif_surface.blit(icon, (10, 10))
            
            # Draw text
            title_surface, _ = self.font.render(
                "Achievement Unlocked!",
                self.notification_style["highlight"]
            )
            name_surface, _ = self.font.render(
                notification.achievement.name,
                self.notification_style["text"]
            )
            
            notif_surface.blit(title_surface, (60, 10))
            notif_surface.blit(name_surface, (60, 30))
            
            # Apply HD-2D post-processing
            self.renderer.apply_hd2d_effects(notif_surface)
            
            # Draw to main surface
            surface.blit(
                notif_surface,
                notification.position,
                special_flags=pygame.BLEND_ALPHA_SDL2
            )
            
    def _render_achievement_panel(self, surface: pygame.Surface):
        screen_size = self.ui_manager.get_screen_size()
        panel_size = (600, 400)
        panel_pos = (
            (screen_size[0] - panel_size[0]) / 2,
            (screen_size[1] - panel_size[1]) / 2
        )
        
        # Create panel surface
        panel_surface = pygame.Surface(panel_size, pygame.SRCALPHA)
        
        # Draw HD-2D style background
        self.renderer.draw_panel_2d(
            panel_surface,
            (0, 0),
            panel_size,
            self.notification_style["background"],
            self.notification_style["border"],
            1.0
        )
        
        # Draw category tabs
        tab_width = panel_size[0] / len(AchievementCategory)
        for i, category in enumerate(AchievementCategory):
            tab_rect = pygame.Rect(i * tab_width, 0, tab_width, 30)
            color = self.notification_style["highlight"] if category == self.selected_category else self.notification_style["border"]
            pygame.draw.rect(panel_surface, color, tab_rect, 1)
            
            tab_text, _ = self.font.render(
                category.value.title(),
                self.notification_style["text"]
            )
            panel_surface.blit(
                tab_text,
                (tab_rect.centerx - tab_text.get_width()/2,
                 tab_rect.centery - tab_text.get_height()/2)
            )
            
        # Draw achievements
        self._render_achievement_list(panel_surface)
        
        # Apply HD-2D effects
        self.renderer.apply_hd2d_effects(panel_surface)
        
        # Draw to main surface
        surface.blit(panel_surface, panel_pos)
        
    def _render_achievement_list(self, surface: pygame.Surface):
        start_y = 40
        height = 50
        width = surface.get_width() - 20
        
        for i in range(self.achievements_per_page):
            index = self.scroll_offset + i
            if index >= len(self.achievements):
                break
                
            achievement = self.achievements[index]
            if achievement.category != self.selected_category:
                continue
                
            # Draw achievement entry with HD-2D style
            entry_rect = pygame.Rect(10, start_y + i * height, width, height - 5)
            self.renderer.draw_panel_2d(
                surface,
                entry_rect.topleft,
                entry_rect.size,
                self.notification_style["background"],
                self.notification_style["border"],
                0.8
            )
            
            # Draw icon
            icon = pygame.image.load(achievement.icon_path)
            icon = pygame.transform.scale(icon, (30, 30))
            self.renderer.apply_hd2d_effects(icon)
            surface.blit(icon, (entry_rect.left + 10, entry_rect.top + 10))
            
            # Draw text
            name_surface, _ = self.font.render(
                achievement.name,
                self.notification_style["text"]
            )
            desc_surface, _ = self.font.render(
                achievement.description,
                self.notification_style["text"]
            )
            
            surface.blit(name_surface, (entry_rect.left + 50, entry_rect.top + 5))
            surface.blit(desc_surface, (entry_rect.left + 50, entry_rect.top + 25))