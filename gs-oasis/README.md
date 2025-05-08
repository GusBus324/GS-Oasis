# GS Oasis Project

## Overview
GS Oasis is a comprehensive web application designed to help users detect and protect against scams by scanning images, links, and files for suspicious content. The application leverages OCR (Optical Character Recognition) and image analysis techniques to identify potential scams.

## Project Structure
```
gs-oasis
├── static
│   ├── css
│   │   └── style.css
│   ├── images
│   │   └── Logo.png
│   ├── js
│   │   ├── main.js
│   │   ├── scan.js
│   │   └── script.js
│   └── temp
├── templates
│   ├── about.html
│   ├── ai_assistant.html
│   ├── auth.html
│   ├── base.html
│   ├── footer.html
│   ├── header.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── resources.html
│   ├── scan_file.html
│   ├── scan_image.html
│   ├── scan_link.html
│   ├── scan_results.html
│   ├── scan.html
│   └── users.html
├── app.py
├── config.py
├── database.db
├── requirements.txt
└── README.md
```

## Installation

### Basic Setup
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd gs-oasis
   ```
3. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

### Installing Tesseract OCR for Image Text Extraction
The OCR functionality requires Tesseract to be installed on your system:

#### For macOS:
1. Install Tesseract using Homebrew:
   ```
   brew install tesseract
   ```
2. Verify installation:
   ```
   tesseract --version
   ```

#### For Windows:
1. Download and install the latest installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Add Tesseract to your PATH environment variable
3. Verify installation:
   ```
   tesseract --version
   ```

#### For Linux:
1. Install using apt:
   ```
   sudo apt update
   sudo apt install tesseract-ocr
   ```
2. Verify installation:
   ```
   tesseract --version
   ```

### Installing OpenCV for Image Analysis

#### For macOS:
1. Install OpenCV using pip:
   ```
   pip install opencv-python
   ```
   
   If you encounter issues, try installing with Homebrew first:
   ```
   brew install opencv
   ```
   Then install the Python bindings:
   ```
   pip install opencv-python
   ```

#### For Windows and Linux:
1. Install using pip:
   ```
   pip install opencv-python
   ```

## Running the Application
To run the application, execute the following command:
```
python app.py
```
The application will start on `http://127.0.0.1:5000/` by default.

## Features
- Image scanning: Upload and scan images for potential scam indicators
- Link scanning: Check URLs for suspicious patterns
- File scanning: Analyze documents for scam content
- User authentication: Secure login and registration
- AI assistant: Get help understanding potential scams
- Educational resources: Learn about common scam techniques

## Troubleshooting

### OCR Issues
If you see "OCR failed: tesseract is not installed or it's not in your PATH":
1. Ensure Tesseract is properly installed (see installation instructions above)
2. Verify the installation is in your PATH by running `tesseract --version` in your terminal
3. For macOS, you may need to restart your terminal after installation

### OpenCV Issues
If you see "OpenCV not available for advanced image analysis":
1. Install OpenCV using the instructions above
2. Try reinstalling with: `pip uninstall opencv-python && pip install opencv-python`
3. For macOS, you might need additional dependencies: `brew install cmake pkg-config`

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.