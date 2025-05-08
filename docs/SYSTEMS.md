# Systèmes de Jeu de Nightfall Defenders

Ce document offre un aperçu complet de tous les systèmes de jeu de Nightfall Defenders, leurs interactions et leurs implémentations.

## Aperçu des Systèmes

Nightfall Defenders est construit autour de plusieurs systèmes interconnectés qui forment une expérience de jeu cohérente. Chaque système est conçu pour fonctionner de manière autonome tout en s'intégrant harmonieusement avec les autres.

Voici une vue d'ensemble des principaux systèmes :

| Système | Description | Fichiers principaux |
|---------|-------------|---------------------|
| Cycle Jour/Nuit | Alterne entre phases d'exploration et de défense | `day_night_cycle.py` |
| Combat Basé sur les Trajectoires | Mécaniques de combat avec différents types de trajectoires | `ability_system.py`, `projectile.py` |
| Progression de Personnage | Arbre de compétences et évolution des capacités | `skill_tree.py`, `skill_definitions.py` |
| Gestion de Ville | Construction et amélioration de la ville centrale | `city_manager.py`, `city_buildings.py` |
| Système de Reliques | Objets spéciaux qui modifient les capacités | `relic_system.py` |
| Exploration de Monde Ouvert | Génération et exploration du monde | `world_integration.py`, `points_of_interest.py` |
| Animation Organique | Mouvements fluides et naturels | `verlet.py`, `cloth_system.py` |
| Psychologie des Ennemis | Réactions adaptatives des ennemis | `enemy_psychology.py` |
| Brouillard Nocturne | Mécanique de brouillard qui avance la nuit | `night_fog.py` |
| Difficulté Adaptative | Ajuste la difficulté selon les performances | `adaptive_difficulty.py` |
| Fusion d'Abilités | Combinaison de capacités | `fusion_recipe_manager.py` |
| Harmonisation | Amélioration des capacités existantes | `harmonization_manager.py` |

## Interactions entre les Systèmes

Les systèmes de Nightfall Defenders sont profondément interconnectés, créant un gameplay riche et cohérent :

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│                 │      │                  │      │                  │
│  Cycle Jour/Nuit├─────►│ Brouillard Nuit  ├─────►│ Psychologie des  │
│                 │      │                  │      │     Ennemis      │
└────────┬────────┘      └──────────────────┘      └──────────────────┘
         │                                                  ▲
         ▼                                                  │
┌─────────────────┐      ┌──────────────────┐      ┌────────┴─────────┐
│                 │      │                  │      │                  │
│    Gestion      ├─────►│   Progression    ├─────►│     Combat       │
│    de Ville     │      │  de Personnage   │      │                  │
└────────┬────────┘      └─────────┬────────┘      └────────┬─────────┘
         │                         │                         │
         │                         ▼                         │
         │               ┌──────────────────┐                │
         │               │                  │                │
         └──────────────►│     Reliques     │◄───────────────┘
                         │                  │
                         └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐      ┌──────────────────┐
                         │                  │      │                  │
                         │  Fusion d'Abilités◄─────┤  Harmonisation   │
                         │                  │      │                  │
                         └──────────────────┘      └──────────────────┘
