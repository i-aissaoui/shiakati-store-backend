#!/usr/bin/env python3
"""
Script to verify the completeness of the APIClient class implementation.
This script checks for required methods and displays the results.
"""
import importlib.util
import sys
import os

# Path to the API client file
api_client_path = os.path.join(
    os.path.dirname(__file__),
    "desktop_app/src/utils/api_client.py"
)

def check_methods():
    """Check if all required methods are implemented in the API client."""
    # Required methods that must be implemented
    required_methods = [
        "get_sales_history",
        "get_orders",
        "get_categories", 
        "get_expenses",
        "get_stats",
        "create_sale"
    ]

    print(f"Checking API client at: {api_client_path}")
    
    if not os.path.isfile(api_client_path):
        print(f"❌ API client file not found at {api_client_path}")
        return False

    try:
        # Add the parent directory to sys.path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(api_client_path)))))
        
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("api_client", api_client_path)
        api_client_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_client_module)
        
        # Create an instance of APIClient
        client = api_client_module.APIClient()
        
        # Check for each required method
        missing_methods = []
        implemented_methods = []
        
        for method_name in required_methods:
            if hasattr(client, method_name) and callable(getattr(client, method_name)):
                implemented_methods.append(method_name)
                print(f"✅ Method '{method_name}' is implemented")
            else:
                missing_methods.append(method_name)
                print(f"❌ Method '{method_name}' is NOT implemented")
        
        # Summary
        print("\n=== SUMMARY ===")
        print(f"Total required methods: {len(required_methods)}")
        print(f"Methods implemented: {len(implemented_methods)}")
        print(f"Methods missing: {len(missing_methods)}")
        
        if missing_methods:
            print(f"\nMissing methods: {', '.join(missing_methods)}")
            return False
        else:
            print("\nAll required methods are implemented! ✨")
            return True
            
    except Exception as e:
        print(f"❌ Error while checking API client: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_methods()
    sys.exit(0 if success else 1)
