# src/main.py
import sys
from engine.window import Window
from engine.core import Engine

def main():
    # Initialize window
    window = Window(width=1280, height=720, title="Nightfall Defenders")
    
    # Create game engine instance
    engine = Engine(window)
    
    try:
        # Start game loop
        engine.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        window.close()

if __name__ == "__main__":
    main()