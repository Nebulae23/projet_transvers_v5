import sys
import os
import time
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import game modules
from game.adaptive_difficulty import AdaptiveDifficultySystem
from game.performance_tracker import PerformanceTracker

class MockGame:
    """Mock Game class for testing"""
    
    def __init__(self):
        self.debug_mode = True
        self.player = None
        self.setup_complete = False
        self.performance_tracker = PerformanceTracker(self)
        self.adaptive_difficulty_system = AdaptiveDifficultySystem(self)
        # Connect systems
        self.adaptive_difficulty_system.set_performance_tracker(self.performance_tracker)
        
    def setup(self):
        """Set up the mock game"""
        self.player = MockPlayer(self)
        self.setup_complete = True
        
class MockPlayer:
    """Mock Player class for testing"""
    
    def __init__(self, game):
        self.game = game
        self.health = 100
        self.max_health = 100
        
class MockEnemy:
    """Mock Enemy class for testing"""
    
    def __init__(self, game, enemy_type="basic"):
        self.game = game
        self.enemy_type = enemy_type
        self.base_health = 50
        self.base_damage = 10
        self.health = self.base_health
        self.damage = self.base_damage
        
    def apply_difficulty_adjustment(self):
        """Apply difficulty adjustment to enemy stats"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            self.health = int(self.base_health * factors['enemy_health'])
            self.damage = self.base_damage * factors['enemy_damage']
            
            print(f"Applied difficulty: Health={self.health}, Damage={self.damage}")
            
class MockBoss:
    """Mock Boss class for testing"""
    
    def __init__(self, game, boss_type="forest_guardian"):
        self.game = game
        self.boss_type = boss_type
        self.base_max_health = 500
        self.base_damage = 30
        self.health = self.base_max_health
        self.max_health = self.base_max_health
        self.damage = self.base_damage
        self.ability_cooldowns = {"slam": 5.0, "charge": 8.0, "summon": 12.0}
        
    def apply_difficulty_adjustment(self):
        """Apply difficulty adjustment to boss stats"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Boss-specific scaling
            health_multiplier = factors['enemy_health'] * factors['boss_difficulty']
            damage_multiplier = factors['enemy_damage'] * (0.7 + (0.3 * factors['boss_difficulty']))
            
            self.max_health = int(self.base_max_health * health_multiplier)
            self.health = self.max_health
            self.damage = self.base_damage * damage_multiplier
            
            # Adjust ability cooldowns
            for ability_name in self.ability_cooldowns:
                base_cooldown = self.ability_cooldowns[ability_name]
                cooldown_modifier = 1.0 / (0.8 + (0.2 * factors['boss_difficulty']))
                self.ability_cooldowns[ability_name] = base_cooldown * cooldown_modifier
            
            print(f"\nBoss with difficulty adjustment:")
            print(f"  Health: {self.max_health} (x{health_multiplier:.2f})")
            print(f"  Damage: {self.damage:.1f} (x{damage_multiplier:.2f})")
            print(f"  Cooldowns: {self.ability_cooldowns}")
            
class MockResourceNode:
    """Mock ResourceNode class for testing"""
    
    def __init__(self, game, resource_type="wood"):
        self.game = game
        self.resource_type = resource_type
        self.initial_resources = 5 if resource_type == "wood" else 3
        self.resources = self.initial_resources
        self.base_resources_per_harvest = 1
        self.resources_per_harvest = self.base_resources_per_harvest
        self.regeneration_time = 60 if resource_type == "wood" else 120
        self.base_regeneration_time = self.regeneration_time
        
    def apply_difficulty_adjustment(self):
        """Apply difficulty adjustment to resource node"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Adjust harvest amount
            self.resources_per_harvest = max(1, int(self.base_resources_per_harvest * factors['resource_drop']))
            
            # Adjust regeneration time (higher resource drop = faster regeneration)
            self.regeneration_time = self.base_regeneration_time / factors['resource_drop']
            
            print(f"\nResource node with difficulty adjustment:")
            print(f"  Type: {self.resource_type}")
            print(f"  Resources per harvest: {self.resources_per_harvest} (x{factors['resource_drop']:.2f})")
            print(f"  Regeneration time: {self.regeneration_time:.1f}s (base: {self.base_regeneration_time}s)")

class MockNightFog:
    """Mock NightFog class for testing"""
    
    def __init__(self, game):
        self.game = game
        self.base_speed = 1.0
        self.base_density = 1.0
        self.difficulty_speed_multiplier = 1.0
        self.difficulty_damage_multiplier = 1.0
        self.difficulty_spawn_multiplier = 1.0
        
    def _apply_adaptive_difficulty(self):
        """Apply adaptive difficulty settings to fog parameters"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            self.difficulty_speed_multiplier = factors['fog_speed']
            self.difficulty_damage_multiplier = factors['enemy_damage']
            self.difficulty_spawn_multiplier = factors['enemy_spawn_rate']
            
            density_modifier = factors['fog_density']
            
            print(f"\nFog with difficulty adjustment:")
            print(f"  Speed: x{self.difficulty_speed_multiplier:.2f}")
            print(f"  Damage: x{self.difficulty_damage_multiplier:.2f}")
            print(f"  Spawn Rate: x{self.difficulty_spawn_multiplier:.2f}")
            print(f"  Density: x{density_modifier:.2f}")

