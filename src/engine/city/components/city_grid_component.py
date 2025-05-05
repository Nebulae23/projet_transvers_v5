import dataclasses
from typing import List, Tuple, Set, Optional

@dataclasses.dataclass
class GridCell:
    """Represents a single cell in the city grid."""
    is_buildable: bool = True
    is_road: bool = False
    building_entity_id: Optional[int] = None # ID of the entity occupying this cell

@dataclasses.dataclass
class CityGridComponent:
    """
    Component managing the city's construction grid.
    Assumes a 2D grid structure.
    """
    width: int = 50  # Grid width in cells
    height: int = 50 # Grid height in cells
    grid: List[List[GridCell]] = dataclasses.field(init=False)
    # Store road connections efficiently, maybe as a set of connected cell pairs
    road_connections: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = dataclasses.field(default_factory=set)

    def __post_init__(self):
        """Initialize the grid after the object is created."""
        self.grid = [[GridCell() for _ in range(self.width)] for _ in range(self.height)]

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        """Checks if the coordinates are within the grid boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def can_build_at(self, x: int, y: int, building_width: int, building_height: int) -> bool:
        """
        Checks if a building of given dimensions can be placed at (x, y).
        Verifies boundaries, buildable status, and collisions.
        """
        for row in range(y, y + building_height):
            for col in range(x, x + building_width):
                if not self.is_valid_coordinate(col, row):
                    return False # Out of bounds
                cell = self.grid[row][col]
                if not cell.is_buildable or cell.building_entity_id is not None or cell.is_road:
                    return False # Cell not buildable, occupied, or is a road
        return True

    def place_building(self, x: int, y: int, building_width: int, building_height: int, entity_id: int):
        """Marks cells as occupied by a building."""
        if self.can_build_at(x, y, building_width, building_height):
            for row in range(y, y + building_height):
                for col in range(x, x + building_width):
                    self.grid[row][col].building_entity_id = entity_id
                    self.grid[row][col].is_buildable = False # Mark as non-buildable once occupied
        else:
            # Consider raising an exception or returning False
            print(f"Error: Cannot place building {entity_id} at ({x},{y})")

    def remove_building(self, x: int, y: int, building_width: int, building_height: int):
         """Marks cells previously occupied by a building as free and buildable."""
         for row in range(y, y + building_height):
            for col in range(x, x + building_width):
                if self.is_valid_coordinate(col, row):
                    # Only remove if the correct building is there (optional check)
                    # if self.grid[row][col].building_entity_id == expected_entity_id:
                    self.grid[row][col].building_entity_id = None
                    self.grid[row][col].is_buildable = True # Make buildable again

    def add_road(self, x: int, y: int):
        """Marks a cell as a road."""
        if self.is_valid_coordinate(x, y) and self.grid[y][x].building_entity_id is None:
            self.grid[y][x].is_road = True
            self.grid[y][x].is_buildable = False # Roads are not buildable areas for buildings
            # Update road connections (simplified example)
            # A more robust system would check neighbors and update connections
            # self._update_road_connections(x, y)

    def remove_road(self, x: int, y: int):
        """Removes a road from a cell."""
        if self.is_valid_coordinate(x, y) and self.grid[y][x].is_road:
            self.grid[y][x].is_road = False
            self.grid[y][x].is_buildable = True # Cell becomes buildable again
            # Update road connections
            # self._update_road_connections(x, y) # Need to remove connections too

    # Placeholder for a more complex road connection logic
    # def _update_road_connections(self, x, y):
    #     pass