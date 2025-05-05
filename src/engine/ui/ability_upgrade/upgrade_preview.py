# src/engine/ui/ability_upgrade/upgrade_preview.py

# Assuming a base UI class exists
# from ..ui_base import UIBaseElement, Text # Example import

class UpgradePreview:
    """
    Displays a preview of the effects of a potential ability upgrade.
    Typically shown when hovering over an upgrade option in the UpgradeMenu.
    """
    def __init__(self):
        self.preview_elements = [] # UI elements for the preview (text, icons)
        self.is_visible = False
        self.position = (0, 0) # Position to draw the preview window

    def show(self, upgrade_node, current_ability_stats, position):
        """
        Makes the preview visible and populates it with details.
        :param upgrade_node: The UpgradeNode being previewed.
        :param current_ability_stats: The current stats of the ability.
        :param position: The (x, y) coordinates to display the preview.
        """
        self.is_visible = True
        self.position = position
        self.populate_preview(upgrade_node, current_ability_stats)
        print(f"Showing preview for upgrade: {upgrade_node.upgrade_id} at {position}")

    def hide(self):
        """Hides the preview."""
        self.is_visible = False
        self.clear_preview()
        print("Hiding upgrade preview.")

    def populate_preview(self, upgrade_node, current_ability_stats):
        """Creates UI elements to show the upgrade's effects."""
        self.clear_preview()
        print(f"Populating preview for: {upgrade_node.description}")

        # 1. Display Upgrade Description
        # Create Text element for upgrade_node.description
        # self.preview_elements.append(Text(upgrade_node.description, ...))

        # 2. Simulate and Display Stat Changes
        # Create a temporary copy of stats to simulate the change
        simulated_stats = current_ability_stats.copy() # Assuming stats object has a copy method
        upgrade_node.modifier.apply(simulated_stats)

        # Compare simulated_stats with current_ability_stats and display differences
        # Example:
        # if simulated_stats.damage != current_ability_stats.damage:
        #     diff = simulated_stats.damage - current_ability_stats.damage
        #     sign = "+" if diff > 0 else ""
        #     text = f"Damage: {current_ability_stats.damage:.1f} -> {simulated_stats.damage:.1f} ({sign}{diff:.1f})"
        #     # Create Text element for this change
        #     # self.preview_elements.append(Text(text, ...))
        #
        # Repeat for other relevant stats (range, cooldown, area, etc.)

        # 3. Display Requirements (Optional)
        # if upgrade_node.required_level > current_ability_stats.level: # Assuming level is in stats
        #     # Create Text element: "Requires Level X"
        # if upgrade_node.prerequisites:
        #     # Create Text element: "Requires Upgrade Y"

    def clear_preview(self):
        """Removes all UI elements from the preview."""
        # Logic to destroy/hide elements in self.preview_elements
        self.preview_elements = []
        # print("Preview UI Cleared.") # Can be noisy

    def draw(self, surface):
        """Draws the preview window and its elements."""
        if not self.is_visible:
            return
        # Draw a background panel at self.position
        # Draw all elements in self.preview_elements relative to the panel
        pass