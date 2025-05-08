#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crafting System for Nightfall Defenders
Implements crafting recipes and upgrade mechanics
"""

class CraftingSystem:
    """Handles crafting recipes and player upgrades"""
    
    def __init__(self, game):
        """
        Initialize the crafting system
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Available recipes
        self.recipes = self._create_recipes()
        
        # Track player's crafted upgrades
        self.crafted_upgrades = {
            "weapon_damage": 0,
            "weapon_cooldown": 0,
            "health_boost": 0,
            "stamina_boost": 0,
            "movement_speed": 0
        }
        
        # Maximum upgrade levels
        self.max_upgrade_level = 5
        
        # Crafting system enhancements from buildings
        self.crafting_speed_multiplier = 1.0
        self.resource_efficiency = 0.0
    
    def _create_recipes(self):
        """Define crafting recipes for various upgrades"""
        return {
            "weapon_damage": {
                "name": "Weapon Damage",
                "description": "Increase base damage of all weapons by 5 per level",
                "effect": {"damage_boost": 5},
                "levels": [
                    {"wood": 5, "stone": 3},
                    {"wood": 10, "stone": 5, "crystal": 1},
                    {"wood": 15, "stone": 8, "crystal": 2},
                    {"wood": 20, "stone": 12, "crystal": 4},
                    {"wood": 30, "stone": 15, "crystal": 8}
                ]
            },
            "weapon_cooldown": {
                "name": "Attack Speed",
                "description": "Reduce weapon cooldown by 10% per level",
                "effect": {"cooldown_reduction": 0.1},
                "levels": [
                    {"wood": 3, "herb": 2},
                    {"wood": 6, "herb": 4},
                    {"wood": 10, "herb": 8, "crystal": 1},
                    {"wood": 15, "herb": 12, "crystal": 2},
                    {"wood": 20, "herb": 15, "crystal": 4}
                ]
            },
            "health_boost": {
                "name": "Health Boost",
                "description": "Increase maximum health by 10 per level",
                "effect": {"health_boost": 10},
                "levels": [
                    {"herb": 5},
                    {"herb": 8, "stone": 3},
                    {"herb": 12, "stone": 6, "crystal": 1},
                    {"herb": 15, "stone": 10, "crystal": 2},
                    {"herb": 20, "stone": 15, "crystal": 4}
                ]
            },
            "stamina_boost": {
                "name": "Stamina Boost",
                "description": "Increase maximum stamina by 10 per level",
                "effect": {"stamina_boost": 10},
                "levels": [
                    {"herb": 3, "wood": 3},
                    {"herb": 6, "wood": 6},
                    {"herb": 10, "wood": 10},
                    {"herb": 15, "wood": 15, "crystal": 1},
                    {"herb": 20, "wood": 20, "crystal": 3}
                ]
            },
            "movement_speed": {
                "name": "Movement Speed",
                "description": "Increase movement speed by 5% per level",
                "effect": {"speed_boost": 0.05},
                "levels": [
                    {"stone": 4, "wood": 4},
                    {"stone": 8, "wood": 8},
                    {"stone": 12, "wood": 12, "crystal": 1},
                    {"stone": 16, "wood": 16, "crystal": 2},
                    {"stone": 20, "wood": 20, "crystal": 3}
                ]
            }
        }
    
    def can_craft(self, recipe_id):
        """
        Check if player has resources to craft an upgrade
        
        Args:
            recipe_id (str): ID of the recipe to check
        
        Returns:
            bool: True if player has resources and upgrade is available
        """
        if recipe_id not in self.recipes:
            return False
        
        # Check if we've reached max upgrade level
        current_level = self.crafted_upgrades.get(recipe_id, 0)
        if current_level >= self.max_upgrade_level:
            return False
        
        # Get cost for the next level
        recipe = self.recipes[recipe_id]
        if current_level >= len(recipe["levels"]):
            return False
        
        cost = recipe["levels"][current_level]
        
        # Check if player has enough resources
        player = self.game.player
        if not player or not hasattr(player, "inventory"):
            return False
        
        for resource, amount in cost.items():
            if player.inventory.get(resource, 0) < amount:
                return False
        
        return True
    
    def craft_upgrade(self, recipe_id):
        """
        Craft an upgrade if player has resources
        
        Args:
            recipe_id (str): ID of the recipe to craft
        
        Returns:
            bool: True if crafting was successful
        """
        if not self.can_craft(recipe_id):
            return False
        
        # Get the current level and cost
        current_level = self.crafted_upgrades.get(recipe_id, 0)
        recipe = self.recipes[recipe_id]
        cost = recipe["levels"][current_level]
        
        # Deduct resources from player
        player = self.game.player
        for resource, amount in cost.items():
            player.inventory[resource] -= amount
        
        # Increment upgrade level
        self.crafted_upgrades[recipe_id] = current_level + 1
        
        # Apply upgrade effects
        self._apply_upgrade_effects(recipe_id)
        
        print(f"Crafted {recipe['name']} (Level {current_level + 1})")
        return True
    
    def _apply_upgrade_effects(self, recipe_id):
        """
        Apply the effects of a crafted upgrade
        
        Args:
            recipe_id (str): ID of the crafted upgrade
        """
        if recipe_id not in self.recipes:
            return
        
        recipe = self.recipes[recipe_id]
        player = self.game.player
        
        # Apply effects based on recipe type
        if recipe_id == "weapon_damage":
            damage_boost = recipe["effect"]["damage_boost"]
            for projectile_type in player.projectile_types.values():
                projectile_type["damage"] += damage_boost
        
        elif recipe_id == "weapon_cooldown":
            cooldown_reduction = recipe["effect"]["cooldown_reduction"]
            for projectile_type in player.projectile_types.values():
                projectile_type["cooldown"] *= (1 - cooldown_reduction)
        
        elif recipe_id == "health_boost":
            health_boost = recipe["effect"]["health_boost"]
            player.max_health += health_boost
            player.health += health_boost
        
        elif recipe_id == "stamina_boost":
            stamina_boost = recipe["effect"]["stamina_boost"]
            player.max_stamina += stamina_boost
            player.stamina += stamina_boost
        
        elif recipe_id == "movement_speed":
            speed_boost = recipe["effect"]["speed_boost"]
            player.speed *= (1 + speed_boost)
    
    def get_recipe_info(self, recipe_id):
        """
        Get formatted information about a recipe
        
        Args:
            recipe_id (str): ID of the recipe
        
        Returns:
            dict: Recipe information, including cost and current level
        """
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        current_level = self.crafted_upgrades.get(recipe_id, 0)
        
        info = {
            "id": recipe_id,
            "name": recipe["name"],
            "description": recipe["description"],
            "current_level": current_level,
            "max_level": self.max_upgrade_level
        }
        
        # Add cost information if not max level
        if current_level < self.max_upgrade_level and current_level < len(recipe["levels"]):
            info["cost"] = recipe["levels"][current_level]
            info["can_craft"] = self.can_craft(recipe_id)
        else:
            info["cost"] = None
            info["can_craft"] = False
        
        return info
    
    def get_all_recipes_info(self):
        """
        Get information about all available recipes
        
        Returns:
            list: List of recipe info dictionaries
        """
        return [self.get_recipe_info(recipe_id) for recipe_id in self.recipes]
    
    def update(self, dt):
        """
        Update the crafting system
        
        Args:
            dt: Delta time in seconds
        """
        # Currently nothing to update over time
        # This method exists for compatibility with other systems
        pass 