# -*- coding: utf-8 -*-
"""
Module définissant les bâtiments défensifs de la ville.
"""

from .building_base import BuildingBase, BuildingState
from abc import abstractmethod

class DefenseBuilding(BuildingBase):
    """Classe de base pour les bâtiments défensifs."""
    def __init__(self, name: str, level: int = 1, max_level: int = 5,
                 cost: dict[str, int] = None, build_time: float = 10.0,
                 initial_health: int = 100, max_health: int = 100,
                 attack_range: float = 0.0, attack_damage: float = 0.0,
                 attack_speed: float = 0.0): # Attaques par seconde
        super().__init__(name, level, max_level, cost, build_time, initial_health, max_health)
        self.attack_range = attack_range
        self.attack_damage = attack_damage
        self.attack_speed = attack_speed

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
    def get_range_for_level(self, level: int) -> float:
        """Retourne la portée pour un niveau donné."""
        pass

    @abstractmethod
    def get_damage_for_level(self, level: int) -> float:
        """Retourne les dégâts pour un niveau donné."""
        pass

    @abstractmethod
    def get_attack_speed_for_level(self, level: int) -> float:
        """Retourne la vitesse d'attaque pour un niveau donné."""
        pass

    def update_level_dependent_stats(self):
        """Met à jour les statistiques dépendantes du niveau (portée, dégâts, vitesse)."""
        self.attack_range = self.get_range_for_level(self.level)
        self.attack_damage = self.get_damage_for_level(self.level)
        self.attack_speed = self.get_attack_speed_for_level(self.level)
        # Mettre à jour aussi max_health si nécessaire

    def _complete_construction_or_upgrade(self):
        """Termine la construction/amélioration et met à jour les stats."""
        super()._complete_construction_or_upgrade()
        if self.state == BuildingState.OPERATIONAL:
            self.update_level_dependent_stats()
            print(f"{self.name} (Niveau {self.level}) - Portée: {self.attack_range}, Dégâts: {self.attack_damage}, Vitesse: {self.attack_speed}/s")

    def get_description(self) -> str:
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        stats_info = ""
        if self.attack_range > 0:
            stats_info += f"Portée: {self.attack_range:.1f}. "
        if self.attack_damage > 0:
            stats_info += f"Dégâts: {self.attack_damage:.1f}. "
        if self.attack_speed > 0:
            stats_info += f"Vitesse: {self.attack_speed:.1f}/s. "

        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. {stats_info}"

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
            "attack_range": self.attack_range,
            "attack_damage": self.attack_damage,
            "attack_speed": self.attack_speed,
            "cost_next_level": self.get_cost_for_level(self.level + 1) if self.level < self.max_level else None,
            "build_time_next_level": self.get_build_time_for_level(self.level + 1) if self.level < self.max_level else None,
        })
        return info

# --- Bâtiments Défensifs Spécifiques ---

