#!/usr/bin/env python3
"""
Comprehensive OCR and Threat Detection Test for GS Oasis
This script tests the entire OCR and threat detection workflow
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random

# Add the current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import extract_text_with_fallback, check_for_scam, analyze_image_content
    print("✅ Successfully imported GS Oasis functions")
except ImportError as e:
    print(f"❌ Failed to import GS Oasis functions: {e}")
    sys.exit(1)

def create_test_image(text, filename="test_ocr_image.png", background_color=(255, 255, 255), 
                      text_color=(0, 0, 0), width=800, height=400, font_size=36):
    """Create a test image with the given text"""
    
    # Create a blank image with white background
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a built-in font or default to a basic font
    try:
        # Try common system fonts
        font_paths = [
            "/Library/Fonts/Arial.ttf",  # macOS
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS alternative
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf"  # Windows
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, font_size)
                break
                
        if font is None:
            # Fall back to default font
            font = ImageFont.load_default()
            
    except Exception:
        # If font loading fails, use default
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (width//2, height//2)
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Draw text on the image
    draw.text(position, text, fill=text_color, font=font)
    
    # Save the image
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

def test_ocr_extraction():
    """Test the OCR text extraction functionality"""
    print("\n=== Testing OCR Text Extraction ===")
    
    # Test cases - normal, scam, and technical text
    test_cases = [
        ("This is a simple test of OCR functionality.", "normal_text.png", False),
        ("URGENT: Your account has been suspended! Click here to verify your identity.", "scam_text.png", True),
        ("Congratulations! You've won a $1,000,000 lottery prize. Claim now!", "lottery_scam.png", True),
        ("Your tax refund of $2,450 is ready for claim. Click the link to process.", "tax_refund_scam.png", True),
        ("Your package delivery has failed. Click here to reschedule.", "delivery_scam.png", True)
    ]
    
    results = []
    for text, filename, is_scam in test_cases:
        print(f"\nTesting with text: '{text}'")
        filepath = create_test_image(text, filename)
        
        # Test OCR extraction
        extracted_text = extract_text_with_fallback(filepath)
        print(f"  Extracted text: '{extracted_text}'")
        
        # Test scam detection if text was extracted
        if extracted_text and not extracted_text.startswith('['):
            scam_result = check_for_scam(extracted_text)
            if isinstance(scam_result, tuple) and len(scam_result) == 3:
                detected_scam, confidence, reasons = scam_result
                print(f"  Scam detected: {detected_scam} (Expected: {is_scam})")
                print(f"  Confidence: {confidence}%")
                if reasons:
                    print("  Reasons:")
                    for reason in reasons:
                        print(f"    - {reason}")
                
                # Add result to summary
                match = detected_scam == is_scam
                results.append((filename, match, confidence if detected_scam else 0))
            else:
                print(f"  ❌ check_for_scam returned unexpected format: {scam_result}")
                results.append((filename, False, 0))
        else:
            print(f"  ❌ OCR failed to extract meaningful text")
            results.append((filename, False, 0))
    
    # Print summary
    print("\n=== OCR and Threat Detection Summary ===")
    success_count = sum(1 for _, match, _ in results if match)
    print(f"Successfully detected {success_count} out of {len(test_cases)} test cases")
    
    for filename, match, confidence in results:
        status = "✅ CORRECT" if match else "❌ INCORRECT"
        print(f"  {filename}: {status} {confidence}% confidence")
    
    return success_count == len(test_cases)

def test_full_image_analysis():
    """Test the full image analysis functionality"""
    print("\n=== Testing Full Image Analysis ===")
    
    # Create a test image with scam text
    test_text = "URGENT: Your account has been locked. Call 555-123-4567 immediately to verify your identity."
    filepath = create_test_image(test_text, "full_analysis_test.png")
    
    # Run the complete image analysis
    try:
        print("Running full image analysis...")
        result = analyze_image_content(filepath)
        
        if isinstance(result, tuple) and len(result) == 3:
            extracted_text, analysis_results, performed_checks = result
            
            print(f"Extracted text: '{extracted_text}'")
            print("\nAnalysis results:")
            for i, analysis in enumerate(analysis_results, 1):
                print(f"  {i}. {analysis}")
            
            print("\nPerformed checks:")
            for i, check in enumerate(performed_checks, 1):
                print(f"  {i}. {check}")
            
            # Check if warning indicators are found in the analysis
            warnings = [result for result in analysis_results if "⚠️" in result]
            print(f"\nDetected {len(warnings)} warnings/threats")
            
            return len(warnings) > 0
        else:
            print(f"❌ analyze_image_content returned unexpected format: {result}")
            return False
    except Exception as e:
        print(f"❌ Error during image analysis: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=== GS Oasis OCR and Threat Detection Test ===")
    
    ocr_success = test_ocr_extraction()
    analysis_success = test_full_image_analysis()
    
    print("\n=== Final Results ===")
    print(f"OCR Text Extraction & Threat Detection: {'✅ PASS' if ocr_success else '❌ FAIL'}")
    print(f"Full Image Analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    
    overall_success = ocr_success and analysis_success
    print(f"\nOverall Test: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
