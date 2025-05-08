#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the ability system with the new secondary abilities
"""

import sys
import os
import unittest

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "")
sys.path.insert(0, src_dir)

from game.ability_factory import AbilityFactory
from game.ability_system import Ability

class MockGame:
    """Mock game class for testing"""
    def __init__(self):
        self.entities = []
        
    def add_entity(self, entity):
        self.entities.append(entity)

class MockEntityManager:
    """Mock entity manager for testing"""
    def __init__(self):
        self.entities = []
        
    def add_entity(self, entity):
        self.entities.append(entity)

class MockEntity:
    """Mock entity class for testing"""
    def __init__(self, position, game=None):
        self.position = position
        self.game = game
        if game:
            game.entity_manager = MockEntityManager()

class TestAbilitySystem(unittest.TestCase):
    """Test the ability system"""
    
    def setUp(self):
        """Set up test environment"""
        self.game = MockGame()
        self.ability_factory = AbilityFactory(self.game)
    
    def test_ability_creation(self):
        """Test ability creation for all classes"""
        classes = ["warrior", "mage", "cleric", "alchemist", "ranger", "summoner"]
        
        for class_type in classes:
            # Test primary ability
            primary = self.ability_factory.create_ability(class_type, "primary")
            self.assertIsNotNone(primary)
            self.assertIsInstance(primary, Ability)
            
            # Test all secondary abilities
            secondary_abilities = self.ability_factory.get_available_secondary_abilities(class_type)
            for ability_name in secondary_abilities:
                ability = self.ability_factory.create_ability(class_type, "secondary", ability_name)
                self.assertIsNotNone(ability)
                self.assertIsInstance(ability, Ability)
                
                # Check that the ability has the correct name
                self.assertEqual(ability.name, secondary_abilities[ability_name]["name"])
    
    def test_ability_cooldown(self):
        """Test ability cooldown mechanics"""
        ability = self.ability_factory.create_ability("warrior", "primary")
        
        # Initially, ability should be ready
        self.assertTrue(ability.is_ready())
        self.assertEqual(ability.current_cooldown, 0)
        
        # Use the ability
        entity = MockEntity(position=(0, 0, 0), game=self.game)
        ability.use(entity, (10, 0, 0))
        
        # Now it should be on cooldown
        self.assertFalse(ability.is_ready())
        self.assertGreater(ability.current_cooldown, 0)
        
        # Update with partial time
        ability.update(0.5)
        self.assertFalse(ability.is_ready())
        
        # Update with remaining time
        ability.update(ability.current_cooldown + 0.1)
        self.assertTrue(ability.is_ready())
    
    def test_ability_upgrade(self):
        """Test ability upgrade mechanics"""
        ability = self.ability_factory.create_ability("mage", "primary")
        
        initial_damage = ability.damage
        initial_cooldown = ability.cooldown
        
        # Upgrade the ability
        result = ability.upgrade()
        self.assertTrue(result)
        
        # Check that stats improved
        self.assertGreater(ability.damage, initial_damage)
        self.assertLess(ability.cooldown, initial_cooldown)
    
    def test_warrior_abilities(self):
        """Test warrior abilities specifically"""
        # Primary ability
        axe_slash = self.ability_factory.create_ability("warrior", "primary")
        self.assertEqual(axe_slash.name, "Axe Slash")
        self.assertEqual(axe_slash.trajectory, "arc")
        
        # Secondary abilities
        ground_slam = self.ability_factory.create_ability("warrior", "secondary", "ground_slam")
        self.assertEqual(ground_slam.name, "Ground Slam")
        self.assertEqual(ground_slam.trajectory, "radial")
        
        whirlwind = self.ability_factory.create_ability("warrior", "secondary", "whirlwind")
        self.assertEqual(whirlwind.name, "Whirlwind")
        self.assertEqual(whirlwind.trajectory, "circular")
    
    def test_mage_abilities(self):
        """Test mage abilities specifically"""
        # Primary ability
        magic_bolt = self.ability_factory.create_ability("mage", "primary")
        self.assertEqual(magic_bolt.name, "Magic Bolt")
        self.assertEqual(magic_bolt.trajectory, "straight")
        
        # Secondary abilities
        fireball = self.ability_factory.create_ability("mage", "secondary", "fireball")
        self.assertEqual(fireball.name, "Fireball")
        self.assertEqual(fireball.trajectory, "arcing")
        
        frost_nova = self.ability_factory.create_ability("mage", "secondary", "frost_nova")
        self.assertEqual(frost_nova.name, "Frost Nova")
        self.assertEqual(frost_nova.trajectory, "radial")
    
    def test_invalid_ability_requests(self):
        """Test invalid ability requests"""
        # Invalid class
        ability = self.ability_factory.create_ability("invalid_class", "primary")
        self.assertIsNone(ability)
        
        # Invalid ability type
        ability = self.ability_factory.create_ability("warrior", "tertiary")
        self.assertIsNone(ability)
        
        # Invalid secondary ability name
        ability = self.ability_factory.create_ability("warrior", "secondary", "invalid_ability")
        self.assertIsNone(ability)
        
        # Missing secondary ability name
        ability = self.ability_factory.create_ability("warrior", "secondary")
        self.assertIsNone(ability)

if __name__ == "__main__":
    unittest.main() 