class WatchTower(DefenseBuilding):
    """Tour de guet : augmente la portée de vision ou détecte les ennemis."""
    def __init__(self, level: int = 1):
        # La tour de guet n'attaque pas, elle détecte. On met les stats d'attaque à 0.
        super().__init__(name="Tour de Guet", level=level, max_level=8,
                         initial_health=120, max_health=120,
                         attack_damage=0, attack_speed=0) # Range sera spécifique
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats() # Pour la portée de détection

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 70, 'stone': 30}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 70 * (1.4**(target_level - 1))
        stone_cost = 30 * (1.3**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 18.0 * (1.2**(target_level - 1))

    def get_range_for_level(self, level: int) -> float:
        # Représente la portée de détection
        return 15.0 * (1.15**(level - 1))

    def get_damage_for_level(self, level: int) -> float:
        return 0.0 # Ne fait pas de dégâts

    def get_attack_speed_for_level(self, level: int) -> float:
        return 0.0 # N'attaque pas

    def get_description(self) -> str:
        # Surcharge pour une description plus appropriée
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        detect_info = f"Portée de détection: {self.attack_range:.1f}."
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. {detect_info}"

    def get_ui_info(self) -> dict:
        info = super().get_ui_info()
        info["detection_range"] = info.pop("attack_range") # Renomme pour la clarté
        info.pop("attack_damage")
        info.pop("attack_speed")
        return info
class ArcherTower(DefenseBuilding):
    """Tour d'archer : attaque les ennemis à distance."""
    def __init__(self, level: int = 1):
        super().__init__(name="Tour d'Archer", level=level, max_level=12,
                         initial_health=180, max_health=180)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats()

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 100, 'stone': 50}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 100 * (1.5**(target_level - 1))
        stone_cost = 50 * (1.4**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 22.0 * (1.25**(target_level - 1))

    def get_range_for_level(self, level: int) -> float:
        return 10.0 * (1.1**(level - 1))

    def get_damage_for_level(self, level: int) -> float:
        return 8.0 * (1.2**(level - 1))

    def get_attack_speed_for_level(self, level: int) -> float:
        # Vitesse d'attaque augmente légèrement avec le niveau
        return 0.8 * (1.05**(level - 1))


class Wall(DefenseBuilding):
    """Mur : défense passive avec beaucoup de points de vie."""
    def __init__(self, level: int = 1):
        # Les murs n'attaquent pas et n'ont pas de portée.
        super().__init__(name="Mur", level=level, max_level=20,
                         initial_health=500, max_health=500, # Haute santé initiale
                         attack_range=0, attack_damage=0, attack_speed=0)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.update_level_dependent_stats() # Pour mettre à jour max_health si besoin

    def _get_default_cost(self) -> dict[str, int]:
        return {'stone': 100} # Principalement de la pierre

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        stone_cost = 100 * (1.7**(target_level - 1))
        # Peut-être ajouter un peu de bois aux niveaux supérieurs ?
        wood_cost = 10 * (1.2**(target_level - 1)) if target_level > 5 else 0
        return {'stone': int(stone_cost), 'wood': int(wood_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 30.0 * (1.3**(target_level - 1))

    def get_range_for_level(self, level: int) -> float:
        return 0.0

    def get_damage_for_level(self, level: int) -> float:
        return 0.0

    def get_attack_speed_for_level(self, level: int) -> float:
        return 0.0

    def update_level_dependent_stats(self):
        """Met à jour la santé maximale du mur."""
        self.max_health = int(500 * (1.4**(self.level - 1)))
        # Assurer que la santé actuelle ne dépasse pas la nouvelle max_health
        self.health = min(self.health, self.max_health)

    def get_description(self) -> str:
        # Surcharge pour une description plus appropriée
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}."

    def get_ui_info(self) -> dict:
        info = super().get_ui_info()
        info.pop("attack_range")
        info.pop("attack_damage")
        info.pop("attack_speed")
        return info


class Trap(DefenseBuilding):
    """Piège : défense active qui se déclenche au passage d'ennemis."""
    def __init__(self, level: int = 1):
        # Les pièges ont des dégâts mais pas de portée/vitesse d'attaque conventionnelles.
        # Ils pourraient avoir un temps de réarmement.
        super().__init__(name="Piège", level=level, max_level=10,
                         initial_health=50, max_health=50, # Faible santé, car consommable ou caché
                         attack_range=0, attack_speed=0)
        self.cost = self.get_cost_for_level(level)
        self.build_time = self.get_build_time_for_level(level)
        self.is_armed = True # Le piège est-il prêt à se déclencher ?
        self.rearm_time = self.get_rearm_time_for_level(level) # Temps pour se réarmer
        self._rearm_progress = 0.0
        self.update_level_dependent_stats() # Pour les dégâts

    def _get_default_cost(self) -> dict[str, int]:
        return {'wood': 30, 'stone': 10}

    def get_cost_for_level(self, target_level: int) -> dict[str, int]:
        wood_cost = 30 * (1.3**(target_level - 1))
        stone_cost = 10 * (1.2**(target_level - 1))
        return {'wood': int(wood_cost), 'stone': int(stone_cost)}

    def get_build_time_for_level(self, target_level: int) -> float:
        return 10.0 * (1.1**(target_level - 1)) # Rapide à construire/améliorer

    def get_range_for_level(self, level: int) -> float:
        return 0.0 # Se déclenche au contact

    def get_damage_for_level(self, level: int) -> float:
        # Dégâts infligés lors du déclenchement
        return 50.0 * (1.4**(level - 1))

    def get_attack_speed_for_level(self, level: int) -> float:
        return 0.0 # Non applicable

    def get_rearm_time_for_level(self, level: int) -> float:
        # Temps nécessaire pour que le piège soit à nouveau actif
        # Diminue légèrement avec le niveau
        return max(5.0, 30.0 * (0.9**(level - 1)))

    def update_rearm(self, delta_time: float):
        """Met à jour le processus de réarmement."""
        if not self.is_armed and self.state == BuildingState.OPERATIONAL:
            self._rearm_progress += delta_time
            if self._rearm_progress >= self.rearm_time:
                self.is_armed = True
                self._rearm_progress = 0.0
                print(f"{self.name} (Niveau {self.level}) est réarmé.")

    def trigger(self, target):
        """Déclenche le piège sur une cible."""
        if self.is_armed and self.state == BuildingState.OPERATIONAL:
            print(f"{self.name} déclenché sur {target}!")
            # Appliquer les dégâts à la cible (logique à implémenter ailleurs)
            damage = self.get_damage_for_level(self.level)
            print(f"Inflige {damage:.1f} dégâts.")
            # target.take_damage(damage) # Exemple d'appel

            self.is_armed = False
            self._rearm_progress = 0.0
            print(f"Réarmement dans {self.rearm_time:.1f}s.")
            # Optionnel : le piège peut être détruit après usage
            # self.state = BuildingState.DESTROYED
            # self.health = 0
            return damage
        return 0 # Pas de dégâts si non armé ou non opérationnel

    def get_description(self) -> str:
        state_desc = {
            BuildingState.UNDER_CONSTRUCTION: f"En construction (Niveau {self.level + (1 if self._construction_progress > 0 else 0)})",
            BuildingState.OPERATIONAL: f"Opérationnel (Niveau {self.level})",
            BuildingState.DAMAGED: f"Endommagé (Niveau {self.level})",
            BuildingState.DESTROYED: "Détruit"
        }.get(self.state, "Inconnu")
        armed_status = "Armé" if self.is_armed else f"Réarmement ({self._rearm_progress:.1f}/{self.rearm_time:.1f}s)"
        damage_info = f"Dégâts: {self.get_damage_for_level(self.level):.1f}."
        return f"{self.name} [{state_desc}] Santé: {self.health}/{self.max_health}. {armed_status}. {damage_info}"

    def get_ui_info(self) -> dict:
        info = super().get_ui_info()
        info["trigger_damage"] = info.pop("attack_damage")
        info["is_armed"] = self.is_armed
        info["rearm_time"] = self.rearm_time
        info.pop("attack_range")
        info.pop("attack_speed")
        return info

    def _complete_construction_or_upgrade(self):
        """Termine la construction/amélioration et met à jour les stats."""
        super()._complete_construction_or_upgrade()
        if self.state == BuildingState.OPERATIONAL:
            self.rearm_time = self.get_rearm_time_for_level(self.level)
            self.update_level_dependent_stats() # Met à jour les dégâts
            self.is_armed = True # S'assurer qu'il est armé après construction/amélioration
            self._rearm_progress = 0.0
            print(f"{self.name} (Niveau {self.level}) - Dégâts: {self.attack_damage}, Réarmement: {self.rearm_time}s")