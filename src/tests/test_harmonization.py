#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the Harmonization System
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import the game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.ability_system import Ability, AbilityType, ElementType, AbilityManager
from game.harmonization_manager import HarmonizationManager, HarmonizationEffect
from game.ability_factory import AbilityFactory


class TestHarmonizationEffect(unittest.TestCase):
    """Test the HarmonizationEffect class"""
    
    def test_initialization(self):
        """Test initializing a harmonization effect"""
        effect = HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.FIRE,
            {'damage_multiplier': 1.5},
            "Enhanced Fireball",
            "A more powerful fireball"
        )
        
        self.assertEqual(effect.ability_type, AbilityType.PROJECTILE)
        self.assertEqual(effect.element_type, ElementType.FIRE)
        self.assertEqual(effect.effect_data, {'damage_multiplier': 1.5})
        self.assertEqual(effect.name, "Enhanced Fireball")
        self.assertEqual(effect.description, "A more powerful fireball")
    
    def test_matching(self):
        """Test matching an effect to an ability"""
        # Create an effect for fire projectiles
        effect = HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.FIRE,
            {'damage_multiplier': 1.5},
            "Enhanced Fireball",
            "A more powerful fireball"
        )
        
        # Create a matching ability
        matching_ability = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        
        # Create a non-matching ability (wrong element)
        wrong_element_ability = Ability(
            "Ice Shard",
            "A shard of ice",
            8,  # damage
            1.5,  # cooldown
            8.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.ICE
        )
        
        # Create a non-matching ability (wrong type)
        wrong_type_ability = Ability(
            "Fire Aura",
            "An aura of fire",
            5,  # damage
            5.0,  # cooldown
            3.0,  # range
            AbilityType.AREA,
            "radial",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        
        # Create a non-matching ability (already harmonized)
        harmonized_ability = Ability(
            "Harmonized Fireball",
            "An enhanced fireball",
            15,  # damage
            2.4,  # cooldown
            12.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        harmonized_ability.is_harmonized = True
        
        # Test matching
        self.assertTrue(effect.matches(matching_ability))
        self.assertFalse(effect.matches(wrong_element_ability))
        self.assertFalse(effect.matches(wrong_type_ability))
        self.assertFalse(effect.matches(harmonized_ability))


class TestHarmonizationManager(unittest.TestCase):
    """Test the HarmonizationManager class"""
    
    def test_initialization(self):
        """Test initializing the harmonization manager"""
        manager = HarmonizationManager()
        
        # Should initialize with default effects
        self.assertGreater(len(manager.effects), 0)
    
    def test_add_effect(self):
        """Test adding an effect to the manager"""
        manager = HarmonizationManager()
        
        # Get initial count
        initial_count = len(manager.effects)
        
        # Add a new effect
        effect = HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.FIRE,
            {'damage_multiplier': 1.5},
            "Custom Fireball",
            "A custom enhanced fireball"
        )
        
        result = manager.add_effect(effect)
        
        # Check results
        self.assertTrue(result)
        self.assertEqual(len(manager.effects), initial_count + 1)
        self.assertIn(effect, manager.effects)
    
    def test_find_effect(self):
        """Test finding an effect for an ability"""
        manager = HarmonizationManager()
        
        # Create a test ability
        fire_ability = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        
        # Create an ice ability
        ice_ability = Ability(
            "Ice Shard",
            "A shard of ice",
            8,  # damage
            1.5,  # cooldown
            8.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.ICE
        )
        
        # Create a generic ability with no element
        generic_ability = Ability(
            "Generic Ability",
            "A generic ability",
            5,  # damage
            1.0,  # cooldown
            5.0,  # range
            AbilityType.UTILITY,
            "none",  # trajectory
            [],  # effects
            ElementType.NONE
        )
        
        # Find effects
        fire_effect = manager.find_effect(fire_ability)
        ice_effect = manager.find_effect(ice_ability)
        generic_effect = manager.find_effect(generic_ability)
        
        # Check results
        self.assertIsNotNone(fire_effect)
        self.assertIsNotNone(ice_effect)
        self.assertIsNone(generic_effect)  # Should not find an effect for generic abilities


class TestAbilityHarmonization(unittest.TestCase):
    """Test harmonizing abilities"""
    
    def test_harmonize_method(self):
        """Test the harmonize method on Ability"""
        ability = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        
        # Initial state
        self.assertFalse(ability.is_harmonized)
        self.assertEqual(ability.harmonization_level, 0)
        self.assertIsNone(ability.harmonization_effect)
        
        # Harmonize with custom effect
        effect_data = {
            'damage_multiplier': 1.5,
            'cooldown_multiplier': 1.2,
            'name': "Enhanced Fireball",
            'description': "A more powerful fireball"
        }
        
        result = ability.harmonize(effect_data)
        
        # Check results
        self.assertTrue(result)
        self.assertTrue(ability.is_harmonized)
        self.assertEqual(ability.harmonization_level, 1)
        self.assertEqual(ability.damage, 15)  # 10 * 1.5
        self.assertEqual(ability.cooldown, 2.4)  # 2.0 * 1.2
        self.assertEqual(ability.name, "Enhanced Fireball")
        self.assertEqual(ability.description, "A more powerful fireball")
        
        # Try to harmonize again - should fail
        result = ability.harmonize()
        self.assertFalse(result)
    
    def test_default_harmonization(self):
        """Test harmonizing with default effects"""
        ability = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        
        # Harmonize with default effect
        result = ability.harmonize()
        
        # Check results
        self.assertTrue(result)
        self.assertTrue(ability.is_harmonized)
        self.assertEqual(ability.harmonization_level, 1)
        self.assertEqual(ability.damage, 13)  # 10 * 1.3
        self.assertEqual(ability.cooldown, 2.4)  # 2.0 * 1.2


class TestAbilityFactoryHarmonization(unittest.TestCase):
    """Test creating harmonized abilities via AbilityFactory"""
    
    def test_create_harmonized_ability(self):
        """Test creating a harmonized ability"""
        # Create a test ability
        original = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        original.ability_id = "fireball_1"
        
        # Create harmonized version
        harmonized = AbilityFactory.create_harmonized_ability(original)
        
        # Check results
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        self.assertEqual(harmonized.ability_id, f"harmonized_{original.ability_id}")
        self.assertGreater(harmonized.damage, original.damage)
        self.assertGreater(harmonized.cooldown, original.cooldown)
        
        # Original should be unchanged
        self.assertFalse(original.is_harmonized)
    
    def test_create_harmonized_ability_with_effect(self):
        """Test creating a harmonized ability with a specific effect"""
        # Create a test ability
        original = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        original.ability_id = "fireball_1"
        
        # Create custom effect
        effect = {
            'damage_multiplier': 2.0,
            'cooldown_multiplier': 1.5,
            'name': "Super Fireball",
            'description': "A super powerful fireball"
        }
        
        # Create harmonized version with custom effect
        harmonized = AbilityFactory.create_harmonized_ability(original, effect)
        
        # Check results
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        self.assertEqual(harmonized.ability_id, f"harmonized_{original.ability_id}")
        self.assertEqual(harmonized.damage, 20)  # 10 * 2.0
        self.assertEqual(harmonized.cooldown, 3.0)  # 2.0 * 1.5
        self.assertEqual(harmonized.name, "Super Fireball")
        self.assertEqual(harmonized.description, "A super powerful fireball")


class TestAbilityManagerHarmonization(unittest.TestCase):
    """Test harmonizing abilities via AbilityManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock player
        self.player = MagicMock()
        self.player.can_harmonize_abilities = True
        self.player.can_use_projectile_harmonization = True
        self.player.can_use_area_harmonization = True
        
        # Create ability manager
        self.ability_manager = AbilityManager(self.player)
        
        # Create test abilities
        self.fireball = Ability(
            "Fireball",
            "A ball of fire",
            10,  # damage
            2.0,  # cooldown
            10.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.FIRE
        )
        self.fireball.ability_id = "fireball_1"
        
        self.ice_nova = Ability(
            "Ice Nova",
            "An explosion of ice",
            15,  # damage
            5.0,  # cooldown
            5.0,  # range
            AbilityType.AREA,
            "radial",  # trajectory
            [],  # effects
            ElementType.ICE
        )
        self.ice_nova.ability_id = "ice_nova_1"
        
        # Add abilities to manager
        self.ability_manager.add_ability(self.fireball)
        self.ability_manager.add_ability(self.ice_nova)
        self.ability_manager.unlock_ability(self.fireball.ability_id)
        self.ability_manager.unlock_ability(self.ice_nova.ability_id)
    
    def test_harmonize_ability(self):
        """Test harmonizing an ability via AbilityManager"""
        # Harmonize fireball
        harmonized_id = self.ability_manager.harmonize_ability(self.fireball.ability_id)
        
        # Check results
        self.assertIsNotNone(harmonized_id)
        harmonized = self.ability_manager.get_ability(harmonized_id)
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        self.assertIn(harmonized_id, self.ability_manager.unlocked_abilities)
        self.assertIn(self.fireball.ability_id, self.ability_manager.harmonization_choices)
    
    def test_harmonize_ability_requirements(self):
        """Test harmonization requirements"""
        # Mock player without harmonization ability
        player_no_harmonize = MagicMock()
        player_no_harmonize.can_harmonize_abilities = False
        
        ability_manager = AbilityManager(player_no_harmonize)
        ability_manager.add_ability(self.fireball)
        ability_manager.unlock_ability(self.fireball.ability_id)
        
        # Try to harmonize - should fail due to missing permission
        harmonized_id = ability_manager.harmonize_ability(self.fireball.ability_id)
        self.assertIsNone(harmonized_id)
        
        # Mock player with general harmonization but missing specific type
        player_partial = MagicMock()
        player_partial.can_harmonize_abilities = True
        player_partial.can_use_projectile_harmonization = False
        
        ability_manager = AbilityManager(player_partial)
        ability_manager.add_ability(self.fireball)
        ability_manager.unlock_ability(self.fireball.ability_id)
        
        # Try to harmonize - should fail due to missing specific permission
        harmonized_id = ability_manager.harmonize_ability(self.fireball.ability_id)
        self.assertIsNone(harmonized_id)


if __name__ == '__main__':
    unittest.main() 