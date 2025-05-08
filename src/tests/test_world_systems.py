#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the new world systems (POI, NPC, Quests, and Boss Patterns)
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - World Systems")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.points_of_interest import PointOfInterestManager, POIType, POIState
from game.npc_system import NPCManager, NPCType, DialogueType
from game.quest_system import QuestManager, QuestType, ObjectiveType, QuestObjective
from game.boss_patterns import BossPatternSystem, PatternType, BossPhase, PatternSequence
from game.challenge_mode import ChallengeSystem, ChallengeType

class MockPlayer:
    """Mock player for testing"""
    
    def __init__(self):
        """Initialize mock player"""
        self.position = Vec3(0, 0, 0)
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.inventory = {
            "wood": 0,
            "stone": 0,
            "crystal": 0,
            "herb": 0,
            "monster_essence": 10
        }
        self.name = "TestPlayer"
        self.character_class = "warrior"
        self.game = None
        
    def take_damage(self, amount, source=None):
        """Mock damage taking"""
        self.health = max(0, self.health - amount)
        print(f"Player took {amount} damage. Health: {self.health}/{self.max_health}")
        
    def add_experience(self, amount):
        """Mock experience gain"""
        print(f"Player gained {amount} experience.")

class MockBoss:
    """Mock boss for testing patterns"""
    
    def __init__(self, boss_type="forest_guardian"):
        """Initialize mock boss"""
        self.boss_type = boss_type
        self.position = Vec3(20, 20, 0)
        self.health = 1000
        self.max_health = 1000
        self.game = None
        
    def fire_projectile(self, projectile_type, direction, speed, damage):
        """Mock projectile firing"""
        print(f"Boss fired {projectile_type} projectile with {damage} damage at speed {speed}")
        
    def spawn_effect(self, effect, duration=1.0, position=None):
        """Mock effect spawning"""
        effect_pos = position if position else self.position
        print(f"Spawned effect at {effect_pos} for {duration} seconds")
        
    def play_transition_effect(self, effect_data):
        """Mock transition effect"""
        print(f"Playing transition effect: {effect_data}")
        
    def on_phase_change(self, old_phase, new_phase):
        """Mock phase change handler"""
        print(f"Boss phase changed from {old_phase.value} to {new_phase.value}")

class TestGame:
    """Mock game for testing"""
    
    def __init__(self):
        """Initialize mock game"""
        self.player = MockPlayer()
        self.player.game = self
        
        # Test boss
        self.test_boss = MockBoss()
        self.test_boss.game = self
        
        # Placeholder for entity manager with bosses
        self.entity_manager = type('obj', (object,), {
            'bosses': {'test_boss': self.test_boss}
        })
        
        # Create managers
        self.poi_manager = None
        self.npc_manager = None
        self.quest_manager = None
        self.challenge_system = None
        
        # Task manager (simple version for testing)
        self.taskMgr = TaskManager()
        
        # Loader for assets (mock version)
        self.loader = MockLoader()
        
    def reset(self):
        """Reset state for new tests"""
        self.player.position = Vec3(0, 0, 0)
        self.player.health = self.player.max_health
        self.test_boss.health = self.test_boss.max_health

