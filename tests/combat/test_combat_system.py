# tests/combat/test_combat_system.py
import unittest
import sys
import os
import numpy as np

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from engine.ecs.world import World
from engine.ecs.entity import Entity
from engine.ecs.components import Transform, Health, Attack, Defense, TrajectoryProjectile
from engine.combat.combat_system import CombatSystem
from engine.combat.ability import SimpleProjectileAbility # Importer la capacité de test

class TestCombatSystemECS(unittest.TestCase):

    def setUp(self):
        """Initialise un monde ECS et le système de combat pour chaque test."""
        self.world = World()
        # Ajouter une ressource 'time' simulée au monde
        self.world.add_resource('time', 0.0)
        self.combat_system = CombatSystem(self.world)

        # Créer une entité attaquante (mêlée)
        self.attacker = self.world.create_entity()
        self.attacker.add_component(Transform(position=np.array([0.0, 0.0])))
        self.attacker.add_component(Health(current_health=100.0, max_health=100.0))
        self.attacker.add_component(Attack(damage=25.0, attack_range=15.0, attack_speed=1.0)) # 1 attaque/sec
        self.attacker.add_component(Defense(armor=5.0))

        # Créer une entité défenseur
        self.defender = self.world.create_entity()
        self.defender.add_component(Transform(position=np.array([10.0, 0.0]))) # À portée de mêlée
        self.defender.add_component(Health(current_health=80.0, max_health=80.0))
        self.defender.add_component(Defense(armor=10.0))

        # Créer une entité lanceur de sorts
        self.caster = self.world.create_entity()
        self.caster.add_component(Transform(position=np.array([100.0, 0.0])))
        self.caster.add_component(Health(current_health=50.0, max_health=50.0))
        # Pas besoin de Attack/Defense pour ce test simple de capacité

    def _advance_time(self, dt: float):
        """Simule l'avancement du temps dans le monde."""
        current_time = self.world.get_resource('time')
        self.world.add_resource('time', current_time + dt)
        self.combat_system.update(dt)

    def test_melee_attack_damage(self):
        """Teste si une attaque de mêlée inflige les bons dégâts."""
        initial_defender_health = self.defender.get_component(Health).current_health
        attacker_damage = self.attacker.get_component(Attack).damage
        defender_armor = self.defender.get_component(Defense).armor
        expected_damage = max(0.0, attacker_damage - defender_armor)

        # Avancer le temps pour permettre l'attaque (supposant que le cooldown initial est 0)
        self._advance_time(0.1) # dt petit pour une seule mise à jour

        final_defender_health = self.defender.get_component(Health).current_health
        inflicted_damage = initial_defender_health - final_defender_health

        self.assertAlmostEqual(inflicted_damage, expected_damage, places=5)

    def test_melee_attack_cooldown(self):
        """Teste le cooldown de l'attaque de mêlée."""
        # Première attaque
        self._advance_time(0.1)
        health_after_first_attack = self.defender.get_component(Health).current_health

        # Tenter une deuxième attaque immédiatement (devrait être en cooldown)
        self._advance_time(0.1) # Temps total < 1.0s / attack_speed
        health_after_second_attempt = self.defender.get_component(Health).current_health
        self.assertAlmostEqual(health_after_first_attack, health_after_second_attempt, places=5, msg="Attack should be on cooldown")

        # Attendre la fin du cooldown et attaquer à nouveau
        self._advance_time(1.0) # Temps total > 1.0s
        health_after_third_attempt = self.defender.get_component(Health).current_health
        self.assertLess(health_after_third_attempt, health_after_first_attack, msg="Attack should hit after cooldown")

    def test_use_ability_creates_projectile(self):
        """Teste si l'utilisation d'une capacité crée un projectile."""
        ability = SimpleProjectileAbility()
        self.combat_system.register_entity_abilities(self.caster, [ability])
        target_pos = np.array([200.0, 0.0])

        projectiles_before = len(self.world.get_entities_with_component(TrajectoryProjectile))
        success = self.combat_system.use_ability(self.caster, 0, target_pos)
        projectiles_after = len(self.world.get_entities_with_component(TrajectoryProjectile))

        self.assertTrue(success, "Ability use should succeed")
        self.assertEqual(projectiles_after, projectiles_before + 1, "One projectile should be created")
        # Vérifier que le cooldown est actif
        self.assertFalse(ability.can_use(self.caster), "Ability should be on cooldown after use")

    def test_projectile_collision_damage(self):
        """Teste la collision d'un projectile et les dégâts infligés."""
        # Créer manuellement un projectile pour le test
        projectile = self.world.create_entity()
        projectile_damage = 30.0
        projectile.add_component(Transform(position=np.array([9.0, 0.0]))) # Juste avant le defender
        projectile.add_component(TrajectoryProjectile(velocity=np.array([100.0, 0.0]), damage=projectile_damage, lifetime=1.0))

        initial_defender_health = self.defender.get_component(Health).current_health
        defender_armor = self.defender.get_component(Defense).armor
        expected_damage = max(0.0, projectile_damage - defender_armor)

        # Avancer le temps pour que la collision se produise et soit traitée
        self._advance_time(0.1) # dt suffisant pour parcourir la distance et entrer en collision

        final_defender_health = self.defender.get_component(Health).current_health
        inflicted_damage = initial_defender_health - final_defender_health

        self.assertAlmostEqual(inflicted_damage, expected_damage, places=5)
        # Vérifier que le projectile a été supprimé après la collision
        self.assertFalse(self.world.has_entity(projectile), "Projectile should be removed after collision")

    def test_entity_death(self):
        """Teste si une entité est supprimée lorsque sa santé atteint zéro."""
        defender_health = self.defender.get_component(Health)
        defender_health.current_health = 5.0 # Mettre la santé très basse
        defender_armor = self.defender.get_component(Defense).armor
        attacker_damage = self.attacker.get_component(Attack).damage
        damage_to_deal = max(0.0, attacker_damage - defender_armor) # Dégâts > 5.0

        self.assertTrue(damage_to_deal > defender_health.current_health, "Attack should be lethal")

        # Lancer l'attaque
        self._advance_time(0.1)

        # Vérifier que le défenseur n'existe plus dans le monde
        self.assertFalse(self.world.has_entity(self.defender), "Defender should be removed from the world upon death")


if __name__ == '__main__':
    unittest.main()