#!/usr/bin/env python3
"""
Simple OCR and Threat Detection Test for GS Oasis
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add the current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import extract_text_with_fallback, check_for_scam
    print("✅ Successfully imported GS Oasis functions")
except ImportError as e:
    print(f"❌ Failed to import GS Oasis functions: {e}")
    sys.exit(1)

def create_test_image(text, filename="test_ocr_simple.png"):
    """Create a test image with the given text"""
    # Create a blank image with white background
    width, height = 800, 200
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw text on the image
    draw.text((50, 50), text, fill=(0, 0, 0))
    
    # Save the image
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

def main():
    """Main test function"""
    print("=== GS Oasis Simple OCR and Threat Detection Test ===")
    
    # Test OCR with a sample text
    print("\nTesting OCR with normal text...")
    normal_text = "This is a simple test of OCR functionality"
    normal_image = create_test_image(normal_text, "normal_text.png")
    
    print("Testing OCR with scam text...")
    scam_text = "URGENT: Your account has been suspended! Click here now!"
    scam_image = create_test_image(scam_text, "scam_text.png")
    
    # Test OCR extraction
    print("\n=== OCR Extraction Test ===")
    normal_extracted = extract_text_with_fallback(normal_image)
    print(f"Normal text extracted: '{normal_extracted}'")
    
    scam_extracted = extract_text_with_fallback(scam_image)
    print(f"Scam text extracted: '{scam_extracted}'")
    
    # Test scam detection
    print("\n=== Scam Detection Test ===")
    
    # Normal text
    if normal_extracted and not normal_extracted.startswith('['):
        normal_result = check_for_scam(normal_extracted)
        print("Normal text scam check:")
        print(f"  Result type: {type(normal_result)}")
        print(f"  Result: {normal_result}")
    else:
        print("Could not check normal text for scam (OCR failed)")
    
    # Scam text
    if scam_extracted and not scam_extracted.startswith('['):
        scam_result = check_for_scam(scam_extracted)
        print("Scam text scam check:")
        print(f"  Result type: {type(scam_result)}")
        print(f"  Result: {scam_result}")
    else:
        print("Could not check scam text for scam (OCR failed)")
    
    print("\n=== Direct Scam Detection Test ===")
    # Test scam detection directly with strings
    direct_normal = check_for_scam("This is a normal message without any scam indicators")
    print(f"Direct normal text: {direct_normal}")
    
    direct_scam = check_for_scam("URGENT: Your account will be suspended! Verify immediately!")
    print(f"Direct scam text: {direct_scam}")
    
    # Clean up
    print("\nCleaning up test files...")
    for file in [normal_image, scam_image]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    
    print("\nTest completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
