#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for City Automation System
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData, Plane, Point3, TextNode

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure Panda3D settings
loadPrcFileData("", "window-title Test - City Automation")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "sync-video 1")

# Import game modules
from game.city_automation import (
    BuildingType, BuildingState, ResourceType,
    Building, CityGrid, ResourceManager
)
from game.city_buildings import create_building

class MockGame:
    """Mock game for testing"""
    
    def __init__(self):
        """Initialize mock game"""
        self.entity_manager = type('obj', (object,), {
            'enemies': {}
        })
        
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
        self.grid = CityGrid(20, 20)
        self.resource_manager = ResourceManager()
        self.buildings = {}
        self.next_building_id = 1
        self.render = None
        
    def create_building(self, building_type, position):
        """Create a new building"""
        building_id = f"building_{self.next_building_id}"
        self.next_building_id += 1
        
        building = create_building(building_type, building_id, position)
        
        # Try to place on grid
        if self.grid.place_building(building):
            self.buildings[building_id] = building
            
            # Create visual representation if render is available
            if self.render:
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
        return (grid_pos[0] * 2, grid_pos[1] * 2, 0)
    
    def world_to_grid(self, world_pos):
        """Convert world position to grid position"""
        # Get x and y from Vec3 or Point3
        if hasattr(world_pos, 'getX'):
            x = int(world_pos.getX() / 2)
            y = int(world_pos.getY() / 2)
        else:
            x = int(world_pos[0] / 2)
            y = int(world_pos[1] / 2)
            
        # Ensure within grid bounds
        x = max(0, min(x, self.grid.width - 1))
        y = max(0, min(y, self.grid.height - 1))
        
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
            
        # Update visual effects
        if self.render and building.node_path:
            building._update_visual_effects(self)
    
    def on_building_upgraded(self, building):
        """Handle building upgrade"""
        print(f"Building upgraded: {building.name} to level {building.level}")
        
        # Update visual effects
        if self.render and building.node_path:
            building._update_visual_effects(self)
            
    def on_building_destroyed(self, building):
        """Handle building destruction"""
        print(f"City manager handling destruction of {building.name}")
        
        # Reverse resource rates
        for resource_type, amount in building.production.items():
            self.resource_manager.update_rate(resource_type, -amount)
            
        for resource_type, amount in building.consumption.items():
            self.resource_manager.update_rate(resource_type, amount)
        
        # Update visual effects
        if self.render and building.node_path:
            building._update_visual_effects(self)
            
    def create_visual_representations(self):
        """Create visual representations for all buildings"""
        if not self.render:
            return
            
        # Create building visualizations
        for building in self.buildings.values():
            building.create_visual_representation(self.render, self)

