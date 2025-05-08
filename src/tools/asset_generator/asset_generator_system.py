#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Asset Generator System for Nightfall Defenders
Système intégré qui gère tous les types de génération d'assets
"""

import os
import sys
import random
import time
import json
from enum import Enum
from tqdm import tqdm

# Importer les classes de base
from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

# Importer les générateurs spécifiques
from src.tools.asset_generator.sprite_generator import SpriteGenerator, SpriteType, CharacterClass
from src.tools.asset_generator.model_generator import ModelGenerator, ModelType
from src.tools.asset_generator.terrain_generator import TerrainGenerator
from src.tools.asset_generator.effect_generator import EffectGenerator, EffectType
from src.tools.asset_generator.animation_generator import AnimationGenerator, AnimationType
from src.tools.asset_generator.ui_generator import UIGenerator
from src.tools.asset_generator.sound_generator import SoundGenerator, SoundType

# Importer le nouveau générateur hybride
from src.tools.asset_generator.hybrid_generator import HybridGenerator, MaterialPresets, PBRMaps

class AssetGeneratorSystem:
    """Système central de génération d'assets pour Nightfall Defenders"""
    
    def __init__(self, output_base_dir="./src/assets/generated", config=None):
        """
        Initialise le système de génération d'assets
        
        Args:
            output_base_dir (str): Répertoire de base pour les assets générés
            config (dict, optional): Configuration pour la génération
        """
        # Charger la configuration
        self.config = config or {}
        
        # Configurer les répertoires de sortie
        self.output_base_dir = output_base_dir
        self.output_dirs = {
            AssetCategory.CHARACTER: os.path.join(output_base_dir, "characters"),
            AssetCategory.ENVIRONMENT: os.path.join(output_base_dir, "environment"),
            AssetCategory.BUILDING: os.path.join(output_base_dir, "buildings"),
            AssetCategory.PROP: os.path.join(output_base_dir, "props"),
            AssetCategory.UI: os.path.join(output_base_dir, "ui"),
            AssetCategory.EFFECT: os.path.join(output_base_dir, "effects")
        }
        
        # Créer les répertoires de sortie
        for directory in self.output_dirs.values():
            os.makedirs(directory, exist_ok=True)
        
        # Initialiser les générateurs spécifiques
        self.generators = {}
        self._init_generators()
        
        # Statistiques
        self.generation_stats = {
            "total_assets_generated": 0,
            "total_generation_time": 0,
            "assets_by_category": {}
        }
        
    def _load_config(self, config_file=None):
        """
        Charge la configuration depuis un fichier JSON
        
        Args:
            config_file (str, optional): Chemin vers le fichier de configuration
            
        Returns:
            dict: Configuration chargée
        """
        if config_file is None:
            config_file = os.path.join("src", "assets", "configs", "asset_generation_config.json")
            
        if not os.path.exists(config_file):
            print(f"Fichier de configuration non trouvé: {config_file}")
            print("Utilisation de la configuration par défaut")
            return {}
            
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return {}
    
    def _init_generators(self):
        """Initialise les générateurs spécifiques pour chaque type d'asset"""
        try:
            # Générateur de sprites 2D
            sprite_output_dir = os.path.join(self.output_base_dir, "sprites")
            self.generators[AssetType.SPRITE_2D] = SpriteGenerator(sprite_output_dir)
            
            # Générateur de modèles 3D
            model_output_dir = os.path.join(self.output_base_dir, "models")
            self.generators[AssetType.MODEL_3D] = ModelGenerator(model_output_dir)
            
            # Générateur de terrain
            terrain_output_dir = os.path.join(self.output_base_dir, "terrain")
            self.generators[AssetType.TERRAIN] = TerrainGenerator(terrain_output_dir)
            
            # Générateur d'effets
            effect_output_dir = os.path.join(self.output_base_dir, "effects")
            self.generators[AssetType.EFFECT] = EffectGenerator(effect_output_dir)
            
            # Générateur d'animations
            animation_output_dir = os.path.join(self.output_base_dir, "animations")
            self.generators[AssetType.ANIMATION] = AnimationGenerator(animation_output_dir)
            
            # Générateur d'interface utilisateur
            ui_output_dir = os.path.join(self.output_base_dir, "ui")
            self.generators["ui"] = UIGenerator(ui_output_dir)
            
            # Générateur de sons
            sound_output_dir = os.path.join(self.output_base_dir, "..", "sounds")
            self.generators["sound"] = SoundGenerator(sound_output_dir)
            
            # Générateur hybride pour matériaux PBR
            hybrid_output_dir = os.path.join(self.output_base_dir, "materials")
            self.generators["pbr_material"] = HybridGenerator(hybrid_output_dir)
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation des générateurs: {e}")
    
    def generate_asset(self, asset_type, asset_category, asset_id, params=None, seed=None):
        """
        Génère un asset du type et de la catégorie spécifiés
        
        Args:
            asset_type (AssetType): Type d'asset à générer
            asset_category (AssetCategory): Catégorie de l'asset
            asset_id (str): Identifiant unique pour l'asset
            params (dict, optional): Paramètres spécifiques pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            tuple: (asset généré, chemin où il a été sauvegardé)
        """
        # Vérifier si le type d'asset est supporté
        if asset_type not in self.generators and asset_type != "pbr_material":
            print(f"Type d'asset non supporté: {asset_type}")
            return None, None
            
        # Préparer les paramètres
        if params is None:
            params = {}
            
        # Ajouter les paramètres de configuration généraux
        category_key = asset_category.value if hasattr(asset_category, 'value') else asset_category
        if category_key in self.config:
            params.update(self.config[category_key])
            
        # Chemin de sortie
        output_dir = self.output_dirs.get(asset_category, self.output_base_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Ensure file extension is present
        if not asset_id.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
            # Add .png as default extension for images
            output_path = os.path.join(output_dir, f"{asset_id}.png")
        else:
            output_path = os.path.join(output_dir, f"{asset_id}")
            
        # Mesurer le temps de génération
        start_time = time.time()
        
        # Générer l'asset
        if asset_type == "pbr_material":
            generator = self.generators["pbr_material"]
        else:
            generator = self.generators[asset_type]
            
        asset = generator.generate_with_cache(asset_id, params, seed)
        
        # Sauvegarder l'asset
        if asset:
            generator.save_asset(asset, output_path)
            
            # Sauvegarder les métadonnées
            metadata = params.copy()
            metadata.update({
                "asset_id": asset_id,
                "asset_type": asset_type.value if hasattr(asset_type, 'value') else asset_type,
                "asset_category": asset_category.value if hasattr(asset_category, 'value') else asset_category,
                "generated_at": time.time(),
                "seed": seed
            })
            
            generator.save_metadata(asset_id, metadata)
        
        # Mettre à jour les statistiques
        generation_time = time.time() - start_time
        self.generation_stats["total_assets_generated"] += 1
        self.generation_stats["total_generation_time"] += generation_time
        
        if category_key not in self.generation_stats["assets_by_category"]:
            self.generation_stats["assets_by_category"][category_key] = 0
        self.generation_stats["assets_by_category"][category_key] += 1
        
        return asset, output_path
    
    def generate_pbr_material(self, material_type, asset_id, size=(512, 512), context=None, age_factor=0.0, use_ml=True, seed=None):
        """
        Génère un matériau PBR en utilisant le générateur hybride
        
        Args:
            material_type (str): Type de matériau (stone, wood, metal, etc.)
            asset_id (str): Identifiant du matériau
            size (tuple): Dimensions des textures (largeur, hauteur)
            context (str, optional): Contexte environnemental (snow, desert, wet)
            age_factor (float): Facteur de vieillissement (0.0-1.0)
            use_ml (bool): Activer le raffinement ML
            seed (int, optional): Seed pour génération déterministe
            
        Returns:
            tuple: (maps PBR générées, répertoire où elles ont été sauvegardées)
        """
        params = {
            "material": material_type,
            "size": size,
            "use_ml_refinement": use_ml,
            "apply_context_rules": context is not None or age_factor > 0,
            "add_details": True,
            "add_micro_details": True,
        }
        
        # Ajouter les paramètres contextuels
        if context or age_factor > 0:
            params["context"] = {}
            
            if context:
                params["context"]["environment"] = context
                
            if age_factor > 0:
                params["context"]["age_factor"] = age_factor
        
        # Récupérer les préréglages du matériau depuis la configuration
        if "pbr_materials" in self.config and "presets" in self.config["pbr_materials"]:
            if material_type in self.config["pbr_materials"]["presets"]:
                material_preset = self.config["pbr_materials"]["presets"][material_type]
                params.update(material_preset)
        
        # Générer le matériau en utilisant la méthode generate_asset
        return self.generate_asset("pbr_material", "materials", asset_id, params, seed)
    
    def batch_generate(self, batch_config, output_dir=None):
        """
        Génère un lot d'assets selon une configuration de batch
        
        Args:
            batch_config (dict): Configuration pour la génération par lots
            output_dir (str, optional): Répertoire de sortie pour ce lot
            
        Returns:
            dict: Statistiques de génération
        """
        # Utiliser le répertoire spécifié ou le répertoire par défaut
        base_output_dir = output_dir or self.output_base_dir
        
        # Vérifier que la configuration de batch est valide
        if not isinstance(batch_config, dict) or not batch_config:
            print("Configuration de batch invalide ou vide")
            return {"error": "Configuration invalide", "assets_generated": 0}
        
        # Initialiser les statistiques du batch
        batch_stats = {
            "total_assets": 0,
            "successful_assets": 0,
            "failed_assets": 0,
            "generation_time": 0,
            "assets_by_category": {},
            "assets_by_type": {}
        }
        
        start_time = time.time()
        
        # Traiter chaque groupe d'assets dans la configuration
        for group_name, group_config in batch_config.items():
            print(f"Génération du groupe d'assets: {group_name}")
            
            # Extraire les paramètres communs du groupe
            asset_type = group_config.get("asset_type")
            asset_category = group_config.get("asset_category")
            base_params = group_config.get("base_params", {})
            variations = group_config.get("variations", [{}])
            count = group_config.get("count", 1)
            use_seed = group_config.get("use_seed", False)
            base_seed = group_config.get("base_seed", random.randint(0, 10000))
            
            # Vérifier les paramètres obligatoires
            if not asset_type or not asset_category:
                print(f"Configuration incomplète pour le groupe {group_name}, ignoré")
                continue
            
            # Créer un sous-répertoire pour ce groupe si spécifié
            group_output_dir = base_output_dir
            if group_config.get("create_subdir", False):
                group_output_dir = os.path.join(base_output_dir, group_name)
                os.makedirs(group_output_dir, exist_ok=True)
            
            # Générer les assets pour ce groupe
            successful_in_group = 0
            
            # Utiliser tqdm pour afficher une barre de progression
            with tqdm(total=count * len(variations), desc=f"Groupe {group_name}") as pbar:
                for i in range(count):
                    for v_idx, variation in enumerate(variations):
                        # Construire l'ID de l'asset
                        asset_id = f"{group_name}_{i}_{v_idx}" if len(variations) > 1 else f"{group_name}_{i}"
                        
                        # Combiner les paramètres de base avec la variation
                        params = base_params.copy()
                        params.update(variation)
                        
                        # Générer un seed déterministe si demandé
                        seed = None
                        if use_seed:
                            seed = base_seed + i * 100 + v_idx
                        
                        try:
                            # Générer l'asset
                            asset, path = self.generate_asset(
                                asset_type, 
                                asset_category, 
                                asset_id, 
                                params, 
                                seed
                            )
                            
                            if asset:
                                successful_in_group += 1
                                
                                # Mettre à jour les statistiques par catégorie
                                category_key = asset_category
                                if hasattr(asset_category, 'value'):
                                    category_key = asset_category.value
                                
                                if category_key not in batch_stats["assets_by_category"]:
                                    batch_stats["assets_by_category"][category_key] = 0
                                batch_stats["assets_by_category"][category_key] += 1
                                
                                # Mettre à jour les statistiques par type
                                type_key = asset_type
                                if hasattr(asset_type, 'value'):
                                    type_key = asset_type.value
                                
                                if type_key not in batch_stats["assets_by_type"]:
                                    batch_stats["assets_by_type"][type_key] = 0
                                batch_stats["assets_by_type"][type_key] += 1
                        
                        except Exception as e:
                            print(f"Erreur lors de la génération de {asset_id}: {e}")
                            batch_stats["failed_assets"] += 1
                        
                        # Mettre à jour la barre de progression
                        pbar.update(1)
            
            # Mettre à jour les statistiques du batch
            batch_stats["total_assets"] += count * len(variations)
            batch_stats["successful_assets"] += successful_in_group
            
            print(f"Génération du groupe {group_name} terminée: {successful_in_group}/{count * len(variations)} assets générés avec succès")
        
        # Calculer le temps total de génération
        batch_stats["generation_time"] = time.time() - start_time
        
        print(f"Génération du batch terminée en {batch_stats['generation_time']:.2f} secondes")
        print(f"Total: {batch_stats['successful_assets']}/{batch_stats['total_assets']} assets générés avec succès")
        
        return batch_stats

    def generate_all(self, seed=None):
        """
        Génère tous les assets selon la configuration
        
        Args:
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            dict: Statistiques de génération
        """
        if seed is not None:
            random.seed(seed)
        
        start_time = time.time()
        total_assets = 0
        errors = 0
        
        # Générer les personnages
        if "characters" in self.config:
            class_types = self.config["characters"].get("class_types", ["warrior", "mage"])
            variations = self.config["characters"].get("variations_per_class", 1)
            
            print(f"Génération de {len(class_types) * variations} personnages...")
            for class_type in tqdm(class_types):
                for i in range(variations):
                    params = {
                        "sprite_type": SpriteType.CHARACTER,
                        "class_type": class_type
                    }
                    
                    try:
                        asset_id = f"{class_type}_{i}"
                        asset, path = self.generate_asset(AssetType.SPRITE_2D, AssetCategory.CHARACTER, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération du personnage {class_type}_{i}: {e}")
                        errors += 1
        
        # Générer le terrain
        if "terrain" in self.config:
            terrain_types = self.config["terrain"].get("terrain_types", ["grass", "desert"])
            variations = self.config["terrain"].get("variations_per_type", 3)
            
            print(f"Génération de {len(terrain_types) * variations} terrains...")
            for terrain_type in tqdm(terrain_types):
                for i in range(variations):
                    params = {
                        "terrain_type": terrain_type
                    }
                    
                    try:
                        asset_id = f"{terrain_type}_{i}"
                        asset, path = self.generate_asset(AssetType.TERRAIN, AssetCategory.ENVIRONMENT, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération du terrain {terrain_type}_{i}: {e}")
                        errors += 1
        
        # Générer les bâtiments
        if "buildings" in self.config:
            building_types = self.config["buildings"].get("building_types", ["house", "tower"])
            variations = self.config["buildings"].get("variations_per_type", 1)
            
            print(f"Génération de {len(building_types) * variations} bâtiments...")
            for building_type in tqdm(building_types):
                for i in range(variations):
                    params = {
                        "model_type": ModelType.BUILDING,
                        "model_subtype": building_type
                    }
                    
                    try:
                        asset_id = f"{building_type}_{i}"
                        asset, path = self.generate_asset(AssetType.MODEL_3D, AssetCategory.BUILDING, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération du bâtiment {building_type}_{i}: {e}")
                        errors += 1
        
        # Générer les props
        if "props" in self.config:
            prop_types = self.config["props"].get("prop_types", ["tree", "rock"])
            variations = self.config["props"].get("variations_per_type", 2)
            
            print(f"Génération de {len(prop_types) * variations} props...")
            for prop_type in tqdm(prop_types):
                for i in range(variations):
                    params = {
                        "model_type": ModelType.PROP,
                        "model_subtype": prop_type
                    }
                    
                    try:
                        asset_id = f"{prop_type}_{i}"
                        asset, path = self.generate_asset(AssetType.MODEL_3D, AssetCategory.PROP, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération du prop {prop_type}_{i}: {e}")
                        errors += 1
        
        # Générer les éléments d'UI
        if "ui" in self.config:
            ui_types = self.config["ui"].get("panel_types", ["inventory", "character"])
            
            print(f"Génération de {len(ui_types)} éléments d'interface...")
            for ui_type in tqdm(ui_types):
                params = {
                    "sprite_type": SpriteType.UI_ELEMENT,
                    "ui_type": ui_type
                }
                
                try:
                    asset_id = f"{ui_type}"
                    asset, path = self.generate_asset(AssetType.SPRITE_2D, AssetCategory.UI, asset_id, params)
                    if asset:
                        total_assets += 1
                except Exception as e:
                    print(f"Erreur lors de la génération de l'UI {ui_type}: {e}")
                    errors += 1
        
        # Générer les effets
        if "effects" in self.config:
            effect_types = self.config["effects"].get("effect_types", ["fire", "water"])
            variations = self.config["effects"].get("variations_per_type", 2)
            
            print(f"Génération de {len(effect_types) * variations} effets...")
            for effect_type in tqdm(effect_types):
                for i in range(variations):
                    params = {
                        "effect_type": effect_type,
                        "intensity": random.uniform(0.8, 1.3),
                        "scale": random.uniform(0.9, 1.2)
                    }
                    
                    try:
                        asset_id = f"{effect_type}_{i}"
                        asset, path = self.generate_asset(AssetType.EFFECT, AssetCategory.EFFECT, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération de l'effet {effect_type}_{i}: {e}")
                        errors += 1
        
        # Générer les animations
        if "animations" in self.config:
            animation_types = self.config["animations"].get("animation_types", ["walk", "attack"])
            character_types = self.config["animations"].get("character_types", ["warrior", "mage"])
            
            print(f"Génération de {len(animation_types) * len(character_types)} animations...")
            for animation_type in tqdm(animation_types):
                for character_type in character_types:
                    params = {
                        "animation_type": animation_type,
                        "character_type": character_type
                    }
                    
                    try:
                        asset_id = f"{character_type}_{animation_type}"
                        asset, path = self.generate_asset(AssetType.ANIMATION, AssetCategory.CHARACTER, asset_id, params)
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération de l'animation {character_type}_{animation_type}: {e}")
                        errors += 1
        
        # Générer les matériaux PBR
        if "materials" in self.config:
            material_types = self.config["materials"].get("material_types", ["stone", "wood"])
            variations = self.config["materials"].get("variations_per_type", 2)
            
            print(f"Génération de {len(material_types) * variations} matériaux PBR...")
            for material_type in tqdm(material_types):
                for i in range(variations):
                    # Utiliser la méthode spécifique pour les matériaux PBR
                    try:
                        asset_id = f"{material_type}_{i}"
                        asset, path = self.generate_pbr_material(
                            material_type, 
                            asset_id,
                            size=(512, 512),
                            context=random.choice([None, "snow", "desert", "wet"]),
                            age_factor=random.uniform(0.0, 0.8)
                        )
                        if asset:
                            total_assets += 1
                    except Exception as e:
                        print(f"Erreur lors de la génération du matériau {material_type}_{i}: {e}")
                        errors += 1
        
        # Calculer le temps total
        total_time = time.time() - start_time
        
        # Préparer les statistiques
        stats = {
            "total_assets": total_assets,
            "errors": errors,
            "time_taken": total_time,
            "categories": self.generation_stats["assets_by_category"]
        }
        
        return stats

# Fonction utilitaire pour la génération d'assets
def generate_all_assets(base_dir, config, seed=None):
    """
    Fonction utilitaire pour générer tous les assets du jeu
    
    Args:
        base_dir (str): Répertoire de base pour les assets
        config (dict): Configuration de génération
        seed (int, optional): Seed pour la génération déterministe
        
    Returns:
        dict: Statistiques de génération
    """
    # Créer le générateur d'assets
    generator_system = AssetGeneratorSystem(base_dir, config)
    
    # Générer tous les assets
    stats = generator_system.generate_all(seed=seed)
    
    return stats 