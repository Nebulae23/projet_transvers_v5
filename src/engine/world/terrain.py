# src/engine/world/terrain.py
from typing import Dict, Tuple, List
import noise
import numpy as np
from OpenGL.GL import *
from ..engine.renderer import ShaderPipeline

class TerrainChunk:
    def __init__(self, position: Tuple[int, int], size: int = 32):
        self.position = position
        self.size = size
        self.heightmap = np.zeros((size, size), dtype=np.float32)
        self.mesh = None
        self.biome_map = np.zeros((size, size), dtype=np.int32)
        
    def generate(self, seed: int, scale: float = 50.0):
        # Generate heightmap using multiple octaves of noise
        for y in range(self.size):
            for x in range(self.size):
                nx = (x + self.position[0] * self.size) / scale
                ny = (y + self.position[1] * self.size) / scale
                
                # Multiple octaves for detail
                self.heightmap[x, y] = (
                    noise.pnoise2(nx, ny, octaves=6, persistence=0.5, lacunarity=2.0, base=seed) +
                    0.5 * noise.pnoise2(2*nx, 2*ny, octaves=4, persistence=0.5, base=seed+1)
                )
                
                # Determine biome based on height and custom noise
                biome_noise = noise.pnoise2(nx*3, ny*3, octaves=2, base=seed+2)
                self.biome_map[x, y] = self._get_biome_type(self.heightmap[x, y], biome_noise)
                
        self._generate_mesh()
        
    def _get_biome_type(self, height: float, variation: float) -> int:
        if height < -0.2:
            return 0  # Water
        elif height < 0.1:
            return 1  # Beach
        elif height < 0.4:
            return 2 if variation > 0 else 3  # Plains or Forest
        else:
            return 4  # Mountains
            
    def _generate_mesh(self):
        vertices = []
        indices = []
        
        # Generate HD-2D style terrain mesh
        for z in range(self.size):
            for x in range(self.size):
                # Position
                px = x + self.position[0] * self.size
                pz = z + self.position[1] * self.size
                py = self.heightmap[x, z] * 20.0  # Scale height for dramatic effect
                
                # Normal calculation
                nx = self._get_normal(x, z, 0)
                ny = 1.0
                nz = self._get_normal(x, z, 1)
                
                # UV coordinates for tiling
                u = x / self.size
                v = z / self.size
                
                # Biome color influence
                biome = self.biome_map[x, z]
                
                vertices.extend([px, py, pz, nx, ny, nz, u, v, biome])
                
        # Generate indices for triangle strips
        for z in range(self.size - 1):
            for x in range(self.size - 1):
                i = z * self.size + x
                indices.extend([i, i + 1, i + self.size, i + self.size + 1])
                
        self.mesh = {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }
        
    def _get_normal(self, x: int, z: int, axis: int) -> float:
        if x < 1 or x >= self.size - 1 or z < 1 or z >= self.size - 1:
            return 0.0
            
        if axis == 0:
            return (self.heightmap[x-1, z] - self.heightmap[x+1, z]) * 0.5
        else:
            return (self.heightmap[x, z-1] - self.heightmap[x, z+1]) * 0.5

class TerrainGenerator:
    def __init__(self):
        self.chunks: Dict[Tuple[int, int], TerrainChunk] = {}
        self.seed = np.random.randint(0, 1000000)
        self.shader = ShaderPipeline().stages['terrain']
        
    def get_chunk(self, chunk_pos: Tuple[int, int]) -> TerrainChunk:
        if chunk_pos not in self.chunks:
            chunk = TerrainChunk(chunk_pos)
            chunk.generate(self.seed)
            self.chunks[chunk_pos] = chunk
        return self.chunks[chunk_pos]
        
    def get_height(self, world_x: float, world_z: float) -> float:
        chunk_x = int(world_x // 32)
        chunk_z = int(world_z // 32)
        
        chunk = self.get_chunk((chunk_x, chunk_z))
        local_x = int(world_x % 32)
        local_z = int(world_z % 32)
        
        return chunk.heightmap[local_x, local_z] * 20.0