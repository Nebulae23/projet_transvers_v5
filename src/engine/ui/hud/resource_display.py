import pygame

class ResourceDisplay:
    def __init__(self, x, y, width, height, player_id, world, resource_type='Mana'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.world = world
        self.resource_type = resource_type
        
        # Default colors - will be updated based on resource type
        self.border_color = (50, 50, 50)
        self.resource_color = (0, 100, 255)  # Default blue for mana
        self.missing_resource_color = (0, 50, 150)
        self.background_color = (0, 20, 80)
        
        # Animation values
        self.displayed_resource_ratio = 1.0
        self.target_resource_ratio = 1.0
        self.animation_speed = 2.0  # Units per second
        
        # Set colors based on resource type
        self._set_colors_by_type()
        
    def _set_colors_by_type(self):
        """Set default colors based on resource type"""
        if self.resource_type.lower() == 'mana':
            self.resource_color = (0, 100, 255)  # Blue
            self.missing_resource_color = (0, 50, 150)
            self.background_color = (0, 20, 80)
        elif self.resource_type.lower() == 'stamina':
            self.resource_color = (255, 200, 0)  # Yellow/gold
            self.missing_resource_color = (150, 100, 0)
            self.background_color = (80, 60, 0)
        elif self.resource_type.lower() == 'rage':
            self.resource_color = (255, 0, 0)  # Red
            self.missing_resource_color = (150, 0, 0)
            self.background_color = (80, 0, 0)
        # Add more resource types as needed
    
    def update(self, dt):
        # Get current resource
        try:
            # Note: This assumes components are named after resource types (e.g., 'Mana', 'Stamina')
            resource_component = self.world.get_entity(self.player_id).get_component(self.resource_type)
            if resource_component:
                current_resource = resource_component.current
                max_resource = resource_component.maximum
                self.target_resource_ratio = max(0.0, min(1.0, current_resource / max_resource if max_resource > 0 else 0))
            else:
                self.target_resource_ratio = 0.0
        except Exception as e:
            print(f"Error updating {self.resource_type} resource display: {e}")
            # Default to 0 if something went wrong
            self.target_resource_ratio = 0.0

        # Animate resource bar
        if self.displayed_resource_ratio != self.target_resource_ratio:
            # Gradually move displayed resource toward target resource
            if self.displayed_resource_ratio < self.target_resource_ratio:
                self.displayed_resource_ratio = min(
                    self.target_resource_ratio, 
                    self.displayed_resource_ratio + self.animation_speed * dt
                )
            else:
                self.displayed_resource_ratio = max(
                    self.target_resource_ratio, 
                    self.displayed_resource_ratio - self.animation_speed * dt
                )

    def draw(self, screen):
        try:
            # Draw background
            bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, self.background_color, bg_rect)
            
            # Draw current resource
            resource_width = int(self.width * self.displayed_resource_ratio)
            if resource_width > 0:
                resource_rect = pygame.Rect(self.x, self.y, resource_width, self.height)
                pygame.draw.rect(screen, self.resource_color, resource_rect)
            
            # Draw border
            pygame.draw.rect(screen, self.border_color, self.rect, 2)
        except Exception as e:
            print(f"Error drawing {self.resource_type} resource display: {e}")

    def handle_event(self, event):
        pass  # Resource display is not interactive

    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            if self.resource_type.lower() == 'mana':
                self.border_color = theme.get('mana_bar_border', self.border_color)
                self.resource_color = theme.get('mana_full', self.resource_color)
                self.missing_resource_color = theme.get('mana_missing', self.missing_resource_color)
                self.background_color = theme.get('mana_background', self.background_color)
            # Add more theme mappings for other resource types
        except Exception as e:
            print(f"Error setting {self.resource_type} resource display colors: {e}")