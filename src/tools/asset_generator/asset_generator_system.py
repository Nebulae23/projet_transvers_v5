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
# Note: Nous les importerons de manière conditionnelle pour gérer les dépendances manquantes

class AssetGeneratorSystem:
    """Système central pour la génération d'assets"""
    
    def __init__(self, base_output_dir, config=None):
        """
        Initialise le système de génération d'assets
        
        Args:
            base_output_dir (str): Répertoire de base pour les assets générés
            config (dict, optional): Configuration du système
        """
        self.base_output_dir = base_output_dir
        self.config = config or {}
        
        # Créer les répertoires de base
        os.makedirs(base_output_dir, exist_ok=True)
        
        # Créer les sous-répertoires pour les différentes catégories
        for category in AssetCategory:
            os.makedirs(os.path.join(base_output_dir, category.value), exist_ok=True)
        
        # Initialiser les générateurs disponibles
        self.generators = {}
        self._init_generators()
        
        # Statistiques de génération
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_assets": 0,
            "errors": 0,
            "by_type": {}
        }
    
    def _init_generators(self):
        """Initialise les générateurs d'assets disponibles"""
        # Vérifier et initialiser le générateur de sprites 2D
        try:
            from src.tools.asset_generator.sprite_generator import SpriteGenerator
            sprite_dir = os.path.join(self.base_output_dir, AssetCategory.CHARACTER.value)
            self.generators[AssetType.SPRITE_2D] = SpriteGenerator(sprite_dir)
            print("Générateur de sprites 2D initialisé")
        except ImportError as e:
            print(f"Impossible d'initialiser le générateur de sprites 2D: {e}")
        
        # Vérifier et initialiser le générateur de modèles 3D
        try:
            from src.tools.asset_generator.model_generator import ModelGenerator
            model_dir = os.path.join(self.base_output_dir, AssetCategory.BUILDING.value)
            self.generators[AssetType.MODEL_3D] = ModelGenerator(model_dir)
            print("Générateur de modèles 3D initialisé")
        except ImportError as e:
            print(f"Impossible d'initialiser le générateur de modèles 3D: {e}")
        
        # Vérifier et initialiser le générateur de terrain
        try:
            from src.tools.asset_generator.terrain_generator import TerrainGenerator
            terrain_dir = os.path.join(self.base_output_dir, AssetCategory.ENVIRONMENT.value)
            self.generators[AssetType.TERRAIN] = TerrainGenerator(terrain_dir)
            print("Générateur de terrain initialisé")
        except ImportError as e:
            print(f"Impossible d'initialiser le générateur de terrain: {e}")
        
        # Vérifier et initialiser le générateur d'effets
        try:
            from src.tools.asset_generator.effect_generator import EffectGenerator
            effect_dir = os.path.join(self.base_output_dir, AssetCategory.EFFECT.value)
            self.generators[AssetType.EFFECT] = EffectGenerator(effect_dir)
            print("Générateur d'effets initialisé")
        except ImportError as e:
            print(f"Impossible d'initialiser le générateur d'effets: {e} (sera ajouté ultérieurement)")
    
    def get_generator(self, asset_type):
        """
        Récupère un générateur par type d'asset
        
        Args:
            asset_type (AssetType): Type d'asset à générer
            
        Returns:
            AssetGenerator or None: Le générateur approprié ou None si non disponible
        """
        return self.generators.get(asset_type)
    
    def generate_asset(self, asset_type, asset_id, params, seed=None):
        """
        Génère un asset spécifique
        
        Args:
            asset_type (AssetType): Type d'asset à générer
            asset_id (str): Identifiant unique pour l'asset
            params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            object: L'asset généré ou None si échec
        """
        generator = self.get_generator(asset_type)
        if not generator:
            print(f"Pas de générateur disponible pour {asset_type}")
            self.stats["errors"] += 1
            return None
        
        try:
            asset = generator.generate_with_cache(asset_id, params, seed)
            
            # Enregistrer des métadonnées pour l'asset
            metadata = {
                "asset_id": asset_id,
                "asset_type": asset_type.value,
                "params": params,
                "seed": seed
            }
            generator.save_metadata(asset_id, metadata)
            
            # Mettre à jour les statistiques
            self.stats["total_assets"] += 1
            self.stats["by_type"][asset_type.value] = self.stats["by_type"].get(asset_type.value, 0) + 1
            
            return asset
        except Exception as e:
            print(f"Erreur lors de la génération de l'asset {asset_id}: {e}")
            self.stats["errors"] += 1
            return None
    
    def save_asset(self, asset_type, asset, filepath, **kwargs):
        """
        Sauvegarde un asset généré
        
        Args:
            asset_type (AssetType): Type d'asset
            asset: L'asset à sauvegarder
            filepath (str): Chemin de destination
            **kwargs: Paramètres supplémentaires pour la sauvegarde
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        generator = self.get_generator(asset_type)
        if not generator:
            print(f"Pas de générateur disponible pour sauvegarder {asset_type}")
            return False
        
        return generator.save_asset(asset, filepath, **kwargs)
    
    def generate_all(self, config=None, seed=None):
        """
        Génère tous les assets définis dans la configuration
        
        Args:
            config (dict, optional): Configuration spécifique pour cette génération
            seed (int, optional): Seed de base pour la génération
            
        Returns:
            dict: Statistiques de génération
        """
        config = config or self.config
        if not config:
            print("Pas de configuration pour la génération d'assets")
            return self.stats
        
        self.stats["start_time"] = time.time()
        
        # Seed global pour la reproductibilité
        if seed is not None:
            random.seed(seed)
            master_seed = seed
        else:
            master_seed = random.randint(1, 10000)
            random.seed(master_seed)
        
        print(f"Génération d'assets avec le seed maître: {master_seed}")
        
        # Génération des personnages
        if "characters" in config:
            self._generate_characters(config["characters"], master_seed)
        
        # Génération du terrain
        if "terrain" in config:
            self._generate_terrain(config["terrain"], master_seed)
        
        # Génération des props
        if "props" in config:
            self._generate_props(config["props"], master_seed)
        
        # Génération des bâtiments
        if "buildings" in config:
            self._generate_buildings(config["buildings"], master_seed)
        
        # Génération de l'UI
        if "ui" in config:
            self._generate_ui(config["ui"], master_seed)
        
        # Génération des effets
        if "effects" in config:
            self._generate_effects(config["effects"], master_seed)
        
        self.stats["end_time"] = time.time()
        self.stats["duration"] = self.stats["end_time"] - self.stats["start_time"]
        
        print(f"Génération terminée en {self.stats['duration']:.2f} secondes")
        print(f"Total d'assets générés: {self.stats['total_assets']}")
        print(f"Erreurs: {self.stats['errors']}")
        
        return self.stats
    
    def _generate_characters(self, config, master_seed):
        """Génère les assets de personnages"""
        print("Génération des personnages...")
        
        generator = self.get_generator(AssetType.SPRITE_2D)
        if not generator:
            print("Générateur de sprites non disponible, génération de personnages ignorée")
            return
        
        # Générer pour chaque classe de personnage
        for class_type in tqdm(config.get("class_types", []), desc="Classes de personnage"):
            # Seed dérivé pour cette classe
            class_seed = master_seed + hash(class_type) % 10000
            
            # Paramètres de base pour cette classe
            params = {
                "class_type": class_type,
                "variations": config.get("variations_per_class", 1)
            }
            
            # Générer des sprites de base
            asset_id = f"character_{class_type}"
            asset = self.generate_asset(AssetType.SPRITE_2D, asset_id, params, class_seed)
            
            if asset:
                # Sauvegarder le sprite
                filepath = os.path.join(
                    self.base_output_dir, 
                    AssetCategory.CHARACTER.value, 
                    f"{class_type}_character.png"
                )
                self.save_asset(AssetType.SPRITE_2D, asset, filepath)
    
    def _generate_terrain(self, config, master_seed):
        """Génère les assets de terrain"""
        print("Génération du terrain...")
        
        generator = self.get_generator(AssetType.TERRAIN)
        if not generator:
            print("Générateur de terrain non disponible, génération de terrain ignorée")
            return
        
        # Générer pour chaque type de terrain
        for terrain_type in tqdm(config.get("terrain_types", []), desc="Types de terrain"):
            # Seed dérivé pour ce type de terrain
            terrain_seed = master_seed + hash(terrain_type) % 10000
            
            # Générer plusieurs variations
            for i in range(config.get("variations_per_type", 3)):
                # Paramètres pour cette variation
                params = {
                    "terrain_type": terrain_type,
                    "variation": i
                }
                
                # Générer le tile de terrain
                asset_id = f"terrain_{terrain_type}_{i+1}"
                asset = self.generate_asset(AssetType.TERRAIN, asset_id, params, terrain_seed + i)
                
                if asset:
                    # Sauvegarder le tile
                    filepath = os.path.join(
                        self.base_output_dir, 
                        AssetCategory.ENVIRONMENT.value,
                        terrain_type,
                        f"{terrain_type}_tile_{i+1}.png"
                    )
                    self.save_asset(AssetType.TERRAIN, asset, filepath)
    
    def _generate_props(self, config, master_seed):
        """Génère les assets de props"""
        print("Génération des props...")
        
        generator = self.get_generator(AssetType.MODEL_3D)
        if not generator:
            print("Générateur de modèles 3D non disponible, génération de props ignorée")
            return
        
        # Générer pour chaque type de prop
        for prop_type in tqdm(config.get("prop_types", []), desc="Types de props"):
            # Seed dérivé pour ce type de prop
            prop_seed = master_seed + hash(prop_type) % 10000
            
            # Générer plusieurs variations
            for i in range(config.get("variations_per_type", 2)):
                # Paramètres pour cette variation
                params = {
                    "model_type": "prop",
                    "prop_subtype": prop_type,
                    "variation": i
                }
                
                # Générer le modèle de prop
                asset_id = f"prop_{prop_type}_{i+1}"
                asset = self.generate_asset(AssetType.MODEL_3D, asset_id, params, prop_seed + i)
                
                if asset:
                    # Sauvegarder le modèle
                    filepath = os.path.join(
                        self.base_output_dir,
                        AssetCategory.PROP.value,
                        prop_type,
                        f"{prop_type}_{i+1}.bam"
                    )
                    self.save_asset(AssetType.MODEL_3D, asset, filepath)
    
    def _generate_buildings(self, config, master_seed):
        """Génère les assets de bâtiments"""
        print("Génération des bâtiments...")
        
        generator = self.get_generator(AssetType.MODEL_3D)
        if not generator:
            print("Générateur de modèles 3D non disponible, génération de bâtiments ignorée")
            return
        
        # Générer pour chaque type de bâtiment
        for building_type in tqdm(config.get("building_types", []), desc="Types de bâtiments"):
            # Seed dérivé pour ce type de bâtiment
            building_seed = master_seed + hash(building_type) % 10000
            
            # Générer plusieurs variations
            for i in range(config.get("variations_per_type", 1)):
                # Paramètres pour cette variation
                params = {
                    "model_type": "building",
                    "building_subtype": building_type,
                    "variation": i
                }
                
                # Générer le modèle de bâtiment
                asset_id = f"building_{building_type}_{i+1}"
                asset = self.generate_asset(AssetType.MODEL_3D, asset_id, params, building_seed + i)
                
                if asset:
                    # Sauvegarder le modèle
                    filepath = os.path.join(
                        self.base_output_dir,
                        AssetCategory.BUILDING.value,
                        building_type,
                        f"{building_type}_{i+1}.bam"
                    )
                    self.save_asset(AssetType.MODEL_3D, asset, filepath)
    
    def _generate_ui(self, config, master_seed):
        """Génère les assets d'interface utilisateur"""
        print("Génération des éléments d'UI...")
        # À implémenter
    
    def _generate_effects(self, config, master_seed):
        """Génère les assets d'effets visuels"""
        print("Génération des effets...")
        # À implémenter

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