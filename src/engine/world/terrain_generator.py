# src/engine/world/terrain_generator.py
from typing import Dict, List, Tuple
import numpy as np
import noise
from dataclasses import dataclass
from enum import Enum

class BiomeType(Enum):
    OCEAN = "ocean"
    BEACH = "beach"
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAINS = "mountains"
    SNOW = "snow"

@dataclass
class BiomeParams:
    base_height: float
    roughness: float
    vegetation_density: float
    color: Tuple[float, float, float]

class TerrainGenerator:
    def __init__(self, size: int = 1024):
        self.size = size
        self.height_map = np.zeros((size, size), dtype=float)
        self.biome_map = np.zeros((size, size), dtype=int)
        self.moisture_map = np.zeros((size, size), dtype=float)
        self.temperature_map = np.zeros((size, size), dtype=float)
        
        # Biome definitions
        self.biomes = {
            BiomeType.OCEAN: BiomeParams(0.2, 0.1, 0.0, (0.0, 0.2, 0.5)),
            BiomeType.BEACH: BiomeParams(0.3, 0.1, 0.1, (0.8, 0.8, 0.6)),
            BiomeType.PLAINS: BiomeParams(0.4, 0.2, 0.3, (0.4, 0.6, 0.3)),
            BiomeType.FOREST: BiomeParams(0.5, 0.4, 0.8, (0.2, 0.5, 0.2)),
            BiomeType.MOUNTAINS: BiomeParams(0.7, 0.7, 0.2, (0.5, 0.5, 0.5)),
            BiomeType.SNOW: BiomeParams(0.8, 0.5, 0.1, (0.9, 0.9, 0.9))
        }
        
    def generate(self, seed: int) -> None:
        np.random.seed(seed)
        
        # Generate base terrain using multiple octaves of noise
        self._generate_base_terrain(seed)
        
        # Generate climate maps
        self._generate_temperature_map(seed)
        self._generate_moisture_map(seed)
        
        # Determine biomes based on height, temperature and moisture
        self._generate_biome_map()
        
        # Apply biome-specific modifications
        self._apply_biome_features()
        
        # Generate detail maps
        self._generate_detail_maps()
        
    def _generate_base_terrain(self, seed: int) -> None:
        scale = 100.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        
        for y in range(self.size):
            for x in range(self.size):
                height = 0
                amplitude = 1.0
                frequency = 1.0
                
                for _ in range(octaves):
                    dx = x / scale * frequency
                    dy = y / scale * frequency
                    height += noise.pnoise2(dx + seed, dy + seed,
                                         octaves=1) * amplitude
                    amplitude *= persistence
                    frequency *= lacunarity
                    
                self.height_map[y, x] = height
                
        # Normalize height map
        self.height_map = (self.height_map - self.height_map.min()) / \
                         (self.height_map.max() - self.height_map.min())
                         
    def _generate_temperature_map(self, seed: int) -> None:
        # Temperature varies with latitude (y-coordinate) and height
        for y in range(self.size):
            base_temp = 1.0 - abs(y - self.size/2) / (self.size/2)
            for x in range(self.size):
                # Add noise for local variations
                temp_noise = noise.pnoise2(x/50 + seed*2, y/50,
                                         octaves=3) * 0.2
                # Height decreases temperature
                height_factor = self.height_map[y, x] * 0.5
                self.temperature_map[y, x] = max(0, min(1,
                    base_temp + temp_noise - height_factor))
                    
    def _generate_moisture_map(self, seed: int) -> None:
        scale = 150.0
        for y in range(self.size):
            for x in range(self.size):
                # Base moisture from noise
                self.moisture_map[y, x] = noise.pnoise2(
                    x/scale + seed*3,
                    y/scale,
                    octaves=4
                )
                
        # Normalize moisture map
        self.moisture_map = (self.moisture_map - self.moisture_map.min()) / \
                           (self.moisture_map.max() - self.moisture_map.min())
                           
        # Oceans and nearby areas have more moisture
        for y in range(self.size):
            for x in range(self.size):
                if self.height_map[y, x] < 0.3:  # Ocean threshold
                    self.moisture_map[y, x] = max(self.moisture_map[y, x], 0.7)
                    
    def _generate_biome_map(self) -> None:
        for y in range(self.size):
            for x in range(self.size):
                height = self.height_map[y, x]
                temp = self.temperature_map[y, x]
                moisture = self.moisture_map[y, x]
                
                # Determine biome based on height, temperature and moisture
                if height < 0.3:
                    biome = BiomeType.OCEAN
                elif height < 0.33:
                    biome = BiomeType.BEACH
                else:
                    if temp < 0.2:
                        biome = BiomeType.SNOW
                    elif height > 0.7:
                        biome = BiomeType.MOUNTAINS
                    elif moisture > 0.6:
                        biome = BiomeType.FOREST
                    else:
                        biome = BiomeType.PLAINS
                        
                self.biome_map[y, x] = biome.value
                
    def _apply_biome_features(self) -> None:
        # Apply biome-specific height and roughness modifications
        for y in range(self.size):
            for x in range(self.size):
                biome = BiomeType(self.biome_map[y, x])
                params = self.biomes[biome]
                
                # Adjust height based on biome
                self.height_map[y, x] = self.height_map[y, x] * \
                    params.roughness + params.base_height * (1 - params.roughness)
                    
                # Add biome-specific noise
                noise_val = noise.pnoise2(x/20, y/20, octaves=3) * \
                    params.roughness * 0.1
                self.height_map[y, x] += noise_val
                
    def _generate_detail_maps(self) -> None:
        # Generate additional detail maps for rendering
        self.normal_map = np.zeros((self.size, self.size, 3), dtype=float)
        self.detail_map = np.zeros((self.size, self.size), dtype=float)
        
        # Calculate normal map
        for y in range(1, self.size-1):
            for x in range(1, self.size-1):
                dx = self.height_map[y, x+1] - self.height_map[y, x-1]
                dy = self.height_map[y+1, x] - self.height_map[y-1, x]
                dz = 2.0
                
                normal = np.array([-dx, -dy, dz])
                normal /= np.linalg.norm(normal)
                
                self.normal_map[y, x] = (normal + 1) * 0.5
                
        # Generate detail noise
        for y in range(self.size):
            for x in range(self.size):
                self.detail_map[y, x] = noise.pnoise2(
                    x/10, y/10,
                    octaves=4,
                    persistence=0.5
                )