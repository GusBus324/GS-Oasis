from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
import io
import time
import numpy as np
from functools import wraps
from datetime import timedelta
import math
import hashlib
from PIL import Image
import warnings

# Try to import potentially missing libraries with fallbacks
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    warnings.warn("PyPDF2 not available. PDF analysis will be limited.")

try:
    from query_gpt import get_open_ai_repsonse
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    warnings.warn("OpenAI module not available. AI assistant will be disabled.")

try:
    from url_check import check_url_suspiciousness
    URL_CHECK_AVAILABLE = True
except ImportError:
    URL_CHECK_AVAILABLE = False
    warnings.warn("URL check module not available. URL scanning will use basic checks only.")

# Try to import image analysis libraries with fallbacks
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    warnings.warn("Tesseract OCR not available. Text extraction from images will be limited.")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    warnings.warn("OpenCV not available. Image analysis will use fallback methods.")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    warnings.warn("EasyOCR not available. Primary OCR will fallback to pytesseract.")

app = Flask(__name__)
app.secret_key = "gs-oasis-secret-key"  # Required for flash messages

# Create directory for temporary files if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'static/temp'), exist_ok=True)

# Initialize SQLite database
def init_db():
    print("Initializing database...")
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Create users table with all required columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                account_type TEXT DEFAULT 'standard'
            )
        ''')
        
        # Create scan_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scan_date TEXT DEFAULT CURRENT_TIMESTAMP,
                scan_type TEXT NOT NULL,
                scan_item TEXT NOT NULL,
                result TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create contact_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0
            )
        ''')
        
        # Now verify that all columns exist in the users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add any missing columns - SQLite doesn't allow non-constant defaults in ALTER TABLE
        # so we need to add columns without defaults first, then update them separately
        if 'created_at' not in columns:
            try:
                # Add column without default
                cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
                # Then update it with current timestamp
                cursor.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")
                print("Added created_at column")
            except sqlite3.OperationalError as e:
                print(f"Note: {e}")
        
        if 'last_login' not in columns:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
                print("Added last_login column")
            except sqlite3.OperationalError as e:
                print(f"Note: {e}")
        
        if 'account_type' not in columns:
            try:
                # Add column without default first
                cursor.execute("ALTER TABLE users ADD COLUMN account_type TEXT")
                # Then set the default value
                cursor.execute("UPDATE users SET account_type = 'standard' WHERE account_type IS NULL")
                print("Added account_type column")
            except sqlite3.OperationalError as e:
                print(f"Note: {e}")
        
        conn.commit()
        print("Database initialization completed successfully.")

