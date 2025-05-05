# src/engine/physics/collision_system.py
import numpy as np
from typing import List, Tuple, Dict, Optional, Any, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field

# Import Verlet physics related classes
from .verlet_system import VerletPoint, VerletStick, PhysicsSystem

class CollisionLayer(Enum):
    """Enum for collision layers to determine what can collide with what."""
    DEFAULT = auto()
    PLAYER = auto()
    ENEMY = auto()
    BUILDING = auto()
    PROJECTILE = auto()
    TERRAIN = auto()
    TRIGGER = auto()
    TOWER = auto()

class CollisionShape(Enum):
    """Enum for different collision shape types."""
    CIRCLE = auto()
    AABB = auto()  # Axis-Aligned Bounding Box
    OBB = auto()   # Oriented Bounding Box
    POINT = auto()

@dataclass
class Collider:
    """Base class for all colliders."""
    position: np.ndarray
    layer: CollisionLayer = CollisionLayer.DEFAULT
    is_trigger: bool = False
    is_static: bool = False
    owner: Any = None  # Reference to the entity that owns this collider
    
    # Callback functions
    on_collision_enter: Optional[Callable[[Any], None]] = None
    on_collision_stay: Optional[Callable[[Any], None]] = None
    on_collision_exit: Optional[Callable[[Any], None]] = None
    
    # Track collisions from previous frame to detect entry/exit
    current_collisions: Set[int] = field(default_factory=set)
    previous_collisions: Set[int] = field(default_factory=set)
    
    # Unique ID for each collider
    id: int = 0
    
    def get_position(self) -> np.ndarray:
        """Get the current position. Can be overridden to track a moving object."""
        if hasattr(self.owner, 'position'):
            return np.array(self.owner.position)
        return self.position
    
    def update_collisions(self, new_collisions: Set[int]):
        """Update collision sets and trigger callbacks."""
        self.previous_collisions = self.current_collisions.copy()
        self.current_collisions = new_collisions
        
        # Find new and ended collisions
        new_entries = new_collisions - self.previous_collisions
        exits = self.previous_collisions - new_collisions
        
        return new_entries, exits

@dataclass
class CircleCollider(Collider):
    """Circle-shaped collider."""
    radius: float = 1.0
    
    def check_collision(self, other: 'CircleCollider') -> bool:
        """Check collision with another circle collider."""
        pos1 = self.get_position()
        pos2 = other.get_position()
        distance = np.linalg.norm(pos1 - pos2)
        return distance < (self.radius + other.radius)
    
    def check_collision_aabb(self, other: 'AABBCollider') -> bool:
        """Check collision with an AABB collider."""
        # Find the closest point on the AABB to the circle
        circle_pos = self.get_position()
        box_pos = other.get_position()
        
        # Calculate the box's corners in world space
        half_size = other.half_size
        min_x = box_pos[0] - half_size[0]
        max_x = box_pos[0] + half_size[0]
        min_y = box_pos[1] - half_size[1]
        max_y = box_pos[1] + half_size[1]
        
        # Find the closest point on the box to the circle
        closest_x = max(min_x, min(circle_pos[0], max_x))
        closest_y = max(min_y, min(circle_pos[1], max_y))
        closest_point = np.array([closest_x, closest_y])
        
        # Check if the closest point is within the circle
        distance = np.linalg.norm(circle_pos - closest_point)
        return distance <= self.radius

@dataclass
class AABBCollider(Collider):
    """Axis-Aligned Bounding Box collider."""
    half_size: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0]))
    
    def check_collision(self, other: 'AABBCollider') -> bool:
        """Check collision with another AABB collider."""
        pos1 = self.get_position()
        pos2 = other.get_position()
        
        # Calculate box extents
        min1 = pos1 - self.half_size
        max1 = pos1 + self.half_size
        min2 = pos2 - other.half_size
        max2 = pos2 + other.half_size
        
        # Check for overlap in both x and y axes
        return (min1[0] <= max2[0] and max1[0] >= min2[0] and
                min1[1] <= max2[1] and max1[1] >= min2[1])
    
    def check_collision_circle(self, circle: CircleCollider) -> bool:
        """Check collision with a circle collider."""
        return circle.check_collision_aabb(self)

