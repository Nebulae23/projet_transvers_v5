# src/engine/city/resources.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

# Use relative imports
from ..time.time_manager import TimeManager
from ..time.day_night_cycle import TimeOfDay

class ResourceType(Enum):
    """Types of resources that can be gathered in the game."""
    WOOD = auto()
    STONE = auto()
    FOOD = auto()
    GOLD = auto()
    IRON = auto()
    METAL = auto()  # Added for building.py

@dataclass
class ResourceNode: # Exemple de structure pour un nœud de production
    production_rate: float
    # On pourrait ajouter des conditions d'activation ici (ex: nécessite personnel)

@dataclass
class ResourceAmount:
    """Represents an amount of a resource with its capacity."""
    amount: float
    capacity: float
    # Les taux de production/consommation globaux peuvent être gérés ailleurs si plus complexe
    # production_rate: float = 0.0 # Peut-être redondant si géré par nœuds
    # consumption_rate: float = 0.0 # Peut-être géré par les bâtiments/unités

class ResourceManager:
    """
    Gère les ressources de la ville, leur stockage, et leur production/consommation,
    en tenant compte du cycle jour/nuit.
    """
    # Facteur de production basé sur la période (0.0 = arrêt, 1.0 = normal)
    PRODUCTION_MODIFIERS = {
        TimeOfDay.DAWN: 0.75, # Production commence
        TimeOfDay.DAY: 1.0,   # Production normale
        TimeOfDay.DUSK: 0.5,  # Production ralentit
        TimeOfDay.NIGHT: 0.1  # Production très faible ou nulle (maintenance?)
    }

    def __init__(self, time_manager: TimeManager):
        """
        Initialise le gestionnaire de ressources.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("ResourceManager requiert une instance de TimeManager.")
        self.time_manager = time_manager

        self.resources: Dict[ResourceType, ResourceAmount] = {
            res_type: ResourceAmount(amount=50.0, capacity=1000.0) # Valeurs initiales exemple
            for res_type in ResourceType
        }
        # Utiliser une structure plus simple si les nœuds sont juste des taux
        self.production_rates: Dict[ResourceType, float] = {
             res_type: 0.0 for res_type in ResourceType
        }
        # La consommation pourrait être calculée dynamiquement par d'autres systèmes
        self.consumption_rates: Dict[ResourceType, float] = {
             res_type: 0.0 for res_type in ResourceType
        }

    def update(self, dt: float):
        """
        Met à jour les quantités de ressources en fonction de la production (modulée par le temps)
        et de la consommation.
        """
        if self.time_manager.is_paused():
            return

        current_period = self.time_manager.get_current_period()
        production_modifier = self.PRODUCTION_MODIFIERS.get(current_period, 0.0) # 0 si période inconnue

        for res_type, res_amount in self.resources.items():
            # Production effective basée sur le taux de base et le modificateur jour/nuit
            effective_production = self.production_rates[res_type] * production_modifier
            consumption = self.consumption_rates[res_type] # Taux de consommation actuel

            # Calculer le changement net
            net_change = (effective_production - consumption) * dt

            # Mettre à jour la quantité, en respectant les limites 0 et capacité
            new_amount = res_amount.amount + net_change
            res_amount.amount = max(0.0, min(new_amount, res_amount.capacity))

            # Optionnel: Afficher les changements pour le débogage
            # if net_change != 0:
            #     print(f"{res_type.name}: {res_amount.amount:.2f}/{res_amount.capacity:.0f} ({net_change/dt:+.2f}/s)")


    def add_production_source(self, resource_type: ResourceType, rate: float) -> bool:
        """Ajoute un taux de production pour une ressource."""
        if resource_type not in self.resources:
            print(f"Erreur: Type de ressource inconnu {resource_type}")
            return False
        self.production_rates[resource_type] += rate
        print(f"Production de {resource_type.name} augmentée de {rate}. Total: {self.production_rates[resource_type]}")
        return True

    def remove_production_source(self, resource_type: ResourceType, rate: float) -> bool:
        """Retire un taux de production pour une ressource."""
        if resource_type not in self.resources:
            print(f"Erreur: Type de ressource inconnu {resource_type}")
            return False
        if self.production_rates[resource_type] >= rate:
            self.production_rates[resource_type] -= rate
            print(f"Production de {resource_type.name} diminuée de {rate}. Total: {self.production_rates[resource_type]}")
            return True
        else:
            print(f"Avertissement: Tentative de retirer plus de production ({rate}) que le taux actuel ({self.production_rates[resource_type]}) pour {resource_type.name}.")
            self.production_rates[resource_type] = 0.0 # Mettre à zéro pour éviter négatif
            return False

    def set_consumption_rate(self, resource_type: ResourceType, rate: float) -> bool:
         """Définit le taux de consommation pour une ressource."""
         if resource_type not in self.resources:
             print(f"Erreur: Type de ressource inconnu {resource_type}")
             return False
         if rate < 0:
             print("Erreur: Le taux de consommation ne peut pas être négatif.")
             return False
         self.consumption_rates[resource_type] = rate
         # print(f"Consommation de {resource_type.name} définie à {rate}/s.")
         return True

    def get_resource_amount(self, resource_type: ResourceType) -> float:
        """Retourne la quantité actuelle d'une ressource."""
        return self.resources.get(resource_type, ResourceAmount(0.0, 0.0)).amount

    def get_resource_capacity(self, resource_type: ResourceType) -> float:
        """Retourne la capacité de stockage d'une ressource."""
        return self.resources.get(resource_type, ResourceAmount(0.0, 0.0)).capacity

    def has_enough(self, resource_type: ResourceType, amount_needed: float) -> bool:
        """Vérifie s'il y a suffisamment d'une ressource."""
        return self.get_resource_amount(resource_type) >= amount_needed

    def consume_resource(self, resource_type: ResourceType, amount: float) -> bool:
        """Tente de consommer une quantité d'une ressource. Retourne True si réussi."""
        if self.has_enough(resource_type, amount):
            self.resources[resource_type].amount -= amount
            return True
        return False

    def add_resource(self, resource_type: ResourceType, amount: float) -> float:
        """Ajoute une quantité d'une ressource, sans dépasser la capacité. Retourne la quantité ajoutée."""
        if resource_type not in self.resources: return 0.0
        res = self.resources[resource_type]
        amount_to_add = max(0.0, amount)
        space_available = res.capacity - res.amount
        actual_added = min(amount_to_add, space_available)
        res.amount += actual_added
        return actual_added
        self.production_nodes[resource_type].append(node)
        return True
        
    def remove_production_node(self, resource_type: ResourceType, node) -> bool:
        if resource_type not in self.resources:
            return False
        try:
            self.production_nodes[resource_type].remove(node)
            return True
        except ValueError:
            return False