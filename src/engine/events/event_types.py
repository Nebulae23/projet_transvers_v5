# src/engine/events/event_types.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Placeholder pour l'état du jeu ou le monde, à adapter selon la structure réelle
GameState = Any

class EventType(Enum):
    COMBAT = auto()
    RESOURCE = auto()
    WEATHER = auto()
    STORY = auto()
    SPECIAL = auto() # Pour des événements uniques ou non catégorisés

@dataclass
class EventParameters:
    duration: float = 0.0 # Durée en secondes, 0 pour instantané
    priority: int = 0 # Priorité de l'événement (plus élevé = plus prioritaire)
    repeatable: bool = False # Si l'événement peut se répéter
    cooldown: float = 0.0 # Temps minimum entre deux occurrences si répétable
    # Ajout de paramètres spécifiques possibles
    specific_params: Optional[Dict[str, Any]] = None

class GameEvent(ABC):
    """Classe de base abstraite pour tous les événements du jeu."""
    def __init__(self, event_type: EventType, params: EventParameters):
        self.event_type = event_type
        self.params = params
        self.is_active = False
        self.elapsed_time = 0.0
        self.completion_progress = 0.0 # Pour les événements avec une progression interne

    @abstractmethod
    def check_conditions(self, game_state: GameState) -> bool:
        """Vérifie si les conditions de déclenchement sont remplies."""
        pass

    @abstractmethod
    def start(self, game_state: GameState) -> bool:
        """Démarre l'événement si les conditions sont remplies."""
        if not self.is_active and self.check_conditions(game_state):
            self.is_active = True
            self.elapsed_time = 0.0
            self.completion_progress = 0.0
            print(f"Starting event: {self.__class__.__name__} ({self.event_type.name})")
            # Logique de démarrage spécifique à l'événement
            return True
        return False

    @abstractmethod
    def update(self, delta_time: float, game_state: GameState):
        """Met à jour l'état de l'événement."""
        if not self.is_active:
            return

        self.elapsed_time += delta_time
        # Logique de mise à jour spécifique
        print(f"Updating event: {self.__class__.__name__} ({self.event_type.name}), elapsed: {self.elapsed_time:.2f}s")

        # Vérifier si l'événement a une durée et s'il est terminé
        if self.params.duration > 0 and self.elapsed_time >= self.params.duration:
            self.end(game_state)

    @abstractmethod
    def end(self, game_state: GameState):
        """Termine l'événement."""
        if self.is_active:
            self.is_active = False
            self.completion_progress = 1.0 # Marquer comme complété
            print(f"Ending event: {self.__class__.__name__} ({self.event_type.name})")
            # Logique de fin spécifique (ex: récompenses)

    def get_progress(self) -> float:
        """Retourne la progression de l'événement (0.0 à 1.0)."""
        if not self.is_active:
            return self.completion_progress # 0.0 si jamais démarré, 1.0 si terminé

        if self.params.duration > 0:
            return min(self.elapsed_time / self.params.duration, 1.0)
        else:
            # Pour les événements sans durée fixe, la progression peut être gérée différemment
            return self.completion_progress

# --- Implémentations spécifiques des événements ---

class CombatEvent(GameEvent):
    """Événement déclenchant un combat."""
    def __init__(self, params: EventParameters, enemy_group: str, difficulty: int):
        super().__init__(EventType.COMBAT, params)
        self.enemy_group = enemy_group
        self.difficulty = difficulty
        # Potentiellement d'autres détails: lieu, conditions de victoire/défaite spécifiques

    def check_conditions(self, game_state: GameState) -> bool:
        # Exemple: Vérifier si le joueur est dans une zone de combat, niveau suffisant, etc.
        print(f"Checking conditions for CombatEvent...")
        # return game_state.player.location.is_combat_zone and game_state.player.level >= self.difficulty
        return True # Placeholder

    def start(self, game_state: GameState) -> bool:
        if super().start(game_state):
            print(f"  -> Initiating combat with {self.enemy_group} (Difficulty: {self.difficulty})")
            # Logique pour démarrer le système de combat avec les ennemis spécifiés
            # game_state.combat_system.start_encounter(self.enemy_group, self.difficulty)
            return True
        return False

    def update(self, delta_time: float, game_state: GameState):
        super().update(delta_time, game_state)
        if self.is_active:
            # Vérifier l'état du combat dans game_state.combat_system
            # Si le combat est terminé (victoire/défaite), appeler self.end()
            # combat_status = game_state.combat_system.get_status(self) # Besoin d'identifier le combat
            # if combat_status.is_over:
            #    self.end(game_state)
            pass # Placeholder

    def end(self, game_state: GameState):
        if self.is_active:
            print(f"  -> Combat event with {self.enemy_group} ended.")
            # Logique de fin de combat (récompenses, nettoyage)
            # game_state.combat_system.end_encounter(self)
            super().end(game_state)