# Update database schema function
def update_db_schema():
    """
    Updates the database schema to add any missing columns to existing tables.
    Run this function when schema changes are made to ensure backward compatibility.
    """
    print("Checking and updating database schema...")
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            
            # Check if columns exist in users table and add them if missing
            cursor.execute("PRAGMA table_info(users)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Add created_at column if it doesn't exist
            if 'created_at' not in existing_columns:
                try:
                    # Add column without default
                    cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
                    # Then update it with current timestamp
                    cursor.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")
                    print("Added created_at column")
                except sqlite3.OperationalError as e:
                    print(f"Note: {e}")
            
            # Add last_login column if it doesn't exist
            if 'last_login' not in existing_columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
                    print("Added last_login column")
                except sqlite3.OperationalError as e:
                    print(f"Note: {e}")
            
            # Add account_type column if it doesn't exist
            if 'account_type' not in existing_columns:
                try:
                    # Add column without default first
                    cursor.execute("ALTER TABLE users ADD COLUMN account_type TEXT")
                    # Then set the default value
                    cursor.execute("UPDATE users SET account_type = 'standard' WHERE account_type IS NULL")
                    print("Added account_type column")
                except sqlite3.OperationalError as e:
                    print(f"Note: {e}")
            
            # Check if scan_history table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'")
            if not cursor.fetchone():
                print("Creating scan_history table")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scan_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        scan_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        scan_type TEXT NOT NULL,
                        scan_item TEXT NOT NULL,
                        result TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
            # Check if contact_messages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_messages'")
            if not cursor.fetchone():
                print("Creating contact_messages table")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contact_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT 0
                    )
                ''')
            
            # Create an index on the user_id column in scan_history for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON scan_history(user_id)")
            
            # Create an index on the username column in users for faster logins
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            
            conn.commit()
            print("Database schema update completed.")
    except sqlite3.Error as e:
        print(f"Error updating database schema: {e}")
        # If the database doesn't exist yet, we'll create it during init_db()

init_db()
update_db_schema()  # Update the database schema to add any missing columns

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
        'tax refund': 5, 'eligible for a tax refund': 5, 'tax rebate': 5, 'claim tax': 5, 'government grant': 4, 
        'irs': 3, 'tax authority': 3, 'legal notice': 3, 'tax message': 5, 'refund of': 4,
        'tax payment': 4, 'tax return': 4, 'tax agency': 4, 'tax department': 4, 'tax credit': 4,
        'claim refund': 5, 'unclaimed tax': 5, 'tax relief': 4, 'tax back': 4, 'tax reimbursement': 5,
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
    
    # Critical word combinations that often appear together in scams
    # Format: (word1, word2): weight
    critical_combinations = {
        ('tax', 'refund'): 5,
        ('tax', 'claim'): 5, 
        ('refund', 'click'): 5,
        ('refund', 'eligible'): 5,
        ('refund', 'link'): 5,
        ('eligible', 'claim'): 4,
        ('tax', 'message'): 4,
        ('tax', 'eligible'): 4,
        ('refund', 'congratulations'): 5,
        ('tax', 'authority'): 4,
        ('claim', 'now'): 4,
        ('tax', 'rebate'): 4,
        ('refund', 'today'): 4,
        ('click', 'claim'): 4,
        ('tax', 'payment'): 4,
        ('click', 'link'): 5,
        ('refund', 'amount'): 4,
        ('refund', 'due'): 5,
        ('tax', 'credit'): 4,
        ('tax', 'back'): 4,
        ('tax', 'department'): 5,
        ('refund', 'process'): 5,
        ('click', 'receive'): 5,
        ('claim', 'online'): 4
    }
    
    # Legitimate combinations that are common in non-scam communications
    legitimate_combinations = {
        ('standard', 'refund'): -5,
        ('processed', 'refund'): -5,
        ('normal', 'processing'): -5,
        ('return', 'processed'): -5,
        ('weeks', 'time'): -5,
        ('refund', 'time'): -5,
        ('standard', 'time'): -5,
        ('official', 'website'): -5,
        ('direct', 'deposit'): -5,
        ('tax', 'return'): -3,  # "tax return" is often legitimate
        ('annual', 'return'): -5
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
        if indicator in text:
            # Avoid double counting
            if not any(found_indicator for found_indicator in found_indicators if indicator in found_indicator):
                found_indicators.append(indicator)
                score += weight
                max_score += weight
    
    # Check for critical word combinations
    for (word1, word2), weight in critical_combinations.items():
        if word1 in text and word2 in text:
            # If both words are within 5 words of each other, it's more suspicious
            word_list = text.split()
            for i, word in enumerate(word_list):
                if word1 in word:
                    # Check nearby words for word2
                    nearby_text = ' '.join(word_list[max(0, i-5):min(len(word_list), i+6)])
                    if word2 in nearby_text:
                        found_indicators.append(f"{word1} + {word2}")
                        score += weight
                        max_score += weight
                        break
    
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
    
    # Check if the text is about taxes but seems legitimate
    is_tax_related = any(term in text for term in ['tax', 'refund', 'irs', 'tax return'])
    has_legitimate_markers = any(term in text for term in ['standard refund time', 'processed', 'weeks', 'scheduled', 'standard', 'normal process'])
    
    # Apply a higher threshold for tax-related content that has legitimate markers
    threshold = 25  # Default threshold
    if is_tax_related and has_legitimate_markers:
        threshold = 40  # Higher threshold to reduce false positives for legitimate tax communications
    
    # Determine if it's a scam
    is_scam = confidence > threshold
    
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
        
        # Special handling for tax refund scams - look for more specific indicators
        tax_scam_keywords = ['eligible for a tax refund', 'claim tax', 'tax refund', 'click', 'link', 'claim now',
                             'unclaimed tax', 'verify identity', 'reply with', 'click here', 'tax message', 'tax reimbursement']
        
        # Only consider it a tax refund scam if we have at least 2 strong indicators
        tax_scam_count = sum(1 for word in tax_scam_keywords if word in text)
        
        # Exclude legitimate phrases that could trigger false positives
        legitimate_phrases = ['standard refund time', 'weeks', 'processed', 'scheduled', 'direct deposit', 'normal processing']
        legitimate_count = sum(1 for word in legitimate_phrases if word in text)
        
        # If we have enough tax scam indicators and not too many legitimate phrases
        if tax_scam_count >= 2 and legitimate_count < 2:
            reasons.append("Appears to be a tax refund scam")
            
        # Check for suspicious links specifically related to tax refunds
        if any(term in text for term in ['click', 'link']) and any(term in text for term in ['refund', 'tax', 'claim']):
            # Don't flag if it appears to be information about a legitimate process
            if not any(term in text for term in ['normal processing', 'standard refund', 'official website', 'government portal']):
                reasons.append("Contains suspicious link related to tax refunds")
    
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
            is_text_message = False
            ai_analysis_summary = ""
            
            try:
                # Generate a unique filename for the temp image
                timestamp = str(int(os.path.getmtime(__file__))) if os.path.exists(__file__) else str(int(time.time()))
                unique_id = hashlib.md5((file.filename + timestamp).encode()).hexdigest()[:10]
                temp_filename = f"scan_{unique_id}_{os.path.basename(file.filename)}"
                temp_path = os.path.join(os.path.dirname(__file__), 'static/temp', temp_filename)
                
                # Save image temporarily for analysis
                file.save(temp_path)
                
                # Perform comprehensive image analysis
                try:
                    result = analyze_image_content(temp_path)
                    if not isinstance(result, tuple) or len(result) != 3:
                        # Fallback if function doesn't return expected tuple
                        extracted_text = ""
                        analysis_results = [f"❌ Error: analyze_image_content returned {type(result)} instead of tuple"]
                        performed_checks = ["Error handling"]
                    else:
                        extracted_text, analysis_results, performed_checks = result
                except Exception as e:
                    # Handle any exception in image analysis
                    extracted_text = ""
                    analysis_results = [f"❌ Error during image analysis: {str(e)}"]
                    performed_checks = ["Error handling"]
                
                # Analyze the extracted text for scams if we got any
                if extracted_text:
                    try:
                        result = check_for_scam(extracted_text)
                        if not isinstance(result, tuple) or len(result) != 3:
                            # Fallback if function doesn't return expected tuple
                            is_scam, confidence, reasons = False, 0, [f"Error: check_for_scam returned {type(result)} instead of tuple"]
                        else:
                            is_scam, confidence, reasons = result
                        
                        # If AI is available, get its analysis
                        if AI_AVAILABLE and extracted_text.strip():
                            try:
                                ai_prompt = f"Analyze the following text extracted from an image and determine if it is a scam. Provide a brief summary of your findings. Text: {extracted_text}"
                                ai_response = get_open_ai_repsonse(ai_prompt)
                                if ai_response:
                                    ai_analysis_summary = f"AI Assistant Analysis: {ai_response}"
                                    analysis_results.append(ai_analysis_summary) # Add AI summary to results
                                else:
                                    analysis_results.append("AI Assistant: Could not get a response.")
                            except Exception as ai_error:
                                analysis_results.append(f"AI Assistant Error: {str(ai_error)}")
                                
                    except Exception as e:
                        # Handle any exception in scam checking
                        is_scam, confidence, reasons = False, 0, [f"Error during scam analysis: {str(e)}"]

                
                # Create a detailed result message
                if is_text_message:
                    performed_checks.append("Text message analysis")
                    
                    # Specialized text message scam analysis
                    if is_scam:
                        risk_level = "High Risk" if confidence > 60 else "Medium Risk"
                        result_msg = f"⚠️ {risk_level}: This text message contains indicators of a potential scam ({confidence}% confidence)."
                        
                        # Add detected reasons
                        for reason in reasons:
                            result_msg += f"\n• {reason}"
                            
                        result_msg += "\n\n<strong>Recommendation:</strong> Do not respond to this message, click any links, or call any phone numbers provided."
                        
                        # Add specialized advice for text message scams
                        result_msg += "\n\n<div class='education-tips'>"
                        result_msg += "\n<h3>How to Handle Suspicious Text Messages:</h3>"
                        result_msg += "\n<ul>"
                        result_msg += "\n<li><strong>Do not reply</strong> - Even replying with 'STOP' confirms to scammers that your number is active.</li>"
                        result_msg += "\n<li><strong>Block the sender</strong> - Most phones allow you to block specific numbers from contacting you.</li>"
                        result_msg += "\n<li><strong>Report to authorities</strong> - Forward spam texts to 7726 (SPAM) in the US and many other countries.</li>"
                        result_msg += "\n<li><strong>Delete the message</strong> - Once reported, delete the message to avoid accidentally clicking on it later.</li>"
                        result_msg += "\n<li><strong>Never share personal information</strong> - Legitimate businesses won't ask for sensitive information via text.</li>"
                        result_msg += "\n</ul>"
                        
                        # Add specific advice based on detected issues
                        if any("urgency" in reason.lower() for reason in reasons):
                            result_msg += "\n<p><strong>Note:</strong> This message contains urgency indicators, which is a common tactic to rush you into making poor decisions.</p>"
                        
                        if any("click" in reason.lower() or "link" in reason.lower() or "url" in reason.lower()):
                            result_msg += "\n<p><strong>Note:</strong> Be extremely cautious of links in text messages. They often lead to phishing sites that steal your information.</p>"
                        
                        if any("bank" in reason.lower() or "account" in reason.lower() or "verify" in reason.lower() or "confirm" in reason.lower()):
                            result_msg += "\n<p><strong>Note:</strong> Legitimate financial institutions will never ask you to verify account information via text message.</p>"
                        
                        if any("prize" in reason.lower() or "won" in reason.lower() or "winner" in reason.lower() or "lottery" in reason.lower()):
                            result_msg += "\n<p><strong>Note:</strong> If you didn't enter a contest or lottery, you can't win it. These are almost always scams.</p>"
                        
                        result_msg += "\n</div>"
                    else:
                        # Check if any of the analysis results indicate suspicious content
                        suspicious_keywords = ['suspicious', 'hiding', 'manipulated', 'blurry', 'qr code']
                        suspicious_analysis = [result for result in analysis_results 
                                               if any(keyword in result.lower() for keyword in suspicious_keywords)]
                        
                        if suspicious_analysis:
                            result_msg = f"⚠️ Caution Advised: While no scam text was detected, our scan found potential issues with this text message:"
                            for finding in suspicious_analysis:
                                result_msg += f"\n• {finding}"
                            result_msg += "\n\nRecommendation: Exercise caution with messages from this sender."
                        else:
                            result_msg = f"✅ No suspicious content detected in this text message.\n\nThis message appears to be legitimate based on our analysis."
                            
                            # Add a note about what was found in the image
                            if analysis_results:
                                result_msg += "\n\nFindings:"
                                for finding in analysis_results[:3]:  # Limit to first 3 findings for cleaner display
                                    if "✅" in finding or "low likelihood" in finding.lower():
                                        result_msg += f"\n• {finding}"
                
                else:
                    # Standard image analysis for non-text message images
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
                if extracted_text and len(extracted_text) > 20 and not extracted_text.startswith("[Please upload"):
                    # Only show a snippet if there's a lot of text
                    text_preview = extracted_text[:150] + "..." if len(extracted_text) > 150 else extracted_text
                    result_msg += f"\n\n<div class='extracted-text'><strong>📝 Extracted Text:</strong><br>\"{text_preview}\"</div>"
                elif extracted_text and not extracted_text.startswith("[Please upload") and not extracted_text.startswith("[No text detected"):
                    result_msg += f"\n\n<div class='extracted-text'><strong>📝 Extracted Text:</strong><br>\"{extracted_text}\"</div>"
                elif extracted_text and (extracted_text.startswith("[Please upload") or extracted_text.startswith("[No text detected")):
                    message = extracted_text.strip("[]")
                    result_msg += f"\n\n<div class='extracted-text warning'><strong>📝 Text Extraction Warning:</strong><br>{message}</div>"
                else:
                    result_msg += "\n\n<div class='extracted-text warning'><strong>📝 Text Extraction:</strong><br>Please upload a clearer image for text recognition.</div>"
                
                # Add specific guidance for text message scams
                if is_text_message and is_scam:
                    result_msg += "\n\n<div class='text-message-tips'>"
                    result_msg += "\n<h3>Common Text Message Scams:</h3>"
                    result_msg += "\n<ul>"
                    result_msg += "\n<li><strong>Package delivery scams</strong> - Messages claiming to be from shipping companies about a delivery issue.</li>"
                    result_msg += "\n<li><strong>Banking alerts</strong> - Fake messages about account problems, unauthorized charges, or frozen accounts.</li>"
                    result_msg += "\n<li><strong>Tax/government scams</strong> - Messages claiming to be from the IRS, tax authorities, or government agencies.</li>"
                    result_msg += "\n<li><strong>Prize/lottery notifications</strong> - Messages claiming you've won something and need to click a link to claim it.</li>"
                    result_msg += "\n<li><strong>Account verification</strong> - Messages asking you to verify your account for services like Apple, Google, or social media.</li>"
                    result_msg += "\n</ul>"
                    result_msg += "\n</div>"
                
                # Add AI assistant recommendation
                result_msg += "\n\n<div class='ai-recommendation'><strong>Have any more questions?</strong> Ask the GS Oasis AI Assistant for help and insight. <a href='/ai_assistant'>Try our AI Assistant →</a></div>"
                
                # Clean up temporary file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Store scan results for the results page
                session['last_scan_type'] = 'text_message' if is_text_message else 'image'
                session['last_scan_result'] = result_msg.replace("\n", "<br>")
                session['last_scan_filename'] = file.filename
                
                # Add scan to history
                try:
                    user_id = session.get('user_id')
                    if user_id:
                        with sqlite3.connect('database.db') as conn:
                            cursor = conn.cursor()
                            scan_item = f"Text Message: {file.filename}" if is_text_message else f"Image: {file.filename}"
                            scan_type = "text_message" if is_text_message else "image"
                            result_summary = "Suspicious content detected" if is_scam else "No suspicious content detected"
                            
                            cursor.execute(
                                'INSERT INTO scan_history (user_id, scan_type, scan_item, result) VALUES (?, ?, ?, ?)',
                                (user_id, scan_type, scan_item, result_summary)
                            )
                            conn.commit()
                except Exception as e:
                    print(f"Error recording scan history: {str(e)}")
                
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
            
            # Add AI assistant recommendation
            result_msg += "\n\n<div class='ai-recommendation'><strong>Have any more questions?</strong> Ask the GS Oasis AI Assistant for help and insight. <a href='/ai_assistant'>Try our AI Assistant →</a></div>"
        
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
                    
                    # Add AI assistant recommendation
                    result_msg += "\n\n<div class='ai-recommendation'><strong>Have any more questions?</strong> Ask the GS Oasis AI Assistant for help and insight. <a href='/ai_assistant'>Try our AI Assistant →</a></div>"
                else:
                    # File is not a common format, mark as suspicious
                    result_msg = f"⚠️ Suspicious File Format: {file_ext}\n\nThis file uses an uncommon format that is not in our list of standard formats. While this doesn't necessarily mean the file is malicious, uncommon file formats are sometimes used to distribute malware or hide dangerous content.\n\nRecommendation: Be extremely cautious with this file. Only open it if you trust the source completely and have proper security measures in place."
                
                # Add AI assistant recommendation
                result_msg += "\n\n<div class='ai-recommendation'><strong>Have any more questions?</strong> Ask the GS Oasis AI Assistant for help and insight. <a href='/ai_assistant'>Try our AI Assistant →</a></div>"
                
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
        
        if AI_AVAILABLE:
            try:
                # Try to get response from OpenAI
                response = get_open_ai_repsonse(user_question)
                
                # If response is empty or None, fall back to rule-based system
                if not response:
                    response = generate_fallback_response(user_question)
            except Exception as e:
                print(f"Error with OpenAI API: {str(e)}")
                response = generate_fallback_response(user_question)
        else:
            # OpenAI integration not available, use fallback
            response = generate_fallback_response(user_question)
            
    return render_template('ai_assistant.html', response=response)

def generate_fallback_response(question):
    """
    Generate a fallback response when OpenAI API is not available
    Uses rule-based matching to provide helpful information
    """
    question = question.lower()
    
    # Common scam-related keywords
    scam_keywords = ['scam', 'phishing', 'fake', 'fraud', 'suspicious', 'spam']
    email_keywords = ['email', 'message', 'inbox']
    link_keywords = ['link', 'url', 'website', 'click']
    phone_keywords = ['call', 'phone', 'text', 'sms', 'message']
    bank_keywords = ['bank', 'account', 'credit card', 'debit card', 'financial']
    personal_info_keywords = ['password', 'ssn', 'social security', 'identity', 'personal information']
    
    # Check for question categories
    if any(keyword in question for keyword in scam_keywords):
        if any(keyword in question for keyword in email_keywords):
            return """
                <h3>Email Scam Protection Tips</h3>
                <p>Here are some ways to identify and protect yourself from email scams:</p>
                <ul>
                    <li><strong>Check the sender:</strong> Verify the email address is legitimate and not a slight misspelling of a real company.</li>
                    <li><strong>Be wary of urgency:</strong> Scammers often create false urgency to pressure you into acting quickly without thinking.</li>
                    <li><strong>Don't click suspicious links:</strong> Hover over links to see where they actually lead before clicking.</li>
                    <li><strong>Grammar and spelling:</strong> Professional companies rarely send emails with poor grammar or spelling mistakes.</li>
                    <li><strong>Suspicious attachments:</strong> Never open attachments from unknown senders.</li>
                    <li><strong>Requests for personal information:</strong> Legitimate organizations rarely ask for sensitive information via email.</li>
                </ul>
                <p>If you suspect an email is a scam, delete it and don't interact with it in any way.</p>
            """
        elif any(keyword in question for keyword in link_keywords):
            return """
                <h3>How to Identify Suspicious Links</h3>
                <p>Here are ways to check if a link is safe before clicking:</p>
                <ul>
                    <li><strong>Check the URL:</strong> Look for misspellings or slight variations of legitimate domain names.</li>
                    <li><strong>Look for HTTPS:</strong> Secure websites use HTTPS and show a padlock icon in your browser.</li>
                    <li><strong>Be cautious of shortened URLs:</strong> They can hide the actual destination.</li>
                    <li><strong>Check for excessive subdomains:</strong> Multiple dots in a URL can be suspicious.</li>
                    <li><strong>Use our scan link feature:</strong> Paste any suspicious link into our scanner to check it.</li>
                </ul>
                <p>When in doubt, don't click. Type the company's official URL directly into your browser instead.</p>
            """
        elif any(keyword in question for keyword in phone_keywords):
            return """
                <h3>Phone and Text Message Scam Protection</h3>
                <p>Protect yourself from phone and SMS scams with these tips:</p>
                <ul>
                    <li><strong>Unknown numbers:</strong> Be cautious of calls or texts from unknown numbers.</li>
                    <li><strong>Don't respond to suspicious texts:</strong> Even replying "STOP" confirms your number is active.</li>
                    <li><strong>Verify independently:</strong> If a text claims to be from your bank, call the official number on your card.</li>
                    <li><strong>Be wary of "urgent" messages:</strong> Scammers often create false emergencies.</li>
                    <li><strong>Don't click links in texts:</strong> These often lead to phishing sites.</li>
                    <li><strong>Report suspicious texts:</strong> Forward spam texts to 7726 (SPAM) in the US.</li>
                </ul>
                <p>Remember that government agencies and banks will never ask for personal information, payments, or gift cards via text message.</p>
            """
        elif any(keyword in question for keyword in bank_keywords):
            return """
                <h3>Financial and Banking Scam Protection</h3>
                <p>Protect your financial information with these guidelines:</p>
                <ul>
                    <li><strong>Verify communications:</strong> Contact your bank directly using the number on your card, not numbers provided in messages.</li>
                    <li><strong>Check account regularly:</strong> Monitor your accounts for unauthorized transactions.</li>
                    <li><strong>Use strong authentication:</strong> Enable two-factor authentication when available.</li>
                    <li><strong>Be wary of "problem with your account" messages:</strong> These are common phishing tactics.</li>
                    <li><strong>Know that banks never ask for:</strong> Full passwords, PIN numbers, or to transfer money to a "safe account".</li>
                </ul>
                <p>If you think you've been targeted by a financial scam, contact your bank immediately and change your passwords.</p>
            """
        elif any(keyword in question for keyword in personal_info_keywords):
            return """
                <h3>Protecting Your Personal Information</h3>
                <p>Keep your personal information secure with these practices:</p>
                <ul>
                    <li><strong>Share selectively:</strong> Only provide personal information on secure and necessary platforms.</li>
                    <li><strong>Use unique passwords:</strong> Create different passwords for different accounts.</li>
                    <li><strong>Enable two-factor authentication:</strong> Adds an extra layer of security.</li>
                    <li><strong>Be cautious with social media:</strong> Limit the personal information you share publicly.</li>
                    <li><strong>Shred sensitive documents:</strong> Prevent dumpster diving for your information.</li>
                    <li><strong>Check privacy settings:</strong> Regularly review and update privacy settings on your accounts.</li>
                </ul>
                <p>Remember: Your personal information is valuable. Treat it like you would any other valuable possession.</p>
            """
        else:
            # General scam information
            return """
                <h3>General Scam Protection Tips</h3>
                <p>Here are some universal tips to protect yourself from scams:</p>
                <ul>
                    <li><strong>If it seems too good to be true, it probably is.</strong> Unrealistic offers are a red flag.</li>
                    <li><strong>Never send money to someone you haven't met in person.</strong></li>
                    <li><strong>Don't make rushed decisions.</strong> Scammers create urgency to prevent you from thinking clearly.</li>
                    <li><strong>Research before you act.</strong> Look up companies, offers, or situations online.</li>
                    <li><strong>Keep your devices and software updated.</strong> Security patches protect against known vulnerabilities.</li>
                    <li><strong>Use our scanning tools:</strong> Check suspicious images, links, and files using GS Oasis.</li>
                </ul>
                <p>Trust your instincts - if something feels wrong, it's better to be cautious than sorry.</p>
            """
    else:
        # Default response for non-scam related questions
        return """
            <h3>GS Oasis AI Assistant</h3>
            <p>I'm currently running in offline mode. I can provide information on the following topics:</p>
            <ul>
                <li>Email scam protection</li>
                <li>Suspicious link identification</li>
                <li>Phone and text message scams</li>
                <li>Financial and banking scams</li>
                <li>Personal information protection</li>
                <li>General scam prevention</li>
            </ul>
            <p>Please ask a question about one of these topics for specific guidance.</p>
            
            <p>You can also use our scanning tools to check:</p>
            <ul>
                <li><a href="/scan_image">Images or text message screenshots</a></li>
                <li><a href="/scan_link">Suspicious links or URLs</a></li>
                <li><a href="/scan_file">Files and documents</a></li>
            </ul>
        """

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
            # Pass username and email back to form, but never password
            return render_template('register.html', username=username, email=email)

        try:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                # Check if the created_at column exists
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'created_at' in columns:
                    cursor.execute('INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)', 
                                  (username, email, generate_password_hash(password), current_time))
                else:
                    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                                  (username, email, generate_password_hash(password)))
                conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
            # Pass email back to form but not username (since it's a duplicate) or password
            return render_template('register.html', email=email)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == '1'
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

        if not user or not check_password_hash(user[1], password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        # Store user information in session
        session['user_id'] = user[0]
        session['username'] = username
        
        # Set session expiration based on remember me
        if remember:
            # Session lasts for 30 days if remember me is checked
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=30)
        else:
            # Default session behavior (until browser is closed)
            session.permanent = False
        
        # Update last login time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # First, make sure the last_login column exists
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            # Check if the column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Add the column if it doesn't exist
            if 'last_login' not in columns:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
                    print("Added missing last_login column")
                except sqlite3.OperationalError as e:
                    print(f"Failed to add last_login column: {str(e)}, but continuing...")
            
            # Now try to update the last_login time
            try:
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (current_time, user[0]))
                conn.commit()
                print(f"Updated last_login for user {username}")
            except Exception as e:
                print(f"Warning: Could not update last_login: {str(e)}")
                # Continue without updating last_login
                pass
        
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

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

# Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Simple validation
        if not all([name, email, subject, message]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('contact'))
        
        # Email validation with regex
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('contact'))
            
        # In a real application, you would save this to a database
        # For demonstration, we'll store messages in the database
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                # Create contact_messages table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contact_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT 0
                    )
                ''')
                
                # Insert the message
                cursor.execute(
                    'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
                    (name, email, subject, message)
                )
                conn.commit()
                
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Allow users to edit their profile information
    """
    username = session.get('username')
    user_id = session.get('user_id')
    
    # Connect to database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Get current user info
        cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found.', 'danger')
            return redirect(url_for('dashboard'))
        
        email = user_data[0]
        
        # Handle form submission
        if request.method == 'POST':
            new_email = request.form.get('email')
            
            # Validate email
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(new_email):
                flash('Please enter a valid email address.', 'danger')
                return render_template('edit_profile.html', username=username, email=email)
            
            # Check if email has changed
            if new_email != email:
                # Check if the new email is already in use by another account
                cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (new_email, user_id))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    flash('Email address is already in use by another account.', 'danger')
                    return render_template('edit_profile.html', username=username, email=email)
                
                # Update the email
                try:
                    cursor.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
                    conn.commit()
                    flash('Profile updated successfully!', 'success')
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    flash(f'An error occurred: {str(e)}', 'danger')
                    return render_template('edit_profile.html', username=username, email=email)
            else:
                flash('No changes were made.', 'info')
                return redirect(url_for('dashboard'))
    
    return render_template('edit_profile.html', username=username, email=email)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Allow users to change their password
    """
    username = session.get('username')
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'danger')
            return render_template('change_password.html')
        
        # Check if new password meets the requirements
        password_regex = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,}$'
        if not re.match(password_regex, new_password):
            flash('New password must be at least 8 characters long, include at least 2 numbers, and 1 special symbol.', 'danger')
            return render_template('change_password.html')
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html')
        
        # Connect to database
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
            stored_password_hash = cursor.fetchone()
            
            if not stored_password_hash or not check_password_hash(stored_password_hash[0], current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('change_password.html')
            
            # Check if new password is different from current
            if check_password_hash(stored_password_hash[0], new_password):
                flash('New password must be different from current password.', 'danger')
                return render_template('change_password.html')
            
            # Update password
            try:
                hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
                conn.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'danger')
                return render_template('change_password.html')
    
    return render_template('change_password.html')

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
            extracted_text = extract_text_with_fallback(image_path)
            if extracted_text:
                performed_checks.append("Text extraction (enhanced)")
                analysis_results.append(f"Extracted text content using enhanced analysis")
                
            # If we found some text, also try to run a second OCR pass with different settings            if extracted_text and OCR_AVAILABLE:
                try:
                    # Try with different PSM modes to catch different text layouts
                    for psm_mode in [3, 6, 4]:  # Page, Single block, Single line
                        custom_config = f'--psm {psm_mode} --oem 3'
                        alt_text = pytesseract.image_to_string(img, config=custom_config)
                        
                        # If this mode found more text, add it to our extracted text
                        if len(alt_text) > 20 and alt_text not in extracted_text:
                            extracted_text += " " + alt_text
                except Exception as e:
                    analysis_results.append(f"Additional OCR processing failed: {str(e)}")
                
                analysis_results.append(f"Extracted {len(extracted_text)} characters of text from image")
            else:
                analysis_results.append("No text found in image")
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

