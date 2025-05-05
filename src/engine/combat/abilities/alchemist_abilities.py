from .ability_base import AbilityBase
from ...ecs.components.ability_stats import AbilityStats
from ...combat.trajectory import TrajectoryType

class Turret(AbilityBase):
    """
    Capacité de l'Alchemist permettant de placer une tourelle autonome.
    """
    def __init__(self, entity_id: int):
        super().__init__(
            entity_id=entity_id,
            name="Deploy Turret",
            description="Place une tourelle qui tire automatiquement sur les ennemis à proximité.",
            stats=AbilityStats(
                damage=5,           # Dégâts faibles par tir
                range=15.0,         # Portée de la tourelle
                cooldown=25.0,      # Long cooldown pour le placement
                cast_time=1.0,
                mana_cost=50,
                duration=30.0,      # Longue durée de la tourelle
                attack_speed=1.0    # Tirs par seconde de la tourelle
            ),
            # La tourelle elle-même utilisera une trajectoire (ex: STRAIGHT_LINE)
            # mais l'acte de placer la tourelle n'a pas de trajectoire propre.
            trajectory_type=TrajectoryType.PLACEMENT,
            icon="assets/icons/abilities/alchemist/turret.png" # Placeholder
        )

    def activate(self, world, target_pos=None):
        """
        Logique d'activation pour placer la tourelle.
        Le CombatSystem créera une nouvelle entité tourelle.
        """
        print(f"Entity {self.entity_id} deploys a Turret at {target_pos}!")
        # La logique de création de l'entité tourelle sera gérée
        # par le CombatSystem ou un système dédié.
        pass

# Ajouter d'autres capacités de l'Alchemist ici si nécessaire