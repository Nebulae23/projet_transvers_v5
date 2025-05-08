#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Difficulty Settings for Nightfall Defenders
Provides UI for adjusting game difficulty
"""

from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectSlider, DirectOptionMenu
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
import sys

from game.adaptive_difficulty import DifficultyPreset

class DifficultySettings:
    """Provides UI for adjusting game difficulty settings"""
    
    def __init__(self, game):
        """
        Initialize the difficulty settings UI
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.adaptive_difficulty_system = None
        
        # If game already has an adaptive difficulty system, store reference
        if hasattr(game, 'adaptive_difficulty_system'):
            self.adaptive_difficulty_system = game.adaptive_difficulty_system
        
        # UI elements
        self.main_frame = None
        self.sliders = {}
        self.labels = {}
        self.buttons = {}
        
        # Default slider ranges
        self.slider_ranges = {
            'enemy_health': (0.6, 1.5),
            'enemy_damage': (0.6, 1.5),
            'enemy_spawn_rate': (0.7, 1.4),
            'enemy_aggression': (0.7, 1.4),
            'resource_drop': (0.7, 1.4),
            'fog_speed': (0.7, 1.5),
            'fog_density': (0.7, 1.5),
            'boss_difficulty': (0.7, 1.5)
        }
        
        # Cached current values
        self.current_values = {}
        for param in self.slider_ranges:
            self.current_values[param] = 1.0
        
        # Current preset selection
        self.current_preset = DifficultyPreset.NORMAL
    
    def show_settings(self):
        """Display the difficulty settings UI"""
        # Hide existing UI if already shown
        self.hide_settings()
        
        # Create main frame
        self.main_frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.1, 0.8),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(0, 0, 0)
        )
        
        # Title
        title = DirectLabel(
            parent=self.main_frame,
            text="Difficulty Settings",
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            pos=(0, 0, 0.7),
            relief=None
        )
        
        # Preset selection
        preset_label = DirectLabel(
            parent=self.main_frame,
            text="Difficulty Preset:",
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            pos=(-0.5, 0, 0.55),
            text_align=TextNode.ALeft,
            relief=None
        )
        
        # Update current preset from the adaptive difficulty system if available
        if self.adaptive_difficulty_system:
            self.current_preset = self.adaptive_difficulty_system.difficulty_preset
            
            # Also update current values from the system
            current_factors = self.adaptive_difficulty_system.get_current_difficulty_factors()
            for param, value in current_factors.items():
                self.current_values[param] = value
        
        # Function to handle preset selection
        def set_preset(preset_name):
            preset_map = {
                "Easy": DifficultyPreset.EASY,
                "Normal": DifficultyPreset.NORMAL,
                "Hard": DifficultyPreset.HARD,
                "Custom": DifficultyPreset.CUSTOM
            }
            preset = preset_map.get(preset_name, DifficultyPreset.NORMAL)
            self.current_preset = preset
            
            # Apply preset immediately if adaptive difficulty system is available
            if self.adaptive_difficulty_system:
                self.adaptive_difficulty_system.set_difficulty_preset(preset)
                
                # Update sliders to reflect new values
                self._update_sliders_from_system()
                
            # Enable/disable sliders based on whether custom is selected
            self._update_slider_states()
        
        preset_menu = DirectOptionMenu(
            parent=self.main_frame,
            scale=0.06,
            pos=(0.15, 0, 0.55),
            items=["Easy", "Normal", "Hard", "Custom"],
            initialitem=self._get_preset_index(),
            command=set_preset
        )
        
        # Add sliders for each difficulty parameter
        self._create_difficulty_sliders()
        
        # Save and cancel buttons
        save_button = DirectButton(
            parent=self.main_frame,
            text="Save",
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            frameColor=(0.2, 0.5, 0.2, 1),
            relief=1,
            pos=(-0.3, 0, -0.7),
            command=self._save_settings
        )
        
        cancel_button = DirectButton(
            parent=self.main_frame,
            text="Cancel",
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            frameColor=(0.5, 0.2, 0.2, 1),
            relief=1,
            pos=(0.3, 0, -0.7),
            command=self.hide_settings
        )
        
        reset_button = DirectButton(
            parent=self.main_frame,
            text="Reset",
            text_fg=(1, 1, 1, 1),
            text_scale=0.06,
            frameSize=(-0.15, 0.15, -0.05, 0.05),
            frameColor=(0.4, 0.4, 0.2, 1),
            relief=1,
            pos=(0, 0, -0.7),
            command=self._reset_to_preset
        )
        
        self.buttons = {
            'save': save_button,
            'cancel': cancel_button,
            'reset': reset_button
        }
        
        # Initial update of slider states
        self._update_slider_states()
    
    def hide_settings(self):
        """Hide the difficulty settings UI"""
        if self.main_frame:
            self.main_frame.destroy()
            self.main_frame = None
            self.sliders = {}
            self.labels = {}
            self.buttons = {}
    
    def _create_difficulty_sliders(self):
        """Create sliders for each difficulty parameter"""
        # Parameters and their user-friendly names
        parameters = [
            ('enemy_health', 'Enemy Health'),
            ('enemy_damage', 'Enemy Damage'),
            ('enemy_spawn_rate', 'Spawn Rate'),
            ('enemy_aggression', 'Enemy Aggression'),
            ('resource_drop', 'Resource Drops'),
            ('fog_speed', 'Fog Speed'),
            ('fog_density', 'Fog Density'),
            ('boss_difficulty', 'Boss Difficulty')
        ]
        
        # Create a slider for each parameter
        y_pos = 0.4
        for i, (param, name) in enumerate(parameters):
            # Skip if beyond frame bounds
            if y_pos < -0.6:
                break
                
            # Parameter label
            param_label = DirectLabel(
                parent=self.main_frame,
                text=name + ":",
                text_fg=(1, 1, 1, 1),
                text_scale=0.05,
                pos=(-0.7, 0, y_pos),
                text_align=TextNode.ALeft,
                relief=None
            )
            
            # Value label (will be updated by slider)
            value_label = DirectLabel(
                parent=self.main_frame,
                text=f"{self.current_values.get(param, 1.0):.2f}x",
                text_fg=(1, 1, 0.8, 1),
                text_scale=0.05,
                pos=(0.7, 0, y_pos),
                text_align=TextNode.ARight,
                relief=None
            )
            
            # Function to update label when slider moves
            def update_label(value, p=param, lbl=value_label):
                # Update current value
                self.current_values[p] = value
                # Update label
                lbl['text'] = f"{value:.2f}x"
                # If we adjust sliders, we're in custom mode
                self.current_preset = DifficultyPreset.CUSTOM
            
            # Create slider
            min_val, max_val = self.slider_ranges.get(param, (0.5, 1.5))
            current_val = self.current_values.get(param, 1.0)
            
            slider = DirectSlider(
                parent=self.main_frame,
                pos=(0, 0, y_pos),
                value=current_val,
                range=(min_val, max_val),
                scale=0.5,
                command=update_label
            )
            
            # Store references to UI elements
            self.sliders[param] = slider
            self.labels[param] = value_label
            
            # Move down for next parameter
            y_pos -= 0.12
    
    def _update_slider_states(self):
        """Update slider states based on preset selection"""
        for param, slider in self.sliders.items():
            # Enable sliders only in Custom mode
            if self.current_preset == DifficultyPreset.CUSTOM:
                slider['state'] = 'normal'
            else:
                slider['state'] = 'disabled'
    
    def _get_preset_index(self):
        """Get the index of the current preset for the dropdown menu"""
        preset_indices = {
            DifficultyPreset.EASY: 0,
            DifficultyPreset.NORMAL: 1,
            DifficultyPreset.HARD: 2,
            DifficultyPreset.CUSTOM: 3
        }
        return preset_indices.get(self.current_preset, 1)  # Default to Normal
    
    def _update_sliders_from_system(self):
        """Update slider values from the adaptive difficulty system"""
        if not self.adaptive_difficulty_system:
            return
            
        # Get current factors
        factors = self.adaptive_difficulty_system.get_current_difficulty_factors()
        
        # Update sliders and labels
        for param, value in factors.items():
            if param in self.sliders:
                self.sliders[param]['value'] = value
                self.labels[param]['text'] = f"{value:.2f}x"
                self.current_values[param] = value
    
    def _save_settings(self):
        """Save the current difficulty settings"""
        if not self.adaptive_difficulty_system:
            print("Cannot save settings: No adaptive difficulty system available")
            self.hide_settings()
            return
            
        # If using a preset, apply it
        if self.current_preset != DifficultyPreset.CUSTOM:
            self.adaptive_difficulty_system.set_difficulty_preset(self.current_preset)
        else:
            # Apply custom settings
            self.adaptive_difficulty_system.set_custom_difficulty(self.current_values)
        
        # Hide the settings UI
        self.hide_settings()
        
        # Print confirmation
        print(f"Difficulty settings saved: {self.current_preset.name}")
    
    def _reset_to_preset(self):
        """Reset sliders to the current preset values"""
        if not self.adaptive_difficulty_system:
            return
            
        # Only reset if not in custom mode
        if self.current_preset != DifficultyPreset.CUSTOM:
            # Get preset values from a temporary application
            current_preset = self.adaptive_difficulty_system.difficulty_preset
            current_values = self.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Temporarily apply the preset we want to see
            self.adaptive_difficulty_system.set_difficulty_preset(self.current_preset)
            preset_values = self.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Restore original values
            self.adaptive_difficulty_system.set_difficulty_preset(current_preset)
            self.adaptive_difficulty_system.set_custom_difficulty(current_values)
            
            # Update our cached values and UI
            for param, value in preset_values.items():
                self.current_values[param] = value
                if param in self.sliders:
                    self.sliders[param]['value'] = value
                    self.labels[param]['text'] = f"{value:.2f}x"
        else:
            # In custom mode, reset to Normal preset values
            temp_system = self.adaptive_difficulty_system
            temp_system.set_difficulty_preset(DifficultyPreset.NORMAL)
            normal_values = temp_system.get_current_difficulty_factors()
            
            # Update sliders
            for param, value in normal_values.items():
                self.current_values[param] = value
                if param in self.sliders:
                    self.sliders[param]['value'] = value
                    self.labels[param]['text'] = f"{value:.2f}x"
            
            # Restore system to custom mode
            temp_system.set_difficulty_preset(DifficultyPreset.CUSTOM) 