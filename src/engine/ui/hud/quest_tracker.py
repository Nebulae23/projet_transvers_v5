import pygame

class QuestTracker:
    def __init__(self, x, y, width, height, player_id, world):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.world = world
        
        # Default settings
        self.padding = 10
        self.line_spacing = 5
        
        # Default colors
        self.bg_color = (10, 10, 10, 170)  # Very dark semi-transparent
        self.title_color = (255, 215, 0)   # Gold
        self.objective_color = (220, 220, 220)
        self.objective_completed_color = (120, 120, 120)
        self.border_color = (90, 90, 90)
        
        # Tracked quests
        self.active_quests = []  # Will hold quest data
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 24)
        self.objective_font = pygame.font.SysFont(None, 20)
        
    def update(self, dt):
        """Update quest data"""
        try:
            # This would normally fetch quests from a quest system
            # For now, just use dummy data
            self.active_quests = [
                {
                    'title': 'Defend the City',
                    'objectives': [
                        {'description': 'Build 3 defense towers', 'current': 1, 'required': 3, 'completed': False},
                        {'description': 'Survive the first night', 'current': 0, 'required': 1, 'completed': False},
                        {'description': 'Defeat the boss', 'current': 0, 'required': 1, 'completed': False}
                    ],
                    'priority': 1
                },
                {
                    'title': 'Gather Resources',
                    'objectives': [
                        {'description': 'Collect 100 wood', 'current': 75, 'required': 100, 'completed': False},
                        {'description': 'Collect 50 stone', 'current': 50, 'required': 50, 'completed': True}
                    ],
                    'priority': 2
                }
            ]
            
            # Sort quests by priority
            self.active_quests.sort(key=lambda q: q['priority'])
            
            # Update objectives completion status
            for quest in self.active_quests:
                for objective in quest['objectives']:
                    objective['completed'] = objective['current'] >= objective['required']
            
        except Exception as e:
            print(f"Error updating quest tracker: {e}")
            
    def draw(self, screen):
        """Draw quest tracker UI"""
        try:
            # Skip if no quests
            if not self.active_quests:
                return
                
            # Create background surface
            tracker_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            tracker_surface.fill(self.bg_color)
            
            # Draw header
            font = pygame.font.SysFont(None, 26)
            header = font.render("Active Quests", True, (255, 255, 255))
            header_rect = header.get_rect(topleft=(self.padding, self.padding))
            tracker_surface.blit(header, header_rect)
            
            # Draw quests
            y_offset = header_rect.bottom + 10
            
            for quest in self.active_quests:
                # Title
                title_surf = self.title_font.render(quest['title'], True, self.title_color)
                title_rect = title_surf.get_rect(topleft=(self.padding, y_offset))
                tracker_surface.blit(title_surf, title_rect)
                y_offset = title_rect.bottom + 5
                
                # Objectives
                for objective in quest['objectives']:
                    # Set color based on completion
                    color = self.objective_completed_color if objective['completed'] else self.objective_color
                    
                    # Format progress
                    if objective['required'] > 1:
                        progress_text = f"{objective['current']}/{objective['required']} "
                    else:
                        progress_text = ""
                        
                    # Create objective text
                    text = f"{progress_text}{objective['description']}"
                    if objective['completed']:
                        text = f"✓ {text}"
                    else:
                        text = f"• {text}"
                        
                    # Render text
                    obj_surf = self.objective_font.render(text, True, color)
                    
                    # Calculate width to fit in panel
                    if obj_surf.get_width() > self.width - (self.padding * 2):
                        # Truncate text or wrap
                        scale = (self.width - (self.padding * 2)) / obj_surf.get_width()
                        obj_surf = pygame.transform.scale(obj_surf, 
                                                       (int(obj_surf.get_width() * scale), 
                                                        obj_surf.get_height()))
                    
                    # Draw objective
                    obj_rect = obj_surf.get_rect(topleft=(self.padding * 2, y_offset))
                    tracker_surface.blit(obj_surf, obj_rect)
                    y_offset = obj_rect.bottom + self.line_spacing
                
                # Add space between quests
                y_offset += 10
                
                # Check if we've run out of space
                if y_offset >= self.height - self.padding:
                    # Draw ellipsis to indicate more quests
                    more_surf = self.objective_font.render("...", True, self.objective_color)
                    more_rect = more_surf.get_rect(topleft=(self.padding, y_offset - 15))
                    tracker_surface.blit(more_surf, more_rect)
                    break
            
            # Draw border
            pygame.draw.rect(tracker_surface, self.border_color, 
                           (0, 0, self.width, self.height), 2)
            
            # Blit to screen
            screen.blit(tracker_surface, (self.x, self.y))
            
        except Exception as e:
            print(f"Error drawing quest tracker: {e}")
            
    def handle_event(self, event):
        """Handle clicks on quest tracker (e.g., select active quest)"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Could implement quest selection or toggling display
                return True
        return False
        
    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            self.bg_color = theme.get('quest_tracker_bg', self.bg_color)
            self.title_color = theme.get('quest_title_color', self.title_color)
            self.objective_color = theme.get('quest_objective_color', self.objective_color)
            self.objective_completed_color = theme.get('quest_objective_completed_color', 
                                                    self.objective_completed_color)
            self.border_color = theme.get('quest_tracker_border', self.border_color)
        except Exception as e:
            print(f"Error setting quest tracker colors: {e}")