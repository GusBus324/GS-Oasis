import sqlite3

def main():
    # Connect to or create the database
    conn = sqlite3.connect('database.db')
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
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema created successfully")

if __name__ == "__main__":
    main()
