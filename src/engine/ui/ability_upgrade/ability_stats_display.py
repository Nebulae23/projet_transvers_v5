# src/engine/ui/ability_upgrade/ability_stats_display.py

# Assuming a base UI class exists
# from ..ui_base import UIBaseElement, Text, ProgressBar # Example import

class AbilityStatsDisplay:
    """
    Displays the current statistics of a selected ability, including level and XP.
    Typically shown as part of the UpgradeMenu when an ability is selected.
    """
    def __init__(self, position=(0, 0), size=(200, 150)):
        self.display_elements = [] # UI elements (Text, ProgressBar)
        self.is_visible = False
        self.position = position
        self.size = size # Optional: for background panel

    def show(self, ability_id, ability_stats, level_comp, xp_comp):
        """
        Makes the stats display visible and updates it with current data.
        :param ability_id: The ID of the ability being displayed.
        :param ability_stats: The current stats object of the ability.
        :param level_comp: The AbilityLevel component of the entity.
        :param xp_comp: The AbilityExperience component of the entity.
        """
        self.is_visible = True
        self.update_display(ability_id, ability_stats, level_comp, xp_comp)
        print(f"Showing stats display for ability: {ability_id}")

    def hide(self):
        """Hides the stats display."""
        self.is_visible = False
        self.clear_display()
        print("Hiding ability stats display.")

    def update_display(self, ability_id, ability_stats, level_comp, xp_comp):
        """Populates UI elements with the ability's current stats."""
        self.clear_display()
        print(f"Updating stats display for: {ability_id}")

        level = level_comp.get_level(ability_id)
        current_xp = xp_comp.get_experience(ability_id)
        needed_xp = xp_comp.get_xp_needed(ability_id)
        xp_percentage = (current_xp / needed_xp) * 100 if needed_xp > 0 else 0

        # Create Text elements for each stat
        # Example:
        # self.display_elements.append(Text(f"Ability: {ability_id.capitalize()}", ...))
        # self.display_elements.append(Text(f"Level: {level}", ...))
        # self.display_elements.append(Text(f"Damage: {ability_stats.damage:.1f}", ...))
        # self.display_elements.append(Text(f"Range: {ability_stats.range:.1f}", ...))
        # self.display_elements.append(Text(f"Cooldown: {ability_stats.cooldown:.1f}s", ...))
        # Add other relevant stats...

        # Create XP Bar (optional)
        # self.display_elements.append(Text(f"XP: {current_xp}/{needed_xp}", ...))
        # self.display_elements.append(ProgressBar(percentage=xp_percentage, ...))

    def clear_display(self):
        """Removes all UI elements from the display."""
        # Logic to destroy/hide elements in self.display_elements
        self.display_elements = []
        # print("Stats Display UI Cleared.") # Can be noisy

    def draw(self, surface):
        """Draws the stats display panel and its elements."""
        if not self.is_visible:
            return
        # Draw a background panel at self.position with self.size (optional)
        # Draw all elements in self.display_elements relative to the panel/position
        pass