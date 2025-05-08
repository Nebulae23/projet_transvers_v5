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
    AntialiasAttrib, TransparencyAttrib, Vec3, Shader, ShaderAttrib, Texture,
    AmbientLight, DirectionalLight, CardMaker
)

# Import game modules
from game.player import Player
from game.day_night_cycle import DayNightCycle
from game.entity_manager import EntityManager
from game.adaptive_difficulty import AdaptiveDifficultySystem
from game.audio_manager import AudioManager
from game.main_menu import MainMenuScene
from game.pause_menu import PauseMenu

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

# Import UI components
from engine.ui.info_box import InfoBoxUI
from engine.ui.notification import NotificationSystem

class NightfallDefendersGame(ShowBase):
    """Main game class for Nightfall Defenders"""
    
    def __init__(self):
        """Initialize the game"""
        ShowBase.__init__(self)
        
        # Game settings
        self.debug_mode = False
        self.paused = False
        self.show_fps = True
        self.game_started = False
        
        # Setup window properties
        self.setup_window()
        
        # Set up the camera
        self.setup_camera()
        
        # Initialize game systems
        self.setup_game_systems()
        
        # Key bindings
        self.setup_keys()
        
        # Create UI elements (only when game starts)
        self.ui_initialized = False
        
        # Main menu - create it first and show it
        self.main_menu = MainMenuScene(self)
        
        # Start the game loop
        self.taskMgr.add(self.update, "GameUpdateTask")
        
        print("Nightfall Defenders initialized in menu mode!")
    
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
        if self.ui_initialized:
            return
            
        # Player stats box
        self.player_stats_box = InfoBoxUI(
            self, 
            "Player Status", 
            (-1.3, 0.9), 
            (0.5, 0.3),
            expanded=True
        )
        self.player_stats_box.add_text_row("Health", "100/100")
        self.player_stats_box.add_text_row("Level", "1")
        self.player_stats_box.add_text_row("XP", "0/100")
        self.player_stats_box.add_text_row("Skill Points", "0")
        
        # Current ability box
        self.ability_box = InfoBoxUI(
            self, 
            "Current Ability", 
            (-1.3, 0.5), 
            (0.5, 0.2),
            expanded=True
        )
        self.ability_box.add_text_row("Primary", "None")
        self.ability_box.add_text_row("Secondary", "None")
        
        # Inventory box (initially collapsed)
        self.inventory_box = InfoBoxUI(
            self, 
            "Inventory", 
            (-1.3, 0.15), 
            (0.5, 0.4),
            expanded=False
        )
        
        # Game info box (time, etc.)
        self.game_info_box = InfoBoxUI(
            self, 
            "Game Info", 
            (1.3, 0.9), 
            (0.5, 0.3),
            expanded=True
        )
        self.game_info_box.add_text_row("Time", "Day 1, 00:00")
        self.game_info_box.add_text_row("Time of Day", "Day")
        self.game_info_box.add_text_row("FPS", "0")
        
        # Skill tree button
        self.skill_tree_button = DirectButton(
            text="Skill Tree",
            scale=0.05,
            pos=(1.15, 0, 0.5),
            command=self.toggle_skill_tree,
            frameColor=(0.2, 0.2, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT
        )
        
        # Create experience bar
        self.create_exp_bar()
        
        self.ui_initialized = True
    
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
        
        # Hide initially until game starts
        self.exp_bar_bg.hide()
        self.exp_bar_fg.hide()
    
    def update_exp_bar(self):
        """Update the experience bar display"""
        if not self.game_started:
            return
            
        if hasattr(self, 'player') and self.player is not None:
            # Get experience percentage
            exp_percent = self.player.get_experience_percent()
            
            # Update bar width
            width = 1.0 * exp_percent
            self.exp_bar_fg["frameSize"] = (-0.5, -0.5 + width, -0.02, 0.02)
            
            # Show exp bar if hidden
            if not self.exp_bar_bg.isShown():
                self.exp_bar_bg.show()
                self.exp_bar_fg.show()
        else:
            # No player, set to zero
            self.exp_bar_fg["frameSize"] = (-0.5, -0.5, -0.02, 0.02)
    
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
        
        # UI systems
        self.notification_system = NotificationSystem(self)
        self.pause_menu = PauseMenu(self)
    
    def setup_keys(self):
        """Set up key bindings"""
        # Movement keys - these will only work after game starts
        self.accept("w", self.set_player_moving, [True, 0])  # Forward
        self.accept("w-up", self.set_player_moving, [False, 0])
        self.accept("s", self.set_player_moving, [True, 1])  # Backward
        self.accept("s-up", self.set_player_moving, [False, 1])
        self.accept("a", self.set_player_moving, [True, 2])  # Left
        self.accept("a-up", self.set_player_moving, [False, 2])
        self.accept("d", self.set_player_moving, [True, 3])  # Right
        self.accept("d-up", self.set_player_moving, [False, 3])
        
        # Action keys - these will only work after game starts
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
        """Create initial game world"""
        if not self.game_started:
            # Don't create world until game starts
            return
            
        # Create UI elements if not already created
        if not self.ui_initialized:
            self.create_ui()
        
        print("Creating game world...")
        
        # Set up terrain
        self.create_terrain()
        
        # Set up lighting
        self.setup_lighting()
        
        # Create player character
        self.create_player()
        
        # Initialize player character
        self.player.initialize()
        
        # Play ambience
        self.audio_manager.play_sound("ambient_birds_morning", loop=True, category="ambient")
        
        # Show the experience bar
        if hasattr(self, 'exp_bar_bg'):
            self.exp_bar_bg.show()
            self.exp_bar_fg.show()
            
        # Display start notification
        if hasattr(self, 'notification_system'):
            self.notification_system.show_notification("Welcome to Nightfall Defenders", "success")
    
    def update(self, task):
        """
        Main game update loop
        
        Args:
            task: Task object from Panda3D task manager
            
        Returns:
            Task.cont to continue the task
        """
        # Calculate delta time since last frame
        dt = globalClock.getDt()
        
        # Update time of day
        if self.game_started and hasattr(self, 'day_night_cycle'):
            self.day_night_cycle.update(dt)
        
        # Update audio
        if hasattr(self, 'audio_manager'):
            self.audio_manager.update(dt)
        
        # If game is paused, don't update gameplay systems
        if self.paused or not self.game_started:
            # Still update UI
            if self.game_started:
                self.update_ui()
            return task.cont
        
        # Update physics
        if hasattr(self, 'physics_manager'):
            self.physics_manager.update(dt)
        
        # Update entities
        if hasattr(self, 'entity_manager'):
            self.entity_manager.update(dt)
        
        # Update player
        if hasattr(self, 'player'):
            self.player.update(dt)
        
        # Update camera
        self.update_camera()
        
        # Update UI
        self.update_ui()
        
        # Update random events
        if hasattr(self, 'random_event_system'):
            self.random_event_system.update(dt)
        
        # Update night fog if enabled
        if hasattr(self, 'night_fog') and self.night_fog.enabled:
            self.night_fog.update(dt)
        
        # Update adaptive difficulty
        if hasattr(self, 'adaptive_difficulty') and self.adaptive_difficulty.enabled:
            self.adaptive_difficulty.update(dt)
            
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
        if hasattr(self, 'player') and self.player is not None:
            # Update health display
            self.player_stats_box.update_value(0, f"{self.player.health}/{self.player.max_health}")
            
            # Update level display
            self.player_stats_box.update_value(1, str(self.player.level))
            
            # Update experience display
            self.player_stats_box.update_value(2, f"{self.player.experience}/{self.player.experience_to_next_level}")
            
            # Update skill points display
            self.player_stats_box.update_value(3, str(self.player.skill_points))
            
            # Update inventory box
            if hasattr(self.player, 'get_inventory_string'):
                inventory_string = self.player.get_inventory_string()
                # Clear the inventory box
                self.inventory_box.clear()
                
                # Add items to inventory box
                if hasattr(self.player, 'inventory') and isinstance(self.player.inventory, dict):
                    for i, (item, amount) in enumerate(self.player.inventory.items()):
                        if amount > 0:
                            self.inventory_box.add_text_row(item.replace('_', ' ').title(), str(amount))
            
            # Update ability info
            if hasattr(self.player, 'current_primary_ability'):
                primary = getattr(self.player, 'current_primary_ability', "None")
                self.ability_box.update_value(0, primary)
                
            if hasattr(self.player, 'current_secondary_ability'):
                secondary = getattr(self.player, 'current_secondary_ability', "None")
                self.ability_box.update_value(1, secondary)
            
            # Update experience bar
            self.update_exp_bar()
        else:
            # Default values when no player exists
            self.player_stats_box.update_value(0, "N/A")
            self.player_stats_box.update_value(1, "N/A")
            self.player_stats_box.update_value(2, "N/A")
            self.player_stats_box.update_value(3, "N/A")
            self.ability_box.update_value(0, "None")
            self.ability_box.update_value(1, "None")
        
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
            
            self.game_info_box.update_value(0, f"Day {day}, {time_str}")
            
            # Update time of day
            if hasattr(self.day_night_cycle, 'time_of_day'):
                time_of_day = self.day_night_cycle.time_of_day
                self.game_info_box.update_value(1, str(time_of_day))
        
        # Update FPS display
        if self.show_fps:
            fps = round(globalClock.getAverageFrameRate(), 1)
            self.game_info_box.update_value(2, str(fps))
    
    def set_player_moving(self, is_pressed, direction):
        """Set player movement direction"""
        if not self.game_started or not hasattr(self, 'player'):
            return
        self.player.set_moving(is_pressed, direction)
    
    def player_primary_attack(self):
        """Trigger player's primary attack"""
        if not self.game_started or not hasattr(self, 'player'):
            return
        self.player.primary_attack()
    
    def player_secondary_attack(self):
        """Trigger player's secondary attack"""
        if not self.game_started or not hasattr(self, 'player'):
            return
        self.player.secondary_attack()
    
    def player_dodge(self):
        """Trigger player's dodge maneuver"""
        if not self.game_started or not hasattr(self, 'player'):
            return
        self.player.dodge()
    
    def player_interact(self):
        """Player interaction with the world"""
        if not self.game_started or not hasattr(self, 'player'):
            return
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
        # Check if player exists
        if not hasattr(self, 'player') or self.player is None:
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("You must select a class first!", duration=2.0, type="error")
            else:
                print("You must select a class first!")
            return
            
        if hasattr(self, 'skill_tree_ui'):
            # Only show if player has a class
            if hasattr(self.player, 'character_class') and self.player.character_class:
                if self.skill_tree_ui.root_frame.isHidden():
                    self.skill_tree_ui.show()
                else:
                    self.skill_tree_ui.hide()
            else:
                if hasattr(self, 'notification_system'):
                    self.notification_system.add_notification("You must select a class first!", duration=2.0, type="error")
                else:
                    print("You must select a class first!")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.set_paused(self.paused)
    
    def set_paused(self, paused):
        """
        Set the pause state
        
        Args:
            paused: Whether to pause the game
        """
        self.paused = paused
        
        # Show/hide pause menu
        if hasattr(self, 'pause_menu'):
            if self.paused:
                self.pause_menu.show()
            else:
                self.pause_menu.hide()
        
        if self.paused:
            # Disable controls when paused
            self.disable_controls()
            
            # Notify with text or sound
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Game Paused", duration=1.0, type="info")
        else:
            # Re-enable controls when unpaused
            self.enable_controls()
            
            # Notify with text or sound
            if hasattr(self, 'notification_system'):
                self.notification_system.add_notification("Game Resumed", duration=1.0, type="info")
    
    def disable_controls(self):
        """Disable player controls"""
        self.ignore("w")
        self.ignore("s")
        self.ignore("a")
        self.ignore("d")
        self.ignore("mouse1")
        self.ignore("mouse3")
        self.ignore("space")
        self.ignore("e")
    
    def enable_controls(self):
        """Re-enable player controls"""
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
        self.accept("mouse1", self.player_primary_attack)  # Primary attack
        self.accept("mouse3", self.player_secondary_attack)  # Secondary attack
        self.accept("space", self.player_dodge)  # Dodge
        self.accept("e", self.player_interact)  # Interact
    
    def on_class_selected(self, class_type):
        """
        Handle class selection
        
        Args:
            class_type: The selected character class
        """
        print(f"Selected class: {class_type}")
        
        # Close class selection UI if it exists
        if hasattr(self, 'class_selection_ui'):
            self.class_selection_ui.hide()
        
        # Set player class
        self.selected_class = class_type
        
        # Now create the world
        if not hasattr(self, 'player'):
            # First create UI elements if not already done
            if not self.ui_initialized:
                self.create_ui()
            
            # Initialize skill tree UI
            self.skill_tree_ui = SkillTreeUI(self, None, None)  # Will be properly initialized when player is created
            
            # Create the game world
            self.create_world()
            
            # Show notification
            if hasattr(self, 'notification_system'):
                self.notification_system.show_notification(f"You begin your journey as a {class_type}", "info", 3.0)
    
    def start_new_game(self):
        """Start a new game"""
        print("Starting new game!")
        
        # Hide main menu
        self.main_menu.hide()
        
        # Set game_started flag
        self.game_started = True
        
        # Open class selection UI
        from game.class_selection_ui import ClassSelectionUI
        self.class_selection_ui = ClassSelectionUI(self, self.on_class_selected)
        
        # Or create the world immediately (uncomment if you want to skip class selection)
        # self.create_world()
    
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

    def create_player(self):
        """Create the player after class selection"""
        # Create the player
        self.player = Player(self)
        self.player.position = LVector3f(0, 0, 0)
        
        # Set player class based on selection
        if hasattr(self, 'selected_class'):
            self.player.set_class(self.selected_class)
            
            # Grant initial resources
            self.player.inventory["monster_essence"] = 20
            
            # Update UI
            self.player.show_current_ability()
        
        # Initialize the skill tree UI with the player instance
        if hasattr(self, 'skill_tree_ui'):
            self.skill_tree_ui.player = self.player
            self.skill_tree_ui.skill_tree = self.player.skill_tree
        
        # Set up physics for the player
        if hasattr(self, 'physics_manager'):
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

    def create_terrain(self):
        """Create the game terrain"""
        # Create ground plane
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
        
        # Add some decoration to the terrain (trees, rocks, etc.)
        self.add_environment_objects()
    
    def add_environment_objects(self):
        """Add decorative objects to the environment"""
        # Add some trees
        try:
            for i in range(20):
                x = random.uniform(-50, 50)
                y = random.uniform(-50, 50)
                
                # Don't place trees too close to the player start position
                if abs(x) < 10 and abs(y) < 10:
                    continue
                    
                tree = self.loader.loadModel("models/tree")
                tree.setPos(x, y, 0)
                tree.setScale(random.uniform(0.8, 1.2))
                tree.reparentTo(self.render)
        except:
            print("Tree models not available, skipping environment decoration")
    
    def setup_lighting(self):
        """Set up scene lighting"""
        # Create ambient light
        ambient_light = self.render.attachNewNode(AmbientLight("ambientLight"))
        ambient_light.node().setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(ambient_light)
        
        # Create directional light (sun/moon)
        directional_light = self.render.attachNewNode(DirectionalLight("directionalLight"))
        directional_light.node().setColor((0.8, 0.8, 0.7, 1))
        directional_light.node().setShadowCaster(True, 512, 512)
        directional_light.setHpr(60, -60, 0)
        self.render.setLight(directional_light)
        
        # Store lights for day/night cycle
        self.lights = {
            "ambient": ambient_light,
            "directional": directional_light
        }
        
        # Connect to day/night cycle
        if hasattr(self, 'day_night_cycle'):
            self.day_night_cycle.set_lights(self.lights)


def main():
    """Main entry point"""
    # Check for missing essential assets
    main_menu_bg_path = os.path.join("src", "assets", "generated", "ui", "main_menu_bg.png")
    if not os.path.exists(main_menu_bg_path):
        print("Main menu background not found. Generating missing assets...")
        try:
            import subprocess
            subprocess.call([sys.executable, "fix_missing_assets.py"])
        except Exception as e:
            print(f"Error generating assets: {e}")
    
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