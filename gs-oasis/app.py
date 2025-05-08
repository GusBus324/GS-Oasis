from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
import io
import time
import numpy as np
from functools import wraps
import PyPDF2
from PIL import Image
import hashlib

# Try to import image analysis libraries
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "gs-oasis-secret-key"  # Required for flash messages

# Create directory for temporary files if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'static/temp'), exist_ok=True)

# Initialize SQLite database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Scam detection function - analyzes text for suspicious content
def check_for_scam(text):
    """
    Analyze text content to detect potential scams or phishing attempts
    Returns a tuple (is_scam, confidence, reasons)
    """
    if not text or not isinstance(text, str):
        return False, 0, []
    
    # Convert text to lowercase for easier matching
    text = text.lower()
    
    # Common scam indicators with weights
    scam_indicators = {
        # Urgency indicators
        'urgent': 3, 'immediately': 3, 'act now': 4, 'limited time': 3,
        
        # Financial bait
        'free money': 5, 'cash prize': 5, 'lottery winner': 5, 'you won': 4,
        'million dollars': 5, 'get rich': 5, 'double your money': 5,
        'cash bonus': 4, 'free gift': 3,
        
        # Request for personal information
        'verify your account': 4, 'update your information': 3,
        'confirm your identity': 4, 'security check': 3,
        'unusual activity': 3, 'suspicious activity': 3,
        
        # Common phishing phrases
        'dear customer': 2, 'dear user': 2, 'valued customer': 2,
        'account suspended': 4, 'account locked': 4, 'unauthorized access': 3,
        
        # Technical deception
        'tech support': 3, 'customer service': 2, 'help desk': 2,
        'virus detected': 4, 'malware detected': 4, 'your computer is infected': 5,
        'security breach': 4,
        
        # Transaction scams
        'payment pending': 3, 'transaction failed': 3, 'refund': 3,
        'billing information': 3, 'invoice attached': 3, 'receipt': 2,
        
        # Government impersonation
        'tax refund': 4, 'government grant': 4, 'irs': 3, 
        'social security': 4, 'legal action': 4, 'lawsuit': 3,
        
        # Common misspellings in legitimate company names (sign of phishing)
        'micr0soft': 5, 'app1e': 5, 'amaz0n': 5, 'g00gle': 5, 'paypa1': 5,
        
        # Cryptocurrency scams
        'bitcoin': 2, 'cryptocurrency': 2, 'crypto': 2, 'invest now': 4,
        'guaranteed return': 5, 'blockchain opportunity': 3,
        
        # Romance scams
        'looking for love': 3, 'found you attractive': 3, 'dating profile': 2,
        
        # Job scams
        'work from home': 2, 'make money online': 3, 'be your own boss': 3,
        'earn extra income': 2, 'job opportunity': 1, 'high paying job': 3
    }
    
    # Look for domain mismatches (e.g. apple.com-secure.xyz)
    domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z0-9-.]+'
    domains = re.findall(domain_pattern, text)
    
    suspicious_domains = [
        'secure-login', 'account-verify', 'signin', 'login-secure',
        'verification', 'secure-verify', 'update-account'
    ]
    
    # Check for indicators in the text
    found_indicators = []
    score = 0
    max_score = 0
    
    for indicator, weight in scam_indicators.items():
        max_score += weight
        if indicator in text:
            found_indicators.append(indicator)
            score += weight
    
    # Check for suspicious domains
    for domain in domains:
        for sus_domain in suspicious_domains:
            if sus_domain in domain:
                found_indicators.append(f"Suspicious domain: {domain}")
                score += 4
                break
    
    # Normalize score to a 0-100 scale
    if max_score > 0:
        confidence = min(100, int((score / max_score) * 100))
    else:
        confidence = 0
    
    # Determine if it's a potential scam based on confidence threshold
    is_scam = confidence > 30  # Adjust threshold as needed
    
    # Generate reasons if it's a potential scam
    reasons = []
    if is_scam:
        if len(found_indicators) > 0:
            reasons.append(f"Found suspicious content: {', '.join(found_indicators[:5])}")
        if 'urgent' in text or 'immediately' in text:
            reasons.append("Creates false urgency")
        if any(term in text for term in ['free money', 'cash prize', 'lottery', 'won']):
            reasons.append("Promises unrealistic financial rewards")
        if any(term in text for term in ['verify', 'update your', 'confirm your']):
            reasons.append("Requests personal information")
    
    return is_scam, confidence, reasons