def test_combat_difficulty_adjustment():
    """Test how adaptive difficulty adjusts combat difficulty"""
    print("\n===== Testing Combat Difficulty Adjustment =====")
    
    # Create game instance
    game = MockGame()
    game.setup()
    
    # Create enemy
    enemy = MockEnemy(game)
    
    # Print initial stats
    print("\nInitial enemy stats:")
    print(f"  Health: {enemy.health}")
    print(f"  Damage: {enemy.damage}")
    
    # Apply difficulty adjustment
    enemy.apply_difficulty_adjustment()
    
    # Simulate combat events
    print("\nSimulating good player performance...")
    for _ in range(10):
        # Player deals damage
        game.performance_tracker.record_combat_event('damage_dealt', random.randint(15, 25))
        
        # Player takes little damage
        game.performance_tracker.record_combat_event('damage_taken', random.randint(1, 5))
        
        # Player kills enemy
        game.performance_tracker.record_combat_event('kill', 3.5, "basic")
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    enemy.apply_difficulty_adjustment()
    
    # Now simulate poor player performance
    print("\nSimulating poor player performance...")
    for _ in range(10):
        # Player deals little damage
        game.performance_tracker.record_combat_event('damage_dealt', random.randint(5, 10))
        
        # Player takes high damage
        game.performance_tracker.record_combat_event('damage_taken', random.randint(15, 25))
        
        # Player dies
        game.performance_tracker.record_combat_event('death')
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    enemy.apply_difficulty_adjustment()
    
    return game

def test_boss_difficulty_adjustment(game):
    """Test how adaptive difficulty adjusts boss difficulty"""
    print("\n===== Testing Boss Difficulty Adjustment =====")
    
    # Create boss
    boss = MockBoss(game)
    
    # Print initial stats
    print("\nInitial boss stats:")
    print(f"  Health: {boss.max_health}")
    print(f"  Damage: {boss.damage}")
    print(f"  Cooldowns: {boss.ability_cooldowns}")
    
    # Apply difficulty adjustment
    boss.apply_difficulty_adjustment()
    
    # Simulate fast boss defeat (skilled player)
    print("\nSimulating fast boss defeat (120 seconds)...")
    game.adaptive_difficulty_system.record_boss_event('encounter')
    game.performance_tracker.record_boss_event('encounter', 'forest_guardian')
    game.adaptive_difficulty_system.record_boss_event('defeat', 120)
    game.performance_tracker.record_boss_event('victory', 'forest_guardian', 120)
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    boss.apply_difficulty_adjustment()
    
    # Simulate slow boss defeat (struggling player)
    print("\nSimulating slow boss defeat (360 seconds)...")
    game.adaptive_difficulty_system.record_boss_event('encounter')
    game.performance_tracker.record_boss_event('encounter', 'mountain_titan')
    game.adaptive_difficulty_system.record_boss_event('defeat', 360)
    game.performance_tracker.record_boss_event('victory', 'mountain_titan', 360)
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    boss.apply_difficulty_adjustment()
    
    # Simulate player death to boss
    print("\nSimulating player death to boss...")
    game.adaptive_difficulty_system.record_boss_event('encounter')
    game.performance_tracker.record_boss_event('encounter', 'frost_giant')
    game.adaptive_difficulty_system.record_boss_event('death')
    game.performance_tracker.record_boss_event('defeat', 'frost_giant')
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    boss.apply_difficulty_adjustment()
    
    return game

