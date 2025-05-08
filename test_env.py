#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Environment for Nightfall Defenders
"""

import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())

# Test imports
try:
    import panda3d
    print("Panda3D version:", panda3d.__version__)
except ImportError:
    print("Failed to import panda3d")

try:
    import numpy
    print("NumPy version:", numpy.__version__)
except ImportError:
    print("Failed to import numpy")

try:
    import PIL
    print("PIL version:", PIL.__version__)
except ImportError:
    print("Failed to import PIL")

try:
    import yaml
    print("PyYAML version:", yaml.__version__)
except ImportError:
    print("Failed to import yaml")

# Test file system
print("\nDirectory listing for src:")
if os.path.exists("src"):
    for item in os.listdir("src"):
        print("-", item)
else:
    print("src directory not found")

print("\nDirectory listing for src/engine:")
if os.path.exists("src/engine"):
    for item in os.listdir("src/engine"):
        print("-", item)
else:
    print("src/engine directory not found")

print("\nDirectory listing for src/game:")
if os.path.exists("src/game"):
    for item in os.listdir("src/game"):
        print("-", item)
else:
    print("src/game directory not found")

print("\nTest completed successfully!") 