#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Day/Night Cycle System
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
loadPrcFileData("", "window-title Test - Day/Night Cycle System")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.day_night_cycle import DayNightCycle, TimeOfDay

class TestApp(ShowBase):
    """Test application for day/night cycle system"""
    
    def __init__(self):
        """Initialize the test"""
        super().__init__()
        
        # Set up a basic scene
        self.setup_scene()
        
        # Create the day/night cycle system
        self.day_night_cycle = DayNightCycle(self)
        
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
        
        print("Day/Night Cycle Test initialized - use 1-5 keys to set time of day, +/- to adjust time scale")
    
    def setup_scene(self):
        """Set up the test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(100, 100, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green grass color
        ground.reparentTo(self.render)
        
        # Add some simple buildings
        self.create_buildings()
        
        # Add some trees
        self.create_trees()
        
        # Add water
        self.create_water()
    
    def create_buildings(self):
        """Create some simple buildings for the scene"""
        # Main building
        building = self.loader.loadModel("models/box")
        building.setScale(5, 5, 4)
        building.setPos(10, 10, 2)
        building.setColor((0.6, 0.6, 0.6, 1))  # Gray
        building.reparentTo(self.render)
        
        # Roof
        roof = self.loader.loadModel("models/box")
        roof.setScale(5.5, 5.5, 1)
        roof.setPos(10, 10, 6)
        roof.setColor((0.8, 0.3, 0.3, 1))  # Red
        roof.reparentTo(self.render)
        
        # Second building
        building2 = self.loader.loadModel("models/box")
        building2.setScale(3, 3, 3)
        building2.setPos(-15, 5, 1.5)
        building2.setColor((0.7, 0.7, 0.5, 1))  # Beige
        building2.reparentTo(self.render)
        
        # Roof 2
        roof2 = self.loader.loadModel("models/box")
        roof2.setScale(3.5, 3.5, 0.5)
        roof2.setPos(-15, 5, 4.5)
        roof2.setColor((0.3, 0.3, 0.8, 1))  # Blue
        roof2.reparentTo(self.render)
    
    def create_trees(self):
        """Create simple tree models"""
        # Create several trees
        tree_positions = [
            (-5, -5, 0),
            (-8, -10, 0),
            (15, -8, 0),
            (20, 5, 0),
            (-20, -15, 0),
            (5, 20, 0)
        ]
        
        for pos in tree_positions:
            # Tree trunk
            trunk = self.loader.loadModel("models/box")
            trunk.setScale(0.5, 0.5, 2)
            trunk.setPos(pos[0], pos[1], pos[2] + 1)
            trunk.setColor((0.6, 0.4, 0.2, 1))  # Brown
            trunk.reparentTo(self.render)
            
            # Tree foliage
            foliage = self.loader.loadModel("models/box")
            foliage.setScale(2, 2, 2)
            foliage.setPos(pos[0], pos[1], pos[2] + 3)
            foliage.setColor((0.1, 0.5, 0.1, 1))  # Dark green
            foliage.reparentTo(self.render)
    
    def create_water(self):
        """Create water surface"""
        water = self.loader.loadModel("models/box")
        water.setScale(30, 20, 0.1)
        water.setPos(-30, -30, -0.05)
        water.setColor((0.2, 0.4, 0.8, 0.8))  # Semi-transparent blue
        water.setTransparency(1)  # Enable transparency
        water.reparentTo(self.render)
    
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
        
        # Time scale controls
        self.accept("=", self.adjust_time_scale, [1.0])
        self.accept("+", self.adjust_time_scale, [1.0])
        self.accept("-", self.adjust_time_scale, [-1.0])
        self.accept("0", self.reset_time_scale)
        
        # Camera controls
        self.accept("arrow_left", self.rotate_camera, [-5])
        self.accept("arrow_right", self.rotate_camera, [5])
        self.accept("arrow_up", self.tilt_camera, [5])
        self.accept("arrow_down", self.tilt_camera, [-5])
        
        # Reset camera
        self.accept("r", self.reset_camera)
        
        # Exit
        self.accept("escape", sys.exit)
    
    def setup_ui(self):
        """Set up UI for test controls"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Test title
        self.title_text = OnscreenText(
            text="Day/Night Cycle System Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Instructions
        self.instructions_text = OnscreenText(
            text="1-5: Set time of day | +/-: Adjust time scale | 0: Reset time scale | Arrow keys: Rotate camera | R: Reset camera | ESC: Exit",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Current time display
        self.time_text = OnscreenText(
            text="Time: Dawn (00:00)",
            pos=(0, -0.8),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Time scale display
        self.scale_text = OnscreenText(
            text="Time Scale: 20.0x",
            pos=(0, -0.9),
            scale=0.06,
            fg=(1, 0.8, 0.8, 1),
            shadow=(0, 0, 0, 1)
        )
    
    def set_time_of_day(self, time_of_day):
        """
        Set the time of day
        
        Args:
            time_of_day: TimeOfDay enum value
        """
        self.day_night_cycle.set_time(time_of_day)
        print(f"Time set to {self.day_night_cycle.get_time_of_day_name()}")
    
    def adjust_time_scale(self, delta):
        """
        Adjust the time scale
        
        Args:
            delta: Amount to adjust by
        """
        current_scale = self.day_night_cycle.time_scale
        new_scale = max(0.1, min(100.0, current_scale + delta))
        self.day_night_cycle.set_time_scale(new_scale)
        print(f"Time scale set to {self.day_night_cycle.time_scale}x")
    
    def reset_time_scale(self):
        """Reset time scale to default"""
        self.day_night_cycle.set_time_scale(1.0)
        print("Time scale reset to 1.0x")
    
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
        
        # Update UI
        self.update_ui()
        
        return task.cont
    
    def update_ui(self):
        """Update UI elements with current time info"""
        # Format time as hours:minutes
        hours = int((self.day_night_cycle.current_time * 24)) % 24
        minutes = int((self.day_night_cycle.current_time * 24 * 60) % 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        
        # Update time display
        self.time_text.setText(f"Time: {self.day_night_cycle.get_time_of_day_name()} ({time_str})")
        
        # Update time scale display
        self.scale_text.setText(f"Time Scale: {self.day_night_cycle.time_scale:.1f}x")

def main():
    """Main function"""
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 