# src/engine/rendering/procedural_generator.py

import os
import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import random
import math
import sys

# Import procedural tools
sys.path.append(os.path.join(os.path.dirname(__file__), '../../tools'))
try:
    from procedural.sprite_generator import generate_sprite
    from procedural.terrain_generator import generate_terrain
    from procedural.building_generator import generate_building_layout, assemble_building, load_modules
    from procedural.vegetation_generator import generate_tree, generate_plant
    from procedural.animation.sprite_animator import generate_walk_cycle, generate_procedural_motion
    from procedural.textures.texture_synthesizer import synthesize_pbr_texture
    PROCEDURAL_TOOLS_AVAILABLE = True
except ImportError:
    PROCEDURAL_TOOLS_AVAILABLE = False
    print("Warning: Procedural tools not available, using basic procedural generation")

class ProceduralGenerator:
    """
    Procedural asset generator for characters, environments, and items.
    Generates high-quality game assets on first launch and manages them.
    """
    def __init__(self):
        """Initialize the procedural generator."""
        # Base directories for generated assets
        self.sprites_dir = os.path.join("assets", "sprites")
        self.player_dir = os.path.join(self.sprites_dir, "player")
        self.character_templates = {}
        self.assets_generated = False
        
        # Asset tracking for caching and management
        self.generated_assets = {
            'characters': {},
            'terrain': {},
            'buildings': {},
            'vegetation': {},
            'textures': {}
        }
        
        # Quality control parameters
        self.generation_quality = 1.0  # Scale from 0.0 (low) to 1.0 (high)
        self.use_lod = True  # Level of detail support
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # Load character templates
        self._load_templates()
        
    def _ensure_directories(self):
        """Ensure that the necessary directories exist."""
        dirs = [
            self.sprites_dir,
            self.player_dir,
            os.path.join(self.player_dir, "male"),
            os.path.join(self.player_dir, "female"),
            os.path.join(self.sprites_dir, "enemies"),
            os.path.join(self.sprites_dir, "npc"),
            os.path.join("assets", "backgrounds"),
            os.path.join("assets", "ui"),
            # Additional directories for new asset types
            os.path.join("assets", "terrain"),
            os.path.join("assets", "buildings"),
            os.path.join("assets", "vegetation"),
            os.path.join("assets", "textures", "pbr"),
            os.path.join("assets", "effects")
        ]
        
        for directory in dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
    def _load_templates(self):
        """Load character templates for generation."""
        # In a real implementation, this would load base textures and parts
        # For now, we'll use simple placeholder generation
        
        # Simple silhouette templates
        self.character_templates = {
            "male": {
                "body": self._create_placeholder_body("male"),
                "head": self._create_placeholder_head("male"),
                "hair_styles": [self._create_placeholder_hair(i, "male") for i in range(6)],
                "face_styles": [self._create_placeholder_face(i, "male") for i in range(4)]
            },
            "female": {
                "body": self._create_placeholder_body("female"),
                "head": self._create_placeholder_head("female"),
                "hair_styles": [self._create_placeholder_hair(i, "female") for i in range(6)],
                "face_styles": [self._create_placeholder_face(i, "female") for i in range(4)]
            }
        }
        
    def _create_placeholder_body(self, gender):
        """Create a placeholder body shape."""
        surface = pygame.Surface((64, 128), pygame.SRCALPHA)
        
        # Different body shapes based on gender
        if gender == "male":
            # Male body is slightly wider at shoulders
            pygame.draw.rect(surface, (200, 200, 200), (16, 40, 32, 50))  # Torso
            pygame.draw.rect(surface, (200, 200, 200), (12, 90, 16, 38))  # Left leg
            pygame.draw.rect(surface, (200, 200, 200), (36, 90, 16, 38))  # Right leg
        else:
            # Female body with different proportions
            pygame.draw.rect(surface, (200, 200, 200), (20, 40, 24, 50))  # Torso
            pygame.draw.rect(surface, (200, 200, 200), (16, 90, 14, 38))  # Left leg
            pygame.draw.rect(surface, (200, 200, 200), (34, 90, 14, 38))  # Right leg
            
        return surface
        
    def _create_placeholder_head(self, gender):
        """Create a placeholder head shape."""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Simple circle for head
        pygame.draw.circle(surface, (200, 200, 200), (20, 20), 18)
        
        return surface
        
    def _create_placeholder_hair(self, style_index, gender):
        """Create a placeholder hair style."""
        surface = pygame.Surface((40, 50), pygame.SRCALPHA)
        
        # Different hair styles
        color = (180, 150, 100)  # Default blonde color
        
        if style_index == 0:  # Short hair
            pygame.draw.ellipse(surface, color, (2, 2, 36, 25))
        elif style_index == 1:  # Medium hair
            pygame.draw.ellipse(surface, color, (2, 2, 36, 30))
            pygame.draw.rect(surface, color, (8, 25, 24, 15))
        elif style_index == 2:  # Long hair
            pygame.draw.ellipse(surface, color, (2, 2, 36, 25))
            pygame.draw.rect(surface, color, (8, 20, 24, 30))
        elif style_index == 3:  # Spiky hair
            for i in range(7):
                x = 5 + i * 5
                height = 10 + random.randint(0, 10)
                pygame.draw.rect(surface, color, (x, 0, 4, height))
        elif style_index == 4:  # Bald/Very short
            pygame.draw.ellipse(surface, color, (8, 5, 24, 10))
        elif style_index == 5:  # Ponytail
            pygame.draw.ellipse(surface, color, (2, 2, 36, 25))
            pygame.draw.rect(surface, color, (20, 20, 10, 30))
            
        return surface
        
    def _create_placeholder_face(self, style_index, gender):
        """Create a placeholder face style."""
        surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Simple face features
        eye_color = (80, 80, 200)
        
        # Different eye shapes/positions based on style
        eye_y = 15
        if style_index == 0:
            # Standard eyes
            pygame.draw.circle(surface, eye_color, (12, eye_y), 3)
            pygame.draw.circle(surface, eye_color, (28, eye_y), 3)
        elif style_index == 1:
            # Narrow eyes
            pygame.draw.ellipse(surface, eye_color, (10, eye_y, 6, 2))
            pygame.draw.ellipse(surface, eye_color, (24, eye_y, 6, 2))
        elif style_index == 2:
            # Wide eyes
            pygame.draw.circle(surface, eye_color, (12, eye_y), 4)
            pygame.draw.circle(surface, eye_color, (28, eye_y), 4)
        elif style_index == 3:
            # Angry eyes
            pygame.draw.polygon(surface, eye_color, [(10, eye_y), (15, eye_y-2), (15, eye_y+2)])
            pygame.draw.polygon(surface, eye_color, [(30, eye_y), (25, eye_y-2), (25, eye_y+2)])
            
        # Add a simple mouth
        pygame.draw.line(surface, (150, 50, 50), (15, 28), (25, 28), 2)
        
        return surface
        
    def generate_character(self, gender="male", skin_tone=0, hair_style=0, hair_color=0, face_style=0, body_type=0):
        """
        Generate a character sprite based on the given parameters.
        
        Args:
            gender (str): "male" or "female"
            skin_tone (int): 0-3 (pale to dark)
            hair_style (int): 0-5 (different styles)
            hair_color (int): 0-5 (blonde, brown, black, red, etc.)
            face_style (int): 0-3 (different facial features)
            body_type (int): 0-2 (average, muscular, thin)
            
        Returns:
            bool: True if generation was successful, False otherwise.
        """
        # Validate parameters
        if gender not in ["male", "female"]:
            print(f"Invalid gender: {gender}, using male")
            gender = "male"
            
        skin_tone = max(0, min(3, skin_tone))
        hair_style = max(0, min(5, hair_style))
        hair_color = max(0, min(5, hair_color))
        face_style = max(0, min(3, face_style))
        body_type = max(0, min(2, body_type))
        
        # Asset cache key
        asset_key = f"{gender}_{skin_tone}_{hair_style}_{hair_color}_{face_style}_{body_type}"
        
        # Check if this character has already been generated
        if asset_key in self.generated_assets['characters']:
            print(f"Using cached character: {asset_key}")
            return True
            
        # Try to use the advanced sprite generator if available
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print(f"Using advanced sprite generator for character: {asset_key}")
                sprite_data = generate_sprite(
                    size=64,
                    style_hint=gender
                )
                
                # In a real implementation, we'd use the sprite_data to generate the character
                # For now, we'll fall back to our existing implementation
                sprite = self._create_character_sprite(gender, skin_tone, hair_style, hair_color, face_style, body_type)
                
                # Save the sprite
                self._save_character_sprite(sprite, gender)
                
                # Generate animations using sprite_animator if available
                self._generate_character_animations(gender, skin_tone, hair_style, hair_color, face_style, body_type)
                
                # Add to cache
                self.generated_assets['characters'][asset_key] = {
                    'gender': gender,
                    'skin_tone': skin_tone,
                    'hair_style': hair_style,
                    'hair_color': hair_color,
                    'face_style': face_style,
                    'body_type': body_type
                }
                
                return True
                
            except Exception as e:
                print(f"Error using advanced sprite generator: {e}")
                print("Falling back to basic character generation")
        
        # Create the character sprite using the built-in method
        sprite = self._create_character_sprite(gender, skin_tone, hair_style, hair_color, face_style, body_type)
        
        # Save the sprite
        self._save_character_sprite(sprite, gender)
        
        # Generate animations (idle, walk, attack)
        self._generate_character_animations(gender, skin_tone, hair_style, hair_color, face_style, body_type)
        
        # Add to cache
        self.generated_assets['characters'][asset_key] = {
            'gender': gender,
            'skin_tone': skin_tone,
            'hair_style': hair_style,
            'hair_color': hair_color,
            'face_style': face_style,
            'body_type': body_type
        }
        
        return True
        
    def _create_character_sprite(self, gender, skin_tone, hair_style, hair_color, face_style, body_type):
        """Create a character sprite by combining components."""
        # Create a surface for the character
        sprite = pygame.Surface((64, 128), pygame.SRCALPHA)
        
        # Get base templates
        body = self.character_templates[gender]["body"].copy()
        head = self.character_templates[gender]["head"].copy()
        hair = self.character_templates[gender]["hair_styles"][hair_style].copy()
        face = self.character_templates[gender]["face_styles"][face_style].copy()
        
        # Apply skin tone to body and head
        skin_colors = [
            (255, 220, 200),  # Pale
            (240, 200, 170),  # Light
            (200, 160, 120),  # Tan
            (140, 100, 70)    # Dark
        ]
        skin_color = skin_colors[skin_tone]
        
        self._colorize_surface(body, (200, 200, 200), skin_color)
        self._colorize_surface(head, (200, 200, 200), skin_color)
        
        # Apply hair color
        hair_colors = [
            (240, 220, 130),  # Blonde
            (180, 120, 70),   # Light brown
            (100, 70, 40),    # Dark brown
            (50, 40, 30),     # Black
            (180, 80, 60),    # Red
            (240, 240, 240)   # White/Gray
        ]
        hair_color_rgb = hair_colors[hair_color]
        self._colorize_surface(hair, (180, 150, 100), hair_color_rgb)
        
        # Apply body type modifications
        if body_type == 1:  # Muscular
            # Make body wider
            if gender == "male":
                pygame.draw.rect(body, skin_color, (14, 40, 36, 50))  # Wider torso
            else:
                pygame.draw.rect(body, skin_color, (18, 40, 28, 50))  # Wider torso
        elif body_type == 2:  # Thin
            # Make body thinner
            if gender == "male":
                pygame.draw.rect(body, (0, 0, 0, 0), (0, 0, 64, 128))  # Clear
                pygame.draw.rect(body, skin_color, (20, 40, 24, 50))  # Thinner torso
                pygame.draw.rect(body, skin_color, (20, 90, 12, 38))  # Left leg
                pygame.draw.rect(body, skin_color, (32, 90, 12, 38))  # Right leg
            else:
                pygame.draw.rect(body, (0, 0, 0, 0), (0, 0, 64, 128))  # Clear
                pygame.draw.rect(body, skin_color, (22, 40, 20, 50))  # Thinner torso
                pygame.draw.rect(body, skin_color, (22, 90, 10, 38))  # Left leg
                pygame.draw.rect(body, skin_color, (32, 90, 10, 38))  # Right leg
                
        # Assemble the sprite
        sprite.blit(body, (0, 0))
        sprite.blit(head, (12, 0))
        sprite.blit(face, (12, 0))
        sprite.blit(hair, (12, -5))
        
        return sprite
        
    def _colorize_surface(self, surface, old_color, new_color):
        """Colorize a surface by replacing one color with another."""
        # Get surface data
        array = pygame.surfarray.pixels3d(surface)
        
        # Find pixels of the old color
        r, g, b = old_color
        mask = (array[:,:,0] == r) & (array[:,:,1] == g) & (array[:,:,2] == b)
        
        # Replace with new color
        array[mask,0] = new_color[0]
        array[mask,1] = new_color[1]
        array[mask,2] = new_color[2]
        
        del array  # Release the surface lock
        
    def _save_character_sprite(self, sprite, gender):
        """Save the generated character sprite."""
        directory = os.path.join(self.player_dir, gender)
        
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        # Save the sprite
        filepath = os.path.join(directory, "default_idle.png")
        pygame.image.save(sprite, filepath)
        print(f"Saved character sprite to {filepath}")
        
    def _generate_character_animations(self, gender, skin_tone, hair_style, hair_color, face_style, body_type):
        """Generate character animations for different actions."""
        # Get the base sprite
        base_sprite = pygame.image.load(os.path.join(self.player_dir, gender, "default_idle.png"))
        
        # If procedural tools are available, use the sprite animator
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print("Using sprite animator for character animations")
                
                # Define sprite sheet info for the walk cycle generator
                sprite_sheet_info = {
                    'walk_start_index': 0,
                    'character_type': gender,
                    'body_type': body_type
                }
                
                # Generate walk cycle animation data
                walk_data = generate_walk_cycle(num_frames=8, sprite_sheet_info=sprite_sheet_info)
                
                # In a real implementation, we would use walk_data to create actual animation frames
                # For now, we'll just create simple frames as we did before
                
                # Create a slight variation for frame 2 (just move it up a bit)
                frame2 = base_sprite.copy()
                
                # Save animation frames
                directory = os.path.join(self.player_dir, gender)
                pygame.image.save(base_sprite, os.path.join(directory, "default_idle_1.png"))
                pygame.image.save(frame2, os.path.join(directory, "default_idle_2.png"))
                
                # Also generate walk animation frames
                walk_frame1 = base_sprite.copy()
                walk_frame2 = base_sprite.copy()
                
                # Save walk animation frames
                pygame.image.save(walk_frame1, os.path.join(directory, "default_walk_1.png"))
                pygame.image.save(walk_frame2, os.path.join(directory, "default_walk_2.png"))
                
                return
                
            except Exception as e:
                print(f"Error using sprite animator: {e}")
                print("Falling back to basic animation generation")
        
        # Fallback animation generation (simple two-frame animation)
        frame2 = base_sprite.copy()
        
        # Save animation frames
        directory = os.path.join(self.player_dir, gender)
        pygame.image.save(base_sprite, os.path.join(directory, "default_idle_1.png"))
        pygame.image.save(frame2, os.path.join(directory, "default_idle_2.png"))
        
    def generate_terrain(self, terrain_type="grass", size=(512, 512), features=None):
        """
        Generate a terrain texture and heightmap.
        
        Args:
            terrain_type (str): Type of terrain (grass, desert, snow, etc.)
            size (tuple): Size of the terrain texture and heightmap
            features (list): List of features to add (rocks, trees, etc.)
            
        Returns:
            dict: Dictionary containing paths to generated terrain files
        """
        # Default parameters
        width, height = size
        scale = 50.0  # Base terrain scale
        octaves = 4   # Number of noise octaves
        persistence = 0.5  # How much each octave contributes
        lacunarity = 2.0  # How much detail is added in each octave
        seed = random.randint(0, 10000)  # Random seed for variation
        
        # Asset key
        asset_key = f"{terrain_type}_{width}x{height}_{seed}"
        
        # Check if this terrain has already been generated
        if asset_key in self.generated_assets['terrain']:
            print(f"Using cached terrain: {asset_key}")
            return self.generated_assets['terrain'][asset_key]
        
        # Directory for terrain assets
        terrain_dir = os.path.join("assets", "terrain")
        os.makedirs(terrain_dir, exist_ok=True)
        
        # Output paths
        heightmap_path = os.path.join(terrain_dir, f"{asset_key}_heightmap.png")
        texture_path = os.path.join(terrain_dir, f"{asset_key}_texture.png")
        normal_path = os.path.join(terrain_dir, f"{asset_key}_normal.png")
        
        # Generate terrain using procedural tools if available
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print(f"Generating terrain using terrain generator: {asset_key}")
                
                # Call the terrain generator
                generate_terrain(width, height, scale, octaves, persistence, lacunarity, seed)
                
                # In a real implementation, the terrain generator would create actual heightmap
                # and texture files. Here we'll create simple placeholders.
                
                # Create a simple placeholder heightmap
                heightmap = pygame.Surface((width, height))
                heightmap.fill((100, 100, 100))  # Gray placeholder
                pygame.image.save(heightmap, heightmap_path)
                
                # Create a simple placeholder texture
                texture = pygame.Surface((width, height))
                
                # Different colors based on terrain type
                if terrain_type == "grass":
                    color = (50, 150, 50)  # Green
                elif terrain_type == "desert":
                    color = (200, 180, 100)  # Sandy
                elif terrain_type == "snow":
                    color = (230, 230, 240)  # White
                else:
                    color = (100, 100, 100)  # Gray default
                    
                texture.fill(color)
                pygame.image.save(texture, texture_path)
                
                # Create a simple placeholder normal map
                normal = pygame.Surface((width, height))
                normal.fill((128, 128, 255))  # Default normal map color
                pygame.image.save(normal, normal_path)
                
                # Store in asset cache
                terrain_data = {
                    'heightmap': heightmap_path,
                    'texture': texture_path,
                    'normal': normal_path,
                    'type': terrain_type,
                    'size': size,
                    'seed': seed
                }
                
                self.generated_assets['terrain'][asset_key] = terrain_data
                return terrain_data
                
            except Exception as e:
                print(f"Error generating terrain with terrain generator: {e}")
                print("Falling back to basic terrain generation")
        
        # Fallback: Create very simple terrain textures
        # Create a simple placeholder heightmap
        heightmap = pygame.Surface((width, height))
        heightmap.fill((100, 100, 100))  # Gray placeholder
        pygame.image.save(heightmap, heightmap_path)
        
        # Create a simple placeholder texture
        texture = pygame.Surface((width, height))
        
        # Different colors based on terrain type
        if terrain_type == "grass":
            color = (50, 150, 50)  # Green
        elif terrain_type == "desert":
            color = (200, 180, 100)  # Sandy
        elif terrain_type == "snow":
            color = (230, 230, 240)  # White
        else:
            color = (100, 100, 100)  # Gray default
            
        texture.fill(color)
        pygame.image.save(texture, texture_path)
        
        # Store in asset cache
        terrain_data = {
            'heightmap': heightmap_path,
            'texture': texture_path,
            'type': terrain_type,
            'size': size
        }
        
        self.generated_assets['terrain'][asset_key] = terrain_data
        return terrain_data
        
    def generate_building(self, building_type="house", style="medieval", size=(2, 2, 2)):
        """
        Generate a building model.
        
        Args:
            building_type (str): Type of building
            style (str): Architectural style
            size (tuple): Size in (width, depth, height)
            
        Returns:
            dict: Dictionary containing paths to generated building files
        """
        # Asset key
        asset_key = f"{building_type}_{style}_{size[0]}x{size[1]}x{size[2]}"
        
        # Check if this building has already been generated
        if asset_key in self.generated_assets['buildings']:
            print(f"Using cached building: {asset_key}")
            return self.generated_assets['buildings'][asset_key]
            
        # Directory for building assets
        buildings_dir = os.path.join("assets", "buildings")
        os.makedirs(buildings_dir, exist_ok=True)
        
        # Output paths
        model_path = os.path.join(buildings_dir, f"{asset_key}_model.obj")
        texture_path = os.path.join(buildings_dir, f"{asset_key}_texture.png")
        
        # Generate building using procedural tools if available
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print(f"Generating building using building generator: {asset_key}")
                
                # Dummy path for modules
                modules_path = os.path.join("assets", "modules", "buildings")
                
                # Load building modules
                available_modules = load_modules(modules_path)
                
                # Generate building layout
                max_floors = size[2]
                footprint_size = max(size[0], size[1])
                building_layout = generate_building_layout(available_modules, max_floors, footprint_size)
                
                # Assemble building
                assemble_building(building_layout)
                
                # In a real implementation, the building generator would create actual model
                # and texture files. Here we'll create simple placeholders.
                
                # Create a simple placeholder texture
                texture = pygame.Surface((256, 256))
                
                # Different colors based on building style
                if style == "medieval":
                    color = (150, 100, 50)  # Brown
                elif style == "modern":
                    color = (200, 200, 220)  # Light gray
                else:
                    color = (180, 180, 180)  # Gray default
                    
                texture.fill(color)
                pygame.image.save(texture, texture_path)
                
                # Create a dummy .obj file
                with open(model_path, 'w') as f:
                    f.write(f"# Building model: {building_type} in {style} style\n")
                    f.write("# This is a placeholder .obj file\n")
                    f.write("v 0 0 0\n")
                    f.write("v 1 0 0\n")
                    f.write("v 1 1 0\n")
                    f.write("v 0 1 0\n")
                    f.write("f 1 2 3 4\n")
                
                # Store in asset cache
                building_data = {
                    'model': model_path,
                    'texture': texture_path,
                    'type': building_type,
                    'style': style,
                    'size': size
                }
                
                self.generated_assets['buildings'][asset_key] = building_data
                return building_data
                
            except Exception as e:
                print(f"Error generating building with building generator: {e}")
                print("Falling back to basic building generation")
        
        # Fallback: Create very simple building model and texture
        texture = pygame.Surface((256, 256))
        
        # Different colors based on building style
        if style == "medieval":
            color = (150, 100, 50)  # Brown
        elif style == "modern":
            color = (200, 200, 220)  # Light gray
        else:
            color = (180, 180, 180)  # Gray default
            
        texture.fill(color)
        pygame.image.save(texture, texture_path)
        
        # Create a dummy .obj file
        with open(model_path, 'w') as f:
            f.write(f"# Building model: {building_type} in {style} style\n")
            f.write("# This is a placeholder .obj file\n")
            f.write("v 0 0 0\n")
            f.write("v 1 0 0\n")
            f.write("v 1 1 0\n")
            f.write("v 0 1 0\n")
            f.write("f 1 2 3 4\n")
        
        # Store in asset cache
        building_data = {
            'model': model_path,
            'texture': texture_path,
            'type': building_type,
            'style': style,
            'size': size
        }
        
        self.generated_assets['buildings'][asset_key] = building_data
        return building_data
        
    def generate_vegetation(self, veg_type="tree", style="pine", size=1.0):
        """
        Generate vegetation (trees, bushes, etc.).
        
        Args:
            veg_type (str): Type of vegetation ("tree", "bush", "grass", etc.)
            style (str): Style/species of vegetation
            size (float): Scale factor for the vegetation
            
        Returns:
            dict: Dictionary containing paths to generated vegetation files
        """
        # Asset key
        asset_key = f"{veg_type}_{style}_{size:.1f}"
        
        # Check if this vegetation has already been generated
        if asset_key in self.generated_assets['vegetation']:
            print(f"Using cached vegetation: {asset_key}")
            return self.generated_assets['vegetation'][asset_key]
            
        # Directory for vegetation assets
        vegetation_dir = os.path.join("assets", "vegetation")
        os.makedirs(vegetation_dir, exist_ok=True)
        
        # Output paths
        model_path = os.path.join(vegetation_dir, f"{asset_key}_model.obj")
        texture_path = os.path.join(vegetation_dir, f"{asset_key}_texture.png")
        
        # Generate vegetation using procedural tools if available
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print(f"Generating vegetation using vegetation generator: {asset_key}")
                
                # Parameters for L-system generation
                iterations = 4
                angle = 25.7
                
                if veg_type == "tree":
                    # Generate tree
                    generate_tree(iterations, angle)
                else:
                    # Generate plant/bush
                    generate_plant(iterations, angle)
                
                # In a real implementation, the vegetation generator would create actual model
                # and texture files. Here we'll create simple placeholders.
                
                # Create a simple placeholder texture
                texture = pygame.Surface((256, 256))
                
                # Different colors based on vegetation type
                if veg_type == "tree":
                    if style == "pine":
                        color = (30, 80, 30)  # Dark green
                    elif style == "oak":
                        color = (70, 120, 40)  # Medium green
                    else:
                        color = (50, 100, 50)  # Default green
                elif veg_type == "bush":
                    color = (60, 110, 60)  # Lighter green
                else:
                    color = (80, 140, 80)  # Light green for grass
                    
                texture.fill(color)
                pygame.image.save(texture, texture_path)
                
                # Create a dummy .obj file
                with open(model_path, 'w') as f:
                    f.write(f"# Vegetation model: {veg_type} in {style} style\n")
                    f.write("# This is a placeholder .obj file\n")
                    f.write("v 0 0 0\n")
                    f.write("v 1 0 0\n")
                    f.write("v 0 1 0\n")
                    f.write("f 1 2 3\n")
                
                # Store in asset cache
                vegetation_data = {
                    'model': model_path,
                    'texture': texture_path,
                    'type': veg_type,
                    'style': style,
                    'size': size
                }
                
                self.generated_assets['vegetation'][asset_key] = vegetation_data
                return vegetation_data
                
            except Exception as e:
                print(f"Error generating vegetation with vegetation generator: {e}")
                print("Falling back to basic vegetation generation")
        
        # Fallback: Create very simple vegetation model and texture
        texture = pygame.Surface((256, 256))
        
        # Different colors based on vegetation type
        if veg_type == "tree":
            color = (50, 100, 50)  # Green
        elif veg_type == "bush":
            color = (60, 110, 60)  # Lighter green
        else:
            color = (80, 140, 80)  # Light green for grass
            
        texture.fill(color)
        pygame.image.save(texture, texture_path)
        
        # Create a dummy .obj file
        with open(model_path, 'w') as f:
            f.write(f"# Vegetation model: {veg_type}\n")
            f.write("# This is a placeholder .obj file\n")
            f.write("v 0 0 0\n")
            f.write("v 1 0 0\n")
            f.write("v 0 1 0\n")
            f.write("f 1 2 3\n")
        
        # Store in asset cache
        vegetation_data = {
            'model': model_path,
            'texture': texture_path,
            'type': veg_type,
            'style': style,
            'size': size
        }
        
        self.generated_assets['vegetation'][asset_key] = vegetation_data
        return vegetation_data
        
    def initialize_all_assets(self):
        """Generate all required assets at first launch."""
        # Check if assets have already been generated
        if self.assets_generated:
            return
            
        print("Initializing all game assets...")
        
        # Generate character assets for both genders
        self.generate_character(gender="male")
        self.generate_character(gender="female")
        
        # Generate terrains (basic types)
        self.generate_terrain(terrain_type="grass", size=(256, 256))
        self.generate_terrain(terrain_type="desert", size=(256, 256))
        self.generate_terrain(terrain_type="snow", size=(256, 256))
        
        # Generate buildings (basic types)
        self.generate_building(building_type="house", style="medieval", size=(2, 2, 2))
        self.generate_building(building_type="shop", style="medieval", size=(2, 2, 1))
        
        # Generate vegetation (basic types)
        self.generate_vegetation(veg_type="tree", style="pine")
        self.generate_vegetation(veg_type="bush", style="shrub")
        
        # Generate PBR material textures (basic types)
        self.generate_pbr_textures(material_type="rock", size=256)
        self.generate_pbr_textures(material_type="wood", size=256)
        self.generate_pbr_textures(material_type="metal", size=256)
        
        # Set the flag
        self.assets_generated = True
        
        print("Asset generation complete!")
        
    def generate_pbr_textures(self, material_type="rock", size=512, variation=0):
        """
        Generate a set of PBR textures (albedo, normal, roughness, metallic, AO).
        
        Args:
            material_type (str): Type of material (rock, wood, metal, etc.)
            size (int): Size of the textures (usually power of 2)
            variation (int): Variation seed for the material
            
        Returns:
            dict: Dictionary containing paths to generated texture files
        """
        # Asset key
        asset_key = f"{material_type}_{size}_{variation}"
        
        # Check if these textures have already been generated
        if asset_key in self.generated_assets['textures']:
            print(f"Using cached PBR textures: {asset_key}")
            return self.generated_assets['textures'][asset_key]
            
        # Directory for texture assets
        textures_dir = os.path.join("assets", "textures", "pbr", material_type)
        os.makedirs(textures_dir, exist_ok=True)
        
        # Output paths
        albedo_path = os.path.join(textures_dir, f"{asset_key}_albedo.png")
        normal_path = os.path.join(textures_dir, f"{asset_key}_normal.png")
        roughness_path = os.path.join(textures_dir, f"{asset_key}_roughness.png")
        metallic_path = os.path.join(textures_dir, f"{asset_key}_metallic.png")
        ao_path = os.path.join(textures_dir, f"{asset_key}_ao.png")
        
        # Generate textures using procedural tools if available
        if PROCEDURAL_TOOLS_AVAILABLE:
            try:
                print(f"Generating PBR textures using texture synthesizer: {asset_key}")
                
                # Material-specific color parameters
                if material_type == "rock":
                    base_color1 = (0.8, 0.7, 0.6)  # Light rock
                    base_color2 = (0.5, 0.45, 0.4)  # Dark rock
                    roughness_params = {'base': 0.7, 'variation': 0.2}
                elif material_type == "wood":
                    base_color1 = (0.6, 0.4, 0.2)  # Light wood
                    base_color2 = (0.3, 0.2, 0.1)  # Dark wood
                    roughness_params = {'base': 0.5, 'variation': 0.3}
                elif material_type == "metal":
                    base_color1 = (0.7, 0.7, 0.7)  # Light metal
                    base_color2 = (0.3, 0.3, 0.3)  # Dark metal
                    roughness_params = {'base': 0.1, 'variation': 0.1}
                else:
                    base_color1 = (0.7, 0.7, 0.7)  # Light gray
                    base_color2 = (0.3, 0.3, 0.3)  # Dark gray
                    roughness_params = {'base': 0.5, 'variation': 0.2}
                
                # Generate PBR texture set
                synthesize_pbr_texture(
                    size=size,
                    base_color1=base_color1,
                    base_color2=base_color2,
                    roughness_params=roughness_params
                )
                
                # In a real implementation, the texture synthesizer would create actual texture files
                # Here we'll create simple placeholders
                
                # Create placeholder textures
                for path, default_color in [
                    (albedo_path, (int(base_color1[0]*255), int(base_color1[1]*255), int(base_color1[2]*255))),
                    (normal_path, (128, 128, 255)),  # Default normal map blue
                    (roughness_path, (int(roughness_params['base']*255),)*3),
                    (metallic_path, (0, 0, 0)),  # Non-metallic by default
                    (ao_path, (255, 255, 255))  # White AO by default
                ]:
                    texture = pygame.Surface((size, size))
                    texture.fill(default_color)
                    pygame.image.save(texture, path)
                
                # Store in asset cache
                texture_data = {
                    'albedo': albedo_path,
                    'normal': normal_path,
                    'roughness': roughness_path,
                    'metallic': metallic_path,
                    'ao': ao_path,
                    'type': material_type,
                    'size': size
                }
                
                self.generated_assets['textures'][asset_key] = texture_data
                return texture_data
                
            except Exception as e:
                print(f"Error generating PBR textures with texture synthesizer: {e}")
                print("Falling back to basic texture generation")
        
        # Fallback: Create very simple texture placeholders
        # Material-specific color parameters
        if material_type == "rock":
            base_color = (170, 160, 150)
        elif material_type == "wood":
            base_color = (140, 100, 60)
        elif material_type == "metal":
            base_color = (180, 180, 190)
        else:
            base_color = (128, 128, 128)
        
        # Create placeholder textures
        for path, default_color in [
            (albedo_path, base_color),
            (normal_path, (128, 128, 255)),  # Default normal map blue
            (roughness_path, (128, 128, 128)),
            (metallic_path, (0, 0, 0)),  # Non-metallic by default
            (ao_path, (255, 255, 255))  # White AO by default
        ]:
            texture = pygame.Surface((size, size))
            texture.fill(default_color)
            pygame.image.save(texture, path)
        
        # Store in asset cache
        texture_data = {
            'albedo': albedo_path,
            'normal': normal_path,
            'roughness': roughness_path,
            'metallic': metallic_path,
            'ao': ao_path,
            'type': material_type,
            'size': size
        }
        
        self.generated_assets['textures'][asset_key] = texture_data
        return texture_data
        
    def populate_world_area(self, area_type="forest", size=(100, 100), density=0.5):
        """
        Generate a full world area populated with appropriate assets.
        
        Args:
            area_type (str): Type of area ("forest", "village", "mountain", etc.)
            size (tuple): Size of the area in world units
            density (float): Density of objects (0.0 to 1.0)
            
        Returns:
            dict: Dictionary containing all generated assets and their positions
        """
        print(f"Populating world area: {area_type} ({size[0]}x{size[1]}, density={density:.1f})")
        
        # Adjust density to valid range
        density = max(0.1, min(1.0, density))
        
        # Create a dictionary to store all area data
        area_data = {
            'type': area_type,
            'size': size,
            'terrain': None,
            'objects': []
        }
        
        # Generate base terrain
        if area_type == "forest":
            area_data['terrain'] = self.generate_terrain(terrain_type="grass", size=(512, 512))
        elif area_type == "desert":
            area_data['terrain'] = self.generate_terrain(terrain_type="desert", size=(512, 512))
        elif area_type == "snow":
            area_data['terrain'] = self.generate_terrain(terrain_type="snow", size=(512, 512))
        elif area_type == "village":
            area_data['terrain'] = self.generate_terrain(terrain_type="grass", size=(512, 512))
        else:
            area_data['terrain'] = self.generate_terrain(terrain_type="grass", size=(512, 512))
        
        # Populate with appropriate objects based on area type
        if area_type == "forest":
            # Add trees
            num_trees = int((size[0] * size[1]) * density * 0.01)  # Adjust density factor as needed
            for _ in range(num_trees):
                x = random.uniform(0, size[0])
                y = random.uniform(0, size[1])
                tree_style = random.choice(["pine", "oak", "birch"])
                tree_size = random.uniform(0.8, 1.2)
                tree_data = self.generate_vegetation(veg_type="tree", style=tree_style, size=tree_size)
                area_data['objects'].append({
                    'type': 'vegetation',
                    'data': tree_data,
                    'position': (x, y, 0)
                })
            
            # Add bushes
            num_bushes = int((size[0] * size[1]) * density * 0.02)
            for _ in range(num_bushes):
                x = random.uniform(0, size[0])
                y = random.uniform(0, size[1])
                bush_data = self.generate_vegetation(veg_type="bush", style="shrub", size=random.uniform(0.5, 1.0))
                area_data['objects'].append({
                    'type': 'vegetation',
                    'data': bush_data,
                    'position': (x, y, 0)
                })
                
        elif area_type == "village":
            # Add buildings
            num_buildings = int((size[0] * size[1]) * density * 0.005)
            for _ in range(num_buildings):
                x = random.uniform(0, size[0])
                y = random.uniform(0, size[1])
                building_type = random.choice(["house", "shop", "inn"])
                building_size = (
                    random.randint(2, 4),
                    random.randint(2, 4),
                    random.randint(1, 3)
                )
                building_data = self.generate_building(building_type=building_type, style="medieval", size=building_size)
                area_data['objects'].append({
                    'type': 'building',
                    'data': building_data,
                    'position': (x, y, 0)
                })
                
            # Add some vegetation too
            num_trees = int((size[0] * size[1]) * density * 0.002)
            for _ in range(num_trees):
                x = random.uniform(0, size[0])
                y = random.uniform(0, size[1])
                tree_data = self.generate_vegetation(veg_type="tree", style="oak", size=random.uniform(0.8, 1.0))
                area_data['objects'].append({
                    'type': 'vegetation',
                    'data': tree_data,
                    'position': (x, y, 0)
                })
        
        # Other area types would have their own population logic
        
        print(f"World area populated with {len(area_data['objects'])} objects")
        return area_data
        
    def _log_info(self, message):
        """Log an informational message."""
        print(f"[ProceduralGenerator INFO] {message}")
        
    def _log_warning(self, message):
        """Log a warning message."""
        print(f"[ProceduralGenerator WARNING] {message}")
        
    def _log_error(self, message, exception=None):
        """Log an error message with optional exception details."""
        error_msg = f"[ProceduralGenerator ERROR] {message}"
        if exception:
            error_msg += f": {type(exception).__name__}: {str(exception)}"
        print(error_msg)
        
    def set_generation_quality(self, quality):
        """
        Set the generation quality for all assets.
        
        Args:
            quality (float): Quality level from 0.0 (lowest) to 1.0 (highest)
        """
        self.generation_quality = max(0.0, min(1.0, quality))
        self._log_info(f"Generation quality set to {self.generation_quality:.1f}")
        
    def toggle_lod(self, use_lod):
        """
        Toggle level of detail support.
        
        Args:
            use_lod (bool): Whether to use level of detail
        """
        self.use_lod = use_lod
        self._log_info(f"Level of detail {'enabled' if use_lod else 'disabled'}")
        
    def clear_asset_cache(self, asset_type=None):
        """
        Clear the asset cache for the specified type, or all types if None.
        
        Args:
            asset_type (str, optional): Type of assets to clear, or None for all
        """
        if asset_type is None:
            # Clear all asset caches
            for key in self.generated_assets:
                self.generated_assets[key] = {}
            self._log_info("Cleared all asset caches")
        elif asset_type in self.generated_assets:
            # Clear specific asset cache
            self.generated_assets[asset_type] = {}
            self._log_info(f"Cleared {asset_type} asset cache")
        else:
            self._log_warning(f"Unknown asset type: {asset_type}")
            
    def get_asset_stats(self):
        """
        Get statistics about generated assets.
        
        Returns:
            dict: Dictionary with asset counts by type
        """
        stats = {}
        for asset_type, assets in self.generated_assets.items():
            stats[asset_type] = len(assets)
        return stats 