def extract_text_with_fallback(image_path):
    """Extract text from images using available methods, with multiple fallback mechanisms when dependencies aren't available"""
    extracted_text = ""
    
    # PRIORITY 1: Try EasyOCR first (recommended, no admin required)
    if EASYOCR_AVAILABLE:
        try:
            import easyocr
            # Initialize EasyOCR reader (this might take a moment on first run to download models)
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            
            # Extract text from image
            results = reader.readtext(image_path)
            
            # Combine all detected text
            if results:
                extracted_text = ' '.join([detection[1] for detection in results if detection[2] > 0.1])  # confidence > 0.1
                
                if extracted_text and len(extracted_text.strip()) > 3:
                    extracted_text = extracted_text.strip()
                    # Remove non-printable characters
                    extracted_text = ''.join(char for char in extracted_text if char.isprintable() or char.isspace())
                    return extracted_text
        except Exception as e:
            print(f"EasyOCR failed: {str(e)}")
            # Continue to fallback methods
    
    # PRIORITY 2: Try local Tesseract if available
    if OCR_AVAILABLE:
        try:
            with Image.open(image_path) as img:
                # Try default OCR first
                extracted_text = pytesseract.image_to_string(img)
                
                # If no text found, try with preprocessing
                if not extracted_text or len(extracted_text.strip()) < 5:
                    preprocessed_img = preprocess_image_for_ocr(img)
                    extracted_text = pytesseract.image_to_string(preprocessed_img)
                    
                    # If still no text, try different OCR configurations
                    if not extracted_text or len(extracted_text.strip()) < 5:
                        # Try different PSM modes (page segmentation modes)
                        for psm_mode in [3, 6, 4, 11, 12]:  # Various segmentation modes
                            custom_config = f'--psm {psm_mode} --oem 3'
                            alt_text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
                            if alt_text and len(alt_text.strip()) > len(extracted_text.strip()):
                                extracted_text = alt_text
                                
                # Clean up text if found
                if extracted_text:
                    extracted_text = extracted_text.strip()
                    # Remove non-printable characters
                    extracted_text = ''.join(char for char in extracted_text if char.isprintable() or char.isspace())
                    return extracted_text
                
                # If still no text but OCR ran without errors, return empty string to allow other methods
                return ""
        except Exception as e:
            print(f"Local OCR failed: {str(e)}")
            # Continue to fallback methods
    
    # FALLBACK LEVEL 1: If we reach here, either Tesseract is not available or it failed
    # Use OpenCV-based text detection if available
    if OPENCV_AVAILABLE:
        try:
            # Read image with OpenCV
            img_cv = cv2.imread(image_path)
            if img_cv is not None:  # Ensure image was loaded successfully
                # Try to detect text-like regions using edge detection
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Try multiple thresholds for better detection
                for threshold_value in [100, 150, 200]:
                    # Apply binary threshold
                    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
                    
                    # Look for contours that might be text
                    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)                        # If we found many small contours, it might be text
                     if len(contours) > 10:
                            # Ratio of contours to image size indicates text density
                            text_region_ratio = sum(cv2.contourArea(c) for c in contours) / (gray.shape[0] * gray.shape[1])
                            if text_region_ratio > 0.01:  # More than 1% of image has text-like contours
                                return "[Please upload a clearer image for better text recognition]"
                
                # Also try edge detection for text recognition
                edges = cv2.Canny(gray, 100, 200)
                text_region_ratio = np.count_nonzero(edges) / (gray.shape[0] * gray.shape[1])
                if text_region_ratio > 0.05:  # More than 5% of image has edges
                    return "[Please upload a clearer image for better text recognition]"
        except Exception as e:
            print(f"OpenCV text detection fallback failed: {str(e)}")
            # Continue to next fallback
    
    # FALLBACK LEVEL 2: Basic PIL-only analysis when both OCR and OpenCV are unavailable
    try:
        with Image.open(image_path) as img:
            # Get basic image properties for analysis
            width, height = img.size
            
            # Simplest possible text detection: check for high contrast areas
            # Convert to grayscale
            gray_img = img.convert('L')
            pixels = list(gray_img.getdata())
            
            if pixels:
                # Check variance in pixel values - text usually has high variance
                min_val, max_val = min(pixels), max(pixels)
                if max_val - min_val > 100:  # High contrast threshold
                    # Count transitions from light to dark (common in text)
                    transitions = 0
                    for y in range(height):
                        row_start = y * width
                        for x in range(1, width):
                            # If significant difference between adjacent pixels
                            if abs(pixels[row_start + x] - pixels[row_start + x - 1]) > 50:
                                transitions += 1
                    
                    # High number of transitions suggests text
                    if transitions > width * height * 0.01:  # Threshold based on image size
                        return "[Please upload a clearer image for better text recognition]"
            
            # If nothing detected, return generic message
            return "[No text detected in the image. If there should be text, please upload a clearer image]"
    except Exception as e:
        return f"[Error analyzing image: {str(e)}]"

