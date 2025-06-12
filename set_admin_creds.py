"""
Set admin user with password 123

This script creates or updates the admin user in the database with username 'admin' and password '123'.
"""
import os
import sys
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add the parent directory to the Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Get database URL from environment (or use default)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shiakati:shiakati@localhost:5432/shiakati")
# For SQLite (if used)
sqlite_path = "shiakati.db"
if os.path.exists(sqlite_path):
    DATABASE_URL = f"sqlite:///{sqlite_path}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define the username and password
username = "admin"
new_password = "123"

# Hash the password
hashed_password = pwd_context.hash(new_password)

def set_admin_password():
    """Set admin user with password 123 in the database"""
    with engine.connect() as connection:
        # Check if admin user exists
        result = connection.execute(text(f"SELECT id FROM admin_users WHERE username = '{username}'"))
        admin_exists = result.fetchone() is not None
        
        if admin_exists:
            # Update existing admin user
            connection.execute(
                text(f"UPDATE admin_users SET hashed_password = :password WHERE username = '{username}'"),
                {"password": hashed_password}
            )
            print(f"Admin user password updated successfully to '{new_password}'")
        else:
            # Create admin user if it doesn't exist
            connection.execute(
                text("INSERT INTO admin_users (username, hashed_password) VALUES (:username, :password)"),
                {"username": username, "password": hashed_password}
            )
            print(f"Admin user created with username '{username}' and password '{new_password}'")
        
        connection.commit()

if __name__ == "__main__":
    set_admin_password()
