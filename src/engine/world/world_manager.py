# src/engine/world/world_manager.py
from typing import Dict, List, Tuple, Optional
from .terrain import TerrainGenerator
from .resource_nodes import ResourceNodeManager
from .npc import NPCManager
from .quest import QuestManager
import numpy as np

class PointOfInterest:
    def __init__(self, poi_type: str, position: Tuple[float, float, float]):
        self.type = poi_type
        self.position = position
        self.discovered = False
        self.linked_quests: List[str] = []
        self.resources: List[str] = []
        
class WorldManager:
    def __init__(self):
        self.terrain_generator = TerrainGenerator()
        self.resource_manager = ResourceNodeManager(self.terrain_generator)
        self.npc_manager = NPCManager()
        self.quest_manager = QuestManager()
        
        self.points_of_interest: Dict[str, PointOfInterest] = {}
        self.active_chunks: List[Tuple[int, int]] = []
        self.view_distance = 3  # Number of chunks in each direction
        
    def generate_world_region(self, center_chunk: Tuple[int, int]):
        """Generate or load world region around player"""
        new_active_chunks = []
        
        # Calculate chunk bounds
        for dx in range(-self.view_distance, self.view_distance + 1):
            for dz in range(-self.view_distance, self.view_distance + 1):
                chunk_pos = (center_chunk[0] + dx, center_chunk[1] + dz)
                new_active_chunks.append(chunk_pos)
                
                # Generate new chunk if needed
                if chunk_pos not in self.active_chunks:
                    self._generate_chunk_content(chunk_pos)
                    
        # Unload distant chunks
        self.active_chunks = new_active_chunks
        
    def _generate_chunk_content(self, chunk_pos: Tuple[int, int]):
        """Generate content for a new chunk"""
        chunk = self.terrain_generator.get_chunk(chunk_pos)
        
        # Generate POIs based on terrain features
        self._generate_points_of_interest(chunk)
        
        # Place resource nodes
        self.resource_manager.generate_nodes(chunk)
        
        # Place NPCs
        self._place_npcs(chunk)
        
    def _generate_points_of_interest(self, chunk):
        # Analyze terrain for suitable POI locations
        heightmap = chunk.heightmap
        for x in range(2, chunk.size - 2, 4):
            for z in range(2, chunk.size - 2, 4):
                if self._is_suitable_poi_location(heightmap, x, z):
                    world_pos = (
                        x + chunk.position[0] * chunk.size,
                        heightmap[x, z] * 20.0,
                        z + chunk.position[1] * chunk.size
                    )
                    poi_type = self._determine_poi_type(heightmap[x, z], chunk.biome_map[x, z])
                    if poi_type:
                        poi_id = f"poi_{world_pos[0]}_{world_pos[2]}"
                        self.points_of_interest[poi_id] = PointOfInterest(poi_type, world_pos)
                        
    def _is_suitable_poi_location(self, heightmap: np.ndarray, x: int, z: int) -> bool:
        # Check if location is suitable for POI (relatively flat, not water)
        center_height = heightmap[x, z]
        if center_height < 0:  # Water
            return False
            
        # Check surrounding area is relatively flat
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if abs(heightmap[x+dx, z+dz] - center_height) > 0.1:
                    return False
        return True
        
    def _determine_poi_type(self, height: float, biome: int) -> Optional[str]:
        if biome == 2:  # Plains
            return "village" if np.random.random() < 0.3 else "camp"
        elif biome == 3:  # Forest
            return "ruins" if np.random.random() < 0.2 else None
        elif biome == 4:  # Mountains
            return "dungeon" if np.random.random() < 0.15 else None
        return None
        
    def _place_npcs(self, chunk):
        # Place NPCs near POIs and in suitable locations
        for poi_id, poi in self.points_of_interest.items():
            if poi.type in ["village", "camp"]:
                self.npc_manager.spawn_npcs_at_location(poi.position, 3)