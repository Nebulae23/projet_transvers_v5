#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI Generator for Nightfall Defenders
Generates UI elements and backgrounds for the game
"""

import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import math

class UIGenerator:
    """Generator for UI elements like backgrounds, buttons, panels"""
    
    def __init__(self, output_dir):
        """
        Initialize the UI generator
        
        Args:
            output_dir (str): Directory to save generated UI elements
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set default sizes
        self.main_menu_bg_size = (1920, 1080)
        
        # UI color palettes
        self.color_schemes = {
            "dark_fantasy": {
                "primary": (30, 30, 60),
                "secondary": (60, 40, 80),
                "accent": (120, 80, 160),
                "highlight": (200, 160, 240)
            },
            "magical": {
                "primary": (20, 40, 80),
                "secondary": (40, 60, 100),
                "accent": (80, 120, 180),
                "highlight": (160, 200, 240)
            },
            "twilight": {
                "primary": (40, 30, 70),
                "secondary": (70, 50, 90),
                "accent": (110, 70, 130),
                "highlight": (180, 140, 200)
            }
        }
    
    def generate_with_cache(self, asset_id, params=None, seed=None):
        """
        Generate a UI asset with caching support
        
        Args:
            asset_id (str): Identifier for the asset
            params (dict): Parameters for generation
            seed (int): Random seed for generation
            
        Returns:
            PIL.Image: The generated UI element
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        if params is None:
            params = {}
            
        # Determine what UI element to generate based on asset_id
        if asset_id == "main_menu_bg" or asset_id.startswith("main_menu_bg"):
            return self.generate_main_menu_background(params)
        elif asset_id.startswith("button_"):
            return self.generate_button(asset_id.split("_")[1], params)
        elif asset_id.startswith("panel_"):
            return self.generate_panel(asset_id.split("_")[1], params)
        else:
            return self.generate_default_ui_element(asset_id, params)
    
    def generate_main_menu_background(self, params=None):
        """
        Generate a background for the main menu
        
        Args:
            params (dict): Generation parameters
            
        Returns:
            PIL.Image: The generated background image
        """
        if params is None:
            params = {}
            
        # Get parameters or use defaults
        width = params.get("width", self.main_menu_bg_size[0])
        height = params.get("height", self.main_menu_bg_size[1])
        style = params.get("style", "magical")
        
        # Get color scheme
        color_scheme = self.color_schemes.get(style, self.color_schemes["magical"])
        
        # Create base image with gradient background
        img = Image.new('RGBA', (width, height), color_scheme["primary"])
        draw = ImageDraw.Draw(img)
        
        # Add gradient from top to bottom
        for y in range(height):
            # Calculate gradient color
            alpha = y / height
            r = int(color_scheme["primary"][0] * (1 - alpha) + color_scheme["secondary"][0] * alpha)
            g = int(color_scheme["primary"][1] * (1 - alpha) + color_scheme["secondary"][1] * alpha)
            b = int(color_scheme["primary"][2] * (1 - alpha) + color_scheme["secondary"][2] * alpha)
            
            # Draw horizontal line with this color
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add some mystical "light rays" from top
        for i in range(10):
            x_center = random.randint(width // 4, width * 3 // 4)
            ray_width = random.randint(50, 200)
            ray_color = color_scheme["highlight"] + (100,)  # semi-transparent
            
            # Draw a triangular ray
            points = [
                (x_center, 0),
                (x_center - ray_width, height),
                (x_center + ray_width, height)
            ]
            draw.polygon(points, fill=ray_color)
        
        # Add some stars/particles
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            color = (brightness, brightness, brightness, random.randint(50, 150))
            
            draw.ellipse([(x, y), (x + size, y + size)], fill=color)
        
        # Add subtle noise texture
        noise_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        noise_draw = ImageDraw.Draw(noise_img)
        
        for x in range(0, width, 2):
            for y in range(0, height, 2):
                if random.random() > 0.8:
                    noise_value = random.randint(0, 30)
                    noise_draw.point((x, y), fill=(noise_value, noise_value, noise_value, 50))
        
        img = Image.alpha_composite(img, noise_img)
        
        # Apply blur to soften the effect
        img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        return img
    
    def generate_button(self, state, params=None):
        """Generate a button UI element"""
        if params is None:
            params = {}
            
        width = params.get("width", 200)
        height = params.get("height", 60)
        style = params.get("style", "magical")
        
        # Get color scheme
        color_scheme = self.color_schemes.get(style, self.color_schemes["magical"])
        
        # Create button based on state
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if state == "normal":
            draw.rectangle([(0, 0), (width, height)], fill=color_scheme["secondary"], outline=color_scheme["accent"], width=2)
        elif state == "hover":
            draw.rectangle([(0, 0), (width, height)], fill=color_scheme["accent"], outline=color_scheme["highlight"], width=2)
        elif state == "pressed":
            draw.rectangle([(0, 0), (width, height)], fill=color_scheme["primary"], outline=color_scheme["accent"], width=2)
        elif state == "disabled":
            draw.rectangle([(0, 0), (width, height)], fill=(100, 100, 100, 150), outline=(150, 150, 150), width=2)
        
        return img
    
    def generate_panel(self, panel_type, params=None):
        """Generate a UI panel"""
        if params is None:
            params = {}
            
        width = params.get("width", 400)
        height = params.get("height", 300)
        style = params.get("style", "magical")
        
        # Get color scheme
        color_scheme = self.color_schemes.get(style, self.color_schemes["magical"])
        
        # Create base panel
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw panel background with border
        draw.rectangle([(0, 0), (width, height)], fill=color_scheme["primary"], outline=color_scheme["accent"], width=3)
        
        # Add header based on panel type
        header_height = height // 8
        draw.rectangle([(0, 0), (width, header_height)], fill=color_scheme["accent"])
        
        return img
    
    def generate_default_ui_element(self, element_id, params=None):
        """Generate a default UI element when specific type is not recognized"""
        if params is None:
            params = {}
            
        width = params.get("width", 100)
        height = params.get("height", 100)
        
        # Create a simple placeholder image
        img = Image.new('RGBA', (width, height), (150, 150, 150, 200))
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([(0, 0), (width-1, height-1)], outline=(100, 100, 100), width=2)
        
        # Add cross pattern to show it's a placeholder
        draw.line([(0, 0), (width, height)], fill=(100, 100, 100), width=2)
        draw.line([(0, height), (width, 0)], fill=(100, 100, 100), width=2)
        
        return img
    
    def save_asset(self, asset, output_path):
        """
        Save the generated asset to disk
        
        Args:
            asset (PIL.Image): The asset to save
            output_path (str): Path to save the asset to
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            asset.save(output_path)
            print(f"Saved UI asset to {output_path}")
        except Exception as e:
            print(f"Error saving UI asset: {e}")
    
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

def main():
    """Main entry point for testing"""
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"
    
    generator = UIGenerator(output_dir)
    
    # Generate and save main menu background
    main_menu_bg = generator.generate_main_menu_background()
    main_menu_bg.save(os.path.join(output_dir, "main_menu_bg.png"))
    
    print("UI generation complete!")

if __name__ == "__main__":
    main() 