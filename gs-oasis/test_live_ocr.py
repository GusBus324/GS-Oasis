#!/usr/bin/env python3
"""
Test script to verify OCR functionality with existing images
"""
import os
import sys
from PIL import Image

# Import our app's OCR function
try:
    from app import analyze_image_content
    print("✅ Successfully imported analyze_image_content from app")
except ImportError as e:
    print(f"❌ Failed to import analyze_image_content: {e}")
    sys.exit(1)

def test_ocr_with_existing_images():
    """Test OCR with images in the temp folder"""
    temp_dir = "static/temp"
    
    if not os.path.exists(temp_dir):
        print(f"❌ Temp directory '{temp_dir}' not found")
        return
    
    # Get list of images
    image_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"❌ No image files found in '{temp_dir}'")
        return
    
    print(f"📁 Found {len(image_files)} images in temp directory")
    
    # Test with the first image
    test_image = image_files[0]
    image_path = os.path.join(temp_dir, test_image)
    
    print(f"\n🔍 Testing OCR with: {test_image}")
    print("=" * 50)
    
    try:
        # Open and verify the image
        with Image.open(image_path) as img:
            print(f"📸 Image size: {img.size}")
            print(f"📸 Image mode: {img.mode}")
        
        # Test our OCR function
        print("\n🔄 Running OCR analysis...")
        extracted_text = analyze_image_content(image_path)
        
        print(f"\n📝 Extracted text ({len(extracted_text)} characters):")
        print("-" * 40)
        if extracted_text.strip():
            print(extracted_text)
        else:
            print("(No text extracted)")
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OCR: {e}")
        return False

if __name__ == "__main__":
    print("GS Oasis Live OCR Test")
    print("=" * 30)
    
    success = test_ocr_with_existing_images()
    
    if success:
        print("\n✅ OCR test completed successfully!")
    else:
        print("\n❌ OCR test failed!")
