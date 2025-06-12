#!/usr/bin/env python3
"""
Test the database connection using the application's actual database configuration.
This script ensures that the application can properly connect to the PostgreSQL database.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Load environment variables
load_dotenv()

try:
    # Import database session from the application
    print("Importing database session...")
    from app.db.session import engine, DATABASE_URL
    
    print(f"Database URL: {DATABASE_URL}")
    
    # Test connection by executing a simple query
    print("Testing database connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"PostgreSQL version: {version}")
        
        print("\nListing tables in database:")
        result = connection.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        ))
        tables = result.fetchall()
        for i, table in enumerate(tables):
            print(f"{i+1}. {table[0]}")
    
    print("\nDatabase connection successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
