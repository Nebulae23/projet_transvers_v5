#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Animation Generator for Nightfall Defenders
Creates organic animations using verlet integration physics
"""

import os
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from enum import Enum
import json

from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

class AnimationType(Enum):
    """Types d'animations que le générateur peut produire"""
    WALK = "walk"
    RUN = "run"
    ATTACK = "attack"
    IDLE = "idle"
    JUMP = "jump"
    FALL = "fall"
    DEATH = "death"
    CAST = "cast"

class BodyPart(Enum):
    """Parties du corps pour le système d'animation verlet"""
    HEAD = "head"
    TORSO = "torso"
    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG = "left_leg"
    RIGHT_LEG = "right_leg"
    WEAPON = "weapon"
    ACCESSORY = "accessory"

class AnimationGenerator(AssetGenerator):
    """Générateur d'animations avec système de physique verlet"""
    
    def __init__(self, output_dir):
        """
        Initialise le générateur d'animations
        
        Args:
            output_dir (str): Répertoire de sortie pour les animations générées
        """
        super().__init__(output_dir)
        
        # Création des sous-répertoires pour les animations
        self.animation_dirs = {anim_type: os.path.join(output_dir, anim_type.value) 
                              for anim_type in AnimationType}
        
        for directory in self.animation_dirs.values():
            os.makedirs(directory, exist_ok=True)
        
        # Paramètres par défaut
        self.base_sprite_size = (64, 64)
        self.frame_count = {
            AnimationType.WALK: 8,
            AnimationType.RUN: 8,
            AnimationType.ATTACK: 6,
            AnimationType.IDLE: 4,
            AnimationType.JUMP: 5,
            AnimationType.FALL: 4,
            AnimationType.DEATH: 10,
            AnimationType.CAST: 8
        }
        
        # Paramètres de physique verlet
        self.gravity = 0.5
        self.friction = 0.95
        self.stiffness = 0.5
        
    def generate(self, asset_id, asset_params, seed=None):
        """
        Génère une animation selon les paramètres spécifiés
        
        Args:
            asset_id (str): Identifiant unique pour l'animation
            asset_params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            dict: Animation générée (frames + metadata)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Extraire les paramètres
        anim_type_str = asset_params.get("animation_type", "idle")
        anim_type = next((at for at in AnimationType if at.value == anim_type_str), AnimationType.IDLE)
        
        size = asset_params.get("size", self.base_sprite_size)
        frame_count = asset_params.get("frame_count", self.frame_count.get(anim_type))
        character_type = asset_params.get("character_type", "warrior")
        
        # Générer le modèle de personnage en verlet pour l'animation
        character_model = self._create_character_model(character_type, size)
        
        # Générer l'animation selon son type
        if anim_type == AnimationType.WALK:
            frames = self._generate_walk_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.RUN:
            frames = self._generate_run_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.ATTACK:
            frames = self._generate_attack_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.IDLE:
            frames = self._generate_idle_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.JUMP:
            frames = self._generate_jump_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.FALL:
            frames = self._generate_fall_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.DEATH:
            frames = self._generate_death_animation(character_model, frame_count, size)
        elif anim_type == AnimationType.CAST:
            frames = self._generate_cast_animation(character_model, frame_count, size)
        else:
            # Type inconnu, générer une animation idle par défaut
            frames = self._generate_idle_animation(character_model, frame_count, size)
        
        # Créer les métadonnées pour l'animation
        animation_data = {
            "frames": frames,
            "metadata": {
                "asset_id": asset_id,
                "animation_type": anim_type.value,
                "character_type": character_type,
                "frame_count": frame_count,
                "frame_duration": 100,  # ms par image par défaut
                "loop": anim_type != AnimationType.DEATH  # Toutes les animations en boucle sauf la mort
            }
        }
        
        return animation_data
    
    def _create_character_model(self, character_type, size):
        """
        Crée un modèle de personnage avec des points et contraintes pour la simulation verlet
        
        Args:
            character_type (str): Type de personnage (warrior, mage, etc.)
            size (tuple): Dimensions de base du sprite
            
        Returns:
            dict: Modèle du personnage avec points et contraintes pour verlet
        """
        width, height = size
        center_x, center_y = width // 2, height // 2
        
        # Définir les points du modèle (position, ancienne position, masse)
        # Les positions sont relatives au centre de l'image
        points = {
            "head": {"pos": [center_x, center_y - 15], "old_pos": [center_x, center_y - 15], "mass": 1.0},
            "torso": {"pos": [center_x, center_y], "old_pos": [center_x, center_y], "mass": 2.0},
            "hip": {"pos": [center_x, center_y + 10], "old_pos": [center_x, center_y + 10], "mass": 1.5},
            "left_hand": {"pos": [center_x - 12, center_y], "old_pos": [center_x - 12, center_y], "mass": 0.5},
            "right_hand": {"pos": [center_x + 12, center_y], "old_pos": [center_x + 12, center_y], "mass": 0.5},
            "left_foot": {"pos": [center_x - 8, center_y + 20], "old_pos": [center_x - 8, center_y + 20], "mass": 0.5},
            "right_foot": {"pos": [center_x + 8, center_y + 20], "old_pos": [center_x + 8, center_y + 20], "mass": 0.5}
        }
        
        # Définir les contraintes qui lient les points (distance fixe)
        constraints = [
            {"p1": "head", "p2": "torso", "distance": 15},
            {"p1": "torso", "p2": "hip", "distance": 10},
            {"p1": "torso", "p2": "left_hand", "distance": 12},
            {"p1": "torso", "p2": "right_hand", "distance": 12},
            {"p1": "hip", "p2": "left_foot", "distance": 20},
            {"p1": "hip", "p2": "right_foot", "distance": 20}
        ]
        
        # Propriétés visuelles (couleurs, tailles) spécifiques au type de personnage
        visual_props = {}
        if character_type == "warrior":
            visual_props = {
                "head_color": (180, 150, 120, 255),
                "torso_color": (180, 30, 30, 255),  # Rouge pour guerrier
                "limb_color": (50, 50, 50, 255),
                "head_size": 5,
                "torso_size": 8,
                "limb_size": 3
            }
        elif character_type == "mage":
            visual_props = {
                "head_color": (180, 150, 120, 255),
                "torso_color": (50, 50, 180, 255),  # Bleu pour mage
                "limb_color": (70, 70, 100, 255),
                "head_size": 5,
                "torso_size": 8,
                "limb_size": 3
            }
        else:
            # Propriétés par défaut
            visual_props = {
                "head_color": (180, 150, 120, 255),
                "torso_color": (100, 100, 100, 255),
                "limb_color": (70, 70, 70, 255),
                "head_size": 5,
                "torso_size": 8,
                "limb_size": 3
            }
        
        # Assembler le modèle complet
        character_model = {
            "points": points,
            "constraints": constraints,
            "visual": visual_props,
            "character_type": character_type
        }
        
        return character_model
    
    def _update_verlet_physics(self, model, dt=1.0):
        """
        Met à jour les positions des points selon la simulation verlet
        
        Args:
            model (dict): Modèle de personnage avec points et contraintes
            dt (float): Pas de temps pour la simulation
            
        Returns:
            dict: Modèle mis à jour
        """
        points = model["points"]
        constraints = model["constraints"]
        
        # Mettre à jour les positions (intégration de verlet)
        for point_name, point in points.items():
            # Sauvegarder la position actuelle
            pos = point["pos"]
            old_pos = point["old_pos"]
            mass = point["mass"]
            
            # Calculer la vélocité
            vel_x = (pos[0] - old_pos[0]) * self.friction
            vel_y = (pos[1] - old_pos[1]) * self.friction
            
            # Mettre à jour l'ancienne position
            point["old_pos"] = [pos[0], pos[1]]
            
            # Appliquer la gravité et mettre à jour la position
            point["pos"] = [
                pos[0] + vel_x,
                pos[1] + vel_y + self.gravity / mass * dt
            ]
        
        # Satisfaire les contraintes (plusieurs itérations pour stabilité)
        for _ in range(5):
            for constraint in constraints:
                p1_name = constraint["p1"]
                p2_name = constraint["p2"]
                distance = constraint["distance"]
                
                p1 = points[p1_name]
                p2 = points[p2_name]
                
                # Calculer le vecteur entre les points
                dx = p2["pos"][0] - p1["pos"][0]
                dy = p2["pos"][1] - p1["pos"][1]
                
                # Calculer la distance actuelle
                current_distance = max(0.01, math.sqrt(dx*dx + dy*dy))
                
                # Calculer le facteur de correction
                difference = (distance - current_distance) / current_distance
                
                # Redistribuer en fonction des masses
                m1 = p1["mass"]
                m2 = p2["mass"]
                total_mass = m1 + m2
                m1_factor = m2 / total_mass
                m2_factor = m1 / total_mass
                
                # Appliquer la correction
                p1["pos"] = [
                    p1["pos"][0] - dx * 0.5 * difference * m1_factor * self.stiffness,
                    p1["pos"][1] - dy * 0.5 * difference * m1_factor * self.stiffness
                ]
                
                p2["pos"] = [
                    p2["pos"][0] + dx * 0.5 * difference * m2_factor * self.stiffness,
                    p2["pos"][1] + dy * 0.5 * difference * m2_factor * self.stiffness
                ]
        
        # Retourner le modèle mis à jour
        return model
    
    def _render_character(self, model, size):
        """
        Rend le modèle de personnage en une image
        
        Args:
            model (dict): Modèle de personnage avec points et contraintes
            size (tuple): Dimensions de l'image
            
        Returns:
            PIL.Image: Rendu du personnage
        """
        # Créer une image vide avec transparence
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        points = model["points"]
        visual = model["visual"]
        
        # Dessiner les connections (membres)
        # Jambes
        draw.line([tuple(points["hip"]["pos"]), tuple(points["left_foot"]["pos"])], 
                  fill=visual["limb_color"], width=visual["limb_size"])
        draw.line([tuple(points["hip"]["pos"]), tuple(points["right_foot"]["pos"])], 
                  fill=visual["limb_color"], width=visual["limb_size"])
        
        # Torse
        draw.line([tuple(points["head"]["pos"]), tuple(points["torso"]["pos"])], 
                  fill=visual["torso_color"], width=visual["torso_size"])
        draw.line([tuple(points["torso"]["pos"]), tuple(points["hip"]["pos"])], 
                  fill=visual["torso_color"], width=visual["torso_size"])
        
        # Bras
        draw.line([tuple(points["torso"]["pos"]), tuple(points["left_hand"]["pos"])], 
                  fill=visual["limb_color"], width=visual["limb_size"])
        draw.line([tuple(points["torso"]["pos"]), tuple(points["right_hand"]["pos"])], 
                  fill=visual["limb_color"], width=visual["limb_size"])
        
        # Dessiner les points (articulations)
        radius = visual["head_size"]
        head_pos = points["head"]["pos"]
        draw.ellipse([
            head_pos[0] - radius, head_pos[1] - radius,
            head_pos[0] + radius, head_pos[1] + radius
        ], fill=visual["head_color"])
        
        # Dessiner les autres points selon besoin
        # ...
        
        # Appliquer des effets de style Octopath Traveler
        img = self._apply_octopath_style(img)
        
        return img
    
    def _apply_octopath_style(self, img):
        """Applique les effets de style Octopath Traveler à une image"""
        # Renforcer les contrastes pour un aspect plus net
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Légère pixelisation pour le style rétro
        original_size = img.size
        reduced_size = (original_size[0] // 2, original_size[1] // 2)
        img = img.resize(reduced_size, Image.NEAREST).resize(original_size, Image.NEAREST)
        
        # Ajouter un léger bloom pour l'effet de profondeur
        bloom = img.filter(ImageFilter.GaussianBlur(2))
        img = ImageChops.screen(img, bloom)
        
        return img
    
    def _generate_walk_animation(self, character_model, frame_count, size):
        """Génère une animation de marche avec physique verlet"""
        frames = []
        model = character_model.copy()
        
        for frame in range(frame_count):
            # Calculer la phase de l'animation (0 à 2π)
            phase = frame / frame_count * 2 * math.pi
            
            # Appliquer les modifications spécifiques à la marche
            model = self._apply_walk_pose(model, phase)
            
            # Mettre à jour la physique
            model = self._update_verlet_physics(model)
            
            # Rendre l'image
            img = self._render_character(model, size)
            frames.append(img)
        
        return frames
    
    def _apply_walk_pose(self, model, phase):
        """Applique une pose de marche au modèle"""
        # Simuler le mouvement de marche en modifiant les positions cibles
        points = model["points"]
        
        # Mouvement des jambes alternant
        leg_swing = math.sin(phase) * 8
        points["left_foot"]["pos"][0] = points["hip"]["pos"][0] - 8 + leg_swing
        points["right_foot"]["pos"][0] = points["hip"]["pos"][0] + 8 - leg_swing
        
        # Hauteur des pieds variant avec la phase
        left_foot_height = -math.sin(phase) * 3
        right_foot_height = -math.sin(phase + math.pi) * 3
        points["left_foot"]["pos"][1] = points["hip"]["pos"][1] + 20 + left_foot_height
        points["right_foot"]["pos"][1] = points["hip"]["pos"][1] + 20 + right_foot_height
        
        # Mouvement des bras opposé aux jambes
        arm_swing = math.sin(phase + math.pi) * 5
        points["left_hand"]["pos"][0] = points["torso"]["pos"][0] - 12 + arm_swing
        points["right_hand"]["pos"][0] = points["torso"]["pos"][0] + 12 - arm_swing
        
        # Léger mouvement vertical du corps
        body_bounce = -math.abs(math.sin(phase * 2)) * 1.5
        points["torso"]["pos"][1] = model["points"]["torso"]["old_pos"][1] + body_bounce
        
        return model
    
    def _generate_run_animation(self, character_model, frame_count, size):
        """Génère une animation de course avec physique verlet"""
        # Similaire à la marche mais plus rapide et avec plus d'amplitude
        frames = []
        # À implémenter
        return frames
    
    def _generate_attack_animation(self, character_model, frame_count, size):
        """Génère une animation d'attaque avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def _generate_idle_animation(self, character_model, frame_count, size):
        """Génère une animation idle avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def _generate_jump_animation(self, character_model, frame_count, size):
        """Génère une animation de saut avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def _generate_fall_animation(self, character_model, frame_count, size):
        """Génère une animation de chute avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def _generate_death_animation(self, character_model, frame_count, size):
        """Génère une animation de mort avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def _generate_cast_animation(self, character_model, frame_count, size):
        """Génère une animation de cast avec physique verlet"""
        frames = []
        # À implémenter
        return frames
    
    def save_asset(self, asset, filepath, **kwargs):
        """
        Sauvegarde l'animation générée
        
        Args:
            asset (dict): Animation générée (frames + metadata)
            filepath (str): Chemin de base où sauvegarder l'animation
            **kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer le répertoire de sortie s'il n'existe pas
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            frames = asset["frames"]
            metadata = asset["metadata"]
            
            # Sauvegarder chaque frame
            for i, frame in enumerate(frames):
                frame_path = f"{filepath}_frame{i:02d}.png"
                frame.save(frame_path, "PNG")
            
            # Sauvegarder les métadonnées
            with open(f"{filepath}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Optionnellement, créer un GIF animé
            if kwargs.get("create_gif", True):
                gif_path = f"{filepath}.gif"
                # Durée de chaque frame en millisecondes
                duration = metadata.get("frame_duration", 100)
                frames[0].save(gif_path, save_all=True, append_images=frames[1:], 
                             optimize=False, duration=duration, loop=0 if metadata.get("loop", True) else 1)
            
            # Optionnellement, créer un spritesheet
            if kwargs.get("create_spritesheet", False):
                spritesheet_path = f"{filepath}_spritesheet.png"
                self._create_spritesheet(frames, spritesheet_path)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'animation: {e}")
            return False
    
    def _create_spritesheet(self, frames, filepath):
        """
        Crée un spritesheet à partir des frames d'animation
        
        Args:
            frames (list): Liste des images de l'animation
            filepath (str): Chemin où sauvegarder le spritesheet
        """
        if not frames:
            return
        
        frame_width, frame_height = frames[0].size
        sprite_cols = min(8, len(frames))  # Maximum 8 frames par ligne
        sprite_rows = (len(frames) + sprite_cols - 1) // sprite_cols
        
        # Créer une image de la taille nécessaire
        spritesheet = Image.new(
            "RGBA",
            (frame_width * sprite_cols, frame_height * sprite_rows),
            (0, 0, 0, 0)
        )
        
        # Coller chaque frame à sa position
        for i, frame in enumerate(frames):
            row = i // sprite_cols
            col = i % sprite_cols
            spritesheet.paste(frame, (col * frame_width, row * frame_height))
        
        # Sauvegarder le spritesheet
        spritesheet.save(filepath, "PNG")

# Fonction principale pour tests
def main():
    """Fonction principale pour tester le générateur d'animations"""
    output_dir = "test_output/animations"
    generator = AnimationGenerator(output_dir)
    
    # Générer une animation de marche
    params = {
        "animation_type": "walk",
        "character_type": "warrior",
        "frame_count": 8
    }
    walk_animation = generator.generate("warrior_walk", params, seed=42)
    generator.save_asset(walk_animation, f"{output_dir}/warrior_walk", create_gif=True, create_spritesheet=True)
    
    print(f"Animation générée et sauvegardée dans {output_dir}")

if __name__ == "__main__":
    main() 