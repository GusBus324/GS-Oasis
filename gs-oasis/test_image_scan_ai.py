#!/usr/bin/env python3
"""
Test script to verify that the image scan results include AI analysis
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_scan_test.log"),
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

def test_image_scan_integration():
    """Test that image scanning correctly integrates with AI analysis"""
    logging.info("Testing image scan AI integration...")
    
    # Create a test scam image
    scam_text = "URGENT: Your account has been locked! Click here immediately to verify your account: www.bank-secure-verify.com"
    scam_image_path = create_test_image(scam_text, "test_scam_ai_integration.png")
    
    if not scam_image_path:
        logging.error("Failed to create test image")
        return False
    
    # Import the necessary functions from app.py
    try:
        # Add the current directory to sys.path if needed
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app import analyze_image_content, check_for_scam
        from query_gpt import get_open_ai_repsonse
        
        # First, analyze the image content
        result = analyze_image_content(scam_image_path)
        
        if not isinstance(result, tuple) or len(result) != 3:
            logging.error(f"analyze_image_content returned unexpected format: {type(result)}")
            return False
        
        extracted_text, analysis_results, performed_checks = result
        
        logging.info(f"Successfully extracted text: '{extracted_text[:100]}...'")
        logging.info(f"Analysis results count: {len(analysis_results)}")
        
        # Now check for scams in the extracted text
        scam_result = check_for_scam(extracted_text)
        
        if not isinstance(scam_result, tuple) or len(scam_result) != 3:
            logging.error(f"check_for_scam returned unexpected format: {type(scam_result)}")
            return False
        
        is_scam, confidence, reasons = scam_result
        
        logging.info(f"Scam detection result: {is_scam}, confidence: {confidence}%")
        logging.info(f"Reasons detected: {len(reasons)}")
        
        # Now test the AI integration
        ai_prompt = f"Analyze the following text extracted from an image and determine if it is a scam. Text: {extracted_text}"
        ai_response = get_open_ai_repsonse(ai_prompt)
        
        if not ai_response:
            logging.warning("No AI response received")
        else:
            logging.info(f"AI response received! Length: {len(ai_response)} characters")
            
            # Check for expected terminology in the AI response
            for term in ["SCAM DETECTED", "SUSPICIOUS CONTENT", "NO SCAM DETECTED", "Analysis", "Educational Information", "Red Flags"]:
                if term in ai_response:
                    logging.info(f"✅ Found expected term in AI response: '{term}'")
                else:
                    logging.warning(f"⚠️ Expected term not found in AI response: '{term}'")
        
        # Clean up
        if os.path.exists(scam_image_path):
            os.remove(scam_image_path)
            logging.info(f"Cleaned up test image: {scam_image_path}")
        
        return True if ai_response else False
    
    except Exception as e:
        logging.error(f"Error during test: {str(e)}", exc_info=True)
        
        # Clean up if possible
        try:
            if 'scam_image_path' in locals() and os.path.exists(scam_image_path):
                os.remove(scam_image_path)
        except:
            pass
        
        return False

if __name__ == "__main__":
    print("\nTESTING IMAGE SCAN AI INTEGRATION")
    print("=================================")
    
    success = test_image_scan_integration()
    
    if success:
        print("\n✅ SUCCESS: Image scan successfully integrates AI analysis")
    else:
        print("\n❌ FAILURE: Image scan AI integration test failed")
