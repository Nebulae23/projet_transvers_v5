import unittest
from unittest.mock import Mock, patch
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from engine.physics.verlet_system import VerletSystem
from engine.physics.collision_system import CollisionSystem

class TestVerletSystem(unittest.TestCase):
    def setUp(self):
        self.verlet_system = VerletSystem()
        self.dt = 0.016  # 60 FPS
        
        # Setup simple cloth points
        self.points = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0]
        ], dtype=np.float32)
        
        self.prev_points = self.points.copy()

    def test_verlet_integration(self):
        gravity = np.array([0, -9.81, 0])
        
        # Single integration step
        next_points = self.verlet_system.integrate(
            self.points,
            self.prev_points,
            self.dt,
            gravity
        )
        
        # Verify points moved
        self.assertFalse(np.array_equal(next_points, self.points))
        
        # Verify gravity effect
        y_displacement = next_points[:, 1] - self.points[:, 1]
        self.assertTrue(np.all(y_displacement < 0))

    def test_cloth_simulation(self):
        constraints = [
            (0, 1),  # Horizontal
            (2, 3),  # Horizontal
            (0, 2),  # Vertical
            (1, 3),  # Vertical
            (0, 3),  # Diagonal
            (1, 2)   # Diagonal
        ]
        
        # Simulate multiple steps
        points = self.points.copy()
        for _ in range(10):
            points = self.verlet_system.simulate_cloth(
                points,
                constraints,
                iterations=10
            )
            
            # Verify constraints
            for p1_idx, p2_idx in constraints:
                distance = np.linalg.norm(
                    points[p1_idx] - points[p2_idx]
                )
                self.assertLess(distance, 1.5)  # Allow some stretch

    def test_particle_effects(self):
        num_particles = 100
        particles = np.random.rand(num_particles, 3)
        velocities = np.random.rand(num_particles, 3) * 2 - 1
        
        # Simulate particle movement
        next_particles = self.verlet_system.simulate_particles(
            particles,
            velocities,
            self.dt
        )
        
        self.assertEqual(next_particles.shape, particles.shape)
        self.assertFalse(np.array_equal(next_particles, particles))

class TestCollisionSystem(unittest.TestCase):
    def setUp(self):
        self.collision_system = CollisionSystem()

    def test_aabb_collision(self):
        box1 = {
            'min': np.array([0, 0, 0]),
            'max': np.array([1, 1, 1])
        }
        
        # Test overlapping box
        box2 = {
            'min': np.array([0.5, 0.5, 0.5]),
            'max': np.array([1.5, 1.5, 1.5])
        }
        self.assertTrue(self.collision_system.check_aabb_collision(box1, box2))
        
        # Test non-overlapping box
        box3 = {
            'min': np.array([2, 2, 2]),
            'max': np.array([3, 3, 3])
        }
        self.assertFalse(self.collision_system.check_aabb_collision(box1, box3))

    def test_collision_response(self):
        velocity = np.array([1, 0, 0])
        normal = np.array([1, 0, 0])
        
        # Test reflection
        reflected = self.collision_system.calculate_reflection(velocity, normal)
        self.assertTrue(np.array_equal(reflected, -velocity))
        
        # Test sliding
        velocity = np.array([1, 1, 0])
        reflected = self.collision_system.calculate_reflection(velocity, normal)
        self.assertEqual(reflected[0], -velocity[0])
        self.assertEqual(reflected[1], velocity[1])

if __name__ == '__main__':
    unittest.main()