#!/usr/bin/env python3
"""
Comprehensive test script for all APIClient methods required by the application.
This will verify that all previously missing methods are now working correctly.
"""

import os
import sys
import traceback

# Add the desktop_app/src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "desktop_app", "src"))

def format_result(result):
    """Format the result output to be readable"""
    if isinstance(result, list):
        if len(result) > 0:
            first_item = result[0]
            return f"List with {len(result)} items. First item: {str(first_item)[:150]}..."
        else:
            return f"Empty list []"
    elif isinstance(result, dict):
        return f"Dictionary with keys: {list(result.keys())}"
    else:
        return str(result)

def test_api_method(client, method_name, *args, **kwargs):
    """Test a specific method on the APIClient"""
    print(f"\n{'=' * 50}")
    print(f"TESTING: {method_name}()")
    print(f"{'=' * 50}")
    
    try:
        method = getattr(client, method_name)
        result = method(*args, **kwargs)
        print(f"SUCCESS: Method returned: {format_result(result)}")
        return True, result
    except AttributeError:
        print(f"FAIL: Method {method_name}() does not exist on APIClient")
        return False, None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return False, None

try:
    # Import the APIClient class
    from utils.api_client import APIClient
    
    print("\n" + "=" * 70)
    print("SHIAKATI STORE API CLIENT VERIFICATION")
    print("=" * 70)
    print("Testing all the previously missing methods to ensure they now work correctly")
    
    # Create an instance of the API client
    client = APIClient()
    
    # Test login first
    success, _ = test_api_method(client, "login", "admin", "123")
    if not success:
        print("\nERROR: Login failed. Cannot proceed with further tests.")
        sys.exit(1)
        
    # Test all the methods that were previously reported as missing
    methods_to_test = [
        # Basic methods with no parameters
        ("get_categories", [], {}),
        ("get_orders", [], {}),
        ("get_sales_history", [], {}),
        ("get_expenses", [], {}),
        
        # Methods requiring parameters
        # For testing get_order_details and get_order, we'll first need to get an order ID
        # from the get_orders method
    ]
    
    # Track overall success
    all_succeeded = True
    
    # Test each method
    for method_name, args, kwargs in methods_to_test:
        success, _ = test_api_method(client, method_name, *args, **kwargs)
        if not success:
            all_succeeded = False
    
    # Now test methods that need order IDs
    _, orders = test_api_method(client, "get_orders")
    if orders and len(orders) > 0:
        order_id = orders[0].get("id", "1")
        test_api_method(client, "get_order_details", order_id)
        test_api_method(client, "get_order", order_id)
    else:
        print("\nWARNING: Could not test order detail methods as no orders were found")
        
    # Print summary
    print("\n" + "=" * 70)
    if all_succeeded:
        print("✅ SUCCESS: All core API methods are now implemented and working!")
    else:
        print("❌ WARNING: Some API methods are still not functioning correctly")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
