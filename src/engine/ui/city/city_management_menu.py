# src/engine/ui/city/city_management_menu.py

class CityManagementMenu:
    """
    UI component for managing existing city buildings.

    Displays building status, upgrade options, and available actions.
    """
    def __init__(self, ui_manager, city_manager):
        self.ui_manager = ui_manager
        self.city_manager = city_manager
        self.selected_building = None
        # TODO: Initialize UI elements (building list, info panel, action buttons)

    def update(self, dt):
        """Updates the management menu state."""
        # TODO: Update based on selected building or city overview
        # TODO: Handle user input for selecting buildings and actions
        pass

    def render(self, surface):
        """Renders the management menu."""
        # TODO: Draw the menu background, building status, upgrade options, actions
        if self.selected_building:
            # TODO: Display detailed info for the selected building
            pass
        else:
            # TODO: Display a city overview or prompt to select a building
            pass

    def set_selected_building(self, building_entity):
        """Sets the currently selected building to display details for."""
        self.selected_building = building_entity
        # TODO: Update UI elements with the selected building's data
        print(f"Selected building for management: {building_entity}") # Placeholder

    def _handle_input(self):
        """Processes user interactions with the management menu."""
        # TODO: Detect clicks on buildings in a list/map, upgrade buttons, action buttons
        pass

    def _perform_upgrade(self):
        """Initiates an upgrade for the selected building."""
        if self.selected_building:
            # TODO: Check if upgrade is possible (resources, prerequisites) via city_manager
            # TODO: Instruct city_manager to start the upgrade
            print(f"Attempting upgrade for: {self.selected_building}") # Placeholder
        else:
            print("Upgrade failed: No building selected.")

    def _perform_action(self, action_id):
        """Performs a specific action available for the selected building."""
        if self.selected_building:
            # TODO: Check action validity via city_manager
            # TODO: Instruct city_manager to perform the action
            print(f"Performing action '{action_id}' on: {self.selected_building}") # Placeholder
        else:
            print(f"Action '{action_id}' failed: No building selected.")