# Middleware to check if user is logged in
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')  # Updated home page to include login and sign-up options

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/scan_image', methods=['GET', 'POST'])
@login_required
def scan_image():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No image part in the request', 'danger')
            return redirect(request.url)
            
        file = request.files['image']
        
        # If user does not select file, browser may submit an empty file
        if file.filename == '':
            flash('No image selected', 'danger')
            return redirect(request.url)
            
        if file:
            # Default values
            is_scam = False
            confidence = 0
            reasons = []
            
            try:
                # Generate a unique filename for the temp image
                timestamp = str(int(os.path.getmtime(__file__))) if os.path.exists(__file__) else str(int(time.time()))
                unique_id = hashlib.md5((file.filename + timestamp).encode()).hexdigest()[:10]
                temp_filename = f"scan_{unique_id}_{os.path.basename(file.filename)}"
                temp_path = os.path.join(os.path.dirname(__file__), 'static/temp', temp_filename)
                
                # Save image temporarily for analysis
                file.save(temp_path)
                
                # Perform comprehensive image analysis
                extracted_text, analysis_results, performed_checks = analyze_image_content(temp_path)
                
                # Analyze the extracted text for scams if we got any
                if extracted_text:
                    is_scam, confidence, reasons = check_for_scam(extracted_text)
                
                # Create a detailed result message
                if is_scam:
                    risk_level = "High Risk" if confidence > 60 else "Medium Risk"
                    result_msg = f"⚠️ {risk_level}: This image contains text with indicators of a potential scam ({confidence}% confidence)."
                    for reason in reasons:
                        result_msg += f"\n• {reason}"
                    result_msg += "\n\nRecommendation: Do not trust information in this image or follow instructions within it."
                else:
                    # Check if any of the analysis results indicate suspicious content
                    suspicious_keywords = ['suspicious', 'hiding', 'manipulated', 'blurry', 'qr code']
                    suspicious_analysis = [result for result in analysis_results 
                                          if any(keyword in result.lower() for keyword in suspicious_keywords)]
                    
                    if suspicious_analysis:
                        result_msg = f"⚠️ Caution Advised: While no scam text was detected, our scan found potential issues with this image:"
                        for finding in suspicious_analysis:
                            result_msg += f"\n• {finding}"
                        result_msg += "\n\nRecommendation: Exercise caution with this image."
                    else:
                        checks_text = ", ".join(performed_checks) if performed_checks else "Basic analysis"
                        result_msg = f"✅ No suspicious content detected.\n\nAnalysis performed: {checks_text}"
                        
                        # Add a note about what was found in the image
                        if analysis_results:
                            result_msg += "\n\nFindings:"
                            for finding in analysis_results[:5]:  # Limit to first 5 findings
                                result_msg += f"\n• {finding}"
                
                # Add information about extracted text
                if extracted_text and len(extracted_text) > 20:
                    # Only show a snippet if there's a lot of text
                    text_preview = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
                    result_msg += f"\n\nExtracted text sample: \"{text_preview}\""
                
                # Clean up temporary file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Store scan results for the results page
                session['last_scan_type'] = 'image'
                session['last_scan_result'] = result_msg.replace("\n", "<br>")
                session['last_scan_filename'] = file.filename
                
                flash('Image scanned successfully!', 'success')
                return redirect(url_for('scan_results'))
                
            except Exception as e:
                flash(f'Error scanning image: {str(e)}', 'danger')
                # Clean up temporary file if it exists
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
                return redirect(request.url)
            
    return render_template('scan_image.html')

