#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Effect Generator for Nightfall Defenders
Generates procedural visual effects in Octopath Traveler style
"""

import os
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
from enum import Enum

from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

class EffectType(Enum):
    """Types d'effets que le générateur peut produire"""
    FIRE = "fire"
    WATER = "water"
    MAGIC = "magic"
    SMOKE = "smoke"
    EXPLOSION = "explosion"
    ELECTRICITY = "electricity"
    AURA = "aura"

class EffectGenerator(AssetGenerator):
    """Générateur d'effets visuels avec style Octopath Traveler"""
    
    def __init__(self, output_dir):
        """
        Initialise le générateur d'effets
        
        Args:
            output_dir (str): Répertoire de sortie pour les effets générés
        """
        super().__init__(output_dir)
        
        # Créer des sous-répertoires pour chaque type d'effet
        self.effect_dirs = {effect_type: os.path.join(output_dir, effect_type.value) 
                           for effect_type in EffectType}
        
        for directory in self.effect_dirs.values():
            os.makedirs(directory, exist_ok=True)
            
        # Paramètres de base pour la génération
        self.base_effect_size = (128, 128)
        self.frame_count = 8  # Nombre d'images pour l'animation par défaut
        
        # Palettes de couleurs pour les différents effets
        self.effect_palettes = {
            EffectType.FIRE: [
                (255, 230, 160), (255, 200, 120), (255, 160, 80), 
                (230, 120, 60), (200, 80, 20), (150, 40, 10)
            ],
            EffectType.WATER: [
                (180, 230, 250), (140, 200, 240), (100, 180, 230), 
                (80, 160, 210), (60, 140, 200), (40, 120, 180)
            ],
            EffectType.MAGIC: [
                (220, 180, 255), (200, 150, 240), (180, 120, 220), 
                (160, 90, 200), (140, 60, 180), (120, 30, 160)
            ],
            EffectType.SMOKE: [
                (240, 240, 240), (220, 220, 220), (200, 200, 200), 
                (180, 180, 180), (160, 160, 160), (140, 140, 140)
            ],
            EffectType.EXPLOSION: [
                (255, 230, 150), (255, 200, 100), (255, 150, 50), 
                (230, 100, 30), (200, 50, 10), (150, 20, 5)
            ],
            EffectType.ELECTRICITY: [
                (220, 240, 255), (180, 210, 255), (140, 180, 255), 
                (100, 150, 255), (70, 120, 240), (40, 90, 220)
            ],
            EffectType.AURA: [
                (200, 255, 200), (160, 240, 180), (120, 220, 160), 
                (80, 200, 140), (40, 180, 120), (20, 160, 100)
            ]
        }
    
    def generate(self, asset_id, asset_params, seed=None):
        """
        Génère un effet visuel selon les paramètres spécifiés
        
        Args:
            asset_id (str): Identifiant unique pour l'effet
            asset_params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            list: Liste des images (frames) de l'effet
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Extraire les paramètres
        effect_type_str = asset_params.get("effect_type", "fire")
        effect_type = next((et for et in EffectType if et.value == effect_type_str), EffectType.FIRE)
        
        size = asset_params.get("size", self.base_effect_size)
        frame_count = asset_params.get("frame_count", self.frame_count)
        intensity = asset_params.get("intensity", 1.0)
        scale = asset_params.get("scale", 1.0)
        
        # Générer l'effet selon son type
        if effect_type == EffectType.FIRE:
            frames = self._generate_fire_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.WATER:
            frames = self._generate_water_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.MAGIC:
            frames = self._generate_magic_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.SMOKE:
            frames = self._generate_smoke_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.EXPLOSION:
            frames = self._generate_explosion_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.ELECTRICITY:
            frames = self._generate_electricity_effect(size, frame_count, intensity, scale)
        elif effect_type == EffectType.AURA:
            frames = self._generate_aura_effect(size, frame_count, intensity, scale)
        else:
            # Type inconnu, générer un effet de feu par défaut
            frames = self._generate_fire_effect(size, frame_count, intensity, scale)
        
        # Appliquer les effets de style Octopath
        frames = [self._apply_octopath_style(frame) for frame in frames]
        
        return frames
    
    def _generate_fire_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet de feu pixelisé style Octopath Traveler"""
        frames = []
        palette = self.effect_palettes[EffectType.FIRE]
        width, height = size
        
        for frame in range(frame_count):
            # Créer une image avec canal alpha
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Paramètres de l'animation
            time_offset = frame / frame_count
            
            # Générer plusieurs particules de feu
            num_particles = int(40 * intensity)
            for i in range(num_particles):
                # Position de base et taille de la particule
                particle_life = random.random()
                particle_x = width // 2 + random.randint(-int(width/4), int(width/4))
                particle_y = height - random.randint(0, int(height * 0.8 * particle_life))
                
                # La taille diminue avec la hauteur (particules plus petites en montant)
                particle_size = max(1, int((1 - particle_life) * 6 * scale))
                
                # Les couleurs varient du jaune au rouge en montant
                color_idx = min(len(palette)-1, int(particle_life * len(palette)))
                color = palette[color_idx]
                
                # Animation de la position - mouvement ondulant
                wave = math.sin((particle_life * 10 + time_offset * 6) * math.pi) * width * 0.05
                particle_x += int(wave)
                
                # Dessiner la particule (pixel carré pour style pixelisé)
                draw.rectangle([
                    particle_x - particle_size, particle_y - particle_size,
                    particle_x + particle_size, particle_y + particle_size
                ], fill=color + (200,))  # Alpha pour transparence
            
            # Appliquer un flou léger pour l'effet de "glow"
            img = img.filter(ImageFilter.GaussianBlur(1))
            
            frames.append(img)
        
        return frames
    
    def _generate_water_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet d'eau pixelisé style Octopath Traveler"""
        frames = []
        palette = self.effect_palettes[EffectType.WATER]
        width, height = size
        
        for frame in range(frame_count):
            # Créer une image avec canal alpha
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Paramètres de l'animation
            time_offset = frame / frame_count
            
            # Générer des vaguelettes d'eau
            num_waves = int(20 * intensity)
            for i in range(num_waves):
                # Position et taille de la vague
                wave_x = random.randint(0, width)
                wave_y = random.randint(int(height * 0.5), height)
                wave_width = random.randint(10, 30) * scale
                wave_height = random.randint(3, 8) * scale
                
                # Animation - les vagues se déplacent horizontalement
                wave_x = (wave_x + int(time_offset * width * 0.5)) % width
                
                # Couleur de la vague
                color_idx = random.randint(0, len(palette) - 1)
                color = palette[color_idx]
                
                # Dessiner une vague stylisée
                points = [
                    (wave_x - wave_width, wave_y),
                    (wave_x - wave_width/2, wave_y - wave_height),
                    (wave_x, wave_y),
                    (wave_x + wave_width/2, wave_y - wave_height),
                    (wave_x + wave_width, wave_y)
                ]
                draw.line(points, fill=color + (180,), width=int(2 * scale))
            
            # Ajouter des reflets (points brillants)
            num_sparkles = int(15 * intensity)
            for i in range(num_sparkles):
                sparkle_x = random.randint(0, width)
                sparkle_y = random.randint(int(height * 0.5), height)
                sparkle_size = random.randint(1, 3) * scale
                
                # Les reflets apparaissent et disparaissent
                alpha = int(200 * abs(math.sin((time_offset + i * 0.1) * math.pi * 2)))
                
                draw.ellipse([
                    sparkle_x - sparkle_size, sparkle_y - sparkle_size,
                    sparkle_x + sparkle_size, sparkle_y + sparkle_size
                ], fill=(255, 255, 255, alpha))
            
            frames.append(img)
        
        return frames
    
    def _generate_magic_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet magique pixelisé style Octopath Traveler"""
        frames = []
        palette = self.effect_palettes[EffectType.MAGIC]
        width, height = size
        
        for frame in range(frame_count):
            # Créer une image avec canal alpha
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Paramètres de l'animation
            time_offset = frame / frame_count
            
            # Générer un cercle magique qui s'élargit
            circle_radius = int(width * 0.1 + width * 0.3 * time_offset) * scale
            circle_x, circle_y = width // 2, height // 2
            
            # Dessiner plusieurs cercles concentriques
            num_circles = 3
            for i in range(num_circles):
                radius = circle_radius - i * (circle_radius // num_circles)
                if radius <= 0:
                    continue
                
                # Couleur du cercle
                color_idx = min(len(palette)-1, i)
                color = palette[color_idx]
                
                # Épaisseur du cercle diminue avec le rayon
                thickness = max(1, int(3 * scale * (1 - i/num_circles)))
                
                # Opacité qui varie avec le temps
                alpha = int(200 * (1 - i/num_circles) * (1 - time_offset))
                
                draw.ellipse([
                    circle_x - radius, circle_y - radius,
                    circle_x + radius, circle_y + radius
                ], outline=color + (alpha,), width=thickness)
            
            # Ajouter des particules magiques
            num_particles = int(50 * intensity)
            for i in range(num_particles):
                # Angle et distance du centre
                angle = 2 * math.pi * (i / num_particles + time_offset)
                distance = circle_radius * random.uniform(0.5, 1.2)
                
                # Position de la particule
                particle_x = circle_x + int(math.cos(angle) * distance)
                particle_y = circle_y + int(math.sin(angle) * distance)
                
                # Taille de la particule
                particle_size = max(1, int(3 * random.random() * scale))
                
                # Couleur de la particule
                color_idx = random.randint(0, len(palette) - 1)
                color = palette[color_idx]
                
                # Alpha basé sur la distance et le temps
                alpha = int(255 * (1 - distance/circle_radius) * random.uniform(0.5, 1.0))
                
                # Dessiner la particule
                draw.rectangle([
                    particle_x - particle_size, particle_y - particle_size,
                    particle_x + particle_size, particle_y + particle_size
                ], fill=color + (alpha,))
            
            # Appliquer un léger flou pour l'effet de glow
            img = img.filter(ImageFilter.GaussianBlur(1))
            
            frames.append(img)
        
        return frames
    
    def _generate_smoke_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet de fumée pixelisé style Octopath Traveler"""
        # Implémentation similaire aux autres effets
        frames = []
        # Code à implémenter
        return [Image.new("RGBA", size, (0, 0, 0, 0)) for _ in range(frame_count)]
    
    def _generate_explosion_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet d'explosion pixelisé style Octopath Traveler"""
        # Implémentation similaire aux autres effets
        frames = []
        # Code à implémenter
        return [Image.new("RGBA", size, (0, 0, 0, 0)) for _ in range(frame_count)]
    
    def _generate_electricity_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet d'électricité pixelisé style Octopath Traveler"""
        # Implémentation similaire aux autres effets
        frames = []
        # Code à implémenter
        return [Image.new("RGBA", size, (0, 0, 0, 0)) for _ in range(frame_count)]
    
    def _generate_aura_effect(self, size, frame_count, intensity=1.0, scale=1.0):
        """Génère un effet d'aura pixelisé style Octopath Traveler"""
        # Implémentation similaire aux autres effets
        frames = []
        # Code à implémenter
        return [Image.new("RGBA", size, (0, 0, 0, 0)) for _ in range(frame_count)]
    
    def _apply_octopath_style(self, img):
        """Applique les effets de style Octopath Traveler à une image"""
        # Renforcer les contrastes pour un aspect plus net
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Ajouter légère pixelisation
        original_size = img.size
        reduced_size = (original_size[0] // 2, original_size[1] // 2)
        img = img.resize(reduced_size, Image.NEAREST).resize(original_size, Image.NEAREST)
        
        # Ajouter un léger bloom pour l'effet de profondeur
        bloom = img.filter(ImageFilter.GaussianBlur(2))
        bloom = ImageEnhance.Brightness(bloom).enhance(1.2)
        img = ImageChops.screen(img, bloom)
        
        return img
    
    def save_asset(self, asset, filepath, **kwargs):
        """
        Sauvegarde les frames de l'effet généré
        
        Args:
            asset (list): Liste des images (frames) de l'effet
            filepath (str): Chemin de base où sauvegarder l'effet
            **kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer le répertoire de sortie s'il n'existe pas
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder chaque frame
            for i, frame in enumerate(asset):
                frame_path = f"{filepath}_frame{i:02d}.png"
                frame.save(frame_path, "PNG")
            
            # Optionnellement, créer un GIF animé
            if kwargs.get("create_gif", True):
                gif_path = f"{filepath}.gif"
                # Durée de chaque frame en millisecondes
                duration = kwargs.get("frame_duration", 100)
                asset[0].save(gif_path, save_all=True, append_images=asset[1:], 
                             optimize=False, duration=duration, loop=0)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'effet: {e}")
            return False

# Fonction principale pour tests
def main():
    """Fonction principale pour tester le générateur d'effets"""
    output_dir = "test_output/effects"
    generator = EffectGenerator(output_dir)
    
    # Générer un effet de feu
    params = {
        "effect_type": "fire",
        "intensity": 1.2,
        "scale": 1.5,
        "frame_count": 12
    }
    fire_frames = generator.generate("test_fire", params, seed=42)
    generator.save_asset(fire_frames, f"{output_dir}/fire_test", create_gif=True)
    
    print(f"Effet généré et sauvegardé dans {output_dir}")

if __name__ == "__main__":
    main() 