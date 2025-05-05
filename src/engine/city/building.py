# src/engine/city/building.py
from typing import Dict, Optional
from dataclasses import dataclass
import numpy as np
from ..renderer import ShaderPipeline
from .resources import ResourceType, ResourceAmount

@dataclass
class BuildingStats:
    level: int = 1
    health: float = 100.0
    productivity: float = 1.0
    satisfaction: float = 1.0
    max_storage: Dict[ResourceType, float] = None

class Building:
    def __init__(self, building_type: str, position: tuple[float, float]):
        self.building_type = building_type
        self.position = position
        self.stats = BuildingStats()
        self.shader = ShaderPipeline().stages['geometry']
        self.material = self._load_building_material()
        self.mesh = self._create_building_mesh()
        self.upgrade_costs: Dict[int, Dict[ResourceType, float]] = self._init_upgrade_costs()
        
    def _load_building_material(self):
        # Load PBR materials for HD-2D style
        return {
            'albedo_map': 'buildings/textures/albedo.png',
            'normal_map': 'buildings/textures/normal.png',
            'roughness_map': 'buildings/textures/roughness.png'
        }
        
    def _create_building_mesh(self):
        # Create a simple cube mesh for buildings
        vertices = np.array([
            # Position(x,y,z), Normal(x,y,z), UV(u,v)
            # Front face
            [-0.5, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.5, 0.0, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0],
            [0.5, 1.0, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0],
            [-0.5, 1.0, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0],
        ], dtype=np.float32)
        return vertices
        
    def _init_upgrade_costs(self):
        # Initialize the costs for each upgrade level
        # In a real implementation, these would be loaded from data
        return {
            2: {ResourceType.WOOD: 10, ResourceType.STONE: 5},
            3: {ResourceType.WOOD: 20, ResourceType.STONE: 15, ResourceType.METAL: 5},
            4: {ResourceType.WOOD: 30, ResourceType.STONE: 25, ResourceType.METAL: 15}
        }
        
    def _get_transform_matrix(self):
        # Create a 4x4 transformation matrix based on position
        # In a real implementation, this would use a proper matrix library
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = 0  # Y is up in our world
        matrix[2, 3] = self.position[1]
        return matrix
        
    def can_upgrade(self, available_resources: Dict[ResourceType, float]) -> bool:
        next_level = self.stats.level + 1
        if next_level not in self.upgrade_costs:
            return False
        
        costs = self.upgrade_costs[next_level]
        return all(available_resources.get(res_type, 0) >= amount 
                  for res_type, amount in costs.items())
                  
    def upgrade(self, resources: Dict[ResourceType, ResourceAmount]) -> bool:
        if not self.can_upgrade(resources):
            return False
            
        next_level = self.stats.level + 1
        costs = self.upgrade_costs[next_level]
        
        # Deduct resources
        for res_type, amount in costs.items():
            resources[res_type].amount -= amount
            
        self.stats.level = next_level
        self.stats.productivity *= 1.5
        self.stats.satisfaction *= 1.2
        return True
        
    def render(self, gl_context):
        self.shader.use()
        self.shader.set_uniform("model_matrix", self._get_transform_matrix())
        self.shader.set_uniform("albedo_map", self.material['albedo_map'])
        self.shader.set_uniform("normal_map", self.material['normal_map'])
        self.shader.set_uniform("roughness_map", self.material['roughness_map'])
        gl_context.draw_mesh(self.mesh)