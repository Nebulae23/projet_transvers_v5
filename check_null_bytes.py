#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility script to check for null bytes in Python files
"""

import os
import sys

def check_file_for_null_bytes(filepath):
    """Check if a file contains null bytes"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            has_null = b'\0' in content
            if has_null:
                # Find position of null byte
                pos = content.find(b'\0')
                context = content[max(0, pos-10):pos+10]
                print(f"NULL BYTES FOUND in {filepath} at position {pos}")
                print(f"Context: {context}")
                return True
            return False
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return False

def scan_directory(directory, extension='.py'):
    """Scan a directory for files with null bytes"""
    found_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                filepath = os.path.join(root, file)
                if check_file_for_null_bytes(filepath):
                    found_files.append(filepath)
    
    return found_files

if __name__ == "__main__":
    # Scan all Python files in the project
    target_dirs = ["src", "generate_assets_v2.py", "generate_assets.py", "generate_hybrid_materials.py"]
    
    for target_dir in target_dirs:
        if os.path.isfile(target_dir):
            print(f"Checking {target_dir}...")
            check_file_for_null_bytes(target_dir)
        else:
            print(f"Scanning {target_dir} for files with null bytes...")
            files_with_null_bytes = scan_directory(target_dir)
            
            if files_with_null_bytes:
                print("\nFiles with null bytes in {target_dir}:")
                for file in files_with_null_bytes:
                    print(f"- {file}")
            else:
                print(f"No files with null bytes found in {target_dir}.") 