#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Building UI for Nightfall Defenders
Provides UI for constructing and managing buildings
"""

from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG, DirectScrolledFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, CardMaker, NodePath, Vec4, Vec3
import math

class BuildingUI:
    """UI for constructing and managing buildings"""
    
    def __init__(self, game):
        """
        Initialize the building UI
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.visible = False
        self.selected_building_type = None
        self.placement_mode = False
        self.placement_indicator = None
        self.current_rotation = 0
        
        # Create UI elements
        self._create_ui()
        
        # Hide the UI initially
        self.main_frame.hide()
        
    def _create_ui(self):
        """Create the UI elements"""
        # Main frame
        self.main_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.2, 0.8),
            frameSize=(-0.6, 0.6, -0.4, 0.4),
            pos=(0, 0, 0)
        )
        
        # Title
        self.title = OnscreenText(
            text="City Management",
            parent=self.main_frame,
            scale=0.07,
            pos=(0, 0.35),
            fg=(1, 1, 0.7, 1)
        )
        
        # Building categories tabs
        self._create_category_tabs()
        
        # Building selection area
        self._create_building_selection()
        
        # Building info panel
        self._create_building_info_panel()
        
        # Action buttons
        self._create_action_buttons()
        
        # Building list (for demolish)
        self._create_building_list()
        
    def _create_category_tabs(self):
        """Create tabs for building categories"""
        categories = ["defense", "resource", "production", "support"]
        tab_width = 0.25
        start_x = -0.5
        y_pos = 0.25
        
        self.category_buttons = {}
        self.current_category = categories[0]
        
        for i, category in enumerate(categories):
            button = DirectButton(
                text=category.capitalize(),
                text_scale=0.04,
                frameSize=(0, tab_width, -0.05, 0.05),
                frameColor=(0.2, 0.2, 0.3, 1.0),
                relief=DGG.FLAT,
                pos=(start_x + (i * tab_width), 0, y_pos),
                parent=self.main_frame,
                command=self._on_category_selected,
                extraArgs=[category]
            )
            self.category_buttons[category] = button
            
        # Highlight the initial category
        self.category_buttons[self.current_category]["frameColor"] = (0.3, 0.3, 0.5, 1.0)
        
    def _create_building_selection(self):
        """Create the building selection area"""
        self.building_selection_frame = DirectScrolledFrame(
            frameColor=(0.15, 0.15, 0.25, 0.9),
            frameSize=(-0.55, 0.55, -0.15, 0.2),
            canvasSize=(-0.53, 0.53, -0.4, 0.18),
            pos=(0, 0, 0.05),
            parent=self.main_frame,
            scrollBarWidth=0.04,
            verticalScroll_relief=DGG.FLAT,
            verticalScroll_frameColor=(0.2, 0.2, 0.3, 1.0),
            verticalScroll_thumb_frameColor=(0.4, 0.4, 0.6, 1.0),
            horizontalScroll_frameColor=(0.2, 0.2, 0.3, 1.0)
        )
        
        self.building_buttons = {}
        
    def _create_building_info_panel(self):
        """Create the building information panel"""
        self.info_panel = DirectFrame(
            frameColor=(0.15, 0.15, 0.25, 0.9),
            frameSize=(-0.25, 0.25, -0.15, 0.15),
            pos=(0.3, 0, -0.2),
            parent=self.main_frame,
        )
        
        # Building name
        self.building_name = OnscreenText(
            text="",
            parent=self.info_panel,
            scale=0.04,
            pos=(0, 0.11),
            fg=(1, 1, 0.7, 1)
        )
        
        # Building description
        self.building_desc = OnscreenText(
            text="",
            parent=self.info_panel,
            scale=0.03,
            pos=(0, 0.05),
            fg=(0.9, 0.9, 0.9, 1),
            align=TextNode.ACenter,
            wordwrap=15
        )
        
        # Building costs
        self.building_costs = OnscreenText(
            text="",
            parent=self.info_panel,
            scale=0.03,
            pos=(-0.2, -0.02),
            fg=(0.9, 0.9, 0.9, 1),
            align=TextNode.ALeft
        )
        
        # Building benefits
        self.building_benefits = OnscreenText(
            text="",
            parent=self.info_panel,
            scale=0.03,
            pos=(-0.2, -0.08),
            fg=(0.7, 1, 0.7, 1),
            align=TextNode.ALeft
        )
        
    def _create_action_buttons(self):
        """Create action buttons"""
        # Build button
        self.build_button = DirectButton(
            text="Build",
            text_scale=0.04,
            frameSize=(-0.1, 0.1, -0.04, 0.04),
            frameColor=(0.2, 0.5, 0.2, 1.0),
            relief=DGG.FLAT,
            pos=(-0.3, 0, -0.2),
            parent=self.main_frame,
            command=self._on_build_clicked,
            state=DGG.DISABLED
        )
        
        # Demolish button
        self.demolish_button = DirectButton(
            text="Demolish",
            text_scale=0.04,
            frameSize=(-0.1, 0.1, -0.04, 0.04),
            frameColor=(0.5, 0.2, 0.2, 1.0),
            relief=DGG.FLAT,
            pos=(-0.3, 0, -0.3),
            parent=self.main_frame,
            command=self._on_demolish_clicked,
            state=DGG.DISABLED
        )
        
        # Close button
        self.close_button = DirectButton(
            text="X",
            text_scale=0.04,
            frameSize=(-0.03, 0.03, -0.03, 0.03),
            frameColor=(0.5, 0.2, 0.2, 1.0),
            relief=DGG.FLAT,
            pos=(0.56, 0, 0.36),
            parent=self.main_frame,
            command=self.hide
        )
        
    def _create_building_list(self):
        """Create the list of built buildings for demolish option"""
        self.building_list_frame = DirectScrolledFrame(
            frameColor=(0.15, 0.15, 0.25, 0.9),
            frameSize=(-0.55, -0.05, -0.35, -0.15),
            canvasSize=(-0.53, -0.08, -0.6, -0.13),
            pos=(0, 0, 0.05),
            parent=self.main_frame,
            scrollBarWidth=0.04,
            verticalScroll_relief=DGG.FLAT,
            verticalScroll_frameColor=(0.2, 0.2, 0.3, 1.0),
            verticalScroll_thumb_frameColor=(0.4, 0.4, 0.6, 1.0),
            horizontalScroll_frameColor=(0.2, 0.2, 0.3, 1.0)
        )
        
        # Title
        self.building_list_title = OnscreenText(
            text="Built Structures",
            parent=self.building_list_frame,
            scale=0.04,
            pos=(-0.3, -0.15),
            fg=(1, 1, 0.7, 1)
        )
        
        self.building_list_buttons = []
        
    def _on_category_selected(self, category):
        """
        Handle category tab selection
        
        Args:
            category: The building category selected
        """
        # Update button colors
        for cat, button in self.category_buttons.items():
            if cat == category:
                button["frameColor"] = (0.3, 0.3, 0.5, 1.0)
            else:
                button["frameColor"] = (0.2, 0.2, 0.3, 1.0)
                
        self.current_category = category
        self._populate_building_selection(category)
        
    def _populate_building_selection(self, category):
        """
        Populate building selection with buildings of the selected category
        
        Args:
            category: The building category to display
        """
        # Clear existing buttons
        for button in self.building_buttons.values():
            button.destroy()
        self.building_buttons = {}
        
        # Get buildings of the current category
        buildings = [btype for btype, bdata in self.game.building_system.building_types.items() 
                    if bdata["category"] == category]
        
        button_width = 0.15
        button_height = 0.15
        padding = 0.03
        columns = 3
        
        # Calculate positions
        for i, building_type in enumerate(buildings):
            col = i % columns
            row = i // columns
            
            x_pos = -0.45 + (col * (button_width + padding))
            y_pos = 0.1 - (row * (button_height + padding))
            
            building_data = self.game.building_system.building_types[building_type]
            
            # Button background
            button = DirectButton(
                frameColor=(0.25, 0.25, 0.35, 1.0),
                frameSize=(0, button_width, -button_height, 0),
                relief=DGG.FLAT,
                pos=(x_pos, 0, y_pos),
                parent=self.building_selection_frame.getCanvas(),
                command=self._on_building_selected,
                extraArgs=[building_type]
            )
            
            # Building name
            name_label = DirectLabel(
                text=building_data["name"],
                text_scale=0.03,
                frameColor=(0, 0, 0, 0),
                pos=(button_width/2, 0, -button_height+0.02),
                parent=button
            )
            
            # Check if player can afford
            can_afford = self.game.building_system.can_build(building_type)
            
            # Availability indicator
            availability = DirectFrame(
                frameColor=(0.2, 0.6, 0.2, 1.0) if can_afford else (0.6, 0.2, 0.2, 1.0),
                frameSize=(0, 0.03, 0, 0.03),
                pos=(button_width-0.05, 0, -0.05),
                parent=button
            )
            
            self.building_buttons[building_type] = button
            
    def _on_building_selected(self, building_type):
        """
        Handle building selection
        
        Args:
            building_type: The selected building type
        """
        self.selected_building_type = building_type
        building_data = self.game.building_system.building_types[building_type]
        
        # Update name and description
        self.building_name.setText(building_data["name"])
        self.building_desc.setText(building_data["description"])
        
        # Update costs
        costs_text = "Costs:\n"
        for resource, amount in building_data["costs"].items():
            costs_text += f"- {resource.capitalize()}: {amount}\n"
        self.building_costs.setText(costs_text)
        
        # Update benefits
        benefits_text = "Benefits:\n"
        for benefit, value in building_data["benefits"].items():
            benefit_name = benefit.replace("_", " ").capitalize()
            benefits_text += f"- {benefit_name}: +{value}\n"
        self.building_benefits.setText(benefits_text)
        
        # Enable/disable build button based on resources
        can_build = self.game.building_system.can_build(building_type)
        self.build_button["state"] = DGG.NORMAL if can_build else DGG.DISABLED
        self.build_button["frameColor"] = (0.2, 0.5, 0.2, 1.0) if can_build else (0.3, 0.3, 0.3, 1.0)
        
    def _on_build_clicked(self):
        """Handle build button click"""
        if not self.selected_building_type:
            return
            
        # Enter placement mode
        self.placement_mode = True
        
        # Hide the UI temporarily
        self.main_frame.hide()
        
        # Create placement indicator
        self._create_placement_indicator()
        
        # Show placement instructions
        self.placement_instructions = OnscreenText(
            text="Left-click to place building | Right-click to cancel | R to rotate",
            scale=0.05,
            pos=(0, -0.8),
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Set up temporary input handlers
        self.game.accept("mouse1", self._on_place_confirm)
        self.game.accept("mouse3", self._cancel_placement)
        self.game.accept("r", self._rotate_placement)
        
    def _create_placement_indicator(self):
        """Create a visual indicator for building placement"""
        if self.placement_indicator:
            self.placement_indicator.removeNode()
            
        # Create a simple placeholder model
        # In actual implementation, this would load the building's model
        cm = CardMaker("placement_indicator")
        cm.setFrame(-1, 1, -1, 1)
        
        self.placement_indicator = self.game.render.attachNewNode(cm.generate())
        self.placement_indicator.setScale(2, 2, 0.1)
        self.placement_indicator.setP(-90)  # Make it flat on the ground
        self.placement_indicator.setColorScale(0.2, 0.8, 0.2, 0.5)  # Semi-transparent green
        
        # In actual implementation, would load the real model:
        # model_path = self.game.building_system.building_types[self.selected_building_type]["model"]
        # self.placement_indicator = self.game.loader.loadModel(model_path)
        # self.placement_indicator.reparentTo(self.game.render)
        
    def _update_placement_position(self, task):
        """
        Update placement indicator position based on mouse position
        
        Args:
            task: The task object
            
        Returns:
            Task result
        """
        if not self.placement_mode or not self.placement_indicator:
            return task.done
            
        # Get mouse position
        if self.game.mouseWatcherNode.hasMouse():
            mouse_pos = self.game.mouseWatcherNode.getMouse()
            
            # Project mouse position onto ground plane
            pos3d = self.game.calculate_ground_point_at_mouse(mouse_pos)
            
            if pos3d:
                # Snap to grid
                grid_size = 2.0
                pos3d.x = math.floor(pos3d.x / grid_size) * grid_size
                pos3d.y = math.floor(pos3d.y / grid_size) * grid_size
                pos3d.z = 0.1  # Slightly above ground
                
                # Update indicator position
                self.placement_indicator.setPos(pos3d)
                
                # Check if placement is valid
                is_valid = self._check_valid_placement(pos3d)
                self.placement_indicator.setColorScale(0.2, 0.8, 0.2, 0.5 if is_valid else 0.8, 0.2, 0.2, 0.5)
        
        return task.cont
        
    def _check_valid_placement(self, position):
        """
        Check if position is valid for building placement
        
        Args:
            position: The world position (Vec3)
            
        Returns:
            bool: True if valid placement, False otherwise
        """
        # Check distance from player
        player_pos = self.game.player.position
        distance = (position - player_pos).length()
        if distance > 20:  # Max building distance
            return False
            
        # Check for overlapping buildings
        for building in self.game.building_system.constructed_buildings:
            building_pos = building["position"]
            distance = (position - building_pos).length()
            if distance < 4:  # Minimum spacing between buildings
                return False
                
        # Check if within city boundaries (if implemented)
        # Add more constraints as needed
        
        return True
        
    def _on_place_confirm(self):
        """Handle building placement confirmation"""
        if not self.placement_mode or not self.placement_indicator:
            return
            
        # Get current position
        position = self.placement_indicator.getPos()
        
        # Check if valid placement
        if not self._check_valid_placement(position):
            # Show feedback (would be better with visual/sound feedback)
            return
            
        # Place the building
        self.game.building_system.start_construction(
            self.selected_building_type, 
            position
        )
        
        # Clean up placement mode
        self._cancel_placement()
        
        # Update UI
        self.show()
        self._update_building_list()
        
    def _rotate_placement(self):
        """Rotate the building preview"""
        if not self.placement_mode or not self.placement_indicator:
            return
            
        # Rotate by 90 degrees
        self.current_rotation = (self.current_rotation + 90) % 360
        self.placement_indicator.setH(self.current_rotation)
        
    def _cancel_placement(self):
        """Cancel building placement mode"""
        self.placement_mode = False
        
        # Remove indicator
        if self.placement_indicator:
            self.placement_indicator.removeNode()
            self.placement_indicator = None
            
        # Remove instructions
        if hasattr(self, 'placement_instructions'):
            self.placement_instructions.destroy()
            
        # Remove temporary input handlers
        self.game.ignore("mouse1")
        self.game.ignore("mouse3")
        self.game.ignore("r")
        
    def _on_demolish_clicked(self):
        """Handle demolish button click"""
        # Get selected building from the list
        if not hasattr(self, 'selected_building_idx') or self.selected_building_idx is None:
            return
            
        # Demolish the building
        self.game.building_system.demolish_building(self.selected_building_idx)
        
        # Update UI
        self._update_building_list()
        self.demolish_button["state"] = DGG.DISABLED
        
    def _update_building_list(self):
        """Update the list of constructed buildings"""
        # Clear current list
        for button in self.building_list_buttons:
            button.destroy()
        self.building_list_buttons = []
        
        # Get constructed buildings
        buildings = self.game.building_system.constructed_buildings
        
        # No buildings scenario
        if not buildings:
            no_buildings_label = DirectLabel(
                text="No buildings constructed",
                text_scale=0.03,
                frameColor=(0, 0, 0, 0),
                pos=(-0.3, 0, -0.2),
                parent=self.building_list_frame.getCanvas()
            )
            self.building_list_buttons.append(no_buildings_label)
            return
            
        # Create button for each building
        for i, building in enumerate(buildings):
            building_type = building["type"]
            building_data = self.game.building_system.building_types[building_type]
            
            y_pos = -0.2 - (i * 0.08)
            
            # Building button
            button = DirectButton(
                text=f"{building_data['name']} ({int(building['construction_progress'])}%)",
                text_scale=0.03,
                text_align=TextNode.ALeft,
                frameColor=(0.25, 0.25, 0.35, 1.0),
                frameSize=(-0.2, 0.15, -0.03, 0.03),
                relief=DGG.FLAT,
                pos=(-0.3, 0, y_pos),
                parent=self.building_list_frame.getCanvas(),
                command=self._on_building_list_selected,
                extraArgs=[i]
            )
            
            self.building_list_buttons.append(button)
        
    def _on_building_list_selected(self, building_idx):
        """
        Handle building selection from the building list
        
        Args:
            building_idx: Index of the selected building
        """
        self.selected_building_idx = building_idx
        self.demolish_button["state"] = DGG.NORMAL
        
        # Update button colors in the list
        for i, button in enumerate(self.building_list_buttons):
            if i == building_idx:
                button["frameColor"] = (0.4, 0.4, 0.6, 1.0)
            else:
                button["frameColor"] = (0.25, 0.25, 0.35, 1.0)
                
    def show(self):
        """Show the building UI"""
        if self.visible:
            return
            
        self.visible = True
        self.main_frame.show()
        
        # Populate UI with current data
        self._on_category_selected(self.current_category)
        self._update_building_list()
        
        # Start placement update task if not already running
        self.game.taskMgr.remove("update_placement")
        
    def hide(self):
        """Hide the building UI"""
        if not self.visible:
            return
            
        self.visible = False
        self.main_frame.hide()
        
        # Cancel placement mode if active
        if self.placement_mode:
            self._cancel_placement()
            
        # Remove update task
        self.game.taskMgr.remove("update_placement")
        
    def toggle(self):
        """Toggle the building UI visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
            
    def update(self, dt):
        """
        Update the building UI
        
        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return
            
        # If in placement mode, update the placement task
        if self.placement_mode and not self.game.taskMgr.hasTaskNamed("update_placement"):
            self.game.taskMgr.add(self._update_placement_position, "update_placement") 