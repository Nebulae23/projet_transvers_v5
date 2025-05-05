# src/engine/progression/ability/trees/procedural_node.py

import random
import hashlib
from ..upgrade_tree import UpgradeNode

class GeneratedUpgradeNode(UpgradeNode):
    """
    An extension of UpgradeNode that supports procedural generation.
    This node can be regenerated with different properties based on seeds.
    """
    def __init__(self, upgrade_id, description, modifier, required_level=1, prerequisites=None, 
                 generation_seed=None, complexity=1, rarity="common"):
        """
        Initialize a procedurally generated upgrade node.
        
        Args:
            upgrade_id (str): Unique identifier for this upgrade.
            description (str): Description of what this upgrade does.
            modifier: The modifier object that will be applied when this upgrade is chosen.
            required_level (int): Minimum level required to unlock this upgrade.
            prerequisites (list): List of upgrade_ids that must be unlocked first.
            generation_seed (str): Seed for procedural generation.
            complexity (int): Complexity level (1-10) affecting the power of generated properties.
            rarity (str): Rarity level of the upgrade (common, uncommon, rare, epic, legendary).
        """
        super().__init__(upgrade_id, description, modifier, required_level, prerequisites)
        self.generation_seed = generation_seed or self._generate_seed()
        self.complexity = complexity
        self.rarity = rarity
        self.is_procedural = True
        self.generation_history = []  # Track regeneration history
        
        # Visual properties for UI representation
        self.visual_properties = {
            "color": self._get_rarity_color(),
            "border_style": "dashed" if self.is_procedural else "solid",
            "special_effect": self._get_special_effect()
        }
        
    def _generate_seed(self):
        """Generate a random seed for procedural generation."""
        return hashlib.md5(str(random.randint(0, 1000000)).encode()).hexdigest()
        
    def _get_rarity_color(self):
        """Return color based on rarity for UI representation."""
        rarity_colors = {
            "common": (150, 150, 150),       # Gray
            "uncommon": (0, 180, 0),         # Green
            "rare": (0, 70, 200),            # Blue
            "epic": (180, 0, 180),           # Purple
            "legendary": (255, 165, 0)       # Orange
        }
        return rarity_colors.get(self.rarity, (255, 255, 255))
        
    def _get_special_effect(self):
        """Return special visual effect based on rarity and complexity."""
        if self.rarity == "legendary":
            return "glow"
        elif self.rarity == "epic":
            return "pulse"
        elif self.complexity >= 8:
            return "shimmer"
        return None
        
    def regenerate(self, new_seed=None, generator=None):
        """
        Regenerate the node with potentially new properties.
        
        Args:
            new_seed (str): Optional new seed for generation.
            generator: Optional ability generator instance to use.
            
        Returns:
            bool: True if regeneration was successful.
        """
        # Store current state in history
        self.generation_history.append({
            "seed": self.generation_seed,
            "description": self.description,
            "modifier": self.modifier,
            "required_level": self.required_level,
            "complexity": self.complexity,
            "rarity": self.rarity
        })
        
        # Set new seed if provided
        if new_seed:
            self.generation_seed = new_seed
        else:
            self.generation_seed = self._generate_seed()
            
        # If a generator is provided, use it to regenerate properties
        if generator:
            try:
                # Generate new properties based on seed and complexity
                new_properties = generator.generate_upgrade_properties(
                    self.generation_seed, 
                    self.complexity, 
                    self.rarity
                )
                
                # Update node properties
                self.description = new_properties.get("description", self.description)
                self.modifier = new_properties.get("modifier", self.modifier)
                # Don't decrease required level when regenerating
                if "required_level" in new_properties and new_properties["required_level"] > self.required_level:
                    self.required_level = new_properties["required_level"]
                
                # Update visual properties
                self.visual_properties = {
                    "color": self._get_rarity_color(),
                    "border_style": "dashed",
                    "special_effect": self._get_special_effect()
                }
                
                return True
            except Exception as e:
                print(f"Error regenerating node {self.upgrade_id}: {e}")
                # Revert to last state in history
                self._revert_to_last_state()
                return False
        
        return True
    
    def _revert_to_last_state(self):
        """Revert to the previous state from history if available."""
        if self.generation_history:
            last_state = self.generation_history.pop()
            self.generation_seed = last_state["seed"]
            self.description = last_state["description"]
            self.modifier = last_state["modifier"]
            self.required_level = last_state["required_level"]
            self.complexity = last_state["complexity"]
            self.rarity = last_state["rarity"]
            
    def upgrade_rarity(self, new_rarity):
        """
        Upgrade the node to a higher rarity level.
        
        Args:
            new_rarity (str): New rarity level.
            
        Returns:
            bool: True if upgrade was successful.
        """
        rarity_levels = ["common", "uncommon", "rare", "epic", "legendary"]
        current_index = rarity_levels.index(self.rarity) if self.rarity in rarity_levels else 0
        new_index = rarity_levels.index(new_rarity) if new_rarity in rarity_levels else 0
        
        if new_index <= current_index:
            return False  # Cannot downgrade rarity
            
        # Store current state in history
        self.generation_history.append({
            "seed": self.generation_seed,
            "description": self.description,
            "modifier": self.modifier,
            "required_level": self.required_level,
            "complexity": self.complexity,
            "rarity": self.rarity
        })
        
        self.rarity = new_rarity
        # Increase complexity with rarity
        self.complexity += (new_index - current_index)
        
        # Update visual properties
        self.visual_properties["color"] = self._get_rarity_color()
        self.visual_properties["special_effect"] = self._get_special_effect()
        
        return True
        
    def increase_complexity(self, amount=1):
        """
        Increase the complexity of the node.
        
        Args:
            amount (int): Amount to increase complexity.
            
        Returns:
            bool: True if increase was successful.
        """
        if self.complexity + amount > 10:
            return False  # Max complexity is 10
            
        # Store current state in history
        self.generation_history.append({
            "seed": self.generation_seed,
            "description": self.description,
            "modifier": self.modifier,
            "required_level": self.required_level,
            "complexity": self.complexity,
            "rarity": self.rarity
        })
        
        self.complexity += amount
        self.visual_properties["special_effect"] = self._get_special_effect()
        
        return True
        
    def to_dict(self):
        """
        Convert the node to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the node.
        """
        node_dict = super().to_dict() if hasattr(super(), "to_dict") else {
            "upgrade_id": self.upgrade_id,
            "description": self.description,
            "required_level": self.required_level,
            "prerequisites": self.prerequisites
        }
        
        # Add procedural-specific properties
        node_dict.update({
            "is_procedural": True,
            "generation_seed": self.generation_seed,
            "complexity": self.complexity,
            "rarity": self.rarity,
            "visual_properties": self.visual_properties
        })
        
        return node_dict
        
    @classmethod
    def from_dict(cls, data, modifier_factory=None):
        """
        Create a node from a dictionary.
        
        Args:
            data (dict): Dictionary data for the node.
            modifier_factory: Function to create modifier objects from data.
            
        Returns:
            GeneratedUpgradeNode: New node instance.
        """
        # Create modifier instance if factory provided
        modifier = None
        if modifier_factory and "modifier_data" in data:
            modifier = modifier_factory(data["modifier_data"])
            
        # Create node
        node = cls(
            upgrade_id=data["upgrade_id"],
            description=data["description"],
            modifier=modifier,
            required_level=data["required_level"],
            prerequisites=data.get("prerequisites", []),
            generation_seed=data.get("generation_seed"),
            complexity=data.get("complexity", 1),
            rarity=data.get("rarity", "common")
        )
        
        # Restore additional properties
        if "visual_properties" in data:
            node.visual_properties = data["visual_properties"]
            
        return node 