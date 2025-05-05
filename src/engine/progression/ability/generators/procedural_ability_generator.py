# src/engine/progression/ability/generators/procedural_ability_generator.py

import json
import random
import math
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..ability_modifiers import AbilityModifier, DamageModifier, RangeModifier

class AbilityGenerator:
    """
    Generates procedural abilities and upgrade nodes based on templates and configuration.
    """
    def __init__(self, templates_path: Path, config_path: Path):
        """
        Initialize the ability generator with templates and configuration.
        
        Args:
            templates_path (Path): Path to the ability templates JSON file.
            config_path (Path): Path to the generation configuration JSON file.
        """
        self.templates = self._load_json(templates_path)
        self.config = self._load_json(config_path)
        
        # Set up seed-based random generator
        self.rand = random.Random()
        
        # Track generated abilities to avoid duplicates
        self.generated_ids = set()

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
            
    def set_seed(self, seed: Any):
        """
        Set the seed for random generation to ensure reproducibility.
        
        Args:
            seed: Seed value (will be converted to string and hashed).
        """
        # Convert seed to string and hash it for consistent integer
        seed_hash = int(hashlib.md5(str(seed).encode()).hexdigest(), 16) % (2**32)
        self.rand.seed(seed_hash)
        
    def generate_ability(self, player_level: int, class_type: str, 
                        base_ability_id: Optional[str] = None, 
                        rarity: Optional[str] = None) -> Dict:
        """
        Generate a procedural ability.
        
        Args:
            player_level (int): Current player level.
            class_type (str): Class type (warrior, mage, etc.).
            base_ability_id (str): Optional base ability to derive from.
            rarity (str): Optional rarity level to enforce.
            
        Returns:
            dict: Generated ability data.
        """
        # Determine rarity if not provided
        if rarity is None:
            rarity = self._select_rarity()
            
        # Determine template based on class
        template_type = self._select_template_for_class(class_type, base_ability_id)
        
        # Get base template
        template = self.templates.get("templates", {}).get(template_type, {})
        if not template:
            raise ValueError(f"No template found for type: {template_type}")
            
        # Generate unique ID
        ability_id = self._generate_unique_id(template_type, class_type, rarity)
        
        # Apply rarity modifiers
        rarity_data = self.templates.get("rarity_modifiers", {}).get(rarity, {"stat_multiplier": 1.0})
        stat_multiplier = rarity_data.get("stat_multiplier", 1.0)
        
        # Scale properties based on player level
        base_properties = template.get("base_properties", {}).copy()
        scaling = template.get("scaling", {})
        
        for prop, value in base_properties.items():
            if isinstance(value, (int, float)) and prop in scaling:
                # Scale property based on player level and rarity
                level_scaling = 1.0 + (player_level * scaling[prop])
                base_properties[prop] = round(value * level_scaling * stat_multiplier, 2)
                
                # Apply balance constraints
                balance = self.config.get("balance", {})
                if prop in balance:
                    prop_range = balance[prop + "_range"]
                    base_properties[prop] = max(prop_range[0], min(prop_range[1], base_properties[prop]))
        
        # Select ability modifiers based on rarity
        modifiers = self._select_modifiers(template, rarity_data.get("modifier_count", 0))
        
        # Select element if elemental is in modifiers
        element = None
        if "elemental" in modifiers and modifiers["elemental"]:
            element = self._select_element_for_class(class_type)
            
        # Generate name and description
        name = self._generate_ability_name(template_type, element, rarity)
        description = self._generate_ability_description(template_type, base_properties, modifiers, element)
        
        # Compile the ability data
        ability_data = {
            "id": ability_id,
            "name": name,
            "description": description,
            "type": template_type,
            "class": class_type,
            "rarity": rarity,
            "properties": base_properties,
            "modifiers": modifiers
        }
        
        if element:
            ability_data["element"] = element
            
        self.generated_ids.add(ability_id)
        return ability_data
    
    def _select_rarity(self) -> str:
        """
        Randomly select a rarity based on weights in config.
        
        Returns:
            str: Selected rarity.
        """
        rarities = []
        weights = []
        
        for rarity, data in self.config.get("rarity", {}).items():
            rarities.append(rarity)
            weights.append(data.get("weight", 1))
            
        if not rarities:
            return "common"
            
        return self.rand.choices(rarities, weights=weights, k=1)[0]
    
    def _select_template_for_class(self, class_type: str, base_ability_id: Optional[str] = None) -> str:
        """
        Select an appropriate template for the given class.
        
        Args:
            class_type (str): Class type (warrior, mage, etc.).
            base_ability_id (str): Optional base ability to derive from.
            
        Returns:
            str: Selected template type.
        """
        class_templates = self.templates.get("class_templates", {}).get(class_type, [])
        
        if not class_templates:
            # Fallback to default templates
            all_templates = list(self.templates.get("templates", {}).keys())
            return self.rand.choice(all_templates) if all_templates else "direct_damage"
            
        return self.rand.choice(class_templates)
    
    def _generate_unique_id(self, template_type: str, class_type: str, rarity: str) -> str:
        """
        Generate a unique ID for an ability.
        
        Args:
            template_type (str): Template type.
            class_type (str): Class type.
            rarity (str): Rarity level.
            
        Returns:
            str: Unique ability ID.
        """
        base = f"{class_type}_{template_type}_{rarity}"
        suffix = 1
        
        while f"{base}_{suffix}" in self.generated_ids:
            suffix += 1
            
        return f"{base}_{suffix}"
    
    def _select_modifiers(self, template: Dict, count: int) -> Dict[str, Any]:
        """
        Select modifiers for an ability based on template and count.
        
        Args:
            template (dict): Ability template.
            count (int): Number of modifiers to select.
            
        Returns:
            dict: Selected modifiers.
        """
        possible_modifiers = template.get("possible_modifiers", [])
        modifiers = {}
        
        if not possible_modifiers or count <= 0:
            return modifiers
            
        # Select 'count' unique modifiers
        selected = []
        for _ in range(min(count, len(possible_modifiers))):
            # Weight selection by base_chance
            weights = []
            available = [m for m in possible_modifiers if m not in selected]
            
            for modifier in available:
                modifier_data = self.config.get("ability_modifiers", {}).get(modifier, {})
                weights.append(modifier_data.get("base_chance", 0.1))
                
            if not available:
                break
                
            choice = self.rand.choices(available, weights=weights, k=1)[0]
            selected.append(choice)
            
        # Generate values for each selected modifier
        for modifier in selected:
            modifier_data = self.config.get("ability_modifiers", {}).get(modifier, {})
            effect = modifier_data.get("effect", {})
            
            # Generate values for each effect property
            modifier_values = {}
            for prop, range_values in effect.items():
                if isinstance(range_values, list) and len(range_values) == 2:
                    # Numeric range
                    min_val, max_val = range_values
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        value = self.rand.randint(min_val, max_val)
                    else:
                        value = self.rand.uniform(min_val, max_val)
                        value = round(value, 2)
                elif isinstance(range_values, list):
                    # Selection from list
                    value = self.rand.choice(range_values)
                else:
                    value = range_values
                    
                modifier_values[prop] = value
                
            modifiers[modifier] = modifier_values
            
        return modifiers
    
    def _select_element_for_class(self, class_type: str) -> str:
        """
        Select an appropriate element for the given class.
        
        Args:
            class_type (str): Class type.
            
        Returns:
            str: Selected element.
        """
        class_modifiers = self.config.get("class_modifiers", {}).get(class_type, {})
        preferred_elements = class_modifiers.get("preferred_elements", [])
        
        if preferred_elements and self.rand.random() < 0.7:  # 70% chance to use preferred element
            return self.rand.choice(preferred_elements)
            
        # Fallback to any element
        all_elements = list(self.templates.get("elements", {}).keys())
        return self.rand.choice(all_elements) if all_elements else "fire"
    
    def _generate_ability_name(self, template_type: str, element: Optional[str], rarity: str) -> str:
        """
        Generate a name for an ability.
        
        Args:
            template_type (str): Template type.
            element (str): Element type.
            rarity (str): Rarity level.
            
        Returns:
            str: Generated name.
        """
        prefixes = self.templates.get("name_prefixes", {})
        suffixes = self.templates.get("name_suffixes", {})
        
        prefix_options = []
        if element and element in prefixes:
            prefix_options.extend(prefixes[element])
        if rarity in prefixes:
            prefix_options.extend(prefixes[rarity])
            
        suffix_options = []
        if template_type in suffixes:
            suffix_options.extend(suffixes[template_type])
            
        if not prefix_options:
            prefix_options = ["Mysterious"]
        if not suffix_options:
            suffix_options = ["Ability"]
            
        prefix = self.rand.choice(prefix_options)
        suffix = self.rand.choice(suffix_options)
        
        return f"{prefix} {suffix}"
    
    def _generate_ability_description(self, template_type: str, properties: Dict, 
                                     modifiers: Dict, element: Optional[str]) -> str:
        """
        Generate a description for an ability.
        
        Args:
            template_type (str): Template type.
            properties (dict): Ability properties.
            modifiers (dict): Ability modifiers.
            element (str): Element type.
            
        Returns:
            str: Generated description.
        """
        # Base description based on template type
        descriptions = {
            "direct_damage": f"Deals {properties.get('damage', 0)} damage to the target.",
            "projectile": f"Fires a projectile dealing {properties.get('damage', 0)} damage.",
            "area_of_effect": f"Creates an explosion dealing {properties.get('damage', 0)} damage in a {properties.get('radius', 0)} meter radius.",
            "buff": f"Boosts stats by {properties.get('stat_boost', 0)}% for {properties.get('duration', 0)} seconds.",
            "debuff": f"Reduces enemy stats by {properties.get('stat_reduction', 0)}% for {properties.get('duration', 0)} seconds.",
            "summon": f"Summons {properties.get('minion_count', 1)} minion(s) with {properties.get('minion_health', 0)} health for {properties.get('duration', 0)} seconds."
        }
        
        base_desc = descriptions.get(template_type, f"A {template_type} ability.")
        
        # Add element information
        if element:
            element_desc = f" Imbued with {element} energy."
            base_desc += element_desc
        
        # Add modifier descriptions
        modifier_descs = []
        for modifier, values in modifiers.items():
            modifier_data = self.config.get("ability_modifiers", {}).get(modifier, {})
            desc = modifier_data.get("description", "")
            
            if desc:
                # Add specific values to description if available
                for prop, value in values.items():
                    desc = desc.replace(f"{{{prop}}}", str(value))
                    
                modifier_descs.append(desc)
                
        if modifier_descs:
            base_desc += " " + " ".join(modifier_descs)
            
        return base_desc
    
    def generate_upgrade_properties(self, seed: Any, complexity: int, rarity: str, 
                                   ability_id: Optional[str] = None, 
                                   parent_node: Optional[Any] = None) -> Dict:
        """
        Generate properties for an upgrade node.
        
        Args:
            seed: Generation seed.
            complexity (int): Complexity level (1-10).
            rarity (str): Rarity level.
            ability_id (str): Associated ability ID.
            parent_node: Optional parent node to derive from.
            
        Returns:
            dict: Generated upgrade properties.
        """
        # Set seed for reproducibility
        self.set_seed(seed)
        
        # Scale complexity to a 0-1 range
        scaled_complexity = min(10, max(1, complexity)) / 10.0
        
        # Get rarity multiplier
        rarity_data = self.templates.get("rarity_modifiers", {}).get(rarity, {"stat_multiplier": 1.0})
        rarity_multiplier = rarity_data.get("stat_multiplier", 1.0)
        
        # Generate upgrade type - what stat will this upgrade improve?
        upgrade_types = ["damage", "range", "cooldown", "mana_cost", "duration", "radius"]
        weights = [0.3, 0.2, 0.15, 0.15, 0.1, 0.1]  # Default weights
        
        # Adjust weights based on parent node if available
        if parent_node and hasattr(parent_node, 'modifier'):
            # If parent improves damage, less likely to improve damage again
            # This encourages variety in the upgrade tree
            modifier_type = type(parent_node.modifier).__name__
            if modifier_type == "DamageModifier":
                weights[0] *= 0.5  # Reduce damage weight
                weights[1] *= 1.5  # Increase range weight
            elif modifier_type == "RangeModifier":
                weights[0] *= 1.5  # Increase damage weight
                weights[1] *= 0.5  # Reduce range weight
                
        upgrade_type = self.rand.choices(upgrade_types, weights=weights, k=1)[0]
        
        # Generate upgrade value based on type, complexity and rarity
        base_values = {
            "damage": {"base": 10, "min": 5, "max": 50},
            "range": {"base": 2, "min": 1, "max": 10},
            "cooldown": {"base": -0.1, "min": -0.5, "max": -0.05},
            "mana_cost": {"base": -5, "min": -20, "max": -1},
            "duration": {"base": 1, "min": 0.5, "max": 5},
            "radius": {"base": 1, "min": 0.5, "max": 3}
        }
        
        value_data = base_values.get(upgrade_type, {"base": 10, "min": 1, "max": 50})
        
        # Calculate value using complexity and rarity
        base = value_data["base"]
        value_range = value_data["max"] - value_data["min"]
        # Add randomness while respecting complexity and min/max range
        random_factor = self.rand.random() * 0.4 + 0.8  # 0.8-1.2 random factor
        
        value = base * (1 + scaled_complexity) * rarity_multiplier * random_factor
        value = max(value_data["min"], min(value_data["max"], value))
        
        # Round appropriately
        if upgrade_type in ["damage", "mana_cost"]:
            value = round(value)
        else:
            value = round(value, 2)
            
        # Generate description
        descriptions = {
            "damage": f"Increases damage by {value}",
            "range": f"Increases range by {value} meters",
            "cooldown": f"Reduces cooldown by {abs(value)} seconds",
            "mana_cost": f"Reduces mana cost by {abs(value)}",
            "duration": f"Increases duration by {value} seconds",
            "radius": f"Increases area of effect by {value} meters"
        }
        
        description = descriptions.get(upgrade_type, f"Improves {upgrade_type} by {value}")
        
        # Add flavor based on rarity
        if rarity == "rare":
            description += " significantly"
        elif rarity == "epic":
            description += " dramatically"
        elif rarity == "legendary":
            description += " enormously"
            
        description += "."
        
        # Create modifier data
        if upgrade_type == "damage":
            modifier_data = {"damage_increase": value}
        elif upgrade_type == "range":
            modifier_data = {"range_increase": value}
        elif upgrade_type == "cooldown":
            modifier_data = {"cooldown_reduction": abs(value)}
        elif upgrade_type == "mana_cost":
            modifier_data = {"cost_reduction": abs(value)}
        elif upgrade_type == "duration":
            modifier_data = {"duration_increase": value}
        elif upgrade_type == "radius":
            modifier_data = {"radius_increase": value}
        else:
            modifier_data = {f"{upgrade_type}_modifier": value}
            
        return {
            "description": description,
            "modifier_data": modifier_data,
            "upgrade_type": upgrade_type,
            "value": value
        }
    
    def create_modifier_from_properties(self, properties: Dict) -> AbilityModifier:
        """
        Create a modifier instance from generated properties.
        
        Args:
            properties (dict): Generated upgrade properties.
            
        Returns:
            AbilityModifier: Modifier instance.
        """
        upgrade_type = properties.get("upgrade_type", "")
        modifier_data = properties.get("modifier_data", {})
        
        if upgrade_type == "damage":
            if "damage_increase" in modifier_data:
                return DamageModifier(flat_damage_increase=modifier_data["damage_increase"])
            elif "damage_increase_percentage" in modifier_data:
                return DamageModifier(damage_increase_percentage=modifier_data["damage_increase_percentage"])
                
        elif upgrade_type == "range":
            if "range_increase" in modifier_data:
                return RangeModifier(flat_range_increase=modifier_data["range_increase"])
            elif "range_increase_percentage" in modifier_data:
                return RangeModifier(range_increase_percentage=modifier_data["range_increase_percentage"])
                
        # For other types, create a custom modifier class if needed
        # For now, return a basic damage modifier as fallback
        return DamageModifier(flat_damage_increase=1)
        
    def generate_ability_components(self, ability_type: str, element: Optional[str] = None, 
                                   rarity: str = "common", complexity: int = 1) -> Dict:
        """
        Generate visual and sound components for an ability.
        
        Args:
            ability_type (str): Type of ability.
            element (str): Optional element type.
            rarity (str): Rarity level.
            complexity (int): Complexity level.
            
        Returns:
            dict: Generated component data.
        """
        # Placeholder for more advanced component generation
        components = {
            "visual": self._generate_visual_components(ability_type, element, rarity, complexity),
            "audio": self._generate_audio_components(ability_type, element, rarity),
            "particles": self._generate_particle_effects(ability_type, element, rarity, complexity)
        }
        
        return components
    
    def _generate_visual_components(self, ability_type: str, element: Optional[str], 
                                  rarity: str, complexity: int) -> Dict:
        """Generate visual components for the ability."""
        # Base color
        base_color = [255, 255, 255]  # Default white
        
        # Element-based color
        if element:
            element_data = self.templates.get("elements", {}).get(element, {})
            if "visual_color" in element_data:
                base_color = element_data["visual_color"]
                
        # Adjust color based on rarity
        rarity_adjustments = {
            "common": 1.0,
            "uncommon": 1.1,
            "rare": 1.2,
            "epic": 1.3,
            "legendary": 1.5
        }
        
        # Brighten color based on rarity (clamped to 255)
        adjustment = rarity_adjustments.get(rarity, 1.0)
        color = [min(255, int(c * adjustment)) for c in base_color]
        
        # Scale based on complexity
        scale = 1.0 + (complexity * 0.05)  # 1.0 to 1.5x scale
        
        return {
            "color": color,
            "scale": scale,
            "glow_intensity": adjustment,
            "animation_speed": 1.0 + (adjustment - 1.0) * 0.5  # Faster for higher rarities
        }
    
    def _generate_audio_components(self, ability_type: str, element: Optional[str], 
                                 rarity: str) -> Dict:
        """Generate audio components for the ability."""
        # Just placeholders for now
        volumes = {
            "common": 0.7,
            "uncommon": 0.8,
            "rare": 0.9,
            "epic": 1.0,
            "legendary": 1.1
        }
        
        pitch_shifts = {
            "common": 1.0,
            "uncommon": 1.05,
            "rare": 1.1,
            "epic": 1.15,
            "legendary": 1.2
        }
        
        return {
            "volume": volumes.get(rarity, 0.7),
            "pitch_shift": pitch_shifts.get(rarity, 1.0)
        }
    
    def _generate_particle_effects(self, ability_type: str, element: Optional[str], 
                                 rarity: str, complexity: int) -> Dict:
        """Generate particle effect settings for the ability."""
        # Particle count increases with rarity and complexity
        base_count = {
            "direct_damage": 10,
            "projectile": 20,
            "area_of_effect": 50,
            "buff": 30,
            "debuff": 25,
            "summon": 40
        }.get(ability_type, 20)
        
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.5,
            "rare": 2.0,
            "epic": 3.0,
            "legendary": 5.0
        }
        
        count = int(base_count * rarity_multipliers.get(rarity, 1.0) * (1 + complexity * 0.1))
        
        # Element color for particles
        color = [255, 255, 255]  # Default white
        if element:
            element_data = self.templates.get("elements", {}).get(element, {})
            if "visual_color" in element_data:
                color = element_data["visual_color"]
                
        return {
            "count": count,
            "color": color,
            "size": 0.1 * rarity_multipliers.get(rarity, 1.0),
            "lifetime": 1.0 + (complexity * 0.2),
            "velocity": 1.0 + (complexity * 0.1)
        } 