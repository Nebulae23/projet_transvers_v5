# src/engine/scenes/city_demo/city_demo_state.py

class CityDemoState:
    """
    Holds the state specific to the city building demo scene.
    """
    def __init__(self):
        # Initial resources for testing
        self.resources = {
            "wood": 1000,
            "stone": 800,
            "food": 500,
            "gold": 200,
            "mana": 100  # Example resource for potential magic elements
        }

        # Initial state of buildings in the city
        self.buildings = [
            {"type": "TownHall", "level": 1, "position": (0, 0)},
            {"type": "House", "level": 1, "position": (5, 5)},
            {"type": "LumberMill", "level": 1, "position": (-5, 5)},
            {"type": "Quarry", "level": 1, "position": (5, -5)},
            {"type": "Farm", "level": 1, "position": (-5, -5)},
        ]

        # Configuration of city defenses
        self.defenses = {
            "walls": {"level": 1, "health": 1000},
            "towers": [
                {"type": "ArcherTower", "level": 1, "position": (10, 0)},
                {"type": "CannonTower", "level": 1, "position": (-10, 0)},
            ]
        }

        # Demo-specific statistics or flags
        self.stats = {
            "day": 1,
            "population": 50,
            "morale": 75, # Percentage
            "threat_level": 1, # Current threat level for potential events
            "event_active": False
        }

    def update_resource(self, resource_type, amount):
        """ Safely updates a resource count. """
        if resource_type in self.resources:
            self.resources[resource_type] += amount
            if self.resources[resource_type] < 0:
                self.resources[resource_type] = 0 # Prevent negative resources
            print(f"Updated {resource_type}: {self.resources[resource_type]}")
        else:
            print(f"Warning: Tried to update unknown resource '{resource_type}'")

    def add_building(self, building_data):
        """ Adds a new building to the state. """
        self.buildings.append(building_data)
        print(f"Added building: {building_data['type']} at {building_data['position']}")

    def get_building_count(self, building_type):
        """ Returns the count of a specific building type. """
        return sum(1 for b in self.buildings if b['type'] == building_type)

    def advance_day(self):
        """ Advances the day and updates relevant stats. """
        self.stats["day"] += 1
        # Potentially trigger daily resource generation, consumption, events etc.
        print(f"Advanced to Day {self.stats['day']}")
        # Example: Basic food consumption
        food_consumed = self.stats["population"] // 10
        self.update_resource("food", -food_consumed)