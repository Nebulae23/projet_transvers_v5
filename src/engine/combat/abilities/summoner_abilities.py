from .ability_base import AbilityBase
from ...ecs.components.ability_stats import AbilityStats
from ...combat.trajectory import TrajectoryType

class SpiritSummon(AbilityBase):
    """
    Capacité du Summoner pour invoquer un esprit combattant.
    """
    def __init__(self, entity_id: int):
        super().__init__(
            entity_id=entity_id,
            name="Summon Spirit",
            description="Invoque un esprit allié qui combat aux côtés du lanceur pendant une durée limitée.",
            stats=AbilityStats(
                # Les dégâts sont infligés par l'esprit invoqué, pas directement par cette capacité.
                # On pourrait mettre des stats pour l'esprit ici, ou les gérer séparément.
                damage=0, # La capacité elle-même n'inflige pas de dégâts directs.
                range=5.0, # Portée pour l'invocation initiale
                cooldown=30.0,
                cast_time=1.5,
                mana_cost=60,
                duration=20.0 # Durée de vie de l'esprit invoqué
                # Ajouter potentiellement des stats spécifiques à l'invocation (PV, dégâts de l'esprit, etc.)
            ),
            # L'acte d'invoquer n'a pas de trajectoire propre.
            trajectory_type=TrajectoryType.PLACEMENT,
            icon="assets/icons/abilities/summoner/spirit_summon.png" # Placeholder
        )

    def activate(self, world, target_pos=None):
        """
        Logique d'activation pour invoquer l'esprit.
        Le CombatSystem créera une nouvelle entité pour l'esprit.
        """
        print(f"Entity {self.entity_id} summons a Spirit!")
        # La logique de création de l'entité esprit et de son IA
        # sera gérée par le CombatSystem ou un système d'invocation dédié.
        pass

# Ajouter d'autres capacités du Summoner ici si nécessaire