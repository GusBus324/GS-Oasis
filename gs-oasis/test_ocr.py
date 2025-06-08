#!/usr/bin/env python3
"""
Test OCR functionality with Google Cloud Vision API
Run this after setting up your Google Cloud credentials.
"""

import os
import sys

def test_ocr():
    print("=== Testing OCR Setup ===\n")
    
    # Test 1: Check if Google Cloud Vision is available
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision library is installed")
    except ImportError:
        print("❌ Google Cloud Vision library not found")
        print("Run: pip install google-cloud-vision")
        return False
    
    # Test 2: Check credentials
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        print("\nTo fix this:")
        print("1. Download your JSON credentials file from Google Cloud Console")
        print("2. Run: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/credentials.json'")
        print("3. Or add it to your ~/.zshrc file for permanent setup")
        return False
    
    creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set to: {creds_path}")
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file does not exist: {creds_path}")
        return False
    
    print("✅ Credentials file exists")
    
    # Test 3: Try to create Vision client
    try:
        client = vision.ImageAnnotatorClient()
        print("✅ Google Cloud Vision client created successfully")
    except Exception as e:
        print(f"❌ Error creating Vision client: {e}")
        return False
    
    print("\n🎉 OCR setup is working! Your GS Oasis app can now extract text from images.")
    return True

def test_tesseract():
    print("\n=== Testing Tesseract (Alternative) ===\n")
    
    # Test Tesseract
    try:
        import pytesseract
        print("✅ pytesseract library is installed")
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract is working, version: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract not working: {e}")
            print("Tesseract binary needs to be installed separately")
            return False
    except ImportError:
        print("❌ pytesseract library not found")
        return False

def test_easyocr():
    print("\n=== Testing EasyOCR (Alternative) ===\n")
    
    # Test EasyOCR
    try:
        import easyocr
        print("✅ EasyOCR library is installed")
        
        try:
            # Try to initialize EasyOCR reader (this will download models on first run)
            print("🔄 Initializing EasyOCR reader (may download models on first run)...")
            reader = easyocr.Reader(['en'], verbose=False)
            print("✅ EasyOCR is working and ready to use")
            return True
        except Exception as e:
            print(f"❌ EasyOCR initialization failed: {e}")
            return False
    except ImportError:
        print("❌ EasyOCR library not found")
        print("Run: pip install easyocr")
        return False

if __name__ == "__main__":
    print("GS Oasis OCR Test Script")
    print("=" * 40)
    
    vision_works = test_ocr()
    tesseract_works = test_tesseract()
    easyocr_works = test_easyocr()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    if vision_works:
        print("✅ Google Cloud Vision API is ready to use")
    elif easyocr_works:
        print("✅ EasyOCR is ready to use")
    elif tesseract_works:
        print("✅ Tesseract OCR is ready to use")
    else:
        print("❌ No OCR method is currently working")
        print("\nRecommendations:")
        print("1. Set up Google Cloud Vision API (most reliable)")
        print("2. Install EasyOCR (easiest: pip install easyocr)")
        print("3. Install Tesseract binary (requires admin access)")
        print("\nInstructions: https://cloud.google.com/vision/docs/setup")
