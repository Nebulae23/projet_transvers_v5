# Structure du Projet Nightfall Defenders

Ce document décrit l'organisation des fichiers et dossiers du projet Nightfall Defenders, ainsi que leur rôle dans l'architecture générale du jeu.

## Aperçu de la Structure des Dossiers

```
projet_transvers_v5/
├── .vscode/                  # Configurations pour VS Code
├── cache/                    # Fichiers de cache temporaires
├── docs/                     # Documentation complète du projet
├── saves/                    # Sauvegardes de jeu
├── src/                      # Code source du jeu
│   ├── assets/               # Ressources du jeu (graphismes, sons, etc.)
│   ├── engine/               # Moteur de jeu personnalisé
│   ├── game/                 # Logique spécifique au jeu
│   ├── tests/                # Tests unitaires et d'intégration
│   └── tools/                # Outils de développement
├── uploads/                  # Fichiers téléchargés/générés
├── .gitattributes            # Configuration Git
├── .gitignore                # Fichiers ignorés par Git
├── .timeline.json            # Chronologie du développement
├── generate_assets.py        # Script de génération d'assets
├── requirements.txt          # Dépendances Python
├── run_*.bat                 # Scripts batch pour lancer différents tests
├── run_game.bat              # Script principal pour lancer le jeu
├── run_game.py               # Point d'entrée Python du jeu
├── test_env.py               # Configuration de l'environnement de test
└── test_import.py            # Test d'importation des modules
```

## Dossiers Principaux

### `/src` - Code Source

Le cœur du projet contenant tout le code source.

#### `/src/engine` - Moteur de Jeu

Implémentation personnalisée du moteur de jeu avec les composants suivants :

- **`__init__.py`** - Point d'entrée du module moteur
- **`config.py`** - Configuration du moteur
- **`entity.py`** - Système d'entités de base
- **`input_manager.py`** - Gestion des entrées utilisateur
- **`renderer.py`** - Système de rendu graphique
- **`resource_manager.py`** - Gestion des ressources (images, sons, etc.)
- **`save_manager.py`** - Système de sauvegarde/chargement
- **`scene_manager.py`** - Gestion des scènes et transitions

##### `/src/engine/physics` - Système de Physique

- **`__init__.py`** - Point d'entrée du module physique
- **`cloth_system.py`** - Système de simulation de tissu
- **`physics_manager.py`** - Gestionnaire principal des physiques
- **`verlet.py`** - Implémentation de l'intégration de Verlet pour animations organiques

##### `/src/engine/ui` - Interface Utilisateur

Composants pour la création d'interfaces utilisateur.

#### `/src/game` - Logique de Jeu

Contient toute la logique spécifique au jeu :

- **`__init__.py`** - Point d'entrée du module jeu
- **`ability_factory.py`** - Fabrique de capacités
- **`ability_system.py`** - Système de capacités
- **`adaptive_difficulty.py`** - Système de difficulté adaptative
- **`audio_manager.py`** - Gestion audio
- **`boss.py`** - Logique des boss
- **`boss_component.py`** - Composants des boss
- **`boss_factory.py`** - Fabrique de boss
- **`boss_patterns.py`** - Modèles d'attaque des boss
- **`building_system.py`** - Système de construction
- **`building_ui.py`** - Interface de construction
- **`camera_controller.py`** - Contrôleur de caméra
- **`challenge_mode.py`** - Mode défi
- **`character_class.py`** - Classes de personnage
- **`city_automation.py`** - Automatisation de la ville
- **`city_buildings.py`** - Bâtiments de la ville
- **`city_manager.py`** - Gestionnaire de ville
- **`class_selection_ui.py`** - Interface de sélection de classe
- **`crafting_bench.py`** - Établi d'artisanat
- **`crafting_system.py`** - Système d'artisanat
- **`crafting_ui.py`** - Interface d'artisanat
- **`day_night_cycle.py`** - Cycle jour/nuit
- **`difficulty_settings.py`** - Paramètres de difficulté
- **`enemy.py`** - Logique des ennemis
- **`enemy_healthbar.py`** - Barre de vie des ennemis
- **`enemy_psychology.py`** - Système psychologique des ennemis
- **`entity_manager.py`** - Gestionnaire d'entités
- **`fusion_recipe_manager.py`** - Gestionnaire de recettes de fusion
- **`fusion_ui.py`** - Interface de fusion
- **`harmonization_manager.py`** - Gestionnaire d'harmonisation
- **`harmonization_ui.py`** - Interface d'harmonisation
- **`main.py`** - Point d'entrée principal du jeu
- **`main_menu.py`** - Menu principal
- **`night_fog.py`** - Brouillard nocturne
- **`npc_system.py`** - Système de PNJ
- **`performance_tracker.py`** - Suivi des performances
- **`player.py`** - Logique du joueur
- **`points_of_interest.py`** - Points d'intérêt sur la carte
- **`projectile.py`** - Système de projectiles
- **`quest_system.py`** - Système de quêtes
- **`random_events.py`** - Événements aléatoires
- **`relic_system.py`** - Système de reliques
- **`relic_ui.py`** - Interface des reliques
- **`resource_drop.py`** - Drops de ressources
- **`resource_node.py`** - Nœuds de ressources
- **`secondary_abilities.py`** - Capacités secondaires
- **`skill_definitions.py`** - Définitions des compétences
- **`skill_tree.py`** - Arbre de compétences
- **`skill_tree_ui.py`** - Interface de l'arbre de compétences
- **`world_integration.py`** - Intégration du monde

#### `/src/assets` - Ressources

Contient toutes les ressources du jeu :

- **`configs/`** - Fichiers de configuration
- **`generated/`** - Assets générés
- **`shaders/`** - Shaders pour effets visuels
- **`sounds/`** - Effets sonores, musiques, etc.

#### `/src/tests` - Tests

Tests unitaires et d'intégration pour assurer la qualité du code.

#### `/src/tools` - Outils

Outils de développement et utilitaires.

### `/docs` - Documentation

Documentation complète du projet (ce que vous lisez actuellement).

### `/saves` - Sauvegardes

Contient les sauvegardes de jeu des utilisateurs.

### `/cache` - Cache

Fichiers temporaires pour améliorer les performances.

### `/uploads` - Téléchargements

Fichiers téléchargés ou générés par les utilisateurs.

## Fichiers Principaux

### Fichiers à la Racine

- **`generate_assets.py`** - Script pour générer des assets
- **`requirements.txt`** - Liste des dépendances Python
- **`run_game.py`** - Script principal pour lancer le jeu
- **`run_*.bat`** - Scripts batch pour exécuter différents tests ou configurations
- **`test_env.py`** - Configuration de l'environnement de test
- **`test_import.py`** - Test d'importation pour vérifier l'intégrité du projet

## Architecture du Code

Nightfall Defenders suit une architecture modulaire avec une séparation claire des préoccupations :

1. **Noyau du Moteur** (`/src/engine`) : Fournit les fonctionnalités de base indépendantes du jeu comme le rendu, la physique, la gestion des ressources, etc.

2. **Logique de Jeu** (`/src/game`) : Implémente les mécaniques et systèmes spécifiques au jeu.

3. **Ressources** (`/src/assets`) : Contient tous les actifs non-code nécessaires au jeu.

4. **Outils** (`/src/tools`) : Utilitaires de développement pour faciliter le processus de création.

Cette architecture permet une grande modularité et une maintenance plus facile. Chaque système peut être développé, testé et modifié de manière relativement indépendante des autres. 