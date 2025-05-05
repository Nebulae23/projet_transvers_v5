import pygame

# TODO: Integrate with a global layout system or screen resolution manager

# Function to get layout based on screen dimensions
def get_layout_config(screen_width, screen_height):
    # General Margins/Padding
    margin = 10  # Margin from screen edges
    padding = 5  # Padding between elements in the same group

    # --- Element Positions and Sizes ---
    # Health Bar (Top-Left)
    health_bar_pos = (margin, margin)
    health_bar_size = (200, 20)

    # Resource Bars (Below Health Bar) - Example for Mana & Stamina
    resource_bar_size = (150, 15)
    mana_bar_pos = (margin, health_bar_pos[1] + health_bar_size[1] + padding)
    stamina_bar_pos = (margin, mana_bar_pos[1] + resource_bar_size[1] + padding)

    # Ability Bar (Bottom-Center)
    ability_bar_slot_size = (40, 40)
    ability_bar_padding = 8
    # Calculate total width needed based on assumed number of slots (e.g., 6)
    num_ability_slots = 6
    ability_bar_total_width = (num_ability_slots * ability_bar_slot_size[0]) + ((num_ability_slots - 1) * ability_bar_padding)
    ability_bar_x = (screen_width - ability_bar_total_width) // 2
    ability_bar_y = screen_height - margin - ability_bar_slot_size[1]
    ability_bar_pos = (ability_bar_x, ability_bar_y)
    ability_bar_size = (ability_bar_total_width, ability_bar_slot_size[1])  # Width depends on slots

    # Minimap (Top-Right)
    minimap_size = (150, 150)
    minimap_pos = (screen_width - margin - minimap_size[0], margin)

    # Status Effects (Below Minimap or near Health Bar)
    # Example: Below Minimap
    status_effects_pos = (minimap_pos[0], minimap_pos[1] + minimap_size[1] + padding)
    status_effects_size = (minimap_size[0], 50)  # Width matches minimap, height adjusts
    status_effects_icon_size = (32, 32)
    status_effects_layout = 'horizontal'  # or 'vertical'

    # Quest Tracker (Mid-Right)
    quest_tracker_size = (250, 300)
    quest_tracker_pos = (screen_width - margin - quest_tracker_size[0], (screen_height - quest_tracker_size[1]) // 2)

    # Return as dictionary for easier access
    return {
        'screen_width': screen_width,
        'screen_height': screen_height,
        'margin': margin,
        'padding': padding,
        'health_bar_pos': health_bar_pos,
        'health_bar_size': health_bar_size,
        'resource_bar_size': resource_bar_size,
        'mana_bar_pos': mana_bar_pos,
        'stamina_bar_pos': stamina_bar_pos,
        'ability_bar_slot_size': ability_bar_slot_size,
        'ability_bar_padding': ability_bar_padding,
        'ability_bar_pos': ability_bar_pos,
        'ability_bar_size': ability_bar_size,
        'minimap_pos': minimap_pos,
        'minimap_size': minimap_size,
        'status_effects_pos': status_effects_pos,
        'status_effects_size': status_effects_size,
        'status_effects_icon_size': status_effects_icon_size,
        'status_effects_layout': status_effects_layout,
        'quest_tracker_pos': quest_tracker_pos,
        'quest_tracker_size': quest_tracker_size
    }