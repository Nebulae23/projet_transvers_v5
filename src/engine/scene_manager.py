#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scene Manager for Nightfall Defenders
Handles scene transitions and management
"""

from panda3d.core import NodePath, TextNode
from direct.gui.OnscreenText import OnscreenText

class Scene:
    """Base class for all game scenes"""
    
    def __init__(self, game, scene_manager):
        """
        Initialize the scene
        
        Args:
            game: The main game instance
            scene_manager: The scene manager instance
        """
        self.game = game
        self.scene_manager = scene_manager
        self.root = NodePath("SceneRoot")
        self.root.reparentTo(self.game.render)
        
        # Set initially as not active
        self.is_active = False
    
    def enter(self):
        """Called when entering the scene"""
        self.is_active = True
        self.root.unstash()
    
    def exit(self):
        """Called when exiting the scene"""
        self.is_active = False
        self.root.stash()
    
    def update(self, dt):
        """
        Update the scene
        
        Args:
            dt (float): Delta time since last update
        """
        pass
    
    def cleanup(self):
        """Clean up the scene resources"""
        self.root.removeNode()


class MainMenuScene(Scene):
    """Main menu scene"""
    
    def __init__(self, game, scene_manager):
        super().__init__(game, scene_manager)
        
        # Create main menu elements
        self.title = OnscreenText(
            text="Nightfall Defenders",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(0, 0.7),
            scale=0.15
        )
        self.title.reparentTo(self.game.aspect2d)
        
        # Menu options
        self.start_text = OnscreenText(
            text="Start Game",
            fg=(1, 1, 1, 1),
            pos=(0, 0.3),
            scale=0.07
        )
        self.start_text.reparentTo(self.game.aspect2d)
        
        self.options_text = OnscreenText(
            text="Options",
            fg=(1, 1, 1, 1),
            pos=(0, 0.1),
            scale=0.07
        )
        self.options_text.reparentTo(self.game.aspect2d)
        
        self.quit_text = OnscreenText(
            text="Quit",
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            scale=0.07
        )
        self.quit_text.reparentTo(self.game.aspect2d)
        
        # Hide UI elements initially
        self.hide_ui()
    
    def hide_ui(self):
        """Hide all UI elements"""
        self.title.stash()
        self.start_text.stash()
        self.options_text.stash()
        self.quit_text.stash()
    
    def show_ui(self):
        """Show all UI elements"""
        self.title.unstash()
        self.start_text.unstash()
        self.options_text.unstash()
        self.quit_text.unstash()
    
    def enter(self):
        """Called when entering the scene"""
        super().enter()
        self.show_ui()
    
    def exit(self):
        """Called when exiting the scene"""
        super().exit()
        self.hide_ui()
    
    def update(self, dt):
        """Update the scene"""
        super().update(dt)
        
        # Check for input to start the game
        if self.game.input_manager.is_pressed("interact"):
            # Start the game when enter/interact is pressed
            self.scene_manager.change_scene("game")
        
        # Check for quit
        if self.game.input_manager.is_pressed("pause"):
            # Quit the game when escape is pressed from the main menu
            self.game.userExit()


class GameScene(Scene):
    """Main gameplay scene"""
    
    def __init__(self, game, scene_manager):
        super().__init__(game, scene_manager)
        
        # Set up the game environment
        self.setup_environment()
        
        # Initialize game systems
        self.time_system = TimeSystem(game)
        
        # Set up UI elements
        self.setup_ui()
    
    def setup_environment(self):
        """Set up the game environment"""
        # This would normally create the world, load terrain, etc.
        # For now, just create a simple ground plane for testing
        from panda3d.core import CardMaker
        from panda3d.core import Vec4
        
        # Create a ground plane
        cm = CardMaker("Ground")
        cm.setFrame(-100, 100, -100, 100)
        ground = self.root.attachNewNode(cm.generate())
        ground.setP(-90)  # Rotate to be flat
        ground.setPos(0, 0, 0)
        ground.setColor(0.3, 0.7, 0.3, 1)  # Green ground
    
    def setup_ui(self):
        """Set up game UI elements"""
        # Create a day/night cycle indicator
        self.time_text = OnscreenText(
            text="Day 1 - 12:00",
            fg=(1, 1, 1, 1),
            pos=(-1.3, 0.9),
            align=TextNode.ALeft,
            scale=0.05
        )
        self.time_text.reparentTo(self.game.aspect2d)
        
        # Health indicator
        self.health_text = OnscreenText(
            text="Health: 100%",
            fg=(1, 0.5, 0.5, 1),
            pos=(-1.3, 0.8),
            align=TextNode.ALeft,
            scale=0.05
        )
        self.health_text.reparentTo(self.game.aspect2d)
        
        # Hide UI elements initially
        self.hide_ui()
    
    def hide_ui(self):
        """Hide all UI elements"""
        self.time_text.stash()
        self.health_text.stash()
    
    def show_ui(self):
        """Show all UI elements"""
        self.time_text.unstash()
        self.health_text.unstash()
    
    def enter(self):
        """Called when entering the scene"""
        super().enter()
        self.show_ui()
    
    def exit(self):
        """Called when exiting the scene"""
        super().exit()
        self.hide_ui()
    
    def update(self, dt):
        """Update the scene"""
        super().update(dt)
        
        # Update game systems
        self.time_system.update(dt)
        
        # Update UI
        self.time_text.setText(f"Day {self.time_system.day} - {self.time_system.get_time_string()}")
        
        # Check for pause
        if self.game.input_manager.is_pressed("pause"):
            # Pause the game when escape is pressed
            self.scene_manager.change_scene("pause")


class PauseScene(Scene):
    """Pause menu scene"""
    
    def __init__(self, game, scene_manager):
        super().__init__(game, scene_manager)
        
        # Create a semi-transparent overlay
        from panda3d.core import CardMaker, TransparencyAttrib
        
        cm = CardMaker("PauseOverlay")
        cm.setFrame(-2, 2, -2, 2)  # Make it cover the whole screen
        
        self.overlay = self.root.attachNewNode(cm.generate())
        self.overlay.setColor(0, 0, 0, 0.5)  # Semi-transparent black
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)
        self.overlay.setPos(0, 0, 0)
        
        # Create pause menu text
        self.pause_text = OnscreenText(
            text="Game Paused",
            fg=(1, 1, 1, 1),
            pos=(0, 0.5),
            scale=0.1
        )
        self.pause_text.reparentTo(self.game.aspect2d)
        
        self.resume_text = OnscreenText(
            text="Resume Game",
            fg=(1, 1, 1, 1),
            pos=(0, 0.2),
            scale=0.07
        )
        self.resume_text.reparentTo(self.game.aspect2d)
        
        self.options_text = OnscreenText(
            text="Options",
            fg=(1, 1, 1, 1),
            pos=(0, 0),
            scale=0.07
        )
        self.options_text.reparentTo(self.game.aspect2d)
        
        self.quit_text = OnscreenText(
            text="Quit to Main Menu",
            fg=(1, 1, 1, 1),
            pos=(0, -0.2),
            scale=0.07
        )
        self.quit_text.reparentTo(self.game.aspect2d)
        
        # Hide UI elements initially
        self.hide_ui()
    
    def hide_ui(self):
        """Hide all UI elements"""
        self.pause_text.stash()
        self.resume_text.stash()
        self.options_text.stash()
        self.quit_text.stash()
    
    def show_ui(self):
        """Show all UI elements"""
        self.pause_text.unstash()
        self.resume_text.unstash()
        self.options_text.unstash()
        self.quit_text.unstash()
    
    def enter(self):
        """Called when entering the scene"""
        super().enter()
        self.show_ui()
    
    def exit(self):
        """Called when exiting the scene"""
        super().exit()
        self.hide_ui()
    
    def update(self, dt):
        """Update the scene"""
        super().update(dt)
        
        # Check for resume
        if self.game.input_manager.is_pressed("pause"):
            # Resume the game when escape is pressed again
            self.scene_manager.change_scene("game")
        
        # Check for resume via interact
        if self.game.input_manager.is_pressed("interact"):
            # Resume the game when enter/interact is pressed
            self.scene_manager.change_scene("game")


class TimeSystem:
    """
    System for managing the day/night cycle
    """
    
    def __init__(self, game):
        """Initialize the time system"""
        self.game = game
        
        # Time settings
        self.day = 1
        self.time = 0.0  # Time in hours (0-24)
        self.day_length = 20.0 * 60.0  # 20 minutes in seconds
        self.time_scale = 24.0 / self.day_length  # Convert seconds to in-game hours
        
        # Time of day thresholds
        self.dawn_time = 6.0
        self.day_time = 7.0
        self.dusk_time = 18.0
        self.night_time = 19.0
        
        # Current time state
        self.is_day = True
        self.is_night = False
        
        # Set up initial lighting
        self.setup_lighting()
    
    def setup_lighting(self):
        """Set up day/night cycle lighting"""
        # This would normally set up dynamic lighting based on time of day
        pass
    
    def update(self, dt):
        """
        Update the time system
        
        Args:
            dt (float): Delta time since last update
        """
        # Advance time
        self.time += dt * self.time_scale
        
        # Check for day/night transition
        if self.time >= 24.0:
            self.time = 0.0
            self.day += 1
        
        # Check for dawn/dusk transitions
        was_day = self.is_day
        was_night = self.is_night
        
        if self.time >= self.dawn_time and self.time < self.night_time:
            self.is_day = True
        else:
            self.is_day = False
            
        if self.time >= self.night_time or self.time < self.dawn_time:
            self.is_night = True
        else:
            self.is_night = False
        
        # Handle day/night transitions
        if was_day != self.is_day or was_night != self.is_night:
            self.handle_time_transition()
    
    def handle_time_transition(self):
        """Handle transition between day and night"""
        if self.is_day and not self.is_night:
            print("Transitioning to day")
            # Handle day transition
            pass
        elif self.is_night and not self.is_day:
            print("Transitioning to night")
            # Handle night transition
            pass
    
    def get_time_string(self):
        """
        Get a formatted time string
        
        Returns:
            str: Time in HH:MM format
        """
        hours = int(self.time)
        minutes = int((self.time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"


class SceneManager:
    """
    Manages game scenes and transitions
    """
    
    def __init__(self, game):
        """Initialize the scene manager"""
        self.game = game
        self.scenes = {}
        self.current_scene = None
        
        # Create scenes
        self.scenes["menu"] = MainMenuScene(game, self)
        self.scenes["game"] = GameScene(game, self)
        self.scenes["pause"] = PauseScene(game, self)
        
        # Start with the main menu
        self.change_scene("menu")
    
    def add_scene(self, name, scene):
        """
        Add a scene to the manager
        
        Args:
            name (str): The name of the scene
            scene (Scene): The scene to add
        """
        self.scenes[name] = scene
    
    def change_scene(self, scene_name):
        """
        Change to a different scene
        
        Args:
            scene_name (str): The name of the scene to change to
        """
        if scene_name not in self.scenes:
            print(f"Scene '{scene_name}' not found")
            return
        
        # Exit current scene if any
        if self.current_scene:
            self.current_scene.exit()
        
        # Enter new scene
        self.current_scene = self.scenes[scene_name]
        self.current_scene.enter()
    
    def update(self, dt):
        """
        Update the current scene
        
        Args:
            dt (float): Delta time since last update
        """
        if self.current_scene:
            self.current_scene.update(dt) 