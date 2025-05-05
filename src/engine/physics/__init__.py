"""
Physics System Module
This package contains physics simulation functionality.
"""

try:
    from .verlet_system import VerletSystem, VerletPoint, VerletStick, PhysicsSystem
    from .collision_system import CollisionSystem, Collider, CircleCollider, AABBCollider, VerletCollider, CollisionLayer
except ImportError as e:
    print(f"Note: Some physics module components couldn't be imported: {e}") 