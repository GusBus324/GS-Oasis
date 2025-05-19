"""
Script to check if Tesseract OCR is installed and working correctly.
If not, it will provide instructions for installation.
"""

import os
import sys
import platform
import subprocess

def check_tesseract():
    """Check if Tesseract is installed and accessible"""
    try:
        # Try to import pytesseract
        import pytesseract
        
        # Try to get tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is installed (version: {version})")
        print("✅ pytesseract Python package is installed")
        return True
    except ImportError:
        print("❌ pytesseract Python package is not installed.")
        print("   Install it with: pip install pytesseract")
        return False
    except Exception as e:
        # pytesseract is installed but tesseract binary might not be
        print(f"❌ Error checking Tesseract: {str(e)}")
        print("   This usually means the Tesseract binary is not installed or not in PATH")
        
        # Provide installation instructions based on operating system
        system = platform.system()
        if system == "Windows":
            print("\nInstallation instructions for Windows:")
            print("1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("2. Install and ensure you check 'Add to PATH' during installation")
            print("3. Restart your terminal/IDE after installation")
        elif system == "Darwin":  # macOS
            print("\nInstallation instructions for macOS:")
            print("1. Install Homebrew if not installed: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. Install Tesseract: brew install tesseract")
        elif system == "Linux":
            print("\nInstallation instructions for Linux:")
            print("1. Install Tesseract: sudo apt-get install tesseract-ocr")
            print("2. Install language data: sudo apt-get install tesseract-ocr-eng")
        
        return False

def check_permissions():
    """Check if user has admin permissions"""
    try:
        # Try to write to a system directory
        test_dir = "/usr/local/bin" if platform.system() != "Windows" else "C:\\Windows\\System32"
        test_file = os.path.join(test_dir, "test_write_permissions.txt")
        
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (PermissionError, OSError):
        return False

def main():
    """Main function to check dependencies"""
    print("Checking OCR dependencies...\n")
    
    tesseract_ok = check_tesseract()
    
    # Also check OpenCV while we're at it
    try:
        import cv2
        print(f"✅ OpenCV is installed (version: {cv2.__version__})")
    except ImportError:
        print("❌ OpenCV is not installed.")
        print("   Install it with: pip install opencv-python")
    
    # Check if user has admin permissions
    has_admin = check_permissions()
    
    print("\nSummary:")
    if tesseract_ok:
        print("✅ OCR functionality should work correctly!")
    else:
        print("❌ OCR functionality will NOT work until Tesseract is installed.")
        
        if not has_admin:
            print("\n⚠️ Notice: You appear to be running without admin privileges.")
            print("   This may prevent you from installing Tesseract.")
            print("   Consider these alternatives:")
            print("   1. Use GS Oasis without OCR functionality")
            print("   2. Set up Google Cloud Vision API (see OCR_INSTALLATION.md)")
            print("   3. Ask your system administrator for help installing Tesseract")
        else:
            print("   Please follow the installation instructions above.")
    
    print("\nNote: After installing Tesseract, you may need to restart your application.")

if __name__ == "__main__":
    main()
