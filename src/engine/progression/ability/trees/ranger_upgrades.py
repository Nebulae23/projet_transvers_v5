# src/engine/progression/ability/trees/ranger_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- Sniping Upgrades ---

# Tier 1: Base Damage or Crit Chance
sniping_damage_1 = UpgradeNode(
    id="sniping_damage_1",
    name="Precision Shot I",
    description="Increases Sniping base damage by 10%.",
    cost=100,
    level_req=1,
    modifier={"damage_multiplier": 1.10}
)

sniping_crit_chance_1 = UpgradeNode(
    id="sniping_crit_chance_1",
    name="Keen Eye I",
    description="Increases Sniping critical hit chance by 5%.",
    cost=150,
    level_req=2, # Crit might be slightly higher req
    modifier={"crit_chance_bonus": 0.05} # Additive bonus
)

# Tier 2: Critical Damage or Armor Piercing
sniping_crit_damage = UpgradeNode(
    id="sniping_crit_damage",
    name="Vital Point Targeting",
    description="Increases Sniping critical hit damage multiplier by 25%.",
    cost=250,
    level_req=3,
    modifier={"crit_damage_multiplier_bonus": 0.25}, # Additive bonus to the multiplier
    prerequisites=["sniping_crit_chance_1"] # Requires Keen Eye
)

sniping_armor_pierce = UpgradeNode(
    id="sniping_armor_pierce",
    name="Armor Piercing Rounds",
    description="Sniping shots ignore 20% of enemy armor.",
    cost=300,
    level_req=4,
    modifier={"armor_penetration_percentage": 0.20},
    prerequisites=["sniping_damage_1"] # Requires base damage upgrade
)

# Tier 3: Guided Shots or Enhanced Crit/Piercing
sniping_guided = UpgradeNode(
    id="sniping_guided",
    name="Guided Shot",
    description="Sniping shots slightly curve towards the target.",
    cost=500,
    level_req=6,
    modifier={"homing_strength": 0.1}, # A value indicating how strongly it guides
    prerequisites=["sniping_crit_damage"] # Example path
)

sniping_enhanced_pierce = UpgradeNode(
    id="sniping_enhanced_pierce",
    name="Enhanced Armor Piercing",
    description="Sniping shots now ignore 40% of enemy armor.",
    cost=450,
    level_req=6,
    modifier={"armor_penetration_percentage": 0.40}, # Overwrites previous value
    prerequisites=["sniping_armor_pierce"] # Example path
)

sniping_crit_chance_2 = UpgradeNode(
    id="sniping_crit_chance_2",
    name="Keen Eye II",
    description="Further increases Sniping critical hit chance by 10%.",
    cost=400,
    level_req=5,
    modifier={"crit_chance_bonus": 0.10}, # Stacks or replaces based on design
    prerequisites=["sniping_crit_chance_1"]
)


# --- Ranger Ability Tree Definition ---
ranger_ability_tree = UpgradeTree(
    ability_id="Sniping",
    nodes={
        sniping_damage_1.id: sniping_damage_1,
        sniping_crit_chance_1.id: sniping_crit_chance_1,
        sniping_crit_damage.id: sniping_crit_damage,
        sniping_armor_pierce.id: sniping_armor_pierce,
        sniping_guided.id: sniping_guided,
        sniping_enhanced_pierce.id: sniping_enhanced_pierce,
        sniping_crit_chance_2.id: sniping_crit_chance_2,
    }
)

# Export or register the tree
UPGRADE_TREES = {
    "Sniping": ranger_ability_tree
}

def get_ranger_upgrade_trees():
    """Returns all defined upgrade trees for the Ranger class."""
    return UPGRADE_TREES