#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration module for Nightfall Defenders
"""

import os
import yaml


class GameConfig:
    """
    Configuration manager for game settings
    Handles loading and saving of configuration files
    """
    
    DEFAULT_CONFIG = {
        "video": {
            "resolution": [1280, 720],
            "fullscreen": False,
            "vsync": True,
            "show_fps": True,
            "graphics_quality": "medium"  # low, medium, high, ultra
        },
        "audio": {
            "master_volume": 0.8,
            "music_volume": 0.7,
            "effects_volume": 0.9,
            "ambient_volume": 0.6,
            "mute": False
        },
        "gameplay": {
            "difficulty": "normal",  # easy, normal, hard
            "day_night_cycle_duration": 1200,  # in seconds (20 minutes)
            "auto_save": True,
            "controller_vibration": True
        },
        "controls": {
            "mouse_sensitivity": 0.5,
            "invert_y": False,
            "controller_enabled": True
        },
        "accessibility": {
            "colorblind_mode": "none",  # none, protanopia, deuteranopia, tritanopia
            "text_size": "medium",  # small, medium, large
            "screen_shake": True,
            "flashing_effects": True
        }
    }
    
    def __init__(self):
        """Initialize the config manager"""
        self.config_path = os.path.join("src", "assets", "configs", "game_config.yaml")
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default if not exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as config_file:
                    return yaml.safe_load(config_file)
            except Exception as e:
                print(f"Error loading config file: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w') as config_file:
                yaml.dump(config, config_file, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, section, key, default=None):
        """Get a configuration value"""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section, key, value):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()
    
    def get_resolution(self):
        """Get the current resolution"""
        return tuple(self.get("video", "resolution", [1280, 720]))
    
    def is_fullscreen(self):
        """Check if fullscreen is enabled"""
        return self.get("video", "fullscreen", False)
    
    def get_graphics_quality(self):
        """Get the graphics quality setting"""
        return self.get("video", "graphics_quality", "medium") 