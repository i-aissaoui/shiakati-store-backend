#!/usr/bin/env python3
"""
Script to test the fixed API client implementation.
"""
print("Starting API client tests...")
import os
import sys
import time
import random
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the APIClient class
    from desktop_app.src.utils.api_client import APIClient
except ImportError as e:
    print(f"Error importing APIClient: {str(e)}")
    # Try alternative import path
    try:
        sys.path.append("/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src")
        from utils.api_client import APIClient
    except ImportError as e:
        print(f"Error with alternative import path: {str(e)}")
        sys.exit(1)

def test_api_client_methods():
    """Test all API client methods to ensure they work correctly."""
    print("=== Testing API Client Methods ===")
    
    # Create an API client instance
    client = APIClient()
    
    # Login
    print("\n== Testing login ==")
    login_success = client.login("admin", "123")
    print(f"Login success: {login_success}")
    assert login_success, "Login failed"
    
    methods_to_test = {
        "get_sales_history": [],
        "get_orders": [],
        "get_categories": [],
        "get_expenses": [],
        "get_stats": [],
        "create_sale": [
            [{"barcode": "123456789", "quantity": 2, "price": 1500}], 3000
        ]
    }
    
    success_count = 0
    total_methods = len(methods_to_test)
    
    for method_name, args in methods_to_test.items():
        print(f"\n== Testing {method_name}() ==")
        try:
            if not hasattr(client, method_name):
                print(f"ERROR: Method {method_name} does not exist")
                continue
                
            method = getattr(client, method_name)
            
            start_time = time.time()
            result = method(*args)
            end_time = time.time()
            
            print(f"Call completed in {end_time - start_time:.2f} seconds")
            
            # Check the result
            if isinstance(result, list):
                print(f"Result is a list with {len(result)} items")
                if result and len(result) > 0:
                    print(f"First item: {result[0]}")
            elif isinstance(result, dict):
                print(f"Result is a dictionary with {len(result)} keys")
                print(f"Keys: {list(result.keys())}")
            else:
                print(f"Result: {result}")
                
            success_count += 1
                
        except Exception as e:
            print(f"ERROR testing {method_name}: {str(e)}")
    
    # Print summary
    print(f"\n=== Testing Summary ===")
    print(f"Tested {total_methods} methods")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_methods - success_count}")
    
    if success_count == total_methods:
        print("\nALL METHODS WORKING CORRECTLY!")
    else:
        print(f"\nSome methods ({total_methods - success_count}) still need fixing.")

if __name__ == "__main__":
    test_api_client_methods()
