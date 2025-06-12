#!/usr/bin/env python3
"""
Simple test script to check if the API client methods are working properly.
"""

import os
import sys
import traceback

# Add the desktop_app/src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "desktop_app", "src"))

try:
    # Import the APIClient class
    from utils.api_client import APIClient
    
    # Create an instance of the API client
    client = APIClient()
    
    # Test login
    print("\n== Testing Login ==")
    login_success = client.login("admin", "123")
    print(f"Login success: {login_success}")
    
    # Test get_categories
    print("\n== Testing get_categories() ==")
    categories = client.get_categories()
    print(f"Retrieved {len(categories)} categories")
    print(f"Categories: {categories}")
    
    # Test get_orders
    print("\n== Testing get_orders() ==")
    orders = client.get_orders()
    print(f"Retrieved {len(orders)} orders")
    if orders:
        print(f"First order: {orders[0]}")
    
    # Test get_sales_history
    print("\n== Testing get_sales_history() ==")
    sales = client.get_sales_history()
    print(f"Retrieved {len(sales)} sales")
    if sales:
        print(f"First sale: {sales[0]}")
    
    # Test get_expenses
    print("\n== Testing get_expenses() ==")
    expenses = client.get_expenses()
    print(f"Retrieved {len(expenses)} expenses")
    if expenses:
        print(f"First expense: {expenses[0]}")
    
    # Test get_order_details
    print("\n== Testing get_order_details() ==")
    if orders:
        order_id = orders[0].get("id")
        order_details = client.get_order_details(order_id)
        print(f"Order details: {order_details is not None}")
    else:
        print("No orders available to test get_order_details")
    
    print("\n== All tests completed successfully ==")

except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()
