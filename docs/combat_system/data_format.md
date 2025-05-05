# Format des Données du Système de Combat

Ce document décrit le format JSON utilisé pour définir les différentes données relatives au système de combat, telles que les capacités, les effets, les améliorations et les courbes de scaling.

## 1. `abilities.json` (Exemple)

Ce fichier définit les caractéristiques de base de chaque capacité disponible dans le jeu.

```json
{
  "abilities": [
    {
      "id": "AxeSlash",
      "name": "Coup de Hache",
      "description": "Une attaque de mêlée puissante avec une hache.",
      "class": "Warrior",
      "type": "MeleeAttack",
      "base_damage": 50,
      "cooldown": 2.5,
      "mana_cost": 0,
      "range": 3.0,
      "aoe_radius": 1.5,
      "aoe_angle": 90.0,
      "tags": ["physical", "melee", "cleave"],
      "visual_effect": "slash_effect",
      "sound_effect": "axe_swing_sfx",
      "upgrade_tree_id": "AxeSlash"
    },
    {
      "id": "MagicBolt",
      "name": "Éclair Magique",
      "description": "Lance un projectile magique.",
      "class": "Mage",
      "type": "Projectile",
      "base_damage": 40,
      "cooldown": 1.5,
      "mana_cost": 20,
      "range": 15.0,
      "projectile_speed": 20.0,
      "tags": ["magic", "ranged", "single_target"],
      "visual_effect": "magic_bolt_effect",
      "sound_effect": "magic_bolt_cast_sfx",
      "upgrade_tree_id": "MagicBolt"
    }
    // ... autres capacités
  ]
}
```

**Champs Clés :**
- `id`: Identifiant unique.
- `name`: Nom affiché.
- `description`: Description pour l'UI.
- `class`: Classe associée.
- `type`: Catégorie de la capacité (MeleeAttack, Projectile, Buff, Summon, etc.).
- `base_damage`: Dégâts de base (si applicable).
- `cooldown`: Temps de recharge en secondes.
- `mana_cost`: Coût en mana (si applicable).
- `range`: Portée de la capacité.
- `aoe_radius`, `aoe_angle`: Paramètres de zone d'effet (si applicable).
- `tags`: Mots-clés pour le système (filtrage, résistances, etc.).
- `visual_effect`, `sound_effect`: Identifiants pour les effets visuels et sonores.
- `upgrade_tree_id`: Lien vers l'arbre d'amélioration correspondant.

## 2. `effects.json` (Exemple)

Ce fichier définit les effets de statut (buffs, debuffs) qui peuvent être appliqués par les capacités ou d'autres systèmes.

```json
{
  "effects": [
    {
      "id": "stun",
      "name": "Étourdissement",
      "type": "Debuff",
      "duration_type": "Fixed", // Fixed, Scaled
      "base_duration": 1.0,
      "is_stackable": false,
      "max_stacks": 1,
      "behavior": {
        "prevents_action": true,
        "prevents_movement": true
      },
      "visual_indicator": "stun_stars_vfx",
      "tags": ["control", "debuff"]
    },
    {
      "id": "poison",
      "name": "Poison",
      "type": "Debuff",
      "duration_type": "Fixed",
      "base_duration": 3.0,
      "tick_rate": 1.0, // Dégâts par seconde
      "is_stackable": true,
      "max_stacks": 5,
      "behavior": {
        "damage_over_time": {
          "type": "poison",
          "base_dps": 5 // Dégâts par seconde par stack
        }
      },
      "visual_indicator": "poison_cloud_vfx",
      "tags": ["damage_over_time", "debuff"]
    }
    // ... autres effets
  ]
}
```

**Champs Clés :**
- `id`: Identifiant unique.
- `name`: Nom affiché.
- `type`: Buff ou Debuff.
- `duration_type`, `base_duration`: Gestion de la durée.
- `is_stackable`, `max_stacks`: Gestion du cumul.
- `behavior`: Définit l'impact de l'effet (empêche action, dégâts sur la durée, modifie stats, etc.).
- `visual_indicator`: Effet visuel sur l'entité affectée.
- `tags`: Mots-clés pour le système.

## 3. `upgrades.json` (Exemple - Structure Hypothetique)

Ce fichier (ou ensemble de fichiers par classe/capacité) définirait les nœuds d'amélioration disponibles dans les arbres.

```json
{
  "upgrade_trees": {
    "AxeSlash": {
      "ability_id": "AxeSlash",
      "nodes": [
        {
          "id": "axe_slash_damage_1",
          "name": "Increased Damage I",
          "description": "Increases AxeSlash damage by 10%.",
          "cost": 1, // Point de compétence
          "level_req": 1,
          "modifier": { "damage_multiplier": 1.10 },
          "prerequisites": [],
          "ui_position": { "x": 0, "y": 0 }
        },
        {
          "id": "axe_slash_arc",
          "name": "Wider Arc",
          "description": "Increases the area of effect of AxeSlash.",
          "cost": 1,
          "level_req": 3,
          "modifier": { "aoe_radius_multiplier": 1.25 },
          "prerequisites": ["axe_slash_damage_1"],
          "ui_position": { "x": 1, "y": 0 }
        }
        // ... autres nœuds
      ]
    }
    // ... autres arbres
  }
}
```
*Note : La structure réelle est définie en Python dans `src/engine/progression/ability/trees/`, mais ce JSON illustre le format des données sous-jacentes.*

**Champs Clés (similaires aux `UpgradeNode` Python) :**
- `id`, `name`, `description`, `cost`, `level_req`, `modifier`, `prerequisites`.
- `ui_position`: Coordonnées pour l'affichage dans l'interface de l'arbre.

## 4. `scaling.json` (Exemple)

Ce fichier définit comment certaines valeurs (dégâts, vie des ennemis, etc.) évoluent en fonction du niveau ou d'autres facteurs.

```json
{
  "scaling_curves": [
    {
      "id": "enemy_health_scaling",
      "type": "Exponential", // Linear, Polynomial, Exponential, CustomPoints
      "base_value": 100,
      "scale_factor": 1.2, // Pour exponentiel
      "input_variable": "enemy_level", // Variable utilisée pour le calcul (level, difficulty, etc.)
      "output_variable": "health"
    },
    {
      "id": "ability_damage_stat_scaling",
      "type": "Linear",
      "base_value": 0, // Les dégâts de base viennent de l'ability.json
      "scale_factor": 0.5, // 0.5 dégât par point de stat
      "input_variable": "relevant_stat", // e.g., Strength pour AxeSlash, Intelligence pour MagicBolt
      "output_variable": "bonus_damage"
    },
    {
      "id": "xp_requirement_scaling",
      "type": "CustomPoints",
      "points": [
        { "input": 1, "output": 100 },
        { "input": 2, "output": 150 },
        { "input": 3, "output": 225 },
        { "input": 4, "output": 337 }
        // ... jusqu'au niveau max
      ],
      "input_variable": "level",
      "output_variable": "xp_required"
    }
    // ... autres courbes
  ]
}
```

**Champs Clés :**
- `id`: Identifiant unique de la courbe.
- `type`: Type de formule de scaling.
- `base_value`, `scale_factor`: Paramètres de la formule.
- `points`: Liste de points définis pour `CustomPoints`.
- `input_variable`: La variable qui détermine la progression sur la courbe.
- `output_variable`: La valeur résultante calculée.