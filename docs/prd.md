# Product Requirements Document (PRD)

Ce document présente les spécifications détaillées du projet Nightfall Defenders, incluant l'architecture technique, la feuille de route de développement, les risques anticipés et les détails d'implémentation des différents systèmes.

## Vue d'Ensemble

"Nightfall Defenders" est un action-RPG de survie avec des mécaniques de combat basées sur les trajectoires. Le jeu offre un mélange unique de gameplay basé sur un cycle jour/nuit où les joueurs explorent un monde ouvert pendant la journée et défendent leur ville contre des hordes de monstres la nuit. Ce jeu s'adresse aux joueurs qui apprécient les systèmes de progression de personnage, la gestion stratégique des ressources et le combat basé sur les compétences.

## Fonctionnalités Principales

### Cycle Jour/Nuit
- **Ce que c'est** : Crée deux boucles de gameplay distinctes - exploration le jour, défense la nuit
- **Pourquoi c'est important** : Offre un rythme et des expériences de jeu variés
- **Comment ça fonctionne** : Cycles de 20 minutes avec changements visuels/environnementaux et un élément d'UI d'horloge

### Combat Basé sur les Trajectoires
- **Ce que c'est** : Offre des mécaniques de combat variées à travers différents modèles et comportements de projectiles
- **Pourquoi c'est important** : Crée un gameplay basé sur les compétences avec une haute rejouabilité
- **Comment ça fonctionne** : Capacités primaires basées sur la physique et chemins prédéterminés avec randomisation pour les capacités secondaires

### Système de Progression de Personnage
- **Ce que c'est** : Permet aux joueurs de développer leur personnage via plusieurs chemins de progression
- **Pourquoi c'est important** : Apporte de la profondeur et de la personnalisation au gameplay
- **Comment ça fonctionne** : Améliorations de statistiques basées sur le niveau, arbres de compétences débloqués via des ressources de monstres, chemins de spécialisation de capacités

### Gestion de Ville
- **Ce que c'est** : Les joueurs développent et améliorent une ville centrale qui fournit des services et peut être défendue la nuit
- **Pourquoi c'est important** : Crée un investissement dans une base centrale et une progression au-delà du développement du personnage
- **Comment ça fonctionne** : Système d'amélioration basé sur les districts avec des bâtiments spécialisés qui fournissent des buffs uniques

### Système de Reliques
- **Ce que c'est** : Fournit des objets spéciaux aléatoires qui modifient les capacités et les statistiques
- **Pourquoi c'est important** : Ajoute des éléments de type roguelike et de la diversité dans les builds
- **Comment ça fonctionne** : Récompenses de coffres nocturnes avec des effets d'activation permanents et des inconvénients potentiels

### Exploration du Monde Ouvert
- **Ce que c'est** : Fournit un monde expansif avec des points d'intérêt à découvrir
- **Pourquoi c'est important** : Encourage l'exploration et la découverte
- **Comment ça fonctionne** : Conception de monde ouvert avec coffres, camps, PNJ, quêtes et énigmes

### Système d'Animation Organique
- **Ce que c'est** : Crée des mouvements fluides et naturels pour les personnages et les ennemis
- **Pourquoi c'est important** : Offre une identité visuelle unique et un gameplay plus dynamique
- **Comment ça fonctionne** : Animation basée sur la physique similaire à Rain World utilisant l'intégration de Verlet

### Système de Résurrection
- **Ce que c'est** : Offre une seconde chance pendant les batailles nocturnes
- **Pourquoi c'est important** : Réduit la frustration tout en maintenant le défi
- **Comment ça fonctionne** : À la mort pendant la nuit, le joueur perd temporairement son équipement et ses reliques jusqu'à l'aube; limité à une fois par nuit (améliorable)

### Système Psychologique des Ennemis
- **Ce que c'est** : Les ennemis réagissent différemment selon le niveau de puissance du joueur
- **Pourquoi c'est important** : Fournit un feedback organique sur la progression
- **Comment ça fonctionne** : Les ennemis peuvent hésiter, fuir ou même prêter allégeance selon la différence de puissance relative

## Architecture Technique