@dataclass
class VerletCollider(Collider):
    """Collider that integrates with Verlet physics."""
    verlet_point: VerletPoint = None
    radius: float = 1.0  # Treating Verlet points as circles
    
    def get_position(self) -> np.ndarray:
        """Get position from the Verlet point."""
        if self.verlet_point:
            return self.verlet_point.current_pos
        return self.position
    
    def apply_collision_response(self, other: 'VerletCollider', penetration: float):
        """Apply collision response between two Verlet points."""
        if self.is_static and other.is_static:
            return  # Both static, no response
            
        pos1 = self.get_position()
        pos2 = other.get_position()
        
        # Direction from other to self
        if np.array_equal(pos1, pos2):
            # Avoid division by zero with a random direction
            direction = np.array([np.random.uniform(-1, 1), np.random.uniform(-1, 1)])
            direction = direction / np.linalg.norm(direction)
        else:
            direction = (pos1 - pos2) / np.linalg.norm(pos1 - pos2)
        
        # Calculate response movement
        move_amount = penetration * 0.5  # Split the penetration equally
        
        # Apply movement based on static status
        if self.is_static and not other.is_static:
            other.verlet_point.current_pos -= direction * penetration
        elif not self.is_static and other.is_static:
            self.verlet_point.current_pos += direction * penetration
        else:
            # Neither is static
            self.verlet_point.current_pos += direction * move_amount
            other.verlet_point.current_pos -= direction * move_amount
    
    def check_collision(self, other: 'VerletCollider') -> Tuple[bool, float]:
        """Check collision with another Verlet collider and return penetration depth."""
        pos1 = self.get_position()
        pos2 = other.get_position()
        distance = np.linalg.norm(pos1 - pos2)
        combined_radius = self.radius + other.radius
        
        if distance < combined_radius:
            penetration = combined_radius - distance
            return True, penetration
        return False, 0.0

