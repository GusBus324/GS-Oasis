#!/usr/bin/env python3
# Test script to verify temp directory and file operations

import os
import sys
import shutil
from pathlib import Path
import time

def test_temp_directory():
    """Test if the temp directory exists and is writable"""
    print("Testing temp directory functionality...")
    
    # Get the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths
    temp_dir = os.path.join(app_dir, 'static', 'temp')
    test_file = os.path.join(temp_dir, f'test_{int(time.time())}.txt')
    
    # Check if directory exists
    if not os.path.exists(temp_dir):
        print(f"❌ ERROR: Temp directory does not exist: {temp_dir}")
        try:
            print(f"Creating directory: {temp_dir}")
            os.makedirs(temp_dir, exist_ok=True)
            print(f"✅ Successfully created temp directory")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return False
    else:
        print(f"✅ Temp directory exists: {temp_dir}")
    
    # Check if directory is writable
    if not os.access(temp_dir, os.W_OK):
        print(f"❌ ERROR: Temp directory is not writable: {temp_dir}")
        try:
            print(f"Updating permissions on temp directory")
            os.chmod(temp_dir, 0o755)
            print(f"✅ Successfully updated permissions")
        except Exception as e:
            print(f"❌ Failed to update permissions: {e}")
            return False
    else:
        print(f"✅ Temp directory is writable")
    
    # Try to create a test file
    try:
        with open(test_file, 'w') as f:
            f.write("Test file for temp directory check")
        print(f"✅ Successfully created test file: {test_file}")
        
        # Clean up
        os.remove(test_file)
        print(f"✅ Successfully removed test file")
    except Exception as e:
        print(f"❌ ERROR: Failed to create/remove test file: {e}")
        return False
    
    print("✅ Temp directory tests passed!")
    return True

if __name__ == "__main__":
    test_temp_directory()
