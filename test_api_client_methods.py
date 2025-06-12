#!/usr/bin/env python3
"""
Test script to verify the fixes to the APIClient class.
This script imports the APIClient class and tests the methods that were previously missing.
"""

import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "desktop_app", "src"))

# Import the APIClient class
from utils.api_client import APIClient

def test_api_client():
    """Test the APIClient class."""
    print("Testing APIClient class...")
    client = APIClient()
    
    # Test login
    print("\n=== Testing login ===")
    login_success = client.login("admin", "123")
    print(f"Login success: {login_success}")
    
    # Test get_sales_history
    print("\n=== Testing get_sales_history ===")
    sales_history = client.get_sales_history()
    print(f"Retrieved {len(sales_history)} sales")
    if sales_history:
        print(f"First sale: {sales_history[0]}")
    
    # Test get_orders
    print("\n=== Testing get_orders ===")
    orders = client.get_orders()
    print(f"Retrieved {len(orders)} orders")
    if orders:
        print(f"First order: {orders[0]}")
    
    # Test get_categories
    print("\n=== Testing get_categories ===")
    categories = client.get_categories()
    print(f"Retrieved {len(categories)} categories")
    if categories:
        print(f"Categories: {categories}")
    
    # Test get_expenses
    print("\n=== Testing get_expenses ===")
    expenses = client.get_expenses()
    print(f"Retrieved {len(expenses)} expenses")
    if expenses:
        print(f"First expense: {expenses[0]}")
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    test_api_client()
