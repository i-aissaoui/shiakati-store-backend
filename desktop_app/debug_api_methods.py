#!/usr/bin/env python3
"""
Simple test script for API client methods with debugging output.
"""
import sys
import traceback

try:
    # Print Python version
    print(f"Python version: {sys.version}")
    
    # Import the module we're testing
    print("Importing modules...")
    import os
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    print("Importing API client...")
    from src.utils.api_client import APIClient
    
    print("Creating API client instance...")
    client = APIClient()
    
    print("Listing methods in APIClient:")
    methods = [m for m in dir(client) if not m.startswith('__')]
    print(methods)
    
    print("\nChecking for our target methods:")
    required_methods = ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']
    for method in required_methods:
        if method in methods:
            print(f"✓ Method '{method}' exists in API client")
            # Call the method to see if it works
            print(f"  Calling {method}...")
            if method == 'get_inventory':
                result = client.get_inventory()
                print(f"  {method} returned {len(result) if result is not None else None} items")
            elif method == 'get_expenses':
                result = client.get_expenses()
                print(f"  {method} returned {len(result) if result is not None else None} items")
            elif method == 'get_expenses_by_date_range':
                result = client.get_expenses_by_date_range("2025-01-01", "2025-06-11")
                print(f"  {method} returned {len(result) if result is not None else None} items")
        else:
            print(f"✗ Method '{method}' NOT found in API client")

    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
