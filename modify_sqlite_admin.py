#!/usr/bin/env python3
"""
Script to directly set username and password in SQLite database
"""
import os
import sqlite3
import hashlib
import bcrypt
from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'shiakati.db')

def set_admin_password():
    """Create or update the admin user with password '123'"""
    # Check if DB exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at: {DB_PATH}")
        return False
        
    username = "admin"
    password = "123"
    hashed_password = pwd_context.hash(password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin_users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users';")
        if not cursor.fetchone():
            # Create the table if it doesn't exist
            print("Creating admin_users table...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            )
            ''')
            
        # Check if admin user exists
        cursor.execute("SELECT id FROM admin_users WHERE username = ?", (username,))
        if cursor.fetchone():
            # Update existing admin
            cursor.execute(
                "UPDATE admin_users SET hashed_password = ? WHERE username = ?",
                (hashed_password, username)
            )
            print(f"Updated password for user '{username}' to '{password}'")
        else:
            # Create new admin user
            cursor.execute(
                "INSERT INTO admin_users (username, hashed_password) VALUES (?, ?)",
                (username, hashed_password)
            )
            print(f"Created new user '{username}' with password '{password}'")
            
        conn.commit()
        
        # Verify the user exists
        cursor.execute("SELECT username, hashed_password FROM admin_users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            print(f"Verified user '{result[0]}' exists in database")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if set_admin_password():
        print("Admin password successfully set!")
    else:
        print("Failed to set admin password.")
