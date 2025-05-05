import abc
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.engine.ecs.world import World
    from src.engine.ecs.components import AbilityStats, Cooldown, Targeting

class AbilityBase(abc.ABC):
    """Classe de base abstraite pour toutes les capacités du jeu."""

    def __init__(self, entity_id: int, world: 'World', stats: 'AbilityStats', cooldown: 'Cooldown', targeting: 'Targeting'):
        """
        Initialise la capacité de base.

        Args:
            entity_id: L'ID de l'entité qui possède cette capacité.
            world: L'instance du monde ECS.
            stats: Les statistiques de la capacité (coût, dégâts de base, etc.).
            cooldown: Le composant de gestion du temps de recharge.
            targeting: Le composant de ciblage.
        """
        self.entity_id = entity_id
        self.world = world
        self.stats = stats
        self.cooldown = cooldown
        self.targeting = targeting

    @abc.abstractmethod
    def activate(self, target_entity_id: Optional[int] = None) -> bool:
        """
        Active la capacité.

        Args:
            target_entity_id: L'ID de l'entité cible (si applicable).

        Returns:
            True si l'activation a réussi, False sinon.
        """
        pass

    @abc.abstractmethod
    def update(self, dt: float):
        """
        Met à jour l'état de la capacité (ex: temps de recharge).

        Args:
            dt: Le temps écoulé depuis la dernière frame.
        """
        pass

    @abc.abstractmethod
    def can_activate(self) -> bool:
        """
        Vérifie si la capacité peut être activée.

        Returns:
            True si la capacité peut être activée, False sinon.
        """
        pass

    def _is_on_cooldown(self) -> bool:
        """Vérifie si la capacité est en temps de recharge."""
        return self.cooldown.is_on_cooldown()

    def _has_enough_resource(self) -> bool:
        """Vérifie si l'entité possède assez de ressources pour utiliser la capacité."""
        # Logique à implémenter pour vérifier les ressources (mana, énergie, etc.)
        # Exemple:
        # owner_stats = self.world.get_component(self.entity_id, StatsComponent)
        # return owner_stats.mana >= self.stats.mana_cost
        return True # Placeholder

    def _is_target_in_range(self, target_entity_id: int) -> bool:
        """Vérifie si la cible est à portée."""
        # Logique à implémenter pour vérifier la portée
        # Exemple:
        # owner_pos = self.world.get_component(self.entity_id, PositionComponent)
        # target_pos = self.world.get_component(target_entity_id, PositionComponent)
        # distance = calculate_distance(owner_pos, target_pos)
        # return distance <= self.stats.range
        return True # Placeholder

    def apply_effects(self, target_entity_id: int):
        """
        Applique les effets de la capacité sur la cible.
        Peut être surchargée par les classes filles.
        """
        # Logique de base pour appliquer des dégâts ou autres effets
        print(f"Applying effects of ability from {self.entity_id} to {target_entity_id}")
        # Exemple:
        # target_health = self.world.get_component(target_entity_id, HealthComponent)
        # target_health.take_damage(self.stats.damage)

    def create_projectile(self, target_position: tuple[float, float]):
        """
        Crée un projectile (pour les capacités à distance).
        Peut être surchargée par les classes filles.
        """
        print(f"Creating projectile from {self.entity_id} towards {target_position}")
        # Logique pour créer une entité projectile avec les composants nécessaires

    def create_area_effect(self, position: tuple[float, float]):
        """
        Crée un effet de zone à la position donnée.
        Peut être surchargée par les classes filles.
        """
        print(f"Creating area effect at {position} from ability of {self.entity_id}")
        # Logique pour créer une entité d'effet de zone

    def handle_animation(self):
        """
        Gère l'animation associée à la capacité.
        Peut être surchargée par les classes filles.
        """
        print(f"Handling animation for ability of {self.entity_id}")
        # Logique pour déclencher une animation sur l'entité propriétaire
        # Exemple:
        # animator = self.world.get_component(self.entity_id, AnimatorComponent)
        # animator.play_animation(self.stats.animation_name)

    def _start_cooldown(self):
        """Démarre le temps de recharge de la capacité."""
        self.cooldown.start()