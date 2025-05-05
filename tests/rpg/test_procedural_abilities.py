# tests/rpg/test_procedural_abilities.py

import unittest
import tempfile
from pathlib import Path
import json
import random
from src.engine.progression.ability.upgrade_tree import AbilityUpgradeTree


# Mock classes for testing
class MockProgressionManager:
    def __init__(self):
        self.trees = {}
        self.unlocked_nodes = {}
        self.player_level = 20
        
    def get_ability_tree(self, ability_id):
        if ability_id not in self.trees:
            # Create a new tree
            self.trees[ability_id] = AbilityUpgradeTree(ability_id)
            self.unlocked_nodes[ability_id] = set()
        return self.trees[ability_id]
        
    def set_ability_tree(self, ability_id, tree):
        self.trees[ability_id] = tree
        
    def can_unlock_node(self, ability_id, node_id):
        if ability_id not in self.trees:
            return False
        tree = self.trees[ability_id]
        if node_id not in tree.nodes:
            return False
        node = tree.nodes[node_id]
        # Check prerequisites
        for prereq in node.prerequisites:
            if prereq not in self.unlocked_nodes.get(ability_id, set()):
                return False
        return True
        
    def unlock_node(self, ability_id, node_id):
        if self.can_unlock_node(ability_id, node_id):
            if ability_id not in self.unlocked_nodes:
                self.unlocked_nodes[ability_id] = set()
            self.unlocked_nodes[ability_id].add(node_id)
            return True
        return False
        
    def get_player_level(self):
        return self.player_level