### Composants du Système
- **Moteur de Rendu** : Moteur PyOpenGL personnalisé pour un éclairage et des effets de haute qualité
- **Système de Physique** : Physique verlet personnalisée pour les animations organiques
- **Système de Combat** : Module de calcul de trajectoire avec intégration physique
- **Système de Progression** : Arbres de compétences interconnectés avec avancement basé sur les nœuds
- **Gestion de Ville** : Placement de bâtiments sur grille avec système de connexion de ressources
- **IA Ennemie** : Machine à états avec réponse psychologique à la puissance du joueur
- **Génération de Monde** : Monde ouvert procédural avec points d'intérêt fixes
- **Système de Ressources** : Nœuds de ressources régénératifs avec taux de réapparition variés
- **Système de Résurrection** : Gestion d'état pour la perte temporaire d'équipement/reliques
- **Système de Classes** : Capacités, statistiques et chemins de progression spécifiques aux personnages
- **Interface de Menu Principal** : Système de menu interactif avec options et gestion des sauvegardes
- **Système de Sauvegarde** : Fonctionnalité de sauvegarde manuelle et automatique avec plusieurs emplacements

### Architecture du Moteur Panda3D Personnalisé
- **Pipeline de Rendu** :
  - Pipeline personnalisé basé sur les shaders pour effets d'éclairage avancés
  - Rendu différé pour de meilleures performances avec de nombreuses sources de lumière
  - Pile de post-traitement pour effets atmosphériques (brouillard, éblouissement, correction colorimétrique)
  - Techniques de rendu spécifiques aux pixels art avec mise à l'échelle de haute qualité
  - Support pour les ombres dynamiques qui évoluent avec le cycle jour/nuit

- **Composants de Base** :
  - Système de regroupement de sprites pour optimisation des performances
  - Système de particules avec intégration physique
  - Gestionnaire d'éclairage dynamique pour les transitions jour/nuit
  - Système de caméra avec suivi fluide et effets de tremblement d'écran
  - Graphe de scène pour rendu d'objets efficace et élimination
  - Gestion d'atlas de textures pour utilisation efficace de la mémoire GPU

- **Intégration Physique** :
  - Implémentation personnalisée de physique verlet pour l'animation organique
  - Détection de collision optimisée pour les environnements 2D en pixel art
  - Partitionnement spatial pour une interaction efficace des entités
  - Effets de particules basés sur la physique qui interagissent avec l'environnement
  - Simulation de trajectoire pour les capacités basées sur les projectiles

- **Fonctionnalités Graphiques** :
  - Éclairage en temps réel avec normal mapping pour la profondeur
  - Système de brouillard atmosphérique pour la phase nocturne
  - Effets de particules avec propriétés d'émission de lumière
  - Contours basés sur les shaders pour les objets interactifs
  - Correction colorimétrique dynamique pour les transitions d'ambiance
  - Occlusion ambiante en espace d'écran pour plus de profondeur

- **Optimisations de Performance** :
  - Élimination de frustum pour éviter le rendu d'objets hors écran
  - Système de niveau de détail pour les objets distants
  - Pooling d'objets pour les entités fréquemment créées/détruites
  - Multi-threading pour les calculs de physique
  - Instanciation GPU pour les objets similaires (arbres, herbe, etc.)
  - Compression de texture et génération de mipmap

### Modèles de Données
- **Données de Personnage** : Statistiques, objets équipés, capacités, progression de l'arbre de compétences
- **Données de Capacité** : Propriétés de base, chemins d'amélioration, options de spécialisation, effets visuels
- **Données d'Ennemi** : Types, comportements, tables de loot, seuils psychologiques
- **Données de Ville** : Districts, bâtiments, niveaux d'amélioration, taux de production de ressources
- **Données de Monde** : Terrain, ressources, points d'intérêt, emplacements de quêtes
- **Données de Relique** : Effets, raretés, représentations visuelles
- **Données de Ressource** : Types, taux de régénération, exigences de traitement
- **Données de Bâtiment** : Capacités de production, chemins d'amélioration, effets de buff
- **Données de Boss** : Modèles d'attaque, phases, capacités spéciales, récompenses
- **Données de Classe** : Statistiques de base, capacités uniques, options de spécialisation
- **Données d'Événement Aléatoire** : Déclencheurs, effets, durée et fréquence
- **Données de Sauvegarde** : Instantanés d'état de jeu, horodatages et métadonnées

