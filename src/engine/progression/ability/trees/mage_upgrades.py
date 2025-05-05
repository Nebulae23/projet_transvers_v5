# src/engine/progression/ability/trees/mage_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- MagicBolt Upgrades ---

# Tier 1: Base Damage/Efficiency Improvement (Example)
magic_bolt_efficiency = UpgradeNode(
    id="magic_bolt_efficiency",
    name="Mana Efficiency",
    description="Reduces the mana cost of MagicBolt by 15%.",
    cost=100,
    level_req=1,
    modifier={"mana_cost_multiplier": 0.85}
)

# Tier 2: Multiple Projectiles or Elemental Damage
magic_bolt_multi_shot = UpgradeNode(
    id="magic_bolt_multi_shot",
    name="Multi-Shot",
    description="MagicBolt fires an additional projectile.",
    cost=250,
    level_req=3,
    modifier={"projectile_count": 2}, # Assuming base is 1
    prerequisites=["magic_bolt_efficiency"]
)

magic_bolt_elemental_fire = UpgradeNode(
    id="magic_bolt_elemental_fire",
    name="Fire Attunement",
    description="MagicBolt now deals additional Fire damage.",
    cost=200,
    level_req=3,
    modifier={"elemental_damage": {"type": "fire", "amount": 10}},
    prerequisites=["magic_bolt_efficiency"]
)

# Tier 3: Target Penetration or Enhanced Elemental/Multi-Shot
magic_bolt_penetration = UpgradeNode(
    id="magic_bolt_penetration",
    name="Piercing Bolt",
    description="MagicBolt can now pierce through one additional target.",
    cost=400,
    level_req=5,
    modifier={"penetration_count": 1}, # Assuming base is 0
    prerequisites=["magic_bolt_multi_shot"] # Example path
)

magic_bolt_enhanced_fire = UpgradeNode(
    id="magic_bolt_enhanced_fire",
    name="Intensified Flames",
    description="Increases the Fire damage of MagicBolt.",
    cost=350,
    level_req=5,
    modifier={"elemental_damage": {"type": "fire", "amount": 20}}, # Overwrites or adds based on system
    prerequisites=["magic_bolt_elemental_fire"] # Example path
)

magic_bolt_triple_shot = UpgradeNode(
    id="magic_bolt_triple_shot",
    name="Triple Shot",
    description="MagicBolt fires two additional projectiles.",
    cost=500,
    level_req=5,
    modifier={"projectile_count": 3}, # Overwrites previous multi-shot
    prerequisites=["magic_bolt_multi_shot"] # Example path
)


# --- Mage Ability Tree Definition ---
mage_ability_tree = UpgradeTree(
    ability_id="MagicBolt",
    nodes={
        magic_bolt_efficiency.id: magic_bolt_efficiency,
        magic_bolt_multi_shot.id: magic_bolt_multi_shot,
        magic_bolt_elemental_fire.id: magic_bolt_elemental_fire,
        magic_bolt_penetration.id: magic_bolt_penetration,
        magic_bolt_enhanced_fire.id: magic_bolt_enhanced_fire,
        magic_bolt_triple_shot.id: magic_bolt_triple_shot,
    }
)

# Export or register the tree
UPGRADE_TREES = {
    "MagicBolt": mage_ability_tree
}

def get_mage_upgrade_trees():
    """Returns all defined upgrade trees for the Mage class."""
    return UPGRADE_TREES