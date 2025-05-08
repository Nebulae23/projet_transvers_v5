#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Relic UI for Nightfall Defenders
Implements a UI for viewing and managing relics
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, CardMaker, NodePath

class RelicUI:
    """UI for displaying and managing relics"""
    
    def __init__(self, game):
        """
        Initialize the relic UI
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.visible = False
        
        # Create UI elements
        self._create_ui()
        
        # Hide the UI initially
        self.main_frame.hide()
    
    def _create_ui(self):
        """Create the UI elements"""
        # Main frame
        self.main_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.8, 0.8, -0.6, 0.6),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = OnscreenText(
            text="Relics",
            parent=self.main_frame,
            pos=(0, 0.5),
            scale=0.08,
            fg=(0.8, 0.6, 1.0, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Close button
        self.close_button = DirectButton(
            text="Close",
            scale=0.06,
            pad=(0.2, 0.2),
            command=self.hide,
            frameColor=(0.3, 0.3, 0.3, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pressEffect=1,
            parent=self.main_frame,
            pos=(0.7, 0, -0.54)
        )
        
        # Debug buttons for testing (add/remove relics)
        self.add_random_button = DirectButton(
            text="Add Random Relic",
            scale=0.06,
            pad=(0.2, 0.2),
            command=self._add_random_relic,
            frameColor=(0.2, 0.5, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pressEffect=1,
            parent=self.main_frame,
            pos=(-0.5, 0, -0.54)
        )
        
        # Create relic slots
        self.relic_slots = []
        self.relic_texts = []
        
        # How many slots to display
        max_slots = 3  # Match the max_active_relics in RelicSystem
        
        # Create slots
        for i in range(max_slots):
            slot = DirectFrame(
                frameColor=(0.15, 0.15, 0.15, 1.0),
                frameSize=(-0.3, 0.3, -0.2, 0.2),
                pos=(0, 0, 0.2 - i * 0.5),
                parent=self.main_frame
            )
            
            # Add empty slot text
            empty_text = OnscreenText(
                text="Empty Relic Slot",
                parent=slot,
                pos=(0, 0),
                scale=0.06,
                fg=(0.5, 0.5, 0.5, 1)
            )
            
            # Add a remove button (hidden initially)
            remove_button = DirectButton(
                text="X",
                scale=0.04,
                pad=(0.1, 0.1),
                command=self._remove_relic,
                extraArgs=[i],
                frameColor=(0.8, 0.2, 0.2, 0.8),
                text_fg=(1, 1, 1, 1),
                relief=DGG.FLAT,
                pressEffect=1,
                parent=slot,
                pos=(0.25, 0, 0.15)
            )
            remove_button.hide()
            
            # Store references
            slot.remove_button = remove_button
            slot.empty_text = empty_text
            slot.slot_index = i
            
            self.relic_slots.append(slot)
            
            # Create detailed text elements (hidden initially)
            relic_text = DirectFrame(
                frameColor=(0.2, 0.2, 0.2, 0),
                frameSize=(-0.28, 0.28, -0.18, 0.18),
                pos=(0, 0, 0),
                parent=slot
            )
            
            # Relic name
            relic_name = OnscreenText(
                text="",
                parent=relic_text,
                pos=(0, 0.12),
                scale=0.05,
                fg=(1, 1, 1, 1)
            )
            
            # Relic description
            relic_desc = OnscreenText(
                text="",
                parent=relic_text,
                pos=(0, 0),
                scale=0.04,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ACenter,
                wordwrap=14
            )
            
            # Rarity indicator
            relic_rarity = OnscreenText(
                text="",
                parent=relic_text,
                pos=(0, -0.14),
                scale=0.04,
                fg=(0.6, 0.6, 0.6, 1)
            )
            
            # Store text references
            relic_text.name_text = relic_name
            relic_text.desc_text = relic_desc
            relic_text.rarity_text = relic_rarity
            
            self.relic_texts.append(relic_text)
            relic_text.hide()
    
    def _add_random_relic(self):
        """Add a random relic for testing"""
        if not hasattr(self.game, 'relic_system'):
            print("Relic system not available")
            return
        
        # Get a random relic
        relic_id = self.game.relic_system.get_random_relic()
        if relic_id:
            success = self.game.relic_system.add_relic(relic_id)
            if success:
                self._update_relic_slots()
                # Show a message
                if hasattr(self.game, 'show_message'):
                    relic_name = self.game.relic_system.available_relics[relic_id]["name"]
                    self.game.show_message(f"Added {relic_name}")
        else:
            # Show a message that no more relics are available
            if hasattr(self.game, 'show_message'):
                self.game.show_message("No more relics available")
    
    def _remove_relic(self, slot_index):
        """Remove a relic from the specified slot"""
        if not hasattr(self.game, 'relic_system'):
            return
        
        # Get active relics
        active_relics = list(self.game.relic_system.active_relics.keys())
        
        # Check if the slot has a relic
        if slot_index < len(active_relics):
            relic_id = active_relics[slot_index]
            self.game.relic_system.remove_relic(relic_id)
            self._update_relic_slots()
    
    def _update_relic_slots(self):
        """Update the display of relic slots"""
        if not hasattr(self.game, 'relic_system'):
            return
        
        # Get active relics
        active_relics = list(self.game.relic_system.active_relics.keys())
        
        # Update each slot
        for i, slot in enumerate(self.relic_slots):
            # Check if this slot has a relic
            if i < len(active_relics):
                relic_id = active_relics[i]
                relic_info = self.game.relic_system.get_relic_info(relic_id)
                
                # Hide the empty text
                slot.empty_text.hide()
                
                # Show the remove button
                slot.remove_button.show()
                
                # Update and show the relic text
                relic_text = self.relic_texts[i]
                relic_text.name_text.setText(relic_info["name"])
                relic_text.desc_text.setText(relic_info["description"])
                
                # Set the rarity text and color
                rarity_text = relic_info["rarity"].capitalize()
                relic_text.rarity_text.setText(rarity_text)
                
                # Set rarity color
                if relic_info["rarity"] == "common":
                    relic_text.rarity_text.setFg((0.7, 0.7, 0.7, 1))  # Light gray
                elif relic_info["rarity"] == "uncommon":
                    relic_text.rarity_text.setFg((0.2, 0.7, 0.2, 1))  # Green
                elif relic_info["rarity"] == "rare":
                    relic_text.rarity_text.setFg((0.2, 0.2, 0.8, 1))  # Blue
                elif relic_info["rarity"] == "legendary":
                    relic_text.rarity_text.setFg((0.8, 0.6, 0.0, 1))  # Gold
                
                relic_text.show()
                
                # Change the background color based on rarity
                if relic_info["rarity"] == "common":
                    slot["frameColor"] = (0.2, 0.2, 0.2, 1.0)
                elif relic_info["rarity"] == "uncommon":
                    slot["frameColor"] = (0.1, 0.3, 0.1, 1.0)
                elif relic_info["rarity"] == "rare":
                    slot["frameColor"] = (0.1, 0.1, 0.3, 1.0)
                elif relic_info["rarity"] == "legendary":
                    slot["frameColor"] = (0.3, 0.2, 0.0, 1.0)
            else:
                # No relic in this slot
                slot.empty_text.show()
                slot.remove_button.hide()
                self.relic_texts[i].hide()
                slot["frameColor"] = (0.15, 0.15, 0.15, 1.0)
    
    def show(self):
        """Show the relic UI"""
        # Only show if we have a player and relic system
        if not hasattr(self.game, 'player') or not hasattr(self.game, 'relic_system'):
            print("Can't show relic UI: player or relic system not available")
            return
        
        # Update the UI based on current game state
        self._update_relic_slots()
        
        # Show the UI
        self.main_frame.show()
        self.visible = True
        
        # Pause the game
        if hasattr(self.game, 'pause_game'):
            self.game.pause_game()
    
    def hide(self):
        """Hide the relic UI"""
        self.main_frame.hide()
        self.visible = False
        
        # Unpause the game
        if hasattr(self.game, 'resume_game'):
            self.game.resume_game()
    
    def toggle(self):
        """Toggle the visibility of the relic UI"""
        if self.visible:
            self.hide()
        else:
            self.show() 