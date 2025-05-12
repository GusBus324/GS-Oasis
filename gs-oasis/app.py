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
from query_gpt import get_open_ai_repsonse


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
    
    # Clean and normalize text for better matching
    text = text.lower()
    # Remove extra spaces and normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove common non-alphanumeric characters that might break pattern matching
    text = re.sub(r'[^\w\s@\.\-\:]', ' ', text)
    
    # Common scam indicators with weights
    scam_indicators = {
        # Urgency indicators
        'urgent': 3, 'immediately': 3, 'act now': 4, 'limited time': 3, 'urgent action': 4,
        'warning': 2, 'alert': 2, 'attention': 2, 'important notice': 3, 'time sensitive': 3,
        'expire': 3, 'expiration': 3, 'expires': 3, 'deadline': 3, 'final notice': 4,
        
        # Financial bait
        'free money': 5, 'cash prize': 5, 'lottery winner': 5, 'you won': 4, 'lucky winner': 5,
        'million dollars': 5, 'get rich': 5, 'double your money': 5, 'easy money': 4,
        'cash bonus': 4, 'free gift': 3, 'prize': 3, 'claim your': 3, 'reward': 3,
        'inheritance': 5, 'payout': 4, 'congrats': 2, 'congratulations': 2, 'winner': 3,
        
        # Request for personal information
        'verify your account': 4, 'update your information': 3, 'confirm your account': 4,
        'confirm your identity': 4, 'security check': 3, 'account details': 3, 'personal details': 3,
        'unusual activity': 3, 'suspicious activity': 3, 'login information': 4, 'password': 3,
        'credit card': 3, 'banking details': 4, 'social security': 4, 'ssn': 4, 'payment details': 4,
        
        # Common phishing phrases
        'dear customer': 2, 'dear user': 2, 'valued customer': 2, 'account holder': 2,
        'account suspended': 4, 'account locked': 4, 'unauthorized access': 3, 'security alert': 3,
        'unusual login': 3, 'policy violation': 3, 'terms of service': 2, 'service agreement': 2,
        'account verification': 4, 'secure your account': 3, 'log in to': 2, 'click here': 2,
        
        # Technical deception
        'tech support': 3, 'customer service': 2, 'help desk': 2, 'contact support': 2,
        'virus detected': 4, 'malware detected': 4, 'your computer is infected': 5, 'your device is infected': 5,
        'security breach': 4, 'hacked': 3, 'compromised': 3, 'infected': 3, 'trojan': 4,
        'ransomware': 4, 'spyware': 4, 'antivirus': 3, 'scan your': 3, 'clean your': 3,
        
        # Transaction scams
        'payment pending': 3, 'transaction failed': 3, 'refund': 3, 'reimbursement': 3,
        'billing information': 3, 'invoice attached': 3, 'receipt': 2, 'shipping': 2,
        'purchase confirmation': 2, 'order status': 2, 'tracking number': 2, 'package delivery': 2,
        
        # Government impersonation
        'tax refund': 4, 'government grant': 4, 'irs': 3, 'tax authority': 3, 'legal notice': 3,
        'social security': 4, 'legal action': 4, 'lawsuit': 3, 'court': 3, 'warrant': 4,
        'fines': 3, 'penalties': 3, 'law enforcement': 3, 'police': 3, 'arrest': 4,
        
        # Common misspellings in legitimate company names (sign of phishing)
        'micr0soft': 5, 'app1e': 5, 'amaz0n': 5, 'g00gle': 5, 'paypa1': 5,
        'faceb00k': 5, 'netfl1x': 5, 'bank0f': 5, 'a\/ple': 5, 'tvvitter': 5,
        
        # Cryptocurrency scams
        'bitcoin': 2, 'cryptocurrency': 2, 'crypto': 2, 'invest now': 4, 'investment opportunity': 3,
        'guaranteed return': 5, 'blockchain opportunity': 3, 'mining': 2, 'wallet': 2,
        'exchange': 2, 'ethereum': 2, 'token': 2, 'ico': 3, 'defi': 2,
        
        # Romance scams
        'looking for love': 3, 'found you attractive': 3, 'dating profile': 2, 'single': 1,
        'romantic relationship': 3, 'overseas': 2, 'foreign country': 2, 'meet in person': 2,
        'love at first sight': 3, 'relationship': 2, 'lonely': 2, 'widow': 2, 'widower': 2,
        
        # Job scams
        'work from home': 2, 'make money online': 3, 'be your own boss': 3, 'remote job': 2,
        'earn extra income': 2, 'job opportunity': 1, 'high paying job': 3, 'passive income': 3,
        'employment': 1, 'hiring': 1, 'flexible hours': 2, 'no experience needed': 3, 'part time': 1,
        
        # Gift card scams
        'gift card': 3, 'itunes card': 4, 'steam card': 4, 'google play card': 4, 'prepaid card': 3,
        'reload card': 3, 'activation code': 3, 'pin code': 3, 'card number': 3,
        
        # AI and modern scams (2024-2025)
        'ai investment': 4, 'ai trading': 4, 'trading bot': 4, 'metaverse': 3, 'digital land': 3,
        'nft opportunity': 3, 'virtual reality': 2, 'quantum computing': 3, 'quantum ai': 4,
        'covid relief': 3, 'pandemic assistance': 3, 'stimulus payment': 3, 'debt forgiveness': 3
    }
    
    # Part-word matching for common indicators that might be split across words
    part_word_indicators = {
        'verif': 3, 'secur': 2, 'activ': 2, 'accoun': 3, 'confirm': 3,
        'suspend': 4, 'restrict': 3, 'unlock': 3, 'alert': 2, 'updat': 3,
        'password': 3, 'login': 3, 'access': 2, 'bank': 3, 'credit': 3,
        'debit': 3, 'pay': 2, 'money': 2, 'cash': 2, 'prize': 3,
        'win': 3, 'congrat': 3, 'invest': 3, 'bitcoin': 3, 'crypto': 3,
        'urgent': 3, 'immediate': 3, 'gift card': 4
    }
    
    # Look for domain mismatches (e.g. apple.com-secure.xyz)
    domain_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z0-9-.]+'
    domains = re.findall(domain_pattern, text)
    
    # Common suspicious domains and TLDs
    suspicious_domains = [
        'secure-login', 'account-verify', 'signin', 'login-secure', 'support-team',
        'verification', 'secure-verify', 'update-account', 'customer-portal',
        'security-check', 'password-reset', 'billing-update', 'payment-update'
    ]
    
    suspicious_tlds = [
        '.xyz', '.top', '.club', '.online', '.site', '.tk', '.ga', '.cf', '.gq', '.ml'
    ]
    
    # Check for indicators in the text
    found_indicators = []
    score = 0
    max_score = 0
    
    # Check for exact matches
    for indicator, weight in scam_indicators.items():
        max_score += weight
        if indicator in text:
            found_indicators.append(indicator)
            score += weight
    
    # Check for part-word matches
    for part_word, weight in part_word_indicators.items():
        if part_word in text:
            # Avoid double counting
            if not any(indicator for indicator in found_indicators if part_word in indicator):
                found_indicators.append(part_word)
                score += weight
    
    # Check for suspicious domains and TLDs
    found_suspicious_domains = []
    
    for domain in domains:
        # Check for suspicious domain names
        for sus_domain in suspicious_domains:
            if sus_domain in domain.lower():
                found_suspicious_domains.append(domain)
                score += 4
                break
                
        # Check for suspicious TLDs
        for sus_tld in suspicious_tlds:
            if domain.lower().endswith(sus_tld):
                found_suspicious_domains.append(domain)
                score += 3
                break
    
    if found_suspicious_domains:
        found_indicators.append(f"Suspicious domain(s): {', '.join(found_suspicious_domains)}")
    
    # Additional pattern checks
    
    # Check for excessive urgency patterns
    urgency_words = ['urgent', 'immediately', 'right now', 'asap', 'today', 'before it', 'expire']
    urgency_count = sum(1 for word in urgency_words if word in text)
    if urgency_count >= 2:
        found_indicators.append(f"Multiple urgency indicators ({urgency_count})")
        score += urgency_count * 2
    
    # Check for patterns of capitalizations (shouting) - common in scams
    if re.search(r'[A-Z]{5,}', text):
        found_indicators.append("Excessive capitalization")
        score += 3
    
    # Check for excessive punctuation (common in scams)
    if re.search(r'[!]{2,}', text) or re.search(r'[?]{2,}', text):
        found_indicators.append("Excessive punctuation")
        score += 2
    
    # Normalize score to a 0-100 scale
    if max_score > 0:
        confidence = min(100, int((score / max_score) * 200))  # Amplified to catch more scams
    else:
        confidence = 0
    
    # Lower threshold for identification as a scam
    is_scam = confidence > 25  # Lowered from 30 to catch more scams
    
    # Generate reasons if it's a potential scam
    reasons = []
    if is_scam:
        if len(found_indicators) > 0:
            reasons.append(f"Found suspicious content: {', '.join(found_indicators[:5])}")
        if any(word in text for word in ['urgent', 'immediately', 'right now', 'asap']):
            reasons.append("Creates false urgency")
        if any(term in text for term in ['free money', 'cash prize', 'lottery', 'won', 'winner']):
            reasons.append("Promises unrealistic financial rewards")
        if any(term in text for term in ['verify', 'update your', 'confirm your', 'security', 'password']):
            reasons.append("Requests personal information")
        if any(term in text for term in ['banking', 'account', 'credit card', 'login', 'sign in']):
            reasons.append("Attempts to impersonate a financial institution")
        if any(term in text for term in ['bitcoin', 'crypto', 'investment', 'trading', 'guarantee']):
            reasons.append("Offers suspicious investment opportunities")
    
    # Add debug info to help with troubleshooting when needed
    # Uncomment to debug: print(f"Text: {text[:100]}..., Score: {score}, Confidence: {confidence}, Scam: {is_scam}")
    
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
        
        # Extract domain for analysis
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(link)
            domain = parsed_url.netloc or parsed_url.path
            if not domain:
                domain = link
        except:
            domain = link
        
        # Create a detailed result message
        if is_scam:
            risk_level = "High Risk" if confidence > 60 else "Medium Risk"
            result_msg = f"⚠️ {risk_level}: This link shows indicators of a potential scam ({confidence}% confidence)."
            
            # Add detected reasons
            for reason in reasons:
                result_msg += f"\n• {reason}"
            
            result_msg += "\n\n<strong>Recommendation:</strong> Do not visit this website or provide any information."
            
            # Add educational content about avoiding scams
            result_msg += "\n\n<div class='education-tips'>"
            result_msg += "\n<h3>How to Protect Yourself from Scam Links:</h3>"
            result_msg += "\n<ul>"
            result_msg += "\n<li><strong>Be wary of unsolicited links</strong> - Don't click on links from unknown sources, even if they appear to be from a trusted organization.</li>"
            result_msg += "\n<li><strong>Check URLs carefully</strong> - Scammers often use domain names that look similar to legitimate sites but have slight misspellings.</li>"
            result_msg += "\n<li><strong>Look for secure connections</strong> - Legitimate sites typically use HTTPS (look for the padlock icon in your browser).</li>"
            result_msg += "\n<li><strong>Be suspicious of urgent or threatening messages</strong> - Scammers often create a false sense of urgency to pressure you into clicking.</li>"
            result_msg += "\n<li><strong>Don't provide personal information</strong> - Legitimate organizations typically don't ask for sensitive information through email links.</li>"
            result_msg += "\n</ul>"
            
            # Add specific advice based on detected issues
            if any("urgency" in reason.lower() for reason in reasons):
                result_msg += "\n<p><strong>Note:</strong> This link contains urgency indicators, which is a common tactic to rush you into making poor decisions.</p>"
            
            if any("personal information" in reason.lower() for reason in reasons):
                result_msg += "\n<p><strong>Note:</strong> This link appears to be designed to collect personal information, which could lead to identity theft.</p>"
            
            if any("financial" in reason.lower() or "money" in reason.lower() or "prize" in reason.lower() or "winner" in reason.lower()):
                result_msg += "\n<p><strong>Note:</strong> This link contains promises of financial rewards, which is a common tactic in scams. Remember: if it sounds too good to be true, it probably is.</p>"
            
            result_msg += "\n</div>"
            
        else:
            result_msg = f"✅ No known threats detected in this link.\nNote: While no threats were detected, always remain cautious when visiting unfamiliar websites."
            
            # Add more detailed information about the link
            result_msg += f"\n\n<strong>Domain:</strong> {domain}"
            
            # Add educational content for safe browsing
            result_msg += "\n\n<div class='education-tips'>"
            result_msg += "\n<h3>Safe Browsing Tips:</h3>"
            result_msg += "\n<ul>"
            result_msg += "\n<li><strong>Keep your browser updated</strong> - Updates often include security patches for newly discovered vulnerabilities.</li>"
            result_msg += "\n<li><strong>Use a secure browser</strong> - Browsers like Chrome, Firefox, and Safari regularly update to protect against threats.</li>"
            result_msg += "\n<li><strong>Consider using a VPN</strong> - A Virtual Private Network can provide an additional layer of privacy and security.</li>"
            result_msg += "\n<li><strong>Install an ad blocker</strong> - This can protect against malicious advertisements that might redirect you.</li>"
            result_msg += "\n<li><strong>Practice good password hygiene</strong> - Use unique, strong passwords for different websites.</li>"
            result_msg += "\n</ul>"
            result_msg += "\n<p>Even though this link appears safe, remember that new threats emerge daily. Always remain vigilant!</p>"
            result_msg += "\n</div>"
        
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
            # Get file extension to determine if it's a common format
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # List of common file extensions
            common_extensions = {
                '.pdf': 'PDF (Portable Document Format)',
                '.tiff': 'TIFF (Tagged Image File Format)',
                '.tif': 'TIFF (Tagged Image File Format)',
                '.gif': 'GIF (Graphics Interchange Format)',
                '.svg': 'SVG (Scalable Vector Graphics)',
                '.xlsx': 'XLSX (Excel Spreadsheet)',
                '.xls': 'XLS (Excel Spreadsheet)',
                '.bmp': 'BMP (Bitmap Image File)',
                '.html': 'HTML (Hypertext Markup Language)',
                '.htm': 'HTML (Hypertext Markup Language)',
                '.jpg': 'JPEG (Joint Photographic Experts Group)',
                '.jpeg': 'JPEG (Joint Photographic Experts Group)',
                '.png': 'PNG (Portable Network Graphics)'
            }
            
            # Check if the file is a common format
            is_common_format = file_ext in common_extensions
            format_name = common_extensions.get(file_ext, "Unknown Format")
            
            try:
                # Default result variables
                result_msg = ""
                
                if is_common_format:
                    # File is a common format, considered safe
                    result_msg = f"✅ File Format: {format_name}\n\nThis is a common file format that is generally used for legitimate purposes. However, still exercise caution when handling files from unknown sources."
                else:
                    # File is not a common format, mark as suspicious
                    result_msg = f"⚠️ Suspicious File Format: {file_ext}\n\nThis file uses an uncommon format that is not in our list of standard formats. While this doesn't necessarily mean the file is malicious, uncommon file formats are sometimes used to distribute malware or hide dangerous content.\n\nRecommendation: Be extremely cautious with this file. Only open it if you trust the source completely and have proper security measures in place."
                
                # Store scan results for the results page
                session['last_scan_type'] = 'file'
                session['last_scan_result'] = result_msg.replace("\n", "<br>")
                session['last_scan_filename'] = file.filename
                
                flash('File format scanned successfully!', 'success')
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
        response = get_open_ai_repsonse(user_question)
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
    
    # 2. Basic image validation that works without specialized libraries
    try:
        with Image.open(image_path) as img:
            # Get basic image info
            width, height = img.size
            format_type = img.format
            mode = img.mode
            file_size = os.path.getsize(image_path)
            
            performed_checks.append("Basic image validation")
            analysis_results.append(f"Image dimensions: {width}x{height} pixels")
            analysis_results.append(f"Format: {format_type}, Mode: {mode}")
            
            # Check for unusually small images (possible hiding technique)
            if width < 100 or height < 100:
                analysis_results.append("⚠️ Image is unusually small, may be hiding content")
            
            # Check file size vs dimensions ratio (compression anomalies)
            pixels = width * height
            if pixels > 0:
                bytes_per_pixel = file_size / pixels
                if bytes_per_pixel > 10:  # Arbitrary threshold
                    analysis_results.append("⚠️ Image has unusually high file size for its dimensions")
                    
            # Check for common image format mismatches
            if format_type == 'JPEG' and mode == 'RGBA':
                analysis_results.append("⚠️ Unusual mode for JPEG format, possible manipulation")
            
            # QR Code detection - common in scams
            if OPENCV_AVAILABLE:
                try:
                    # Convert PIL image to OpenCV format
                    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # Initialize QR Code detector
                    qr_detector = cv2.QRCodeDetector()
                    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(img_cv)
                    
                    if retval:
                        performed_checks.append("QR code detection")
                        analysis_results.append(f"⚠️ QR code detected in image. QR codes in unsolicited images may link to malicious websites.")
                        # Add the decoded information if available
                        if decoded_info and any(decoded_info):
                            qr_urls = [url for url in decoded_info if url.startswith(('http://', 'https://'))]
                            if qr_urls:
                                for url in qr_urls:
                                    analysis_results.append(f"⚠️ QR code contains URL: {url[:50]}{'...' if len(url) > 50 else ''}")
                                    # Check if the URL itself is suspicious
                                    is_suspicious, reason = check_url_suspiciousness(url)
                                    if is_suspicious:
                                        analysis_results.append(f"⚠️ QR code URL appears suspicious: {reason}")
                except Exception as e:
                    pass  # Silently fail QR detection if something goes wrong
            
            # 3. Extract text using OCR if available
            if OCR_AVAILABLE:
                try:
                    # First try normal OCR
                    extracted_text = pytesseract.image_to_string(img)
                    performed_checks.append("Text extraction (OCR)")
                    
                    # If no text was found or very little text, try preprocessing the image
                    if len(extracted_text) < 10:
                        performed_checks.append("Enhanced OCR with preprocessing")
                        # Apply preprocessing to enhance text detection
                        preprocessed_img = preprocess_image_for_ocr(img)
                        enhanced_text = pytesseract.image_to_string(preprocessed_img)
                        
                        # If preprocessing found more text, use that instead
                        if len(enhanced_text) > len(extracted_text):
                            extracted_text = enhanced_text
                            analysis_results.append("Used enhanced OCR to extract text")
                    
                    # If we found some text, also try to run a second OCR pass with different settings
                    if extracted_text:
                        # Try with different PSM modes to catch different text layouts
                        for psm_mode in [3, 6, 4]:  # Page, Single block, Single line
                            custom_config = f'--psm {psm_mode} --oem 3'
                            alt_text = pytesseract.image_to_string(img, config=custom_config)
                            
                            # If this mode found more text, add it to our extracted text
                            if len(alt_text) > 20 and alt_text not in extracted_text:
                                extracted_text += " " + alt_text
                                
                        analysis_results.append(f"Extracted {len(extracted_text)} characters of text from image")
                except Exception as e:
                    analysis_results.append(f"OCR failed: {str(e)}")
            else:
                analysis_results.append("OCR (text recognition) is not available - install tesseract for text detection")
                
                # AI-based image pattern analysis (when OCR is unavailable)
                # This is a simplified pattern recognition system as a fallback
                performed_checks.append("AI pattern recognition")
                
                # Convert to bytes for analysis
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=format_type)
                img_bytes = img_bytes.getvalue()
                
                # Calculate entropy of image data as a measure of potential hidden content
                entropy = 0
                for i in range(256):
                    p = img_bytes.count(i.to_bytes(1, byteorder='big')) / len(img_bytes)
                    if p > 0:
                        entropy -= p * math.log2(p)
                
                if entropy > 7.5:  # High entropy threshold
                    analysis_results.append("⚠️ Image has high information entropy, possible steganography")
                
                # Analyze color distribution for anomalies that might indicate hidden content
                try:
                    # Sample pixels for analysis
                    pixels_data = list(img.getdata())
                    pixel_sample = pixels_data[::100]  # Take every 100th pixel for performance
                    
                    # Check for unusual color patterns 
                    unique_colors = len(set(pixel_sample))
                    color_ratio = unique_colors / len(pixel_sample) if pixel_sample else 0
                    
                    if mode == 'RGBA' and color_ratio < 0.01:
                        analysis_results.append("⚠️ Suspicious color pattern detected, possible hidden content")
                    
                    # Use perceptual hash as a simplified way to detect common scam templates
                    # This simulates comparing against a database of known scam patterns
                    if perform_simplified_image_similarity_check(img):
                        analysis_results.append("⚠️ Image matches patterns commonly found in scam content")
                        
                except Exception as e:
                    pass
                
            # 4. Check metadata (EXIF data) for any suspicious elements
            performed_checks.append("Metadata analysis")
            try:
                exif_data = img._getexif()
                if exif_data:
                    # Note that we found metadata
                    analysis_results.append("Image contains metadata/EXIF data")
                    
                    # Check for suspicious metadata
                    if exif_data and isinstance(exif_data, dict):
                        for tag_id, value in exif_data.items():
                            if tag_id == 40091 or tag_id == 40092:  # XMP metadata
                                analysis_results.append("⚠️ Image contains extended metadata (XMP)")
                            if tag_id == 37510:  # UserComment
                                analysis_results.append("⚠️ Image contains user comments in metadata")
                                
                                # Try to extract text from metadata
                                if isinstance(value, bytes) or isinstance(value, str):
                                    try:
                                        comment_text = value.decode('utf-8') if isinstance(value, bytes) else value
                                        if len(comment_text) > 10:  # Only consider substantial text
                                            extracted_text += " " + comment_text
                                            analysis_results.append(f"⚠️ Extracted text from metadata: {comment_text[:50]}...")
                                    except:
                                        pass
            except Exception as e:
                # Many images don't have exif data, so this isn't critical
                pass
                
            # Check for transparency (PNG only)
            if mode == 'RGBA':
                try:
                    transparent_pixels = 0
                    for pixel in img.getdata():
                        if len(pixel) == 4 and pixel[3] < 255:  # Alpha channel < 255 means some transparency
                            transparent_pixels += 1
                    
                    if transparent_pixels > 0:
                        analysis_results.append(f"⚠️ Image has {transparent_pixels} transparent pixels which might hide content")
                except Exception as e:
                    pass
                    
    except Exception as e:
        analysis_results.append(f"Basic image analysis failed: {str(e)}")
        return extracted_text, analysis_results, performed_checks
    
    # 5. Perform visual analysis using OpenCV if available
    if OPENCV_AVAILABLE:
        try:
            # Read the image with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                analysis_results.append("Could not load image for analysis with OpenCV")
            else:
                # Get image dimensions and calculate image hash for analysis
                height, width, channels = img.shape
                performed_checks.append("Advanced image integrity check")
                performed_checks.append("Visual content analysis")
                
                # Basic image quality check
                blurriness = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
                if blurriness < 100:  # Arbitrary threshold, adjust as needed
                    analysis_results.append("⚠️ Image appears blurry, which may indicate manipulation")
                
                # Check for hidden text that OCR might have missed using edge detection
                edges = cv2.Canny(img, 100, 200)
                text_region_ratio = np.count_nonzero(edges) / (height * width)
                if text_region_ratio > 0.1 and not extracted_text:  # If there seem to be text-like edges but OCR found nothing
                    analysis_results.append("⚠️ Image may contain text that couldn't be extracted")
                    
                    # Try to extract text from the edge-detected image if OCR is available
                    if OCR_AVAILABLE and text_region_ratio > 0.15:
                        try:
                            # Convert edges to PIL Image for OCR
                            edge_img = Image.fromarray(edges)
                            edge_text = pytesseract.image_to_string(edge_img)
                            
                            if edge_text and len(edge_text) > 10:
                                extracted_text += " " + edge_text
                                analysis_results.append("Extracted text from edge detection")
                        except:
                            pass
                
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
                        analysis_results.append(f"⚠️ Found QR code in image that points to: {decoded_info}")
                        # Analyze the QR URL for potential scams
                        for url in decoded_info:
                            if url:
                                is_scam, confidence, reasons = check_for_scam(url)
                                if is_scam:
                                    analysis_results.append(f"⚠️ QR code contains suspicious URL: {url}")
                except Exception as e:
                    # QR detection is optional, don't fail if this doesn't work
                    pass
                
                # Try advanced text detection with OpenCV EAST text detector if no text was found yet
                if not extracted_text and OCR_AVAILABLE:
                    try:
                        # Use simple automatic thresholding for better text extraction
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                        
                        # Save to temp file and use OCR
                        temp_thresh_path = image_path + "_thresh.jpg"
                        cv2.imwrite(temp_thresh_path, thresh)
                        
                        with Image.open(temp_thresh_path) as thresh_img:
                            thresh_text = pytesseract.image_to_string(thresh_img)
                            if thresh_text and len(thresh_text) > 10:
                                extracted_text += " " + thresh_text
                                analysis_results.append("Extracted text using advanced thresholding")
                        
                        # Clean up temp file
                        if os.path.exists(temp_thresh_path):
                            os.remove(temp_thresh_path)
                    except:
                        pass
                
        except Exception as e:
            analysis_results.append(f"OpenCV analysis failed: {str(e)}")
    else:
        analysis_results.append("OpenCV not available - install opencv-python for advanced image analysis")
        
        # Extra AI-based analysis when OpenCV is unavailable
        performed_checks.append("Simplified visual pattern analysis")
        analysis_results.append("Using alternative AI-based pattern analysis")
        
        # Analyze file signature for tampering
        with open(image_path, 'rb') as f:
            header = f.read(32)  # Read file header
            
        # Check file signature against known patterns
        if format_type == 'PNG' and not header.startswith(b'\x89PNG\r\n\x1a\n'):
            analysis_results.append("⚠️ PNG header is invalid, possible file tampering")
        elif format_type == 'JPEG' and not (header.startswith(b'\xff\xd8\xff') or header.startswith(b'\xff\xd8')):
            analysis_results.append("⚠️ JPEG header is invalid, possible file tampering")
    
    # Clean up extracted text
    if extracted_text:
        # Remove extra whitespace and normalize
        extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()
        # Remove non-printable characters
        extracted_text = ''.join(char for char in extracted_text if char.isprintable() or char.isspace())
    
    # 6. Final step: AI-based scam likelihood assessment
    performed_checks.append("AI-based scam likelihood assessment")
    
    # Check for scam content in extracted text
    if extracted_text and len(extracted_text) > 10:
        is_scam, confidence, reasons = check_for_scam(extracted_text)
        if is_scam:
            risk_level = "High Risk" if confidence > 60 else "Medium Risk"
            analysis_results.append(f"⚠️ {risk_level}: Detected scam text in image ({confidence}% confidence)")
            for reason in reasons:
                analysis_results.append(f"⚠️ {reason}")
    
    # Suspicious patterns typically found in scam images
    scam_indicators = [
        result for result in analysis_results if "⚠️" in result
    ]
    
    # Evaluate with simple heuristic approach
    if len(scam_indicators) >= 3:
        analysis_results.append("⚠️ HIGH LIKELIHOOD OF SCAM: Multiple suspicious patterns detected")
    elif len(scam_indicators) >= 1:
        analysis_results.append("⚠️ MEDIUM LIKELIHOOD OF SCAM: Some suspicious patterns detected") 
    else:
        analysis_results.append("✅ LOW LIKELIHOOD OF SCAM: No significant suspicious patterns detected")
    
    return extracted_text, analysis_results, performed_checks

