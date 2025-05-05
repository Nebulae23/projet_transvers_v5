# src/engine/quests/quest_generator.py
import json
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any

# --- Suppositions sur les structures de données existantes ---
# Si elles n'existent pas, elles devront être créées/ajustées
class QuestType(Enum):
    FETCH = auto()
    KILL = auto()
    ESCORT = auto()
    EXPLORE = auto()
    # Ajoutez d'autres types si nécessaire

@dataclass
class Objective:
    id: str
    description: str
    type: str # e.g., 'kill', 'fetch', 'reach'
    target: Any # e.g., 'Goblin', 'Sunpetal', 'Ancient Ruins'
    required_amount: int
    current_amount: int = 0
    # Potentiellement d'autres champs comme 'location'

@dataclass
class Reward:
    type: str # e.g., 'experience', 'gold', 'item'
    value: Any # Peut être un int (XP, gold) ou un str (item_id)
    amount: int = 1

@dataclass
class Quest:
    id: str
    title: str
    description: str
    type: QuestType
    objectives: List[Objective]
    rewards: List[Reward]
    status: str = "available" # e.g., available, active, completed, failed
    required_level: int = 1
    difficulty: int = 1
    is_daily: bool = False
    # Potentiellement: chain_quest_id: Optional[str] = None

# --- Fin des suppositions ---

@dataclass
class QuestTemplate:
    type: QuestType
    difficulty_range: Tuple[int, int]
    objective_count: Tuple[int, int]
    reward_multiplier: float
    required_level: int
    repeatable: bool
    chain_probability: float = 0.0
    possible_objectives: List[Dict[str, Any]] = field(default_factory=list)
    # Ajout possible : title_format: str, description_format: str