### Exigences Techniques
- **Python** : Langage de programmation principal
- **PyOpenGL** : Interface graphique de bas niveau
- **NumPy** : Opérations mathématiques pour la physique et les trajectoires
- **Physique Personnalisée** : Intégration Verlet pour l'animation organique
- **Stockage de Données** : JSON/SQLite pour la persistance de l'état du jeu
- **Pipeline d'Assets** : Outils personnalisés pour la gestion des sprites et l'animation
- **Système de Shader** : Shaders GLSL personnalisés pour l'éclairage et les effets
- **Framework UI** : Système UI personnalisé pour les menus et les interfaces en jeu

## Feuille de Route de Développement

### Phase 1 : Systèmes de Base
- Moteur de rendu personnalisé avec éclairage de base
- Mouvement de personnage et collision
- Combat simple basé sur les trajectoires (capacité unique)
- Implémentation du cycle jour/nuit
- IA ennemie basique
- Art et son provisoires
- Implémentation du système de sauvegarde
- Interface de menu principal et options

### Phase 2 : Fondations de Progression
- Système de niveau de personnage
- Allocation de statistiques de base
- Arbre de compétences simple avec 2-3 capacités
- Système d'équipement avec objets basiques
- Mécaniques de collecte de ressources
- Mécanique de résurrection (version basique)
- Système de classes initial avec 2 classes de personnage

### Phase 3 : Ville et Monde
- Disposition de base de la ville et placement des bâtiments
- Gestion simple des ressources
- Conception initiale du monde ouvert avec zones d'exploration
- Boucle de gameplay d'exploration diurne
- Boucle de gameplay de défense nocturne
- Métriques de santé de la ville
- Mécaniques de régénération des ressources

### Phase 4 : Progression Avancée
- Implémentation complète de l'arbre de compétences
- Chemins de spécialisation des capacités
- Système de fusion de capacités
- Implémentation du système de reliques
- Types et comportements d'ennemis avancés
- Rencontres initiales de boss (motif unique)
- Système de classes élargi avec 4 classes de personnage

### Phase 5 : Polissage et Expansion
- Éclairage amélioré et effets visuels
- Système d'animation organique complet
- Gestion avancée de la ville avec tous les districts
- Monde ouvert complet avec tous les points d'intérêt
- Quêtes et services de PNJ
- Rencontres de boss et événements
- IA de boss complexe avec de multiples modèles
- Système de classes complet avec les 6 classes de personnage

### Phase 6 : Fonctionnalités Avancées
- Système psychologique des ennemis
- Système de difficulté adaptative
- Modes de défi de fin de jeu
- Système de prestige
- Classements
- Système d'événements aléatoires
- Automatisation avancée de la ville
- Arbre de progression post-niveau-maximum

### Phase 7 : Polissage Final
- Perfectionnement des effets visuels
- Optimisation des performances
- Système audio avancé avec éléments réactifs
- Système de tutoriel complet
- Options d'accessibilité
- Équilibrage de la difficulté
- Passe d'équilibrage final sur tous les systèmes

## Classes de Personnage

- **Guerrier** : Spécialiste de la mêlée avec défense élevée et capacités à courte portée
    **Capacité Principale** :
        - Coup de Hache
    **Capacités secondaires** :
    - À déterminer

- **Mage** : Spécialiste à distance avec capacités basées sur les éléments et faible défense
    **Capacité Principale** :
        - Projectile Magique
    **Capacités secondaires** :
    - À déterminer

- **Clerc** : Personnage de soutien avec capacités de guérison et défense moyenne
    **Capacité Principale** :
        - Coup de Masse
    **Capacités secondaires** :
    - À déterminer

- **Alchimiste** : Personnage polyvalent avec capacités basées sur les potions et utilité
    **Capacité Principale** :
        - Tourelles
    **Capacités secondaires** :
    - À déterminer

