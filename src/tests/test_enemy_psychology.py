#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Enemy Psychological System
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData

# Ensure the src directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - Enemy Psychological System")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.entity_manager import EntityManager
from game.player import Player
from game.enemy import BasicEnemy, RangedEnemy
from game.camera_controller import CameraController
from game.enemy_psychology import PsychologicalState

class TestApp(ShowBase):
    """Test application for enemy psychological system"""
    
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
        
        # Create test enemies at different positions
        self.create_test_enemies()
        
        # Add controls
        self.setup_controls()
        
        # Enable debug mode
        self.debug_mode = True
        
        # Add UI for test status
        self.setup_ui()
        
        # Add update task
        self.taskMgr.add(self.update, "update")
        
        print("Test initialized - use WASD to move, 1-9 to change player power level")
    
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
        
        # Make accessible directly
        self.player = self.player
    
    def create_test_enemies(self):
        """Create test enemies at different positions"""
        # Create a ring of enemies around the player
        enemies_count = 12
        radius = 10.0
        
        for i in range(enemies_count):
            angle = (i / enemies_count) * 360
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            
            # Alternate between basic and ranged enemies
            if i % 2 == 0:
                enemy = BasicEnemy(self, Vec3(x, y, 0))
            else:
                enemy = RangedEnemy(self, Vec3(x, y, 0))
            
            # Add to entity manager
            self.entity_manager.enemies.append(enemy)
    
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
        
        # Exit
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Set up UI for test status"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Test title
        self.title_text = OnscreenText(
            text="Enemy Psychological System Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Instructions
        self.instructions_text = OnscreenText(
            text="WASD: Move | 1-5: Change player power level | ESC: Exit",
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
        
        # Enemy states summary
        self.enemy_states_text = OnscreenText(
            text="Enemy States: Normal: 12, Hesitant: 0, Fearful: 0, Terrified: 0, Subservient: 0",
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
    
    def update(self, task):
        """Update the test"""
        # Calculate delta time
        dt = globalClock.getDt()
        
        # Update entity manager
        self.entity_manager.update(dt)
        
        # Update player
        self.player.update(dt)
        
        # Update camera
        self.camera_controller.update(dt)
        
        # Update UI with enemy states
        self.update_enemy_states_ui()
        
        return task.cont
    
    def update_enemy_states_ui(self):
        """Update the UI with enemy psychological states summary"""
        # Count enemies in each state
        state_counts = {
            PsychologicalState.NORMAL: 0,
            PsychologicalState.HESITANT: 0,
            PsychologicalState.FEARFUL: 0,
            PsychologicalState.TERRIFIED: 0,
            PsychologicalState.SUBSERVIENT: 0
        }
        
        # Count enemies in each state
        for enemy in self.entity_manager.enemies:
            if hasattr(enemy, 'psychology') and hasattr(enemy.psychology, 'state'):
                state_counts[enemy.psychology.state] += 1
        
        # Update text
        text = "Enemy States: "
        text += f"Normal: {state_counts[PsychologicalState.NORMAL]}, "
        text += f"Hesitant: {state_counts[PsychologicalState.HESITANT]}, "
        text += f"Fearful: {state_counts[PsychologicalState.FEARFUL]}, "
        text += f"Terrified: {state_counts[PsychologicalState.TERRIFIED]}, "
        text += f"Subservient: {state_counts[PsychologicalState.SUBSERVIENT]}"
        
        self.enemy_states_text.setText(text)

def main():
    """Main function"""
    app = TestApp()
    app.run()

if __name__ == "__main__":
    import math  # Needed for test enemy placement
    main() 