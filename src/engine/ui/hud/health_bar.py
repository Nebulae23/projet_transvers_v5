import pygame

class HealthBar:
    def __init__(self, x, y, width, height, player_id, world):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.world = world
        # Default colors
        self.border_color = (50, 50, 50)
        self.health_color = (0, 255, 0)
        self.missing_health_color = (255, 0, 0)
        self.background_color = (40, 0, 0)
        # Animation values
        self.displayed_health_ratio = 1.0
        self.target_health_ratio = 1.0
        self.animation_speed = 2.0  # Units per second

    def update(self, dt):
        # Get current health
        try:
            health_component = self.world.get_entity(self.player_id).get_component('Health')
            if health_component:
                current_health = health_component.current_health
                max_health = health_component.max_health
                self.target_health_ratio = max(0.0, min(1.0, current_health / max_health if max_health > 0 else 0))
            else:
                self.target_health_ratio = 0.0
        except Exception as e:
            print(f"Error updating health bar: {e}")
            # Default to 0 if something went wrong
            self.target_health_ratio = 0.0

        # Animate health bar
        if self.displayed_health_ratio != self.target_health_ratio:
            # Gradually move displayed health toward target health
            if self.displayed_health_ratio < self.target_health_ratio:
                self.displayed_health_ratio = min(
                    self.target_health_ratio, 
                    self.displayed_health_ratio + self.animation_speed * dt
                )
            else:
                self.displayed_health_ratio = max(
                    self.target_health_ratio, 
                    self.displayed_health_ratio - self.animation_speed * dt
                )

    def draw(self, screen):
        try:
            # Draw background
            bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, self.background_color, bg_rect)
            
            # Draw current health
            health_width = int(self.width * self.displayed_health_ratio)
            if health_width > 0:
                health_rect = pygame.Rect(self.x, self.y, health_width, self.height)
                pygame.draw.rect(screen, self.health_color, health_rect)
            
            # Draw border
            pygame.draw.rect(screen, self.border_color, self.rect, 2)
        except Exception as e:
            print(f"Error drawing health bar: {e}")

    def handle_event(self, event):
        pass  # Health bar is not interactive

    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            self.border_color = theme.get('health_bar_border', self.border_color)
            self.health_color = theme.get('health_full', self.health_color)
            self.missing_health_color = theme.get('health_missing', self.missing_health_color)
            self.background_color = theme.get('health_background', self.background_color)
        except Exception as e:
            print(f"Error setting health bar colors: {e}")