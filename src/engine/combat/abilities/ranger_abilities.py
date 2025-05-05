from .ability_base import AbilityBase
from ...ecs.components.ability_stats import AbilityStats
from ...combat.trajectory import TrajectoryType

class Sniping(AbilityBase):
    """
    Capacité de tir de précision à longue portée du Ranger.
    """
    def __init__(self, entity_id: int):
        super().__init__(
            entity_id=entity_id,
            name="Sniping Shot",
            description="Tire une flèche précise à très longue distance, infligeant des dégâts massifs.",
            stats=AbilityStats(
                damage=50,          # Dégâts élevés
                range=40.0,         # Très longue portée
                cooldown=15.0,      # Long cooldown
                cast_time=2.0,      # Temps de visée/cast
                mana_cost=30
            ),
            trajectory_type=TrajectoryType.STRAIGHT_LINE, # Trajectoire directe
            icon="assets/icons/abilities/ranger/sniping.png" # Placeholder
        )

    def activate(self, world, target_pos=None):
        """
        Logique d'activation pour le tir de sniper.
        Le CombatSystem créera le projectile.
        """
        print(f"Entity {self.entity_id} uses Sniping Shot towards {target_pos}!")
        # La logique de création du projectile sera gérée par le CombatSystem
        # en utilisant les stats et la trajectoire définies.
        pass

# Ajouter d'autres capacités du Ranger ici si nécessaire