#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pause Menu for Nightfall Defenders
Implements an enhanced pause menu with game information
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG, OnscreenText
from panda3d.core import TextNode, TransparencyAttrib, Vec4

class PauseMenu:
    """Enhanced pause menu with information display and options"""
    
    def __init__(self, game):
        """
        Initialize the pause menu
        
        Args:
            game: The game instance
        """
        self.game = game
        
        # Create root node
        self.root = self.game.aspect2d.attachNewNode("pause_menu_root")
        self.root.hide()
        
        # Semi-transparent background overlay
        self.background = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-2, 2, -2, 2),  # Cover entire screen
            pos=(0, 0, 0),
            parent=self.root
        )
        
        # Main menu container
        self.container = DirectFrame(
            frameColor=(0.2, 0.2, 0.3, 0.9),
            frameSize=(-0.7, 0.7, -0.8, 0.8),
            pos=(0, 0, 0),
            parent=self.root
        )
        
        # Title
        self.title = DirectLabel(
            text="Game Paused",
            text_scale=0.08,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.7),
            parent=self.container
        )
        
        # Create the menu sections
        self.create_menu_buttons()
        self.create_player_info()
        self.create_game_info()
    
    def create_menu_buttons(self):
        """Create main menu buttons"""
        button_width = 0.4
        button_height = 0.08
        button_spacing = 0.12
        start_y = 0.3
        
        # Container for buttons
        self.buttons_container = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-button_width/2, button_width/2, 
                       -button_height*3, button_height),
            pos=(0, 0, 0),
            parent=self.container
        )
        
        # Resume button
        self.resume_button = DirectButton(
            text="Resume Game",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.3, 0.6, 0.3, 0.8),
            frameSize=(-button_width/2, button_width/2, 
                      -button_height/2, button_height/2),
            relief=DGG.FLAT,
            pos=(0, 0, start_y),
            command=self.on_resume,
            parent=self.buttons_container
        )
        
        # Options button
        self.options_button = DirectButton(
            text="Options",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.3, 0.3, 0.6, 0.8),
            frameSize=(-button_width/2, button_width/2, 
                      -button_height/2, button_height/2),
            relief=DGG.FLAT,
            pos=(0, 0, start_y - button_spacing),
            command=self.on_options,
            parent=self.buttons_container
        )
        
        # Save button
        self.save_button = DirectButton(
            text="Save Game",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.3, 0.5, 0.6, 0.8),
            frameSize=(-button_width/2, button_width/2, 
                      -button_height/2, button_height/2),
            relief=DGG.FLAT,
            pos=(0, 0, start_y - button_spacing*2),
            command=self.on_save,
            parent=self.buttons_container
        )
        
        # Main Menu button
        self.main_menu_button = DirectButton(
            text="Return to Main Menu",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.6, 0.3, 0.3, 0.8),
            frameSize=(-button_width/2, button_width/2, 
                      -button_height/2, button_height/2),
            relief=DGG.FLAT,
            pos=(0, 0, start_y - button_spacing*3),
            command=self.on_main_menu,
            parent=self.buttons_container
        )
        
        # Quit button
        self.quit_button = DirectButton(
            text="Quit Game",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.5, 0.2, 0.2, 0.8),
            frameSize=(-button_width/2, button_width/2, 
                      -button_height/2, button_height/2),
            relief=DGG.FLAT,
            pos=(0, 0, start_y - button_spacing*4),
            command=self.on_quit,
            parent=self.buttons_container
        )
    
    def create_player_info(self):
        """Create player information panel"""
        panel_width = 0.5
        panel_height = 0.5
        
        # Panel container
        self.player_info = DirectFrame(
            frameColor=(0.3, 0.3, 0.4, 0.7),
            frameSize=(-panel_width/2, panel_width/2, 
                      -panel_height/2, panel_height/2),
            pos=(-0.45, 0, -0.4),
            parent=self.container
        )
        
        # Panel title
        self.player_info_title = DirectLabel(
            text="Player Information",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, panel_height/2 - 0.07),
            parent=self.player_info
        )
        
        # Player stats
        self.player_stats = []
        
        # We'll populate these dynamically when shown
        stats = [
            ("Class", "Unknown"),
            ("Level", "1"),
            ("Health", "100/100"),
            ("Experience", "0/100"),
            ("Skill Points", "0")
        ]
        
        for i, (label, value) in enumerate(stats):
            y_pos = panel_height/2 - 0.15 - i * 0.07
            
            # Label
            label_obj = DirectLabel(
                text=label + ":",
                text_scale=0.04,
                text_align=TextNode.ALeft,
                text_fg=(0.9, 0.9, 0.9, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-panel_width/2 + 0.05, 0, y_pos),
                parent=self.player_info
            )
            
            # Value
            value_obj = DirectLabel(
                text=value,
                text_scale=0.04,
                text_align=TextNode.ARight,
                text_fg=(1, 1, 0.8, 1),
                frameColor=(0, 0, 0, 0),
                pos=(panel_width/2 - 0.05, 0, y_pos),
                parent=self.player_info
            )
            
            self.player_stats.append((label_obj, value_obj))
    
    def create_game_info(self):
        """Create game information panel"""
        panel_width = 0.5
        panel_height = 0.5
        
        # Panel container
        self.game_info = DirectFrame(
            frameColor=(0.3, 0.3, 0.4, 0.7),
            frameSize=(-panel_width/2, panel_width/2, 
                      -panel_height/2, panel_height/2),
            pos=(0.45, 0, -0.4),
            parent=self.container
        )
        
        # Panel title
        self.game_info_title = DirectLabel(
            text="Game Information",
            text_scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, panel_height/2 - 0.07),
            parent=self.game_info
        )
        
        # Game stats
        self.game_stats = []
        
        # We'll populate these dynamically when shown
        stats = [
            ("Time", "Day 1, 00:00"),
            ("Time of Day", "Day"),
            ("Difficulty", "Normal"),
            ("Location", "City Center"),
            ("Active Events", "None")
        ]
        
        for i, (label, value) in enumerate(stats):
            y_pos = panel_height/2 - 0.15 - i * 0.07
            
            # Label
            label_obj = DirectLabel(
                text=label + ":",
                text_scale=0.04,
                text_align=TextNode.ALeft,
                text_fg=(0.9, 0.9, 0.9, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-panel_width/2 + 0.05, 0, y_pos),
                parent=self.game_info
            )
            
            # Value
            value_obj = DirectLabel(
                text=value,
                text_scale=0.04,
                text_align=TextNode.ARight,
                text_fg=(1, 1, 0.8, 1),
                frameColor=(0, 0, 0, 0),
                pos=(panel_width/2 - 0.05, 0, y_pos),
                parent=self.game_info
            )
            
            self.game_stats.append((label_obj, value_obj))
    
    def update_info(self):
        """Update displayed information"""
        # Update player info if player exists
        if hasattr(self.game, 'player'):
            player = self.game.player
            
            # Update basic stats
            self._update_stat(0, getattr(player, 'class_type', 'Unknown'))
            self._update_stat(1, str(getattr(player, 'level', 1)))
            self._update_stat(2, f"{getattr(player, 'health', 0)}/{getattr(player, 'max_health', 100)}")
            self._update_stat(3, f"{getattr(player, 'experience', 0)}/{getattr(player, 'experience_to_next_level', 100)}")
            self._update_stat(4, str(getattr(player, 'skill_points', 0)))
        
        # Update game info
        if hasattr(self.game, 'day_night_cycle'):
            # Get current day
            day = getattr(self.game.day_night_cycle, 'current_day', 1)
            
            # Get time string
            time_value = getattr(self.game.day_night_cycle, 'current_time', 0.5)
            hour = int(time_value * 24)
            minute = int((time_value * 24 * 60) % 60)
            time_str = f"Day {day}, {hour:02d}:{minute:02d}"
            
            # Update time of day
            time_of_day = "Day"
            if hasattr(self.game.day_night_cycle, 'time_of_day'):
                time_of_day = self.game.day_night_cycle.time_of_day
            
            self._update_game_stat(0, time_str)
            self._update_game_stat(1, time_of_day)
        
        # Update difficulty
        if hasattr(self.game, 'adaptive_difficulty'):
            difficulty = getattr(self.game.adaptive_difficulty, 'current_difficulty', "Normal")
            self._update_game_stat(2, difficulty)
        
        # Update active events
        if hasattr(self.game, 'random_event_system'):
            active_events = getattr(self.game.random_event_system, 'active_events', [])
            events_str = ', '.join(active_events) if active_events else "None"
            self._update_game_stat(4, events_str)
    
    def _update_stat(self, index, value):
        """Update a player stat value"""
        if 0 <= index < len(self.player_stats):
            _, value_label = self.player_stats[index]
            value_label["text"] = str(value)
    
    def _update_game_stat(self, index, value):
        """Update a game stat value"""
        if 0 <= index < len(self.game_stats):
            _, value_label = self.game_stats[index]
            value_label["text"] = str(value)
    
    def show(self):
        """Show the pause menu"""
        # Update information before showing
        self.update_info()
        
        # Show the menu
        self.root.show()
    
    def hide(self):
        """Hide the pause menu"""
        self.root.hide()
    
    def on_resume(self):
        """Resume the game"""
        self.hide()
        if hasattr(self.game, 'set_paused'):
            self.game.set_paused(False)
    
    def on_options(self):
        """Show options menu"""
        # TODO: Implement options menu
        pass
    
    def on_save(self):
        """Save the game"""
        # If save system exists, save the game
        if hasattr(self.game, 'save_system') and hasattr(self.game.save_system, 'save_game'):
            self.game.save_system.save_game()
            
            # Show notification if notification system exists
            if hasattr(self.game, 'notification_system'):
                self.game.notification_system.add_notification("Game saved successfully!", type="success")
    
    def on_main_menu(self):
        """Return to main menu"""
        # Hide pause menu
        self.hide()
        
        # Unpause game
        if hasattr(self.game, 'set_paused'):
            self.game.set_paused(False)
        
        # Show confirmation dialog
        self._show_confirmation_dialog(
            "Return to Main Menu?",
            "Any unsaved progress will be lost.",
            self._confirm_main_menu
        )
    
    def on_quit(self):
        """Quit the game"""
        # Show confirmation dialog
        self._show_confirmation_dialog(
            "Quit Game?",
            "Any unsaved progress will be lost.",
            self._confirm_quit
        )
    
    def _show_confirmation_dialog(self, title, message, confirm_callback):
        """Show a confirmation dialog"""
        # Create dialog overlay
        dialog = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-2, 2, -2, 2),
            pos=(0, 0, 0),
            parent=self.game.aspect2d
        )
        
        # Dialog box
        dialog_box = DirectFrame(
            frameColor=(0.3, 0.3, 0.4, 0.9),
            frameSize=(-0.5, 0.5, -0.3, 0.3),
            pos=(0, 0, 0),
            parent=dialog
        )
        
        # Title
        title_label = DirectLabel(
            text=title,
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.2),
            parent=dialog_box
        )
        
        # Message
        message_label = DirectLabel(
            text=message,
            text_scale=0.04,
            text_fg=(1, 1, 0.8, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.05),
            parent=dialog_box
        )
        
        # Confirm button
        confirm_button = DirectButton(
            text="Confirm",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.7, 0.3, 0.3, 0.8),
            frameSize=(-0.2, 0.2, -0.06, 0.06),
            relief=DGG.FLAT,
            pos=(-0.15, 0, -0.15),
            command=lambda: (confirm_callback(), dialog.destroy()),
            parent=dialog_box
        )
        
        # Cancel button
        cancel_button = DirectButton(
            text="Cancel",
            text_scale=0.04,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.3, 0.3, 0.6, 0.8),
            frameSize=(-0.2, 0.2, -0.06, 0.06),
            relief=DGG.FLAT,
            pos=(0.15, 0, -0.15),
            command=dialog.destroy,
            parent=dialog_box
        )
    
    def _confirm_main_menu(self):
        """Confirmed return to main menu"""
        # Implement main menu transition
        if hasattr(self.game, 'main_menu') and hasattr(self.game.main_menu, 'show'):
            # Show main menu
            self.game.main_menu.show()
            
            # Reset game state (optional, depending on implementation)
            if hasattr(self.game, 'reset_game_state'):
                self.game.reset_game_state()
    
    def _confirm_quit(self):
        """Confirmed quit game"""
        # Implement clean exit
        if hasattr(self.game, 'cleanup'):
            self.game.cleanup()
        
        # Exit the application
        self.game.userExit()
    
    def cleanup(self):
        """Clean up resources"""
        self.root.removeNode() 