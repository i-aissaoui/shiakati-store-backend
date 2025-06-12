#!/usr/bin/env python3
"""
Script to directly test the API client implementation to confirm methods exist.
"""
import sys
import os
import importlib.util

# Path to the API client file
api_client_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "desktop_app/src/utils/api_client.py"
))

def check_methods():
    """Check if all required methods exist directly."""
    print(f"Testing API client at: {api_client_path}")
    
    if not os.path.isfile(api_client_path):
        print(f"File not found: {api_client_path}")
        return False
        
    # Add the parent directory to sys.path
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(api_client_path))))
    sys.path.append(parent_dir)
    
    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("api_client", api_client_path)
        api_client_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_client_module)
        
        # Create an instance
        client = api_client_module.APIClient()
        
        # Required methods
        required_methods = [
            "get_sales_history",
            "get_orders",
            "get_categories",
            "get_expenses",
            "get_stats",
            "create_sale"
        ]
        
        # Check each method
        for method_name in required_methods:
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                if callable(method):
                    print(f"✅ Method '{method_name}' exists and is callable")
                else:
                    print(f"❌ Method '{method_name}' exists but is not callable")
            else:
                print(f"❌ Method '{method_name}' does not exist")
        
        # Test the get_stats method to verify it works
        print("\nTesting get_stats method:")
        try:
            stats = client.get_stats()
            print(f"Stats: {stats}")
        except Exception as e:
            print(f"Error calling get_stats: {str(e)}")
            
        return True
    except Exception as e:
        print(f"Error checking API client: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_methods()