@app.route('/scan_link', methods=['GET', 'POST'])
@login_required
def scan_link():
    if request.method == 'POST':
        link = request.form.get('link')
        
        if not link:
            flash('No link provided', 'danger')
            return redirect(request.url)
        
        # Perform scam detection on the link
        is_scam, confidence, reasons = check_for_scam(link)
        
        # Create a detailed result message
        if is_scam:
            risk_level = "High Risk" if confidence > 60 else "Medium Risk"
            result_msg = f"⚠️ {risk_level}: This link shows indicators of a potential scam ({confidence}% confidence)."
            for reason in reasons:
                result_msg += f"\n• {reason}"
            result_msg += "\n\nRecommendation: Do not visit this website or provide any information."
        else:
            result_msg = f"✅ No known threats detected in this link.\nNote: While no threats were detected, always remain cautious when visiting unfamiliar websites."
            
        # Store scan results for the results page
        session['last_scan_type'] = 'link'
        session['last_scan_result'] = result_msg.replace("\n", "<br>")
        session['last_scan_url'] = link
        
        flash('Link scanned successfully!', 'success')
        return redirect(url_for('scan_results'))
            
    return render_template('scan_link.html')

@app.route('/scan_file', methods=['GET', 'POST'])
@login_required
def scan_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        # If user does not select file, browser may submit an empty file
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if file:
            # Get file extension to determine how to extract text
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # Default values
            is_scam = False
            confidence = 0
            reasons = []
            extracted_text = ""
            
            # Extract text based on file type
            try:
                if file_ext == '.txt':
                    # Read text file directly
                    extracted_text = file.read().decode('utf-8', errors='ignore')
                    
                elif file_ext == '.pdf':
                    # Extract text from PDF
                    try:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            extracted_text += page.extract_text() + " "
                    except Exception as e:
                        flash(f'Error reading PDF: {str(e)}', 'warning')
                
                elif file_ext in ['.doc', '.docx']:
                    # For Word documents, we'd need additional libraries
                    # This is a placeholder for implementation with python-docx
                    flash('Word document scanning is currently under development.', 'info')
                    extracted_text = file.filename  # Just use filename for now
                
                else:
                    # For other file types, just analyze the filename
                    extracted_text = file.filename
                    flash('Full content scanning not available for this file type. Analyzing filename only.', 'info')
                
                # Perform scam detection on the extracted text
                if extracted_text:
                    is_scam, confidence, reasons = check_for_scam(extracted_text)
                
                # Create a detailed result message
                if is_scam:
                    risk_level = "High Risk" if confidence > 60 else "Medium Risk"
                    result_msg = f"⚠️ {risk_level}: This file contains indicators of a potential scam ({confidence}% confidence)."
                    for reason in reasons:
                        result_msg += f"\n• {reason}"
                    result_msg += "\n\nRecommendation: Do not share this file or follow instructions within it."
                else:
                    result_msg = f"✅ No scam indicators detected in the file content.\nNote: While no threats were detected, always remain cautious with files from unknown sources."
                
                # Store scan results for the results page
                session['last_scan_type'] = 'file'
                session['last_scan_result'] = result_msg.replace("\n", "<br>")
                session['last_scan_filename'] = file.filename
                
                flash('File scanned successfully!', 'success')
                return redirect(url_for('scan_results'))
            
            except Exception as e:
                flash(f'Error scanning file: {str(e)}', 'danger')
                return redirect(request.url)
            
    return render_template('scan_file.html')

@app.route('/scan_results')
@login_required
def scan_results():
    # Get scan results from session
    scan_type = session.get('last_scan_type', None)
    result = session.get('last_scan_result', 'No scan results available.')
    
    if not scan_type:
        flash('No scan results found. Please perform a scan first.', 'warning')
        return redirect(url_for('index'))
        
    return render_template('scan_results.html', scan_type=scan_type, result=result)

