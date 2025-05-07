from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = "gs-oasis-secret-key"  # Required for flash messages

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
            # Process the image - this is where you'd run the actual scanning logic
            # For now, we'll just simulate a successful scan
            flash('Image scanned successfully!', 'success')
            # You could save the scan results to the session or db for the results page
            session['last_scan_type'] = 'image'
            session['last_scan_result'] = 'No threats detected in your image.'
            return redirect(url_for('scan_results'))
            
    return render_template('scan_image.html')

@app.route('/scan_link', methods=['GET', 'POST'])
@login_required
def scan_link():
    if request.method == 'POST':
        link = request.form.get('link')
        
        if not link:
            flash('No link provided', 'danger')
            return redirect(request.url)
            
        # Process the link - this is where you'd run the actual link scanning logic
        # For now, we'll just simulate a successful scan
        flash('Link scanned successfully!', 'success')
        # Store scan results for the results page
        session['last_scan_type'] = 'link'
        session['last_scan_result'] = f'The link {link} appears to be safe.'
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
            # Process the file - this is where you'd run the actual file scanning logic
            # For now, we'll just simulate a successful scan
            flash('File scanned successfully!', 'success')
            # Store scan results for the results page
            session['last_scan_type'] = 'file'
            session['last_scan_result'] = f'No threats detected in {file.filename}.'
            return redirect(url_for('scan_results'))
            
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

if __name__ == '__main__':
    app.run(debug=True)