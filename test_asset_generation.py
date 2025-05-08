#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour la génération d'assets de Nightfall Defenders
Ce script permet de tester les différentes fonctionnalités du système de génération d'assets
"""

import os
import sys
import time
import json
import argparse
import random
from PIL import Image, ImageDraw

def main():
    """Point d'entrée principal pour le test de génération d'assets"""
    parser = argparse.ArgumentParser(description="Test du système de génération d'assets")
    parser.add_argument("--mode", choices=["2d", "3d", "hybrid"], help="Mode de test", default="hybrid")
    parser.add_argument("--output", type=str, help="Répertoire de sortie", default="test_assets")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Test du système de génération d'assets de Nightfall Defenders")
    print("=" * 60)
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(args.output, exist_ok=True)
    
    # Générer des assets de test
    if args.mode == "2d" or args.mode == "hybrid":
        test_2d_generation(args.output)
    
    if args.mode == "3d" or args.mode == "hybrid":
        test_3d_generation(args.output)
    
    print("\nTest terminé. Les assets générés ont été sauvegardés dans", args.output)
    
    return 0

def test_2d_generation(output_dir):
    """Teste la génération d'assets 2D"""
    print("\nTest de génération d'assets 2D...")
    
    # Créer un sous-répertoire pour les assets 2D
    output_dir_2d = os.path.join(output_dir, "2d")
    os.makedirs(output_dir_2d, exist_ok=True)
    
    # Générer des sprites de personnages simples
    print("Génération de sprites de personnages...")
    character_dir = os.path.join(output_dir_2d, "characters")
    os.makedirs(character_dir, exist_ok=True)
    
    character_classes = ["warrior", "mage", "cleric", "ranger", "alchemist", "summoner"]
    for class_type in character_classes:
        print(f"- Génération de la classe {class_type}")
        sprite = generate_character_sprite(class_type)
        sprite.save(os.path.join(character_dir, f"{class_type}.png"))
    
    # Générer des tiles de terrain
    print("Génération de tiles de terrain...")
    terrain_dir = os.path.join(output_dir_2d, "terrain")
    os.makedirs(terrain_dir, exist_ok=True)
    
    terrain_types = ["grass", "desert", "forest", "water", "mountain", "snow"]
    for terrain_type in terrain_types:
        print(f"- Génération du terrain {terrain_type}")
        terrain_type_dir = os.path.join(terrain_dir, terrain_type)
        os.makedirs(terrain_type_dir, exist_ok=True)
        for i in range(3):  # Générer 3 variations
            sprite = generate_terrain_tile(terrain_type, i)
            sprite.save(os.path.join(terrain_type_dir, f"{terrain_type}_{i+1}.png"))
    
    # Générer des éléments d'UI
    print("Génération d'éléments d'UI...")
    ui_dir = os.path.join(output_dir_2d, "ui")
    os.makedirs(ui_dir, exist_ok=True)
    
    # Générer des boutons
    button_states = ["normal", "hover", "pressed", "disabled"]
    for state in button_states:
        print(f"- Génération de bouton en état {state}")
        sprite = generate_button(state)
        sprite.save(os.path.join(ui_dir, f"button_{state}.png"))

