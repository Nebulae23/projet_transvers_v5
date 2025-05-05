# src/engine/progression/ability/trees/cleric_upgrades.py

from src.engine.progression.ability.upgrade_tree import UpgradeNode, UpgradeTree

# --- MaceHit Upgrades (Assuming MaceHit can also trigger healing effects or is linked to a heal ability) ---
# Option 1: MaceHit itself gains healing properties
# Option 2: MaceHit enhances a separate Heal ability (more likely)
# Let's assume MaceHit enhances a linked 'HolyLight' heal ability for this example.

# Tier 1: Increased Healing Potency
holy_light_potency_1 = UpgradeNode(
    id="holy_light_potency_1",
    name="Enhanced Healing I",
    description="Increases the amount healed by Holy Light by 15%.",
    cost=120, # Clerics might have slightly different costs
    level_req=1,
    modifier={"heal_amount_multiplier": 1.15} # Modifies the linked heal ability
)

# Tier 2: Area of Effect Healing or Increased Potency
holy_light_aoe = UpgradeNode(
    id="holy_light_aoe",
    name="Healing Aura",
    description="Holy Light now heals allies in a small area around the target.",
    cost=220,
    level_req=3,
    modifier={"heal_aoe_radius": 5.0}, # Adds an AoE component
    prerequisites=["holy_light_potency_1"]
)

holy_light_potency_2 = UpgradeNode(
    id="holy_light_potency_2",
    name="Enhanced Healing II",
    description="Further increases the amount healed by Holy Light by 20%.",
    cost=280,
    level_req=3,
    modifier={"heal_amount_multiplier": 1.20},
    prerequisites=["holy_light_potency_1"]
)

# Tier 3: Protective Effect or Ultimate Healing/AoE
holy_light_protection = UpgradeNode(
    id="holy_light_protection",
    name="Protective Ward",
    description="Allies healed by Holy Light gain a temporary defensive buff.",
    cost=450,
    level_req=5,
    modifier={"buff_on_heal": {"type": "defense_boost", "duration": 5.0, "value": 0.10}}, # 10% defense boost
    prerequisites=["holy_light_aoe"] # Example path
)

holy_light_large_aoe = UpgradeNode(
    id="holy_light_large_aoe",
    name="Expansive Aura",
    description="Significantly increases the area of the Healing Aura.",
    cost=400,
    level_req=5,
    modifier={"heal_aoe_radius": 10.0}, # Increases radius further
    prerequisites=["holy_light_aoe"] # Example path
)

holy_light_potency_3 = UpgradeNode(
    id="holy_light_potency_3",
    name="Divine Intervention",
    description="Massively increases the healing potency of Holy Light by 30%.",
    cost=550,
    level_req=5,
    modifier={"heal_amount_multiplier": 1.30},
    prerequisites=["holy_light_potency_2"] # Example path
)


# --- Cleric Ability Tree Definition ---
# Assuming 'HolyLight' is the ability being upgraded, potentially triggered or linked by 'MaceHit'
cleric_ability_tree = UpgradeTree(
    ability_id="HolyLight", # ID of the ability being modified
    nodes={
        holy_light_potency_1.id: holy_light_potency_1,
        holy_light_aoe.id: holy_light_aoe,
        holy_light_potency_2.id: holy_light_potency_2,
        holy_light_protection.id: holy_light_protection,
        holy_light_large_aoe.id: holy_light_large_aoe,
        holy_light_potency_3.id: holy_light_potency_3,
    }
)

# Export or register the tree
UPGRADE_TREES = {
    "HolyLight": cleric_ability_tree # Or "MaceHit" if it directly applies these
}

def get_cleric_upgrade_trees():
    """Returns all defined upgrade trees for the Cleric class."""
    return UPGRADE_TREES