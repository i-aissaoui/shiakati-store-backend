#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop_app", "src"))

from utils.api_client import APIClient

def test_method(client, method_name, *args, **kwargs):
    """Test a specific method on the APIClient and print the result."""
    print(f"\n== Testing {method_name}() ==")
    try:
        method = getattr(client, method_name)
        result = method(*args, **kwargs)
        print(f"Method exists and returned: {result[:100] if isinstance(result, str) else result}")
        return True
    except AttributeError:
        print(f"Method {method_name}() does not exist on APIClient")
        return False
    except Exception as e:
        print(f"Error calling {method_name}(): {str(e)}")
        return False

def main():
    print("Testing if API Client methods exist...")
    client = APIClient()
    
    # Test login first
    print("\n== Testing login() ==")
    try:
        success = client.login("admin", "123")
        print(f"Login result: {success}")
    except Exception as e:
        print(f"Error in login: {str(e)}")
    
    # Test the previously missing methods
    methods_to_test = [
        "get_categories",
        "get_orders",
        "get_sales_history",
        "get_expenses",
        "get_order_details",
        "get_order",
        "get_inventory"
    ]
    
    for method in methods_to_test:
        args = []
        if method in ["get_order", "get_order_details"]:
            args = ["1"]  # Pass a dummy order ID
        
        test_method(client, method, *args)
    
    # Test the date range method separately
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    print(f"\n== Testing get_orders_by_date_range() with dates: {start_date} to {end_date} ==")
    try:
        orders = client.get_orders_by_date_range(start_date, end_date)
        print(f"Retrieved {len(orders)} orders in date range")
        if orders:
            print("First order sample:")
            print(f"  Order ID: {orders[0].get('id')}")
            print(f"  Customer: {orders[0].get('customer_name')}")
            print(f"  Total: {orders[0].get('total')}")
            print(f"  Items: {len(orders[0].get('items', []))}")
    except AttributeError:
        print("Method get_orders_by_date_range() does not exist on APIClient")
    except Exception as e:
        print(f"Error calling get_orders_by_date_range(): {str(e)}")

if __name__ == "__main__":
    main()
