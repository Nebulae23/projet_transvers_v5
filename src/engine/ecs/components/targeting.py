import dataclasses
from enum import Enum, auto
from typing import Optional, Tuple

# Supposons l'existence d'un type EntityId, qui pourrait être un int ou un UUID
# Si ce n'est pas défini ailleurs, vous pouvez utiliser 'int' pour le moment.
# from src.engine.ecs.entity import EntityId # Décommentez si EntityId est défini
EntityId = int

class TargetingType(Enum):
    """Définit les différents types de ciblage possibles."""
    SELF = auto()       # La capacité cible le lanceur lui-même.
    ENTITY = auto()     # La capacité cible une entité spécifique.
    POSITION = auto()   # La capacité cible une position spécifique au sol/dans l'espace.
    AREA = auto()       # La capacité cible une zone autour d'une position.

@dataclasses.dataclass
class Targeting:
    """
    Gère les informations de ciblage d'une capacité.

    Attributes:
        type (TargetingType): Le type de ciblage utilisé.
        target_entity_id (Optional[EntityId]): L'ID de l'entité cible (si type est ENTITY).
        target_position (Optional[Tuple[float, float]]): La position cible (si type est POSITION ou AREA).
                                                        Utilise un tuple (x, y) ou (x, y, z).
        max_range (float): La portée maximale pour valider la cible (utilisé pour ENTITY, POSITION, AREA).
                           Pour SELF, la portée est implicitement 0.
    """
    type: TargetingType = TargetingType.SELF
    target_entity_id: Optional[EntityId] = None
    target_position: Optional[Tuple[float, float]] = None # Ou Tuple[float, float, float] pour la 3D
    max_range: float = 0.0 # La portée est définie par AbilityStats, mais peut être utile ici pour validation rapide

    def set_target_entity(self, entity_id: EntityId, current_range: float):
        """Définit une entité comme cible."""
        if self.type == TargetingType.ENTITY and current_range <= self.max_range:
            self.target_entity_id = entity_id
            self.target_position = None # Efface la position si on cible une entité
        else:
            # Gérer l'erreur ou l'invalidation (ex: log, exception, ou juste ne rien faire)
            print(f"WARN: Impossible de cibler l'entité {entity_id}. Type: {self.type}, Portée: {current_range}/{self.max_range}")
            self.target_entity_id = None


    def set_target_position(self, position: Tuple[float, float], current_range: float):
        """Définit une position comme cible."""
        if (self.type == TargetingType.POSITION or self.type == TargetingType.AREA) and current_range <= self.max_range:
            self.target_position = position
            self.target_entity_id = None # Efface l'entité si on cible une position
        else:
            # Gérer l'erreur ou l'invalidation
            print(f"WARN: Impossible de cibler la position {position}. Type: {self.type}, Portée: {current_range}/{self.max_range}")
            self.target_position = None


    def clear_target(self):
        """Réinitialise la cible."""
        self.target_entity_id = None
        self.target_position = None

    def is_target_valid(self, caster_position: Tuple[float, float], world) -> bool:
        """
        Vérifie si la cible actuelle est valide.
        NOTE: Une validation complète peut nécessiter l'accès au 'world' ECS
              pour vérifier l'existence de l'entité ou la distance réelle.

        Args:
            caster_position (Tuple[float, float]): Position actuelle du lanceur.
            world: L'instance du monde ECS (pour des vérifications plus poussées).

        Returns:
            bool: True si la cible est considérée comme valide, False sinon.
        """
        if self.type == TargetingType.SELF:
            return True # Le ciblage sur soi est toujours valide

        if self.type == TargetingType.ENTITY:
            if self.target_entity_id is None:
                return False
            # Validation plus poussée (optionnelle ici, pourrait être dans un système)
            # target_entity = world.get_entity(self.target_entity_id)
            # if target_entity is None: return False
            # distance = calculate_distance(caster_position, target_entity.position)
            # return distance <= self.max_range
            return True # Simplifié pour le moment

        if self.type == TargetingType.POSITION or self.type == TargetingType.AREA:
            if self.target_position is None:
                return False
            # Validation plus poussée (optionnelle ici)
            # distance = calculate_distance(caster_position, self.target_position)
            # return distance <= self.max_range
            return True # Simplifié pour le moment

        return False # Type de ciblage inconnu ou invalide

# Helper function (exemple, à placer où c'est pertinent)
# import math
# def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
#    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)