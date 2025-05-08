#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Character Class System for Nightfall Defenders
Implements different character classes with unique abilities and attributes
"""

from enum import Enum
from .ability_factory import create_ability

class ClassType(Enum):
    """Types of character classes"""
    WARRIOR = "warrior"
    MAGE = "mage"
    CLERIC = "cleric"
    RANGER = "ranger"
    ALCHEMIST = "alchemist"
    SUMMONER = "summoner"


class CharacterClass:
    """Base class for all character classes"""
    
    def __init__(self, class_type, name, description, icon=None):
        """
        Initialize a character class
        
        Args:
            class_type (ClassType): Type of class
            name (str): Display name
            description (str): Description of the class
            icon (str): Path to the icon texture
        """
        self.class_type = class_type
        self.name = name
        self.description = description
        self.icon = icon
        
        # Base stat modifiers
        self.health_modifier = 1.0
        self.stamina_modifier = 1.0
        self.speed_modifier = 1.0
        self.damage_modifier = 1.0
        
        # Starting abilities
        self.starting_abilities = []
        
        # Class-specific passives
        self.passives = {}
    
    def apply_class_bonuses(self, player):
        """
        Apply class-specific bonuses to the player
        
        Args:
            player: Player entity
        """
        # Apply stat modifiers
        player.max_health = int(player.max_health * self.health_modifier)
        player.health = player.max_health
        
        player.max_stamina = int(player.max_stamina * self.stamina_modifier)
        player.stamina = player.max_stamina
        
        player.speed = player.speed * self.speed_modifier
        player.damage_multiplier = player.damage_multiplier * self.damage_modifier
        
        # Apply class-specific passive effects
        for passive_id, passive_data in self.passives.items():
            if hasattr(player, 'add_passive'):
                player.add_passive(passive_id, passive_data)
    
    def get_starting_abilities(self):
        """
        Get the starting abilities for this class
        
        Returns:
            list: List of Ability objects
        """
        abilities = []
        for ability_id in self.starting_abilities:
            ability = create_ability(ability_id)
            if ability:
                abilities.append(ability)
        return abilities
    
    def get_available_skill_nodes(self):
        """
        Get the skill tree nodes available to this class
        
        Returns:
            list: List of skill node IDs
        """
        # Override in subclasses
        return []
    
    def on_level_up(self, player, level):
        """
        Handle class-specific level up effects
        
        Args:
            player: Player entity
            level: New level
        """
        # Override in subclasses
        pass


class Warrior(CharacterClass):
    """Warrior class focusing on melee combat and high health"""
    
    def __init__(self):
        """Initialize the Warrior class"""
        super().__init__(
            ClassType.WARRIOR,
            "Warrior",
            "A powerful melee fighter with high health and close-range abilities.",
            "warrior_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 1.3
        self.stamina_modifier = 1.1
        self.speed_modifier = 0.9
        self.damage_modifier = 1.2
        
        # Starting abilities
        self.starting_abilities = ["axe_slash"]
        
        # Class passives
        self.passives = {
            "warrior_resilience": {
                "name": "Warrior's Resilience",
                "description": "Take 10% less damage from all sources.",
                "effects": {
                    "damage_reduction": 0.1
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get warrior skill nodes"""
        return [
            "warrior_root",
            "strength_1",
            "toughness_1", 
            "axe_mastery",
            "whirlwind"
        ]
    
    def on_level_up(self, player, level):
        """Handle warrior level up effects"""
        # Every 3 levels, increase max health
        if level % 3 == 0:
            health_bonus = 10
            player.max_health += health_bonus
            player.health += health_bonus


