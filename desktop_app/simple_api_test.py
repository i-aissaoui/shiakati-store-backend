#!/usr/bin/env python3
import sys
import os
import inspect

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the API client
    from src.utils.api_client import APIClient
    
    print("Successfully imported APIClient")
    
    # Create an instance
    client = APIClient()
    
    # Print all the methods
    methods = [method for method in dir(client) if not method.startswith('_')]
    print(f"Available methods in APIClient: {methods}")
    
    # Check if the missing methods exist
    missing_methods = ["get_inventory", "get_expenses", "get_expenses_by_date_range"]
    for method in missing_methods:
        if method in methods:
            print(f"Method {method} exists")
        else:
            print(f"Method {method} DOES NOT exist")
    
    # Try calling each method
    try:
        print("\nTrying to call get_inventory():")
        inventory = client.get_inventory()
        print(f"get_inventory() returned {len(inventory)} items")
    except Exception as e:
        print(f"Error calling get_inventory(): {e}")
    
    try:
        print("\nTrying to call get_expenses():")
        expenses = client.get_expenses()
        print(f"get_expenses() returned {len(expenses)} items")
    except Exception as e:
        print(f"Error calling get_expenses(): {e}")
    
    try:
        print("\nTrying to call get_expenses_by_date_range():")
        expenses = client.get_expenses_by_date_range("2025-01-01", "2025-06-12")
        print(f"get_expenses_by_date_range() returned {len(expenses)} items")
    except Exception as e:
        print(f"Error calling get_expenses_by_date_range(): {e}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
