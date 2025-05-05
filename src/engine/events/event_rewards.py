# src/engine/events/event_rewards.py
from typing import List, Dict, Any
from .weather_event import EventReward, EventRewardType

class RewardManager:
    def __init__(self):
        self.temporary_effects: Dict[str, float] = {}  # effect_id -> remaining_duration
        
        # Define reward templates
        self.item_templates = {
            "rain_coat": {
                "name": "Rainweaver's Cloak",
                "type": "armor",
                "stats": {"rain_resistance": 0.5}
            },
            "lightning_blade": {
                "name": "Stormforge Blade",
                "type": "weapon",
                "stats": {"lightning_damage": 25}
            },
            "storm_crystal": {
                "name": "Storm Crystal",
                "type": "material",
                "stats": {"energy_capacity": 100}
            }
        }
        
        self.ability_templates = {
            "nature_blessing": {
                "name": "Nature's Blessing",
                "type": "buff",
                "effect": "heal_in_rain"
            },
            "thunder_strike": {
                "name": "Thunder Strike",
                "type": "attack",
                "damage": 50,
                "element": "lightning"
            },
            "chain_lightning": {
                "name": "Chain Lightning",
                "type": "area_attack",
                "damage": 30,
                "chains": 3
            },
            "wind_dash": {
                "name": "Wind Dash",
                "type": "mobility",
                "distance": 10
            }
        }

    def grant_rewards(self, rewards: List[EventReward], player: Any) -> List[str]:
        """Grant rewards to player and return messages"""
        messages = []
        
        for reward in rewards:
            if reward.type == EventRewardType.ITEM:
                self._grant_item(reward, player, messages)
            elif reward.type == EventRewardType.RESOURCE:
                self._grant_resource(reward, player, messages)
            elif reward.type == EventRewardType.ABILITY:
                self._grant_ability(reward, player, messages)
            elif reward.type == EventRewardType.STAT_BOOST:
                self._apply_stat_boost(reward, player, messages)
                
        return messages

    def update(self, dt: float):
        """Update temporary effects"""
        expired_effects = []
        
        for effect_id, duration in self.temporary_effects.items():
            remaining = duration - dt
            if remaining <= 0:
                expired_effects.append(effect_id)
            else:
                self.temporary_effects[effect_id] = remaining
                
        for effect_id in expired_effects:
            del self.temporary_effects[effect_id]

    def _grant_item(self, reward: EventReward, player: Any, messages: List[str]):
        if reward.value in self.item_templates:
            item = self.item_templates[reward.value].copy()
            player.inventory.add_item(item, reward.quantity)
            messages.append(f"Received {reward.quantity}x {item['name']}")

    def _grant_resource(self, reward: EventReward, player: Any, messages: List[str]):
        player.resources[reward.value] += reward.quantity
        messages.append(f"Gained {reward.quantity} {reward.value}")

    def _grant_ability(self, reward: EventReward, player: Any, messages: List[str]):
        if reward.value in self.ability_templates:
            ability = self.ability_templates[reward.value].copy()
            player.learn_ability(ability)
            messages.append(f"Learned new ability: {ability['name']}")

    def _apply_stat_boost(self, reward: EventReward, player: Any, messages: List[str]):
        boost_id = f"boost_{reward.value}_{id(reward)}"
        player.add_stat_modifier(reward.value, reward.quantity)
        
        if reward.duration:
            self.temporary_effects[boost_id] = reward.duration
            messages.append(f"Gained {reward.value} boost for {reward.duration:.1f} seconds")
        else:
            messages.append(f"Gained permanent {reward.value} boost")