#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for environment objects that react to day/night cycle
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Vec4, Point3, loadPrcFileData
from direct.task import Task

# Ensure the src directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - Environment with Day/Night Cycle")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.day_night_cycle import DayNightCycle, TimeOfDay

class EnvironmentObject:
    """Base class for environment objects that react to day/night cycle"""
    
    def __init__(self, render_node, day_night_cycle, position=Vec3(0, 0, 0)):
        """
        Initialize the environment object
        
        Args:
            render_node: The render node to attach this object to
            day_night_cycle: The day/night cycle system
            position: Position for this object
        """
        self.render = render_node
        self.day_night_cycle = day_night_cycle
        self.position = position
        
        # Create the object's node
        self.root = self.render.attachNewNode(f"env_object")
        self.root.setPos(position)
        
        # Set up the object
        self.setup()
        
        # Update based on initial time
        self.update_for_time(day_night_cycle.time_of_day)
    
    def setup(self):
        """Set up the object's visuals (override in subclasses)"""
        pass
    
    def update_for_time(self, time_of_day):
        """
        Update the object based on time of day
        
        Args:
            time_of_day: Current time of day enum value
        """
        pass


class Lantern(EnvironmentObject):
    """A lantern that lights up at night"""
    
    def setup(self):
        """Set up the lantern's visuals"""
        # Create the lantern model
        from panda3d.core import CardMaker
        
        # Lantern post
        post = self.render.loader.loadModel("models/box")
        post.setScale(0.1, 0.1, 1.0)
        post.setPos(0, 0, 0.5)
        post.setColor(0.3, 0.3, 0.3, 1)
        post.reparentTo(self.root)
        
        # Lantern housing
        housing = self.render.loader.loadModel("models/box")
        housing.setScale(0.2, 0.2, 0.2)
        housing.setPos(0, 0, 1.2)
        housing.setColor(0.4, 0.4, 0.2, 1)
        housing.reparentTo(self.root)
        
        # Light source (will turn on at night)
        from panda3d.core import PointLight
        self.light = PointLight("lantern_light")
        self.light.setColor((1.0, 0.9, 0.7, 1.0))
        self.light.setAttenuation((1.0, 0.0, 0.1))  # Set light falloff
        self.light_node = self.root.attachNewNode(self.light)
        self.light_node.setPos(0, 0, 1.2)
        
        # Light visual (glowing center)
        self.light_visual = self.render.loader.loadModel("models/box")
        self.light_visual.setScale(0.1, 0.1, 0.1)
        self.light_visual.setPos(0, 0, 1.2)
        self.light_visual.setColor(1.0, 0.9, 0.7, 1)
        self.light_visual.reparentTo(self.root)
        
        # Light is off initially
        self.render.clearLight(self.light_node)
    
    def update_for_time(self, time_of_day):
        """Turn the light on at night, off during the day"""
        if time_of_day in [TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT, TimeOfDay.DUSK]:
            # Light on at night and dusk
            if time_of_day == TimeOfDay.DUSK:
                # Dim light at dusk
                self.light.setColor((0.7, 0.6, 0.5, 1.0))
                self.light_visual.setColor(0.7, 0.6, 0.5, 1)
            else:
                # Full brightness at night
                self.light.setColor((1.0, 0.9, 0.7, 1.0))
                self.light_visual.setColor(1.0, 0.9, 0.7, 1)
            
            # Turn on the light
            self.render.setLight(self.light_node)
            
            # Make the light visual emissive
            self.light_visual.setColorScale(4.0, 4.0, 4.0, 1.0)
        else:
            # Light off during day
            self.render.clearLight(self.light_node)
            
            # Make the light visual normal (not emissive)
            self.light_visual.setColorScale(1.0, 1.0, 1.0, 1.0)
            self.light_visual.setColor(0.9, 0.9, 0.3, 1)


