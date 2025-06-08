#!/usr/bin/env python3

import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_function():
    try:
        print("=== Testing analyze_image_content function ===")
        
        # Import the app module
        import app
        print("✓ App module imported successfully")
        
        # Check if the function exists
        if not hasattr(app, 'analyze_image_content'):
            print("✗ analyze_image_content function not found in app module")
            return False
            
        func = app.analyze_image_content
        print(f"✓ Function found: {func}")
        
        # Test with a non-existent file to see the error handling
        print("\n--- Testing with non-existent file ---")
        result = func('/non/existent/file.png')
        print(f"Result type: {type(result)}")
        print(f"Result value: {result}")
        
        if isinstance(result, bool):
            print("✗ ERROR: Function returned a boolean instead of tuple!")
            return False
        elif isinstance(result, tuple):
            if len(result) == 3:
                print("✓ Function returned correct tuple format")
                extracted_text, analysis_results, performed_checks = result
                print(f"  - extracted_text: {type(extracted_text)} = {repr(extracted_text)}")
                print(f"  - analysis_results: {type(analysis_results)} = {analysis_results}")
                print(f"  - performed_checks: {type(performed_checks)} = {performed_checks}")
            else:
                print(f"✗ ERROR: Tuple has {len(result)} elements instead of 3")
                return False
        else:
            print(f"✗ ERROR: Function returned {type(result)} instead of tuple")
            return False
            
        # Test with an actual image file if one exists
        test_images = [
            'test_images/scam1.png',
            'test_images/test_text.png',
            'test_images/test_text2.png',
            'static/temp/test.png'  # Could be leftover from previous tests
        ]
        
        for test_image in test_images:
            if os.path.exists(test_image):
                print(f"\n--- Testing with existing file: {test_image} ---")
                result = func(test_image)
                print(f"Result type: {type(result)}")
                
                if isinstance(result, bool):
                    print("✗ ERROR: Function returned a boolean with real file!")
                    return False
                elif isinstance(result, tuple) and len(result) == 3:
                    print("✓ Function returned correct tuple format with real file")
                    extracted_text, analysis_results, performed_checks = result
                    print(f"  - extracted_text: {repr(extracted_text[:100])}")
                    print(f"  - analysis_results count: {len(analysis_results)}")
                    print(f"  - performed_checks: {performed_checks}")
                else:
                    print(f"✗ ERROR: Bad return format with real file: {type(result)}")
                    return False
                break
        else:
            print("\n--- No test images found for real file testing ---")
            
        print("\n✓ All tests passed - function returns tuples correctly")
        return True
        
    except Exception as e:
        print(f"✗ ERROR during testing: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_function()
    if not success:
        print("\n❌ TESTS FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED")
