# -*- coding: utf-8 -*-
"""
Module définissant les bâtiments de production et de stockage de ressources.
"""

from .building_base import BuildingBase, BuildingState
from abc import abstractmethod # Ajout import

class ResourceBuilding(BuildingBase):
    """Classe de base pour les bâtiments liés aux ressources."""
    def __init__(self, name: str, level: int = 1, max_level: int = 5,
                 cost: dict[str, int] = None, build_time: float = 10.0,
                 initial_health: int = 100, max_health: int = 100,
                 resource_type: str = "unknown", production_rate: float = 0.0,
                 capacity: int = 0):
        super().__init__(name, level, max_level, cost, build_time, initial_health, max_health)
        self.resource_type = resource_type
        self.production_rate = production_rate # Unités par seconde
        self.capacity = capacity # Capacité de stockage interne ou limite de production

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
    def get_production_rate_for_level(self, level: int) -> float:
        """Retourne le taux de production pour un niveau donné."""
        pass

    @abstractmethod
    def get_capacity_for_level(self, level: int) -> int:
        """Retourne la capacité pour un niveau donné."""
        pass

    def update_level_dependent_stats(self):
        """Met à jour les statistiques dépendantes du niveau (production, capacité)."""
        self.production_rate = self.get_production_rate_for_level(self.level)
        self.capacity = self.get_capacity_for_level(self.level)
        # Potentiellement mettre à jour aussi max_health, etc. si ça dépend du niveau

    def _complete_construction_or_upgrade(self):
        """Termine la construction/amélioration et met à jour les stats."""
        super()._complete_construction_or_upgrade()
        if self.state == BuildingState.OPERATIONAL:
            self.update_level_dependent_stats()
            print(f"{self.name} (Niveau {self.level}) - Production: {self.production_rate}/s, Capacité: {self.capacity}")


    def get_description(self) -> str:
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        prod_info = f"Produit {self.production_rate:.2f} {self.resource_type}/s." if self.production_rate > 0 else ""
        cap_info = f"Capacité: {self.capacity} {self.resource_type}." if self.capacity > 0 else ""
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. {prod_info} {cap_info}"

    def get_ui_info(self) -> dict:
        # Tente d'appeler get_ui_info de la classe parent si elle existe
        try:
            # Note: BuildingBase n'a pas get_ui_info, donc on initialise un dict vide
            # Si BuildingBase avait get_ui_info, on utiliserait super().get_ui_info()
            info = {}
        except AttributeError:
             info = {} # Fallback

        info.update({
            "name": self.name,
            "level": self.level,
            "max_level": self.max_level,
            "state": self.state.name,
            "health": self.health,
            "max_health": self.max_health,
            "resource_type": self.resource_type,
            "production_rate": self.production_rate,
            "capacity": self.capacity,
            "cost_next_level": self.get_cost_for_level(self.level + 1) if self.level < self.max_level else None,
            "build_time_next_level": self.get_build_time_for_level(self.level + 1) if self.level < self.max_level else None,
        })
        return info

# --- Bâtiments de Production ---

class Sawmill(ResourceBuilding):
    """Produit du bois."""
    def __init__(self, level: int = 1):
        super().__init__(name="Scierie", level=level, max_level=10,
                         resource_type="wood", initial_health=150, max_health=150)
        # Initialisation après super() pour utiliser les méthodes get_...
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats() # Initialiser production/capacité

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 50, 'stone': 20}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 50 * (1.5**(target_level - 1))
        stone_cost = 20 * (1.4**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 15.0 * (1.2**(target_level - 1))

    def get_production_rate_for_level(self, level: int) -> float:
        return 0.5 * (1.3**(level - 1)) # Bois par seconde

    def get_capacity_for_level(self, level: int) -> int:
        return 0 # La scierie ne stocke pas, elle produit directement

class Mine(ResourceBuilding):
    """Produit de la pierre ou du minerai."""
    def __init__(self, level: int = 1, resource_type: str = "stone"):
        # Le type de ressource pourrait dépendre de l'emplacement sur la carte
        super().__init__(name="Mine", level=level, max_level=10,
                         resource_type=resource_type, initial_health=200, max_health=200)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 80, 'stone': 40}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 80 * (1.4**(target_level - 1))
        stone_cost = 40 * (1.6**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 20.0 * (1.25**(target_level - 1))

    def get_production_rate_for_level(self, level: int) -> float:
        # Exemple : 0.4 pierre/s ou 0.2 minerai/s au niveau 1
        base_rate = 0.4 if self.resource_type == "stone" else 0.2
        return base_rate * (1.35**(level - 1))

    def get_capacity_for_level(self, level: int) -> int:
        return 0 # La mine ne stocke pas

class Farm(ResourceBuilding):
    """Produit de la nourriture."""
    def __init__(self, level: int = 1):
        super().__init__(name="Ferme", level=level, max_level=8,
                         resource_type="food", initial_health=100, max_health=100)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 60, 'food': 10} # Coûte un peu de nourriture pour démarrer

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 60 * (1.3**(target_level - 1))
        food_cost = 10 * (1.2**(target_level - 1))
        return {'wood': int(wood_cost), 'food': int(food_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 12.0 * (1.15**(target_level - 1))

    def get_production_rate_for_level(self, level: int) -> float:
        return 1.0 * (1.4**(level - 1)) # Nourriture par seconde

    def get_capacity_for_level(self, level: int) -> int:
        return 0 # La ferme ne stocke pas

# --- Bâtiment de Stockage ---

class Warehouse(ResourceBuilding):
    """Augmente la capacité de stockage globale des ressources."""
    def __init__(self, level: int = 1):
        # Note: Ce bâtiment n'a pas de 'resource_type' spécifique ni de 'production_rate'
        # Sa 'capacity' représente l'augmentation de la capacité *globale*
        super().__init__(name="Entrepôt", level=level, max_level=15,
                         resource_type="storage", production_rate=0.0,
                         initial_health=250, max_health=250)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats() # Pour la capacité

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 150, 'stone': 100}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 150 * (1.6**(target_level - 1))
        stone_cost = 100 * (1.5**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 25.0 * (1.3**(target_level - 1))

    def get_production_rate_for_level(self, level: int) -> float:
        return 0.0 # Ne produit rien

    def get_capacity_for_level(self, level: int) -> int:
        # Augmentation de la capacité de stockage globale par niveau
        # Utilisation d'une formule exponentielle pour la capacité
        return int(500 * (1.5**(level - 1)))


    def get_description(self) -> str:
        # Surcharge pour une description plus appropriée
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        cap_info = f"Augmente la capacité de stockage de {int(self.capacity)}."
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. {cap_info}"

    def get_ui_info(self) -> dict:
        # Surcharge pour enlever production_rate et resource_type non pertinents
        # Appel correct à la méthode get_ui_info de la classe parent (BuildingBase)
        try:
            # Récupère les infos de base de BuildingBase via ResourceBuilding
            info = super(Warehouse, self).get_ui_info()
        except AttributeError:
             info = {} # Fallback

        # Met à jour avec les infos spécifiques à Warehouse et nettoie
        info.update({
            "storage_increase": self.capacity,
            "cost_next_level": self.get_cost_for_level(self.level + 1) if self.level < self.max_level else None,
            "build_time_next_level": self.get_build_time_for_level(self.level + 1) if self.level < self.max_level else None,
        })
        # Nettoyage des clés non pertinentes
        info.pop("resource_type", None)
        info.pop("production_rate", None)
        info.pop("capacity", None) # Remplacé par storage_increase
        return info