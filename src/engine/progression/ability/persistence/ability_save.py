# src/engine/progression/ability/persistence/ability_save.py

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

class AbilitySaveManager:
    """
    Manages saving and loading of ability data, including procedural abilities.
    """
    def __init__(self, save_dir: Path):
        """
        Initialize the ability save manager.
        
        Args:
            save_dir (Path): Directory to store ability save files.
        """
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def save_player_abilities(self, player_id: str, abilities_data: Dict) -> bool:
        """
        Save ability data for a player.
        
        Args:
            player_id (str): Player ID.
            abilities_data (dict): Ability data to save.
            
        Returns:
            bool: True if save was successful.
        """
        try:
            # Create backup of existing save if exists
            save_path = self.save_dir / f"{player_id}_abilities.json"
            if save_path.exists():
                backup_path = self.save_dir / f"{player_id}_abilities_backup_{int(time.time())}.json"
                with open(save_path, "r") as f:
                    backup_data = f.read()
                with open(backup_path, "w") as f:
                    f.write(backup_data)
                    
            # Save new data
            with open(save_path, "w") as f:
                json.dump(abilities_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving player abilities: {e}")
            return False
            
    def load_player_abilities(self, player_id: str) -> Optional[Dict]:
        """
        Load ability data for a player.
        
        Args:
            player_id (str): Player ID.
            
        Returns:
            dict: Loaded ability data, or None if load failed.
        """
        try:
            save_path = self.save_dir / f"{player_id}_abilities.json"
            if not save_path.exists():
                return None
                
            with open(save_path, "r") as f:
                data = json.load(f)
                
            # Validate loaded data
            if not self._validate_ability_data(data):
                print(f"Warning: Invalid ability data found for player {player_id}")
                # Try to load a backup
                return self._load_backup(player_id)
                
            return data
            
        except Exception as e:
            print(f"Error loading player abilities: {e}")
            # Try to load a backup
            return self._load_backup(player_id)
            
    def _load_backup(self, player_id: str) -> Optional[Dict]:
        """
        Load the most recent valid backup.
        
        Args:
            player_id (str): Player ID.
            
        Returns:
            dict: Loaded backup data, or None if no valid backup exists.
        """
        try:
            # Find all backups for this player
            backups = []
            for file in self.save_dir.glob(f"{player_id}_abilities_backup_*.json"):
                try:
                    # Extract timestamp from filename
                    timestamp = int(file.stem.split("_")[-1])
                    backups.append((timestamp, file))
                except:
                    continue
                    
            # Sort by timestamp (most recent first)
            backups.sort(reverse=True)
            
            # Try each backup until a valid one is found
            for _, backup_path in backups:
                try:
                    with open(backup_path, "r") as f:
                        data = json.load(f)
                        
                    if self._validate_ability_data(data):
                        print(f"Loaded backup from {backup_path}")
                        return data
                except:
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Error loading backup: {e}")
            return None
            
    def _validate_ability_data(self, data: Dict) -> bool:
        """
        Validate loaded ability data.
        
        Args:
            data (dict): Loaded ability data.
            
        Returns:
            bool: True if data is valid.
        """
        if not isinstance(data, dict):
            return False
            
        # Check required top-level keys
        required_keys = ["procedural_abilities", "unlocked_nodes", "procedural_trees"]
        if not all(key in data for key in required_keys):
            return False
            
        # Validate procedural abilities
        abilities = data.get("procedural_abilities", {})
        if not isinstance(abilities, dict):
            return False
            
        for ability_id, ability_data in abilities.items():
            if not isinstance(ability_data, dict):
                return False
                
            # Check required ability keys
            if not all(key in ability_data for key in ["id", "name", "description"]):
                return False
                
        # Basic validation passed
        return True
        
    def get_all_player_saves(self) -> List[str]:
        """
        Get a list of all player IDs with saved abilities.
        
        Returns:
            list: List of player IDs.
        """
        player_ids = []
        for file in self.save_dir.glob("*_abilities.json"):
            try:
                # Extract player ID from filename
                player_id = file.stem.split("_")[0]
                player_ids.append(player_id)
            except:
                continue
                
        return player_ids
        
    def delete_player_save(self, player_id: str) -> bool:
        """
        Delete a player's ability save.
        
        Args:
            player_id (str): Player ID.
            
        Returns:
            bool: True if deletion was successful.
        """
        try:
            save_path = self.save_dir / f"{player_id}_abilities.json"
            if save_path.exists():
                save_path.unlink()
                
            # Delete backups
            for backup in self.save_dir.glob(f"{player_id}_abilities_backup_*.json"):
                backup.unlink()
                
            return True
            
        except Exception as e:
            print(f"Error deleting player save: {e}")
            return False
            
    def export_ability_data(self, player_id: str, export_path: Path) -> bool:
        """
        Export ability data to a file (for sharing or modding).
        
        Args:
            player_id (str): Player ID.
            export_path (Path): Path to export to.
            
        Returns:
            bool: True if export was successful.
        """
        try:
            abilities_data = self.load_player_abilities(player_id)
            if not abilities_data:
                return False
                
            # Add metadata for exported file
            export_data = {
                "metadata": {
                    "player_id": player_id,
                    "export_time": time.time(),
                    "export_version": "1.0"
                },
                "abilities": abilities_data
            }
            
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error exporting ability data: {e}")
            return False
            
    def import_ability_data(self, import_path: Path, target_player_id: Optional[str] = None) -> bool:
        """
        Import ability data from a file.
        
        Args:
            import_path (Path): Path to import from.
            target_player_id (str): Optional player ID to import to (defaults to original player).
            
        Returns:
            bool: True if import was successful.
        """
        try:
            with open(import_path, "r") as f:
                import_data = json.load(f)
                
            # Validate import data format
            if not isinstance(import_data, dict) or "abilities" not in import_data:
                print(f"Invalid import data format.")
                return False
                
            # Get original player ID from metadata
            metadata = import_data.get("metadata", {})
            original_player_id = metadata.get("player_id")
            
            # Use target player ID if provided, otherwise use original
            player_id = target_player_id or original_player_id
            if not player_id:
                print("No player ID found in import data and no target player provided.")
                return False
                
            # Save the imported abilities
            return self.save_player_abilities(player_id, import_data["abilities"])
            
        except Exception as e:
            print(f"Error importing ability data: {e}")
            return False
            
    def migrate_data_format(self, player_id: str) -> bool:
        """
        Migrate data format to the latest version (for future updates).
        
        Args:
            player_id (str): Player ID.
            
        Returns:
            bool: True if migration was successful.
        """
        # This will be implemented in future updates as the data format evolves
        # For now, just check if the data is valid and return True
        
        abilities_data = self.load_player_abilities(player_id)
        if not abilities_data:
            return False
            
        return True 