class TaskManager:
    """Simple task manager for testing"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks = []
        
    def add(self, func, name):
        """Add a task"""
        self.tasks.append((func, name))
        print(f"Added task: {name}")
        return self
        
    def doMethodLater(self, delay, func, name):
        """Schedule a task for later"""
        print(f"Scheduled task: {name} after {delay} seconds")
        return self

class MockLoader:
    """Mock asset loader"""
    
    def loadModel(self, path):
        """Mock model loading"""
        print(f"Loading model: {path}")
        return MockModel(path)
        
    def loadSfx(self, path):
        """Mock sound loading"""
        print(f"Loading sound: {path}")
        return MockSound(path)

class MockModel:
    """Mock 3D model"""
    
    def __init__(self, path):
        """Initialize mock model"""
        self.path = path
        
    def reparentTo(self, parent):
        """Mock parenting"""
        pass
        
    def setScale(self, *args):
        """Mock scaling"""
        pass
        
    def setPos(self, *args):
        """Mock positioning"""
        pass
        
    def setColor(self, *args):
        """Mock coloring"""
        pass

class MockSound:
    """Mock sound effect"""
    
    def __init__(self, path):
        """Initialize mock sound"""
        self.path = path
        
    def play(self):
        """Mock sound playing"""
        print(f"Playing sound: {self.path}")
        
class TestApp(ShowBase):
    """Test application for world systems"""
    
    def __init__(self):
        """Initialize test application"""
        super().__init__()
        
        # Create test game
        self.test_game = TestGame()
        
        # Set up a simple scene
        self.setup_scene()
        
        # Set up camera and controls
        self.setup_camera()
        self.setup_controls()
        
        # Set up UI
        self.setup_ui()
        
        # Run tests
        self.run_tests()
        
    def setup_scene(self):
        """Set up a simple test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(50, 50, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green color
        ground.reparentTo(self.render)
        
    def setup_camera(self):
        """Set up the camera"""
        self.disableMouse()
        self.camera.setPos(0, -30, 20)
        self.camera.lookAt(0, 0, 0)
        
    def setup_controls(self):
        """Set up controls"""
        # Add key bindings
        self.accept("escape", sys.exit)
        self.accept("1", self.test_poi_system)
        self.accept("2", self.test_npc_system)
        self.accept("3", self.test_quest_system)
        self.accept("4", self.test_boss_patterns)
        self.accept("5", self.test_challenge_system)
        self.accept("space", self.run_tests)
        
    def setup_ui(self):
        """Set up UI elements"""
        from direct.gui.OnscreenText import OnscreenText
        
        self.title = OnscreenText(
            text="World Systems Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        self.instructions = OnscreenText(
            text="Press 1-5 to run individual tests, SPACE to run all tests, ESC to exit",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        self.results = OnscreenText(
            text="Ready to run tests",
            pos=(0, -0.8),
            scale=0.05,
            fg=(0.8, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
    def run_tests(self):
        """Run all tests"""
        print("\n===== Running all world system tests =====")
        
        # Reset test state
        self.test_game.reset()
        
        self.test_poi_system()
        self.test_npc_system()
        self.test_quest_system()
        self.test_boss_patterns()
        self.test_challenge_system()
        
        self.results.setText("All tests completed!")
        
    def test_poi_system(self):
        """Test POI system"""
        print("\n----- Testing POI System -----")
        
        # Create POI manager
        self.test_game.poi_manager = PointOfInterestManager(self.test_game)
        
        # Create some test POIs
        dungeon = self.test_game.poi_manager.create_poi(
            "test_dungeon",
            "Dark Cavern",
            POIType.DUNGEON,
            Vec3(10, 10, 0),
            "A dangerous cave system.",
            difficulty=5
        )
        
        merchant = self.test_game.poi_manager.create_poi(
            "test_merchant",
            "Traveling Merchant",
            POIType.MERCHANT_CAMP,
            Vec3(-15, 5, 0),
            "A small trading post.",
            difficulty=2
        )
        
        # Test discovery
        print("Testing POI discovery...")
        # Move player near POI
        self.test_game.player.position = Vec3(12, 9, 0)
        
        # Update POI manager to trigger discovery
        self.test_game.poi_manager.discovery_range = 5.0
        self.test_game.poi_manager.update(self.test_game.player.position)
        
        # Check if discovered
        if dungeon.state == POIState.DISCOVERED:
            print("POI discovery successful!")
        else:
            print("POI discovery failed.")
            
        # Test POI query functions
        nearest = self.test_game.poi_manager.get_nearest_poi(self.test_game.player.position)
        if nearest:
            print(f"Found nearest POI: {nearest.name} at distance {nearest.get_distance_to(self.test_game.player.position)}")
            
        in_radius = self.test_game.poi_manager.get_pois_in_radius(self.test_game.player.position, 20.0)
        print(f"Found {len(in_radius)} POIs within radius.")
        
        # Test save/load
        data = self.test_game.poi_manager.save_data()
        print(f"Saved {len(data['pois'])} POIs")
        
        self.test_game.poi_manager = PointOfInterestManager(self.test_game)
        self.test_game.poi_manager.load_data(data)
        print(f"Loaded {len(self.test_game.poi_manager.points_of_interest)} POIs")
        
        print("POI system test completed!")
        self.results.setText("POI system test completed!")
        
    def test_npc_system(self):
        """Test NPC system"""
        print("\n----- Testing NPC System -----")
        
        # Create NPC manager
        self.test_game.npc_manager = NPCManager(self.test_game)
        
        # Create test NPCs
        quest_giver = self.test_game.npc_manager.create_npc(
            "quest_giver_1",
            "Village Elder",
            NPCType.QUEST_GIVER,
            Vec3(5, 5, 0),
            "models/elder"
        )
        
        merchant = self.test_game.npc_manager.create_npc(
            "merchant_1",
            "Traveling Merchant",
            NPCType.MERCHANT,
            Vec3(-5, 5, 0),
            "models/merchant"
        )
        
        # Add dialogue and items
        quest_giver.add_dialogue(DialogueType.GREETING, "Greetings, adventurer.")
        quest_giver.add_dialogue(DialogueType.QUEST_OFFER, "I have a task for you.")
        
        merchant.add_dialogue(DialogueType.GREETING, "Welcome to my shop!")
        merchant.add_merchant_item("potion", 10, 5)
        
        # Test interaction
        print("Testing NPC interaction...")
        
        # Interact with quest giver
        interaction = quest_giver.interact(self.test_game.player)
        print(f"Quest giver dialogue: {interaction['dialogue']}")
        print(f"Options: {len(interaction['options'])}")
        
        # Interact with merchant
        interaction = merchant.interact(self.test_game.player)
        print(f"Merchant dialogue: {interaction['dialogue']}")
        print(f"Options: {len(interaction['options'])}")
        
        # Test NPC finding
        self.test_game.player.position = Vec3(4, 4, 0)
        nearest = self.test_game.npc_manager.get_nearest_npc(self.test_game.player.position)
        
        if nearest:
            print(f"Found nearest NPC: {nearest.name}")
            at_pos = self.test_game.npc_manager.get_npc_at_position(self.test_game.player.position, 3.0)
            if at_pos:
                print(f"NPC in interaction range: {at_pos.name}")
        
        # Update NPCs
        self.test_game.npc_manager.update(0.1, self.test_game.player.position)
        
        # Test save/load
        data = self.test_game.npc_manager.save_data()
        print(f"Saved {len(data['npcs'])} NPCs")
        
        print("NPC system test completed!")
        self.results.setText("NPC system test completed!")
        
    def test_quest_system(self):
        """Test quest system"""
        print("\n----- Testing Quest System -----")
        
        # Create quest manager
        self.test_game.quest_manager = QuestManager(self.test_game)
        
        # Create test quests
        main_quest = self.test_game.quest_manager.create_quest(
            "main_quest_1",
            "The Dark Cavern",
            QuestType.MAIN,
            "Explore the dark cavern and defeat the boss.",
            level_requirement=1
        )
        
        # Add objectives
        objective1 = QuestObjective(
            "discover_cavern",
            "Discover the Dark Cavern",
            ObjectiveType.DISCOVER,
            "test_dungeon",
            1
        )
        main_quest.add_objective(objective1)
        
        objective2 = QuestObjective(
            "kill_enemies",
            "Defeat 5 cave creatures",
            ObjectiveType.KILL,
            "cave_creature",
            5
        )
        main_quest.add_objective(objective2)
        
        # Add rewards
        main_quest.add_reward("experience", 100)
        main_quest.add_reward("gold", 50)
        
        # Make available
        main_quest.make_available()
        
        # Test quest acceptance
        print("Testing quest acceptance...")
        result = self.test_game.quest_manager.accept_quest("main_quest_1")
        if result:
            print("Quest accepted successfully")
        else:
            print("Quest acceptance failed")
            
        # Test objective updates
        print("Testing objective updates...")
        # Update discover objective
        if main_quest.update_objective_progress(ObjectiveType.DISCOVER, "test_dungeon", 1):
            print("Discovery objective updated")
            
        # Update kill objective
        for i in range(5):
            if main_quest.update_objective_progress(ObjectiveType.KILL, "cave_creature", 1):
                print(f"Kill objective updated: {main_quest.objectives[1].get_progress_text()}")
                
        # Test quest completion
        print("Testing quest completion...")
        if main_quest.is_ready_to_complete():
            print("Quest is ready to complete")
            
            result = self.test_game.quest_manager.complete_quest("main_quest_1")
            if result:
                print("Quest completed successfully")
            else:
                print("Quest completion failed")
        else:
            print("Quest is not ready to complete")
            
        # Test quest management functions
        active_quests = self.test_game.quest_manager.get_active_quests()
        print(f"Active quests: {len(active_quests)}")
        
        available_quests = self.test_game.quest_manager.get_available_quests()
        print(f"Available quests: {len(available_quests)}")
        
        print("Quest system test completed!")
        self.results.setText("Quest system test completed!")
        
    def test_boss_patterns(self):
        """Test boss pattern system"""
        print("\n----- Testing Boss Pattern System -----")
        
        # Create pattern system
        self.test_game.test_boss.pattern_system = BossPatternSystem(self.test_game.test_boss)
        
        # Import pattern types
        from game.boss_patterns import (
            PatternSequence, PatternDifficulty,
            create_pattern
        )
        
        # Create pattern sequences for each phase
        phase1 = PatternSequence(BossPhase.PHASE_1, 1.0)
        
        # Create patterns
        pattern1 = create_pattern(
            PatternType.PROJECTILE_BURST,
            "fireball_burst",
            "Fireball Burst",
            PatternDifficulty.MEDIUM
        )
        
        pattern2 = create_pattern(
            PatternType.CHARGE,
            "rush_attack",
            "Rush Attack",
            PatternDifficulty.MEDIUM
        )
        
        # Add patterns to sequence
        phase1.add_pattern(pattern1, 2.0)
        phase1.add_pattern(pattern2, 1.0)
        
        # Add sequence to boss
        self.test_game.test_boss.pattern_system.add_sequence(BossPhase.PHASE_1, phase1)
        
        # Test pattern selection and execution
        print("Testing pattern selection and execution...")
        player_pos = Vec3(15, 15, 0)
        
        # Select pattern
        pattern = phase1.select_next_pattern(self.test_game.test_boss, player_pos)
        if pattern:
            print(f"Selected pattern: {pattern.name}")
            
            # Start pattern
            phase1.start_pattern(self.test_game.test_boss)
            
            # Update pattern for execution
            phase1.update(0.1, self.test_game.test_boss, player_pos)
            
            print("Pattern executing...")
        else:
            print("No pattern selected")
            
        # Test phase transition
        print("Testing phase transition...")
        # Reduce boss health to trigger phase change
        self.test_game.test_boss.health = int(self.test_game.test_boss.max_health * 0.6)
        
        # Create phase 2 sequence
        phase2 = PatternSequence(BossPhase.PHASE_2, 1.2)
        
        # Create more difficult patterns
        pattern3 = create_pattern(
            PatternType.GROUND_SLAM,
            "ground_slam",
            "Ground Slam",
            PatternDifficulty.HARD
        )
        
        # Add patterns to sequence
        phase2.add_pattern(pattern3, 1.0)
        
        # Add sequence to boss
        self.test_game.test_boss.pattern_system.add_sequence(BossPhase.PHASE_2, phase2)
        
        # Add transition effect
        self.test_game.test_boss.pattern_system.add_transition_effect(
            BossPhase.PHASE_1,
            BossPhase.PHASE_2,
            {"visual": "phase_transition", "sound": "roar"}
        )
        
        # Check phase transition
        self.test_game.test_boss.pattern_system._check_phase_transition()
        
        print(f"Current phase: {self.test_game.test_boss.pattern_system.get_current_phase()}")
        
        # Update pattern system
        self.test_game.test_boss.pattern_system.update(0.1, player_pos)
        
        print("Boss pattern system test completed!")
        self.results.setText("Boss pattern system test completed!")
        
    def test_challenge_system(self):
        """Test challenge system"""
        print("\n----- Testing Challenge System -----")
        
        # Create challenge system
        self.test_game.challenge_system = ChallengeSystem(self.test_game)
        
        # Check default challenges
        challenges = self.test_game.challenge_system.get_available_challenges()
        print(f"Available challenges: {len(challenges)}")
        
        if challenges:
            # Start a challenge
            challenge_id = challenges[0].challenge_id
            print(f"Starting challenge: {challenge_id}")
            
            result = self.test_game.challenge_system.start_challenge(challenge_id)
            if result:
                print("Challenge started successfully")
                
                # Test challenge scoring
                self.test_game.challenge_system.on_enemy_killed("basic_enemy", 1)
                print("Added score for enemy kill")
                
                # Get UI data
                ui_data = self.test_game.challenge_system.get_challenge_ui_data()
                if ui_data["active_challenge"]:
                    print(f"Active challenge: {ui_data['active_challenge']['name']}")
                    print(f"Score: {ui_data['score']}")
                    print(f"Progress: {ui_data['progress']}%")
                
                # Update challenge
                self.test_game.challenge_system.update(0.1)
                
                # Abandon challenge
                result = self.test_game.challenge_system.abandon_challenge()
                if result:
                    print("Challenge abandoned successfully")
            else:
                print("Challenge start failed")
                
        # Test save/load
        data = self.test_game.challenge_system.save_data()
        print(f"Saved challenge data with {len(data['completed_challenges'])} completed challenges")
        
        print("Challenge system test completed!")
        self.results.setText("Challenge system test completed!")

def main():
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 