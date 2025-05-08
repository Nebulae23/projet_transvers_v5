#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Asset Generation Script (v2)
Système amélioré de génération d'assets qui supporte à la fois les assets 2D et 3D
"""

import os
import sys
import argparse
import time
import json
from tqdm import tqdm

def main():
    """Point d'entrée principal pour la génération d'assets v2"""
    parser = argparse.ArgumentParser(description="Nightfall Defenders Asset Generator v2")
    parser.add_argument("--seed", type=int, help="Seed pour la génération d'assets", default=None)
    parser.add_argument("--config", type=str, help="Fichier de configuration JSON", default=None)
    parser.add_argument("--mode", choices=["2d", "3d", "all"], help="Mode de génération", default="all")
    parser.add_argument("--output", type=str, help="Répertoire de sortie", default=None)
    args = parser.parse_args()
    
    print("=" * 60)
    print("Nightfall Defenders - Asset Generation v2")
    print("=" * 60)
    
    # Enregistrer l'heure de début
    start_time = time.time()
    
    # Déterminer le répertoire de sortie
    output_dir = args.output or os.path.join("src", "assets", "generated")
    os.makedirs(output_dir, exist_ok=True)
    
    # Charger la configuration
    config = load_config(args.config)
    if args.mode != "all":
        config = filter_config_by_mode(config, args.mode)
    
    # Afficher les informations
    seed = args.seed or int(time.time())
    print(f"Utilisation du seed: {seed}")
    print(f"Répertoire de sortie: {output_dir}")
    print(f"Mode de génération: {args.mode}")
    
    # Initialiser le système de génération d'assets
    try:
        from src.tools.asset_generator.asset_generator_system import generate_all_assets
        
        # Générer tous les assets
        stats = generate_all_assets(output_dir, config, seed)
        
        # Calculer la durée
        duration = time.time() - start_time
        
        # Afficher les résultats
        print()
        print(f"Génération d'assets terminée en {duration:.2f} secondes!")
        print(f"Total d'assets générés: {stats['total_assets']}")
        print(f"Erreurs: {stats['errors']}")
        print()
        print("Vous pouvez maintenant lancer le jeu avec: python run_game.py")
        
        return 0
    
    except ImportError as e:
        print(f"ERREUR: Impossible d'importer le système de génération d'assets: {e}")
        print("Assurez-vous que toutes les dépendances sont installées.")
        return 1
    
    except Exception as e:
        print(f"ERREUR: La génération d'assets a échoué: {e}")
        return 1

def load_config(config_file=None):
    """
    Charge la configuration pour la génération d'assets
    
    Args:
        config_file (str, optional): Chemin du fichier de configuration
        
    Returns:
        dict: Configuration chargée
    """
    # Configuration par défaut
    default_config = {
        "characters": {
            "class_types": ["warrior", "mage", "cleric", "alchemist", "ranger", "summoner"],
            "variations_per_class": 1,
            "animation_frames": {
                "idle": 4,
                "walk": 8,
                "attack": 6
            }
        },
        "terrain": {
            "terrain_types": ["grass", "forest", "mountain", "water", "desert", "snow"],
            "variations_per_type": 3
        },
        "props": {
            "prop_types": ["tree", "rock", "bush", "flower", "chest", "sign"],
            "variations_per_type": 2
        },
        "buildings": {
            "building_types": ["house", "shop", "temple", "tower", "wall", "gate"],
            "variations_per_type": 1
        },
        "ui": {
            "button_states": ["normal", "hover", "pressed", "disabled"],
            "panel_types": ["inventory", "character", "map", "options"],
            "icon_types": ["health", "mana", "stamina", "attack", "defense", "speed"]
        },
        "effects": {
            "effect_types": ["fire", "water", "lightning", "magic", "healing"],
            "variations_per_type": 2
        }
    }
    
    # Si un fichier de configuration est spécifié, le charger
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                
            # Fusionner avec la configuration par défaut
            for key, value in custom_config.items():
                default_config[key] = value
                
            print(f"Configuration chargée depuis {config_file}")
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            print("Utilisation de la configuration par défaut")
    
    return default_config

def filter_config_by_mode(config, mode):
    """
    Filtre la configuration selon le mode de génération
    
    Args:
        config (dict): Configuration complète
        mode (str): Mode de génération ('2d' ou '3d')
        
    Returns:
        dict: Configuration filtrée
    """
    filtered_config = {}
    
    if mode == "2d":
        # Conserver seulement les éléments 2D
        for key in ["characters", "terrain", "ui"]:
            if key in config:
                filtered_config[key] = config[key]
    
    elif mode == "3d":
        # Conserver seulement les éléments 3D
        for key in ["props", "buildings", "effects"]:
            if key in config:
                filtered_config[key] = config[key]
    
    return filtered_config

if __name__ == "__main__":
    sys.exit(main()) 