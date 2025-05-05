# src/engine/systems/cloud_save_system.py
from typing import Optional, Dict, Any
import json
import os
import time
import asyncio
import aiohttp
from pathlib import Path
import hashlib
from datetime import datetime

class CloudSaveSystem:
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.local_save_dir = Path("saves")
        self.local_save_dir.mkdir(exist_ok=True)
        self.current_save: Optional[str] = None
        self.auto_save_interval = 300  # 5 minutes
        self.last_auto_save = time.time()

    async def save_game(self, save_name: str, game_state: dict) -> bool:
        # Create save data with metadata
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "save_name": save_name
            },
            "state": game_state
        }

        # Save locally first
        local_success = await self._save_local(save_name, save_data)
        if not local_success:
            return False

        # Then try to sync with cloud
        cloud_success = await self._sync_to_cloud(save_name, save_data)
        return cloud_success

    async def load_game(self, save_name: str) -> Optional[dict]:
        # Try to get latest version from cloud first
        cloud_data = await self._fetch_from_cloud(save_name)
        
        if cloud_data:
            # Update local save with cloud version
            await self._save_local(save_name, cloud_data)
            return cloud_data.get("state")

        # Fall back to local save if cloud sync fails
        return await self._load_local(save_name)

    async def _save_local(self, save_name: str, save_data: dict) -> bool:
        try:
            save_path = self.local_save_dir / f"{save_name}.json"
            async with aiofiles.open(save_path, 'w') as f:
                await f.write(json.dumps(save_data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving locally: {e}")
            return False

    async def _load_local(self, save_name: str) -> Optional[dict]:
        try:
            save_path = self.local_save_dir / f"{save_name}.json"
            if not save_path.exists():
                return None
                
            async with aiofiles.open(save_path, 'r') as f:
                content = await f.read()
                save_data = json.loads(content)
                return save_data.get("state")
        except Exception as e:
            print(f"Error loading local save: {e}")
            return None

    async def _sync_to_cloud(self, save_name: str, save_data: dict) -> bool:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_endpoint}/saves/{save_name}",
                    headers=headers,
                    json=save_data
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error syncing to cloud: {e}")
            return False

    async def _fetch_from_cloud(self, save_name: str) -> Optional[dict]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_endpoint}/saves/{save_name}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
            return None
        except Exception as e:
            print(f"Error fetching from cloud: {e}")
            return None

    def check_auto_save(self) -> bool:
        current_time = time.time()
        if (current_time - self.last_auto_save) >= self.auto_save_interval:
            self.last_auto_save = current_time
            return True
        return False

    async def list_saves(self) -> Dict[str, Any]:
        local_saves = {}
        cloud_saves = {}

        # Get local saves
        for save_file in self.local_save_dir.glob("*.json"):
            try:
                async with aiofiles.open(save_file, 'r') as f:
                    content = await f.read()
                    save_data = json.loads(content)
                    local_saves[save_file.stem] = save_data["metadata"]
            except Exception as e:
                print(f"Error reading local save {save_file}: {e}")

        # Get cloud saves
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_endpoint}/saves",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        cloud_saves = await response.json()
        except Exception as e:
            print(f"Error fetching cloud saves: {e}")

        return {
            "local": local_saves,
            "cloud": cloud_saves
        }

    def cleanup_old_saves(self, max_saves: int = 10):
        saves = list(self.local_save_dir.glob("*.json"))
        saves.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(saves) > max_saves:
            for save in saves[max_saves:]:
                try:
                    save.unlink()
                except Exception as e:
                    print(f"Error deleting old save {save}: {e}")