#!/usr/bin/env python3

import sys
import os

# Add the necessary path to import the API client
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop_app", "src"))

print("Python path:", sys.path)

try:
    # Try to import the APIClient class
    print("Attempting to import APIClient...")
    from desktop_app.src.utils.api_client import APIClient
    print("Successfully imported APIClient!")
except ImportError as e:
    print(f"Error importing APIClient from desktop_app.src.utils.api_client: {str(e)}")
    try:
        print("Trying alternative import...")
        from utils.api_client import APIClient
        print("Successfully imported APIClient from utils.api_client!")
    except ImportError as e2:
        print(f"Error importing from utils.api_client: {str(e2)}")
        sys.exit(1)

# Test if we got the APIClient class
print("\nVerifying APIClient class...")
print(f"APIClient is type: {type(APIClient)}")

# Create an instance and test basic functionality
print("\nCreating APIClient instance...")
client = APIClient()
print("APIClient instance created successfully!")

# Check for required methods
print("\nChecking for required methods...")
required_methods = [
    "get_sales_history",
    "get_orders", 
    "get_categories", 
    "get_expenses", 
    "get_stats", 
    "create_sale"
]

for method in required_methods:
    has_method = hasattr(client, method)
    print(f"Method {method}: {'EXISTS' if has_method else 'MISSING'}")

# Test login functionality
print("\nTesting login...")
login_success = client.login("admin", "123")
print(f"Login success: {login_success}")

# Test get_stats method
print("\nTesting get_stats method...")
try:
    stats = client.get_stats()
    print(f"Stats keys: {list(stats.keys())}")
    print(f"Total sales: {stats.get('total_sales')}")
    print(f"Total orders: {stats.get('total_orders')}")
    print(f"Total revenue: {stats.get('total_revenue')}")
    print(f"Top products: {len(stats.get('top_products', []))} items")
except Exception as e:
    print(f"Error calling get_stats: {str(e)}")

print("\nTest complete!")
