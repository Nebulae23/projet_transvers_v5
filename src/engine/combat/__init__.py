"""
Combat System Module
This package contains combat-related functionality.
"""

try:
    from .combat_system import CombatSystem
    from .ability import Ability
except ImportError as e:
    print(f"Note: Some combat module components couldn't be imported: {e}") 