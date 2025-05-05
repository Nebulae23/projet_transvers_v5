# src/engine/progression/ability/trees/alchemist_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- Turret Upgrades ---

# Tier 1: Base Improvement (e.g., Duration or Health)
turret_duration_1 = UpgradeNode(
    id="turret_duration_1",
    name="Extended Deployment I",
    description="Increases the duration turrets stay active by 20%.",
    cost=100,
    level_req=1,
    modifier={"duration_multiplier": 1.20}
)

# Tier 2: Increased Fire Rate or First Additional Turret
turret_fire_rate_1 = UpgradeNode(
    id="turret_fire_rate_1",
    name="Rapid Fire I",
    description="Increases turret fire rate by 15%.",
    cost=200,
    level_req=3,
    modifier={"fire_rate_multiplier": 1.15},
    prerequisites=["turret_duration_1"]
)

turret_count_2 = UpgradeNode(
    id="turret_count_2",
    name="Additional Unit",
    description="Allows deployment of a second turret simultaneously.",
    cost=300,
    level_req=4, # Maybe slightly higher level for a second unit
    modifier={"max_turrets": 2}, # Assuming base is 1
    prerequisites=["turret_duration_1"]
)

# Tier 3: Status Effects, Further Fire Rate/Count
turret_status_poison = UpgradeNode(
    id="turret_status_poison",
    name="Poison Rounds",
    description="Turret attacks now have a chance to apply poison.",
    cost=400,
    level_req=5,
    modifier={"status_effect_on_hit": {"type": "poison", "chance": 0.20, "duration": 3.0, "dps": 5}},
    prerequisites=["turret_fire_rate_1"] # Example path
)

turret_fire_rate_2 = UpgradeNode(
    id="turret_fire_rate_2",
    name="Rapid Fire II",
    description="Further increases turret fire rate by 20%.",
    cost=350,
    level_req=5,
    modifier={"fire_rate_multiplier": 1.20}, # Stacks or replaces based on design
    prerequisites=["turret_fire_rate_1"] # Example path
)

turret_count_3 = UpgradeNode(
    id="turret_count_3",
    name="Reinforced Deployment",
    description="Allows deployment of a third turret simultaneously.",
    cost=550,
    level_req=6, # Higher level for third unit
    modifier={"max_turrets": 3}, # Replaces previous count
    prerequisites=["turret_count_2"] # Example path
)


# --- Alchemist Ability Tree Definition ---
alchemist_ability_tree = UpgradeTree(
    ability_id="Turret",
    nodes={
        turret_duration_1.id: turret_duration_1,
        turret_fire_rate_1.id: turret_fire_rate_1,
        turret_count_2.id: turret_count_2,
        turret_status_poison.id: turret_status_poison,
        turret_fire_rate_2.id: turret_fire_rate_2,
        turret_count_3.id: turret_count_3,
    }
)

# Export or register the tree
UPGRADE_TREES = {
    "Turret": alchemist_ability_tree
}

def get_alchemist_upgrade_trees():
    """Returns all defined upgrade trees for the Alchemist class."""
    return UPGRADE_TREES