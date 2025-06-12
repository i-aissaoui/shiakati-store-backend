#!/usr/bin/env python3
"""
Script to test the direct connection to the PostgreSQL database and verify tables.
This script will directly access the database and run basic queries to check if everything is working.
"""

import psycopg2
import os
import sys
import json
from tabulate import tabulate
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB', 'shiakati'),
    'user': os.getenv('POSTGRES_USER', 'shiakati'),
    'password': os.getenv('POSTGRES_PASSWORD', 'shiakati'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# API connection parameters
API_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "123"

def get_auth_token():
    """Get an authentication token from the API."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": USERNAME, "password": PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        print(f"Error getting token: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Exception getting token: {str(e)}")
        return None

def test_api_connection():
    """Test the API connection and access to data."""
    print("\n=== Testing API Connection ===")
    print(f"Connecting to API at {API_URL}")
    
    # First check if the API is up without authentication
    try:
        response = requests.get(f"{API_URL}/docs", timeout=2)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"⚠️ API documentation returned status code: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not access API documentation: {str(e)}")
    
    # Get authentication token
    print("Attempting to authenticate...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token from the API")
        return False
    
    print("✅ Successfully authenticated with the API")
    
    # Try to access categories
    print("Testing categories endpoint...")
    try:
        response = requests.get(
            f"{API_URL}/categories/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Successfully retrieved {len(categories)} categories from the API")
            print("Categories:")
            for cat in categories:
                print(f"  - ID: {cat['id']}, Name: {cat['name']}, Products: {cat['products_count']}")
        else:
            print(f"❌ Failed to retrieve categories: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            return False
    except Exception as e:
        print(f"❌ Exception requesting categories: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    # Try to access products
    print("\nTesting products endpoint...")
    try:
        response = requests.get(
            f"{API_URL}/products/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Successfully retrieved {len(products)} products from the API")
            if products:
                print("Sample products:")
                for p in products[:3]:  # Show first 3 products
                    print(f"  - ID: {p['id']}, Name: {p['name']}")
        else:
            print(f"⚠️ Could not retrieve products: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
    except Exception as e:
        print(f"⚠️ Exception requesting products: {str(e)}")
    
    return True

def test_db_connection():
    """Test the direct database connection."""
    print("\n=== Testing Direct Database Connection ===")
    try:
        # Connect to the PostgreSQL database
        print(f"Connecting to PostgreSQL database: {DB_PARAMS['dbname']} as {DB_PARAMS['user']} at {DB_PARAMS['host']}:{DB_PARAMS['port']}...")
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("✅ Successfully connected to the database")
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {version}")
        
        # List all tables
        print("Fetching table list...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"\nFound {len(tables)} tables in the database: {', '.join(table_names)}")
        
        # Check row counts in tables
        print("\nRow counts in tables:")
        table_counts = []
        for table_name in table_names:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
                count = cursor.fetchone()[0]
                table_counts.append((table_name, count))
                print(f"  - {table_name}: {count} rows")
            except Exception as e:
                error_msg = str(e)
                table_counts.append((table_name, f"Error: {error_msg}"))
                print(f"  - {table_name}: ERROR - {error_msg}")
        
        # Sample some data from each table
        print("\nSample data from tables:")
        for table_name in table_names:
            try:
                cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT 1;")
                row = cursor.fetchone()
                if row:
                    print(f"  - {table_name}: Found data")
                else:
                    print(f"  - {table_name}: Empty table")
            except Exception as e:
                error_msg = str(e)
                print(f"  - {table_name}: ERROR retrieving data - {error_msg}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\n✅ Database connection test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run tests."""
    print("=== Database and API Connection Test ===")
    print(f"Database: {DB_PARAMS['dbname']} at {DB_PARAMS['host']}:{DB_PARAMS['port']}")
    
    # Test direct database connection
    db_result = test_db_connection()
    
    # Test API connection
    api_result = test_api_connection()
    
    # Print final results
    print("\n=== Test Results ===")
    print(f"✅ Direct DB Connection: {'SUCCESS' if db_result else 'FAILED'}")
    print(f"✅ API Connection: {'SUCCESS' if api_result else 'FAILED'}")
    
    return 0 if db_result and api_result else 1

if __name__ == "__main__":
    sys.exit(main())
