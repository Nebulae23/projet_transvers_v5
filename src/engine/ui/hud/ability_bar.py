import pygame

class AbilityBar:
    def __init__(self, x, y, width, height, player_id, world):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.world = world
        
        # Default settings
        self.slot_size = (50, 50)
        self.padding = 5
        self.border_color = (120, 120, 120)
        self.slot_bg_color = (60, 60, 60)
        self.cooldown_overlay_color = (30, 30, 30, 180)  # Semi-transparent
        self.cooldown_text_color = (240, 240, 240)
        
        # Placeholder for ability slots
        self.ability_slots = []
        self.num_slots = 6  # Default number of slots
        
        # Initialize slots
        self._init_slots()
        
    def _init_slots(self):
        """Initialize ability slots based on width and slot size"""
        # Calculate how many slots can fit in the given width
        max_slots = (self.width + self.padding) // (self.slot_size[0] + self.padding)
        self.num_slots = min(max_slots, 6)  # Cap at 6 slots or available space
        
        # Create slots
        self.ability_slots = []
        for i in range(self.num_slots):
            slot_x = self.x + i * (self.slot_size[0] + self.padding)
            slot_y = self.y
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size[0], self.slot_size[1])
            self.ability_slots.append({
                'rect': slot_rect,
                'ability_id': None,
                'cooldown': 0,
                'max_cooldown': 0,
                'icon': None
            })
    
    def update(self, dt):
        """Update ability cooldowns"""
        # For now just use a dummy implementation
        pass
        
    def draw(self, screen):
        """Draw ability slots and icons"""
        try:
            # Draw each ability slot
            for slot in self.ability_slots:
                # Draw slot background
                pygame.draw.rect(screen, self.slot_bg_color, slot['rect'])
                
                # Draw slot border
                pygame.draw.rect(screen, self.border_color, slot['rect'], 2)
                
                # If an ability icon exists, draw it
                if slot['icon']:
                    # This would draw the ability icon texture
                    pass
                
                # Draw a placeholder if no icon
                else:
                    font = pygame.font.SysFont(None, 20)
                    text = font.render("?", True, (200, 200, 200))
                    text_rect = text.get_rect(center=slot['rect'].center)
                    screen.blit(text, text_rect)
                
                # If on cooldown, draw overlay
                if slot['cooldown'] > 0:
                    # Draw semi-transparent cooldown overlay
                    cooldown_surf = pygame.Surface(slot['rect'].size, pygame.SRCALPHA)
                    cooldown_surf.fill(self.cooldown_overlay_color)
                    screen.blit(cooldown_surf, slot['rect'])
                    
                    # Draw cooldown text
                    cooldown_text = f"{slot['cooldown']:.1f}"
                    if slot['cooldown'] < 1:
                        cooldown_text = f"{slot['cooldown']:.1f}"
                    else:
                        cooldown_text = f"{int(slot['cooldown'])}"
                        
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(cooldown_text, True, self.cooldown_text_color)
                    text_rect = text.get_rect(center=slot['rect'].center)
                    screen.blit(text, text_rect)
                    
        except Exception as e:
            print(f"Error drawing ability bar: {e}")
            
    def handle_event(self, event):
        """Handle mouse clicks on ability slots"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for i, slot in enumerate(self.ability_slots):
                if slot['rect'].collidepoint(pos):
                    print(f"Ability slot {i+1} clicked")
                    # Here you would trigger the ability
                    return True
        return False
        
    def set_colors(self, theme):
        """Set colors based on theme"""
        try:
            self.border_color = theme.get('ability_slot_border', self.border_color)
            self.slot_bg_color = theme.get('ability_slot_bg', self.slot_bg_color)
            self.cooldown_overlay_color = theme.get('ability_cooldown_overlay', self.cooldown_overlay_color)
            self.cooldown_text_color = theme.get('ability_cooldown_text', self.cooldown_text_color)
        except Exception as e:
            print(f"Error setting ability bar colors: {e}")