#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skill Definitions for Nightfall Defenders
Contains definitions for all skills in the skill tree
"""

from .skill_tree import SkillType

# Dictionary of all skills in the game
SKILLS = {
    # ========== Warrior Skills ==========
    "warrior_root": {
        "id": "warrior_root",
        "name": "Path of the Warrior",
        "description": "Begin your journey as a Warrior, specializing in close combat and high survivability.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "warrior_base"},
        "position": (0, 0),
        "icon": "warrior_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "warrior"
    },
    
    "strength_1": {
        "id": "strength_1",
        "name": "Strength I",
        "description": "Increase your damage by 10%.",
        "type": SkillType.STAT_BOOST,
        "effects": {"damage_multiplier": 0.1},
        "position": (0, 5),
        "icon": "strength_icon.png",
        "cost": {"monster_essence": 15},
        "required_class": "warrior"
    },
    
    "toughness_1": {
        "id": "toughness_1",
        "name": "Toughness I",
        "description": "Increase your maximum health by 15.",
        "type": SkillType.STAT_BOOST,
        "effects": {"max_health": 15},
        "position": (-4, 5),
        "icon": "toughness_icon.png",
        "cost": {"monster_essence": 15},
        "required_class": "warrior"
    },
    
    "whirlwind": {
        "id": "whirlwind",
        "name": "Whirlwind",
        "description": "Unlock the Whirlwind ability, striking all enemies around you.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "whirlwind"},
        "position": (0, 10),
        "icon": "whirlwind_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "warrior"
    },
    
    "axe_mastery": {
        "id": "axe_mastery",
        "name": "Axe Mastery",
        "description": "Enhance your Axe Slash ability, increasing damage by 20% and reducing cooldown by 10%.",
        "type": SkillType.ABILITY_MODIFIER,
        "effects": {
            "ability_id": "axe_slash",
            "modifiers": {
                "damage_multiplier": 1.2,
                "cooldown_multiplier": 0.9
            }
        },
        "position": (4, 5),
        "icon": "axe_mastery_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "warrior"
    },
    
    # ========== Mage Skills ==========
    "mage_root": {
        "id": "mage_root",
        "name": "Path of the Mage",
        "description": "Begin your journey as a Mage, wielding elemental magic from a distance.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "mage_base"},
        "position": (15, 0),
        "icon": "mage_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "mage"
    },
    
    "fireball": {
        "id": "fireball",
        "name": "Fireball",
        "description": "Unlock the Fireball ability, throwing a ball of fire that explodes on impact.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "fireball"},
        "position": (15, 5),
        "icon": "fireball_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "mage"
    },
    
    "arcane_intellect": {
        "id": "arcane_intellect",
        "name": "Arcane Intellect",
        "description": "Increase the damage of all magical abilities by 15%.",
        "type": SkillType.STAT_BOOST,
        "effects": {"spell_damage_multiplier": 0.15},
        "position": (11, 5),
        "icon": "intellect_icon.png",
        "cost": {"monster_essence": 15},
        "required_class": "mage"
    },
    
    "mana_shield": {
        "id": "mana_shield",
        "name": "Mana Shield",
        "description": "Unlock the Mana Shield ability, absorbing damage at the cost of mana.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "mana_shield"},
        "position": (19, 5),
        "icon": "mana_shield_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "mage"
    },
    
    "fireball_specialization": {
        "id": "fireball_specialization",
        "name": "Fireball Specialization",
        "description": "Choose how to enhance your Fireball ability.",
        "type": SkillType.SPECIALIZATION,
        "effects": {"specialization_path": "fireball"},
        "position": (15, 10),
        "icon": "fireball_spec_icon.png",
        "cost": {"monster_essence": 30, "fire_essence": 5},
        "required_class": "mage"
    },
    
    # ========== Cleric Skills ==========
    "cleric_root": {
        "id": "cleric_root",
        "name": "Path of the Cleric",
        "description": "Begin your journey as a Cleric, providing healing and support.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "cleric_base"},
        "position": (30, 0),
        "icon": "cleric_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "cleric"
    },
    
    "healing_light": {
        "id": "healing_light",
        "name": "Healing Light",
        "description": "Unlock the Healing Light ability, restoring health to yourself and nearby allies.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "healing_light"},
        "position": (30, 5),
        "icon": "healing_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "cleric"
    },
    
    "divine_favor": {
        "id": "divine_favor",
        "name": "Divine Favor",
        "description": "Increase the effectiveness of healing abilities by 20%.",
        "type": SkillType.STAT_BOOST,
        "effects": {"healing_multiplier": 0.2},
        "position": (26, 5),
        "icon": "divine_favor_icon.png",
        "cost": {"monster_essence": 15},
        "required_class": "cleric"
    },
    
    "holy_strike": {
        "id": "holy_strike",
        "name": "Holy Strike",
        "description": "Enhance your Mace Hit ability with holy energy, dealing bonus damage to undead enemies.",
        "type": SkillType.ABILITY_MODIFIER,
        "effects": {
            "ability_id": "mace_hit",
            "modifiers": {
                "damage_multiplier": 1.1,
                "undead_damage_multiplier": 1.5
            }
        },
        "position": (34, 5),
        "icon": "holy_strike_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "cleric"
    },
    
    "consecration": {
        "id": "consecration",
        "name": "Consecration",
        "description": "Unlock the Consecration ability, creating a circle of holy energy that damages enemies and heals allies.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "consecration"},
        "position": (30, 10),
        "icon": "consecration_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "cleric"
    },
    
    # ========== Ranger Skills ==========
    "ranger_root": {
        "id": "ranger_root",
        "name": "Path of the Ranger",
        "description": "Begin your journey as a Ranger, specializing in precision attacks and traps.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "ranger_base"},
        "position": (45, 0),
        "icon": "ranger_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "ranger"
    },
    
    "precision_1": {
        "id": "precision_1",
        "name": "Precision I",
        "description": "Increase critical strike chance by 10%.",
        "type": SkillType.STAT_BOOST,
        "effects": {"crit_chance_bonus": 0.1},
        "position": (45, 5),
        "icon": "precision_icon.png",
        "cost": {"monster_essence": 15},
        "required_class": "ranger"
    },
    
    "trap_efficiency": {
        "id": "trap_efficiency",
        "name": "Trap Efficiency",
        "description": "Traps cost 25% less stamina to deploy and last 20% longer.",
        "type": SkillType.STAT_BOOST,
        "effects": {
            "trap_cost_multiplier": 0.75,
            "trap_duration_multiplier": 1.2
        },
        "position": (41, 5),
        "icon": "trap_efficiency_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "ranger"
    },
    
    "multi_shot": {
        "id": "multi_shot",
        "name": "Multi Shot",
        "description": "Unlock the Multi Shot ability, firing three arrows in a spread pattern.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "multi_shot"},
        "position": (49, 5),
        "icon": "multi_shot_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "ranger"
    },
    
    "snare_trap": {
        "id": "snare_trap",
        "name": "Snare Trap",
        "description": "Unlock the Snare Trap ability, placing a trap that slows enemies who step on it.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "snare_trap"},
        "position": (41, 10),
        "icon": "snare_trap_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "ranger"
    },
    
    "evasion_roll": {
        "id": "evasion_roll",
        "name": "Evasion Roll",
        "description": "Unlock the Evasion Roll ability, quickly dodging in any direction.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "evasion_roll"},
        "position": (49, 10),
        "icon": "evasion_roll_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "ranger"
    },
    
    # ========== Fusion Skills ==========
    "elemental_fusion": {
        "id": "elemental_fusion",
        "name": "Elemental Fusion",
        "description": "Unlock the ability to combine elemental abilities into powerful hybrid spells.",
        "type": SkillType.FUSION,
        "effects": {"fusion_type": "elemental"},
        "position": (15, 15),
        "icon": "fusion_icon.png",
        "cost": {"monster_essence": 40, "magical_essence": 10},
        "required_class": "mage"
    },
    
    "divine_weapon": {
        "id": "divine_weapon",
        "name": "Divine Weapon",
        "description": "Unlock the ability to infuse weapons with holy energy.",
        "type": SkillType.FUSION,
        "effects": {"fusion_type": "divine_weapon"},
        "position": (30, 15),
        "icon": "divine_weapon_icon.png",
        "cost": {"monster_essence": 40, "holy_essence": 10},
        "required_class": "cleric"
    },
    
    # ========== Alchemist Skills ==========
    "alchemist_root": {
        "id": "alchemist_root",
        "name": "Path of the Alchemist",
        "description": "Begin your journey as an Alchemist, creating potions and deploying turrets.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "alchemist_base"},
        "position": (60, 0),
        "icon": "alchemist_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "alchemist"
    },
    
    "potion_mastery": {
        "id": "potion_mastery",
        "name": "Potion Mastery",
        "description": "Potions are 20% more effective and have 15% larger area of effect.",
        "type": SkillType.STAT_BOOST,
        "effects": {
            "potion_effectiveness_multiplier": 1.2,
            "potion_aoe_multiplier": 1.15
        },
        "position": (56, 5),
        "icon": "potion_mastery_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "alchemist"
    },
    
    "turret_specialization": {
        "id": "turret_specialization",
        "name": "Turret Specialization",
        "description": "Turrets have 25% more health and deal 15% more damage.",
        "type": SkillType.STAT_BOOST,
        "effects": {
            "turret_health_multiplier": 1.25,
            "turret_damage_multiplier": 1.15
        },
        "position": (64, 5),
        "icon": "turret_spec_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "alchemist"
    },
    
    "acid_flask": {
        "id": "acid_flask",
        "name": "Acid Flask",
        "description": "Unlock the Acid Flask ability, throwing a potion that creates a damaging pool.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "acid_flask"},
        "position": (56, 10),
        "icon": "acid_flask_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "alchemist"
    },
    
    "healing_elixir": {
        "id": "healing_elixir",
        "name": "Healing Elixir",
        "description": "Unlock the Healing Elixir ability, creating a potion that restores health.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "healing_elixir"},
        "position": (60, 10),
        "icon": "healing_elixir_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "alchemist"
    },
    
    "flame_turret": {
        "id": "flame_turret",
        "name": "Flame Turret",
        "description": "Unlock the Flame Turret ability, deploying a turret that shoots fire projectiles.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "flame_turret"},
        "position": (64, 10),
        "icon": "flame_turret_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "alchemist"
    },
    
    # ========== Summoner Skills ==========
    "summoner_root": {
        "id": "summoner_root",
        "name": "Path of the Summoner",
        "description": "Begin your journey as a Summoner, calling forth spirits to fight on your behalf.",
        "type": SkillType.PASSIVE,
        "effects": {"passive_id": "summoner_base"},
        "position": (75, 0),
        "icon": "summoner_icon.png",
        "cost": {"monster_essence": 0},  # Free root node
        "required_class": "summoner"
    },
    
    "spirit_mastery": {
        "id": "spirit_mastery",
        "name": "Spirit Mastery",
        "description": "Summoned spirits deal 20% more damage and have 15% more health.",
        "type": SkillType.STAT_BOOST,
        "effects": {
            "summon_damage_multiplier": 1.2,
            "summon_health_multiplier": 1.15
        },
        "position": (71, 5),
        "icon": "spirit_mastery_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "summoner"
    },
    
    "multiple_summons": {
        "id": "multiple_summons",
        "name": "Multiple Summons",
        "description": "Increase the maximum number of active summons by 1.",
        "type": SkillType.STAT_BOOST,
        "effects": {"max_summons_bonus": 1},
        "position": (75, 5),
        "icon": "multiple_summons_icon.png",
        "cost": {"monster_essence": 25},
        "required_class": "summoner"
    },
    
    "elemental_binding": {
        "id": "elemental_binding",
        "name": "Elemental Binding",
        "description": "Unlocks the ability to summon elemental spirits.",
        "type": SkillType.PASSIVE,
        "effects": {"elemental_summon_unlock": True},
        "position": (79, 5),
        "icon": "elemental_binding_icon.png",
        "cost": {"monster_essence": 20},
        "required_class": "summoner"
    },
    
    "summon_fire_elemental": {
        "id": "summon_fire_elemental",
        "name": "Summon Fire Elemental",
        "description": "Unlock the ability to summon a fire elemental that deals fire damage to enemies.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "summon_fire_elemental"},
        "position": (71, 10),
        "icon": "fire_elemental_icon.png",
        "cost": {"monster_essence": 25, "fire_essence": 5},
        "required_class": "summoner",
        "required_nodes": ["elemental_binding"]
    },
    
    "summon_frost_elemental": {
        "id": "summon_frost_elemental",
        "name": "Summon Frost Elemental",
        "description": "Unlock the ability to summon a frost elemental that slows and damages enemies.",
        "type": SkillType.ABILITY_UNLOCK,
        "effects": {"ability_id": "summon_frost_elemental"},
        "position": (79, 10),
        "icon": "frost_elemental_icon.png",
        "cost": {"monster_essence": 25, "frost_essence": 5},
        "required_class": "summoner",
        "required_nodes": ["elemental_binding"]
    },
    
    "spirit_link": {
        "id": "spirit_link",
        "name": "Spirit Link",
        "description": "When your summons deal damage, you recover health equal to 5% of the damage dealt.",
        "type": SkillType.PASSIVE,
        "effects": {"summon_damage_heal_percent": 0.05},
        "position": (75, 15),
        "icon": "spirit_link_icon.png",
        "cost": {"monster_essence": 30},
        "required_class": "summoner"
    }
}

# Connection data (parent -> child relationships)
SKILL_CONNECTIONS = [
    # Warrior connections
    {"parent": "warrior_root", "child": "strength_1"},
    {"parent": "warrior_root", "child": "toughness_1"},
    {"parent": "warrior_root", "child": "axe_mastery"},
    {"parent": "strength_1", "child": "whirlwind"},
    
    # Mage connections
    {"parent": "mage_root", "child": "fireball"},
    {"parent": "mage_root", "child": "arcane_intellect"},
    {"parent": "mage_root", "child": "mana_shield"},
    {"parent": "fireball", "child": "fireball_specialization"},
    {"parent": "fireball_specialization", "child": "elemental_fusion"},
    
    # Cleric connections
    {"parent": "cleric_root", "child": "healing_light"},
    {"parent": "cleric_root", "child": "divine_favor"},
    {"parent": "cleric_root", "child": "holy_strike"},
    {"parent": "healing_light", "child": "consecration"},
    {"parent": "consecration", "child": "divine_weapon"},
    
    # Ranger connections
    {"parent": "ranger_root", "child": "precision_1"},
    {"parent": "ranger_root", "child": "trap_efficiency"},
    {"parent": "ranger_root", "child": "multi_shot"},
    {"parent": "ranger_root", "child": "snare_trap"},
    {"parent": "ranger_root", "child": "evasion_roll"},
    
    # Alchemist connections
    {"parent": "alchemist_root", "child": "potion_mastery"},
    {"parent": "alchemist_root", "child": "turret_specialization"},
    {"parent": "alchemist_root", "child": "acid_flask"},
    {"parent": "alchemist_root", "child": "healing_elixir"},
    {"parent": "alchemist_root", "child": "flame_turret"},
    
    # Summoner connections
    {"parent": "summoner_root", "child": "spirit_mastery"},
    {"parent": "summoner_root", "child": "multiple_summons"},
    {"parent": "summoner_root", "child": "elemental_binding"},
    {"parent": "spirit_mastery", "child": "summon_fire_elemental"},
    {"parent": "spirit_mastery", "child": "summon_frost_elemental"},
    {"parent": "spirit_mastery", "child": "spirit_link"}
]

class SkillDefinitions:
    """Class for creating and managing skill definitions"""
    
    def __init__(self):
        """Initialize with default templates"""
        pass
    
    def create_skill_tree_template(self):
        """Create a template for initializing the skill tree"""
        # Create the template structure
        template = {
            "warrior": {
                "root": "warrior_root",
                "skills": [
                    "warrior_root",
                    "strength_1",
                    "toughness_1",
                    "whirlwind",
                    "axe_mastery"
                ],
                "connections": [
                    ("warrior_root", "strength_1"),
                    ("warrior_root", "toughness_1"),
                    ("warrior_root", "axe_mastery"),
                    ("strength_1", "whirlwind")
                ]
            },
            "mage": {
                "root": "mage_root",
                "skills": [
                    "mage_root",
                    "fireball",
                    "arcane_intellect",
                    "mana_shield",
                    "fireball_specialization"
                ],
                "connections": [
                    ("mage_root", "fireball"),
                    ("mage_root", "arcane_intellect"),
                    ("mage_root", "mana_shield"),
                    ("fireball", "fireball_specialization")
                ]
            },
            "cleric": {
                "root": "cleric_root",
                "skills": [
                    "cleric_root",
                    "healing_light",
                    "divine_favor",
                    "holy_strike",
                    "consecration"
                ],
                "connections": [
                    ("cleric_root", "healing_light"),
                    ("cleric_root", "divine_favor"),
                    ("cleric_root", "holy_strike"),
                    ("healing_light", "consecration")
                ]
            },
            "ranger": {
                "root": "ranger_root",
                "skills": [
                    "ranger_root",
                    "precision_1",
                    "trap_efficiency",
                    "multi_shot"
                ],
                "connections": [
                    ("ranger_root", "precision_1"),
                    ("ranger_root", "trap_efficiency"),
                    ("precision_1", "multi_shot")
                ]
            }
        }
        
        return template
    
    def _create_offensive_skills(self):
        """Create offensive skill branch"""
        # To be implemented
        pass
    
    def _create_defensive_skills(self):
        """Create defensive skill branch"""
        # To be implemented
        pass
    
    def _create_utility_skills(self):
        """Create utility skill branch"""
        # To be implemented
        pass
    
    def _create_class_skills(self):
        """Create class-specific skills"""
        # To be implemented
        pass
    
    def _create_fusion_skills(self):
        """Create multi-class fusion skills"""
        # To be implemented
        pass
    
    def _create_harmonization_skills(self):
        """Create late-game harmonization skills"""
        # To be implemented
        pass

# Create a function at the module level to create a skill tree template
def create_skill_tree_template():
    """Create a template for initializing the skill tree"""
    skill_defs = SkillDefinitions()
    return skill_defs.create_skill_tree_template()

# Warrior abilities
WARRIOR_ABILITIES = {
    "primary": {
        "name": "Axe Slash",
        "description": "A powerful slash with an axe that deals damage in a wide arc",
        "damage": 25,
        "cooldown": 1.0,
        "range": 2.5,
        "type": "melee",
        "trajectory": "arc",
        "effects": ["knockback_small"]
    },
    "secondary": {
        "ground_slam": {
            "name": "Ground Slam",
            "description": "Slam your weapon into the ground, creating a shockwave that damages and stuns enemies",
            "damage": 30,
            "cooldown": 8.0,
            "range": 5.0,
            "type": "aoe",
            "trajectory": "radial",
            "effects": ["stun_short", "knockback_medium"]
        },
        "battle_cry": {
            "name": "Battle Cry",
            "description": "Release a powerful shout that intimidates enemies, reducing their damage",
            "damage": 0,
            "cooldown": 15.0,
            "range": 8.0,
            "type": "buff",
            "trajectory": "radial",
            "effects": ["enemy_damage_reduction", "enemy_psychology_fear"]
        },
        "whirlwind": {
            "name": "Whirlwind",
            "description": "Spin rapidly, dealing damage to all surrounding enemies",
            "damage": 20,
            "cooldown": 12.0,
            "range": 3.5,
            "type": "aoe",
            "trajectory": "circular",
            "effects": ["movement_speed_buff", "damage_over_time"]
        },
        "defensive_stance": {
            "name": "Defensive Stance",
            "description": "Adopt a defensive posture, significantly reducing incoming damage",
            "damage": 0,
            "cooldown": 20.0,
            "range": 0,
            "type": "buff",
            "trajectory": "self",
            "effects": ["damage_reduction_large", "movement_speed_penalty", "taunt"]
        }
    }
}

# Mage abilities
MAGE_ABILITIES = {
    "primary": {
        "name": "Magic Bolt",
        "description": "A bolt of arcane energy that deals damage to a single target",
        "damage": 20,
        "cooldown": 0.75,
        "range": 12.0,
        "type": "projectile",
        "trajectory": "straight",
        "effects": ["magic_damage"]
    },
    "secondary": {
        "fireball": {
            "name": "Fireball",
            "description": "Launch a ball of fire that explodes on impact, dealing area damage",
            "damage": 35,
            "cooldown": 6.0,
            "range": 10.0,
            "type": "projectile",
            "trajectory": "arcing",
            "effects": ["fire_damage", "burn_dot", "aoe_explosion"]
        },
        "frost_nova": {
            "name": "Frost Nova",
            "description": "Release a wave of freezing energy that slows enemies and deals damage",
            "damage": 25,
            "cooldown": 9.0,
            "range": 6.0,
            "type": "aoe",
            "trajectory": "radial",
            "effects": ["ice_damage", "slow_movement", "slow_attack"]
        },
        "arcane_shield": {
            "name": "Arcane Shield",
            "description": "Create a shield of arcane energy that blocks incoming damage",
            "damage": 0,
            "cooldown": 12.0,
            "range": 0,
            "type": "buff",
            "trajectory": "self",
            "effects": ["damage_absorption", "reflect_projectiles"]
        },
        "lightning_chain": {
            "name": "Lightning Chain",
            "description": "Call down a bolt of lightning that jumps between nearby enemies",
            "damage": 30,
            "cooldown": 10.0,
            "range": 14.0,
            "type": "projectile",
            "trajectory": "chain",
            "effects": ["lightning_damage", "stun_short", "chain_reduction"]
        }
    }
}

# Cleric abilities
CLERIC_ABILITIES = {
    "primary": {
        "name": "Mace Hit",
        "description": "A powerful strike with a mace that deals damage to a single target",
        "damage": 18,
        "cooldown": 1.2,
        "range": 2.0,
        "type": "melee",
        "trajectory": "direct",
        "effects": ["holy_damage"]
    },
    "secondary": {
        "healing_circle": {
            "name": "Healing Circle",
            "description": "Create a circle of healing energy that restores health to allies within it",
            "damage": 0,
            "cooldown": 15.0,
            "range": 5.0,
            "type": "heal",
            "trajectory": "circular",
            "effects": ["heal_over_time", "buff_regeneration"]
        },
        "divine_smite": {
            "name": "Divine Smite",
            "description": "Call down a beam of holy light that deals heavy damage to undead and corrupted enemies",
            "damage": 40,
            "cooldown": 8.0,
            "range": 8.0,
            "type": "projectile",
            "trajectory": "direct",
            "effects": ["holy_damage", "bonus_vs_undead", "light_aura"]
        },
        "protective_blessing": {
            "name": "Protective Blessing",
            "description": "Bless an ally, reducing damage taken and providing immunity to negative effects",
            "damage": 0,
            "cooldown": 20.0,
            "range": 10.0,
            "type": "buff",
            "trajectory": "target",
            "effects": ["damage_reduction", "status_immunity", "small_heal"]
        },
        "holy_nova": {
            "name": "Holy Nova",
            "description": "Release a wave of holy energy that damages enemies and heals allies",
            "damage": 25,
            "cooldown": 12.0,
            "range": 7.0,
            "type": "aoe",
            "trajectory": "radial",
            "effects": ["holy_damage", "heal_allies", "repel_undead"]
        }
    }
}

# Alchemist abilities
ALCHEMIST_ABILITIES = {
    "primary": {
        "name": "Deploy Turret",
        "description": "Deploy an alchemical turret that fires at nearby enemies",
        "damage": 10,
        "cooldown": 2.0,
        "range": 5.0,
        "type": "summon",
        "trajectory": "place",
        "effects": ["turret_summon"]
    },
    "secondary": {
        "acid_bomb": {
            "name": "Acid Bomb",
            "description": "Throw a vial of corrosive acid that deals damage over time and reduces armor",
            "damage": 15,
            "cooldown": 7.0,
            "range": 9.0,
            "type": "projectile",
            "trajectory": "arcing",
            "effects": ["acid_damage", "armor_reduction", "dot_damage"]
        },
        "smoke_screen": {
            "name": "Smoke Screen",
            "description": "Create a cloud of smoke that obscures vision and causes enemies to miss",
            "damage": 0,
            "cooldown": 12.0,
            "range": 8.0,
            "type": "aoe",
            "trajectory": "place",
            "effects": ["vision_reduction", "miss_chance", "slow_movement"]
        },
        "healing_potion": {
            "name": "Healing Potion",
            "description": "Throw a healing potion that restores health to allies in the area",
            "damage": 0,
            "cooldown": 15.0,
            "range": 7.0,
            "type": "heal",
            "trajectory": "arcing",
            "effects": ["instant_heal", "regeneration_buff"]
        },
        "transmutation": {
            "name": "Transmutation",
            "description": "Temporarily transform an enemy into a harmless creature",
            "damage": 0,
            "cooldown": 25.0,
            "range": 6.0,
            "type": "control",
            "trajectory": "direct",
            "effects": ["polymorph", "disable", "damage_vulnerability"]
        }
    }
}

# Ranger abilities
RANGER_ABILITIES = {
    "primary": {
        "name": "Precision Shot",
        "description": "A carefully aimed shot that deals high damage to a single target",
        "damage": 30,
        "cooldown": 1.5,
        "range": 15.0,
        "type": "projectile",
        "trajectory": "straight",
        "effects": ["critical_chance", "penetration"]
    },
    "secondary": {
        "multishot": {
            "name": "Multishot",
            "description": "Fire multiple arrows simultaneously in a spread pattern",
            "damage": 15,
            "cooldown": 8.0,
            "range": 12.0,
            "type": "projectile",
            "trajectory": "spread",
            "effects": ["multiple_projectiles", "reduced_accuracy"]
        },
        "trap": {
            "name": "Snare Trap",
            "description": "Place a trap that immobilizes enemies that step on it",
            "damage": 10,
            "cooldown": 10.0,
            "range": 6.0,
            "type": "trap",
            "trajectory": "place",
            "effects": ["root", "reveal", "dot_damage"]
        },
        "camouflage": {
            "name": "Camouflage",
            "description": "Blend into the environment, becoming invisible to enemies",
            "damage": 0,
            "cooldown": 20.0,
            "range": 0,
            "type": "buff",
            "trajectory": "self",
            "effects": ["invisibility", "movement_speed", "damage_bonus_first_hit"]
        },
        "poison_arrow": {
            "name": "Poison Arrow",
            "description": "Fire an arrow coated with potent toxins that deal damage over time",
            "damage": 20,
            "cooldown": 12.0,
            "range": 14.0,
            "type": "projectile",
            "trajectory": "straight",
            "effects": ["poison_damage", "slow", "healing_reduction"]
        }
    }
}

# Summoner abilities
SUMMONER_ABILITIES = {
    "primary": {
        "name": "Spirit Summon",
        "description": "Summon a spirit ally that attacks nearby enemies",
        "damage": 15,
        "cooldown": 2.5,
        "range": 8.0,
        "type": "summon",
        "trajectory": "place",
        "effects": ["spirit_summon"]
    },
    "secondary": {
        "elemental_guardian": {
            "name": "Elemental Guardian",
            "description": "Summon a powerful elemental guardian that protects you and attacks enemies",
            "damage": 25,
            "cooldown": 30.0,
            "range": 3.0,
            "type": "summon",
            "trajectory": "place",
            "effects": ["guardian_summon", "element_adaptive", "taunt_enemies"]
        },
        "soul_link": {
            "name": "Soul Link",
            "description": "Create a link with your summons, healing them and boosting their damage",
            "damage": 0,
            "cooldown": 15.0,
            "range": 12.0,
            "type": "buff",
            "trajectory": "target",
            "effects": ["summon_heal", "summon_damage_boost", "summon_speed_boost"]
        },
        "spirit_swarm": {
            "name": "Spirit Swarm",
            "description": "Summon a swarm of small spirits that surround and damage nearby enemies",
            "damage": 5,
            "cooldown": 12.0,
            "range": 10.0,
            "type": "aoe",
            "trajectory": "circular",
            "effects": ["multiple_summons", "damage_over_time", "slow_enemies"]
        },
        "sacrificial_pact": {
            "name": "Sacrificial Pact",
            "description": "Sacrifice a summon to create a powerful explosion, healing you in the process",
            "damage": 40,
            "cooldown": 20.0,
            "range": 8.0,
            "type": "special",
            "trajectory": "target_summon",
            "effects": ["sacrifice_summon", "aoe_damage", "self_heal"]
        }
    }
}

# Create a dictionary of all classes and their abilities for easy access
CLASS_ABILITIES = {
    "warrior": WARRIOR_ABILITIES,
    "mage": MAGE_ABILITIES,
    "cleric": CLERIC_ABILITIES,
    "alchemist": ALCHEMIST_ABILITIES,
    "ranger": RANGER_ABILITIES,
    "summoner": SUMMONER_ABILITIES
} 