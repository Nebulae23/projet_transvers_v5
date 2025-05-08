#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Asset Generation Script
Generates all required assets for the game
"""

import os
import sys
import argparse
import time
import subprocess

def main():
    """Main asset generation entry point"""
    parser = argparse.ArgumentParser(description="Nightfall Defenders Asset Generator")
    parser.add_argument("--seed", type=int, help="Random seed for asset generation", default=42)
    args = parser.parse_args()
    
    print("=" * 60)
    print("Nightfall Defenders - Asset Generation")
    print("=" * 60)
    
    # Record start time
    start_time = time.time()
    
    # Create asset directories if they don't exist
    asset_dir = os.path.join("src", "assets")
    generated_dir = os.path.join(asset_dir, "generated")
    os.makedirs(asset_dir, exist_ok=True)
    os.makedirs(generated_dir, exist_ok=True)
    
    print(f"Using random seed: {args.seed}")
    
    # Run each asset generator directly
    try:
        print("Setting up output directories...")
        character_dir = os.path.join(generated_dir, "characters")
        environment_dir = os.path.join(generated_dir, "environment")
        props_dir = os.path.join(generated_dir, "props")
        buildings_dir = os.path.join(generated_dir, "buildings")
        ui_dir = os.path.join(generated_dir, "ui")
        
        os.makedirs(character_dir, exist_ok=True)
        os.makedirs(environment_dir, exist_ok=True)
        os.makedirs(props_dir, exist_ok=True)
        os.makedirs(buildings_dir, exist_ok=True)
        os.makedirs(ui_dir, exist_ok=True)
        
        # Generate character sprites
        print("Generating character sprites...")
        sprite_generator_path = os.path.join("src", "tools", "asset_generator", "sprite_generator.py")
        subprocess.run([sys.executable, sprite_generator_path], check=True)
        
        # Generate terrain tiles
        print("Generating terrain tiles...")
        terrain_generator_path = os.path.join("src", "tools", "asset_generator", "terrain_generator.py")
        subprocess.run([sys.executable, terrain_generator_path], check=True)
        
        # Record end time and calculate duration
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Asset generation complete in {duration:.2f} seconds!")
        print("You can now run the game with: python run_game.py")
        
        return 0
    
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Asset generation failed: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Asset generation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 