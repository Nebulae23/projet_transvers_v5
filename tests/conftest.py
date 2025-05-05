"""
Pytest configuration file.
This automatically adds the project root to the Python path to enable imports.
"""
import os
import sys
from pathlib import Path
import pytest

# Add the project root to sys.path
project_root = Path(__file__).parent.parent  # Go up one level from tests/
sys.path.insert(0, str(project_root))

# Print the Python path for debugging
print(f"Python path for tests: {sys.path}")

# Add any shared fixtures needed for tests

@pytest.fixture
def test_data_path():
    """Returns the path to test data directory"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def assets_data_path():
    """Returns the path to assets/data directory"""
    return project_root / "assets" / "data" 