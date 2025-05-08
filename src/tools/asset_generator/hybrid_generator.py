#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Generator for Nightfall Defenders
Combines procedural rules with PBR technique and machine learning refinement
for realistic asset generation
"""

import os
import random
import math
import json
import numpy as np
import torch
import cv2
from PIL import Image, ImageDraw, ImageFilter
from skimage import exposure, color, filters
import opensimplex
from scipy.ndimage import gaussian_filter

# Import base generator classes
from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

# Custom Worley noise implementation to replace the worley package
def custom_worley(width, height, points=20, noise_scale=1.0):
    """
    Implémentation personnalisée de Worley noise utilisant NumPy et OpenCV
    
    Args:
        width (int): Largeur de l'image
        height (int): Hauteur de l'image
        points (int): Nombre de points à générer (cellules)
        noise_scale (float): Échelle du bruit
        
    Returns:
        numpy.ndarray: Worley noise map (0-1)
    """
    # Créer des points aléatoires (centres des cellules)
    np.random.seed(random.randint(0, 10000))  # Pour la reproductibilité mais avec variation
    feature_points = np.random.rand(points, 2) * noise_scale
    
    # Créer la grille
    x = np.linspace(0, 1, width) * noise_scale
    y = np.linspace(0, 1, height) * noise_scale
    X, Y = np.meshgrid(x, y)
    
    # Initialiser la map avec des valeurs infinies
    worley_map = np.full((height, width), np.inf)
    
    # Calculer la distance au point le plus proche pour chaque pixel
    for p in feature_points:
        dx = X - p[0]
        dy = Y - p[1]
        distance = np.sqrt(dx**2 + dy**2)
        worley_map = np.minimum(worley_map, distance)
    
    # Normaliser
    if np.max(worley_map) > 0:
        worley_map = worley_map / np.max(worley_map)
    
    return worley_map

class PBRMaps:
    """Types de maps PBR supportées par le générateur"""
    DIFFUSE = "diffuse"  # Base color
    NORMAL = "normal"    # Surface details
    ROUGHNESS = "roughness"  # Surface smoothness
    METALLIC = "metallic"  # How metallic a surface is
    AO = "ambient_occlusion"  # Ambient occlusion
    HEIGHT = "height"  # Height/displacement map
    EMISSIVE = "emissive"  # Self-illumination

class MaterialPresets:
    """Presets de matériaux pour la génération PBR"""
    STONE = "stone"
    WOOD = "wood"
    METAL = "metal"
    FABRIC = "fabric"
    LEATHER = "leather"
    GRASS = "grass"
    WATER = "water"
    SNOW = "snow"
    SAND = "sand"
    
class NoiseTypes:
    """Types de bruit supportés"""
    PERLIN = "perlin"
    SIMPLEX = "simplex"
    WORLEY = "worley"
    FRACTAL = "fractal"
    CURL = "curl"

class HybridGenerator(AssetGenerator):
    """
    Générateur hybride qui combine génération procédurale avancée,
    techniques PBR et raffinement par machine learning
    """
    
    def __init__(self, output_dir):
        """
        Initialise le générateur hybride
        
        Args:
            output_dir (str): Répertoire de sortie pour les assets générés
        """
        super().__init__(output_dir)
        
        # Création des sous-répertoires pour les différents types de maps
        self.pbr_dirs = {
            PBRMaps.DIFFUSE: os.path.join(output_dir, "diffuse"),
            PBRMaps.NORMAL: os.path.join(output_dir, "normal"),
            PBRMaps.ROUGHNESS: os.path.join(output_dir, "roughness"),
            PBRMaps.METALLIC: os.path.join(output_dir, "metallic"),
            PBRMaps.AO: os.path.join(output_dir, "ao"),
            PBRMaps.HEIGHT: os.path.join(output_dir, "height"),
            PBRMaps.EMISSIVE: os.path.join(output_dir, "emissive")
        }
        
        for directory in self.pbr_dirs.values():
            os.makedirs(directory, exist_ok=True)
            
        # Initialiser le modèle ML pour le raffinement (si disponible)
        self.ml_model = None
        self.ml_available = False
        
        try:
            # Tente de charger un modèle ONNX simple pour le raffinement des textures
            import onnxruntime as ort
            model_path = os.path.join(os.path.dirname(__file__), "models", "texture_refiner.onnx")
            if os.path.exists(model_path):
                self.ml_model = ort.InferenceSession(model_path)
                self.ml_available = True
            else:
                print("Modèle ML non trouvé. Le raffinement ML sera désactivé.")
        except ImportError:
            print("onnxruntime non disponible. Le raffinement ML sera désactivé.")
            
        # Initialiser les générateurs de bruit
        self.simplex_gen = opensimplex.OpenSimplex()
        # Worley generator est remplacé par notre implémentation personnalisée
        
        # Prérégler les configurations de matériaux pour cohérence
        self.material_presets = self._init_material_presets()
        
    def generate(self, asset_id, asset_params, seed=None):
        """
        Génère un asset avec une approche hybride PBR et ML
        
        Args:
            asset_id (str): Identifiant unique pour l'asset
            asset_params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            dict: Ensemble des maps PBR générées
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # Extraire les paramètres communs
        size = asset_params.get("size", (512, 512))
        asset_type = asset_params.get("asset_type", AssetType.MODEL_3D)
        material_type = asset_params.get("material", MaterialPresets.STONE)
        
        # Générer les maps PBR de base avec les règles procédurales
        pbr_maps = self._generate_pbr_maps(asset_id, asset_params, size, material_type)
        
        # Appliquer la couche de raffinement ML si disponible
        if self.ml_available and asset_params.get("use_ml_refinement", True):
            pbr_maps = self._apply_ml_refinement(pbr_maps)
            
        # Appliquer les règles contextuelles si nécessaire
        if asset_params.get("apply_context_rules", True):
            context = asset_params.get("context", {})
            pbr_maps = self._apply_context_rules(pbr_maps, context)
            
        return pbr_maps
        
    def _generate_pbr_maps(self, asset_id, params, size, material_type):
        """
        Génère l'ensemble des maps PBR pour un asset
        
        Args:
            asset_id (str): Identifiant de l'asset
            params (dict): Paramètres de génération
            size (tuple): Dimensions des textures (largeur, hauteur)
            material_type (str): Type de matériau à générer
            
        Returns:
            dict: Maps PBR générées (diffuse, normal, roughness, etc.)
        """
        # Récupérer les préréglages pour ce matériau
        material_preset = self.material_presets.get(material_type, self.material_presets[MaterialPresets.STONE])
        
        # Générer une texture de hauteur de base (utilisée pour les autres maps)
        height_map = self._generate_height_map(size, params, material_preset)
        
        # Générer les autres maps PBR en se basant sur la height map
        pbr_maps = {
            PBRMaps.HEIGHT: height_map,
            PBRMaps.DIFFUSE: self._generate_diffuse_map(height_map, params, material_preset),
            PBRMaps.NORMAL: self._generate_normal_map(height_map, params, material_preset),
            PBRMaps.ROUGHNESS: self._generate_roughness_map(height_map, params, material_preset),
            PBRMaps.METALLIC: self._generate_metallic_map(height_map, params, material_preset),
            PBRMaps.AO: self._generate_ao_map(height_map, params, material_preset)
        }
        
        # Générer la carte émissive si nécessaire
        if params.get("has_emission", False):
            pbr_maps[PBRMaps.EMISSIVE] = self._generate_emissive_map(height_map, params, material_preset)
            
        return pbr_maps
        
    def _apply_ml_refinement(self, pbr_maps):
        """
        Applique un raffinement par ML aux textures générées
        
        Args:
            pbr_maps (dict): Maps PBR à raffiner
            
        Returns:
            dict: Maps PBR raffinées
        """
        if not self.ml_available:
            return pbr_maps
            
        refined_maps = {}
        
        try:
            # Pour chaque map, appliquer le raffinement ML
            for map_type, map_data in pbr_maps.items():
                # Convertir l'image en format compatible avec le modèle ML
                input_data = self._prepare_map_for_ml(map_data, map_type)
                
                # Appliquer le modèle
                output_data = self.ml_model.run(None, {"input": input_data})[0]
                
                # Reconvertir en format image
                refined_maps[map_type] = self._process_ml_output(output_data, map_type)
                
            return refined_maps
        except Exception as e:
            print(f"Erreur lors du raffinement ML: {e}")
            return pbr_maps
            
    def _apply_context_rules(self, pbr_maps, context):
        """
        Applique des règles contextuelles pour adapter l'asset à son environnement
        
        Args:
            pbr_maps (dict): Maps PBR à adapter
            context (dict): Informations contextuelles (environnement, âge, etc.)
            
        Returns:
            dict: Maps PBR adaptées au contexte
        """
        # Si aucun contexte fourni, retourner les maps inchangées
        if not context:
            return pbr_maps
            
        modified_maps = pbr_maps.copy()
        
        # Appliquer les effets environnementaux
        environment = context.get("environment")
        if environment:
            if environment == "snow":
                modified_maps = self._apply_snow_effect(modified_maps)
            elif environment == "desert":
                modified_maps = self._apply_sand_effect(modified_maps)
            elif environment == "wet" or environment == "water":
                modified_maps = self._apply_wet_effect(modified_maps)
                
        # Appliquer les effets de vieillissement
        age_factor = context.get("age_factor", 0.0)  # 0.0 = neuf, 1.0 = vieux
        if age_factor > 0:
            modified_maps = self._apply_aging_effect(modified_maps, age_factor)
            
        return modified_maps
    
    def _init_material_presets(self):
        """
        Initialise les préréglages de matériaux pour la génération PBR
        
        Returns:
            dict: Préréglages de matériaux
        """
        return {
            MaterialPresets.STONE: {
                "noise_type": NoiseTypes.FRACTAL,
                "noise_scale": 0.1,
                "octaves": 6,
                "persistence": 0.5,
                "lacunarity": 2.0,
                "base_color": (0.7, 0.7, 0.7),
                "color_variation": 0.2,
                "roughness_base": 0.7,
                "metallic_base": 0.0,
                "height_scale": 1.0
            },
            MaterialPresets.WOOD: {
                "noise_type": NoiseTypes.SIMPLEX,
                "noise_scale": 0.05,
                "octaves": 4,
                "persistence": 0.6,
                "lacunarity": 2.0,
                "base_color": (0.6, 0.4, 0.2),
                "color_variation": 0.15,
                "roughness_base": 0.5,
                "metallic_base": 0.0,
                "grain_amount": 0.8,
                "grain_orientation": 0.0,
                "height_scale": 0.6
            },
            # Autres préréglages de matériaux...
            MaterialPresets.METAL: {
                "noise_type": NoiseTypes.SIMPLEX,
                "noise_scale": 0.03,
                "octaves": 2,
                "persistence": 0.5,
                "lacunarity": 2.0,
                "base_color": (0.8, 0.8, 0.9),
                "color_variation": 0.1,
                "roughness_base": 0.3,
                "metallic_base": 0.9,
                "height_scale": 0.2
            }
        } 

    def _generate_height_map(self, size, params, material_preset):
        """
        Génère une height map de base
        
        Args:
            size (tuple): Dimensions de la texture
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            numpy.ndarray: Height map générée (0-1)
        """
        width, height = size
        noise_type = params.get("noise_type", material_preset.get("noise_type", NoiseTypes.SIMPLEX))
        noise_scale = params.get("noise_scale", material_preset.get("noise_scale", 0.1))
        octaves = params.get("octaves", material_preset.get("octaves", 4))
        persistence = params.get("persistence", material_preset.get("persistence", 0.5))
        lacunarity = params.get("lacunarity", material_preset.get("lacunarity", 2.0))
        height_scale = params.get("height_scale", material_preset.get("height_scale", 1.0))
        
        # Créer une map vide
        height_map = np.zeros((height, width), dtype=np.float32)
        
        # Générer selon le type de bruit
        if noise_type == NoiseTypes.SIMPLEX:
            for y in range(height):
                for x in range(width):
                    nx = x / width - 0.5
                    ny = y / height - 0.5
                    # Utiliser opensimplex pour générer le bruit
                    height_map[y, x] = self.simplex_gen.noise2(nx * noise_scale, ny * noise_scale)
                    
        elif noise_type == NoiseTypes.WORLEY:
            # Utiliser notre implémentation personnalisée de Worley noise
            num_points = params.get("worley_points", material_preset.get("worley_points", 20))
            height_map = custom_worley(width, height, points=num_points, noise_scale=noise_scale)
                    
        elif noise_type == NoiseTypes.FRACTAL:
            # Bruit fractal (FBM - Fractional Brownian Motion)
            for y in range(height):
                for x in range(width):
                    nx = x / width - 0.5
                    ny = y / height - 0.5
                    
                    amplitude = 1.0
                    frequency = 1.0
                    noise_value = 0
                    
                    # Additionner plusieurs octaves de bruit
                    for i in range(octaves):
                        noise_value += amplitude * self.simplex_gen.noise2(
                            nx * noise_scale * frequency, 
                            ny * noise_scale * frequency
                        )
                        amplitude *= persistence
                        frequency *= lacunarity
                        
                    height_map[y, x] = noise_value
        
        # Normaliser les valeurs
        height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min() + 1e-10)
        
        # Appliquer l'échelle de hauteur
        height_map *= height_scale
        
        return height_map
    
    def _generate_normal_map(self, height_map, params, material_preset):
        """
        Génère une normal map à partir de la height map
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: Normal map générée (RGB)
        """
        # Intensité des normales
        strength = params.get("normal_strength", 1.0)
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Calculer les gradients
        grad_x = cv2.Sobel(height_map, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(height_map, cv2.CV_32F, 0, 1, ksize=3)
        
        # Inverser le gradient y pour correspondre aux conventions des normal maps
        grad_y = -grad_y
        
        # Normaliser les gradients
        grad_x = cv2.normalize(grad_x, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        grad_y = cv2.normalize(grad_y, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        
        # Ajuster l'intensité
        grad_x = ((grad_x * 0.5 + 0.5) - 0.5) * strength + 0.5
        grad_y = ((grad_y * 0.5 + 0.5) - 0.5) * strength + 0.5
        
        # Créer la normal map (RGB)
        normal_map = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.uint8)
        
        # R = x, G = y, B = z (toujours positif en tangent space)
        normal_map[..., 0] = grad_x * 255
        normal_map[..., 1] = grad_y * 255
        normal_map[..., 2] = 255  # Z toujours positif dans tangent space
        
        return Image.fromarray(normal_map)
    
    def _generate_diffuse_map(self, height_map, params, material_preset):
        """
        Génère une diffuse map (albedo) basée sur la height map
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: Diffuse map générée (RGB)
        """
        # Paramètres de couleur
        base_color = params.get("base_color", material_preset.get("base_color", (0.7, 0.7, 0.7)))
        color_variation = params.get("color_variation", material_preset.get("color_variation", 0.2))
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Créer une base de couleur
        diffuse_map = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.float32)
        diffuse_map[..., 0] = base_color[0]
        diffuse_map[..., 1] = base_color[1]
        diffuse_map[..., 2] = base_color[2]
        
        # Ajouter des variations de couleur basées sur la height map
        for c in range(3):
            variation = (height_map - 0.5) * color_variation
            diffuse_map[..., c] = np.clip(diffuse_map[..., c] + variation, 0, 1)
        
        # Ajout de détails (optionnel)
        if params.get("add_details", True):
            # Générer du bruit à plus petite échelle pour les détails
            detail_scale = params.get("detail_scale", 10)
            detail_strength = params.get("detail_strength", 0.1)
            
            height, width = height_map.shape
            detail_map = np.zeros_like(height_map)
            
            for y in range(height):
                for x in range(width):
                    nx = x / width - 0.5
                    ny = y / height - 0.5
                    detail_map[y, x] = self.simplex_gen.noise2(
                        nx * detail_scale, 
                        ny * detail_scale
                    )
            
            # Normaliser les détails
            detail_map = (detail_map - detail_map.min()) / (detail_map.max() - detail_map.min())
            
            # Ajouter les détails à diffuse map
            for c in range(3):
                variation = (detail_map - 0.5) * detail_strength
                diffuse_map[..., c] = np.clip(diffuse_map[..., c] + variation, 0, 1)
        
        # Convertir en 8-bit
        diffuse_map = (diffuse_map * 255).astype(np.uint8)
        
        return Image.fromarray(diffuse_map)
    
    def _generate_roughness_map(self, height_map, params, material_preset):
        """
        Génère une roughness map basée sur la height map
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: Roughness map générée (grayscale)
        """
        # Paramètres de rugosité
        roughness_base = params.get("roughness_base", material_preset.get("roughness_base", 0.5))
        roughness_variation = params.get("roughness_variation", material_preset.get("roughness_variation", 0.3))
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Créer une base de rugosité
        roughness_map = np.full_like(height_map, roughness_base)
        
        # Ajouter des variations basées sur la height map
        variation = (height_map - 0.5) * roughness_variation
        roughness_map = np.clip(roughness_map + variation, 0, 1)
        
        # Ajouter du grain/détails microscopiques
        if params.get("add_micro_details", True):
            # Micro-détails aléatoires pour simuler la rugosité de surface
            noise = np.random.rand(*roughness_map.shape) * 0.1
            roughness_map = np.clip(roughness_map + noise, 0, 1)
            
            # Lisser légèrement pour éviter le bruit du pixel
            roughness_map = gaussian_filter(roughness_map, sigma=0.5)
        
        # Convertir en 8-bit
        roughness_map = (roughness_map * 255).astype(np.uint8)
        
        return Image.fromarray(roughness_map)
    
    def _generate_metallic_map(self, height_map, params, material_preset):
        """
        Génère une metallic map basée sur le material
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: Metallic map générée (grayscale)
        """
        # Paramètres métalliques
        metallic_base = params.get("metallic_base", material_preset.get("metallic_base", 0.0))
        metallic_variation = params.get("metallic_variation", material_preset.get("metallic_variation", 0.1))
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Créer une base métallique
        metallic_map = np.full_like(height_map, metallic_base)
        
        # Pour la plupart des matériaux, la valeur métallique est constante (0 ou 1)
        # Mais pour certains cas mixtes (ex: métal rouillé), on peut ajouter des variations
        if metallic_variation > 0:
            variation = (height_map - 0.5) * metallic_variation
            metallic_map = np.clip(metallic_map + variation, 0, 1)
        
        # Convertir en 8-bit
        metallic_map = (metallic_map * 255).astype(np.uint8)
        
        return Image.fromarray(metallic_map)
    
    def _generate_ao_map(self, height_map, params, material_preset):
        """
        Génère une ambient occlusion map basée sur la height map
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: AO map générée (grayscale)
        """
        # Paramètres d'AO
        ao_strength = params.get("ao_strength", material_preset.get("ao_strength", 0.7))
        ao_radius = params.get("ao_radius", material_preset.get("ao_radius", 3))
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Calculer une approximation simple de l'AO en utilisant le Laplacien de la height map
        # Un Laplacien détecte les bords/coins où l'occlusion se produit généralement
        laplacian = cv2.Laplacian(height_map, cv2.CV_32F)
        
        # Normaliser
        laplacian = cv2.normalize(laplacian, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        
        # Inverser et ajuster pour l'AO (zones sombres = occlusion)
        ao_map = 1.0 - (laplacian * ao_strength)
        
        # Appliquer un flou pour adoucir l'effet
        ao_map = cv2.GaussianBlur(ao_map, (ao_radius*2+1, ao_radius*2+1), 0)
        
        # Ajuster le contraste
        ao_map = np.clip((ao_map - 0.5) * 1.2 + 0.5, 0, 1)
        
        # Convertir en 8-bit
        ao_map = (ao_map * 255).astype(np.uint8)
        
        return Image.fromarray(ao_map)
    
    def _generate_emissive_map(self, height_map, params, material_preset):
        """
        Génère une emissive map pour les matériaux lumineux
        
        Args:
            height_map (numpy.ndarray): Height map source
            params (dict): Paramètres de génération
            material_preset (dict): Préréglages du matériau
            
        Returns:
            PIL.Image: Emissive map générée (RGB)
        """
        # Si le matériau n'est pas émissif, retourner une map noire
        if not params.get("has_emission", False):
            emissive_map = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.uint8)
            return Image.fromarray(emissive_map)
        
        # Paramètres d'émission
        emission_color = params.get("emission_color", (0.0, 1.0, 0.2))  # Vert par défaut
        emission_strength = params.get("emission_strength", 0.8)
        emission_pattern = params.get("emission_pattern", "noise")
        
        # Convertir la height map en image au besoin
        if isinstance(height_map, Image.Image):
            height_map = np.array(height_map)
        
        # Créer une base d'émission
        emissive_map = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.float32)
        
        # Appliquer différents patterns d'émission
        if emission_pattern == "noise":
            # Pattern de bruit pour l'émission
            for y in range(height_map.shape[0]):
                for x in range(height_map.shape[1]):
                    nx = x / height_map.shape[1] - 0.5
                    ny = y / height_map.shape[0] - 0.5
                    noise_val = abs(self.simplex_gen.noise2(nx * 5, ny * 5))
                    # Seuil pour rendre certaines zones émissives
                    if noise_val > 0.7:
                        intensity = (noise_val - 0.7) / 0.3  # Normaliser à 0-1
                        emissive_map[y, x, 0] = emission_color[0] * intensity * emission_strength
                        emissive_map[y, x, 1] = emission_color[1] * intensity * emission_strength
                        emissive_map[y, x, 2] = emission_color[2] * intensity * emission_strength
        
        elif emission_pattern == "cracks":
            # Pattern de fissures pour l'émission
            threshold = params.get("emission_threshold", 0.7)
            edge_map = filters.sobel(height_map)
            mask = edge_map > threshold
            
            # Appliquer le masque à la carte d'émission
            for c in range(3):
                temp = np.zeros_like(height_map)
                temp[mask] = emission_color[c] * emission_strength
                emissive_map[..., c] = temp
        
        # Convertir en 8-bit
        emissive_map = np.clip(emissive_map * 255, 0, 255).astype(np.uint8)
        
        return Image.fromarray(emissive_map)
    
    def _prepare_map_for_ml(self, map_data, map_type):
        """
        Prépare une map pour le traitement par le modèle ML
        
        Args:
            map_data: Map source (PIL.Image ou numpy.ndarray)
            map_type (str): Type de map (diffuse, normal, etc.)
            
        Returns:
            numpy.ndarray: Données préparées pour le modèle ML
        """
        # Convertir en numpy array si nécessaire
        if isinstance(map_data, Image.Image):
            map_data = np.array(map_data)
            
        # Normaliser à [0, 1]
        if map_data.dtype == np.uint8:
            map_data = map_data.astype(np.float32) / 255.0
            
        # Formater selon le modèle (ex: ajouter dimension de batch, normaliser, etc.)
        # Note: à adapter selon les spécifications exactes du modèle ML
        
        # Exemple simple: redimensionner à la taille attendue par le modèle
        expected_size = (256, 256)  # À adapter selon modèle
        if map_data.shape[:2] != expected_size:
            # Redimensionner tout en préservant le nombre de canaux
            channels = 1 if len(map_data.shape) == 2 else map_data.shape[2]
            resized = np.zeros((*expected_size, channels), dtype=np.float32)
            
            if channels == 1:
                resized[..., 0] = cv2.resize(map_data, expected_size)
            else:
                for c in range(channels):
                    resized[..., c] = cv2.resize(map_data[..., c], expected_size)
                    
            map_data = resized
            
        # Ajouter dimension batch (requis par la plupart des modèles)
        map_data = np.expand_dims(map_data, axis=0)
        
        return map_data
    
    def _process_ml_output(self, output_data, map_type):
        """
        Convertit la sortie du modèle ML en map utilisable
        
        Args:
            output_data (numpy.ndarray): Données de sortie du modèle ML
            map_type (str): Type de map (diffuse, normal, etc.)
            
        Returns:
            PIL.Image: Image résultante
        """
        # Retirer la dimension batch
        output_data = np.squeeze(output_data, axis=0)
        
        # Normaliser à [0, 255] et convertir en uint8
        output_data = np.clip(output_data * 255, 0, 255).astype(np.uint8)
        
        # Convertir en image PIL
        if output_data.ndim == 2:
            return Image.fromarray(output_data)
        else:
            return Image.fromarray(output_data)
    
    def _apply_snow_effect(self, pbr_maps):
        """
        Applique un effet de neige aux maps PBR
        
        Args:
            pbr_maps (dict): Maps PBR à modifier
            
        Returns:
            dict: Maps PBR modifiées
        """
        modified_maps = pbr_maps.copy()
        
        # Modifier la height map pour ajouter de la neige sur les surfaces supérieures
        height_map = np.array(pbr_maps[PBRMaps.HEIGHT])
        
        # Générer un masque pour les zones supérieures (où la neige s'accumulerait)
        # Simuler l'accumulation en utilisant un gradient vertical simple
        h, w = height_map.shape
        gradient = np.zeros_like(height_map)
        for y in range(h):
            gradient[y, :] = 1.0 - (y / h)  # Plus élevé au sommet
            
        # Combiner avec la height map pour déterminer où la neige s'accumule
        snow_mask = (gradient * 0.7 + height_map * 0.3) > 0.6
        
        # Modifier la diffuse map (blanchir les zones avec neige)
        diffuse_map = np.array(pbr_maps[PBRMaps.DIFFUSE])
        snow_color = np.array([240, 240, 250])  # Légèrement bleuté
        
        for y in range(h):
            for x in range(w):
                if snow_mask[y, x]:
                    # Mélanger avec la couleur de neige en fonction de l'intensité
                    blend = min(1.0, height_map[y, x] * 1.5)
                    diffuse_map[y, x] = diffuse_map[y, x] * (1 - blend) + snow_color * blend
        
        # Modifier la roughness map (neige fraîche = moins rugueuse)
        roughness_map = np.array(pbr_maps[PBRMaps.ROUGHNESS])
        for y in range(h):
            for x in range(w):
                if snow_mask[y, x]:
                    # Réduire la rugosité pour la neige
                    roughness_map[y, x] = max(0, roughness_map[y, x] - 100)
        
        # Mettre à jour les maps modifiées
        modified_maps[PBRMaps.DIFFUSE] = Image.fromarray(diffuse_map)
        modified_maps[PBRMaps.ROUGHNESS] = Image.fromarray(roughness_map)
        
        return modified_maps
    
    def _apply_sand_effect(self, pbr_maps):
        """
        Applique un effet de sable/désert aux maps PBR
        
        Args:
            pbr_maps (dict): Maps PBR à modifier
            
        Returns:
            dict: Maps PBR modifiées
        """
        modified_maps = pbr_maps.copy()
        
        # Modifier la diffuse map (teinte sable)
        diffuse_map = np.array(pbr_maps[PBRMaps.DIFFUSE])
        sand_color = np.array([220, 200, 140])  # Couleur sable
        
        # Teinter progressivement vers la couleur sable
        blend_factor = 0.7
        diffuse_map = diffuse_map * (1 - blend_factor) + sand_color * blend_factor
        
        # Ajouter des variations de texture de sable (grain)
        h, w, _ = diffuse_map.shape
        for y in range(h):
            for x in range(w):
                nx = x / w - 0.5
                ny = y / h - 0.5
                sand_noise = self.simplex_gen.noise2(nx * 20, ny * 20) * 15
                diffuse_map[y, x] = np.clip(diffuse_map[y, x] + sand_noise, 0, 255)
        
        # Modifier la roughness map (sable = plus rugueux)
        roughness_map = np.array(pbr_maps[PBRMaps.ROUGHNESS])
        roughness_map = np.clip(roughness_map + 40, 0, 255)  # Augmenter la rugosité
        
        # Mettre à jour les maps modifiées
        modified_maps[PBRMaps.DIFFUSE] = Image.fromarray(diffuse_map.astype(np.uint8))
        modified_maps[PBRMaps.ROUGHNESS] = Image.fromarray(roughness_map)
        
        return modified_maps
    
    def _apply_wet_effect(self, pbr_maps):
        """
        Applique un effet mouillé aux maps PBR
        
        Args:
            pbr_maps (dict): Maps PBR à modifier
            
        Returns:
            dict: Maps PBR modifiées
        """
        modified_maps = pbr_maps.copy()
        
        # Assombrir légèrement la diffuse map
        diffuse_map = np.array(pbr_maps[PBRMaps.DIFFUSE])
        diffuse_map = diffuse_map * 0.9  # Assombrir
        
        # Réduire la roughness (surfaces mouillées = plus lisses/réfléchissantes)
        roughness_map = np.array(pbr_maps[PBRMaps.ROUGHNESS])
        roughness_map = np.clip(roughness_map * 0.5, 0, 255)  # Réduire la rugosité
        
        # Ajouter des reflets spéculaires (zones plus lisses)
        h, w = roughness_map.shape
        for y in range(h):
            for x in range(w):
                nx = x / w - 0.5
                ny = y / h - 0.5
                wet_noise = self.simplex_gen.noise2(nx * 15, ny * 15)
                if wet_noise > 0.3:
                    # Surfaces encore plus lisses dans certaines zones (flaques)
                    roughness_map[y, x] = roughness_map[y, x] * 0.3
        
        # Mettre à jour les maps modifiées
        modified_maps[PBRMaps.DIFFUSE] = Image.fromarray(diffuse_map.astype(np.uint8))
        modified_maps[PBRMaps.ROUGHNESS] = Image.fromarray(roughness_map)
        
        return modified_maps
    
    def _apply_aging_effect(self, pbr_maps, age_factor):
        """
        Applique un effet de vieillissement aux maps PBR
        
        Args:
            pbr_maps (dict): Maps PBR à modifier
            age_factor (float): Facteur de vieillissement (0.0 = neuf, 1.0 = très vieux)
            
        Returns:
            dict: Maps PBR modifiées
        """
        modified_maps = pbr_maps.copy()
        
        # Récupérer les maps
        diffuse_map = np.array(pbr_maps[PBRMaps.DIFFUSE])
        roughness_map = np.array(pbr_maps[PBRMaps.ROUGHNESS])
        normal_map = np.array(pbr_maps[PBRMaps.NORMAL])
        
        # Assombrir et désaturer la diffuse map
        h, w, _ = diffuse_map.shape
        
        # Convertir en HSV pour ajuster la saturation
        hsv = color.rgb2hsv(diffuse_map)
        # Réduire la saturation
        hsv[..., 1] *= max(0.0, 1.0 - (age_factor * 0.5))
        # Réduire la luminosité
        hsv[..., 2] *= max(0.5, 1.0 - (age_factor * 0.3))
        # Reconvertir en RGB
        diffuse_map = color.hsv2rgb(hsv) * 255
        
        # Ajouter des taches/rayures selon le facteur d'âge
        if age_factor > 0.3:
            scratch_density = age_factor * 10  # Nombre de rayures
            for _ in range(int(scratch_density)):
                # Position et taille aléatoires
                start_x = random.randint(0, w-1)
                start_y = random.randint(0, h-1)
                length = random.randint(5, 30)
                width = random.randint(1, 3)
                angle = random.random() * math.pi * 2
                
                # Dessiner une rayure
                for i in range(length):
                    x = int(start_x + math.cos(angle) * i)
                    y = int(start_y + math.sin(angle) * i)
                    
                    if 0 <= x < w and 0 <= y < h:
                        # Rayon de la rayure
                        for dx in range(-width, width+1):
                            for dy in range(-width, width+1):
                                if dx*dx + dy*dy <= width*width:
                                    nx, ny = x + dx, y + dy
                                    if 0 <= nx < w and 0 <= ny < h:
                                        # Assombrir la diffuse map
                                        diffuse_map[ny, nx] = diffuse_map[ny, nx] * 0.7
                                        # Augmenter la rugosité
                                        roughness_map[ny, nx] = min(255, roughness_map[ny, nx] + 50)
                                        # Modifier légèrement les normales
                                        if random.random() > 0.5:
                                            normal_map[ny, nx, 0] = 128
                                            normal_map[ny, nx, 1] = 128
        
        # Augmenter la rugosité globale
        roughness_map = np.clip(roughness_map + (age_factor * 50), 0, 255)
        
        # Mettre à jour les maps modifiées
        modified_maps[PBRMaps.DIFFUSE] = Image.fromarray(diffuse_map.astype(np.uint8))
        modified_maps[PBRMaps.ROUGHNESS] = Image.fromarray(roughness_map)
        modified_maps[PBRMaps.NORMAL] = Image.fromarray(normal_map)
        
        return modified_maps
    
    def save_asset(self, asset, filepath, **kwargs):
        """
        Sauvegarde un asset généré (ensemble de maps PBR)
        
        Args:
            asset (dict): Maps PBR à sauvegarder
            filepath (str): Chemin de base pour la sauvegarde
            **kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        try:
            # S'assurer que le répertoire existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Déterminer le format de sauvegarde
            format = kwargs.get("format", "PNG")
            quality = kwargs.get("quality", 95)
            
            # Sauvegarder chaque map dans son sous-répertoire approprié
            saved_paths = {}
            
            for map_type, map_data in asset.items():
                # Déterminer le sous-répertoire
                if map_type in self.pbr_dirs:
                    map_dir = self.pbr_dirs[map_type]
                else:
                    map_dir = os.path.dirname(filepath)
                
                # Générer le nom de fichier
                filename = os.path.basename(filepath)
                if "." in filename:
                    base_name, ext = os.path.splitext(filename)
                    map_filename = f"{base_name}_{map_type}{ext}"
                else:
                    map_filename = f"{filename}_{map_type}.png"
                
                # Chemin complet pour cette map
                map_path = os.path.join(map_dir, map_filename)
                
                # Sauvegarder l'image
                if isinstance(map_data, np.ndarray):
                    image = Image.fromarray(map_data)
                else:
                    image = map_data
                
                image.save(map_path, format=format, quality=quality)
                saved_paths[map_type] = map_path
            
            # Enregistrer également un fichier de métadonnées
            metadata = {
                "maps": saved_paths,
                "type": "pbr_material",
                "generated_by": "hybrid_generator"
            }
            metadata_path = f"{filepath}_metadata.json"
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'asset PBR: {e}")
            return False

def main():
    """Test du générateur hybride"""
    import argparse
    import time
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Générateur d'assets hybride PBR")
    parser.add_argument("--output", "-o", default="./test_output/hybrid", help="Répertoire de sortie")
    parser.add_argument("--material", "-m", default="stone", 
                       choices=["stone", "wood", "metal", "fabric", "leather", "grass", "water", "snow", "sand"],
                       help="Type de matériau à générer")
    parser.add_argument("--size", "-s", default=512, type=int, help="Taille des textures (px)")
    parser.add_argument("--seed", type=int, help="Seed pour génération déterministe")
    parser.add_argument("--context", "-c", default=None, 
                       choices=["snow", "desert", "wet", None],
                       help="Contexte environnemental à appliquer")
    parser.add_argument("--age", "-a", default=0.0, type=float, 
                       help="Facteur de vieillissement (0.0-1.0)")
    parser.add_argument("--refinement", "-r", action="store_true", 
                       help="Activer le raffinement ML (si disponible)")
    
    args = parser.parse_args()
    
    # Créer le répertoire de sortie
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Initialisation du générateur hybride...")
    generator = HybridGenerator(str(output_dir))
    
    # Configurer les paramètres de génération
    params = {
        "material": args.material,
        "size": (args.size, args.size),
        "use_ml_refinement": args.refinement,
        "apply_context_rules": args.context is not None,
        "add_details": True,
        "add_micro_details": True,
    }
    
    if args.context:
        params["context"] = {"environment": args.context}
    
    if args.age > 0:
        params["context"] = params.get("context", {})
        params["context"]["age_factor"] = args.age
    
    # Générer l'asset
    print(f"Génération de texture {args.material} ({args.size}x{args.size})...")
    start_time = time.time()
    
    pbr_asset = generator.generate(
        f"test_{args.material}",
        params,
        seed=args.seed
    )
    
    generation_time = time.time() - start_time
    print(f"Génération terminée en {generation_time:.2f}s")
    
    # Sauvegarder l'asset
    asset_path = output_dir / f"{args.material}_texture"
    print(f"Sauvegarde dans {asset_path}...")
    
    generator.save_asset(pbr_asset, str(asset_path))
    print("Sauvegarde terminée!")
    
    # Afficher les statistiques
    print("Stats de génération:", generator.get_statistics())
    
    
if __name__ == "__main__":
    main() 