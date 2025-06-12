#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection.
"""

import psycopg2
import sys

def test_postgres_connection():
    print("Attempting to connect to PostgreSQL database...")
    
    try:
        # Connection parameters
        conn_params = {
            "dbname": "shiakati",
            "user": "shiakati",
            "password": "shiakati",
            "host": "localhost",
            "port": "5432"
        }
        
        # Attempt connection
        conn = psycopg2.connect(**conn_params)
        
        # Get cursor
        cursor = conn.cursor()
        
        # Test a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("Connection successful!")
        print(f"PostgreSQL database version: {db_version[0]}")
        
        # Try to get tables in the database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = test_postgres_connection()
    sys.exit(0 if result else 1)
