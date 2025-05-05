import pygame

class Minimap:
    def __init__(self, x, y, width, height, world, player_id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.world = world
        self.player_id = player_id
        
        # Default colors
        self.bg_color = (20, 20, 20, 200)  # Dark semi-transparent
        self.border_color = (150, 150, 150)
        self.player_icon_color = (255, 50, 50)  # Red
        self.npc_icon_color = (50, 255, 50)  # Green
        self.poi_icon_color = (255, 255, 50)  # Yellow
        
        # Map scaling
        self.map_scale = 0.1  # World units to minimap pixels
        self.centered = True  # Whether to center on player
        
    def update(self, dt):
        """Update minimap data"""
        # This would update entity positions, etc.
        pass
        
    def draw(self, screen):
        """Draw the minimap"""
        try:
            # Create semi-transparent surface for minimap background
            minimap_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            minimap_surface.fill(self.bg_color)
            
            # Draw entities on minimap
            try:
                # Get player position for centering
                player_entity = self.world.get_entity(self.player_id)
                if player_entity:
                    transform = player_entity.get_component('Transform')
                    if transform:
                        player_pos = transform.position
                        
                        # Calculate minimap center position
                        center_x = self.width // 2
                        center_y = self.height // 2
                        
                        # Draw player at center
                        pygame.draw.circle(minimap_surface, self.player_icon_color, 
                                          (center_x, center_y), 5)
                        
                        # Draw other entities relative to player
                        for entity in self.world.entities:
                            if entity.id == self.player_id:
                                continue  # Skip player, already drawn
                                
                            entity_transform = entity.get_component('Transform')
                            if entity_transform:
                                # Calculate position relative to player
                                rel_x = (entity_transform.position[0] - player_pos[0]) * self.map_scale
                                rel_y = (entity_transform.position[1] - player_pos[1]) * self.map_scale
                                
                                # Calculate screen position
                                screen_x = center_x + rel_x
                                screen_y = center_y + rel_y
                                
                                # Skip if outside minimap bounds
                                if (screen_x < 0 or screen_x >= self.width or 
                                    screen_y < 0 or screen_y >= self.height):
                                    continue
                                
                                # Determine color based on entity type
                                entity_color = self.npc_icon_color
                                # You would determine this based on entity components
                                
                                # Draw entity
                                pygame.draw.circle(minimap_surface, entity_color, 
                                                 (int(screen_x), int(screen_y)), 3)
            except Exception as e:
                print(f"Error drawing entities on minimap: {e}")
                
            # Draw border
            pygame.draw.rect(minimap_surface, self.border_color, 
                            (0, 0, self.width, self.height), 2)
            
            # Blit minimap to screen
            screen.blit(minimap_surface, (self.x, self.y))
            
        except Exception as e:
            print(f"Error drawing minimap: {e}")
            
    def handle_event(self, event):
        """Handle clicks on minimap"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Calculate world position from minimap click
                # This would be used for navigation
                return True
        return False
        
    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            self.bg_color = theme.get('minimap_bg', self.bg_color)
            self.border_color = theme.get('minimap_border', self.border_color)
            self.player_icon_color = theme.get('minimap_player_icon', self.player_icon_color)
            self.npc_icon_color = theme.get('minimap_npc_icon', self.npc_icon_color)
            self.poi_icon_color = theme.get('minimap_poi_icon', self.poi_icon_color)
        except Exception as e:
            print(f"Error setting minimap colors: {e}")