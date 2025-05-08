#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Asset Generator for Nightfall Defenders
Generates all game assets procedurally
"""

import os
import sys
import argparse
from tqdm import tqdm

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.tools.asset_generator.sprite_generator import SpriteGenerator
from src.tools.asset_generator.terrain_generator import TerrainGenerator

# Define asset generation configurations
ASSET_CONFIG = {
    "characters": {
        "class_types": ["warrior", "mage", "cleric", "alchemist", "ranger", "summoner"],
        "variations_per_class": 1,
        "animation_frames": {
            "idle": 4,
            "walk": 8,
            "attack": 6
        }
    },
    "terrain": {
        "terrain_types": ["grass", "forest", "mountain", "water", "desert", "snow"],
        "variations_per_type": 3
    },
    "props": {
        "prop_types": ["tree", "rock", "bush", "flower", "chest", "sign"],
        "variations_per_type": 2
    },
    "buildings": {
        "building_types": ["house", "shop", "temple", "tower", "wall", "gate"],
        "variations_per_type": 1
    },
    "ui": {
        "button_states": ["normal", "hover", "pressed", "disabled"],
        "panel_types": ["inventory", "character", "map", "options"],
        "icon_types": ["health", "mana", "stamina", "attack", "defense", "speed"]
    }
}

def setup_output_directories():
    """Set up output directories for generated assets"""
    # Create base directories
    base_dir = os.path.join("src", "assets", "generated")
    os.makedirs(base_dir, exist_ok=True)
    
    # Create subdirectories for each asset type
    directories = [
        os.path.join(base_dir, "characters"),
        os.path.join(base_dir, "environment"),
        os.path.join(base_dir, "props"),
        os.path.join(base_dir, "buildings"),
        os.path.join(base_dir, "ui")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create subdirectories for character classes
    for class_type in ASSET_CONFIG["characters"]["class_types"]:
        os.makedirs(os.path.join(base_dir, "characters", class_type), exist_ok=True)
    
    # Create subdirectories for terrain types
    for terrain_type in ASSET_CONFIG["terrain"]["terrain_types"]:
        os.makedirs(os.path.join(base_dir, "environment", terrain_type), exist_ok=True)
    
    return base_dir

def generate_character_assets(base_dir, seed=None):
    """Generate character assets"""
    print("Generating character assets...")
    
    # Create sprite generator
    character_dir = os.path.join(base_dir, "characters")
    sprite_generator = SpriteGenerator(character_dir)
    
    # Generate each character class
    for class_type in tqdm(ASSET_CONFIG["characters"]["class_types"], desc="Character Classes"):
        class_dir = os.path.join(character_dir, class_type)
        
        # Generate variations
        for i in range(ASSET_CONFIG["characters"]["variations_per_class"]):
            # Use a deterministic seed if provided
            if seed is not None:
                var_seed = seed + hash(class_type + str(i)) % 1000
            else:
                var_seed = None
            
            # Generate base character sprite
            sprite = sprite_generator.generate_character(class_type, seed=var_seed)
            sprite_generator.save_sprite(sprite, os.path.join(class_type, f"{class_type}_base_{i+1}.png"))
            
            # In a full implementation, we would generate animation frames here
            # For now, just use the base sprite for all frames
            for anim_type, frame_count in ASSET_CONFIG["characters"]["animation_frames"].items():
                for frame in range(frame_count):
                    sprite_generator.save_sprite(sprite, os.path.join(class_type, f"{class_type}_{anim_type}_{frame+1}.png"))
    
    print(f"Generated {len(ASSET_CONFIG['characters']['class_types'])} character classes")

def generate_terrain_assets(base_dir, seed=None):
    """Generate terrain assets"""
    print("Generating terrain assets...")
    
    # Create terrain generator
    environment_dir = os.path.join(base_dir, "environment")
    terrain_generator = TerrainGenerator(environment_dir)
    
    # Generate each terrain type
    all_tiles = terrain_generator.generate_all_terrain_types(
        variations_per_type=ASSET_CONFIG["terrain"]["variations_per_type"],
        seed=seed
    )
    
    # Save all generated tiles
    for terrain_type, tiles in all_tiles.items():
        for i, tile in enumerate(tiles):
            filename = f"{terrain_type}_tile_{i+1}.png"
            terrain_generator.save_tile(tile, filename)
    
    print(f"Generated {len(ASSET_CONFIG['terrain']['terrain_types'])} terrain types")

def generate_prop_assets(base_dir, seed=None):
    """Generate prop assets"""
    print("Generating prop assets (placeholder)...")
    
    # In a full implementation, we would have a dedicated prop generator
    # For now, just create placeholder images
    props_dir = os.path.join(base_dir, "props")
    
    for prop_type in tqdm(ASSET_CONFIG["props"]["prop_types"], desc="Props"):
        # Create prop subdirectory
        prop_subdir = os.path.join(props_dir, prop_type)
        os.makedirs(prop_subdir, exist_ok=True)
        
        # Generate variations
        for i in range(ASSET_CONFIG["props"]["variations_per_type"]):
            # Create a simple colored square as a placeholder
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Use different colors for different prop types
            colors = {
                "tree": (40, 100, 40),
                "rock": (120, 120, 120),
                "bush": (60, 120, 60),
                "flower": (200, 100, 200),
                "chest": (180, 140, 60),
                "sign": (140, 100, 60)
            }
            
            # Draw a simple shape
            color = colors.get(prop_type, (150, 150, 150))
            draw.rectangle([(4, 4), (28, 28)], fill=color)
            
            # Save the placeholder
            filename = os.path.join(prop_subdir, f"{prop_type}_{i+1}.png")
            img.save(filename, "PNG")
    
    print(f"Generated placeholders for {len(ASSET_CONFIG['props']['prop_types'])} prop types")

def generate_building_assets(base_dir, seed=None):
    """Generate building assets"""
    print("Generating building assets (placeholder)...")
    
    # In a full implementation, we would have a dedicated building generator
    # For now, just create placeholder images
    buildings_dir = os.path.join(base_dir, "buildings")
    
    for building_type in tqdm(ASSET_CONFIG["buildings"]["building_types"], desc="Buildings"):
        # Create building subdirectory
        building_subdir = os.path.join(buildings_dir, building_type)
        os.makedirs(building_subdir, exist_ok=True)
        
        # Generate variations
        for i in range(ASSET_CONFIG["buildings"]["variations_per_type"]):
            # Create a simple colored rectangle as a placeholder
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Use different colors for different building types
            colors = {
                "house": (180, 120, 80),
                "shop": (160, 140, 100),
                "temple": (200, 200, 220),
                "tower": (140, 140, 160),
                "wall": (120, 120, 120),
                "gate": (100, 100, 100)
            }
            
            # Draw a simple building shape
            color = colors.get(building_type, (150, 150, 150))
            
            if building_type in ["house", "shop", "temple"]:
                # House-like buildings
                # Main building
                draw.rectangle([(8, 20), (56, 60)], fill=color)
                # Roof
                draw.polygon([(8, 20), (32, 4), (56, 20)], fill=(100, 60, 60))
            elif building_type == "tower":
                # Tower
                draw.rectangle([(16, 8), (48, 60)], fill=color)
                # Top
                draw.polygon([(16, 8), (32, 2), (48, 8)], fill=(80, 80, 100))
            elif building_type in ["wall", "gate"]:
                # Wall or gate
                draw.rectangle([(4, 30), (60, 60)], fill=color)
                if building_type == "gate":
                    # Gate opening
                    draw.rectangle([(24, 40), (40, 60)], fill=(0, 0, 0, 0))
            
            # Save the placeholder
            filename = os.path.join(building_subdir, f"{building_type}_{i+1}.png")
            img.save(filename, "PNG")
    
    print(f"Generated placeholders for {len(ASSET_CONFIG['buildings']['building_types'])} building types")

def generate_ui_assets(base_dir, seed=None):
    """Generate UI assets"""
    print("Generating UI assets (placeholder)...")
    
    # In a full implementation, we would have a dedicated UI generator
    # For now, just create placeholder images
    ui_dir = os.path.join(base_dir, "ui")
    
    # Generate buttons
    buttons_dir = os.path.join(ui_dir, "buttons")
    os.makedirs(buttons_dir, exist_ok=True)
    
    for state in tqdm(ASSET_CONFIG["ui"]["button_states"], desc="UI Buttons"):
        # Create a simple button as a placeholder
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (120, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Use different colors for different button states
        colors = {
            "normal": (80, 80, 100, 230),
            "hover": (100, 100, 140, 230),
            "pressed": (60, 60, 80, 230),
            "disabled": (80, 80, 80, 180)
        }
        
        # Draw a simple button shape
        color = colors.get(state, (100, 100, 100, 200))
        draw.rectangle([(0, 0), (120, 40)], fill=color, outline=(255, 255, 255, 100), width=2)
        
        # Save the placeholder
        filename = os.path.join(buttons_dir, f"button_{state}.png")
        img.save(filename, "PNG")
    
    # Generate panels
    panels_dir = os.path.join(ui_dir, "panels")
    os.makedirs(panels_dir, exist_ok=True)
    
    for panel_type in tqdm(ASSET_CONFIG["ui"]["panel_types"], desc="UI Panels"):
        # Create a simple panel as a placeholder
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (300, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple panel shape
        draw.rectangle([(0, 0), (300, 200)], fill=(40, 40, 60, 200), outline=(255, 255, 255, 150), width=2)
        
        # Save the placeholder
        filename = os.path.join(panels_dir, f"panel_{panel_type}.png")
        img.save(filename, "PNG")
    
    # Generate icons
    icons_dir = os.path.join(ui_dir, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    for icon_type in tqdm(ASSET_CONFIG["ui"]["icon_types"], desc="UI Icons"):
        # Create a simple icon as a placeholder
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Use different colors for different icon types
        colors = {
            "health": (200, 60, 60),
            "mana": (60, 100, 200),
            "stamina": (60, 180, 60),
            "attack": (200, 100, 50),
            "defense": (80, 80, 180),
            "speed": (180, 180, 50)
        }
        
        # Draw a simple icon shape
        color = colors.get(icon_type, (150, 150, 150))
        draw.ellipse([(2, 2), (30, 30)], fill=color)
        
        # Save the placeholder
        filename = os.path.join(icons_dir, f"icon_{icon_type}.png")
        img.save(filename, "PNG")
    
    print(f"Generated placeholders for UI elements")

def generate_all_assets(seed=None):
    """Generate all game assets"""
    print(f"Generating all assets with seed: {seed if seed is not None else 'random'}")
    
    # Setup directories
    base_dir = setup_output_directories()
    
    # Generate assets
    generate_character_assets(base_dir, seed)
    generate_terrain_assets(base_dir, seed)
    generate_prop_assets(base_dir, seed)
    generate_building_assets(base_dir, seed)
    generate_ui_assets(base_dir, seed)
    
    print("Asset generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate game assets for Nightfall Defenders')
    parser.add_argument('--seed', type=int, help='Random seed for deterministic generation')
    args = parser.parse_args()
    
    generate_all_assets(args.seed) 