def generate_character_sprite(class_type):
    """
    Génère un sprite de personnage simple
    
    Args:
        class_type (str): Type de classe de personnage
        
    Returns:
        PIL.Image: Le sprite généré
    """
    # Créer une image vide avec fond transparent
    size = (64, 64)
    sprite = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    
    # Déterminer la couleur principale selon la classe
    colors = {
        "warrior": (180, 30, 30, 255),      # Rouge
        "mage": (30, 30, 180, 255),         # Bleu
        "cleric": (180, 180, 30, 255),      # Jaune
        "ranger": (30, 180, 30, 255),       # Vert
        "alchemist": (180, 30, 180, 255),   # Violet
        "summoner": (30, 180, 180, 255)     # Turquoise
    }
    main_color = colors.get(class_type, (100, 100, 100, 255))
    
    # Dessiner le corps du personnage
    width, height = size
    
    # Tête
    head_radius = int(width * 0.15)
    head_center = (width // 2, int(height * 0.25))
    draw.ellipse((
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius
    ), fill=(255, 220, 180, 255))
    
    # Corps
    if class_type in ["mage", "summoner"]:
        # Robe (triangle)
        robe_width = int(width * 0.4)
        robe_height = int(height * 0.6)
        robe_left = (width - robe_width) // 2
        robe_top = head_center[1] + head_radius - 5
        
        points = [
            (robe_left, robe_top),
            (robe_left + robe_width, robe_top),
            (robe_left + robe_width + 5, robe_top + robe_height),
            (robe_left - 5, robe_top + robe_height)
        ]
        draw.polygon(points, fill=main_color)
    else:
        # Corps (rectangle)
        body_width = int(width * 0.3)
        body_height = int(height * 0.4)
        body_left = (width - body_width) // 2
        body_top = head_center[1] + head_radius - 5
        draw.rectangle((
            body_left,
            body_top,
            body_left + body_width,
            body_top + body_height
        ), fill=main_color)
        
        # Jambes
        leg_width = int(body_width * 0.4)
        leg_height = int(height * 0.25)
        # Jambe gauche
        draw.rectangle((
            body_left,
            body_top + body_height,
            body_left + leg_width,
            body_top + body_height + leg_height
        ), fill=(50, 50, 50, 255))
        # Jambe droite
        draw.rectangle((
            body_left + body_width - leg_width,
            body_top + body_height,
            body_left + body_width,
            body_top + body_height + leg_height
        ), fill=(50, 50, 50, 255))
    
    return sprite

def generate_terrain_tile(terrain_type, variation):
    """
    Génère un tile de terrain simple
    
    Args:
        terrain_type (str): Type de terrain
        variation (int): Numéro de variation
        
    Returns:
        PIL.Image: Le tile généré
    """
    # Taille standard pour les tiles de terrain
    size = (128, 128)
    sprite = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    
    # Couleurs de base selon le type de terrain
    colors = {
        "grass": (30, 180, 30, 255),         # Vert
        "desert": (220, 180, 60, 255),       # Jaune sable
        "forest": (20, 120, 20, 255),        # Vert foncé
        "water": (30, 100, 200, 255),        # Bleu
        "mountain": (120, 120, 120, 255),    # Gris
        "snow": (230, 230, 240, 255)         # Blanc cassé
    }
    main_color = colors.get(terrain_type, (100, 100, 100, 255))
    
    # Modifier légèrement la couleur en fonction de la variation
    r, g, b, a = main_color
    variation_offset = 20
    r = max(0, min(255, r + random.randint(-variation_offset, variation_offset)))
    g = max(0, min(255, g + random.randint(-variation_offset, variation_offset)))
    b = max(0, min(255, b + random.randint(-variation_offset, variation_offset)))
    varied_color = (r, g, b, a)
    
    # Remplir le fond avec la couleur de base
    draw.rectangle((0, 0, size[0], size[1]), fill=varied_color)
    
    # Ajouter des détails spécifiques selon le type de terrain
    if terrain_type == "grass":
        # Ajouter quelques détails d'herbe
        for _ in range(30):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            length = random.randint(5, 15)
            draw.line((x, y, x, y - length), fill=(10, 160, 10, 200), width=2)
    
    elif terrain_type == "desert":
        # Ajouter quelques grains de sable
        for _ in range(50):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            radius = random.randint(1, 3)
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), 
                         fill=(240, 220, 180, 200))
    
    elif terrain_type == "water":
        # Ajouter quelques vagues
        for _ in range(10):
            x1 = random.randint(0, size[0])
            y1 = random.randint(0, size[1])
            x2 = x1 + random.randint(20, 40)
            y2 = y1 + random.randint(-5, 5)
            draw.line((x1, y1, x2, y2), fill=(200, 220, 255, 180), width=2)
    
    return sprite

