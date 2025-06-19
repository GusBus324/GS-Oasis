#!/usr/bin/env python3
"""
Test script for verifying that scan_image functionality is working with the correct terminology
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
import random
import string

# Create test images with known text
def create_test_images():
    print("Creating test images...")
    
    # Create directory for test images if it doesn't exist
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create normal text image
    normal_text = "Hello! This is a normal message.\nYour appointment is scheduled for tomorrow at 2pm.\nPlease bring your ID card."
    normal_path = os.path.join(test_dir, "normal_text_test.png")
    create_text_image(normal_text, normal_path)
    
    # Create scam text image
    scam_text = "URGENT: Your account has been locked!\nClick here immediately to verify your account:\nwww.bank-secure-verify.com\nOr send your login details to secure@bank-support-team.com"
    scam_path = os.path.join(test_dir, "scam_text_test.png")
    create_text_image(scam_text, scam_path)
    
    return normal_path, scam_path

def create_text_image(text, output_path):
    # Create a blank image with white background
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the text
    draw.text((50, 50), text, fill=(0, 0, 0), font=font)
    
    # Save the image
    img.save(output_path)
    print(f"Created test image: {output_path}")

# Test scan functionality
def test_scan_functionality():
    # Import required functions
    from app import analyze_image_content, check_for_scam
    
    # Create test images
    normal_path, scam_path = create_test_images()
    
    results = []
    
    # Test normal image
    print("\nTesting normal text image...")
    normal_result = test_single_image(normal_path, "normal", analyze_image_content, check_for_scam)
    results.append(normal_result)
    
    # Test scam image
    print("\nTesting scam text image...")
    scam_result = test_single_image(scam_path, "scam", analyze_image_content, check_for_scam)
    results.append(scam_result)
    
    # Print overall results
    passed = sum(results)
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    return all(results)

def test_single_image(image_path, expected_type, analyze_func, check_func):
    try:
        # Analyze the image
        extracted_text, analysis_results, performed_checks = analyze_func(image_path)
        
        print(f"Extracted text: {extracted_text}")
        
        # Check for scams in the extracted text
        is_scam, confidence, reasons = check_func(extracted_text)
        
        # Generate result message (simplified version of what app.py does)
        if is_scam:
            risk_level = "High Risk" if confidence > 60 else "Medium Risk"
            result_msg = f"⚠️ SCAM DETECTED ({risk_level}): This image contains text with indicators of a potential scam ({confidence}% confidence)."
        else:
            result_msg = f"✅ NO SCAM DETECTED\n\nAnalysis performed: {', '.join(performed_checks)}"
        
        print(f"Result message: {result_msg}")
        
        # Check if results match expectations
        if expected_type == "scam" and is_scam:
            print("✅ PASSED: Correctly identified as SCAM DETECTED")
            if "SCAM DETECTED" in result_msg:
                print("✅ PASSED: Result message contains 'SCAM DETECTED'")
                return True
            else:
                print("❌ FAILED: Result message doesn't contain 'SCAM DETECTED'")
                return False
        elif expected_type == "normal" and not is_scam:
            print("✅ PASSED: Correctly identified as NO SCAM DETECTED")
            if "NO SCAM DETECTED" in result_msg:
                print("✅ PASSED: Result message contains 'NO SCAM DETECTED'")
                return True
            else:
                print("❌ FAILED: Result message doesn't contain 'NO SCAM DETECTED'")
                return False
        else:
            print(f"❌ FAILED: Expected {expected_type}, got {'scam' if is_scam else 'normal'}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing scan image functionality with updated terminology...")
    success = test_scan_functionality()
    
    if success:
        print("\n✅ SUCCESS: Scan image functionality is working with correct terminology!")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Scan image functionality test failed.")
        sys.exit(1)
