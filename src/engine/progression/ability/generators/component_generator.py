# src/engine/progression/ability/generators/component_generator.py

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class AbilityComponentGenerator:
    """
    Generates visual and audio components for abilities.
    """
    def __init__(self, config_path: Path):
        """
        Initialize the component generator with configuration.
        
        Args:
            config_path (Path): Path to the component configuration JSON file.
        """
        self.config = self._load_json(config_path)
        self.name_prefixes = self.config.get("name_prefixes", {})
        self.name_suffixes = self.config.get("name_suffixes", {})
        
        # Set up seed-based random generator
        self.rand = random.Random()
    
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
    
    def generate_visual_effect(self, ability_type: str, element: Optional[str] = None, 
                              rarity: str = "common") -> Dict:
        """
        Generate visual effect parameters for an ability.
        
        Args:
            ability_type (str): Type of ability.
            element (str): Optional element type.
            rarity (str): Rarity level.
            
        Returns:
            dict: Visual effect parameters.
        """
        # Get element color
        element_color = self._get_element_color(element)
        
        # Apply rarity adjustments
        rarity_data = self.config.get("rarity_modifiers", {}).get(rarity, {})
        intensity_modifier = rarity_data.get("visual_intensity", 1.0)
        
        # Base effect types by ability type
        effect_types = {
            "direct_damage": ["slash", "impact", "burst"],
            "projectile": ["projectile", "beam", "orb"],
            "area_of_effect": ["explosion", "wave", "vortex"],
            "buff": ["aura", "glow", "runes"],
            "debuff": ["cloud", "chains", "curse"],
            "summon": ["portal", "circle", "symbols"]
        }
        
        # Select a base effect type
        available_effects = effect_types.get(ability_type, ["generic"])
        base_effect = self.rand.choice(available_effects)
        
        # Generate parameters
        effect = {
            "type": base_effect,
            "color": element_color,
            "scale": 1.0 * intensity_modifier,
            "duration": 0.5 * intensity_modifier,
            "intensity": 1.0 * intensity_modifier,
            "particle_count": int(20 * intensity_modifier)
        }
        
        # Add element-specific modifications
        if element:
            element_data = self.config.get("elements", {}).get(element, {})
            effect_mods = element_data.get("visual_effects", {})
            
            for key, value in effect_mods.items():
                if key in effect:
                    # Multiply existing value if numeric
                    if isinstance(effect[key], (int, float)) and isinstance(value, (int, float)):
                        effect[key] *= value
                    else:
                        effect[key] = value
                else:
                    # Add new property
                    effect[key] = value
                    
        return effect
        
    def _get_element_color(self, element: Optional[str]) -> List[int]:
        """
        Get the color for an element.
        
        Args:
            element (str): Element type.
            
        Returns:
            list: RGB color values.
        """
        if not element:
            return [255, 255, 255]  # Default white
            
        element_data = self.config.get("elements", {}).get(element, {})
        return element_data.get("visual_color", [255, 255, 255])
        
    def generate_sound_effect(self, ability_type: str, element: Optional[str] = None, 
                            rarity: str = "common") -> Dict:
        """
        Generate sound effect parameters for an ability.
        
        Args:
            ability_type (str): Type of ability.
            element (str): Optional element type.
            rarity (str): Rarity level.
            
        Returns:
            dict: Sound effect parameters.
        """
        # Base sound types by ability type
        sound_types = {
            "direct_damage": ["slash", "impact", "hit"],
            "projectile": ["launch", "whoosh", "shoot"],
            "area_of_effect": ["explosion", "blast", "boom"],
            "buff": ["enchant", "power", "boost"],
            "debuff": ["curse", "weaken", "drain"],
            "summon": ["summon", "conjure", "call"]
        }
        
        # Select a base sound type
        available_sounds = sound_types.get(ability_type, ["generic"])
        base_sound = self.rand.choice(available_sounds)
        
        # Apply rarity adjustments
        rarity_data = self.config.get("rarity_modifiers", {}).get(rarity, {})
        volume_modifier = rarity_data.get("sound_volume", 1.0)
        pitch_modifier = rarity_data.get("sound_pitch", 1.0)
        
        # Generate parameters
        sound = {
            "type": base_sound,
            "volume": 0.8 * volume_modifier,
            "pitch": 1.0 * pitch_modifier,
            "spatial": True,
            "distance": 20.0
        }
        
        # Add element-specific modifications
        if element:
            element_data = self.config.get("elements", {}).get(element, {})
            sound_mods = element_data.get("sound_effects", {})
            
            for key, value in sound_mods.items():
                if key in sound:
                    # Multiply existing value if numeric
                    if isinstance(sound[key], (int, float)) and isinstance(value, (int, float)):
                        sound[key] *= value
                    else:
                        sound[key] = value
                else:
                    # Add new property
                    sound[key] = value
                    
        return sound
        
    def generate_name(self, ability_type: str, element: Optional[str] = None, 
                     rarity: str = "common") -> str:
        """
        Generate a name for an ability.
        
        Args:
            ability_type (str): Type of ability.
            element (str): Optional element type.
            rarity (str): Rarity level.
            
        Returns:
            str: Generated name.
        """
        prefixes = []
        
        # Add element prefixes
        if element and element in self.name_prefixes:
            prefixes.extend(self.name_prefixes[element])
            
        # Add rarity prefixes
        if rarity in self.name_prefixes:
            prefixes.extend(self.name_prefixes[rarity])
            
        # Fallback
        if not prefixes:
            prefixes = ["Mysterious"]
            
        # Get suffixes for ability type
        suffixes = self.name_suffixes.get(ability_type, ["Ability"])
        
        # Select random prefix and suffix
        prefix = self.rand.choice(prefixes)
        suffix = self.rand.choice(suffixes)
        
        return f"{prefix} {suffix}"
        
    def generate_description(self, ability_params: Dict) -> str:
        """
        Generate a description for an ability.
        
        Args:
            ability_params (dict): Ability parameters.
            
        Returns:
            str: Generated description.
        """
        ability_type = ability_params.get("type", "generic")
        properties = ability_params.get("properties", {})
        modifiers = ability_params.get("modifiers", {})
        element = ability_params.get("element")
        
        # Base descriptions by ability type
        descriptions = {
            "direct_damage": f"Deals {properties.get('damage', 0)} damage to the target.",
            "projectile": f"Fires a projectile dealing {properties.get('damage', 0)} damage.",
            "area_of_effect": f"Creates an explosion dealing {properties.get('damage', 0)} damage in a {properties.get('radius', 0)} meter radius.",
            "buff": f"Boosts stats by {properties.get('stat_boost', 0)}% for {properties.get('duration', 0)} seconds.",
            "debuff": f"Reduces enemy stats by {properties.get('stat_reduction', 0)}% for {properties.get('duration', 0)} seconds.",
            "summon": f"Summons {properties.get('minion_count', 1)} minion(s) with {properties.get('minion_health', 0)} health for {properties.get('duration', 0)} seconds."
        }
        
        base_desc = descriptions.get(ability_type, f"A {ability_type} ability.")
        
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
                # Replace placeholders with values
                for prop, value in values.items():
                    desc = desc.replace(f"{{{prop}}}", str(value))
                    
                modifier_descs.append(desc)
                
        if modifier_descs:
            base_desc += " " + " ".join(modifier_descs)
            
        return base_desc
        
    def generate_icon_params(self, ability_type: str, element: Optional[str] = None, 
                           rarity: str = "common") -> Dict:
        """
        Generate parameters for ability icon rendering.
        
        Args:
            ability_type (str): Type of ability.
            element (str): Optional element type.
            rarity (str): Rarity level.
            
        Returns:
            dict: Icon parameters.
        """
        # Base icon types by ability type
        icon_types = {
            "direct_damage": ["sword", "hammer", "axe"],
            "projectile": ["arrow", "orb", "dart"],
            "area_of_effect": ["explosion", "fireball", "nova"],
            "buff": ["shield", "wing", "star"],
            "debuff": ["skull", "poison", "web"],
            "summon": ["pentagram", "creature", "hand"]
        }
        
        # Select a base icon type
        available_icons = icon_types.get(ability_type, ["generic"])
        base_icon = self.rand.choice(available_icons)
        
        # Get element color
        element_color = self._get_element_color(element)
        
        # Get rarity border color
        rarity_colors = {
            "common": [150, 150, 150],
            "uncommon": [0, 180, 0],
            "rare": [0, 70, 200],
            "epic": [180, 0, 180],
            "legendary": [255, 165, 0]
        }
        border_color = rarity_colors.get(rarity, [150, 150, 150])
        
        # Generate parameters
        icon = {
            "base_type": base_icon,
            "main_color": element_color,
            "border_color": border_color,
            "has_glow": rarity in ["epic", "legendary"],
            "has_particles": rarity in ["rare", "epic", "legendary"],
            "border_thickness": 1 if rarity == "common" else 2
        }
        
        return icon 