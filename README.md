# Nightfall Defenders

## Aperçu du Projet

Nightfall Defenders est un jeu de survie action-RPG avec des mécaniques de combat basées sur les trajectoires. Le jeu offre un mélange unique de gameplay basé sur un cycle jour/nuit où les joueurs explorent un monde ouvert pendant la journée et défendent leur ville contre des hordes de monstres la nuit.

## Caractéristiques Principales

- **Cycle Jour/Nuit**: Deux boucles de gameplay distinctes - exploration le jour, défense la nuit
- **Combat basé sur les Trajectoires**: Mécaniques de combat diversifiées via différents motifs de projectiles
- **Système de Progression de Personnage**: Développez votre personnage via plusieurs chemins de progression
- **Gestion de Ville**: Développez et améliorez une ville centrale qui fournit des services et peut être défendue
- **Système de Reliques**: Objets spéciaux qui modifient les capacités et les statistiques
- **Animation Organique**: Mouvements fluides et naturels basés sur l'intégration de Verlet
- **Système Psychologique des Ennemis**: Les ennemis réagissent différemment selon votre puissance

## Documentation

Une documentation complète est disponible dans le dossier `docs/` :

- [Introduction](docs/index.md) - Point d'entrée de la documentation
- [Structure du Projet](docs/STRUCTURE.md) - Organisation des fichiers et dossiers
- [Aspects Techniques](docs/TECHNICAL.md) - Architecture technique du projet
- [Document des Exigences](docs/PRD.md) - Spécifications détaillées du projet
- [Guide de Contribution](docs/CONTRIBUTING.md) - Comment contribuer au projet

### Documentation des Systèmes

- [Aperçu des Systèmes](docs/SYSTEMS.md) - Vue d'ensemble de tous les systèmes
- [Système de Combat](docs/systems/COMBAT.md) - Détails du système de combat basé sur les trajectoires
- [Cycle Jour/Nuit](docs/systems/DAY_NIGHT_CYCLE.md) - Fonctionnement du cycle jour/nuit
- [Psychologie des Ennemis](docs/systems/ENEMY_PSYCHOLOGY.md) - Système de réaction des ennemis

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/nightfall-defenders/nightfall-defenders.git
cd nightfall-defenders

# Installer les dépendances
pip install -r requirements.txt

# Lancer le jeu
python run_game.py
```

## Exigences Système

- Python 3.8 ou supérieur
- OpenGL 3.3 ou supérieur
- 4 Go de RAM minimum
- 2 Go d'espace disque

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Remerciements

- Inspiré par des jeux comme Rain World pour l'animation organique
- Utilise Panda3D comme moteur de rendu de base
- Développé par l'équipe Nightfall Defenders

![Nightfall Defenders](docs/images/game_banner.png)

## Roadmap

Le développement de Nightfall Defenders suit la roadmap définie dans notre [PRD](docs/PRD.md), qui inclut les phases suivantes:

1. Systèmes fondamentaux (moteur, contrôles, cycle jour/nuit)
2. Fondations de progression (arbre de compétences, classes)
3. Ville et monde (construction, exploration)
4. Progression avancée (spécialisation, fusion, reliques)
5. Polissage et expansion (tous les effets visuels, animations organiques)
6. Fonctionnalités avancées (psychologie des ennemis, difficulté adaptative)
7. Polissage final (optimisations, équilibrage)

