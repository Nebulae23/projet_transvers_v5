import pygame

def get_theme():
    """Returns a dictionary with HUD theme values"""

    # Return theme as dictionary without font initialization
    return {
        # Colors
        'primary_color': (200, 200, 200),
        'secondary_color': (100, 100, 100),
        'accent_color': (255, 165, 0),  # Orange accent

        # Health Bar
        'health_bar_border': (50, 50, 50),
        'health_full': (0, 200, 0),
        'health_missing': (180, 0, 0),
        'health_background': (40, 0, 0),

        # Resource Bars (Example: Mana)
        'mana_bar_border': (50, 50, 50),
        'mana_full': (0, 100, 255),
        'mana_missing': (0, 50, 150),
        'mana_background': (0, 20, 80),

        # Ability Bar
        'ability_slot_bg': (60, 60, 60),
        'ability_slot_border': (120, 120, 120),
        'ability_cooldown_overlay': (30, 30, 30, 190),  # Darker semi-transparent
        'ability_cooldown_text': (240, 240, 240),

        # Minimap
        'minimap_bg': (20, 20, 20, 200),  # Semi-transparent dark
        'minimap_border': (150, 150, 150),
        'minimap_player_icon': (255, 50, 50),
        'minimap_npc_icon': (50, 255, 50),
        'minimap_poi_icon': (255, 255, 50),

        # Status Effects
        'status_icon_bg': (40, 40, 40, 180),
        'status_icon_border': (90, 90, 90),
        'status_duration_text': (230, 230, 230),
        'status_duration_bg': (0, 0, 0, 150),

        # Quest Tracker
        'quest_tracker_bg': (10, 10, 10, 170),  # Very dark semi-transparent
        'quest_title_color': (255, 215, 0),  # Gold
        'quest_objective_color': (220, 220, 220),
        'quest_objective_completed_color': (120, 120, 120),

        # Fonts - These will be initialized later when pygame is ready
        'font_default_size': 18,
        'font_large_size': 24,
        'font_small_size': 16
    } 