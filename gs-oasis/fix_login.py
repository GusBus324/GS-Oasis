#!/usr/bin/env python3
import sqlite3

def fix_last_login_column():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # First, try to create the users table if it doesn't exist
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
        
        # Now check if the column exists
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # If last_login doesn't exist, add it
        if 'last_login' not in existing_columns:
            print("Adding last_login column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
            print("Column added successfully")
        else:
            print("last_login column already exists")
        
        conn.commit()
        conn.close()
        
        print("Database update completed successfully")
        return True
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        return False

if __name__ == "__main__":
    fix_last_login_column()
