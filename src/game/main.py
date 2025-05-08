#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Main Game Module
Implements the core game loop and initializes game systems
"""

import os
import sys
import argparse
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties, Vec3, ConfigVariableBool

from game.character_class import ClassManager

# Ensure the src directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import engine modules
from engine.config import GameConfig
from engine.resource_manager import ResourceManager
from engine.renderer import Renderer
from engine.input_manager import InputManager
from engine.scene_manager import SceneManager
from engine.save_manager import SaveManager
from engine.ui.ui_manager import UIManager

# Import game modules
from game.day_night_cycle import DayNightCycle, TimeOfDay
from game.camera_controller import CameraController
from game.entity_manager import EntityManager
from game.crafting_system import CraftingSystem
from game.crafting_ui import CraftingUI
from game.relic_system import RelicSystem
from game.relic_ui import RelicUI
from game.building_system import BuildingSystem
from game.building_ui import BuildingUI
from game.city_manager import CityManager
from game.night_fog import NightFog
from game.adaptive_difficulty import AdaptiveDifficultySystem, DifficultyPreset
from game.performance_tracker import PerformanceTracker
from game.difficulty_settings import DifficultySettings
from game.class_selection_ui import ClassSelectionUI
from game.secondary_abilities import SecondaryAbilityManager

class NightfallDefenders(ShowBase):
    """Main game class that extends Panda3D's ShowBase"""
    
    def __init__(self, enable_adaptive_difficulty=False):
        """
        Initialize the game
        
        Args:
            enable_adaptive_difficulty: Whether to enable adaptive difficulty system
        """
        # Configure Panda3D settings first
        self._configure_panda3d()
        
        # Initialize ShowBase
        super().__init__()
        
        # Load our custom game configuration
        self.game_config = GameConfig()
        
        # Set up window properties
        self._setup_window()
        
        # Initialize game systems
        self.resource_manager = ResourceManager(self)
        self.input_manager = InputManager(self)
        self.scene_manager = SceneManager(self)
        self.renderer = Renderer(self)
        
        # Add the UI Manager
        self.ui_manager = UIManager(self)
        
        # Add the Save Manager
        self.save_manager = SaveManager(self)
        
        # Initialize game-specific systems
        self.game_time = 0
        self.entity_manager = EntityManager(self)
        self.day_night_cycle = DayNightCycle(self)
        self.camera_controller = CameraController(self)
        
        # Initialize the class system
        self.class_manager = ClassManager()
        
        # Create player
        self.player = None
        self.entity_manager.create_player()
        
        # Create the crafting system
        self.crafting_system = CraftingSystem(self)
        self.crafting_ui = CraftingUI(self)
        
        # Create the relic system
        self.relic_system = RelicSystem(self)
        self.relic_ui = RelicUI(self)
        
        # Create the city management system
        self.city_manager = CityManager(self)
        self.building_system = BuildingSystem(self)
        self.building_ui = BuildingUI(self)
        
        # Create the night fog system
        self.night_fog = NightFog(self)
        
        # Create the class selection UI
        self.class_selection_ui = ClassSelectionUI(self)
        
        # Create secondary abilities system
        # The secondary ability manager will be initialized when the player is created
        
        # Create the adaptive difficulty system if enabled
        if enable_adaptive_difficulty:
            self.adaptive_difficulty_system = AdaptiveDifficultySystem(self)
            self.performance_tracker = PerformanceTracker(self)
            self.difficulty_settings = DifficultySettings(self)
            print("Adaptive Difficulty System enabled.")
        
        # Track play time
        self.play_time = 0
        
        # Set up the game world
        self._setup_world()
        
        # Populate the world with resources
        self._populate_world()
        
        # Set up key bindings
        self._setup_key_bindings()
        
        # Initialize UI components
        self._setup_ui()
        
        # Initial game state
        self.paused = False
        self.debug_mode = False
        
        # Debug settings
        self.debug_display_enabled = False
        
        # Register our custom scenes
        self._register_scenes()
        
        # Add the update task
        self.task_mgr.add(self._update, "update_task")
        
        # Show controls help
        self.setup_help_text()
        
        # Start with the main menu
        self.scene_manager.change_scene("main_menu")
        
        # Print startup message
        print("Nightfall Defenders initialized successfully!")
    
    def _configure_panda3d(self):
        """Configure Panda3D engine settings"""
        # Set up basic Panda3D configuration
        loadPrcFileData("", "window-title Nightfall Defenders")
        loadPrcFileData("", "win-size 1280 720")
        loadPrcFileData("", "fullscreen 0")
        loadPrcFileData("", "sync-video 1")
        loadPrcFileData("", "texture-anisotropic-degree 16")
        loadPrcFileData("", "texture-minfilter linear-mipmap-linear")
        loadPrcFileData("", "texture-magfilter linear")
        loadPrcFileData("", "model-cache-dir cache")
        loadPrcFileData("", "audio-library-name p3openal_audio")
    
    def _setup_window(self):
        """Set up the game window properties"""
        # Get window properties and configure
        wp = WindowProperties()
        wp.setTitle("Nightfall Defenders")
        wp.setIconFilename("src/assets/generated/ui/icon.png")
        wp.setCursorHidden(False)
        self.win.requestProperties(wp)
    
    def _setup_key_bindings(self):
        """Set up keyboard and mouse bindings"""
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
        self.accept("space", self.player.dodge)
        self.accept("mouse1", self.player.primary_attack)
        self.accept("mouse3", self.player.secondary_attack)
        self.accept("e", self.player.interact)
        
        # Game controls
        self.accept("escape", self.cleanup_and_exit)
        self.accept("f1", self.toggle_debug_display)
        self.accept("t", self.toggle_day_night)  # Toggle day/night cycle
        self.accept("f", self.toggle_fog)  # Toggle fog (debug)
        
        # UI controls
        self.accept("c", self.toggle_crafting_ui)
        self.accept("r", self.toggle_relic_ui)
        self.accept("b", self.toggle_building_ui)
        
        # Add difficulty settings toggle if adaptive difficulty is enabled
        if hasattr(self, 'difficulty_settings'):
            self.accept("o", self.toggle_difficulty_settings)  # Show difficulty settings
        
    def _setup_world(self):
        """Set up the game world"""
        # Create the ground
        self._create_ground()
        
        # Create environmental objects
        self._create_environment()
        
        # Add a light
        self._setup_lighting()
    
    def _populate_world(self):
        """Populate the world with entities and objects"""
        # Populate resource nodes
        self.entity_manager.populate_resource_nodes(count=30, area_size=50)
        
        # Create initial enemies
        self.entity_manager.spawn_random_enemies(5)
        
        # Create a crafting bench
        from panda3d.core import Vec3
        self.entity_manager.create_crafting_bench(Vec3(10, 10, 0))
        
        # Set player position
        self.player.position = Vec3(0, 0, 0)
        
        # Set the city center at the player's starting position
        self.city_manager.set_city_center(Vec3(0, 0, 0))
    
    def _create_ground(self):
        """Create the ground plane for the game world"""
        ground = self.loader.loadModel("models/box")
        ground.setScale(100, 100, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green grass color
        ground.reparentTo(self.render)
        
        # Set up collision with ground
        from panda3d.core import CollisionNode, CollisionPlane, Plane, Point3, Vec3
        collision_node = CollisionNode("ground_collision")
        collision_node.addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))
        collision_node_path = ground.attachNewNode(collision_node)
    
    def _create_environment(self):
        """Create environmental objects like trees, rocks, etc."""
        # Add some trees
        import random
        
        # Tree positions
        tree_positions = []
        for _ in range(15):
            x = random.uniform(-40, 40)
            y = random.uniform(-40, 40)
            # Keep trees away from center (player spawn)
            if abs(x) < 15 and abs(y) < 15:
                continue
            tree_positions.append((x, y))
            
        # Create trees
        for x, y in tree_positions:
            try:
                tree = self.loader.loadModel("models/box")  # Placeholder for tree model
                tree.setScale(1, 1, 3)
                tree.setPos(x, y, 1.5)
                tree.setColor((0.5, 0.3, 0.1, 1))  # Brown trunk color
                
                # Add tree top
                tree_top = self.loader.loadModel("models/box")
                tree_top.setScale(2, 2, 2)
                tree_top.setPos(0, 0, 1.5)
                tree_top.setColor((0.1, 0.6, 0.1, 1))  # Green leaves color
                tree_top.reparentTo(tree)
                
                tree.reparentTo(self.render)
            except Exception as e:
                print(f"Error creating tree: {e}")
                
        # Add some rocks
        rock_positions = []
        for _ in range(10):
            x = random.uniform(-40, 40)
            y = random.uniform(-40, 40)
            # Keep rocks away from center (player spawn)
            if abs(x) < 10 and abs(y) < 10:
                continue
            rock_positions.append((x, y))
            
        # Create rocks
        for x, y in rock_positions:
            try:
                rock = self.loader.loadModel("models/box")  # Placeholder for rock model
                rock.setScale(1.5, 1.5, 0.8)
                rock.setPos(x, y, 0.4)
                rock.setColor((0.5, 0.5, 0.5, 1))  # Gray rock color
                rock.reparentTo(self.render)
            except Exception as e:
                print(f"Error creating rock: {e}")
                
    def _setup_lighting(self):
        """Set up the lighting for the game world"""
        # Main directional light (sun/moon)
        from panda3d.core import DirectionalLight
        
        # Create the main directional light
        main_light = DirectionalLight("main_light")
        main_light.setColor((0.8, 0.8, 0.8, 1))
        main_light_np = self.render.attachNewNode(main_light)
        main_light_np.setHpr(45, -45, 0)
        self.render.setLight(main_light_np)
        
        # Ambient light for overall scene illumination
        from panda3d.core import AmbientLight
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)
        
        # The day/night cycle system manages lighting now
        # No need to store references as the system creates its own lights
        # Remove the following lines when the new system is integrated
        # self.day_night_cycle.main_light = main_light
        # self.day_night_cycle.main_light_np = main_light_np
        # self.day_night_cycle.ambient_light = ambient_light
    
    def _setup_ui(self):
        """Set up the game's UI components"""
        # Create the crafting UI
        self.crafting_ui = CraftingUI(self)
        
        # Create the relic UI
        self.relic_ui = RelicUI(self)
        
        # Create message display for notifications
        from direct.gui.OnscreenText import OnscreenText
        self.message_text = OnscreenText(
            text="",
            style=1,
            fg=(1, 1, 1, 1),
            bg=(0, 0, 0, 0.5),
            pos=(0, 0.7),  # Top center
            scale=0.06,
            shadow=(0, 0, 0, 1)
        )
        self.message_text.hide()
    
    def _register_scenes(self):
        """Register game scenes with the scene manager"""
        from game.main_menu import MainMenuScene
        
        # Main menu scene
        self.scene_manager.add_scene("main_menu", MainMenuScene(self))
        
        # Game scenes already registered through scene_manager
    
    def _update(self, task):
        """
        Update game state
        
        Args:
            task: Task object from Panda3D
            
        Returns:
            Task continuation constant
        """
        # Get delta time
        dt = globalClock.getDt()
        
        # Update play time if not paused and in the game scene
        if not self.paused and self.scene_manager.current_scene_name == "game":
            self.play_time += dt
        
        # Update game systems
        if not self.paused:
            # Update the scene manager
            self.scene_manager.update(dt)
            
            # Update other systems only if in game scene
            if self.scene_manager.current_scene_name == "game":
                # Update day/night cycle
                self.day_night_cycle.update(dt)
                
                # Update entities
                self.entity_manager.update(dt)
                
                # Update camera
                self.camera_controller.update(dt)
                
                # Check for autosave trigger (e.g., at dawn)
                if hasattr(self, 'day_night_cycle') and self.day_night_cycle.time_of_day == 'dawn':
                    # Only autosave once per day
                    if not getattr(self, '_last_autosave_day', None) == self.day_night_cycle.day:
                        self._trigger_autosave()
                        self._last_autosave_day = self.day_night_cycle.day
        
        # Always update debug info if enabled
        if self.debug_display_enabled:
            self._update_debug_info()
        
        return task.cont
    
    def _trigger_autosave(self):
        """Trigger an autosave"""
        if hasattr(self, 'save_manager'):
            self.save_manager.autosave()
            
            # Show message to player
            self.show_message("Game autosaved")
    
    def _update_debug_info(self):
        """Update debugging information display"""
        if not hasattr(self, 'debug_text'):
            return
        
        # Player info
        player_pos = "N/A"
        player_health = "N/A"
        player_level = "N/A"
        
        if self.player:
            player_pos = f"({self.player.position.x:.1f}, {self.player.position.y:.1f}, {self.player.position.z:.1f})"
            player_health = f"{self.player.health}/{self.player.max_health}"
            player_level = f"{self.player.level}"
        
        # Game state info
        time_of_day = self.day_night_cycle.get_time_of_day_name()
        game_time = f"{int(self.day_night_cycle.current_time / 60):02d}:{int(self.day_night_cycle.current_time % 60):02d}"
        
        # Entities info
        entity_count = len(self.entity_manager.entities)
        enemy_count = len(self.entity_manager.enemies)
        projectile_count = len(self.entity_manager.projectiles)
        
        # FPS info
        fps = globalClock.getAverageFrameRate()
        
        # City info
        city_health = "N/A"
        city_defense = "N/A"
        
        if hasattr(self, 'city_manager'):
            city_defense = f"{self.city_manager.defense:.1f}"
            
            # Calculate city health as average of section health
            if self.city_manager.sections:
                total_health = sum(section['health'] for section in self.city_manager.sections)
                max_health = sum(section['max_health'] for section in self.city_manager.sections)
                if max_health > 0:
                    city_health = f"{(total_health / max_health) * 100:.1f}%"
        
        # Difficulty info
        difficulty_preset = "N/A"
        enemy_hp_mult = "N/A"
        enemy_dmg_mult = "N/A"
        
        if hasattr(self, 'adaptive_difficulty_system'):
            difficulty_preset = self.adaptive_difficulty_system.difficulty_preset.name
            factors = self.adaptive_difficulty_system.get_current_difficulty_factors()
            enemy_hp_mult = f"{factors['enemy_health']:.2f}x"
            enemy_dmg_mult = f"{factors['enemy_damage']:.2f}x"
        
        # Format debug text
        debug_text = (
            f"Player: Pos={player_pos} HP={player_health} LVL={player_level}\n"
            f"Time: {time_of_day} ({game_time})\n"
            f"Entities: {entity_count} (Enemies: {enemy_count}, Projectiles: {projectile_count})\n"
            f"City: HP={city_health} DEF={city_defense}\n"
            f"Difficulty: {difficulty_preset} (HP={enemy_hp_mult}, DMG={enemy_dmg_mult})\n"
            f"FPS: {fps:.1f}"
        )
        
        # Update the text
        self.debug_text.setText(debug_text)
    
    def toggle_pause(self):
        """Toggle game pause state"""
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'resumed'}")
    
    def toggle_debug(self):
        """Toggle debug information display"""
        self.debug_mode = not self.debug_mode
        
        if self.debug_mode:
            # Create debug text display if it doesn't exist
            if not hasattr(self, 'debug_text'):
                from direct.gui.OnscreenText import OnscreenText
                self.debug_text = OnscreenText(
                    text="DEBUG",
                    style=1,
                    fg=(1, 1, 1, 1),
                    bg=(0, 0, 0, 0.5),
                    pos=(-1.3, 0.9),
                    align=0, scale=0.05
                )
            else:
                self.debug_text.show()
                
            # Hide the regular weapon text when debug is on
            if hasattr(self, 'weapon_text'):
                self.weapon_text.hide()
        else:
            # Hide debug text
            if hasattr(self, 'debug_text'):
                self.debug_text.hide()
                
            # Show the weapon text again
            if hasattr(self, 'weapon_text'):
                self.weapon_text.show()
        
        print(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")
    
    def toggle_day_night(self):
        """Toggle between day and night for testing"""
        current_time = self.day_night_cycle.time_of_day
        
        if current_time in [TimeOfDay.DAWN, TimeOfDay.DAY]:
            # Switch to night
            self.day_night_cycle.set_time(TimeOfDay.NIGHT)
            message = "Night has fallen... Beware of stronger enemies!"
            print("Switching to night")
        else:
            # Switch to day
            self.day_night_cycle.set_time(TimeOfDay.DAY)
            message = "The sun rises, bringing safety and light."
            print("Switching to day")
            
        # Show message to player
        if hasattr(self, 'show_message'):
            self.show_message(message, 3.0)
    
    def spawn_player(self):
        """Debug function to respawn player at origin"""
        if hasattr(self, 'player') and self.player:
            self.entity_manager.remove_entity(self.player)
        
        self.player = self.entity_manager.create_player()
        self.camera_controller.set_target(self.player.root)
        print("Player respawned at origin.")
    
    def spawn_enemies(self):
        """Debug function to spawn test enemies"""
        self.entity_manager.spawn_random_enemies(5)
        print(f"Spawned enemies. Total: {len(self.entity_manager.enemies)}")
    
    def clear_entities(self):
        """Debug function to clear all entities except player"""
        self.entity_manager.clear_all_entities()
        print("All entities cleared except player.")
    
    def setup_help_text(self):
        """Setup help text for controls"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Create control help text
        self.help_text = OnscreenText(
            text="WASD: Move | MOUSE1: Attack | E: Interact/Gather | SPACE: Dodge\n"
                 "1-4: Change Projectile | T: Toggle Day/Night | F: Toggle Fog | F1: Toggle Debug | C: Crafting | R: Relics | O: Difficulty Settings",
            style=1,
            fg=(1, 1, 1, 1),
            bg=(0, 0, 0, 0.5),
            pos=(0, -0.9),  # Bottom center
            align=0,
            scale=0.04
        )
        
        # Create help text for current weapon
        self.weapon_text = OnscreenText(
            text="Current Weapon: Straight Shot (1)",
            style=1,
            fg=(1, 0.8, 0.2, 1),
            bg=(0, 0, 0, 0.5),
            pos=(0, 0.9),  # Top center
            align=0,
            scale=0.05
        )
    
    def toggle_crafting_ui(self):
        """Toggle the crafting UI"""
        if hasattr(self, 'crafting_ui'):
            self.crafting_ui.toggle()
    
    def toggle_relic_ui(self):
        """Toggle the relic UI"""
        if hasattr(self, 'relic_ui'):
            self.relic_ui.toggle()
    
    def toggle_building_ui(self):
        """Toggle the building UI visibility"""
        self.building_ui.toggle()
    
    def pause_game(self):
        """Pause the game"""
        if not self.paused:
            self.paused = True
            print("Game paused")
    
    def resume_game(self):
        """Resume the game"""
        if self.paused:
            self.paused = False
            print("Game resumed")
    
    def show_message(self, text, duration=2.0):
        """
        Show a temporary message on screen
        
        Args:
            text (str): Message to display
            duration (float): How long to show the message for
        """
        # Set message text
        self.message_text.setText(text)
        self.message_text.show()
        
        # Remove any existing hide tasks
        taskMgr.remove("hide_message")
        
        # Schedule task to hide message
        taskMgr.doMethodLater(duration, self._hide_message, "hide_message")
    
    def _hide_message(self, task):
        """Hide the message text"""
        self.message_text.hide()
        return task.done

    def calculate_ground_point_at_mouse(self, mouse_pos):
        """
        Calculate the 3D point on the ground plane at the given mouse position
        
        Args:
            mouse_pos: The 2D mouse position from mouse watcher
            
        Returns:
            Vec3: The 3D point on the ground, or None if not found
        """
        from panda3d.core import CollisionRay, CollisionNode, CollisionHandlerQueue, GeomNode, CollisionTraverser
        
        try:
            # Create collision ray
            picker_ray = CollisionRay()
            picker_ray.setFromLens(self.camNode, mouse_pos.x, mouse_pos.y)
            
            # Set up collision traverser
            picker_node = CollisionNode('picker_ray')
            picker_node.addSolid(picker_ray)
            picker_node_path = self.camera.attachNewNode(picker_node)
            picker_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
            
            # Create collision queue
            picker_queue = CollisionHandlerQueue()
            
            # Traverse for collisions
            picker_traverser = CollisionTraverser('picker_traverser')
            picker_traverser.addCollider(picker_node_path, picker_queue)
            picker_traverser.traverse(self.render)
            
            # Clean up
            picker_node_path.removeNode()
            
            # Check for hits
            if picker_queue.getNumEntries() > 0:
                # Sort entries by distance
                picker_queue.sortEntries()
                entry = picker_queue.getEntry(0)
                hit_pos = entry.getSurfacePoint(self.render)
                return hit_pos
                
            return None
        except Exception as e:
            print(f"Error in calculate_ground_point_at_mouse: {e}")
            return None

    def cleanup_and_exit(self):
        """Clean up resources and exit the game"""
        # Clean up UI manager
        if hasattr(self, 'ui_manager'):
            self.ui_manager.cleanup()
        
        # Clean up other resources
        # (existing code)
        
        # Exit the game
        self.userExit()
        
    def toggle_debug_display(self):
        """Toggle the debug display"""
        if hasattr(self, 'debug_display_enabled'):
            self.debug_display_enabled = not self.debug_display_enabled
        else:
            self.debug_display_enabled = True
            
        # Create debug display if enabling for the first time
        if self.debug_display_enabled and not hasattr(self, 'debug_display'):
            self._setup_debug_display()
            
    def _setup_debug_display(self):
        """Set up the debug display"""
        from direct.gui.OnscreenText import OnscreenText
        
        self.debug_display = {}
        self.debug_display['fps'] = OnscreenText(
            text="FPS: --",
            pos=(-1.3, 0.9),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            mayChange=True
        )
        
        self.debug_display['player'] = OnscreenText(
            text="Player: --",
            pos=(-1.3, 0.8),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            mayChange=True
        )
        
        self.debug_display['entities'] = OnscreenText(
            text="Entities: --",
            pos=(-1.3, 0.7),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            mayChange=True
        )
        
        self.debug_display['city'] = OnscreenText(
            text="City: --",
            pos=(-1.3, 0.6),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=0,
            mayChange=True
        )
        
    def update_debug_display(self):
        """Update the debug display with current information"""
        if not hasattr(self, 'debug_display') or not self.debug_display_enabled:
            return
            
        # Update FPS
        fps = round(self.taskMgr.globalClock.getAverageFrameRate(), 1)
        self.debug_display['fps'].setText(f"FPS: {fps}")
        
        # Update player info
        if self.player:
            player_text = f"Player: Pos({self.player.position.x:.1f}, {self.player.position.y:.1f}) "
            player_text += f"HP: {self.player.health}/{self.player.max_health} "
            player_text += f"Level: {self.player.level} "
            player_text += f"XP: {self.player.experience}/{self.player.experience_to_next_level}"
            self.debug_display['player'].setText(player_text)
            
        # Update entity info
        entity_text = f"Entities: {len(self.entity_manager.entities)} "
        entity_text += f"Enemies: {len(self.entity_manager.enemies)} "
        entity_text += f"Buildings: {len(self.entity_manager.buildings)} "
        self.debug_display['entities'].setText(entity_text)
        
        # Update city info
        if hasattr(self, 'city_manager'):
            city_stats = self.city_manager.get_city_stats()
            city_text = f"City: Level {city_stats['level']} "
            city_text += f"Defense: {city_stats['defense']} "
            city_text += f"Food: {city_stats['food_storage']} "
            city_text += f"Defenders: {city_stats['current_defenders']}/{city_stats['max_defenders']}"
            self.debug_display['city'].setText(city_text)

    def toggle_fog(self):
        """Toggle night fog for testing"""
        if hasattr(self, 'night_fog'):
            self.night_fog.toggle_fog()
            
            if self.night_fog.active:
                message = "Night fog activated"
            else:
                message = "Night fog deactivated"
                
            # Show message to player
            if hasattr(self, 'show_message'):
                self.show_message(message, 2.0)

    def toggle_difficulty_settings(self):
        """Show the difficulty settings UI"""
        self.difficulty_settings.show_settings()
        
        # Pause the game while settings are open
        self.pause_game()
        
        # Add a task to check when settings are closed
        self.taskMgr.add(self._check_difficulty_settings_closed, "check_settings_closed")
        
    def _check_difficulty_settings_closed(self, task):
        """Check if difficulty settings UI has been closed and resume game if so"""
        if not self.difficulty_settings.main_frame:
            self.resume_game()
            return task.done
        return task.cont

def main():
    """Main entry point for the game"""
    parser = argparse.ArgumentParser(description="Nightfall Defenders Game")
    parser.add_argument("--adaptive-difficulty", action="store_true", help="Enable adaptive difficulty system")
    args = parser.parse_args()
    
    # Create and run the game
    app = NightfallDefenders(enable_adaptive_difficulty=args.adaptive_difficulty)
    app.run()

if __name__ == "__main__":
    main()
