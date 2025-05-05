"""
Import Path Management Utility
This module makes sure that the project root is in the Python path.
Import this at the top of any script or notebook to enable imports from src.
"""

import os
import sys
from pathlib import Path

def add_project_root_to_path():
    """Add the project root directory to sys.path if it's not already there."""
    # Get the directory containing this file
    current_file_dir = Path(__file__).resolve().parent
    
    # Project root is one level up from src
    project_root = current_file_dir.parent
    
    # Add to path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"Added {project_root} to Python path")
    
    return project_root

# Automatically add to path when this module is imported
project_root = add_project_root_to_path()

if __name__ == "__main__":
    print(f"Python path now includes: {project_root}")
    print("You can now import packages using 'from src.engine...' syntax") 