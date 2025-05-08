#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for building destruction mechanics
"""

import sys
import os
import math
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData, TextNode, CardMaker

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - Building Destruction")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.city_automation import BuildingType, BuildingState, ResourceType
from game.city_buildings import create_building
from game.enemy import BuildingRaider

class MockPlayer:
    """Mock player for testing"""
    
    def __init__(self, position=Vec3(0, 0, 0)):
        """Initialize the player"""
        self.position = position
        self.health = 100
        self.max_health = 100
        
    def take_damage(self, amount, source=None):
        """Take damage"""
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"Player took {amount} damage, health: {self.health}/{self.max_health}")

class MockGame:
    """Mock game for testing"""
    
    def __init__(self, app):
        """Initialize mock game"""
        self.render = app.render
        self.loader = app.loader
        self.player = MockPlayer(Vec3(0, 0, 0))
        
        # Simple task manager (for testing)
        self.taskMgr = TaskManager()

class TaskManager:
    """Simple task manager for testing"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks = []
        
    def add(self, func, name):
        """Add a task"""
        self.tasks.append((func, name))
        print(f"Added task: {name}")
        return self
        
    def doMethodLater(self, delay, func, name):
        """Schedule a task for later"""
        print(f"Scheduled task: {name} after {delay} seconds")
        return self

class CityManager:
    """Simple city manager for testing"""
    
    def __init__(self, game):
        """Initialize the city manager"""
        self.game = game
        self.render = game.render
        self.grid_size = 50
        from game.city_automation import CityGrid, ResourceManager
        self.grid = CityGrid(20, 20)
        self.resource_manager = ResourceManager()
        self.buildings = {}
        self.next_building_id = 1
        
        # City center position
        self.city_center = (10, 10)
        
    def create_building(self, building_type, position):
        """Create a new building"""
        building_id = f"building_{self.next_building_id}"
        self.next_building_id += 1
        
        building = create_building(building_type, building_id, position)
        
        # Try to place on grid
        if self.grid.place_building(building):
            self.buildings[building_id] = building
            
            # Create visual representation
            building.create_visual_representation(self.render, self)
            
            print(f"Created {building.name} at {position}")
            return building
        
        print(f"Failed to place {building_type.value} at {position}")
        return None
    
    def update(self, dt):
        """Update city state"""
        # Update resources
        self.resource_manager.update(dt)
        
        # Update buildings
        for building in self.buildings.values():
            building.update(dt, self)
    
    def grid_to_world(self, grid_pos):
        """Convert grid position to world position"""
        return (grid_pos[0] * 2 - 20, grid_pos[1] * 2 - 20, 0)
    
    def world_to_grid(self, world_pos):
        """Convert world position to grid position"""
        if hasattr(world_pos, 'getX'):
            x = int((world_pos.getX() + 20) / 2)
            y = int((world_pos.getY() + 20) / 2)
        else:
            x = int((world_pos[0] + 20) / 2)
            y = int((world_pos[1] + 20) / 2)
            
        return (x, y)
    
    def on_building_completed(self, building):
        """Handle building completion"""
        print(f"Building completed: {building.name}")
        
        # Update resource rates
        for resource_type, amount in building.production.items():
            self.resource_manager.update_rate(resource_type, amount)
            
        for resource_type, amount in building.consumption.items():
            self.resource_manager.update_rate(resource_type, -amount)
            
        # Update storage capacity
        for resource_type, amount in building.storage.items():
            self.resource_manager.increase_capacity(resource_type, amount)
    
    def on_building_upgraded(self, building):
        """Handle building upgrade"""
        print(f"Building upgraded: {building.name} to level {building.level}")
    
    def on_building_destroyed(self, building):
        """Handle building destruction"""
        print(f"Building destroyed: {building.name}")
        
        # Trigger any events
        if hasattr(self.game, 'event_manager'):
            self.game.event_manager.trigger_event('building_destroyed', {
                'building': building,
                'position': building.position,
                'building_type': building.building_type
            })
    
    def damage_building(self, building, amount, source=None):
        """
        Damage a building and handle destruction if needed
        
        Args:
            building: The building to damage
            amount: Amount of damage
            source: Entity that caused the damage (optional)
            
        Returns:
            bool: True if building was destroyed
        """
        print(f"{building.name} taking {amount:.1f} damage, health: {building.health:.1f}/{building.max_health:.1f}")
        was_destroyed = building.take_damage(amount, source)
        
        if was_destroyed:
            building.on_destroyed(self)
        elif building.state == BuildingState.DAMAGED and building.node_path:
            # Update visual effects to show damage
            building._update_visual_effects(self)
            
        return was_destroyed
    
    def setup_city(self):
        """Set up a test city"""
        # Add initial resources
        for resource_type in ResourceType:
            self.resource_manager.add_resource(resource_type, 100)
        
        # Create buildings around the city center
        
        # House
        house = self.create_building(BuildingType.HOUSE, (9, 9))
        if house:
            house.construction_progress = 100
            house._on_construction_complete(self)
            house.assign_workers(3)
        
        # Farm
        farm = self.create_building(BuildingType.FARM, (12, 9))
        if farm:
            farm.construction_progress = 100
            farm._on_construction_complete(self)
            farm.assign_workers(5)
        
        # Tower
        tower = self.create_building(BuildingType.TOWER, (7, 12))
        if tower:
            tower.construction_progress = 100
            tower._on_construction_complete(self)
            tower.assign_workers(2)
        
        # Storage
        storage = self.create_building(BuildingType.STORAGE, (14, 12))
        if storage:
            storage.construction_progress = 100
            storage._on_construction_complete(self)

