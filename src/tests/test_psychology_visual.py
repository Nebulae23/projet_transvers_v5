#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Enemy Psychology Visualization Test for Nightfall Defenders
Shows the improved visual indicators for enemy psychological states
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
from direct.gui.DirectGui import DirectButton, DirectLabel, DirectFrame
from panda3d.core import TextNode, Vec3, Vec4, NodePath, AmbientLight, DirectionalLight

from game.enemy_psychology import PsychologicalState, EnemyPsychology

class DummyEnemy:
    """Placeholder enemy for testing psychological states"""
    
    def __init__(self, game, position, name="Enemy"):
        self.game = game
        self.position = Vec3(*position)
        self.name = name
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.height = 1.0
        
        # Create visual representation
        self.render_node = NodePath(f"enemy_{name}")
        self.render_node.reparentTo(game.render)
        self.render_node.setPos(self.position)
        
        # Create enemy model (simple box for now)
        model = game.loader.loadModel("models/box")
        model.setScale(0.5, 0.5, 1.0)  # More human-like proportions
        model.setColor(0.7, 0.2, 0.2, 1.0)  # Red for enemy
        model.reparentTo(self.render_node)
        
        # Add psychology system
        self.psychology = EnemyPsychology(self)

class PsychologyVisualTest(ShowBase):
    """Test application for the enhanced psychology visualization system"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Hide the default mouse cursor and set window title
        self.window_props = self.win.getProperties()
        self.window_props.setTitle("Nightfall Defenders - Psychology Visualization Test")
        self.win.requestProperties(self.window_props)
        
        # Set up the camera
        self.disableMouse()
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 0)
        
        # Set up lighting
        self.setup_lighting()
        
        # Create a floor
        self.create_floor()
        
        # Game time tracking
        self.game_time = 0.0
        
        # Create UI
        self.create_ui()
        
        # Create test enemies to showcase different psychological states
        self.enemies = []
        self.create_test_enemies()
        
        # Set up a task to update the visualization
        self.taskMgr.add(self.update, "update_task")
    
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
            text="Enhanced Enemy Psychology Visualization",
            pos=(0, 0.9),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ACenter
        )
        
        # Instructions
        self.instructions = OnscreenText(
            text="Press keys 1-6 to change the enemy states\n" +
                 "Press R to reset all enemies to normal state\n" +
                 "Use arrow keys to rotate camera",
            pos=(0, 0.8),
            scale=0.04,
            fg=(1, 0.9, 0.8, 1),
            align=TextNode.ACenter
        )
        
        # State buttons
        states = [
            ("1: Normal", PsychologicalState.NORMAL),
            ("2: Hesitant", PsychologicalState.HESITANT),
            ("3: Fearful", PsychologicalState.FEARFUL),
            ("4: Terrified", PsychologicalState.TERRIFIED),
            ("5: Subservient", PsychologicalState.SUBSERVIENT),
            ("6: Empowered", PsychologicalState.EMPOWERED)
        ]
        
        # Create buttons for each state
        button_colors = [
            (0.5, 0.5, 0.5, 0.8),  # Normal - Gray
            (0.8, 0.7, 0.2, 0.8),  # Hesitant - Yellow
            (0.8, 0.5, 0.2, 0.8),  # Fearful - Orange
            (0.8, 0.2, 0.2, 0.8),  # Terrified - Red
            (0.4, 0.4, 0.8, 0.8),  # Subservient - Blue
            (0.6, 0.2, 0.8, 0.8)   # Empowered - Purple
        ]
        
        # Create state buttons
        for i, (label, state) in enumerate(states):
            pos_x = -0.8 + (i % 3) * 0.4
            pos_y = -0.7 - (i // 3) * 0.1
            
            DirectButton(
                text=label,
                scale=0.05,
                pos=(pos_x, 0, pos_y),
                frameColor=button_colors[i],
                command=self.set_all_enemy_states,
                extraArgs=[state],
                relief=4
            )
        
        # Reset button
        DirectButton(
            text="Reset All",
            scale=0.05,
            pos=(0.8, 0, -0.7),
            frameColor=(0.2, 0.6, 0.2, 0.8),
            command=self.reset_enemy_states,
            relief=4
        )
        
        # Add legend
        legend_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.3, 0.3, -0.2, 0.2),
            pos=(0.8, 0, 0.7)
        )
        
        legend_title = DirectLabel(
            text="Psychological States",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.15),
            parent=legend_frame
        )
        
        # Legend entries
        legend_items = [
            ("😐 Normal", (0.7, 0.7, 0.7, 1.0)),
            ("😟 Hesitant", (1.0, 0.8, 0.2, 1.0)),
            ("😨 Fearful", (1.0, 0.5, 0.0, 1.0)),
            ("😱 Terrified", (1.0, 0.0, 0.0, 1.0)),
            ("🙇 Subservient", (0.5, 0.5, 1.0, 1.0)),
            ("😈 Empowered", (0.7, 0.0, 1.0, 1.0))
        ]
        
        for i, (text, color) in enumerate(legend_items):
            y_pos = 0.1 - i * 0.05
            
            label = DirectLabel(
                text=text,
                text_scale=0.03,
                text_fg=color,
                text_align=TextNode.ALeft,
                frameColor=(0, 0, 0, 0),
                pos=(-0.25, 0, y_pos),
                parent=legend_frame
            )
        
        # Add key bindings
        self.accept("1", self.set_all_enemy_states, [PsychologicalState.NORMAL])
        self.accept("2", self.set_all_enemy_states, [PsychologicalState.HESITANT])
        self.accept("3", self.set_all_enemy_states, [PsychologicalState.FEARFUL])
        self.accept("4", self.set_all_enemy_states, [PsychologicalState.TERRIFIED])
        self.accept("5", self.set_all_enemy_states, [PsychologicalState.SUBSERVIENT])
        self.accept("6", self.set_all_enemy_states, [PsychologicalState.EMPOWERED])
        self.accept("r", self.reset_enemy_states)
        
        # Camera controls
        self.accept("arrow_left", self.rotate_camera, [-10, 0])
        self.accept("arrow_right", self.rotate_camera, [10, 0])
        self.accept("arrow_up", self.rotate_camera, [0, -10])
        self.accept("arrow_down", self.rotate_camera, [0, 10])
    
    def create_test_enemies(self):
        """Create test enemies in a circular formation"""
        num_enemies = 10
        radius = 5
        
        for i in range(num_enemies):
            angle = (i / num_enemies) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            enemy = DummyEnemy(self, (x, y, 0), f"Enemy_{i+1}")
            self.enemies.append(enemy)
    
    def set_all_enemy_states(self, state):
        """Set all enemies to the specified psychological state"""
        for enemy in self.enemies:
            enemy.psychology.state = state
            enemy.psychology._update_visual_indicator()
    
    def reset_enemy_states(self):
        """Reset all enemies to the normal state"""
        self.set_all_enemy_states(PsychologicalState.NORMAL)
    
    def rotate_camera(self, h_change, p_change):
        """Rotate the camera around the scene"""
        current_h = self.camera.getH()
        current_p = self.camera.getP()
        
        self.camera.setH(current_h + h_change)
        self.camera.setP(current_p + p_change)
    
    def update(self, task):
        """Update the scene"""
        dt = globalClock.getDt()
        self.game_time += dt
        
        # Update each enemy
        for enemy in self.enemies:
            # Rotate enemies slightly to make the scene more dynamic
            enemy.render_node.setH(enemy.render_node.getH() + dt * 5)
            
            # Update psychology
            enemy.psychology.update_indicator_animation(dt)
        
        return task.cont

def main():
    app = PsychologyVisualTest()
    app.run()

if __name__ == "__main__":
    main() 