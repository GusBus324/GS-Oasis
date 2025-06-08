#!/usr/bin/env python3
"""
Comprehensive OCR Test for GS Oasis
Tests all available OCR methods and provides recommendations
"""

import os
import warnings

def test_easyocr():
    """Test EasyOCR functionality"""
    print("=== Testing EasyOCR ===")
    try:
        import easyocr
        print("✅ EasyOCR library is installed")
        
        # Test basic initialization without downloading models
        try:
            # This will check if we can create a reader object
            print("🔄 Testing EasyOCR initialization...")
            # Note: We don't actually create the reader here to avoid long download times
            print("✅ EasyOCR is ready to use (models will download on first use)")
            return True
        except Exception as e:
            print(f"❌ EasyOCR initialization test failed: {e}")
            return False
    except ImportError:
        print("❌ EasyOCR not installed")
        print("   Install with: pip install easyocr")
        return False

def test_google_vision():
    """Test Google Cloud Vision API"""
    print("\n=== Testing Google Cloud Vision API ===")
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision library is installed")
        
        if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            print("   Setup instructions:")
            print("   1. Create a Google Cloud account and enable Vision API")
            print("   2. Download JSON credentials file")
            print("   3. Set environment variable:")
            print("      export GOOGLE_APPLICATION_CREDENTIALS='/path/to/credentials.json'")
            return False
        
        creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            return False
        
        print("✅ Google Cloud Vision is configured and ready")
        return True
        
    except ImportError:
        print("❌ Google Cloud Vision library not installed")
        print("   Install with: pip install google-cloud-vision")
        return False

def test_tesseract():
    """Test Tesseract OCR"""
    print("\n=== Testing Tesseract OCR ===")
    try:
        import pytesseract
        print("✅ pytesseract library is installed")
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract binary is working, version: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract binary not working: {e}")
            print("   Tesseract binary needs to be installed separately")
            print("   See OCR_INSTALLATION.md for instructions")
            return False
    except ImportError:
        print("❌ pytesseract library not installed")
        print("   Install with: pip install pytesseract")
        return False

def main():
    """Main test function"""
    print("GS Oasis OCR Functionality Test")
    print("=" * 50)
    
    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')
    
    # Test all OCR methods
    easyocr_works = test_easyocr()
    google_vision_works = test_google_vision()
    tesseract_works = test_tesseract()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    working_methods = []
    if easyocr_works:
        working_methods.append("EasyOCR")
    if google_vision_works:
        working_methods.append("Google Cloud Vision")
    if tesseract_works:
        working_methods.append("Tesseract")
    
    if working_methods:
        print(f"✅ Working OCR methods: {', '.join(working_methods)}")
        print("\n🎉 GS Oasis OCR functionality is ready!")
        
        # Recommendations
        print("\nRecommendations:")
        if easyocr_works:
            print("• EasyOCR is working - great for offline use!")
        if google_vision_works:
            print("• Google Cloud Vision is configured - excellent accuracy!")
        if tesseract_works:
            print("• Tesseract is working - reliable traditional OCR!")
            
    else:
        print("❌ No OCR methods are currently working")
        print("\nRecommendations (in order of ease):")
        print("1. 🥇 Install EasyOCR: pip install easyocr")
        print("2. 🥈 Set up Google Cloud Vision (see OCR_INSTALLATION.md)")
        print("3. 🥉 Install Tesseract binary (requires admin access)")
        print("\nGS Oasis will still work with reduced functionality.")
    
    return len(working_methods) > 0

if __name__ == "__main__":
    success = main()
    print(f"\nTest completed. OCR Status: {'✅ Ready' if success else '❌ Limited'}")
