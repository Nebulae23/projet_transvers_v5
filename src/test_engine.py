# src/test_engine.py
import sys
from engine.window import Window
from engine.core import Engine
from engine.renderer import Renderer

def main():
    try:
        # Create window
        window = Window(width=800, height=600, title="OpenGL Engine Test")
        
        # Create and initialize engine
        engine = Engine(window)
        
        # Create and initialize renderer
        renderer = Renderer()
        renderer.initialize()
        
        # Custom render function for test
        def test_render():
            renderer.render()
            window.swap_buffers()
        
        # Override engine's render method for this test
        engine.render = test_render
        
        print("Starting engine test...")
        print("You should see a white triangle on a black background")
        print("Press ESC to exit")
        
        # Run the engine
        engine.run()
        
    except Exception as e:
        print(f"Error during engine test: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        renderer.cleanup()
        window.cleanup()
        
if __name__ == "__main__":
    main()