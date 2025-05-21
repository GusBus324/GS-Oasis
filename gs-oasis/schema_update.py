import sqlite3
import time

def update_db_schema():
    """
    Updates the database schema to add any missing columns to existing tables.
    Run this function when schema changes are made to ensure backward compatibility.
    """
    print("Checking and updating database schema...")
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Check if columns exist in users table and add them if missing
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add created_at column if it doesn't exist
        if 'created_at' not in existing_columns:
            print("Adding created_at column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
        
        # Add last_login column if it doesn't exist
        if 'last_login' not in existing_columns:
            print("Adding last_login column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
        
        # Add account_type column if it doesn't exist
        if 'account_type' not in existing_columns:
            print("Adding account_type column to users table")
            cursor.execute("ALTER TABLE users ADD COLUMN account_type TEXT DEFAULT 'standard'")
        
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
        
        conn.commit()
        print("Database schema update completed.")

if __name__ == "__main__":
    # Run schema update independently
    update_db_schema()
