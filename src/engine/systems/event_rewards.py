# src/engine/systems/event_rewards.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random
from ..inventory.items import Item, ItemRarity
from ..progression.experience import ExperienceSystem

class RewardType(Enum):
    ITEM = "item"
    CURRENCY = "currency"
    EXPERIENCE = "experience"
    RESOURCE = "resource"
    REPUTATION = "reputation"

@dataclass
class Reward:
    type: RewardType
    value: Any
    quantity: int = 1
    rarity: Optional[ItemRarity] = None

class RewardTable:
    def __init__(self, base_rewards: List[Reward], bonus_rewards: List[Reward],
                 guaranteed_picks: int = 1, bonus_picks: int = 0,
                 rarity_weights: Dict[ItemRarity, float] = None):
        self.base_rewards = base_rewards
        self.bonus_rewards = bonus_rewards
        self.guaranteed_picks = guaranteed_picks
        self.bonus_picks = bonus_picks
        self.rarity_weights = rarity_weights or {
            ItemRarity.COMMON: 0.6,
            ItemRarity.UNCOMMON: 0.25,
            ItemRarity.RARE: 0.1,
            ItemRarity.EPIC: 0.04,
            ItemRarity.LEGENDARY: 0.01
        }

class EventRewardSystem:
    def __init__(self, experience_system: ExperienceSystem):
        self.experience_system = experience_system
        self.reward_tables: Dict[str, RewardTable] = {}
        self._initialize_reward_tables()

    def _initialize_reward_tables(self):
        # City event rewards
        self.reward_tables["city_defense"] = RewardTable(
            base_rewards=[
                Reward(RewardType.CURRENCY, "gold", 100),
                Reward(RewardType.RESOURCE, "wood", 50),
                Reward(RewardType.RESOURCE, "stone", 30)
            ],
            bonus_rewards=[
                Reward(RewardType.ITEM, "defense_blueprint", 1, ItemRarity.RARE),
                Reward(RewardType.REPUTATION, "city_guard", 100)
            ],
            guaranteed_picks=2,
            bonus_picks=1
        )

        # Combat event rewards
        self.reward_tables["boss_defeat"] = RewardTable(
            base_rewards=[
                Reward(RewardType.EXPERIENCE, "combat_exp", 1000),
                Reward(RewardType.CURRENCY, "gold", 500)
            ],
            bonus_rewards=[
                Reward(RewardType.ITEM, "boss_weapon", 1, ItemRarity.EPIC),
                Reward(RewardType.ITEM, "boss_armor", 1, ItemRarity.EPIC)
            ],
            guaranteed_picks=2,
            bonus_picks=1
        )

    def generate_rewards(self, event_type: str, 
                        bonus_multiplier: float = 1.0,
                        luck_modifier: float = 1.0) -> List[Reward]:
        if event_type not in self.reward_tables:
            return []

        table = self.reward_tables[event_type]
        rewards = []

        # Generate guaranteed rewards
        guaranteed = random.sample(
            table.base_rewards,
            min(table.guaranteed_picks, len(table.base_rewards))
        )
        rewards.extend(guaranteed)

        # Generate bonus rewards
        if table.bonus_picks > 0 and random.random() < (0.3 * luck_modifier):
            bonus = random.sample(
                table.bonus_rewards,
                min(table.bonus_picks, len(table.bonus_rewards))
            )
            rewards.extend(bonus)

        # Apply bonus multiplier
        for reward in rewards:
            if reward.type in [RewardType.CURRENCY, RewardType.EXPERIENCE, RewardType.RESOURCE]:
                reward.quantity = int(reward.quantity * bonus_multiplier)

        return rewards

    def apply_rewards(self, rewards: List[Reward], player_inventory, city_manager):
        for reward in rewards:
            if reward.type == RewardType.EXPERIENCE:
                self.experience_system.gain_experience(reward.quantity)
            elif reward.type == RewardType.CURRENCY:
                player_inventory.add_currency(reward.value, reward.quantity)
            elif reward.type == RewardType.ITEM:
                item = self._create_item(reward)
                player_inventory.add_item(item)
            elif reward.type == RewardType.RESOURCE:
                city_manager.add_resource(reward.value, reward.quantity)
            elif reward.type == RewardType.REPUTATION:
                city_manager.modify_reputation(reward.value, reward.quantity)

    def _create_item(self, reward: Reward) -> Item:
        # Create item instance based on reward data
        return Item(
            reward.value,
            reward.rarity or ItemRarity.COMMON,
            level=self.experience_system.get_level()
        )

    def get_reward_preview(self, event_type: str) -> List[dict]:
        if event_type not in self.reward_tables:
            return []

        table = self.reward_tables[event_type]
        preview = []

        for reward in table.base_rewards:
            preview.append({
                "type": reward.type.value,
                "description": self._get_reward_description(reward),
                "guaranteed": True
            })

        for reward in table.bonus_rewards:
            preview.append({
                "type": reward.type.value,
                "description": self._get_reward_description(reward),
                "guaranteed": False
            })

        return preview

    def _get_reward_description(self, reward: Reward) -> str:
        if reward.type == RewardType.ITEM:
            rarity_text = f"{reward.rarity.value} " if reward.rarity else ""
            return f"{rarity_text}{reward.value}"
        elif reward.type == RewardType.CURRENCY:
            return f"{reward.quantity} {reward.value}"
        elif reward.type == RewardType.EXPERIENCE:
            return f"{reward.quantity} experience points"
        elif reward.type == RewardType.RESOURCE:
            return f"{reward.quantity} {reward.value}"
        elif reward.type == RewardType.REPUTATION:
            return f"{reward.quantity} reputation with {reward.value}"
        return "Unknown reward"