def generate_button(state):
    """
    Génère un bouton d'interface
    
    Args:
        state (str): État du bouton (normal, hover, pressed, disabled)
        
    Returns:
        PIL.Image: Le bouton généré
    """
    # Taille standard pour les boutons
    size = (120, 40)
    button = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(button)
    
    # Couleur de base selon l'état
    if state == "normal":
        color = (80, 80, 100, 255)
    elif state == "hover":
        color = (100, 100, 120, 255)
    elif state == "pressed":
        color = (60, 60, 80, 255)
    elif state == "disabled":
        color = (60, 60, 60, 180)
    else:
        color = (80, 80, 100, 255)
    
    # Fond du bouton
    draw.rectangle((0, 0, size[0], size[1]), fill=color)
    
    # Bordure
    border_color = tuple(min(c + 50, 255) for c in color[:3]) + (color[3],)
    draw.rectangle((0, 0, size[0], size[1]), outline=border_color, width=2)
    
    # Effet de lumière
    if state != "pressed":
        highlight_points = [(0, 0), (size[0], 0), (size[0], size[1]//4), (0, size[1]//4)]
        highlight_color = tuple(min(c + 30, 255) for c in color[:3]) + (100,)
        draw.polygon(highlight_points, fill=highlight_color)
    
    return button

def test_3d_generation(output_dir):
    """Teste la génération d'assets 3D"""
    print("\nTest de génération d'assets 3D...")
    
    # Créer un sous-répertoire pour les assets 3D
    output_dir_3d = os.path.join(output_dir, "3d")
    os.makedirs(output_dir_3d, exist_ok=True)
    
    # Pour ce test, nous allons simplement créer des fichiers de métadonnées
    # qui décrivent les modèles 3D que nous aurions générés
    
    # Modèles de bâtiments
    print("Génération de métadonnées pour modèles de bâtiments...")
    building_dir = os.path.join(output_dir_3d, "buildings")
    os.makedirs(building_dir, exist_ok=True)
    
    building_types = ["house", "shop", "temple", "tower"]
    for building_type in building_types:
        building_type_dir = os.path.join(building_dir, building_type)
        os.makedirs(building_type_dir, exist_ok=True)
        
        print(f"- Génération de métadonnées pour {building_type}")
        for i in range(2):  # Générer 2 variations
            metadata = generate_building_metadata(building_type)
            
            with open(os.path.join(building_type_dir, f"{building_type}_{i+1}_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
    
    # Modèles de props
    print("Génération de métadonnées pour modèles de props...")
    prop_dir = os.path.join(output_dir_3d, "props")
    os.makedirs(prop_dir, exist_ok=True)
    
    prop_types = ["tree", "rock", "chest", "sign"]
    for prop_type in prop_types:
        prop_type_dir = os.path.join(prop_dir, prop_type)
        os.makedirs(prop_type_dir, exist_ok=True)
        
        print(f"- Génération de métadonnées pour {prop_type}")
        for i in range(2):  # Générer 2 variations
            metadata = generate_prop_metadata(prop_type)
            
            with open(os.path.join(prop_type_dir, f"{prop_type}_{i+1}_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)

def generate_building_metadata(building_type):
    """
    Génère des métadonnées pour un modèle de bâtiment
    
    Args:
        building_type (str): Type de bâtiment
        
    Returns:
        dict: Métadonnées du modèle
    """
    # Paramètres de base pour les bâtiments
    base_params = {
        "house": {
            "width": random.uniform(5.0, 10.0),
            "depth": random.uniform(5.0, 10.0),
            "height": random.uniform(3.0, 5.0),
            "roof_style": random.choice(["flat", "peaked", "dome"]),
            "material": random.choice(["wood", "stone", "brick"])
        },
        "shop": {
            "width": random.uniform(6.0, 12.0),
            "depth": random.uniform(6.0, 12.0),
            "height": random.uniform(3.0, 5.0),
            "storefront": True,
            "sign": True,
            "material": random.choice(["wood", "stone", "brick"])
        },
        "temple": {
            "width": random.uniform(8.0, 15.0),
            "depth": random.uniform(12.0, 20.0),
            "height": random.uniform(6.0, 10.0),
            "style": random.choice(["classical", "ornate", "simple"]),
            "columns": random.randint(4, 8),
            "material": "stone"
        },
        "tower": {
            "width": random.uniform(3.0, 5.0),
            "depth": random.uniform(3.0, 5.0),
            "height": random.uniform(10.0, 20.0),
            "shape": random.choice(["round", "square", "octagonal"]),
            "material": random.choice(["stone", "brick"])
        }
    }
    
    # Utiliser les paramètres de base pour le type de bâtiment
    params = base_params.get(building_type, {})
    
    # Générer des métadonnées communes à tous les bâtiments
    metadata = {
        "model_type": "building",
        "building_type": building_type,
        "procedural_params": params,
        "generated_at": time.time(),
        "format": "bam",  # Format pour Panda3D
        "vertices": random.randint(500, 5000),
        "triangles": random.randint(300, 3000),
        "has_collision": True,
        "has_textures": True,
        "texture_resolution": "1024x1024"
    }
    
    return metadata

def generate_prop_metadata(prop_type):
    """
    Génère des métadonnées pour un modèle de prop
    
    Args:
        prop_type (str): Type de prop
        
    Returns:
        dict: Métadonnées du modèle
    """
    # Paramètres de base pour les props
    base_params = {
        "tree": {
            "height": random.uniform(5.0, 12.0),
            "trunk_radius": random.uniform(0.3, 0.8),
            "canopy_radius": random.uniform(2.0, 5.0),
            "species": random.choice(["oak", "pine", "palm", "willow"]),
            "leaf_density": random.uniform(0.5, 1.0)
        },
        "rock": {
            "size": random.uniform(0.5, 2.5),
            "roughness": random.uniform(0.2, 0.8),
            "shape": random.choice(["rounded", "angular", "flat"]),
            "moss_coverage": random.uniform(0.0, 0.5)
        },
        "chest": {
            "width": random.uniform(1.0, 1.5),
            "depth": random.uniform(0.8, 1.2),
            "height": random.uniform(0.8, 1.0),
            "material": random.choice(["wood", "metal", "ornate"]),
            "has_lock": random.choice([True, False])
        },
        "sign": {
            "height": random.uniform(1.2, 2.0),
            "width": random.uniform(0.8, 1.5),
            "style": random.choice(["post", "hanging", "wall"]),
            "material": "wood",
            "has_text": True
        }
    }
    
    # Utiliser les paramètres de base pour le type de prop
    params = base_params.get(prop_type, {})
    
    # Générer des métadonnées communes à tous les props
    metadata = {
        "model_type": "prop",
        "prop_type": prop_type,
        "procedural_params": params,
        "generated_at": time.time(),
        "format": "bam",  # Format pour Panda3D
        "vertices": random.randint(100, 2000),
        "triangles": random.randint(50, 1000),
        "has_collision": True,
        "has_textures": True,
        "texture_resolution": "512x512"
    }
    
    return metadata

if __name__ == "__main__":
    sys.exit(main()) 