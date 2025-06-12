#!/usr/bin/env python3
"""
Test script to verify if the inventory and expenses methods work in isolation.
"""
import os
import sys
import time

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the API client
from src.utils.api_client import APIClient

def test_methods():
    client = APIClient()
    print("\n=== Testing API Client Methods ===")
    
    print("\n1. Testing get_inventory method...")
    try:
        start_time = time.time()
        inventory = client.get_inventory()
        duration = time.time() - start_time
        if inventory is not None:
            print(f"✓ get_inventory method works! Retrieved {len(inventory)} items in {duration:.2f} seconds.")
            print(f"  First few inventory items: {inventory[:2]}")
        else:
            print("✗ get_inventory method returned None!")
    except Exception as e:
        print(f"✗ get_inventory method failed with error: {str(e)}")
    
    print("\n2. Testing get_expenses method...")
    try:
        start_time = time.time()
        expenses = client.get_expenses()
        duration = time.time() - start_time
        if expenses is not None:
            print(f"✓ get_expenses method works! Retrieved {len(expenses)} expenses in {duration:.2f} seconds.")
            print(f"  First few expenses: {expenses[:2]}")
        else:
            print("✗ get_expenses method returned None!")
    except Exception as e:
        print(f"✗ get_expenses method failed with error: {str(e)}")
    
    print("\n3. Testing get_expenses_by_date_range method...")
    try:
        start_time = time.time()
        date_expenses = client.get_expenses_by_date_range("2025-01-01", "2025-06-11")
        duration = time.time() - start_time
        if date_expenses is not None:
            print(f"✓ get_expenses_by_date_range method works! Retrieved {len(date_expenses)} expenses in {duration:.2f} seconds.")
            print(f"  First few date-filtered expenses: {date_expenses[:2]}")
        else:
            print("✗ get_expenses_by_date_range method returned None!")
    except Exception as e:
        print(f"✗ get_expenses_by_date_range method failed with error: {str(e)}")
    
    print("\nTest completed!")
    return True

if __name__ == "__main__":
    test_methods()
