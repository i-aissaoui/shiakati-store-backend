#!/usr/bin/env python3
"""
List all methods in the APIClient class.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Try to import the API client
try:
    print("Importing API client...")
    from src.utils.api_client import APIClient
    
    # Create an instance
    print("Creating API client instance...")
    client = APIClient()
    
    # Get all the methods
    print("\nMethods in API client:")
    methods = [m for m in dir(client) if not m.startswith('__')]
    methods.sort()  # Sort for easier reading
    
    for method in methods:
        print(f"- {method}")
    
    # Check for specific methods
    required_methods = ['get_inventory', 'get_expenses', 'get_expenses_by_date_range']
    print("\nChecking for required methods:")
    for required in required_methods:
        if required in methods:
            print(f"✓ {required} is present")
        else:
            print(f"✗ {required} is MISSING")
            
except Exception as e:
    import traceback
    print(f"\nERROR: {str(e)}")
    traceback.print_exc()