class ProceduralAbilityTest(unittest.TestCase):
    """Test cases for the procedural ability generation system."""
    
    def setUp(self):
        """Set up the test environment."""
        from src.engine.progression.ability.ability_forge import AbilityForgeSystem
        from src.engine.progression.ability.upgrade_tree import AbilityUpgradeTree, UpgradeNode
        from src.engine.progression.ability.ability_modifiers import DamageModifier
        
        # Create temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        
        # Create test config files
        self.templates_path = self.data_dir / "ability_templates.json"
        self.config_path = self.data_dir / "generation_config.json"
        
        # Write basic template data
        template_data = {
            "templates": {
                "direct_damage": {
                    "base_properties": {
                        "damage": 15,
                        "mana_cost": 20,
                        "cooldown": 1.5,
                        "range": 10
                    },
                    "scaling": {
                        "damage": 0.1,
                        "mana_cost": 0.05
                    },
                    "possible_modifiers": ["elemental", "critical", "aoe"]
                },
                "projectile": {
                    "base_properties": {
                        "damage": 12,
                        "mana_cost": 15,
                        "cooldown": 1.0,
                        "range": 15
                    },
                    "scaling": {
                        "damage": 0.12,
                        "mana_cost": 0.05
                    },
                    "possible_modifiers": ["piercing", "elemental"]
                }
            },
            "class_templates": {
                "warrior": ["direct_damage"],
                "mage": ["projectile"]
            },
            "elements": {
                "fire": {
                    "damage_bonus": 0.2,
                    "visual_color": [255, 100, 0]
                },
                "ice": {
                    "slow_effect": True,
                    "visual_color": [100, 200, 255]
                }
            },
            "rarity_modifiers": {
                "common": {
                    "stat_multiplier": 1.0,
                    "modifier_count": 0
                },
                "uncommon": {
                    "stat_multiplier": 1.2,
                    "modifier_count": 1
                }
            },
            "name_prefixes": {
                "fire": ["Burning", "Fiery"],
                "ice": ["Frozen", "Chilling"],
                "common": ["Basic", "Standard"]
            },
            "name_suffixes": {
                "direct_damage": ["Strike", "Blow"],
                "projectile": ["Bolt", "Arrow"]
            }
        }
        
        config_data = {
            "rarity": {
                "common": {"weight": 70, "stat_bonus": 0},
                "uncommon": {"weight": 30, "stat_bonus": 10}
            },
            "procedural_generation": {
                "unlock_level_threshold": 15,
                "max_branch_depth": 2,
                "max_branches_per_node": 2
            },
            "ability_modifiers": {
                "elemental": {
                    "base_chance": 0.5,
                    "description": "Adds elemental damage",
                    "effect": {"element_type": ["fire", "ice"]}
                },
                "critical": {
                    "base_chance": 0.3,
                    "description": "Increases critical hit chance",
                    "effect": {"crit_chance_bonus": [0.05, 0.2]}
                }
            }
        }
        
        with open(self.templates_path, "w") as f:
            json.dump(template_data, f)
            
        with open(self.config_path, "w") as f:
            json.dump(config_data, f)
            
        # Create progression manager
        self.progression_manager = MockProgressionManager()
        
        # Create sample ability tree
        self.test_ability_id = "test_ability"
        tree = self.progression_manager.get_ability_tree(self.test_ability_id)
        
        # Add some nodes to the tree
        base_node = UpgradeNode(
            upgrade_id="base_node",
            description="Base ability upgrade",
            modifier=DamageModifier(flat_damage_increase=5),
            required_level=1
        )
        tree.add_node(base_node)
        
        damage_node = UpgradeNode(
            upgrade_id="damage_node",
            description="Increase damage",
            modifier=DamageModifier(flat_damage_increase=10),
            required_level=5,
            prerequisites=["base_node"]
        )
        tree.add_node(damage_node)
        
        terminal_node = UpgradeNode(
            upgrade_id="terminal_node",
            description="Final upgrade",
            modifier=DamageModifier(flat_damage_increase=15),
            required_level=10,
            prerequisites=["damage_node"]
        )
        tree.add_node(terminal_node)
        
        # Create the ability forge system
        self.forge = AbilityForgeSystem(
            progression_manager=self.progression_manager,
            templates_path=self.templates_path,
            config_path=self.config_path
        )
        
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
        
    def test_forge_creation(self):
        """Test that the forge system was created correctly."""
        self.assertIsNotNone(self.forge)
        self.assertEqual(self.forge.level_threshold, 15)
        
    def test_unlock_nodes(self):
        """Test unlocking nodes in the ability tree."""
        # Unlock base node
        result = self.forge.unlock_ability_node(self.test_ability_id, "base_node")
        self.assertTrue(result)
        
        # Unlock damage node
        result = self.forge.unlock_ability_node(self.test_ability_id, "damage_node")
        self.assertTrue(result)
        
        # Unlock terminal node
        result = self.forge.unlock_ability_node(self.test_ability_id, "terminal_node")
        self.assertTrue(result)
        
        # Check that nodes were marked as unlocked
        self.assertIn("base_node", self.forge.unlocked_nodes[self.test_ability_id])
        self.assertIn("damage_node", self.forge.unlocked_nodes[self.test_ability_id])
        self.assertIn("terminal_node", self.forge.unlocked_nodes[self.test_ability_id])
        
    def test_procedural_generation(self):
        """Test procedural generation after unlocking nodes."""
        # Unlock all nodes
        self.forge.unlock_ability_node(self.test_ability_id, "base_node")
        self.forge.unlock_ability_node(self.test_ability_id, "damage_node")
        self.forge.unlock_ability_node(self.test_ability_id, "terminal_node")
        
        # Get the extended tree
        tree = self.forge._get_upgrade_tree(self.test_ability_id)
        self.assertIsNotNone(tree)
        
        # Check that procedural generation was enabled
        self.assertTrue(tree.procedural_enabled)
        
        # Check that procedural nodes were generated
        self.assertGreater(len(tree.procedural_nodes), 0)
        
    def test_forge_new_ability(self):
        """Test creating a completely new procedural ability."""
        ability = self.forge.forge_new_ability(
            player_level=20,
            class_type="warrior",
            rarity="uncommon"
        )
        
        self.assertIsNotNone(ability)
        self.assertEqual(ability["rarity"], "uncommon")
        self.assertIn("name", ability)
        self.assertIn("description", ability)
        self.assertIn("properties", ability)
        self.assertIn("components", ability)
        
        # Check that the ability was stored
        ability_id = ability["id"]
        self.assertIn(ability_id, self.forge.procedural_abilities)
        
    def test_regenerate_ability(self):
        """Test regenerating an existing procedural ability."""
        # Create an initial ability
        ability = self.forge.forge_new_ability(
            player_level=20,
            class_type="mage",
            rarity="common"
        )
        
        ability_id = ability["id"]
        original_name = ability["name"]
        
        # Regenerate the ability
        regenerated = self.forge.regenerate_ability(ability_id)
        
        self.assertIsNotNone(regenerated)
        self.assertEqual(regenerated["id"], ability_id)  # ID should stay the same
        self.assertNotEqual(regenerated["name"], original_name)  # Name should change
        
    def test_save_and_load(self):
        """Test saving and loading ability data."""
        from ..src.engine.progression.ability.persistence.ability_save import AbilitySaveManager
        
        # Create a save manager
        save_dir = self.data_dir / "saves"
        save_dir.mkdir(exist_ok=True)
        save_manager = AbilitySaveManager(save_dir)
        
        # Create an ability
        ability = self.forge.forge_new_ability(
            player_level=20,
            class_type="warrior",
            rarity="uncommon"
        )
        
        # Unlock nodes
        self.forge.unlock_ability_node(self.test_ability_id, "base_node")
        self.forge.unlock_ability_node(self.test_ability_id, "damage_node")
        self.forge.unlock_ability_node(self.test_ability_id, "terminal_node")
        
        # Save the data
        save_data = self.forge.save_data()
        player_id = "test_player"
        result = save_manager.save_player_abilities(player_id, save_data)
        self.assertTrue(result)
        
        # Load the data
        loaded_data = save_manager.load_player_abilities(player_id)
        self.assertIsNotNone(loaded_data)
        
        # Check that loaded data is valid
        self.assertIn("procedural_abilities", loaded_data)
        self.assertIn("unlocked_nodes", loaded_data)
        self.assertIn("procedural_trees", loaded_data)
        
        # Check that ability data was preserved
        ability_id = ability["id"]
        self.assertIn(ability_id, loaded_data["procedural_abilities"])
        
if __name__ == "__main__":
    unittest.main() 