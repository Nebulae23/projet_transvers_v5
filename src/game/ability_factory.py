#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ability Factory for Nightfall Defenders
Creates specialized and fused abilities
"""

import uuid
import math
from panda3d.core import Vec3

from .ability_system import (
    AbilityType, Ability, ElementType, ProjectileAbility, MeleeAbility, 
    SpecializationPath, AreaAbility
)

class AbilityFactory:
    """Factory for creating abilities and fusions"""
    
    @staticmethod
    def create_ability(ability_type, **kwargs):
        """
        Create an ability of the specified type
        
        Args:
            ability_type (str): Type of ability to create
            **kwargs: Keyword arguments for the ability
            
        Returns:
            Ability: The created ability
        """
        ability_id = kwargs.get('ability_id', str(uuid.uuid4()))
        
        if ability_type == "projectile":
            return AbilityFactory.create_projectile_ability(ability_id, **kwargs)
        elif ability_type == "melee":
            return AbilityFactory.create_melee_ability(ability_id, **kwargs)
        elif ability_type == "area":
            return AbilityFactory.create_area_ability(ability_id, **kwargs)
        else:
            # Default to basic ability
            return Ability(
                ability_id,
                kwargs.get('name', 'Unknown Ability'),
                kwargs.get('description', 'No description'),
                AbilityType.UTILITY,
                kwargs.get('cooldown', 1.0),
                kwargs.get('resource_cost', 0),
                kwargs.get('icon', None)
            )
    
    @staticmethod
    def create_harmonized_ability(ability, effect=None):
        """
        Create a harmonized version of an ability
        
        Args:
            ability (Ability): The ability to harmonize
            effect (dict, optional): Specific harmonization effect to apply
                                     If None, a default effect will be used
                                     based on the ability type and element
            
        Returns:
            Ability: The harmonized ability, or None if harmonization not possible
        """
        # Check if ability can be harmonized
        if ability.is_harmonized or ability.is_fused:
            return None
            
        # If no specific effect provided, try to find a matching one
        if effect is None:
            from game.harmonization_manager import HarmonizationManager
            manager = HarmonizationManager()
            harmonization_effect = manager.find_effect(ability)
            
            if harmonization_effect:
                effect = harmonization_effect.effect_data
                effect['name'] = harmonization_effect.name
                effect['description'] = harmonization_effect.description
        
        # Create a copy of the ability
        if isinstance(ability, ProjectileAbility):
            harmonized = ProjectileAbility(
                f"harmonized_{ability.ability_id}",
                ability.name,
                ability.description,
                ability.projectile_type,
                ability.damage,
                ability.speed,
                ability.cooldown,
                ability.resource_cost,
                ability.icon
            )
            
            # Copy additional projectile properties
            harmonized.pierce = ability.pierce
            harmonized.chain = ability.chain
            harmonized.aoe_radius = ability.aoe_radius
            
        elif isinstance(ability, MeleeAbility):
            harmonized = MeleeAbility(
                f"harmonized_{ability.ability_id}",
                ability.name,
                ability.description,
                ability.damage,
                ability.range,
                ability.angle,
                ability.cooldown,
                ability.resource_cost,
                ability.icon
            )
            
        elif isinstance(ability, AreaAbility):
            harmonized = AreaAbility(
                f"harmonized_{ability.ability_id}",
                ability.name,
                ability.description,
                ability.effect_type,
                ability.value,
                ability.radius,
                ability.duration,
                ability.cooldown,
                ability.resource_cost,
                ability.icon
            )
            
        else:
            # Generic ability
            harmonized = Ability(
                ability.name,
                ability.description,
                ability.damage,
                ability.cooldown,
                ability.range,
                ability.ability_type,
                ability.trajectory,
                ability.effects.copy(),
                ability.element_type
            )
            harmonized.ability_id = f"harmonized_{ability.ability_id}"
            
        # Apply the harmonization effect
        harmonized.harmonize(effect)
        
        # Apply special harmonization modifications based on ability type and element
        AbilityFactory._apply_harmonization_special_effects(harmonized, effect)
        
        return harmonized
        
    @staticmethod
    def _apply_harmonization_special_effects(ability, effect):
        """
        Apply special harmonization effects based on ability type and element
        
        Args:
            ability (Ability): The harmonized ability
            effect (dict): The harmonization effect data
        """
        if not effect:
            return
            
        # Apply special visual effects
        if ability.element_type == ElementType.FIRE:
            ability.visual_effect = "harmonized_fire"
        elif ability.element_type == ElementType.ICE:
            ability.visual_effect = "harmonized_ice"
        elif ability.element_type == ElementType.LIGHTNING:
            ability.visual_effect = "harmonized_lightning"
            
        # Apply special sound effects
        ability.sound_effect = f"harmonized_{ability.element_type.value}"
        
        # Apply ability-type specific modifications
        if ability.ability_type == AbilityType.PROJECTILE:
            if 'projectile_count' in effect:
                # Multi-projectile effect - store for use in _create_projectile
                ability.harmonized_projectile_count = effect['projectile_count']
                if 'spread_angle' in effect:
                    ability.harmonized_spread_angle = effect['spread_angle']
                else:
                    ability.harmonized_spread_angle = 30  # Default spread
                    
            if 'duration' in effect and 'damage_ramp' in effect:
                # Sustained damage effect - store for use in damage calculation
                ability.harmonized_duration = effect['duration']
                ability.harmonized_damage_ramp = effect['damage_ramp']
                
        elif ability.ability_type == AbilityType.AREA:
            if 'pulse_count' in effect and 'pulse_interval' in effect:
                # Pulsing effect - store for use in area effect creation
                ability.harmonized_pulse_count = effect['pulse_count']
                ability.harmonized_pulse_interval = effect['pulse_interval']
                if 'radius_growth' in effect:
                    ability.harmonized_radius_growth = effect['radius_growth']
    
    @staticmethod
    def create_projectile_ability(ability_id, **kwargs):
        """Create a projectile ability"""
        return ProjectileAbility(
            ability_id,
            kwargs.get('name', 'Unknown Projectile'),
            kwargs.get('description', 'No description'),
            kwargs.get('projectile_type', 'straight'),
            kwargs.get('damage', 10),
            kwargs.get('speed', 10.0),
            kwargs.get('cooldown', 1.0),
            kwargs.get('resource_cost', 0),
            kwargs.get('icon', None)
        )
    
    @staticmethod
    def create_melee_ability(ability_id, **kwargs):
        """Create a melee ability"""
        return MeleeAbility(
            ability_id,
            kwargs.get('name', 'Unknown Melee'),
            kwargs.get('description', 'No description'),
            kwargs.get('damage', 20),
            kwargs.get('range', 2.0),
            kwargs.get('angle', 90.0),
            kwargs.get('cooldown', 0.5),
            kwargs.get('resource_cost', 0),
            kwargs.get('icon', None)
        )
    
    @staticmethod
    def create_area_ability(ability_id, **kwargs):
        """Create an area ability"""
        return AreaAbility(
            ability_id,
            kwargs.get('name', 'Unknown Area'),
            kwargs.get('description', 'No description'),
            kwargs.get('effect_type', 'damage'),
            kwargs.get('value', 10),
            kwargs.get('radius', 5.0),
            kwargs.get('duration', 0.0),
            kwargs.get('cooldown', 5.0),
            kwargs.get('resource_cost', 20),
            kwargs.get('icon', None)
        )
    
    @staticmethod
    def create_fusion(ability1, ability2):
        """
        Create a fusion of two abilities
        
        Args:
            ability1 (Ability): First ability
            ability2 (Ability): Second ability
            
        Returns:
            Ability or None: The fused ability, or None if fusion not possible
        """
        # Check if abilities can be fused
        if not ability1.can_fuse_with(ability2):
            return None
        
        # Create unique ID for fusion
        fusion_id = f"fusion_{ability1.ability_id}_{ability2.ability_id}"
        
        # Check for a matching fusion recipe
        from game.fusion_recipe_manager import FusionRecipeManager
        recipe_manager = FusionRecipeManager()
        recipe = recipe_manager.find_recipe(ability1, ability2)
        
        if recipe:
            # Create ability based on the recipe
            output_props = recipe.output
            
            # Determine the base ability type for the fusion
            ability_type = output_props.get('ability_type', ability1.ability_type)
            
            # Create the appropriate ability type
            if ability_type == AbilityType.PROJECTILE:
                fusion = AbilityFactory._create_recipe_projectile_fusion(fusion_id, ability1, ability2, recipe)
            elif ability_type == AbilityType.MELEE:
                fusion = AbilityFactory._create_recipe_melee_fusion(fusion_id, ability1, ability2, recipe)
            elif ability_type == AbilityType.AREA:
                fusion = AbilityFactory._create_recipe_area_fusion(fusion_id, ability1, ability2, recipe)
            else:
                fusion = AbilityFactory._create_recipe_default_fusion(fusion_id, ability1, ability2, recipe)
            
            return fusion
        
        # If no recipe found, fall back to standard fusion logic
        # Find fusion based on ability types
        if ability1.ability_type == AbilityType.PROJECTILE and ability2.ability_type == AbilityType.PROJECTILE:
            return AbilityFactory._create_projectile_fusion(fusion_id, ability1, ability2)
        
        elif ability1.ability_type == AbilityType.MELEE and ability2.ability_type == AbilityType.PROJECTILE:
            return AbilityFactory._create_melee_projectile_fusion(fusion_id, ability1, ability2)
        
        elif ability1.ability_type == AbilityType.PROJECTILE and ability2.ability_type == AbilityType.MELEE:
            return AbilityFactory._create_melee_projectile_fusion(fusion_id, ability2, ability1)
        
        elif ability1.ability_type == AbilityType.MELEE and ability2.ability_type == AbilityType.MELEE:
            return AbilityFactory._create_melee_fusion(fusion_id, ability1, ability2)
        
        # Default fusion (simple combination of effects)
        return AbilityFactory._create_default_fusion(fusion_id, ability1, ability2)
    
    @staticmethod
    def _create_projectile_fusion(fusion_id, proj1, proj2):
        """Create a fusion of two projectile abilities"""
        # Create a new projectile with combined effects
        fusion = ProjectileAbility(
            fusion_id,
            f"{proj1.name} + {proj2.name}",
            f"A fusion of {proj1.name} and {proj2.name}.",
            "fusion", # Special projectile type for the fusion
            (proj1.damage + proj2.damage) * 0.8, # Slightly less than sum
            (proj1.speed + proj2.speed) / 2, # Average speed
            (proj1.cooldown + proj2.cooldown) * 0.7, # Reduced cooldown
            max(proj1.resource_cost, proj2.resource_cost), # Max cost
            None # Icon will be set separately
        )
        
        # Special properties
        fusion.pierce = max(proj1.pierce, proj2.pierce) + 1
        fusion.aoe_radius = max(proj1.aoe_radius, proj2.aoe_radius) + 1.0
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [proj1.ability_id, proj2.ability_id]
        fusion.fusion_type = "projectile_combo"
        
        return fusion
    
    @staticmethod
    def _create_melee_fusion(fusion_id, melee1, melee2):
        """Create a fusion of two melee abilities"""
        # Create a new melee with combined effects
        fusion = MeleeAbility(
            fusion_id,
            f"{melee1.name} + {melee2.name}",
            f"A fusion of {melee1.name} and {melee2.name}.",
            (melee1.damage + melee2.damage) * 0.8, # Slightly less than sum
            (melee1.range + melee2.range) * 0.6, # Increased range
            min(360, melee1.angle + melee2.angle * 0.5), # Wider angle
            (melee1.cooldown + melee2.cooldown) * 0.7, # Reduced cooldown
            max(melee1.resource_cost, melee2.resource_cost), # Max cost
            None # Icon will be set separately
        )
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [melee1.ability_id, melee2.ability_id]
        fusion.fusion_type = "melee_combo"
        
        return fusion
    
    @staticmethod
    def _create_melee_projectile_fusion(fusion_id, melee, projectile):
        """Create a fusion of melee and projectile abilities"""
        # Create a special melee ability that also fires projectiles
        fusion = MeleeAbility(
            fusion_id,
            f"{melee.name} + {projectile.name}",
            f"A fusion of {melee.name} and {projectile.name} that strikes enemies and fires projectiles.",
            melee.damage * 0.7, # Reduced melee damage
            melee.range,
            melee.angle,
            (melee.cooldown + projectile.cooldown) * 0.6, # Reduced cooldown
            melee.resource_cost + projectile.resource_cost * 0.5, # Increased cost
            None # Icon will be set separately
        )
        
        # Store projectile properties for use in custom implementation
        fusion.projectile_damage = projectile.damage * 0.6
        fusion.projectile_type = projectile.projectile_type
        fusion.projectile_speed = projectile.speed
        
        # Custom use method to handle both melee and projectile
        original_use = fusion.use
        
        def fusion_use(caster, target=None, position=None):
            # Call original melee use
            if not original_use(caster, target, position):
                return False
            
            # Also fire projectiles in a spread
            if hasattr(caster.game, 'entity_manager'):
                forward = caster.direction.normalized()
                
                # Create 3 projectiles in a spread
                for angle_offset in [-20, 0, 20]:
                    # Calculate direction with offset
                    angle_rad = math.radians(angle_offset)
                    dir_x = forward.getX() * math.cos(angle_rad) - forward.getY() * math.sin(angle_rad)
                    dir_y = forward.getX() * math.sin(angle_rad) + forward.getY() * math.cos(angle_rad)
                    
                    direction = Vec3(dir_x, dir_y, 0)
                    
                    # Create projectile
                    caster.game.entity_manager.create_projectile(
                        fusion.projectile_type,
                        caster.position,
                        direction,
                        owner=caster,
                        damage=fusion.projectile_damage,
                        speed=fusion.projectile_speed
                    )
            
            return True
        
        # Replace use method with custom implementation
        fusion.use = fusion_use
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [melee.ability_id, projectile.ability_id]
        fusion.fusion_type = "melee_projectile_combo"
        
        return fusion
    
    @staticmethod
    def _create_default_fusion(fusion_id, ability1, ability2):
        """Create a default fusion for any two abilities"""
        # Use the "stronger" ability as base
        base = ability1 if ability1.cooldown > ability2.cooldown else ability2
        
        # Create a copy with enhanced properties
        fusion = Ability(
            fusion_id,
            f"{ability1.name} + {ability2.name}",
            f"A fusion of {ability1.name} and {ability2.name}.",
            base.ability_type,
            (ability1.cooldown + ability2.cooldown) * 0.7, # Reduced cooldown
            ability1.resource_cost + ability2.resource_cost, # Combined cost
            None # Icon will be set separately
        )
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [ability1.ability_id, ability2.ability_id]
        fusion.fusion_type = "generic_combo"
        
        return fusion
    
    @staticmethod
    def _create_recipe_projectile_fusion(fusion_id, ability1, ability2, recipe):
        """
        Create a projectile fusion based on a recipe
        
        Args:
            fusion_id (str): Unique ID for the fusion ability
            ability1 (Ability): First ability
            ability2 (Ability): Second ability
            recipe (FusionRecipe): The matching recipe
            
        Returns:
            ProjectileAbility: The fused projectile ability
        """
        output = recipe.output
        element_type = output.get('element_type', ElementType.NONE)
        effects = output.get('effects', [])
        
        # Combine the base stats from both abilities
        damage = (ability1.damage + ability2.damage) * 0.8  # Slightly less than sum
        cooldown = (ability1.cooldown + ability2.cooldown) * 0.6  # Reduced cooldown
        resource_cost = max(ability1.resource_cost, ability2.resource_cost) * 1.2  # Increased cost
        
        # Create the fusion ability
        fusion = ProjectileAbility(
            fusion_id,
            recipe.name,
            recipe.description,
            "fusion",  # Special projectile type
            damage,
            15.0,  # Standard speed for fusion projectiles
            cooldown,
            resource_cost,
            None  # Icon will be set separately
        )
        
        # Set the element type
        fusion.element_type = element_type
        
        # Special properties based on effects
        if 'area_damage' in effects:
            fusion.aoe_radius = 3.0
        if 'pierce' in effects:
            fusion.pierce = 3
        if 'enhanced_damage' in effects:
            fusion.damage *= 1.5
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [ability1.ability_id, ability2.ability_id]
        fusion.fusion_type = f"{element_type.value}_projectile_fusion"
        
        return fusion
    
    @staticmethod
    def _create_recipe_melee_fusion(fusion_id, ability1, ability2, recipe):
        """
        Create a melee fusion based on a recipe
        
        Args:
            fusion_id (str): Unique ID for the fusion ability
            ability1 (Ability): First ability
            ability2 (Ability): Second ability
            recipe (FusionRecipe): The matching recipe
            
        Returns:
            MeleeAbility: The fused melee ability
        """
        output = recipe.output
        element_type = output.get('element_type', ElementType.NONE)
        effects = output.get('effects', [])
        
        # Combine the base stats from both abilities
        damage = (ability1.damage + ability2.damage) * 0.8  # Slightly less than sum
        range_val = max(ability1.range, ability2.range) * 1.2  # Increased range
        angle = min(360, max(ability1.angle, ability2.angle) * 1.3)  # Wider angle
        cooldown = (ability1.cooldown + ability2.cooldown) * 0.6  # Reduced cooldown
        resource_cost = max(ability1.resource_cost, ability2.resource_cost) * 1.2  # Increased cost
        
        # Create the fusion ability
        fusion = MeleeAbility(
            fusion_id,
            recipe.name,
            recipe.description,
            damage,
            range_val,
            angle,
            cooldown,
            resource_cost,
            None  # Icon will be set separately
        )
        
        # Set the element type
        fusion.element_type = element_type
        
        # Special properties based on effects
        if 'push' in effects:
            fusion.push_force = 5.0
        if 'stun' in effects:
            fusion.stun_duration = 1.5
        if 'enhanced_damage' in effects:
            fusion.damage *= 1.5
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [ability1.ability_id, ability2.ability_id]
        fusion.fusion_type = f"{element_type.value}_melee_fusion"
        
        return fusion
    
    @staticmethod
    def _create_recipe_area_fusion(fusion_id, ability1, ability2, recipe):
        """
        Create an area fusion based on a recipe
        
        Args:
            fusion_id (str): Unique ID for the fusion ability
            ability1 (Ability): First ability
            ability2 (Ability): Second ability
            recipe (FusionRecipe): The matching recipe
            
        Returns:
            AreaAbility: The fused area ability
        """
        output = recipe.output
        element_type = output.get('element_type', ElementType.NONE)
        effects = output.get('effects', [])
        
        # Determine the primary effect type
        effect_type = "damage"  # Default
        if 'heal' in effects:
            effect_type = "heal"
        elif 'buff' in effects:
            effect_type = "buff"
        elif 'debuff' in effects:
            effect_type = "debuff"
        elif 'summon' in effects:
            effect_type = "summon"
        
        # Combine the base stats from both abilities
        value = max(ability1.damage, ability2.damage) * 1.2  # Increased effect value
        radius = 5.0  # Standard radius for fusion area effects
        duration = 5.0  # Standard duration for fusion area effects
        cooldown = (ability1.cooldown + ability2.cooldown) * 0.7  # Reduced cooldown
        resource_cost = max(ability1.resource_cost, ability2.resource_cost) * 1.5  # Increased cost
        
        # Create the fusion ability
        fusion = AreaAbility(
            fusion_id,
            recipe.name,
            recipe.description,
            effect_type,
            value,
            radius,
            duration,
            cooldown,
            resource_cost,
            None  # Icon will be set separately
        )
        
        # Set the element type
        fusion.element_type = element_type
        
        # Apply special properties based on effects
        if 'damage_over_time' in effects:
            fusion.damage_over_time = value / 5  # Damage per second
            fusion.dot_duration = duration
        if 'slow' in effects:
            fusion.slow_factor = 0.5  # 50% slow
        if 'stun' in effects:
            fusion.stun_duration = 1.0  # 1 second stun
        if 'obscure_vision' in effects:
            fusion.vision_reduction = 0.7  # 70% vision reduction
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [ability1.ability_id, ability2.ability_id]
        fusion.fusion_type = f"{element_type.value}_area_fusion"
        
        return fusion
    
    @staticmethod
    def _create_recipe_default_fusion(fusion_id, ability1, ability2, recipe):
        """
        Create a default fusion based on a recipe
        
        Args:
            fusion_id (str): Unique ID for the fusion ability
            ability1 (Ability): First ability
            ability2 (Ability): Second ability
            recipe (FusionRecipe): The matching recipe
            
        Returns:
            Ability: The fused ability
        """
        output = recipe.output
        element_type = output.get('element_type', ElementType.NONE)
        effects = output.get('effects', [])
        
        # Use the primary ability as a base (the one with the longer cooldown)
        base = ability1 if ability1.cooldown > ability2.cooldown else ability2
        ability_type = output.get('ability_type', base.ability_type)
        
        # Combine the base stats
        cooldown = (ability1.cooldown + ability2.cooldown) * 0.7  # Reduced cooldown
        resource_cost = max(ability1.resource_cost, ability2.resource_cost) * 1.2  # Slightly increased cost
        
        # Create the fusion ability
        fusion = Ability(
            fusion_id,
            recipe.name,
            recipe.description,
            ability1.damage + ability2.damage,  # Combined damage
            cooldown,
            max(ability1.range, ability2.range),  # Max range
            ability_type,
            base.trajectory,
            effects
        )
        
        # Set the element type
        fusion.element_type = element_type
        
        # Mark as fusion
        fusion.is_fused = True
        fusion.fusion_components = [ability1.ability_id, ability2.ability_id]
        fusion.fusion_type = f"{element_type.value}_fusion"
        
        return fusion

    @staticmethod
    def _create_ability_from_data(ability_id, data):
        """
        Create an ability from data dictionary
        
        Args:
            ability_id (str): ID for the ability
            data (dict): Ability data
            
        Returns:
            Ability: The created ability
        """
        if data["type"] == "projectile":
            # Create a projectile ability
            ability = ProjectileAbility(
                ability_id=ability_id,
                name=data["name"],
                description=data["description"],
                projectile_type=data.get("projectile_type", "straight"),
                damage=data.get("damage", 10),
                speed=data.get("speed", 10.0),
                cooldown=data.get("cooldown", 1.0),
                resource_cost=data.get("resource_cost", 0),
                icon=data.get("icon")
            )
            
            # Add piercing if specified
            if "pierce" in data:
                ability.pierce = data["pierce"]
            
            # Add element type if specified
            if "element_type" in data:
                ability.element_type = data["element_type"]
            
            return ability
            
        elif data["type"] == "melee":
            # Create a melee ability
            ability = MeleeAbility(
                ability_id=ability_id,
                name=data["name"],
                description=data["description"],
                damage=data.get("damage", 20),
                range=data.get("range", 2.0),
                angle=data.get("angle", 90.0),
                cooldown=data.get("cooldown", 0.5),
                resource_cost=data.get("resource_cost", 0),
                icon=data.get("icon")
            )
            
            # Add element type if specified
            if "element_type" in data:
                ability.element_type = data["element_type"]
            
            return ability
            
        elif data["type"] == "area":
            # Create an area ability
            ability = AreaAbility(
                ability_id=ability_id,
                name=data["name"],
                description=data["description"],
                effect_type=data.get("effect_type", "damage"),
                value=data.get("value", 10),
                radius=data.get("radius", 5.0),
                duration=data.get("duration", 0.0),
                cooldown=data.get("cooldown", 5.0),
                resource_cost=data.get("resource_cost", 20),
                icon=data.get("icon")
            )
            
            # Add summon type if specified
            if "summon_type" in data:
                ability.summon_type = data["summon_type"]
            
            # Add element type if specified
            if "element_type" in data:
                ability.element_type = data["element_type"]
            
            return ability
            
        else:
            # Create a default ability
            return Ability(
                data["name"],
                data["description"],
                data.get("damage", 0),
                data.get("cooldown", 1.0),
                data.get("range", 0),
                data.get("ability_type", AbilityType.UTILITY),
                data.get("trajectory", "none"),
                data.get("effects", []),
                data.get("element_type", ElementType.NONE)
            )


# Define standard abilities
STANDARD_ABILITIES = {
    # Warrior abilities
    "axe_slash": {
        "type": "melee",
        "name": "Axe Slash",
        "description": "A powerful slash with your axe.",
        "damage": 20,
        "range": 2.0,
        "angle": 90.0,
        "cooldown": 0.8,
        "resource_cost": 0,
        "element_type": ElementType.NONE,
        "icon": "axe_slash_icon.png"
    },
    
    "whirlwind": {
        "type": "melee",
        "name": "Whirlwind",
        "description": "Spin in a circle, damaging all enemies around you.",
        "damage": 15,
        "range": 3.0,
        "angle": 360.0,
        "cooldown": 5.0,
        "resource_cost": 20,
        "element_type": ElementType.WIND,
        "icon": "whirlwind_icon.png"
    },
    
    # Mage abilities
    "magic_bolt": {
        "type": "projectile",
        "name": "Magic Bolt",
        "description": "Fire a bolt of arcane energy.",
        "projectile_type": "straight",
        "damage": 15,
        "speed": 15.0,
        "cooldown": 0.5,
        "resource_cost": 5,
        "element_type": ElementType.ARCANE,
        "icon": "magic_bolt_icon.png"
    },
    
    "fireball": {
        "type": "projectile",
        "name": "Fireball",
        "description": "Launch a ball of fire that explodes on impact.",
        "projectile_type": "arcing",
        "damage": 30,
        "speed": 10.0,
        "cooldown": 3.0,
        "resource_cost": 15,
        "element_type": ElementType.FIRE,
        "icon": "fireball_icon.png"
    },
    
    # Cleric abilities
    "mace_hit": {
        "type": "melee",
        "name": "Mace Hit",
        "description": "Strike with your mace.",
        "damage": 18,
        "range": 1.8,
        "angle": 60.0,
        "cooldown": 0.7,
        "resource_cost": 0,
        "element_type": ElementType.NONE,
        "icon": "mace_hit_icon.png"
    },
    
    "healing_light": {
        "type": "area",
        "name": "Healing Light",
        "description": "Create an area of healing energy.",
        "effect_type": "heal",
        "value": 20,
        "radius": 4.0,
        "duration": 3.0,
        "cooldown": 6.0,
        "resource_cost": 25,
        "element_type": ElementType.HOLY,
        "icon": "healing_light_icon.png"
    },
    
    # Ranger abilities
    "sniper_shot": {
        "type": "projectile",
        "name": "Sniper Shot",
        "description": "Fire a high-damage arrow at a single target.",
        "projectile_type": "straight",
        "damage": 40,
        "speed": 25.0,
        "cooldown": 4.0,
        "resource_cost": 15,
        "element_type": ElementType.NONE,
        "icon": "sniper_shot_icon.png"
    },
    
    "multishot": {
        "type": "projectile",
        "name": "Multishot",
        "description": "Fire multiple arrows in a spread.",
        "projectile_type": "spread",
        "damage": 12,
        "speed": 15.0,
        "cooldown": 2.5,
        "resource_cost": 10,
        "element_type": ElementType.NONE,
        "icon": "multishot_icon.png"
    },
    
    # Alchemist abilities
    "deploy_turret": {
        "type": "area",
        "name": "Deploy Turret",
        "description": "Deploy an automatic turret that shoots nearby enemies.",
        "effect_type": "summon",
        "value": 8,  # Damage per shot
        "radius": 0.5,  # Turret size
        "duration": 20.0,  # Turret lifetime
        "cooldown": 10.0,
        "resource_cost": 25,
        "element_type": ElementType.NONE,
        "icon": "turret_icon.png"
    },
    
    "potion_throw": {
        "type": "projectile",
        "name": "Potion Throw",
        "description": "Throw a volatile potion that explodes on impact, dealing area damage.",
        "projectile_type": "arcing",
        "damage": 25,
        "speed": 12.0,
        "cooldown": 3.0,
        "resource_cost": 15,
        "element_type": ElementType.ARCANE,
        "icon": "potion_icon.png"
    },
    
    "healing_potion": {
        "type": "area",
        "name": "Healing Potion",
        "description": "Throw a healing potion that creates a mist, healing allies in the area over time.",
        "effect_type": "heal",
        "value": 5,  # Healing per second
        "radius": 3.0,
        "duration": 5.0,
        "cooldown": 12.0,
        "resource_cost": 30,
        "element_type": ElementType.WATER,
        "icon": "healing_potion_icon.png"
    },
    
    "multi_turret": {
        "type": "area",
        "name": "Multi-Turret",
        "description": "Deploy three smaller turrets in a triangle formation.",
        "effect_type": "summon",
        "value": 5,  # Damage per shot (per turret)
        "radius": 0.3,  # Turret size
        "duration": 15.0,  # Turret lifetime
        "cooldown": 20.0,
        "resource_cost": 40,
        "element_type": ElementType.NONE,
        "icon": "multi_turret_icon.png"
    },
    
    # Summoner abilities
    "spirit_summon": {
        "type": "area",
        "name": "Spirit Summon",
        "description": "Summon a spirit to fight for you.",
        "effect_type": "summon",
        "value": 15,  # Spirit damage
        "radius": 1.0,  # Spirit size
        "duration": 30.0,  # Spirit lifetime
        "cooldown": 8.0,
        "resource_cost": 30,
        "element_type": ElementType.ARCANE,
        "icon": "spirit_icon.png"
    },
    
    "spirit_command": {
        "type": "area",
        "name": "Spirit Command",
        "description": "Order your spirits to focus on a target area, increasing their damage.",
        "effect_type": "buff",
        "value": 1.5,  # Damage multiplier
        "radius": 5.0,
        "element_type": ElementType.ARCANE,
        "duration": 5.0,
        "cooldown": 10.0,
        "resource_cost": 15,
        "icon": "command_icon.png"
    },
    
    "spirit_shield": {
        "type": "area",
        "name": "Spirit Shield",
        "description": "Create a protective barrier of spirits that absorbs damage.",
        "effect_type": "buff",
        "value": 50,  # Shield amount
        "radius": 2.0,
        "duration": 8.0,
        "cooldown": 15.0,
        "resource_cost": 25,
        "element_type": ElementType.ARCANE,
        "icon": "spirit_shield_icon.png"
    },
    
    "spirit_fusion": {
        "type": "area",
        "name": "Spirit Fusion",
        "description": "Fuse all active spirits into a powerful elemental that deals massive damage.",
        "effect_type": "summon",
        "value": 50,  # Elemental damage
        "radius": 2.0,  # Elemental size
        "duration": 10.0,  # Elemental lifetime
        "cooldown": 30.0,
        "resource_cost": 50,
        "element_type": ElementType.ARCANE,
        "icon": "fusion_spirit_icon.png"
    }
}

def create_ability(ability_id):
    """
    Create an ability from predefined templates
    
    Args:
        ability_id (str): ID of the ability to create
        
    Returns:
        Ability: The created ability, or None if not found
    """
    # Class primary abilities
    ability_definitions = {
        # ========== Warrior Abilities ==========
        "axe_slash": {
            "name": "Axe Slash",
            "description": "A powerful melee attack with your axe",
            "type": "melee",
            "damage": 20,
            "range": 2.0,
            "angle": 90.0,
            "cooldown": 0.5,
            "resource_cost": 5,
            "icon": "axe_slash_icon.png"
        },
        "whirlwind": {
            "name": "Whirlwind",
            "description": "Spin around, damaging all enemies in a circle",
            "type": "melee",
            "damage": 15,
            "range": 3.0,
            "angle": 360.0,
            "cooldown": 4.0,
            "resource_cost": 15,
            "icon": "whirlwind_icon.png"
        },
        
        # ========== Mage Abilities ==========
        "magic_bolt": {
            "name": "Magic Bolt",
            "description": "Hurl a bolt of arcane energy",
            "type": "projectile",
            "projectile_type": "straight",
            "damage": 15,
            "speed": 12.0,
            "cooldown": 0.7,
            "resource_cost": 5,
            "icon": "magic_bolt_icon.png"
        },
        "fireball": {
            "name": "Fireball",
            "description": "Throw a ball of fire that explodes on impact",
            "type": "projectile",
            "projectile_type": "arcing",
            "damage": 25,
            "speed": 10.0,
            "cooldown": 3.0,
            "resource_cost": 15,
            "icon": "fireball_icon.png",
            "on_hit_effect": "explosion",
            "explosion_radius": 3.0,
            "explosion_damage": 10
        },
        "mana_shield": {
            "name": "Mana Shield",
            "description": "Create a protective barrier that absorbs damage at the cost of mana",
            "type": "area",
            "effect_type": "shield",
            "value": 50,
            "radius": 0,
            "duration": 8.0,
            "cooldown": 12.0,
            "resource_cost": 25,
            "icon": "mana_shield_icon.png"
        },
        
        # ========== Cleric Abilities ==========
        "mace_hit": {
            "name": "Mace Hit",
            "description": "Strike with your mace",
            "type": "melee",
            "damage": 18,
            "range": 2.0,
            "angle": 60.0,
            "cooldown": 0.6,
            "resource_cost": 5,
            "icon": "mace_hit_icon.png"
        },
        "healing_light": {
            "name": "Healing Light",
            "description": "Create a burst of healing energy that restores health to you and nearby allies",
            "type": "area",
            "effect_type": "heal",
            "value": 25,
            "radius": 5.0,
            "duration": 0,
            "cooldown": 8.0,
            "resource_cost": 20,
            "icon": "healing_light_icon.png"
        },
        "consecration": {
            "name": "Consecration",
            "description": "Sanctify the ground, damaging enemies and healing allies in the area",
            "type": "area",
            "effect_type": "dual",
            "damage_value": 5,
            "heal_value": 3,
            "radius": 4.0,
            "duration": 6.0,
            "cooldown": 10.0,
            "resource_cost": 25,
            "icon": "consecration_icon.png"
        },
        
        # ========== Ranger Abilities ==========
        "snipe_shot": {
            "name": "Snipe Shot",
            "description": "Fire a precise shot with your bow",
            "type": "projectile",
            "projectile_type": "straight",
            "damage": 18,
            "speed": 15.0,
            "cooldown": 0.8,
            "resource_cost": 5,
            "icon": "snipe_shot_icon.png",
            "crit_chance_bonus": 0.1
        },
        "multi_shot": {
            "name": "Multi Shot",
            "description": "Fire three arrows in a spread pattern",
            "type": "projectile",
            "projectile_type": "spread",
            "projectile_count": 3,
            "spread_angle": 30,
            "damage": 12,
            "speed": 12.0,
            "cooldown": 3.0,
            "resource_cost": 15,
            "icon": "multi_shot_icon.png"
        },
        "snare_trap": {
            "name": "Snare Trap",
            "description": "Place a trap that slows enemies when triggered",
            "type": "area",
            "effect_type": "trap",
            "value": 5,
            "radius": 2.0,
            "duration": 15.0,
            "effect_duration": 5.0,
            "slow_amount": 0.5,
            "cooldown": 8.0,
            "resource_cost": 15,
            "icon": "snare_trap_icon.png"
        },
        "evasion_roll": {
            "name": "Evasion Roll",
            "description": "Quickly dodge in any direction, becoming briefly invulnerable",
            "type": "movement",
            "distance": 5.0,
            "invulnerability_duration": 0.5,
            "cooldown": 5.0,
            "resource_cost": 10,
            "icon": "evasion_roll_icon.png"
        },
        
        # ========== Alchemist Abilities ==========
        "deploy_turret": {
            "name": "Deploy Turret",
            "description": "Place an automated turret that fires at nearby enemies",
            "type": "summon",
            "summon_type": "turret",
            "summon_health": 50,
            "summon_damage": 8,
            "summon_range": 8.0,
            "attack_speed": 1.0,
            "duration": 20.0,
            "cooldown": 12.0,
            "resource_cost": 20,
            "icon": "deploy_turret_icon.png"
        },
        "acid_flask": {
            "name": "Acid Flask",
            "description": "Throw a flask of acid that creates a damaging pool",
            "type": "projectile",
            "projectile_type": "arcing",
            "damage": 5,
            "speed": 8.0,
            "cooldown": 6.0,
            "resource_cost": 15,
            "on_hit_effect": "acid_pool",
            "acid_pool_radius": 3.0,
            "acid_pool_damage": 8,
            "acid_pool_duration": 5.0,
            "icon": "acid_flask_icon.png"
        },
        "healing_elixir": {
            "name": "Healing Elixir",
            "description": "Create a potion that restores health",
            "type": "item",
            "effect_type": "heal",
            "value": 35,
            "cooldown": 15.0,
            "resource_cost": 20,
            "icon": "healing_elixir_icon.png"
        },
        "flame_turret": {
            "name": "Flame Turret",
            "description": "Deploy a turret that fires flaming projectiles",
            "type": "summon",
            "summon_type": "flame_turret",
            "summon_health": 40,
            "summon_damage": 12,
            "fire_damage_over_time": 3,
            "fire_duration": 3.0,
            "summon_range": 7.0,
            "attack_speed": 1.2,
            "duration": 15.0,
            "cooldown": 15.0,
            "resource_cost": 25,
            "icon": "flame_turret_icon.png"
        },
        
        # ========== Summoner Abilities ==========
        "summon_spirit": {
            "name": "Summon Spirit",
            "description": "Call forth a spirit to fight for you",
            "type": "summon",
            "summon_type": "spirit",
            "summon_health": 40,
            "summon_damage": 10,
            "summon_range": 5.0,
            "attack_speed": 1.0,
            "duration": 30.0,
            "cooldown": 8.0,
            "resource_cost": 20,
            "icon": "summon_spirit_icon.png"
        },
        "summon_fire_elemental": {
            "name": "Summon Fire Elemental",
            "description": "Summon a fire elemental that burns enemies",
            "type": "summon",
            "summon_type": "fire_elemental",
            "summon_health": 60,
            "summon_damage": 15,
            "fire_damage_over_time": 5,
            "fire_duration": 3.0,
            "summon_range": 4.0,
            "attack_speed": 1.2,
            "duration": 20.0,
            "cooldown": 15.0,
            "resource_cost": 30,
            "icon": "fire_elemental_icon.png"
        },
        "summon_frost_elemental": {
            "name": "Summon Frost Elemental",
            "description": "Summon a frost elemental that slows enemies",
            "type": "summon",
            "summon_type": "frost_elemental",
            "summon_health": 70,
            "summon_damage": 12,
            "slow_amount": 0.4,
            "slow_duration": 2.0,
            "summon_range": 4.0,
            "attack_speed": 0.8,
            "duration": 20.0,
            "cooldown": 15.0,
            "resource_cost": 30,
            "icon": "frost_elemental_icon.png"
        }
    }
    
    if ability_id in ability_definitions:
        ability_data = ability_definitions[ability_id]
        ability = AbilityFactory._create_ability_from_data(ability_id, ability_data)
        return ability
    
    return None

class AbilityFactory:
    """Factory class for creating and managing abilities"""
    
    def __init__(self, game):
        """Initialize the ability factory"""
        self.game = game
        self.ability_cache = {}  # Cache of created abilities
        
        # Load ability definitions
        from game.skill_definitions import CLASS_ABILITIES
        self.ability_definitions = CLASS_ABILITIES
    
    def create_ability(self, class_type, ability_type, ability_name=None):
        """
        Create an ability for the specified class and type
        
        Args:
            class_type: The character class (warrior, mage, etc.)
            ability_type: Whether this is a "primary" or "secondary" ability
            ability_name: For secondary abilities, the specific ability name
                          (e.g., "fireball", "ground_slam", etc.)
        
        Returns:
            An ability instance
        """
        class_type = class_type.lower()
        
        # Validate class type
        if class_type not in self.ability_definitions:
            print(f"Warning: Unknown class type '{class_type}'")
            return None
        
        # Validate ability type
        if ability_type not in self.ability_definitions[class_type]:
            print(f"Warning: Unknown ability type '{ability_type}' for class '{class_type}'")
            return None
        
        # For primary abilities, no name is needed
        if ability_type == "primary":
            ability_data = self.ability_definitions[class_type][ability_type]
            return self._instantiate_ability(class_type, ability_type, ability_data)
        
        # For secondary abilities, we need the specific ability name
        elif ability_type == "secondary":
            if ability_name is None:
                print(f"Warning: No ability name provided for secondary ability")
                return None
                
            if ability_name not in self.ability_definitions[class_type][ability_type]:
                print(f"Warning: Unknown secondary ability '{ability_name}' for class '{class_type}'")
                return None
                
            ability_data = self.ability_definitions[class_type][ability_type][ability_name]
            return self._instantiate_ability(class_type, ability_type, ability_data, ability_name)
            
        return None
    
    def _instantiate_ability(self, class_type, ability_type, ability_data, ability_name=None):
        """
        Instantiate an ability based on its data
        
        Args:
            class_type: The character class
            ability_type: Primary or secondary
            ability_data: The ability definition data
            ability_name: Optional specific name for secondary abilities
        
        Returns:
            An ability instance
        """
        from game.ability_system import Ability
        
        # Create a unique key for this ability
        if ability_name:
            key = f"{class_type}_{ability_type}_{ability_name}"
        else:
            key = f"{class_type}_{ability_type}"
            
        # Return from cache if already created
        if key in self.ability_cache:
            return self.ability_cache[key]
            
        # Create the ability
        ability = Ability(
            name=ability_data["name"],
            description=ability_data["description"],
            damage=ability_data["damage"],
            cooldown=ability_data["cooldown"],
            range=ability_data["range"],
            ability_type=ability_data["type"],
            trajectory=ability_data["trajectory"],
            effects=ability_data["effects"]
        )
        
        # Store in cache
        self.ability_cache[key] = ability
        
        return ability
    
    def get_available_secondary_abilities(self, class_type):
        """
        Get all available secondary abilities for a class
        
        Args:
            class_type: The character class
            
        Returns:
            Dictionary of ability_name: ability_data
        """
        class_type = class_type.lower()
        
        if class_type not in self.ability_definitions:
            print(f"Warning: Unknown class type '{class_type}'")
            return {}
            
        if "secondary" not in self.ability_definitions[class_type]:
            print(f"Warning: No secondary abilities defined for class '{class_type}'")
            return {}
            
        return self.ability_definitions[class_type]["secondary"]
    
    def get_ability_names_by_class(self, class_type):
        """
        Get all ability names for a class
        
        Args:
            class_type: The character class
            
        Returns:
            Dictionary with 'primary' and 'secondary' keys
        """
        class_type = class_type.lower()
        
        if class_type not in self.ability_definitions:
            print(f"Warning: Unknown class type '{class_type}'")
            return {"primary": None, "secondary": []}
            
        # Get primary ability name
        primary_name = self.ability_definitions[class_type]["primary"]["name"]
        
        # Get all secondary ability names
        secondary_names = []
        if "secondary" in self.ability_definitions[class_type]:
            secondary_names = [
                ability_data["name"]
                for ability_name, ability_data in self.ability_definitions[class_type]["secondary"].items()
            ]
            
        return {
            "primary": primary_name,
            "secondary": secondary_names
        } 