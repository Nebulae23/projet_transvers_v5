# Tests pour les composants de la ville (BuildingComponent, ResourceComponent, DefenseComponent, CityGridComponent)
import unittest
from src.engine.city.components.building_component import BuildingComponent

class TestBuildingComponent(unittest.TestCase):

    def test_initialization(self):
        """Test the initialization of BuildingComponent properties."""
        pos = (10, 20)
        dims = (2, 3)
        cost = {"wood": 50}
        b_type = "house"
        building = BuildingComponent(
            position=pos,
            dimensions=dims,
            health=150.0,
            max_health=200.0,
            construction_progress=0.5,
            is_constructed=False,
            level=2,
            upgrades={"speed": 1},
            construction_cost=cost,
            construction_time=15.0,
            building_type_id=b_type
        )
        self.assertEqual(building.position, pos)
        self.assertEqual(building.dimensions, dims)
        self.assertEqual(building.health, 150.0)
        self.assertEqual(building.max_health, 200.0)
        self.assertEqual(building.construction_progress, 0.5)
        self.assertFalse(building.is_constructed)
        self.assertEqual(building.level, 2)
        self.assertEqual(building.upgrades, {"speed": 1})
        self.assertEqual(building.construction_cost, cost)
        self.assertEqual(building.construction_time, 15.0)
        self.assertEqual(building.building_type_id, b_type)

    def test_default_values(self):
        """Test the default values of BuildingComponent."""
        pos = (0, 0)
        dims = (1, 1)
        building = BuildingComponent(position=pos, dimensions=dims)
        self.assertEqual(building.position, pos)
        self.assertEqual(building.dimensions, dims)
        self.assertEqual(building.health, 100.0)
        self.assertEqual(building.max_health, 100.0)
        self.assertEqual(building.construction_progress, 0.0)
        self.assertFalse(building.is_constructed)
        self.assertEqual(building.level, 1)
        self.assertEqual(building.upgrades, {})
        self.assertEqual(building.construction_cost, {})
        self.assertEqual(building.construction_time, 10.0)
        self.assertEqual(building.building_type_id, "")

    def test_construction_state(self):
        """Test the construction state properties."""
        building = BuildingComponent(position=(0,0), dimensions=(1,1))
        self.assertFalse(building.is_constructed)
        self.assertEqual(building.construction_progress, 0.0)

        building.is_constructed = True
        building.construction_progress = 1.0
        self.assertTrue(building.is_constructed)
        self.assertEqual(building.construction_progress, 1.0)

    def test_level_and_upgrades(self):
        """Test the level and upgrades properties."""
        building = BuildingComponent(position=(0,0), dimensions=(1,1))
        self.assertEqual(building.level, 1)
        self.assertEqual(building.upgrades, {})

        building.level = 3
        building.upgrades["efficiency"] = 2
        self.assertEqual(building.level, 3)
        self.assertEqual(building.upgrades, {"efficiency": 2})

