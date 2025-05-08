#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Save/Load System for Nightfall Defenders
Manages game save files, autosaves, and save metadata
"""

import os
import json
import time
import datetime
import shutil
import hashlib
import base64
import zlib
from typing import Dict, List, Any, Optional, Tuple

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PNMImage, Filename

class SaveManager:
    """Manages game saving and loading operations"""
    
    # Save file version - increment when save format changes
    SAVE_VERSION = 1
    
    # Subdirectory for save files
    SAVES_DIR = "saves"
    
    # Maximum number of autosave slots
    MAX_AUTOSAVES = 3
    
    def __init__(self, game):
        """
        Initialize the save manager
        
        Args:
            game: Main game instance
        """
        self.game = game
        
        # Ensure save directory exists
        self.save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), self.SAVES_DIR)
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Track current loaded save
        self.current_save_slot = None
        
        print(f"Save Manager initialized. Save directory: {self.save_dir}")
    
    def save_game(self, slot_name: str, is_autosave: bool = False, screenshot: Optional[PNMImage] = None) -> bool:
        """
        Save the current game state
        
        Args:
            slot_name: Name of the save slot
            is_autosave: Whether this is an automatic save
            screenshot: Optional screenshot image to save with the file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Generate save data from all game systems
            save_data = self._collect_save_data()
            
            # Create save metadata
            save_data["metadata"] = self._create_metadata(slot_name, is_autosave)
            
            # Create filename
            safe_name = self._sanitize_filename(slot_name)
            filename = f"{safe_name}.json"
            filepath = os.path.join(self.save_dir, filename)
            
            # Save the data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            
            # Save screenshot if provided
            if screenshot:
                thumb_path = os.path.join(self.save_dir, f"{safe_name}_thumb.png")
                screenshot.write(Filename(thumb_path))
            else:
                # Generate screenshot if not provided
                self._save_screenshot(safe_name)
            
            # Update current save slot
            self.current_save_slot = slot_name
            
            print(f"Game saved to slot '{slot_name}'")
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, slot_name: str) -> bool:
        """
        Load a game from a save slot
        
        Args:
            slot_name: Name of the save slot
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        try:
            # Create filename
            safe_name = self._sanitize_filename(slot_name)
            filepath = os.path.join(self.save_dir, f"{safe_name}.json")
            
            # Check if file exists
            if not os.path.exists(filepath):
                print(f"Save file not found: {filepath}")
                return False
            
            # Load the data
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Verify save data
            if not self._verify_save_data(save_data):
                print("Save data verification failed")
                return False
            
            # Apply the loaded data to game systems
            if self._apply_save_data(save_data):
                # Update current save slot
                self.current_save_slot = slot_name
                print(f"Game loaded from slot '{slot_name}'")
                return True
            else:
                print("Failed to apply save data")
                return False
                
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def autosave(self) -> bool:
        """
        Create an autosave
        
        Returns:
            bool: True if autosave was successful, False otherwise
        """
        # Create autosave name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        slot_name = f"autosave_{timestamp}"
        
        # Perform save
        result = self.save_game(slot_name, is_autosave=True)
        
        # Clean up old autosaves if we have too many
        if result:
            self._cleanup_autosaves()
        
        return result
    
    def delete_save(self, slot_name: str) -> bool:
        """
        Delete a save slot
        
        Args:
            slot_name: Name of the save slot
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Create filename
            safe_name = self._sanitize_filename(slot_name)
            filepath = os.path.join(self.save_dir, f"{safe_name}.json")
            thumb_path = os.path.join(self.save_dir, f"{safe_name}_thumb.png")
            
            # Delete files if they exist
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            
            # Clear current save slot if it was the deleted one
            if self.current_save_slot == slot_name:
                self.current_save_slot = None
            
            print(f"Deleted save slot '{slot_name}'")
            return True
            
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def get_save_slots(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available save slots with metadata
        
        Returns:
            List of dictionaries containing save slot information
        """
        save_slots = []
        
        # Get all .json files in save directory
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                # Extract save slot name from filename
                slot_name = filename[:-5]  # Remove .json
                
                try:
                    # Load metadata from save file
                    filepath = os.path.join(self.save_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    # Get metadata
                    metadata = save_data.get("metadata", {})
                    
                    # Check if thumbnail exists
                    thumb_path = os.path.join(self.save_dir, f"{slot_name}_thumb.png")
                    has_thumbnail = os.path.exists(thumb_path)
                    
                    # Add to save slots list
                    save_slots.append({
                        "slot_name": self._desanitize_filename(slot_name),
                        "display_name": metadata.get("display_name", slot_name),
                        "date": metadata.get("save_date", "Unknown"),
                        "character": metadata.get("character_info", {}).get("class", "Unknown"),
                        "level": metadata.get("character_info", {}).get("level", 1),
                        "play_time": metadata.get("play_time", "0:00:00"),
                        "is_autosave": metadata.get("is_autosave", False),
                        "has_thumbnail": has_thumbnail,
                        "thumbnail_path": thumb_path if has_thumbnail else None
                    })
                    
                except Exception as e:
                    print(f"Error loading metadata for {filename}: {e}")
        
        # Sort by date (newest first)
        save_slots.sort(key=lambda x: x["date"], reverse=True)
        
        return save_slots
    
    def _collect_save_data(self) -> Dict[str, Any]:
        """
        Collect save data from all game systems
        
        Returns:
            Dictionary containing all game state data
        """
        save_data = {}
        
        # Get data from game systems that support save_data()
        systems_to_save = [
            # Player and character data
            ("player", self.game.player if hasattr(self.game, "player") else None),
            
            # World and environment
            ("day_night_cycle", self.game.day_night_cycle if hasattr(self.game, "day_night_cycle") else None),
            ("entity_manager", self.game.entity_manager if hasattr(self.game, "entity_manager") else None),
            
            # City and building systems
            ("city_manager", self.game.city_manager if hasattr(self.game, "city_manager") else None),
            ("building_system", self.game.building_system if hasattr(self.game, "building_system") else None),
            
            # Progression systems
            ("relic_system", self.game.relic_system if hasattr(self.game, "relic_system") else None),
            ("crafting_system", self.game.crafting_system if hasattr(self.game, "crafting_system") else None),
            
            # Check for other systems with save_data method
            ("quest_system", self.game.quest_system if hasattr(self.game, "quest_system") else None),
            ("points_of_interest", self.game.poi_manager if hasattr(self.game, "poi_manager") else None),
            ("npc_system", self.game.npc_manager if hasattr(self.game, "npc_manager") else None),
            ("random_events", self.game.random_events if hasattr(self.game, "random_events") else None),
            ("challenge_system", self.game.challenge_system if hasattr(self.game, "challenge_system") else None),
        ]
        
        # Collect data from each system
        for system_name, system in systems_to_save:
            try:
                if system and hasattr(system, "save_data"):
                    save_data[system_name] = system.save_data()
                elif system and hasattr(system, "save_state"):
                    save_data[system_name] = system.save_state()
            except Exception as e:
                print(f"Error saving data for {system_name}: {e}")
                # Continue with other systems even if one fails
        
        return save_data
    
    def _apply_save_data(self, save_data: Dict[str, Any]) -> bool:
        """
        Apply loaded save data to all game systems
        
        Args:
            save_data: Dictionary containing all game state data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Systems to load, with their data keys
        systems_to_load = [
            # Player and character data
            ("player", self.game.player if hasattr(self.game, "player") else None, "player"),
            
            # World and environment
            ("day_night_cycle", self.game.day_night_cycle if hasattr(self.game, "day_night_cycle") else None, "day_night_cycle"),
            ("entity_manager", self.game.entity_manager if hasattr(self.game, "entity_manager") else None, "entity_manager"),
            
            # City and building systems
            ("city_manager", self.game.city_manager if hasattr(self.game, "city_manager") else None, "city_manager"),
            ("building_system", self.game.building_system if hasattr(self.game, "building_system") else None, "building_system"),
            
            # Progression systems
            ("relic_system", self.game.relic_system if hasattr(self.game, "relic_system") else None, "relic_system"),
            ("crafting_system", self.game.crafting_system if hasattr(self.game, "crafting_system") else None, "crafting_system"),
            
            # Check for other systems with load_data method
            ("quest_system", self.game.quest_system if hasattr(self.game, "quest_system") else None, "quest_system"),
            ("points_of_interest", self.game.poi_manager if hasattr(self.game, "poi_manager") else None, "points_of_interest"),
            ("npc_system", self.game.npc_manager if hasattr(self.game, "npc_manager") else None, "npc_system"),
            ("random_events", self.game.random_events if hasattr(self.game, "random_events") else None, "random_events"),
            ("challenge_system", self.game.challenge_system if hasattr(self.game, "challenge_system") else None, "challenge_system"),
        ]
        
        # Apply data to each system
        for system_name, system, data_key in systems_to_load:
            try:
                if system and data_key in save_data:
                    if hasattr(system, "load_data"):
                        system.load_data(save_data[data_key])
                    elif hasattr(system, "load_state"):
                        system.load_state(save_data[data_key])
            except Exception as e:
                print(f"Error loading data for {system_name}: {e}")
                # Continue with other systems even if one fails
        
        return True
    
    def _create_metadata(self, slot_name: str, is_autosave: bool) -> Dict[str, Any]:
        """
        Create metadata for a save file
        
        Args:
            slot_name: Name of the save slot
            is_autosave: Whether this is an automatic save
            
        Returns:
            Dictionary containing save metadata
        """
        # Get current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get player information if available
        character_info = {}
        if hasattr(self.game, "player") and self.game.player:
            player = self.game.player
            character_info = {
                "class": player.character_class.name if hasattr(player, "character_class") else "Unknown",
                "level": player.level if hasattr(player, "level") else 1,
                "position": {
                    "x": float(player.position.x) if hasattr(player, "position") else 0,
                    "y": float(player.position.y) if hasattr(player, "position") else 0,
                    "z": float(player.position.z) if hasattr(player, "position") else 0
                }
            }
        
        # Get play time if available
        play_time_str = "0:00:00"
        if hasattr(self.game, "play_time"):
            hours = int(self.game.play_time // 3600)
            minutes = int((self.game.play_time % 3600) // 60)
            seconds = int(self.game.play_time % 60)
            play_time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        # Get day/night cycle info if available
        day_info = {}
        if hasattr(self.game, "day_night_cycle") and self.game.day_night_cycle:
            day_night = self.game.day_night_cycle
            current_time = getattr(day_night, "current_time", 0)
            day_info = {
                "current_time": current_time,
                "time_of_day": getattr(day_night, "time_of_day", "day")
            }
        
        # Create metadata
        metadata = {
            "save_version": self.SAVE_VERSION,
            "display_name": slot_name,
            "save_date": date_str,
            "timestamp": time.time(),
            "is_autosave": is_autosave,
            "play_time": play_time_str,
            "character_info": character_info,
            "day_info": day_info,
            "checksum": ""  # Will be added after data is compiled
        }
        
        return metadata
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Convert a user-friendly name to a safe filename
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Replace spaces with underscores
        safe_name = filename.replace(" ", "_")
        
        # Remove any illegal characters
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")
        
        return safe_name
    
    def _desanitize_filename(self, filename: str) -> str:
        """
        Convert a safe filename back to a user-friendly name
        
        Args:
            filename: Safe filename
            
        Returns:
            User-friendly name
        """
        # Replace underscores with spaces
        display_name = filename.replace("_", " ")
        
        return display_name
    
    def _save_screenshot(self, slot_name: str) -> bool:
        """
        Save a screenshot for the save thumbnail
        
        Args:
            slot_name: Name of the save slot (sanitized)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            thumb_path = os.path.join(self.save_dir, f"{slot_name}_thumb.png")
            
            # Create a PNMImage to store the screenshot
            screenshot = PNMImage()
            
            # Take a screenshot of the current frame
            base = self.game
            base.win.getScreenshot(screenshot)
            
            # Save the image
            screenshot.write(Filename(thumb_path))
            
            return True
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return False
    
    def _verify_save_data(self, save_data: Dict[str, Any]) -> bool:
        """
        Verify save data integrity
        
        Args:
            save_data: Save data to verify
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        # Check for metadata
        if "metadata" not in save_data:
            print("Save data missing metadata")
            return False
        
        # Check save version
        version = save_data["metadata"].get("save_version", 0)
        if version > self.SAVE_VERSION:
            print(f"Save data version ({version}) is newer than supported version ({self.SAVE_VERSION})")
            return False
        
        # TODO: Add checksum verification when implemented
        
        return True
    
    def _cleanup_autosaves(self) -> None:
        """Clean up old autosaves, keeping only the most recent ones"""
        # Get all autosaves
        autosaves = [s for s in self.get_save_slots() if s["is_autosave"]]
        
        # If we have more than the maximum, delete the oldest ones
        if len(autosaves) > self.MAX_AUTOSAVES:
            # Sort by date (oldest first)
            autosaves.sort(key=lambda x: x["date"])
            
            # Delete oldest autosaves
            for i in range(len(autosaves) - self.MAX_AUTOSAVES):
                self.delete_save(autosaves[i]["slot_name"]) 