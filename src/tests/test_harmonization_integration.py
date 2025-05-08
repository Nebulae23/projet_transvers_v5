#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration tests for the Harmonization System
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import the game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.ability_system import Ability, AbilityType, ElementType, AbilityManager
from game.player import Player
from game.game import Game
from game.skill_tree import SkillTree
from game.harmonization_manager import HarmonizationManager
from game.ability_factory import AbilityFactory


class MockGame:
    """Mock game class for testing"""
    
    def __init__(self):
        """Initialize mock game"""
        self.render = MagicMock()
        self.skill_definitions = MagicMock()
        self.skill_definitions.create_skill_tree_template = MagicMock(return_value={
            'groups': {},
            'skills': {}
        })
        
        # Mock UI manager
        self.ui_manager = MagicMock()
        self.ui_manager.show_notification = MagicMock()


class TestHarmonizationIntegration(unittest.TestCase):
    """Test the integration of the harmonization system with the rest of the game"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock game
        self.game = MockGame()
        
        # Create player
        self.player = Player(self.game)
        
        # Create abilities
        self.create_test_abilities()
        
        # Unlock harmonization for the player
        self.player.can_harmonize_abilities = True
        self.player.can_use_projectile_harmonization = True
        self.player.can_use_area_harmonization = True
        self.player.can_use_melee_harmonization = True
        
        # Add harmonization essence to inventory
        self.player.inventory['harmonization_essence'] = 5
    
    def create_test_abilities(self):
        """Create test abilities for the player"""
        # Add some test abilities to the player
        fireball = Ability(
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
        fireball.ability_id = "fireball_1"
        
        ice_nova = Ability(
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
        ice_nova.ability_id = "ice_nova_1"
        
        lightning_bolt = Ability(
            "Lightning Bolt",
            "A bolt of lightning",
            20,  # damage
            3.0,  # cooldown
            15.0,  # range
            AbilityType.PROJECTILE,
            "straight",  # trajectory
            [],  # effects
            ElementType.LIGHTNING
        )
        lightning_bolt.ability_id = "lightning_bolt_1"
        
        earth_slam = Ability(
            "Earth Slam",
            "A powerful melee attack",
            25,  # damage
            4.0,  # cooldown
            2.0,  # range
            AbilityType.MELEE,
            "straight",  # trajectory
            [],  # effects
            ElementType.EARTH
        )
        earth_slam.ability_id = "earth_slam_1"
        
        # Add abilities to player
        self.player.ability_manager.add_ability(fireball)
        self.player.ability_manager.add_ability(ice_nova)
        self.player.ability_manager.add_ability(lightning_bolt)
        self.player.ability_manager.add_ability(earth_slam)
        
        # Unlock abilities
        self.player.ability_manager.unlock_ability(fireball.ability_id)
        self.player.ability_manager.unlock_ability(ice_nova.ability_id)
        self.player.ability_manager.unlock_ability(lightning_bolt.ability_id)
        self.player.ability_manager.unlock_ability(earth_slam.ability_id)
    
    def test_harmonize_projectile_ability(self):
        """Test harmonizing a projectile ability"""
        # Harmonize the fireball ability
        fireball_id = "fireball_1"
        harmonized_id = self.player.harmonize_ability(fireball_id)
        
        # Check results
        self.assertIsNotNone(harmonized_id)
        harmonized = self.player.ability_manager.get_ability(harmonized_id)
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        self.assertEqual(harmonized.harmonization_level, 1)
        
        # Check resource consumption
        self.assertEqual(self.player.inventory['harmonization_essence'], 4)  # 5 - 1
        
        # Original ability should still be available and not harmonized
        original = self.player.ability_manager.get_ability(fireball_id)
        self.assertFalse(original.is_harmonized)
    
    def test_harmonize_area_ability(self):
        """Test harmonizing an area ability"""
        # Harmonize the ice nova ability
        ice_nova_id = "ice_nova_1"
        harmonized_id = self.player.harmonize_ability(ice_nova_id)
        
        # Check results
        self.assertIsNotNone(harmonized_id)
        harmonized = self.player.ability_manager.get_ability(harmonized_id)
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        
        # Check for ice-specific modifications
        self.assertEqual(harmonized.element_type, ElementType.ICE)
        
        # Check resource consumption
        self.assertEqual(self.player.inventory['harmonization_essence'], 4)  # 5 - 1
    
    def test_harmonize_melee_ability(self):
        """Test harmonizing a melee ability"""
        # Harmonize the earth slam ability
        earth_slam_id = "earth_slam_1"
        harmonized_id = self.player.harmonize_ability(earth_slam_id)
        
        # Check results
        self.assertIsNotNone(harmonized_id)
        harmonized = self.player.ability_manager.get_ability(harmonized_id)
        self.assertIsNotNone(harmonized)
        self.assertTrue(harmonized.is_harmonized)
        
        # Check for melee-specific modifications
        self.assertEqual(harmonized.ability_type, AbilityType.MELEE)
        
        # Check resource consumption
        self.assertEqual(self.player.inventory['harmonization_essence'], 4)  # 5 - 1
    
    def test_harmonize_all_abilities(self):
        """Test harmonizing all available abilities"""
        # Harmonize all abilities
        ability_ids = list(self.player.ability_manager.unlocked_abilities)
        harmonized_ids = []
        
        for ability_id in ability_ids:
            harmonized_id = self.player.harmonize_ability(ability_id)
            if harmonized_id:
                harmonized_ids.append(harmonized_id)
        
        # Should have harmonized all 4 abilities
        self.assertEqual(len(harmonized_ids), 4)
        
        # Check resource consumption (4 abilities at 1 essence each)
        self.assertEqual(self.player.inventory['harmonization_essence'], 1)  # 5 - 4
        
        # Check that all harmonized abilities are in the player's unlocked abilities
        for harmonized_id in harmonized_ids:
            self.assertIn(harmonized_id, self.player.ability_manager.unlocked_abilities)
    
    def test_insufficient_resources(self):
        """Test trying to harmonize with insufficient resources"""
        # Set resources to 0
        self.player.inventory['harmonization_essence'] = 0
        
        # Try to harmonize
        harmonized_id = self.player.harmonize_ability("fireball_1")
        
        # Should fail
        self.assertIsNone(harmonized_id)
        
        # Notification should have been shown
        self.game.ui_manager.show_notification.assert_called()
    
    def test_missing_permission(self):
        """Test trying to harmonize without permission"""
        # Remove harmonization permission
        self.player.can_harmonize_abilities = False
        
        # Try to harmonize
        harmonized_id = self.player.harmonize_ability("fireball_1")
        
        # Should fail
        self.assertIsNone(harmonized_id)
    
    def test_harmonize_with_ui(self):
        """Test opening and using the harmonization UI"""
        # Mock the harmonization UI
        mock_ui = MagicMock()
        mock_ui.show = MagicMock()
        
        # Create and patch the UI
        with patch('game.harmonization_ui.HarmonizationUI', return_value=mock_ui):
            # Open the UI
            result = self.player.open_harmonization_ui()
            
            # Check results
            self.assertTrue(result)
            mock_ui.show.assert_called_with(self.player)
    
    def test_ui_without_permission(self):
        """Test opening the harmonization UI without permission"""
        # Remove harmonization permission
        self.player.can_harmonize_abilities = False
        
        # Mock the UI
        mock_ui = MagicMock()
        
        # Create and patch the UI
        with patch('game.harmonization_ui.HarmonizationUI', return_value=mock_ui):
            # Try to open the UI
            result = self.player.open_harmonization_ui()
            
            # Should fail
            self.assertFalse(result)
            mock_ui.show.assert_not_called()
            
            # Notification should have been shown
            self.game.ui_manager.show_notification.assert_called()


class TestHarmonizationSkillUnlocks(unittest.TestCase):
    """Test unlocking harmonization through the skill tree"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock game
        self.game = MockGame()
        
        # Create player
        self.player = Player(self.game)
        
        # Mock the skill tree template
        self.skill_tree_template = {
            'groups': {
                'harmonization': {
                    'name': 'Ability Harmonization',
                    'description': 'Skills related to harmonizing abilities'
                }
            },
            'skills': {
                'basic_harmonization': {
                    'name': 'Ability Harmonization',
                    'description': 'Unlock the ability to harmonize your abilities.',
                    'icon': 'harmonization_icon',
                    'cost': 3,
                    'prerequisites': [],
                    'effects': {
                        'unlock_ability': 'can_harmonize_abilities'
                    },
                    'group': 'harmonization',
                    'position': (0, 0),
                    'tier': 3,
                },
                'projectile_harmonization': {
                    'name': 'Projectile Harmonization',
                    'description': 'Unlock advanced harmonization for projectile abilities.',
                    'icon': 'projectile_harmonization_icon',
                    'cost': 2,
                    'prerequisites': ['basic_harmonization'],
                    'effects': {
                        'unlock_ability': 'projectile_harmonization'
                    },
                    'group': 'harmonization',
                    'position': (-1, 2),
                    'tier': 4,
                }
            }
        }
        
        # Create and initialize the skill tree
        self.player.skill_tree = SkillTree()
        self.player.skill_tree.create_from_template(self.skill_tree_template)
        
        # Give player some skill points
        self.player.skill_points = 10
    
    def test_unlock_harmonization_skill(self):
        """Test unlocking the harmonization skill"""
        # Verify initial state
        self.assertFalse(getattr(self.player, 'can_harmonize_abilities', False))
        
        # Unlock the basic harmonization skill
        self.player.skill_tree.unlock_skill('basic_harmonization', self.player)
        
        # Check if player now has the ability
        self.assertTrue(getattr(self.player, 'can_harmonize_abilities', False))
        
        # Skill points should be reduced
        self.assertEqual(self.player.skill_points, 7)  # 10 - 3
    
    def test_unlock_projectile_harmonization(self):
        """Test unlocking projectile harmonization"""
        # Unlock prerequisite first
        self.player.skill_tree.unlock_skill('basic_harmonization', self.player)
        
        # Verify initial state for the specific type
        self.assertFalse(getattr(self.player, 'can_use_projectile_harmonization', False))
        
        # Unlock the projectile harmonization skill
        self.player.skill_tree.unlock_skill('projectile_harmonization', self.player)
        
        # Check if player now has the ability
        self.assertTrue(getattr(self.player, 'can_use_projectile_harmonization', False))
        
        # Skill points should be further reduced
        self.assertEqual(self.player.skill_points, 5)  # 10 - 3 - 2
    
    def test_unlock_requirement(self):
        """Test that prerequisite requirements are enforced"""
        # Try to unlock projectile harmonization without its prerequisite
        result = self.player.skill_tree.unlock_skill('projectile_harmonization', self.player)
        
        # Should fail
        self.assertFalse(result)
        
        # Player should not have the ability
        self.assertFalse(getattr(self.player, 'can_use_projectile_harmonization', False))
        
        # Skill points should be unchanged
        self.assertEqual(self.player.skill_points, 10)


if __name__ == '__main__':
    unittest.main() 