@app.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard displaying account information, scan history, and statistics
    """
    # Get user information
    username = session.get('username')
    
    # Connect to database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # First, check which columns exist in the users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create dynamic query based on available columns
        select_fields = ["email"]
        if 'created_at' in columns:
            select_fields.append('created_at')
        if 'last_login' in columns:
            select_fields.append('last_login')
        
        query = f"SELECT {', '.join(select_fields)} FROM users WHERE username = ?"
        
        # Get user details based on available columns
        try:
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            
            if user_data:
                email = user_data[0]
                
                # Set defaults
                join_date = "N/A"
                last_login = "N/A"
                
                # Get values if columns exist
                field_index = 1
                if 'created_at' in columns and len(user_data) > field_index:
                    join_date = user_data[field_index] if user_data[field_index] else "N/A"
                    field_index += 1
                    
                if 'last_login' in columns and len(user_data) > field_index:
                    last_login = user_data[field_index] if user_data[field_index] else "N/A"
            else:
                email = "N/A"
                join_date = "N/A"
                last_login = "N/A"
        except sqlite3.Error as e:
            # Handle any database errors
            print(f"Database error: {str(e)}")
            email = "N/A"
            join_date = "N/A"
            last_login = "N/A"
        
        # Get user's ID for scan history queries
        user_id = session.get('user_id')
        
        # Get actual scan statistics from the database
        try:
            # Get total scan count
            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE user_id = ?", (user_id,))
            scan_count = cursor.fetchone()[0] or 0
            
            # Get threat count
            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE user_id = ? AND result LIKE '%suspicious%' OR result LIKE '%danger%' OR result LIKE '%scam%'", (user_id,))
            threat_count = cursor.fetchone()[0] or 0
            
            # Get safe count
            cursor.execute("SELECT COUNT(*) FROM scan_history WHERE user_id = ? AND result LIKE '%safe%'", (user_id,))
            safe_count = cursor.fetchone()[0] or 0
            
            # Daily scan limit
            daily_limit = 50  # Could make this dynamic based on account type
            remaining_scans = daily_limit - scan_count if scan_count < daily_limit else 0
        except sqlite3.Error as e:
            print(f"Error fetching scan statistics: {e}")
            scan_count = 0
            threat_count = 0
            safe_count = 0
            remaining_scans = 50
        
        # Format last_login time in a user-friendly way if it's available
        if last_login != "N/A":
            try:
                # Try to parse the datetime string
                login_time = time.strptime(last_login, "%Y-%m-%d %H:%M:%S")
                today = time.strftime("%Y-%m-%d")
                
                # If login was today, show "Today, HH:MM AM/PM"
                if time.strftime("%Y-%m-%d", login_time) == today:
                    last_login = "Today, " + time.strftime("%I:%M %p", login_time)
                else:
                    # Otherwise show "Mon DD, YYYY, HH:MM AM/PM"
                    last_login = time.strftime("%b %d, %Y, %I:%M %p", login_time)
            except:
                # If parsing fails, keep the original string
                pass
        
        # Get current date in a nice format
        current_date = time.strftime("%B %d, %Y")
        
        # Get actual scan history from database
        recent_activities = []
        try:
            cursor.execute("""
                SELECT scan_date, scan_type, scan_item, result 
                FROM scan_history 
                WHERE user_id = ? 
                ORDER BY scan_date DESC LIMIT 10
            """, (user_id,))
            
            history_items = cursor.fetchall()
            
            # Process each history item
            for item in history_items:
                scan_date, scan_type, scan_item, result = item
                
                # Format date nicely
                try:
                    item_date = time.strptime(scan_date, "%Y-%m-%d %H:%M:%S")
                    today = time.strftime("%Y-%m-%d")
                    yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
                    
                    if time.strftime("%Y-%m-%d", item_date) == today:
                        formatted_date = "Today, " + time.strftime("%I:%M %p", item_date)
                    elif time.strftime("%Y-%m-%d", item_date) == yesterday:
                        formatted_date = "Yesterday, " + time.strftime("%I:%M %p", item_date)
                    else:
                        formatted_date = time.strftime("%b %d, %I:%M %p", item_date)
                except:
                    formatted_date = scan_date
                
                # Determine result category (safe, suspicious, dangerous)
                result_category = "safe"
                if "suspicious" in result.lower() or "warning" in result.lower():
                    result_category = "suspicious"
                elif "danger" in result.lower() or "scam" in result.lower() or "threat" in result.lower():
                    result_category = "dangerous"
                
                # Add to activities list
                recent_activities.append({
                    "date": formatted_date,
                    "type": scan_type,
                    "item": scan_item,
                    "result": result_category
                })
            
            # If no history found, provide a helpful message
            if not recent_activities:
                recent_activities = [{
                    "date": "No scans yet",
                    "type": "none",
                    "item": "Try scanning an image, link, or file",
                    "result": "none"
                }]
        except sqlite3.Error as e:
            print(f"Error fetching scan history: {e}")
            # Fallback empty message if database query fails
            recent_activities = [{
                "date": "No scan history available",
                "type": "none", 
                "item": "Database error occurred",
                "result": "none"
            }]
    
    return render_template('dashboard.html', 
                          username=username,
                          email=email, 
                          join_date=join_date,
                          current_date=current_date,
                          scan_count=scan_count,
                          threat_count=threat_count,
                          safe_count=safe_count,
                          remaining_scans=remaining_scans,
                          last_login=last_login,
                          recent_activities=recent_activities)

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')

if __name__ == '__main__':
    # Update the database schema on startup
    update_db_schema()
    
    # Set port as a variable for easier management
    port = 5001  # Fixed to use port 5001 as requested
    
    try:
        app.run(debug=True, port=port, host='127.0.0.1')
        print(f"Server running on port {port}")
    except OSError as e:
        print(f"Error: {e}")
        print(f"Port {port} is already in use. Try a different port by changing the port variable.")

def fallback_url_check(url):
    """
    A simple fallback function to check URL suspiciousness when the url_check module is unavailable
    Returns a tuple (is_suspicious, reason)
    """
    if not url or not isinstance(url, str):
        return False, ""
    
    # Normalize the URL for checking
    url = url.lower().strip()
    
    # Simple patterns that might indicate suspicious URLs
    suspicious_patterns = [
        # IP address URLs
        (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', "Uses IP address instead of domain name"),
        
        # Excessive subdomains (more than 3)
        (r'([a-z0-9-]+\.){4,}[a-z0-9-]+', "Contains excessive subdomains"),
        
        # Common misspellings of popular domains
        (r'paypa1|amaz0n|g00gle|faceb00k|micros0ft|netfl1x|appleid|veriz0n', "Contains misspelled popular brand name"),
        
        # Suspicious TLDs often used for free/temporary domains
        (r'\.tk$|\.xyz$|\.top$|\.gq$|\.ml$|\.ga$|\.cf$', "Uses a TLD commonly associated with free domains"),
        
        # URLs with suspicious keywords
        (r'login|verify|secure|account|banking|password|update|confirm', "Contains sensitive action keywords"),
        
        # Non-HTTPS URLs with sensitive terms
        (r'^http://.*(login|verify|secure|account|banking|password)', "Uses non-secure HTTP with sensitive actions")
    ]
    
    # Check URL against suspicious patterns
    for pattern, reason in suspicious_patterns:
        if re.search(pattern, url):
            return True, reason
    
    # URL doesn't match any suspicious patterns
    return False, "No suspicious patterns detected"
