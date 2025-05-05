# src/engine/progression/ability/ability_modifiers.py

from abc import ABC, abstractmethod

class AbilityModifier(ABC):
    """
    Abstract base class for all ability modifiers.
    """
    @abstractmethod
    def apply(self, ability_stats):
        """
        Applies the modification to the ability stats.
        :param ability_stats: The stats object of the ability to modify.
        """
        pass

class DamageModifier(AbilityModifier):
    """
    Modifies the damage of an ability.
    """
    def __init__(self, damage_increase_percentage=0, flat_damage_increase=0):
        self.damage_increase_percentage = damage_increase_percentage
        self.flat_damage_increase = flat_damage_increase

    def apply(self, ability_stats):
        """
        Increases damage by a percentage and/or a flat amount.
        """
        if self.damage_increase_percentage > 0:
            ability_stats.damage *= (1 + self.damage_increase_percentage / 100)
        if self.flat_damage_increase > 0:
            ability_stats.damage += self.flat_damage_increase
        print(f"Applied damage modifier: +{self.damage_increase_percentage}% / +{self.flat_damage_increase} flat. New damage: {ability_stats.damage}")

class RangeModifier(AbilityModifier):
    """
    Modifies the range of an ability.
    """
    def __init__(self, range_increase_percentage=0, flat_range_increase=0):
        self.range_increase_percentage = range_increase_percentage
        self.flat_range_increase = flat_range_increase

    def apply(self, ability_stats):
        """
        Increases range by a percentage and/or a flat amount.
        """
        if self.range_increase_percentage > 0:
            ability_stats.range *= (1 + self.range_increase_percentage / 100)
        if self.flat_range_increase > 0:
            ability_stats.range += self.flat_range_increase
        print(f"Applied range modifier: +{self.range_increase_percentage}% / +{self.flat_range_increase} flat. New range: {ability_stats.range}")

# Add other modifiers as needed (e.g., CooldownModifier, AreaOfEffectModifier, etc.)