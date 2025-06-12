#!/usr/bin/env python3
"""
Script to directly check each required method in the API client.
This script includes more detailed printing for debugging.
"""
import sys
import os
import importlib.util
import traceback

def main():
    """Main function to check methods."""
    print("Starting method check script...")
    
    # Path to the API client file
    api_client_path = "/home/ismail/Desktop/projects/shiakati_store/backend/desktop_app/src/utils/api_client.py"
    print(f"API client path: {api_client_path}")
    
    # Check if file exists
    if not os.path.isfile(api_client_path):
        print(f"ERROR: API client file not found at {api_client_path}")
        return False
        
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(api_client_path))))
    print(f"Adding to sys.path: {parent_dir}")
    sys.path.append(parent_dir)
    
    try:
        print("Importing module...")
        spec = importlib.util.spec_from_file_location("api_client", api_client_path)
        api_client_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_client_module)
        
        print("Creating APIClient instance...")
        client = api_client_module.APIClient()
        print("APIClient instance created successfully!")
        
        # Check each required method
        required_methods = [
            "get_sales_history",
            "get_orders",
            "get_categories",
            "get_expenses",
            "get_stats",
            "create_sale"
        ]
        
        missing_methods = []
        
        print("\n=== API Client Methods Check ===")
        for method_name in required_methods:
            print(f"Checking method: {method_name}...", end=" ")
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                if callable(method):
                    print("✅ EXISTS and is callable")
                else:
                    print("❌ EXISTS but is NOT callable")
                    missing_methods.append(method_name)
            else:
                print("❌ DOES NOT EXIST")
                missing_methods.append(method_name)
        
        print("\n=== Summary ===")
        if missing_methods:
            print(f"Missing methods: {', '.join(missing_methods)}")
            return False
        else:
            print("All required methods are implemented! ✨")
            return True
            
    except Exception as e:
        print(f"ERROR during API client check: {str(e)}")
        traceback.print_exc()
        return False
        
if __name__ == "__main__":
    success = main()
    print(f"\nFinal result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)
