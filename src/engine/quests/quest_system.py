# src/engine/quests/quest_system.py

import json
from typing import Dict, List, Optional, Set
from .quest_data import Quest, Objective, ObjectiveType, Reward

class QuestSystem:
    """
    Gère les quêtes actives, leur progression et leurs récompenses.
    """
    def __init__(self, player_inventory, player_stats): # Dependencies injected
        self.active_quests: Dict[str, Quest] = {}  # quest_id: Quest (avec progression dans les objectifs)
        self.completed_quests: Set[str] = set()  # Ensemble des quest_ids terminées
        self.available_quests: Dict[str, Quest] = {} # Quêtes chargées depuis la source de données
        self.player_inventory = player_inventory # Référence vers l'inventaire du joueur
        self.player_stats = player_stats # Référence vers les stats du joueur (pour l'XP)
        print("QuestSystem initialized.")

    def load_quests(self, filepath: str = "src/engine/quests/data/quest_definitions.json"):
        """
        Charge les définitions de quêtes depuis un fichier JSON.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                quests_data = json.load(f)

            for quest_id, data in quests_data.items():
                objectives = [Objective(**obj_data) for obj_data in data['objectives']]
                rewards = Reward(**data['rewards'])
                quest = Quest(
                    id=quest_id,
                    type=QuestType[data['type']],
                    title=data['title'],
                    description=data['description'],
                    objectives=objectives,
                    rewards=rewards,
                    prerequisites=data.get('prerequisites', []),
                    time_limit=data.get('time_limit')
                )
                self.available_quests[quest_id] = quest
            print(f"Loaded {len(self.available_quests)} quests from {filepath}")
        except FileNotFoundError:
            print(f"Error: Quest definitions file not found at {filepath}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filepath}")
        except Exception as e:
            print(f"An unexpected error occurred during quest loading: {e}")

    def can_start_quest(self, quest_id: str) -> bool:
        """ Vérifie si une quête peut être démarrée (disponible, prérequis remplis). """
        if quest_id not in self.available_quests:
            print(f"Quest {quest_id} not available.")
            return False
        if quest_id in self.active_quests or quest_id in self.completed_quests:
            print(f"Quest {quest_id} already active or completed.")
            return False

        quest = self.available_quests[quest_id]
        for prereq_id in quest.prerequisites:
            if prereq_id not in self.completed_quests:
                print(f"Prerequisite quest {prereq_id} not completed for {quest_id}.")
                return False
        return True

    def start_quest(self, quest_id: str):
        """
        Démarre une nouvelle quête si elle est disponible et les prérequis sont remplis.
        """
        if self.can_start_quest(quest_id):
            quest_definition = self.available_quests[quest_id]
            # Crée une copie pour suivre la progression individuelle
            active_quest = Quest(
                id=quest_definition.id,
                type=quest_definition.type,
                title=quest_definition.title,
                description=quest_definition.description,
                objectives=[Objective(**obj.__dict__) for obj in quest_definition.objectives], # Copie profonde des objectifs
                rewards=quest_definition.rewards, # Les récompenses sont immuables
                prerequisites=quest_definition.prerequisites,
                time_limit=quest_definition.time_limit
            )
            self.active_quests[quest_id] = active_quest
            print(f"Quest started: {quest_id} - {active_quest.title}")
            # TODO: Ajouter la logique de timer si time_limit est défini
        else:
             print(f"Quest {quest_id} could not be started.")


    def update_quest_progress(self, event_type: ObjectiveType, target_id: str, amount: int = 1):
        """
        Met à jour la progression des objectifs des quêtes actives basées sur un événement.
        """
        print(f"Received event: {event_type.name}, Target: {target_id}, Amount: {amount}")
        quests_to_check_completion = []

        for quest_id, quest in list(self.active_quests.items()): # Itérer sur une copie pour permettre la modification
            updated = False
            for objective in quest.objectives:
                if objective.type == event_type and objective.target == target_id and objective.current < objective.amount:
                    objective.current = min(objective.current + amount, objective.amount)
                    print(f"  Quest '{quest.title}': Objective '{objective.description}' progress {objective.current}/{objective.amount}")
                    updated = True

            if updated:
                quests_to_check_completion.append(quest_id)

        # Vérifier la complétion après avoir traité tous les objectifs affectés par l'événement
        for quest_id in quests_to_check_completion:
             if quest_id in self.active_quests and self.check_quest_completion(quest_id):
                 self._complete_quest(quest_id)


    def check_quest_completion(self, quest_id: str) -> bool:
        """
        Vérifie si tous les objectifs non optionnels d'une quête active sont terminés.
        """
        if quest_id not in self.active_quests:
            return False

        quest = self.active_quests[quest_id]
        for objective in quest.objectives:
            if not objective.optional and objective.current < objective.amount:
                return False  # Un objectif requis n'est pas terminé

        print(f"Quest '{quest.title}' objectives met.")
        return True

    def _complete_quest(self, quest_id: str):
        """
        Gère la complétion d'une quête, accorde les récompenses et met à jour le statut.
        """
        if quest_id not in self.active_quests:
            print(f"Error: Trying to complete non-active quest {quest_id}")
            return

        quest = self.active_quests[quest_id]
        print(f"Completing quest: {quest_id} - {quest.title}")

        # Accorder les récompenses
        self._award_quest_rewards(quest.rewards)

        # Déplacer de active à completed
        del self.active_quests[quest_id]
        self.completed_quests.add(quest_id)
        print(f"Quest {quest_id} completed and moved to completed list.")

        # Débloquer les quêtes suivantes (si nécessaire)
        # Note: Le démarrage effectif se fera via start_quest quand le joueur interagit
        for unlocked_quest_id in quest.rewards.unlock_quests:
            if unlocked_quest_id in self.available_quests:
                 print(f"Quest {unlocked_quest_id} is now potentially available.")
            else:
                 print(f"Warning: Unlocked quest {unlocked_quest_id} not found in definitions.")


    def _award_quest_rewards(self, rewards: Reward):
        """
        Accorde les récompenses spécifiées au joueur.
        """
        print(f"Awarding rewards: {rewards}")
        # Donner les ressources
        if rewards.resources:
            for resource_id, amount in rewards.resources.items():
                print(f"  Adding {amount} of {resource_id}")
                # self.player_inventory.add_resource(resource_id, amount) # Placeholder pour l'intégration réelle

        # Donner l'expérience
        if rewards.experience > 0:
            print(f"  Adding {rewards.experience} XP")
            # self.player_stats.add_experience(rewards.experience) # Placeholder

        # Donner les items spéciaux
        if rewards.special_items:
            for item_id in rewards.special_items:
                print(f"  Adding special item: {item_id}")
                # self.player_inventory.add_item(item_id) # Placeholder

        # Les quêtes débloquées sont gérées dans _complete_quest

    def get_active_quests_summary(self) -> List[str]:
        """ Retourne une liste de résumés des quêtes actives. """
        summary = []
        for quest in self.active_quests.values():
            obj_summary = []
            for obj in quest.objectives:
                 status = "✓" if obj.current >= obj.amount else f"{obj.current}/{obj.amount}"
                 optional_tag = "[Opt] " if obj.optional else ""
                 obj_summary.append(f"  - {optional_tag}{obj.description}: {status}")
            summary.append(f"{quest.title}:\n" + "\n".join(obj_summary))
        return summary

    def is_quest_active(self, quest_id: str) -> bool:
        return quest_id in self.active_quests

    def is_quest_completed(self, quest_id: str) -> bool:
        return quest_id in self.completed_quests

# Note: La classe QuestStatus n'est plus nécessaire car la progression est stockée
# directement dans les objets Objective copiés dans self.active_quests.
# L'intégration avec player_inventory et player_stats est nécessaire pour une fonctionnalité complète.