#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Enemy Psychology System with Night Fog interaction
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
loadPrcFileData("", "window-title Test - Enemy Psychology with Night Fog")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.enemy import BasicEnemy
from game.enemy_psychology import EnemyPsychology, PsychologicalState
from game.day_night_cycle import DayNightCycle, TimeOfDay
from game.night_fog import NightFog

class PlayerDummy:
    """Dummy player class for testing"""
    def __init__(self, position=Vec3(0, 0, 0), level=1):
        self.position = position
        self.level = level
        self.health = 100
        self.max_health = 100
        self.projectile_type = 'straight'
        self.projectile_types = {
            'straight': {'damage': 10, 'name': 'Straight Shot'}
        }

class TestApp(ShowBase):
    """Test application for enemy psychology system"""
    
    def __init__(self):
        """Initialize the test"""
        super().__init__()
        
        # Create basic game structure for testing
        self.setup_scene()
        
        # Create player
        self.player = PlayerDummy()
        
        # Create the day/night cycle system
        self.day_night_cycle = DayNightCycle(self)
        
        # Create the night fog system
        self.night_fog = NightFog(self)
        
        # Set accelerated time for testing
        self.day_night_cycle.time_scale = 10.0  # 10x normal speed
        
        # Create test enemies
        self.test_enemies = []
        self.create_test_enemies()
        
        # Add controls
        self.setup_controls()
        
        # Set up UI for test controls
        self.setup_ui()
        
        # Add update task
        self.taskMgr.add(self.update, "update")
        
        # Position camera
        self.setup_camera()
        
        print("Psychology Test initialized - use keys to control test")
    
    def setup_scene(self):
        """Set up the test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(100, 100, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green grass color
        ground.reparentTo(self.render)
        
        # Create city area in center
        city_ground = self.loader.loadModel("models/box")
        city_ground.setScale(10, 10, 0.2)
        city_ground.setPos(0, 0, 0)
        city_ground.setColor((0.5, 0.5, 0.5, 1))  # Gray for city area
        city_ground.reparentTo(self.render)
        
        # Create marker for player position
        player_marker = self.loader.loadModel("models/box")
        player_marker.setScale(1, 1, 2)
        player_marker.setPos(0, 0, 1)
        player_marker.setColor((0.2, 0.8, 0.2, 1))  # Green
        player_marker.reparentTo(self.render)
    
    def setup_camera(self):
        """Set up the camera"""
        self.camera.setPos(0, -40, 30)
        self.camera.lookAt(0, 0, 0)
    
    def create_test_enemies(self):
        """Create test enemies with different states"""
        # Create several enemies in different positions
        positions = [
            Vec3(-15, 0, 0),  # Left
            Vec3(15, 0, 0),   # Right
            Vec3(0, 15, 0),   # Back
            Vec3(0, -15, 0),  # Front
            Vec3(-10, 10, 0),  # Diagonal
            Vec3(10, -10, 0),  # Diagonal
        ]
        
        for i, pos in enumerate(positions):
            enemy = BasicEnemy(self, pos)
            
            # Add a visual indicator for psychological state
            indicator = self.loader.loadModel("models/box")
            indicator.setScale(0.5, 0.5, 0.5)
            indicator.setPos(0, 0, 3)  # Above enemy
            indicator.reparentTo(enemy.model)
            enemy.psych_indicator = indicator
            
            # Store the enemy
            self.test_enemies.append(enemy)
    
    def setup_controls(self):
        """Set up keyboard controls"""
        # Time of day controls
        self.accept("1", self.set_time_of_day, [TimeOfDay.DAWN])
        self.accept("2", self.set_time_of_day, [TimeOfDay.DAY])
        self.accept("3", self.set_time_of_day, [TimeOfDay.DUSK])
        self.accept("4", self.set_time_of_day, [TimeOfDay.NIGHT])
        self.accept("5", self.set_time_of_day, [TimeOfDay.MIDNIGHT])
        
        # Fog controls
        self.accept("f", self.toggle_fog)
        self.accept("i", self.increase_fog_intensity)
        self.accept("k", self.decrease_fog_intensity)
        
        # Player level controls
        self.accept("l", self.increase_player_level)
        self.accept("j", self.decrease_player_level)
        
        # Player position controls
        self.accept("w", self.move_player, [Vec3(0, 5, 0)])
        self.accept("s", self.move_player, [Vec3(0, -5, 0)])
        self.accept("a", self.move_player, [Vec3(-5, 0, 0)])
        self.accept("d", self.move_player, [Vec3(5, 0, 0)])
        
        # Reset player position
        self.accept("r", self.reset_player)
        
        # Toggle test fog tendrils
        self.accept("t", self.spawn_test_tendrils)
        
        # Exit
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Set up UI for test controls"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Test title
        self.title_text = OnscreenText(
            text="Enemy Psychology with Night Fog Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Instructions
        self.instructions_text = OnscreenText(
            text="1-5: Set time of day | F: Toggle fog | I/K: Increase/Decrease fog intensity\n"
                 "L/J: Increase/Decrease player level | WASD: Move player | R: Reset player\n"
                 "T: Spawn test fog tendrils | ESC: Exit",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Current time and player info
        self.info_text = OnscreenText(
            text="Time: Dawn | Player Level: 1 | Fog: Inactive",
            pos=(-1.0, -0.8),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1),
            align=0,
            mayChange=True
        )
        
        # Enemy state text (to be updated)
        self.enemy_text = OnscreenText(
            text="Enemy States: Initializing...",
            pos=(-1.0, -0.9),
            scale=0.06,
            fg=(1, 0.8, 0.8, 1),
            shadow=(0, 0, 0, 1),
            align=0,
            mayChange=True
        )
    
    def set_time_of_day(self, time_of_day):
        """Set the time of day for testing"""
        self.day_night_cycle.set_time(time_of_day)
        print(f"Time set to {self.day_night_cycle.get_time_of_day_name()}")
    
    def toggle_fog(self):
        """Toggle night fog on/off"""
        if hasattr(self, 'night_fog'):
            self.night_fog.toggle_fog()
            status = "Active" if self.night_fog.active else "Inactive"
            print(f"Fog toggled: {status}")
    
    def increase_fog_intensity(self):
        """Increase fog intensity"""
        if hasattr(self, 'night_fog'):
            new_intensity = min(1.0, self.night_fog.intensity + 0.1)
            self.night_fog.set_intensity(new_intensity)
            print(f"Fog intensity increased to {new_intensity:.1f}")
    
    def decrease_fog_intensity(self):
        """Decrease fog intensity"""
        if hasattr(self, 'night_fog'):
            new_intensity = max(0.0, self.night_fog.intensity - 0.1)
            self.night_fog.set_intensity(new_intensity)
            print(f"Fog intensity decreased to {new_intensity:.1f}")
    
    def increase_player_level(self):
        """Increase player level to affect power ratio"""
        self.player.level += 1
        print(f"Player level increased to {self.player.level}")
    
    def decrease_player_level(self):
        """Decrease player level to affect power ratio"""
        if self.player.level > 1:
            self.player.level -= 1
            print(f"Player level decreased to {self.player.level}")
    
    def move_player(self, delta):
        """Move player by delta amount"""
        self.player.position += delta
        # Update player marker
        if hasattr(self, 'player_marker'):
            self.player_marker.setPos(self.player.position)
        print(f"Player moved to {self.player.position}")
    
    def reset_player(self):
        """Reset player to center position"""
        self.player.position = Vec3(0, 0, 0)
        # Update player marker
        if hasattr(self, 'player_marker'):
            self.player_marker.setPos(self.player.position)
        print("Player reset to center")
    
    def spawn_test_tendrils(self):
        """Manually spawn test fog tendrils"""
        if hasattr(self, 'night_fog'):
            # Force active
            self.night_fog.active = True
            self.night_fog.intensity = 0.8
            
            # Force spawn some tendrils
            for _ in range(3):
                self.night_fog._spawn_tendrils()
            
            print("Spawned test fog tendrils")
    
    def update(self, task):
        """Update the test"""
        # Calculate delta time
        dt = globalClock.getDt()
        
        # Update day/night cycle
        self.day_night_cycle.update(dt)
        
        # Update night fog
        self.night_fog.update(dt)
        
        # Update enemies
        for enemy in self.test_enemies:
            if hasattr(enemy, 'update'):
                enemy.update(dt)
        
        # Update UI
        self.update_ui()
        
        return task.cont
    
    def update_ui(self):
        """Update UI with current state information"""
        # Update time and player info
        fog_status = "Active" if self.night_fog.active else "Inactive"
        fog_intensity = self.night_fog.intensity if self.night_fog.active else 0.0
        
        info_text = f"Time: {self.day_night_cycle.get_time_of_day_name()} | "
        info_text += f"Player Level: {self.player.level} | "
        info_text += f"Fog: {fog_status} ({fog_intensity:.1f})"
        
        self.info_text.setText(info_text)
        
        # Update enemy state info
        enemy_states = []
        for i, enemy in enumerate(self.test_enemies):
            if hasattr(enemy, 'psychology') and hasattr(enemy.psychology, 'state'):
                state = enemy.psychology.get_state_description()
                # Add indicator for fog empowerment
                fog_indicator = ""
                if hasattr(enemy.psychology, 'fog_empowerment') and enemy.psychology.fog_empowerment > 0:
                    fog_indicator = f" (Fog: {enemy.psychology.fog_empowerment:.1f})"
                enemy_states.append(f"Enemy {i+1}: {state}{fog_indicator}")
        
        # Format enemy state text
        enemy_text = "Enemy States:\n" + "\n".join(enemy_states)
        self.enemy_text.setText(enemy_text)

def main():
    """Main function"""
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 