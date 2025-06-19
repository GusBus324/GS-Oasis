#!/usr/bin/env python3
"""
Final test script to verify image scan results with AI integration
Tests all three possible outcomes: SCAM DETECTED, SUSPICIOUS CONTENT, and NO SCAM DETECTED
"""

import os
import sys
import time
import logging
import flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scan_results_verification.log"),
        logging.StreamHandler()
    ]
)

def create_test_image(content, filename):
    """Create a test image with the given content"""
    # Make sure the test_images directory exists
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Import and use PIL to create an image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image with white background
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, or fall back to default
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw the text on the image
        draw.text((50, 50), content, fill='black', font=font)
        
        # Save the image
        filepath = os.path.join(test_dir, filename)
        img.save(filepath)
        
        logging.info(f"Created test image: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"Error creating test image: {str(e)}")
        return None

def test_scan_results_integration():
    """Test all three possible scan result outcomes with AI integration"""
    logging.info("Testing scan results with AI integration...")
    
    try:
        # Add the current directory to sys.path if needed
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Create a mock Flask app and request context
        app = flask.Flask(__name__)
        app.secret_key = 'test_secret_key'
        
        # Import necessary functions
        from app import analyze_image_content, check_for_scam
        from query_gpt import get_open_ai_repsonse
        
        # Test cases for different outcomes
        test_cases = [
            {
                "name": "Scam",
                "text": "URGENT: Your account has been locked! Click here immediately to verify your account: www.bank-secure-verify.com",
                "expected_outcome": "SCAM DETECTED"
            },
            {
                "name": "Suspicious",
                "text": "Please review your account settings. Some unusual activity has been detected. Visit account-settings.com for more information.",
                "expected_outcome": "SUSPICIOUS CONTENT"
            },
            {
                "name": "Safe",
                "text": "Hello, this is a reminder about your appointment tomorrow at 2:00 PM. Please bring your ID card. Thank you!",
                "expected_outcome": "NO SCAM DETECTED"
            }
        ]
        
        results = []
        
        for test in test_cases:
            logging.info(f"Testing {test['name']} case...")
            
            # Create test image
            image_path = create_test_image(test["text"], f"test_{test['name'].lower()}_case.png")
            
            if not image_path:
                logging.error(f"Failed to create test image for {test['name']} case")
                continue
            
            # Analyze image content
            result = analyze_image_content(image_path)
            if not isinstance(result, tuple) or len(result) != 3:
                logging.error(f"analyze_image_content returned unexpected format: {type(result)}")
                continue
            
            extracted_text, analysis_results, performed_checks = result
            logging.info(f"{test['name']} case - Extracted text: '{extracted_text[:50]}...'")
            
            # Check for scams
            scam_result = check_for_scam(extracted_text)
            if not isinstance(scam_result, tuple) or len(scam_result) != 3:
                logging.error(f"check_for_scam returned unexpected format: {type(scam_result)}")
                continue
            
            is_scam, confidence, reasons = scam_result
            logging.info(f"{test['name']} case - Scam detection: {is_scam}, confidence: {confidence}%")
            
            # Get AI analysis
            ai_prompt = f"Analyze the following text extracted from an image and determine if it is a scam. Text: {extracted_text}"
            ai_response = get_open_ai_repsonse(ai_prompt)
            
            if not ai_response:
                logging.warning(f"{test['name']} case - No AI response received")
            else:
                logging.info(f"{test['name']} case - AI response received! Length: {len(ai_response)} characters")
                
                # Check if the AI response contains the expected outcome
                contains_expected = test["expected_outcome"] in ai_response
                logging.info(f"{test['name']} case - Contains expected outcome '{test['expected_outcome']}': {contains_expected}")
                
                # Check for educational content and red flags
                has_educational = "Educational Information" in ai_response
                has_red_flags = "Red Flags" in ai_response
                
                logging.info(f"{test['name']} case - Has educational content: {has_educational}")
                logging.info(f"{test['name']} case - Has red flags: {has_red_flags}")
                
                # Save response for inspection
                with open(f"{test['name'].lower()}_response.html", "w") as f:
                    f.write(ai_response)
                
                results.append({
                    "case": test["name"],
                    "expected_outcome": test["expected_outcome"],
                    "contains_expected": contains_expected,
                    "has_educational": has_educational,
                    "has_red_flags": has_red_flags
                })
            
            # Clean up
            if os.path.exists(image_path):
                os.remove(image_path)
                logging.info(f"Cleaned up test image: {image_path}")
        
        # Summarize results
        print("\nSUMMARY OF RESULTS:")
        print("===================")
        
        all_passed = True
        for result in results:
            outcome = "✅ PASSED" if result["contains_expected"] and result["has_educational"] and result["has_red_flags"] else "❌ FAILED"
            if outcome == "❌ FAILED":
                all_passed = False
            
            print(f"{outcome} - {result['case']} case:")
            print(f"  Expected outcome: {result['expected_outcome']}")
            print(f"  Contains expected outcome: {result['contains_expected']}")
            print(f"  Has educational content: {result['has_educational']}")
            print(f"  Has red flags: {result['has_red_flags']}")
            print()
        
        return all_passed
    
    except Exception as e:
        logging.error(f"Error during test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("\nTESTING SCAN RESULTS WITH AI INTEGRATION")
    print("=======================================")
    
    success = test_scan_results_integration()
    
    if success:
        print("\n✅ SUCCESS: All scan result outcomes correctly integrate AI analysis")
    else:
        print("\n⚠️ WARNING: Some scan result outcomes may not correctly integrate AI analysis")
