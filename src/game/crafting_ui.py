#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crafting UI for Nightfall Defenders
Implements a simple UI for the crafting system
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

class CraftingUI:
    """UI for interacting with the crafting system"""
    
    def __init__(self, game):
        """
        Initialize the crafting UI
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.visible = False
        self.current_recipe = None
        
        # Create UI elements
        self._create_ui()
        
        # Hide the UI initially without calling hide()
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
            text="Crafting Station",
            parent=self.main_frame,
            pos=(0, 0.5),
            scale=0.08,
            fg=(1, 0.9, 0.3, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Create recipe buttons
        self.recipe_buttons = {}
        self.recipe_labels = {}
        
        # Add close button
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
        
        # Recipe information frame
        self.info_frame = DirectFrame(
            frameColor=(0.15, 0.15, 0.15, 1.0),
            frameSize=(-0.35, 0.35, -0.25, 0.25),
            pos=(0.4, 0, 0.1),
            parent=self.main_frame
        )
        
        # Recipe info labels
        self.recipe_name = OnscreenText(
            text="Select a Recipe",
            parent=self.info_frame,
            pos=(0, 0.20),
            scale=0.06,
            fg=(1, 1, 1, 1)
        )
        
        self.recipe_description = OnscreenText(
            text="",
            parent=self.info_frame,
            pos=(0, 0.10),
            scale=0.04,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            wordwrap=15
        )
        
        self.recipe_level = OnscreenText(
            text="",
            parent=self.info_frame,
            pos=(0, 0.0),
            scale=0.05,
            fg=(0.2, 0.8, 0.2, 1)
        )
        
        self.recipe_cost = OnscreenText(
            text="",
            parent=self.info_frame,
            pos=(0, -0.1),
            scale=0.04,
            fg=(0.9, 0.9, 0.6, 1),
            align=TextNode.ACenter,
            wordwrap=15
        )
        
        # Craft button
        self.craft_button = DirectButton(
            text="Craft",
            scale=0.06,
            pad=(0.2, 0.2),
            command=self._craft_selected,
            frameColor=(0.2, 0.5, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            relief=DGG.FLAT,
            pressEffect=1,
            parent=self.info_frame,
            pos=(0, 0, -0.2)
        )
        
        # Inventory display
        self.inventory_frame = DirectFrame(
            frameColor=(0.15, 0.15, 0.15, 1.0),
            frameSize=(-0.35, 0.35, -0.18, 0.18),
            pos=(0.4, 0, -0.35),
            parent=self.main_frame
        )
        
        self.inventory_title = OnscreenText(
            text="Inventory",
            parent=self.inventory_frame,
            pos=(0, 0.12),
            scale=0.05,
            fg=(0.8, 0.8, 1, 1)
        )
        
        self.inventory_text = OnscreenText(
            text="",
            parent=self.inventory_frame,
            pos=(0, -0.02),
            scale=0.04,
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            wordwrap=18
        )
    
    def _create_recipe_buttons(self):
        """Create buttons for each recipe"""
        # Clear existing buttons
        for button in self.recipe_buttons.values():
            button.destroy()
        
        self.recipe_buttons = {}
        
        # Get all recipes info
        recipes = self.game.crafting_system.get_all_recipes_info()
        
        # Create a button for each recipe
        for i, recipe in enumerate(recipes):
            button = DirectButton(
                text=recipe["name"],
                scale=0.05,
                frameSize=(-0.4, 0.4, -0.4, 0.4),
                pad=(0.3, 0.1),
                command=self._select_recipe,
                extraArgs=[recipe["id"]],
                frameColor=(0.3, 0.3, 0.3, 0.8),
                text_fg=(1, 1, 1, 1),
                relief=DGG.FLAT,
                pressEffect=1,
                parent=self.main_frame,
                pos=(-0.4, 0, 0.3 - i * 0.12)
            )
            
            # Add level indicator
            level_text = f"Lv. {recipe['current_level']}/{recipe['max_level']}"
            level_label = OnscreenText(
                text=level_text,
                parent=button,
                pos=(0.25, -0.02),
                scale=0.7,
                fg=(0.2, 0.8, 0.2, 1) if recipe["current_level"] > 0 else (0.7, 0.7, 0.7, 1)
            )
            
            self.recipe_buttons[recipe["id"]] = button
            self.recipe_labels[recipe["id"]] = level_label
    
    def _select_recipe(self, recipe_id):
        """
        Select a recipe and display its information
        
        Args:
            recipe_id (str): ID of the recipe to select
        """
        self.current_recipe = recipe_id
        self._update_recipe_info()
    
    def _update_recipe_info(self):
        """Update the recipe information panel"""
        if not self.current_recipe:
            self.recipe_name.setText("Select a Recipe")
            self.recipe_description.setText("")
            self.recipe_level.setText("")
            self.recipe_cost.setText("")
            self.craft_button["state"] = DGG.DISABLED
            return
        
        # Get recipe info
        recipe = self.game.crafting_system.get_recipe_info(self.current_recipe)
        if not recipe:
            return
        
        # Update info displays
        self.recipe_name.setText(recipe["name"])
        self.recipe_description.setText(recipe["description"])
        
        level_text = f"Level: {recipe['current_level']}/{recipe['max_level']}"
        self.recipe_level.setText(level_text)
        
        # Update cost information
        if recipe["cost"]:
            cost_text = "Cost: "
            for resource, amount in recipe["cost"].items():
                cost_text += f"{resource}: {amount}, "
            cost_text = cost_text[:-2]  # Remove trailing comma and space
            self.recipe_cost.setText(cost_text)
        else:
            self.recipe_cost.setText("Max level reached")
        
        # Update craft button state
        if recipe["can_craft"]:
            self.craft_button["state"] = DGG.NORMAL
            self.craft_button["frameColor"] = (0.2, 0.5, 0.2, 0.8)
        else:
            self.craft_button["state"] = DGG.DISABLED
            self.craft_button["frameColor"] = (0.4, 0.4, 0.4, 0.8)
    
    def _update_inventory_text(self):
        """Update the inventory display text"""
        if not hasattr(self.game, 'player') or not self.game.player:
            self.inventory_text.setText("No player inventory")
            return
        
        inventory_text = ""
        for resource, amount in self.game.player.inventory.items():
            inventory_text += f"{resource}: {amount}\n"
        
        self.inventory_text.setText(inventory_text)
    
    def _craft_selected(self):
        """Craft the currently selected recipe"""
        if not self.current_recipe:
            return
        
        # Try to craft the recipe
        success = self.game.crafting_system.craft_upgrade(self.current_recipe)
        
        if success:
            # Update the UI
            self._create_recipe_buttons()
            self._update_recipe_info()
            self._update_inventory_text()
            
            # Show a temporary message
            self.game.show_message(f"Crafted {self.game.crafting_system.recipes[self.current_recipe]['name']}!")
    
    def toggle(self):
        """Toggle the visibility of the crafting UI"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def show(self):
        """Show the crafting UI"""
        # Only show if we have a player and crafting system
        if not hasattr(self.game, 'player') or not hasattr(self.game, 'crafting_system'):
            print("Can't show crafting UI: player or crafting system not available")
            return
        
        # Update the UI based on current game state
        self._create_recipe_buttons()
        self._update_inventory_text()
        
        # Show the UI
        self.main_frame.show()
        self.visible = True
        
        # Pause the game if the method exists
        if hasattr(self.game, 'pause_game'):
            self.game.pause_game()
    
    def hide(self):
        """Hide the crafting UI"""
        self.main_frame.hide()
        self.visible = False
        
        # Unpause the game if the method exists
        if hasattr(self.game, 'resume_game'):
            self.game.resume_game()
        
        # Clear selection
        self.current_recipe = None 