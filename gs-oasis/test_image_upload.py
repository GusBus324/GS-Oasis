#!/usr/bin/env python3
"""
Test script to simulate image upload and scanning functionality
"""

import os
import sys
import tempfile
import shutil
from io import BytesIO
from PIL import Image

# Add the current directory to the path
sys.path.append('.')

def create_test_image():
    """Create a simple test image with text"""
    # Create a simple image with text-like patterns
    img = Image.new('RGB', (400, 200), color='white')
    # We can't easily add real text without external libraries,
    # but we can create a pattern that might trigger text detection
    pixels = img.load()
    
    # Create some horizontal lines that might look like text
    for y in range(50, 60):
        for x in range(50, 350):
            pixels[x, y] = (0, 0, 0)  # Black line
    
    for y in range(80, 90):
        for x in range(50, 250):
            pixels[x, y] = (0, 0, 0)  # Another black line
    
    for y in range(110, 120):
        for x in range(50, 300):
            pixels[x, y] = (0, 0, 0)  # Another black line
    
    return img

def test_image_scanning():
    """Test the image scanning functionality"""
    try:
        # Import the app and functions
        from app import app, analyze_image_content
        
        print("=== TESTING IMAGE SCANNING FUNCTIONALITY ===")
        
        # Create a test image
        test_img = create_test_image()
        
        # Save it to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            test_img.save(temp_file.name, 'PNG')
            temp_path = temp_file.name
        
        print(f"Created test image: {temp_path}")
        
        try:
            # Test the analyze_image_content function
            print("\n--- Testing analyze_image_content function ---")
            result = analyze_image_content(temp_path)
            
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result) if isinstance(result, (tuple, list)) else 'Not a sequence'}")
            
            if isinstance(result, tuple) and len(result) == 3:
                extracted_text, analysis_results, performed_checks = result
                print("✅ Successfully unpacked tuple!")
                print(f"Extracted text: {extracted_text[:100]}..." if len(extracted_text) > 100 else f"Extracted text: {extracted_text}")
                print(f"Analysis results count: {len(analysis_results)}")
                print(f"Performed checks count: {len(performed_checks)}")
                
                # Show some analysis results
                print("\nAnalysis results:")
                for i, result in enumerate(analysis_results[:5]):  # Show first 5
                    print(f"  {i+1}. {result}")
                
                print("\nPerformed checks:")
                for i, check in enumerate(performed_checks):
                    print(f"  {i+1}. {check}")
                    
            else:
                print("❌ Unexpected result format!")
                print(f"Result: {result}")
            
            # Test with the Flask app
            print("\n--- Testing Flask app image upload route ---")
            with app.test_client() as client:
                # Read the test image
                with open(temp_path, 'rb') as f:
                    img_data = f.read()
                
                # Simulate file upload
                response = client.post('/scan_image', 
                                     data={'file': (BytesIO(img_data), 'test.png')},
                                     content_type='multipart/form-data')
                
                print(f"Upload response status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Image upload successful!")
                    # The response should be the scan_results.html page
                    response_text = response.get_data(as_text=True)
                    if 'scan_results' in response_text or 'analysis' in response_text.lower():
                        print("✅ Response contains expected scan results content")
                    else:
                        print("⚠️  Response might not contain scan results")
                        print(f"Response preview: {response_text[:200]}...")
                else:
                    print(f"❌ Upload failed with status {response.status_code}")
                    print(f"Response: {response.get_data(as_text=True)[:500]}")
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print(f"\nCleaned up test image: {temp_path}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_image_scanning()
