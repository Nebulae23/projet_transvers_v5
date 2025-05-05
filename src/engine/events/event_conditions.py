# src/engine/events/event_conditions.py
from abc import ABC, abstractmethod
from typing import List, Any, Literal

# Placeholder pour l'état du jeu ou le monde, à adapter selon la structure réelle
GameState = Any

class EventCondition(ABC):
    """Classe de base abstraite pour les conditions de déclenchement d'événements."""
    @abstractmethod
    def check(self, game_state: GameState) -> bool:
        """
        Vérifie si la condition est remplie dans l'état actuel du jeu.

        :param game_state: L'état actuel du jeu (ou monde).
        :return: True si la condition est remplie, False sinon.
        """
        pass

class TimeCondition(EventCondition):
    """Condition basée sur le temps de jeu."""
    def __init__(self, min_time: float = 0.0, max_time: float = float('inf')):
        """
        Initialise la condition temporelle.

        :param min_time: Temps de jeu minimum (en secondes ou autre unité de temps du jeu).
        :param max_time: Temps de jeu maximum (en secondes ou autre unité de temps du jeu).
        """
        self.min_time = min_time
        self.max_time = max_time
        if min_time > max_time:
            raise ValueError("min_time ne peut pas être supérieur à max_time")

    def check(self, game_state: GameState) -> bool:
        """Vérifie si le temps de jeu actuel est dans l'intervalle spécifié."""
        # Suppose que game_state a un attribut ou une méthode pour obtenir le temps actuel
        current_time = getattr(game_state, 'current_time', 0.0) # Exemple: game_state.time_manager.get_time()
        print(f"Checking TimeCondition: {self.min_time} <= {current_time} < {self.max_time}")
        return self.min_time <= current_time < self.max_time

class ResourceCondition(EventCondition):
    """Condition basée sur le niveau d'une ressource."""
    def __init__(self, resource_type: str, min_amount: int = 0, max_amount: int = float('inf'), target: str = "player"):
        """
        Initialise la condition de ressource.

        :param resource_type: Le type de ressource à vérifier (ex: 'gold', 'wood').
        :param min_amount: Quantité minimale requise.
        :param max_amount: Quantité maximale autorisée.
        :param target: L'entité dont la ressource est vérifiée ('player', 'city', etc.).
        """
        self.resource_type = resource_type
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.target = target
        if min_amount > max_amount:
            raise ValueError("min_amount ne peut pas être supérieur à max_amount")

    def check(self, game_state: GameState) -> bool:
        """Vérifie si la quantité de ressource de la cible est dans l'intervalle spécifié."""
        # Suppose que game_state peut accéder aux ressources de la cible
        # Exemple: target_entity = game_state.get_entity(self.target)
        # current_amount = target_entity.get_resource(self.resource_type) if target_entity else 0
        current_amount = 0 # Placeholder
        try:
            # Placeholder pour obtenir la ressource
            target_entity = game_state.get_entity(self.target) # Hypothetical method
            if target_entity:
                 current_amount = target_entity.resources.get(self.resource_type, 0) # Hypothetical access
            else:
                 print(f"Warning: Target '{self.target}' not found for ResourceCondition.")
                 return False
        except AttributeError:
             print(f"Warning: Could not access resources for target '{self.target}' in game_state.")
             return False # Impossible de vérifier

        print(f"Checking ResourceCondition ({self.target}.{self.resource_type}): {self.min_amount} <= {current_amount} < {self.max_amount}")
        return self.min_amount <= current_amount < self.max_amount

class ProgressCondition(EventCondition):
    """Condition basée sur la progression dans une quête, une histoire ou un niveau."""
    def __init__(self, progress_key: str, required_value: Any, comparison: Literal['>=', '<=', '==', '!=', '>', '<'] = '>='):
        """
        Initialise la condition de progression.

        :param progress_key: Clé identifiant la progression à vérifier (ex: 'main_quest_step', 'player_level').
        :param required_value: La valeur de progression requise.
        :param comparison: L'opérateur de comparaison ('==', '!=', '>=', '<=', '>', '<').
        """
        self.progress_key = progress_key
        self.required_value = required_value
        self.comparison = comparison
        if comparison not in ['>=', '<=', '==', '!=', '>', '<']:
            raise ValueError(f"Opérateur de comparaison invalide: {comparison}")

    def check(self, game_state: GameState) -> bool:
        """Vérifie si la progression actuelle satisfait la condition."""
        # Suppose que game_state peut accéder aux données de progression
        # Exemple: current_value = game_state.progression_system.get_value(self.progress_key)
        current_value = None # Placeholder
        try:
            # Placeholder pour obtenir la valeur de progression
            # Exemple: current_value = game_state.player.level ou game_state.quest_log['main_quest'].current_step
            if self.progress_key == 'player_level': # Exemple spécifique
                 current_value = getattr(game_state.player, 'level', 0)
            else:
                 # Accès plus générique, potentiellement via un dictionnaire ou un système dédié
                 current_value = game_state.get_progress_value(self.progress_key) # Hypothetical method
        except AttributeError:
             print(f"Warning: Could not access progress key '{self.progress_key}' in game_state.")
             return False # Impossible de vérifier

        if current_value is None:
             print(f"Warning: Progress key '{self.progress_key}' returned None.")
             return False

        print(f"Checking ProgressCondition ({self.progress_key}): {current_value} {self.comparison} {self.required_value}")

        try:
            if self.comparison == '>=':
                return current_value >= self.required_value
            elif self.comparison == '<=':
                return current_value <= self.required_value
            elif self.comparison == '==':
                return current_value == self.required_value
            elif self.comparison == '!=':
                return current_value != self.required_value
            elif self.comparison == '>':
                return current_value > self.required_value
            elif self.comparison == '<':
                return current_value < self.required_value
        except TypeError:
            print(f"Warning: Type mismatch for comparison in ProgressCondition ({self.progress_key}): {type(current_value)} vs {type(self.required_value)}")
            return False # Erreur de type lors de la comparaison

        return False # Ne devrait pas être atteint