- **Rôdeur** : Infligeur de dégâts physiques à distance avec pièges et évasion
  **Capacité Principale** :
        - Tir Précis
    **Capacités secondaires** :
    - À déterminer

- **Invocateur** : Classe basée sur les familiers qui commande des alliés
  **Capacité Principale** :
        - Invocation d'Esprit
    **Capacités secondaires** :
        - À déterminer

## Détails d'Extension des Capacités

### Types de Capacités de Base
- Dégâts directs (projectiles, coups de mêlée, laser)
- Zone d'effet (explosions, vagues)
- Utilité (mouvement, buffs)
- Soutien (guérison, boucliers)

### Détails du Système de Trajectoires (Exemples)
- **Trajectoires Primaires Basées sur la Physique** :
  - Ligne droite : Projectiles basiques avec détection de collision
  - Arc : Projectiles affectés par la gravité
  - À tête chercheuse : Recherche des cibles avec différents degrés de suivi
  - Orbital : Projectiles qui tournent autour du joueur avant de se lancer

- **Trajectoires Secondaires Prédéterminées** (Exemples) :
  - Zigzag : Projectiles qui suivent un motif en zigzag
  - Spirale : Motif en spirale s'étendant vers l'extérieur
  - Rebondissant : Projectiles qui rebondissent sur les surfaces
  - Aléatoire : Projectiles avec des emplacements d'apparition aléatoires
  - Vague : Motifs d'onde sinusoïdale

### Système de Progression de l'Arbre de Compétences
- **Visibilité des Nœuds** :
  - Les joueurs ne peuvent voir que les nœuds directement connectés à ceux débloqués
  - Icônes point d'interrogation sur les nœuds jusqu'à ce que les prérequis soient remplis
  - Nœuds de fusion visibles comme des "liens de portail" spéciaux entre capacités
  - Descriptions de nœuds révélées uniquement lorsque les prérequis sont remplis
  - Connexions de chemin visibles même pour les nœuds verrouillés

- **Mécaniques de Déverrouillage** :
  - Ressources de monstres requises pour les déverrouillages de nœuds réguliers
  - Ressources spéciales pour les nœuds de fusion/spécialisation
  - Un déverrouillage de capacité possible par nuit basé sur les éliminations
  - Loot de ressources basé sur la probabilité des monstres
  - Impossible de revenir en arrière après les choix de spécialisation

### Exemples de Chemins de Spécialisation
- Boule de Feu → Météore (dégâts augmentés, zone)
- Boule de Feu → Laser (dégâts continus, précision)
- Boule de Feu → Nova de Feu (propagation à 360°)

### Exemples de Système de Fusion
- Feu + Glace = Vapeur (obscurcit la vision, dégâts sur la durée)
- Foudre + Mouvement = Téléportation
- Bouclier + Projectile = Barrière Réfléchissante

### Exemples d'Harmonisation
- Météore + Harmonisation = Multiples petits météores
- Laser + Harmonisation = Rayon soutenu avec dégâts croissants
- Nova de Feu + Harmonisation = Vagues de feu pulsantes

## Détails du Système de Ressources

### Types de Ressources
- **Basiques** : Bois, Pierre, Nourriture, Eau (régénération rapide)
- **Avancées** : Métal, Cristaux, Herbes (régénération moyenne)
- **Rares** : Essences Magiques, Artefacts Anciens (régénération lente/aucune)

### Nœuds de Ressources
- **Petits nœuds** : Ressources limitées qui se régénèrent (arbres, affleurements rocheux)
- **Grandes zones** : Ressources illimitées avec entretien plus élevé (forêts, montagnes) pour l'extraction de la ville
- **Nœuds spéciaux** : Ressources uniques qui apparaissent dans des conditions spécifiques

### Chaînes de Production
- **Traitement primaire** : Matières premières → Matériaux de base (rondins → planches)
- **Traitement secondaire** : Matériaux de base → Articles avancés (planches + métal → meubles)
- **Traitement avancé** : Matériaux combinés → Articles spécialisés (planches + cristaux → objets magiques)

## Système de Rencontres de Boss