def perform_simplified_image_similarity_check(img):
    """
    Performs a simplified perceptual hash comparison to detect common scam patterns.
    This is a fallback when advanced libraries aren't available.
    """
    import math
    
    # Create a simplified perceptual hash
    # We'll resize the image to 8x8, convert to grayscale, and compare pixel values
    try:
        # Resize to small dimensions for simplified perceptual hash
        small_img = img.resize((8, 8), Image.LANCZOS).convert('L')
        pixels = list(small_img.getdata())
        
        # Calculate average pixel value
        avg = sum(pixels) / len(pixels) if pixels else 0
        
        # Create binary hash (1 if pixel > avg, 0 otherwise)
        binary_hash = ''.join('1' if p > avg else '0' for p in pixels)
        
        # Common hash patterns found in scam images (simplified examples)
        # In a real system, you would have a database of hashes from known scam images
        common_scam_patterns = [
            # Pattern for fake bank notifications
            '1111000011110000111100001111000011110000111100001111000011110000',
            # Pattern for fake login pages
            '0000111100001111000011110000111100001111000011110000111100001111',
            # Pattern for QR code scams (simplified)
            '1010101010101010101010101010101010101010101010101010101010101010',
            # Pattern for high-contrast text on solid background (common in scams)
            '1111111100000000111111110000000011111111000000001111111100000000'
        ]
        
        # Check similarity with known patterns
        for pattern in common_scam_patterns:
            # Calculate Hamming distance (number of different bits)
            hamming_distance = sum(b1 != b2 for b1, b2 in zip(binary_hash, pattern))
            
            # If hash is close to a known pattern (allowing for some variation)
            if hamming_distance < 16:  # Threshold for 8x8 image (64 bits)
                return True
        
        # Additional checks for common scam visual characteristics
        
        # Check for high contrast (common in scam images with bold text)
        min_val, max_val = min(pixels), max(pixels)
        if max_val - min_val > 200:  # High contrast threshold
            # Check if image is mostly text on solid background
            dark_pixels = sum(1 for p in pixels if p < 50)
            light_pixels = sum(1 for p in pixels if p > 200)
            
            # If most pixels are either very dark or very light (text on plain background)
            if (dark_pixels + light_pixels) / len(pixels) > 0.8:
                return True
        
        # Check for artificial borders (common in phishing/scam attempts)
        border_pixels = [
            pixels[0:8],  # Top row
            pixels[56:64],  # Bottom row
            pixels[0:57:8],  # Left column
            pixels[7:64:8]  # Right column
        ]
        
        # Flatten the border pixels
        border_pixels = [p for row in border_pixels for p in row]
        
        # Calculate standard deviation of border pixels
        if border_pixels:
            mean = sum(border_pixels) / len(border_pixels)
            std_dev = math.sqrt(sum((p - mean) ** 2 for p in border_pixels) / len(border_pixels))
            
            # Uniform borders often appear in scam images
            if std_dev < 10:  # Low standard deviation indicates uniform border
                return True
    
    except Exception as e:
        # If anything fails, err on the side of caution and don't report a match
        pass
    
    return False

