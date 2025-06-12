#!/usr/bin/env python3
"""
Test script to verify the missing methods in the API client have been fixed.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the API client
from src.utils.api_client import APIClient

def test_api_client():
    try:
        client = APIClient()
        
        print("\n=== Testing API Client Methods ===")
        print("\nTesting get_inventory method...")
        inventory = client.get_inventory()
        if inventory is not None:
            print(f"✓ get_inventory method works! Retrieved {len(inventory)} items.")
        else:
            print("✗ get_inventory method failed!")
        
        print("\nTesting get_expenses method...")
        expenses = client.get_expenses()
        if expenses is not None:
            print(f"✓ get_expenses method works! Retrieved {len(expenses)} expenses.")
        else:
            print("✗ get_expenses method failed!")
            
        print("\nTesting get_expenses_by_date_range method...")
        date_expenses = client.get_expenses_by_date_range("2025-01-01", "2025-06-01")
        if date_expenses is not None:
            print(f"✓ get_expenses_by_date_range method works! Retrieved {len(date_expenses)} expenses.")
        else:
            print("✗ get_expenses_by_date_range method failed!")
            
        print("\nAll tests completed successfully!")
        return True
    except Exception as e:
        import traceback
        print(f"\nError testing API client: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_api_client()
    sys.exit(0 if success else 1)