class Fireflies(EnvironmentObject):
    """Fireflies that appear at dusk and night"""
    
    def setup(self):
        """Set up the firefly particle system"""
        # Create a node for the firefly particles
        self.fireflies_node = self.root.attachNewNode("fireflies")
        
        # Create individual firefly particles as small, glowing points
        from panda3d.core import PointLight
        
        self.firefly_points = []
        for i in range(20):  # 20 fireflies
            # Create a small light for each firefly
            firefly = PointLight(f"firefly_{i}")
            firefly.setColor((0.3, 1.0, 0.1, 1.0))  # Green-yellow glow
            firefly.setAttenuation((1.0, 0.0, 2.0))  # Fast falloff
            
            # Create and position the node
            firefly_node = self.fireflies_node.attachNewNode(firefly)
            
            # Random positions around the center
            import random
            x = random.uniform(-2.0, 2.0)
            y = random.uniform(-2.0, 2.0)
            z = random.uniform(0.5, 2.5)
            firefly_node.setPos(x, y, z)
            
            # Store the firefly
            self.firefly_points.append({
                "node": firefly_node,
                "light": firefly,
                "visible": False,
                "start_pos": Vec3(x, y, z),
                "speed": random.uniform(0.2, 0.7),
                "phase": random.uniform(0, 6.28)  # Random starting phase 0-2π
            })
        
        # Start with fireflies hidden
        self.visible = False
    
    def update_animation(self, task):
        """Update firefly movement and blinking"""
        # If not visible, skip update
        if not self.visible:
            return task.cont
        
        import math
        import random
        
        # Current time for animation
        t = task.time
        
        for firefly in self.firefly_points:
            # Gently move in a random pattern
            node = firefly["node"]
            start_pos = firefly["start_pos"]
            speed = firefly["speed"]
            phase = firefly["phase"]
            
            # Simple harmonic motion with some randomness
            x = start_pos.x + math.sin(t * speed + phase) * 0.8
            y = start_pos.y + math.cos(t * speed + phase * 1.5) * 0.8
            z = start_pos.z + math.sin(t * speed * 0.7 + phase * 0.8) * 0.4
            
            # Update position
            node.setPos(x, y, z)
            
            # Blink effect (periodic brightness change)
            blink = (math.sin(t * speed * 3 + phase) + 1) * 0.5  # 0-1 value
            intensity = 0.1 + blink * 0.9
            firefly["light"].setColor((0.3 * intensity, 1.0 * intensity, 0.1 * intensity, 1.0))
            
            # Random chance to teleport to a new location (simulating fireflies disappearing/reappearing)
            if random.random() < 0.001:  # 0.1% chance per update
                new_x = random.uniform(-2.0, 2.0)
                new_y = random.uniform(-2.0, 2.0)
                new_z = random.uniform(0.5, 2.5)
                firefly["start_pos"] = Vec3(new_x, new_y, new_z)
        
        return task.cont
    
    def update_for_time(self, time_of_day):
        """Show fireflies at dusk and night, hide during day"""
        show_fireflies = time_of_day in [TimeOfDay.DUSK, TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT]
        
        if show_fireflies and not self.visible:
            # Turn on fireflies
            for firefly in self.firefly_points:
                self.render.setLight(firefly["node"])
            self.visible = True
        elif not show_fireflies and self.visible:
            # Turn off fireflies
            for firefly in self.firefly_points:
                self.render.clearLight(firefly["node"])
            self.visible = False


class TestApp(ShowBase):
    """Test application for environment objects that react to day/night cycle"""
    
    def __init__(self):
        """Initialize the test"""
        super().__init__()
        
        # Set up a basic scene
        self.setup_scene()
        
        # Create the day/night cycle system
        self.day_night_cycle = DayNightCycle(self)
        
        # Set accelerated time for testing
        self.day_night_cycle.time_scale = 10.0  # 10x normal speed
        
        # Create environment objects
        self.create_environment_objects()
        
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
        
        print("Environment Objects Test initialized - use 1-5 keys to set time of day, +/- to adjust time scale")
    
    def setup_scene(self):
        """Set up the test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(50, 50, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green grass color
        ground.reparentTo(self.render)
        
        # Add a path
        path = self.loader.loadModel("models/box")
        path.setScale(10, 0.5, 0.05)
        path.setPos(0, 0, 0)
        path.setColor((0.7, 0.6, 0.5, 1))  # Brown path
        path.reparentTo(self.render)
        
        # Add some vegetation patches
        for pos in [(-5, 5, 0), (5, -7, 0), (-8, -3, 0), (7, 4, 0)]:
            grass = self.loader.loadModel("models/box")
            grass.setScale(2, 2, 0.05)
            grass.setPos(*pos)
            grass.setColor((0.2, 0.6, 0.1, 1))  # Dark green
            grass.reparentTo(self.render)
    
    def create_environment_objects(self):
        """Create various environment objects that react to time of day"""
        self.env_objects = []
        
        # Create lanterns along the path
        for x in range(-8, 9, 4):
            lantern_left = Lantern(self.render, self.day_night_cycle, Vec3(x, 1.0, 0))
            lantern_right = Lantern(self.render, self.day_night_cycle, Vec3(x, -1.0, 0))
            self.env_objects.extend([lantern_left, lantern_right])
        
        # Create firefly areas
        for pos in [(-6, 6, 0), (6, -6, 0), (-3, -8, 0), (8, 2, 0)]:
            fireflies = Fireflies(self.render, self.day_night_cycle, Vec3(*pos))
            # Start the animation task for each firefly group
            self.taskMgr.add(fireflies.update_animation, f"fireflies_anim_{pos}")
            self.env_objects.append(fireflies)
    
    def setup_camera(self):
        """Set up the camera"""
        # Position the camera for a good view of the scene
        self.camera.setPos(0, -20, 10)
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
            text="Environment Objects with Day/Night Cycle",
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
            text="Time Scale: 10.0x",
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
        
        # Update all environment objects
        for obj in self.env_objects:
            obj.update_for_time(time_of_day)
            
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
        pos.z = max(5, min(30, pos.z + angle * 0.5))
        
        # Set new position
        self.camera.setPos(pos)
        
        # Look at center
        self.camera.lookAt(0, 0, 0)
    
    def reset_camera(self):
        """Reset camera to initial position"""
        self.camera.setPos(0, -20, 10)
        self.camera.lookAt(0, 0, 0)
        print("Camera reset")
    
    def update(self, task):
        """Update the test"""
        # Calculate delta time
        dt = globalClock.getDt()
        
        # Update day/night cycle
        self.day_night_cycle.update(dt)
        
        # When time of day changes, update environment objects
        current_time = self.day_night_cycle.time_of_day
        if not hasattr(self, 'last_time') or self.last_time != current_time:
            for obj in self.env_objects:
                obj.update_for_time(current_time)
            self.last_time = current_time
        
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