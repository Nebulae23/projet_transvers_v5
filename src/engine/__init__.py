"""
Engine Core Package
This module contains the main game engine components.
"""

# Import convenience - comment out any modules that don't exist yet
try:
    from . import combat
    from . import physics
    from . import world
    from . import ecs
    from . import scenes
    from . import ui
    from . import weather
    from . import data
    from . import progression
    from . import events
    from . import quests
    from . import inventory
    from . import time
    from . import rendering
except ImportError as e:
    # Don't fail on import, just note which modules aren't available
    # This allows partial functionality even if some modules are missing
    print(f"Note: Some engine modules could not be imported: {e}") 