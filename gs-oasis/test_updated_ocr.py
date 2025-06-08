#!/usr/bin/env python3
"""
Test script to verify the updated OCR functionality using EasyOCR as primary
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Add the current directory to Python path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the updated function from app.py
from app import extract_text_with_fallback, EASYOCR_AVAILABLE, OCR_AVAILABLE

def create_test_image_with_text(text, filename):
    """Create a simple test image with text"""
    # Create a white background image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw the text in black
    draw.text((50, 80), text, fill='black', font=font)
    
    # Save the image
    img.save(filename)
    return filename

def test_ocr_functionality():
    """Test the updated OCR functionality"""
    print("=== Testing Updated OCR Functionality ===")
    print(f"EasyOCR Available: {EASYOCR_AVAILABLE}")
    print(f"Tesseract Available: {OCR_AVAILABLE}")
    print()
    
    # Create test images
    test_cases = [
        ("This is a test message", "test_simple.png"),
        ("URGENT: Click here now!", "test_scam.png"),
        ("Account suspended immediately", "test_urgent.png")
    ]
    
    for test_text, filename in test_cases:
        print(f"Testing with text: '{test_text}'")
        
        # Create test image
        image_path = create_test_image_with_text(test_text, filename)
        
        try:
            # Test the OCR function
            extracted_text = extract_text_with_fallback(image_path)
            
            print(f"  Created image: {filename}")
            print(f"  Extracted text: '{extracted_text}'")
            
            # Check if the extraction was successful
            if extracted_text and len(extracted_text.strip()) > 0:
                # Check if key words from original text are present
                original_words = test_text.lower().split()
                extracted_words = extracted_text.lower().split()
                
                matches = sum(1 for word in original_words if any(word in ext_word for ext_word in extracted_words))
                success_rate = matches / len(original_words) if original_words else 0
                
                if success_rate > 0.5:  # More than 50% of words matched
                    print(f"  ✅ SUCCESS: {success_rate:.1%} word match rate")
                else:
                    print(f"  ⚠️  PARTIAL: {success_rate:.1%} word match rate")
            else:
                print(f"  ❌ FAILED: No text extracted")
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        
        print()
        
        # Clean up test image
        try:
            os.remove(image_path)
        except:
            pass

if __name__ == "__main__":
    test_ocr_functionality()
