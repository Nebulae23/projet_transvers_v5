# src/engine/progression/ability/trees/warrior_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- AxeSlash Upgrades ---

# Tier 1: Damage Increase
axe_slash_damage_1 = UpgradeNode(
    id="axe_slash_damage_1",
    name="Increased Damage I",
    description="Increases AxeSlash damage by 10%.",
    cost=100,
    level_req=1,
    modifier={"damage_multiplier": 1.10}
)

# Tier 2: Wider Arc or More Damage
axe_slash_arc = UpgradeNode(
    id="axe_slash_arc",
    name="Wider Arc",
    description="Increases the area of effect of AxeSlash.",
    cost=200,
    level_req=3,
    modifier={"aoe_radius_multiplier": 1.25},
    prerequisites=["axe_slash_damage_1"]
)

axe_slash_damage_2 = UpgradeNode(
    id="axe_slash_damage_2",
    name="Increased Damage II",
    description="Further increases AxeSlash damage by 15%.",
    cost=250,
    level_req=3,
    modifier={"damage_multiplier": 1.15}, # Note: Multipliers might stack or be additive based on system design
    prerequisites=["axe_slash_damage_1"]
)

# Tier 3: Stun Effect or Ultimate Damage
axe_slash_stun = UpgradeNode(
    id="axe_slash_stun",
    name="Stunning Blow",
    description="Adds a chance to stun enemies hit by AxeSlash.",
    cost=400,
    level_req=5,
    modifier={"status_effect": {"type": "stun", "chance": 0.25, "duration": 1.0}},
    prerequisites=["axe_slash_arc"] # Example prerequisite path
)

axe_slash_damage_3 = UpgradeNode(
    id="axe_slash_damage_3",
    name="Devastating Strike",
    description="Massively increases AxeSlash damage by 25%.",
    cost=500,
    level_req=5,
    modifier={"damage_multiplier": 1.25},
    prerequisites=["axe_slash_damage_2"] # Example prerequisite path
)


# --- Warrior Ability Tree Definition ---
# Assuming AxeSlash is the primary ability for Warrior in this context
warrior_ability_tree = UpgradeTree(
    ability_id="AxeSlash", # Link to the specific ability ID
    nodes={
        axe_slash_damage_1.id: axe_slash_damage_1,
        axe_slash_arc.id: axe_slash_arc,
        axe_slash_damage_2.id: axe_slash_damage_2,
        axe_slash_stun.id: axe_slash_stun,
        axe_slash_damage_3.id: axe_slash_damage_3,
    }
)

# You might have trees for other warrior abilities here as well
# e.g., shield_bash_tree, charge_tree, etc.

# Export or register the tree
UPGRADE_TREES = {
    "AxeSlash": warrior_ability_tree
}

def get_warrior_upgrade_trees():
    """Returns all defined upgrade trees for the Warrior class."""
    return UPGRADE_TREES