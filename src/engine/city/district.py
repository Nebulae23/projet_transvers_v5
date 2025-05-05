# src/engine/city/district.py
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from ..core import OpenGLContext
from ..renderer import ShaderPipeline

@dataclass
class DistrictData:
    name: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    level: int = 1
    prosperity: float = 0.0
    happiness: float = 0.0

class District:
    def __init__(self, name: str, position: Tuple[float, float], size: Tuple[float, float]):
        self.data = DistrictData(name, position, size)
        self.buildings = []
        self.shader = ShaderPipeline().stages['geometry']
        self.mesh = self._create_district_mesh()
        
    def _create_district_mesh(self):
        # Create a tilted plane mesh for HD-2D style
        vertices = np.array([
            # Position(x,y,z), Normal(x,y,z), UV(u,v)
            [-0.5, 0.0, -0.5,  0.0, 1.0, 0.0,  0.0, 0.0],
            [ 0.5, 0.0, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0],
            [ 0.5, 0.0,  0.5,  0.0, 1.0, 0.0,  1.0, 1.0],
            [-0.5, 0.0,  0.5,  0.0, 1.0, 0.0,  0.0, 1.0],
        ], dtype=np.float32)
        return vertices

    def update(self, dt: float):
        self.data.prosperity += self._calculate_prosperity(dt)
        self.data.happiness += self._calculate_happiness(dt)
        
    def render(self, gl_context: OpenGLContext):
        self.shader.use()
        self.shader.set_uniform("model_matrix", self._get_transform_matrix())
        gl_context.draw_mesh(self.mesh)
        
    def _calculate_prosperity(self, dt: float) -> float:
        return sum(building.productivity for building in self.buildings) * dt
        
    def _calculate_happiness(self, dt: float) -> float:
        return sum(building.satisfaction for building in self.buildings) * dt