# src/engine/combat/abilities/warrior_abilities.py
from .ability_base import AbilityBase
# Importer d'autres modules nécessaires, par exemple pour les patterns et effets
# from ..patterns.arc_pattern import ArcPattern # Exemple, à adapter si nécessaire
# from ...fx.effect_manager import EffectManager # Exemple

class AxeSlash(AbilityBase):
    """
    Capacité d'attaque en mêlée pour le Guerrier.
    Inflige des dégâts dans un arc devant le personnage.
    """
    def __init__(self, owner_entity):
        super().__init__(
            owner_entity=owner_entity,
            name="Axe Slash",
            description="Une attaque rapide en arc de cercle.",
            cooldown=1.5,  # Cooldown moyen
            range=50,      # Courte portée
            damage=25,     # Dégâts élevés
            mana_cost=0
        )
        # Définir le pattern de la trajectoire (ex: un arc)
        # self.trajectory_pattern = ArcPattern(angle=90, radius=self.range) # Exemple
        self.visual_effect = "axe_slash_effect" # Nom de l'effet visuel à charger

    def activate(self, world, target_position):
        """
        Active la capacité Axe Slash.
        """
        print(f"{self.owner_entity.name} utilise {self.name}!")
        # Logique d'activation :
        # 1. Vérifier le cooldown et le mana (géré par AbilityBase ou CombatSystem)
        # 2. Déterminer la zone d'effet basée sur la position et l'orientation du lanceur
        # 3. Trouver les entités dans la zone d'effet
        # 4. Appliquer les dégâts aux entités touchées
        # 5. Jouer l'effet visuel (ex: via EffectManager)
        # world.effect_manager.spawn_effect(self.visual_effect, self.owner_entity.position, ...)
        # 6. Mettre la capacité en cooldown (géré par AbilityBase ou CombatSystem)

        # --- Logique simplifiée pour l'exemple ---
        # Simuler la recherche d'ennemis dans la zone (à remplacer par la vraie logique ECS)
        enemies_in_range = self._find_enemies_in_arc(world)
        for enemy in enemies_in_range:
            # Appliquer les dégâts (simplifié)
            print(f"   -> Touche {enemy.name} pour {self.damage} dégâts.")
            # Ici, il faudrait interagir avec le CombatSystem ou les composants de l'ennemi
            # enemy.get_component('Health').take_damage(self.damage)

        # Jouer l'effet visuel (simulation)
        print(f"   -> Effet visuel '{self.visual_effect}' joué.")

        # Mettre en cooldown (géré par le système appelant)
        self.start_cooldown()
        return True # Succès

    def _find_enemies_in_arc(self, world):
        """
        Méthode privée (exemple) pour trouver les ennemis dans l'arc d'attaque.
        Devrait utiliser le système de requêtes ECS du 'world'.
        """
        # Logique de détection de collision en arc (à implémenter)
        print("   -> Recherche d'ennemis dans l'arc...")
        # Retourne une liste vide pour l'exemple
        return []

    def update(self, dt):
        """
        Mise à jour de la capacité (par exemple, pour les effets continus).
        """
        super().update(dt)
        # Logique de mise à jour spécifique si nécessaire

# Ajouter d'autres capacités du guerrier ici si besoin