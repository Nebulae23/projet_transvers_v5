#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de génération de matériaux PBR avec le système hybride
Ce script est un exemple d'utilisation du générateur hybride dans le système
principal de génération d'assets
"""

import os
import time
import argparse
from pathlib import Path

from src.tools.asset_generator.asset_generator_system import AssetGeneratorSystem
from src.tools.asset_generator.base_generator import AssetCategory, AssetType

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Génération de matériaux PBR pour Nightfall Defenders")
    parser.add_argument("--output", "-o", default="./src/assets/generated", help="Répertoire de sortie")
    parser.add_argument("--material", "-m", required=True, 
                        choices=["stone", "wood", "metal", "all"],
                        help="Type de matériau à générer (ou 'all' pour tous)")
    parser.add_argument("--contexts", "-c", nargs='+', default=[], 
                       choices=["snow", "desert", "wet"],
                       help="Contextes environnementaux à appliquer")
    parser.add_argument("--age", "-a", action="store_true", help="Générer des variations d'âge")
    parser.add_argument("--size", "-s", default=512, type=int, help="Taille des textures")
    parser.add_argument("--no-ml", action="store_true", help="Désactiver le raffinement ML")
    parser.add_argument("--seed", type=int, default=42, help="Seed pour la génération")
    parser.add_argument("--pack", "-p", action="store_true", help="Emballer les matériaux pour le jeu")
    
    args = parser.parse_args()
    
    # Créer le répertoire de sortie
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Initialisation du système de génération d'assets...")
    system = AssetGeneratorSystem(output_base_dir=str(output_dir))
    
    # Définir les matériaux à générer
    materials = []
    if args.material == "all":
        materials = ["stone", "wood", "metal"]
    else:
        materials = [args.material]
    
    # Suivi des temps de génération
    start_time = time.time()
    materials_generated = 0
    
    print(f"\n=== Génération des matériaux de base ===")
    for material in materials:
        print(f"Génération du matériau {material}...")
        asset, path = system.generate_pbr_material(
            material,
            f"{material}_base",
            size=(args.size, args.size),
            use_ml=not args.no_ml,
            seed=args.seed + hash(material) % 1000
        )
        
        if asset:
            materials_generated += 1
            print(f"  > Matériau {material} généré dans {path}\n")
    
    # Générer des variations environnementales
    if args.contexts:
        print(f"\n=== Génération des variations environnementales ===")
        for material in materials:
            for context in args.contexts:
                print(f"Génération de {material} avec contexte {context}...")
                asset, path = system.generate_pbr_material(
                    material,
                    f"{material}_{context}",
                    size=(args.size, args.size),
                    context=context,
                    use_ml=not args.no_ml,
                    seed=args.seed + hash(f"{material}_{context}") % 1000
                )
                
                if asset:
                    materials_generated += 1
                    print(f"  > Matériau {material} ({context}) généré dans {path}\n")
    
    # Générer des variations d'âge
    if args.age:
        print(f"\n=== Génération des variations d'âge ===")
        age_factors = [0.3, 0.7]
        
        for material in materials:
            for age_factor in age_factors:
                print(f"Génération de {material} avec facteur d'âge {age_factor}...")
                asset, path = system.generate_pbr_material(
                    material,
                    f"{material}_aged_{int(age_factor*100)}",
                    size=(args.size, args.size),
                    age_factor=age_factor,
                    use_ml=not args.no_ml,
                    seed=args.seed + hash(f"{material}_aged_{age_factor}") % 1000
                )
                
                if asset:
                    materials_generated += 1
                    print(f"  > Matériau {material} (âge {age_factor}) généré dans {path}\n")
    
    # Emballer les matériaux si demandé
    if args.pack:
        print(f"\n=== Préparation des matériaux pour le jeu ===")
        # Cette fonction dépendrait du pipeline spécifique du jeu
        # Par exemple, créer des fichiers de configuration, compresser des textures, etc.
        print("Fonctionnalité d'emballage à implémenter selon les besoins spécifiques du jeu")
    
    # Afficher les statistiques de génération
    total_time = time.time() - start_time
    print(f"\n=== Résumé de la génération ===")
    print(f"Matériaux générés: {materials_generated}")
    print(f"Temps total: {total_time:.2f}s")
    if materials_generated > 0:
        print(f"Temps moyen: {total_time/materials_generated:.2f}s par matériau")
    print(f"Statistiques du système: {system.generation_stats}")
    
    print(f"\nGénération terminée avec succès! Les matériaux sont disponibles dans {output_dir}/materials")

if __name__ == "__main__":
    main() 