def preprocess_image_for_ocr(img):
    """
    Apply various preprocessing techniques to enhance text detection for OCR.
    This function helps extract text from images with difficult-to-read text.
    """
    import io
    import numpy as np
    from PIL import Image, ImageFilter, ImageEnhance
    
    try:
        # Make a copy of the image to avoid modifying the original
        preprocessed = img.copy()
        
        # 1. Resize for better OCR performance (if image is very small)
        width, height = preprocessed.size
        if width < 1000 or height < 1000:
            scale_factor = 2
            preprocessed = preprocessed.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
        
        # 2. Convert to grayscale for better text recognition
        if preprocessed.mode != 'L':
            preprocessed = preprocessed.convert('L')
        
        # 3. Increase contrast to make text more visible
        enhancer = ImageEnhance.Contrast(preprocessed)
        preprocessed = enhancer.enhance(2.0)  # Increase contrast
        
        # 4. Apply threshold to make text more distinct (black and white)
        threshold_value = 150  # Adjust as needed (0-255)
        preprocessed = preprocessed.point(lambda x: 0 if x < threshold_value else 255, '1')
        
        # 5. Apply slight sharpening for better edge definition
        preprocessed = preprocessed.filter(ImageFilter.SHARPEN)
        
        # 6. Apply noise reduction
        preprocessed = preprocessed.filter(ImageFilter.MedianFilter(size=3))
        
        # 7. Apply dilate/erode morphological operations (similar to OpenCV's dilate/erode)
        # Simulate dilation by expanding dark regions
        dilated = preprocessed.filter(ImageFilter.MaxFilter(size=3))
        
        return dilated
    except Exception as e:
        # If preprocessing fails, return the original image
        return img

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed port from 5000 to 5001
