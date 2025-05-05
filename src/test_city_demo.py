# src/test_city_demo.py

import pygame
import sys
import os

# Adjust path if necessary to find the engine components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.core import EngineCore # Assuming EngineCore orchestrates managers
from engine.scenes.city_demo.city_demo_scene import CityDemoScene
from engine.input.input_manager import InputManager
from engine.renderer import Renderer # Assuming base class
from engine.ui.ui_manager import UIManager # Assuming exists
from engine.asset_loader import AssetManager # Assuming exists

# --- Configuration ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

def main():
    """Main function to run the city demo."""
    pygame.init()
    print("Pygame Initialized.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nightfall Defenders - City Demo")
    clock = pygame.time.Clock()

    # --- Engine Initialization ---
    print("Initializing Engine Systems...")
    try:
        # Instantiate core managers (adjust based on actual EngineCore structure)
        input_manager = InputManager()
        print("  - Input Manager OK")
        # Asset manager needs base path
        asset_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        asset_manager = AssetManager(asset_base_path)
        print(f"  - Asset Manager OK (Base: {asset_base_path})")
        renderer = Renderer(screen) # Pass the screen surface
        print("  - Renderer OK")
        # Pass dependencies like input_manager and asset_manager to UIManager if needed
        ui_manager = UIManager(input_manager, asset_manager)
        print("  - UI Manager OK")

        # Create the main engine core instance
        engine_core = EngineCore(
            screen=screen,
            input_manager=input_manager,
            asset_manager=asset_manager,
            renderer=renderer,
            ui_manager=ui_manager
            # Add other managers as needed (time, audio, etc.)
        )
        print("Engine Core Initialized.")

    except Exception as e:
        print(f"\n--- ERROR DURING ENGINE INITIALIZATION ---")
        print(e)
        pygame.quit()
        sys.exit(1)

    # --- Load Assets (Example - adapt to your AssetManager) ---
    print("Loading common assets...")
    try:
        # asset_manager.load_manifest("common_manifest.json") # Example
        # asset_manager.load_font("default_font", "fonts/YourFont.ttf", 16) # Example
        print("Common assets loaded (Placeholder).")
    except Exception as e:
        print(f"\n--- ERROR LOADING ASSETS ---")
        print(e)
        pygame.quit()
        sys.exit(1)


    # --- Scene Setup ---
    print("Setting up City Demo Scene...")
    city_demo_scene = CityDemoScene(engine_core)
    try:
        city_demo_scene.load() # Load scene resources and initialize
        print("City Demo Scene Loaded.")
    except Exception as e:
        print(f"\n--- ERROR LOADING SCENE ---")
        print(e)
        pygame.quit()
        sys.exit(1)

    # --- User Instructions ---
    print("\n--- City Demo Controls ---")
    print("  B: Build Test House (if resources available)")
    print("  M: Add Test Resources (+500 Wood/Stone, +200 Food, +100 Gold)")
    print("  R: Trigger Random Event (Placeholder)")
    print("  D: Toggle Debug Overlay (Placeholder)")
    print("  F1: Show Build Menu (Placeholder)")
    print("  F2: Show Management Menu (Placeholder)")
    print("  F3: Show Defense Overview (Placeholder)")
    print("  F4: Advance to Next Day")
    print("  F9: Toggle Fast Forward (Placeholder)")
    print("  F10: Print Current State to Console")
    print("  Middle Mouse Drag: Pan Camera (Placeholder)")
    print("  Mouse Wheel: Zoom Camera (Placeholder)")
    print("  ESC: Quit Demo")
    print("------------------------\n")


    # --- Main Loop ---
    running = True
    print("Starting Main Loop...")
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

        # --- Event Handling ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            # Pass events to Input Manager and Scene/UI Manager
            input_manager.process_event(event)
            city_demo_scene.handle_event(event) # Scene handles UI events internally

        # --- Update ---
        input_manager.update() # Update key states etc.
        # engine_core.update(dt) # Update core systems (if any) - Scene update might be enough
        city_demo_scene.update(dt) # Update current scene logic

        # --- Render ---
        renderer.clear() # Clear screen for new frame
        city_demo_scene.render() # Render the scene content
        renderer.present() # Flip the display buffer

    # --- Cleanup ---
    print("Exiting Demo...")
    city_demo_scene.unload()
    pygame.quit()
    print("Pygame Quit.")
    sys.exit()

if __name__ == '__main__':
    main()