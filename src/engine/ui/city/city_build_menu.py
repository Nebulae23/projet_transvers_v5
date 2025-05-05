# src/engine/ui/city/city_build_menu.py

class CityBuildMenu:
    """
    UI component for the city building menu.

    Handles displaying available buildings, costs, prerequisites,
    and initiating the placement mode.
    """
    def __init__(self, ui_manager, city_manager):
        self.ui_manager = ui_manager
        self.city_manager = city_manager
        self.available_buildings = []
        self.selected_building = None
        self.is_placement_mode = False
        # TODO: Initialize UI elements (buttons, lists, etc.)

    def update(self, dt):
        """Updates the build menu state."""
        # TODO: Update available buildings based on city state and resources
        # TODO: Handle user input for selecting buildings and entering placement mode
        pass

    def render(self, surface):
        """Renders the build menu."""
        # TODO: Draw the menu background, building list, costs, prerequisites
        if self.is_placement_mode:
            # TODO: Render placement preview or indicators
            pass

    def _update_available_buildings(self):
        """Fetches and updates the list of buildable structures."""
        # TODO: Query city_manager or building database for available buildings
        # Consider player resources, technology unlocks, etc.
        pass

    def _handle_input(self):
        """Processes user interactions with the build menu."""
        # TODO: Detect clicks on building entries, build button, close button
        pass

    def _enter_placement_mode(self, building_data):
        """Activates building placement mode."""
        self.selected_building = building_data
        self.is_placement_mode = True
        # TODO: Notify other systems (e.g., input manager) about placement mode
        print(f"Entering placement mode for: {building_data['name']}")

    def _exit_placement_mode(self):
        """Deactivates building placement mode."""
        self.selected_building = None
        self.is_placement_mode = False
        # TODO: Notify other systems
        print("Exiting placement mode.")

    def _confirm_placement(self, position):
        """Attempts to place the selected building at the given position."""
        if self.selected_building and self.is_placement_mode:
            # TODO: Check placement validity (collision, terrain, cost) via city_manager
            # TODO: If valid, instruct city_manager to construct the building
            print(f"Placing {self.selected_building['name']} at {position}")
            self._exit_placement_mode()
        else:
            print("Placement confirmation failed: No building selected or not in placement mode.")