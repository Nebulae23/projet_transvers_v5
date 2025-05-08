#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI Asset Generator for Nightfall Defenders
Generates UI assets for the game, focusing on skill tree visualization elements
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import math

def ensure_dir(directory):
    """Ensure that a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_default_node_icon(output_path, size=128, color=(80, 80, 100), border_color=(150, 150, 170)):
    """Create a default node icon"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw filled circle
    padding = int(size * 0.1)
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=color,
        outline=border_color,
        width=int(size * 0.05)
    )
    
    # Save the image
    img.save(output_path)
    print(f"Created default node icon: {output_path}")

def create_question_mark_icon(output_path, size=128, bg_color=(60, 60, 80), text_color=(200, 200, 220)):
    """Create a question mark icon for unknown nodes"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw filled circle
    padding = int(size * 0.1)
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=bg_color,
        outline=(100, 100, 120),
        width=int(size * 0.05)
    )
    
    # Add question mark
    try:
        # Try to load a font
        font = ImageFont.truetype("arial.ttf", int(size * 0.6))
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text size to center it
    text = "?"
    try:
        text_width = draw.textlength(text, font=font)
    except AttributeError:
        # Fallback for older PIL versions
        text_width = font.getsize(text)[0]
    text_height = int(size * 0.6)  # Approximate height
    
    # Draw text centered
    draw.text(
        (size // 2 - text_width // 2, size // 2 - text_height // 2 - int(size * 0.05)),
        text,
        fill=text_color,
        font=font
    )
    
    # Save the image
    img.save(output_path)
    print(f"Created question mark icon: {output_path}")

def create_locked_icon(output_path, size=128, color=(100, 100, 100, 180)):
    """Create a lock overlay for locked nodes"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw lock body
    lock_width = int(size * 0.5)
    lock_height = int(size * 0.4)
    lock_x = (size - lock_width) // 2
    lock_y = (size - lock_height) // 2 + int(size * 0.05)
    
    # Draw rectangle for lock body (no rounded corners)
    draw.rectangle(
        [lock_x, lock_y, lock_x + lock_width, lock_y + lock_height],
        fill=color
    )
    
    # Draw lock shackle
    shackle_width = int(lock_width * 0.6)
    shackle_height = int(size * 0.3)
    shackle_x = (size - shackle_width) // 2
    shackle_y = lock_y - shackle_height
    
    # Draw shackle as a U shape
    draw.line(
        [
            shackle_x, lock_y,
            shackle_x, shackle_y,
            shackle_x + shackle_width, shackle_y,
            shackle_x + shackle_width, lock_y
        ],
        fill=color,
        width=int(size * 0.08)
    )
    
    # Save the image
    img.save(output_path)
    print(f"Created locked icon: {output_path}")

def create_fusion_overlay(output_path, size=128, color1=(180, 120, 255, 200), color2=(120, 80, 220, 200)):
    """Create a fusion node overlay with a spiral pattern"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a spiral pattern
    center_x, center_y = size // 2, size // 2
    max_radius = size // 2 - int(size * 0.15)
    
    # Create a spiral effect
    num_points = 60
    for i in range(num_points):
        angle = (i / num_points) * math.pi * 8  # 4 rotations
        radius = max_radius * (i / num_points)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        # Alternate colors
        color = color1 if i % 2 == 0 else color2
        
        # Draw point as a small circle
        point_size = int(size * 0.06) - int((i / num_points) * size * 0.04)
        draw.ellipse(
            [x - point_size, y - point_size, x + point_size, y + point_size],
            fill=color
        )
    
    # Save the image
    img.save(output_path)
    print(f"Created fusion overlay: {output_path}")

def main():
    """Main function to generate all UI assets"""
    # Define output directory
    output_dir = os.path.join("src", "assets", "generated", "ui")
    ensure_dir(output_dir)
    
    # Generate skill tree assets
    create_default_node_icon(os.path.join(output_dir, "default_node.png"))
    create_question_mark_icon(os.path.join(output_dir, "question_mark.png"))
    create_locked_icon(os.path.join(output_dir, "locked.png"))
    create_fusion_overlay(os.path.join(output_dir, "fusion_overlay.png"))
    
    print("UI asset generation complete!")

if __name__ == "__main__":
    main() 