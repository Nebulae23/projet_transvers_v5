import pygame

class StatusEffectsDisplay:
    def __init__(self, x, y, width, height, player_id, world):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.world = world
        
        # Default settings
        self.icon_size = (32, 32)
        self.padding = 4
        self.max_icons_per_row = 5  # Maximum number of icons per row
        self.layout = 'horizontal'  # 'horizontal' or 'vertical'
        
        # Default colors
        self.bg_color = (40, 40, 40, 180)  # Semi-transparent dark bg
        self.border_color = (90, 90, 90)
        self.duration_text_color = (230, 230, 230)
        self.duration_bg_color = (0, 0, 0, 150)
        
        # Active status effects
        self.active_effects = []  # Will hold status effect data
        
    def update(self, dt):
        """Update status effects and durations"""
        try:
            # This would normally fetch status effects from the player entity
            # For now, just use dummy data
            self.active_effects = []
            
            # Example dummy effects for testing
            dummy_effects = [
                {'name': 'Poison', 'duration': 5.2, 'icon': None, 'positive': False},
                {'name': 'Strength', 'duration': 12.7, 'icon': None, 'positive': True},
                {'name': 'Haste', 'duration': 8.3, 'icon': None, 'positive': True}
            ]
            
            # Update durations (would happen in game logic)
            for effect in dummy_effects:
                effect['duration'] -= dt
                if effect['duration'] > 0:
                    self.active_effects.append(effect)
            
        except Exception as e:
            print(f"Error updating status effects: {e}")
            
    def draw(self, screen):
        """Draw status effect icons and durations"""
        try:
            # Skip drawing if no effects
            if not self.active_effects:
                return
                
            # Create background surface
            bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg_surface.fill(self.bg_color)
            
            # Calculate layout
            max_per_row = min(self.max_icons_per_row, 
                             (self.width + self.padding) // (self.icon_size[0] + self.padding))
            
            # Draw each effect
            for i, effect in enumerate(self.active_effects):
                # Calculate position based on layout
                if self.layout == 'horizontal':
                    row = i // max_per_row
                    col = i % max_per_row
                else:  # vertical
                    col = i // max_per_row
                    row = i % max_per_row
                    
                # Calculate pixel position
                pos_x = self.padding + col * (self.icon_size[0] + self.padding)
                pos_y = self.padding + row * (self.icon_size[1] + self.padding)
                
                # Create icon rect
                icon_rect = pygame.Rect(pos_x, pos_y, self.icon_size[0], self.icon_size[1])
                
                # Draw icon background (colored based on positive/negative)
                if effect.get('positive', False):
                    icon_bg_color = (0, 100, 0)  # Green for positive
                else:
                    icon_bg_color = (100, 0, 0)  # Red for negative
                pygame.draw.rect(bg_surface, icon_bg_color, icon_rect)
                
                # Draw icon border
                pygame.draw.rect(bg_surface, self.border_color, icon_rect, 1)
                
                # Draw icon (if available) or text
                if effect.get('icon'):
                    # bg_surface.blit(effect['icon'], icon_rect.topleft)
                    pass  # Would draw icon here
                else:
                    # Draw text for icon name
                    font = pygame.font.SysFont(None, 16)
                    text = font.render(effect['name'][:2], True, (255, 255, 255))
                    text_rect = text.get_rect(center=icon_rect.center)
                    bg_surface.blit(text, text_rect)
                
                # Draw duration text
                if effect.get('duration', 0) > 0:
                    duration_text = f"{effect['duration']:.1f}"
                    if effect['duration'] > 10:
                        duration_text = f"{int(effect['duration'])}"
                        
                    font = pygame.font.SysFont(None, 14)
                    duration_surf = font.render(duration_text, True, self.duration_text_color)
                    
                    # Draw text background
                    text_bg_rect = pygame.Rect(
                        icon_rect.left, 
                        icon_rect.bottom - 14, 
                        icon_rect.width, 
                        14
                    )
                    text_bg = pygame.Surface((text_bg_rect.width, text_bg_rect.height), pygame.SRCALPHA)
                    text_bg.fill((0, 0, 0, 200))
                    bg_surface.blit(text_bg, text_bg_rect)
                    
                    # Draw text
                    text_rect = duration_surf.get_rect(center=text_bg_rect.center)
                    bg_surface.blit(duration_surf, text_rect)
            
            # Draw border around the whole panel
            pygame.draw.rect(bg_surface, self.border_color, 
                           (0, 0, self.width, self.height), 1)
            
            # Blit to screen
            screen.blit(bg_surface, (self.x, self.y))
            
        except Exception as e:
            print(f"Error drawing status effects: {e}")
            
    def handle_event(self, event):
        """Handle mouse events on status effects (e.g., hover for details)"""
        # Could implement tooltips on hover
        return False
        
    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            self.bg_color = theme.get('status_icon_bg', self.bg_color)
            self.border_color = theme.get('status_icon_border', self.border_color)
            self.duration_text_color = theme.get('status_duration_text', self.duration_text_color)
            self.duration_bg_color = theme.get('status_duration_bg', self.duration_bg_color)
            self.icon_size = theme.get('status_effects_icon_size', self.icon_size)
        except Exception as e:
            print(f"Error setting status effects colors: {e}")