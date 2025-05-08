#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Organic Animation Test for Nightfall Defenders
Demonstrates the enhanced verlet physics-based animation system
"""

import os
import sys
import math
import random

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectLabel, DirectRadioButton, DirectFrame
from panda3d.core import TextNode, Vec3, Vec4, NodePath, AmbientLight, DirectionalLight, LineSegs

from engine.physics.verlet import VerletSystem, VerletPoint

class OrganicAnimationTest(ShowBase):
    """Test application for the enhanced organic animation system"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Hide the default mouse cursor and set window title
        self.window_props = self.win.getProperties()
        self.window_props.setTitle("Nightfall Defenders - Organic Animation Test")
        self.win.requestProperties(self.window_props)
        
        # Set up the camera
        self.disableMouse()
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 0)
        
        # Set up lighting
        self.setup_lighting()
        
        # Create a floor
        self.create_floor()
        
        # Create UI
        self.create_ui()
        
        # Physics variables
        self.verlet_system = VerletSystem()
        self.character_rigs = {}
        self.current_character = "humanoid"
        self.visual_nodes = {}
        self.debug_lines = None
        
        # Time tracking
        self.time = 0.0
        self.paused = False
        
        # Create initial character rig
        self.create_character("humanoid", Vec3(0, 0, 0))
        
        # Add a task to update the physics
        self.taskMgr.add(self.update, "update_task")
        
        # Set up key bindings
        self.setup_keys()
    
    def setup_lighting(self):
        """Set up basic lighting for the scene"""
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor(Vec4(0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Main directional light
        dlight = DirectionalLight('dlight')
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
    
    def create_floor(self):
        """Create a simple floor for the scene"""
        floor = self.loader.loadModel("models/box")
        floor.setScale(10, 10, 0.1)
        floor.setPos(0, 0, -0.1)
        floor.setColor(0.3, 0.3, 0.3, 1)
        floor.reparentTo(self.render)
    
    def create_ui(self):
        """Create the user interface"""
        # Title
        self.title = OnscreenText(
            text="Enhanced Organic Animation System",
            pos=(0, 0.9),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ACenter
        )
        
        # Instructions
        self.instructions = OnscreenText(
            text="Press H to switch to Humanoid, Q to switch to Quadruped\n" +
                 "Press SPACE to toggle animation, R to reset position\n" +
                 "Press G to apply gravity effects, W to add wind\n" +
                 "Use arrow keys to rotate camera",
            pos=(0, 0.8),
            scale=0.04,
            fg=(1, 0.9, 0.8, 1),
            align=TextNode.ACenter
        )
        
        # Character type radio buttons
        character_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.25, 0.25, -0.15, 0.15),
            pos=(-0.7, 0, 0.7)
        )
        
        character_label = DirectLabel(
            text="Character Type",
            scale=0.04,
            pos=(0, 0, 0.1),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=character_frame
        )
        
        self.character_buttons = []
        var = [0]  # Shared variable for radio button state
        
        humanoid_button = DirectRadioButton(
            text="Humanoid (H)",
            variable=var,
            value=[0],
            scale=0.04,
            pos=(-0.15, 0, 0.02),
            text_align=TextNode.ALeft,
            command=self.set_character_type,
            extraArgs=["humanoid"],
            parent=character_frame
        )
        
        quadruped_button = DirectRadioButton(
            text="Quadruped (Q)",
            variable=var,
            value=[1],
            scale=0.04,
            pos=(-0.15, 0, -0.06),
            text_align=TextNode.ALeft,
            command=self.set_character_type,
            extraArgs=["quadruped"],
            parent=character_frame
        )
        
        humanoid_button.setOthers([quadruped_button])
        quadruped_button.setOthers([humanoid_button])
        
        # Initially select humanoid
        humanoid_button.commandFunc([0])
        
        # Effect buttons
        effect_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.25, 0.25, -0.2, 0.15),
            pos=(0.7, 0, 0.7)
        )
        
        effect_label = DirectLabel(
            text="Effects",
            scale=0.04,
            pos=(0, 0, 0.1),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=effect_frame
        )
        
        gravity_button = DirectButton(
            text="Apply Gravity (G)",
            scale=0.04,
            pos=(0, 0, 0.02),
            command=self.apply_gravity,
            frameColor=(0.3, 0.3, 0.6, 0.8),
            parent=effect_frame
        )
        
        wind_button = DirectButton(
            text="Apply Wind (W)",
            scale=0.04,
            pos=(0, 0, -0.06),
            command=self.apply_wind,
            frameColor=(0.3, 0.5, 0.3, 0.8),
            parent=effect_frame
        )
        
        reset_button = DirectButton(
            text="Reset Position (R)",
            scale=0.04,
            pos=(0, 0, -0.14),
            command=self.reset_character,
            frameColor=(0.6, 0.3, 0.3, 0.8),
            parent=effect_frame
        )
        
        # Animation controls
        anim_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.25, 0.25, -0.2, 0.15),
            pos=(0, 0, -0.7)
        )
        
        anim_label = DirectLabel(
            text="Animation Controls",
            scale=0.04,
            pos=(0, 0, 0.1),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=anim_frame
        )
        
        toggle_button = DirectButton(
            text="Toggle Animation (SPACE)",
            scale=0.04,
            pos=(0, 0, 0.02),
            command=self.toggle_animation,
            frameColor=(0.3, 0.3, 0.6, 0.8),
            parent=anim_frame
        )
        
        # Animation presets
        idle_button = DirectButton(
            text="Idle Animation",
            scale=0.04,
            pos=(0, 0, -0.06),
            command=self.set_animation,
            extraArgs=["idle"],
            frameColor=(0.3, 0.5, 0.3, 0.8),
            parent=anim_frame
        )
        
        walk_button = DirectButton(
            text="Walk Animation",
            scale=0.04,
            pos=(0, 0, -0.14),
            command=self.set_animation,
            extraArgs=["walk"],
            frameColor=(0.3, 0.5, 0.3, 0.8),
            parent=anim_frame
        )
    
    def setup_keys(self):
        """Set up key bindings"""
        self.accept("h", self.set_character_type, ["humanoid"])
        self.accept("q", self.set_character_type, ["quadruped"])
        self.accept("g", self.apply_gravity)
        self.accept("w", self.apply_wind)
        self.accept("r", self.reset_character)
        self.accept("space", self.toggle_animation)
        
        # Camera rotation
        self.accept("arrow_left", self.rotate_camera, [-10, 0])
        self.accept("arrow_right", self.rotate_camera, [10, 0])
        self.accept("arrow_up", self.rotate_camera, [0, -10])
        self.accept("arrow_down", self.rotate_camera, [0, 10])
    
    def create_character(self, character_type, position):
        """Create a character rig of the specified type"""
        # Clean up any existing rig
        if character_type in self.character_rigs:
            self.remove_character(character_type)
        
        # Create a new rig in the physics system
        rig = self.verlet_system.create_character_rig(position, height=2.0, character_type=character_type)
        self.character_rigs[character_type] = rig
        
        # Create visual representation
        self.create_visual_representation(character_type, rig)
        
        # Set current character
        self.current_character = character_type
    
    def remove_character(self, character_type):
        """Remove a character rig"""
        if character_type in self.visual_nodes:
            self.visual_nodes[character_type].removeNode()
            del self.visual_nodes[character_type]
        
        # Physics system will be reset when creating a new character
    
    def create_visual_representation(self, character_type, rig):
        """Create visual representation of the character rig"""
        # Create a parent node
        node = NodePath(f"{character_type}_visual")
        node.reparentTo(self.render)
        
        # Create spheres for joints
        for joint_name, point in rig.items():
            # Create a sphere for the joint
            sphere = self.loader.loadModel("models/box")
            sphere.setScale(0.1, 0.1, 0.1)
            sphere.setPos(point.position)
            
            # Color based on joint type
            if "head" in joint_name:
                sphere.setColor(0.9, 0.7, 0.7, 1.0)  # Pink-ish for head
                sphere.setScale(0.15, 0.15, 0.15)  # Larger for head
            elif "hand" in joint_name or "foot" in joint_name:
                sphere.setColor(0.7, 0.7, 0.9, 1.0)  # Blue-ish for extremities
            elif "shoulder" in joint_name or "hip" in joint_name:
                sphere.setColor(0.9, 0.9, 0.7, 1.0)  # Yellow-ish for major joints
            else:
                sphere.setColor(0.7, 0.9, 0.7, 1.0)  # Green-ish for other joints
            
            sphere.reparentTo(node)
            
            # Store reference to sphere
            point.visual_node = sphere
        
        # Create connection lines
        self.update_connection_lines(character_type, rig)
        
        # Store reference to the visual node
        self.visual_nodes[character_type] = node
    
    def update_connection_lines(self, character_type, rig):
        """Update the visual lines connecting the joints"""
        # Remove old lines if they exist
        if self.debug_lines:
            self.debug_lines.removeNode()
        
        # Create new lines
        lines = LineSegs()
        lines.setColor(1, 1, 1, 0.8)
        lines.setThickness(3)
        
        # Add segments based on character type
        if character_type == "humanoid":
            # Connections list (joint pairs)
            connections = [
                # Torso connections
                ("pelvis", "chest"),
                ("chest", "neck"),
                ("neck", "head"),
                
                # Left arm
                ("chest", "l_shoulder"),
                ("l_shoulder", "l_elbow"),
                ("l_elbow", "l_hand"),
                
                # Right arm
                ("chest", "r_shoulder"),
                ("r_shoulder", "r_elbow"),
                ("r_elbow", "r_hand"),
                
                # Left leg
                ("pelvis", "l_hip"),
                ("l_hip", "l_knee"),
                ("l_knee", "l_foot"),
                
                # Right leg
                ("pelvis", "r_hip"),
                ("r_hip", "r_knee"),
                ("r_knee", "r_foot")
            ]
            
        elif character_type == "quadruped":
            # Connections list for quadruped
            connections = [
                # Body
                ("rear", "mid"),
                ("mid", "front"),
                ("front", "neck"),
                ("neck", "head"),
                
                # Tail
                ("rear", "tail_base"),
                ("tail_base", "tail_mid"),
                ("tail_mid", "tail_tip"),
                
                # Front legs
                ("front", "fl_shoulder"),
                ("fl_shoulder", "fl_knee"),
                ("fl_knee", "fl_foot"),
                
                ("front", "fr_shoulder"),
                ("fr_shoulder", "fr_knee"),
                ("fr_knee", "fr_foot"),
                
                # Rear legs
                ("rear", "rl_hip"),
                ("rl_hip", "rl_knee"),
                ("rl_knee", "rl_foot"),
                
                ("rear", "rr_hip"),
                ("rr_hip", "rr_knee"),
                ("rr_knee", "rr_foot")
            ]
        else:
            # Simple fallback
            connections = [
                ("pelvis", "chest"),
                ("chest", "head"),
                ("chest", "l_hand"),
                ("chest", "r_hand"),
                ("pelvis", "l_foot"),
                ("pelvis", "r_foot")
            ]
        
        # Draw each connection
        for start, end in connections:
            if start in rig and end in rig:
                start_pos = rig[start].position
                end_pos = rig[end].position
                
                lines.moveTo(start_pos)
                lines.drawTo(end_pos)
        
        # Create node path and attach to scene
        self.debug_lines = self.render.attachNewNode(lines.create())
    
    def set_character_type(self, character_type):
        """Switch to a different character type"""
        if character_type != self.current_character:
            self.create_character(character_type, Vec3(0, 0, 0))
    
    def apply_gravity(self):
        """Apply a gravity force to the character"""
        self.verlet_system.apply_force_to_all(Vec3(0, 0, -9.8))
    
    def apply_wind(self):
        """Apply a wind force to the character"""
        # Random wind direction
        wind_dir_x = random.uniform(-1, 1)
        wind_dir_y = random.uniform(-1, 1)
        wind_strength = random.uniform(5, 15)
        
        self.verlet_system.apply_force_to_all(Vec3(wind_dir_x, wind_dir_y, 0) * wind_strength)
    
    def reset_character(self):
        """Reset the character to its initial position"""
        # Simply recreate the current character
        self.create_character(self.current_character, Vec3(0, 0, 0))
    
    def toggle_animation(self):
        """Toggle animation paused/running"""
        self.paused = not self.paused
    
    def set_animation(self, animation_type):
        """Set a specific animation preset"""
        if self.current_character not in self.character_rigs:
            return
        
        rig = self.character_rigs[self.current_character]
        
        if animation_type == "idle":
            # Simple idle breathing animation
            self.animation_type = "idle"
            # Reset will be handled in update
            
        elif animation_type == "walk":
            # Walking animation
            self.animation_type = "walk"
            # Reset will be handled in update
    
    def rotate_camera(self, h_change, p_change):
        """Rotate the camera around the scene"""
        current_h = self.camera.getH()
        current_p = self.camera.getP()
        
        self.camera.setH(current_h + h_change)
        self.camera.setP(current_p + p_change)
    
    def update_idle_animation(self, dt, character_type, rig):
        """Update idle breathing animation"""
        self.time += dt
        
        # Simple breathing motion
        breathing = math.sin(self.time * 2.0) * 0.03
        
        if character_type == "humanoid":
            if "chest" in rig:
                current_pos = rig["chest"].position
                rig["chest"].position.z = current_pos.z + breathing
            
            if "head" in rig:
                current_pos = rig["head"].position
                rig["head"].position.z = current_pos.z + breathing * 0.5
        
        elif character_type == "quadruped":
            if "mid" in rig:
                current_pos = rig["mid"].position
                rig["mid"].position.z = current_pos.z + breathing
            
            if "head" in rig:
                current_pos = rig["head"].position
                rig["head"].position.z = current_pos.z + breathing * 0.5
                
            # Tail wagging
            if "tail_mid" in rig and "tail_tip" in rig:
                tail_wag = math.sin(self.time * 5.0) * 0.1
                rig["tail_mid"].position.y = tail_wag
                rig["tail_tip"].position.y = tail_wag * 2.0
    
    def update_walk_animation(self, dt, character_type, rig):
        """Update walking animation"""
        self.time += dt
        
        # Walking cycle frequency
        cycle = self.time * 3.0
        
        if character_type == "humanoid":
            # Leg motion
            if "l_knee" in rig and "r_knee" in rig:
                leg_motion = math.sin(cycle) * 0.3
                rig["l_knee"].position.x = rig["l_hip"].position.x + leg_motion
                rig["r_knee"].position.x = rig["r_hip"].position.x - leg_motion
            
            # Arm swing
            if "l_elbow" in rig and "r_elbow" in rig:
                arm_motion = math.sin(cycle) * 0.3
                rig["l_elbow"].position.x = rig["l_shoulder"].position.x - arm_motion
                rig["r_elbow"].position.x = rig["r_shoulder"].position.x + arm_motion
            
            # Body bounce
            if "pelvis" in rig:
                bounce = abs(math.sin(cycle * 2.0)) * 0.05
                rig["pelvis"].position.z = bounce + rig["pelvis"].old_position.z
                
        elif character_type == "quadruped":
            # Leg motion (diagonal pairs move together)
            front_left = math.sin(cycle) * 0.2
            front_right = math.sin(cycle + math.pi) * 0.2
            rear_left = math.sin(cycle + math.pi) * 0.2
            rear_right = math.sin(cycle) * 0.2
            
            if "fl_knee" in rig:
                rig["fl_knee"].position.x = rig["fl_shoulder"].position.x + front_left
            
            if "fr_knee" in rig:
                rig["fr_knee"].position.x = rig["fr_shoulder"].position.x + front_right
                
            if "rl_knee" in rig:
                rig["rl_knee"].position.x = rig["rl_hip"].position.x + rear_left
                
            if "rr_knee" in rig:
                rig["rr_knee"].position.x = rig["rr_hip"].position.x + rear_right
            
            # Body motion
            if "mid" in rig:
                bounce = abs(math.sin(cycle * 2.0)) * 0.05
                rig["mid"].position.z = bounce + rig["mid"].old_position.z
            
            # Head bob
            if "head" in rig:
                head_bob = math.sin(cycle) * 0.05
                rig["head"].position.z = rig["head"].old_position.z + head_bob
            
            # Tail wag while walking
            if "tail_mid" in rig and "tail_tip" in rig:
                tail_wag = math.sin(cycle * 2.0) * 0.15
                rig["tail_mid"].position.y = tail_wag
                rig["tail_tip"].position.y = tail_wag * 2.0
    
    def update(self, task):
        """Update the physics simulation"""
        if not self.paused:
            dt = globalClock.getDt()
            
            # Update physics
            self.verlet_system.update(dt)
            
            # Update animations if not paused
            if hasattr(self, 'animation_type'):
                if self.animation_type == "idle":
                    self.update_idle_animation(dt, self.current_character, self.character_rigs[self.current_character])
                elif self.animation_type == "walk":
                    self.update_walk_animation(dt, self.current_character, self.character_rigs[self.current_character])
            
            # Update visual representation
            for joint_name, point in self.character_rigs[self.current_character].items():
                if hasattr(point, 'visual_node') and point.visual_node:
                    point.visual_node.setPos(point.position)
            
            # Update connection lines
            self.update_connection_lines(self.current_character, self.character_rigs[self.current_character])
        
        return task.cont

def main():
    app = OrganicAnimationTest()
    app.run()

if __name__ == "__main__":
    main() 