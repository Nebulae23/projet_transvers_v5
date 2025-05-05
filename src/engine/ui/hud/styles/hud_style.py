# src/engine/ui/hud/styles/hud_style.py

class HUDStyle:
    """
    HUD style definitions for game UI.
    Provides color schemes and styling parameters for HUD components.
    """
    
    # Color schemes
    PRIMARY_COLOR = (220, 220, 255)  # Light blue-ish white
    SECONDARY_COLOR = (180, 180, 220)  # Slightly darker blue-ish white
    
    ACCENT_COLOR = (255, 220, 150)  # Gold/amber accent
    ACCENT_DARK = (200, 170, 100)  # Darker gold/amber
    
    HEALTH_COLOR = (220, 50, 50)  # Red for health
    HEALTH_BG_COLOR = (60, 30, 30)  # Dark red for health background
    
    MANA_COLOR = (50, 100, 220)  # Blue for mana/resource
    MANA_BG_COLOR = (30, 40, 60)  # Dark blue for mana background
    
    STAMINA_COLOR = (50, 220, 50)  # Green for stamina
    STAMINA_BG_COLOR = (30, 60, 30)  # Dark green for stamina background
    
    XP_COLOR = (220, 150, 255)  # Purple for experience
    XP_BG_COLOR = (60, 40, 70)  # Dark purple for experience background
    
    UI_BG_COLOR = (20, 20, 30, 180)  # Semi-transparent dark blue
    UI_BORDER_COLOR = (100, 100, 140)  # Light blue-ish border
    
    # Font sizes
    TITLE_FONT_SIZE = 36
    SUBTITLE_FONT_SIZE = 24
    NORMAL_FONT_SIZE = 18
    SMALL_FONT_SIZE = 14
    
    # Border sizes
    THIN_BORDER = 1
    NORMAL_BORDER = 2
    THICK_BORDER = 3
    
    # Padding and margins
    SMALL_PADDING = 5
    NORMAL_PADDING = 10
    LARGE_PADDING = 20
    
    # Element sizes
    ICON_SIZE_SMALL = 24
    ICON_SIZE_NORMAL = 32
    ICON_SIZE_LARGE = 48
    
    BUTTON_HEIGHT = 30
    BUTTON_WIDTH_SMALL = 100
    BUTTON_WIDTH_NORMAL = 150
    BUTTON_WIDTH_LARGE = 200
    
    # Animation parameters
    ANIMATION_SPEED_SLOW = 0.5
    ANIMATION_SPEED_NORMAL = 1.0
    ANIMATION_SPEED_FAST = 2.0
    
    # Hover effect
    HOVER_COLOR_SHIFT = 30  # Amount to lighten colors on hover
    
    @classmethod
    def get_button_colors(cls, state="normal"):
        """
        Get button colors based on state.
        
        Args:
            state (str): Button state ('normal', 'hover', 'pressed', 'disabled')
            
        Returns:
            tuple: (bg_color, text_color, border_color)
        """
        if state == "normal":
            return ((40, 40, 60, 220), cls.PRIMARY_COLOR, cls.UI_BORDER_COLOR)
        elif state == "hover":
            return ((60, 60, 80, 220), cls.PRIMARY_COLOR, cls.ACCENT_COLOR)
        elif state == "pressed":
            return ((30, 30, 50, 220), cls.ACCENT_COLOR, cls.ACCENT_DARK)
        elif state == "disabled":
            return ((30, 30, 40, 180), (150, 150, 180), (80, 80, 100))
        return ((40, 40, 60, 220), cls.PRIMARY_COLOR, cls.UI_BORDER_COLOR)
    
    @classmethod
    def lighten_color(cls, color, amount=30):
        """
        Lighten a color by the specified amount.
        
        Args:
            color (tuple): RGBA or RGB color.
            amount (int): Amount to lighten (0-255).
            
        Returns:
            tuple: Lightened color.
        """
        if len(color) == 4:
            # RGBA color
            return (min(255, color[0] + amount), 
                   min(255, color[1] + amount), 
                   min(255, color[2] + amount),
                   color[3])
        else:
            # RGB color
            return (min(255, color[0] + amount), 
                   min(255, color[1] + amount), 
                   min(255, color[2] + amount))
    
    @classmethod
    def darken_color(cls, color, amount=30):
        """
        Darken a color by the specified amount.
        
        Args:
            color (tuple): RGBA or RGB color.
            amount (int): Amount to darken (0-255).
            
        Returns:
            tuple: Darkened color.
        """
        if len(color) == 4:
            # RGBA color
            return (max(0, color[0] - amount), 
                   max(0, color[1] - amount), 
                   max(0, color[2] - amount),
                   color[3])
        else:
            # RGB color
            return (max(0, color[0] - amount), 
                   max(0, color[1] - amount), 
                   max(0, color[2] - amount)) 