def test_resource_difficulty_adjustment(game):
    """Test how adaptive difficulty adjusts resource gathering"""
    print("\n===== Testing Resource Difficulty Adjustment =====")
    
    # Create resource nodes
    wood_node = MockResourceNode(game, "wood")
    crystal_node = MockResourceNode(game, "crystal")
    
    # Print initial stats
    print("\nInitial resource node stats:")
    print(f"  Wood: {wood_node.resources_per_harvest} per harvest, {wood_node.regeneration_time}s regen")
    print(f"  Crystal: {crystal_node.resources_per_harvest} per harvest, {crystal_node.regeneration_time}s regen")
    
    # Apply difficulty adjustment
    wood_node.apply_difficulty_adjustment()
    crystal_node.apply_difficulty_adjustment()
    
    # Simulate resource scarcity (reduce resources)
    print("\nSimulating resource scarcity...")
    # Directly manipulate the resource_drop factor
    factors = game.adaptive_difficulty_system.get_current_difficulty_factors()
    factors['resource_drop'] = 0.5
    game.adaptive_difficulty_system.difficulty_factors = factors
    
    # Apply updated difficulty
    wood_node.apply_difficulty_adjustment()
    crystal_node.apply_difficulty_adjustment()
    
    # Simulate resource abundance (increase resources)
    print("\nSimulating resource abundance...")
    # Directly manipulate the resource_drop factor
    factors = game.adaptive_difficulty_system.get_current_difficulty_factors()
    factors['resource_drop'] = 1.5
    game.adaptive_difficulty_system.difficulty_factors = factors
    
    # Apply updated difficulty
    wood_node.apply_difficulty_adjustment()
    crystal_node.apply_difficulty_adjustment()
    
    # Simulate resource events
    print("\nSimulating resource gathering events...")
    for _ in range(10):
        # Record different resource types
        game.performance_tracker.record_resource_event("wood", random.randint(1, 3), "node")
        game.performance_tracker.record_resource_event("stone", random.randint(1, 2), "node")
        game.performance_tracker.record_resource_event("crystal", 1, "node")
    
    # Record resource performance score
    resource_score = game.performance_tracker.get_resource_efficiency_score()
    print(f"\nResource efficiency score: {resource_score:.2f}")
    
    return game

def test_fog_difficulty_adjustment(game):
    """Test how adaptive difficulty adjusts night fog"""
    print("\n===== Testing Night Fog Difficulty Adjustment =====")
    
    # Create mock fog
    fog = MockNightFog(game)
    
    # Apply difficulty adjustment
    fog._apply_adaptive_difficulty()
    
    # Simulate struggling with fog
    print("\nSimulating player struggling with fog...")
    for _ in range(5):
        game.performance_tracker.record_city_event('damage', random.randint(10, 20))
        game.performance_tracker.record_combat_event('death')
        game.performance_tracker.record_survival_event('night_survived')
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    fog._apply_adaptive_difficulty()
    
    # Simulate mastering fog
    print("\nSimulating player mastering fog...")
    for _ in range(5):
        game.performance_tracker.record_city_event('defense_success', 0.9)
        game.performance_tracker.record_combat_event('damage_dealt', random.randint(20, 30))
        game.performance_tracker.record_survival_event('night_survived')
    
    # Wait for difficulty to adjust
    time.sleep(1)
    
    # Apply updated difficulty
    fog._apply_adaptive_difficulty()
    
    return game

def test_overall_performance_scores(game):
    """Test overall performance scores"""
    print("\n===== Testing Overall Performance Scores =====")
    
    # Get individual scores
    combat_score = game.performance_tracker.get_combat_efficiency_score()
    resource_score = game.performance_tracker.get_resource_efficiency_score()
    city_score = game.performance_tracker.get_city_defense_score()
    boss_score = game.performance_tracker.get_boss_performance_score()
    survival_score = game.performance_tracker.get_survival_score()
    overall_score = game.performance_tracker.get_overall_performance_score()
    
    print("\nPerformance Scores:")
    print(f"  Combat: {combat_score:.2f}")
    print(f"  Resource: {resource_score:.2f}")
    print(f"  City: {city_score:.2f}")
    print(f"  Boss: {boss_score:.2f}")
    print(f"  Survival: {survival_score:.2f}")
    print(f"  Overall: {overall_score:.2f}")
    
    # Get difficulty factors
    factors = game.adaptive_difficulty_system.get_current_difficulty_factors()
    print("\nFinal Difficulty Factors:")
    for factor, value in factors.items():
        print(f"  {factor}: x{value:.2f}")
    
    return game

def test_adaptive_difficulty():
    """Main test function that runs all tests"""
    print("Running Adaptive Difficulty System Tests")
    
    # Run the tests
    game = test_combat_difficulty_adjustment()
    game = test_boss_difficulty_adjustment(game)
    game = test_resource_difficulty_adjustment(game)
    game = test_fog_difficulty_adjustment(game)
    game = test_overall_performance_scores(game)
    
    print("\nAdaptive Difficulty System Tests Complete")

if __name__ == "__main__":
    # Configure Panda3D
    loadPrcFileData("", "window-type none")  # Headless mode
    
    # Create app instance without window
    app = ShowBase()
    
    # Run the test
    test_adaptive_difficulty()
    
    # Clean exit
    sys.exit(0) 