class TestResourceComponent(unittest.TestCase):

    def test_initialization_defaults(self):
        """Test default initialization of ResourceComponent."""
        rc = ResourceComponent()
        self.assertEqual(rc.current_resources, {"wood": 0.0, "stone": 0.0, "gold": 0.0, "food": 0.0})
        self.assertEqual(rc.storage_capacity, {"wood": 1000.0, "stone": 1000.0, "gold": 5000.0, "food": 500.0})
        self.assertEqual(rc.production_rates, {"wood": 0.0, "stone": 0.0, "gold": 0.0, "food": 0.0})
        self.assertEqual(rc.production_modifiers, {"wood": 1.0, "stone": 1.0, "gold": 1.0, "food": 1.0})

    def test_initialization_custom(self):
        """Test custom initialization of ResourceComponent."""
        current = {"wood": 100.0, "gold": 50.0}
        capacity = {"wood": 500.0}
        rates = {"wood": 5.0, "food": -1.0}
        modifiers = {"wood": 1.2}
        rc = ResourceComponent(
            current_resources=current,
            storage_capacity=capacity,
            production_rates=rates,
            production_modifiers=modifiers
        )
        # Les dictionnaires sont fusionnés avec les valeurs par défaut si des clés manquent
        self.assertEqual(rc.current_resources, {"wood": 100.0, "stone": 0.0, "gold": 50.0, "food": 0.0})
        self.assertEqual(rc.storage_capacity, {"wood": 500.0, "stone": 1000.0, "gold": 5000.0, "food": 500.0})
        self.assertEqual(rc.production_rates, {"wood": 5.0, "stone": 0.0, "gold": 0.0, "food": -1.0})
        self.assertEqual(rc.production_modifiers, {"wood": 1.2, "stone": 1.0, "gold": 1.0, "food": 1.0})


    def test_effective_production_rate(self):
        """Test calculation of effective production rate."""
        rc = ResourceComponent(
            production_rates={"wood": 10.0, "stone": 5.0},
            production_modifiers={"wood": 1.5, "gold": 0.8} # Bonus bois, malus or (non produit)
        )
        self.assertAlmostEqual(rc.get_effective_production_rate("wood"), 15.0) # 10 * 1.5
        self.assertAlmostEqual(rc.get_effective_production_rate("stone"), 5.0) # 5 * 1.0 (default modifier)
        self.assertAlmostEqual(rc.get_effective_production_rate("gold"), 0.0) # 0 * 0.8
        self.assertAlmostEqual(rc.get_effective_production_rate("food"), 0.0) # 0 * 1.0 (default modifier)
        self.assertAlmostEqual(rc.get_effective_production_rate("unknown"), 0.0) # Unknown resource

    def test_add_resources_within_capacity(self):
        """Test adding resources below or at capacity."""
        rc = ResourceComponent(
            current_resources={"wood": 100.0, "stone": 950.0},
            storage_capacity={"wood": 200.0, "stone": 1000.0}
        )
        rc.add_resources({"wood": 50.0, "stone": 50.0})
        self.assertEqual(rc.current_resources["wood"], 150.0)
        self.assertEqual(rc.current_resources["stone"], 1000.0)

    def test_add_resources_exceeding_capacity(self):
        """Test adding resources exceeding capacity."""
        rc = ResourceComponent(
            current_resources={"wood": 150.0, "gold": 4900.0},
            storage_capacity={"wood": 200.0, "gold": 5000.0}
        )
        rc.add_resources({"wood": 100.0, "gold": 200.0})
        self.assertEqual(rc.current_resources["wood"], 200.0) # Capped at capacity
        self.assertEqual(rc.current_resources["gold"], 5000.0) # Capped at capacity

    def test_add_resources_new_type(self):
        """Test adding a resource type not initially present (should use default capacity)."""
        rc = ResourceComponent() # Defaults: wood=0, capacity=1000
        rc.add_resources({"iron": 50.0}) # Iron not in defaults
        # It should not add iron as it's not a defined resource type in the component
        self.assertNotIn("iron", rc.current_resources)
        # Let's test adding a defined type
        rc.add_resources({"wood": 50.0})
        self.assertEqual(rc.current_resources["wood"], 50.0)


    def test_can_afford(self):
        """Test the can_afford method."""
        rc = ResourceComponent(current_resources={"wood": 100.0, "stone": 50.0})
        self.assertTrue(rc.can_afford({"wood": 50.0}))
        self.assertTrue(rc.can_afford({"wood": 100.0, "stone": 50.0}))
        self.assertFalse(rc.can_afford({"wood": 101.0}))
        self.assertFalse(rc.can_afford({"wood": 50.0, "stone": 51.0}))
        self.assertFalse(rc.can_afford({"gold": 10.0})) # Cannot afford resource not present
        self.assertTrue(rc.can_afford({})) # Can always afford nothing

    def test_spend_resources_sufficient(self):
        """Test spending resources when affordable."""
        rc = ResourceComponent(current_resources={"wood": 100.0, "stone": 50.0})
        cost = {"wood": 30.0, "stone": 20.0}
        can_spend = rc.spend_resources(cost)
        self.assertTrue(can_spend)
        self.assertEqual(rc.current_resources["wood"], 70.0)
        self.assertEqual(rc.current_resources["stone"], 30.0)

    def test_spend_resources_insufficient(self):
        """Test spending resources when not affordable."""
        rc = ResourceComponent(current_resources={"wood": 20.0, "stone": 50.0})
        initial_wood = rc.current_resources["wood"]
        initial_stone = rc.current_resources["stone"]
        cost = {"wood": 30.0, "stone": 20.0}
        can_spend = rc.spend_resources(cost)
        self.assertFalse(can_spend)
        # Resources should not change
        self.assertEqual(rc.current_resources["wood"], initial_wood)
        self.assertEqual(rc.current_resources["stone"], initial_stone)

