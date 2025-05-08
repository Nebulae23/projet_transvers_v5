#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Menu System for Nightfall Defenders
Provides the game's main menu interface
"""

import os
from panda3d.core import NodePath, Vec3, Vec4, TextNode, TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

from engine.ui.button import Button

class MainMenuScene:
    """Main menu interface for the game"""
    
    def __init__(self, game):
        """
        Initialize the main menu
        
        Args:
            game: Main game instance
        """
        self.game = game
        
        # Create root node for all menu elements
        self.root = NodePath("main_menu_root")
        self.root.reparentTo(self.game.render2d)
        
        # Menu state
        self.current_menu = "main"  # main, options, save_browser, character_select
        
        # UI elements for different menus
        self.main_menu_elements = []
        self.options_menu_elements = []
        self.save_browser_elements = []
        self.character_select_elements = []
        
        # Background
        self.setup_background()
        
        # Create the main menu elements
        self.setup_main_menu()
        
        # Create the options menu (initially hidden)
        self.setup_options_menu()
        
        # Create the save browser (initially hidden)
        self.setup_save_browser()
        
        # Create the character selection menu (initially hidden)
        self.setup_character_select()
        
        # Show the main menu initially
        self.show_menu("main")
    
    def setup_background(self):
        """Set up the menu background"""
        # Background image
        try:
            self.background = OnscreenImage(
                image="src/assets/generated/ui/main_menu_bg.png",
                pos=(0, 0, 0),
                scale=(1.33, 1, 1)  # Adjusted for 16:9 aspect ratio
            )
            self.background.setTransparency(TransparencyAttrib.MAlpha)
            self.background.reparentTo(self.root)
        except:
            # Fallback to a colored background if image not found
            print("Warning: Main menu background image not found, using fallback")
            from direct.gui.DirectGui import DirectFrame
            self.background = DirectFrame(
                frameColor=(0.1, 0.1, 0.2, 1),
                frameSize=(-1.33, 1.33, -1, 1),
                parent=self.root
            )
        
        # Title
        self.title = OnscreenText(
            text="Nightfall Defenders",
            pos=(0, 0.7),
            scale=0.12,
            fg=(1, 0.9, 0.7, 1),
            shadow=(0.1, 0.1, 0.1, 0.5),
            shadowOffset=(0.04, 0.04),
            font=self.game.loader.loadFont("src/assets/fonts/main_title.ttf") if os.path.exists("src/assets/fonts/main_title.ttf") else None,
            parent=self.root,
            align=TextNode.ACenter
        )
        
        # Version text
        self.version_text = OnscreenText(
            text="Version 0.1.0",
            pos=(1.25, -0.95),
            scale=0.04,
            fg=(0.7, 0.7, 0.7, 1),
            parent=self.root,
            align=TextNode.ARight
        )
    
    def setup_main_menu(self):
        """Set up the main menu buttons"""
        button_width = 0.4
        button_height = 0.1
        button_spacing = 0.15
        start_y = 0.2
        
        # Container for main menu buttons
        self.main_menu_container = NodePath("main_menu_container")
        self.main_menu_container.reparentTo(self.root)
        
        # Continue button (only enabled if saves exist)
        self.continue_button = Button(
            self.game,
            text="Continue Game",
            position=(0, start_y, 0),
            size=(button_width, button_height),
            parent=self.main_menu_container,
            command=self.on_continue,
            disabled=not self._has_save_games()
        )
        self.main_menu_elements.append(self.continue_button)
        
        # New Game button
        self.new_game_button = Button(
            self.game,
            text="New Game",
            position=(0, start_y - button_spacing, 0),
            size=(button_width, button_height),
            parent=self.main_menu_container,
            command=self.on_new_game
        )
        self.main_menu_elements.append(self.new_game_button)
        
        # Load Game button
        self.load_game_button = Button(
            self.game,
            text="Load Game",
            position=(0, start_y - button_spacing * 2, 0),
            size=(button_width, button_height),
            parent=self.main_menu_container,
            command=self.on_load_game,
            disabled=not self._has_save_games()
        )
        self.main_menu_elements.append(self.load_game_button)
        
        # Options button
        self.options_button = Button(
            self.game,
            text="Options",
            position=(0, start_y - button_spacing * 3, 0),
            size=(button_width, button_height),
            parent=self.main_menu_container,
            command=self.on_options
        )
        self.main_menu_elements.append(self.options_button)
        
        # Quit button
        self.quit_button = Button(
            self.game,
            text="Quit",
            position=(0, start_y - button_spacing * 4, 0),
            size=(button_width, button_height),
            parent=self.main_menu_container,
            command=self.on_quit
        )
        self.main_menu_elements.append(self.quit_button)
        
        # Hide the main menu initially
        self.main_menu_container.hide()
    
    def setup_options_menu(self):
        """Set up the options menu"""
        # Container for options menu
        self.options_menu_container = NodePath("options_menu_container")
        self.options_menu_container.reparentTo(self.root)
        
        # Options header
        self.options_header = OnscreenText(
            text="Options",
            pos=(0, 0.6),
            scale=0.08,
            fg=(1, 0.9, 0.7, 1),
            shadow=(0.1, 0.1, 0.1, 0.5),
            shadowOffset=(0.03, 0.03),
            parent=self.options_menu_container,
            align=TextNode.ACenter
        )
        self.options_menu_elements.append(self.options_header)
        
        # TODO: Add actual options controls (graphics, audio, gameplay, etc.)
        # For now, just add a placeholder text
        self.options_placeholder = OnscreenText(
            text="Options coming soon...",
            pos=(0, 0.2),
            scale=0.06,
            fg=(0.9, 0.9, 0.9, 1),
            parent=self.options_menu_container,
            align=TextNode.ACenter
        )
        self.options_menu_elements.append(self.options_placeholder)
        
        # Back button
        self.options_back_button = Button(
            self.game,
            text="Back",
            position=(0, -0.6, 0),
            size=(0.4, 0.1),
            parent=self.options_menu_container,
            command=lambda: self.show_menu("main")
        )
        self.options_menu_elements.append(self.options_back_button)
        
        # Hide the options menu initially
        self.options_menu_container.hide()
    
    def setup_save_browser(self):
        """Set up the save game browser"""
        # Container for save browser
        self.save_browser_container = NodePath("save_browser_container")
        self.save_browser_container.reparentTo(self.root)
        
        # Save browser header
        self.save_browser_header = OnscreenText(
            text="Load Game",
            pos=(0, 0.7),
            scale=0.08,
            fg=(1, 0.9, 0.7, 1),
            shadow=(0.1, 0.1, 0.1, 0.5),
            shadowOffset=(0.03, 0.03),
            parent=self.save_browser_container,
            align=TextNode.ACenter
        )
        self.save_browser_elements.append(self.save_browser_header)
        
        # Save slot container (populated when shown)
        self.save_slots_container = NodePath("save_slots_container")
        self.save_slots_container.reparentTo(self.save_browser_container)
        
        # Back button
        self.save_browser_back_button = Button(
            self.game,
            text="Back",
            position=(0, -0.8, 0),
            size=(0.4, 0.1),
            parent=self.save_browser_container,
            command=lambda: self.show_menu("main")
        )
        self.save_browser_elements.append(self.save_browser_back_button)
        
        # Save slots will be dynamically created when the menu is shown
        self.save_slot_elements = []
        
        # Hide the save browser initially
        self.save_browser_container.hide()
    
    def setup_character_select(self):
        """Set up the character selection menu"""
        # Container for character selection
        self.character_select_container = NodePath("character_select_container")
        self.character_select_container.reparentTo(self.root)
        
        # Character selection header
        self.character_select_header = OnscreenText(
            text="Select Character",
            pos=(0, 0.7),
            scale=0.08,
            fg=(1, 0.9, 0.7, 1),
            shadow=(0.1, 0.1, 0.1, 0.5),
            shadowOffset=(0.03, 0.03),
            parent=self.character_select_container,
            align=TextNode.ACenter
        )
        self.character_select_elements.append(self.character_select_header)
        
        # Character classes from the PRD
        character_classes = [
            {"name": "Warrior", "description": "Melee specialist with high defense and close-range abilities"},
            {"name": "Mage", "description": "Ranged specialist with elemental-based abilities and low defense"},
            {"name": "Cleric", "description": "Support character with healing abilities and medium defense"},
            {"name": "Alchemist", "description": "Versatile character with potion-based abilities and utility"},
            {"name": "Ranger", "description": "Ranged physical damage dealer with traps and evasion"},
            {"name": "Summoner", "description": "Pet-based class that commands allies"}
        ]
        
        # Character selection buttons
        button_width = 0.35
        button_height = 0.1
        button_spacing = 0.12
        start_y = 0.4
        buttons_per_row = 2
        button_x_offset = 0.4
        
        for i, character_class in enumerate(character_classes):
            # Calculate position
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = col * button_x_offset * 2 - (button_x_offset if buttons_per_row > 1 else 0)
            y = start_y - row * button_spacing * 2
            
            # Create button
            button = Button(
                self.game,
                text=character_class["name"],
                position=(x, y, 0),
                size=(button_width, button_height),
                parent=self.character_select_container,
                command=lambda c=character_class["name"]: self.on_character_selected(c)
            )
            self.character_select_elements.append(button)
            
            # Create description text
            description = OnscreenText(
                text=character_class["description"],
                pos=(x, y - button_spacing),
                scale=0.04,
                fg=(0.9, 0.9, 0.9, 1),
                parent=self.character_select_container,
                align=TextNode.ACenter,
                wordwrap=15
            )
            self.character_select_elements.append(description)
        
        # Back button
        self.character_select_back_button = Button(
            self.game,
            text="Back",
            position=(0, -0.8, 0),
            size=(0.4, 0.1),
            parent=self.character_select_container,
            command=lambda: self.show_menu("main")
        )
        self.character_select_elements.append(self.character_select_back_button)
        
        # Hide the character selection menu initially
        self.character_select_container.hide()
    
    def show_menu(self, menu_name):
        """
        Show a specific menu and hide others
        
        Args:
            menu_name: Name of the menu to show ("main", "options", "save_browser", "character_select")
        """
        # Hide all menus first
        self.main_menu_container.hide()
        self.options_menu_container.hide()
        self.save_browser_container.hide()
        self.character_select_container.hide()
        
        # Show the requested menu
        if menu_name == "main":
            self.main_menu_container.show()
            # Update continue and load buttons based on save existence
            has_saves = self._has_save_games()
            self.continue_button.enable() if has_saves else self.continue_button.disable()
            self.load_game_button.enable() if has_saves else self.load_game_button.disable()
        elif menu_name == "options":
            self.options_menu_container.show()
        elif menu_name == "save_browser":
            # Populate save slots before showing
            self._populate_save_slots()
            self.save_browser_container.show()
        elif menu_name == "character_select":
            self.character_select_container.show()
        
        # Update current menu
        self.current_menu = menu_name
    
    def _has_save_games(self):
        """
        Check if there are any save games available
        
        Returns:
            bool: True if save games exist, False otherwise
        """
        if hasattr(self.game, "save_manager"):
            save_slots = self.game.save_manager.get_save_slots()
            return len(save_slots) > 0
        return False
    
    def _populate_save_slots(self):
        """Populate the save slots in the save browser"""
        # Clear existing save slots
        for element in self.save_slot_elements:
            element.cleanup()
        self.save_slot_elements = []
        
        # Get save slots from save manager
        if hasattr(self.game, "save_manager"):
            save_slots = self.game.save_manager.get_save_slots()
            
            if not save_slots:
                # No save slots, show message
                no_saves_text = OnscreenText(
                    text="No saved games found",
                    pos=(0, 0),
                    scale=0.06,
                    fg=(0.9, 0.9, 0.9, 1),
                    parent=self.save_slots_container,
                    align=TextNode.ACenter
                )
                self.save_slot_elements.append(no_saves_text)
                return
            
            # Display save slots
            slot_width = 0.8
            slot_height = 0.15
            slot_spacing = 0.17
            max_slots = 5  # Maximum number of slots to show at once
            start_y = 0.5
            
            for i, slot in enumerate(save_slots[:max_slots]):
                # Create a frame for the save slot
                from direct.gui.DirectGui import DirectFrame
                slot_frame = DirectFrame(
                    frameSize=(-slot_width/2, slot_width/2, -slot_height/2, slot_height/2),
                    frameColor=(0.2, 0.2, 0.2, 0.8),
                    pos=(0, 0, start_y - i * slot_spacing),
                    parent=self.save_slots_container
                )
                
                # Add slot information
                slot_title = OnscreenText(
                    text=slot["display_name"],
                    pos=(-slot_width/2 + 0.05, 0.02),
                    scale=0.05,
                    fg=(1, 1, 1, 1),
                    align=TextNode.ALeft,
                    parent=slot_frame
                )
                
                slot_info = OnscreenText(
                    text=f"{slot['character']} (Level {slot['level']}) - {slot['date']} - {slot['play_time']}",
                    pos=(-slot_width/2 + 0.05, -0.03),
                    scale=0.04,
                    fg=(0.8, 0.8, 0.8, 1),
                    align=TextNode.ALeft,
                    parent=slot_frame
                )
                
                # Load button
                load_button = Button(
                    self.game,
                    text="Load",
                    position=(slot_width/2 - 0.1, 0, 0),
                    size=(0.15, 0.08),
                    parent=slot_frame,
                    command=lambda s=slot["slot_name"]: self.on_load_slot(s)
                )
                
                # Delete button
                delete_button = Button(
                    self.game,
                    text="Delete",
                    position=(slot_width/2 - 0.3, 0, 0),
                    size=(0.15, 0.08),
                    parent=slot_frame,
                    command=lambda s=slot["slot_name"]: self.on_delete_slot(s)
                )
                
                # Add thumbnail if available
                if slot["has_thumbnail"]:
                    from direct.gui.OnscreenImage import OnscreenImage
                    thumbnail = OnscreenImage(
                        image=slot["thumbnail_path"],
                        pos=(-slot_width/2 + 0.18, 0, 0),
                        scale=(0.1, 1, 0.06),
                        parent=slot_frame
                    )
                    thumbnail.setTransparency(TransparencyAttrib.MAlpha)
                    self.save_slot_elements.append(thumbnail)
                
                # Add elements to cleanup list
                self.save_slot_elements.extend([slot_frame, slot_title, slot_info, load_button, delete_button])
    
    def on_continue(self):
        """Handle continue button click - load most recent save"""
        if hasattr(self.game, "save_manager"):
            save_slots = self.game.save_manager.get_save_slots()
            if save_slots:
                # Get the most recent save (first in the sorted list)
                most_recent = save_slots[0]
                self.on_load_slot(most_recent["slot_name"])
    
    def on_new_game(self):
        """Handle new game button click - show character selection"""
        self.show_menu("character_select")
    
    def on_load_game(self):
        """Handle load game button click - show save browser"""
        self.show_menu("save_browser")
    
    def on_options(self):
        """Handle options button click - show options menu"""
        self.show_menu("options")
    
    def on_quit(self):
        """Handle quit button click - exit the game"""
        self.game.userExit()
    
    def on_character_selected(self, character_class):
        """
        Handle character selection
        
        Args:
            character_class: Name of the selected character class
        """
        print(f"Selected character class: {character_class}")
        
        # TODO: Start new game with selected character
        if hasattr(self.game, "scene_manager"):
            self.game.scene_manager.change_scene("game")
    
    def on_load_slot(self, slot_name):
        """
        Handle loading a save slot
        
        Args:
            slot_name: Name of the save slot to load
        """
        print(f"Loading save slot: {slot_name}")
        
        # Load the save
        if hasattr(self.game, "save_manager"):
            if self.game.save_manager.load_game(slot_name):
                # Change to game scene
                if hasattr(self.game, "scene_manager"):
                    self.game.scene_manager.change_scene("game")
    
    def on_delete_slot(self, slot_name):
        """
        Handle deleting a save slot
        
        Args:
            slot_name: Name of the save slot to delete
        """
        print(f"Deleting save slot: {slot_name}")
        
        # Show confirmation dialog
        self._show_delete_confirmation(slot_name)
    
    def _show_delete_confirmation(self, slot_name):
        """
        Show a confirmation dialog for deleting a save
        
        Args:
            slot_name: Name of the save slot to delete
        """
        # Create a semi-transparent overlay
        from direct.gui.DirectGui import DirectFrame
        overlay = DirectFrame(
            frameColor=(0, 0, 0, 0.7),
            frameSize=(-2, 2, -2, 2),
            parent=self.root
        )
        
        # Create confirmation dialog
        dialog_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-0.4, 0.4, -0.3, 0.3),
            parent=overlay
        )
        
        # Confirmation text
        confirmation_text = OnscreenText(
            text=f"Are you sure you want to delete the save '{slot_name}'?",
            pos=(0, 0.1),
            scale=0.05,
            fg=(1, 1, 1, 1),
            parent=dialog_frame,
            align=TextNode.ACenter,
            wordwrap=15
        )
        
        # Yes button
        yes_button = Button(
            self.game,
            text="Yes",
            position=(-0.15, -0.15, 0),
            size=(0.15, 0.1),
            parent=dialog_frame,
            command=lambda: self._confirm_delete(slot_name, overlay)
        )
        
        # No button
        no_button = Button(
            self.game,
            text="No",
            position=(0.15, -0.15, 0),
            size=(0.15, 0.1),
            parent=dialog_frame,
            command=lambda: overlay.destroy()
        )
    
    def _confirm_delete(self, slot_name, overlay):
        """
        Confirm deletion of a save slot
        
        Args:
            slot_name: Name of the save slot to delete
            overlay: Confirmation dialog overlay to remove
        """
        # Delete the save
        if hasattr(self.game, "save_manager"):
            if self.game.save_manager.delete_save(slot_name):
                # Refresh save slots
                self._populate_save_slots()
        
        # Remove confirmation dialog
        overlay.destroy()
    
    def cleanup(self):
        """Clean up resources"""
        # Clean up all UI elements
        for element in (
            self.main_menu_elements + 
            self.options_menu_elements + 
            self.save_browser_elements + 
            self.character_select_elements +
            self.save_slot_elements
        ):
            if hasattr(element, 'cleanup'):
                element.cleanup()
        
        # Remove the root node
        self.root.removeNode() 