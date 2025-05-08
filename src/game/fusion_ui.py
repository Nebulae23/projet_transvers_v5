#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fusion UI for Nightfall Defenders
Provides interface for selecting and fusing abilities
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode, TransparencyAttrib, Vec4

from game.ability_system import ElementType, AbilityType

class FusionUI:
    """UI for selecting and fusing abilities"""
    
    def __init__(self, game):
        """
        Initialize the fusion UI
        
        Args:
            game: Game instance
        """
        self.game = game
        self.visible = False
        self.selection = [None, None]  # Selected abilities
        self.ability_buttons = []
        self.player = None
        
        # Create UI components
        self._create_ui()
        
        # Hide UI initially
        self.hide()
    
    def _create_ui(self):
        """Create the fusion UI components"""
        # Main frame
        self.main_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.3, 0.8),
            frameSize=(-0.9, 0.9, -0.7, 0.7),
            pos=(0, 0, 0),
            relief=1
        )
        
        # Title
        self.title = OnscreenText(
            text="Ability Fusion",
            parent=self.main_frame,
            scale=0.08,
            pos=(0, 0.6),
            fg=(0.9, 0.7, 1.0, 1.0),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Description
        self.description = OnscreenText(
            text="Select two abilities to fuse them into a new ability",
            parent=self.main_frame,
            scale=0.05,
            pos=(0, 0.5),
            fg=(0.8, 0.8, 1.0, 1.0)
        )
        
        # Selection frames
        self.selection_frames = []
        for i in range(2):
            frame = DirectFrame(
                parent=self.main_frame,
                frameColor=(0.2, 0.2, 0.4, 0.7),
                frameSize=(-0.2, 0.2, -0.2, 0.2),
                pos=(-0.4 + i * 0.8, 0, 0.2),
                relief=1
            )
            
            # Add label
            label = DirectLabel(
                parent=frame,
                text=f"Ability {i+1}",
                scale=0.05,
                pos=(0, 0, 0.23),
                text_fg=(0.9, 0.9, 0.9, 1.0)
            )
            
            # Add "Selected: None" text
            selected_text = OnscreenText(
                text="Selected: None",
                parent=frame,
                scale=0.045,
                pos=(0, -0.25),
                fg=(0.8, 0.8, 0.8, 1.0)
            )
            
            # Store components
            self.selection_frames.append({
                'frame': frame,
                'label': label,
                'selected_text': selected_text,
                'image': None
            })
        
        # Fusion result frame
        self.result_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.3, 0.2, 0.5, 0.7),
            frameSize=(-0.25, 0.25, -0.25, 0.25),
            pos=(0, 0, -0.2),
            relief=1
        )
        
        # Result label
        self.result_label = DirectLabel(
            parent=self.result_frame,
            text="Fusion Result",
            scale=0.05,
            pos=(0, 0, 0.28),
            text_fg=(1.0, 0.8, 1.0, 1.0)
        )
        
        # Result description
        self.result_text = OnscreenText(
            text="Select two abilities to see result",
            parent=self.result_frame,
            scale=0.04,
            pos=(0, -0.3),
            fg=(0.9, 0.9, 0.9, 1.0)
        )
        
        # Fusion button
        self.fusion_button = DirectButton(
            parent=self.main_frame,
            text="Fuse Abilities",
            scale=0.07,
            pos=(0, 0, -0.5),
            pad=(0.2, 0.1),
            command=self._perform_fusion,
            frameColor=(0.4, 0.2, 0.6, 0.8),
            relief=1,
            text_fg=(1, 1, 1, 1),
            pressEffect=True
        )
        
        # Close button
        self.close_button = DirectButton(
            parent=self.main_frame,
            text="Close",
            scale=0.06,
            pos=(0.8, 0, 0.6),
            pad=(0.1, 0.05),
            command=self.hide,
            frameColor=(0.5, 0.3, 0.3, 0.8),
            relief=1
        )
        
        # Ability selection area
        self.ability_scroll_frame = DirectFrame(
            parent=self.main_frame,
            frameColor=(0.15, 0.15, 0.25, 0.8),
            frameSize=(-0.85, 0.85, -0.65, -0.05),
            pos=(0, 0, -0.1),
            relief=1
        )
    
    def show(self, player):
        """
        Show the fusion UI
        
        Args:
            player: Player instance
        """
        self.player = player
        self.visible = True
        self.main_frame.show()
        
        # Reset selection
        self.selection = [None, None]
        for i in range(2):
            self.selection_frames[i]['selected_text'].setText("Selected: None")
            if self.selection_frames[i]['image']:
                self.selection_frames[i]['image'].destroy()
                self.selection_frames[i]['image'] = None
        
        # Update ability buttons
        self._update_ability_buttons()
        
        # Update result
        self._update_result_preview()
        
        # Disable fusion button initially
        self.fusion_button['state'] = 'disabled'
    
    def hide(self):
        """Hide the fusion UI"""
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
        unlocked_abilities = []
        
        for ability_id in ability_manager.unlocked_abilities:
            ability = ability_manager.get_ability(ability_id)
            if ability and not ability.is_fused:  # Only show non-fusion abilities
                unlocked_abilities.append(ability)
        
        # Create buttons
        button_width = 0.15
        button_height = 0.15
        buttons_per_row = 5
        spacing_x = 0.17
        spacing_y = 0.17
        start_x = -0.7
        start_y = -0.15
        
        for i, ability in enumerate(unlocked_abilities):
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
                frameColor=(0.2, 0.2, 0.3, 0.8),
                command=self._select_ability,
                extraArgs=[ability, i]
            )
            
            # Add ability name
            name = OnscreenText(
                text=ability.name,
                parent=button,
                scale=0.04,
                pos=(0, -button_height/2 - 0.03),
                fg=(0.9, 0.9, 0.9, 1.0)
            )
            
            # Add icon (placeholder text for now)
            element_color = (0.8, 0.8, 0.8, 1.0)  # Default color
            if ability.element_type.value == "fire":
                element_color = (1.0, 0.4, 0.2, 1.0)
            elif ability.element_type.value == "ice":
                element_color = (0.2, 0.6, 1.0, 1.0)
            elif ability.element_type.value == "lightning":
                element_color = (0.8, 0.6, 1.0, 1.0)
            elif ability.element_type.value == "earth":
                element_color = (0.6, 0.4, 0.2, 1.0)
            elif ability.element_type.value == "water":
                element_color = (0.2, 0.4, 0.8, 1.0)
            elif ability.element_type.value == "wind":
                element_color = (0.6, 0.9, 0.6, 1.0)
            elif ability.element_type.value == "arcane":
                element_color = (0.8, 0.2, 0.8, 1.0)
            
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
    
    def _select_ability(self, ability, button_index):
        """
        Select an ability for fusion
        
        Args:
            ability: The ability to select
            button_index: Index of the button that was clicked
        """
        # Determine which selection slot to use
        slot = 0 if self.selection[1] is not None else 1
        if self.selection[0] is not None and self.selection[1] is not None:
            # Both slots are full, replace slot 0
            slot = 0
        
        # Set selection
        self.selection[slot] = ability
        
        # Update selection display
        self._update_selection_display(slot, ability)
        
        # Update result preview
        self._update_result_preview()
        
        # Enable fusion button if both abilities are selected
        if self.selection[0] is not None and self.selection[1] is not None:
            self.fusion_button['state'] = 'normal'
        else:
            self.fusion_button['state'] = 'disabled'
    
    def _update_selection_display(self, slot, ability):
        """
        Update the display of a selected ability
        
        Args:
            slot: Selection slot (0 or 1)
            ability: The selected ability
        """
        # Update text
        self.selection_frames[slot]['selected_text'].setText(f"Selected: {ability.name}")
        
        # Remove existing image if any
        if self.selection_frames[slot]['image']:
            self.selection_frames[slot]['image'].destroy()
        
        # Create new image (placeholder)
        element_color = (0.8, 0.8, 0.8, 1.0)  # Default color
        if ability.element_type.value == "fire":
            element_color = (1.0, 0.4, 0.2, 1.0)
        elif ability.element_type.value == "ice":
            element_color = (0.2, 0.6, 1.0, 1.0)
        elif ability.element_type.value == "lightning":
            element_color = (0.8, 0.6, 1.0, 1.0)
        elif ability.element_type.value == "earth":
            element_color = (0.6, 0.4, 0.2, 1.0)
        elif ability.element_type.value == "water":
            element_color = (0.2, 0.4, 0.8, 1.0)
        elif ability.element_type.value == "wind":
            element_color = (0.6, 0.9, 0.6, 1.0)
        elif ability.element_type.value == "arcane":
            element_color = (0.8, 0.2, 0.8, 1.0)
        
        image = DirectFrame(
            parent=self.selection_frames[slot]['frame'],
            frameSize=(-0.15, 0.15, -0.15, 0.15),
            frameColor=element_color,
            pos=(0, 0, 0),
            relief=1
        )
        
        # Add ability type and element text
        type_text = OnscreenText(
            text=ability.ability_type.value.capitalize(),
            parent=image,
            scale=0.04,
            pos=(0, 0.03),
            fg=(0.1, 0.1, 0.1, 1.0)
        )
        
        element_text = OnscreenText(
            text=ability.element_type.value.capitalize(),
            parent=image,
            scale=0.04,
            pos=(0, -0.05),
            fg=(0.1, 0.1, 0.1, 1.0)
        )
        
        self.selection_frames[slot]['image'] = image
    
    def _update_result_preview(self):
        """Update the fusion result preview based on selected abilities"""
        if self.selection[0] is None or self.selection[1] is None:
            self.result_text.setText("Select two abilities to see result")
            return
        
        ability1 = self.selection[0]
        ability2 = self.selection[1]
        
        # Check if fusion is possible
        if not ability1.can_fuse_with(ability2):
            self.result_text.setText("These abilities cannot be fused")
            return
        
        # Check if player has unlocked the appropriate fusion type
        if ability1.element_type != ElementType.NONE and ability2.element_type != ElementType.NONE:
            # For elemental fusions, check if player has unlocked elemental fusion
            if not getattr(self.player, 'can_use_elemental_fusion', False):
                self.result_text.setText("Elemental fusion not unlocked")
                self.fusion_button['state'] = 'disabled'
                return
        
        if (ability1.ability_type == AbilityType.MELEE or ability1.ability_type == AbilityType.PROJECTILE) and \
           (ability2.ability_type == AbilityType.MELEE or ability2.ability_type == AbilityType.PROJECTILE):
            # For weapon fusions, check if player has unlocked weapon fusion
            if not getattr(self.player, 'can_use_divine_weapon_fusion', False):
                self.result_text.setText("Weapon fusion not unlocked")
                self.fusion_button['state'] = 'disabled'
                return
        
        # Get fusion recipe
        from game.fusion_recipe_manager import FusionRecipeManager
        recipe_manager = FusionRecipeManager()
        recipe = recipe_manager.find_recipe(ability1, ability2)
        
        if recipe:
            # Show recipe-based fusion result
            self.result_text.setText(f"Result: {recipe.name}\n{recipe.description}")
        else:
            # Show generic fusion result
            self.result_text.setText(f"Result: {ability1.name} + {ability2.name}\nA fusion of {ability1.name} and {ability2.name}.")
    
    def _perform_fusion(self):
        """Perform the ability fusion and add it to the player's abilities"""
        if self.selection[0] is None or self.selection[1] is None:
            return
        
        ability1 = self.selection[0]
        ability2 = self.selection[1]
        
        if not hasattr(self.player, 'ability_manager'):
            return
        
        # Create fusion
        ability_manager = self.player.ability_manager
        fusion_id = ability_manager.create_fusion(ability1.ability_id, ability2.ability_id)
        
        if fusion_id:
            # Show success message
            self.result_text.setText("Fusion successful!\nNew ability added to your abilities.")
            
            # Reset selection
            self.selection = [None, None]
            for i in range(2):
                self.selection_frames[i]['selected_text'].setText("Selected: None")
                if self.selection_frames[i]['image']:
                    self.selection_frames[i]['image'].destroy()
                    self.selection_frames[i]['image'] = None
            
            # Update ability buttons
            self._update_ability_buttons()
            
            # Disable fusion button
            self.fusion_button['state'] = 'disabled'
        else:
            # Show failure message
            self.result_text.setText("Fusion failed. These abilities cannot be fused.")
    
    def update(self, dt):
        """
        Update the UI
        
        Args:
            dt: Delta time
        """
        if not self.visible:
            return
        
        # Add any animations or dynamic updates here 