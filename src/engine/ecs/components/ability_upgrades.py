# src/engine/ecs/components/ability_upgrades.py

class AbilityUpgrades:
    """
    Component to track the active/unlocked upgrades for each ability
    an entity possesses.
    """
    def __init__(self):
        # Dictionary mapping ability_id to a set of unlocked upgrade_ids
        self.unlocked_upgrades = {}

    def add_upgrade(self, ability_id, upgrade_id):
        """Adds an unlocked upgrade to a specific ability."""
        if ability_id not in self.unlocked_upgrades:
            self.unlocked_upgrades[ability_id] = set()
        
        if upgrade_id not in self.unlocked_upgrades[ability_id]:
            self.unlocked_upgrades[ability_id].add(upgrade_id)
            print(f"Unlocked upgrade '{upgrade_id}' for ability '{ability_id}'.")
            return True
        else:
            print(f"Upgrade '{upgrade_id}' already unlocked for ability '{ability_id}'.")
            return False

    def get_unlocked_upgrades(self, ability_id):
        """Gets the set of unlocked upgrade IDs for a specific ability."""
        return self.unlocked_upgrades.get(ability_id, set())

    def has_upgrade(self, ability_id, upgrade_id):
        """Checks if a specific upgrade is unlocked for an ability."""
        return upgrade_id in self.get_unlocked_upgrades(ability_id)