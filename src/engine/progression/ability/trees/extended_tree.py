# src/engine/progression/ability/trees/extended_tree.py

import random
from ..upgrade_tree import AbilityUpgradeTree
from .procedural_node import GeneratedUpgradeNode

class ExtendedUpgradeTree(AbilityUpgradeTree):
    """
    An extension of AbilityUpgradeTree that supports dynamic procedural branches.
    This tree starts with fixed nodes but can grow procedural branches after
    specific nodes are unlocked.
    """
    def __init__(self, ability_id, max_procedural_depth=3, max_branches=2):
        """
        Initialize an extended upgrade tree with procedural capabilities.
        
        Args:
            ability_id (str): The ID of the ability this tree represents.
            max_procedural_depth (int): Maximum depth of procedural branches.
            max_branches (int): Maximum branches per terminal node.
        """
        super().__init__(ability_id)
        self.max_procedural_depth = max_procedural_depth
        self.max_branches = max_branches
        self.procedural_enabled = False
        self.procedural_nodes = {}  # Dictionary mapping node_id to procedural nodes
        self.terminal_nodes = set()  # Set of node IDs that can grow procedural branches
        self.current_depth = {}  # Dictionary mapping node_id to its depth in the tree
        
    def add_node(self, node):
        """
        Adds an upgrade node to the tree.
        
        Args:
            node: The node to add (UpgradeNode or GeneratedUpgradeNode).
        """
        super().add_node(node)
        
        # If this is a procedural node, add it to the procedural nodes dictionary
        if hasattr(node, 'is_procedural') and node.is_procedural:
            self.procedural_nodes[node.upgrade_id] = node
        
        # Update depth information
        self._update_depth_info(node.upgrade_id)
        
        # Update terminal nodes
        self._update_terminal_nodes()
            
    def _update_depth_info(self, node_id, parent_depth=0):
        """
        Update the depth information for a node and its children.
        
        Args:
            node_id (str): The ID of the node to update.
            parent_depth (int): The depth of the parent node.
        """
        # Set depth for this node
        self.current_depth[node_id] = parent_depth + 1
        
        # Find all nodes that have this node as a prerequisite
        children = [nid for nid, node in self.nodes.items() 
                  if node_id in node.prerequisites]
        
        # Update depth for children
        for child_id in children:
            self._update_depth_info(child_id, self.current_depth[node_id])
            
    def _update_terminal_nodes(self):
        """
        Update the set of terminal nodes that can grow procedural branches.
        A terminal node is one that has no children in the tree.
        """
        # Get all nodes that are prerequisites for other nodes
        prerequisite_nodes = set()
        for node in self.nodes.values():
            prerequisite_nodes.update(node.prerequisites)
            
        # Terminal nodes are those that are not prerequisites for any other node
        self.terminal_nodes = {node_id for node_id in self.nodes 
                             if node_id not in prerequisite_nodes}
                
    def enable_procedural_generation(self, seed=None, generator=None):
        """
        Enable procedural generation for this tree.
        
        Args:
            seed (str): Optional seed for deterministic generation.
            generator: Optional ability generator instance to use.
            
        Returns:
            bool: True if procedural generation was enabled.
        """
        if self.procedural_enabled:
            return False  # Already enabled
            
        self.procedural_enabled = True
        
        # Generate procedural branches from terminal nodes
        if generator:
            for node_id in self.terminal_nodes:
                self._grow_procedural_branch(node_id, seed, generator)
                
        return True
        
    def _grow_procedural_branch(self, terminal_node_id, seed=None, generator=None, depth=0):
        """
        Grow a procedural branch from a terminal node.
        
        Args:
            terminal_node_id (str): The ID of the terminal node to grow from.
            seed (str): Optional seed for deterministic generation.
            generator: Optional ability generator instance to use.
            depth (int): Current depth of the branch.
            
        Returns:
            list: List of procedural node IDs in the new branch.
        """
        if depth >= self.max_procedural_depth:
            return []  # Maximum depth reached
            
        if terminal_node_id not in self.nodes:
            return []  # Node does not exist
            
        # Generate a list of new procedural nodes
        new_node_ids = []
        parent_node = self.nodes[terminal_node_id]
        
        # Number of branches to generate
        num_branches = random.randint(1, self.max_branches)
        
        for i in range(num_branches):
            # Generate unique ID for the new node
            branch_seed = seed or random.randint(0, 1000000)
            branch_seed = f"{branch_seed}_{terminal_node_id}_{depth}_{i}"
            new_id = f"proc_{self.ability_id}_{terminal_node_id}_{depth}_{i}"
            
            # Get parent node required level to calculate new level requirement
            parent_level = parent_node.required_level
            # New level should be higher but not too much
            level_increase = random.randint(1, 3)
            new_level = parent_level + level_increase
            
            # Determine rarity and complexity based on depth
            rarity = self._get_rarity_for_depth(depth)
            complexity = self._get_complexity_for_depth(depth)
            
            if generator:
                # Use generator to create a procedural node
                try:
                    # Generate properties
                    props = generator.generate_upgrade_properties(
                        branch_seed, complexity, rarity, self.ability_id, parent_node
                    )
                    
                    # Create node modifier
                    modifier = generator.create_modifier_from_properties(props)
                    
                    # Create the node
                    new_node = GeneratedUpgradeNode(
                        upgrade_id=new_id,
                        description=props.get("description", f"Procedural Upgrade {new_id}"),
                        modifier=modifier,
                        required_level=new_level,
                        prerequisites=[terminal_node_id],
                        generation_seed=branch_seed,
                        complexity=complexity,
                        rarity=rarity
                    )
                    
                    # Add the node to the tree
                    self.add_node(new_node)
                    new_node_ids.append(new_id)
                    
                    # Recursively grow branches from this node
                    child_ids = self._grow_procedural_branch(new_id, branch_seed, generator, depth + 1)
                    new_node_ids.extend(child_ids)
                    
                except Exception as e:
                    print(f"Error generating procedural node from {terminal_node_id}: {e}")
                    continue
                    
        return new_node_ids
        
    def _get_rarity_for_depth(self, depth):
        """
        Get appropriate rarity for a node at the given depth.
        
        Args:
            depth (int): Depth of the node in the tree.
            
        Returns:
            str: Rarity level.
        """
        # Higher depth increases chances of higher rarity
        rarities = ["common", "uncommon", "rare", "epic", "legendary"]
        weights = [
            max(70 - depth * 20, 10),  # common: decreases with depth
            max(20 + depth * 5, 10),   # uncommon: slight increase
            max(8 + depth * 10, 10),   # rare: medium increase
            max(2 + depth * 5, 5),     # epic: small increase
            max(0 + depth * 2, 0)      # legendary: very small increase
        ]
        
        # Normalize weights
        total = sum(weights)
        if total <= 0:
            return "common"
            
        weights = [w / total for w in weights]
        
        # Random choice based on weights
        return random.choices(rarities, weights=weights, k=1)[0]
        
    def _get_complexity_for_depth(self, depth):
        """
        Get appropriate complexity for a node at the given depth.
        
        Args:
            depth (int): Depth of the node in the tree.
            
        Returns:
            int: Complexity value (1-10).
        """
        # Base complexity increases with depth
        base = 1 + depth * 2
        # Add some randomness
        variation = random.randint(-1, 1)
        # Clamp to 1-10 range
        return max(1, min(10, base + variation))
        
    def regenerate_procedural_branches(self, seed=None, generator=None):
        """
        Regenerate all procedural branches in the tree.
        
        Args:
            seed (str): Optional seed for deterministic generation.
            generator: Optional ability generator instance to use.
            
        Returns:
            bool: True if regeneration was successful.
        """
        if not self.procedural_enabled:
            return False
            
        # Remove all procedural nodes
        to_remove = list(self.procedural_nodes.keys())
        for node_id in to_remove:
            self.nodes.pop(node_id, None)
            
        self.procedural_nodes = {}
        
        # Update terminal nodes
        self._update_terminal_nodes()
        
        # Regenerate procedural branches
        if generator:
            for node_id in self.terminal_nodes:
                self._grow_procedural_branch(node_id, seed, generator)
                
        return True
        
    def regenerate_node(self, node_id, seed=None, generator=None):
        """
        Regenerate a specific procedural node.
        
        Args:
            node_id (str): The ID of the node to regenerate.
            seed (str): Optional seed for deterministic generation.
            generator: Optional ability generator instance to use.
            
        Returns:
            bool: True if regeneration was successful.
        """
        if node_id not in self.procedural_nodes:
            return False
            
        try:
            # Regenerate the node
            node = self.procedural_nodes[node_id]
            return node.regenerate(seed, generator)
        except Exception as e:
            print(f"Error regenerating node {node_id}: {e}")
            return False
            
    def to_dict(self):
        """
        Convert the tree to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the tree.
        """
        tree_dict = {
            "ability_id": self.ability_id,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "procedural_enabled": self.procedural_enabled,
            "max_procedural_depth": self.max_procedural_depth,
            "max_branches": self.max_branches,
            "terminal_nodes": list(self.terminal_nodes)
        }
        return tree_dict
        
    @classmethod
    def from_dict(cls, data, modifier_factory=None):
        """
        Create a tree from a dictionary.
        
        Args:
            data (dict): Dictionary data for the tree.
            modifier_factory: Function to create modifier objects from data.
            
        Returns:
            ExtendedUpgradeTree: New tree instance.
        """
        tree = cls(
            ability_id=data["ability_id"],
            max_procedural_depth=data.get("max_procedural_depth", 3),
            max_branches=data.get("max_branches", 2)
        )
        
        # Set procedural attributes
        tree.procedural_enabled = data.get("procedural_enabled", False)
        tree.terminal_nodes = set(data.get("terminal_nodes", []))
        
        # Create and add all nodes
        for node_id, node_data in data.get("nodes", {}).items():
            # Determine if this is a procedural node
            if node_data.get("is_procedural", False):
                # Create procedural node
                from .procedural_node import GeneratedUpgradeNode
                node = GeneratedUpgradeNode.from_dict(node_data, modifier_factory)
                tree.procedural_nodes[node_id] = node
            else:
                # Create regular node
                from ..upgrade_tree import UpgradeNode
                
                # Create modifier instance if factory provided
                modifier = None
                if modifier_factory and "modifier_data" in node_data:
                    modifier = modifier_factory(node_data["modifier_data"])
                    
                node = UpgradeNode(
                    upgrade_id=node_data["upgrade_id"],
                    description=node_data["description"],
                    modifier=modifier,
                    required_level=node_data["required_level"],
                    prerequisites=node_data.get("prerequisites", [])
                )
                
            # Add the node to the tree
            tree.nodes[node_id] = node
            
        # Update depth information for all nodes
        for node_id in tree.nodes:
            tree._update_depth_info(node_id)
            
        return tree 