class QuestGenerator:
    def __init__(self, player_stats, world_state, templates_path="src/engine/quests/data/quest_templates.json"):
        self.player_stats = player_stats # Contient le niveau, etc.
        self.world_state = world_state # Contient l'état actuel du monde, NPCs, etc.
        self.templates: Dict[str, QuestTemplate] = {}
        self.templates_path = templates_path
        self.load_templates()

    def load_templates(self):
        """Charge les templates de quêtes depuis un fichier JSON."""
        try:
            with open(self.templates_path, 'r') as f:
                templates_data = json.load(f)
            for template_id, data in templates_data.items():
                try:
                    # Convertir le type string en QuestType Enum
                    quest_type_str = data.get("type", "").upper()
                    quest_type = QuestType[quest_type_str] if quest_type_str in QuestType.__members__ else None

                    if quest_type is None:
                        print(f"Warning: Invalid or missing quest type '{data.get('type')}' for template '{template_id}'. Skipping.")
                        continue

                    self.templates[template_id] = QuestTemplate(
                        type=quest_type,
                        difficulty_range=tuple(data.get("difficulty_range", [1, 1])),
                        objective_count=tuple(data.get("objective_count", [1, 1])),
                        reward_multiplier=data.get("reward_multiplier", 1.0),
                        required_level=data.get("required_level", 1),
                        repeatable=data.get("repeatable", False),
                        chain_probability=data.get("chain_probability", 0.0),
                        possible_objectives=data.get("possible_objectives", [])
                    )
                except KeyError as e:
                    print(f"Warning: Missing key {e} in template '{template_id}'. Skipping.")
                except Exception as e:
                    print(f"Error loading template '{template_id}': {e}")
            print(f"Loaded {len(self.templates)} quest templates.")
        except FileNotFoundError:
            print(f"Error: Quest templates file not found at {self.templates_path}")
            self.templates = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.templates_path}")
            self.templates = {}

    def _get_eligible_templates(self, min_level: int, max_level: int, allow_repeatable: bool = True) -> List[str]:
        """Retourne les IDs des templates éligibles pour le niveau donné."""
        eligible = []
        for template_id, template in self.templates.items():
            if template.required_level <= max_level:
                 # Pourrait être affiné avec une logique de difficulté/niveau max
                 if allow_repeatable or not template.repeatable: # Gérer la répétabilité
                     # Ici, on pourrait ajouter une vérification pour ne pas redonner
                     # une quête non répétable déjà complétée par le joueur
                     eligible.append(template_id)
        return eligible


    def generate_quest(self, template_id: Optional[str] = None, target_difficulty: Optional[int] = None) -> Optional[Quest]:
        """
        Génère une quête spécifique à partir d'un template ID ou une quête aléatoire
        adaptée au niveau du joueur si aucun ID n'est fourni.
        """
        if template_id and template_id not in self.templates:
            print(f"Error: Template ID '{template_id}' not found.")
            return None

        player_level = self.player_stats.get('level', 1) # Suppose que player_stats a 'level'

        if not template_id:
            # Choisir un template aléatoire éligible si aucun ID n'est donné
            eligible_templates = self._get_eligible_templates(player_level - 5, player_level + 2) # Exemple de plage de niveau
            if not eligible_templates:
                print("No eligible quest templates found for player level.")
                return None
            template_id = random.choice(eligible_templates)

        template = self.templates[template_id]

        # Vérifier le niveau requis
        if player_level < template.required_level:
            print(f"Player level {player_level} too low for quest '{template_id}' (requires {template.required_level}).")
            return None

        # Déterminer la difficulté réelle de la quête
        # Si non spécifiée, choisir aléatoirement dans la plage du template
        actual_difficulty = target_difficulty if target_difficulty is not None else random.randint(*template.difficulty_range)
        # On pourrait ici appeler une fonction de scaling externe si besoin
        # actual_difficulty = scale_difficulty(actual_difficulty, player_level, world_state)

        # Générer les objectifs
        objectives = self.generate_objectives(template, actual_difficulty)
        if not objectives:
            print(f"Failed to generate objectives for quest '{template_id}'.")
            return None

        # Calculer les récompenses
        rewards = self.calculate_rewards(template, actual_difficulty)

        # Créer l'instance de la quête
        quest_id = f"{template_id}_{random.randint(10000, 99999)}"
        # Utiliser des formats pour titre/description si définis dans le template
        title = f"{template.type.name.capitalize()} Quest: {template_id}" # Placeholder title
        description = f"Complete the objectives for this {template.type.name.lower()} quest." # Placeholder description

        quest = Quest(
            id=quest_id,
            title=title,
            description=description,
            type=template.type,
            objectives=objectives,
            rewards=rewards,
            required_level=template.required_level,
            difficulty=actual_difficulty
        )

        print(f"Generated quest '{quest.id}' (Difficulty: {quest.difficulty}) from template '{template_id}'.")
        return quest

    def generate_objectives(self, template: QuestTemplate, difficulty: int) -> List[Objective]:
        """Génère une liste d'objectifs basés sur le template et la difficulté."""
        objectives = []
        num_objectives_to_generate = random.randint(*template.objective_count)

        if not template.possible_objectives:
             # Gérer les types de quêtes sans objectifs prédéfinis (ex: Escort)
            if template.type == QuestType.ESCORT:
                 # Logique spécifique pour générer un objectif d'escorte
                 # Peut nécessiter des infos du world_state (NPC à escorter, destination)
                 npc_to_escort = self.world_state.find_random_npc_for_escort() # Supposition
                 destination = self.world_state.find_random_location() # Supposition
                 if npc_to_escort and destination:
                     obj_id = f"escort_{npc_to_escort.id}_{random.randint(100,999)}"
                     desc = f"Escort {npc_to_escort.name} to {destination.name}."
                     objectives.append(Objective(id=obj_id, description=desc, type="escort", target=npc_to_escort.id, required_amount=1))
                 else:
                     print("Warning: Could not generate ESCORT objective (no suitable NPC/destination).")
                     return [] # Échec si on ne peut pas générer l'objectif principal
            elif template.type == QuestType.EXPLORE:
                 # Logique pour EXPLORE
                 target_location = self.world_state.find_explorable_location(difficulty) # Supposition
                 if target_location:
                     obj_id = f"explore_{target_location.id}_{random.randint(100,999)}"
                     desc = f"Explore the {target_location.name}."
                     objectives.append(Objective(id=obj_id, description=desc, type="explore", target=target_location.id, required_amount=1))
                 else:
                     print("Warning: Could not generate EXPLORE objective (no suitable location).")
                     return []
            else:
                 print(f"Warning: No possible objectives defined for template type {template.type} and none generated.")
                 # Pourrait retourner une erreur ou un objectif générique par défaut
                 return [] # Retourne vide si aucun objectif ne peut être généré

        else:
            # Sélectionner parmi les objectifs possibles définis dans le template
            available_objectives = list(template.possible_objectives) # Copie pour pouvoir supprimer
            random.shuffle(available_objectives)

            for _ in range(num_objectives_to_generate):
                if not available_objectives:
                    break # Plus d'objectifs possibles à choisir

                obj_data = available_objectives.pop(0)
                obj_id = f"{template.type.name.lower()}_{obj_data.get('target', obj_data.get('item', obj_data.get('location', 'generic')))}{random.randint(100,999)}"
                description = f"Objective: {obj_data}" # Placeholder description
                obj_type = template.type.name.lower() # Simpliste, pourrait être plus spécifique
                target = None
                required_amount = 1

                if template.type == QuestType.FETCH:
                    target = obj_data.get("item")
                    count_range = obj_data.get("count_range", [1, 1])
                    # Adapter la quantité requise à la difficulté
                    base_amount = random.randint(*count_range)
                    required_amount = max(1, int(base_amount * (1 + (difficulty - template.difficulty_range[0]) * 0.2))) # Scaling simple
                    description = f"Collect {required_amount} x {target}"
                    obj_type = "fetch"
                elif template.type == QuestType.KILL:
                    target = obj_data.get("target")
                    count_range = obj_data.get("count_range", [1, 1])
                    # Adapter la quantité requise à la difficulté
                    base_amount = random.randint(*count_range)
                    required_amount = max(1, int(base_amount * (1 + (difficulty - template.difficulty_range[0]) * 0.15))) # Scaling simple
                    description = f"Defeat {required_amount} x {target}"
                    obj_type = "kill"
                elif template.type == QuestType.EXPLORE:
                     target = obj_data.get("location")
                     # Pourrait avoir des sous-objectifs ou des conditions spécifiques
                     description = f"Explore the area: {target}"
                     obj_type = "explore"
                     required_amount = 1 # Généralement 1 pour l'exploration principale

                if target:
                    objectives.append(Objective(
                        id=obj_id,
                        description=description,
                        type=obj_type,
                        target=target,
                        required_amount=required_amount
                    ))
                else:
                    print(f"Warning: Could not determine target for objective data: {obj_data}")


        return objectives


    def calculate_rewards(self, template: QuestTemplate, difficulty: int) -> List[Reward]:
        """Calcule les récompenses pour une quête en fonction de sa difficulté."""
        # Logique de base pour les récompenses. Pourrait être dans quest_scaling.py
        base_xp = 50 + (difficulty * 10)
        base_gold = 10 + (difficulty * 5)

        scaled_xp = int(base_xp * template.reward_multiplier)
        scaled_gold = int(base_gold * template.reward_multiplier)

        rewards = [
            Reward(type="experience", value=scaled_xp),
            Reward(type="gold", value=scaled_gold)
        ]

        # Potentiellement ajouter des récompenses en objets basées sur la difficulté/template
        if random.random() < 0.1 * difficulty: # Chance d'obtenir un objet
             # Logique pour choisir un objet approprié (peut-être via world_state ou une loot table)
             item_reward = self.world_state.get_random_item_reward(difficulty) # Supposition
             if item_reward:
                 rewards.append(Reward(type="item", value=item_reward.id, amount=1))

        return rewards

    def generate_daily_quests(self, count: int = 3) -> List[Quest]:
        """Génère une liste de quêtes quotidiennes."""
        daily_quests = []
        player_level = self.player_stats.get('level', 1)
        # Filtrer les templates répétables et adaptés au niveau
        eligible_templates = [
            tid for tid, t in self.templates.items()
            if t.repeatable and t.required_level <= player_level + 5 # Marge pour les quotidiennes
        ]

        if not eligible_templates:
            print("No eligible repeatable templates found for daily quests.")
            return []

        attempts = 0
        max_attempts = count * 3 # Pour éviter boucle infinie si peu de templates
        while len(daily_quests) < count and attempts < max_attempts:
            attempts += 1
            template_id = random.choice(eligible_templates)
            # Générer avec une difficulté proche du niveau du joueur
            target_difficulty = random.randint(
                max(self.templates[template_id].difficulty_range[0], player_level - 2),
                min(self.templates[template_id].difficulty_range[1], player_level + 3)
            )
            target_difficulty = max(1, target_difficulty) # Assurer difficulté >= 1

            quest = self.generate_quest(template_id=template_id, target_difficulty=target_difficulty)
            if quest:
                quest.is_daily = True
                quest.title = f"[Daily] {quest.title}"
                # Assurer que l'ID est unique pour cette session de quotidiennes
                quest.id = f"daily_{quest.id}"
                # Éviter les doublons de templates si possible
                if template_id in [q.id.split('_')[1] for q in daily_quests]: # Vérif simple
                    continue
                daily_quests.append(quest)

        print(f"Generated {len(daily_quests)} daily quests.")
        return daily_quests

