"""
Reset admin password

This script updates the password for the admin user in the database.
"""
import os
import sys
from sqlalchemy import create_engine, text
import bcrypt
from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add the parent directory to the Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Get database URL from environment (or use default)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shiakati:shiakati@localhost:5432/shiakati")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define the new password
new_password = "password123"

# Hash the password
hashed_password = pwd_context.hash(new_password)

def reset_admin_password():
    """Reset the admin password in the database"""
    with engine.connect() as connection:
        # Check if admin user exists
        result = connection.execute(text("SELECT id FROM admin_users WHERE username = 'admin'"))
        admin_exists = result.fetchone() is not None
        
        if admin_exists:
            # Update existing admin user
            connection.execute(
                text("UPDATE admin_users SET hashed_password = :password WHERE username = 'admin'"),
                {"password": hashed_password}
            )
            print(f"Admin user password updated successfully to '{new_password}'")
        else:
            # Create admin user if it doesn't exist
            connection.execute(
                text("INSERT INTO admin_users (username, hashed_password) VALUES ('admin', :password)"),
                {"password": hashed_password}
            )
            print(f"Admin user created with password '{new_password}'")
        
        connection.commit()

if __name__ == "__main__":
    reset_admin_password()
