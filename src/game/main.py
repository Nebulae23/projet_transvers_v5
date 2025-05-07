#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Main Game Module
Implements the core game loop and initializes game systems
"""

import os
import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties, Vec3, ConfigVariableBool

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

# Import game modules
from game.day_night_cycle import DayNightCycle
from game.camera_controller import CameraController
from game.entity_manager import EntityManager
from game.crafting_system import CraftingSystem
from game.crafting_ui import CraftingUI
from game.relic_system import RelicSystem
from game.relic_ui import RelicUI
from game.building_system import BuildingSystem
from game.building_ui import BuildingUI
from game.city_manager import CityManager

class NightfallDefenders(ShowBase):
    """Main game class that extends Panda3D's ShowBase"""
    
    def __init__(self):
        """Initialize the game"""
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
        
        # Initialize game-specific systems
        self.game_time = 0
        self.entity_manager = EntityManager(self)
        self.day_night_cycle = DayNightCycle(self)
        self.camera_controller = CameraController(self)
        
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
        
        # Populate the world with resources
        self._populate_world()
        
        # Set up key bindings
        self._setup_key_bindings()
        
        # Set up the game world
        self._setup_world()
        
        # Initialize UI components
        self._setup_ui()
        
        # Initial game state
        self.paused = False
        self.debug_mode = False
        
        # Debug settings
        self.debug_display_enabled = False
        
        # Add the update task
        self.task_mgr.add(self._update, "update_task")
        
        # Show controls help
        self.setup_help_text()
        
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
        
        # UI controls
        self.accept("c", self.toggle_crafting_ui)
        self.accept("r", self.toggle_relic_ui)
        self.accept("b", self.toggle_building_ui)
        
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
        
        # Store lighting references for day/night cycle
        self.day_night_cycle.main_light = main_light
        self.day_night_cycle.main_light_np = main_light_np
        self.day_night_cycle.ambient_light = ambient_light
    
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
    
    def _update(self, task):
        """Main game update loop"""
        # First time initialization
        if not hasattr(task, 'last'):
            task.last = 0
            
        # Calculate delta time
        dt = task.time - task.last
        task.last = task.time
        
        # Cap dt to prevent physics issues on lag spikes
        if dt > 0.1:
            dt = 0.1
            
        # Update game time
        self.game_time += dt
        
        # Update systems
        self.day_night_cycle.update(dt)
        self.entity_manager.update(dt)
        self.camera_controller.update(dt)
        self.crafting_system.update(dt)
        self.relic_system.update(dt)
        self.building_system.update(dt)
        self.city_manager.update(dt)
        
        # Update UIs
        if hasattr(self, 'crafting_ui') and self.crafting_ui.visible:
            self.crafting_ui.update(dt)
            
        if hasattr(self, 'relic_ui') and self.relic_ui.visible:
            self.relic_ui.update(dt)
            
        if hasattr(self, 'building_ui') and self.building_ui.visible:
            self.building_ui.update(dt)
            
        # Update debug display
        if self.debug_mode:
            self._update_debug_info()
        
        return task.cont
    
    def _update_debug_info(self):
        """Update debug information display"""
        fps = round(globalClock.getAverageFrameRate(), 1)
        time_of_day = self.day_night_cycle.get_time_of_day_string()
        day_phase = self.day_night_cycle.get_day_phase()
        day_num = self.day_night_cycle.day
        
        # Entity counts
        entity_info = self.entity_manager.get_debug_info()
        
        debug_text = f"FPS: {fps}\n"
        debug_text += f"Day: {day_num}, Time: {time_of_day} ({day_phase})\n"
        debug_text += f"Camera Mode: {self.camera_controller.current_mode}\n"
        debug_text += f"Camera Pos: {self.camera.getPos()}\n"
        debug_text += f"Entities: {len(self.entity_manager.entities)} "
        debug_text += f"(Enemies: {entity_info['enemy_count']}, "
        debug_text += f"Projectiles: {entity_info['projectile_count']}, "
        debug_text += f"Resources: {entity_info['resource_node_count'] + entity_info['resource_drop_count']})\n"
        
        # Player stats
        if self.player:
            health_percent = int((self.player.health / self.player.max_health) * 100)
            stamina_percent = int((self.player.stamina / self.player.max_stamina) * 100)
            weapon_type = self.player.projectile_type
            
            debug_text += f"Player Pos: {self.player.position}\n"
            debug_text += f"Health: {self.player.health}/{self.player.max_health} ({health_percent}%)\n"
            debug_text += f"Stamina: {self.player.stamina}/{self.player.max_stamina} ({stamina_percent}%)\n"
            debug_text += f"Level: {self.player.level} - XP: {self.player.experience}/{self.player.experience_to_next_level} "
            debug_text += f"({int(self.player.get_experience_percent())}%)\n"
            debug_text += f"Weapon: {self.player.projectile_types[weapon_type]['name']} "
            debug_text += f"(Dmg: {self.player.projectile_types[weapon_type]['damage']})\n"
            debug_text += f"Inventory: {self.player.get_inventory_string()}\n"
            
            # Add damage reduction if any
            if hasattr(self.player, 'damage_reduction') and self.player.damage_reduction > 0:
                reduction_percent = int(self.player.damage_reduction * 100)
                debug_text += f"Damage Reduction: {reduction_percent}%\n"
        
        # Enemy stats
        debug_text += f"Enemies Killed: {entity_info['enemies_killed']}\n"
        
        # Crafting stats if available
        if hasattr(self, 'crafting_system'):
            debug_text += "Upgrades: "
            any_upgrades = False
            for upgrade_id, level in self.crafting_system.crafted_upgrades.items():
                if level > 0:
                    any_upgrades = True
                    name = self.crafting_system.recipes[upgrade_id]["name"]
                    debug_text += f"{name} Lv.{level}, "
            
            if not any_upgrades:
                debug_text += "None"
            else:
                debug_text = debug_text[:-2]  # Remove trailing comma and space
        
        # Relic stats if available
        if hasattr(self, 'relic_system') and self.relic_system.active_relics:
            debug_text += "\nRelics: "
            for relic_id in self.relic_system.active_relics:
                relic_name = self.relic_system.available_relics[relic_id]["name"]
                debug_text += f"{relic_name}, "
            debug_text = debug_text[:-2]  # Remove trailing comma and space
        
        # Update the on-screen text
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
        if self.day_night_cycle.is_daytime:
            self.day_night_cycle.current_time = self.day_night_cycle.dusk_start
        else:
            self.day_night_cycle.current_time = self.day_night_cycle.dawn_start
        
        print(f"Switching to {'night' if self.day_night_cycle.is_daytime else 'day'}")
    
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
                 "1-4: Change Projectile | T: Toggle Day/Night | F1: Toggle Debug | C: Crafting | R: Relics",
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
        """Clean up and exit the game"""
        print("Exiting game...")
        # Save game state if needed
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

def main():
    """Main entry point for the game"""
    try:
        app = NightfallDefenders()
        app.run()
    except Exception as e:
        import traceback
        print(f"ERROR: Game crashed: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
