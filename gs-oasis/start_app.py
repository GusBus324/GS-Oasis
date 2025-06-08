#!/usr/bin/env python3
"""
Utility script to start the GS Oasis application with automatic port selection
"""

import socket
import os
import sys
from importlib import import_module

def find_free_port(start_port=5000, max_attempts=20):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def start_app():
    """Start the Flask application with automatic port selection"""
    # Find an available port
    port = find_free_port(5000)
    
    if not port:
        print("ERROR: Could not find an available port between 5000 and 5020.")
        return False
    
    try:
        # Import the app from app.py
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app, update_db_schema
        
        # Update the database schema
        update_db_schema()
        
        # Start the app on the available port
        print(f"Starting GS Oasis on port {port}...")
        print(f"Access the application at: http://localhost:{port}")
        app.run(debug=True, port=port)
        return True
    except Exception as e:
        print(f"ERROR starting application: {e}")
        return False

if __name__ == "__main__":
    print("╔════════════════════════════════════════════╗")
    print("║             GS OASIS LAUNCHER              ║")
    print("╚════════════════════════════════════════════╝")
    
    # Start the application
    if not start_app():
        print("Failed to start the application.")
        sys.exit(1)
