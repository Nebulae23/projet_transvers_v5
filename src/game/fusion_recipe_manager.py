#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fusion Recipe Manager for Nightfall Defenders
Manages recipes for ability fusion combinations
"""

from .ability_system import ElementType, AbilityType

class FusionRecipe:
    """Represents a recipe for fusing two abilities"""
    
    def __init__(self, input1, input2, output, name, description):
        """
        Initialize a fusion recipe
        
        Args:
            input1 (dict): First input criteria (element_type, ability_type, or ability_id)
            input2 (dict): Second input criteria (element_type, ability_type, or ability_id)
            output (dict): Output ability properties
            name (str): Name of the fused ability
            description (str): Description of the fused ability
        """
        self.input1 = input1
        self.input2 = input2
        self.output = output
        self.name = name
        self.description = description
    
    def matches(self, ability1, ability2):
        """
        Check if two abilities match this recipe
        
        Args:
            ability1: First ability to check
            ability2: Second ability to check
            
        Returns:
            bool: True if the abilities match this recipe
        """
        # Try matching in both orders
        return (self._match_ability(ability1, self.input1) and self._match_ability(ability2, self.input2)) or \
               (self._match_ability(ability1, self.input2) and self._match_ability(ability2, self.input1))
    
    def _match_ability(self, ability, criteria):
        """
        Check if an ability matches the given criteria
        
        Args:
            ability: The ability to check
            criteria: Criteria to match against
            
        Returns:
            bool: True if the ability matches the criteria
        """
        for key, value in criteria.items():
            if key == 'element_type':
                if ability.element_type != value:
                    return False
            elif key == 'ability_type':
                if ability.ability_type != value:
                    return False
            elif key == 'ability_id':
                if not hasattr(ability, 'ability_id') or ability.ability_id != value:
                    return False
        return True


class FusionRecipeManager:
    """Manages fusion recipes for the ability system"""
    
    def __init__(self):
        """Initialize the fusion recipe manager"""
        self.recipes = []
        self._initialize_default_recipes()
    
    def add_recipe(self, recipe):
        """
        Add a fusion recipe
        
        Args:
            recipe (FusionRecipe): The recipe to add
            
        Returns:
            bool: True if added successfully
        """
        self.recipes.append(recipe)
        return True
    
    def find_recipe(self, ability1, ability2):
        """
        Find a recipe that matches the given abilities
        
        Args:
            ability1: First ability
            ability2: Second ability
            
        Returns:
            FusionRecipe or None: The matching recipe, or None if no match found
        """
        for recipe in self.recipes:
            if recipe.matches(ability1, ability2):
                return recipe
        return None
    
    def _initialize_default_recipes(self):
        """Initialize default fusion recipes"""
        # Fire + Ice = Steam (obscures vision, damage over time)
        self.add_recipe(FusionRecipe(
            {'element_type': ElementType.FIRE},
            {'element_type': ElementType.ICE},
            {
                'element_type': ElementType.WATER,
                'ability_type': AbilityType.AREA,
                'effects': ['obscure_vision', 'damage_over_time']
            },
            "Steam Cloud",
            "A cloud of steam that obscures vision and deals damage over time"
        ))
        
        # Lightning + Movement = Teleport
        self.add_recipe(FusionRecipe(
            {'element_type': ElementType.LIGHTNING},
            {'ability_type': AbilityType.MOVEMENT},
            {
                'element_type': ElementType.LIGHTNING,
                'ability_type': AbilityType.MOVEMENT,
                'effects': ['teleport']
            },
            "Lightning Teleport",
            "Instantly teleport to a target location in a flash of lightning"
        ))
        
        # Shield + Projectile = Reflective Barrier
        self.add_recipe(FusionRecipe(
            {'ability_type': AbilityType.BUFF, 'effects': ['shield']},
            {'ability_type': AbilityType.PROJECTILE},
            {
                'ability_type': AbilityType.BUFF,
                'effects': ['reflect_projectiles', 'shield']
            },
            "Reflective Barrier",
            "A barrier that reflects projectiles back at enemies"
        ))
        
        # Fire + Wind = Firestorm (area damage + push)
        self.add_recipe(FusionRecipe(
            {'element_type': ElementType.FIRE},
            {'element_type': ElementType.WIND},
            {
                'element_type': ElementType.FIRE,
                'ability_type': AbilityType.AREA,
                'effects': ['area_damage', 'push']
            },
            "Firestorm",
            "A raging storm of fire that damages enemies and pushes them away"
        ))
        
        # Earth + Water = Mud Slick (slow + trap)
        self.add_recipe(FusionRecipe(
            {'element_type': ElementType.EARTH},
            {'element_type': ElementType.WATER},
            {
                'element_type': ElementType.EARTH,
                'ability_type': AbilityType.AREA,
                'effects': ['slow', 'trap']
            },
            "Mud Slick",
            "Creates a muddy area that slows enemies and can trap them"
        ))
        
        # Lightning + Water = Electrified Water (area damage + stun)
        self.add_recipe(FusionRecipe(
            {'element_type': ElementType.LIGHTNING},
            {'element_type': ElementType.WATER},
            {
                'element_type': ElementType.LIGHTNING,
                'ability_type': AbilityType.AREA,
                'effects': ['area_damage', 'stun']
            },
            "Electrified Water",
            "Water charged with electricity that shocks and stuns enemies"
        ))
        
        # Arcane + Any Element = Enhanced Element (increased damage/effect)
        for element in [ElementType.FIRE, ElementType.ICE, ElementType.LIGHTNING, 
                     ElementType.EARTH, ElementType.WATER, ElementType.WIND]:
            self.add_recipe(FusionRecipe(
                {'element_type': ElementType.ARCANE},
                {'element_type': element},
                {
                    'element_type': element,
                    'effects': ['enhanced_damage', 'enhanced_effect']
                },
                f"Enhanced {element.value.capitalize()}",
                f"An arcane-enhanced {element.value} ability with increased damage and effects"
            )) 