# src/engine/ecs/components/ability_level.py

class AbilityLevel:
    """
    Component to track the current level of each ability an entity possesses.
    """
    def __init__(self, max_level=10):
        # Dictionary mapping ability_id to its current level
        self.levels = {}
        self.max_level = max_level

    def get_level(self, ability_id):
        """Gets the current level for a specific ability."""
        return self.levels.get(ability_id, 1) # Default to level 1 if not tracked

    def set_level(self, ability_id, level):
        """Sets the level for a specific ability, respecting the max level."""
        if level <= self.max_level:
            self.levels[ability_id] = level
            print(f"Set ability {ability_id} to level {level}.")
        else:
            self.levels[ability_id] = self.max_level
            print(f"Ability {ability_id} reached max level {self.max_level}.")

    def increment_level(self, ability_id):
        """Increments the level of a specific ability."""
        current_level = self.get_level(ability_id)
        if current_level < self.max_level:
            self.set_level(ability_id, current_level + 1)
            return True # Level increased
        return False # Max level reached