class TestApp(ShowBase):
    """Test application for building destruction"""
    
    def __init__(self):
        """Initialize the test application"""
        super().__init__()
        
        # Create the game instance
        self.game = MockGame(self)
        
        # Create city manager
        self.game.city_manager = CityManager(self.game)
        
        # Setup city
        self.game.city_manager.setup_city()
        
        # Setup ground
        self.setup_ground()
        
        # Setup camera
        self.setup_camera()
        
        # Setup controls
        self.setup_controls()
        
        # Setup UI
        self.setup_ui()
        
        # Setup grid visualization
        self.setup_grid()
        
        # Create raiders that will attack buildings
        self.raiders = []
        
        # Add update task
        self.taskMgr.add(self.update, "update_test")
    
    def setup_ground(self):
        """Setup a simple ground plane"""
        cm = CardMaker("ground")
        cm.setFrame(-50, 50, -50, 50)
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)  # Rotate to be horizontal
        ground.setPos(0, 0, -0.1)
        ground.setColor(0.3, 0.5, 0.2, 1)  # Green
    
    def setup_camera(self):
        """Setup the camera"""
        self.disableMouse()
        self.camera.setPos(0, -40, 30)
        self.camera.setHpr(0, -30, 0)
    
    def setup_controls(self):
        """Setup controls"""
        self.accept("escape", sys.exit)
        self.accept("r", self.spawn_raider)
        self.accept("t", self.spawn_raiders_around_city)
        self.accept("b", self.attack_random_building)
        
        # Camera controls
        self.accept("w", self.move_camera, [0, 5, 0])
        self.accept("s", self.move_camera, [0, -5, 0])
        self.accept("a", self.move_camera, [-5, 0, 0])
        self.accept("d", self.move_camera, [5, 0, 0])
        self.accept("q", self.move_camera, [0, 0, 5])
        self.accept("e", self.move_camera, [0, 0, -5])
    
    def move_camera(self, x, y, z):
        """Move camera by offset"""
        self.camera.setPos(self.camera.getPos() + Vec3(x, y, z))
    
    def setup_ui(self):
        """Setup UI elements"""
        from direct.gui.OnscreenText import OnscreenText
        
        # Title
        self.title = OnscreenText(
            text="Building Destruction Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Instructions
        self.instructions = OnscreenText(
            text="Press R to spawn a raider\n"
                 "Press T to spawn raiders around the city\n"
                 "Press B to test attack on random building\n"
                 "Use W/A/S/D/Q/E to move camera",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
    
    def setup_grid(self):
        """Setup a grid visualization"""
        grid_node = self.render.attachNewNode("grid")
        
        # Create grid lines
        for i in range(-10, 11):
            # Horizontal line
            cm = CardMaker(f"h_line_{i}")
            cm.setFrame(-20, 20, 0, 0.05)
            line = grid_node.attachNewNode(cm.generate())
            line.setPos(-20, i * 2, 0.05)
            line.setColor(0.5, 0.5, 0.5, 0.3)
            
            # Vertical line
            cm = CardMaker(f"v_line_{i}")
            cm.setFrame(0, 0.05, -20, 20)
            line = grid_node.attachNewNode(cm.generate())
            line.setPos(i * 2, -20, 0.05)
            line.setColor(0.5, 0.5, 0.5, 0.3)
    
    def spawn_raider(self):
        """Spawn a building raider enemy"""
        # Create raider at a random position outside the city
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(25, 35)
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        
        raider = BuildingRaider(self.game, Vec3(x, y, 0))
        
        # Add to raiders list
        self.raiders.append(raider)
        
        print(f"Spawned raider at ({x:.1f}, {y:.1f})")
    
    def spawn_raiders_around_city(self):
        """Spawn multiple raiders around the city"""
        # Create 5 raiders at different positions around the city
        for i in range(5):
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(25, 35)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            
            raider = BuildingRaider(self.game, Vec3(x, y, 0))
            
            # Add to raiders list
            self.raiders.append(raider)
            
        print(f"Spawned 5 raiders around the city")
    
    def attack_random_building(self):
        """Test attack on a random building"""
        if not self.game.city_manager.buildings:
            print("No buildings to attack")
            return
            
        building = random.choice(list(self.game.city_manager.buildings.values()))
        
        print(f"Testing attack on {building.name}")
        
        # Apply some damage
        self.game.city_manager.damage_building(building, 30, None)
    
    def update(self, task):
        """Update function called every frame"""
        dt = task.time - task.last if hasattr(task, 'last') else 0.033
        task.last = task.time
        
        # Update city
        self.game.city_manager.update(dt)
        
        # Update raiders
        for raider in self.raiders[:]:
            raider.update(dt)
            
            # Remove dead raiders
            if raider.health <= 0:
                raider.root.removeNode()
                self.raiders.remove(raider)
        
        return task.cont
        
def main():
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 