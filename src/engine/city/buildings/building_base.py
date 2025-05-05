# -*- coding: utf-8 -*-
"""
Module définissant la classe de base abstraite pour tous les bâtiments de la ville.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto

class BuildingState(Enum):
    """Énumération des états possibles d'un bâtiment."""
    UNDER_CONSTRUCTION = auto()
    OPERATIONAL = auto()
    DAMAGED = auto()
    DESTROYED = auto()

class BuildingBase(ABC):
    """
    Classe de base abstraite pour tous les bâtiments.

    Attributs:
        name (str): Le nom du type de bâtiment.
        level (int): Le niveau actuel du bâtiment.
        max_level (int): Le niveau maximum que le bâtiment peut atteindre.
        cost (dict[str, int]): Coût en ressources pour construire ou améliorer.
                               Exemple: {'wood': 100, 'stone': 50}
        build_time (float): Temps nécessaire pour construire ou améliorer (en secondes).
        state (BuildingState): L'état actuel du bâtiment.
        health (int): Points de vie actuels du bâtiment.
        max_health (int): Points de vie maximum du bâtiment.
    """

    def __init__(self, name: str, level: int = 1, max_level: int = 5,
                 cost: dict[str, int] = None, build_time: float = 10.0,
                 initial_health: int = 100, max_health: int = 100):
        """
        Initialise un bâtiment de base.

        Args:
            name (str): Le nom du type de bâtiment.
            level (int): Le niveau initial (par défaut 1).
            max_level (int): Le niveau maximum (par défaut 5).
            cost (dict[str, int]): Le coût initial. Doit être défini par les sous-classes.
            build_time (float): Le temps de construction initial.
            initial_health (int): La santé initiale.
            max_health (int): La santé maximale.
        """
        self.name = name
        self.level = level
        self.max_level = max_level
        # Le coût doit être défini spécifiquement par chaque type de bâtiment
        self.cost = cost if cost is not None else self._get_default_cost()
        self.build_time = build_time
        self.state = BuildingState.UNDER_CONSTRUCTION # Commence en construction par défaut
        self.health = initial_health
        self.max_health = max_health
        self._construction_progress = 0.0 # Temps écoulé depuis le début de la construction/amélioration

    @abstractmethod
    def _get_default_cost(self) -> dict[str, int]:
        """Méthode abstraite pour obtenir le coût par défaut du niveau 1."""
        pass

    @abstractmethod
    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        """
        Calcule le coût pour atteindre un niveau cible.

        Args:
            target_level (int): Le niveau pour lequel calculer le coût.

        Returns:
            dict[str, int]: Le dictionnaire des coûts en ressources.
        """
        pass

    @abstractmethod
    def get_build_time_for_level(self, target_level: int) -> float:
        """
        Calcule le temps de construction pour atteindre un niveau cible.

        Args:
            target_level (int): Le niveau pour lequel calculer le temps.

        Returns:
            float: Le temps de construction en secondes.
        """
        pass

    def start_construction(self):
        """Lance la construction du bâtiment (niveau 1)."""
        if self.level == 0 and self.state != BuildingState.UNDER_CONSTRUCTION:
             self.state = BuildingState.UNDER_CONSTRUCTION
             self.level = 1 # Marque comme niveau 1 en construction
             self.cost = self.get_cost_for_level(1)
             self.build_time = self.get_build_time_for_level(1)
             self._construction_progress = 0.0
             print(f"Construction de {self.name} (Niveau 1) démarrée. Coût: {self.cost}, Temps: {self.build_time}s")
        else:
            print(f"Impossible de démarrer la construction de {self.name}. État actuel: {self.state}, Niveau: {self.level}")


    def start_upgrade(self):
        """Lance l'amélioration du bâtiment au niveau suivant."""
        if self.state == BuildingState.OPERATIONAL and self.level < self.max_level:
            next_level = self.level + 1
            self.cost = self.get_cost_for_level(next_level)
            self.build_time = self.get_build_time_for_level(next_level)
            self.state = BuildingState.UNDER_CONSTRUCTION
            self._construction_progress = 0.0
            print(f"Amélioration de {self.name} vers Niveau {next_level} démarrée. Coût: {self.cost}, Temps: {self.build_time}s")
        elif self.level >= self.max_level:
            print(f"{self.name} est déjà au niveau maximum ({self.max_level}).")
        elif self.state != BuildingState.OPERATIONAL:
             print(f"Impossible d'améliorer {self.name}. État actuel: {self.state}")


    def update_construction(self, delta_time: float):
        """
        Met à jour la progression de la construction ou de l'amélioration.

        Args:
            delta_time (float): Le temps écoulé depuis la dernière mise à jour.
        """
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self._construction_progress += delta_time
            if self._construction_progress >= self.build_time:
                self._complete_construction_or_upgrade()

    def _complete_construction_or_upgrade(self):
        """Termine la construction ou l'amélioration."""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
             # Si level était 1 (construction initiale), il reste 1.
             # Si level était > 1 (amélioration), on incrémente.
             if self._construction_progress >= self.build_time: # Vérifie si c'est une amélioration
                 if self.level > 0 and self.build_time == self.get_build_time_for_level(self.level + 1):
                     self.level += 1

             self.state = BuildingState.OPERATIONAL
             self.health = self.max_health # Restaurer la santé après construction/amélioration
             self._construction_progress = 0.0
             print(f"{self.name} (Niveau {self.level}) est maintenant opérationnel.")


    def take_damage(self, amount: int):
        """
        Applique des dégâts au bâtiment.

        Args:
            amount (int): La quantité de dégâts à infliger.
        """
        if self.state == BuildingState.OPERATIONAL or self.state == BuildingState.DAMAGED:
            self.health -= amount
            print(f"{self.name} a subi {amount} dégâts. Santé restante: {self.health}/{self.max_health}")
            if self.health <= 0:
                self.health = 0
                self.state = BuildingState.DESTROYED
                print(f"{self.name} a été détruit !")
            elif self.health < self.max_health * 0.5 and self.state != BuildingState.DAMAGED: # Seuil pour être endommagé
                self.state = BuildingState.DAMAGED
                print(f"{self.name} est maintenant endommagé.")

    def repair(self, amount: int):
        """
        Répare le bâtiment.

        Args:
            amount (int): La quantité de points de vie à restaurer.
        """
        if self.state == BuildingState.DAMAGED or self.state == BuildingState.DESTROYED:
            self.health += amount
            if self.health >= self.max_health:
                self.health = self.max_health
                self.state = BuildingState.OPERATIONAL
                print(f"{self.name} est entièrement réparé et opérationnel.")
            elif self.health >= self.max_health * 0.5 and self.state == BuildingState.DAMAGED:
                 self.state = BuildingState.OPERATIONAL # Repasse opérationnel si au-dessus du seuil
                 print(f"{self.name} n'est plus considéré comme endommagé (Santé: {self.health}/{self.max_health}).")
            else:
                 print(f"{self.name} réparé de {amount}. Santé actuelle: {self.health}/{self.max_health}")
        else:
            print(f"{self.name} n'a pas besoin de réparation (État: {self.state}).")


    @abstractmethod
    def get_description(self) -> str:
        """Retourne une description textuelle du bâtiment et de son état."""
        pass

    @abstractmethod
    def get_ui_info(self) -> dict:
        """
        Retourne un dictionnaire d'informations pour l'affichage dans l'interface utilisateur.
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} (Niveau {self.level}) - État: {self.state.name}, Santé: {self.health}/{self.max_health}"