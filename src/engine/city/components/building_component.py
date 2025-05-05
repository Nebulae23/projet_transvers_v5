import dataclasses
from typing import Tuple, Dict

@dataclasses.dataclass
class BuildingComponent:
    """
    Component storing data for a building entity.
    """
    position: Tuple[int, int]  # Position (x, y) on the grid
    dimensions: Tuple[int, int]  # Size (width, height) in grid cells
    health: float = 100.0  # Current health points
    max_health: float = 100.0 # Maximum health points
    construction_progress: float = 0.0  # 0.0 to 1.0
    is_constructed: bool = False
    level: int = 1
    upgrades: Dict[str, int] = dataclasses.field(default_factory=dict)  # e.g., {"efficiency": 2}
    construction_cost: Dict[str, int] = dataclasses.field(default_factory=dict) # e.g., {"wood": 100, "stone": 50}
    construction_time: float = 10.0  # Time in seconds
    building_type_id: str = "" # Reference to the building type definition