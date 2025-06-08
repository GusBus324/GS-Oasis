#!/usr/bin/env python3

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_functions():
    print("=== DEBUGGING TUPLE UNPACKING ERROR ===")
    
    # Import the module
    try:
        import app
        print("✓ App module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import app module: {e}")
        return
    
    # Check if functions exist and are callable
    check_for_scam = getattr(app, 'check_for_scam', None)
    analyze_image_content = getattr(app, 'analyze_image_content', None)
    
    print(f"check_for_scam function: {check_for_scam}")
    print(f"analyze_image_content function: {analyze_image_content}")
    
    if not callable(check_for_scam):
        print("✗ check_for_scam is not callable!")
        return
    
    if not callable(analyze_image_content):
        print("✗ analyze_image_content is not callable!")
        return
    
    # Test check_for_scam with various inputs
    test_cases = [
        "",
        None,
        "normal text",
        "URGENT: Click here now to verify your account!"
    ]
    
    print("\n=== TESTING check_for_scam ===")
    for i, test_input in enumerate(test_cases):
        print(f"\nTest {i+1}: {repr(test_input)}")
        try:
            result = check_for_scam(test_input)
            print(f"  Result type: {type(result)}")
            print(f"  Result: {result}")
            
            # Try to unpack it
            if result is None:
                print("  ✗ Result is None!")
                continue
            elif isinstance(result, bool):
                print(f"  ✗ Result is boolean: {result}")
                continue
            elif not isinstance(result, (tuple, list)):
                print(f"  ✗ Result is not tuple/list: {type(result)}")
                continue
            elif len(result) != 3:
                print(f"  ✗ Result has wrong length: {len(result)}")
                continue
            else:
                is_scam, confidence, reasons = result
                print(f"  ✓ Successfully unpacked: is_scam={is_scam}, confidence={confidence}, reasons={reasons}")
                
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Test analyze_image_content
    print("\n=== TESTING analyze_image_content ===")
    test_images = [
        "test_images/scam_test.png",
        "test_images/test_text.png", 
        "test_images/test_text2.png"
    ]
    
    for test_image in test_images:
        if os.path.exists(test_image):
            print(f"\nTesting with image: {test_image}")
            try:
                result = analyze_image_content(test_image)
                print(f"  Result type: {type(result)}")
                print(f"  Result: {result}")
                
                # Try to unpack it
                if result is None:
                    print("  ✗ Result is None!")
                    continue
                elif isinstance(result, bool):
                    print(f"  ✗ Result is boolean: {result}")
                    continue
                elif not isinstance(result, (tuple, list)):
                    print(f"  ✗ Result is not tuple/list: {type(result)}")
                    continue
                elif len(result) != 3:
                    print(f"  ✗ Result has wrong length: {len(result)}")
                    continue
                else:
                    extracted_text, analysis_results, performed_checks = result
                    print(f"  ✓ Successfully unpacked:")
                    print(f"    extracted_text: {repr(extracted_text)}")
                    print(f"    analysis_results: {analysis_results}")
                    print(f"    performed_checks: {performed_checks}")
                    
            except Exception as e:
                print(f"  ✗ Exception: {e}")
                import traceback
                traceback.print_exc()
            break
    else:
        print("No test images found")

if __name__ == "__main__":
    debug_functions()