### Boss Réguliers (Tous les 7 nuits)
- Trois boss potentiels par emplacement de rencontre avec un sélectionné aléatoirement
- Mise à l'échelle progressive de la difficulté avec la progression du joueur
- Modèles d'attaque et comportements uniques pour chaque boss
- Récompenses spéciales incluant des reliques rares et des matériaux d'artisanat

### Philosophie de Conception des Boss
- Attaques basées sur des modèles qui nécessitent la compétence du joueur pour les éviter
- Phases multiples avec des modèles d'attaque évolutifs
- Annonce visuelle des attaques à venir
- Interactions environnementales pendant les combats de boss

## Détails du Système de Résurrection

- Activation à la mort pendant la phase nocturne
- Le joueur conserve ses capacités mais perd temporairement son équipement et ses reliques
- Tous les objets sont restaurés à l'aube
- Limité à une fois par nuit par défaut
- Amélioration possible via le district du Temple dans la ville
- L'effet visuel indique l'état de résurrection
- Les ennemis peuvent réagir différemment au joueur ressuscité
- Pénalités de statistiques temporaires pendant l'état ressuscité

## Implémentation du Système Psychologique des Ennemis

### Niveaux de Confiance
- **Normal** : Comportement standard
- **Hésitant** : Pauses avant d'attaquer, peut se replier temporairement
- **Craintif** : Évite activement le joueur, n'attaque que lorsqu'il est acculé
- **Terrifié** : Fuit à vue, n'attaque jamais
- **Soumis** : Suit le joueur, attaque d'autres ennemis

### Calculs de Seuil
- Basés sur le niveau du joueur, la force de l'équipement et la puissance des capacités
- Différents types d'ennemis ont différentes valeurs de seuil
- Les ennemis de type boss ont des seuils plus élevés
- Influencés par la force de défense de la ville pendant la phase nocturne
- Ajustement dynamique basé sur le taux de réussite/échec du joueur

## Système d'Événements Aléatoires

### Types d'Événements
- **Positifs** : Bonus de ressources, buffs temporaires, PNJ amicaux
- **Négatifs** : "Maladie" (-25% de santé max), "Famine" (-75% de production de la ville)
- **Neutres** : Changements de temps, caravanes de marchands, ennemis errants

### Conditions de Déclenchement
- **Basées sur le temps** : Se produisent après un nombre spécifique de jours
- **Basées sur les conditions** : Déclenchées par les actions du joueur ou les états des ressources
- **Aléatoires** : Apparaissent avec une certaine probabilité chaque jour

## Système de Difficulté Adaptative

### Paramètres de Difficulté
- Paramètres de difficulté de base (Facile, Normal, Difficile)
- Chaque paramètre établit des paramètres de référence pour tous les systèmes
- Options de difficulté personnalisées pour les joueurs expérimentés

### Facteurs d'Ajustement Dynamique
- Taux de réussite du joueur dans les batailles nocturnes
- Statistiques de santé/dégâts de la ville
- Temps de complétion des boss
- Efficacité de la collecte de ressources
- Fréquence de mort du joueur
- Qualité et synergie des reliques

## Mécaniques du Brouillard Nocturne

### Comportement du Brouillard
- S'approche de la ville centrale à la tombée de la nuit
- Se déplace à vitesse variable selon la difficulté
- Crée des limitations de visibilité pour le joueur
- Sert de médium d'apparition pour les monstres nocturnes
- Endommage les sections de ville non protégées

### Progression du Brouillard
- Des vrilles initiales apparaissent aux bords de la carte
- S'épaissit et avance progressivement
- Recule à l'aube indépendamment du résultat de la bataille
- Devient plus dense et dangereux dans les phases avancées du jeu
- Des événements spéciaux peuvent causer un comportement inhabituel du brouillard

### Interaction du Joueur
- Les capacités peuvent temporairement dissiper ou repousser le brouillard
- Les améliorations de ville peuvent créer des barrières anti-brouillard ou des répulsifs
- L'équipement spécial fournit une résistance au brouillard ou une visibilité
- Certaines capacités exploitent le brouillard pour des effets améliorés
- Certains types d'ennemis se déplacent plus rapidement ou gagnent des pouvoirs dans le brouillard 