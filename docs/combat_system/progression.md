# Progression du Personnage dans le Système de Combat

Ce document décrit le système d'expérience (XP) et les arbres d'amélioration des capacités qui régissent la progression du personnage liée au combat.

## Système d'Expérience (XP)

Le système d'XP permet aux personnages de monter de niveau et de devenir plus puissants au fur et à mesure de leur aventure.

### Acquisition d'XP
L'expérience est généralement acquise en :
- Vainquant des ennemis.
- Accomplissant des quêtes.
- Participant à des événements spéciaux.

### Montée de Niveau
- Chaque niveau requiert une quantité spécifique d'XP pour être atteint.
- La quantité d'XP nécessaire augmente de manière exponentielle à chaque niveau. La formule utilisée est approximativement `XP_requis = floor(100 * (1.5 ^ (niveau - 1)))`.
- Le niveau maximum actuel est fixé à 50.

### Récompenses de Niveau
À chaque montée de niveau, le personnage reçoit des récompenses :
- **Points de Statistique** (`stat_point_X`) : Utilisés pour augmenter les attributs de base (Force, Intelligence, etc.).
- **Points de Compétence** (`skill_point_X`) : Utilisés pour débloquer ou améliorer des capacités dans les arbres d'amélioration.
- **Récompenses Spéciales** (`special_reward_X`) : Des récompenses uniques (objets, accès à de nouvelles fonctionnalités, etc.) sont attribuées tous les 5 niveaux.

Le système notifie également les autres parties du jeu (comme l'UI) lorsqu'un personnage monte de niveau via un système de callbacks (`on_level_up`).

## Arbres d'Amélioration des Capacités

Chaque capacité principale associée à une classe de personnage possède son propre arbre d'amélioration, permettant une spécialisation et une personnalisation poussées.

### Structure d'un Arbre
- Un arbre est composé de plusieurs **Nœuds d'Amélioration** (`UpgradeNode`).
- Chaque nœud représente une amélioration spécifique pour la capacité (augmentation des dégâts, réduction du temps de recharge, ajout d'effets, etc.).
- **Attributs d'un Nœud :**
    - `id`: Identifiant unique du nœud.
    - `name`: Nom de l'amélioration (affiché dans l'UI).
    - `description`: Description de l'effet de l'amélioration.
    - `cost`: Coût en points de compétence pour débloquer le nœud.
    - `level_req`: Niveau minimum requis pour débloquer le nœud.
    - `modifier`: L'effet technique de l'amélioration (ex: `{"damage_multiplier": 1.10}`).
    - `prerequisites`: Liste des `id` d'autres nœuds qui doivent être débloqués au préalable.

### Fonctionnement
- Les joueurs dépensent les **Points de Compétence** (gagnés en montant de niveau) pour débloquer les nœuds dans les arbres des capacités qu'ils souhaitent améliorer.
- La structure des prérequis crée des chemins de progression, obligeant souvent à faire des choix stratégiques entre différentes branches d'amélioration.
- Les arbres sont organisés en **tiers**, avec des améliorations de plus en plus puissantes et coûteuses aux niveaux supérieurs.

### Arbres Disponibles
Les capacités principales suivantes possèdent actuellement un arbre d'amélioration défini :
- **Guerrier :** `AxeSlash`
- **Mage :** `MagicBolt`
- **Alchimiste :** `Turret`
- **Clerc :** `HolyLight` (potentiellement lié à `MaceHit`)
- **Rôdeur :** `Sniping`
- **Invocateur :** `SpiritSummon`