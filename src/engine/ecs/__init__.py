"""
Entity Component System Module
This package contains the core ECS architecture.
"""

try:
    from .entity import Entity
    from .world import World
    from .components import Transform, Health, TrajectoryProjectile, Attack, Defense
except ImportError as e:
    print(f"Note: Some ECS module components couldn't be imported: {e}") 