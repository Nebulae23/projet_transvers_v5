#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Relic System for Nightfall Defenders
Implements special items that modify abilities and stats
"""

import random
import math

class RelicRarity:
    """Enumeration of relic rarities"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"  # Super rare, powerful relics

class RelicSystem:
    """Handles relics and their effects on the player"""
    
    def __init__(self, game):
        """
        Initialize the relic system
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Available relics with their effects
        self.available_relics = self._create_relics()
        
        # Player's active relics
        self.active_relics = {}
        
        # Maximum number of relics a player can have active (can be increased)
        self.max_active_relics = 3
        
        # Relic inventory (stored but not active)
        self.relic_inventory = {}
        
        # Night reward chest system
        self.chest_reward_ready = False
        self.nights_survived = 0
        self.chest_quality = RelicRarity.COMMON
        self.chest_rewards = []
        
        # Relic fluctuation variables
        self.random_stat_timers = {}
    
    def _create_relics(self):
        """Define all available relics"""
        relics = {
            # Original relics
            "hunters_amulet": {
                "name": "Hunter's Amulet",
                "description": "Increases damage by 20% but reduces max health by 10%",
                "rarity": RelicRarity.COMMON,
                "effects": {
                    "damage_multiplier": 1.2,
                    "max_health_multiplier": 0.9
                },
                "visual": "hunters_amulet.png"
            },
            "arcane_catalyst": {
                "name": "Arcane Catalyst",
                "description": "Reduces cooldowns by 15% but increases stamina cost by 10%",
                "rarity": RelicRarity.COMMON,
                "effects": {
                    "cooldown_multiplier": 0.85,
                    "stamina_cost_multiplier": 1.1
                },
                "visual": "arcane_catalyst.png"
            },
            "iron_heart": {
                "name": "Iron Heart",
                "description": "Increases max health by 15% but reduces movement speed by 5%",
                "rarity": RelicRarity.COMMON,
                "effects": {
                    "max_health_multiplier": 1.15,
                    "speed_multiplier": 0.95
                },
                "visual": "iron_heart.png"
            },
            "swift_boots": {
                "name": "Swift Boots",
                "description": "Increases movement speed by 15% but reduces max stamina by 10%",
                "rarity": RelicRarity.COMMON,
                "effects": {
                    "speed_multiplier": 1.15,
                    "max_stamina_multiplier": 0.9
                },
                "visual": "swift_boots.png"
            },
            "crystal_focus": {
                "name": "Crystal Focus",
                "description": "Increases projectile velocity by 20% but reduces damage by 5%",
                "rarity": RelicRarity.UNCOMMON,
                "effects": {
                    "projectile_speed_multiplier": 1.2,
                    "damage_multiplier": 0.95
                },
                "visual": "crystal_focus.png"
            },
            "vampiric_emblem": {
                "name": "Vampiric Emblem",
                "description": "Restores 5% of damage dealt as health but reduces max stamina by 15%",
                "rarity": RelicRarity.UNCOMMON,
                "effects": {
                    "life_steal": 0.05,
                    "max_stamina_multiplier": 0.85
                },
                "visual": "vampiric_emblem.png"
            },
            "unstable_catalyst": {
                "name": "Unstable Catalyst",
                "description": "Increases damage by 30% but has a 10% chance to damage yourself",
                "rarity": RelicRarity.RARE,
                "effects": {
                    "damage_multiplier": 1.3,
                    "self_damage_chance": 0.1,
                    "self_damage_percent": 0.05
                },
                "visual": "unstable_catalyst.png"
            },
            "guardian_talisman": {
                "name": "Guardian Talisman",
                "description": "Reduces all incoming damage by 15% but decreases cooldown recovery by 10%",
                "rarity": RelicRarity.RARE,
                "effects": {
                    "damage_reduction": 0.15,
                    "cooldown_multiplier": 1.1
                },
                "visual": "guardian_talisman.png"
            },
            "celestial_prism": {
                "name": "Celestial Prism",
                "description": "Projectiles can pierce through one enemy but reduces projectile speed by 10%",
                "rarity": RelicRarity.LEGENDARY,
                "effects": {
                    "projectile_pierce": 1,
                    "projectile_speed_multiplier": 0.9
                },
                "visual": "celestial_prism.png"
            },
            "essence_of_chaos": {
                "name": "Essence of Chaos",
                "description": "All stats randomly fluctuate between -10% and +30% every 30 seconds",
                "rarity": RelicRarity.LEGENDARY,
                "effects": {
                    "random_stats": True,
                    "stat_min_multiplier": 0.9,
                    "stat_max_multiplier": 1.3,
                    "fluctuation_time": 30
                },
                "visual": "essence_of_chaos.png"
            },
            
            # New relics with significant drawbacks (as per PRD)
            "moonlight_mirror": {
                "name": "Moonlight Mirror",
                "description": "Increases all damage by 40% at night, but decreases damage by 20% during day",
                "rarity": RelicRarity.EPIC,
                "effects": {
                    "conditional_damage_multiplier": {
                        "night": 1.4,
                        "day": 0.8
                    }
                },
                "visual": "moonlight_mirror.png"
            },
            "wrath_of_the_elements": {
                "name": "Wrath of the Elements",
                "description": "Adds elemental damage to all attacks, but you take double damage from elemental sources",
                "rarity": RelicRarity.EPIC,
                "effects": {
                    "elemental_damage_bonus": 0.3,
                    "elemental_vulnerability": 2.0
                },
                "visual": "wrath_elements.png"
            },
            "glass_cannon": {
                "name": "Glass Cannon",
                "description": "Doubles your damage output, but halves your maximum health",
                "rarity": RelicRarity.RARE,
                "effects": {
                    "damage_multiplier": 2.0,
                    "max_health_multiplier": 0.5
                },
                "visual": "glass_cannon.png"
            },
            "nightweaver": {
                "name": "Nightweaver",
                "description": "Move 25% faster in fog but take 10% more damage",
                "rarity": RelicRarity.UNCOMMON,
                "effects": {
                    "fog_speed_bonus": 1.25,
                    "damage_vulnerability": 1.1
                },
                "visual": "nightweaver.png"
            },
            "berserker_totem": {
                "name": "Berserker Totem",
                "description": "Damage increases as health decreases, up to 100% more at 1 HP",
                "rarity": RelicRarity.EPIC,
                "effects": {
                    "health_based_damage": True,
                    "max_damage_boost": 2.0
                },
                "visual": "berserker_totem.png"
            },
            "crown_of_thorns": {
                "name": "Crown of Thorns",
                "description": "Reflect 30% of damage back to enemies, but you cannot regenerate health naturally",
                "rarity": RelicRarity.RARE,
                "effects": {
                    "damage_reflection": 0.3,
                    "disable_health_regen": True
                },
                "visual": "crown_thorns.png"
            },
            "timeworn_hourglass": {
                "name": "Timeworn Hourglass",
                "description": "All cooldowns reduced by 40%, but day/night cycle progresses 25% faster",
                "rarity": RelicRarity.LEGENDARY,
                "effects": {
                    "cooldown_multiplier": 0.6,
                    "time_flow_multiplier": 1.25
                },
                "visual": "timeworn_hourglass.png"
            },
            "shadow_bond": {
                "name": "Shadow Bond",
                "description": "Create a shadow clone that mimics 40% of your attacks, but you take 15% more damage",
                "rarity": RelicRarity.LEGENDARY,
                "effects": {
                    "shadow_clone": 0.4,
                    "damage_vulnerability": 1.15
                },
                "visual": "shadow_bond.png"
            },
            "heart_of_ice": {
                "name": "Heart of Ice",
                "description": "Immune to fire damage, but take double damage from cold attacks and move 10% slower",
                "rarity": RelicRarity.RARE,
                "effects": {
                    "fire_immunity": True,
                    "cold_vulnerability": 2.0,
                    "speed_multiplier": 0.9
                },
                "visual": "heart_of_ice.png"
            },
            "phoenix_feather": {
                "name": "Phoenix Feather",
                "description": "Upon death, revive once with 30% health, then the relic crumbles to ash",
                "rarity": RelicRarity.MYTHICAL,
                "effects": {
                    "resurrection": True,
                    "resurrection_health": 0.3,
                    "one_time_use": True
                },
                "visual": "phoenix_feather.png"
            },
            "obsidian_skull": {
                "name": "Obsidian Skull",
                "description": "Ignore 50% of enemy armor, but you lose 5% of your maximum health per minute",
                "rarity": RelicRarity.EPIC,
                "effects": {
                    "armor_penetration": 0.5,
                    "health_decay": 0.05,
                    "health_decay_interval": 60  # seconds
                },
                "visual": "obsidian_skull.png"
            },
            "void_tether": {
                "name": "Void Tether",
                "description": "Pull enemies toward you with attacks, but you also get pulled toward enemies when hit",
                "rarity": RelicRarity.EPIC,
                "effects": {
                    "enemy_pull": True,
                    "self_pull": True
                },
                "visual": "void_tether.png"
            },
            "eye_of_the_storm": {
                "name": "Eye of the Storm",
                "description": "Create lightning strikes that hit nearby enemies, but you attract more enemies at night",
                "rarity": RelicRarity.LEGENDARY,
                "effects": {
                    "lightning_strikes": True,
                    "lightning_damage": 20,
                    "lightning_frequency": 5,  # seconds
                    "enemy_attraction_multiplier": 1.5
                },
                "visual": "eye_storm.png"
            }
        }
        
        return relics
    
    def get_random_relic(self, exclude_active=True, rarity_weights=None):
        """
        Get a random relic from the available relics
        
        Args:
            exclude_active (bool): Whether to exclude already active relics
            rarity_weights (dict): Weights for each rarity (default favors common)
        
        Returns:
            str: Relic ID or None if no relics available
        """
        # Default rarity weights if not provided
        if rarity_weights is None:
            rarity_weights = {
                RelicRarity.COMMON: 0.5,
                RelicRarity.UNCOMMON: 0.25,
                RelicRarity.RARE: 0.15,
                RelicRarity.EPIC: 0.07,
                RelicRarity.LEGENDARY: 0.025,
                RelicRarity.MYTHICAL: 0.005
            }
        
        # Filter out active relics if requested
        available = {}
        for relic_id, relic in self.available_relics.items():
            if exclude_active and relic_id in self.active_relics:
                continue
            available[relic_id] = relic
        
        if not available:
            return None
        
        # Group relics by rarity for weighted selection
        relics_by_rarity = {
            RelicRarity.COMMON: [],
            RelicRarity.UNCOMMON: [],
            RelicRarity.RARE: [],
            RelicRarity.EPIC: [],
            RelicRarity.LEGENDARY: [],
            RelicRarity.MYTHICAL: []
        }
        
        for relic_id, relic in available.items():
            rarity = relic["rarity"]
            relics_by_rarity[rarity].append(relic_id)
        
        # Choose rarity based on weights
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # If no relics of chosen rarity, try another rarity
        while not relics_by_rarity[chosen_rarity]:
            # Remove the empty rarity
            idx = rarities.index(chosen_rarity)
            rarities.pop(idx)
            weights.pop(idx)
            
            # No rarities left
            if not rarities:
                return None
            
            # Normalize weights
            total = sum(weights)
            if total > 0:
                weights = [w/total for w in weights]
            
            # Choose another rarity
            chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # Choose a random relic from the chosen rarity
        return random.choice(relics_by_rarity[chosen_rarity])
    
    def night_completed(self, success=True, difficulty_level=1.0):
        """
        Called when a night is completed to update chest rewards
        
        Args:
            success (bool): Whether the night was survived successfully
            difficulty_level (float): The difficulty level of the night (affects rewards)
            
        Returns:
            bool: Whether a chest reward is ready
        """
        if success:
            self.nights_survived += 1
            
            # Determine chest quality based on nights survived and difficulty
            # Higher difficulty = better rewards
            quality_threshold = 5.0 / difficulty_level  # At difficulty 1.0, requires 5 nights for better chest
            
            if self.nights_survived >= quality_threshold * 4:
                self.chest_quality = RelicRarity.MYTHICAL
            elif self.nights_survived >= quality_threshold * 3:
                self.chest_quality = RelicRarity.LEGENDARY
            elif self.nights_survived >= quality_threshold * 2:
                self.chest_quality = RelicRarity.EPIC
            elif self.nights_survived >= quality_threshold:
                self.chest_quality = RelicRarity.RARE
            elif self.nights_survived >= quality_threshold / 2:
                self.chest_quality = RelicRarity.UNCOMMON
            else:
                self.chest_quality = RelicRarity.COMMON
            
            # Generate chest contents
            self._generate_chest_rewards()
            
            # Set chest as ready
            self.chest_reward_ready = True
            
            # Debug output
            print(f"Night {self.nights_survived} completed. Chest quality: {self.chest_quality}")
            
            return True
        return False
    
    def _generate_chest_rewards(self):
        """Generate rewards for the chest based on quality"""
        self.chest_rewards = []
        
        # Number of relics based on chest quality
        num_relics = 1
        if self.chest_quality == RelicRarity.UNCOMMON:
            num_relics = 2
        elif self.chest_quality == RelicRarity.RARE:
            num_relics = 2
        elif self.chest_quality == RelicRarity.EPIC:
            num_relics = 3
        elif self.chest_quality == RelicRarity.LEGENDARY:
            num_relics = 3
        elif self.chest_quality == RelicRarity.MYTHICAL:
            num_relics = 4
        
        # Adjust rarity weights based on chest quality
        rarity_weights = {
            RelicRarity.COMMON: 0.5,
            RelicRarity.UNCOMMON: 0.25,
            RelicRarity.RARE: 0.15,
            RelicRarity.EPIC: 0.07,
            RelicRarity.LEGENDARY: 0.025,
            RelicRarity.MYTHICAL: 0.005
        }
        
        # Boost weights for better rarities based on chest quality
        if self.chest_quality == RelicRarity.UNCOMMON:
            rarity_weights[RelicRarity.COMMON] = 0.4
            rarity_weights[RelicRarity.UNCOMMON] = 0.35
        elif self.chest_quality == RelicRarity.RARE:
            rarity_weights[RelicRarity.COMMON] = 0.2
            rarity_weights[RelicRarity.UNCOMMON] = 0.4
            rarity_weights[RelicRarity.RARE] = 0.25
        elif self.chest_quality == RelicRarity.EPIC:
            rarity_weights[RelicRarity.COMMON] = 0.1
            rarity_weights[RelicRarity.UNCOMMON] = 0.2
            rarity_weights[RelicRarity.RARE] = 0.4
            rarity_weights[RelicRarity.EPIC] = 0.2
        elif self.chest_quality == RelicRarity.LEGENDARY:
            rarity_weights[RelicRarity.COMMON] = 0.0
            rarity_weights[RelicRarity.UNCOMMON] = 0.1
            rarity_weights[RelicRarity.RARE] = 0.3
            rarity_weights[RelicRarity.EPIC] = 0.4
            rarity_weights[RelicRarity.LEGENDARY] = 0.15
        elif self.chest_quality == RelicRarity.MYTHICAL:
            rarity_weights[RelicRarity.COMMON] = 0.0
            rarity_weights[RelicRarity.UNCOMMON] = 0.0
            rarity_weights[RelicRarity.RARE] = 0.2
            rarity_weights[RelicRarity.EPIC] = 0.3
            rarity_weights[RelicRarity.LEGENDARY] = 0.4
            rarity_weights[RelicRarity.MYTHICAL] = 0.1
        
        # Get unique relics
        all_relics = set()
        for _ in range(num_relics):
            relic_id = self.get_random_relic(exclude_active=False, rarity_weights=rarity_weights)
            if relic_id and relic_id not in all_relics:
                all_relics.add(relic_id)
                self.chest_rewards.append(relic_id)
        
        # Debug output
        print(f"Generated chest rewards: {', '.join([self.available_relics[r]['name'] for r in self.chest_rewards])}")
    
    def open_chest(self):
        """
        Open the reward chest
        
        Returns:
            list: Relic IDs that were obtained, or empty list if no chest
        """
        if not self.chest_reward_ready:
            return []
        
        # Take rewards
        rewards = self.chest_rewards
        
        # Add relics to inventory
        for relic_id in rewards:
            if relic_id not in self.relic_inventory:
                self.relic_inventory[relic_id] = self.available_relics[relic_id].copy()
        
        # Reset chest
        self.chest_reward_ready = False
        self.chest_rewards = []
        
        return rewards
    
    def add_relic(self, relic_id):
        """
        Add a relic to the player's active relics
        
        Args:
            relic_id (str): ID of the relic to add
        
        Returns:
            bool: True if the relic was added, False otherwise
        """
        # Check if the relic exists
        if relic_id not in self.available_relics:
            print(f"Relic {relic_id} does not exist")
            return False
        
        # Check if the player has room for another relic
        if len(self.active_relics) >= self.max_active_relics:
            print(f"Player already has maximum relics ({self.max_active_relics})")
            return False
        
        # Add the relic
        self.active_relics[relic_id] = self.available_relics[relic_id].copy()
        
        # Apply relic effects
        self._apply_relic_effects(relic_id)
        
        # Remove from inventory if it was there
        if relic_id in self.relic_inventory:
            del self.relic_inventory[relic_id]
        
        # Show a message
        if hasattr(self.game, 'show_message'):
            relic_name = self.available_relics[relic_id]["name"]
            self.game.show_message(f"Obtained {relic_name}!")
        
        print(f"Added relic: {self.available_relics[relic_id]['name']}")
        return True
    
    def remove_relic(self, relic_id):
        """
        Remove a relic from the player's active relics
        
        Args:
            relic_id (str): ID of the relic to remove
        
        Returns:
            bool: True if the relic was removed, False otherwise
        """
        # Check if the relic is active
        if relic_id not in self.active_relics:
            return False
        
        # Remove the relic
        relic = self.active_relics.pop(relic_id)
        
        # Remove relic effects (by applying inverse effects)
        self._remove_relic_effects(relic_id)
        
        print(f"Removed relic: {relic['name']}")
        return True
    
    def _apply_relic_effects(self, relic_id):
        """
        Apply the effects of a relic to the player
        
        Args:
            relic_id (str): ID of the relic to apply
        """
        # Ensure player exists
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        
        player = self.game.player
        relic = self.active_relics[relic_id]
        effects = relic["effects"]
        
        # Apply each effect
        for effect, value in effects.items():
            # Skip special effects that are handled elsewhere
            if effect in ["random_stats", "life_steal", "self_damage_chance", "projectile_pierce"]:
                continue
                
            # Apply stat multipliers
            if effect == "damage_multiplier":
                for projectile_type in player.projectile_types.values():
                    projectile_type["damage"] *= value
            
            elif effect == "cooldown_multiplier":
                for projectile_type in player.projectile_types.values():
                    projectile_type["cooldown"] *= value
            
            elif effect == "max_health_multiplier":
                old_max_health = player.max_health
                player.max_health *= value
                # Adjust current health proportionally
                player.health = (player.health / old_max_health) * player.max_health
                if player.health < 1:
                    player.health = 1
            
            elif effect == "max_stamina_multiplier":
                old_max_stamina = player.max_stamina
                player.max_stamina *= value
                # Adjust current stamina proportionally
                player.stamina = (player.stamina / old_max_stamina) * player.max_stamina
            
            elif effect == "speed_multiplier":
                player.speed *= value
            
            elif effect == "projectile_speed_multiplier":
                for projectile_type in player.projectile_types.values():
                    if "speed" in projectile_type:
                        projectile_type["speed"] *= value
            
            elif effect == "damage_reduction":
                if hasattr(player, "damage_reduction"):
                    player.damage_reduction = player.damage_reduction + value - (player.damage_reduction * value)
                else:
                    player.damage_reduction = value
    
    def _remove_relic_effects(self, relic_id):
        """
        Remove the effects of a relic from the player
        
        Args:
            relic_id (str): ID of the relic to remove
        """
        # Ensure player exists
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        
        player = self.game.player
        relic = self.available_relics[relic_id]
        effects = relic["effects"]
        
        # Remove each effect (invert the multiplier)
        for effect, value in effects.items():
            # Skip special effects that are handled elsewhere
            if effect in ["random_stats", "life_steal", "self_damage_chance", "projectile_pierce"]:
                continue
                
            # Apply inverse stat multipliers
            if effect == "damage_multiplier":
                for projectile_type in player.projectile_types.values():
                    projectile_type["damage"] /= value
            
            elif effect == "cooldown_multiplier":
                for projectile_type in player.projectile_types.values():
                    projectile_type["cooldown"] /= value
            
            elif effect == "max_health_multiplier":
                old_max_health = player.max_health
                player.max_health /= value
                # Adjust current health proportionally
                player.health = (player.health / old_max_health) * player.max_health
            
            elif effect == "max_stamina_multiplier":
                old_max_stamina = player.max_stamina
                player.max_stamina /= value
                # Adjust current stamina proportionally
                player.stamina = (player.stamina / old_max_stamina) * player.max_stamina
            
            elif effect == "speed_multiplier":
                player.speed /= value
            
            elif effect == "projectile_speed_multiplier":
                for projectile_type in player.projectile_types.values():
                    if "speed" in projectile_type:
                        projectile_type["speed"] /= value
            
            elif effect == "damage_reduction":
                if hasattr(player, "damage_reduction"):
                    # Invert damage reduction formula
                    player.damage_reduction = (player.damage_reduction - value) / (1 - value)
                    if player.damage_reduction < 0:
                        player.damage_reduction = 0
    
    def update(self, dt):
        """
        Update the relic system
        
        Args:
            dt (float): Delta time since last update
        """
        if not hasattr(self.game, 'player') or not self.game.player:
            return
        
        player = self.game.player
        
        # Check for special effects that need to be processed every frame
        for relic_id, relic in self.active_relics.items():
            effects = relic["effects"]
            
            # Handle life steal
            if "life_steal" in effects and player.last_damage_dealt > 0:
                life_steal_amount = player.last_damage_dealt * effects["life_steal"]
                player.heal(life_steal_amount)
                player.last_damage_dealt = 0
            
            # Handle random stat fluctuations
            if "random_stats" in effects and effects["random_stats"]:
                # Check if it's time to fluctuate stats
                if not hasattr(self, '_fluctuation_timer'):
                    self._fluctuation_timer = 0
                    self._apply_random_fluctuation(relic_id)
                
                self._fluctuation_timer += dt
                if self._fluctuation_timer >= effects["fluctuation_time"]:
                    self._fluctuation_timer = 0
                    self._apply_random_fluctuation(relic_id)
        
        # Check for chance-based effects when the player attacks
        if player.is_attacking and not hasattr(player, '_last_attack_check'):
            for relic_id, relic in self.active_relics.items():
                effects = relic["effects"]
                
                # Handle self-damage chance
                if "self_damage_chance" in effects:
                    if random.random() < effects["self_damage_chance"]:
                        damage = player.max_health * effects["self_damage_percent"]
                        player.take_damage(damage)
                        if hasattr(self.game, 'show_message'):
                            self.game.show_message("Unstable Catalyst backfired!")
            
            # Mark this attack as checked
            player._last_attack_check = True
        elif not player.is_attacking and hasattr(player, '_last_attack_check'):
            delattr(player, '_last_attack_check')
    
    def _apply_random_fluctuation(self, relic_id):
        """
        Apply random stat fluctuations for the Essence of Chaos relic
        
        Args:
            relic_id (str): ID of the relic to apply fluctuations for
        """
        player = self.game.player
        effects = self.active_relics[relic_id]["effects"]
        
        # Generate random multipliers for each stat
        multipliers = {
            "damage": random.uniform(effects["stat_min_multiplier"], effects["stat_max_multiplier"]),
            "health": random.uniform(effects["stat_min_multiplier"], effects["stat_max_multiplier"]),
            "stamina": random.uniform(effects["stat_min_multiplier"], effects["stat_max_multiplier"]),
            "speed": random.uniform(effects["stat_min_multiplier"], effects["stat_max_multiplier"]),
            "cooldown": random.uniform(effects["stat_min_multiplier"], effects["stat_max_multiplier"])
        }
        
        # Store the base stats if not already stored
        if not hasattr(self, '_base_stats'):
            self._base_stats = {
                "damage": {type_id: type_info["damage"] for type_id, type_info in player.projectile_types.items()},
                "health": player.max_health,
                "stamina": player.max_stamina,
                "speed": player.speed,
                "cooldown": {type_id: type_info["cooldown"] for type_id, type_info in player.projectile_types.items()}
            }
        
        # Apply the new multipliers
        # Damage
        for type_id, base_damage in self._base_stats["damage"].items():
            player.projectile_types[type_id]["damage"] = base_damage * multipliers["damage"]
        
        # Health
        old_max_health = player.max_health
        player.max_health = self._base_stats["health"] * multipliers["health"]
        # Adjust current health proportionally
        player.health = (player.health / old_max_health) * player.max_health
        if player.health < 1:
            player.health = 1
        
        # Stamina
        old_max_stamina = player.max_stamina
        player.max_stamina = self._base_stats["stamina"] * multipliers["stamina"]
        # Adjust current stamina proportionally
        player.stamina = (player.stamina / old_max_stamina) * player.max_stamina
        
        # Speed
        player.speed = self._base_stats["speed"] * multipliers["speed"]
        
        # Cooldown
        for type_id, base_cooldown in self._base_stats["cooldown"].items():
            player.projectile_types[type_id]["cooldown"] = base_cooldown * multipliers["cooldown"]
        
        # Show a message about the fluctuation
        if hasattr(self.game, 'show_message'):
            self.game.show_message("Essence of Chaos fluctuates your stats!")
    
    def get_relic_info(self, relic_id):
        """
        Get information about a relic
        
        Args:
            relic_id (str): ID of the relic
        
        Returns:
            dict: Relic information or None if the relic doesn't exist
        """
        if relic_id not in self.available_relics:
            return None
        
        return self.available_relics[relic_id].copy()
    
    def get_active_relics_info(self):
        """
        Get information about all active relics
        
        Returns:
            list: List of active relic information
        """
        return [self.available_relics[relic_id].copy() for relic_id in self.active_relics] 