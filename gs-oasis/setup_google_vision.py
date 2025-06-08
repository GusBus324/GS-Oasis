#!/usr/bin/env python3
"""
Setup script for Google Cloud Vision API
This script helps you configure Google Cloud Vision for OCR functionality.
"""

import os
import json

def main():
    print("=== Google Cloud Vision API Setup ===")
    print()
    
    print("To use Google Cloud Vision API for OCR, you need to:")
    print("1. Create a Google Cloud account at: https://cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable the Cloud Vision API")
    print("4. Create a service account and download JSON credentials")
    print("5. Set the GOOGLE_APPLICATION_CREDENTIALS environment variable")
    print()
    
    # Check if credentials are already set
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is already set to: {creds_path}")
        
        if os.path.exists(creds_path):
            print("✅ Credentials file exists")
            try:
                with open(creds_path, 'r') as f:
                    creds = json.load(f)
                    print(f"✅ Project ID: {creds.get('project_id', 'Not found')}")
            except Exception as e:
                print(f"❌ Error reading credentials: {e}")
        else:
            print("❌ Credentials file does not exist")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print()
        print("To set it temporarily for this session:")
        print('export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"')
        print()
        print("To set it permanently, add the above line to your ~/.zshrc file")
    
    print()
    print("=== Alternative: Try to install Tesseract manually ===")
    print()
    print("If you prefer to use Tesseract instead of Google Cloud Vision:")
    print("1. Download Tesseract from: https://github.com/tesseract-ocr/tesseract/releases")
    print("2. Or try installing with: python3 -m pip install tesseract")
    print("3. Or ask your system administrator to install it")
    
    # Test current setup
    print()
    print("=== Testing Current Setup ===")
    
    try:
        import pytesseract
        print("✅ pytesseract Python package is installed")
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract binary is working")
        except Exception as e:
            print(f"❌ Tesseract binary not working: {e}")
    except ImportError:
        print("❌ pytesseract not installed")
    
    try:
        from google.cloud import vision
        print("✅ Google Cloud Vision package is installed")
        
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            try:
                client = vision.ImageAnnotatorClient()
                print("✅ Google Cloud Vision client can be created")
            except Exception as e:
                print(f"❌ Google Cloud Vision client error: {e}")
        else:
            print("ℹ️ Google Cloud Vision available but credentials not set")
    except ImportError:
        print("❌ Google Cloud Vision not installed")

if __name__ == "__main__":
    main()