```

## Descriptions Détaillées des Systèmes

### 1. Système de Cycle Jour/Nuit

Le cycle jour/nuit est le fondement du gameplay de Nightfall Defenders, alternant entre deux boucles de jeu distinctes.

**Implémentation :** `day_night_cycle.py`

**Caractéristiques principales :**
- Cycle complet de 20 minutes (configurable)
- Transitions visuelles fluides entre phases
- Modification de l'éclairage et des effets atmosphériques
- Influence sur les comportements des ennemis et les ressources

**Interactions clés :**
- Déclenche l'apparition du brouillard nocturne
- Modifie les taux d'apparition des ennemis
- Affecte les ressources disponibles

### 2. Système de Combat Basé sur les Trajectoires

Un système de combat unique basé sur différents types de trajectoires pour les projectiles et les capacités.

**Implémentation :** `ability_system.py`, `projectile.py`

**Caractéristiques principales :**
- Capacités primaires à base de physique
- Trajectoires secondaires prédéterminées avec randomisation
- Fusion et harmonisation des capacités
- Spécialisation des capacités

**Types de trajectoires :**
- Ligne droite (collision simple)
- Arc (influencé par la gravité)
- À tête chercheuse (différents degrés de suivi)
- Orbital (cercle autour du joueur avant lancement)
- Zigzag (motif en zigzag)
- Spirale (motif en spirale)
- Rebondissante (rebondit sur les surfaces)
- Aléatoire (points d'apparition randomisés)
- Onde (motifs sinusoïdaux)

### 3. Système de Progression de Personnage

Un système complet de progression avec arbres de compétences et amélioration des capacités.

**Implémentation :** `skill_tree.py`, `skill_definitions.py`

**Caractéristiques principales :**
- Arbre de compétences avec spécialisations multiples
- Progression basée sur les ressources des monstres
- Chemins de spécialisation exclusifs
- Nœuds de fusion qui relient les capacités

### 4. Système de Gestion de Ville

Système de construction et d'amélioration de la ville centrale qui sert de base au joueur.

**Implémentation :** `city_manager.py`, `city_buildings.py`, `city_automation.py`

**Caractéristiques principales :**
- Construction de districts spécialisés
- Bâtiments avec capacités uniques
- Automatisation de la production de ressources
- Systèmes de défense contre les attaques nocturnes

### 5. Système de Reliques

Objets spéciaux qui modifient profondément les capacités et les statistiques du joueur.

**Implémentation :** `relic_system.py`, `relic_ui.py`

**Caractéristiques principales :**
- Reliques avec effets uniques
- Synergies entre reliques
- Effets permanents et temporaires
- Potentiels inconvénients équilibrant les avantages

### 6. Système d'Exploration de Monde Ouvert

Génération et exploration d'un monde ouvert avec des points d'intérêt.

**Implémentation :** `world_integration.py`, `points_of_interest.py`

**Caractéristiques principales :**
- Monde généré avec zones fixes et aléatoires
- Points d'intérêt comme des coffres, des camps et des PNJ
- Quêtes et énigmes à découvrir
- Régénération des ressources

### 7. Système d'Animation Organique

Système d'animation basé sur la physique pour des mouvements fluides et naturels.

**Implémentation :** `verlet.py`, `cloth_system.py`

**Caractéristiques principales :**
- Animation basée sur l'intégration de Verlet
- Mouvements naturels et réalistes
- Réactions physiques aux environnements
- Contrôles précis des mouvements

### 8. Système Psychologique des Ennemis

Système qui fait réagir les ennemis différemment en fonction de la puissance relative du joueur.

**Implémentation :** `enemy_psychology.py`

**Caractéristiques principales :**
- États psychologiques multiples (normal, hésitant, effrayé, terrifié, soumis)
- Réactions basées sur la puissance relative du joueur
- Influence du groupe sur le comportement individuel
- Indicateurs visuels de l'état psychologique

### 9. Système de Brouillard Nocturne

Brouillard qui s'approche de la ville la nuit et sert de médium pour faire apparaître des monstres.

**Implémentation :** `night_fog.py`

**Caractéristiques principales :**
- Approche progressive vers la ville
- Effets de visibilité réduite
- Source d'apparition des ennemis
- Interactions avec les capacités du joueur

### 10. Système de Difficulté Adaptative

Ajuste dynamiquement la difficulté en fonction des performances du joueur.

**Implémentation :** `adaptive_difficulty.py`

**Caractéristiques principales :**
- Ajustement basé sur multiples métriques de performance
- Préréglages de difficulté (Facile, Normal, Difficile)
- Scaling des ennemis, des récompenses et du brouillard
- Fonctionnalités anti-frustration

### 11. Système de Fusion d'Abilités

Permet de combiner des capacités pour créer de nouvelles capacités hybrides.

**Implémentation :** `fusion_recipe_manager.py`, `fusion_ui.py`

**Caractéristiques principales :**
- Recettes de fusion spécifiques
- Nouvelles capacités avec effets uniques
- Interface visuelle pour les combinaisons possibles

**Exemples de fusion :**
- Feu + Glace = Vapeur (obscurcit la vision, dégâts sur la durée)
- Foudre + Mouvement = Téléportation
- Bouclier + Projectile = Barrière Réfléchissante

### 12. Système d'Harmonisation

Permet d'améliorer les capacités existantes avec des effets supplémentaires.

**Implémentation :** `harmonization_manager.py`, `harmonization_ui.py`

**Caractéristiques principales :**
- Amélioration des capacités sans les transformer complètement
- Effets visuels et mécaniques améliorés
- Complexité de gameplay accrue

**Exemples d'harmonisation :**
- Météore + Harmonisation = Multiples petits météores
- Laser + Harmonisation = Rayon continu avec dégâts croissants
- Nova de Feu + Harmonisation = Vagues de feu pulsantes

## Implémentation et Détails Techniques

Chaque système est implémenté de manière modulaire, avec des interfaces claires pour l'interaction avec d'autres systèmes. Cette architecture permet une maintenance facile et une extensibilité.

Pour des détails techniques plus approfondis sur chaque système, consultez les documents spécifiques dans le dossier `docs/systems/`.

## Évolution Future des Systèmes

Les systèmes de Nightfall Defenders sont conçus pour être extensibles. Des plans d'évolution future incluent :

- Système de météo dynamique affectant le gameplay
- Système social avec factions et réputation
- Système de commerce avancé entre villes
- Personnalisation approfondie des personnages
- Mode multijoueur coopératif 