#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Terrain Generator for Nightfall Defenders
Procedurally generates environment tiles in Octopath Traveler style
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import random
import noise
import math
import colorsys

class TerrainGenerator:
    """Generator for procedural terrain tiles and environment assets"""
    
    def __init__(self, output_dir):
        """
        Initialize the terrain generator
        
        Args:
            output_dir (str): Directory to save generated terrain
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories for different terrain types
        self.terrain_dirs = {
            "grass": os.path.join(output_dir, "grass"),
            "forest": os.path.join(output_dir, "forest"),
            "mountain": os.path.join(output_dir, "mountain"),
            "water": os.path.join(output_dir, "water"),
            "desert": os.path.join(output_dir, "desert"),
            "snow": os.path.join(output_dir, "snow"),
            "buildings": os.path.join(output_dir, "buildings"),
            "props": os.path.join(output_dir, "props")
        }
        
        for directory in self.terrain_dirs.values():
            os.makedirs(directory, exist_ok=True)
        
        # Tile settings
        self.tile_size = 64
        self.pixel_scale = 1  # For pixel art scaling
        
        # Terrain color palettes (RGB)
        self.terrain_palettes = {
            "grass": {
                "base": (76, 153, 76),
                "variation": [(60, 130, 60), (90, 170, 90)],
                "detail": (40, 100, 40),
                "highlight": (120, 180, 120)
            },
            "forest": {
                "base": (40, 100, 50),
                "variation": [(30, 80, 40), (60, 120, 60)],
                "detail": (25, 60, 30),
                "highlight": (70, 140, 70)
            },
            "mountain": {
                "base": (120, 110, 100),
                "variation": [(100, 90, 80), (140, 130, 120)],
                "detail": (80, 70, 60),
                "highlight": (160, 150, 140)
            },
            "water": {
                "base": (60, 100, 180),
                "variation": [(50, 80, 160), (70, 120, 200)],
                "detail": (40, 70, 150),
                "highlight": (100, 140, 220)
            },
            "desert": {
                "base": (210, 180, 130),
                "variation": [(190, 160, 110), (230, 200, 150)],
                "detail": (170, 140, 90),
                "highlight": (240, 220, 180)
            },
            "snow": {
                "base": (230, 230, 240),
                "variation": [(210, 210, 220), (250, 250, 255)],
                "detail": (190, 190, 200),
                "highlight": (255, 255, 255)
            }
        }
    
    def generate_tile(self, terrain_type, seed=None):
        """
        Generate a terrain tile of the specified type
        
        Args:
            terrain_type (str): Type of terrain to generate
            seed (int): Random seed for deterministic generation
            
        Returns:
            PIL.Image: The generated tile
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        if terrain_type not in self.terrain_palettes:
            raise ValueError(f"Unknown terrain type: {terrain_type}")
        
        # Create a base tile image
        img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
        
        # Generate terrain based on type
        if terrain_type == "grass":
            img = self.generate_grass_tile(img, seed)
        elif terrain_type == "forest":
            img = self.generate_forest_tile(img, seed)
        elif terrain_type == "mountain":
            img = self.generate_mountain_tile(img, seed)
        elif terrain_type == "water":
            img = self.generate_water_tile(img, seed)
        elif terrain_type == "desert":
            img = self.generate_desert_tile(img, seed)
        elif terrain_type == "snow":
            img = self.generate_snow_tile(img, seed)
        
        # Apply Octopath Traveler style post-processing
        img = self.apply_octopath_style(img)
        
        # Scale up the image for pixel art clarity
        if self.pixel_scale > 1:
            img = img.resize(
                (self.tile_size * self.pixel_scale, self.tile_size * self.pixel_scale),
                Image.NEAREST
            )
        
        return img
    
    def generate_grass_tile(self, img, seed=None):
        """Generate a grass terrain tile"""
        draw = ImageDraw.Draw(img)
        palette = self.terrain_palettes["grass"]
        
        # Fill base color
        draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill=palette["base"])
        
        # Add noise variation
        img = self.apply_perlin_noise(img, palette["variation"], scale=20.0, seed=seed)
        
        # Add grass detail
        self.add_grass_detail(img, palette, density=40, seed=seed)
        
        return img
    
    def generate_forest_tile(self, img, seed=None):
        """Generate a forest terrain tile"""
        # Start with a grass base
        img = self.generate_grass_tile(img, seed)
        palette = self.terrain_palettes["forest"]
        
        # Make it a bit darker overall
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.85)
        
        # Add tree base shapes (just random dark spots for now)
        self.add_tree_spots(img, palette, density=3, seed=seed)
        
        return img
    
    def generate_mountain_tile(self, img, seed=None):
        """Generate a mountain terrain tile"""
        draw = ImageDraw.Draw(img)
        palette = self.terrain_palettes["mountain"]
        
        # Fill base color
        draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill=palette["base"])
        
        # Add noise variation for rocky texture
        img = self.apply_perlin_noise(img, palette["variation"], scale=10.0, octaves=4, seed=seed)
        
        # Add rocky detail
        self.add_rocky_detail(img, palette, density=15, seed=seed)
        
        return img
    
    def generate_water_tile(self, img, seed=None):
        """Generate a water terrain tile"""
        draw = ImageDraw.Draw(img)
        palette = self.terrain_palettes["water"]
        
        # Fill base color
        draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill=palette["base"])
        
        # Add noise variation for water ripples
        # Use a lower amplitude noise to make it subtle
        img = self.apply_perlin_noise(img, palette["variation"], scale=30.0, amplitude=0.5, seed=seed)
        
        # Add wave highlights
        self.add_wave_detail(img, palette, density=10, seed=seed)
        
        return img
    
    def generate_desert_tile(self, img, seed=None):
        """Generate a desert terrain tile"""
        draw = ImageDraw.Draw(img)
        palette = self.terrain_palettes["desert"]
        
        # Fill base color
        draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill=palette["base"])
        
        # Add noise variation for sandy texture
        img = self.apply_perlin_noise(img, palette["variation"], scale=15.0, seed=seed)
        
        # Add sand dune detail
        self.add_sand_detail(img, palette, density=8, seed=seed)
        
        return img
    
    def generate_snow_tile(self, img, seed=None):
        """Generate a snow terrain tile"""
        draw = ImageDraw.Draw(img)
        palette = self.terrain_palettes["snow"]
        
        # Fill base color
        draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill=palette["base"])
        
        # Add noise variation for snow texture
        img = self.apply_perlin_noise(img, palette["variation"], scale=25.0, amplitude=0.3, seed=seed)
        
        # Add snow detail (subtle sparkles)
        self.add_snow_detail(img, palette, density=20, seed=seed)
        
        return img
    
    def apply_perlin_noise(self, img, variation_colors, scale=20.0, octaves=2, persistence=0.5, amplitude=1.0, seed=None):
        """Apply Perlin noise variation to an image"""
        if seed is not None:
            noise_seed = seed
        else:
            noise_seed = random.randint(0, 1000)
        
        # Create a copy of the image to work with
        result = img.copy()
        pixels = result.load()
        
        # Get color variation range
        color_min = variation_colors[0]
        color_max = variation_colors[1]
        
        # Apply noise to each pixel
        for y in range(self.tile_size):
            for x in range(self.tile_size):
                # Get Perlin noise value
                nx = x / self.tile_size * scale
                ny = y / self.tile_size * scale
                noise_val = noise.pnoise2(nx, ny, octaves=octaves, persistence=persistence, base=noise_seed)
                
                # Normalize noise to 0-1 range
                noise_val = (noise_val + 1) / 2
                
                # Adjust by amplitude
                noise_val = 0.5 + (noise_val - 0.5) * amplitude
                
                # Get current pixel color
                r, g, b, a = pixels[x, y]
                
                if (r, g, b, a) == (0, 0, 0, 0):  # If transparent, skip
                    continue
                
                # Interpolate between variation colors based on noise
                new_r = int(color_min[0] + (color_max[0] - color_min[0]) * noise_val)
                new_g = int(color_min[1] + (color_max[1] - color_min[1]) * noise_val)
                new_b = int(color_min[2] + (color_max[2] - color_min[2]) * noise_val)
                
                # Set new pixel color
                pixels[x, y] = (new_r, new_g, new_b, a)
        
        return result
    
    def add_grass_detail(self, img, palette, density=30, seed=None):
        """Add grass details to a terrain tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add small grass clumps
        for _ in range(density):
            x = random.randint(0, self.tile_size - 1)
            y = random.randint(0, self.tile_size - 1)
            
            # Randomize size
            size = random.randint(1, 3)
            
            # Choose detail or highlight color
            if random.random() < 0.7:
                color = palette["detail"]
            else:
                color = palette["highlight"]
            
            # Draw grass tuft
            if random.random() < 0.5:
                # Small lines
                angle = random.uniform(0, math.pi)
                x2 = x + size * math.cos(angle)
                y2 = y + size * math.sin(angle)
                draw.line([(x, y), (x2, y2)], fill=color, width=1)
            else:
                # Small dots
                draw.point([(x, y)], fill=color)
    
    def add_tree_spots(self, img, palette, density=3, seed=None):
        """Add tree base shapes to a forest tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add tree bases as dark circles
        for _ in range(density):
            x = random.randint(5, self.tile_size - 5)
            y = random.randint(5, self.tile_size - 5)
            
            # Randomize size
            radius = random.randint(3, 8)
            
            # Draw tree base
            draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=palette["detail"])
            
            # Draw highlight on one side for 3D effect
            highlight_angle = random.uniform(0, 2*math.pi)
            hx = x + int(radius * 0.7 * math.cos(highlight_angle))
            hy = y + int(radius * 0.7 * math.sin(highlight_angle))
            draw.ellipse([(hx-1, hy-1), (hx+1, hy+1)], fill=palette["highlight"])
    
    def add_rocky_detail(self, img, palette, density=15, seed=None):
        """Add rocky details to a mountain tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add rock shapes
        for _ in range(density):
            x = random.randint(5, self.tile_size - 5)
            y = random.randint(5, self.tile_size - 5)
            
            # Randomize size
            size = random.randint(2, 6)
            
            # Draw rock
            if random.random() < 0.7:
                # Angular rock
                points = []
                for i in range(5):
                    angle = math.pi * 2 * i / 5 + random.uniform(0, 0.5)
                    dist = size * (0.8 + random.random() * 0.4)
                    px = x + dist * math.cos(angle)
                    py = y + dist * math.sin(angle)
                    points.append((px, py))
                
                # Choose detail or highlight color
                if random.random() < 0.6:
                    color = palette["detail"]
                else:
                    color = palette["highlight"]
                    
                draw.polygon(points, fill=color)
            else:
                # Simple circular rock
                draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=palette["detail"])
    
    def add_wave_detail(self, img, palette, density=10, seed=None):
        """Add wave details to a water tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add wave highlights as curved lines
        for _ in range(density):
            x = random.randint(5, self.tile_size - 15)
            y = random.randint(5, self.tile_size - 5)
            
            # Randomize size
            width = random.randint(5, 15)
            height = random.randint(1, 3)
            
            # Draw a curved wave
            points = []
            for i in range(5):
                px = x + (width * i / 4)
                py = y + height * math.sin(i * math.pi / 2)
                points.append((px, py))
            
            draw.line(points, fill=palette["highlight"], width=1)
    
    def add_sand_detail(self, img, palette, density=8, seed=None):
        """Add sand details to a desert tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add sand ripples as curved lines
        for _ in range(density):
            x = random.randint(0, self.tile_size - 20)
            y = random.randint(0, self.tile_size - 1)
            
            # Randomize size
            width = random.randint(15, 30)
            height = random.randint(1, 2)
            
            # Draw a curved sand ripple
            points = []
            for i in range(width):
                px = x + i
                # Slight curve for ripple effect
                py = y + height * math.sin(i * math.pi / width)
                points.append((px, py))
            
            # Choose detail or highlight color
            if random.random() < 0.5:
                color = palette["detail"]
            else:
                color = palette["highlight"]
                
            draw.line(points, fill=color, width=1)
    
    def add_snow_detail(self, img, palette, density=20, seed=None):
        """Add snow details to a snow tile"""
        if seed is not None:
            random.seed(seed)
        
        draw = ImageDraw.Draw(img)
        
        # Add snow sparkles as small dots
        for _ in range(density):
            x = random.randint(0, self.tile_size - 1)
            y = random.randint(0, self.tile_size - 1)
            
            # Always use highlight color for sparkles
            color = palette["highlight"]
            
            # Draw a small sparkle
            if random.random() < 0.7:
                # Single pixel
                draw.point([(x, y)], fill=color)
            else:
                # Small cross
                draw.line([(x-1, y), (x+1, y)], fill=color, width=1)
                draw.line([(x, y-1), (x, y+1)], fill=color, width=1)
    
    def apply_octopath_style(self, img):
        """Apply Octopath Traveler-inspired post-processing effects"""
        # Increase contrast slightly
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Add a slight blur for anti-aliasing edges
        img = img.filter(ImageFilter.GaussianBlur(0.5))
        
        # Re-sharpen to maintain pixel art feel
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        
        return img
    
    def generate_tileset(self, terrain_type, variations=5, seed=None):
        """
        Generate a set of terrain tiles of the specified type
        
        Args:
            terrain_type (str): Type of terrain to generate
            variations (int): Number of tile variations to generate
            seed (int): Base random seed for deterministic generation
            
        Returns:
            list: List of generated tile images
        """
        tiles = []
        
        for i in range(variations):
            if seed is not None:
                # Use different but deterministic seeds for each variation
                var_seed = seed + i * 100
            else:
                var_seed = None
                
            tile = self.generate_tile(terrain_type, seed=var_seed)
            tiles.append(tile)
            
        return tiles
    
    def save_tile(self, tile, filename):
        """
        Save a generated tile to disk
        
        Args:
            tile (PIL.Image): The tile image to save
            filename (str): The filename to save as
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            tile.save(filename)
            print(f"Saved terrain tile to {filename}")
        except Exception as e:
            print(f"Error saving terrain tile: {e}")
    
    def generate_with_cache(self, asset_id, params=None, seed=None):
        """
        Generate a terrain asset with caching support
        
        Args:
            asset_id (str): Identifier for the asset
            params (dict): Parameters for generation
            seed (int): Random seed for generation
            
        Returns:
            PIL.Image: The generated terrain
        """
        if params is None:
            params = {}
        
        # Extract terrain type from asset_id if not in params
        if "terrain_type" not in params:
            parts = asset_id.split('_')
            if parts and parts[0] in self.terrain_palettes:
                params["terrain_type"] = parts[0]
            else:
                # Default to grass if no terrain type found
                params["terrain_type"] = "grass"
        
        # Generate the terrain tile
        return self.generate_tile(params["terrain_type"], seed)
    
    def save_asset(self, asset, output_path):
        """
        Save the generated asset to disk
        
        Args:
            asset (PIL.Image): The asset to save
            output_path (str): Path to save the asset to
        """
        try:
            asset.save(output_path)
            print(f"Saved terrain asset to {output_path}")
        except Exception as e:
            print(f"Error saving terrain asset: {e}")
    
    def save_metadata(self, asset_id, metadata):
        """
        Save metadata for the generated asset
        
        Args:
            asset_id (str): Identifier for the asset
            metadata (dict): Metadata to save
        """
        # Create metadata directory if it doesn't exist
        metadata_dir = os.path.join(self.output_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        # Save metadata to JSON file
        import json
        metadata_path = os.path.join(metadata_dir, f"{asset_id}.json")
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def generate_all_terrain_types(self, variations_per_type=3, seed=None):
        """
        Generate tiles for all terrain types
        
        Args:
            variations_per_type (int): Number of variations per terrain type
            seed (int): Base random seed
            
        Returns:
            dict: Dictionary of terrain_type -> list of tile images
        """
        all_tiles = {}
        
        for terrain_type in self.terrain_palettes.keys():
            if seed is not None:
                # Use different but deterministic seeds for each type
                type_seed = seed + hash(terrain_type) % 1000
            else:
                type_seed = None
                
            all_tiles[terrain_type] = self.generate_tileset(terrain_type, variations=variations_per_type, seed=type_seed)
            
        return all_tiles


def main():
    """Generate and save example terrain tiles"""
    output_dir = os.path.join("src", "assets", "generated", "environment")
    generator = TerrainGenerator(output_dir)
    
    # Generate tiles for each terrain type
    all_tiles = generator.generate_all_terrain_types(variations_per_type=3, seed=42)
    
    # Save all generated tiles
    for terrain_type, tiles in all_tiles.items():
        for i, tile in enumerate(tiles):
            filename = f"{terrain_type}_tile_{i+1}.png"
            generator.save_tile(tile, filename)
            print(f"Generated {terrain_type} tile {i+1}")


if __name__ == "__main__":
    main() 