#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test for the Verlet-based physics character animation system
Demonstrates procedural body part generation and physics-based animation
"""

import sys
import os
import math
import random
from typing import Dict, List, Tuple, Optional

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Vec3, Point3, NodePath, LineSegs, PandaNode
from panda3d.core import AmbientLight, DirectionalLight, LVector3
from panda3d.core import KeyboardButton

# Add src parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.engine.physics.verlet import VerletSystem
from src.game.character_physics import CharacterPhysics, MovementState
from src.tools.asset_generator.body_part_generator import BodyPartGenerator, CharacterClass

class TestVerletCharacter(ShowBase):
    """Test application for physics-based character animation"""
    
    def __init__(self):
        """Initialize the test application"""
        ShowBase.__init__(self)
        
        # Set up camera
        self.disableMouse()
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 2)
        
        # Set up lighting
        self._setup_lighting()
        
        # Create physics system
        self.verlet_system = VerletSystem()
        self.verlet_system.set_gravity(Vec3(0, 0, -9.81))
        
        # Add ground plane
        self.verlet_system.add_collision_plane(Vec3(0, 0, 1), 0, friction=0.95, bounce=0.3)
        
        # Add obstacles
        self.verlet_system.add_collision_box(
            Vec3(2, -1, 0), 
            Vec3(3, 1, 1.5),
            friction=0.8,
            bounce=0.4
        )
        
        self.verlet_system.add_collision_box(
            Vec3(-3, -1, 0), 
            Vec3(-2, 1, 0.5),
            friction=0.8,
            bounce=0.4
        )
        
        # Enable debug visualization
        self.verlet_system.enable_debug_visualization(self.render)
        
        # Create body part generator
        self.body_generator = BodyPartGenerator()
        
        # Create characters
        self.characters = []
        self._create_characters()
        
        # Set up tasks
        self.taskMgr.add(self._update_task, "UpdateTask")
        
        # Set up input
        self.keys = {}
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self._set_key, ["left", True])
        self.accept("arrow_left-up", self._set_key, ["left", False])
        self.accept("arrow_right", self._set_key, ["right", True])
        self.accept("arrow_right-up", self._set_key, ["right", False])
        self.accept("arrow_up", self._set_key, ["up", True])
        self.accept("arrow_up-up", self._set_key, ["up", False])
        self.accept("arrow_down", self._set_key, ["down", True])
        self.accept("arrow_down-up", self._set_key, ["down", False])
        self.accept("space", self._set_key, ["jump", True])
        self.accept("space-up", self._set_key, ["jump", False])
        
        # Set up info text
        self._setup_instructions()
        
        # Camera follow target
        self.camera_target = self.characters[0] if self.characters else None
    
    def _set_key(self, key, value):
        """Record key states"""
        self.keys[key] = value
    
    def _setup_lighting(self):
        """Set up scene lighting"""
        # Add ambient light
        ambient_light = AmbientLight("ambient")
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        ambient_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_np)
        
        # Add directional light
        directional_light = DirectionalLight("directional")
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        directional_light.setDirection(LVector3(-1, -1, -2))
        directional_np = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_np)
    
    def _setup_instructions(self):
        """Set up on-screen instructions"""
        instructions = [
            "Physics-Based Character Animation Test",
            "Controls:",
            "  Left/Right Arrow: Move character",
            "  Space: Jump",
            "  Up/Down Arrow: Change character tension",
            "  Escape: Quit"
        ]
        
        self.instruction_text = self.addText("\n".join(instructions), pos=(-1.3, 0.9), scale=0.05)
    
    def _create_characters(self):
        """Create demonstration characters"""
        # Create different character types
        character_classes = [
            CharacterClass.WARRIOR, 
            CharacterClass.MAGE,
            CharacterClass.RANGER
        ]
        
        positions = [
            Vec3(-1, 0, 1),
            Vec3(0, 0, 1),
            Vec3(1, 0, 1)
        ]
        
        for i, (char_class, position) in enumerate(zip(character_classes, positions)):
            # Generate character model
            height = 2.0
            character_model = self.body_generator.generate_character_model(
                char_class, 
                height, 
                variation_seed=i
            )
            
            # Create character physics
            character = CharacterPhysics(self.verlet_system)
            character.initialize_from_model(character_model, position, facing_right=(i % 2 == 0))
            character.set_ground_height(0)
            
            # Enable debug visualization
            character.enable_debug_visualization(self.render)
            
            # Set initial pose
            character.set_movement_state(MovementState.IDLE)
            character.set_tension(0.7)
            
            # Store character
            self.characters.append(character)
    
    def _update_task(self, task):
        """Main update task"""
        dt = globalClock.getDt()
        
        # Update character control for the first character
        if self.characters:
            self._process_input(self.characters[0], dt)
        
        # Update physics
        self.verlet_system.update(dt, substeps=4)
        
        # Update characters
        for character in self.characters:
            character.update(dt)
        
        # Update debug visualization
        self.verlet_system.update_debug_visualization()
        for character in self.characters:
            character.update_debug_visualization()
        
        # Update camera to follow target
        if self.camera_target:
            center = self.camera_target._get_character_center()
            target_pos = center - Vec3(0, -8, -2)
            
            # Smooth camera movement
            current_pos = self.camera.getPos()
            self.camera.setPos(current_pos + (target_pos - current_pos) * min(1.0, dt * 2.0))
            self.camera.lookAt(center)
        
        return Task.cont
    
    def _process_input(self, character, dt):
        """Process input for character control"""
        # Movement direction
        move_x = 0
        move_z = 0
        
        if self.keys.get("left", False):
            move_x -= 1
        if self.keys.get("right", False):
            move_x += 1
        
        # Handle jumping
        if self.keys.get("jump", False) and character.on_ground:
            # Apply upward force to torso
            if "torso_mid" in character.points:
                character.points["torso_mid"].apply_force(Vec3(0, 0, 200))
                
            # Also to hips
            if "hip_left" in character.points:
                character.points["hip_left"].apply_force(Vec3(0, 0, 100))
            if "hip_right" in character.points:
                character.points["hip_right"].apply_force(Vec3(0, 0, 100))
            
            character.set_movement_state(MovementState.JUMPING)
        
        # Adjust tension
        if self.keys.get("up", False):
            character.set_tension(min(1.0, character.tension + dt))
        if self.keys.get("down", False):
            character.set_tension(max(0.2, character.tension - dt))
        
        # Set movement state based on input
        if abs(move_x) > 0.1:
            # Set direction
            character.facing_direction = 1 if move_x > 0 else -1
            
            # Set movement state
            character.set_movement_state(
                MovementState.WALKING, 
                target_velocity=Vec3(move_x * 2, 0, 0)
            )
            
            # Apply movement force
            if character.on_ground:
                center = character._get_character_center()
                
                # Apply force to all parts to move
                for point_name, point in character.points.items():
                    # Less force to extremities
                    force_mult = 1.0
                    if "wrist" in point_name or "ankle" in point_name:
                        force_mult = 0.4
                    elif "elbow" in point_name or "knee" in point_name:
                        force_mult = 0.6
                    
                    point.apply_force(Vec3(move_x * 5 * force_mult, 0, 0))
        else:
            if character.on_ground:
                character.set_movement_state(MovementState.IDLE)
            else:
                character.set_movement_state(MovementState.FALLING)
                
def main():
    """Run the test application"""
    app = TestVerletCharacter()
    app.run()

if __name__ == "__main__":
    main() 