class Mage(CharacterClass):
    """Mage class focusing on ranged magical attacks"""
    
    def __init__(self):
        """Initialize the Mage class"""
        super().__init__(
            ClassType.MAGE,
            "Mage",
            "A master of arcane energy with powerful ranged attacks.",
            "mage_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 0.8
        self.stamina_modifier = 1.0
        self.speed_modifier = 1.0
        self.damage_modifier = 1.3
        
        # Starting abilities
        self.starting_abilities = ["magic_bolt"]
        
        # Class passives
        self.passives = {
            "mana_attunement": {
                "name": "Mana Attunement",
                "description": "Regenerate mana 20% faster.",
                "effects": {
                    "mana_regen_multiplier": 1.2
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get mage skill nodes"""
        return [
            "mage_root",
            "fireball",
            "arcane_intellect",
            "mana_shield",
            "fireball_specialization"
        ]
    
    def on_level_up(self, player, level):
        """Handle mage level up effects"""
        # Every 3 levels, increase spell damage
        if level % 3 == 0:
            if not hasattr(player, 'spell_damage_multiplier'):
                player.spell_damage_multiplier = 1.0
            player.spell_damage_multiplier += 0.05


class Cleric(CharacterClass):
    """Cleric class focusing on support and healing"""
    
    def __init__(self):
        """Initialize the Cleric class"""
        super().__init__(
            ClassType.CLERIC,
            "Cleric",
            "A holy warrior with healing abilities and divine powers.",
            "cleric_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 1.1
        self.stamina_modifier = 1.2
        self.speed_modifier = 0.95
        self.damage_modifier = 0.9
        
        # Starting abilities
        self.starting_abilities = ["mace_hit"]
        
        # Class passives
        self.passives = {
            "divine_blessing": {
                "name": "Divine Blessing",
                "description": "Healing effects are 15% more powerful.",
                "effects": {
                    "healing_multiplier": 1.15
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get cleric skill nodes"""
        return [
            "cleric_root",
            "healing_light",
            "divine_favor",
            "holy_strike",
            "consecration"
        ]
    
    def on_level_up(self, player, level):
        """Handle cleric level up effects"""
        # Every 3 levels, increase healing power
        if level % 3 == 0:
            if not hasattr(player, 'healing_multiplier'):
                player.healing_multiplier = 1.0
            player.healing_multiplier += 0.05


class Ranger(CharacterClass):
    """Ranger class focusing on long-range physical attacks and traps"""
    
    def __init__(self):
        """Initialize the Ranger class"""
        super().__init__(
            ClassType.RANGER,
            "Ranger",
            "A skilled marksman with traps and high mobility.",
            "ranger_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 0.9
        self.stamina_modifier = 1.2
        self.speed_modifier = 1.2
        self.damage_modifier = 1.1
        
        # Starting abilities
        self.starting_abilities = ["snipe_shot"]
        
        # Class passives
        self.passives = {
            "sharpshooter": {
                "name": "Sharpshooter",
                "description": "Increase critical strike chance by 10% and critical damage by 20%.",
                "effects": {
                    "crit_chance_bonus": 0.1,
                    "crit_damage_multiplier": 1.2
                }
            },
            "trap_master": {
                "name": "Trap Master",
                "description": "Traps placed by the Ranger deal 15% more damage and last 20% longer.",
                "effects": {
                    "trap_damage_multiplier": 1.15,
                    "trap_duration_multiplier": 1.2
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get ranger skill nodes"""
        return [
            "ranger_root",
            "precision_1",
            "trap_efficiency",
            "multi_shot",
            "snare_trap",
            "evasion_roll"
        ]
    
    def on_level_up(self, player, level):
        """Handle ranger level up effects"""
        # Every 3 levels, increase critical hit chance
        if level % 3 == 0:
            if not hasattr(player, 'crit_chance_bonus'):
                player.crit_chance_bonus = 0.0
            player.crit_chance_bonus += 0.02  # +2% crit chance every 3 levels


class Alchemist(CharacterClass):
    """Alchemist class focusing on potions, turrets and area control"""
    
    def __init__(self):
        """Initialize the Alchemist class"""
        super().__init__(
            ClassType.ALCHEMIST,
            "Alchemist",
            "A master of potions and mechanical turrets with area control.",
            "alchemist_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 0.95
        self.stamina_modifier = 1.0
        self.speed_modifier = 1.0
        self.damage_modifier = 1.0
        
        # Starting abilities
        self.starting_abilities = ["deploy_turret"]
        
        # Class passives
        self.passives = {
            "mixology": {
                "name": "Mixology",
                "description": "Potions and elixirs are 25% more effective and last 20% longer.",
                "effects": {
                    "potion_effectiveness_multiplier": 1.25,
                    "potion_duration_multiplier": 1.2
                }
            },
            "engineering_insight": {
                "name": "Engineering Insight",
                "description": "Turrets have 15% more health and deal 10% more damage.",
                "effects": {
                    "turret_health_multiplier": 1.15,
                    "turret_damage_multiplier": 1.1
                }
            },
            "resource_efficiency": {
                "name": "Resource Efficiency",
                "description": "20% chance to not consume resources when crafting items.",
                "effects": {
                    "crafting_resource_save_chance": 0.2
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get alchemist skill nodes"""
        return [
            "alchemist_root",
            "potion_mastery",
            "turret_specialization",
            "acid_flask",
            "healing_elixir",
            "flame_turret",
            "frost_turret"
        ]
    
    def on_level_up(self, player, level):
        """Handle alchemist level up effects"""
        # Every 3 levels, increase turret damage
        if level % 3 == 0:
            if not hasattr(player, 'turret_damage_multiplier'):
                player.turret_damage_multiplier = 1.0
            player.turret_damage_multiplier += 0.05  # +5% turret damage every 3 levels
        
        # Every 4 levels, increase potion duration
        if level % 4 == 0:
            if not hasattr(player, 'potion_duration_multiplier'):
                player.potion_duration_multiplier = 1.0
            player.potion_duration_multiplier += 0.1  # +10% potion duration every 4 levels


class Summoner(CharacterClass):
    """Summoner class focusing on calling minions to fight"""
    
    def __init__(self):
        """Initialize the Summoner class"""
        super().__init__(
            ClassType.SUMMONER,
            "Summoner",
            "A mystic who calls forth spirits and elementals to battle.",
            "summoner_icon.png"
        )
        
        # Stat modifiers
        self.health_modifier = 0.85
        self.stamina_modifier = 0.9
        self.speed_modifier = 0.95
        self.damage_modifier = 0.8  # Lower direct damage, relies on summons
        
        # Starting abilities
        self.starting_abilities = ["summon_spirit"]
        
        # Class passives
        self.passives = {
            "spiritual_bond": {
                "name": "Spiritual Bond",
                "description": "Summons have 20% more health and deal 15% more damage.",
                "effects": {
                    "summon_health_multiplier": 1.2,
                    "summon_damage_multiplier": 1.15
                }
            },
            "soul_harvest": {
                "name": "Soul Harvest",
                "description": "When your summons defeat an enemy, you recover 5% of your maximum health and mana.",
                "effects": {
                    "kill_health_restore_percent": 0.05,
                    "kill_mana_restore_percent": 0.05
                }
            },
            "conjurer's_focus": {
                "name": "Conjurer's Focus",
                "description": "Reduce the summoning cost of all minions by 15%.",
                "effects": {
                    "summon_cost_multiplier": 0.85
                }
            }
        }
    
    def get_available_skill_nodes(self):
        """Get summoner skill nodes"""
        return [
            "summoner_root",
            "spirit_mastery",
            "multiple_summons",
            "elemental_binding",
            "summon_fire_elemental",
            "summon_frost_elemental",
            "spirit_link"
        ]
    
    def on_level_up(self, player, level):
        """Handle summoner level up effects"""
        # Every 2 levels, increase maximum number of summons
        if level % 2 == 0:
            if not hasattr(player, 'max_summons'):
                player.max_summons = 1
            player.max_summons += 1
        
        # Every 3 levels, increase summon duration
        if level % 3 == 0:
            if not hasattr(player, 'summon_duration_multiplier'):
                player.summon_duration_multiplier = 1.0
            player.summon_duration_multiplier += 0.1  # +10% summon duration every 3 levels


class ClassManager:
    """Manages character classes and selection"""
    
    def __init__(self):
        """Initialize the class manager"""
        self.classes = {
            ClassType.WARRIOR: Warrior(),
            ClassType.MAGE: Mage(),
            ClassType.CLERIC: Cleric(),
            ClassType.RANGER: Ranger(),
            ClassType.ALCHEMIST: Alchemist(),
            ClassType.SUMMONER: Summoner()
        }
    
    def get_class(self, class_type):
        """
        Get a class by type
        
        Args:
            class_type (ClassType): Type of class to get
            
        Returns:
            CharacterClass or None: The class if found, None otherwise
        """
        return self.classes.get(class_type)
    
    def get_all_classes(self):
        """
        Get all available classes
        
        Returns:
            dict: Dictionary of all classes by type
        """
        return self.classes
    
    def apply_class(self, player, class_type):
        """
        Apply a class to a player
        
        Args:
            player: Player entity
            class_type (ClassType): Type of class to apply
            
        Returns:
            bool: True if class was applied successfully
        """
        character_class = self.get_class(class_type)
        if not character_class:
            return False
        
        # Set class on player
        player.character_class = class_type.value
        
        # Apply class bonuses
        character_class.apply_class_bonuses(player)
        
        # Add starting abilities
        if hasattr(player, 'ability_manager'):
            for ability in character_class.get_starting_abilities():
                player.ability_manager.add_ability(ability)
                player.ability_manager.unlock_ability(ability.ability_id)
        
        return True 