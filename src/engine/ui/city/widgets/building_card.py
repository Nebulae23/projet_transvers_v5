# src/engine/ui/city/widgets/building_card.py

# Assuming a base UI widget class exists, e.g., in src/engine/ui/widgets/base_widget.py
# from src.engine.ui.widgets.base_widget import BaseWidget
# If not, this class would need basic drawing and layout capabilities.

class BuildingCard: # Or inherit from BaseWidget
    """
    A UI widget representing a single building in a list or menu.

    Displays key information like name, icon, cost, and status.
    Can be interactive (e.g., clickable).
    """
    def __init__(self, building_data, position, size):
        """
        Initializes the BuildingCard.

        Args:
            building_data (dict): Information about the building
                                  (e.g., name, icon_path, cost, prerequisites).
            position (tuple): (x, y) coordinates for the card's top-left corner.
            size (tuple): (width, height) of the card.
        """
        # super().__init__(position, size) # If inheriting
        self.building_data = building_data
        self.position = position
        self.size = size
        self.is_hovered = False
        self.is_clickable = True # Example property
        self.is_affordable = True # Example state based on player resources

        # TODO: Load building icon/image
        # TODO: Pre-render text elements for performance if needed

    def update(self, dt, mouse_pos, click_event):
        """Updates the card's state (hover, click)."""
        # TODO: Check for hover state based on mouse_pos and self.position/self.size
        # TODO: Check for click event within bounds
        # TODO: Update visual state based on affordability, prerequisites met, etc.
        pass

    def render(self, surface):
        """Renders the building card."""
        # TODO: Draw card background (potentially different if hovered, disabled)
        # TODO: Draw building icon
        # TODO: Draw building name
        # TODO: Draw cost (e.g., Wood: 50, Stone: 20)
        # TODO: Draw prerequisites if not met (e.g., requires Barracks Lvl 2)
        # TODO: Indicate if affordable/buildable
        pass

    def get_rect(self):
        """Returns the pygame.Rect representing the card's bounds."""
        # Requires pygame or similar library
        # return pygame.Rect(self.position, self.size)
        return (self.position[0], self.position[1], self.size[0], self.size[1]) # Placeholder

    def on_click(self):
        """Action to perform when the card is clicked."""
        if self.is_clickable:
            print(f"Building card clicked: {self.building_data.get('name', 'Unknown')}")
            # TODO: Trigger an event or callback, e.g., select this building for placement
            return self.building_data # Return data for the caller
        return None