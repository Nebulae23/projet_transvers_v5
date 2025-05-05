# src/engine/combat/abilities/mage_abilities.py
from .ability_base import AbilityBase
from ..patterns.straight_line import StraightLinePattern # Assurez-vous que ce chemin est correct
from ..trajectories.trajectory_system import TrajectorySystem # Ou ProjectilePool si utilisé

class MagicBolt(AbilityBase):
    """
    Capacité de projectile magique pour le Mage.
    Lance un projectile en ligne droite vers la cible.
    """
    def __init__(self, owner_entity):
        super().__init__(
            owner_entity=owner_entity,
            name="Magic Bolt",
            description="Lance un projectile d'énergie magique.",
            cooldown=0.8,  # Cooldown court
            range=250,     # Longue portée
            damage=15,     # Dégâts moyens
            mana_cost=10   # Coûte du mana
        )
        # Le pattern est utilisé par le système de trajectoire pour créer le projectile
        self.trajectory_pattern = StraightLinePattern()
        self.projectile_speed = 300 # Vitesse du projectile
        self.visual_effect = "magic_bolt_effect" # Effet visuel du projectile
        self.launch_effect = "magic_bolt_launch" # Effet au lancement

    def activate(self, world, target_position):
        """
        Active la capacité Magic Bolt.
        """
        print(f"{self.owner_entity.name} lance {self.name} vers {target_position}!")
        # Logique d'activation :
        # 1. Vérifier le cooldown et le mana (géré par AbilityBase ou CombatSystem)
        # 2. Calculer la direction du projectile
        # 3. Demander au TrajectorySystem de lancer un projectile
        # 4. Jouer l'effet visuel de lancement
        # 5. Mettre la capacité en cooldown

        # --- Logique simplifiée pour l'exemple ---
        # Assurez-vous que l'entité propriétaire a un composant Transform
        transform_comp = self.owner_entity.get_component('Transform')
        if not transform_comp:
             print(f"   -> ERREUR: Le propriétaire {self.owner_entity.name} n'a pas de composant Transform.")
             return False

        start_pos = transform_comp.position # Position du lanceur

        # Assurez-vous que target_position est un vecteur ou peut être soustrait
        try:
            direction = (target_position - start_pos).normalize() # Calculer le vecteur direction normalisé
        except AttributeError:
             # Si target_position n'est pas un vecteur compatible (ex: tuple), essayez de le convertir
             # Ceci dépend de votre implémentation de vecteur (ex: pygame.Vector2)
             try:
                 from pygame import Vector2 # Exemple avec Pygame
                 target_vec = Vector2(target_position)
                 start_vec = Vector2(start_pos) # Assurez-vous que start_pos est aussi compatible
                 if (target_vec - start_vec).length_squared() > 0: # Éviter la division par zéro
                     direction = (target_vec - start_vec).normalize()
                 else:
                     direction = Vector2(1, 0) # Direction par défaut si la cible est sur le lanceur
             except Exception as e:
                 print(f"   -> ERREUR: Impossible de calculer la direction vers {target_position}. Erreur: {e}")
                 return False


        # Utiliser le système de trajectoire pour créer le projectile
        trajectory_system = world.get_system(TrajectorySystem) # Obtenir le système
        if trajectory_system:
            trajectory_system.create_projectile(
                pattern=self.trajectory_pattern,
                start_position=start_pos,
                direction=direction,
                speed=self.projectile_speed,
                range=self.range,
                damage=self.damage,
                owner_entity=self.owner_entity,
                visual_effect_key=self.visual_effect # Clé pour l'asset du projectile
            )
            print(f"   -> Projectile '{self.visual_effect}' lancé.")
        else:
            print("   -> ERREUR: TrajectorySystem non trouvé.")
            return False # Échec si le système n'existe pas

        # Jouer l'effet visuel de lancement (simulation)
        print(f"   -> Effet de lancement '{self.launch_effect}' joué.")
        # world.effect_manager.spawn_effect(self.launch_effect, start_pos, ...)

        # Mettre en cooldown (géré par le système appelant)
        self.start_cooldown()
        return True # Succès

    def update(self, dt):
        """
        Mise à jour de la capacité.
        """
        super().update(dt)
        # Logique de mise à jour spécifique si nécessaire

# Ajouter d'autres capacités du mage ici si besoin