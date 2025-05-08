#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the ability fusion system
"""

import sys
import os
import unittest

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "")
sys.path.insert(0, src_dir)

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3

from game.ability_system import Ability, ElementType, AbilityType, AbilityManager
from game.ability_factory import AbilityFactory
from game.fusion_recipe_manager import FusionRecipeManager, FusionRecipe


class MockPlayer:
    """Mock player for testing fusion system"""
    def __init__(self):
        self.ability_manager = None
        self.can_create_fusions = True
        self.can_use_elemental_fusion = True
        self.can_use_divine_weapon_fusion = True
    
    def unlock_fusion_type(self, fusion_type):
        """Unlock a fusion type"""
        setattr(self, f"can_use_{fusion_type}_fusion", True)
        return True


class MockGame:
    """Mock game for testing fusion UI"""
    def __init__(self):
        self.entities = []
        self.player = MockPlayer()
    
    def add_entity(self, entity):
        self.entities.append(entity)


class TestAbilityFusion(unittest.TestCase):
    """Test the ability fusion system"""
    
    def setUp(self):
        """Set up test environment"""
        self.player = MockPlayer()
        self.ability_manager = AbilityManager(self.player)
        self.player.ability_manager = self.ability_manager
        self.recipe_manager = FusionRecipeManager()
        
        # Create some test abilities
        self.fire_ability = self._create_test_ability(
            "fire_bolt", "Fire Bolt", "A bolt of fire", 
            AbilityType.PROJECTILE, ElementType.FIRE
        )
        
        self.ice_ability = self._create_test_ability(
            "ice_shard", "Ice Shard", "A shard of ice",
            AbilityType.PROJECTILE, ElementType.ICE
        )
        
        self.lightning_ability = self._create_test_ability(
            "lightning_strike", "Lightning Strike", "A bolt of lightning",
            AbilityType.PROJECTILE, ElementType.LIGHTNING
        )
        
        self.melee_ability = self._create_test_ability(
            "sword_slash", "Sword Slash", "A slash with a sword",
            AbilityType.MELEE, ElementType.NONE
        )
        
        self.movement_ability = self._create_test_ability(
            "dash", "Dash", "A quick dash",
            AbilityType.MOVEMENT, ElementType.NONE
        )
        
        # Add abilities to the ability manager
        self.ability_manager.add_ability(self.fire_ability)
        self.ability_manager.add_ability(self.ice_ability)
        self.ability_manager.add_ability(self.lightning_ability)
        self.ability_manager.add_ability(self.melee_ability)
        self.ability_manager.add_ability(self.movement_ability)
        
        # Unlock abilities
        self.ability_manager.unlock_ability("fire_bolt")
        self.ability_manager.unlock_ability("ice_shard")
        self.ability_manager.unlock_ability("lightning_strike")
        self.ability_manager.unlock_ability("sword_slash")
        self.ability_manager.unlock_ability("dash")
    
    def _create_test_ability(self, ability_id, name, description, ability_type, element_type):
        """Create a test ability"""
        ability = Ability(
            name, description, 10, 1.0, 10, ability_type, "straight", []
        )
        ability.ability_id = ability_id
        ability.element_type = element_type
        return ability
    
    def test_fusion_creation(self):
        """Test creating a fusion"""
        # Test Fire + Ice = Steam (should match a recipe)
        fusion_id = self.ability_manager.create_fusion("fire_bolt", "ice_shard")
        self.assertIsNotNone(fusion_id)
        
        # Get the fusion ability
        fusion = self.ability_manager.get_ability(fusion_id)
        self.assertIsNotNone(fusion)
        
        # Check fusion properties
        self.assertTrue(fusion.is_fused)
        self.assertEqual(len(fusion.fusion_components), 2)
        self.assertIn("fire_bolt", fusion.fusion_components)
        self.assertIn("ice_shard", fusion.fusion_components)
        
        # Check that it has the expected element type (water for steam)
        self.assertEqual(fusion.element_type, ElementType.WATER)
    
    def test_lightning_movement_fusion(self):
        """Test Lightning + Movement = Teleport (should match a recipe)"""
        fusion_id = self.ability_manager.create_fusion("lightning_strike", "dash")
        self.assertIsNotNone(fusion_id)
        
        # Get the fusion ability
        fusion = self.ability_manager.get_ability(fusion_id)
        self.assertIsNotNone(fusion)
        
        # Check fusion properties
        self.assertTrue(fusion.is_fused)
        self.assertEqual(len(fusion.fusion_components), 2)
        self.assertIn("lightning_strike", fusion.fusion_components)
        self.assertIn("dash", fusion.fusion_components)
        
        # Check that it has the expected ability type
        self.assertEqual(fusion.ability_type, AbilityType.MOVEMENT)
    
    def test_generic_fusion(self):
        """Test generic fusion (no recipe match)"""
        fusion_id = self.ability_manager.create_fusion("fire_bolt", "sword_slash")
        self.assertIsNotNone(fusion_id)
        
        # Get the fusion ability
        fusion = self.ability_manager.get_ability(fusion_id)
        self.assertIsNotNone(fusion)
        
        # Check fusion properties
        self.assertTrue(fusion.is_fused)
        self.assertEqual(len(fusion.fusion_components), 2)
        self.assertIn("fire_bolt", fusion.fusion_components)
        self.assertIn("sword_slash", fusion.fusion_components)
    
    def test_fusion_restrictions(self):
        """Test fusion restrictions"""
        # Disable ability to create fusions
        self.player.can_create_fusions = False
        
        # Try to create a fusion
        fusion_id = self.ability_manager.create_fusion("fire_bolt", "ice_shard")
        self.assertIsNone(fusion_id)
        
        # Re-enable ability to create fusions
        self.player.can_create_fusions = True
        
        # Disable elemental fusion
        self.player.can_use_elemental_fusion = False
        
        # Try to create an elemental fusion
        fusion_id = self.ability_manager.create_fusion("fire_bolt", "ice_shard")
        self.assertIsNone(fusion_id)
        
        # Enable elemental fusion
        self.player.can_use_elemental_fusion = True
        
        # Now it should work
        fusion_id = self.ability_manager.create_fusion("fire_bolt", "ice_shard")
        self.assertIsNotNone(fusion_id)
    
    def test_recipe_matching(self):
        """Test recipe matching"""
        # Create a test recipe
        test_recipe = FusionRecipe(
            {'ability_id': 'fire_bolt'},
            {'ability_id': 'ice_shard'},
            {
                'element_type': ElementType.WATER,
                'ability_type': AbilityType.AREA
            },
            "Test Fusion",
            "A test fusion recipe"
        )
        
        # Check if the recipe matches
        self.assertTrue(test_recipe.matches(self.fire_ability, self.ice_ability))
        self.assertTrue(test_recipe.matches(self.ice_ability, self.fire_ability))
        self.assertFalse(test_recipe.matches(self.fire_ability, self.lightning_ability))


class TestFusionUI(unittest.TestCase):
    """Test the fusion UI"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock game and player
        self.game = MockGame()
        self.player = self.game.player
        
        # Setup ability manager
        self.ability_manager = AbilityManager(self.player)
        self.player.ability_manager = self.ability_manager
        
        # Create some test abilities
        self.fire_ability = self._create_test_ability(
            "fire_bolt", "Fire Bolt", "A bolt of fire", 
            AbilityType.PROJECTILE, ElementType.FIRE
        )
        
        self.ice_ability = self._create_test_ability(
            "ice_shard", "Ice Shard", "A shard of ice",
            AbilityType.PROJECTILE, ElementType.ICE
        )
        
        # Add abilities to the ability manager
        self.ability_manager.add_ability(self.fire_ability)
        self.ability_manager.add_ability(self.ice_ability)
        
        # Unlock abilities
        self.ability_manager.unlock_ability("fire_bolt")
        self.ability_manager.unlock_ability("ice_shard")
    
    def _create_test_ability(self, ability_id, name, description, ability_type, element_type):
        """Create a test ability"""
        ability = Ability(
            name, description, 10, 1.0, 10, ability_type, "straight", []
        )
        ability.ability_id = ability_id
        ability.element_type = element_type
        return ability
    
    def test_fusion_ui_creation(self):
        """Test creating the fusion UI"""
        # Skip this test when not running in a graphical environment
        if not os.environ.get('DISPLAY') and not sys.platform.startswith('win'):
            self.skipTest("No display available")
        
        try:
            # Initialize Panda3D
            base = ShowBase()
            
            # Import FusionUI here to avoid import errors when not in a graphical environment
            from game.fusion_ui import FusionUI
            
            # Create fusion UI
            fusion_ui = FusionUI(self.game)
            
            # Test showing and hiding
            fusion_ui.show(self.player)
            self.assertTrue(fusion_ui.visible)
            
            fusion_ui.hide()
            self.assertFalse(fusion_ui.visible)
            
            # Clean up
            fusion_ui.cleanup()
            base.destroy()
        except Exception as e:
            # Clean up and pass the error
            try:
                base.destroy()
            except:
                pass
            raise e


if __name__ == "__main__":
    unittest.main() 