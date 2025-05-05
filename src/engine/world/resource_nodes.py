# src/engine/world/resource_nodes.py
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from .terrain import TerrainChunk

@dataclass
class ResourceNode:
    node_id: str
    resource_type: str
    position: Tuple[float, float, float]
    quantity: int
    respawn_time: float
    last_harvested: float = 0.0
    
    def can_harvest(self, current_time: float) -> bool:
        return current_time - self.last_harvested >= self.respawn_time
        
    def harvest(self, current_time: float, amount: int) -> int:
        if not self.can_harvest(current_time):
            return 0
            
        harvested = min(amount, self.quantity)
        self.quantity -= harvested
        self.last_harvested = current_time
        return harvested

class ResourceNodeManager:
    def __init__(self, terrain_generator):
        self.terrain_generator = terrain_generator
        self.nodes: Dict[str, ResourceNode] = {}
        self.node_types = {
            'iron_ore': {'biomes': [4], 'height_range': (0.6, 1.0), 'quantity': (50, 100)},
            'gold_ore': {'biomes': [4], 'height_range': (0.7, 1.0), 'quantity': (20, 40)},
            'wood': {'biomes': [3], 'height_range': (0.1, 0.7), 'quantity': (100, 200)},
            'stone': {'biomes': [2, 4], 'height_range': (0.3, 1.0), 'quantity': (80, 150)},
            'herbs': {'biomes': [2, 3], 'height_range': (0.1, 0.6), 'quantity': (30, 60)}
        }
        
    def generate_nodes(self, chunk: TerrainChunk):
        """Generate resource nodes for a new chunk based on terrain"""
        for x in range(chunk.size):
            for z in range(chunk.size):
                height = chunk.heightmap[x, z]
                biome = chunk.biome_map[x, z]
                
                # Check each resource type for placement
                for res_type, params in self.node_types.items():
                    if (biome in params['biomes'] and 
                        params['height_range'][0] <= height <= params['height_range'][1] and
                        np.random.random() < 0.05):  # 5% chance per valid location
                        
                        world_x = x + chunk.position[0] * chunk.size
                        world_z = z + chunk.position[1] * chunk.size
                        world_y = height * 20.0
                        
                        node_id = f"{res_type}_{world_x}_{world_z}"
                        quantity = np.random.randint(*params['quantity'])
                        
                        self.nodes[node_id] = ResourceNode(
                            node_id=node_id,
                            resource_type=res_type,
                            position=(world_x, world_y, world_z),
                            quantity=quantity,
                            respawn_time=300.0  # 5 minutes
                        )
                        
    def get_nearby_nodes(self, position: Tuple[float, float, float], radius: float) -> List[ResourceNode]:
        """Get all resource nodes within radius of position"""
        nearby = []
        for node in self.nodes.values():
            dx = node.position[0] - position[0]
            dz = node.position[2] - position[2]
            if (dx * dx + dz * dz) <= radius * radius:
                nearby.append(node)
        return nearby
        
    def harvest_node(self, node_id: str, current_time: float, amount: int) -> int:
        """Attempt to harvest a resource node"""
        if node_id in self.nodes:
            return self.nodes[node_id].harvest(current_time, amount)
        return 0
        
    def update(self, current_time: float):
        """Update node states and remove depleted nodes"""
        depleted = []
        for node_id, node in self.nodes.items():
            if node.quantity <= 0 and node.can_harvest(current_time):
                depleted.append(node_id)
                
        for node_id in depleted:
            del self.nodes[node_id]