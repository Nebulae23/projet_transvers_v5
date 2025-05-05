# src/engine/city/defense.py
from typing import List, Tuple, Optional
import numpy as np
from ..renderer import ShaderPipeline
from ..physics.collision_system import CollisionSystem
from .resources import ResourceType, ResourceAmount

class DefenseTower:
    def __init__(self, position: Tuple[float, float], tower_type: str):
        self.position = position
        self.tower_type = tower_type
        self.level = 1
        self.health = 100.0
        self.range = 10.0
        self.damage = 20.0
        self.attack_speed = 1.0
        self.attack_timer = 0.0
        
        self.shader = ShaderPipeline().stages['geometry']
        self.mesh = self._create_tower_mesh()
        self.material = self._load_tower_material()
        
    def _create_tower_mesh(self):
        # Create HD-2D style tower mesh
        vertices = np.array([
            # Base
            [-0.5, 0.0, -0.5,  0.0, 1.0, 0.0,  0.0, 0.0],
            [ 0.5, 0.0, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0],
            [ 0.5, 0.0,  0.5,  0.0, 1.0, 0.0,  1.0, 1.0],
            [-0.5, 0.0,  0.5,  0.0, 1.0, 0.0,  0.0, 1.0],
            # Top
            [-0.3, 2.0, -0.3,  0.0, 1.0, 0.0,  0.2, 0.2],
            [ 0.3, 2.0, -0.3,  0.0, 1.0, 0.0,  0.8, 0.2],
            [ 0.3, 2.0,  0.3,  0.0, 1.0, 0.0,  0.8, 0.8],
            [-0.3, 2.0,  0.3,  0.0, 1.0, 0.0,  0.2, 0.8],
        ], dtype=np.float32)
        return vertices
        
    def _load_tower_material(self):
        """Load materials for the tower"""
        return {
            'albedo_map': 'towers/textures/albedo.png',
            'normal_map': 'towers/textures/normal.png',
            'roughness_map': 'towers/textures/roughness.png'
        }
        
    def render(self, gl_context):
        """Render the tower with the shader"""
        self.shader.use()
        self.shader.set_uniform("model_matrix", self._get_transform_matrix())
        self.shader.set_uniform("albedo_map", self.material['albedo_map'])
        self.shader.set_uniform("normal_map", self.material['normal_map'])
        self.shader.set_uniform("roughness_map", self.material['roughness_map'])
        gl_context.draw_mesh(self.mesh)
        
    def _get_transform_matrix(self):
        """Create a transformation matrix for the tower"""
        # Create a 4x4 transformation matrix based on position
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = 0  # Y is up in our world
        matrix[2, 3] = self.position[1]
        return matrix

class DefenseManager:
    def __init__(self, collision_system: CollisionSystem):
        self.towers: List[DefenseTower] = []
        self.collision_system = collision_system
        
    def add_tower(self, position: Tuple[float, float], tower_type: str) -> Optional[DefenseTower]:
        if self._can_place_tower(position):
            tower = DefenseTower(position, tower_type)
            self.towers.append(tower)
            self.collision_system.add_collider(tower)
            return tower
        return None
        
    def update(self, dt: float, enemies: List):
        for tower in self.towers:
            tower.attack_timer += dt
            if tower.attack_timer >= 1.0 / tower.attack_speed:
                self._process_tower_attack(tower, enemies)
                tower.attack_timer = 0.0
                
    def _process_tower_attack(self, tower: DefenseTower, enemies: List):
        for enemy in enemies:
            if self._is_in_range(tower, enemy):
                enemy.take_damage(tower.damage)
                break
                
    def _can_place_tower(self, position: Tuple[float, float]) -> bool:
        return not any(
            self._calculate_distance(position, tower.position) < 2.0
            for tower in self.towers
        )
        
    def _is_in_range(self, tower: DefenseTower, enemy) -> bool:
        return self._calculate_distance(tower.position, enemy.position) <= tower.range
        
    @staticmethod
    def _calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
    def render(self, gl_context):
        """Render all towers"""
        for tower in self.towers:
            tower.render(gl_context)