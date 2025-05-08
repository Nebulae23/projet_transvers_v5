#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class Selection UI for Nightfall Defenders
Implements the UI for selecting character classes
"""

from direct.gui.DirectGui import (
    DirectFrame, DirectButton, DirectLabel, 
    DGG, OnscreenText, OnscreenImage
)
from panda3d.core import (
    TextNode, TransparencyAttrib, LVector3f
)
from .character_class import ClassType

class ClassSelectionUI:
    """UI for selecting a character class"""
    
    def __init__(self, game, on_class_selected_callback=None):
        """
        Initialize the class selection UI
        
        Args:
            game: The game instance
            on_class_selected_callback: Callback function to call when class is selected
        """
        self.game = game
        self.selected_class = None
        self.on_class_selected_callback = on_class_selected_callback
        
        # Create UI elements
        self.create_ui()
        
        # Initialize ability factory for ability info
        from game.ability_factory import AbilityFactory
        self.ability_factory = AbilityFactory(game)
        
    def create_ui(self):
        """Create the UI elements"""
        # Get needed imports
        from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
        from panda3d.core import TextNode
        
        # Create main frame
        self.frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.2, 0.9),
            frameSize=(-1.0, 1.0, -0.8, 0.8),
            pos=(0, 0, 0),
            parent=self.game.aspect2d
        )
        self.frame.hide()
        
        # Title
        self.title = DirectLabel(
            text="Select Your Class",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.7),
            parent=self.frame
        )
        
        # Class buttons
        self.class_buttons = {}
        class_types = [
            {"name": "Warrior", "pos": (-0.7, 0, 0.4), "color": (0.7, 0.3, 0.3, 1)},
            {"name": "Mage", "pos": (-0.24, 0, 0.4), "color": (0.3, 0.3, 0.8, 1)},
            {"name": "Cleric", "pos": (0.24, 0, 0.4), "color": (0.8, 0.8, 0.2, 1)},
            {"name": "Alchemist", "pos": (-0.7, 0, 0.1), "color": (0.3, 0.7, 0.3, 1)},
            {"name": "Ranger", "pos": (-0.24, 0, 0.1), "color": (0.3, 0.7, 0.7, 1)},
            {"name": "Summoner", "pos": (0.24, 0, 0.1), "color": (0.7, 0.3, 0.7, 1)}
        ]
        
        for class_info in class_types:
            button = DirectButton(
                text=class_info["name"],
                text_fg=(1, 1, 1, 1),
                text_scale=0.05,
                frameColor=class_info["color"],
                frameSize=(-0.2, 0.2, -0.1, 0.1),
                pos=class_info["pos"],
                command=self.select_class,
                extraArgs=[class_info["name"].lower()],
                relief=DGG.FLAT,
                parent=self.frame
            )
            self.class_buttons[class_info["name"].lower()] = button
        
        # Class description
        self.class_description = DirectLabel(
            text="",
            text_fg=(1, 1, 1, 1),
            text_scale=0.04,
            frameColor=(0.2, 0.2, 0.3, 0.8),
            frameSize=(-0.9, 0.9, -0.2, 0.2),
            pos=(0, 0, -0.15),
            text_align=TextNode.ALeft,
            text_wordwrap=30,
            parent=self.frame
        )
        
        # Ability information
        self.ability_info = DirectLabel(
            text="",
            text_fg=(1, 1, 1, 1),
            text_scale=0.04,
            frameColor=(0.2, 0.2, 0.3, 0.8),
            frameSize=(-0.9, 0.9, -0.4, 0.4),
            pos=(0, 0, -0.5),
            text_align=TextNode.ALeft,
            text_wordwrap=30,
            parent=self.frame
        )
        
        # Confirm button
        self.confirm_button = DirectButton(
            text="Confirm Selection",
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            frameColor=(0.3, 0.6, 0.3, 1),
            frameSize=(-0.3, 0.3, -0.08, 0.08),
            pos=(0, 0, -0.7),
            command=self.confirm_selection,
            state=DGG.DISABLED,  # Start disabled until class is selected
            parent=self.frame
        )
    
    def select_class(self, class_type):
        """
        Handle class selection
        
        Args:
            class_type: The selected class type
        """
        # Update selected class
        self.selected_class = class_type
        
        # Highlight selected button
        for button_class, button in self.class_buttons.items():
            if button_class == class_type:
                # Selected button - add border
                button["frameColor"] = (1, 1, 1, 1)
            else:
                # Reset other buttons
                class_colors = {
                    "warrior": (0.7, 0.3, 0.3, 1),
                    "mage": (0.3, 0.3, 0.8, 1),
                    "cleric": (0.8, 0.8, 0.2, 1),
                    "alchemist": (0.3, 0.7, 0.3, 1),
                    "ranger": (0.3, 0.7, 0.7, 1),
                    "summoner": (0.7, 0.3, 0.7, 1)
                }
                button["frameColor"] = class_colors.get(button_class, (0.5, 0.5, 0.5, 1))
        
        # Update description
        class_descriptions = {
            "warrior": "A powerful melee fighter who excels at close combat. Warriors have high health and defense, and can deal significant damage with their axes and war hammers.",
            "mage": "A master of the arcane arts who can cast powerful spells from a distance. Mages have low health but can deal massive damage with their magical abilities.",
            "cleric": "A divine spellcaster who can heal allies and smite enemies. Clerics balance offense and defense, with abilities that support the team.",
            "alchemist": "A versatile inventor who uses potions, turrets, and chemical concoctions. Alchemists can control areas with deployable devices and status effects.",
            "ranger": "A skilled marksman who excels at long-range combat and traps. Rangers have high accuracy and can deal consistent damage from safety.",
            "summoner": "A mysterious spellcaster who calls forth spirits and elemental beings to fight. Summoners command an army of minions to overwhelm enemies."
        }
        
        self.class_description["text"] = class_descriptions.get(class_type, "No description available.")
        
        # Update ability information
        self.update_ability_info(class_type)
        
        # Enable confirm button
        self.confirm_button["state"] = DGG.NORMAL
        
    def update_ability_info(self, class_type):
        """
        Update the ability information for the selected class
        
        Args:
            class_type: The selected class type
        """
        abilities = self.ability_factory.get_ability_names_by_class(class_type)
        
        # Get more detailed ability information
        primary_info = self.get_primary_ability_info(class_type)
        secondary_info = self.get_secondary_abilities_info(class_type)
        
        # Combine information
        info_text = f"Primary Ability: {primary_info}\n\nSecondary Abilities:\n"
        for ability_info in secondary_info:
            info_text += f"• {ability_info}\n"
        
        self.ability_info["text"] = info_text
        
    def get_primary_ability_info(self, class_type):
        """Get formatted information about the primary ability"""
        try:
            ability_data = self.ability_factory.ability_definitions[class_type]["primary"]
            return f"{ability_data['name']}: {ability_data['description']}"
        except:
            return "Unknown ability"
            
    def get_secondary_abilities_info(self, class_type):
        """Get formatted information about secondary abilities"""
        result = []
        try:
            secondary_abilities = self.ability_factory.ability_definitions[class_type]["secondary"]
            for ability_name, ability_data in secondary_abilities.items():
                result.append(f"{ability_data['name']}: {ability_data['description']}")
        except:
            result.append("No secondary abilities defined")
            
        return result
        
    def confirm_selection(self):
        """Confirm the class selection"""
        if self.selected_class:
            # Call the callback if provided, otherwise fall back to game's method
            if self.on_class_selected_callback:
                self.on_class_selected_callback(self.selected_class)
            elif hasattr(self.game, 'on_class_selected'):
                self.game.on_class_selected(self.selected_class)
            
            # Hide the selection UI
            self.hide()
        
    def show(self):
        """Show the class selection UI"""
        self.frame.show()
        
    def hide(self):
        """Hide the class selection UI"""
        self.frame.hide()
        
    def cleanup(self):
        """Clean up the UI"""
        self.frame.destroy() 