@app.route('/ai_assistant', methods=['GET', 'POST'])
@login_required
def ai_assistant():
    response = None
    if request.method == 'POST':
        user_question = request.form.get('question')
        # AI processing logic would go here
        response = f"This is a placeholder response for: {user_question}"
    return render_template('ai_assistant.html', response=response)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Password validation
        password_regex = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$'
        if not re.match(password_regex, password):
            flash('Password must be at least 8 characters long, include at least 2 numbers, and 1 special symbol.', 'danger')
            return render_template('register.html')

        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                               (username, email, generate_password_hash(password)))
                conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

        if not user or not check_password_hash(user[0], password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        session['user_id'] = username  # Store the username in session
        flash('Login successful!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/users')
def users_list():
    # Fetch users from the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users')
        users = cursor.fetchall()
    return render_template('users.html', users=users)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/logo.png')
def logo():
    return send_from_directory('static/images', 'Logo.png')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# Image analysis utilities
def analyze_image_content(image_path):
    """
    Analyze an image for suspicious elements and extract text.
    Returns a tuple (extracted_text, analysis_results, performed_checks)
    """
    analysis_results = []
    performed_checks = []
    extracted_text = ""
    
    # 1. Check if the image exists
    if not os.path.exists(image_path):
        return extracted_text, ["Image file not found or inaccessible"], ["File access check"]
    
    # 2. Extract text using OCR if available
    if OCR_AVAILABLE:
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            performed_checks.append("Text extraction (OCR)")
            
            if extracted_text:
                analysis_results.append(f"Extracted {len(extracted_text)} characters of text from image")
        except Exception as e:
            analysis_results.append(f"OCR failed: {str(e)}")
    
    # 3. Perform visual analysis using OpenCV if available
    if OPENCV_AVAILABLE:
        try:
            # Read the image with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                analysis_results.append("Could not load image for analysis")
                return extracted_text, analysis_results, performed_checks
            
            # Get image dimensions and calculate image hash for analysis
            height, width, channels = img.shape
            performed_checks.append("Image integrity check")
            performed_checks.append("Visual content analysis")
            
            # Check image dimensions (unusually large or small images might be suspicious)
            if width < 100 or height < 100:
                analysis_results.append("Image is unusually small, may be hiding content")
            
            # Basic image quality check
            blurriness = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            if blurriness < 100:  # Arbitrary threshold, adjust as needed
                analysis_results.append("Image appears blurry, which may indicate manipulation")
            
            # Check for hidden text that OCR might have missed using edge detection
            edges = cv2.Canny(img, 100, 200)
            text_region_ratio = np.count_nonzero(edges) / (height * width)
            if text_region_ratio > 0.1 and not extracted_text:  # If there seem to be text-like edges but OCR found nothing
                analysis_results.append("Image may contain text that couldn't be extracted")
            
            # Compute image hash for potential comparison with known scam images
            img_hash = hashlib.md5(img.tobytes()).hexdigest()
            # In a real system, you would compare against a database of known scam image hashes
            
            # Check for QR codes or barcodes that might lead to malicious sites
            try:
                # This is a simplified check. In production, you'd use a dedicated QR code scanner
                qr_detector = cv2.QRCodeDetector()
                retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(img)
                
                if retval:
                    performed_checks.append("QR code detection")
                    analysis_results.append(f"Found QR code in image that points to: {decoded_info}")
                    # Analyze the QR URL for potential scams
                    for url in decoded_info:
                        if url:
                            is_scam, confidence, reasons = check_for_scam(url)
                            if is_scam:
                                analysis_results.append(f"QR code contains suspicious URL: {url}")
            except Exception as e:
                # QR detection is optional, don't fail if this doesn't work
                pass
            
        except Exception as e:
            analysis_results.append(f"Visual analysis failed: {str(e)}")
    else:
        analysis_results.append("OpenCV not available for advanced image analysis")
    
    # 4. Check metadata (EXIF data) for any suspicious elements
    try:
        with Image.open(image_path) as img:
            performed_checks.append("Metadata analysis")
            exif_data = img._getexif()
            if exif_data:
                # Just note that we found metadata
                analysis_results.append("Image contains metadata/EXIF data")
            
            # Check for common image manipulation
            if img.format == 'PNG' and img.mode == 'RGBA':
                # Check for transparency which could be hiding content
                transparent_pixels = 0
                for pixel in img.getdata():
                    if len(pixel) == 4 and pixel[3] < 255:  # Alpha channel < 255 means some transparency
                        transparent_pixels += 1
                
                if transparent_pixels > 0:
                    analysis_results.append(f"Image has {transparent_pixels} transparent pixels which might hide content")
    except Exception as e:
        analysis_results.append(f"Metadata analysis failed: {str(e)}")
    
    return extracted_text, analysis_results, performed_checks

if __name__ == '__main__':
    app.run(debug=True)
