#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base Asset Generator for Nightfall Defenders
Provides the foundation for all asset generation classes
"""

import os
import json
import random
import time
from enum import Enum
from abc import ABC, abstractmethod

class AssetType(Enum):
    """Types d'assets que le système peut générer"""
    SPRITE_2D = "sprite_2d"  # Images 2D pour personnages, UI, etc.
    MODEL_3D = "model_3d"    # Modèles 3D pour objets, bâtiments, etc.
    TERRAIN = "terrain"      # Tiles de terrain (peut être 2D ou 3D)
    EFFECT = "effect"        # Effets visuels comme particules, sorts
    ANIMATION = "animation"  # Séquences d'animation
    SOUND = "sound"          # Effets sonores procéduraux (futur)

class AssetCategory(Enum):
    """Catégories d'assets pour l'organisation"""
    CHARACTER = "characters"
    ENVIRONMENT = "environment"
    BUILDING = "buildings"
    PROP = "props"
    UI = "ui"
    EFFECT = "effects"

class AssetGenerator(ABC):
    """Classe de base abstraite pour tous les générateurs d'assets"""
    
    def __init__(self, output_dir, metadata_dir=None):
        """
        Initialise le générateur d'assets
        
        Args:
            output_dir (str): Répertoire de sortie pour les assets générés
            metadata_dir (str, optional): Répertoire pour stocker les métadonnées des assets
        """
        self.output_dir = output_dir
        self.metadata_dir = metadata_dir or os.path.join(output_dir, "_metadata")
        
        # Créer les répertoires nécessaires
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Attributs pour le logging et le suivi
        self.generation_stats = {
            "assets_generated": 0,
            "generation_time": 0,
            "errors": 0
        }
        
        # Cache pour éviter de régénérer les mêmes assets (basé sur seed et paramètres)
        self.asset_cache = {}
    
    @abstractmethod
    def generate(self, asset_id, asset_params, seed=None):
        """
        Méthode abstraite pour générer un asset
        
        Args:
            asset_id (str): Identifiant unique pour l'asset
            asset_params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            object: L'asset généré (type dépend de l'implémentation)
        """
        pass
    
    def save_asset(self, asset, filepath, **kwargs):
        """
        Sauvegarde un asset généré
        
        Args:
            asset: L'asset à sauvegarder
            filepath (str): Chemin où sauvegarder l'asset
            **kwargs: Paramètres supplémentaires spécifiques au format
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer le répertoire parent s'il n'existe pas
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # La méthode de sauvegarde dépend du type d'asset
            # Les sous-classes doivent implémenter cette logique
            
            # Par défaut, on tente d'appeler une méthode save sur l'asset
            if hasattr(asset, 'save'):
                asset.save(filepath, **kwargs)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'asset: {e}")
            self.generation_stats["errors"] += 1
            return False
    
    def save_metadata(self, asset_id, metadata):
        """
        Sauvegarde les métadonnées d'un asset
        
        Args:
            asset_id (str): Identifiant de l'asset
            metadata (dict): Métadonnées à sauvegarder
        """
        try:
            metadata_file = os.path.join(self.metadata_dir, f"{asset_id}.json")
            
            # Ajouter un timestamp
            metadata["generated_at"] = time.time()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des métadonnées pour {asset_id}: {e}")
    
    def load_metadata(self, asset_id):
        """
        Charge les métadonnées d'un asset existant
        
        Args:
            asset_id (str): Identifiant de l'asset
            
        Returns:
            dict: Métadonnées de l'asset ou None si non trouvé
        """
        metadata_file = os.path.join(self.metadata_dir, f"{asset_id}.json")
        
        if not os.path.exists(metadata_file):
            return None
            
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des métadonnées pour {asset_id}: {e}")
            return None
    
    def generate_with_cache(self, asset_id, asset_params, seed=None):
        """
        Génère un asset avec mise en cache pour éviter les régénérations
        
        Args:
            asset_id (str): Identifiant de l'asset
            asset_params (dict): Paramètres pour la génération
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            object: L'asset généré (depuis le cache ou nouvellement généré)
        """
        # Créer une clé de cache basée sur l'ID et les paramètres
        cache_key = f"{asset_id}_{hash(str(asset_params))}_{seed}"
        
        # Vérifier si l'asset est déjà en cache
        if cache_key in self.asset_cache:
            return self.asset_cache[cache_key]
        
        # Mesurer le temps de génération
        start_time = time.time()
        
        # Générer l'asset
        asset = self.generate(asset_id, asset_params, seed)
        
        # Mettre à jour les statistiques
        generation_time = time.time() - start_time
        self.generation_stats["assets_generated"] += 1
        self.generation_stats["generation_time"] += generation_time
        
        # Mettre en cache l'asset généré
        self.asset_cache[cache_key] = asset
        
        return asset
    
    def get_statistics(self):
        """
        Retourne les statistiques de génération
        
        Returns:
            dict: Statistiques de génération
        """
        return self.generation_stats
    
    def clear_cache(self):
        """Vide le cache des assets générés"""
        self.asset_cache.clear() 