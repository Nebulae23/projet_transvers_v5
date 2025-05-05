# src/engine/scenes/city_demo/city_demo_controller.py

import pygame
from engine.input.input_manager import InputManager
# Assuming a base PlayerController exists or adapt as needed
# from engine.ecs.components.player_controller import PlayerController

class CityDemoController: # Or inherit if base class exists: class CityDemoController(PlayerController):
    """
    Handles input specific to the city building demo scene.
    Provides test commands and demo actions.
    """
    def __init__(self, input_manager: InputManager, scene_state: 'CityDemoState', city_systems: dict):
        # super().__init__(input_manager) # If inheriting
        self.input_manager = input_manager
        self.state = scene_state
        self.city_systems = city_systems # Access to city management, building systems etc.
        print("CityDemoController Initialized")

        # Register key bindings for demo actions
        self._register_bindings()

    def _register_bindings(self):
        """Register specific key bindings for the demo."""
        # Test Commands
        self.input_manager.add_key_action(pygame.K_b, self.build_test_house)
        self.input_manager.add_key_action(pygame.K_m, self.add_test_resources)
        self.input_manager.add_key_action(pygame.K_r, self.trigger_random_event) # Placeholder
        self.input_manager.add_key_action(pygame.K_d, self.toggle_debug_overlay) # Placeholder

        # Demo Actions (Function Keys)
        self.input_manager.add_key_action(pygame.K_F1, self.show_build_menu) # Placeholder
        self.input_manager.add_key_action(pygame.K_F2, self.show_management_menu) # Placeholder
        self.input_manager.add_key_action(pygame.K_F3, self.show_defense_overview) # Placeholder
        self.input_manager.add_key_action(pygame.K_F4, self.advance_day_action)

        # Debug Shortcuts
        self.input_manager.add_key_action(pygame.K_F9, self.toggle_fast_forward) # Placeholder
        self.input_manager.add_key_action(pygame.K_F10, self.print_current_state)

        print("CityDemoController key bindings registered.")


    def update(self, dt):
        """Processes input each frame."""
        # Base class update if inheriting: super().update(dt)

        # Handle continuous actions like camera movement (if applicable)
        mouse_dx, mouse_dy = self.input_manager.get_mouse_relative()
        if self.input_manager.is_mouse_button_pressed(2): # Middle mouse button drag
            # Example: Pan camera - implementation depends on camera system
            # self.camera.pan(-mouse_dx * dt, -mouse_dy * dt)
            pass

        scroll = self.input_manager.get_mouse_scroll()
        if scroll != 0:
            # Example: Zoom camera - implementation depends on camera system
            # self.camera.zoom(1 + scroll * 0.1)
            pass

        # Check for triggered key actions (handled by InputManager callbacks)


    # --- Test Command Callbacks ---

    def build_test_house(self):
        """Action triggered by 'B' key."""
        print("Debug: Build Test House command received.")
        # Example: Find a free spot and add a house
        # Requires logic to determine position, check resources etc.
        # For demo, just add to state directly if resources allow
        if self.state.resources["wood"] >= 50 and self.state.resources["stone"] >= 20:
            self.state.update_resource("wood", -50)
            self.state.update_resource("stone", -20)
            # Find a dummy position - replace with actual placement logic
            pos_x = 10 + self.state.get_building_count("House") * 2
            pos_y = 10
            self.state.add_building({"type": "House", "level": 1, "position": (pos_x, pos_y)})
            # Potentially trigger building system: self.city_systems["building"].place_building(...)
        else:
            print("Debug: Not enough resources to build test house.")

    def add_test_resources(self):
        """Action triggered by 'M' key."""
        print("Debug: Add Test Resources command received.")
        self.state.update_resource("wood", 500)
        self.state.update_resource("stone", 500)
        self.state.update_resource("food", 200)
        self.state.update_resource("gold", 100)

    def trigger_random_event(self):
        """Action triggered by 'R' key."""
        print("Debug: Trigger Random Event command received. (Not Implemented)")
        # Example: self.city_systems["event"].trigger_random_event()

    def toggle_debug_overlay(self):
        """Action triggered by 'D' key."""
        print("Debug: Toggle Debug Overlay command received. (Not Implemented)")
        # Example: self.renderer.toggle_debug_view()

    # --- Demo Action Callbacks ---

    def show_build_menu(self):
        """Action triggered by F1 key."""
        print("Demo Action: Show Build Menu. (Not Implemented)")
        # Example: self.ui_manager.open_menu("build_menu")

    def show_management_menu(self):
        """Action triggered by F2 key."""
        print("Demo Action: Show Management Menu. (Not Implemented)")
        # Example: self.ui_manager.open_menu("management_menu")

    def show_defense_overview(self):
        """Action triggered by F3 key."""
        print("Demo Action: Show Defense Overview. (Not Implemented)")
        # Example: self.ui_manager.open_menu("defense_overview")

    def advance_day_action(self):
        """Action triggered by F4 key."""
        print("Demo Action: Advance Day.")
        self.state.advance_day()
        # Potentially trigger time system: self.city_systems["time"].advance_day()

    # --- Debug Shortcut Callbacks ---

    def toggle_fast_forward(self):
        """Action triggered by F9 key."""
        print("Debug: Toggle Fast Forward command received. (Not Implemented)")
        # Example: self.time_manager.toggle_fast_forward()

    def print_current_state(self):
        """Action triggered by F10 key."""
        print("\n--- Current City Demo State ---")
        print(f"  Day: {self.state.stats['day']}")
        print(f"  Population: {self.state.stats['population']}")
        print(f"  Morale: {self.state.stats['morale']}%")
        print("  Resources:")
        for res, amount in self.state.resources.items():
            print(f"    {res.capitalize()}: {amount}")
        print("  Buildings:")
        for i, building in enumerate(self.state.buildings):
            print(f"    {i+1}. {building['type']} (Lvl {building['level']}) at {building['position']}")
        print("  Defenses:")
        print(f"    Walls: Level {self.state.defenses['walls']['level']}, Health {self.state.defenses['walls']['health']}")
        for i, tower in enumerate(self.state.defenses['towers']):
             print(f"    Tower {i+1}: {tower['type']} (Lvl {tower['level']}) at {tower['position']}")
        print("-----------------------------\n")