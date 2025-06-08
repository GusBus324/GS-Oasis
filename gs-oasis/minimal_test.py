#!/usr/bin/env python3
"""
Minimal test to isolate the tuple unpacking error
"""

import os
import sys

# Add the path to app.py
sys.path.insert(0, '/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis')

def test_minimal():
    print("Starting minimal test...")
    
    # First test: Import and check functions exist
    try:
        print("1. Testing imports...")
        import app
        print("   - app imported successfully")
        
        check_for_scam = getattr(app, 'check_for_scam', None)
        analyze_image_content = getattr(app, 'analyze_image_content', None)
        
        print(f"   - check_for_scam function: {check_for_scam}")
        print(f"   - analyze_image_content function: {analyze_image_content}")
        
        if check_for_scam is None:
            print("ERROR: check_for_scam function not found!")
            return False
            
        if analyze_image_content is None:
            print("ERROR: analyze_image_content function not found!")
            return False
            
    except Exception as e:
        print(f"ERROR during import: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Second test: Test check_for_scam function
    try:
        print("\n2. Testing check_for_scam function...")
        test_text = "URGENT: Click here now!"
        
        print(f"   - Calling check_for_scam with text: '{test_text}'")
        result = check_for_scam(test_text)
        
        print(f"   - Result type: {type(result)}")
        print(f"   - Result value: {result}")
        
        if not isinstance(result, tuple):
            print(f"ERROR: check_for_scam returned {type(result)} instead of tuple!")
            return False
            
        if len(result) != 3:
            print(f"ERROR: check_for_scam returned tuple of length {len(result)} instead of 3!")
            return False
            
        is_scam, confidence, reasons = result
        print(f"   - is_scam: {is_scam} (type: {type(is_scam)})")
        print(f"   - confidence: {confidence} (type: {type(confidence)})")
        print(f"   - reasons: {reasons} (type: {type(reasons)})")
        
    except Exception as e:
        print(f"ERROR during check_for_scam test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Third test: Test analyze_image_content function with a simple image
    try:
        print("\n3. Testing analyze_image_content function...")
        
        # Try to find a test image
        test_image_paths = [
            "/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis/test_images/scam_test.png",
            "/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis/test_images/test_text.png",
            "/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis/test_images/test_text2.png"
        ]
        
        test_image = None
        for path in test_image_paths:
            if os.path.exists(path):
                test_image = path
                break
                
        if test_image:
            print(f"   - Using test image: {test_image}")
            result = analyze_image_content(test_image)
            
            print(f"   - Result type: {type(result)}")
            print(f"   - Result value: {result}")
            
            if not isinstance(result, tuple):
                print(f"ERROR: analyze_image_content returned {type(result)} instead of tuple!")
                return False
                
            if len(result) != 3:
                print(f"ERROR: analyze_image_content returned tuple of length {len(result)} instead of 3!")
                return False
                
            extracted_text, analysis_results, performed_checks = result
            print(f"   - extracted_text: '{extracted_text}' (type: {type(extracted_text)})")
            print(f"   - analysis_results: {analysis_results} (type: {type(analysis_results)})")
            print(f"   - performed_checks: {performed_checks} (type: {type(performed_checks)})")
        else:
            print("   - No test images found, skipping analyze_image_content test")
            
    except Exception as e:
        print(f"ERROR during analyze_image_content test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nAll tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_minimal()
    if not success:
        sys.exit(1)
    else:
        print("✅ No tuple unpacking errors detected!")
