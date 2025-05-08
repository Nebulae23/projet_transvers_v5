#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Night Fog System
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
loadPrcFileData("", "window-title Test - Night Fog System")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.day_night_cycle import DayNightCycle, TimeOfDay
from game.night_fog import NightFog
from game.entity_manager import EntityManager

class TestApp(ShowBase):
    """Test application for night fog system"""
    
    def __init__(self):
        """Initialize the test"""
        super().__init__()
        
        # Create basic game structure for testing
        self.setup_scene()
        
        # Set up mock entity manager
        self.entity_manager = EntityManager(self)
        
        # Create the day/night cycle system
        self.day_night_cycle = DayNightCycle(self)
        
        # Create the night fog system
        self.night_fog = NightFog(self)
        
        # Set accelerated time for testing
        self.day_night_cycle.time_scale = 20.0  # 20x normal speed
        
        # Create a simple camera controller
        self.setup_camera()
        
        # Add controls
        self.setup_controls()
        
        # Enable debug mode for visualization
        self.debug_mode = True
        
        # Set up UI for test controls
        self.setup_ui()
        
        # Add update task
        self.taskMgr.add(self.update, "update")
        
        # Create player dummy
        self.create_player_dummy()
        
        print("Night Fog Test initialized - use 1-5 keys to set time of day, +/- to adjust time scale, F to toggle fog")
    
    def create_player_dummy(self):
        """Create a dummy player object for testing"""
        # Simple box to represent player
        player_model = self.loader.loadModel("models/box")
        player_model.setScale(1, 1, 2)
        player_model.setPos(0, 0, 1)
        player_model.setColor((0.2, 0.8, 0.2, 1))  # Green for player
        player_model.reparentTo(self.render)
        
        # Create player object with position property for fog system
        class PlayerDummy:
            def __init__(self, position):
                self.position = position
                self.is_player = True
                
        self.player = PlayerDummy(Vec3(0, 0, 0))
    
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
        
        # Add some simple buildings
        self.create_buildings()
    
    def create_buildings(self):
        """Create some simple buildings for the scene"""
        # City center building
        center = self.loader.loadModel("models/box")
        center.setScale(3, 3, 5)
        center.setPos(0, 0, 2.5)
        center.setColor((0.7, 0.7, 0.7, 1))
        center.reparentTo(self.render)
        
        # Add some houses around center
        house_positions = [
            (5, 5, 0),
            (-5, 5, 0),
            (5, -5, 0),
            (-5, -5, 0)
        ]
        
        for i, (x, y, z) in enumerate(house_positions):
            house = self.loader.loadModel("models/box")
            house.setScale(2, 2, 2)
            house.setPos(x, y, z + 1)
            
            # Different colors for different houses
            colors = [
                (0.8, 0.3, 0.3, 1),  # Red
                (0.3, 0.8, 0.3, 1),  # Green
                (0.3, 0.3, 0.8, 1),  # Blue
                (0.8, 0.8, 0.3, 1)   # Yellow
            ]
            house.setColor(colors[i % len(colors)])
            house.reparentTo(self.render)
    
    def setup_camera(self):
        """Set up the camera"""
        # Position the camera for a good view of the scene
        self.camera.setPos(30, -30, 25)
        self.camera.lookAt(0, 0, 0)
    
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
        
        # Time scale controls
        self.accept("=", self.adjust_time_scale, [1.0])
        self.accept("+", self.adjust_time_scale, [1.0])
        self.accept("-", self.adjust_time_scale, [-1.0])
        
        # Camera controls
        self.accept("arrow_left", self.rotate_camera, [-5])
        self.accept("arrow_right", self.rotate_camera, [5])
        self.accept("arrow_up", self.tilt_camera, [5])
        self.accept("arrow_down", self.tilt_camera, [-5])
        
        # Reset camera
        self.accept("r", self.reset_camera)
        
        # Spawn test fog tendrils
        self.accept("t", self.spawn_test_tendrils)
        
        # Exit
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Set up UI for test controls"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Test title
        self.title_text = OnscreenText(
            text="Night Fog System Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Instructions
        self.instructions_text = OnscreenText(
            text="1-5: Set time of day | F: Toggle fog | I/K: Increase/Decrease fog intensity\n"
                 "+/-: Adjust time scale | Arrow keys: Rotate camera | R: Reset camera | T: Spawn test tendrils | ESC: Exit",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Current time display
        self.time_text = OnscreenText(
            text="Time: Dawn (00:00)",
            pos=(-1.0, -0.8),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1),
            align=0  # Fixed: Use integer constant instead of string
        )
        
        # Fog intensity display
        self.fog_text = OnscreenText(
            text="Fog: Inactive (0.0)",
            pos=(-1.0, -0.9),
            scale=0.06,
            fg=(0.8, 0.8, 1.0, 1),
            shadow=(0, 0, 0, 1),
            align=0  # Fixed: Use integer constant instead of string
        )
    
    def set_time_of_day(self, time_of_day):
        """
        Set the time of day
        
        Args:
            time_of_day: TimeOfDay enum value
        """
        self.day_night_cycle.set_time(time_of_day)
        print(f"Time set to {self.day_night_cycle.get_time_of_day_name()}")
    
    def toggle_fog(self):
        """Toggle night fog on/off"""
        if hasattr(self, 'night_fog'):
            self.night_fog.toggle()
            
            # Update UI text
            if self.night_fog.active:
                self.fog_text.setText(f"Fog: Active ({self.night_fog.intensity:.1f})")
            else:
                self.fog_text.setText(f"Fog: Inactive ({self.night_fog.intensity:.1f})")
    
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
    
    def adjust_time_scale(self, delta):
        """
        Adjust the time scale
        
        Args:
            delta: Amount to adjust by
        """
        current_scale = self.day_night_cycle.time_scale
        new_scale = max(0.1, min(100.0, current_scale + delta))
        self.day_night_cycle.time_scale = new_scale
        print(f"Time scale set to {self.day_night_cycle.time_scale}x")
    
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
    
    def rotate_camera(self, angle):
        """
        Rotate the camera around the scene
        
        Args:
            angle: Angle to rotate by in degrees
        """
        # Get current camera position
        pos = self.camera.getPos()
        
        # Rotate around Y axis
        import math
        radius = math.sqrt(pos.x * pos.x + pos.y * pos.y)
        current_angle = math.atan2(pos.y, pos.x)
        new_angle = current_angle + math.radians(angle)
        
        # Calculate new position
        new_x = radius * math.cos(new_angle)
        new_y = radius * math.sin(new_angle)
        
        # Set new position
        self.camera.setPos(new_x, new_y, pos.z)
        
        # Look at center
        self.camera.lookAt(0, 0, 0)
    
    def tilt_camera(self, angle):
        """
        Tilt the camera up or down
        
        Args:
            angle: Angle to tilt by in degrees
        """
        # Get current camera position
        pos = self.camera.getPos()
        
        # Adjust height
        pos.z = max(5, min(50, pos.z + angle * 0.5))
        
        # Set new position
        self.camera.setPos(pos)
        
        # Look at center
        self.camera.lookAt(0, 0, 0)
    
    def reset_camera(self):
        """Reset camera to initial position"""
        self.camera.setPos(30, -30, 25)
        self.camera.lookAt(0, 0, 0)
        print("Camera reset")
    
    def update(self, task):
        """Update the test"""
        # Calculate delta time
        dt = globalClock.getDt()
        
        # Update day/night cycle
        self.day_night_cycle.update(dt)
        
        # Update night fog
        self.night_fog.update(dt)
        
        # Update UI
        self.update_ui()
        
        return task.cont
    
    def update_ui(self):
        """Update UI elements with current time and fog info"""
        # Format time as hours:minutes
        hours = int((self.day_night_cycle.current_time * 24)) % 24
        minutes = int((self.day_night_cycle.current_time * 24 * 60) % 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        
        # Update time display
        self.time_text.setText(f"Time: {self.day_night_cycle.get_time_of_day_name()} ({time_str})")
        
        # Update fog display
        if hasattr(self, 'night_fog'):
            status = "Active" if self.night_fog.active else "Inactive"
            self.fog_text.setText(f"Fog: {status} ({self.night_fog.intensity:.1f})")
            
            # Update fog text color based on intensity
            if self.night_fog.active:
                # More red as intensity increases
                red = 0.8 + self.night_fog.intensity * 0.2
                green = 0.8 - self.night_fog.intensity * 0.6
                blue = 1.0 - self.night_fog.intensity * 0.7
                self.fog_text.setFg((red, green, blue, 1))
            else:
                self.fog_text.setFg((0.8, 0.8, 1.0, 1))

def main():
    """Main function"""
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 