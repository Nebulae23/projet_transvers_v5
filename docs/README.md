# Documentation du Projet Nightfall Defenders

Bienvenue dans la documentation du projet Nightfall Defenders. Ce document sert de point d'entrée pour comprendre l'architecture, les systèmes et les conventions du projet.

## Table des Matières

- **[PRD (Product Requirements Document)](prd.md)** : Définit les objectifs et les exigences fonctionnelles du jeu.
- **[Conception Système Globale](../nightfall_defenders_system_design.md)** : Vue d'ensemble de l'architecture logicielle.
- **Système de Combat**
    - **[Architecture](combat_system/architecture.md)** : Structure ECS, composants et flux de données du combat.
    - **[Capacités](combat_system/abilities.md)** : Description des capacités principales des classes.
    - **[Progression](combat_system/progression.md)** : Système d'XP et arbres d'amélioration.
    - **[Format des Données](combat_system/data_format.md)** : Exemples de JSON pour les capacités, effets, etc.
- **Graphismes Avancés**
    - **[PRD Graphismes](advanced_graphics_prd.md)** : Exigences spécifiques aux fonctionnalités graphiques avancées.
    - **[Conception Graphique](graphics_design.md)** : Détails sur le pipeline de rendu, shaders, effets.
    - **[Intégration Graphique](graphics_integration_design.md)** : Comment les systèmes graphiques interagissent avec le reste du moteur.
- **Améliorations Gameplay**
    - **[PRD Améliorations](improvements_prd.md)** : Exigences pour les nouvelles fonctionnalités de gameplay.
    - **[Conception Améliorations](improvements_design/improvements_system_design.md)** : Architecture des systèmes d'événements, météo, IA, etc.
- **Diagrammes**
    - [Diagramme de Classes Global](../nightfall_defenders_class_diagram.mermaid)
    - [Diagramme de Séquence Global](../nightfall_defenders_sequence_diagram.mermaid)
    - [Diagramme de Classes Graphismes](graphics_class_diagram.mermaid)
    - [Diagramme de Séquence Graphismes](graphics_sequence_diagram.mermaid)
    - [Diagramme de Classes Améliorations](improvements_design/improvements_class_diagram.mermaid)
    - [Diagramme de Séquence Améliorations](improvements_design/improvements_sequence_diagram.mermaid)

## Guide de Démarrage Rapide (Développement)

1.  **Cloner le Répertoire :**
    ```bash
    git clone <url_du_repository>
    cd projet_transvers_v5
    ```
2.  **Installer les Dépendances :** Assurez-vous d'avoir Python 3.x installé.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Lancer le Jeu :**
    ```bash
    python src/main.py
    ```
4.  **Explorer le Code :**
    - `src/engine/`: Contient les systèmes principaux du moteur (ECS, rendu, physique, etc.).
    - `src/engine/combat/`: Logique spécifique au système de combat.
    - `src/engine/progression/`: Gestion de l'XP et des améliorations.
    - `assets/`: Ressources du jeu (images, données JSON, etc.).
    - `docs/`: Toute la documentation.
    - `tests/`: Tests unitaires et d'intégration.
5.  **Consulter la Documentation :** Référez-vous aux fichiers Markdown listés ci-dessus pour des détails sur des systèmes spécifiques.