class CollisionSystem:
    """System to handle collision detection and resolution."""
    def __init__(self, physics_system: Optional[PhysicsSystem] = None):
        self.colliders: List[Collider] = []
        self.verlet_colliders: List[VerletCollider] = []
        self.circle_colliders: List[CircleCollider] = []
        self.aabb_colliders: List[AABBCollider] = []
        self.physics_system = physics_system
        self.next_id = 1
        
        # Collision matrix for layers
        self.collision_matrix: Dict[CollisionLayer, List[CollisionLayer]] = {
            layer: list(CollisionLayer) for layer in CollisionLayer
        }
        
        # Spatial partitioning (simple grid-based for now)
        self.cell_size = 10.0
        self.spatial_grid = {}
    
    def add_collider(self, collider: Collider) -> int:
        """Add a collider to the system and return its ID."""
        # Assign a unique ID
        collider.id = self.next_id
        self.next_id += 1
        
        # Add to the appropriate list
        self.colliders.append(collider)
        
        if isinstance(collider, VerletCollider):
            self.verlet_colliders.append(collider)
        elif isinstance(collider, CircleCollider):
            self.circle_colliders.append(collider)
        elif isinstance(collider, AABBCollider):
            self.aabb_colliders.append(collider)
        
        return collider.id
    
    def remove_collider(self, collider_id: int) -> bool:
        """Remove a collider by its ID."""
        for collider in self.colliders:
            if collider.id == collider_id:
                self.colliders.remove(collider)
                
                if isinstance(collider, VerletCollider):
                    self.verlet_colliders.remove(collider)
                elif isinstance(collider, CircleCollider):
                    self.circle_colliders.remove(collider)
                elif isinstance(collider, AABBCollider):
                    self.aabb_colliders.remove(collider)
                
                return True
        return False
    
    def set_collision_filter(self, layer1: CollisionLayer, layer2: CollisionLayer, should_collide: bool):
        """Set whether two layers should collide with each other."""
        if should_collide:
            if layer2 not in self.collision_matrix[layer1]:
                self.collision_matrix[layer1].append(layer2)
            if layer1 not in self.collision_matrix[layer2]:
                self.collision_matrix[layer2].append(layer1)
        else:
            if layer2 in self.collision_matrix[layer1]:
                self.collision_matrix[layer1].remove(layer2)
            if layer1 in self.collision_matrix[layer2]:
                self.collision_matrix[layer2].remove(layer1)
    
    def should_check_collision(self, layer1: CollisionLayer, layer2: CollisionLayer) -> bool:
        """Check if two layers should collide according to the collision matrix."""
        return layer2 in self.collision_matrix[layer1]
    
    def update(self, dt: float):
        """Update the collision system."""
        # Clear spatial partitioning
        self.spatial_grid = {}
        
        # Update spatial partitioning
        self._update_spatial_grid()
        
        # Process Verlet physics collisions
        self._process_verlet_collisions()
        
        # Process general collisions and callbacks
        self._process_general_collisions()
    
    def _update_spatial_grid(self):
        """Update the spatial partitioning grid."""
        for collider in self.colliders:
            pos = collider.get_position()
            cell_x = int(pos[0] / self.cell_size)
            cell_y = int(pos[1] / self.cell_size)
            cell_key = (cell_x, cell_y)
            
            if cell_key not in self.spatial_grid:
                self.spatial_grid[cell_key] = []
            
            self.spatial_grid[cell_key].append(collider)
    
    def _get_nearby_colliders(self, collider: Collider) -> List[Collider]:
        """Get colliders that are in nearby cells."""
        pos = collider.get_position()
        cell_x = int(pos[0] / self.cell_size)
        cell_y = int(pos[1] / self.cell_size)
        
        nearby_colliders = []
        
        # Check 9 cells around the collider
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell_key = (cell_x + dx, cell_y + dy)
                if cell_key in self.spatial_grid:
                    nearby_colliders.extend(self.spatial_grid[cell_key])
        
        return [c for c in nearby_colliders if c.id != collider.id]
    
    def _process_verlet_collisions(self):
        """Process collisions between Verlet colliders."""
        for i, collider1 in enumerate(self.verlet_colliders):
            for collider2 in self._get_nearby_colliders(collider1):
                if not isinstance(collider2, VerletCollider):
                    continue
                    
                # Skip if they shouldn't collide based on layers
                if not self.should_check_collision(collider1.layer, collider2.layer):
                    continue
                
                # Check collision
                collision, penetration = collider1.check_collision(collider2)
                if collision:
                    # Apply collision response
                    collider1.apply_collision_response(collider2, penetration)
    
    def _process_general_collisions(self):
        """Process collisions and trigger callbacks."""
        # Track all current collisions for callbacks
        current_collision_pairs = set()
        
        # Check all colliders
        for i, collider1 in enumerate(self.colliders):
            new_collisions = set()
            
            for collider2 in self._get_nearby_colliders(collider1):
                # Skip if they shouldn't collide based on layers
                if not self.should_check_collision(collider1.layer, collider2.layer):
                    continue
                
                # Determine collision based on collider types
                collision = False
                
                if isinstance(collider1, CircleCollider) and isinstance(collider2, CircleCollider):
                    collision = collider1.check_collision(collider2)
                elif isinstance(collider1, AABBCollider) and isinstance(collider2, AABBCollider):
                    collision = collider1.check_collision(collider2)
                elif isinstance(collider1, CircleCollider) and isinstance(collider2, AABBCollider):
                    collision = collider1.check_collision_aabb(collider2)
                elif isinstance(collider1, AABBCollider) and isinstance(collider2, CircleCollider):
                    collision = collider1.check_collision_circle(collider2)
                elif isinstance(collider1, VerletCollider) and isinstance(collider2, VerletCollider):
                    collision, _ = collider1.check_collision(collider2)
                
                if collision:
                    new_collisions.add(collider2.id)
                    
                    # Record the collision pair
                    pair = tuple(sorted([collider1.id, collider2.id]))
                    current_collision_pairs.add(pair)
            
            # Update collisions and trigger callbacks
            new_entries, exits = collider1.update_collisions(new_collisions)
            
            # Trigger callbacks
            if collider1.on_collision_enter:
                for other_id in new_entries:
                    other = next((c for c in self.colliders if c.id == other_id), None)
                    if other:
                        collider1.on_collision_enter(other)
            
            if collider1.on_collision_exit:
                for other_id in exits:
                    other = next((c for c in self.colliders if c.id == other_id), None)
                    if other:
                        collider1.on_collision_exit(other)
            
            if collider1.on_collision_stay:
                staying = new_collisions.intersection(collider1.previous_collisions)
                for other_id in staying:
                    other = next((c for c in self.colliders if c.id == other_id), None)
                    if other:
                        collider1.on_collision_stay(other)
    
    def create_circle_collider(self, position: np.ndarray, radius: float, layer: CollisionLayer = CollisionLayer.DEFAULT, 
                              is_trigger: bool = False, is_static: bool = False, owner: Any = None) -> CircleCollider:
        """Convenience method to create and add a circle collider."""
        collider = CircleCollider(
            position=np.array(position),
            radius=radius,
            layer=layer,
            is_trigger=is_trigger,
            is_static=is_static,
            owner=owner
        )
        self.add_collider(collider)
        return collider
    
    def create_aabb_collider(self, position: np.ndarray, half_size: np.ndarray, layer: CollisionLayer = CollisionLayer.DEFAULT,
                            is_trigger: bool = False, is_static: bool = False, owner: Any = None) -> AABBCollider:
        """Convenience method to create and add an AABB collider."""
        collider = AABBCollider(
            position=np.array(position),
            half_size=np.array(half_size),
            layer=layer,
            is_trigger=is_trigger,
            is_static=is_static,
            owner=owner
        )
        self.add_collider(collider)
        return collider
    
    def create_verlet_collider(self, verlet_point: VerletPoint, radius: float, layer: CollisionLayer = CollisionLayer.DEFAULT,
                              is_trigger: bool = False, is_static: bool = False, owner: Any = None) -> VerletCollider:
        """Convenience method to create and add a Verlet collider."""
        collider = VerletCollider(
            position=verlet_point.current_pos.copy(),
            verlet_point=verlet_point,
            radius=radius,
            layer=layer,
            is_trigger=is_trigger,
            is_static=is_static,
            owner=owner
        )
        self.add_collider(collider)
        return collider

# Update the __init__.py to import this
if __name__ == "__main__":
    # Simple test
    physics = PhysicsSystem()
    collision = CollisionSystem(physics)
    
    # Create Verlet points
    p1 = physics.add_point(np.array([100.0, 100.0]))
    p2 = physics.add_point(np.array([150.0, 100.0]))
    
    # Create Verlet colliders
    c1 = collision.create_verlet_collider(p1, 10.0)
    c2 = collision.create_verlet_collider(p2, 10.0)
    
    # Test collision
    is_colliding, penetration = c1.check_collision(c2)
    print(f"Colliding: {is_colliding}, Penetration: {penetration}") 