class TestDefenseComponent(unittest.TestCase):

    def test_initialization_defaults(self):
        """Test default initialization of DefenseComponent."""
        dc = DefenseComponent()
        self.assertEqual(dc.defense_points, 100.0)
        self.assertEqual(dc.max_defense_points, 100.0)
        self.assertEqual(dc.resistance, {})
        self.assertFalse(dc.can_attack)
        self.assertEqual(dc.attack_range, 0.0)
        self.assertEqual(dc.base_damage, 10.0)
        self.assertEqual(dc.attack_speed, 1.0)
        self.assertEqual(dc.damage_types, [])
        self.assertEqual(dc.ammunition, -1)
        self.assertEqual(dc.max_ammunition, -1)
        self.assertEqual(dc.priority_targets, [])

    def test_initialization_custom(self):
        """Test custom initialization of DefenseComponent."""
        res = {"physical": 0.2}
        dmg_types = ["fire"]
        targets = ["goblin"]
        dc = DefenseComponent(
            defense_points=150.0,
            max_defense_points=200.0,
            resistance=res,
            can_attack=True,
            attack_range=5.0,
            base_damage=25.0,
            attack_speed=0.5,
            damage_types=dmg_types,
            ammunition=10,
            max_ammunition=20,
            priority_targets=targets
        )
        self.assertEqual(dc.defense_points, 150.0)
        self.assertEqual(dc.max_defense_points, 200.0)
        self.assertEqual(dc.resistance, res)
        self.assertTrue(dc.can_attack)
        self.assertEqual(dc.attack_range, 5.0)
        self.assertEqual(dc.base_damage, 25.0)
        self.assertEqual(dc.attack_speed, 0.5)
        self.assertEqual(dc.damage_types, dmg_types)
        self.assertEqual(dc.ammunition, 10)
        self.assertEqual(dc.max_ammunition, 20)
        self.assertEqual(dc.priority_targets, targets)

    def test_take_damage_no_resistance(self):
        """Test taking damage without specific resistance."""
        dc = DefenseComponent(defense_points=100.0)
        dc.take_damage(30.0, "physical")
        self.assertEqual(dc.defense_points, 70.0)
        dc.take_damage(80.0, "fire") # Should bring to 0
        self.assertEqual(dc.defense_points, 0.0)
        dc.take_damage(10.0) # Damage below zero
        self.assertEqual(dc.defense_points, 0.0)

    def test_take_damage_with_resistance(self):
        """Test taking damage with resistance."""
        dc = DefenseComponent(defense_points=100.0, resistance={"physical": 0.2, "fire": 1.0}) # 20% physical, 100% fire resist
        dc.take_damage(50.0, "physical") # 50 * (1 - 0.2) = 40 damage
        self.assertEqual(dc.defense_points, 60.0)
        dc.take_damage(1000.0, "fire") # 1000 * (1 - 1.0) = 0 damage
        self.assertEqual(dc.defense_points, 60.0)
        dc.take_damage(10.0, "magic") # No resistance for magic, 10 damage
        self.assertEqual(dc.defense_points, 50.0)

    def test_repair(self):
        """Test the repair method."""
        dc = DefenseComponent(defense_points=50.0, max_defense_points=150.0)
        dc.repair(30.0)
        self.assertEqual(dc.defense_points, 80.0)
        dc.repair(100.0) # Should cap at max_defense_points
        self.assertEqual(dc.defense_points, 150.0)
        dc.repair(10.0) # Repairing at max health
        self.assertEqual(dc.defense_points, 150.0)

    def test_can_fire(self):
        """Test the can_fire method."""
        # Cannot attack by default
        dc_no_attack = DefenseComponent(can_attack=False)
        self.assertFalse(dc_no_attack.can_fire())

        # Can attack, infinite ammo
        dc_infinite = DefenseComponent(can_attack=True, ammunition=-1)
        self.assertTrue(dc_infinite.can_fire())

        # Can attack, has ammo
        dc_has_ammo = DefenseComponent(can_attack=True, ammunition=5)
        self.assertTrue(dc_has_ammo.can_fire())

        # Can attack, no ammo
        dc_no_ammo = DefenseComponent(can_attack=True, ammunition=0)
        self.assertFalse(dc_no_ammo.can_fire())

    def test_consume_ammo(self):
        """Test the consume_ammo method."""
        # Infinite ammo
        dc_infinite = DefenseComponent(can_attack=True, ammunition=-1)
        dc_infinite.consume_ammo()
        self.assertEqual(dc_infinite.ammunition, -1) # Should not change

        # Finite ammo
        dc_finite = DefenseComponent(can_attack=True, ammunition=5)
        dc_finite.consume_ammo()
        self.assertEqual(dc_finite.ammunition, 4)
        dc_finite.consume_ammo()
        self.assertEqual(dc_finite.ammunition, 3)

        # No ammo
        dc_no_ammo = DefenseComponent(can_attack=True, ammunition=0)
        dc_no_ammo.consume_ammo()
        self.assertEqual(dc_no_ammo.ammunition, 0) # Should not go below 0

        # Cannot attack
        dc_no_attack = DefenseComponent(can_attack=False, ammunition=10)
        dc_no_attack.consume_ammo()
        self.assertEqual(dc_no_attack.ammunition, 10) # Should not consume if cannot attack