class TestApp(ShowBase):
    """Test application for city automation"""
    
    def __init__(self):
        """Initialize test application"""
        super().__init__()
        
        # Create mock game
        self.game = MockGame()
        
        # Create city manager
        self.city_manager = CityManager(self.game)
        self.city_manager.render = self.render
        
        # Set up a simple scene
        self.setup_scene()
        
        # Set up camera and controls
        self.setup_camera()
        self.setup_controls()
        
        # Set up UI
        self.setup_ui()
        
        # Add city grid
        self.grid_model = None
        self.setup_grid()
        
        # Run initial tests
        self.run_tests()
        
        # Create visual representations for all buildings
        self.city_manager.create_visual_representations()
        
        # Set up update task
        self.taskMgr.add(self.update, "update_city")
        
    def setup_scene(self):
        """Set up a simple test scene"""
        # Create ground
        ground = self.loader.loadModel("models/box")
        ground.setScale(50, 50, 0.1)
        ground.setPos(0, 0, -0.1)
        ground.setColor((0.3, 0.5, 0.2, 1))  # Green color
        ground.reparentTo(self.render)
        
    def setup_camera(self):
        """Set up the camera"""
        self.disableMouse()
        self.camera.setPos(20, -40, 30)
        self.camera.lookAt(20, 20, 0)
        
    def setup_controls(self):
        """Set up controls"""
        # Add key bindings
        self.accept("escape", sys.exit)
        self.accept("1", self.test_create_buildings)
        self.accept("2", self.test_resource_production)
        self.accept("3", self.test_building_upgrade)
        self.accept("space", self.run_tests)
        
        # Camera controls
        self.accept("w", self.move_camera, [0, 2, 0])
        self.accept("s", self.move_camera, [0, -2, 0])
        self.accept("a", self.move_camera, [-2, 0, 0])
        self.accept("d", self.move_camera, [2, 0, 0])
        self.accept("q", self.move_camera, [0, 0, 2])
        self.accept("e", self.move_camera, [0, 0, -2])
        
    def move_camera(self, x, y, z):
        """Move camera by offset"""
        self.camera.setPos(self.camera.getPos() + Vec3(x, y, z))
        
    def setup_ui(self):
        """Set up UI elements"""
        from direct.gui.OnscreenText import OnscreenText
        from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
        
        self.title = OnscreenText(
            text="City Automation Test",
            pos=(0, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        self.instructions = OnscreenText(
            text="Press 1-3 to run individual tests, SPACE to run all tests, ESC to exit\n"
                 "W/A/S/D/Q/E to move camera",
            pos=(0, 0.8),
            scale=0.05,
            fg=(1, 1, 0.8, 1),
            shadow=(0, 0, 0, 0.5)
        )
        
        # Resource display frame
        self.resource_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.3, 0.3, -0.25, 0.25),
            pos=(0.7, 0, 0.7)
        )
        
        # Resource labels
        self.resource_labels = {}
        resources = [
            ResourceType.FOOD,
            ResourceType.WOOD,
            ResourceType.STONE,
            ResourceType.GOLD,
            ResourceType.IRON,
            ResourceType.POPULATION,
            ResourceType.ENERGY,
            ResourceType.KNOWLEDGE
        ]
        
        for i, resource in enumerate(resources):
            y_pos = 0.2 - i * 0.05
            
            # Resource name
            DirectLabel(
                text=resource.value.capitalize(),
                scale=0.04,
                pos=(-0.15, 0, y_pos),
                text_align=TextNode.ALeft,
                text_fg=(1, 1, 1, 1),
                parent=self.resource_frame
            )
            
            # Resource value
            self.resource_labels[resource] = DirectLabel(
                text="0",
                scale=0.04,
                pos=(0.15, 0, y_pos),
                text_align=TextNode.ARight,
                text_fg=(1, 1, 0.8, 1),
                parent=self.resource_frame
            )
        
        # Setup building UI
        self.setup_building_ui()
        
        # Setup mouse picking for building placement
        self.accept("mouse1", self.handle_building_placement)
    
    def setup_building_ui(self):
        """Set up UI for building placement"""
        from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
        
        # Building selection frame
        self.building_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.8),
            frameSize=(-0.3, 0.3, -0.35, 0.05),
            pos=(-0.7, 0, 0.7)
        )
        
        # Title
        DirectLabel(
            text="Buildings",
            scale=0.05,
            pos=(0, 0, 0),
            text_fg=(1, 1, 1, 1),
            parent=self.building_frame
        )
        
        # Current selection
        self.selected_building_type = None
        self.selected_building_label = DirectLabel(
            text="None Selected",
            scale=0.04,
            pos=(0, 0, -0.07),
            text_fg=(1, 1, 0.8, 1),
            parent=self.building_frame
        )
        
        # Building buttons
        button_width = 0.12
        button_height = 0.06
        spacing = 0.02
        
        # Row 1
        DirectButton(
            text="House",
            scale=0.04,
            frameSize=(-button_width, button_width, -button_height, button_height),
            pos=(-0.15, 0, -0.15),
            command=self.select_building,
            extraArgs=[BuildingType.HOUSE],
            parent=self.building_frame
        )
        
        DirectButton(
            text="Farm",
            scale=0.04,
            frameSize=(-button_width, button_width, -button_height, button_height),
            pos=(0.15, 0, -0.15),
            command=self.select_building,
            extraArgs=[BuildingType.FARM],
            parent=self.building_frame
        )
        
        # Row 2
        DirectButton(
            text="Tower",
            scale=0.04,
            frameSize=(-button_width, button_width, -button_height, button_height),
            pos=(-0.15, 0, -0.15 - spacing - button_height * 2),
            command=self.select_building,
            extraArgs=[BuildingType.TOWER],
            parent=self.building_frame
        )
        
        DirectButton(
            text="Storage",
            scale=0.04,
            frameSize=(-button_width, button_width, -button_height, button_height),
            pos=(0.15, 0, -0.15 - spacing - button_height * 2),
            command=self.select_building,
            extraArgs=[BuildingType.STORAGE],
            parent=self.building_frame
        )
        
        # Cancel button
        DirectButton(
            text="Cancel",
            scale=0.04,
            frameSize=(-button_width, button_width, -button_height, button_height),
            pos=(0, 0, -0.15 - spacing * 2 - button_height * 4),
            command=self.select_building,
            extraArgs=[None],
            parent=self.building_frame
        )
    
    def setup_grid(self):
        """Set up visual grid"""
        # Create a node for the grid
        self.grid_model = self.render.attachNewNode("grid")
        
        # Create grid lines
        for i in range(21):  # 0 to 20
            # Horizontal line
            line = self.loader.loadModel("models/box")
            line.setScale(20, 0.05, 0.05)
            line.setPos(10, i, 0.1)
            line.setColor((0.5, 0.5, 0.5, 1))
            line.reparentTo(self.grid_model)
            
            # Vertical line
            line = self.loader.loadModel("models/box")
            line.setScale(0.05, 20, 0.05)
            line.setPos(i, 10, 0.1)
            line.setColor((0.5, 0.5, 0.5, 1))
            line.reparentTo(self.grid_model)
    
    def select_building(self, building_type):
        """Select a building type for placement"""
        self.selected_building_type = building_type
        
        if building_type:
            self.selected_building_label['text'] = f"Selected: {building_type.value.capitalize()}"
        else:
            self.selected_building_label['text'] = "None Selected"
    
    def handle_building_placement(self):
        """Handle mouse click for building placement"""
        if hasattr(base, 'mouseWatcherNode') and base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            
            # Ray casting for picking
            pickerRay = base.camLens.makeRay(mpos.getX(), mpos.getY())
            
            # Transform to world coordinates
            pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            
            # Get intersection with XY plane (Z=0)
            plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
            entry = plane.intersectsLine(
                Point3(0, 0, 0) + base.camera.getPos(render),
                Point3(0, 0, 0) + base.camera.getPos(render) + pickerRay.getDirection() * 1000
            )
            
            if entry:
                # Convert to grid coordinates
                world_pos = entry
                grid_pos = self.city_manager.world_to_grid(world_pos)
                
                # Check if there's already a building there
                existing_building = self.city_manager.grid.get_building_at(grid_pos)
                
                if existing_building:
                    # Building exists - check if we can repair/upgrade it
                    self.show_building_actions(existing_building, grid_pos)
                elif self.selected_building_type:
                    # No building - try to place a new one
                    print(f"Attempting to place {self.selected_building_type.value} at grid position {grid_pos}")
                    building = self.city_manager.create_building(self.selected_building_type, grid_pos)
                    
                    if building:
                        print(f"Building placed: {building.name} at {grid_pos}")
                        
                        # Immediately start construction
                        building.construction_progress = 0  # Reset to ensure visual effect
                        if self.city_manager.render:
                            building._update_visual_effects(self.city_manager)
    
    def show_building_actions(self, building, grid_pos):
        """Show action menu for an existing building"""
        from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
        
        # Remove any existing menu
        if hasattr(self, 'action_menu') and self.action_menu:
            self.action_menu.destroy()
        
        # Create menu at mouse position
        self.action_menu = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.9),
            frameSize=(-0.2, 0.2, -0.25, 0.1),
            pos=(0, 0, 0)  # Will be positioned at cursor
        )
        
        # Position at cursor
        if hasattr(base, 'mouseWatcherNode') and base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.action_menu.setPos(render2d, mpos.getX(), 0, mpos.getY())
        
        # Building info
        DirectLabel(
            text=f"{building.name} ({building.state.value})",
            scale=0.04,
            pos=(0, 0, 0.05),
            text_fg=(1, 1, 0.8, 1),
            parent=self.action_menu
        )
        
        # Health info
        health_pct = int(100 * building.health / building.max_health)
        health_color = (0.2, 1.0, 0.2, 1) if health_pct > 50 else (1.0, 0.7, 0.2, 1) if health_pct > 25 else (1.0, 0.3, 0.3, 1)
        
        DirectLabel(
            text=f"Health: {health_pct}%",
            scale=0.035,
            pos=(0, 0, 0.0),
            text_fg=health_color,
            parent=self.action_menu
        )
        
        # Add buttons based on state
        button_width = 0.15
        button_height = 0.05
        
        # Close button
        DirectButton(
            text="Close",
            scale=0.035,
            frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
            pos=(0, 0, -0.2),
            command=self.close_action_menu,
            parent=self.action_menu
        )
        
        # Action buttons
        if building.state == BuildingState.DAMAGED:
            # Repair button for damaged buildings
            DirectButton(
                text="Repair",
                scale=0.035,
                frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
                pos=(-0.1, 0, -0.1),
                command=self.repair_building,
                extraArgs=[building],
                parent=self.action_menu
            )
            
            # Show repair cost
            repair_costs = building.calculate_repair_costs()
            cost_text = "Cost: "
            for resource, amount in repair_costs.items():
                cost_text += f"{resource.value}: {amount}, "
            cost_text = cost_text[:-2]  # Remove last comma and space
            
            DirectLabel(
                text=cost_text,
                scale=0.025,
                pos=(0, 0, -0.15),
                text_fg=(0.7, 0.7, 1.0, 1),
                parent=self.action_menu
            )
            
        elif building.state == BuildingState.DESTROYED:
            # Rebuild button for destroyed buildings
            DirectButton(
                text="Rebuild",
                scale=0.035,
                frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
                pos=(-0.1, 0, -0.1),
                command=self.rebuild_building,
                extraArgs=[building],
                parent=self.action_menu
            )
            
            # Show rebuild cost
            rebuild_costs = building.calculate_repair_costs()
            cost_text = "Cost: "
            for resource, amount in rebuild_costs.items():
                cost_text += f"{resource.value}: {amount}, "
            cost_text = cost_text[:-2]  # Remove last comma and space
            
            DirectLabel(
                text=cost_text,
                scale=0.025,
                pos=(0, 0, -0.15),
                text_fg=(0.7, 0.7, 1.0, 1),
                parent=self.action_menu
            )
            
        elif building.state == BuildingState.OPERATIONAL:
            # Upgrade button for operational buildings
            DirectButton(
                text="Upgrade",
                scale=0.035,
                frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
                pos=(-0.1, 0, -0.1),
                command=self.upgrade_building,
                extraArgs=[building],
                parent=self.action_menu
            )
        
        # Button to add workers if applicable
        if building.worker_capacity > 0:
            # Button to assign workers
            DirectButton(
                text="+Worker",
                scale=0.035,
                frameSize=(-button_width/2, button_width/2, -button_height/2, button_height/2),
                pos=(0.1, 0, -0.1),
                command=self.assign_worker,
                extraArgs=[building],
                parent=self.action_menu
            )
            
            # Show worker count
            DirectLabel(
                text=f"Workers: {building.assigned_workers}/{building.worker_capacity}",
                scale=0.03,
                pos=(0, 0, -0.05),
                text_fg=(0.7, 1.0, 0.7, 1),
                parent=self.action_menu
            )
    
    def close_action_menu(self):
        """Close the building action menu"""
        if hasattr(self, 'action_menu') and self.action_menu:
            self.action_menu.destroy()
            self.action_menu = None
    
    def repair_building(self, building):
        """Repair a damaged building"""
        if building.start_repair(self.city_manager):
            print(f"Repairing {building.name}")
            
            # Close the menu
            self.close_action_menu()
        else:
            print(f"Can't repair {building.name}")
    
    def rebuild_building(self, building):
        """Rebuild a destroyed building"""
        if building.rebuild(self.city_manager):
            print(f"Rebuilding {building.name}")
            
            # Close the menu
            self.close_action_menu()
        else:
            print(f"Can't rebuild {building.name}")
    
    def upgrade_building(self, building):
        """Upgrade an operational building"""
        building.start_upgrade(self.city_manager)
        print(f"Upgrading {building.name}")
        
        # Close the menu
        self.close_action_menu()
    
    def assign_worker(self, building):
        """Assign a worker to the building"""
        # Check if we have available population
        if self.city_manager.resource_manager.consume_resource(ResourceType.POPULATION, 1):
            # Assign one worker
            building.assign_workers(1)
            print(f"Assigned worker to {building.name}. Now has {building.assigned_workers} workers.")
        else:
            print("Not enough population to assign worker")
            
        # Close the menu
        self.close_action_menu()
    
    def update(self, task):
        """Update task"""
        dt = task.time - task.last if hasattr(task, 'last') else 0.033
        task.last = task.time
        
        # Update city
        self.city_manager.update(dt)
        
        # Update UI
        self.update_resource_display()
        
        return task.cont
    
    def update_resource_display(self):
        """Update resource display"""
        for resource, label in self.resource_labels.items():
            amount = self.city_manager.resource_manager.get_resource(resource)
            rate = self.city_manager.resource_manager.get_rate(resource)
            
            # Format as integer if whole number, otherwise show decimal
            if amount == int(amount):
                amount_str = str(int(amount))
            else:
                amount_str = f"{amount:.1f}"
                
            # Add rate indicator
            if rate > 0:
                rate_str = f" (+{rate:.1f})"
                color = (0.2, 1, 0.2, 1)  # Green for positive
            elif rate < 0:
                rate_str = f" ({rate:.1f})"
                color = (1, 0.4, 0.4, 1)  # Red for negative
            else:
                rate_str = ""
                color = (1, 1, 0.8, 1)  # Default color
                
            label['text'] = amount_str + rate_str
            label['text_fg'] = color
    
    def run_tests(self):
        """Run all tests"""
        print("\n===== Running all city automation tests =====")
        
        # Test building creation
        self.test_create_buildings()
        
        # Test resource production
        self.test_resource_production()
        
        # Test building upgrade
        self.test_building_upgrade()
        
        # Test building damage and destruction
        self.test_building_damage()
        
    def test_create_buildings(self):
        """Test creating different buildings"""
        print("\n----- Testing Building Creation -----")
        
        # Add initial resources
        for resource in ResourceType:
            self.city_manager.resource_manager.add_resource(resource, 100)
        
        # Create a house
        house = self.city_manager.create_building(BuildingType.HOUSE, (5, 5))
        if house:
            # Assign workers
            house.assign_workers(3)
            print(f"Assigned {house.assigned_workers} workers to house")
            
            # Quickly complete construction
            house.construction_progress = 100
            house._on_construction_complete(self.city_manager)
            
            # Update visual representation
            if self.city_manager.render:
                house._update_visual_effects(self.city_manager)
        
        # Create a farm
        farm = self.city_manager.create_building(BuildingType.FARM, (8, 5))
        if farm:
            # Assign workers
            farm.assign_workers(5)
            print(f"Assigned {farm.assigned_workers} workers to farm")
            
            # Quickly complete construction
            farm.construction_progress = 100
            farm._on_construction_complete(self.city_manager)
            
            # Update visual representation
            if self.city_manager.render:
                farm._update_visual_effects(self.city_manager)
        
        # Create a tower
        tower = self.city_manager.create_building(BuildingType.TOWER, (3, 8))
        if tower:
            # Assign workers
            tower.assign_workers(2)
            print(f"Assigned {tower.assigned_workers} workers to tower")
            
            # Quickly complete construction
            tower.construction_progress = 100
            tower._on_construction_complete(self.city_manager)
            
            # Update visual representation
            if self.city_manager.render:
                tower._update_visual_effects(self.city_manager)
        
        # Create storage
        storage = self.city_manager.create_building(BuildingType.STORAGE, (10, 10))
        if storage:
            # Quickly complete construction
            storage.construction_progress = 100
            storage._on_construction_complete(self.city_manager)
            
            # Update visual representation
            if self.city_manager.render:
                storage._update_visual_effects(self.city_manager)
    
    def test_resource_production(self):
        """Test resource production and consumption"""
        print("\n----- Testing Resource Production -----")
        
        # Print current rates
        for resource in ResourceType:
            rate = self.city_manager.resource_manager.get_rate(resource)
            print(f"{resource.value}: {rate:+.1f} per second")
        
        # Fast-forward simulation
        print("Simulating 10 seconds of production...")
        self.city_manager.update(10)
        
        # Print new resource levels
        for resource in ResourceType:
            amount = self.city_manager.resource_manager.get_resource(resource)
            print(f"{resource.value}: {amount:.1f}")
    
    def test_building_upgrade(self):
        """Test building upgrade"""
        print("\n----- Testing Building Upgrade -----")
        
        # Find a building to upgrade
        if not self.city_manager.buildings:
            print("No buildings to upgrade")
            return
            
        # Get the first building
        building = next(iter(self.city_manager.buildings.values()))
        
        # Check if it's operational
        if building.state != BuildingState.OPERATIONAL:
            print(f"Building {building.name} is not operational")
            return
            
        # Start upgrade
        print(f"Starting upgrade for {building.name}")
        building.start_upgrade(self.city_manager)
        
        # Update visual effects for upgrading state
        if self.city_manager.render:
            building._update_visual_effects(self.city_manager)
        
        # Quickly complete upgrade
        building.upgrade_progress = 100
        building._on_upgrade_complete(self.city_manager)
        
        # Update visual effects for operational state
        if self.city_manager.render:
            building._update_visual_effects(self.city_manager)
        
        # Print new stats
        print(f"New health: {building.health:.1f}/{building.max_health:.1f}")
        for resource, amount in building.production.items():
            print(f"Production - {resource.value}: {amount:.1f}")
        for resource, amount in building.consumption.items():
            print(f"Consumption - {resource.value}: {amount:.1f}")
            
    def test_building_damage(self):
        """Test building damage and destruction"""
        print("\n----- Testing Building Damage and Destruction -----")
        
        # Find a building to damage
        if not self.city_manager.buildings:
            print("No buildings to damage")
            return
            
        # Get the first building
        building = next(iter(self.city_manager.buildings.values()))
        
        # Apply damage
        print(f"Damaging {building.name} - Current health: {building.health:.1f}/{building.max_health:.1f}")
        
        # Apply 50% damage to make it damaged
        damage_amount = building.health * 0.5
        was_destroyed = building.take_damage(damage_amount)
        
        # Update visual effects for damaged state
        if self.city_manager.render:
            building._update_visual_effects(self.city_manager)
        
        print(f"Applied {damage_amount:.1f} damage - New health: {building.health:.1f}/{building.max_health:.1f}")
        print(f"Building state: {building.state.value}")
        
        # Apply more damage to destroy it
        if not was_destroyed:
            print(f"\nDestroying {building.name}...")
            damage_amount = building.health + 10
            was_destroyed = building.take_damage(damage_amount)
            
            if was_destroyed:
                # Call on_destroyed to handle destruction effects
                building.on_destroyed(self.city_manager)
                
                # Update visual effects for destroyed state
                if self.city_manager.render:
                    building._update_visual_effects(self.city_manager)
                
                print(f"{building.name} was destroyed!")
                print(f"Building state: {building.state.value}")
            else:
                print(f"Failed to destroy building")

def main():
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 