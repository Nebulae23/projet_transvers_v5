#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ability System for Nightfall Defenders
Implements abilities with specialization and fusion mechanics
"""

import uuid
from enum import Enum
import math
import random

class AbilityType(Enum):
    """Types of abilities"""
    PROJECTILE = "projectile"
    MELEE = "melee"
    AREA = "area"
    BUFF = "buff"
    DEBUFF = "debuff"
    SUMMON = "summon"
    MOVEMENT = "movement"
    UTILITY = "utility"


class SpecializationPath(Enum):
    """Specialization paths for abilities"""
    DAMAGE = "damage"      # Focuses on increasing damage
    UTILITY = "utility"    # Focuses on adding utility effects
    EFFICIENCY = "efficiency"  # Focuses on reducing cooldown/cost
    AREA = "area"          # Focuses on affecting multiple targets
    DURATION = "duration"  # Focuses on extending effect durations
    HYBRID = "hybrid"      # Mixed specialization


class ElementType(Enum):
    """Elemental types for abilities"""
    NONE = "none"          # Non-elemental
    FIRE = "fire"          # Fire element
    ICE = "ice"            # Ice element
    LIGHTNING = "lightning" # Lightning element
    EARTH = "earth"        # Earth element
    WATER = "water"        # Water element
    WIND = "wind"          # Wind element
    ARCANE = "arcane"      # Arcane/magic element
    HOLY = "holy"          # Holy/divine element
    SHADOW = "shadow"      # Shadow/dark element


class Ability:
    """Represents a character ability with trajectory-based effects"""
    
    def __init__(self, name, description, damage, cooldown, range, ability_type, trajectory, effects, element_type=ElementType.NONE):
        """
        Initialize an ability
        
        Args:
            name: Ability name
            description: Ability description
            damage: Base damage
            cooldown: Cooldown time in seconds
            range: Maximum range
            ability_type: Type of ability (projectile, melee, aoe, etc.)
            trajectory: Trajectory type (straight, arc, radial, etc.)
            effects: List of status effects this ability can apply
            element_type: Elemental type of the ability (fire, ice, etc.)
        """
        self.name = name
        self.description = description
        self.damage = damage
        self.cooldown = cooldown
        self.range = range
        self.ability_type = ability_type
        self.trajectory = trajectory
        self.effects = effects
        self.element_type = element_type
        
        # Runtime state
        self.level = 1
        self.current_cooldown = 0
        self.owner = None
        self.is_specialized = False
        self.specialization_path = None
        self.is_fused = False
        self.fusion_components = []
        
        # Harmonization properties
        self.is_harmonized = False
        self.harmonization_level = 0
        self.harmonization_effect = None
        
        # Visuals
        self.visual_effect = None
        self.sound_effect = None
        
        # Upgrades and modifications
        self.modifiers = {}
    
    def use(self, caster, target_pos):
        """
        Use the ability
        
        Args:
            caster: The entity using the ability
            target_pos: Target position (Vec3)
            
        Returns:
            True if ability was used, False if on cooldown
        """
        if self.current_cooldown > 0:
            return False
            
        # Set cooldown
        self.current_cooldown = self.cooldown
        
        # Create projectile or effect based on ability type
        if self.ability_type == "projectile":
            self._create_projectile(caster, target_pos)
        elif self.ability_type == "melee":
            self._perform_melee_attack(caster, target_pos)
        elif self.ability_type == "aoe":
            self._create_aoe_effect(caster, target_pos)
        elif self.ability_type == "buff":
            self._apply_buff(caster, target_pos)
        elif self.ability_type == "summon":
            self._summon_entity(caster, target_pos)
        elif self.ability_type == "trap":
            self._place_trap(caster, target_pos)
        elif self.ability_type == "heal":
            self._create_healing_effect(caster, target_pos)
        elif self.ability_type == "control":
            self._apply_control_effect(caster, target_pos)
        elif self.ability_type == "special":
            self._perform_special_ability(caster, target_pos)
        
        # Play sound effect
        if self.sound_effect:
            self._play_sound_effect()
            
        return True
        
    def update(self, dt):
        """
        Update ability state
        
        Args:
            dt: Delta time in seconds
        """
        # Update cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
            if self.current_cooldown < 0:
                self.current_cooldown = 0
    
    def get_cooldown_percent(self):
        """
        Get the cooldown percentage
        
        Returns:
            Cooldown percentage (0.0 to 1.0)
        """
        if self.cooldown <= 0:
            return 0.0
        return self.current_cooldown / self.cooldown
    
    def is_ready(self):
        """
        Check if ability is ready to use
        
        Returns:
            True if ready, False if on cooldown
        """
        return self.current_cooldown <= 0
    
    def upgrade(self):
        """
        Upgrade the ability to the next level
        
        Returns:
            True if upgraded, False if at max level
        """
        # Base implementation - can be overridden for different abilities
        max_level = 5
        if self.level >= max_level:
            return False
            
        self.level += 1
        
        # Enhance stats based on level
        self.damage = int(self.damage * 1.2)  # 20% damage increase per level
        self.cooldown = max(0.5, self.cooldown * 0.9)  # 10% cooldown reduction per level
        
        return True
    
    def add_modifier(self, mod_id, mod_data):
        """
        Add a modifier to the ability
        
        Args:
            mod_id: Unique modifier ID
            mod_data: Modifier data dictionary
        """
        self.modifiers[mod_id] = mod_data
        self._apply_modifiers()
    
    def remove_modifier(self, mod_id):
        """
        Remove a modifier from the ability
        
        Args:
            mod_id: Modifier ID to remove
        
        Returns:
            True if removed, False if not found
        """
        if mod_id in self.modifiers:
            del self.modifiers[mod_id]
            self._apply_modifiers()
            return True
        return False
    
    def _apply_modifiers(self):
        """Apply all current modifiers to the ability"""
        # Reset to base stats first
        # Then apply all modifiers
        pass
    
    def specialize(self, path):
        """
        Specialize the ability along a specific path
        
        Args:
            path: Specialization path name
            
        Returns:
            True if specialized, False if already specialized
        """
        if self.is_specialized:
            return False
            
        self.is_specialized = True
        self.specialization_path = path
        
        # Apply specialization effects
        # This would be implemented differently for each ability
        
        return True
    
    def _create_projectile(self, caster, target_pos):
        """Create a projectile based on ability trajectory"""
        if not hasattr(caster, 'game'):
            print("Warning: Caster has no game attribute")
            return
            
        # Calculate direction vector
        from panda3d.core import Vec3
        direction = target_pos - caster.position
        direction.normalize()
        
        # Create projectile entity
        from game.projectile import Projectile
        
        # Determine projectile behavior based on trajectory type
        if self.trajectory == "straight":
            projectile = Projectile(
                game=caster.game,
                position=caster.position + Vec3(0, 0, 0.5),  # Slight height offset
                direction=direction,
                speed=15.0,
                damage=self.get_total_damage(),
                range=self.range,
                owner=caster,
                ability=self
            )
        elif self.trajectory == "arcing":
            projectile = Projectile(
                game=caster.game,
                position=caster.position + Vec3(0, 0, 0.5),
                direction=direction,
                speed=12.0,
                damage=self.get_total_damage(),
                range=self.range,
                owner=caster,
                ability=self,
                arc_height=2.0,
                gravity=9.8
            )
        elif self.trajectory == "homing":
            projectile = Projectile(
                game=caster.game,
                position=caster.position + Vec3(0, 0, 0.5),
                direction=direction,
                speed=8.0,
                damage=self.get_total_damage(),
                range=self.range,
                owner=caster,
                ability=self,
                homing=True,
                turn_rate=0.1
            )
        elif self.trajectory == "spread":
            # Create multiple projectiles in a spread pattern
            num_projectiles = 3
            spread_angle = 15.0  # degrees
            
            for i in range(num_projectiles):
                angle = (i - (num_projectiles - 1) / 2) * spread_angle
                # Rotate direction vector by angle
                from math import sin, cos, radians
                rot_angle = radians(angle)
                new_dir = Vec3(
                    direction.x * cos(rot_angle) - direction.y * sin(rot_angle),
                    direction.x * sin(rot_angle) + direction.y * cos(rot_angle),
                    direction.z
                )
                
                projectile = Projectile(
                    game=caster.game,
                    position=caster.position + Vec3(0, 0, 0.5),
                    direction=new_dir,
                    speed=15.0,
                    damage=self.get_total_damage() * 0.8,  # Reduced damage for spread
                    range=self.range,
                    owner=caster,
                    ability=self
                )
        elif self.trajectory == "chain":
            projectile = Projectile(
                game=caster.game,
                position=caster.position + Vec3(0, 0, 0.5),
                direction=direction,
                speed=20.0,
                damage=self.get_total_damage(),
                range=self.range,
                owner=caster,
                ability=self,
                chain=True,
                chain_count=3,
                chain_range=5.0
            )
        else:
            # Default to straight projectile
            projectile = Projectile(
                game=caster.game,
                position=caster.position + Vec3(0, 0, 0.5),
                direction=direction,
                speed=15.0,
                damage=self.get_total_damage(),
                range=self.range,
                owner=caster,
                ability=self
            )
            
        # Add the projectile to the game
        caster.game.entity_manager.add_entity(projectile)
    
    def get_total_damage(self):
        """Calculate total damage with modifiers"""
        base_damage = self.damage * (1 + 0.1 * (self.level - 1))  # 10% per level
        
        # Apply modifiers
        modifier_multiplier = 1.0
        for mod_id, mod_data in self.modifiers.items():
            if 'damage_multiplier' in mod_data:
                modifier_multiplier *= mod_data['damage_multiplier']
        
        return int(base_damage * modifier_multiplier)
        
    def _perform_melee_attack(self, caster, target_pos):
        """Perform a melee attack"""
        # Similar to projectile but with instant hit in close range
        pass
        
    def _create_aoe_effect(self, caster, target_pos):
        """Create an area of effect"""
        pass
        
    def _apply_buff(self, caster, target_pos):
        """Apply a buff to target or self"""
        pass
        
    def _summon_entity(self, caster, target_pos):
        """Summon an entity at the target position"""
        pass
        
    def _place_trap(self, caster, target_pos):
        """Place a trap at the target position"""
        pass
        
    def _create_healing_effect(self, caster, target_pos):
        """Create a healing effect"""
        pass
        
    def _apply_control_effect(self, caster, target_pos):
        """Apply a control effect to enemies"""
        pass
        
    def _perform_special_ability(self, caster, target_pos):
        """Perform a special ability with unique effects"""
        pass
        
    def _play_sound_effect(self):
        """Play ability sound effect"""
        # Implement sound playback logic here
        pass
    
    def can_fuse_with(self, other_ability):
        """
        Check if this ability can be fused with another ability
        
        Args:
            other_ability (Ability): The ability to check fusion compatibility with
            
        Returns:
            bool: True if the abilities can be fused, False otherwise
        """
        # Cannot fuse with self
        if self == other_ability:
            return False
            
        # Cannot fuse if either ability is already a fusion
        if self.is_fused or other_ability.is_fused:
            return False
            
        # Check if the player has unlocked the appropriate fusion type
        # (e.g., elemental fusion for elemental abilities)
        # This would be checked via the player object in a real implementation
        
        # For now, allow fusion of any two different abilities
        return True
    
    def create_fusion(self, other_ability):
        """
        Create a fusion with another ability
        
        Args:
            other_ability (Ability): The ability to fuse with
            
        Returns:
            Ability or None: The fused ability, or None if fusion not possible
        """
        # Check if fusion is possible
        if not self.can_fuse_with(other_ability):
            return None
            
        # Defer to AbilityFactory for actual creation
        from game.ability_factory import AbilityFactory
        return AbilityFactory.create_fusion(self, other_ability)
    
    def harmonize(self, effect_data=None):
        """
        Harmonize this ability, enhancing its effects
        
        Args:
            effect_data (dict): Optional effect data to apply. If None, 
                                a default harmonization will be applied
        
        Returns:
            bool: True if harmonized successfully, False if already harmonized
        """
        # Cannot harmonize an already harmonized ability
        if self.is_harmonized:
            return False
            
        # Cannot harmonize a fused ability (for game balance)
        if self.is_fused:
            return False
        
        # Apply harmonization
        self.is_harmonized = True
        self.harmonization_level = 1
        
        if effect_data:
            self.harmonization_effect = effect_data
            
            # Apply effect modifiers based on the ability type
            if 'damage_multiplier' in effect_data:
                self.damage *= effect_data['damage_multiplier']
                
            if 'cooldown_multiplier' in effect_data:
                self.cooldown *= effect_data['cooldown_multiplier']
                
            if 'range_multiplier' in effect_data and hasattr(self, 'range'):
                self.range *= effect_data['range_multiplier']
            
            # Update ability name and description if provided
            if 'name' in effect_data:
                self.name = effect_data['name']
                
            if 'description' in effect_data:
                self.description = effect_data['description']
        else:
            # Default harmonization (if no specific effect provided)
            self.damage *= 1.3  # 30% damage increase
            self.cooldown *= 1.2  # 20% cooldown increase (balance)
            self.harmonization_effect = {
                'damage_multiplier': 1.3,
                'cooldown_multiplier': 1.2
            }
            
        return True


class ProjectileAbility(Ability):
    """Ability that fires a projectile"""
    
    def __init__(self, ability_id, name, description, 
                 projectile_type="straight", damage=10, speed=10.0, 
                 cooldown=1.0, resource_cost=0, icon=None):
        """Initialize a projectile ability"""
        super().__init__(
            name, description, damage, cooldown, 0, 
            AbilityType.PROJECTILE, projectile_type, []
        )
        
        self.projectile_type = projectile_type
        self.base_damage = damage
        self.damage = damage
        self.speed = speed
        self.pierce = 0  # Number of targets the projectile can pierce
        self.chain = 0   # Number of targets the projectile can chain to
        self.aoe_radius = 0  # Explosion radius (if explodes)
    
    def use(self, caster, target=None, position=None):
        """Use the projectile ability, creating a projectile"""
        if not super().use(caster, position):
            return False
        
        # Calculate direction
        direction = None
        
        if position:
            # Direction toward position
            direction = position - caster.position
            if direction.length() > 0:
                direction.normalize()
        elif target:
            # Direction toward target
            direction = target.position - caster.position
            if direction.length() > 0:
                direction.normalize()
        else:
            # Default to forward direction
            direction = caster.direction.normalized()
        
        # Create the projectile
        if hasattr(caster.game, 'entity_manager'):
            caster.game.entity_manager.create_projectile(
                self.projectile_type,
                caster.position,
                direction,
                owner=caster,
                damage=self.damage,
                speed=self.speed,
                pierce=self.pierce,
                chain=self.chain,
                aoe_radius=self.aoe_radius
            )
        
        return True
    
    def apply_specialization(self, path, level=1):
        """Apply specialization to projectile ability"""
        if not super().apply_specialization(path, level):
            return False
        
        # Apply projectile-specific specialization effects
        if path == SpecializationPath.DAMAGE:
            self.damage = self.base_damage * self.damage_multiplier
        
        elif path == SpecializationPath.UTILITY:
            # Add utility effects based on level
            if level >= 1:
                self.pierce = 1
            if level >= 2:
                self.aoe_radius = 2.0
            if level >= 3:
                self.chain = 2
        
        elif path == SpecializationPath.AREA:
            self.aoe_radius = 1.5 * self.area_multiplier
            self.damage = self.base_damage * self.damage_multiplier
        
        return True


class MeleeAbility(Ability):
    """Ability that performs a melee attack"""
    
    def __init__(self, ability_id, name, description, 
                 damage=20, range=2.0, angle=90.0,
                 cooldown=0.5, resource_cost=0, icon=None):
        """Initialize a melee ability"""
        super().__init__(
            name, description, damage, cooldown, range, 
            AbilityType.MELEE, "straight", []
        )
        
        self.base_damage = damage
        self.damage = damage
        self.range = range
        self.angle = angle  # Arc angle in degrees
    
    def use(self, caster, target=None, position=None):
        """Use the melee ability, damaging enemies in an arc"""
        if not super().use(caster, position):
            return False
        
        # Get entities in range and arc
        if hasattr(caster.game, 'entity_manager'):
            entities = caster.game.entity_manager.get_nearby_entities(
                caster.position, self.range
            )
            
            # Filter entities in the arc
            for entity in entities:
                if entity == caster:
                    continue
                
                # Calculate angle to entity
                direction = entity.position - caster.position
                if direction.length() == 0:
                    continue
                
                # Check if entity is within the arc
                forward = caster.direction.normalized()
                direction.normalize()
                
                dot = forward.dot(direction)
                angle = math.acos(dot) * 180 / math.pi
                
                if angle <= self.angle / 2:
                    # Entity is in the arc, damage it
                    if hasattr(entity, 'take_damage'):
                        entity.take_damage(self.damage, source=caster)
        
        return True
    
    def apply_specialization(self, path, level=1):
        """Apply specialization to melee ability"""
        if not super().apply_specialization(path, level):
            return False
        
        # Apply melee-specific specialization effects
        if path == SpecializationPath.DAMAGE:
            self.damage = self.base_damage * self.damage_multiplier
        
        elif path == SpecializationPath.AREA:
            self.angle = min(360, self.angle * self.area_multiplier)
            self.range = self.range * self.area_multiplier
            self.damage = self.base_damage * self.damage_multiplier
        
        return True


class AreaAbility(Ability):
    """Ability that affects an area"""
    
    def __init__(self, ability_id, name, description, 
                 effect_type="damage", value=10, radius=5.0, duration=0.0,
                 cooldown=5.0, resource_cost=20, icon=None):
        """Initialize an area ability"""
        super().__init__(
            name, description, value, cooldown, 0, 
            AbilityType.AREA, "straight", []
        )
        
        self.effect_type = effect_type  # damage, heal, buff, debuff
        self.base_value = value
        self.value = value
        self.radius = radius
        self.base_duration = duration
        self.duration = duration
    
    def use(self, caster, target=None, position=None):
        """Use the area ability, affecting entities in an area"""
        if not super().use(caster, position):
            return False
        
        # Determine center position
        center = None
        if position:
            center = position
        elif target:
            center = target.position
        else:
            center = caster.position
        
        # Apply effect based on type
        if hasattr(caster.game, 'entity_manager'):
            entities = caster.game.entity_manager.get_nearby_entities(
                center, self.radius
            )
            
            for entity in entities:
                if self.effect_type == "damage":
                    # Damage enemies only
                    if entity != caster and hasattr(entity, 'take_damage'):
                        entity.take_damage(self.value, source=caster)
                
                elif self.effect_type == "heal":
                    # Heal allies (including self)
                    if hasattr(entity, 'heal'):
                        entity.heal(self.value)
                
                elif self.effect_type == "buff":
                    # Apply buff to allies
                    if hasattr(entity, 'add_buff'):
                        entity.add_buff("area_buff", self.value, self.duration)
                
                elif self.effect_type == "debuff":
                    # Apply debuff to enemies
                    if entity != caster and hasattr(entity, 'add_debuff'):
                        entity.add_debuff("area_debuff", self.value, self.duration)
        
        # Create visual effect
        if hasattr(caster.game, 'entity_manager') and hasattr(caster.game.entity_manager, 'create_area_effect'):
            caster.game.entity_manager.create_area_effect(
                center, self.radius, self.effect_type, self.duration
            )
        
        return True
    
    def apply_specialization(self, path, level=1):
        """Apply specialization to area ability"""
        if not super().apply_specialization(path, level):
            return False
        
        # Apply area-specific specialization effects
        if path == SpecializationPath.DAMAGE and self.effect_type == "damage":
            self.value = self.base_value * self.damage_multiplier
        
        elif path == SpecializationPath.AREA:
            self.radius = self.radius * self.area_multiplier
            # Adjust value based on area (larger area = less value per target)
            self.value = self.base_value * self.damage_multiplier
        
        elif path == SpecializationPath.DURATION and self.duration > 0:
            self.duration = self.base_duration * self.duration_multiplier
        
        return True


class AbilityManager:
    """Manages all abilities for an entity"""
    
    def __init__(self, owner):
        """
        Initialize the ability manager
        
        Args:
            owner: Entity that owns these abilities
        """
        self.owner = owner
        self.abilities = {}  # Dictionary of ability_id -> Ability
        self.active_abilities = []  # List of ability_ids that are equipped/active
        self.max_active_abilities = 4  # Maximum number of active abilities
        self.unlocked_abilities = set()  # Set of unlocked ability_ids
        self.specialization_choices = {}  # Dict of ability_id -> chosen specialization
        self.harmonization_choices = set()  # Set of harmonized ability_ids
    
    def add_ability(self, ability):
        """
        Add an ability to the manager
        
        Args:
            ability (Ability): Ability to add
            
        Returns:
            bool: True if added successfully
        """
        self.abilities[ability.ability_id] = ability
        return True
    
    def unlock_ability(self, ability_id):
        """
        Unlock an ability for use
        
        Args:
            ability_id (str): ID of ability to unlock
            
        Returns:
            bool: True if unlocked successfully
        """
        if ability_id in self.abilities:
            self.unlocked_abilities.add(ability_id)
            
            # If we have space, automatically equip it
            if len(self.active_abilities) < self.max_active_abilities:
                self.active_abilities.append(ability_id)
            
            return True
        return False
    
    def activate_ability(self, ability_id, slot=None):
        """
        Activate an ability in a specific slot
        
        Args:
            ability_id (str): ID of ability to activate
            slot (int): Slot to place the ability in (0-based)
            
        Returns:
            bool: True if activated successfully
        """
        if ability_id not in self.unlocked_abilities:
            return False
        
        if slot is None:
            # Find the first available slot
            if len(self.active_abilities) < self.max_active_abilities:
                self.active_abilities.append(ability_id)
                return True
            return False
        
        # Ensure slot is valid
        if slot < 0 or slot >= self.max_active_abilities:
            return False
        
        # If slot is already occupied, replace it
        while len(self.active_abilities) <= slot:
            self.active_abilities.append(None)
        
        self.active_abilities[slot] = ability_id
        return True
    
    def use_ability(self, slot, target=None, position=None):
        """
        Use the ability in the specified slot
        
        Args:
            slot (int): Slot of the ability to use (0-based)
            target: Target entity (if targeting an entity)
            position: Target position (if targeting a location)
            
        Returns:
            bool: True if the ability was used successfully
        """
        if slot < 0 or slot >= len(self.active_abilities):
            return False
        
        ability_id = self.active_abilities[slot]
        if not ability_id or ability_id not in self.abilities:
            return False
        
        ability = self.abilities[ability_id]
        return ability.use(self.owner, target, position)
    
    def update(self, dt):
        """
        Update all abilities
        
        Args:
            dt (float): Delta time
        """
        for ability in self.abilities.values():
            ability.update(dt)
    
    def get_ability(self, ability_id):
        """
        Get an ability by ID
        
        Args:
            ability_id (str): ID of the ability
            
        Returns:
            Ability or None: The ability if found, None otherwise
        """
        return self.abilities.get(ability_id)
    
    def modify_ability(self, ability_id, modifiers):
        """
        Apply modifiers to an ability
        
        Args:
            ability_id (str): ID of the ability to modify
            modifiers (dict): Dictionary of modifiers to apply
            
        Returns:
            bool: True if modified successfully
        """
        ability = self.get_ability(ability_id)
        if not ability:
            return False
        
        # Apply modifiers
        for modifier, value in modifiers.items():
            if hasattr(ability, modifier):
                setattr(ability, modifier, value)
        
        # Recalculate stats
        ability.recalculate_stats()
        return True
    
    def specialize_ability(self, ability_id, path):
        """
        Specialize an ability along a path
        
        Args:
            ability_id (str): ID of the ability to specialize
            path (SpecializationPath): Specialization path
            
        Returns:
            bool: True if specialized successfully
        """
        ability = self.get_ability(ability_id)
        if not ability:
            return False
        
        # Check if already specialized on a different path
        if ability_id in self.specialization_choices and self.specialization_choices[ability_id] != path:
            return False
        
        # Get current level (0 if not specialized yet)
        current_level = 0
        if ability_id in self.specialization_choices:
            current_level = ability.specialization_level
        
        # Apply specialization at next level
        success = ability.apply_specialization(path, current_level + 1)
        
        if success:
            self.specialization_choices[ability_id] = path
        
        return success
    
    def harmonize_ability(self, ability_id):
        """
        Harmonize an ability to enhance its effects
        
        Args:
            ability_id (str): ID of the ability to harmonize
            
        Returns:
            str or None: ID of the harmonized ability or None if harmonization failed
        """
        original_ability = self.get_ability(ability_id)
        if not original_ability:
            return None
        
        # Check if player has unlocked the ability to harmonize abilities
        if hasattr(self.owner, 'can_harmonize_abilities') and not getattr(self.owner, 'can_harmonize_abilities', False):
            return None
        
        # Check if ability is already harmonized or fused
        if original_ability.is_harmonized or original_ability.is_fused:
            return None
        
        # Check if this ability type requires a specific harmonization unlock
        if original_ability.ability_type == AbilityType.PROJECTILE:
            unlock_name = 'projectile_harmonization'
        elif original_ability.ability_type == AbilityType.MELEE:
            unlock_name = 'melee_harmonization'
        elif original_ability.ability_type == AbilityType.AREA:
            unlock_name = 'area_harmonization'
        else:
            unlock_name = 'basic_harmonization'
            
        # Check if player has the specific harmonization unlock
        if hasattr(self.owner, f'can_use_{unlock_name}') and not getattr(self.owner, f'can_use_{unlock_name}', False):
            return None
            
        # Create harmonized ability
        from game.ability_factory import AbilityFactory
        harmonized_ability = AbilityFactory.create_harmonized_ability(original_ability)
        
        if not harmonized_ability:
            return None
            
        # Add the harmonized ability
        self.add_ability(harmonized_ability)
        self.unlock_ability(harmonized_ability.ability_id)
        
        # Record that this ability has been harmonized
        self.harmonization_choices.add(ability_id)
        
        return harmonized_ability.ability_id
    
    def create_fusion(self, ability_id1, ability_id2):
        """
        Create a fusion of two abilities
        
        Args:
            ability_id1 (str): ID of first ability
            ability_id2 (str): ID of second ability
            
        Returns:
            str or None: ID of the new fused ability or None if fusion failed
        """
        ability1 = self.get_ability(ability_id1)
        ability2 = self.get_ability(ability_id2)
        
        if not ability1 or not ability2:
            return None
        
        # Check if player has unlocked the ability to create fusions
        if hasattr(self.owner, 'can_create_fusions') and not self.owner.can_create_fusions:
            return None
        
        # Check for element-specific fusion restrictions
        if ability1.element_type != ElementType.NONE and ability2.element_type != ElementType.NONE:
            # For elemental fusions, check if player has unlocked elemental fusion
            if hasattr(self.owner, 'can_use_elemental_fusion') and not getattr(self.owner, 'can_use_elemental_fusion', False):
                return None
        
        # Check for weapon-specific fusion restrictions
        if (ability1.ability_type == AbilityType.MELEE or ability1.ability_type == AbilityType.PROJECTILE) and \
           (ability2.ability_type == AbilityType.MELEE or ability2.ability_type == AbilityType.PROJECTILE):
            # For weapon fusions, check if player has unlocked weapon fusion
            if hasattr(self.owner, 'can_use_divine_weapon_fusion') and not getattr(self.owner, 'can_use_divine_weapon_fusion', False):
                return None
        
        # Create the fusion
        fused_ability = ability1.create_fusion(ability2)
        if not fused_ability:
            return None
        
        # Add the fused ability
        self.add_ability(fused_ability)
        self.unlock_ability(fused_ability.ability_id)
        
        return fused_ability.ability_id 