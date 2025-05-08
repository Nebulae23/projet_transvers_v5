#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Secondary Abilities System for Nightfall Defenders
Implements secondary abilities and their acquisition for character classes
"""

from enum import Enum
from .ability_factory import create_ability

class AbilityUnlockType(Enum):
    """Types of ability unlock methods"""
    LEVEL = "level"
    SKILL_TREE = "skill_tree"
    QUEST = "quest"
    SPECIAL_ITEM = "special_item"
    FUSION = "fusion"
    CHALLENGE = "challenge"


class SecondaryAbilityManager:
    """Manages character secondary abilities and their unlocking"""
    
    def __init__(self, player):
        """
        Initialize the secondary ability manager
        
        Args:
            player: The player character
        """
        self.player = player
        self.unlocked_abilities = []
        self.equipped_abilities = {}  # Slot ID -> Ability ID
        self.max_slots = 3  # Default max secondary abilities
        
        # Track ability unlock progress
        self.unlock_progress = {}
        
    def unlock_ability(self, ability_id, unlock_type=AbilityUnlockType.SKILL_TREE):
        """
        Unlock a secondary ability
        
        Args:
            ability_id (str): Ability ID to unlock
            unlock_type (AbilityUnlockType): How the ability was unlocked
            
        Returns:
            bool: True if successful, False if already unlocked or invalid
        """
        # Check if already unlocked
        if ability_id in self.unlocked_abilities:
            return False
            
        # Create the ability to validate it exists
        ability = create_ability(ability_id)
        if not ability:
            return False
            
        # Unlock the ability
        self.unlocked_abilities.append(ability_id)
        
        # Notify player of unlock
        print(f"Unlocked new ability: {ability.name} - {ability.description}")
        
        return True
    
    def equip_ability(self, ability_id, slot):
        """
        Equip an ability to a secondary slot
        
        Args:
            ability_id (str): Ability ID to equip
            slot (int): Slot to equip to (0-based)
            
        Returns:
            bool: True if successful, False if invalid
        """
        # Check if ability is unlocked
        if ability_id not in self.unlocked_abilities:
            return False
            
        # Check if slot is valid
        if slot < 0 or slot >= self.max_slots:
            return False
            
        # Equip the ability
        self.equipped_abilities[slot] = ability_id
        
        return True
    
    def unequip_ability(self, slot):
        """
        Remove an ability from a slot
        
        Args:
            slot (int): Slot to clear (0-based)
            
        Returns:
            bool: True if successful, False if invalid
        """
        if slot in self.equipped_abilities:
            del self.equipped_abilities[slot]
            return True
        return False
    
    def get_equipped_abilities(self):
        """
        Get all equipped abilities
        
        Returns:
            list: List of Ability objects currently equipped
        """
        abilities = []
        for slot in range(self.max_slots):
            ability_id = self.equipped_abilities.get(slot)
            if ability_id:
                ability = create_ability(ability_id)
                if ability:
                    abilities.append(ability)
            else:
                abilities.append(None)  # Empty slot
        return abilities
    
    def get_unlocked_abilities(self):
        """
        Get all unlocked abilities
        
        Returns:
            list: List of Ability objects that are unlocked
        """
        abilities = []
        for ability_id in self.unlocked_abilities:
            ability = create_ability(ability_id)
            if ability:
                abilities.append(ability)
        return abilities
    
    def use_ability(self, slot, target=None, position=None):
        """
        Use an equipped secondary ability
        
        Args:
            slot (int): Slot of the ability to use (0-based)
            target: Optional target entity
            position: Optional target position
            
        Returns:
            bool: True if ability was used, False if not
        """
        # Check if slot has an ability
        ability_id = self.equipped_abilities.get(slot)
        if not ability_id:
            return False
            
        # Create the ability
        ability = create_ability(ability_id)
        if not ability:
            return False
            
        # Use the ability
        return ability.use(self.player, target, position)
    
    def update(self, dt):
        """
        Update all abilities
        
        Args:
            dt (float): Delta time in seconds
        """
        # Update cooldowns for equipped abilities
        for slot, ability_id in self.equipped_abilities.items():
            ability = create_ability(ability_id)
            if ability:
                ability.update(dt)
    
    def increase_max_slots(self, amount=1):
        """
        Increase the maximum number of secondary ability slots
        
        Args:
            amount (int): Number of slots to add
            
        Returns:
            int: New max slots
        """
        self.max_slots += amount
        return self.max_slots
    
    def get_available_abilities_by_class(self, class_type):
        """
        Get abilities available to a specific class
        
        Args:
            class_type (str): Type of class to check
            
        Returns:
            list: List of ability IDs available to this class
        """
        # Define abilities available to each class
        class_abilities = {
            "warrior": [
                "whirlwind", 
                "shield_bash", 
                "battle_shout", 
                "charge"
            ],
            "mage": [
                "fireball", 
                "mana_shield", 
                "frost_nova", 
                "teleport"
            ],
            "cleric": [
                "healing_light", 
                "divine_shield", 
                "consecration", 
                "holy_nova"
            ],
            "ranger": [
                "multi_shot", 
                "snare_trap", 
                "evasion_roll", 
                "volley"
            ],
            "alchemist": [
                "acid_flask", 
                "healing_elixir", 
                "flame_turret", 
                "frost_turret"
            ],
            "summoner": [
                "summon_fire_elemental", 
                "summon_frost_elemental", 
                "spirit_shield", 
                "spirit_link"
            ]
        }
        
        return class_abilities.get(class_type.lower(), []) 