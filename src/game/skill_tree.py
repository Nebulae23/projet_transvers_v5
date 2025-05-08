#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skill Tree System for Nightfall Defenders
Implements a node-based skill tree with unlockable abilities and stat improvements
"""

from enum import Enum
import uuid

class SkillType(Enum):
    """Enumeration of different skill types"""
    STAT_BOOST = "stat_boost"  # Increases player stats
    ABILITY_UNLOCK = "ability_unlock"  # Unlocks a new ability
    ABILITY_MODIFIER = "ability_modifier"  # Modifies an existing ability
    PASSIVE = "passive"  # Passive effect
    SPECIALIZATION = "specialization"  # Specialization choice node
    FUSION = "fusion"  # Unlocks fusion capability


class SkillNode:
    """Represents a single node in the skill tree"""
    
    def __init__(self, 
                 node_id, 
                 name, 
                 description, 
                 skill_type, 
                 effects,
                 position=(0, 0),
                 icon=None,
                 cost=None,
                 required_class=None):
        """
        Initialize a skill node
        
        Args:
            node_id (str): Unique identifier for the node
            name (str): Display name of the skill
            description (str): Description of the skill's effects
            skill_type (SkillType): Type of skill
            effects (dict): Dictionary of effects this skill provides
            position (tuple): (x, y) position in the skill tree for UI
            icon (str): Path to the icon texture
            cost (dict): Resources required to unlock this node
            required_class (str): Class required to unlock this node, or None if any class can unlock
        """
        self.node_id = node_id
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.effects = effects
        self.position = position
        self.icon = icon
        self.cost = cost or {"monster_essence": 10}  # Default cost
        self.required_class = required_class
        
        # Node state
        self.is_unlocked = False
        self.is_visible = False
        
        # Connections
        self.parents = []  # Nodes that must be unlocked before this one
        self.children = []  # Nodes that this one unlocks
    
    def add_parent(self, parent_node):
        """
        Add a parent node to this node
        
        Args:
            parent_node (SkillNode): Parent node
        """
        if parent_node not in self.parents:
            self.parents.append(parent_node)
            
        # Add this node as a child of the parent
        if self not in parent_node.children:
            parent_node.children.append(self)
    
    def add_child(self, child_node):
        """
        Add a child node to this node
        
        Args:
            child_node (SkillNode): Child node
        """
        if child_node not in self.children:
            self.children.append(child_node)
            
        # Add this node as a parent of the child
        if self not in child_node.parents:
            child_node.parents.append(self)
    
    def can_unlock(self, player):
        """
        Check if this node can be unlocked by the player
        
        Args:
            player: Player entity
            
        Returns:
            tuple: (can_unlock, reason) - Boolean indicating if it can be unlocked and reason if not
        """
        # Check if already unlocked
        if self.is_unlocked:
            return False, "Already unlocked"
        
        # Check if visible (connected to an unlocked node)
        if not self.is_visible:
            return False, "Not yet visible"
            
        # Check class requirement
        if self.required_class and player.character_class != self.required_class:
            return False, f"Requires {self.required_class} class"
        
        # Check if all parents are unlocked
        if not all(parent.is_unlocked for parent in self.parents):
            return False, "Prerequisites not met"
        
        # Check if player has enough resources
        for resource, amount in self.cost.items():
            if player.inventory.get(resource, 0) < amount:
                return False, f"Not enough {resource}"
        
        return True, "Can unlock"
    
    def unlock(self, player):
        """
        Unlock this node, consuming resources
        
        Args:
            player: Player entity
            
        Returns:
            bool: True if unlocked successfully, False otherwise
        """
        can_unlock, reason = self.can_unlock(player)
        if not can_unlock:
            print(f"Cannot unlock {self.name}: {reason}")
            return False
        
        # Consume resources
        for resource, amount in self.cost.items():
            player.inventory[resource] = player.inventory.get(resource, 0) - amount
        
        # Mark as unlocked
        self.is_unlocked = True
        
        # Update visibility of child nodes
        for child in self.children:
            child.is_visible = True
        
        print(f"Unlocked skill: {self.name}")
        return True
    
    def apply_effects(self, player):
        """
        Apply this node's effects to the player
        
        Args:
            player: Player entity
        """
        if not self.is_unlocked:
            return
        
        # Apply effects based on skill type
        if self.skill_type == SkillType.STAT_BOOST:
            for stat, value in self.effects.items():
                if stat == "max_health":
                    player.max_health += value
                    player.health = min(player.health + value, player.max_health)
                elif stat == "speed":
                    player.speed += value
                elif stat == "damage_multiplier":
                    player.damage_multiplier += value
                # Add other stats as needed
        
        elif self.skill_type == SkillType.ABILITY_UNLOCK:
            ability_id = self.effects.get("ability_id")
            if ability_id and hasattr(player, "unlock_ability"):
                player.unlock_ability(ability_id)
        
        elif self.skill_type == SkillType.ABILITY_MODIFIER:
            ability_id = self.effects.get("ability_id")
            modifiers = self.effects.get("modifiers", {})
            if ability_id and hasattr(player, "modify_ability"):
                player.modify_ability(ability_id, modifiers)
        
        elif self.skill_type == SkillType.PASSIVE:
            passive_id = self.effects.get("passive_id")
            if passive_id and hasattr(player, "add_passive"):
                player.add_passive(passive_id, self.effects)
        
        elif self.skill_type == SkillType.SPECIALIZATION:
            spec_path = self.effects.get("specialization_path")
            if spec_path and hasattr(player, "set_specialization"):
                player.set_specialization(spec_path)
        
        elif self.skill_type == SkillType.FUSION:
            fusion_type = self.effects.get("fusion_type")
            if fusion_type and hasattr(player, "unlock_fusion_type"):
                player.unlock_fusion_type(fusion_type)


class SkillTree:
    """Manages a complete skill tree with multiple nodes"""
    
    def __init__(self):
        """Initialize the skill tree"""
        self.nodes = {}  # Dictionary of all nodes by ID
        self.root_nodes = []  # Starting nodes of the tree
    
    def add_node(self, node):
        """
        Add a node to the skill tree
        
        Args:
            node (SkillNode): Node to add
        """
        self.nodes[node.node_id] = node
        
        # If this node has no parents, it's a root node
        if not node.parents:
            self.root_nodes.append(node)
            node.is_visible = True  # Root nodes are always visible
    
    def connect_nodes(self, parent_id, child_id):
        """
        Connect two nodes as parent-child
        
        Args:
            parent_id (str): ID of the parent node
            child_id (str): ID of the child node
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if parent_id not in self.nodes or child_id not in self.nodes:
            return False
        
        parent = self.nodes[parent_id]
        child = self.nodes[child_id]
        
        parent.add_child(child)
        return True
    
    def get_visible_nodes(self, player):
        """
        Get all nodes that should be visible to the player
        
        Args:
            player: Player entity
            
        Returns:
            list: List of visible SkillNodes
        """
        return [node for node in self.nodes.values() if node.is_visible]
    
    def get_unlockable_nodes(self, player):
        """
        Get all nodes that can currently be unlocked by the player
        
        Args:
            player: Player entity
            
        Returns:
            list: List of unlockable SkillNodes
        """
        return [node for node in self.get_visible_nodes(player) 
                if node.can_unlock(player)[0]]
    
    def reset(self):
        """Reset the skill tree to its initial state"""
        for node in self.nodes.values():
            node.is_unlocked = False
            node.is_visible = False
        
        # Make root nodes visible
        for node in self.root_nodes:
            node.is_visible = True
    
    def create_from_template(self, template):
        """
        Create skill tree from a template
        
        Args:
            template (dict): Template for skill tree
            
        Returns:
            bool: True if created successfully
        """
        if not template:
            return False
            
        # Clear existing skills
        self.skills = {}
        self.skill_groups = {}
        self.selected_skills = set()
        
        # Add groups
        for group_id, group_data in template.get('groups', {}).items():
            self.skill_groups[group_id] = {
                'name': group_data.get('name', 'Unnamed Group'),
                'description': group_data.get('description', ''),
                'skills': []
            }
        
        # Add skills
        for skill_id, skill_data in template.get('skills', {}).items():
            skill = {
                'id': skill_id,
                'name': skill_data.get('name', 'Unnamed Skill'),
                'description': skill_data.get('description', ''),
                'icon': skill_data.get('icon', 'default_icon'),
                'cost': skill_data.get('cost', 1),
                'prerequisites': skill_data.get('prerequisites', []),
                'effects': skill_data.get('effects', {}),
                'group': skill_data.get('group', None),
                'position': skill_data.get('position', (0, 0)),
                'tier': skill_data.get('tier', 1),
                'unlocked': False
            }
            
            self.skills[skill_id] = skill
            
            # Add to group if specified
            if skill.get('group') and skill.get('group') in self.skill_groups:
                self.skill_groups[skill.get('group')]['skills'].append(skill_id)
                
        return True
                
    def add_harmonization_skills(self, skill_definitions):
        """
        Add harmonization-related skills to the skill tree
        
        Args:
            skill_definitions: Skill definitions manager
            
        Returns:
            bool: True if added successfully
        """
        # Create harmonization skill group if it doesn't exist
        if 'harmonization' not in self.skill_groups:
            self.skill_groups['harmonization'] = {
                'name': 'Ability Harmonization',
                'description': 'Unlock the power to harmonize your abilities, enhancing their effects',
                'skills': []
            }
            
        # Add basic harmonization skill
        basic_harmonization = {
            'id': 'basic_harmonization',
            'name': 'Ability Harmonization',
            'description': 'Unlock the ability to harmonize your abilities, enhancing their effects.',
            'icon': 'harmonization_icon',
            'cost': 3,
            'prerequisites': [],  # No prerequisites
            'effects': {
                'unlock_ability': 'can_harmonize_abilities'
            },
            'group': 'harmonization',
            'position': (0, 0),
            'tier': 3,  # Higher tier ability
            'unlocked': False
        }
        
        self.skills['basic_harmonization'] = basic_harmonization
        self.skill_groups['harmonization']['skills'].append('basic_harmonization')
        
        # Add element-specific harmonization skills
        element_skills = [
            {
                'id': 'fire_harmonization',
                'name': 'Fire Harmonization',
                'description': 'Unlock advanced harmonization for fire abilities.',
                'icon': 'fire_harmonization_icon',
                'cost': 2,
                'prerequisites': ['basic_harmonization'],
                'effects': {
                    'unlock_ability': 'fire_harmonization'
                },
                'group': 'harmonization',
                'position': (-1, 1),
                'tier': 4,
                'unlocked': False
            },
            {
                'id': 'ice_harmonization',
                'name': 'Ice Harmonization',
                'description': 'Unlock advanced harmonization for ice abilities.',
                'icon': 'ice_harmonization_icon',
                'cost': 2,
                'prerequisites': ['basic_harmonization'],
                'effects': {
                    'unlock_ability': 'ice_harmonization'
                },
                'group': 'harmonization',
                'position': (0, 1),
                'tier': 4,
                'unlocked': False
            },
            {
                'id': 'lightning_harmonization',
                'name': 'Lightning Harmonization',
                'description': 'Unlock advanced harmonization for lightning abilities.',
                'icon': 'lightning_harmonization_icon',
                'cost': 2,
                'prerequisites': ['basic_harmonization'],
                'effects': {
                    'unlock_ability': 'lightning_harmonization'
                },
                'group': 'harmonization',
                'position': (1, 1),
                'tier': 4,
                'unlocked': False
            }
        ]
        
        # Add ability type harmonization skills
        type_skills = [
            {
                'id': 'projectile_harmonization',
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
                'unlocked': False
            },
            {
                'id': 'area_harmonization',
                'name': 'Area Harmonization',
                'description': 'Unlock advanced harmonization for area abilities.',
                'icon': 'area_harmonization_icon',
                'cost': 2,
                'prerequisites': ['basic_harmonization'],
                'effects': {
                    'unlock_ability': 'area_harmonization'
                },
                'group': 'harmonization',
                'position': (0, 2),
                'tier': 4,
                'unlocked': False
            },
            {
                'id': 'melee_harmonization',
                'name': 'Melee Harmonization',
                'description': 'Unlock advanced harmonization for melee abilities.',
                'icon': 'melee_harmonization_icon',
                'cost': 2,
                'prerequisites': ['basic_harmonization'],
                'effects': {
                    'unlock_ability': 'melee_harmonization'
                },
                'group': 'harmonization',
                'position': (1, 2),
                'tier': 4,
                'unlocked': False
            }
        ]
        
        # Advanced harmonization skill (master)
        master_harmonization = {
            'id': 'master_harmonization',
            'name': 'Master Harmonization',
            'description': 'Master the art of harmonization, enabling more powerful enhancements.',
            'icon': 'master_harmonization_icon',
            'cost': 5,
            'prerequisites': ['fire_harmonization', 'ice_harmonization', 'lightning_harmonization', 
                             'projectile_harmonization', 'area_harmonization', 'melee_harmonization'],
            'effects': {
                'unlock_ability': 'master_harmonization',
                'harmonization_power': 1.5  # 50% more powerful harmonization effects
            },
            'group': 'harmonization',
            'position': (0, 3),
            'tier': 5,
            'unlocked': False
        }
        
        # Add all skills
        for skill in element_skills + type_skills:
            self.skills[skill['id']] = skill
            self.skill_groups['harmonization']['skills'].append(skill['id'])
            
        self.skills['master_harmonization'] = master_harmonization
        self.skill_groups['harmonization']['skills'].append('master_harmonization')
        
        return True
    
    def apply_all_effects(self, player):
        """
        Apply effects from all unlocked nodes to the player
        
        Args:
            player: Player entity
        """
        for node in self.nodes.values():
            if node.is_unlocked:
                node.apply_effects(player)


