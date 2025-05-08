#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Harmonization Manager for Nightfall Defenders
Manages the harmonization of abilities which enhances their effects
"""

from .ability_system import ElementType, AbilityType

class HarmonizationEffect:
    """Represents a harmonization effect for an ability"""
    
    def __init__(self, ability_type, element_type, effect_data, name, description):
        """
        Initialize a harmonization effect
        
        Args:
            ability_type (AbilityType): Type of ability this effect applies to
            element_type (ElementType): Element type this effect applies to
            effect_data (dict): Effect modifiers and properties
            name (str): Name of the harmonized ability
            description (str): Description of the harmonized ability
        """
        self.ability_type = ability_type
        self.element_type = element_type
        self.effect_data = effect_data
        self.name = name
        self.description = description
    
    def matches(self, ability):
        """
        Check if this effect can be applied to the ability
        
        Args:
            ability: The ability to check
            
        Returns:
            bool: True if the effect can be applied
        """
        # Check if ability type matches
        if self.ability_type and ability.ability_type != self.ability_type:
            return False
            
        # Check if element type matches
        if self.element_type and ability.element_type != self.element_type:
            return False
            
        # Check if ability can be harmonized (not already harmonized)
        if hasattr(ability, 'is_harmonized') and ability.is_harmonized:
            return False
            
        return True


class HarmonizationManager:
    """Manages harmonization effects for abilities"""
    
    def __init__(self):
        """Initialize the harmonization manager"""
        self.effects = []
        self._initialize_default_effects()
    
    def add_effect(self, effect):
        """
        Add a harmonization effect
        
        Args:
            effect (HarmonizationEffect): The effect to add
            
        Returns:
            bool: True if added successfully
        """
        self.effects.append(effect)
        return True
    
    def find_effect(self, ability):
        """
        Find a harmonization effect for an ability
        
        Args:
            ability: The ability to harmonize
            
        Returns:
            HarmonizationEffect or None: The matching effect, or None if no match found
        """
        for effect in self.effects:
            if effect.matches(ability):
                return effect
        return None
    
    def _initialize_default_effects(self):
        """Initialize default harmonization effects based on PRD examples"""
        # Meteor harmonization - Multiple smaller meteors
        self.add_effect(HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.FIRE,
            {
                'projectile_count': 5,
                'damage_multiplier': 0.7,
                'spread_angle': 30,
                'cooldown_multiplier': 1.2
            },
            "Meteor Shower",
            "Creates multiple smaller meteors that rain down on an area"
        ))
        
        # Laser harmonization - Sustained beam with increasing damage
        self.add_effect(HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.FIRE,
            {
                'duration': 3.0,
                'damage_ramp': 0.2,  # 20% more damage per second
                'range_multiplier': 1.5,
                'cooldown_multiplier': 1.3
            },
            "Sustained Beam",
            "A powerful continuous beam that deals increasing damage the longer it hits"
        ))
        
        # Fire Nova harmonization - Pulsing waves of fire
        self.add_effect(HarmonizationEffect(
            AbilityType.AREA,
            ElementType.FIRE,
            {
                'pulse_count': 3,
                'pulse_interval': 0.5,
                'radius_growth': 1.5,  # Each pulse is 50% larger
                'cooldown_multiplier': 1.4
            },
            "Pulsing Nova",
            "Multiple waves of fire that expand outward in sequence"
        ))
        
        # Ice shard harmonization - Crystalline fragments
        self.add_effect(HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.ICE,
            {
                'shard_count': 7,
                'shatter_on_impact': True,
                'slow_effect': 0.3,  # 30% slow
                'cooldown_multiplier': 1.2
            },
            "Crystalline Shards",
            "Ice shards that shatter on impact, creating smaller fragments"
        ))
        
        # Lightning harmonization - Chain lightning
        self.add_effect(HarmonizationEffect(
            AbilityType.PROJECTILE,
            ElementType.LIGHTNING,
            {
                'chain_count': 4,
                'chain_range': 5.0,
                'damage_falloff': 0.8,  # 20% less damage per chain
                'cooldown_multiplier': 1.3
            },
            "Chain Lightning",
            "Lightning that jumps from one target to nearby enemies"
        ))
        
        # Earth harmonization - Upheaval
        self.add_effect(HarmonizationEffect(
            AbilityType.AREA,
            ElementType.EARTH,
            {
                'stun_duration': 1.0,
                'damage_multiplier': 1.2,
                'knockback': 3.0,
                'cooldown_multiplier': 1.3
            },
            "Tectonic Upheaval",
            "A violent earth eruption that knocks enemies up and stuns them"
        ))
        
        # Water harmonization - Tidal wave
        self.add_effect(HarmonizationEffect(
            AbilityType.AREA,
            ElementType.WATER,
            {
                'wave_speed': 8.0,
                'wave_width': 10.0,
                'push_force': 10.0,
                'cooldown_multiplier': 1.3
            },
            "Tidal Wave",
            "A massive wave that pushes enemies away and deals damage"
        ))
        
        # Wind harmonization - Tornado
        self.add_effect(HarmonizationEffect(
            AbilityType.AREA,
            ElementType.WIND,
            {
                'duration': 4.0,
                'radius': 3.0,
                'pull_force': 5.0,
                'cooldown_multiplier': 1.4
            },
            "Vortex",
            "A swirling tornado that pulls enemies in and damages them"
        ))
        
        # Arcane harmonization - Reality distortion
        self.add_effect(HarmonizationEffect(
            AbilityType.AREA,
            ElementType.ARCANE,
            {
                'slow_time': True,
                'slow_factor': 0.5,
                'damage_multiplier': 1.3,
                'cooldown_multiplier': 1.5
            },
            "Reality Distortion",
            "Warps reality in an area, slowing enemies and increasing damage"
        ))
        
        # Holy harmonization - Divine intervention
        self.add_effect(HarmonizationEffect(
            AbilityType.BUFF,
            ElementType.HOLY,
            {
                'duration': 5.0,
                'heal_amount': 10,
                'damage_reduction': 0.3,
                'cooldown_multiplier': 1.4
            },
            "Divine Shield",
            "A powerful shield that heals allies and reduces damage taken"
        ))
        
        # Melee harmonization - Sweeping strikes
        self.add_effect(HarmonizationEffect(
            AbilityType.MELEE,
            None,  # Any element type
            {
                'sweep_count': 3,
                'sweep_interval': 0.2,
                'angle_multiplier': 1.2,
                'cooldown_multiplier': 1.3
            },
            "Sweeping Strikes",
            "Multiple rapid strikes that hit in a wide arc"
        ))
        
        # Movement harmonization - Afterimage
        self.add_effect(HarmonizationEffect(
            AbilityType.MOVEMENT,
            None,  # Any element type
            {
                'creates_afterimage': True,
                'afterimage_damage': 5,
                'afterimage_duration': 1.0,
                'cooldown_multiplier': 1.2
            },
            "Phantom Rush",
            "Leaves behind a damaging afterimage when moving"
        )) 