# --- Fichier quest_scaling.py (Exemple de ce qui pourrait y être) ---
# Ce code devrait aller dans src/engine/quests/quest_scaling.py

# def scale_difficulty(base_difficulty: int, player_level: int, world_state) -> int:
#     """Ajuste la difficulté en fonction de facteurs externes."""
#     # Exemple : Augmenter la difficulté si le joueur est dans une zone dangereuse
#     zone_modifier = world_state.get_zone_difficulty_modifier() # Supposition
#     scaled_diff = base_difficulty * zone_modifier
#     # Ajuster légèrement basé sur l'écart de niveau
#     level_diff_factor = 1 + (player_level - base_difficulty) * 0.05
#     return max(1, int(scaled_diff * level_diff_factor))

# def scale_rewards(base_rewards: List[Reward], quest_difficulty: int, player_level: int) -> List[Reward]:
#     """Ajuste les récompenses finales."""
#     # Appliquer des bonus/malus basés sur le niveau du joueur par rapport à la quête, etc.
#     scaled_rewards = []
#     for reward in base_rewards:
#         # Copier la récompense pour ne pas modifier l'original
#         new_reward = Reward(type=reward.type, value=reward.value, amount=reward.amount)
#         if new_reward.type == "experience":
#             level_diff = player_level - quest_difficulty
#             xp_multiplier = max(0.1, 1 - level_diff * 0.1) # Moins d'XP si quête trop facile
#             new_reward.value = int(new_reward.value * xp_multiplier)
#         elif new_reward.type == "gold":
#             # Peut-être un bonus si le joueur a des compétences de marchandage
#             pass
#         scaled_rewards.append(new_reward)
#     return scaled_rewards

