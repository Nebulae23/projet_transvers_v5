# src/engine/ui/ability_upgrade/upgrade_menu.py

# Assuming a base UI class exists, e.g., from src/engine/ui/ui_base.py
# from ..ui_base import UIBaseElement, Button # Example import

class AbilityUpgradeMenu: # Potentially inherit from a base menu class
    """
    Manages the UI for viewing and selecting ability upgrades.
    """
    def __init__(self, player_entity, world, progression_manager, upgrade_tree_provider):
        self.player_entity = player_entity
        self.world = world
        self.progression_manager = progression_manager
        self.upgrade_tree_provider = upgrade_tree_provider # Function/object to get upgrade trees
        self.selected_ability_id = None
        self.available_upgrades = []
        self.ui_elements = [] # List to hold buttons, text, etc.
        self.is_visible = False

        # Get necessary components from the player entity
        self.ability_level_comp = world.get_component(player_entity, 'AbilityLevel')
        self.ability_xp_comp = world.get_component(player_entity, 'AbilityExperience')
        self.ability_upgrades_comp = world.get_component(player_entity, 'AbilityUpgrades')
        # Assume player has a component listing their abilities, e.g., 'AbilitiesComponent'
        self.player_abilities = world.get_component(player_entity, 'AbilitiesComponent').abilities

    def show(self):
        """Makes the upgrade menu visible and populates it."""
        self.is_visible = True
        self.populate_ability_list()
        print("Ability Upgrade Menu opened.")

    def hide(self):
        """Hides the upgrade menu."""
        self.is_visible = False
        self.selected_ability_id = None
        self.clear_ui()
        print("Ability Upgrade Menu closed.")

    def populate_ability_list(self):
        """Creates UI elements to select an ability."""
        self.clear_ui()
        print("Populating ability list...")
        # Create buttons or list items for each ability the player has
        for ability_id in self.player_abilities:
             # Create a button/element for ability_id
             # On click, call self.select_ability(ability_id)
             pass

    def select_ability(self, ability_id):
        """Handles the selection of an ability to view its upgrade tree."""
        self.selected_ability_id = ability_id
        print(f"Selected ability: {ability_id}")
        self.populate_upgrade_options()

    def populate_upgrade_options(self):
        """Displays available upgrades for the selected ability."""
        if not self.selected_ability_id:
            return

        self.clear_ui() # Clear previous elements (or just the upgrade part)
        print(f"Populating upgrades for {self.selected_ability_id}...")

        current_level = self.ability_level_comp.get_level(self.selected_ability_id)
        unlocked_ids = self.ability_upgrades_comp.get_unlocked_upgrades(self.selected_ability_id)
        upgrade_tree = self.upgrade_tree_provider(self.selected_ability_id) # Get the tree

        if not upgrade_tree:
            print(f"No upgrade tree found for {self.selected_ability_id}")
            # Display message: No upgrades available
            return

        self.available_upgrades = upgrade_tree.get_available_upgrades(current_level, unlocked_ids)

        if not self.available_upgrades:
            print("No upgrades currently available for this ability.")
            # Display message: No upgrades available / Max level reached?
            return

        # Create UI elements (buttons) for each available upgrade
        for upgrade_node in self.available_upgrades:
            # Create button with upgrade_node.description
            # On hover, potentially show preview (call UpgradePreview)
            # On click, call self.confirm_upgrade(upgrade_node)
            pass
        # Also display current stats (call AbilityStatsDisplay)

    def confirm_upgrade(self, upgrade_node):
        """Handles the confirmation and application of an upgrade."""
        print(f"Attempting to unlock upgrade: {upgrade_node.upgrade_id} for {self.selected_ability_id}")
        # Potentially add a confirmation step here

        # Apply the upgrade via the progression system/components
        success = self.ability_upgrades_comp.add_upgrade(self.selected_ability_id, upgrade_node.upgrade_id)
        if success:
             # Apply the modifier effect (this might happen in a dedicated system)
             # For now, just log it
             print(f"Successfully unlocked {upgrade_node.upgrade_id}. Modifier needs application.")
             # Refresh the upgrade options
             self.populate_upgrade_options()
        else:
             print(f"Failed to unlock {upgrade_node.upgrade_id}.")


    def clear_ui(self):
        """Removes all UI elements from the menu."""
        # Logic to destroy/hide all buttons, text, etc. in self.ui_elements
        self.ui_elements = []
        print("UI Cleared.")

    def handle_input(self, event):
        """Processes user input for the menu."""
        if not self.is_visible:
            return
        # Pass input events to UI elements (buttons, etc.)
        pass

    def draw(self, surface):
        """Draws the menu UI elements."""
        if not self.is_visible:
            return
        # Draw background, borders, and all elements in self.ui_elements
        pass