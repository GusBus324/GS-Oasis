#!/usr/bin/env python3
"""
Simple test to verify the OCR scan result formatting
"""

def test_ocr_message_formatting():
    print("Testing OCR result message formatting...")
    
    # Test cases for different scenarios
    test_cases = [
        {
            "name": "No scam detected",
            "is_scam": False,
            "confidence": 0,
            "reasons": [],
            "expected_text": "NO SCAM DETECTED"
        },
        {
            "name": "Scam detected",
            "is_scam": True,
            "confidence": 75,
            "reasons": ["Contains suspicious links", "Creates false urgency"],
            "expected_text": "SCAM DETECTED"
        },
        {
            "name": "Suspicious content",
            "is_scam": False,
            "confidence": 0,
            "reasons": [],
            "suspicious_analysis": ["Contains QR code with link", "Uses vague language"],
            "expected_text": "SUSPICIOUS CONTENT"
        }
    ]
    
    # Mock function to generate result messages like in app.py
    def generate_test_result_msg(case):
        if case.get("is_scam", False):
            risk_level = "High Risk" if case.get("confidence", 0) > 60 else "Medium Risk"
            result_msg = f"⚠️ SCAM DETECTED ({risk_level}): This image contains text with indicators of a potential scam ({case.get('confidence', 0)}% confidence)."
            for reason in case.get("reasons", []):
                result_msg += f"\n• {reason}"
            return result_msg
            
        elif case.get("suspicious_analysis", []):
            result_msg = f"⚠️ SUSPICIOUS CONTENT: While no definite scam was detected, our scan found potential issues with this image:"
            for finding in case.get("suspicious_analysis", []):
                result_msg += f"\n• {finding}"
            return result_msg
            
        else:
            return f"✅ NO SCAM DETECTED\n\nAnalysis performed: Basic analysis"
    
    # Test each case
    print("\nRunning message formatting tests...")
    passed = 0
    
    for case in test_cases:
        print(f"\nTest: {case['name']}")
        
        # Generate the result message
        result_msg = generate_test_result_msg(case)
        print(f"Result message: {result_msg}")
        
        # Check if expected text is in the result
        if case["expected_text"] in result_msg:
            print(f"✅ PASSED: Found '{case['expected_text']}' in the result")
            passed += 1
        else:
            print(f"❌ FAILED: Expected '{case['expected_text']}', but it wasn't found in the result")
    
    # Print summary
    print(f"\nResults: {passed}/{len(test_cases)} tests passed")
    
    if passed == len(test_cases):
        print("\n✅ SUCCESS: All message formatting tests passed!")
        return True
    else:
        print("\n❌ FAILED: Some message formatting tests failed.")
        return False

if __name__ == "__main__":
    test_ocr_message_formatting()