class CompoundCondition(EventCondition):
    """Condition composée qui combine plusieurs autres conditions (logique AND ou OR)."""
    def __init__(self, conditions: List[EventCondition], logic: Literal['AND', 'OR'] = 'AND'):
        """
        Initialise la condition composée.

        :param conditions: Une liste d'objets EventCondition à combiner.
        :param logic: L'opérateur logique à utiliser ('AND' ou 'OR').
        """
        if not conditions:
            raise ValueError("La liste des conditions ne peut pas être vide pour CompoundCondition")
        if logic not in ['AND', 'OR']:
            raise ValueError("La logique doit être 'AND' ou 'OR'")

        self.conditions = conditions
        self.logic = logic

    def check(self, game_state: GameState) -> bool:
        """Vérifie si la combinaison des conditions est remplie selon la logique spécifiée."""
        print(f"Checking CompoundCondition ({self.logic}) with {len(self.conditions)} sub-conditions:")
        if self.logic == 'AND':
            # Toutes les conditions doivent être vraies
            for i, condition in enumerate(self.conditions):
                print(f"  -> Checking sub-condition {i+1}/{len(self.conditions)} ({condition.__class__.__name__})")
                if not condition.check(game_state):
                    print(f"  <- Sub-condition {i+1} FAILED. CompoundCondition result: False")
                    return False
            print(f"  <- All sub-conditions PASSED. CompoundCondition result: True")
            return True
        elif self.logic == 'OR':
            # Au moins une condition doit être vraie
            for i, condition in enumerate(self.conditions):
                print(f"  -> Checking sub-condition {i+1}/{len(self.conditions)} ({condition.__class__.__name__})")
                if condition.check(game_state):
                    print(f"  <- Sub-condition {i+1} PASSED. CompoundCondition result: True")
                    return True
            print(f"  <- All sub-conditions FAILED. CompoundCondition result: False")
            return False
        return False # Ne devrait pas être atteint

# Exemple d'utilisation (à des fins de test ou d'illustration)
if __name__ == '__main__':
    # Créer un faux game_state pour les tests
    class MockGameState:
        def __init__(self):
            self.current_time = 50.0
            self.player = type('obj', (object,), {'resources': {'gold': 150}, 'level': 5})()
            self.city = type('obj', (object,), {'resources': {'wood': 80}})()
            self.progress_data = {'main_quest_step': 3, 'faction_rep_elves': 25}

        def get_entity(self, target_name):
            if target_name == "player":
                return self.player
            elif target_name == "city":
                return self.city
            return None

        def get_progress_value(self, key):
            return self.progress_data.get(key)

    mock_state = MockGameState()

    print("--- Testing Conditions ---")

    time_cond_ok = TimeCondition(min_time=40.0, max_time=60.0)
    time_cond_fail = TimeCondition(min_time=60.0)
    print(f"Time OK: {time_cond_ok.check(mock_state)}") # True
    print(f"Time Fail: {time_cond_fail.check(mock_state)}") # False

    resource_cond_ok = ResourceCondition(resource_type='gold', min_amount=100, max_amount=200, target='player')
    resource_cond_fail = ResourceCondition(resource_type='wood', min_amount=100, target='city')
    print(f"Resource OK: {resource_cond_ok.check(mock_state)}") # True
    print(f"Resource Fail: {resource_cond_fail.check(mock_state)}") # False

    progress_cond_ok = ProgressCondition(progress_key='main_quest_step', required_value=3, comparison='==')
    progress_cond_fail = ProgressCondition(progress_key='player_level', required_value=6, comparison='>=')
    print(f"Progress OK: {progress_cond_ok.check(mock_state)}") # True
    print(f"Progress Fail: {progress_cond_fail.check(mock_state)}") # False

    compound_and_ok = CompoundCondition([time_cond_ok, resource_cond_ok, progress_cond_ok], logic='AND')
    compound_and_fail = CompoundCondition([time_cond_ok, resource_cond_fail], logic='AND')
    compound_or_ok = CompoundCondition([time_cond_fail, resource_cond_ok], logic='OR')
    compound_or_fail = CompoundCondition([time_cond_fail, resource_cond_fail], logic='OR')

    print(f"Compound AND OK: {compound_and_ok.check(mock_state)}") # True
    print(f"Compound AND Fail: {compound_and_fail.check(mock_state)}") # False
    print(f"Compound OR OK: {compound_or_ok.check(mock_state)}") # True
    print(f"Compound OR Fail: {compound_or_fail.check(mock_state)}") # False
    print("--- Testing Finished ---")