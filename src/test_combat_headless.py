# src/test_combat_headless.py
import numpy as np
from engine.combat.trajectory import (
    LinearTrajectory, ArcingTrajectory, HomingTrajectory,
    OrbitalTrajectory, ZigzagTrajectory, SpiralTrajectory
)
from engine.ecs.world import World
from engine.ecs.components import Transform, TrajectoryProjectile, Health
from engine.combat.ability import MageAbility, WarriorAbility
from engine.combat.combat_system import CombatSystem

def test_linear_trajectory():
    """Test linear trajectory calculations"""
    trajectory = LinearTrajectory(speed=5.0)
    current_pos = np.array([0.0, 0.0])
    target_pos = np.array([3.0, 4.0])
    velocity = trajectory.calculate_velocity(current_pos, target_pos)
    
    # Check velocity magnitude matches speed
    assert np.abs(np.linalg.norm(velocity) - 5.0) < 0.001
    
    # Check direction is correct
    expected_direction = np.array([0.6, 0.8])  # Normalized [3,4]
    actual_direction = velocity / np.linalg.norm(velocity)
    assert np.all(np.abs(actual_direction - expected_direction) < 0.001)
    print("Linear trajectory test passed!")

def test_arcing_trajectory():
    """Test arcing trajectory calculations"""
    trajectory = ArcingTrajectory(speed=10.0, gravity=9.81)
    distance = 20.0
    angle = np.pi / 4  # 45 degrees
    
    velocity = trajectory.calculate_initial_velocity(distance, angle)
    assert len(velocity) == 2
    
    # Check initial velocity components
    assert np.abs(velocity[0] - (10.0 * np.cos(angle))) < 0.001
    assert np.abs(velocity[1] - (10.0 * np.sin(angle))) < 0.001
    print("Arcing trajectory test passed!")

def test_homing_trajectory():
    """Test homing trajectory calculations"""
    trajectory = HomingTrajectory(speed=3.0, turn_rate=2.0)
    current_pos = np.array([0.0, 0.0])
    target_pos = np.array([1.0, 1.0])
    
    velocity = trajectory.calculate_velocity(current_pos, target_pos)
    assert np.linalg.norm(velocity) - 3.0 < 0.001  # Check speed
    print("Homing trajectory test passed!")

def test_combat_system():
    """Test combat system functionality"""
    try:
        world = World()
        combat_system = CombatSystem(world)
        
        print("1. Created world and combat system")
        
        # Create attacker
        attacker = world.create_entity()
        attacker.add_component(Transform(position=np.array([0.0, 0.0])))
        
        print("2. Created attacker entity")
        
        # Create target
        target = world.create_entity()
        target.add_component(Transform(position=np.array([10.0, 0.0])))
        target.add_component(Health(max_health=100.0))
        
        print("3. Created target entity")
        
        # Add abilities to attacker
        abilities = [MageAbility(), WarriorAbility()]
        combat_system.register_entity_abilities(attacker, abilities)
        
        print("4. Registered abilities")
        
        # Test ability usage
        target_pos = np.array([10.0, 0.0])
        success = combat_system.use_ability(attacker, 0, target_pos)
        assert success, "Failed to use ability"
        
        print("5. Used ability successfully")
        
        # Update combat system
        combat_system.update(0.016)  # One frame at 60 FPS
        
        print("6. Updated combat system")
        
        # Check projectile creation
        projectiles = world.get_entities_with_component(TrajectoryProjectile)
        assert len(projectiles) > 0, "No projectiles created"
        
        print("Combat system test passed!")
        
    except Exception as e:
        print(f"Combat system test failed at step: {e}")
        raise

def main():
    print("Running headless tests for combat and trajectory systems...")
    
    try:
        test_linear_trajectory()
        test_arcing_trajectory()
        test_homing_trajectory()
        test_combat_system()
        
        print("\nAll tests passed successfully!")
        
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()