class TestCityGridComponent(unittest.TestCase):

    def test_initialization(self):
        """Test grid initialization with default and custom sizes."""
        grid_default = CityGridComponent()
        self.assertEqual(grid_default.width, 50)
        self.assertEqual(grid_default.height, 50)
        self.assertEqual(len(grid_default.grid), 50)
        self.assertEqual(len(grid_default.grid[0]), 50)
        self.assertIsInstance(grid_default.grid[0][0], GridCell)
        self.assertTrue(grid_default.grid[0][0].is_buildable)
        self.assertIsNone(grid_default.grid[0][0].building_entity_id)
        self.assertFalse(grid_default.grid[0][0].is_road)

        grid_custom = CityGridComponent(width=10, height=5)
        self.assertEqual(grid_custom.width, 10)
        self.assertEqual(grid_custom.height, 5)
        self.assertEqual(len(grid_custom.grid), 5)
        self.assertEqual(len(grid_custom.grid[0]), 10)

    def test_is_valid_coordinate(self):
        """Test coordinate validation."""
        grid = CityGridComponent(width=10, height=10)
        self.assertTrue(grid.is_valid_coordinate(0, 0))
        self.assertTrue(grid.is_valid_coordinate(9, 9))
        self.assertTrue(grid.is_valid_coordinate(5, 5))
        self.assertFalse(grid.is_valid_coordinate(-1, 5))
        self.assertFalse(grid.is_valid_coordinate(5, -1))
        self.assertFalse(grid.is_valid_coordinate(10, 5))
        self.assertFalse(grid.is_valid_coordinate(5, 10))

    def test_can_build_at_empty_grid(self):
        """Test build possibility on an empty grid."""
        grid = CityGridComponent(width=10, height=10)
        self.assertTrue(grid.can_build_at(0, 0, 1, 1))
        self.assertTrue(grid.can_build_at(0, 0, 3, 3))
        self.assertTrue(grid.can_build_at(7, 7, 3, 3)) # Fits exactly at the corner
        # Out of bounds
        self.assertFalse(grid.can_build_at(8, 8, 3, 3)) # Exceeds width and height
        self.assertFalse(grid.can_build_at(0, 8, 1, 3)) # Exceeds height
        self.assertFalse(grid.can_build_at(8, 0, 3, 1)) # Exceeds width
        self.assertFalse(grid.can_build_at(10, 0, 1, 1)) # Starts out of bounds (x)
        self.assertFalse(grid.can_build_at(0, 10, 1, 1)) # Starts out of bounds (y)

    def test_can_build_at_occupied_cell(self):
        """Test build possibility when a cell is occupied."""
        grid = CityGridComponent(width=10, height=10)
        grid.grid[1][1].building_entity_id = 1 # Occupy cell (1, 1)
        grid.grid[1][1].is_buildable = False
        self.assertFalse(grid.can_build_at(1, 1, 1, 1)) # Cannot build on occupied cell
        self.assertFalse(grid.can_build_at(0, 0, 2, 2)) # Building overlaps occupied cell
        self.assertTrue(grid.can_build_at(0, 0, 1, 1)) # Can build next to it
        self.assertTrue(grid.can_build_at(2, 1, 1, 1)) # Can build next to it

    def test_can_build_at_non_buildable_cell(self):
        """Test build possibility when a cell is marked non-buildable."""
        grid = CityGridComponent(width=10, height=10)
        grid.grid[2][2].is_buildable = False
        self.assertFalse(grid.can_build_at(2, 2, 1, 1))
        self.assertFalse(grid.can_build_at(1, 1, 3, 3)) # Overlaps non-buildable cell
        self.assertTrue(grid.can_build_at(0, 0, 2, 2))

    def test_can_build_on_road(self):
        """Test build possibility on a road cell."""
        grid = CityGridComponent(width=10, height=10)
        grid.add_road(3, 3)
        self.assertFalse(grid.can_build_at(3, 3, 1, 1)) # Cannot build directly on road
        self.assertFalse(grid.can_build_at(2, 2, 2, 2)) # Cannot build overlapping road

    def test_place_building_success(self):
        """Test successfully placing a building."""
        grid = CityGridComponent(width=10, height=10)
        entity_id = 123
        grid.place_building(2, 3, 2, 2, entity_id)
        # Check all cells occupied by the building
        for r in range(3, 5):
            for c in range(2, 4):
                cell = grid.grid[r][c]
                self.assertEqual(cell.building_entity_id, entity_id)
                self.assertFalse(cell.is_buildable)
        # Check adjacent cell is still buildable
        self.assertTrue(grid.grid[3][4].is_buildable)
        self.assertIsNone(grid.grid[3][4].building_entity_id)

    def test_place_building_failure(self):
        """Test failing to place a building due to collision."""
        grid = CityGridComponent(width=10, height=10)
        grid.place_building(1, 1, 2, 2, 1) # Place building 1
        initial_cell_state = grid.grid[2][2].building_entity_id

        grid.place_building(2, 2, 2, 2, 2) # Attempt to place overlapping building 2
        # Check that the overlapping cell (2, 2) still belongs to building 1
        self.assertEqual(grid.grid[2][2].building_entity_id, initial_cell_state)
        self.assertEqual(grid.grid[2][2].building_entity_id, 1)
        # Check that no part of building 2 was placed
        self.assertIsNone(grid.grid[3][3].building_entity_id)

    def test_remove_building(self):
        """Test removing a placed building."""
        grid = CityGridComponent(width=10, height=10)
        entity_id = 456
        x, y, w, h = 4, 5, 3, 2
        grid.place_building(x, y, w, h, entity_id)
        # Verify placement first
        self.assertEqual(grid.grid[y][x].building_entity_id, entity_id)
        self.assertFalse(grid.grid[y][x].is_buildable)

        grid.remove_building(x, y, w, h)
        # Verify removal
        for r in range(y, y + h):
            for c in range(x, x + w):
                cell = grid.grid[r][c]
                self.assertIsNone(cell.building_entity_id)
                self.assertTrue(cell.is_buildable)

    def test_add_road(self):
        """Test adding a road."""
        grid = CityGridComponent(width=10, height=10)
        grid.add_road(5, 5)
        cell = grid.grid[5][5]
        self.assertTrue(cell.is_road)
        self.assertFalse(cell.is_buildable)
        self.assertIsNone(cell.building_entity_id)

    def test_add_road_on_building(self):
        """Test adding a road on an occupied cell (should fail silently or log)."""
        grid = CityGridComponent(width=10, height=10)
        grid.place_building(5, 5, 1, 1, 789)
        grid.add_road(5, 5) # Attempt to add road on building
        cell = grid.grid[5][5]
        self.assertFalse(cell.is_road) # Should still be part of the building
        self.assertFalse(cell.is_buildable)
        self.assertEqual(cell.building_entity_id, 789)

    def test_remove_road(self):
        """Test removing a road."""
        grid = CityGridComponent(width=10, height=10)
        grid.add_road(6, 7)
        # Verify road exists
        self.assertTrue(grid.grid[7][6].is_road)
        self.assertFalse(grid.grid[7][6].is_buildable)

        grid.remove_road(6, 7)
        # Verify road is removed
        cell = grid.grid[7][6]
        self.assertFalse(cell.is_road)
        self.assertTrue(cell.is_buildable) # Should become buildable again
        self.assertIsNone(cell.building_entity_id)

if __name__ == '__main__':
    unittest.main()