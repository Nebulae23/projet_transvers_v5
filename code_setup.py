"""
Notebook Setup Utilities
Import this at the top of any notebook to properly set up imports.
"""
import os
import sys
from pathlib import Path

def setup_notebook_environment():
    """Set up the notebook environment for proper imports"""
    # Get the current working directory (where the notebook is run from)
    notebook_dir = Path.cwd()
    
    # Add the project root to sys.path if not already there
    if str(notebook_dir) not in sys.path:
        sys.path.insert(0, str(notebook_dir))
        print(f"Added {notebook_dir} to Python path")
    
    # Install required dependencies if needed
    try:
        import pytest
        import pluggy
        print(f"Found pytest {pytest.__version__} and pluggy {pluggy.__version__}")
    except ImportError:
        print("Installing pytest and pluggy...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest>=7.4.0", "pluggy==1.2.0"])
        
    print("Notebook environment setup complete!")
    return notebook_dir

# Run automatically when imported
project_dir = setup_notebook_environment()

if __name__ == "__main__":
    setup_notebook_environment()
    print("You can now import packages using proper import paths") 