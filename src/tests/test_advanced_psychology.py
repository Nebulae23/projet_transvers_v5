#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Advanced Enemy Psychological System
Tests pack behavior, alpha enemies, and complex decision making
"""

import sys
import os
import math
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData

# Ensure the src directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - Advanced Enemy Psychology")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.entity_manager import EntityManager
from game.player import Player
from game.enemy import BasicEnemy, RangedEnemy, AlphaEnemy, NimbleEnemy, BruteEnemy, create_enemy
from game.camera_controller import CameraController
from game.enemy_psychology import PsychologicalState

class TestApp(ShowBase):
    """Test application for advanced enemy psychological system"""
    
    def __init__(self):
        """Initialize the test"""
        super().__init__()
        
        # Set up a basic scene
        self.setup_scene()
        
        # Create entity manager
        self.entity_manager = EntityManager(self)
        
        # Create player
        self.create_player()
        
        # Set up camera controller
        self.camera_controller = CameraController(self)
        self.camera_controller.set_target(self.player.root)
        
        # Create test enemies with different types
        self.create_test_enemy_groups()
        
        # Add controls
        self.setup_controls()
        
        # Enable debug mode
        self.debug_mode = True
        
        # Add UI for test status
        self.setup_ui()
        
        # Add update task
        self.taskMgr.add(self.update, "update")
        
        # Test scenario state
        self.current_test = "default"
        self.test_timer = 0
        
        print("Advanced Psychology Test initialized - use WASD to move, 1-5 to change player power level")
        print("P: Test pack behavior, A: Test alpha rally, D: Test diverse enemies")
    
    def setup_scene(self):
        """Set up the test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(100, 100, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green grass color
        ground.reparentTo(self.render)
    
    def create_player(self):
        """Create the player entity"""
        self.player = Player(self)
        self.player.position = Vec3(0, 0, 0)
        
        # Add to entity manager
        self.entity_manager.players.append(self.player)
    
    def create_test_enemy_groups(self):
        """Create test enemy groups with different types"""
        # Clear existing enemies
        self.entity_manager.enemies = []
        
        # Create an array of enemy groups
        self.enemy_groups = []
        
        # Group 1: Basic enemy pack
        basic_group = []
        basic_group_positions = [
            Vec3(-20, 10, 0),
            Vec3(-22, 8, 0),
            Vec3(-24, 12, 0),
            Vec3(-21, 14, 0),
            Vec3(-19, 11, 0),
        ]
        
        for pos in basic_group_positions:
            enemy = create_enemy(self, "basic", pos)
            basic_group.append(enemy)
            self.entity_manager.enemies.append(enemy)
            
        self.enemy_groups.append({
            "name": "Basic Pack",
            "enemies": basic_group,
            "position": Vec3(-20, 10, 0)
        })
        
        # Group 2: Alpha-led pack
        alpha_group = []
        
        # Alpha leader at center
        alpha = create_enemy(self, "alpha", Vec3(20, 10, 0))
        alpha_group.append(alpha)
        self.entity_manager.enemies.append(alpha)
        
        # Followers
        follower_positions = [
            Vec3(18, 12, 0),
            Vec3(22, 8, 0),
            Vec3(19, 7, 0),
            Vec3(23, 12, 0),
        ]
        
        for pos in follower_positions:
            enemy = create_enemy(self, "basic", pos)
            alpha_group.append(enemy)
            self.entity_manager.enemies.append(enemy)
            
        self.enemy_groups.append({
            "name": "Alpha Pack",
            "enemies": alpha_group,
            "position": Vec3(20, 10, 0)
        })
        
        # Group 3: Diverse enemy types
        diverse_group = []
        
        # One of each type
        enemy_types = ["basic", "ranged", "alpha", "nimble", "brute"]
        diverse_positions = [
            Vec3(0, -20, 0),
            Vec3(-5, -18, 0),
            Vec3(5, -22, 0),
            Vec3(-4, -25, 0),
            Vec3(4, -20, 0),
        ]
        
        for i, enemy_type in enumerate(enemy_types):
            enemy = create_enemy(self, enemy_type, diverse_positions[i])
            diverse_group.append(enemy)
            self.entity_manager.enemies.append(enemy)
            
        self.enemy_groups.append({
            "name": "Diverse Group",
            "enemies": diverse_group,
            "position": Vec3(0, -20, 0)
        })
    
    def setup_controls(self):
        """Set up keyboard controls"""
        # Player movement
        self.accept("w", self.player.set_moving, [True, 0])
        self.accept("w-up", self.player.set_moving, [False, 0])
        self.accept("s", self.player.set_moving, [True, 1])
        self.accept("s-up", self.player.set_moving, [False, 1])
        self.accept("a", self.player.set_moving, [True, 2])
        self.accept("a-up", self.player.set_moving, [False, 2])
        self.accept("d", self.player.set_moving, [True, 3])
        self.accept("d-up", self.player.set_moving, [False, 3])
        
        # Player actions
        self.accept("mouse1", self.player.primary_attack)
        
        # Test controls for changing player power level
        self.accept("1", self.set_player_power_level, [1])  # Default
        self.accept("2", self.set_player_power_level, [2])  # Hesitant threshold
        self.accept("3", self.set_player_power_level, [3])  # Fearful threshold
        self.accept("4", self.set_player_power_level, [4])  # Terrified threshold
        self.accept("5", self.set_player_power_level, [5])  # Subservient threshold
        
        # Test scenario controls
        self.accept("p", self.run_pack_test)     # Pack behavior test
        self.accept("a", self.run_alpha_test)    # Alpha rally test
        self.accept("d", self.run_diverse_test)  # Diverse enemies test
        self.accept("k", self.kill_nearest_enemy) # Kill nearest enemy to test reactions
        
        # Exit
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Set up UI for test status"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Test title
        self.title_text = OnscreenText(
            text="Advanced Enemy Psychology Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Instructions
        self.instructions_text = OnscreenText(
            text="WASD: Move | 1-5: Change power level | P: Pack test | A: Alpha test | D: Diverse test | K: Kill enemy | ESC: Exit",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Player power level
        self.power_level_text = OnscreenText(
            text="Player Power Level: 1 (Normal)",
            pos=(0, -0.8),
            scale=0.05,
            fg=(0.8, 1, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Current test info
        self.test_info_text = OnscreenText(
            text="Current Test: Default",
            pos=(0, -0.9),
            scale=0.05,
            fg=(1, 0.8, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
    
    def set_player_power_level(self, level):
        """
        Set the player's power level for testing
        
        Args:
            level (int): Power level from 1-5
        """
        if level == 1:
            # Default level
            self.player.level = 1
            self.player.damage_multiplier = 1.0
            description = "Normal"
        elif level == 2:
            # Hesitant threshold
            self.player.level = 2
            self.player.damage_multiplier = 1.2
            description = "Hesitant Threshold"
        elif level == 3:
            # Fearful threshold
            self.player.level = 3
            self.player.damage_multiplier = 1.5
            description = "Fearful Threshold"
        elif level == 4:
            # Terrified threshold
            self.player.level = 5
            self.player.damage_multiplier = 2.0
            description = "Terrified Threshold"
        elif level == 5:
            # Subservient threshold
            self.player.level = 8
            self.player.damage_multiplier = 3.0
            description = "Subservient Threshold"
        
        # Update UI
        self.power_level_text.setText(f"Player Power Level: {level} ({description})")
        
        # Print status
        print(f"Player power level set to {level} ({description})")
    
    def run_pack_test(self):
        """Run test scenario for pack behavior"""
        # Reset player position
        self.player.position = Vec3(0, 0, 0)
        
        # Set test state
        self.current_test = "pack"
        self.test_timer = 0
        
        # Update UI
        self.test_info_text.setText("Current Test: Pack Behavior - Approach the basic enemy group")
        
        # Print instructions
        print("PACK BEHAVIOR TEST: Approach the basic enemy group to see how they respond as a group")
        print("Watch how confidence spreads through the group based on your power level")
    
    def run_alpha_test(self):
        """Run test scenario for alpha leadership"""
        # Reset player position
        self.player.position = Vec3(0, 0, 0)
        
        # Set test state
        self.current_test = "alpha"
        self.test_timer = 0
        
        # Update UI
        self.test_info_text.setText("Current Test: Alpha Leadership - Approach the alpha-led group")
        
        # Print instructions
        print("ALPHA LEADERSHIP TEST: Approach the alpha-led group to see how the alpha influences others")
        print("Watch for the alpha's rally ability and how it affects the group's response to threats")
    
    def run_diverse_test(self):
        """Run test scenario for diverse enemy types"""
        # Reset player position
        self.player.position = Vec3(0, 0, 0)
        
        # Set test state
        self.current_test = "diverse"
        self.test_timer = 0
        
        # Update UI
        self.test_info_text.setText("Current Test: Diverse Enemies - Approach the mixed enemy group")
        
        # Print instructions
        print("DIVERSE ENEMIES TEST: Approach the mixed enemy group to see how different types respond")
        print("Notice how each enemy type has different psychological thresholds and behaviors")
    
    def kill_nearest_enemy(self):
        """Kill the nearest enemy to test psychological reactions"""
        if not self.entity_manager.enemies:
            return
            
        # Find nearest enemy
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.entity_manager.enemies:
            distance = (enemy.position - self.player.position).length()
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        if nearest_enemy:
            # Kill the enemy
            print(f"Killing nearest enemy at distance {min_distance:.1f}")
            
            # Notify nearby enemies before removing
            for enemy in self.entity_manager.enemies:
                if enemy != nearest_enemy:
                    distance_to_killed = (enemy.position - nearest_enemy.position).length()
                    if distance_to_killed < 10.0:  # Within awareness range
                        enemy.ally_died(nearest_enemy)
            
            # Remove from entity manager
            self.entity_manager.enemies.remove(nearest_enemy)
            
            # Clean up
            nearest_enemy.root.removeNode()
    
    def update(self, task):
        """Update the test"""
        # Calculate delta time
        dt = globalClock.getDt()
        
        # Update test timer
        self.test_timer += dt
        
        # Update entity manager
        self.entity_manager.update(dt)
        
        # Update player
        self.player.update(dt)
        
        # Update camera
        self.camera_controller.update(dt)
        
        # Handle test-specific logic
        self.update_current_test(dt)
        
        return task.cont
    
    def update_current_test(self, dt):
        """Update current test scenario"""
        if self.current_test == "pack":
            # Check for specific pack behavior tests
            pass
        elif self.current_test == "alpha":
            # Check for alpha rally events
            for group in self.enemy_groups:
                if group["name"] == "Alpha Pack":
                    # Find the alpha
                    alpha = None
                    for enemy in group["enemies"]:
                        if isinstance(enemy, AlphaEnemy):
                            alpha = enemy
                            break
                    
                    if alpha and alpha.rally_active:
                        # Alpha is currently rallying
                        print(f"Alpha enemy is rallying the pack! Rally duration: {alpha.rally_duration:.1f}")
        elif self.current_test == "diverse":
            # Check for diverse behavior patterns
            pass

def main():
    """Run the test"""
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 