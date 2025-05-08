#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Harmonization UI for Nightfall Defenders
Provides interface for harmonizing abilities
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode, TransparencyAttrib, Vec4

from game.ability_system import ElementType, AbilityType

class HarmonizationUI:
    """UI for harmonizing abilities"""
    
    def __init__(self, game):
        """
        Initialize the harmonization UI
        
        Args:
            game: Game instance
        """
        self.game = game
        self.visible = False
        self.selected_ability = None
        self.ability_buttons = []
        self.player = None
        
        # Create UI components
        self._create_ui()
        
        # Hide UI initially
        self.hide()
    
    def _create_ui(self):
        """Create the harmonization UI components"""
        # Main frame
        self.main_frame = DirectFrame(
            frameColor=(0.1, 0.2, 0.3, 0.8),
            frameSize=(-0.8, 0.8, -0.7, 0.7),
            pos=(0, 0, 0),
            relief=1
        )
        
        # Title
        self.title = OnscreenText(
            text="Ability Harmonization",
            parent=self.main_frame,
            scale=0.08,
            pos=(0, 0.6),
            fg=(0.7, 0.9, 1.0, 1.0),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Description
        self.description = OnscreenText(
            text="Select an ability to enhance its power through harmonization",
            parent=self.main_frame,
            scale=0.05,
            pos=(0, 0.5),
            fg=(0.8, 0.9, 1.0, 1.0)
        )
        
        # Selection frame
        self.selection_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.2, 0.3, 0.4, 0.7),
            frameSize=(-0.3, 0.3, -0.3, 0.3),
            pos=(0, 0, 0.2),
            relief=1
        )
        
        # Add label
        self.selection_label = DirectLabel(
            parent=self.selection_frame,
            text="Selected Ability",
            scale=0.05,
            pos=(0, 0, 0.33),
            text_fg=(0.9, 0.9, 0.9, 1.0)
        )
        
        # Add "Selected: None" text
        self.selected_text = OnscreenText(
            text="Selected: None",
            parent=self.selection_frame,
            scale=0.045,
            pos=(0, -0.35),
            fg=(0.8, 0.8, 0.8, 1.0)
        )
        
        # Harmonization result frame
        self.result_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.2, 0.4, 0.5, 0.7),
            frameSize=(-0.3, 0.3, -0.3, 0.3),
            pos=(0, 0, -0.2),
            relief=1
        )
        
        # Result label
        self.result_label = DirectLabel(
            parent=self.result_frame,
            text="Harmonization Result",
            scale=0.05,
            pos=(0, 0, 0.33),
            text_fg=(0.8, 1.0, 1.0, 1.0)
        )
        
        # Result description
        self.result_text = OnscreenText(
            text="Select an ability to see harmonization result",
            parent=self.result_frame,
            scale=0.04,
            pos=(0, 0),
            fg=(0.9, 0.9, 0.9, 1.0)
        )
        
        # Resource requirement text
        self.resource_text = OnscreenText(
            text="Required: 1 Harmonization Essence",
            parent=self.result_frame,
            scale=0.04,
            pos=(0, -0.35),
            fg=(0.9, 0.7, 0.7, 1.0)
        )
        
        # Harmonize button
        self.harmonize_button = DirectButton(
            parent=self.main_frame,
            text="Harmonize Ability",
            scale=0.07,
            pos=(0, 0, -0.5),
            pad=(0.2, 0.1),
            command=self._perform_harmonization,
            frameColor=(0.2, 0.4, 0.6, 0.8),
            relief=1,
            text_fg=(1, 1, 1, 1),
            pressEffect=True
        )
        
        # Close button
        self.close_button = DirectButton(
            parent=self.main_frame,
            text="Close",
            scale=0.06,
            pos=(0.7, 0, 0.6),
            pad=(0.1, 0.05),
            command=self.hide,
            frameColor=(0.5, 0.3, 0.3, 0.8),
            relief=1
        )
        
        # Ability selection area
        self.ability_scroll_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.15, 0.25, 0.35, 0.8),
            frameSize=(-0.75, 0.75, -0.65, -0.05),
            pos=(0, 0, -0.1),
            relief=1
        )
    
    def show(self, player):
        """
        Show the harmonization UI
        
        Args:
            player: Player instance
        """
        self.player = player
        self.visible = True
        self.main_frame.show()
        
        # Reset selection
        self.selected_ability = None
        self.selected_text.setText("Selected: None")
        if hasattr(self, 'selection_image') and self.selection_image:
            self.selection_image.destroy()
            self.selection_image = None
        
        # Update ability buttons
        self._update_ability_buttons()
        
        # Update result
        self._update_result_preview()
        
        # Update resource text
        self._update_resource_text()
        
        # Disable harmonize button initially
        self.harmonize_button['state'] = 'disabled'
    
    def hide(self):
        """Hide the harmonization UI"""
        self.visible = False
        self.main_frame.hide()
    
    def cleanup(self):
        """Clean up UI components"""
        self.main_frame.destroy()
        for button in self.ability_buttons:
            button.destroy()
    
    def _update_ability_buttons(self):
        """Update the ability selection buttons based on player's unlocked abilities"""
        # Clear existing buttons
        for button in self.ability_buttons:
            button.destroy()
        self.ability_buttons = []
        
        if not hasattr(self.player, 'ability_manager'):
            return
        
        # Get unlocked abilities
        ability_manager = self.player.ability_manager
        harmonizable_abilities = []
        
        for ability_id in ability_manager.unlocked_abilities:
            ability = ability_manager.get_ability(ability_id)
            # Only show abilities that can be harmonized (not already harmonized or fused)
            if ability and not ability.is_harmonized and not ability.is_fused:
                harmonizable_abilities.append(ability)
        
        # Create buttons
        button_width = 0.15
        button_height = 0.15
        buttons_per_row = 5
        spacing_x = 0.17
        spacing_y = 0.17
        start_x = -0.6
        start_y = -0.15
        
        for i, ability in enumerate(harmonizable_abilities):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            x = start_x + col * spacing_x
            y = start_y - row * spacing_y
            
            # Create button
            button = DirectButton(
                parent=self.ability_scroll_frame,
                frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
                pos=(x, 0, y),
                relief=1,
                frameColor=(0.2, 0.3, 0.4, 0.8),
                command=self._select_ability,
                extraArgs=[ability]
            )
            
            # Add ability name
            name = OnscreenText(
                text=ability.name,
                parent=button,
                scale=0.04,
                pos=(0, -button_height/2 - 0.03),
                fg=(0.9, 0.9, 0.9, 1.0)
            )
            
            # Add icon (placeholder with element color)
            element_color = self._get_element_color(ability.element_type)
            
            icon = DirectFrame(
                parent=button,
                frameSize=(-button_width/2 + 0.02, button_width/2 - 0.02, 
                           -button_height/2 + 0.02, button_height/2 - 0.02),
                frameColor=element_color,
                relief=1
            )
            
            element_text = OnscreenText(
                text=ability.element_type.value.capitalize(),
                parent=icon,
                scale=0.035,
                pos=(0, -0.03),
                fg=(0.2, 0.2, 0.2, 1.0)
            )
            
            self.ability_buttons.append(button)
    
    def _get_element_color(self, element_type):
        """Get a color based on element type"""
        element_colors = {
            ElementType.NONE: (0.8, 0.8, 0.8, 1.0),  # Gray
            ElementType.FIRE: (1.0, 0.4, 0.2, 1.0),  # Red-orange
            ElementType.ICE: (0.2, 0.6, 1.0, 1.0),   # Light blue
            ElementType.LIGHTNING: (0.8, 0.6, 1.0, 1.0),  # Purple
            ElementType.EARTH: (0.6, 0.4, 0.2, 1.0),  # Brown
            ElementType.WATER: (0.2, 0.4, 0.8, 1.0),  # Blue
            ElementType.WIND: (0.6, 0.9, 0.6, 1.0),   # Light green
            ElementType.ARCANE: (0.8, 0.2, 0.8, 1.0),  # Pink
            ElementType.HOLY: (1.0, 0.9, 0.5, 1.0),    # Gold
            ElementType.SHADOW: (0.3, 0.3, 0.4, 1.0)   # Dark blue-gray
        }
        return element_colors.get(element_type, (0.8, 0.8, 0.8, 1.0))
    
    def _select_ability(self, ability):
        """
        Select an ability for harmonization
        
        Args:
            ability: The ability to select
        """
        # Set selection
        self.selected_ability = ability
        
        # Update selection display
        self.selected_text.setText(f"Selected: {ability.name}")
        
        # Remove existing image if any
        if hasattr(self, 'selection_image') and self.selection_image:
            self.selection_image.destroy()
        
        # Create new image (placeholder)
        element_color = self._get_element_color(ability.element_type)
        
        self.selection_image = DirectFrame(
            parent=self.selection_frame,
            frameSize=(-0.2, 0.2, -0.2, 0.2),
            frameColor=element_color,
            pos=(0, 0, 0),
            relief=1
        )
        
        # Add ability type and element text
        type_text = OnscreenText(
            text=ability.ability_type.value.capitalize(),
            parent=self.selection_image,
            scale=0.04,
            pos=(0, 0.05),
            fg=(0.1, 0.1, 0.1, 1.0)
        )
        
        element_text = OnscreenText(
            text=ability.element_type.value.capitalize(),
            parent=self.selection_image,
            scale=0.04,
            pos=(0, -0.05),
            fg=(0.1, 0.1, 0.1, 1.0)
        )
        
        # Update result preview
        self._update_result_preview()
        
        # Enable harmonize button if resources are available
        self._update_button_state()
    
    def _update_result_preview(self):
        """Update the harmonization result preview based on selected ability"""
        if not self.selected_ability:
            self.result_text.setText("Select an ability to see harmonization result")
            return
        
        # Try to find a harmonization effect for this ability
        from game.harmonization_manager import HarmonizationManager
        manager = HarmonizationManager()
        effect = manager.find_effect(self.selected_ability)
        
        if effect:
            # Show effect-based harmonization result
            result_name = effect.name
            result_desc = effect.description
            
            self.result_text.setText(f"Result: {result_name}\n\n{result_desc}")
        else:
            # Show generic harmonization result
            self.result_text.setText(
                f"Result: Harmonized {self.selected_ability.name}\n\n"
                f"Enhanced version with 30% more damage but 20% longer cooldown."
            )
    
    def _update_resource_text(self):
        """Update the resource requirement text based on player's inventory"""
        resource_name = "harmonization_essence"
        resource_count = self.player.inventory.get(resource_name, 0)
        required = 1
        
        if resource_count >= required:
            self.resource_text.setText(f"Required: {required} {resource_name.replace('_', ' ').title()} ({resource_count} available)")
            self.resource_text.setFg((0.7, 1.0, 0.7, 1.0))  # Green
        else:
            self.resource_text.setText(f"Required: {required} {resource_name.replace('_', ' ').title()} ({resource_count} available - NOT ENOUGH)")
            self.resource_text.setFg((1.0, 0.5, 0.5, 1.0))  # Red
    
    def _update_button_state(self):
        """Update the harmonize button state based on selection and resources"""
        if not self.selected_ability:
            self.harmonize_button['state'] = 'disabled'
            return
        
        # Check if player has required resources
        resource_name = "harmonization_essence"
        resource_count = self.player.inventory.get(resource_name, 0)
        
        if resource_count >= 1:
            self.harmonize_button['state'] = 'normal'
        else:
            self.harmonize_button['state'] = 'disabled'
    
    def _perform_harmonization(self):
        """Perform the ability harmonization and add it to the player's abilities"""
        if not self.selected_ability:
            return
        
        # Harmonize the ability
        harmonized_id = self.player.harmonize_ability(self.selected_ability.ability_id)
        
        if harmonized_id:
            # Show success message
            harmonized_ability = self.player.ability_manager.get_ability(harmonized_id)
            self.result_text.setText(f"Harmonization successful!\n\nCreated: {harmonized_ability.name}")
            
            # Reset selection
            self.selected_ability = None
            self.selected_text.setText("Selected: None")
            if hasattr(self, 'selection_image') and self.selection_image:
                self.selection_image.destroy()
                self.selection_image = None
            
            # Update ability buttons
            self._update_ability_buttons()
            
            # Update resource text
            self._update_resource_text()
            
            # Disable harmonize button
            self.harmonize_button['state'] = 'disabled'
            
            # Update result preview
            self._update_result_preview()
        else:
            # Show failure message
            self.result_text.setText("Harmonization failed. Make sure you have enough resources.")
    
    def update(self, dt):
        """
        Update the UI
        
        Args:
            dt: Delta time
        """
        if not self.visible:
            return
        
        # Add any animations or dynamic updates here 