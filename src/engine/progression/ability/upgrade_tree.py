# src/engine/progression/ability/upgrade_tree.py

class UpgradeNode:
    """
    Represents a single upgrade node in the ability upgrade tree.
    """
    def __init__(self, upgrade_id, description, modifier, required_level=1, prerequisites=None):
        self.upgrade_id = upgrade_id
        self.description = description
        self.modifier = modifier  # Instance of an AbilityModifier subclass
        self.required_level = required_level
        self.prerequisites = prerequisites if prerequisites else [] # List of upgrade_ids

class AbilityUpgradeTree:
    """
    Defines the upgrade tree structure for a specific ability.
    """
    def __init__(self, ability_id):
        self.ability_id = ability_id
        self.nodes = {} # Dictionary mapping upgrade_id to UpgradeNode

    def add_node(self, node):
        """
        Adds an upgrade node to the tree.
        """
        if node.upgrade_id in self.nodes:
            print(f"Warning: Upgrade node {node.upgrade_id} already exists for ability {self.ability_id}.")
        self.nodes[node.upgrade_id] = node

    def get_available_upgrades(self, current_level, unlocked_upgrade_ids):
        """
        Returns a list of upgrade nodes that can be unlocked.
        """
        available = []
        for node_id, node in self.nodes.items():
            if node_id not in unlocked_upgrade_ids and node.required_level <= current_level:
                # Check if all prerequisites are met
                prereqs_met = all(prereq_id in unlocked_upgrade_ids for prereq_id in node.prerequisites)
                if prereqs_met:
                    available.append(node)
        return available

# Example Usage (can be loaded from data files later)
# from .ability_modifiers import DamageModifier, RangeModifier
#
# fireball_tree = AbilityUpgradeTree("fireball")
#
# fireball_tree.add_node(UpgradeNode("fb_dmg_1", "Increase damage by 10%", DamageModifier(damage_increase_percentage=10), required_level=2))
# fireball_tree.add_node(UpgradeNode("fb_range_1", "Increase range by 5", RangeModifier(flat_range_increase=5), required_level=3))
# fireball_tree.add_node(UpgradeNode("fb_dmg_2", "Increase damage by 15%", DamageModifier(damage_increase_percentage=15), required_level=5, prerequisites=["fb_dmg_1"]))