# --- Fin de l'exemple pour quest_scaling.py ---

# Exemple d'utilisation (à intégrer dans le système principal)
if __name__ == '__main__':
    # Mock player stats and world state for testing
    mock_player_stats = {'level': 5}
    class MockWorldState:
        def find_random_npc_for_escort(self):
            class MockNPC: id, name = "npc123", "Boblin"
            return MockNPC()
        def find_random_location(self):
            class MockLoc: id, name = "loc456", "Whispering Caves"
            return MockLoc()
        def find_explorable_location(self, difficulty):
             class MockLoc: id, name = f"ruins{difficulty}", f"Level {difficulty} Ruins"
             return MockLoc()
        def get_random_item_reward(self, difficulty):
             class MockItem: id = f"sword_lvl{difficulty}"
             return MockItem()

    mock_world_state = MockWorldState()

    # Créer un fichier template temporaire pour le test
    temp_template_path = "temp_quest_templates.json"
    temp_templates = {
      "fetch_herbs_test": {
        "type": "FETCH", "difficulty_range": [1, 5], "objective_count": [1, 2],
        "reward_multiplier": 1.0, "required_level": 1, "repeatable": True,
        "possible_objectives": [{"item": "Glowleaf", "count_range": [2, 4]}]
      },
      "kill_goblins_test": {
        "type": "KILL", "difficulty_range": [3, 8], "objective_count": [1, 1],
        "reward_multiplier": 1.5, "required_level": 3, "repeatable": True,
        "possible_objectives": [{"target": "Goblin Warrior", "count_range": [3, 6]}]
      },
       "escort_test": {
        "type": "ESCORT", "difficulty_range": [5, 10], "objective_count": [1, 1],
        "reward_multiplier": 2.0, "required_level": 5, "repeatable": False
      },
       "explore_test": {
        "type": "EXPLORE", "difficulty_range": [2, 6], "objective_count": [1, 1],
        "reward_multiplier": 1.2, "required_level": 2, "repeatable": True
      }
    }
    try:
        with open(temp_template_path, 'w') as f:
            json.dump(temp_templates, f, indent=2)

        generator = QuestGenerator(mock_player_stats, mock_world_state, templates_path=temp_template_path)

        print("\n--- Generating Specific Quest ---")
        fetch_quest = generator.generate_quest("fetch_herbs_test")
        if fetch_quest:
            print(fetch_quest)

        print("\n--- Generating Quest for Player Level ---")
        random_quest = generator.generate_quest() # Laisse le générateur choisir
        if random_quest:
            print(random_quest)

        print("\n--- Generating Daily Quests ---")
        daily_quests = generator.generate_daily_quests(count=2)
        for quest in daily_quests:
            print(quest)

        print("\n--- Generating Escort Quest ---")
        escort_quest = generator.generate_quest("escort_test")
        if escort_quest:
            print(escort_quest)

        print("\n--- Generating Explore Quest ---")
        explore_quest = generator.generate_quest("explore_test")
        if explore_quest:
            print(explore_quest)

    finally:
        # Nettoyer le fichier temporaire
        import os
        if os.path.exists(temp_template_path):
            os.remove(temp_template_path)