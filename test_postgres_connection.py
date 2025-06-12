#!/usr/bin/env python3
import psycopg2
import sys
import traceback

def test_postgres_connection():
    """Test connection to PostgreSQL database with shiakati credentials."""
    try:
        print("Attempting to connect to PostgreSQL database...")
        # Try to connect to the database
        print("Connection parameters:")
        print("  - Database: shiakati")
        print("  - User: shiakati")
        print("  - Password: shiakati")
        print("  - Host: localhost")
        print("  - Port: 5432")
        
        conn = psycopg2.connect(
            dbname="shiakati",
            user="shiakati",
            password="shiakati",
            host="localhost",
            port="5432"
        )
        
        # If connection is successful, print success message
        print("Successfully connected to PostgreSQL database!")
        
        # Get database version
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # List all tables
        print("\nListing all tables in the database:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        print("\nConnection closed.")
        return True
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postgres_connection()
    sys.exit(0 if success else 1)
