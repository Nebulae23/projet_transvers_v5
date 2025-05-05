# src/engine/ecs/components/ability_experience.py

class AbilityExperience:
    """
    Component to track the experience points (XP) for each ability
    an entity possesses.
    """
    def __init__(self):
        # Dictionary mapping ability_id to current experience points
        self.experience = {}
        # Dictionary mapping ability_id to experience needed for the next level
        self.xp_to_next_level = {}

    def add_experience(self, ability_id, amount):
        """Adds experience to a specific ability."""
        if ability_id not in self.experience:
            self.experience[ability_id] = 0
            # TODO: Define how xp_to_next_level is determined (e.g., based on level)
            self.xp_to_next_level[ability_id] = 100 # Placeholder

        self.experience[ability_id] += amount
        print(f"Added {amount} XP to ability {ability_id}. Total: {self.experience[ability_id]}/{self.xp_to_next_level.get(ability_id, 'N/A')}")
        # Return True if a level up might be triggered
        return self.experience[ability_id] >= self.xp_to_next_level.get(ability_id, float('inf'))

    def get_experience(self, ability_id):
        """Gets the current experience for a specific ability."""
        return self.experience.get(ability_id, 0)

    def get_xp_needed(self, ability_id):
        """Gets the XP needed for the next level for a specific ability."""
        return self.xp_to_next_level.get(ability_id, 100) # Placeholder default

    def set_xp_needed(self, ability_id, amount):
        """Sets the XP needed for the next level, typically after leveling up."""
        self.xp_to_next_level[ability_id] = amount
        # Reset current XP relative to the new threshold if needed, or handle in level up logic
        # self.experience[ability_id] = 0 # Or subtract the previous threshold