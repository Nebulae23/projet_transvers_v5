# Génération d'Assets pour Nightfall Defenders

Ce document décrit le système de génération d'assets procéduraux pour Nightfall Defenders, qui prend en charge à la fois les assets 2D et 3D.

## Architecture du système

Le système de génération d'assets utilise une architecture modulaire avec les composants suivants :

### Classes de base

- **`AssetGenerator`** : Classe abstraite de base pour tous les générateurs d'assets
- **`AssetType`** : Énumération définissant les différents types d'assets (SPRITE_2D, MODEL_3D, TERRAIN, EFFECT, etc.)
- **`AssetCategory`** : Énumération définissant les catégories d'assets (CHARACTER, ENVIRONMENT, BUILDING, PROP, UI, etc.)

### Générateurs spécifiques

- **`SpriteGenerator`** : Génère des sprites 2D pour personnages, UI et effets visuels 2D
- **`ModelGenerator`** : Génère des modèles 3D pour bâtiments, props et éléments du monde
- **`TerrainGenerator`** : Génère des tiles de terrain (peut produire à la fois des versions 2D et 3D)
- **`EffectGenerator`** : Génère des effets visuels (particules, animations)

### Système central

- **`AssetGeneratorSystem`** : Orchestrateur qui coordonne les différents générateurs et gère la génération globale

## Fonctionnement 

Le système utilise une approche de "génération sur demande" avec mise en cache pour optimiser les performances. Les étapes typiques sont :

1. Initialiser le système avec la configuration désirée
2. Demander la génération d'un asset spécifique par type et paramètres
3. Le système détermine le générateur approprié et lui délègue la création
4. L'asset est généré, mis en cache et sauvegardé sur disque

## Génération hybride 2D/3D

Le système est conçu pour supporter la génération hybride d'assets :

### Assets 2D

- Sprites de personnages et d'ennemis
- Éléments d'interface utilisateur
- Tiles de terrain en vue du dessus
- Effets visuels en 2D

Les assets 2D sont générés en utilisant des algorithmes procéduraux adaptés aux sprites, avec :
- Formes géométriques de base
- Palettes de couleurs cohérentes
- Détails procéduraux spécifiques à chaque type d'entité

### Assets 3D

- Modèles de bâtiments et structures
- Props et objets du monde
- Terrain en 3D
- Effets visuels volumétriques

Les assets 3D sont générés en utilisant :
- Construction de maillages procéduraux
- Paramètres aléatoires contrôlés (seed)
- Compatibilité avec le moteur de rendu Panda3D

### Stratégie de décision

Le système utilise une stratégie de décision pour choisir le type d'asset (2D ou 3D) en fonction de :

1. Le paramètre de configuration `asset_format_priorities` qui définit les priorités par catégorie
2. La disponibilité des générateurs pour le type d'asset spécifique
3. Les capacités de rendu détectées dans l'environnement d'exécution

En cas d'indisponibilité d'un générateur, le système utilise une stratégie de repli (`fallback_strategy`) qui peut être :
- `use_placeholder` : Utiliser un asset placeholder
- `use_alternative_format` : Tenter un autre format (ex: 2D si 3D non disponible)
- `skip` : Ignorer la génération de cet asset

## Configuration

Le système est hautement configurable via un fichier JSON qui définit :

- Les types d'assets à générer
- Les paramètres pour chaque type d'asset
- Le nombre de variations 
- Les priorités de format
- Les paramètres de qualité

Exemple de configuration :

```json
{
    "characters": {
        "class_types": ["warrior", "mage", "cleric", "ranger"],
        "variations_per_class": 2
    },
    "buildings": {
        "building_types": ["house", "shop", "temple"],
        "use_3d_models": true
    },
    "generation_settings": {
        "asset_format_priorities": {
            "characters": ["2d", "3d"],
            "buildings": ["3d", "2d"]
        }
    }
}
```

## Utilisation

Pour utiliser le système de génération d'assets, exécutez le script principal :

```bash
python generate_assets_v2.py --config config.json --seed 12345
```

Options disponibles :
- `--config` : Chemin vers le fichier de configuration JSON
- `--seed` : Seed pour la génération déterministe
- `--mode` : Mode de génération ("2d", "3d" ou "all")
- `--output` : Répertoire de sortie des assets

## Exemple de génération

Voici quelques exemples d'assets qui peuvent être générés :

### Personnage 2D (Guerrier)
- Sprite de base avec armure rouge
- Animations d'idle, marche et attaque
- Équipement procédural adapté à la classe

### Bâtiment 3D (Maison)
- Structure de base avec toit et murs
- Variations de style architectural
- Détails procéduraux comme fenêtres et portes

### Terrain hybride
- Tiles 2D pour les éléments de base (herbe, eau, sable)
- Modèles 3D pour les variations de hauteur et détails

## Extension du système

Le système est conçu pour être facilement extensible. Pour ajouter un nouveau générateur d'assets :

1. Créez une classe qui hérite de `AssetGenerator`
2. Implémentez la méthode `generate()`
3. Ajoutez votre générateur au système dans la méthode `_init_generators()` de `AssetGeneratorSystem`

## Dépendances

Le système utilise les bibliothèques suivantes :
- PIL/Pillow pour la génération d'images 2D
- Panda3D pour la génération et manipulation de modèles 3D
- NumPy pour les opérations mathématiques et génération de bruit
- Tqdm pour l'affichage de la progression 