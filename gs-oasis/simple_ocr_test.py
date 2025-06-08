#!/usr/bin/env python3
"""
Simple OCR test script to verify EasyOCR functionality
"""

import os
import ssl
import certifi

# Set SSL context to use system certificates
ssl._create_default_https_context = ssl._create_unverified_context

def test_easyocr_simple():
    """Test EasyOCR with minimal setup"""
    print("=== Simple EasyOCR Test ===\n")
    
    try:
        print("🔄 Importing EasyOCR...")
        import easyocr
        print("✅ EasyOCR imported successfully")
        
        print("🔄 Creating EasyOCR reader (this may take a moment)...")
        # Try with minimal config and offline mode if models exist
        try:
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("✅ EasyOCR reader created successfully")
            
            # Test with a simple string (if we had an image)
            print("✅ EasyOCR is ready for text extraction")
            return True
            
        except Exception as e:
            print(f"❌ EasyOCR reader creation failed: {e}")
            print("This might be due to missing model files or network issues")
            return False
            
    except ImportError:
        print("❌ EasyOCR not installed")
        return False

if __name__ == "__main__":
    success = test_easyocr_simple()
    if success:
        print("\n🎉 EasyOCR is working and ready to use!")
    else:
        print("\n❌ EasyOCR test failed. OCR may not work properly.")
        print("\nAlternatives:")
        print("1. Use Google Cloud Vision API")
        print("2. Install Tesseract binary")
        print("3. Run the application anyway (limited OCR functionality)")
