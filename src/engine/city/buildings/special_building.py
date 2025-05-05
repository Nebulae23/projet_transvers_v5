# -*- coding: utf-8 -*-
"""
Module définissant les bâtiments spéciaux avec des fonctions uniques.
"""

from .building_base import BuildingBase, BuildingState
from abc import abstractmethod

class SpecialBuilding(BuildingBase):
    """Classe de base pour les bâtiments spéciaux."""
    def __init__(self, name: str, level: int = 1, max_level: int = 5,
                 cost: dict[str, int] = None, build_time: float = 10.0,
                 initial_health: int = 100, max_health: int = 100,
                 effect_description: str = "Effet spécial"):
        super().__init__(name, level, max_level, cost, build_time, initial_health, max_health)
        self.effect_description = effect_description
        # Les effets spécifiques seront gérés par les sous-classes ou le système de jeu

    @abstractmethod
    def _get_default_cost(self) -> dict[str, int]:
        pass

    @abstractmethod
    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        pass

    @abstractmethod
    def get_build_time_for_level(self, target_level: int) -> float:
        pass

    @abstractmethod
    def get_effect_description_for_level(self, level: int) -> str:
        """Retourne la description de l'effet pour un niveau donné."""
        pass

    def update_level_dependent_stats(self):
        """Met à jour les statistiques/effets dépendant du niveau."""
        self.effect_description = self.get_effect_description_for_level(self.level)
        # Mettre à jour max_health si nécessaire

    def _complete_construction_or_upgrade(self):
        """Termine la construction/amélioration et met à jour les stats."""
        super()._complete_construction_or_upgrade()
        if self.state == BuildingState.OPERATIONAL:
            self.update_level_dependent_stats()
            print(f"{self.name} (Niveau {self.level}) - Effet: {self.effect_description}")

    def get_description(self) -> str:
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. Effet: {self.effect_description}"

    def get_ui_info(self) -> dict:
        try:
            info = {} # BuildingBase n'a pas get_ui_info
        except AttributeError:
             info = {}

        info.update({
            "name": self.name,
            "level": self.level,
            "max_level": self.max_level,
            "state": self.state.name,
            "health": self.health,
            "max_health": self.max_health,
            "effect_description": self.effect_description,
            "cost_next_level": self.get_cost_for_level(self.level + 1) if self.level < self.max_level else None,
            "build_time_next_level": self.get_build_time_for_level(self.level + 1) if self.level < self.max_level else None,
        })
        return info

# --- Bâtiments Spéciaux Spécifiques ---

class TownHall(SpecialBuilding):
    """Hôtel de ville : Bâtiment central, peut influencer la population ou les limites."""
    def __init__(self, level: int = 1):
        super().__init__(name="Hôtel de Ville", level=level, max_level=10,
                         initial_health=1000, max_health=1000) # Santé élevée
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.population_cap = self.get_population_cap_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        # Coût initial élevé, car c'est le bâtiment principal
        return {'wood': 500, 'stone': 500, 'food': 100}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        # Progression de coût très élevée
        wood_cost = 500 * (2.0**(target_level - 1))
        stone_cost = 500 * (2.0**(target_level - 1))
        food_cost = 100 * (1.5**(target_level - 1))
        # Pourrait nécessiter des ressources spéciales à haut niveau
        return {'wood': int(wood_cost), 'stone': int(stone_cost), 'food': int(food_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 120.0 * (1.5**(target_level - 1)) # Temps de construction long

    def get_population_cap_for_level(self, level: int) -> int:
        # Le niveau de l'hôtel de ville détermine la population maximale
        return 10 + (level * 5)

    def get_effect_description_for_level(self, level: int) -> str:
        self.population_cap = self.get_population_cap_for_level(level)
        return f"Permet une population maximale de {self.population_cap}. Débloque d'autres bâtiments."

    def update_level_dependent_stats(self):
        super().update_level_dependent_stats()
        self.population_cap = self.get_population_cap_for_level(self.level)
        self.max_health = int(1000 * (1.3**(self.level - 1)))
        self.health = min(self.health, self.max_health)

    def get_ui_info(self) -> dict:
        info = super().get_ui_info()
        info["population_cap"] = self.population_cap
        return info
class Forge(SpecialBuilding):
    """Forge : Permet les améliorations d'équipement."""
    def __init__(self, level: int = 1):
        super().__init__(name="Forge", level=level, max_level=8,
                         initial_health=300, max_health=300)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 150, 'stone': 200, 'iron': 50} # Suppose une ressource 'iron'

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 150 * (1.4**(target_level - 1))
        stone_cost = 200 * (1.5**(target_level - 1))
        iron_cost = 50 * (1.8**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost), 'iron': int(iron_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 45.0 * (1.3**(target_level - 1))

    def get_effect_description_for_level(self, level: int) -> str:
        # Le niveau pourrait débloquer des paliers d'amélioration
        return f"Permet d'améliorer l'équipement jusqu'au niveau {level}." # Exemple simple

    # Pas d'autres stats spécifiques à mettre à jour pour l'instant
    # update_level_dependent_stats est hérité et met à jour la description


class Temple(SpecialBuilding):
    """Temple : Fournit des bonus passifs ou permet des bénédictions."""
    def __init__(self, level: int = 1):
        super().__init__(name="Temple", level=level, max_level=7,
                         initial_health=250, max_health=250)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        # Coût peut inclure des ressources plus rares ou 'faveur divine'
        return {'stone': 300, 'gold': 100} # Suppose une ressource 'gold'

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        stone_cost = 300 * (1.6**(target_level - 1))
        gold_cost = 100 * (1.9**(target_level - 1))
        return {'stone': int(stone_cost), 'gold': int(gold_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 60.0 * (1.4**(target_level - 1))

    def get_effect_description_for_level(self, level: int) -> str:
        # Le bonus pourrait être un % ou une valeur fixe
        bonus_percentage = 2 + (level * 1) # Exemple : +3% au niveau 1, +4% au niveau 2...
        return f"Fournit un bonus passif de +{bonus_percentage}% (ex: moral, production globale)."


class Laboratory(SpecialBuilding):
    """Laboratoire : Permet de rechercher de nouvelles technologies."""
    def __init__(self, level: int = 1):
        super().__init__(name="Laboratoire", level=level, max_level=10,
                         initial_health=200, max_health=200)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        # Pourrait nécessiter des ressources spécifiques comme 'cristaux' ou 'manuscrits'
        return {'wood': 100, 'stone': 150, 'gold': 50}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 100 * (1.3**(target_level - 1))
        stone_cost = 150 * (1.4**(target_level - 1))
        gold_cost = 50 * (1.7**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost), 'gold': int(gold_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 50.0 * (1.35**(target_level - 1))

    def get_effect_description_for_level(self, level: int) -> str:
        # Le niveau pourrait débloquer des paliers de recherche ou accélérer la recherche
        research_speed_bonus = level * 5 # Exemple : +5% vitesse au niveau 1
        return f"Permet la recherche technologique. Bonus de vitesse de recherche: +{research_speed_bonus}%."