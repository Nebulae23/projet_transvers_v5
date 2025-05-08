#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sprite Generator for Nightfall Defenders
Generates procedural 2D sprites for characters and UI elements
"""

import os
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Import base generator classes
from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

class SpriteType:
    """Types de sprites que le générateur peut produire"""
    CHARACTER = "character"
    ITEM = "item"
    UI_ELEMENT = "ui_element"

class CharacterClass:
    """Classes de personnages disponibles"""
    WARRIOR = "warrior"
    MAGE = "mage"
    RANGER = "ranger"
    CLERIC = "cleric"
    ALCHEMIST = "alchemist"
    SUMMONER = "summoner"

class SpriteGenerator(AssetGenerator):
    """Générateur de sprites 2D procéduraux"""
    
    def __init__(self, output_dir):
        """
        Initialise le générateur de sprites
        
        Args:
            output_dir (str): Répertoire de sortie pour les sprites générés
        """
        super().__init__(output_dir)
        
        # Paramètres de base pour la génération
        self.base_sprite_size = (64, 64)  # Taille par défaut des sprites
    
    def generate(self, asset_id, asset_params, seed=None):
        """
        Génère un sprite 2D selon les paramètres spécifiés
        
        Args:
            asset_id (str): Identifiant unique pour le sprite
            asset_params (dict): Paramètres de génération du sprite
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            PIL.Image: Le sprite généré
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Extraire les paramètres communs
        sprite_type = asset_params.get("sprite_type", SpriteType.CHARACTER)
        size = asset_params.get("size", self.base_sprite_size)
        
        # Générer selon le type de sprite
        if sprite_type == SpriteType.CHARACTER:
            return self._generate_character(asset_id, asset_params, size)
        elif sprite_type == SpriteType.ITEM:
            return self._generate_item(asset_id, asset_params, size)
        elif sprite_type == SpriteType.UI_ELEMENT:
            return self._generate_ui_element(asset_id, asset_params, size)
        else:
            # Type inconnu, générer un sprite par défaut
            return self._generate_default_sprite(asset_id, size)
    
    def _generate_character(self, asset_id, params, size):
        """
        Génère un sprite de personnage
        
        Args:
            asset_id (str): Identifiant du sprite
            params (dict): Paramètres pour la génération
            size (tuple): Dimensions du sprite (largeur, hauteur)
            
        Returns:
            PIL.Image: Sprite de personnage
        """
        # Extraire les paramètres spécifiques
        class_type = params.get("class_type", CharacterClass.WARRIOR)
        
        # Créer une image vide avec transparence
        sprite = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        
        # Générer selon la classe de personnage
        if class_type == CharacterClass.WARRIOR:
            self._generate_warrior(sprite, draw, params)
        elif class_type == CharacterClass.MAGE:
            self._generate_mage(sprite, draw, params)
        else:
            # Classe inconnue, générer un personnage générique
            self._generate_generic_character(sprite, draw, params)
        
        # Appliquer un léger flou pour adoucir les contours
        sprite = sprite.filter(ImageFilter.SMOOTH)
        return sprite
    
    def _generate_item(self, asset_id, params, size):
        """Génère un sprite d'objet"""
        sprite = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        
        # À implémenter
        self._draw_generic_item(draw, size)
        
        return sprite
    
    def _generate_ui_element(self, asset_id, params, size):
        """Génère un élément d'interface utilisateur"""
        sprite = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        
        # À implémenter
        self._draw_generic_ui_element(draw, size)
        
        return sprite
    
    def _generate_default_sprite(self, asset_id, size):
        """Génère un sprite par défaut (placeholder)"""
        sprite = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        
        # Dessiner une forme simple pour indiquer un placeholder
        draw.rectangle([10, 10, size[0]-10, size[1]-10], outline=(255, 0, 0, 255), width=2)
        draw.line([10, 10, size[0]-10, size[1]-10], fill=(255, 0, 0, 255), width=2)
        draw.line([10, size[1]-10, size[0]-10, 10], fill=(255, 0, 0, 255), width=2)
        
        return sprite
    
    # Méthodes de génération spécifiques aux classes de personnages
    
    def _generate_warrior(self, sprite, draw, params):
        """Génère un sprite de guerrier"""
        width, height = sprite.size
        
        # Couleurs pour le guerrier
        main_color = (180, 30, 30, 255)  # Rouge pour le guerrier
        
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
    
    def _generate_mage(self, sprite, draw, params):
        """Génère un sprite de mage"""
        width, height = sprite.size
        
        # Couleurs pour le mage
        main_color = (50, 50, 180, 255)  # Bleu pour le mage
        
        # Tête
        head_radius = int(width * 0.15)
        head_center = (width // 2, int(height * 0.25))
        draw.ellipse((
            head_center[0] - head_radius,
            head_center[1] - head_radius,
            head_center[0] + head_radius,
            head_center[1] + head_radius
        ), fill=(255, 220, 180, 255))
        
        # Corps/Robe
        robe_width = int(width * 0.5)
        robe_height = int(height * 0.6)
        robe_left = (width - robe_width) // 2
        robe_top = head_center[1] + head_radius - 5
        
        # Dessiner une robe évasée vers le bas
        points = [
            (robe_left, robe_top),
            (robe_left + robe_width, robe_top),
            (robe_left + robe_width + 10, robe_top + robe_height),
            (robe_left - 10, robe_top + robe_height)
        ]
        draw.polygon(points, fill=main_color)
    
    def _generate_generic_character(self, sprite, draw, params):
        """Génère un personnage générique"""
        width, height = sprite.size
        
        # Couleur aléatoire
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        main_color = (r, g, b, 255)
        
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
        draw.rectangle((
            body_left,
            body_top + body_height,
            body_left + leg_width,
            body_top + body_height + leg_height
        ), fill=(50, 50, 100, 255))
        draw.rectangle((
            body_left + body_width - leg_width,
            body_top + body_height,
            body_left + body_width,
            body_top + body_height + leg_height
        ), fill=(50, 50, 100, 255))
    
    # Méthodes auxiliaires pour dessiner des éléments
    
    def _draw_generic_ui_element(self, draw, size):
        """Dessine un élément d'UI générique"""
        width, height = size
        
        # Fond du bouton
        draw.rectangle((0, 0, width, height), fill=(80, 80, 100, 200))
        
        # Bordure
        draw.rectangle((0, 0, width, height), outline=(200, 200, 200, 255), width=2)
    
    def _draw_generic_item(self, draw, size):
        """Dessine un item générique"""
        width, height = size
        
        # Simple rectangle avec un contour
        margin = width // 4
        draw.rectangle((
            margin, margin,
            width - margin, height - margin
        ), fill=(100, 100, 100, 200), outline=(200, 200, 200, 255), width=2)
    
    # Méthode de sauvegarde spécifique pour les sprites
    
    def save_asset(self, asset, filepath, **kwargs):
        """
        Sauvegarde un sprite dans un fichier
        
        Args:
            asset (PIL.Image): Le sprite à sauvegarder
            filepath (str): Chemin où sauvegarder le sprite
            **kwargs: Paramètres supplémentaires pour la sauvegarde
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        try:
            # Créer le répertoire parent s'il n'existe pas
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder l'image
            asset.save(filepath)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du sprite: {e}")
            self.generation_stats["errors"] += 1
            return False


def main():
    """Generate and save example sprites"""
    output_dir = os.path.join("src", "assets", "generated", "characters")
    generator = SpriteGenerator(output_dir)
    
    # Generate one of each class with a consistent seed
    sprites = generator.generate_all_classes(seed=42)
    
    for class_name, sprite in sprites.items():
        filename = f"{class_name}_character.png"
        generator.save_sprite(sprite, filename)
        print(f"Generated sprite for {class_name} class")


if __name__ == "__main__":
    main() 