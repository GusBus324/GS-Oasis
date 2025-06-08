#!/usr/bin/env python3
"""
Quick test to verify OCR functionality is working
"""

def test_imports():
    """Test all OCR-related imports"""
    results = {}
    
    # Test Flask
    try:
        from flask import Flask
        results['flask'] = True
    except ImportError:
        results['flask'] = False
    
    # Test Tesseract
    try:
        import pytesseract
        results['pytesseract'] = True
    except ImportError:
        results['pytesseract'] = False
    
    # Test OpenCV
    try:
        import cv2
        results['cv2'] = True
    except ImportError:
        results['cv2'] = False
    
    # Test Google Cloud Vision
    try:
        from google.cloud import vision
        results['google_vision'] = True
    except ImportError:
        results['google_vision'] = False
    
    # Test EasyOCR
    try:
        import easyocr
        results['easyocr'] = True
    except ImportError:
        results['easyocr'] = False
    
    return results

def main():
    print("=== GS Oasis OCR Integration Test ===")
    results = test_imports()
    
    print("\nImport Results:")
    for lib, status in results.items():
        status_text = "✅ Available" if status else "❌ Not available"
        print(f"  {lib}: {status_text}")
    
    # Check OCR capabilities
    ocr_methods = []
    if results['pytesseract']:
        ocr_methods.append("Tesseract")
    if results['google_vision']:
        ocr_methods.append("Google Cloud Vision")
    if results['easyocr']:
        ocr_methods.append("EasyOCR")
    
    print(f"\nAvailable OCR Methods: {', '.join(ocr_methods) if ocr_methods else 'None'}")
    
    if ocr_methods:
        print("✅ OCR functionality is available!")
    else:
        print("❌ No OCR methods available")
    
    return len(ocr_methods) > 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Ready to run GS Oasis with OCR support!")
    else:
        print("\n⚠️  GS Oasis will run with limited OCR functionality")
