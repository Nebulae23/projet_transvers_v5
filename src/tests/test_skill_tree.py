#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the skill tree and ability systems
"""

import sys
import os

# Add the parent directory to the path so we can import the game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.game.skill_tree import SkillTree, SkillNode, SkillType
from src.game.ability_system import (
    AbilityManager, Ability, ProjectileAbility, MeleeAbility,
    AbilityType, SpecializationPath
)
from src.game.character_class import ClassManager, ClassType
from src.game.ability_factory import AbilityFactory, create_ability
import src.game.skill_definitions as skill_definitions

class MockPlayer:
    """Mock player for testing"""
    
    def __init__(self):
        """Initialize the mock player"""
        self.max_health = 100
        self.health = 100
        self.speed = 5.0
        self.damage_multiplier = 1.0
        self.character_class = "warrior"
        self.inventory = {"monster_essence": 100}
        
        # Ability manager
        self.ability_manager = AbilityManager(self)
        
        # Track ability unlocks and modifications
        self.unlocked_abilities = []
        self.modified_abilities = {}
        self.added_passives = {}
    
    def unlock_ability(self, ability_id):
        """Mock ability unlock"""
        self.unlocked_abilities.append(ability_id)
        print(f"[Player] Unlocked ability: {ability_id}")
        return True
    
    def modify_ability(self, ability_id, modifiers):
        """Mock ability modification"""
        self.modified_abilities[ability_id] = modifiers
        print(f"[Player] Modified ability: {ability_id} with {modifiers}")
        return True
    
    def add_passive(self, passive_id, effects):
        """Mock passive addition"""
        self.added_passives[passive_id] = effects
        print(f"[Player] Added passive: {passive_id} with effects {effects}")
        return True
    
    def set_specialization(self, spec_path):
        """Mock specialization setting"""
        print(f"[Player] Set specialization: {spec_path}")
        return True
    
    def unlock_fusion_type(self, fusion_type):
        """Mock fusion type unlock"""
        print(f"[Player] Unlocked fusion type: {fusion_type}")
        return True


class MockGame:
    """Mock game for testing"""
    
    def __init__(self):
        """Initialize the mock game"""
        pass


def test_skill_tree():
    """Test the skill tree system"""
    print("\n===== Testing Skill Tree System =====")
    
    # Create a mock player
    player = MockPlayer()
    
    # Create a skill tree
    skill_tree = SkillTree()
    
    # Create some test nodes
    root_node = SkillNode(
        "test_root",
        "Test Root",
        "Root node for testing",
        SkillType.PASSIVE,
        {"passive_id": "test_passive"},
        position=(0, 0)
    )
    
    skill_1 = SkillNode(
        "skill_1",
        "Skill 1",
        "First skill",
        SkillType.STAT_BOOST,
        {"damage_multiplier": 0.1},
        position=(0, 5),
        cost={"monster_essence": 10}
    )
    
    skill_2 = SkillNode(
        "skill_2",
        "Skill 2",
        "Second skill",
        SkillType.ABILITY_UNLOCK,
        {"ability_id": "fireball"},
        position=(0, 10),
        cost={"monster_essence": 20}
    )
    
    # Add nodes to tree
    skill_tree.add_node(root_node)
    skill_tree.add_node(skill_1)
    skill_tree.add_node(skill_2)
    
    # Connect nodes
    root_node.add_child(skill_1)
    skill_1.add_child(skill_2)
    
    # Make root node visible and unlocked
    root_node.is_visible = True
    root_node.is_unlocked = True
    
    # Make child nodes visible
    for child in root_node.children:
        child.is_visible = True
    
    # Test skill tree functionality
    print("\nVisible nodes:")
    visible_nodes = skill_tree.get_visible_nodes(player)
    for node in visible_nodes:
        print(f"  - {node.name} ({node.node_id})")
    
    print("\nUnlockable nodes:")
    unlockable_nodes = skill_tree.get_unlockable_nodes(player)
    for node in unlockable_nodes:
        print(f"  - {node.name} ({node.node_id})")
    
    # Unlock a node
    print("\nUnlocking first skill:")
    skill_1.unlock(player)
    
    # Test node effects
    print("\nApplying node effects:")
    skill_1.apply_effects(player)
    print(f"  Player damage multiplier after boost: {player.damage_multiplier}")
    
    # Check unlockable nodes again
    print("\nUnlockable nodes after first unlock:")
    unlockable_nodes = skill_tree.get_unlockable_nodes(player)
    for node in unlockable_nodes:
        print(f"  - {node.name} ({node.node_id})")
    
    # Unlock another node
    print("\nUnlocking second skill:")
    skill_2.unlock(player)
    skill_2.apply_effects(player)
    
    # Check abilities unlocked
    print("\nAbilities unlocked:")
    for ability_id in player.unlocked_abilities:
        print(f"  - {ability_id}")
    
    print("\nSkill tree test completed successfully!")


def test_ability_system():
    """Test the ability system"""
    print("\n===== Testing Ability System =====")
    
    # Create a mock player and game
    player = MockPlayer()
    game = MockGame()
    player.game = game
    
    # Create some abilities
    print("\nCreating abilities:")
    
    fireball = ProjectileAbility(
        "fireball",
        "Fireball",
        "Launch a ball of fire",
        "arcing",
        damage=30,
        speed=10.0,
        cooldown=3.0,
        resource_cost=15
    )
    
    slash = MeleeAbility(
        "slash",
        "Slash",
        "Slash with your weapon",
        damage=20,
        range=2.0,
        angle=90.0,
        cooldown=0.5
    )
    
    print(f"  Created {fireball.name} ({fireball.ability_id})")
    print(f"  Created {slash.name} ({slash.ability_id})")
    
    # Add abilities to player
    player.ability_manager.add_ability(fireball)
    player.ability_manager.add_ability(slash)
    player.ability_manager.unlock_ability("fireball")
    player.ability_manager.unlock_ability("slash")
    
    print("\nActive abilities:")
    for i, ability_id in enumerate(player.ability_manager.active_abilities):
        ability = player.ability_manager.get_ability(ability_id)
        print(f"  Slot {i}: {ability.name} ({ability.ability_id})")
    
    # Test ability specialization
    print("\nTesting ability specialization:")
    
    print("  Specializing Fireball for increased damage:")
    player.ability_manager.specialize_ability("fireball", SpecializationPath.DAMAGE)
    
    fireball = player.ability_manager.get_ability("fireball")
    print(f"  Fireball damage multiplier: {fireball.damage_multiplier}")
    print(f"  Fireball cooldown multiplier: {fireball.cooldown_multiplier}")
    print(f"  Fireball damage: {fireball.damage}")
    
    print("\nSpecializing Slash for area effect:")
    player.ability_manager.specialize_ability("slash", SpecializationPath.AREA)
    
    slash = player.ability_manager.get_ability("slash")
    print(f"  Slash area multiplier: {slash.area_multiplier}")
    print(f"  Slash angle: {slash.angle} degrees")
    print(f"  Slash range: {slash.range}")
    
    print("\nAbility system test completed successfully!")


def test_character_class():
    """Test the character class system"""
    print("\n===== Testing Character Class System =====")
    
    # Create a class manager
    class_manager = ClassManager()
    
    # Create a mock player
    player = MockPlayer()
    
    # List available classes
    print("\nAvailable classes:")
    for class_type, class_obj in class_manager.get_all_classes().items():
        print(f"  - {class_obj.name}: {class_obj.description}")
    
    # Apply a class to the player
    print("\nApplying Warrior class to player:")
    class_manager.apply_class(player, ClassType.WARRIOR)
    
    # Check stat modifications
    warrior = class_manager.get_class(ClassType.WARRIOR)
    print(f"  Health modifier: {warrior.health_modifier}")
    print(f"  Speed modifier: {warrior.speed_modifier}")
    print(f"  Damage modifier: {warrior.damage_modifier}")
    
    # Get starting abilities
    print("\nWarrior starting abilities:")
    for ability in warrior.get_starting_abilities():
        print(f"  - {ability.name} ({ability.ability_id})")
    
    # Get skill tree nodes
    print("\nWarrior skill tree nodes:")
    for node_id in warrior.get_available_skill_nodes():
        print(f"  - {node_id}")
    
    print("\nCharacter class test completed successfully!")


def test_complete_integration():
    """Test complete integration of all systems"""
    print("\n===== Testing Complete Integration =====")
    
    # Create mock player and game
    player = MockPlayer()
    game = MockGame()
    player.game = game
    
    # Apply class
    class_manager = ClassManager()
    class_manager.apply_class(player, ClassType.MAGE)
    
    # Set up skill tree from definitions
    skill_tree = SkillTree()
    skill_tree.create_from_template(skill_definitions.create_skill_tree_template())
    
    # Make root node for mage visible and unlocked
    mage_root = skill_tree.nodes.get("mage_root")
    if mage_root:
        mage_root.is_unlocked = True
        mage_root.is_visible = True
        
        # Make child nodes visible
        for child in mage_root.children:
            child.is_visible = True
    
    # Show visible nodes
    print("\nVisible skill nodes for Mage:")
    for node in skill_tree.get_visible_nodes(player):
        print(f"  - {node.name} ({node.node_id})")
    
    # Unlock fireball skill
    fireball_node = skill_tree.nodes.get("fireball")
    if fireball_node:
        print("\nUnlocking Fireball skill:")
        fireball_node.unlock(player)
        fireball_node.apply_effects(player)
    
    # Check if the ability was unlocked
    print("\nUnlocked abilities:")
    for ability_id in player.unlocked_abilities:
        print(f"  - {ability_id}")
    
    # Create and add a fireball ability manually
    fireball = create_ability("fireball")
    if fireball:
        player.ability_manager.add_ability(fireball)
        player.ability_manager.unlock_ability("fireball")
    
    # Specialize the fireball ability
    print("\nSpecializing Fireball ability:")
    player.ability_manager.specialize_ability("fireball", SpecializationPath.DAMAGE)
    
    # Unlock specialization node
    spec_node = skill_tree.nodes.get("fireball_specialization")
    if spec_node:
        print("\nUnlocking Fireball Specialization node:")
        player.inventory["fire_essence"] = 10  # Add resource for specialized node
        spec_node.unlock(player)
        spec_node.apply_effects(player)
    
    print("\nComplete integration test completed successfully!")


def main():
    """Main test function"""
    print("=== NIGHTFALL DEFENDERS SKILL TREE AND ABILITY SYSTEM TEST ===\n")
    
    # Run individual tests
    test_skill_tree()
    test_ability_system()
    test_character_class()
    test_complete_integration()
    
    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main() 