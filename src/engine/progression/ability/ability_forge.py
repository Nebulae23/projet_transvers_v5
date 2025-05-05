# src/engine/progression/ability/ability_forge.py

import json
import time
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

from .generators.procedural_ability_generator import AbilityGenerator
from .generators.component_generator import AbilityComponentGenerator
from .trees.extended_tree import ExtendedUpgradeTree

class AbilityForgeSystem:
    """
    Manages the unlocking and generation of procedural abilities.
    Handles the transition from fixed to procedural abilities.
    """
    def __init__(self, progression_manager, templates_path: Path, config_path: Path):
        """
        Initialize the ability forge system.
        
        Args:
            progression_manager: Reference to the ability progression manager.
            templates_path (Path): Path to the ability templates JSON file.
            config_path (Path): Path to the generation configuration JSON file.
        """
        self.progression_manager = progression_manager
        self.ability_generator = AbilityGenerator(templates_path, config_path)
        self.component_generator = AbilityComponentGenerator(config_path)
        
        # Config values from the generation config
        self.config = self._load_json(config_path)
        self.procedural_config = self.config.get("procedural_generation", {})
        self.level_threshold = self.procedural_config.get("unlock_level_threshold", 15)
        
        # Track unlocked procedural abilities
        self.procedural_abilities: Dict[str, Dict] = {}  # Map ability_id to ability data
        self.procedural_trees: Dict[str, ExtendedUpgradeTree] = {}  # Map ability_id to upgrade tree
        self.unlocked_nodes: Dict[str, Set[str]] = {}  # Map ability_id to set of unlocked node_ids

    def _load_json(self, path: Path) -> Dict:
        """
        Load JSON from a file path.
        
        Args:
            path (Path): Path to the JSON file.
            
        Returns:
            dict: Loaded JSON data.
        """
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {path}: {e}")
            return {}
            
    def unlock_ability_node(self, ability_id: str, node_id: str) -> bool:
        """
        Unlock a node in the ability tree.
        If it's a terminal node, enable procedural generation.
        
        Args:
            ability_id (str): Ability ID.
            node_id (str): Node ID to unlock.
            
        Returns:
            bool: True if the node was unlocked successfully.
        """
        # Check if we should enable procedural generation
        if ability_id not in self.unlocked_nodes:
            self.unlocked_nodes[ability_id] = set()
            
        # Get the upgrade tree
        tree = self._get_upgrade_tree(ability_id)
        if not tree:
            return False  # Tree not found
            
        # Check if the node can be unlocked
        if self.progression_manager.can_unlock_node(ability_id, node_id):
            # Unlock the node through the progression manager
            result = self.progression_manager.unlock_node(ability_id, node_id)
            if result:
                # Add to unlocked nodes
                self.unlocked_nodes[ability_id].add(node_id)
                
                # Check if this is a terminal node
                if node_id in tree.terminal_nodes:
                    # Enable procedural generation if the player meets the level requirement
                    player_level = self.progression_manager.get_player_level()
                    if player_level >= self.level_threshold:
                        self._enable_procedural_generation(ability_id)
                        
                return True
                
        return False
        
    def _get_upgrade_tree(self, ability_id: str) -> Optional[ExtendedUpgradeTree]:
        """
        Get the upgrade tree for an ability, converting to ExtendedUpgradeTree if needed.
        
        Args:
            ability_id (str): Ability ID.
            
        Returns:
            ExtendedUpgradeTree: The upgrade tree.
        """
        # Check if we already have an extended tree
        if ability_id in self.procedural_trees:
            return self.procedural_trees[ability_id]
            
        # Get the base tree from the progression manager
        base_tree = self.progression_manager.get_ability_tree(ability_id)
        if not base_tree:
            return None
            
        # If it's already an ExtendedUpgradeTree, use it
        if isinstance(base_tree, ExtendedUpgradeTree):
            self.procedural_trees[ability_id] = base_tree
            return base_tree
            
        # Otherwise, create a new ExtendedUpgradeTree and copy nodes
        extended_tree = ExtendedUpgradeTree(
            ability_id=base_tree.ability_id,
            max_procedural_depth=self.procedural_config.get("max_branch_depth", 3),
            max_branches=self.procedural_config.get("max_branches_per_node", 2)
        )
        
        # Copy all nodes from base tree
        for node_id, node in base_tree.nodes.items():
            extended_tree.add_node(node)
            
        # Replace the tree in the progression manager if possible
        if hasattr(self.progression_manager, 'set_ability_tree'):
            self.progression_manager.set_ability_tree(ability_id, extended_tree)
            
        # Store for future use
        self.procedural_trees[ability_id] = extended_tree
        return extended_tree
        
    def _enable_procedural_generation(self, ability_id: str) -> bool:
        """
        Enable procedural generation for an ability.
        
        Args:
            ability_id (str): Ability ID.
            
        Returns:
            bool: True if procedural generation was enabled.
        """
        tree = self._get_upgrade_tree(ability_id)
        if not tree or tree.procedural_enabled:
            return False
            
        # Create a seed based on ability_id and current time
        seed = f"{ability_id}_{int(time.time())}_{random.randint(0, 10000)}"
        
        # Enable procedural generation
        tree.enable_procedural_generation(seed, self.ability_generator)
        
        print(f"Enabled procedural generation for ability {ability_id}")
        
        return True
        
    def forge_new_ability(self, player_level: int, class_type: str, 
                         base_ability_id: Optional[str] = None, 
                         rarity: Optional[str] = None) -> Optional[Dict]:
        """
        Generate a new procedural ability.
        
        Args:
            player_level (int): Current player level.
            class_type (str): Class type (warrior, mage, etc.).
            base_ability_id (str): Optional base ability to derive from.
            rarity (str): Optional rarity level to enforce.
            
        Returns:
            dict: Generated ability data, or None if generation failed.
        """
        try:
            # Generate the ability
            ability_data = self.ability_generator.generate_ability(
                player_level=player_level,
                class_type=class_type,
                base_ability_id=base_ability_id,
                rarity=rarity
            )
            
            # Generate visual and audio components
            ability_type = ability_data.get("type", "generic")
            ability_element = ability_data.get("element")
            ability_rarity = ability_data.get("rarity", "common")
            
            components = {
                "visual": self.component_generator.generate_visual_effect(
                    ability_type, ability_element, ability_rarity
                ),
                "audio": self.component_generator.generate_sound_effect(
                    ability_type, ability_element, ability_rarity
                ),
                "icon": self.component_generator.generate_icon_params(
                    ability_type, ability_element, ability_rarity
                )
            }
            
            # Add components to ability data
            ability_data["components"] = components
            
            # Store the procedural ability
            ability_id = ability_data["id"]
            self.procedural_abilities[ability_id] = ability_data
            
            return ability_data
            
        except Exception as e:
            print(f"Error generating procedural ability: {e}")
            return None
            
    def regenerate_ability(self, ability_id: str) -> Optional[Dict]:
        """
        Regenerate an existing procedural ability.
        
        Args:
            ability_id (str): Ability ID.
            
        Returns:
            dict: Regenerated ability data, or None if regeneration failed.
        """
        if ability_id not in self.procedural_abilities:
            return None
            
        # Get existing ability data
        existing = self.procedural_abilities[ability_id]
        
        try:
            # Generate new seed
            seed = f"{ability_id}_{int(time.time())}_{random.randint(0, 10000)}"
            self.ability_generator.set_seed(seed)
            
            # Generate new ability with same base parameters
            new_ability = self.ability_generator.generate_ability(
                player_level=self.progression_manager.get_player_level(),
                class_type=existing.get("class", "warrior"),
                rarity=existing.get("rarity", "common")
            )
            
            # Keep original ID to maintain references
            new_ability["id"] = ability_id
            
            # Generate new components
            ability_type = new_ability.get("type", "generic")
            ability_element = new_ability.get("element")
            ability_rarity = new_ability.get("rarity", "common")
            
            components = {
                "visual": self.component_generator.generate_visual_effect(
                    ability_type, ability_element, ability_rarity
                ),
                "audio": self.component_generator.generate_sound_effect(
                    ability_type, ability_element, ability_rarity
                ),
                "icon": self.component_generator.generate_icon_params(
                    ability_type, ability_element, ability_rarity
                )
            }
            
            # Add components to ability data
            new_ability["components"] = components
            
            # Update stored ability
            self.procedural_abilities[ability_id] = new_ability
            
            return new_ability
            
        except Exception as e:
            print(f"Error regenerating procedural ability {ability_id}: {e}")
            return None
            
    def regenerate_procedural_branch(self, ability_id: str, node_id: str) -> bool:
        """
        Regenerate a procedural branch starting from a specific node.
        
        Args:
            ability_id (str): Ability ID.
            node_id (str): Node ID to start regeneration from.
            
        Returns:
            bool: True if the branch was regenerated successfully.
        """
        tree = self._get_upgrade_tree(ability_id)
        if not tree or not tree.procedural_enabled:
            return False
            
        # Check if the node exists and is a procedural node
        if node_id not in tree.procedural_nodes:
            return False
            
        # Create a new seed
        seed = f"{ability_id}_{node_id}_{int(time.time())}_{random.randint(0, 10000)}"
        
        # Regenerate the node and its children
        return tree.regenerate_node(node_id, seed, self.ability_generator)
        
    def upgrade_node_rarity(self, ability_id: str, node_id: str, new_rarity: str) -> bool:
        """
        Upgrade a node to a higher rarity level.
        
        Args:
            ability_id (str): Ability ID.
            node_id (str): Node ID to upgrade.
            new_rarity (str): New rarity level.
            
        Returns:
            bool: True if the node was upgraded successfully.
        """
        tree = self._get_upgrade_tree(ability_id)
        if not tree:
            return False
            
        # Check if the node exists and is a procedural node
        if node_id not in tree.procedural_nodes:
            return False
            
        # Upgrade the node
        node = tree.procedural_nodes[node_id]
        return node.upgrade_rarity(new_rarity)
        
    def get_procedural_ability(self, ability_id: str) -> Optional[Dict]:
        """
        Get data for a procedural ability.
        
        Args:
            ability_id (str): Ability ID.
            
        Returns:
            dict: Ability data, or None if not found.
        """
        return self.procedural_abilities.get(ability_id)
        
    def get_procedural_abilities(self) -> Dict[str, Dict]:
        """
        Get all procedural abilities.
        
        Returns:
            dict: Map of ability_id to ability data.
        """
        return self.procedural_abilities
        
    def is_procedural_ability(self, ability_id: str) -> bool:
        """
        Check if an ability is procedural.
        
        Args:
            ability_id (str): Ability ID.
            
        Returns:
            bool: True if the ability is procedural.
        """
        return ability_id in self.procedural_abilities
        
    def save_data(self) -> Dict:
        """
        Save forge system data for persistence.
        
        Returns:
            dict: Serializable data.
        """
        data = {
            "procedural_abilities": self.procedural_abilities,
            "unlocked_nodes": {ability_id: list(nodes) for ability_id, nodes in self.unlocked_nodes.items()},
            "procedural_trees": {ability_id: tree.to_dict() for ability_id, tree in self.procedural_trees.items()}
        }
        return data
        
    def load_data(self, data: Dict):
        """
        Load forge system data from persistence.
        
        Args:
            data (dict): Serialized data.
        """
        # Load procedural abilities
        self.procedural_abilities = data.get("procedural_abilities", {})
        
        # Load unlocked nodes
        unlocked = data.get("unlocked_nodes", {})
        self.unlocked_nodes = {ability_id: set(nodes) for ability_id, nodes in unlocked.items()}
        
        # Load procedural trees
        trees_data = data.get("procedural_trees", {})
        for ability_id, tree_data in trees_data.items():
            # Create modifier factory if needed
            def modifier_factory(modifier_data):
                return self.ability_generator.create_modifier_from_properties({
                    "modifier_data": modifier_data
                })
                
            tree = ExtendedUpgradeTree.from_dict(tree_data, modifier_factory)
            self.procedural_trees[ability_id] = tree 