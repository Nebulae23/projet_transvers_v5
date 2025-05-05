from .ability_base import AbilityBase
from ...ecs.components.ability_stats import AbilityStats
from ...combat.trajectory import TrajectoryType

class MaceHit(AbilityBase):
    """
    Attaque de mêlée du Cleric qui inflige des dégâts et soigne légèrement le lanceur.
    """
    def __init__(self, entity_id: int):
        super().__init__(
            entity_id=entity_id,
            name="Mace Hit",
            description="Frappe un ennemi proche avec une masse, infligeant des dégâts et restaurant une petite quantité de santé.",
            stats=AbilityStats(
                damage=15,          # Dégâts moyens
                heal_amount=5,      # Effet de soin
                range=2.0,          # Portée courte
                cooldown=1.5,
                cast_time=0.5,
                mana_cost=10
            ),
            trajectory_type=TrajectoryType.MELEE, # Pas de projectile, effet direct
            icon="assets/icons/abilities/cleric/mace_hit.png" # Chemin d'icône placeholder
        )

    def activate(self, world, target_pos=None):
        """
        Logique d'activation de Mace Hit.
        Applique les dégâts à la cible et le soin au lanceur.
        (La logique détaillée sera implémentée dans le CombatSystem)
        """
        print(f"Entity {self.entity_id} uses Mace Hit!")
        # La logique de dégâts/soin sera gérée par le CombatSystem
        # basé sur les stats et la détection de collision/portée.
        pass

# Ajouter d'autres capacités du Cleric ici si nécessaire