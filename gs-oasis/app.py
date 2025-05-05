from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

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

@app.route('/')
def index():
    return render_template('index.html')  # Updated home page to include login and sign-up options

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/scan-image', methods=['GET', 'POST'])
def scan_image():
    if request.method == 'POST':
        # Image scanning logic would go here
        flash('Image scanned successfully!', 'success')
        return redirect(url_for('scan_results'))
    return render_template('scan_image.html')

@app.route('/scan-link', methods=['GET', 'POST'])
def scan_link():
    if request.method == 'POST':
        # Link scanning logic would go here
        flash('Link scanned successfully!', 'success')
        return redirect(url_for('scan_results'))
    return render_template('scan_link.html')

@app.route('/scan-file', methods=['GET', 'POST'])
def scan_file():
    if request.method == 'POST':
        # File scanning logic would go here
        flash('File scanned successfully!', 'success')
        return redirect(url_for('scan_results'))
    return render_template('scan_file.html')

@app.route('/scan-results')
def scan_results():
    # This would display results from the last scan
    return render_template('scan_results.html')

@app.route('/ai-assistant', methods=['GET', 'POST'])
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

        flash('Login successful!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/users')
def users_list():
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)