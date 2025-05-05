# src/engine/combat/combat_system.py
from typing import List, Dict, Type
import numpy as np
from ..ecs.entity import Entity
# Importer les nouveaux composants
from ..ecs.components import Transform, Health, TrajectoryProjectile, Attack, Defense
from ..ecs.world import World # Importer World pour l'annotation de type
from .ability import Ability

class CombatSystem:
    def __init__(self, world: World):
        self.world = world
        # self.active_projectiles: List[Entity] = [] # Retiré, géré par le world
        self.active_abilities: Dict[Entity, List[Ability]] = {}

    def register_entity_abilities(self, entity: Entity, abilities: List[Ability]):
        """Register abilities for an entity."""
        self.active_abilities[entity] = abilities

    def update(self, dt: float):
        """Update combat system state."""
        self._update_abilities(dt)
        self._update_projectiles(dt)
        self._check_collisions()
        self._check_melee_attacks(dt) # Ajouter la vérification des attaques de mêlée

    def _update_abilities(self, dt: float):
        """Update ability cooldowns."""
        for entity, abilities in list(self.active_abilities.items()): # Utiliser list() pour itérer sur une copie si la suppression est possible
            if not self.world.has_entity(entity): # Vérifier si l'entité existe toujours
                del self.active_abilities[entity]
                continue
            for ability in abilities:
                ability.update(dt)

    def _update_projectiles(self, dt: float):
        """Update projectile positions and check lifetime."""
        # Utiliser list() pour itérer sur une copie car des entités peuvent être supprimées
        for projectile in list(self.world.get_entities_with_component(TrajectoryProjectile)):
            if not self.world.has_entity(projectile): # Vérifier si le projectile existe toujours
                continue

            transform = projectile.get_component(Transform)
            trajectory = projectile.get_component(TrajectoryProjectile)

            if not transform or not trajectory:
                continue

            # Update position based on velocity and acceleration
            transform.position += trajectory.velocity * dt
            trajectory.velocity += trajectory.acceleration * dt

            # Update lifetime
            trajectory.lifetime -= dt
            if trajectory.lifetime <= 0:
                self.world.remove_entity(projectile)

    def _check_collisions(self):
        """Check for collisions between projectiles and entities."""
        projectiles = list(self.world.get_entities_with_component(TrajectoryProjectile))
        targets = list(self.world.get_entities_with_component(Health))

        for projectile in projectiles:
            # Vérifier si le projectile existe toujours (peut avoir été supprimé par une autre collision dans la même frame)
            if not self.world.has_entity(projectile):
                continue

            proj_transform = projectile.get_component(Transform)
            proj_trajectory = projectile.get_component(TrajectoryProjectile)

            if not proj_transform or not proj_trajectory:
                continue

            for target in targets:
                # Vérifier si la cible existe toujours et n'est pas le projectile lui-même
                if not self.world.has_entity(target) or projectile == target:
                    continue

                target_transform = target.get_component(Transform)
                target_health = target.get_component(Health)
                target_defense = target.get_component(Defense) # Obtenir le composant Defense

                if not target_transform or not target_health:
                    continue

                # Simple circle collision check (utiliser un rayon configurable ?)
                # TODO: Utiliser des composants Collider pour des formes plus complexes
                collision_radius = 15.0 # Exemple de rayon
                distance = np.linalg.norm(
                    target_transform.position - proj_transform.position
                )

                if distance < collision_radius:
                    # Calculer les dégâts en tenant compte de la défense
                    raw_damage = proj_trajectory.damage
                    armor = target_defense.armor if target_defense else 0.0
                    actual_damage = max(0.0, raw_damage - armor) # Dégâts minimum de 0

                    # Appliquer les dégâts
                    if actual_damage > 0:
                        target_health.take_damage(actual_damage)
                        print(f"Entity {target.entity_id} took {actual_damage:.2f} damage from projectile. Health: {target_health.current_health:.2f}")
                        if target_health.current_health <= 0:
                            print(f"Entity {target.entity_id} defeated.")
                            self.world.remove_entity(target) # Supprimer l'entité si sa santé est à 0

                    # Supprimer le projectile après la collision
                    self.world.remove_entity(projectile)
                    # Passer au projectile suivant car celui-ci est détruit
                    break

    def _check_melee_attacks(self, dt: float):
        """Check for melee attacks between entities."""
        # Get entities that can attack (have all three components)
        attackers = []
        entities_with_transform = self.world.get_entities_with_component(Transform)
        for entity in entities_with_transform:
            if entity.has_component(Attack) and entity.has_component(Health):
                attackers.append(entity)
        
        # Get potential targets (entities with Transform and Health)
        targets = []
        for entity in entities_with_transform:
            if entity.has_component(Health):
                targets.append(entity)

        # Use the current time from the dt parameter rather than a resource
        current_time = dt  # Use elapsed time instead of a time resource

        for attacker in attackers:
             # Vérifier si l'attaquant existe toujours
            if not self.world.has_entity(attacker):
                continue

            attacker_transform = attacker.get_component(Transform)
            attacker_attack = attacker.get_component(Attack)
            attacker_health = attacker.get_component(Health)

            # Ne pas attaquer si l'attaquant est mort
            if attacker_health.current_health <= 0:
                continue

            # Vérifier le cooldown de l'attaque
            if current_time < attacker_attack.last_attack_time + (1.0 / attacker_attack.attack_speed):
                 continue # Attaque en cooldown

            for target in targets:
                 # Vérifier si la cible existe toujours et n'est pas l'attaquant lui-même
                if not self.world.has_entity(target) or attacker == target:
                    continue

                target_transform = target.get_component(Transform)
                target_health = target.get_component(Health)
                target_defense = target.get_component(Defense)

                if not target_transform or not target_health:
                    continue

                # Vérifier la portée de l'attaque
                distance = np.linalg.norm(target_transform.position - attacker_transform.position)

                if distance <= attacker_attack.attack_range:
                    # L'attaque est à portée, vérifier le cooldown et attaquer
                    if current_time >= attacker_attack.last_attack_time + (1.0 / attacker_attack.attack_speed):

                        # Calculer les dégâts
                        raw_damage = attacker_attack.damage
                        armor = target_defense.armor if target_defense else 0.0
                        actual_damage = max(0.0, raw_damage - armor)

                        if actual_damage > 0:
                            target_health.take_damage(actual_damage)
                            print(f"Entity {target.entity_id} took {actual_damage:.2f} melee damage from {attacker.entity_id}. Health: {target_health.current_health:.2f}")
                            if target_health.current_health <= 0:
                                print(f"Entity {target.entity_id} defeated by {attacker.entity_id}.")
                                self.world.remove_entity(target)

                        # Mettre à jour le temps de la dernière attaque
                        attacker_attack.last_attack_time = current_time

                        # En mêlée, une attaque peut toucher plusieurs cibles à portée si désiré,
                        # mais ici on arrête après la première cible touchée pour simplifier.
                        # Si on veut toucher plusieurs cibles, il ne faut pas break.
                        break # L'attaquant a touché une cible, passe à l'attaquant suivant


    def use_ability(self,
                   caster: Entity,
                   ability_index: int,
                   target_pos: np.ndarray) -> bool:
        """Use an ability if possible."""
        if not self.world.has_entity(caster) or caster not in self.active_abilities:
            print(f"Debug: Caster {caster.entity_id if caster else 'None'} not found or has no abilities.")
            return False

        abilities = self.active_abilities[caster]
        if ability_index < 0 or ability_index >= len(abilities):
            print(f"Debug: Invalid ability index {ability_index} for caster {caster.entity_id}.")
            return False

        ability = abilities[ability_index]
        if not ability.can_use():
            print(f"Debug: Ability {ability.name} cannot be used by caster {caster.entity_id} (cooldown?).")
            return False

        # Utiliser la capacité et récupérer les projectiles créés (ou autres effets)
        # La méthode use de l'ability devrait maintenant retourner une liste d'entités créées (projectiles)
        created_entities = ability.use(caster, target_pos, self.world) # Passer le world à l'ability

        # Ajouter les entités créées (projectiles) au monde
        for entity in created_entities:
            # L'ajout se fait maintenant potentiellement dans ability.use ou nécessite une méthode world.add_entity
            # Assumons que ability.use ajoute déjà l'entité au monde si nécessaire,
            # ou que le world a une méthode pour cela.
            # Si ability.use ne fait que créer l'objet Entity, il faut l'ajouter ici :
            if not self.world.has_entity(entity):
                 self.world.add_entity(entity) # Assurez-vous que World a cette méthode
            print(f"Debug: Caster {caster.entity_id} used ability {ability.name}, created entity {entity.entity_id}.")


        # self.active_projectiles.append(projectile) # Retiré
        # self.world.entities.append(projectile) # Remplacé par world.add_entity si nécessaire

        return True

    def cleanup(self):
        """Clean up resources used by the combat system."""
        # Clear active abilities
        self.active_abilities.clear()
        print("Combat system cleaned up")