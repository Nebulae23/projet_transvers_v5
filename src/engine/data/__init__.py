"""
Data Management Module
This package contains data loading and validation functionality.
"""

try:
    from .ability_loader import load_ability_data
    from .upgrade_loader import load_upgrade_data
    from .effect_loader import load_effect_data
    from .data_validator import (
        validate_ability_data,
        validate_upgrade_data,
        validate_effect_data,
    )
    
    # Optional - uncomment when implemented
    # from .scaling_loader import load_scaling_data
    # from .data_validator import validate_scaling_data
except ImportError as e:
    print(f"Note: Some data module components couldn't be imported: {e}") 