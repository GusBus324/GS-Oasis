#!/usr/bin/env python3

import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

try:
    print("Attempting to import app module...")
    import app
    print("SUCCESS: app module imported")
    
    print("Checking for analyze_image_content function...")
    if hasattr(app, 'analyze_image_content'):
        print("SUCCESS: analyze_image_content function found")
        func = app.analyze_image_content
        print(f"Function: {func}")
    else:
        print("ERROR: analyze_image_content function not found")
        
    print("Checking for check_for_scam function...")
    if hasattr(app, 'check_for_scam'):
        print("SUCCESS: check_for_scam function found")
        func = app.check_for_scam
        print(f"Function: {func}")
    else:
        print("ERROR: check_for_scam function not found")
        
except Exception as e:
    print(f"ERROR importing app: {e}")
    import traceback
    traceback.print_exc()

print("Test complete.")
