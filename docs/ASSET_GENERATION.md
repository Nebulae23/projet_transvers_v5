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

## Générateur Hybride PBR

Le système d'asset generation de Nightfall Defenders inclut maintenant un générateur hybride qui combine techniques procédurales avancées, rendu PBR (Physically Based Rendering) et raffinement par machine learning pour créer des textures et matériaux réalistes.

### Principe du générateur hybride

Le générateur hybride fonctionne en trois phases principales :

1. **Génération procédurale avancée** : Utilisation d'algorithmes de bruit sophistiqués (Simplex, Worley, fractals) pour créer les structures de base.

2. **Pipeline PBR complet** : Génération automatique de maps PBR cohérentes (diffuse, normal, roughness, metallic, AO, height) depuis une base procédurale.

3. **Raffinement par machine learning** : Application optionnelle d'un modèle ML léger pour améliorer le réalisme des textures générées.

### Types de matériaux supportés

Le générateur hybride prend en charge différents types de matériaux avec des préréglages spécifiques :

- **Stone** (pierre) : Surfaces rocheuses avec variations de hauteur significatives
- **Wood** (bois) : Grain de bois directionnel et texture organique
- **Metal** (métal) : Surfaces lisses avec réflexion élevée
- **Fabric** (tissu) : Textures tissées avec microdétails
- **Leather** (cuir) : Texture avec imperfections de surface naturelles

### Maps PBR générées

Pour chaque matériau, le générateur produit les maps suivantes :

- **Diffuse/Albedo** : Couleur de base du matériau
- **Normal** : Détails de surface (bosses, rainures)
- **Roughness** : Rugosité de la surface (brillant vs. mat)
- **Metallic** : Propriétés métalliques de la surface
- **Ambient Occlusion** : Ombres subtiles dans les crevasses
- **Height** : Déplacements de géométrie (utilisée pour le parallax mapping ou le displacement)
- **Emissive** (facultatif) : Zones auto-illuminées

### Système de règles contextuelles

Un aspect unique du générateur hybride est sa capacité à adapter les matériaux au contexte environnemental :

- **Environnements** : Adaptation automatique aux environnements neige, désert, ou zones humides
- **Vieillissement** : Simulation de l'usure, patine, et détérioration avec le temps
- **Position spatiale** : Adaptation aux caractéristiques topographiques (ex: mousse au nord)

### Paramètres de configuration

Les paramètres du générateur hybride sont configurés dans `src/assets/configs/asset_generation_config.json` dans la section `pbr_materials` :

```json
"pbr_materials": {
    "material_types": ["stone", "wood", "metal", "fabric", "leather", "grass", "water", "snow", "sand"],
    "base_size": 512,
    "maps": ["diffuse", "normal", "roughness", "metallic", "ambient_occlusion", "height", "emissive"],
    "noise_types": ["perlin", "simplex", "worley", "fractal", "curl"],
    "presets": {
        "stone": {
            "noise_type": "fractal",
            "noise_scale": 0.1,
            "octaves": 6,
            "persistence": 0.5,
            "lacunarity": 2.0,
            "base_color": [0.7, 0.7, 0.7],
            "color_variation": 0.2,
            "roughness_base": 0.7,
            "metallic_base": 0.0,
            "height_scale": 1.0
        },
        // Autres préréglages...
    }
}
```

### Utilisation du générateur hybride

Il existe plusieurs façons d'utiliser le générateur hybride :

1. **Utilisation directe** :

```python
from src.tools.asset_generator.hybrid_generator import HybridGenerator

generator = HybridGenerator("./output_dir")
material = generator.generate(
    "stone_wall", 
    {
        "material": "stone",
        "size": (512, 512),
        "context": {"environment": "snow", "age_factor": 0.5}
    },
    seed=42
)
generator.save_asset(material, "./output_dir/stone_wall")
```

2. **Via le système de génération** :

```python
from src.tools.asset_generator.asset_generator_system import AssetGeneratorSystem

system = AssetGeneratorSystem()
asset, path = system.generate_pbr_material(
    "stone",
    "stone_wall",
    context="snow",
    age_factor=0.5,
    seed=42
)
```

3. **Via le script de ligne de commande** :

```bash
python generate_hybrid_materials.py --material stone --contexts snow --age --size 1024
```

### Génération de lots

Pour générer des séries de matériaux liés, utilisez le script de test :

```bash
python test_hybrid_generator.py --materials stone wood metal --contexts snow desert wet --age
```

### Exemple du pipeline

Pour une texture de pierre avec de la neige :

1. Génération de la heightmap de base avec du bruit fractal
2. Création de la normal map à partir de la heightmap
3. Création de la diffuse map avec variation de couleur selon la heightmap
4. Génération des maps roughness, metallic et AO
5. Application du contexte "neige" sur les zones supérieures
6. Application optionnelle du raffinement ML

### Intégration avec le pipeline 3D

Les textures générées peuvent être utilisées avec la plupart des moteurs 3D, y compris Panda3D. Pour intégrer les matériaux PBR dans Panda3D, vous pouvez utiliser l'exemple suivant :

```python
from panda3d.core import TextureStage, Texture, SamplerState
from panda3d.core import Material

# Charger les maps PBR
diffuse_tex = loader.loadTexture("materials/stone/stone_diffuse.png")
normal_tex = loader.loadTexture("materials/stone/stone_normal.png")
roughness_tex = loader.loadTexture("materials/stone/stone_roughness.png")
metallic_tex = loader.loadTexture("materials/stone/stone_metallic.png")

# Configurer le matériau
material = Material()
material.setName("stone_material")
material.setDiffuse((1, 1, 1, 1))
material.setSpecular((1, 1, 1, 1))
material.setShininess(10)

# Appliquer les textures au modèle
model = loader.loadModel("models/wall.egg")
model.setMaterial(material)

# Diffuse map (base color)
ts_diffuse = TextureStage("diffuse")
ts_diffuse.setMode(TextureStage.MModulate)
model.setTexture(ts_diffuse, diffuse_tex)

# Normal map
ts_normal = TextureStage("normal")
ts_normal.setMode(TextureStage.MNormal)
model.setTexture(ts_normal, normal_tex)

# Roughness map
ts_rough = TextureStage("roughness")
ts_rough.setMode(TextureStage.MSelector)
model.setTexture(ts_rough, roughness_tex)

# Metallic map
ts_metal = TextureStage("metallic")
ts_metal.setMode(TextureStage.MSelector)
model.setTexture(ts_metal, metallic_tex)
```

## Conclusion

Le système de génération d'assets de Nightfall Defenders offre une solution complète et flexible pour générer tous les types d'assets nécessaires au jeu. En combinant des approches 2D et 3D, et maintenant avec le générateur hybride PBR, le système permet de créer rapidement un grand nombre d'assets cohérents et détaillés. 