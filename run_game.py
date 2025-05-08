#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for Nightfall Defenders game
"""

import sys
import os
import math
import random
import argparse

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DGG
from panda3d.core import (
    WindowProperties, TextNode, LVector3f, 
    AntialiasAttrib, TransparencyAttrib, Vec3, Shader, ShaderAttrib, Texture
)

# Import game modules
from game.player import Player
from game.day_night_cycle import DayNightCycle
from game.entity_manager import EntityManager
from game.adaptive_difficulty import AdaptiveDifficultySystem
from game.audio_manager import AudioManager

# Import physics systems
from src.engine.physics import PhysicsManager

# Import new systems
from game.character_class import ClassManager, ClassType
from game.skill_tree import SkillTree
from game.class_selection_ui import ClassSelectionUI
from game.skill_tree_ui import SkillTreeUI
import game.skill_definitions as skill_definitions
from game.random_events import RandomEventSystem
from game.night_fog import NightFog

class NightfallDefendersGame(ShowBase):
    """Main game class for Nightfall Defenders"""
    
    def __init__(self):
        """Initialize the game"""
        ShowBase.__init__(self)
        
        # Game settings
        self.debug_mode = False
        self.paused = False
        self.show_fps = True
        
        # Setup window properties
        self.setup_window()
        
        # Set up the camera
        self.setup_camera()
        
        # Create UI elements
        self.create_ui()
        
        # Initialize game systems
        self.setup_game_systems()
        
        # Key bindings
        self.setup_keys()
        
        # Create initial game world
        self.create_world()
        
        # Start the game loop
        self.taskMgr.add(self.update, "GameUpdateTask")
        
        print("Nightfall Defenders game initialized!")
    
    def setup_window(self):
        """Set up the game window"""
        props = WindowProperties()
        props.setTitle("Nightfall Defenders")
        props.setSize(1920, 1080)
        self.win.requestProperties(props)
        
        # Enable antialiasing
        self.render.setAntialias(AntialiasAttrib.MAuto)
    
    def setup_camera(self):
        """Set up the game camera"""
        # Disable the default mouse control
        self.disableMouse()
        
        # Position the camera
        self.camera.setPos(0, -20, 15)
        self.camera.lookAt(0, 0, 0)
    
    def create_ui(self):
        """Create UI elements"""
        # Health and status display
        self.health_text = OnscreenText(
            text="Health: 100/100", 
            pos=(-1.3, 0.9), 
            scale=0.05,
            align=TextNode.ALeft,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Experience display
        self.exp_text = OnscreenText(
            text="Level: 1 | XP: 0/100", 
            pos=(-1.3, 0.8), 
            scale=0.05,
            align=TextNode.ALeft,
            fg=(0.8, 0.8, 1, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Current weapon/ability display
        self.weapon_text = OnscreenText(
            text="Current Ability: None", 
            pos=(-1.3, 0.7), 
            scale=0.05,
            align=TextNode.ALeft,
            fg=(1, 0.8, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Time display
        self.time_text = OnscreenText(
            text="Time: Day 1, 00:00", 
            pos=(1.3, 0.9), 
            scale=0.05,
            align=TextNode.ARight,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # FPS counter
        self.fps_text = OnscreenText(
            text="FPS: 0", 
            pos=(1.3, 0.8), 
            scale=0.05,
            align=TextNode.ARight,
            fg=(0.8, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Inventory display
        self.inventory_text = OnscreenText(
            text="Inventory: Empty", 
            pos=(-1.3, -0.9), 
            scale=0.05,
            align=TextNode.ALeft,
            fg=(0.8, 0.8, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Skill points display
        self.skill_points_text = OnscreenText(
            text="Skill Points: 0", 
            pos=(-1.3, 0.6), 
            scale=0.05,
            align=TextNode.ALeft,
            fg=(0.4, 1, 0.4, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Create skill tree button
        self.skill_tree_button = DirectButton(
            text="Skill Tree",
            scale=0.05,
            pos=(1.15, 0, 0.7),
            command=self.toggle_skill_tree,
            frameColor=(0.2, 0.2, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT
        )
        
        # Experience bar
        self.create_exp_bar()
    
    def create_exp_bar(self):
        """Create the experience bar"""
        # Background bar
        self.exp_bar_bg = DirectFrame(
            frameColor=(0.2, 0.2, 0.4, 0.8),
            frameSize=(-0.5, 0.5, -0.02, 0.02),
            pos=(0, 0, -0.85),
            parent=self.aspect2d
        )
        
        # Foreground (progress) bar
        self.exp_bar_fg = DirectFrame(
            frameColor=(0.4, 0.4, 1, 0.9),
            frameSize=(-0.5, -0.5, -0.02, 0.02),  # Will be updated
            pos=(0, 0, -0.85),
            parent=self.aspect2d
        )
    
    def update_exp_bar(self):
        """Update the experience bar display"""
        if hasattr(self, 'player'):
            # Get experience percentage
            exp_percent = self.player.get_experience_percent()
            
            # Update bar width
            width = 1.0 * exp_percent
            self.exp_bar_fg["frameSize"] = (-0.5, -0.5 + width, -0.02, 0.02)
    
    def setup_game_systems(self):
        """Initialize game systems"""
        # Entity manager
        self.entity_manager = EntityManager(self)
        
        # Day/night cycle
        self.day_night_cycle = DayNightCycle(self)
        
        # Audio manager
        self.audio_manager = AudioManager(self)
        
        # Physics manager
        self.physics_manager = PhysicsManager(self)
        
        # New systems
        self.class_manager = ClassManager()
        self.skill_definitions = skill_definitions
        
        # Adaptive difficulty
        self.adaptive_difficulty = AdaptiveDifficultySystem(self)
        
        # Random event system
        self.random_event_system = RandomEventSystem(self)
        
        # Night fog system
        self.night_fog = NightFog(self)
    
    def setup_keys(self):
        """Set up key bindings"""
        # Movement keys
        self.accept("w", self.set_player_moving, [True, 0])  # Forward
        self.accept("w-up", self.set_player_moving, [False, 0])
        self.accept("s", self.set_player_moving, [True, 1])  # Backward
        self.accept("s-up", self.set_player_moving, [False, 1])
        self.accept("a", self.set_player_moving, [True, 2])  # Left
        self.accept("a-up", self.set_player_moving, [False, 2])
        self.accept("d", self.set_player_moving, [True, 3])  # Right
        self.accept("d-up", self.set_player_moving, [False, 3])
        
        # Action keys
        self.accept("mouse1", self.player_primary_attack)
        self.accept("mouse3", self.player_secondary_attack)
        self.accept("space", self.player_dodge)
        self.accept("e", self.player_interact)
        
        # UI keys
        self.accept("f3", self.toggle_debug)
        self.accept("k", self.toggle_skill_tree)
        self.accept("escape", self.toggle_pause)
        
        # Debug keys
        self.accept("f9", self.give_skill_point)
        self.accept("f10", self.give_monster_essence)
        self.accept("f", self.toggle_night_fog)  # Toggle night fog
    
    def create_world(self):
        """Create the initial game world"""
        # Create the player
        self.player = Player(self)
        self.player.position = LVector3f(0, 0, 0)
        
        # Create the UI for the new systems
        self.class_selection_ui = ClassSelectionUI(self, self.on_class_selected)
        self.skill_tree_ui = SkillTreeUI(self, self.player, self.player.skill_tree)
        
        # Show class selection at start
        self.taskMgr.doMethodLater(0.5, lambda task: self.class_selection_ui.show(), "ShowClassSelection")
        
        # Create ground plane (temporary)
        try:
            # Try to load plane model first
            ground = self.loader.loadModel("models/plane")
        except:
            # Fallback to box model if plane isn't available
            print("Plane model not found, using box model for ground instead")
            ground = self.loader.loadModel("models/box")
            ground.setScale(100, 100, 0.1)  # Make it flat like a plane
        
        ground.setColor(0.3, 0.6, 0.3, 1)  # Green color
        ground.reparentTo(self.render)
        
        # Example physics entity (player)
        if hasattr(self, 'player') and hasattr(self, 'physics_manager'):
            self.physics_manager.register_physics_entity(
                "player", 
                self.player.get_position(), 
                0.5,  # Radius
                1.0   # Mass
            )
            
            # Create character rig for player
            player_rig = self.physics_manager.create_character_rig("player", 2.0)
            
            # Example cloth (flag or cape)
            if self.render:
                flag_position = Vec3(5, 0, 3)  # Some position in the world
                self.physics_manager.create_cloth(
                    flag_position, 
                    2.0,   # Width
                    1.5,   # Height
                    self.render,
                    None,  # No texture for now
                    "flag"
                )
    
    def update(self, task):
        """Main game update loop"""
        # Get time elapsed since last frame
        dt = globalClock.getDt()
        
        # Skip updates if paused
        if self.paused:
            return task.cont
        
        try:
            # Update game systems
            if hasattr(self, 'day_night_cycle'):
                self.day_night_cycle.update(dt)
                
                # Manually update shader time of day if needed
                if hasattr(self, 'filter_manager') and hasattr(self, '_last_time_of_day') and \
                   not hasattr(self.day_night_cycle, 'add_time_changed_callback'):
                    # Get current time of day - check which method is available
                    current_time = 0.5  # Default to midday
                    if hasattr(self.day_night_cycle, 'get_time_of_day'):
                        time_value = self.day_night_cycle.get_time_of_day()
                        # Ensure it's a numeric value
                        current_time = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    elif hasattr(self.day_night_cycle, 'getTimeOfDay'):
                        time_value = self.day_night_cycle.getTimeOfDay()
                        # Ensure it's a numeric value
                        current_time = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    elif hasattr(self.day_night_cycle, 'time_of_day'):
                        time_value = self.day_night_cycle.time_of_day
                        # Ensure it's a numeric value
                        current_time = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    
                    # Only update if changed significantly
                    if abs(current_time - self._last_time_of_day) > 0.01:
                        self.update_shader_time_of_day(current_time)
                        self._last_time_of_day = current_time
            
            if hasattr(self, 'entity_manager'):
                self.entity_manager.update(dt)
                
            if hasattr(self, 'adaptive_difficulty'):
                self.adaptive_difficulty.update(dt)
                
            if hasattr(self, 'audio_manager'):
                self.audio_manager.update(dt)
                
            if hasattr(self, 'random_event_system'):
                self.random_event_system.update(dt)
                
            if hasattr(self, 'physics_manager'):
                self.physics_manager.update(dt)
                
            if hasattr(self, 'night_fog') and self.night_fog.enabled:
                # Check if it's night time
                if hasattr(self, 'day_night_cycle'):
                    # Get current time of day - check which method is available
                    time_of_day = 0.5  # Default to midday
                    if hasattr(self.day_night_cycle, 'get_time_of_day'):
                        time_value = self.day_night_cycle.get_time_of_day()
                        # Ensure it's a numeric value
                        time_of_day = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    elif hasattr(self.day_night_cycle, 'getTimeOfDay'):
                        time_value = self.day_night_cycle.getTimeOfDay()
                        # Ensure it's a numeric value
                        time_of_day = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    elif hasattr(self.day_night_cycle, 'time_of_day'):
                        time_value = self.day_night_cycle.time_of_day
                        # Ensure it's a numeric value
                        time_of_day = float(time_value) if isinstance(time_value, (int, float)) else 0.5
                    
                    # Night is roughly from 0.7 to 0.3 (wrapping around midnight)
                    is_night = time_of_day > 0.7 or time_of_day < 0.3
                    
                    # Update fog intensity based on time of day
                    if is_night:
                        # Calculate how deep into the night we are (0-1)
                        if time_of_day > 0.7:
                            night_progress = (time_of_day - 0.7) / 0.3
                        else:
                            night_progress = 1.0 - (time_of_day / 0.3)
                            
                        self.night_fog.set_intensity(night_progress * 0.7 + 0.3)
                    else:
                        self.night_fog.set_intensity(0.0)
                
                self.night_fog.update(dt)
            
            # Player updates
            if hasattr(self, 'player') and self.player is not None:
                self.player.update(dt)
            
            # Camera updates
            self.update_camera()
            
            # UI updates
            self.update_ui()
        
        except Exception as e:
            print(f"Error in update loop: {e}")
        
        return task.cont
    
    def update_camera(self):
        """Update camera position to follow player"""
        # Set the camera to follow the player with a fixed offset
        if hasattr(self, 'player'):
            camera_height = 15
            camera_distance = 20
            
            # Calculate camera position
            camera_pos = self.player.position + LVector3f(0, -camera_distance, camera_height)
            self.camera.setPos(camera_pos)
            
            # Look at player
            self.camera.lookAt(self.player.position)
    
    def update_ui(self):
        """Update UI elements"""
        if hasattr(self, 'player'):
            # Update health display
            self.health_text.setText(f"Health: {self.player.health}/{self.player.max_health}")
            
            # Update experience display
            self.exp_text.setText(
                f"Level: {self.player.level} | XP: {self.player.experience}/{self.player.experience_to_next_level}"
            )
            
            # Update inventory display
            self.inventory_text.setText(self.player.get_inventory_string())
            
            # Update skill points display
            self.skill_points_text.setText(f"Skill Points: {self.player.skill_points}")
        
        # Update time display
        if hasattr(self, 'day_night_cycle'):
            # Use day 1 as default if current_day isn't available
            day = getattr(self.day_night_cycle, 'current_day', 1)
            
            # Check if time_of_day is a number
            if hasattr(self.day_night_cycle, 'current_time') and isinstance(self.day_night_cycle.current_time, (int, float)):
                time_value = self.day_night_cycle.current_time
                hour = int(time_value * 24)
                minute = int((time_value * 24 * 60) % 60)
                time_str = f"{hour:02d}:{minute:02d}"
            else:
                # Get current time string from the day/night cycle
                time_str = getattr(self.day_night_cycle, 'current_time_name', "00:00")
            
            self.time_text.setText(f"Time: Day {day}, {time_str}")
        
        # Update FPS display
        if self.show_fps:
            fps = round(globalClock.getAverageFrameRate(), 1)
            self.fps_text.setText(f"FPS: {fps}")
    
    def set_player_moving(self, is_pressed, direction):
        """Set player movement state"""
        if hasattr(self, 'player'):
            self.player.set_moving(is_pressed, direction)
    
    def player_primary_attack(self):
        """Handle player primary attack input"""
        if hasattr(self, 'player') and not self.paused:
            self.player.perform_primary_attack()
            # Play attack sound
            if hasattr(self, 'audio_manager'):
                self.audio_manager.play_combat_sound("swing", 1.0, self.player.get_position())
    
    def player_secondary_attack(self):
        """Handle player secondary attack input"""
        if hasattr(self, 'player') and not self.paused:
            self.player.perform_secondary_attack()
            # Play attack sound
            if hasattr(self, 'audio_manager'):
                self.audio_manager.play_combat_sound("magic", 1.0, self.player.get_position())
    
    def player_dodge(self):
        """Handle player dodge input"""
        if hasattr(self, 'player') and not self.paused:
            self.player.dodge()
    
    def player_interact(self):
        """Handle player interact input"""
        if hasattr(self, 'player') and not self.paused:
            self.player.interact()
    
    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        
        # Play UI sound
        if hasattr(self, 'audio_manager'):
            self.audio_manager.play_sound("ui_toggle", 1.0, False, None, "ui")
        
        # Toggle physics debug visualization
        if hasattr(self, 'physics_manager'):
            if self.debug_mode:
                self.physics_manager.enable_debug_visualization(self.render)
            self.physics_manager.show_debug = self.debug_mode
        
        print(f"Debug mode: {self.debug_mode}")
    
    def toggle_skill_tree(self):
        """Toggle skill tree UI"""
        if hasattr(self, 'skill_tree_ui'):
            # Only show if player has a class
            if hasattr(self.player, 'character_class') and self.player.character_class:
                if self.skill_tree_ui.root_frame.isHidden():
                    self.skill_tree_ui.show()
                else:
                    self.skill_tree_ui.hide()
            else:
                print("You must select a class first!")
    
    def toggle_pause(self):
        """Toggle game pause"""
        self.set_paused(not self.paused)
    
    def set_paused(self, paused):
        """Set game pause state"""
        self.paused = paused
        
        # Show pause indicator if paused
        if hasattr(self, 'pause_text'):
            if paused:
                self.pause_text.show()
            else:
                self.pause_text.hide()
        else:
            # Create pause text if it doesn't exist
            if paused:
                self.pause_text = OnscreenText(
                    text="PAUSED", 
                    pos=(0, 0), 
                    scale=0.1,
                    fg=(1, 1, 1, 1),
                    shadow=(0, 0, 0, 0.5)
                )
            else:
                self.pause_text = OnscreenText(
                    text="PAUSED", 
                    pos=(0, 0), 
                    scale=0.1,
                    fg=(1, 1, 1, 1),
                    shadow=(0, 0, 0, 0.5)
                )
                self.pause_text.hide()
    
    def on_class_selected(self, class_type):
        """Handle class selection"""
        if hasattr(self, 'player'):
            success = self.player.set_class(class_type)
            
            if success:
                print(f"You have chosen the {class_type.value} class!")
                
                # Grant initial resources
                self.player.inventory["monster_essence"] = 20
                
                # Update UI
                self.player.show_current_ability()
    
    def give_skill_point(self):
        """Debug function to give a skill point"""
        if hasattr(self, 'player'):
            self.player.skill_points += 1
            print(f"Skill point added! Total: {self.player.skill_points}")
    
    def give_monster_essence(self):
        """Debug function to give monster essence"""
        if hasattr(self, 'player'):
            self.player.inventory["monster_essence"] = self.player.inventory.get("monster_essence", 0) + 50
            print(f"Added 50 monster essence! Total: {self.player.inventory.get('monster_essence', 0)}")
    
    def toggle_night_fog(self):
        """Toggle the night fog effect on/off"""
        if not hasattr(self, 'night_fog') or self.night_fog is None:
            # Create night fog effect
            self.night_fog = NightFog(self)
            self.night_fog.enable()
            print("Night fog enabled")
        else:
            # Toggle existing night fog
            if self.night_fog.enabled:
                self.night_fog.disable()
                print("Night fog disabled")
            else:
                self.night_fog.enable()
                print("Night fog enabled")
                
    def setup_enhanced_visuals(self):
        """Set up enhanced visual effects for the Octopath Traveler style"""
        try:
            from panda3d.core import Shader, NodePath, CardMaker, AntialiasAttrib
            
            # Enable antialiasing
            self.render.setAntialias(AntialiasAttrib.MAuto)
            
            # Initialize the renderer if not done yet
            if not hasattr(self, 'renderer'):
                from src.engine.renderer import Renderer
                self.renderer = Renderer(self)
            
            # Set up the shader pipeline
            self.setup_shader_pipeline()
            
            # Set time of day for shaders
            self.update_shader_time_of_day(0.25)  # Start at day time
            
            print("Enhanced visuals set up successfully!")
        except Exception as e:
            print(f"Error setting up enhanced visuals: {e}")
            import traceback
            traceback.print_exc()

    def setup_shader_pipeline(self):
        """Set up the shader pipeline for post-processing effects"""
        try:
            # Create a framebuffer for the main scene
            window_props = self.win.getProperties()
            buffer_size = (window_props.getXSize(), window_props.getYSize())
            
            # Create a TextureStage for the scene buffer
            from panda3d.core import GraphicsOutput, Texture, GraphicsBuffer
            from panda3d.core import FrameBufferProperties, WindowProperties
            
            fb_props = FrameBufferProperties()
            fb_props.setRgbColor(True)
            fb_props.setAlphaBits(1)
            fb_props.setDepthBits(1)
            
            # Create and set up the scene buffer
            self.scene_buffer = self.win.makeTextureBuffer("scene_buffer", buffer_size[0], buffer_size[1])
            self.scene_buffer.setClearColor((0, 0, 0, 1))
            
            # Create a camera for the scene buffer
            self.scene_camera = self.makeCamera(self.scene_buffer)
            self.scene_camera.node().setLens(self.cam.node().getLens())
            
            # Reparent the original camera and make it follow the scene camera
            self.cam.reparentTo(self.scene_camera)
            
            # Create textures for effects
            self.scene_tex = Texture()
            self.scene_buffer.addRenderTexture(self.scene_tex, GraphicsOutput.RTMCopyRam)
            
            # Create a quad for displaying the final result
            cm = CardMaker("display_quad")
            cm.setFrameFullscreenQuad()
            self.display_quad = self.render2d.attachNewNode(cm.generate())
            
            # Set the scene texture to be displayed
            self.display_quad.setTexture(self.scene_tex)
            
            # Set up shader inputs to link the renderer's post-processing chain
            if hasattr(self, 'renderer'):
                self.renderer.diorama_quad.setShaderInput("scene_texture", self.scene_tex)
                
                # Apply proper ordering of effects
                self.renderer.diorama_quad.setBin("fixed", 10)
                self.renderer.tilt_shift_quad.setBin("fixed", 20)
                self.renderer.color_grading_quad.setBin("fixed", 30)
                
                # Connect shaders in sequence
                if hasattr(self.renderer, 'diorama_quad') and hasattr(self.renderer, 'tilt_shift_quad'):
                    # Create intermediate textures if needed
                    self.diorama_result_tex = Texture()
                    # Set up connections between shader stages
                    self.renderer.tilt_shift_quad.setShaderInput("p3d_Texture0", self.diorama_result_tex)
            
            print("Shader pipeline set up successfully")
        except Exception as e:
            print(f"Error setting up shader pipeline: {e}")
            import traceback
            traceback.print_exc()

    def update_shader_time_of_day(self, time_of_day):
        """
        Update the shader parameters for time of day
        
        Args:
            time_of_day: Value from 0.0 (dawn) to 1.0 (midnight)
        """
        if hasattr(self, 'renderer') and hasattr(self.renderer, 'color_grading_quad'):
            # Calculate day/night blend for shader
            day_night_blend = 0.0
            
            # Map time_of_day to appropriate blend values
            # 0.0-0.25 (dawn to day): 0.0
            # 0.25-0.5 (day to dusk): 0.0-0.3
            # 0.5-0.75 (dusk to night): 0.3-0.8
            # 0.75-1.0 (night to midnight): 0.8-1.0
            
            if time_of_day <= 0.25:
                day_night_blend = 0.0
            elif time_of_day <= 0.5:
                t = (time_of_day - 0.25) / 0.25
                day_night_blend = t * 0.3
            elif time_of_day <= 0.75:
                t = (time_of_day - 0.5) / 0.25
                day_night_blend = 0.3 + t * 0.5
            else:
                t = (time_of_day - 0.75) / 0.25
                day_night_blend = 0.8 + t * 0.2
            
            # Update shader parameters
            self.renderer.color_grading_quad.setShaderInput("day_night_blend", day_night_blend)
            
            # Adjust color tints based on time
            if time_of_day < 0.25:  # Dawn
                day_tint = (1.0, 0.9, 0.8)
            elif time_of_day < 0.5:  # Day
                day_tint = (1.0, 1.0, 1.0)
            else:  # Dusk or later
                day_tint = (1.0, 0.8, 0.7)
                
            if time_of_day < 0.75:  # Night
                night_tint = (0.6, 0.7, 0.9)
            else:  # Midnight
                night_tint = (0.4, 0.5, 0.8)
                
            # Set the tint values
            self.renderer.color_grading_quad.setShaderInput("day_tint", day_tint)
            self.renderer.color_grading_quad.setShaderInput("night_tint", night_tint)
            
            # Adjust other visual parameters based on time
            contrast = 1.1
            saturation = 1.0
            brightness = 1.0
            
            if time_of_day >= 0.75:  # Night to midnight
                contrast = 1.2
                saturation = 0.9
                brightness = 0.9
            
            self.renderer.color_grading_quad.setShaderInput("contrast", contrast)
            self.renderer.color_grading_quad.setShaderInput("saturation", saturation)
            self.renderer.color_grading_quad.setShaderInput("brightness", brightness)


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Nightfall Defenders')
    parser.add_argument('--enable-enhanced-audio', action='store_true', 
                        help='Enable enhanced audio system with 3D positional audio')
    parser.add_argument('--enable-enhanced-visuals', action='store_true',
                        help='Enable enhanced visual effects (shaders, etc.)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--adaptive-difficulty', action='store_true',
                        help='Enable adaptive difficulty system')
    parser.add_argument('--night-fog', action='store_true',
                        help='Enable night fog effect')
    args = parser.parse_args()
    
    # Create and start the game
    app = NightfallDefendersGame()
    
    # Apply command line options
    if args.debug:
        app.debug_mode = True
        print("Debug mode enabled")
    
    if args.adaptive_difficulty:
        app.adaptive_difficulty.enabled = True
        print("Adaptive difficulty enabled")
    
    if args.night_fog:
        app.toggle_night_fog()
        print("Night fog enabled")
        
    if args.enable_enhanced_audio:
        # Configure audio system with enhanced features
        app.audio_manager.load_config()  # Load from our JSON config
        print("Enhanced audio system enabled")
        
    if args.enable_enhanced_visuals:
        # Enable enhanced shader effects
        print("Enhanced visual effects enabled")
        # Set up enhanced shaders with better parameters
        app.setup_enhanced_visuals()
    
    app.run()


if __name__ == "__main__":
    main() 