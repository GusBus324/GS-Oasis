# OCR Installation Guide for GS Oasis

## About OCR in GS Oasis

GS Oasis uses Optical Character Recognition (OCR) to extract text from images during scanning. This helps identify potential scams or suspicious content in images by analyzing the text content.

## Options for OCR Functionality

### Option 1: EasyOCR (Recommended - No Admin Required)

EasyOCR is now integrated as the easiest OCR solution that doesn't require administrator privileges:

1. Install EasyOCR:
   ```
   pip install easyocr
   ```

2. EasyOCR will automatically download required models on first use
3. No additional configuration needed - works out of the box!

**Advantages:**
- No administrator access required
- Works offline after initial model download
- Supports multiple languages
- Good accuracy for most text types

### Option 2: Google Cloud Vision API (Cloud-based)

If you prefer a cloud-based solution or EasyOCR doesn't work for you:

1. Create a free Google Cloud account at https://cloud.google.com/
2. Enable the Vision API in Google Cloud Console
3. Create a service account and download the JSON credentials file
4. Install the Google Cloud Vision library:
   ```
   pip install google-cloud-vision
   ```
5. Set the environment variable to your credentials file:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-credentials.json"
   ```

### Option 3: Using GS Oasis Without OCR

The application will work without OCR, but with reduced functionality:
- Image scanning will continue to work using alternative methods
- Text extraction from images will not be available
- Other security features like QR code detection will still work

### Option 4: Tesseract OCR (Requires Admin Privileges)

#### macOS

1. Install using Homebrew:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install tesseract
   ```

2. Verify installation:
   ```
   tesseract --version
   ```

#### Windows

1. Download the installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and make sure to check "Add to PATH" during installation

#### Linux (Ubuntu/Debian)

1. Install using apt:
   ```
   sudo apt update
   sudo apt install tesseract-ocr
   sudo apt install libtesseract-dev
   ```

### Option 4: Ask Your System Administrator

If you're using a managed computer, you might need to ask your system administrator to install Tesseract for you.

## Testing OCR Installation

After installing Tesseract or configuring Cloud Vision, you can run the following test script to verify it's working:

```
python check_tesseract.py
```

## Troubleshooting

If you encounter issues:
1. Check that pytesseract is installed: `pip install pytesseract`
2. Ensure the application has proper permissions
3. Try restarting your application after installation