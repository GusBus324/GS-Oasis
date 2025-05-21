#!/usr/bin/env python3

import sqlite3
import os

def create_clean_database():
    db_path = 'database.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Connect to create a new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table with all required columns
    print("Creating users table...")
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
    print("Creating scan_history table...")
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
    print("Creating contact_messages table...")
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
    
    # Verify the database was created and has a valid size
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"Database created successfully! Size: {size} bytes")
        return True
    else:
        print("Failed to create database!")
        return False

if __name__ == "__main__":
    create_clean_database()
