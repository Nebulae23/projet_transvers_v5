# src/engine/progression/ability/trees/summoner_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- SpiritSummon Upgrades ---

# Tier 1: Base Improvement (e.g., Spirit Duration or Health)
spirit_duration_1 = UpgradeNode(
    id="spirit_duration_1",
    name="Lingering Essence I",
    description="Increases the duration summoned spirits remain active by 20%.",
    cost=100,
    level_req=1,
    modifier={"summon_duration_multiplier": 1.20}
)

spirit_health_1 = UpgradeNode(
    id="spirit_health_1",
    name="Resilient Spirits I",
    description="Increases the health of summoned spirits by 15%.",
    cost=120,
    level_req=1,
    modifier={"summon_health_multiplier": 1.15}
)

# Tier 2: Multiple Spirits or Increased Strength
spirit_count_2 = UpgradeNode(
    id="spirit_count_2",
    name="Twin Souls",
    description="Allows summoning a second spirit simultaneously.",
    cost=300,
    level_req=3,
    modifier={"max_summons": 2}, # Assuming base is 1
    prerequisites=["spirit_duration_1"] # Example prerequisite
)

spirit_strength_1 = UpgradeNode(
    id="spirit_strength_1",
    name="Empowered Spirits I",
    description="Increases the damage dealt by summoned spirits by 20%.",
    cost=250,
    level_req=3,
    modifier={"summon_damage_multiplier": 1.20},
    prerequisites=["spirit_health_1"] # Example prerequisite
)

# Tier 3: Enhanced Strength/Duration or More Spirits
spirit_strength_2 = UpgradeNode(
    id="spirit_strength_2",
    name="Empowered Spirits II",
    description="Further increases the damage dealt by summoned spirits by 25%.",
    cost=450,
    level_req=5,
    modifier={"summon_damage_multiplier": 1.25}, # Stacks or replaces
    prerequisites=["spirit_strength_1"] # Example path
)

spirit_duration_2 = UpgradeNode(
    id="spirit_duration_2",
    name="Lingering Essence II",
    description="Further increases the duration summoned spirits remain active by 30%.",
    cost=400,
    level_req=5,
    modifier={"summon_duration_multiplier": 1.30}, # Stacks or replaces
    prerequisites=["spirit_duration_1"] # Example path
)

spirit_count_3 = UpgradeNode(
    id="spirit_count_3",
    name="Spirit Horde",
    description="Allows summoning a third spirit simultaneously.",
    cost=600,
    level_req=6,
    modifier={"max_summons": 3}, # Replaces previous count
    prerequisites=["spirit_count_2"] # Example path
)


# --- Summoner Ability Tree Definition ---
summoner_ability_tree = UpgradeTree(
    ability_id="SpiritSummon",
    nodes={
        spirit_duration_1.id: spirit_duration_1,
        spirit_health_1.id: spirit_health_1,
        spirit_count_2.id: spirit_count_2,
        spirit_strength_1.id: spirit_strength_1,
        spirit_strength_2.id: spirit_strength_2,
        spirit_duration_2.id: spirit_duration_2,
        spirit_count_3.id: spirit_count_3,
    }
)

# Export or register the tree
UPGRADE_TREES = {
    "SpiritSummon": summoner_ability_tree
}

def get_summoner_upgrade_trees():
    """Returns all defined upgrade trees for the Summoner class."""
    return UPGRADE_TREES