# Example of creating a simple skill tree
def create_basic_skill_tree():
    """Create a basic skill tree for testing"""
    tree = SkillTree()
    
    # Create root nodes (one per class)
    warrior_root = SkillNode(
        "warrior_root",
        "Warrior Path",
        "Begin the path of the Warrior",
        SkillType.PASSIVE,
        {"passive_id": "warrior_base"},
        position=(0, 0),
        icon="warrior_icon.png",
        required_class="warrior"
    )
    
    mage_root = SkillNode(
        "mage_root",
        "Mage Path",
        "Begin the path of the Mage",
        SkillType.PASSIVE,
        {"passive_id": "mage_base"},
        position=(10, 0),
        icon="mage_icon.png",
        required_class="mage"
    )
    
    cleric_root = SkillNode(
        "cleric_root",
        "Cleric Path",
        "Begin the path of the Cleric",
        SkillType.PASSIVE,
        {"passive_id": "cleric_base"},
        position=(20, 0),
        icon="cleric_icon.png",
        required_class="cleric"
    )
    
    ranger_root = SkillNode(
        "ranger_root",
        "Ranger Path",
        "Begin the path of the Ranger",
        SkillType.PASSIVE,
        {"passive_id": "ranger_base"},
        position=(30, 0),
        icon="ranger_icon.png",
        required_class="ranger"
    )
    
    # Add roots to tree
    tree.add_node(warrior_root)
    tree.add_node(mage_root)
    tree.add_node(cleric_root)
    tree.add_node(ranger_root)
    
    # Create and connect some child nodes
    strength_node = SkillNode(
        "strength_1",
        "Strength I",
        "Increase your strength",
        SkillType.STAT_BOOST,
        {"damage_multiplier": 0.1},
        position=(0, 5),
        cost={"monster_essence": 15}
    )
    tree.add_node(strength_node)
    warrior_root.add_child(strength_node)
    
    fireball_node = SkillNode(
        "fireball_1",
        "Fireball",
        "Learn to cast Fireball",
        SkillType.ABILITY_UNLOCK,
        {"ability_id": "fireball"},
        position=(10, 5),
        cost={"monster_essence": 20}
    )
    tree.add_node(fireball_node)
    mage_root.add_child(fireball_node)
    
    return tree 