class ResourceEvent(GameEvent):
    """Événement modifiant les ressources (gain/perte)."""
    def __init__(self, params: EventParameters, resource_type: str, amount: int, target: str = "player"):
        super().__init__(EventType.RESOURCE, params)
        self.resource_type = resource_type
        self.amount = amount
        self.target = target # Qui reçoit/perd la ressource ('player', 'city', etc.)

    def check_conditions(self, game_state: GameState) -> bool:
        # Exemple: Vérifier si la cible existe, si la ressource peut être modifiée
        print(f"Checking conditions for ResourceEvent...")
        # target_entity = game_state.get_entity(self.target)
        # return target_entity is not None and target_entity.has_resource(self.resource_type)
        return True # Placeholder

    def start(self, game_state: GameState) -> bool:
        if super().start(game_state):
            print(f"  -> Applying resource change: {self.amount} {self.resource_type} for {self.target}")
            # Logique pour modifier la ressource
            # target_entity = game_state.get_entity(self.target)
            # target_entity.modify_resource(self.resource_type, self.amount)
            # Si l'événement est instantané (duration=0), terminer immédiatement
            if self.params.duration == 0:
                self.end(game_state)
            return True
        return False

    def update(self, delta_time: float, game_state: GameState):
        # Les événements de ressources sont souvent instantanés ou gérés au démarrage/fin
        super().update(delta_time, game_state)
        # Si c'est un événement sur la durée (ex: gain progressif), implémenter ici

    def end(self, game_state: GameState):
        if self.is_active:
            print(f"  -> Resource event ({self.resource_type}) finished.")
            super().end(game_state)


class WeatherEvent(GameEvent):
    """Événement changeant la météo."""
    def __init__(self, params: EventParameters, weather_condition: str, intensity: float):
        super().__init__(EventType.WEATHER, params)
        self.weather_condition = weather_condition
        self.intensity = intensity

    def check_conditions(self, game_state: GameState) -> bool:
        # Exemple: Vérifier si la météo actuelle est différente, si la zone le permet
        print(f"Checking conditions for WeatherEvent...")
        # return game_state.weather_system.current_condition != self.weather_condition
        return True # Placeholder

    def start(self, game_state: GameState) -> bool:
        if super().start(game_state):
            print(f"  -> Changing weather to {self.weather_condition} (Intensity: {self.intensity})")
            # Logique pour changer la météo via le système météo
            # game_state.weather_system.set_weather(self.weather_condition, self.intensity, self.params.duration)
            return True
        return False

    def update(self, delta_time: float, game_state: GameState):
        super().update(delta_time, game_state)
        # Le système météo gère probablement sa propre transition/durée
        # On pourrait vérifier ici si la transition est terminée pour synchroniser self.end()

    def end(self, game_state: GameState):
        if self.is_active:
            print(f"  -> Weather event ({self.weather_condition}) finished.")
            # Logique de fin (ex: retour à la météo normale si non géré par le système météo)
            # game_state.weather_system.revert_weather() # Ou laisser le système gérer
            super().end(game_state)


class StoryEvent(GameEvent):
    """Événement lié à la progression de l'histoire ou à un script."""
    def __init__(self, params: EventParameters, story_key: str, step: int):
        super().__init__(EventType.STORY, params)
        self.story_key = story_key # Identifiant unique de l'arc narratif ou quête
        self.step = step # Étape spécifique dans cet arc

    def check_conditions(self, game_state: GameState) -> bool:
        # Exemple: Vérifier la progression du joueur dans l'histoire
        print(f"Checking conditions for StoryEvent...")
        # return game_state.story_manager.check_progression(self.story_key, self.step - 1)
        return True # Placeholder

    def start(self, game_state: GameState) -> bool:
        if super().start(game_state):
            print(f"  -> Triggering story event: {self.story_key} - Step {self.step}")
            # Logique pour déclencher des dialogues, cinématiques, objectifs, etc.
            # game_state.story_manager.trigger_step(self.story_key, self.step)
            # Les événements d'histoire peuvent être instantanés ou avoir une durée (cinématique)
            if self.params.duration == 0:
                 self.end(game_state)
            return True
        return False

    def update(self, delta_time: float, game_state: GameState):
        super().update(delta_time, game_state)
        # Mettre à jour la progression si l'événement a une durée ou des étapes internes
        # (ex: attendre la fin d'un dialogue)
        # if game_state.dialogue_manager.is_active():
        #     self.completion_progress = game_state.dialogue_manager.get_progress()
        # elif self.is_active and self.params.duration == 0: # Si instantané et démarré
        #     self.end(game_state)

    def end(self, game_state: GameState):
        if self.is_active:
            print(f"  -> Story event {self.story_key} - Step {self.step} finished.")
            # Mettre à jour la progression globale de l'histoire
            # game_state.story_manager.complete_step(self.story_key, self.step)
            super().end(game_state)

# On pourrait ajouter SpecialEvent ici si nécessaire pour des cas très spécifiques
# class SpecialEvent(GameEvent):
#     def __init__(self, params: EventParameters, event_id: str):
#         super().__init__(EventType.SPECIAL, params)
#         self.event_id = event_id
#     # ... implémentation spécifique ...