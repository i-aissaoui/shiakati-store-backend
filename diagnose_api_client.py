#!/usr/bin/env python3
"""
Diagnostic script to be run alongside the main application.
This will help verify that the APIClient methods are working as expected.
"""
import os
import sys
import time

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, "desktop_app", "src"))

from utils.api_client import APIClient

def main():
    """Main function to test the APIClient methods."""
    print("=== API Client Diagnostics ===")
    print("This script will test the following methods:")
    print("- get_sales_history")
    print("- get_orders")
    print("- get_categories")
    print("- get_expenses")
    print("============================")
    
    api = APIClient()
    
    # Login
    print("\nLogging in...")
    api.login("admin", "123")
    
    # Test methods
    methods_to_test = [
        ("get_sales_history", api.get_sales_history),
        ("get_orders", api.get_orders),
        ("get_categories", api.get_categories),
        ("get_expenses", api.get_expenses)
    ]
    
    for name, method in methods_to_test:
        print(f"\nTesting {name}()...")
        try:
            start_time = time.time()
            result = method()
            end_time = time.time()
            
            print(f"  Success! Method completed in {end_time - start_time:.2f} seconds")
            if isinstance(result, list):
                print(f"  Retrieved {len(result)} items")
                if result and name != "get_categories":  # Categories might be small
                    print(f"  First item: {result[0]}")
                elif result:
                    print(f"  Categories: {[cat.get('name', 'Unknown') for cat in result]}")
            else:
                print(f"  Result: {result}")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    print("\n=== Diagnostics Complete ===")

if __name__ == "__main__":
    main()
