#!/usr/bin/env python3
"""
Debug script to test the analyze_image_content function and check for tuple unpacking errors.
"""

import os
import sys
sys.path.append('/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis')

# Import the functions from app.py
from app import analyze_image_content, check_for_scam

def test_functions():
    print("Testing analyze_image_content and check_for_scam functions...")
    
    # Test with a sample image (if it exists)
    test_image_path = "/Users/gussimmonds/Desktop/SOFWARE MAJOR/GS-Oasis/gs-oasis/test_images/scam_test.png"
    
    if os.path.exists(test_image_path):
        print(f"Testing with image: {test_image_path}")
        
        try:
            # Test analyze_image_content function
            print("Testing analyze_image_content...")
            result = analyze_image_content(test_image_path)
            print(f"analyze_image_content result type: {type(result)}")
            print(f"analyze_image_content result: {result}")
            
            # Check if it's a tuple with 3 elements
            if isinstance(result, tuple) and len(result) == 3:
                extracted_text, analysis_results, performed_checks = result
                print(f"Extracted text: {extracted_text}")
                print(f"Analysis results: {analysis_results}")
                print(f"Performed checks: {performed_checks}")
                
                # Test check_for_scam function if we have text
                if extracted_text:
                    print("\nTesting check_for_scam...")
                    scam_result = check_for_scam(extracted_text)
                    print(f"check_for_scam result type: {type(scam_result)}")
                    print(f"check_for_scam result: {scam_result}")
                    
                    # Check if it's a tuple with 3 elements
                    if isinstance(scam_result, tuple) and len(scam_result) == 3:
                        is_scam, confidence, reasons = scam_result
                        print(f"Is scam: {is_scam}")
                        print(f"Confidence: {confidence}")
                        print(f"Reasons: {reasons}")
                    else:
                        print(f"ERROR: check_for_scam returned {type(scam_result)} instead of tuple!")
                        return False
                else:
                    print("No text extracted to test scam detection")
                    
            else:
                print(f"ERROR: analyze_image_content returned {type(result)} instead of tuple!")
                return False
                
        except Exception as e:
            print(f"ERROR during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"Test image not found: {test_image_path}")
        print("Testing with sample text only...")
        
        # Test check_for_scam with sample text
        sample_text = "URGENT: Your account will be suspended! Click here immediately to verify your identity."
        try:
            print("Testing check_for_scam with sample text...")
            scam_result = check_for_scam(sample_text)
            print(f"check_for_scam result type: {type(scam_result)}")
            print(f"check_for_scam result: {scam_result}")
            
            if isinstance(scam_result, tuple) and len(scam_result) == 3:
                is_scam, confidence, reasons = scam_result
                print(f"Is scam: {is_scam}")
                print(f"Confidence: {confidence}")
                print(f"Reasons: {reasons}")
            else:
                print(f"ERROR: check_for_scam returned {type(scam_result)} instead of tuple!")
                return False
                
        except Exception as e:
            print(f"ERROR during scam testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_functions()
